from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import Item, UserItem
from ..serializers import ItemPurchaseSerializer, ItemSerializer, UserItemSerializer


# 사용자용 아이템 리스트
@extend_schema(
    tags=["Item"],
    summary="사용자용 아이템 리스트",
    description="사용자가 모든 아이템을 조회합니다.",
    responses={
        200: ItemSerializer(many=True),
        404: OpenApiResponse(description="아이템을 찾을 수 없음"),
    },
)
class ItemListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ItemSerializer
    queryset = Item.objects.all()


# 특정 아이템 상세 정보
@extend_schema(
    tags=["Item"],
    summary="특정 아이템 상세 정보",
    description="사용자가 특정 아이템의 상세 정보를 조회합니다.",
    parameters=[
        OpenApiParameter(
            name="item_id",
            description="조회할 아이템의 ID",
            required=True,
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
        )
    ],
    responses={
        200: ItemSerializer,
        404: OpenApiResponse(description="아이템을 찾을 수 없음"),
    },
)
class ItemDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ItemSerializer
    lookup_field = "id"
    lookup_url_kwarg = "item_id"
    queryset = Item.objects.all()


# 아이템 구매
@extend_schema(
    tags=["Item"],
    summary="아이템 구매",
    description="사용자가 상점에서 특정 아이템을 구매합니다.",
    request=ItemPurchaseSerializer,
    responses={
        200: OpenApiResponse(description="아이템 구매 성공"),
        400: OpenApiResponse(description="구매 실패: 잔액 부족 또는 기타 에러"),
        404: OpenApiResponse(description="아이템을 찾을 수 없음"),
    },
)
class ItemPurchaseView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ItemPurchaseSerializer

    def create(self, request, *args, **kwargs):
        user = request.user
        item_id = request.data.get("item_id")
        item = Item.objects.filter(id=item_id).first()

        if not item:
            return Response(
                {"detail": "아이템을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND
            )

        # 사용자의 코인 체크
        if user.coin_balance < item.price:
            return Response(
                {"detail": "코인이 부족합니다."}, status=status.HTTP_400_BAD_REQUEST
            )

        # 아이템 구매 처리
        UserItem.objects.create(user=user, item=item)
        user.coin_balance -= item.price
        user.save()

        return Response(
            {"message": "아이템 구매 성공", "remaining_balance": user.coin_balance},
            status=status.HTTP_200_OK,
        )


# 사용자 구매 아이템 로그
@extend_schema(
    tags=["Item"],
    summary="사용자 구매 이력 조회",
    description="사용자가 구매한 모든 아이템 이력을 조회합니다.",
    responses={
        200: UserItemSerializer(many=True),
        404: OpenApiResponse(description="사용자를 찾을 수 없음"),
    },
)
class UserItemPurchaseLogView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserItemSerializer

    def get_queryset(self):
        return UserItem.objects.filter(user=self.request.user)
