import requests
from django.utils import timezone
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
)
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Github
from .serializers import (
    GithubDateRequestSerializer,
    GithubPeriodRequestSerializer,
    GithubSerializer,
)
from .utils import update_user_github_commits


class UpdateGithubCommitsView(generics.GenericAPIView):
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


class GetTotalGithubCommitsView(generics.RetrieveAPIView):
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


class GetTodayGithubCommitsView(generics.RetrieveAPIView):
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


class GetDateGithubCommitsView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GithubDateRequestSerializer

    @extend_schema(
        methods=["POST"],
        tags=["github"],
        summary="특정 날짜의 깃허브 커밋 수 조회",
        description="특정 날짜의 깃허브 커밋 수를 조회합니다",
        request=GithubDateRequestSerializer,
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
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        date = serializer.validated_data["date"]

        try:
            date_record = Github.objects.get(user=user, date=date)

            if date == user.github_initial_date:
                date_commits = date_record.commit_num - user.github_initial_commits
            else:
                previous_date = date - timezone.timedelta(days=1)
                previous_date_record = Github.objects.get(user=user, date=previous_date)
                date_commits = date_record.commit_num - previous_date_record.commit_num

            return Response({"date_commits": date_commits})

        except Github.DoesNotExist:
            return Response(
                {"error": "해당 날짜의 깃허브 커밋 정보가 없습니다"},
                status=status.HTTP_404_NOT_FOUND,
            )


class GetPeriodGithubCommitsView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GithubPeriodRequestSerializer

    @extend_schema(
        methods=["POST"],
        tags=["github"],
        summary="특정 기간의 깃허브 커밋 수 조회",
        description="지정된 시작일부터 종료일까지의 깃허브 커밋 수를 조회합니다",
        request=GithubPeriodRequestSerializer,
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
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        start_date = serializer.validated_data["start_date"]
        end_date = serializer.validated_data["end_date"]
        user = request.user

        if start_date > end_date:
            return Response(
                {"error": "시작일이 종료일보다 늦을 수 없습니다"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            end_record = Github.objects.get(user=user, date=end_date)

            if start_date == user.github_initial_date:
                period_commits = end_record.commit_num - user.github_initial_commits
            else:
                start_record = Github.objects.get(user=user, date=start_date)
                period_commits = end_record.commit_num - start_record.commit_num

            return Response({"period_commits": period_commits})

        except Github.DoesNotExist:
            return Response(
                {"error": "해당 기간의 깃허브 커밋 정보가 없습니다"},
                status=status.HTTP_404_NOT_FOUND,
            )


class GetPeriodDailyGithubCommitsView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GithubPeriodRequestSerializer

    @extend_schema(
        methods=["POST"],
        tags=["github"],
        summary="특정 기간의 날짜별 깃허브 커밋 수 조회",
        description="지정된 시작일부터 종료일까지의 날짜별 깃허브 커밋 수를 조회합니다",
        request=GithubPeriodRequestSerializer,
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="특정 기간의 날짜별 깃허브 커밋 수",
                examples=[
                    OpenApiExample(
                        "Success Response",
                        value={
                            "period_commits": {
                                "2024-11-01": 3,
                                "2024-11-02": 5,
                                "2024-11-03": 2,
                            }
                        },
                        response_only=True,
                    )
                ],
            ),
            400: OpenApiResponse(description="잘못된 요청"),
            404: OpenApiResponse(description="해당 기간의 깃허브 커밋 정보가 없습니다"),
        },
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        start_date = serializer.validated_data["start_date"]
        end_date = serializer.validated_data["end_date"]
        user = request.user

        if start_date > end_date:
            return Response(
                {"error": "시작일이 종료일보다 늦을 수 없습니다"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            period_commits = {}
            current_date = start_date
            if current_date == user.github_initial_date:
                prev_commit_num = user.github_initial_commits
            else:
                prev_date = current_date - timezone.timedelta(days=1)
                prev_record = Github.objects.get(user=user, date=prev_date)
                prev_commit_num = prev_record.commit_num

            while current_date <= end_date:
                try:
                    record = Github.objects.get(user=user, date=current_date)

                    daily_commits = record.commit_num - prev_commit_num
                    period_commits[current_date.strftime("%Y-%m-%d")] = daily_commits
                    prev_commit_num = record.commit_num
                except Github.DoesNotExist:
                    period_commits[current_date.strftime("%Y-%m-%d")] = 0

                current_date += timezone.timedelta(days=1)

            return Response({"period_commits": period_commits})

        except Github.DoesNotExist:
            return Response(
                {"error": "해당 기간의 깃허브 커밋 정보가 없습니다"},
                status=status.HTTP_404_NOT_FOUND,
            )
