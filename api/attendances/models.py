from common.models import TimeStampModel
from django.db import models
from users.models import User  


class Attendance(TimeStampModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="attendances")
    coin_awarded = models.PositiveSmallIntegerField(default=0)  # 지급된 코인의 수
    date = models.DateField(auto_now_add=True)  # 출석한 날짜

    class Meta:
        unique_together = (
            "user",
            "date",
        )  # 같은 유저가 같은 날짜에 중복 출석하지 못하도록 설정
        verbose_name = "Attendance"
        verbose_name_plural = "Attendances"

    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.coin_awarded} coins"
