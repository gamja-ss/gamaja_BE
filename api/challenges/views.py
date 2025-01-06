from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from users.models import User

from .models import Challenge, ChallengeStatus
from .serializers import (
    ChallengeCreateSerializer,
    ChallengeLogSerializer,
    ChallengeResponseSerializer,
    ChallengeResultSerializer,
    ChallengeSerializer,
)


@extend_schema_view(
    list=extend_schema(description="수신/발신 챌린지 요청 리스트 조회"),
    create=extend_schema(
        description="새로운 챌린지 생성",
        request=ChallengeCreateSerializer,
        responses={201: ChallengeSerializer},
    ),
    retrieve=extend_schema(description="특정 챌린지 상세 조회"),
    destroy=extend_schema(description="챌린지 삭제"),
)
class ChallengeViewSet(viewsets.ModelViewSet):
    queryset = Challenge.objects.all()
    serializer_class = ChallengeSerializer

    def get_serializer_class(self):
        if self.action == "create":
            return ChallengeCreateSerializer
        elif self.action == "log":
            return ChallengeLogSerializer
        elif self.action == "result":
            return ChallengeResultSerializer
        return ChallengeSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_ids = serializer.validated_data.pop("user_ids")
        request_user = request.user  # 챌린지 생성자

        challenge = serializer.save()
        challenge.participants.add(request_user)  # 생성자는 자동 참가

        # 참가자 추가 및 웹소켓 요청 전송
        users = User.objects.filter(id__in=user_ids)
        challenge.participants.add(*users)

        channel_layer = get_channel_layer()
        for user in users:
            async_to_sync(channel_layer.group_send)(
                f"user_{user.id}",
                {
                    "type": "challenge.request",
                    "message": {
                        "text": f"{request_user.username}님이 챌린지 초대를 보냈습니다.",
                        "challenge_id": challenge.id,
                    },
                },
            )

        return Response(
            ChallengeSerializer(challenge).data, status=status.HTTP_201_CREATED
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status == ChallengeStatus.ONGOING.value:
            return Response(
                {"error": "진행 중인 챌린지는 삭제할 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        request=ChallengeResponseSerializer,
        responses={200: {"message": "챌린지 응답 완료"}},
        description="챌린지 요청에 대한 수락/거절",
    )
    @action(detail=True, methods=["post"], url_path="response")
    def challenge_response(self, request, pk=None):
        serializer = ChallengeResponseSerializer(data=request.data)
        if serializer.is_valid():
            challenge = self.get_object()
            user = request.user
            accepted = serializer.validated_data["accepted"]

            if accepted:
                challenge.participants.add(user)
                challenge.save()

                # WebSocket을 통해 챌린지 상태 업데이트
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f"challenge_{challenge.id}",
                    {
                        "type": "challenge.update",
                        "message": {"status": "accepted", "user_id": user.id},
                    },
                )

                return Response({"message": "챌린지 참가 완료"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "챌린지 참가 거절"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(description="챌린지 진행 로그 조회")
    @action(detail=False, methods=["get"], url_path="log")
    def log(self, request):
        queryset = Challenge.objects.filter(status__in=["ongoing", "completed"])
        serializer = ChallengeLogSerializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(description="특정 챌린지 최종 결과 조회")
    @action(detail=True, methods=["get"], url_path="result")
    def result(self, request, pk=None):
        challenge = self.get_object()
        serializer = ChallengeResultSerializer(challenge)
        return Response(serializer.data)
