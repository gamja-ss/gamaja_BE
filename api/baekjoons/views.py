from django.utils import timezone
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
)
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Baekjoon
from .serializers import (
    BaekjoonDateRequestSerializer,
    BaekjoonPeriodRequestSerializer,
    BaekjoonSerializer,
)
from .utils import get_boj_profile


class UpdateBaekjoonInfoView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BaekjoonSerializer

    @extend_schema(
        methods=["POST"],
        tags=["baekjoon"],
        summary="백준 정보 업데이트(백엔드 서버용)",
        description="사용자의 백준 문제 풀이 정보를 업데이트합니다",
        responses={
            200: OpenApiResponse(
                description="백준 정보가 성공적으로 업데이트되었습니다",
                response=BaekjoonSerializer,
            ),
            400: OpenApiResponse(description="백준 ID가 설정되지 않았습니다"),
            404: OpenApiResponse(description="백준 정보를 가져오는데 실패했습니다"),
        },
    )
    def post(self, request):
        user = request.user
        bj_id = user.baekjoon_id

        if not bj_id:
            return Response(
                {"error": "백준 ID가 설정되지 않았습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        profile = get_boj_profile(bj_id)
        if not profile:
            return Response(
                {"error": "백준 정보를 가져오는데 실패했습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        baekjoon, created = Baekjoon.objects.update_or_create(
            user=user,
            date=timezone.now().date(),
            defaults={
                "solved": profile["solved"],
                "score": profile["score"],
                "tier": profile["tier"],
            },
        )

        serializer = self.get_serializer(baekjoon)
        return Response(
            {
                "message": "백준 정보가 성공적으로 업데이트되었습니다.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class GetTotalBaekjoonInfoView(generics.GenericAPIView):
    serializer_class = BaekjoonSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        methods=["GET"],
        tags=["baekjoon"],
        summary="백준 전체 정보 조회",
        description="현재 사용자의 오늘 날짜 기준 전체 백준 정보를 조회합니다.",
        responses={
            200: OpenApiResponse(
                response=BaekjoonSerializer,
                description="성공적으로 정보를 조회했습니다.",
            ),
            404: OpenApiResponse(description="오늘 날짜의 백준 정보가 없습니다."),
        },
    )
    def get(self, request):
        today = timezone.now().date()
        try:
            baekjoon_info = Baekjoon.objects.get(user=request.user, date=today)
            serializer = self.get_serializer(baekjoon_info)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Baekjoon.DoesNotExist:
            return Response(
                {"error": "오늘 날짜의 백준 정보가 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )


class GetTodayBaekjoonSolvedView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        methods=["GET"],
        tags=["baekjoon"],
        summary="오늘의 백준 푼 문제 수 조회",
        description="오늘의 백준 푼 문제 수를 조회합니다",
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.INT,
                description="오늘의 백준 푼 문제 수",
                examples=[
                    OpenApiExample(
                        "Success Response",
                        value={"today_solved": 5},
                        response_only=True,
                    )
                ],
            ),
            404: OpenApiResponse(description="오늘의 백준 정보가 없습니다"),
        },
    )
    def get(self, request):
        user = request.user
        today = timezone.now().date()

        try:
            today_record = Baekjoon.objects.get(user=user, date=today)

            if today == user.baekjoon_initial_date:
                today_solved = today_record.solved - user.baekjoon_initial_solved
            else:
                yesterday = today - timezone.timedelta(days=1)
                yesterday_record = Baekjoon.objects.get(user=user, date=yesterday)
                today_solved = today_record.solved - yesterday_record.solved

            return Response({"today_solved": today_solved})
        except Baekjoon.DoesNotExist:
            return Response(
                {"error": "오늘의 백준 정보가 없습니다"},
                status=status.HTTP_404_NOT_FOUND,
            )


class GetTodayBaekjoonScoreView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        methods=["GET"],
        tags=["baekjoon"],
        summary="오늘의 백준 점수 조회",
        description="오늘의 백준 점수를 조회합니다",
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.INT,
                description="오늘의 백준 점수",
                examples=[
                    OpenApiExample(
                        "Success Response",
                        value={"today_score": 5},
                        response_only=True,
                    )
                ],
            ),
            404: OpenApiResponse(description="오늘의 백준 정보가 없습니다"),
        },
    )
    def get(self, request):
        user = request.user
        today = timezone.now().date()

        try:
            today_record = Baekjoon.objects.get(user=user, date=today)

            if today == user.baekjoon_initial_date:
                today_score = today_record.score - user.baekjoon_initial_score
            else:
                yesterday = today - timezone.timedelta(days=1)
                yesterday_record = Baekjoon.objects.get(user=user, date=yesterday)
                today_score = today_record.score - yesterday_record.score

            return Response({"today_score": today_score})
        except Baekjoon.DoesNotExist:
            return Response(
                {"error": "오늘의 백준 정보가 없습니다"},
                status=status.HTTP_404_NOT_FOUND,
            )


