from django.urls import path
from users.views import user_profile_views

urlpatterns = [
    path(
        "stack/", user_profile_views.UserStack_SelectionView.as_view(), name="UserStack"
    ),
    path("nickname/", user_profile_views.ChangeNicknameView.as_view(), name="Nickname"),
]
