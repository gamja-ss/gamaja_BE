from django.urls import path
from githubs.views import (
    GetDateGithubCommitsView,
    GetPeriodDailyGithubCommitsView,
    GetPeriodGithubCommitsView,
    GetTodayGithubCommitsView,
    GetTotalGithubCommitsView,
    UpdateGithubCommitsView,
)

urlpatterns = [
    path("update/", UpdateGithubCommitsView.as_view(), name="update_github_commits"),
    path(
        "total/", GetTotalGithubCommitsView.as_view(), name="get_total_github_commits"
    ),
    path(
        "today/", GetTodayGithubCommitsView.as_view(), name="get_today_github_commits"
    ),
    path(
        "date/",
        GetDateGithubCommitsView.as_view(),
        name="get_date_github_commits",
    ),
    path(
        "period/",
        GetPeriodGithubCommitsView.as_view(),
        name="get_period_github_commits",
    ),
    path(
        "period/daily/",
        GetPeriodDailyGithubCommitsView.as_view(),
        name="get_period_daily_github_commits",
    ),
]
