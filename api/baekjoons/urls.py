from django.urls import path

from .views import (
    GetDateBaekjoonScore,
    GetDateBaekjoonSolved,
    GetPeriodBaekjoonScore,
    GetPeriodBaekjoonSolved,
    GetTodayBaekjoonScore,
    GetTodayBaekjoonSolved,
    GetTotalBaekjoonInfo,
    UpdateBaekjoonInfo,
)

urlpatterns = [
    path("update/", UpdateBaekjoonInfo.as_view(), name="update_baekjoon_info"),
    path("total/", GetTotalBaekjoonInfo.as_view(), name="get_total_baekjoon_info"),
    path(
        "today/solved/",
        GetTodayBaekjoonSolved.as_view(),
        name="get_today_baekjoon_solved",
    ),
    path(
        "today/score/", GetTodayBaekjoonScore.as_view(), name="get_today_baekjoon_score"
    ),
    path(
        "date/solved/",
        GetDateBaekjoonSolved.as_view(),
        name="get_date_baekjoon_solved",
    ),
    path(
        "date/score/",
        GetDateBaekjoonScore.as_view(),
        name="get_date_baekjoon_score",
    ),
    path(
        "period/solved/",
        GetPeriodBaekjoonSolved.as_view(),
        name="get_period_baekjoon_solved",
    ),
    path(
        "period/score/",
        GetPeriodBaekjoonScore.as_view(),
        name="get_period_baekjoon_score",
    ),
]
