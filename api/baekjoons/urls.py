from django.urls import path

from .views import GetTodayBaekjoon, UpdateBaekjoon

urlpatterns = [
    path("update/", UpdateBaekjoon.as_view(), name="update_baekjoon"),
    path("today/", GetTodayBaekjoon.as_view(), name="get_today_baekjoon"),
]
