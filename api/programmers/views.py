from django.shortcuts import render

# Create your views here.
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

from .models import Programmers
from .serializers import (
    ProgrammersDateRequestSerializer,
    ProgrammersPeriodRequestSerializer,
    ProgrammersSerializer,
)
from .utils import get_programmers_data


class UpdateProgrammersInfoView(generics.GenericAPIView):
    serializer_class = ProgrammersSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["programmers"],
        summary="프로그래머스 정보 업데이트(백엔드 서버용)",
        description="현재 사용자의 프로그래머스 정보를 업데이트합니다.",
        responses={
            200: OpenApiResponse(
                response=ProgrammersSerializer,
                description="프로그래머스 정보가 성공적으로 업데이트되었습니다.",
            ),
            400: OpenApiResponse(
                description="프로그래머스 계정 정보가 설정되지 않았거나 정보를 가져오는데 실패했습니다."
            ),
        },
    )
    def post(self, request):
        user = request.user
        if not user.programmers_id or not user.programmers_password:
            return Response(
                {"error": "프로그래머스 계정 정보가 설정되지 않았습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        programmers_data = get_programmers_data(
            user.programmers_id, user.programmers_password
        )
        if not programmers_data:
            return Response(
                {"error": "프로그래머스 정보를 가져오는데 실패했습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        programmers, created = Programmers.objects.update_or_create(
            user=user,
            defaults={
                "level": programmers_data["level"],
                "score": programmers_data["score"],
                "solved": programmers_data["solved"],
                "rank": programmers_data["rank"],
                "date": timezone.now().date(),
            },
        )

        serializer = self.get_serializer(programmers)
        return Response(
            {
                "message": "프로그래머스 정보가 성공적으로 업데이트되었습니다.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class GetTotalProgrammersInfoView(generics.GenericAPIView):
    serializer_class = ProgrammersSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["programmers"],
        summary="프로그래머스 전체 정보 조회",
        description="현재 사용자의 오늘 날짜 기준 프로그래머스 전체 정보를 조회합니다.",
        responses={
            200: OpenApiResponse(
                response=ProgrammersSerializer,
                description="성공적으로 정보를 조회했습니다.",
            ),
            404: OpenApiResponse(
                description="오늘 날짜의 프로그래머스 정보가 없습니다."
            ),
        },
    )
    def get(self, request):
        today = timezone.now().date()
        try:
            programmer_info = Programmers.objects.get(user=request.user, date=today)
            serializer = self.get_serializer(programmer_info)
            return Response(serializer.data)
        except Programmers.DoesNotExist:
            return Response(
                {"error": "오늘 날짜의 프로그래머스 정보가 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )


class GetTodayProgrammersSolvedView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        methods=["GET"],
        tags=["programmers"],
        summary="오늘의 프로그래머스 푼 문제 수 조회",
        description="오늘의 프로그래머스 푼 문제 수를 조회합니다",
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.INT,
                description="오늘의 프로그래머스 푼 문제 수",
                examples=[
                    OpenApiExample(
                        "Success Response",
                        value={"today_solved": 5},
                        response_only=True,
                    )
                ],
            ),
            404: OpenApiResponse(description="오늘의 프로그래머스 정보가 없습니다"),
        },
    )
    def get(self, request):
        user = request.user
        today = timezone.now().date()

        try:
            today_record = Programmers.objects.get(user=user, date=today)

            if today == user.programmers_initial_date:
                today_solved = today_record.solved - user.programmers_initial_solved
            else:
                yesterday = today - timezone.timedelta(days=1)
                yesterday_record = Programmers.objects.get(user=user, date=yesterday)
                today_solved = today_record.solved - yesterday_record.solved

            return Response({"today_solved": today_solved})
        except Programmers.DoesNotExist:
            return Response(
                {"error": "오늘의 프로그래머스 정보가 없습니다"},
                status=status.HTTP_404_NOT_FOUND,
            )


class GetTodayProgrammersScoreView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        methods=["GET"],
        tags=["programmers"],
        summary="오늘의 프로그래머스 점수 조회",
        description="오늘의 프로그래머스 점수를 조회합니다",
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.INT,
                description="오늘의 프로그래머스 점수",
                examples=[
                    OpenApiExample(
                        "Success Response",
                        value={"today_score": 5},
                        response_only=True,
                    )
                ],
            ),
            404: OpenApiResponse(description="오늘의 프로그래머스 정보가 없습니다"),
        },
    )
    def get(self, request):
        user = request.user
        today = timezone.now().date()

        try:
            today_record = Programmers.objects.get(user=user, date=today)

            if today == user.programmers_initial_date:
                today_score = today_record.score - user.programmers_initial_score
            else:
                yesterday = today - timezone.timedelta(days=1)
                yesterday_record = Programmers.objects.get(user=user, date=yesterday)
                today_score = today_record.score - yesterday_record.score

            return Response({"today_score": today_score})
        except Programmers.DoesNotExist:
            return Response(
                {"error": "오늘의 프로그래머스 정보가 없습니다"},
                status=status.HTTP_404_NOT_FOUND,
            )


