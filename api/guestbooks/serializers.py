from rest_framework import serializers

from .models import Guestbook


class GuestbookSerializer(serializers.ModelSerializer):
    guest_nickname = serializers.CharField(source="guest.nickname", read_only=True)

    class Meta:
        model = Guestbook
        fields = ["id", "host", "guest_nickname", "content", "created_at", "updated_at"]
        read_only_fields = ["id", "guest_nickname", "created_at", "updated_at"]
