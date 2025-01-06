from enum import Enum

from coins.models import Coin
from django.db import models
from django.utils.timezone import now, timedelta
from users.models import User


class ChallengeCondition(Enum):
    GITHUB_COMMITS = "github_commits"
    PROBLEM_SOLVING = "problem_solving"


class ChallengeStatus(Enum):
    PENDING = "pending"  # 모집 중
    ONGOING = "ongoing"  # 진행 중
    COMPLETED = "completed"  # 완료됨
    REJECTED = "rejected"  # 거절됨


class Challenge(models.Model):
    participants = models.ManyToManyField(User, related_name="challenges")
    winner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="won_challenges",
    )

    condition = models.CharField(
        max_length=20,
        choices=[(tag.value, tag.name) for tag in ChallengeCondition],
        verbose_name="Competition Condition",
    )

    start_date = models.DateField(verbose_name="Start Date")
    duration = models.IntegerField(
        choices=[(3, "3일"), (7, "7일"), (30, "30일")],
        verbose_name="Challenge Duration",
        default=7,
    )

    end_date = models.DateField(
        verbose_name="End Date", blank=True, null=True
    )  # 종료 날짜 계산

    status = models.CharField(
        max_length=20,
        choices=[(tag.value, tag.name) for tag in ChallengeStatus],
        default=ChallengeStatus.PENDING.value,
        verbose_name="Status",
    )

    total_bet_coins = models.PositiveIntegerField(
        verbose_name="Total Bet Coins", default=0
    )
    reward_coins = models.PositiveIntegerField(verbose_name="Reward Coins", default=0)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    def __str__(self):
        return f"Challenge {self.id} - {self.condition} ({self.status})"

    def save(self, *args, **kwargs):
        if self.start_date and self.duration is not None:
            self.end_date = self.start_date + timedelta(days=self.duration)
        super().save(*args, **kwargs)

    # 챌린지 시작 메서드
    def start_challenge(self):
        today = now().date()

        if self.participants.count() < 2:
            raise ValueError("챌린지는 최소 2명 이상 참여해야 합니다.")

        if self.start_date > today:
            raise ValueError(f"챌린지는 {self.start_date}부터 시작할 수 있습니다.")

        total_bet = 0

        for participant in self.participants.all():
            if participant.coins_balance >= self.total_bet_coins:
                participant.coins_balance -= self.total_bet_coins
                participant.save()
                Coin.objects.create(
                    user=participant, verb="challenge_bet", coins=-self.total_bet_coins
                )
                total_bet += self.total_bet_coins
            else:
                raise ValueError(f"{participant.username}님이 베팅할 코인이 부족합니다.")

        self.total_bet_coins = total_bet
        self.status = ChallengeStatus.ONGOING.value
        self.save()

    # 챌린지 완료 메서드 (승자 1명)
    def complete_challenge(self, winner):
        if self.status != ChallengeStatus.ONGOING.value:
            raise ValueError("진행 중인 챌린지만 완료할 수 있습니다.")

        self.status = ChallengeStatus.COMPLETED.value
        self.winner = winner
        self.save()

        reward = self.total_bet_coins

        winner.coins_balance += reward
        winner.save()

        Coin.objects.create(user=winner, verb="challenge_reward", coins=reward)
