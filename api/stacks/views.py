from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import generics, status

from .models import Stack
from .serializers import StackSerializer


class StackListView(generics.ListAPIView):
    queryset = Stack.objects.all()
    serializer_class = StackSerializer

    @extend_schema(
        methods=["GET"],
        tags=["stack"],
        summary="모든 기술 스택 조회",
        description="등록된 모든 기술 스택을 조회합니다.",
        responses={
            status.HTTP_200_OK: OpenApiTypes.OBJECT,
            status.HTTP_400_BAD_REQUEST: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                "요청 예시",
                summary="모들 기술 스택 조회",
                description="등록된 모든 기술 스택을 조회합니다.",
                value=None,
                request_only=True,
            ),
            OpenApiExample(
                "성공",
                value=[
                    {"id": 1, "name": "Python"},
                    {"id": 2, "name": "Java"},
                    {"id": 3, "name": "JavaScript"},
                ],
                response_only=True,
                status_codes=["200"],
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
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
