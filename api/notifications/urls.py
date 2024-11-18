from django.urls import path
from notifications.views import (
    NotificationDetailView,
    NotificationListView,
    NotificationStatusView,
)

urlpatterns = [
    path(
        "", NotificationListView.as_view(), name="notification-list"
    ),  # WebSocket 전용 (Socket.IO에서 처리 가능)
    path("<int:pk>/", NotificationDetailView.as_view(), name="notification-detail"),
    path(
        "<int:pk>/status/", NotificationStatusView.as_view(), name="notification-status"
    ),
]
