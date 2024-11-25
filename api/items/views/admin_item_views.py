from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import generics, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from ..models import Item
from ..serializers import ItemImageUploadSerializer, ItemSerializer


# 아이템 리스트 조회 및 등록
@extend_schema(
    tags=["Item"],
    summary="아이템 리스트 조회 및 등록",
    description="관리자가 판매 중인 모든 아이템 목록을 조회하거나 새로운 아이템을 등록합니다.",
    responses={
        200: ItemSerializer(many=True),
        201: OpenApiResponse(description="아이템 등록 성공"),
        403: OpenApiResponse(description="관리자 권한 없음"),
    },
)
class AdminItemListView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = ItemSerializer
    queryset = Item.objects.all()


# 아이템 이미지 등록
@extend_schema(
    tags=["Item"],
    summary="아이템 이미지 업로드",
    description="관리자가 아이템의 이미지를 업로드하거나 수정합니다.",
    request=ItemImageUploadSerializer,
    responses={
        200: ItemImageUploadSerializer,
        400: OpenApiResponse(description="잘못된 요청 데이터"),
        403: OpenApiResponse(description="관리자 권한 없음"),
    },
)
class AdminItemImageUploadView(generics.CreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = ItemImageUploadSerializer
    queryset = Item.objects.all()
    lookup_field = "id"
    lookup_url_kwarg = "item_id"

    parser_classes = [MultiPartParser, FormParser]


# 특정 아이템 조회, 수정 및 삭제
@extend_schema(
    tags=["Item"],
    summary="특정 아이템 조회, 수정 및 삭제",
    description="관리자가 특정 아이템의 정보를 조회하거나 수정하거나 삭제합니다.",
    parameters=[
        OpenApiParameter(
            name="item_id",
            description="조회, 수정 또는 삭제할 아이템의 ID",
            required=True,
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
        )
    ],
    responses={
        200: ItemSerializer,
        204: OpenApiResponse(description="아이템 삭제 성공"),
        400: OpenApiResponse(description="유효하지 않은 요청 데이터"),
        404: OpenApiResponse(description="아이템을 찾을 수 없음"),
    },
)
class AdminItemDetailView(generics.GenericAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = ItemSerializer
    lookup_field = "id"
    lookup_url_kwarg = "item_id"
    queryset = Item.objects.all()

    def get(self, request, *args, **kwargs):
        item = self.get_object()
        serializer = self.get_serializer(item)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        item = self.get_object()
        serializer = self.get_serializer(item, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        item = self.get_object()
        item.delete()
        return Response({"message": "아이템 삭제 성공"}, status=status.HTTP_204_NO_CONTENT)
