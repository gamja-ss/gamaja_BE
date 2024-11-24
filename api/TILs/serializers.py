from rest_framework import serializers

from .models import TIL


class TILSerializer(serializers.ModelSerializer):
    class Meta:
        model = TIL
        fields = ["id", "title", "content", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
