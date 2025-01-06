from django.shortcuts import get_object_or_404
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
)
from rest_framework import generics, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from users.models import User

from .models import Follow
from .serializers import FollowListSerializer, UserSerializer


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
class UserSearchView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = User.objects.all()
        nickname = self.request.query_params.get("nickname")
        if nickname:
            queryset = queryset.filter(nickname__icontains=nickname)
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


class FollowUnfollowMixin:
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_user_to_follow(self, nickname):
        return get_object_or_404(User, nickname=nickname)

    def check_self_action(self, user, action):
        if self.request.user == user:
            return Response(
                {"error": f"자기 자신을 {action}할 수 없습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return None


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
class FollowView(FollowUnfollowMixin, generics.CreateAPIView):
    def create(self, request, nickname):
        user_to_follow = self.get_user_to_follow(nickname)
        self_check = self.check_self_action(user_to_follow, "팔로우")
        if self_check:
            return self_check

        follow, created = Follow.objects.get_or_create(
            follower=request.user, followed=user_to_follow
        )
        if created:
            return Response(
                {"message": f"{user_to_follow.nickname}님을 팔로우했습니다."},
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"message": f"이미 {user_to_follow.nickname}님을 팔로우하고 있습니다."},
            status=status.HTTP_200_OK,
        )


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
class UnfollowView(FollowUnfollowMixin, generics.DestroyAPIView):
    def destroy(self, request, nickname):
        user_to_unfollow = self.get_user_to_follow(nickname)
        self_check = self.check_self_action(user_to_unfollow, "언팔로우")
        if self_check:
            return self_check

        follow = Follow.objects.filter(
            follower=request.user, followed=user_to_unfollow
        ).first()
        if follow:
            follow.delete()
            return Response(
                {"message": f"{user_to_unfollow.nickname}님을 언팔로우했습니다."},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"message": f"{user_to_unfollow.nickname}님을 팔로우하고 있지 않습니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )


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
        204: OpenApiResponse(description="팔로워 삭제 성공"),
        400: OpenApiResponse(description="잘못된 요청"),
        404: OpenApiResponse(description="사용자를 찾을 수 없음"),
    },
)
class RemoveFollowerView(generics.DestroyAPIView):
    queryset = User.objects.all()
    lookup_field = "nickname"
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        follower_to_remove = self.get_object()
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
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {"message": f"{follower_to_remove.nickname}님은 당신의 팔로워가 아닙니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class FollowPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = None
    max_page_size = 20


class FollowListMixin:
    serializer_class = UserSerializer
    pagination_class = FollowPagination

    def get_response_data(self, user, queryset):
        serializer = self.get_serializer(queryset, many=True)
        return {
            "users": serializer.data,
            "total_followers": user.followers_count,
            "total_following": user.following_count,
        }

    def get_queryset(self, user, relationship):
        if not user:
            return User.objects.none()
        return User.objects.filter(**{relationship: user})


class OwnFollowersListView(FollowListMixin, generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["follow"],
        summary="팔로워 목록 조회 (현재 사용자)",
        description="현재 사용자의 팔로워 목록과 총 팔로워/팔로잉 수를 조회합니다.",
        responses={200: FollowListSerializer},
        operation_id="own_follower_list",
    )
    def get(self, request):
        user = self.request.user
        queryset = self.get_queryset(user, relationship="following__followed")
        return Response(self.get_response_data(user, queryset))


class UserFollowersListView(FollowListMixin, generics.ListAPIView):
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
        operation_id="user_follower_list",
    )
    def get(self, request, nickname):
        user = get_object_or_404(User, nickname=nickname)
        queryset = self.get_queryset(user, relationship="following__followed")
        return Response(self.get_response_data(user, queryset))


class OwnFollowingListView(FollowListMixin, generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["follow"],
        summary="팔로잉 목록 조회 (현재 사용자)",
        description="현재 사용자가 팔로우하는 사용자 목록과 총 팔로워/팔로잉 수를 조회합니다.",
        responses={200: FollowListSerializer},
        operation_id="own_following_list",
    )
    def get(self, request):
        user = self.request.user
        queryset = self.get_queryset(user, relationship="followers__follower")
        return Response(self.get_response_data(user, queryset))


class UserFollowingListView(FollowListMixin, generics.ListAPIView):
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
        operation_id="user_following_list",
    )
    def get(self, request, nickname):
        user = get_object_or_404(User, nickname=nickname)
        queryset = self.get_queryset(user, relationship="followers__follower")
        return Response(self.get_response_data(user, queryset))
