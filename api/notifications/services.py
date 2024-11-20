from notifications.models import Notification
from coins.models import Coin


class NotificationService:
    @staticmethod
    def create_attendance_notification(attendance):
        user = attendance.user
        # 코인 지급 정보를 가져옴
        recent_coin = Coin.objects.filter(user=user, verb="attendance").latest("timestamp")
        Notification.objects.create(
            user=user,
            type="attendance",
            message=f"{recent_coin.coins} 코인이 지급되었습니다.",
        )

#웹소켓 알림 페이로드 설정
    @staticmethod
    def get_notification_payload(attendance):
        user = attendance.user
        recent_notification = Notification.objects.filter(user=user, type="attendance").latest("created_at")

        return {
            "id": recent_notification.id,
            "type": recent_notification.type,
            "message": recent_notification.message,
            "is_read": recent_notification.is_read,
            "created_at": recent_notification.created_at.isoformat(),
        }
