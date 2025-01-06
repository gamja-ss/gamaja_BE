from rest_framework import serializers

from .models import Challenge


#  챌린지 Serializer
class ChallengeSerializer(serializers.ModelSerializer):
    participants = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    winner = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Challenge
        fields = "__all__"


#  챌린지 생성 Serializer
class ChallengeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenge
        fields = ["condition", "start_date", "duration", "total_bet_coins"]


#  챌린지 요청 Serializer
class ChallengeRequestSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    challenge_id = serializers.IntegerField()


#  챌린지 응답 Serializer
class ChallengeResponseSerializer(serializers.Serializer):
    accepted = serializers.BooleanField()  # T/F


# 챌린지 로그 Serializer
class ChallengeLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenge
        fields = [
            "id",
            "status",
            "total_bet_coins",
            "reward_coins",
            "created_at",
            "updated_at",
        ]


# 챌린지 결과 Serializer (챌린지 종료 후)
class ChallengeResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenge
        fields = ["id", "status", "reward_coins"]
