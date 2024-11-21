from common.models import TimeStampModel
from django.db import models
from users.models import User


class Guestbook(TimeStampModel):
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name="host")
    guest = models.ForeignKey(User, on_delete=models.CASCADE, related_name="guest")
    content = models.TextField(null=False)
