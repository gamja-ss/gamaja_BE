from common.models import TimeStampModel
from django.db import models
from users.models import User


class Baekjoon(TimeStampModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    solved_problem = models.IntegerField()
    score = models.IntegerField()
    tier = models.CharField(max_length=20)
    date = models.DateField()

    def __str__(self):
        return f"{self.date}-{self.score}"
