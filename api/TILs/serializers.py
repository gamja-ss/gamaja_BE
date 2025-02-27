from rest_framework import serializers

from .models import TIL


class TILListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TIL
        fields = ["id", "title", "created_at"]


class TILDetailSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()

    class Meta:
        model = TIL
        fields = ["id", "title", "content", "created_at", "images"]

    def get_images(self, obj):
        return [{"id": image.id, "url": image.image} for image in obj.images.all()]
