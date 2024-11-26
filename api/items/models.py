from common.models import TimeStampModel
from django.conf import settings
from django.db import models


# 아이템 이미지 s3업로드
def item_image_upload_to(instance, filename):
    return f"items/item_{instance.id}_{filename}"


class Item(TimeStampModel):
    name = models.CharField(max_length=100, null=False)
    description = models.TextField(blank=True)
    price = models.PositiveIntegerField(null=False)
    item_type = models.CharField(max_length=50, null=False)
    image = models.ImageField(upload_to=item_image_upload_to, null=True, blank=True)

    def __str__(self):
        return self.name


class UserItem(TimeStampModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_items"
    )
    item = models.ForeignKey(
        Item, on_delete=models.CASCADE, related_name="owned_by_users"
    )
    purchase_date = models.DateTimeField(auto_now_add=True)
    is_selected = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} owns {self.item}"
