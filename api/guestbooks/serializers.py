from typing import Optional

from rest_framework import serializers
from users.models import User

from .models import Guestbook


class GuestbookSerializer(serializers.ModelSerializer):
    guest_nickname = serializers.SerializerMethodField()

    class Meta:
        model = Guestbook
        fields = ["id", "host", "guest_nickname", "content", "created_at", "updated_at"]
        read_only_fields = ["id", "guest_nickname", "created_at", "updated_at"]

    def get_guest_nickname(self, obj) -> Optional[str]:
        try:
            return obj.guest.nickname
        except User.DoesNotExist:
            return None
