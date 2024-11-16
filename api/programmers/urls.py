from django.urls import path

from .views import (
    GetDateProgrammersScoreView,
    GetDateProgrammersSolvedView,
    GetPeriodProgrammersScoreView,
    GetPeriodProgrammersSolvedView,
    GetTodayProgrammersScoreView,
    GetTodayProgrammersSolvedView,
    GetTotalProgrammersInfoView,
    UpdateProgrammersInfoView,
)

urlpatterns = [
    path(
        "update/",
        UpdateProgrammersInfoView.as_view(),
        name="update_programmers_info",
    ),
    path(
        "total/",
        GetTotalProgrammersInfoView.as_view(),
        name="get_total_programmers_info",
    ),
    path(
        "today/solved/",
        GetTodayProgrammersSolvedView.as_view(),
        name="get_today_programmers_solved",
    ),
    path(
        "today/score/",
        GetTodayProgrammersScoreView.as_view(),
        name="get_today_programmers_score",
    ),
    path(
        "date/solved/",
        GetDateProgrammersSolvedView.as_view(),
        name="get_date_programmers_solved",
    ),
    path(
        "date/score/",
        GetDateProgrammersScoreView.as_view(),
        name="get_date_programmers_score",
    ),
    path(
        "period/solved/",
        GetPeriodProgrammersSolvedView.as_view(),
        name="get_period_programmers_solved",
    ),
    path(
        "period/score/",
        GetPeriodProgrammersScoreView.as_view(),
        name="get_period_programmers_score",
    ),
]
