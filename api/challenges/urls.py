from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ChallengeViewSet

# ViewSet사용
router = DefaultRouter()
router.register(r"", ChallengeViewSet, basename="challenge")

urlpatterns = [
    path("", include(router.urls)),
]
