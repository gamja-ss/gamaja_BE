from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from users.models import User

from .models import Guestbook
from .serializers import GuestbookSerializer


class CreateGuestbookView(generics.GenericAPIView):
    serializer_class = GuestbookSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["guestbook"],
        summary="방명록 작성",
        description="새로운 방명록을 작성합니다.",
        request=GuestbookSerializer,
        responses={201: GuestbookSerializer},
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        host_id = request.data.get("host")
        host = get_object_or_404(User, id=host_id)
        serializer.save(guest=request.user, host=host)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UpdateGuestbookView(generics.GenericAPIView):
    serializer_class = GuestbookSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["guestbook"],
        summary="작성자 방명록 수정",
        description="작성자가 자신의 방명록을 수정합니다.",
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
    def put(self, request, id):
        try:
            instance = Guestbook.objects.get(id=id)
        except Guestbook.DoesNotExist:
            return Response(
                {"error": "방명록을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if instance.guest != request.user:
            return Response(
                {"error": "자신의 방명록만 수정할 수 있습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class DeleteGuestbookByGuestView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["guestbook"],
        summary="작성자 방명록 삭제",
        description="작성자가 자신의 방명록을 삭제합니다.",
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
    def delete(self, request, id):
        try:
            instance = Guestbook.objects.get(id=id)
        except Guestbook.DoesNotExist:
            return Response(
                {"error": "방명록을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if instance.guest != request.user:
            return Response(
                {"error": "자신의 방명록만 삭제할 수 있습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )

        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DeleteGuestbookByHostView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["guestbook"],
        summary="주인 방명록 삭제",
        description="방명록의 주인이 방명록을 삭제합니다.",
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
    def delete(self, request, id):
        try:
            instance = Guestbook.objects.get(id=id)
        except Guestbook.DoesNotExist:
            return Response(
                {"error": "방명록을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if instance.host != request.user:
            return Response(
                {"error": "자신의 방명록 페이지의 글만 삭제할 수 있습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )

        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ListGuestbookView(generics.ListAPIView):
    serializer_class = GuestbookSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["guestbook"],
        summary="방명록 리스트 조회",
        description="특정 사용자의 방명록 리스트를 조회합니다.",
        parameters=[
            OpenApiParameter(
                name="host_nickname",
                description="방명록 주인의 닉네임",
                required=True,
                type=OpenApiTypes.STR,
            ),
        ],
        responses={200: GuestbookSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        host_nickname = request.query_params.get("host_nickname")
        if not host_nickname:
            return Response(
                {"error": "host_nickname is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            host = User.objects.get(nickname=host_nickname)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        queryset = self.get_queryset(host)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self, host):
        return Guestbook.objects.filter(host=host).order_by("-created_at")