class GetDateBaekjoonSolvedView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BaekjoonDateRequestSerializer

    @extend_schema(
        methods=["POST"],
        tags=["baekjoon"],
        summary="특정 날짜의 백준 푼 문제 수 조회",
        description="특정 날짜의 백준 푼 문제 수를 조회합니다",
        request=BaekjoonDateRequestSerializer,
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.INT,
                description="특정 날짜의 백준 푼 문제 수",
                examples=[
                    OpenApiExample(
                        "Success Response",
                        value={"date_solved": 5},
                        response_only=True,
                    )
                ],
            ),
            404: OpenApiResponse(description="해당 날짜의 백준 정보가 없습니다"),
        },
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        date = serializer.validated_data["date"]

        try:
            date_record = Baekjoon.objects.get(user=user, date=date)

            if date == user.baekjoon_initial_date:
                date_solved = date_record.solved - user.baekjoon_initial_solved
            else:
                previous_date = date - timezone.timedelta(days=1)
                previous_date_record = Baekjoon.objects.get(
                    user=user, date=previous_date
                )
                date_solved = date_record.solved - previous_date_record.solved

            return Response({"date_solved": date_solved})

        except Baekjoon.DoesNotExist:
            return Response(
                {"error": "해당 날짜의 백준 정보가 없습니다"},
                status=status.HTTP_404_NOT_FOUND,
            )


class GetDateBaekjoonScoreView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BaekjoonDateRequestSerializer

    @extend_schema(
        methods=["POST"],
        tags=["baekjoon"],
        summary="특정 날짜의 백준 점수 조회",
        description="특정 날짜의 백준 점수를 조회합니다",
        request=BaekjoonDateRequestSerializer,
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.INT,
                description="특정 날짜의 백준 점수",
                examples=[
                    OpenApiExample(
                        "Success Response",
                        value={"date_score": 5},
                        response_only=True,
                    )
                ],
            ),
            404: OpenApiResponse(description="해당 날짜의 백준 정보가 없습니다"),
        },
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        date = serializer.validated_data["date"]


        try:
            date_record = Baekjoon.objects.get(user=user, date=date)

            if date == user.baekjoon_initial_date:
                date_score = date_record.score - user.baekjoon_initial_score
            else:
                previous_date = date - timezone.timedelta(days=1)
                previous_date_record = Baekjoon.objects.get(
                    user=user, date=previous_date
                )
                date_score = date_record.score - previous_date_record.score

            return Response({"date_score": date_score})

        except Baekjoon.DoesNotExist:
            return Response(
                {"error": "해당 날짜의 백준 정보가 없습니다"},
                status=status.HTTP_404_NOT_FOUND,
            )


class GetPeriodBaekjoonSolvedView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BaekjoonPeriodRequestSerializer

    @extend_schema(
        methods=["POST"],
        tags=["baekjoon"],
        summary="특정 기간의 백준 푼 문제 수 조회",
        description="지정된 시작일부터 종료일까지의 백준 푼 문제 수를 조회합니다",
        request=BaekjoonPeriodRequestSerializer,
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.INT,
                description="오늘의 백준 푼 문제 수",
                examples=[
                    OpenApiExample(
                        "Success Response",
                        value={"period_solved": 5},
                        response_only=True,
                    )
                ],
            ),
            404: OpenApiResponse(description="해당 기간의 백준 정보가 없습니다"),
        },
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        start_date = serializer.validated_data["start_date"]
        end_date = serializer.validated_data["end_date"]
        user = request.user

        if start_date > end_date:
            return Response(
                {"error": "시작일이 종료일보다 늦을 수 없습니다"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            end_record = Baekjoon.objects.get(user=user, date=end_date)

            if start_date == user.baekjoon_initial_date:
                period_solved = end_record.solved - user.baekjoon_initial_solved
            else:
                start_record = Baekjoon.objects.get(user=user, date=start_date)
                period_solved = end_record.solved - start_record.solved

            return Response({"period_solved": period_solved})

        except Baekjoon.DoesNotExist:
            return Response(
                {"error": "해당 기간의 백준 정보가 없습니다"},
                status=status.HTTP_404_NOT_FOUND,
            )


class GetPeriodBaekjoonScoreView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BaekjoonPeriodRequestSerializer

    @extend_schema(
        methods=["POST"],
        tags=["baekjoon"],
        summary="특정 기간의 백준 점수 조회",
        description="지정된 시작일부터 종료일까지의 백준 점수를 조회합니다",
        request=BaekjoonPeriodRequestSerializer,
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.INT,
                description="오늘의 백준 점수",
                examples=[
                    OpenApiExample(
                        "Success Response",
                        value={"period_score": 5},
                        response_only=True,
                    )
                ],
            ),
            404: OpenApiResponse(description="해당 기간의 백준 정보가 없습니다"),
        },
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        start_date = serializer.validated_data["start_date"]
        end_date = serializer.validated_data["end_date"]
        user = request.user

        if start_date > end_date:
            return Response(
                {"error": "시작일이 종료일보다 늦을 수 없습니다"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            end_record = Baekjoon.objects.get(user=user, date=end_date)

            if start_date == user.baekjoon_initial_date:
                period_score = end_record.score - user.baekjoon_initial_score
            else:
                start_record = Baekjoon.objects.get(user=user, date=start_date)
                period_score = end_record.score - start_record.score

            return Response({"period_score": period_score})

        except Baekjoon.DoesNotExist:
            return Response(
                {"error": "해당 기간의 백준 정보가 없습니다"},
                status=status.HTTP_404_NOT_FOUND,
            )
