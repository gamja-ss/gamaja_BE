from django.shortcuts import get_object_or_404
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
)
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from users.models import User
from users.serializers.user_profile_serializers import UserSerializer

from .models import Follow
from .serializers import FollowListSerializer


class UserSearchView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["follow"],
        summary="사용자 검색",
        description="닉네임으로 사용자를 검색합니다.",
        parameters=[
            OpenApiParameter(
                name="nickname",
                type=str,
                location=OpenApiParameter.QUERY,
                description="검색할 닉네임",
                required=False,
            ),
        ],
        responses={200: UserSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = User.objects.all()
        nickname = self.request.query_params.get("nickname", None)
        if nickname:
            queryset = queryset.filter(nickname__icontains=nickname)
        return queryset


class FollowView(generics.GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["follow"],
        summary="사용자 팔로우",
        description="특정 사용자를 닉네임으로 팔로우합니다.",
        parameters=[
            OpenApiParameter(
                name="nickname",
                description="팔로우할 사용자의 닉네임",
                required=True,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
            ),
        ],
        responses={
            201: OpenApiResponse(description="팔로우 성공"),
            400: OpenApiResponse(description="잘못된 요청"),
            404: OpenApiResponse(description="사용자를 찾을 수 없음"),
        },
    )
    def post(self, request, nickname):
        try:
            user_to_follow = User.objects.get(nickname=nickname)
            if request.user == user_to_follow:
                return Response(
                    {"error": "자기 자신을 팔로우할 수 없습니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            follow, created = Follow.objects.get_or_create(
                follower=request.user, followed=user_to_follow
            )
            if created:
                return Response(
                    {"message": f"{user_to_follow.nickname}님을 팔로우했습니다."},
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(
                    {"message": f"이미 {user_to_follow.nickname}님을 팔로우하고 있습니다."},
                    status=status.HTTP_200_OK,
                )
        except User.DoesNotExist:
            return Response(
                {"error": "사용자를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )


class UnfollowView(generics.GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["follow"],
        summary="사용자 언팔로우",
        description="특정 사용자를 닉네임으로 언팔로우합니다.",
        parameters=[
            OpenApiParameter(
                name="nickname",
                description="언팔로우할 사용자의 닉네임",
                required=True,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
            ),
        ],
        responses={
            200: OpenApiResponse(description="언팔로우 성공"),
            400: OpenApiResponse(description="잘못된 요청"),
            404: OpenApiResponse(description="사용자를 찾을 수 없음"),
        },
    )
    def delete(self, request, nickname):
        try:
            user_to_unfollow = User.objects.get(nickname=nickname)
            if request.user == user_to_unfollow:
                return Response(
                    {"error": "자기 자신을 언팔로우할 수 없습니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            follow = Follow.objects.filter(
                follower=request.user, followed=user_to_unfollow
            ).first()
            if follow:
                follow.delete()
                return Response(
                    {"message": f"{user_to_unfollow.nickname}님을 언팔로우했습니다."},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"message": f"{user_to_unfollow.nickname}님을 팔로우하고 있지 않습니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except User.DoesNotExist:
            return Response(
                {"error": "사용자를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )


class RemoveFollowerView(generics.GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["follow"],
        summary="팔로워 삭제",
        description="자신을 팔로우한 사용자를 팔로워 목록에서 삭제합니다.",
        parameters=[
            OpenApiParameter(
                name="nickname",
                description="삭제할 팔로워의 닉네임",
                required=True,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
            ),
        ],
        responses={
            200: OpenApiResponse(description="팔로워 삭제 성공"),
            400: OpenApiResponse(description="잘못된 요청"),
            404: OpenApiResponse(description="사용자를 찾을 수 없음"),
        },
    )
    def delete(self, request, nickname):
        try:
            follower_to_remove = User.objects.get(nickname=nickname)
            if request.user == follower_to_remove:
                return Response(
                    {"error": "자기 자신을 팔로워 목록에서 삭제할 수 없습니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            follow = Follow.objects.filter(
                follower=follower_to_remove, followed=request.user
            ).first()
            if follow:
                follow.delete()
                return Response(
                    {"message": f"{follower_to_remove.nickname}님을 팔로워 목록에서 삭제했습니다."},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"message": f"{follower_to_remove.nickname}님은 당신의 팔로워가 아닙니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except User.DoesNotExist:
            return Response(
                {"error": "사용자를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )


class OwnFollowerListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["follow"],
        summary="팔로워 목록 조회 (현재 사용자)",
        description="현재 사용자의 팔로워 목록과 총 팔로워/팔로잉 수를 조회합니다.",
        responses={200: FollowListSerializer},
        operation_id="get_own_follower_list",
    )
    def get(self, request):
        user = self.request.user
        queryset = self.get_queryset(user)
        serializer = self.get_serializer(queryset, many=True)

        response_data = {
            "users": serializer.data,
            "total_followers": user.followers_count,
            "total_following": user.following_count,
        }

        return Response(response_data)

    def get_queryset(self, user):
        if not user:
            return User.objects.none()
        return User.objects.filter(following__followed=user)


class UserFollowerListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["follow"],
        summary="팔로워 목록 조회 (특정 사용자)",
        description="특정 사용자의 팔로워 목록과 총 팔로워/팔로잉 수를 조회합니다.",
        parameters=[
            OpenApiParameter(
                name="nickname",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description="조회할 사용자의 닉네임",
                required=True,
            ),
        ],
        responses={200: FollowListSerializer},
        operation_id="get_user_follower_list",
    )
    def get(self, request, nickname):
        user = get_object_or_404(User, nickname=nickname)
        queryset = self.get_queryset(user)
        serializer = self.get_serializer(queryset, many=True)

        response_data = {
            "users": serializer.data,
            "total_followers": user.followers_count,
            "total_following": user.following_count,
        }

        return Response(response_data)

    def get_queryset(self, user):
        if not user:
            return User.objects.none()
        return User.objects.filter(following__followed=user)


class OwnFollowingListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["follow"],
        summary="팔로잉 목록 조회 (현재 사용자)",
        description="현재 사용자가 팔로우하는 사용자 목록과 총 팔로워/팔로잉 수를 조회합니다.",
        responses={200: FollowListSerializer},
        operation_id="get_own_following_list",
    )
    def get(self, request):
        user = self.request.user
        queryset = self.get_queryset(user)
        serializer = self.get_serializer(queryset, many=True)

        response_data = {
            "users": serializer.data,
            "total_followers": user.followers_count,
            "total_following": user.following_count,
        }

        return Response(response_data)

    def get_queryset(self, user):
        if not user:
            return User.objects.none()
        return User.objects.filter(followers__follower=user)


class UserFollowingListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["follow"],
        summary="팔로잉 목록 조회 (특정 사용자)",
        description="특정 사용자가 팔로우하는 사용자 목록과 총 팔로워/팔로잉 수를 조회합니다.",
        parameters=[
            OpenApiParameter(
                name="nickname",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description="조회할 사용자의 닉네임",
                required=True,
            ),
        ],
        responses={200: FollowListSerializer},
        operation_id="get_user_following_list",
    )
    def get(self, request, nickname):
        user = get_object_or_404(User, nickname=nickname)
        queryset = self.get_queryset(user)
        serializer = self.get_serializer(queryset, many=True)

        response_data = {
            "users": serializer.data,
            "total_followers": user.followers_count,
            "total_following": user.following_count,
        }

        return Response(response_data)

    def get_queryset(self, user):
        if not user:
            return User.objects.none()
        return User.objects.filter(followers__follower=user)
