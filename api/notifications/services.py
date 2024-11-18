from notifications.models import Notification


class NotificationService:
    @staticmethod
    def create_attendance_notification(attendance):
        user = attendance.user
        coin = attendance.coin_awarded
        Notification.objects.create(
            user=user,
            type="attendance",
            message=f"{coin} 코인이 지급되었습니다.",
        )
