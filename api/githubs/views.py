import requests
from django.utils import timezone
from drf_spectacular.utils import OpenApiResponse, OpenApiTypes, extend_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Github
from .serializers import GithubSerializer


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
            )
        },
    )
    def post(self, request):
        user = request.user
        github_token = user.github_access_token
        github_username = user.username

        query = """
        query($username: String!) {
          user(login: $username) {
            contributionsCollection {
              totalCommitContributions
            }
          }
        }
        """

        variables = {"username": github_username}
        headers = {
            "Authorization": f"Bearer {github_token}",
            "Content-Type": "application/json",
        }

        response = requests.post(
            "https://api.github.com/graphql",
            json={"query": query, "variables": variables},
            headers=headers,
        )

        if response.status_code != 200:
            return Response(
                {"error": "GitHub API 요청 실패"}, status=status.HTTP_400_BAD_REQUEST
            )

        data = response.json()
        total_commits = data["data"]["user"]["contributionsCollection"][
            "totalCommitContributions"
        ]

        today = timezone.now().date()
        github_record, created = Github.objects.update_or_create(
            user=user, date=today, defaults={"commit_num": total_commits}
        )

        serializer = self.get_serializer(github_record)
        return Response(
            {
                "message": "GitHub 커밋 수가 성공적으로 업데이트되었습니다",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class GetTodayGithubCommits(generics.RetrieveAPIView):
    serializer_class = GithubSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        methods=["GET"],
        tags=["github"],
        summary="오늘의 깃허브 커밋 수 조회",
        description="사용자의 오늘 날짜 깃허브 커밋 수를 조회합니다",
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
