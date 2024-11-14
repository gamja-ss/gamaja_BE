from django.urls import path

from .views import GetTodayProgrammers, UpdateProgrammers

urlpatterns = [
    path("update/", UpdateProgrammers.as_view(), name="update_programmers"),
    path("today/", GetTodayProgrammers.as_view(), name="get_today_programmers"),
]
