from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import TIL
from .serializers import TILSerializer


@extend_schema(
    tags=["til"],
    summary="TIL 작성",
    description="새로운 TIL을 작성합니다.",
    responses={
        201: OpenApiResponse(response=TILSerializer, description="TIL 작성 성공"),
        400: OpenApiResponse(description="잘못된 요청"),
    },
)
class CreateTILAPI(generics.CreateAPIView):
    serializer_class = TILSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@extend_schema(
    tags=["til"],
    summary="TIL 수정",
    description="기존 TIL을 수정합니다.",
    responses={
        200: OpenApiResponse(response=TILSerializer, description="TIL 수정 성공"),
        400: OpenApiResponse(description="잘못된 요청"),
        403: OpenApiResponse(description="권한 없음"),
        404: OpenApiResponse(description="TIL을 찾을 수 없음"),
    },
)
class UpdateTILAPI(generics.UpdateAPIView):
    serializer_class = TILSerializer
    permission_classes = [IsAuthenticated]
    queryset = TIL.objects.all()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            return Response(
                {"error": "이 TIL을 수정할 권한이 없습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().update(request, *args, **kwargs)


@extend_schema(
    tags=["til"],
    summary="TIL 삭제",
    description="TIL을 삭제합니다.",
    responses={
        204: OpenApiResponse(description="TIL 삭제 성공"),
        403: OpenApiResponse(description="권한 없음"),
        404: OpenApiResponse(description="TIL을 찾을 수 없음"),
    },
)
class DeleteTILAPI(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = TIL.objects.all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            return Response(
                {"error": "이 TIL을 삭제할 권한이 없습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)
