from django.urls import path

from .views import (
    GetDateBaekjoonScoreView,
    GetDateBaekjoonSolvedView,
    GetPeriodBaekjoonScoreView,
    GetPeriodBaekjoonSolvedView,
    GetTodayBaekjoonScoreView,
    GetTodayBaekjoonSolvedView,
    GetTotalBaekjoonInfoView,
    UpdateBaekjoonInfoView,
)

urlpatterns = [
    path("update/", UpdateBaekjoonInfoView.as_view(), name="update_baekjoon_info"),
    path("total/", GetTotalBaekjoonInfoView.as_view(), name="get_total_baekjoon_info"),
    path(
        "today/solved/",
        GetTodayBaekjoonSolvedView.as_view(),
        name="get_today_baekjoon_solved",
    ),
    path(
        "today/score/",
        GetTodayBaekjoonScoreView.as_view(),
        name="get_today_baekjoon_score",
    ),
    path(
        "date/solved/",
        GetDateBaekjoonSolvedView.as_view(),
        name="get_date_baekjoon_solved",
    ),
    path(
        "date/score/",
        GetDateBaekjoonScoreView.as_view(),
        name="get_date_baekjoon_score",
    ),
    path(
        "period/solved/",
        GetPeriodBaekjoonSolvedView.as_view(),
        name="get_period_baekjoon_solved",
    ),
    path(
        "period/score/",
        GetPeriodBaekjoonScoreView.as_view(),
        name="get_period_baekjoon_score",
    ),
]
