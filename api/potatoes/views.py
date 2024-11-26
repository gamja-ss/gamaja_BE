from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from items.models import Item
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Potato, UserPreset
from .serializers import (
    UserPotatoPresetApplySerializer,
    UserPotatoPresetCreateSerializer,
    UserPotatoPresetDetailSerializer,
    UserPotatoPresetListSerializer,
    UserPotatoPresetUpdateSerializer,
    UserPotatoSerializer,
)


# 감자 조회 및 수정
class UserPotatoView(generics.GenericAPIView):
    serializer_class = UserPotatoSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["potato"],
        summary="사용자의 감자 조회",
        description="사용자의 감자가 착용 중인 아이템 정보를 조회합니다.",
        responses={
            200: UserPotatoSerializer,
            404: OpenApiResponse(description="감자를 찾을 수 없습니다."),
        },
    )
    def get(self, request):
        potato = get_object_or_404(
            Potato.objects.select_related("skin_item"), user=request.user
        )
        serializer = self.get_serializer(potato)
        return Response(serializer.data)

    @extend_schema(
        tags=["potato"],
        summary="사용자의 감자 아이템 업데이트",
        description="사용자의 감자에 새로운 아이템(or 스킨)을 적용합니다.",
        request=UserPotatoSerializer,
        responses={
            200: UserPotatoSerializer,
            400: OpenApiResponse(description="유효하지 않은 요청 데이터입니다."),
            404: OpenApiResponse(description="감자를 찾을 수 없습니다."),
        },
    )
    def put(self, request):
        potato = get_object_or_404(
            Potato.objects.select_related("skin_item"), user=request.user
        )
        serializer = self.get_serializer(potato, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


#  프리셋 리스트 조회
@extend_schema(
    summary="사용자의 모든 프리셋 조회",
    responses={
        200: UserPotatoPresetListSerializer(many=True),
    },
)
class UserPotatoPresetListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserPotatoPresetListSerializer

    def get_queryset(self):
        user = self.request.user
        return UserPreset.objects.filter(user=user).prefetch_related("item_ids")


# 특정 프리셋 상세 조회
@extend_schema(
    summary="특정 프리셋 상세 조회",
    parameters=[
        OpenApiParameter("preset_id", OpenApiTypes.INT, location=OpenApiParameter.PATH),
    ],
    responses={
        200: UserPotatoPresetDetailSerializer,
        404: OpenApiResponse(description="Preset not found."),
    },
)
class UserPotatoPresetDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserPotatoPresetDetailSerializer
    lookup_field = "id"
    lookup_url_kwarg = "preset_id"

    def get_queryset(self):
        user = self.request.user
        return UserPreset.objects.filter(user=user).prefetch_related("item_ids")


# 프리셋 생성
@extend_schema(
    summary="사용자의 새로운 프리셋 생성",
    request=UserPotatoPresetCreateSerializer,
    responses={
        201: UserPotatoPresetCreateSerializer,
        400: OpenApiResponse(description="Maximum preset limit reached."),
    },
)
class UserPotatoPresetCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserPotatoPresetCreateSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# 프리셋 수정 (아이템들의 변경 및 삭제 반영)
@extend_schema(
    summary="사용자의 프리셋 수정 (아이템 추가 및 삭제)",
    description=(
        "사용자의 프리셋을 수정합니다. 새로운 item_ids를 제공하면 기존 아이템과 "
        "합쳐지거나 덮어씌워집니다. 빈 배열을 전달하면 아이템이 모두 삭제됩니다."
    ),
    parameters=[
        OpenApiParameter(
            name="preset_id",
            description="수정할 프리셋의 ID",
            required=True,
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
        ),
    ],
    request=UserPotatoPresetUpdateSerializer,
    responses={
        200: UserPotatoPresetUpdateSerializer,
        400: OpenApiResponse(description="유효하지 않은 요청입니다."),
        404: OpenApiResponse(description="프리셋을 찾을 수 없습니다."),
    },
)
class UserPotatoPresetUpdateView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserPotatoPresetUpdateSerializer
    lookup_field = "id"
    lookup_url_kwarg = "preset_id"

    def get_queryset(self):
        user = self.request.user
        return UserPreset.objects.filter(user=user)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()

        new_item_ids = request.data.get("item_ids", None)

        if new_item_ids is not None:
            if not new_item_ids:
                # 빈 배열이 전달되면 아이템 모두 삭제
                request.data["item_ids"] = []
            else:
                existing_item_ids = instance.item_ids or []
                merged_item_ids = list(set(existing_item_ids + new_item_ids))
                request.data["item_ids"] = merged_item_ids

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data, status=status.HTTP_200_OK)


# 프리셋 적용
@extend_schema(
    tags=["potato"],
    summary="프리셋 적용",
    description="사용자가 저장한 프리셋을 감자에 적용합니다.",
    parameters=[
        OpenApiParameter(
            name="preset_id",
            description="적용할 프리셋 ID",
            required=True,
            type=int,
            location=OpenApiParameter.PATH,
        ),
    ],
    request=UserPotatoPresetApplySerializer,
    responses={
        200: OpenApiResponse(description="프리셋이 성공적으로 적용되었습니다."),
        403: OpenApiResponse(description="권한이 없습니다."),
        404: OpenApiResponse(description="프리셋 또는 감자를 찾을 수 없습니다."),
    },
)
class UserPotatoPresetApplyView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        serializer = UserPotatoPresetApplySerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        preset_id = serializer.validated_data["preset_id"]

        user = request.user
        potato = (
            Potato.objects.select_related("user")
            .prefetch_related("applied_items")
            .get(user=user)
        )
        preset = get_object_or_404(
            UserPreset.objects.prefetch_related("user"), id=preset_id, user=user
        )

        item_ids = preset.item_ids
        items = Item.objects.filter(id__in=item_ids)

        if not items.exists():
            return Response(
                {"error": "프리셋에 유효한 아이템이 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        potato.applied_items.set(items)
        potato.save()

        return Response(
            {
                "message": "프리셋이 성공적으로 적용되었습니다.",
                "applied_items": [item.id for item in items],
            },
            status=status.HTTP_200_OK,
        )
