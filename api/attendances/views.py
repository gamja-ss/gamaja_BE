import logging

from coins.models import Coin
from django.db import transaction
from django.utils.timezone import now
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Attendance
from .serializers import AttendanceSerializer

logger = logging.getLogger("django")


class AttendanceView(generics.GenericAPIView):
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        methods=["POST"],
        summary="출석 체크",
        description="현재 로그인한 사용자의 출석을 서버 시간 기준으로 처리하고 코인을 지급합니다.",
        responses={
            201: OpenApiResponse(
                description="출석 성공",
                examples=[
                    OpenApiExample(
                        "성공 응답",
                        value={"message": "출석이 완료되었습니다."},
                    )
                ],
            ),
            400: OpenApiResponse(
                description="출석 실패 (이미 출석)",
                examples=[
                    OpenApiExample(
                        "출석 중복",
                        value={"message": "이미 출석하셨습니다."},
                    )
                ],
            ),
        },
    )
    def post(self, request):
        user = request.user
        today = now().date()
        logger.info(f"User: {request.user}")

        # 출석 중복 확인
        if Attendance.objects.filter(user=user, date=today).exists():
            return Response(
                {"message": "이미 출석하셨습니다."}, status=status.HTTP_400_BAD_REQUEST
            )
        # 코인의 원자성 보장을 위한 트랜젝션 처리
        try:
            with transaction.atomic():
                # 출석 처리
                Attendance.objects.create(user=user, date=today)

                # 코인 지급 처리
                Coin.objects.create(user=user, verb="attendance", coins=10)

        except Exception as e:
            if "duplicate key value" in str(e):
                logger.warning(f"Duplicate attendance entry detected: {e}")
                return Response(
                    {"message": "이미 출석하셨습니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            logger.error(f"Error during attendance creation: {e}")
            return Response(
                {"message": "출석 처리 중 오류가 발생했습니다.", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {"message": "출석이 완료되었습니다."},
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        methods=["GET"],
        summary="출석 이력 조회",
        description="현재 로그인한 사용자의 출석 이력을 반환합니다.",
        responses={
            200: OpenApiResponse(
                response=AttendanceSerializer(many=True),
                description="출석 이력 조회 성공",
                examples=[
                    OpenApiExample(
                        "성공 응답",
                        value=[
                            {
                                "id": 1,
                                "user": 1,
                                "date": "2024-11-16",
                                "created_at": "2024-11-16T01:00:00Z",
                            },
                            {
                                "id": 2,
                                "user": 1,
                                "date": "2024-11-17",
                                "created_at": "2024-11-17T01:00:00Z",
                            },
                        ],
                    )
                ],
            ),
        },
    )
    def get(self, request):
        user = request.user
        attendances = Attendance.objects.filter(user=user)
        serializer = AttendanceSerializer(attendances, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
