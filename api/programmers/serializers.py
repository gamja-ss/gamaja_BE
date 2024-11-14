from rest_framework import serializers

from .models import Programmers


class ProgrammersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Programmers
        fields = ["level", "score", "solved_tests", "rank", "date"]
