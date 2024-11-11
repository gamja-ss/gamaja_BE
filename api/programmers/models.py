from common.models import TimeStampModel
from django.db import models
from users.models import User


class Programmers(TimeStampModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    solved_tests = models.IntegerField()
    score = models.IntegerField()
    rank = models.IntegerField()
    level = models.IntegerField()
    date = models.DateField()

    def __str__(self):
        return f"{self.date}-{self.score}"
