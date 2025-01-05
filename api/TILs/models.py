from common.models import TimeStampModel
from django.db import models
from users.models import User


class TIL(TimeStampModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    title = models.CharField(max_length=250, null=False)
    content = models.TextField(null=False)


class TILImage(TimeStampModel):
    TIL = models.ForeignKey(
        TIL, on_delete=models.CASCADE, null=True, related_name="images"
    )
    image = models.URLField(max_length=500, null=False)  # S3 URL을 직접 저장
    is_temporary = models.BooleanField(default=True)

    @property
    def image_url(self):
        return self.image if self.image else None  # 이미지를 반환할 때는 S3 URL 반환
