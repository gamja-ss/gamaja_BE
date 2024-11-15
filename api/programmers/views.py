from django.shortcuts import render

# Create your views here.
from django.utils import timezone
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
)
from rest_framework import generics, serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Programmers
from .serializers import ProgrammersSerializer
from .utils import get_programmers_data


class UpdateProgrammersInfo(generics.GenericAPIView):
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
                "solved_tests": programmers_data["solved_tests"],
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


class GetTotalProgrammersInfo(generics.GenericAPIView):
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


class GetTodayProgrammersST(generics.RetrieveAPIView):
    serializer_class = ProgrammersSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        methods=["GET"],
        tags=["programmers"],
        summary="오늘의 프로그래머스 푼 문제 수 조회",
        description="오늘의 프로그래머스 푼 문제 수를 조회합니다",
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer(
                    {"today_solved_problem": serializers.IntegerField()}
                )
            ),
            404: OpenApiResponse(description="오늘의 프로그래머스 정보가 없습니다"),
        },
    )
    def get(self, request):
        user = request.user
        today = timezone.now().date()
        yesterday = today - timezone.timedelta(days=1)

        try:
            today_record = Programmers.objects.get(user=user, date=today)

            if today == user.programmers_initial_date:
                today_st = (
                    today_record.solved_tests - user.programmers_initial_solved_tests
                )
            else:
                yesterday = today - timezone.timedelta(days=1)
                yesterday_record = Programmers.objects.get(user=user, date=yesterday)
                today_st = today_record.solved_tests - yesterday_record.solved_tests

            return Response({"today_solved_tests": today_st})
        except Programmers.DoesNotExist:
            return Response(
                {"error": "오늘의 프로그래머스 정보가 없습니다"},
                status=status.HTTP_404_NOT_FOUND,
            )


class GetTodayProgrammersScore(generics.RetrieveAPIView):
    serializer_class = ProgrammersSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        methods=["GET"],
        tags=["programmers"],
        summary="오늘의 프로그래머스 점수 조회",
        description="오늘의 프로그래머스 점수를 조회합니다",
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer(
                    {"today_score": serializers.IntegerField()}
                )
            ),
            404: OpenApiResponse(description="오늘의 프로그래머스 정보가 없습니다"),
        },
    )
    def get(self, request):
        user = request.user
        today = timezone.now().date()
        yesterday = today - timezone.timedelta(days=1)

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


