import requests
from django.utils import timezone
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
)
from rest_framework import generics, serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Github
from .serializers import GithubSerializer
from .utils import update_user_github_commits


class UpdateGithubCommits(generics.GenericAPIView):
    serializer_class = GithubSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        methods=["POST"],
        tags=["github"],
        summary="깃허브 커밋 업데이트(백엔드 서버용)",
        description="사용자의 깃허브 커밋 정보를 업데이트합니다",
        responses={
            200: OpenApiResponse(
                description="GitHub 커밋 수가 성공적으로 업데이트되었습니다",
                response=GithubSerializer,
            ),
            400: OpenApiResponse(description="GitHub API 요청 실패"),
        },
    )
    def post(self, request):
        user = request.user

        # utils.py의 함수 호출
        github_record = update_user_github_commits(user)

        if github_record is None:
            return Response(
                {"error": "GitHub API 요청 실패"}, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(github_record)
        return Response(
            {
                "message": "GitHub 커밋 수가 성공적으로 업데이트되었습니다",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class GetTotalGithubCommits(generics.RetrieveAPIView):
    serializer_class = GithubSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        methods=["GET"],
        tags=["github"],
        summary="깃허브 전체 커밋 수 조회",
        description="사용자의 오늘 날짜 기준 깃허브 전체 커밋 수를 조회합니다",
        responses={
            200: GithubSerializer,
            404: OpenApiResponse(description="오늘 날짜의 깃허브 커밋 정보가 없습니다"),
        },
    )
    def get(self, request):
        user = request.user
        today = timezone.now().date()
        try:
            github_record = Github.objects.get(user=user, date=today)
            serializer = self.get_serializer(github_record)
            return Response(serializer.data)
        except Github.DoesNotExist:
            return Response(
                {"error": "오늘 날짜의 깃허브 커밋 정보가 없습니다"},
                status=status.HTTP_404_NOT_FOUND,
            )


class GetTodayGithubCommits(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        methods=["GET"],
        tags=["github"],
        summary="오늘의 깃허브 커밋 수 조회",
        description="오늘의 깃허브 커밋 수를 조회합니다",
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.INT,
                description="오늘의 깃허브 커밋 수",
                examples=[
                    OpenApiExample(
                        "Success Response",
                        value={"today_commits": 5},
                        response_only=True,
                    )
                ],
            ),
            404: OpenApiResponse(description="오늘의 깃허브 커밋 정보가 없습니다"),
        },
    )
    def get(self, request):
        user = request.user
        today = timezone.now().date()

        try:
            today_record = Github.objects.get(user=user, date=today)

            if today == user.github_initial_date:
                today_commits = today_record.commit_num - user.github_initial_commits
            else:
                yesterday = today - timezone.timedelta(days=1)
                yesterday_record = Github.objects.get(user=user, date=yesterday)
                today_commits = today_record.commit_num - yesterday_record.commit_num

            return Response({"today_commits": today_commits})
        except Github.DoesNotExist:
            return Response(
                {"error": "오늘의 깃허브 커밋 정보가 없습니다"},
                status=status.HTTP_404_NOT_FOUND,
            )


class GetDateGithubCommits(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        methods=["GET"],
        tags=["github"],
        summary="특정 날짜의 깃허브 커밋 수 조회",
        description="특정 날짜의 깃허브 커밋 수를 조회합니다",
        parameters=[
            OpenApiParameter(
                name="date",
                description="조회할 날짜 (YYYY-MM-DD)",
                required=True,
                type=str,
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.INT,
                description="특정 날짜의 깃허브 커밋 수",
                examples=[
                    OpenApiExample(
                        "Success Response",
                        value={"date_commits": 5},
                        response_only=True,
                    )
                ],
            ),
            404: OpenApiResponse(description="해당 날짜의 깃허브 커밋 정보가 없습니다"),
        },
    )
    def get(self, request):
        user = request.user
        date_str = request.query_params.get("date")
        if not date_str:
            return Response({"error": "날짜를 지정해주세요"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            date = timezone.datetime.strptime(date_str, "%Y-%m-%d").date()
            date_record = Github.objects.get(user=user, date=date)

            if date == user.github_initial_date:
                date_commits = date_record.commit_num - user.github_initial_commits
            else:
                previous_date = date - timezone.timedelta(days=1)
                previous_date_record = Github.objects.get(user=user, date=previous_date)
                date_commits = date_record.commit_num - previous_date_record.commit_num

            return Response({"date_commits": date_commits})
        except ValueError:
            return Response(
                {"error": "올바른 날짜 형식이 아닙니다"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Github.DoesNotExist:
            return Response(
                {"error": "해당 날짜의 깃허브 커밋 정보가 없습니다"},
                status=status.HTTP_404_NOT_FOUND,
            )


class GetPeriodGithubCommits(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        methods=["GET"],
        tags=["github"],
        summary="특정 기간의 깃허브 커밋 수 조회",
        description="지정된 시작일부터 종료일까지의 깃허브 커밋 수를 조회합니다",
        parameters=[
            OpenApiParameter(
                name="start_date",
                description="시작 날짜 (YYYY-MM-DD)",
                required=True,
                type=str,
            ),
            OpenApiParameter(
                name="end_date",
                description="종료 날짜 (YYYY-MM-DD)",
                required=True,
                type=str,
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.INT,
                description="특정 기간의 깃허브 커밋 수",
                examples=[
                    OpenApiExample(
                        "Success Response",
                        value={"period_commits": 5},
                        response_only=True,
                    )
                ],
            ),
            404: OpenApiResponse(description="해당 기간의 깃허브 커밋 정보가 없습니다"),
        },
    )
    def get(self, request):
        user = request.user
        start_date_str = request.query_params.get("start_date")
        end_date_str = request.query_params.get("end_date")

        if not start_date_str or not end_date_str:
            return Response(
                {"error": "시작일과 종료일을 모두 지정해주세요"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            start_date = timezone.datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = timezone.datetime.strptime(end_date_str, "%Y-%m-%d").date()

            if start_date > end_date:
                return Response(
                    {"error": "시작일이 종료일보다 늦을 수 없습니다"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            end_record = Github.objects.get(user=user, date=end_date)

            if start_date == user.github_initial_date:
                period_commits = end_record.commit_num - user.github_initial_commits
            else:
                start_record = Github.objects.get(user=user, date=start_date)
                period_commits = end_record.commit_num - start_record.commit_num

            return Response({"period_commits": period_commits})
        except ValueError:
            return Response(
                {"error": "올바른 날짜 형식이 아닙니다"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Github.DoesNotExist:
            return Response(
                {"error": "해당 기간의 깃허브 커밋 정보가 없습니다"},
                status=status.HTTP_404_NOT_FOUND,
            )
