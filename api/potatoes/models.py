from common.models import TimeStampModel
from django.conf import settings
from django.db import models
from items.models import Item


class Potato(TimeStampModel):
    # 각 사용자는 하나의 감자만 소유
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="potato",
        unique=True,
    )
    # 현재 적용된 스킨 아이템 (nullable)
    skin_item = models.ForeignKey(
        Item,
        on_delete=models.SET_NULL,
        related_name="potatoes_with_skin",
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.user}'s Potato"

    # 기본감자 생성
    @classmethod
    def create_default(cls, user):
        default_skin_item = Item.objects.filter(item_type="skin").first()
        return cls.objects.create(user=user, skin_item=default_skin_item)


class UserPreset(TimeStampModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="presets"
    )
    preset_name = models.CharField(max_length=50)
    item_ids = models.JSONField()  # 아이템 ID 배열을 JSON 필드로 저장

    def __str__(self):
        return f"{self.user}'s Preset: {self.preset_name}"