class GetDateProgrammersST(generics.RetrieveAPIView):
    serializer_class = ProgrammersSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        methods=["GET"],
        tags=["programmers"],
        summary="특정 날짜의 프로그래머스 푼 문제 수 조회",
        description="특정 날짜의 프로그래머스 푼 문제 수를 조회합니다",
        parameters=[
            OpenApiParameter(
                name="date",
                description="조회할 날짜 (YYYY-MM-DD)",
                required=True,
                type=str,
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer(
                    {"date_solved_tests": serializers.IntegerField()}
                )
            ),
            404: OpenApiResponse(
                description="해당 날짜의 프로그래머스 정보가 없습니다"
            ),
        },
    )
    def get(self, request):
        user = request.user
        date_str = request.query_params.get("date")
        if not date_str:
            return Response(
                {"error": "날짜를 지정해주세요"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            date = timezone.datetime.strptime(date_str, "%Y-%m-%d").date()
            date_record = Programmers.objects.get(user=user, date=date)

            if date == user.programmers_initial_date:
                date_st = (
                    date_record.solved_tests - user.programmers_initial_solved_tests
                )
            else:
                previous_date = date - timezone.timedelta(days=1)
                previous_date_record = Programmers.objects.get(
                    user=user, date=previous_date
                )
                date_st = date_record.solved_tests - previous_date_record.solved_tests

            return Response({"date_solved_problem": date_st})
        except ValueError:
            return Response(
                {"error": "올바른 날짜 형식이 아닙니다"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Programmers.DoesNotExist:
            return Response(
                {"error": "해당 날짜의 프로그래머스 정보가 없습니다"},
                status=status.HTTP_404_NOT_FOUND,
            )


class GetDateProgrammersScore(generics.RetrieveAPIView):
    serializer_class = ProgrammersSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        methods=["GET"],
        tags=["programmers"],
        summary="특정 날짜의 프로그래머스 점수 조회",
        description="특정 날짜의 프로그래머스 점수를 조회합니다",
        parameters=[
            OpenApiParameter(
                name="date",
                description="조회할 날짜 (YYYY-MM-DD)",
                required=True,
                type=str,
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer(
                    {"date_score": serializers.IntegerField()}
                )
            ),
            404: OpenApiResponse(
                description="해당 날짜의 프로그래머스 정보가 없습니다"
            ),
        },
    )
    def get(self, request):
        user = request.user
        date_str = request.query_params.get("date")
        if not date_str:
            return Response(
                {"error": "날짜를 지정해주세요"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            date = timezone.datetime.strptime(date_str, "%Y-%m-%d").date()
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
        except ValueError:
            return Response(
                {"error": "올바른 날짜 형식이 아닙니다"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Programmers.DoesNotExist:
            return Response(
                {"error": "해당 날짜의 백준 정보가 없습니다"},
                status=status.HTTP_404_NOT_FOUND,
            )


class GetPeriodProgrammersST(generics.RetrieveAPIView):
    serializer_class = ProgrammersSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        methods=["GET"],
        tags=["programmers"],
        summary="특정 기간의 프로그래머스 푼 문제 수 조회",
        description="지정된 시작일부터 종료일까지의 프로그래머스 푼 문제 수를 조회합니다",
        parameters=[
            OpenApiParameter(
                name="start_date",
                description="시작 날짜 (YYYY-MM-DD)",
                required=True,
                type=str,
            ),
            OpenApiParameter(
                name="end_date",
                description="종료 날짜 (YYYY-MM-DD)",
                required=True,
                type=str,
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer(
                    {"period_solved_tests": serializers.IntegerField()}
                )
            ),
            404: OpenApiResponse(
                description="해당 기간의 프로그래머스 정보가 없습니다"
            ),
        },
    )
    def get(self, request):
        user = request.user
        start_date_str = request.query_params.get("start_date")
        end_date_str = request.query_params.get("end_date")

        if not start_date_str or not end_date_str:
            return Response(
                {"error": "시작일과 종료일을 모두 지정해주세요"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            start_date = timezone.datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = timezone.datetime.strptime(end_date_str, "%Y-%m-%d").date()

            if start_date > end_date:
                return Response(
                    {"error": "시작일이 종료일보다 늦을 수 없습니다"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            end_record = Programmers.objects.get(user=user, date=end_date)

            if start_date == user.programmers_initial_date:
                period_st = (
                    end_record.solved_tests - user.programmers_initial_solved_tests
                )
            else:
                start_record = Programmers.objects.get(user=user, date=start_date)
                period_st = end_record.solved_tests - start_record.solved_tests

            return Response({"period_solved_tests": period_st})
        except ValueError:
            return Response(
                {"error": "올바른 날짜 형식이 아닙니다"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Programmers.DoesNotExist:
            return Response(
                {"error": "해당 기간의 프로그래머스 정보가 없습니다"},
                status=status.HTTP_404_NOT_FOUND,
            )


class GetPeriodProgrammersScore(generics.RetrieveAPIView):
    serializer_class = ProgrammersSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        methods=["GET"],
        tags=["programmers"],
        summary="특정 기간의 프로그래머스 점수 조회",
        description="지정된 시작일부터 종료일까지의 프로그래머스 점수를 조회합니다",
        parameters=[
            OpenApiParameter(
                name="start_date",
                description="시작 날짜 (YYYY-MM-DD)",
                required=True,
                type=str,
            ),
            OpenApiParameter(
                name="end_date",
                description="종료 날짜 (YYYY-MM-DD)",
                required=True,
                type=str,
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=serializers.Serializer(
                    {"period_score": serializers.IntegerField()}
                )
            ),
            404: OpenApiResponse(
                description="해당 기간의 프로그래머스 정보가 없습니다"
            ),
        },
    )
    def get(self, request):
        user = request.user
        start_date_str = request.query_params.get("start_date")
        end_date_str = request.query_params.get("end_date")

        if not start_date_str or not end_date_str:
            return Response(
                {"error": "시작일과 종료일을 모두 지정해주세요"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            start_date = timezone.datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = timezone.datetime.strptime(end_date_str, "%Y-%m-%d").date()

            if start_date > end_date:
                return Response(
                    {"error": "시작일이 종료일보다 늦을 수 없습니다"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            end_record = Programmers.objects.get(user=user, date=end_date)

            if start_date == user.programmers_initial_date:
                period_score = end_record.score - user.programmers_initial_score
            else:
                start_record = Programmers.objects.get(user=user, date=start_date)
                period_score = end_record.score - start_record.score

            return Response({"period_score": period_score})
        except ValueError:
            return Response(
                {"error": "올바른 날짜 형식이 아닙니다"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Programmers.DoesNotExist:
            return Response(
                {"error": "해당 기간의 프로그래머스 정보가 없습니다"},
                status=status.HTTP_404_NOT_FOUND,
            )
