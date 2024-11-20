from rest_framework import serializers
from users.serializers.user_profile_serializers import UserSerializer


class FollowListSerializer(serializers.Serializer):
    users = UserSerializer(many=True)
    total_followers = serializers.IntegerField()
    total_following = serializers.IntegerField()
