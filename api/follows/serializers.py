from rest_framework import serializers
from users.models import User

from .models import Follow


class UserSerializer(serializers.ModelSerializer):
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "nickname", "user_tier", "is_following"]

    def get_is_following(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Follow.objects.filter(follower=request.user, followed=obj).exists()
        return None


class FollowListSerializer(serializers.Serializer):
    users = UserSerializer(many=True)
    total_followers = serializers.IntegerField()
    total_following = serializers.IntegerField()
