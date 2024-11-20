from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save
from django.dispatch import receiver

#출석 기록이 생성되면 알림을 생성하고 웹소켓을 통해 클라이언트에 push.
@receiver(post_save, sender="attendances.Attendance")  # 모델 이름으로 지정
def handle_attendance_notification(sender, instance, created, **kwargs):
    
    if created:
        # 지연 임포트를 사용하여 순환 참조 방지
        from attendances.models import Attendance
        from notifications.models import Notification

        # 출석 기록이 성공적으로 생성되었을 때 알림 생성
        notification = Notification.objects.create(
            user=instance.user,
            type="attendance",
            related_id=instance.id,
            message=f"코인이 지급되었습니다.",
        )

        # 웹소켓으로 알림 데이터 푸시
        channel_layer = get_channel_layer()
        if channel_layer:  # 채널 레이어가 설정된 경우에만 실행
            async_to_sync(channel_layer.group_send)(
                f"user_{instance.user.id}",  # 유저 ID를 그룹명으로 사용
                {
                    "type": "send_notification",  # consumer에서 처리할 메서드 이름
                    "message": {
                        "id": notification.id,
                        "type": notification.type,
                        "message": notification.message,
                        "is_read": notification.is_read,
                        "created_at": notification.created_at.isoformat(),
                    },
                },
            )
