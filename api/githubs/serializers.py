from rest_framework import serializers

from .models import Github


class GithubSerializer(serializers.ModelSerializer):
    class Meta:
        model = Github
        fields = ["user", "commit_num", "date"]


class GithubDateRequestSerializer(serializers.Serializer):
    date = serializers.DateField(required=True)


class GithubPeriodRequestSerializer(serializers.Serializer):
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)
