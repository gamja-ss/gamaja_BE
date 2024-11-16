from django.urls import path

from .views import (
    GetDateProgrammersScore,
    GetDateProgrammersSolved,
    GetPeriodProgrammersScore,
    GetPeriodProgrammersSolved,
    GetTodayProgrammersScore,
    GetTodayProgrammersSolved,
    GetTotalProgrammersInfo,
    UpdateProgrammersInfo,
)

urlpatterns = [
    path("update/", UpdateProgrammersInfo.as_view(), name="update_programmers_info"),
    path(
        "total/", GetTotalProgrammersInfo.as_view(), name="get_total_programmers_info"
    ),
    path(
        "today/solved/",
        GetTodayProgrammersSolved.as_view(),
        name="get_today_programmers_solved",
    ),
    path(
        "today/score/",
        GetTodayProgrammersScore.as_view(),
        name="get_today_programmers_score",
    ),
    path(
        "date/solved/",
        GetDateProgrammersSolved.as_view(),
        name="get_date_programmers_solved",
    ),
    path(
        "date/score/",
        GetDateProgrammersScore.as_view(),
        name="get_date_programmers_score",
    ),
    path(
        "period/solved/",
        GetPeriodProgrammersSolved.as_view(),
        name="get_period_programmers_solved",
    ),
    path(
        "period/score/",
        GetPeriodProgrammersScore.as_view(),
        name="get_period_programmers_score",
    ),
]
