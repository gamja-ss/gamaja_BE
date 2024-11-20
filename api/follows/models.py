from common.models import TimeStampModel
from django.db import models
from django.db.models import F
from users.models import User


class Follow(TimeStampModel):
    follower = models.ForeignKey(
        User, related_name="following", on_delete=models.CASCADE
    )
    followed = models.ForeignKey(
        User, related_name="followers", on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ("follower", "followed")

    def save(self, *args, **kwargs):
        created = not self.pk
        super().save(*args, **kwargs)
        if created:
            self.followed.followers_count = F("followers_count") + 1
            self.followed.save()
            self.follower.following_count = F("following_count") + 1
            self.follower.save()

    def delete(self, *args, **kwargs):
        self.followed.followers_count = F("followers_count") - 1
        self.followed.save()
        self.follower.following_count = F("following_count") - 1
        self.follower.save()
        super().delete(*args, **kwargs)
