from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Coin
from .serializers import CoinSerializer


@extend_schema(
    tags=["coin"],
    summary="사용자의 전체 코인 수 조회",
    description="현재 로그인한 사용자의 총 코인 수를 조회합니다.",
    responses={
        200: OpenApiResponse(
            OpenApiTypes.INT,
            description="사용자의 총 코인 수",
            examples=[
                OpenApiExample(
                    "Successful Response",
                    value={"total_coins": 100},
                    response_only=True,
                )
            ],
        ),
    },
)
class UserTotalCoinsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"total_coins": request.user.total_coins})


class CoinPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = None
    max_page_size = 20


@extend_schema(
    tags=["coin"],
    summary="사용자의 코인 로그 조회",
    description="현재 로그인한 사용자의 코인 획득/사용 로그를 페이지네이션(20개씩)하여 조회합니다.",
    parameters=[
        OpenApiParameter(
            name="page",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="페이지 번호",
            default=1,
        ),
    ],
    responses={200: CoinSerializer(many=True)},
)
class UserCoinLogView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CoinSerializer
    pagination_class = CoinPagination

    def get_queryset(self):
        return Coin.objects.filter(user=self.request.user).order_by("-timestamp")
