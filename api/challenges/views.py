from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import User

from .models import Challenge
from .serializers import (
    ChallengeCreateSerializer,
    ChallengeLogSerializer,
    ChallengeResponseSerializer,
    ChallengeSerializer,
)


class ChallengeCreateView(CreateAPIView):
    queryset = Challenge.objects.all()
    serializer_class = ChallengeCreateSerializer

    @extend_schema(
        summary="챌린지 생성",
        description="챌린지를 생성하면서 참가자를 선택하고 WebSocket을 통해 자동 요청을 전송합니다.",
        request=ChallengeCreateSerializer,
        responses={201: ChallengeSerializer},
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_ids = serializer.validated_data.pop("user_ids")
        request_user = request.user  # 챌린지 생성자

        challenge = serializer.save()
        challenge.participants.add(request_user)

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


class ChallengeResponseView(APIView):
    @extend_schema(
        summary="챌린지 응답 (수락/거절)",
        description="참가자가 챌린지 요청을 수락 또는 거절합니다. (WebSocket으로 알림 전송)",
        request=ChallengeResponseSerializer,
        responses={200: OpenApiResponse(description="응답 완료")},
        parameters=[
            OpenApiParameter(
                name="id",
                location=OpenApiParameter.PATH,
                description="챌린지 ID",
                required=True,
                type=int,
            )
        ],
    )
    def put(self, request, pk, *args, **kwargs):
        challenge = get_object_or_404(Challenge, pk=pk)
        serializer = ChallengeResponseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        accepted = serializer.validated_data["accepted"]

        if accepted:
            challenge.participants.add(user)
            challenge.save()

            # WebSocket을 통해 참가 확정 알림 전송
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


class ChallengeLogView(ListAPIView):
    queryset = Challenge.objects.filter(status__in=["ongoing", "completed"])
    serializer_class = ChallengeLogSerializer

    @extend_schema(
        summary="챌린지 로그 조회",
        description="현재 진행 중인 챌린지의 로그를 조회합니다.",
        responses={200: ChallengeLogSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


from rest_framework.generics import RetrieveAPIView

from .serializers import ChallengeResultSerializer


class ChallengeResultView(RetrieveAPIView):
    queryset = Challenge.objects.all()
    serializer_class = ChallengeResultSerializer

    @extend_schema(
        summary="챌린지 결과 조회",
        description="특정 챌린지의 최종 결과를 조회합니다.",
        parameters=[
            OpenApiParameter(
                name="id",
                location=OpenApiParameter.PATH,
                description="챌린지 ID",
                required=True,
                type=int,
            )
        ],
        responses={200: ChallengeResultSerializer},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


from rest_framework.generics import DestroyAPIView


class ChallengeDeleteView(DestroyAPIView):
    queryset = Challenge.objects.all()
    serializer_class = ChallengeSerializer

    @extend_schema(
        summary="챌린지 삭제",
        description="진행 중이지 않은 챌린지를 삭제합니다.",
        parameters=[
            OpenApiParameter(
                name="id",
                location=OpenApiParameter.PATH,
                description="챌린지 ID",
                required=True,
                type=int,
            )
        ],
        responses={204: OpenApiResponse(description="삭제 완료")},
    )
    def delete(self, request, *args, **kwargs):
        challenge = self.get_object()
        if challenge.status == "ongoing":
            return Response(
                {"error": "진행 중인 챌린지는 삭제할 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST
            )
        return super().delete(request, *args, **kwargs)
