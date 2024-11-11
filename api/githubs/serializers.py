from rest_framework import serializers

from .models import Github


class GithubSerializer(serializers.ModelSerializer):
    class Meta:
        model = Github
        fields = ["user", "commit_num", "date"]
