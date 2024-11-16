from rest_framework import serializers

from .models import Programmers


class ProgrammersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Programmers
        fields = ["level", "score", "solved", "rank", "date"]


class ProgrammersDateRequestSerializer(serializers.Serializer):
    date = serializers.DateField(required=True)


class ProgrammersPeriodRequestSerializer(serializers.Serializer):
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)
