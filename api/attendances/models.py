from coins.models import Coin
from common.models import TimeStampModel
from django.db import models
from users.models import User


class Attendance(TimeStampModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="attendances")
    date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = (
            "user",
            "date",
        )  # 같은 유저가 같은 날짜에 중복 출석하지 못하도록 설정
        verbose_name = "Attendance"
        verbose_name_plural = "Attendances"

    def __str__(self):
        return f"{self.user.username} - {self.date}"

    # 출석 저장 시 Coin 지급 처리
    def save(self, *args, **kwargs):

        created = not self.pk  # 출석이 새로 생성된 경우인지 확인
        super().save(*args, **kwargs)

        if created:
            # 출석 시 코인 지급 로직 추가
            Coin.objects.create(
                user=self.user,
                verb="attendance",
                coins=10,
            )
