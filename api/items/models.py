from common.models import TimeStampModel
from django.conf import settings
from django.db import models


class Item(TimeStampModel):
    name = models.CharField(max_length=100, null=False)  # 아이템 이름
    description = models.TextField(blank=True)  # 아이템 설명
    price = models.PositiveIntegerField(null=False)  # 아이템 가격 (코인)
    item_type = models.CharField(
        max_length=50, null=False
    )  # 아이템 종류 (예: 'skin', 'decoration')

    def __str__(self):
        return self.name


class UserItem(TimeStampModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_items"
    )
    item = models.ForeignKey(
        Item, on_delete=models.CASCADE, related_name="owned_by_users"
    )
    purchase_date = models.DateTimeField(auto_now_add=True)  # 구매일
    is_selected = models.BooleanField(default=False)  # 현재 감자에 적용된 상태

    def __str__(self):
        return f"{self.user} owns {self.item}"
