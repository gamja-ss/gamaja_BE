from django.db import models
from users.models import User

COIN_TYPES = (
    ("attendance", "출석"),
    ("github", "깃허브 커밋"),
    ("baekjoon", "백준 문제 풀이"),
    ("programmers", "프로그래머스 문제 풀이"),
    ("challenge_bet", "챌린지 베팅"),
    ("challenge_reward", "챌린지 보상"),
    ("purchase", "아이템 구매"),
)


class Coin(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="coins")
    verb = models.CharField(max_length=255, choices=COIN_TYPES)
    coins = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.user.update_total_coins()
