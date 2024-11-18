from drf_spectacular.utils import extend_schema
from notifications.models import Notification
from notifications.serializers import NotificationSerializer
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class NotificationStatusView(generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = Notification.objects.all()
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="알림 읽음 상태 변경",
        description="사용자에게 온 특정 알림의 읽음 상태를 업데이트합니다.",
    )
    def put(self, request, *args, **kwargs):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response(
            {"message": "Notification marked as read"}, status=status.HTTP_200_OK
        )

    @extend_schema(
        summary="특정 알림 삭제",
        description="사용자에게 온 특정 알림을 삭제합니다.",
    )
    def delete(self, request, *args, **kwargs):
        notification = self.get_object()
        notification.delete()
        return Response(
            {"message": "Notification deleted"}, status=status.HTTP_204_NO_CONTENT
        )


class NotificationDetailView(generics.RetrieveAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="특정 알림 세부정보 조회",
        description="사용자가 받은 특정 알림의 세부 정보를 반환합니다.",
        responses={200: NotificationSerializer},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
