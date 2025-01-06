from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (OpenApiParameter, OpenApiResponse,
                                   extend_schema)
from rest_framework import generics, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from users.models import User

from .models import Guestbook
from .serializers import GuestbookSerializer


@extend_schema(
    tags=["guestbook"],
    summary="방명록 작성",
    description="새로운 방명록을 작성합니다.",
    request=GuestbookSerializer,
    responses={201: GuestbookSerializer},
)
class CreateGuestbookView(generics.CreateAPIView):
    serializer_class = GuestbookSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        host = get_object_or_404(User, id=self.request.data.get("host"))
        serializer.save(guest=self.request.user, host=host)


@extend_schema(
    tags=["guestbook"],
    summary="작성자 방명록 수정",
    description="작성자가 자신의 방명록을 수정합니다.",
    methods=["PATCH"],
    parameters=[
        OpenApiParameter(
            name="id",
            description="수정할 방명록의 ID",
            required=True,
            type=int,
            location=OpenApiParameter.PATH,
        ),
    ],
    request=GuestbookSerializer,
    responses={
        200: GuestbookSerializer,
        403: OpenApiResponse(description="권한 없음"),
        404: OpenApiResponse(description="방명록을 찾을 수 없음"),
    },
)
class UpdateGuestbookView(generics.UpdateAPIView):
    queryset = Guestbook.objects.all()
    serializer_class = GuestbookSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"
    http_method_names = ["patch"]  # patch 메서드만 허용

    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    def perform_update(self, serializer):
        instance = serializer.instance
        if instance.guest != self.request.user:
            return Response(
                {"error": "자신의 방명록만 수정할 수 있습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer.save()


@extend_schema(
    tags=["guestbook"],
    summary="방명록 삭제",
    description="작성자 또는 방명록의 주인이 방명록을 삭제합니다.",
    parameters=[
        OpenApiParameter(
            name="id",
            description="삭제할 방명록의 ID",
            required=True,
            type=int,
            location=OpenApiParameter.PATH,
        ),
    ],
    responses={
        204: None,
        403: OpenApiResponse(description="권한 없음"),
        404: OpenApiResponse(description="방명록을 찾을 수 없음"),
    },
)
class DeleteGuestbookView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Guestbook.objects.all()
    lookup_field = "id"

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.guest != request.user and instance.host != request.user:
            return Response(
                {"error": "이 방명록을 삭제할 권한이 없습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class GuestbookPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = None
    max_page_size = 10


@extend_schema(
    tags=["guestbook"],
    summary="방명록 리스트 조회",
    description="특정 사용자의 방명록 리스트를 조회합니다.",
    parameters=[
        OpenApiParameter(
            name="nickname",
            description="방명록 주인의 닉네임",
            required=True,
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
        ),
    ],
    responses={200: GuestbookSerializer(many=True)},
)
class ListGuestbookView(generics.ListAPIView):
    serializer_class = GuestbookSerializer
    permission_classes = [AllowAny]
    pagination_class = GuestbookPagination

    def get_queryset(self):
        nickname = self.kwargs.get("nickname")
        host = get_object_or_404(User, nickname=nickname)
        return Guestbook.objects.filter(host=host).order_by("-created_at")
