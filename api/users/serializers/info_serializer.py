from rest_framework import serializers
from users.models import User


class ProgrammersInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["programmers_id", "programmers_password"]
        extra_kwargs = {"programmers_password": {"write_only": True}}
