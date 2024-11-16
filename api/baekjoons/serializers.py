from rest_framework import serializers

from .models import Baekjoon


class BaekjoonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Baekjoon
        fields = ["solved", "score", "tier", "date"]


class BaekjoonDateRequestSerializer(serializers.Serializer):
    date = serializers.DateField(required=True)


class BaekjoonPeriodRequestSerializer(serializers.Serializer):
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)
