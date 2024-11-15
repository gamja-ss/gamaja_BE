from django.utils import timezone
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
)
from rest_framework import generics, serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Baekjoon
from .serializers import BaekjoonSerializer
from .utils import get_boj_profile


class UpdateBaekjoonInfo(generics.GenericAPIView):
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
                "solved_problem": profile["solved_count"],
                "score": profile["rating"],
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


class GetTotalBaekjoonInfo(generics.GenericAPIView):
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


class GetTodayBaekjoonSP(generics.RetrieveAPIView):
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
                        value={"today_solved_problem": 5},
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
                today_sp = (
                    today_record.solved_problem - user.baekjoon_initial_solved_problem
                )
            else:
                yesterday = today - timezone.timedelta(days=1)
                yesterday_record = Baekjoon.objects.get(user=user, date=yesterday)
                today_sp = today_record.solved_problem - yesterday_record.solved_problem

            return Response({"today_solved_problem": today_sp})
        except Baekjoon.DoesNotExist:
            return Response(
                {"error": "오늘의 백준 정보가 없습니다"},
                status=status.HTTP_404_NOT_FOUND,
            )


class GetTodayBaekjoonScore(generics.RetrieveAPIView):
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


class GetDateBaekjoonSP(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        methods=["GET"],
        tags=["baekjoon"],
        summary="특정 날짜의 백준 푼 문제 수 조회",
        description="특정 날짜의 백준 푼 문제 수를 조회합니다",
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
                response=OpenApiTypes.INT,
                description="특정 날짜의 백준 푼 문제 수",
                examples=[
                    OpenApiExample(
                        "Success Response",
                        value={"date_solved_problem": 5},
                        response_only=True,
                    )
                ],
            ),
            404: OpenApiResponse(description="해당 날짜의 백준 정보가 없습니다"),
        },
    )
    def get(self, request):
        user = request.user
        date_str = request.query_params.get("date")
        if not date_str:
            return Response({"error": "날짜를 지정해주세요"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            date = timezone.datetime.strptime(date_str, "%Y-%m-%d").date()
            date_record = Baekjoon.objects.get(user=user, date=date)

            if date == user.baekjoon_initial_date:
                date_sp = (
                    date_record.solved_problem - user.baekjoon_initial_solved_problem
                )
            else:
                previous_date = date - timezone.timedelta(days=1)
                previous_date_record = Baekjoon.objects.get(
                    user=user, date=previous_date
                )
                date_sp = (
                    date_record.solved_problem - previous_date_record.solved_problem
                )

            return Response({"date_solved_problem": date_sp})
        except ValueError:
            return Response(
                {"error": "올바른 날짜 형식이 아닙니다"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Baekjoon.DoesNotExist:
            return Response(
                {"error": "해당 날짜의 백준 정보가 없습니다"},
                status=status.HTTP_404_NOT_FOUND,
            )


class GetDateBaekjoonScore(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        methods=["GET"],
        tags=["baekjoon"],
        summary="특정 날짜의 백준 점수 조회",
        description="특정 날짜의 백준 점수를 조회합니다",
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
    def get(self, request):
        user = request.user
        date_str = request.query_params.get("date")
        if not date_str:
            return Response({"error": "날짜를 지정해주세요"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            date = timezone.datetime.strptime(date_str, "%Y-%m-%d").date()
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
        except ValueError:
            return Response(
                {"error": "올바른 날짜 형식이 아닙니다"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Baekjoon.DoesNotExist:
            return Response(
                {"error": "해당 날짜의 백준 정보가 없습니다"},
                status=status.HTTP_404_NOT_FOUND,
            )


class GetPeriodBaekjoonSP(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        methods=["GET"],
        tags=["baekjoon"],
        summary="특정 기간의 백준 푼 문제 수 조회",
        description="지정된 시작일부터 종료일까지의 백준 푼 문제 수를 조회합니다",
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
                response=OpenApiTypes.INT,
                description="오늘의 백준 푼 문제 수",
                examples=[
                    OpenApiExample(
                        "Success Response",
                        value={"period_solved_problem": 5},
                        response_only=True,
                    )
                ],
            ),
            404: OpenApiResponse(description="해당 기간의 백준 정보가 없습니다"),
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

            end_record = Baekjoon.objects.get(user=user, date=end_date)

            if start_date == user.baekjoon_initial_date:
                period_sp = (
                    end_record.solved_problem - user.baekjoon_initial_solved_problem
                )
            else:
                start_record = Baekjoon.objects.get(user=user, date=start_date)
                period_sp = end_record.solved_problem - start_record.solved_problem

            return Response({"period_solved_problem": period_sp})
        except ValueError:
            return Response(
                {"error": "올바른 날짜 형식이 아닙니다"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Baekjoon.DoesNotExist:
            return Response(
                {"error": "해당 기간의 백준 정보가 없습니다"},
                status=status.HTTP_404_NOT_FOUND,
            )


class GetPeriodBaekjoonScore(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        methods=["GET"],
        tags=["baekjoon"],
        summary="특정 기간의 백준 점수 조회",
        description="지정된 시작일부터 종료일까지의 백준 점수를 조회합니다",
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

            end_record = Baekjoon.objects.get(user=user, date=end_date)

            if start_date == user.baekjoon_initial_date:
                period_score = end_record.score - user.baekjoon_initial_score
            else:
                start_record = Baekjoon.objects.get(user=user, date=start_date)
                period_score = end_record.score - start_record.score

            return Response({"period_score": period_score})
        except ValueError:
            return Response(
                {"error": "올바른 날짜 형식이 아닙니다"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Baekjoon.DoesNotExist:
            return Response(
                {"error": "해당 기간의 백준 정보가 없습니다"},
                status=status.HTTP_404_NOT_FOUND,
            )
