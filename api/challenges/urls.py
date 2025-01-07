from django.urls import path

from .views import (
    ChallengeCreateView,
    ChallengeDeleteView,
    ChallengeLogView,
    ChallengeResponseView,
    ChallengeResultView,
)

urlpatterns = [
    path("", ChallengeCreateView.as_view(), name="challenge_create"),
    path(
        "<int:pk>/response/",
        ChallengeResponseView.as_view(),
        name="challenge_response",
    ),
    path("log/", ChallengeLogView.as_view(), name="challenge_log"),
    path(
        "<int:pk>/result/",
        ChallengeResultView.as_view(),
        name="challenge_result",
    ),
    path("<int:pk>/", ChallengeDeleteView.as_view(), name="challenge_delete"),
]
