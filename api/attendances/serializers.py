from rest_framework import serializers

from .models import Attendance

class AttendanceSerializer(serializers.ModelSerializer):
    total_coins = serializers.IntegerField(source="user.total_coins", read_only=True)

    class Meta:
        model = Attendance
        fields = ["id", "user", "date", "created_at", "total_coins"]
        read_only_fields = ["id", "user", "created_at", "date", "total_coins"]
