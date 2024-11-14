from django.urls import path
from users.views.user_info_views import ProgrammersInfoView

urlpatterns = [
    path("programmers-info/", ProgrammersInfoView.as_view(), name="programmers-info"),
]
