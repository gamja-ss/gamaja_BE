from rest_framework import serializers

from .models import Attendance


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = [
            "id",
            "user",
            "coin_awarded",
            "date",
            "created_at",
        ]
        read_only_fields = ["id", "user", "created_at", "date"]
