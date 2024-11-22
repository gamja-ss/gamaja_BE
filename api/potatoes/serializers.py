from items.models import Item
from rest_framework import serializers

from .models import Potato, UserPreset


# 아이템 직렬화
class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ["id", "name", "description", "price", "item_type"]


# 감자 조회 및 수정
class UserPotatoSerializer(serializers.ModelSerializer):
    skin_item = ItemSerializer(read_only=True)  # 스킨 아이템의 상세 정보는 아이템시리얼라이저에서참조

    class Meta:
        model = Potato
        fields = ["id", "user", "skin_item", "created_at", "updated_at"]
        read_only_fields = ["id", "user", "created_at", "updated_at"]

    def update(self, instance, validated_data):
        skin_item_id = validated_data.get("skin_item_id")
        if skin_item_id:
            instance.skin_item = Item.objects.get(id=skin_item_id)
        instance.save()
        return instance


# 전체 프리셋 리스트 조회
class UserPotatoPresetListSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreset
        fields = ["id", "preset_name", "item_ids", "created_at"]


# 특정 프리셋 상세 조회
class UserPotatoPresetDetailSerializer(serializers.ModelSerializer):
    item_details = serializers.SerializerMethodField()

    class Meta:
        model = UserPreset
        fields = ["id", "preset_name", "item_details", "created_at"]

    def get_item_details(self, obj):
        items = Item.objects.filter(id__in=obj.item_ids)
        return ItemSerializer(items, many=True).data


# 프리셋 생성
class UserPotatoPresetCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreset
        fields = ["preset_name", "item_ids"]

    # 프리셋 유저당 3개로 갯수제한
    def validate(self, data):
        user = self.context["request"].user
        if UserPreset.objects.filter(user=user).count() >= 3:
            raise serializers.ValidationError("최대 3개의 프리셋만 소유할 수 있습니다.")
        return data

    # 프리셋 DB 저장
    def create(self, validated_data):
        user = self.context["request"].user
        return UserPreset.objects.create(user=user, **validated_data)


# 프리셋 수정 및 삭제
class UserPotatoPresetUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreset
        fields = ["preset_name", "item_ids"]

    def update(self, instance, validated_data):
        instance.preset_name = validated_data.get("preset_name", instance.preset_name)
        instance.item_ids = validated_data.get("item_ids", instance.item_ids)
        instance.save()
        return instance


# 프리셋 감자에 적용
class UserPotatoPresetApplySerializer(serializers.Serializer):
    preset_id = serializers.IntegerField()

    def validate_preset_id(self, value):
        user = self.context["request"].user
        preset = UserPreset.objects.filter(id=value, user=user).first()
        if not preset:
            raise serializers.ValidationError("해당 프리셋이 존재하지 않거나 권한이 없습니다.")

        # 프리셋에 포함된 아이템 유효성 확인
        if not Item.objects.filter(id__in=preset.item_ids).exists():
            raise serializers.ValidationError("프리셋에 유효한 아이템이 포함되어 있지 않습니다.")
        return value

    def save(self):
        user = self.context["request"].user
        preset = UserPreset.objects.get(id=self.validated_data["preset_id"], user=user)
        potato = Potato.objects.get(user=user)
        potato.skin_item = Item.objects.get(id=preset.item_ids[0])  # 예: 첫 번째 아이템만 적용
        potato.save()
        return potato
