from coins.models import Coin
from rest_framework import serializers

from .models import Attendance


class CoinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coin
        fields = ["user", "verb", "coins", "timestamp"]


class AttendanceSerializer(serializers.ModelSerializer):
    # 출석 시 지급된 코인 정보도 반환할 수 있도록 CoinSerializer 포함
    coin_awarded = CoinSerializer(read_only=True)

    class Meta:
        model = Attendance
        fields = "__all__"
        read_only_fields = ["id", "user", "created_at", "date", "coin_awarded"]

    # 필요한 경우 custom save() 메소드 등 추가할 수 있습니다.
