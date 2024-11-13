from django.urls import path
from githubs.views import (
    GetDateGithubCommits,
    GetPeriodGithubCommits,
    GetTodayGithubCommits,
    GetTotalGithubCommits,
    UpdateGithubCommits,
)

urlpatterns = [
    path("update/", UpdateGithubCommits.as_view(), name="update_github_commits"),
    path("total/", GetTotalGithubCommits.as_view(), name="get_total_github_commits"),
    path("today/", GetTodayGithubCommits.as_view(), name="get_today_github_commits"),
    path(
        "date/",
        GetDateGithubCommits.as_view(),
        name="get_date_github_commits",
    ),
    path("period/", GetPeriodGithubCommits.as_view(), name="get_period_github_commits"),
]
