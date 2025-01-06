from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
    extend_schema_view,
)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Challenge, ChallengeStatus
from .serializers import (
    ChallengeCreateSerializer,
    ChallengeLogSerializer,
    ChallengeRequestSerializer,
    ChallengeResponseSerializer,
    ChallengeResultSerializer,
    ChallengeSerializer,
)


@extend_schema_view(
    list=extend_schema(description="수신/발신 챌린지 요청 리스트 조회"),
    create=extend_schema(description="새로운 챌린지 생성"),
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

    # 챌린지 삭제(진행중은 예외처리)
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status == ChallengeStatus.ONGOING.value:
            return Response(
                {"error": "진행 중인 챌린지는 삭제할 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        request=ChallengeRequestSerializer,
        responses={200: {"message": "챌린지 요청 완료"}},
        description="다른 유저에게 챌린지를 신청",
    )
    @action(detail=False, methods=["post"], url_path="request/(?P<user_id>[^/.]+)")
    def challenge_request(self, request, user_id):
        serializer = ChallengeRequestSerializer(data=request.data)
        if serializer.is_valid():
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"user_{user_id}",
                {
                    "type": "challenge.request",
                    "message": {"text": "새로운 챌린지 요청이 도착했습니다!"},
                },
            )
            return Response({"message": "챌린지 요청 완료"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
            accepted = serializer.validated_data["accepted"]

            if accepted:
                challenge.status = ChallengeStatus.ONGOING.value
                challenge.save()

                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f"challenge_{challenge.id}",
                    {"type": "challenge.start", "message": {"text": "챌린지가 시작되었습니다!"}},
                )
                return Response({"message": "챌린지 수락"}, status=status.HTTP_200_OK)
            else:
                challenge.status = ChallengeStatus.REJECTED.value
                challenge.save()
                return Response({"message": "챌린지 거절"}, status=status.HTTP_200_OK)

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
