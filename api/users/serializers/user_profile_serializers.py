from rest_framework import serializers
from stacks.models import Stack, UserStack
from stacks.serializers import StackSerializer

from ..models import User


class NicknameSerializer(serializers.Serializer):
    nickname = serializers.CharField(
        max_length=20, help_text="새로운 닉네임 (알파벳, 숫자, 밑줄, 한글 가능)"
    )


class UserStackSerializer(serializers.ModelSerializer):
    stack_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)
    selected_stacks = StackSerializer(many=True, read_only=True, source="stack")

    class Meta:
        model = UserStack
        fields = ["stack_ids", "selected_stacks"]

    def create(self, validated_data):
        user = self.context["request"].user
        stack_ids = validated_data.pop("stack_ids", [])

        # 기존 스택 제거 후 새롭게 추가
        UserStack.objects.filter(user=user).delete()
        selected_stacks = []
        for stack_id in stack_ids:
            stack = Stack.objects.get(id=stack_id)
            user_stack = UserStack.objects.create(user=user, stack=stack)
            selected_stacks.append(user_stack)

        return {"selected_stacks": selected_stacks}
