from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from .models import Item, UserItem


# 아이템 목록
class ItemSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    is_purchased = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = [
            "id",
            "name",
            "description",
            "price",
            "item_type",
            "image_url",
            "is_purchased",
        ]

    # 이미지 URL 반환. S3에 저장된 URL을 반환하거나 이미지가 없으면 None 반환.
    @extend_schema_field(OpenApiTypes.STR)
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get("request")
            return (
                request.build_absolute_uri(obj.image.url) if request else obj.image.url
            )

        return None

    def get_is_purchased(self, obj):
        # 요청 사용자를 가져옴
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False

        # 사용자가 해당 아이템을 구매했는지 여부 확인
        return UserItem.objects.filter(user=request.user, item=obj).exists()


# 사용자 구매한 아이템 로그
class UserItemSerializer(serializers.ModelSerializer):
    item = ItemSerializer(read_only=True)  # 구매한 아이템의 상세 정보를 포함

    class Meta:
        model = UserItem
        fields = ["id", "user", "item", "purchase_date", "is_selected"]
        read_only_fields = ["id", "user", "purchase_date"]


# 아이템 구매
class ItemPurchaseSerializer(serializers.Serializer):
    item_id = serializers.IntegerField()

    def validate_item_id(self, value):
        if not Item.objects.filter(id=value).exists():
            raise serializers.ValidationError("유효하지 않은 아이템 ID입니다.")
        return value
