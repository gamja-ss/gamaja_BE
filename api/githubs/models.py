from common.models import TimeStampModel
from django.db import models
from users.models import User


class Github(TimeStampModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    commit_num = models.BigIntegerField()
    date = models.DateField()

    def __str__(self):
        return f"{self.date}-{self.commit_num}"
