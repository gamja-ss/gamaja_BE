from django.urls import path

from .views import (
    GetDateBaekjoonScore,
    GetDateBaekjoonSP,
    GetPeriodBaekjoonScore,
    GetPeriodBaekjoonSP,
    GetTodayBaekjoonScore,
    GetTodayBaekjoonSP,
    GetTotalBaekjoonInfo,
    UpdateBaekjoonInfo,
)

urlpatterns = [
    path("update/", UpdateBaekjoonInfo.as_view(), name="update_baekjoon_info"),
    path("total/", GetTotalBaekjoonInfo.as_view(), name="get_total_baekjoon_info"),
    path("today/sp/", GetTodayBaekjoonSP.as_view(), name="get_today_baekjoon_sp"),
    path(
        "today/score/", GetTodayBaekjoonScore.as_view(), name="get_today_baekjoon_score"
    ),
    path(
        "date/sp/",
        GetDateBaekjoonSP.as_view(),
        name="get_date_baekjoon_sp",
    ),
    path(
        "date/score/",
        GetDateBaekjoonScore.as_view(),
        name="get_date_baekjoon_score",
    ),
    path("period/sp/", GetPeriodBaekjoonSP.as_view(), name="get_period_baekjoon_sp"),
    path(
        "period/score/",
        GetPeriodBaekjoonScore.as_view(),
        name="get_period_baekjoon_score",
    ),
]
