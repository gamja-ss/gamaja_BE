import re

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from stacks.models import Stack, UserStack
from users.models import User
from users.serializers.user_profile_serializers import (
    NicknameSerializer,
    UserProfileSerializer,
    UserStackSerializer,
)


# 사용자 기술스택 선택 뷰
class UserStack_SelectionView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserStackSerializer

    @extend_schema(
        methods=["POST"],
        tags=["info"],
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
                    "selected_stacks": [1, 2, 3],
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


# 사용자 닉네임 수정 뷰
class ChangeNicknameView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NicknameSerializer

    @extend_schema(
        methods=["PATCH"],
        tags=["info"],
        summary="닉네임 변경",
        description="사용자가 자신의 닉네임을 변경하는 엔드포인트입니다.",
        responses={
            status.HTTP_200_OK: {
                "type": "object",
                "properties": {
                    "nickname": {
                        "type": "string",
                        "example": "New_Nickname",
                    }
                },
            },
            status.HTTP_400_BAD_REQUEST: {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "string",
                        "example": "Nickname already taken",
                    }
                },
            },
        },
        examples=[
            OpenApiExample(
                "성공 요청",
                value={"nickname": "새로운닉네임"},
                request_only=True,
                summary="닉네임 변경 요청 예시",
            ),
            OpenApiExample(
                "성공 응답",
                value={"nickname": "새로운닉네임"},
                response_only=True,
                status_codes=["200"],
                summary="닉네임 변경 성공 응답",
            ),
            OpenApiExample(
                "닉네임 중복 오류",
                value={"error": "Nickname already taken"},
                response_only=True,
                status_codes=["400"],
                summary="닉네임 중복 오류 응답",
            ),
            OpenApiExample(
                "잘못된 요청 오류",
                value={"error": "Invalid request parameters"},
                response_only=True,
                status_codes=["400"],
                summary="잘못된 요청 오류 응답",
            ),
        ],
    )
    def patch(self, request, *args, **kwargs):
        new_nickname = request.data.get("nickname")

        # 닉네임 유효성 검사
        if not new_nickname or len(new_nickname) < 2 or len(new_nickname) > 20:
            return Response(
                {"닉네임은 2자 이상 20자이하만 가능합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not re.match("^[A-Za-z0-9_가-힣]+$", new_nickname):
            return Response(
                {"error": "알파벳, 숫자, 밑줄, 한글 포함 가능/ 특수문자 불가능"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 닉네임 중복 확인
        if User.objects.filter(nickname=new_nickname).exists():
            return Response(
                {"error": "Nickname already taken"}, status=status.HTTP_400_BAD_REQUEST
            )

        # 닉네임 업데이트
        request.user.nickname = new_nickname
        request.user.save()

        return Response({"nickname": new_nickname}, status=status.HTTP_200_OK)


# 본인 프로필 조회 뷰
@extend_schema(
    tags=["info"],
    summary="사용자 프로필 조회",
    description="로그인한 사용자의 프로필 정보를 조회합니다.",
    responses={status.HTTP_200_OK: UserProfileSerializer},
)
class MyProfileDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get(self, request):
        user = request.user

        profile = User.objects.get(id=user.id)

        serializer = self.get_serializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 사용자 프로필 조회 뷰
@extend_schema(
    tags=["info"],
    summary="사용자 프로필 조회",
    description="다른 사용자의 프로필 정보를 조회합니다.",
    responses={status.HTTP_200_OK: UserProfileSerializer},
)
class UserProfileDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get(self, request, nickname):
        profile = get_object_or_404(User, nickname=nickname)

        serializer = self.get_serializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
