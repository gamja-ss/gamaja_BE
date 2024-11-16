from django.urls import path
from users.views.user_info_views import (
    BaekjoonInfo,
    ProgrammersInfo,
    VerifyBaekjoonAccount,
)

urlpatterns = [
    path("programmers/", ProgrammersInfo.as_view(), name="programmers-info"),
    path("baekjoon/", BaekjoonInfo.as_view(), name="baekjoon-info"),
    path(
        "baekjoon/verify/",
        VerifyBaekjoonAccount.as_view(),
        name="verify_baekjoon_account",
    ),
]
