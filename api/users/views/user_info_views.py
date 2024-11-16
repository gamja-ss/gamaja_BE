from baekjoons.utils import get_boj_profile
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.serializers.info_serializer import (
    BaekjoonInfoSerializer,
    ProgrammersInfoSerializer,
)


class ProgrammersInfo(generics.RetrieveUpdateAPIView):
    serializer_class = ProgrammersInfoSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    @extend_schema(
        methods=["GET"],
        tags=["info"],
        summary="프로그래머스 정보 조회",
        description="사용자의 프로그래머스 아이디를 조회합니다.",
        responses={200: ProgrammersInfoSerializer},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        methods=["PUT"],
        tags=["info"],
        summary="프로그래머스 정보 업데이트",
        description="사용자의 프로그래머스 아이디와 비밀번호를 업데이트합니다.",
        request=ProgrammersInfoSerializer,
        responses={200: ProgrammersInfoSerializer},
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        methods=["PATCH"],
        tags=["info"],
        summary="프로그래머스 정보 부분 업데이트",
        description="사용자의 프로그래머스 아이디 또는 비밀번호를 부분적으로 업데이트합니다.",
        request=ProgrammersInfoSerializer,
        responses={200: ProgrammersInfoSerializer},
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class BaekjoonInfo(generics.GenericAPIView):
    serializer_class = BaekjoonInfoSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "put"]

    def get_object(self):
        return self.request.user

    @extend_schema(
        methods=["GET"],
        tags=["info"],
        summary="백준 정보 조회",
        description="사용자의 백준 아이디를 조회합니다.",
        responses={200: ProgrammersInfoSerializer},
    )
    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @extend_schema(
        methods=["PUT"],
        tags=["info"],
        summary="백준 정보 업데이트",
        description="사용자의 백준 아이디를 업데이트합니다.",
        request=BaekjoonInfoSerializer,
        responses={200: BaekjoonInfoSerializer},
    )
    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class VerifyBaekjoonAccount(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BaekjoonInfoSerializer

    @extend_schema(
        methods=["POST"],
        tags=["info"],
        summary="백준 계정 검증",
        description="제공된 백준 아이디를 검증하고, bio가 'gamjass_{username}'과 일치하는지 확인합니다.",
        request=BaekjoonInfoSerializer,
        responses={
            200: OpenApiResponse(description="계정 검증 성공"),
            400: OpenApiResponse(description="계정 검증 실패 또는 잘못된 요청"),
            404: OpenApiResponse(description="백준 계정을 찾을 수 없음"),
        },
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        baekjoon_id = serializer.validated_data["baekjoon_id"]
        profile = get_boj_profile(baekjoon_id)
        if profile is None:
            return Response(
                {"error": "백준 계정을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        expected_bio = f"gamjass_{request.user.username}"
        print(f"1:{expected_bio}, 2:{profile["bio"]}")
        if profile["bio"] == expected_bio:
            return Response(
                {"message": "백준 계정이 성공적으로 검증되었습니다."},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "계정 검증에 실패했습니다. bio를 확인해주세요."},
                status=status.HTTP_400_BAD_REQUEST,
            )
