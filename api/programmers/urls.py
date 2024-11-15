from django.urls import path

from .views import (
    GetDateProgrammersScore,
    GetDateProgrammersST,
    GetPeriodProgrammersScore,
    GetPeriodProgrammersST,
    GetTodayProgrammersScore,
    GetTodayProgrammersST,
    GetTotalProgrammersInfo,
    UpdateProgrammersInfo,
)

urlpatterns = [
    path("update/", UpdateProgrammersInfo.as_view(), name="update_programmers_info"),
    path(
        "total/", GetTotalProgrammersInfo.as_view(), name="get_total_programmers_info"
    ),
    path(
        "today/st/", GetTodayProgrammersST.as_view(), name="get_today_programmersn_st"
    ),
    path(
        "today/score/",
        GetTodayProgrammersScore.as_view(),
        name="get_today_programmers_score",
    ),
    path(
        "date/st/",
        GetDateProgrammersST.as_view(),
        name="get_date_programmers_st",
    ),
    path(
        "date/score/",
        GetDateProgrammersScore.as_view(),
        name="get_date_programmers_score",
    ),
    path(
        "period/st/", GetPeriodProgrammersST.as_view(), name="get_period_programmers_st"
    ),
    path(
        "period/score/",
        GetPeriodProgrammersScore.as_view(),
        name="get_period_programmers_score",
    ),
]