class GetDateProgrammersSolvedView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProgrammersDateRequestSerializer

    @extend_schema(
        methods=["GET"],
        tags=["programmers"],
        summary="특정 날짜의 프로그래머스 푼 문제 수 조회",
        description="특정 날짜의 프로그래머스 푼 문제 수를 조회합니다",
        request=ProgrammersDateRequestSerializer,
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.INT,
                description="특정 날짜의 프로그래머스 푼 문제 수",
                examples=[
                    OpenApiExample(
                        "Success Response",
                        value={"date_solved": 5},
                        response_only=True,
                    )
                ],
            ),
            404: OpenApiResponse(
                description="해당 날짜의 프로그래머스 정보가 없습니다"
            ),
        },
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        date = serializer.validated_data["date"]

        try:
            date_record = Programmers.objects.get(user=user, date=date)

            if date == user.programmers_initial_date:
                date_solved = date_record.solved - user.programmers_initial_solved
            else:
                previous_date = date - timezone.timedelta(days=1)
                previous_date_record = Programmers.objects.get(
                    user=user, date=previous_date
                )
                date_solved = date_record.solved - previous_date_record.solved

            return Response({"date_solved": date_solved})

        except Programmers.DoesNotExist:
            return Response(
                {"error": "해당 날짜의 프로그래머스 정보가 없습니다"},
                status=status.HTTP_404_NOT_FOUND,
            )


class GetDateProgrammersScoreView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProgrammersDateRequestSerializer

    @extend_schema(
        methods=["POST"],
        tags=["programmers"],
        summary="특정 날짜의 프로그래머스 점수 조회",
        description="특정 날짜의 프로그래머스 점수를 조회합니다",
        request=ProgrammersDateRequestSerializer,
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.INT,
                description="특정 날짜의 프로그래머스 점수",
                examples=[
                    OpenApiExample(
                        "Success Response",
                        value={"today_score": 5},
                        response_only=True,
                    )
                ],
            ),
            404: OpenApiResponse(
                description="해당 날짜의 프로그래머스 정보가 없습니다"
            ),
        },
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        date = serializer.validated_data["date"]

        try:
            date_record = Programmers.objects.get(user=user, date=date)

            if date == user.programmers_initial_date:
                date_score = date_record.score - user.programmers_initial_score
            else:
                previous_date = date - timezone.timedelta(days=1)
                previous_date_record = Programmers.objects.get(
                    user=user, date=previous_date
                )
                date_score = date_record.score - previous_date_record.score

            return Response({"date_score": date_score})

        except Programmers.DoesNotExist:
            return Response(
                {"error": "해당 날짜의 백준 정보가 없습니다"},
                status=status.HTTP_404_NOT_FOUND,
            )


class GetPeriodProgrammersSolvedView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProgrammersPeriodRequestSerializer

    @extend_schema(
        methods=["POST"],
        tags=["programmers"],
        summary="특정 기간의 프로그래머스 푼 문제 수 조회",
        description="지정된 시작일부터 종료일까지의 프로그래머스 푼 문제 수를 조회합니다",
        request=ProgrammersPeriodRequestSerializer,
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.INT,
                description="특정 기간의 프로그래머스 푼 문제 수",
                examples=[
                    OpenApiExample(
                        "Success Response",
                        value={"period_solved": 5},
                        response_only=True,
                    )
                ],
            ),
            404: OpenApiResponse(
                description="해당 기간의 프로그래머스 정보가 없습니다"
            ),
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
            end_record = Programmers.objects.get(user=user, date=end_date)

            if start_date == user.programmers_initial_date:
                period_solved = end_record.solved - user.programmers_initial_solved
            else:
                start_record = Programmers.objects.get(user=user, date=start_date)
                period_solved = end_record.solved - start_record.solved

            return Response({"period_solved": period_solved})

        except Programmers.DoesNotExist:
            return Response(
                {"error": "해당 기간의 프로그래머스 정보가 없습니다"},
                status=status.HTTP_404_NOT_FOUND,
            )


class GetPeriodProgrammersScoreView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProgrammersPeriodRequestSerializer

    @extend_schema(
        methods=["POST"],
        tags=["programmers"],
        summary="특정 기간의 프로그래머스 점수 조회",
        description="지정된 시작일부터 종료일까지의 프로그래머스 점수를 조회합니다",
        request=ProgrammersPeriodRequestSerializer,
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.INT,
                description="특정 기간의 프로그래머스 점수",
                examples=[
                    OpenApiExample(
                        "Success Response",
                        value={"today_score": 5},
                        response_only=True,
                    )
                ],
            ),
            404: OpenApiResponse(
                description="해당 기간의 프로그래머스 정보가 없습니다"
            ),
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
            end_record = Programmers.objects.get(user=user, date=end_date)

            if start_date == user.programmers_initial_date:
                period_score = end_record.score - user.programmers_initial_score
            else:
                start_record = Programmers.objects.get(user=user, date=start_date)
                period_score = end_record.score - start_record.score

            return Response({"period_score": period_score})

        except Programmers.DoesNotExist:
            return Response(
                {"error": "해당 기간의 프로그래머스 정보가 없습니다"},
                status=status.HTTP_404_NOT_FOUND,
            )
