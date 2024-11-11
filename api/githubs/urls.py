from django.urls import path
from githubs.views import GetTodayGithubCommits, UpdateGithubCommits

urlpatterns = [
    path("update/", UpdateGithubCommits.as_view(), name="update_github_commits"),
    path("today/", GetTodayGithubCommits.as_view(), name="get_today_github_commits"),
]
