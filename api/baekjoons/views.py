from django.utils import timezone
from drf_spectacular.utils import OpenApiResponse, OpenApiTypes, extend_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Baekjoon
from .serializers import BaekjoonSerializer
from .utils import get_boj_profile


class UpdateBaekjoon(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BaekjoonSerializer

    @extend_schema(
        methods=["POST"],
        tags=["baekjoon"],
        summary="백준 정보 업데이트(백엔드 서버용)",
        description="사용자의 백준 문제 풀이 정보를 업데이트합니다",
        responses={
            200: OpenApiResponse(
                description="백준 정보가 성공적으로 업데이트되었습니다",
                response=BaekjoonSerializer,
            ),
            400: OpenApiResponse(description="백준 ID가 설정되지 않았습니다"),
            404: OpenApiResponse(description="백준 정보를 가져오는데 실패했습니다"),
        },
    )
    def post(self, request):
        user = request.user
        bj_id = user.baekjoon_id

        if not bj_id:
            return Response(
                {"error": "백준 ID가 설정되지 않았습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        profile = get_boj_profile(bj_id)
        if not profile:
            return Response(
                {"error": "백준 정보를 가져오는데 실패했습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        baekjoon, created = Baekjoon.objects.update_or_create(
            user=user,
            date=timezone.now().date(),
            defaults={
                "solved_problem": profile["solved_count"],
                "score": profile["rating"],
                "tier": f"Tier {profile['tier']}",
            },
        )

        serializer = self.get_serializer(baekjoon)
        return Response(
            {
                "message": "백준 정보가 성공적으로 업데이트되었습니다.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class GetTodayBaekjoon(generics.GenericAPIView):
    serializer_class = BaekjoonSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        methods=["GET"],
        tags=["baekjoon"],
        summary="오늘의 백준 정보 조회",
        description="현재 사용자의 오늘 날짜 백준 정보를 조회합니다.",
        responses={
            200: OpenApiResponse(
                response=BaekjoonSerializer,
                description="성공적으로 정보를 조회했습니다.",
            ),
            404: OpenApiResponse(description="오늘 날짜의 백준 정보가 없습니다."),
        },
    )
    def get(self, request):
        today = timezone.now().date()
        try:
            baekjoon_info = Baekjoon.objects.get(user=request.user, date=today)
            serializer = self.get_serializer(baekjoon_info)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Baekjoon.DoesNotExist:
            return Response(
                {"error": "오늘 날짜의 백준 정보가 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )
