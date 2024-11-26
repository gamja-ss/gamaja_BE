from common.models import TimeStampModel
from django.db import models
from users.models import User


class TIL(TimeStampModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    title = models.CharField(max_length=250, null=False)
    content = models.TextField(null=False)
