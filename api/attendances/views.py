from django.utils.timezone import now
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Attendance
from .serializers import AttendanceSerializer


class AttendanceView(APIView):
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
                        value={"message": "출석이 완료되었습니다.", "coin_awarded": 10},
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
        today = now().date()  # 서버 시간을 기준으로 오늘 날짜 가져오기

        # 출석 중복 확인
        if Attendance.objects.filter(user=user, date=today).exists():
            return Response(
                {"message": "이미 출석하셨습니다."}, status=status.HTTP_400_BAD_REQUEST
            )

        # 출석 처리
        coin_awarded = 10
        Attendance.objects.create(user=user, coin_awarded=coin_awarded, date=today)
        user.total_coins += coin_awarded
        user.save()

        return Response(
            {"message": "출석이 완료되었습니다.", "coin_awarded": coin_awarded},
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
                                "coin_awarded": 10,
                                "date": "2024-11-16",
                                "created_at": "2024-11-16T01:00:00Z",
                            },
                            {
                                "id": 2,
                                "user": 1,
                                "coin_awarded": 10,
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
