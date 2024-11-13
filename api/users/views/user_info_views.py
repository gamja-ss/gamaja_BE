from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions
from rest_framework.response import Response
from users.serializers.info_serializer import ProgrammersInfoSerializer


class ProgrammersInfoView(generics.RetrieveUpdateAPIView):
    serializer_class = ProgrammersInfoSerializer
    permission_classes = [permissions.IsAuthenticated]

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
