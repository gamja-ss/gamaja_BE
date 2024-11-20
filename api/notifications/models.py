from common.models import TimeStampModel
from django.db import models
from users.models import User


class Notification(TimeStampModel):
    TYPE_CHOICES = [
        ("follow_request", "Follow Request"),
        ("guestbook_entry", "Guestbook Entry"),
        ("level_up", "Level Up"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    related_id = models.BigIntegerField(null=True, blank=True)
    message = models.TextField(null=False)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.type}: {self.message[:20]}"
