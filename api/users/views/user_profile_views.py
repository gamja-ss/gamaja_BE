from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from stacks.models import Stack, UserStack
from users.models import User
from users.user_profile_serializers import UserStackSerializer


class UserStack_SelectionView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserStackSerializer

    @extend_schema(
        methods=["POST"],
        tags=["Account"],
        summary="사용자가 선택한 기술 스택 저장",
        description="사용자가 선택한 기술 스택을 저장하는 엔드포인트입니다.",
        request=UserStackSerializer,
        responses={status.HTTP_201_CREATED: UserStackSerializer},
        examples=[
            OpenApiExample(
                "성공",
                value={"user": 1, "stack_ids": [1, 2, 3]},
                request_only=True,
                summary="기술 스택 선택 요청 예시",
            ),
            OpenApiExample(
                "성공 응답",
                value={
                    "selected_stacks": [
                        {"id": 1, "name": "Python"},
                        {"id": 2, "name": "Java"},
                        {"id": 3, "name": "JavaScript"},
                    ],
                },
                response_only=True,
                status_codes=["201"],
            ),
            OpenApiExample(
                "실패",
                summary="Bad Request Response",
                value={"error": "Invalid request parameters"},
                response_only=True,
                status_codes=["400"],
            ),
        ],
    )
    def post(self, request, *args, **kwargs):
        user = request.user
        stack_ids = request.data.get("stack_ids", [])

        # 선택된 스택 저장
        UserStack.objects.filter(user=user).delete()  # 기존 스택 삭제
        selected_stacks = []
        for stack_id in stack_ids:
            stack = Stack.objects.get(id=stack_id)
            user_stack = UserStack.objects.create(user=user, stack=stack)
            selected_stacks.append({"id": stack.id, "name": stack.name})

        return Response(
            {
                "selected_stacks": selected_stacks,
            },
            status=status.HTTP_201_CREATED,
        )
