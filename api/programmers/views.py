from django.shortcuts import render

# Create your views here.
from django.utils import timezone
from drf_spectacular.utils import OpenApiResponse, OpenApiTypes, extend_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Programmers
from .serializers import ProgrammersSerializer
from .utils import get_programmers_data


class UpdateProgrammers(generics.GenericAPIView):
    serializer_class = ProgrammersSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["programmers"],
        summary="프로그래머스 정보 업데이트(백엔드 서버용)",
        description="현재 사용자의 프로그래머스 정보를 업데이트합니다.",
        responses={
            200: OpenApiResponse(
                response=ProgrammersSerializer,
                description="프로그래머스 정보가 성공적으로 업데이트되었습니다.",
            ),
            400: OpenApiResponse(
                description="프로그래머스 계정 정보가 설정되지 않았거나 정보를 가져오는데 실패했습니다."
            ),
        },
    )
    def post(self, request):
        user = request.user
        if not user.programmers_id or not user.programmers_password:
            return Response(
                {"error": "프로그래머스 계정 정보가 설정되지 않았습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        programmers_data = get_programmers_data(
            user.programmers_id, user.programmers_password
        )
        if not programmers_data:
            return Response(
                {"error": "프로그래머스 정보를 가져오는데 실패했습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        programmers, created = Programmers.objects.update_or_create(
            user=user,
            defaults={
                "level": programmers_data["level"],
                "score": programmers_data["score"],
                "solved_tests": programmers_data["solved_tests"],
                "rank": programmers_data["rank"],
                "date": timezone.now().date(),
            },
        )

        serializer = self.get_serializer(programmers)
        return Response(
            {
                "message": "프로그래머스 정보가 성공적으로 업데이트되었습니다.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class GetTodayProgrammers(generics.GenericAPIView):
    serializer_class = ProgrammersSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["programmers"],
        summary="오늘의 프로그래머스 정보 조회",
        description="현재 사용자의 오늘 날짜 프로그래머스 정보를 조회합니다.",
        responses={
            200: OpenApiResponse(
                response=ProgrammersSerializer,
                description="성공적으로 정보를 조회했습니다.",
            ),
            404: OpenApiResponse(description="오늘 날짜의 프로그래머스 정보가 없습니다."),
        },
    )
    def get(self, request):
        today = timezone.now().date()
        try:
            programmer_info = Programmers.objects.get(user=request.user, date=today)
            serializer = self.get_serializer(programmer_info)
            return Response(serializer.data)
        except Programmers.DoesNotExist:
            return Response(
                {"error": "오늘 날짜의 프로그래머스 정보가 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )
