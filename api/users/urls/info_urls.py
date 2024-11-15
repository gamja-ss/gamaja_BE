from django.urls import path
from users.views.user_info_views import BaekjoonInfoView, ProgrammersInfoView

urlpatterns = [
    path("programmers-info/", ProgrammersInfoView.as_view(), name="programmers-info"),
    path("baekjoon-info/", BaekjoonInfoView.as_view(), name="baekjoon-info"),
]
