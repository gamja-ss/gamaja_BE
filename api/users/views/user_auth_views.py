import os

import requests
from common.logger import logger
from config.settings import GITHUB_CONFIG
from django.db import transaction
from django.shortcuts import redirect
from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from users.models import User
from users.serializers.auth_serializer import (
    EmptySerializer,
    UserLogoutSerializer,
    UserTokenRefreshSerializer,
)
from users.services import SocialLoginCallbackService, SocialLoginService
from users.utils import GamjaAuthClass


class GithubLogin(generics.GenericAPIView):
    serializer_class = EmptySerializer
    permission_classes = [AllowAny]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gh = SocialLoginService(
            client_id=GITHUB_CONFIG["CLIENT_ID"],
            redirect_uri=GITHUB_CONFIG["REDIRECT_URI"],
            login_uri=GITHUB_CONFIG["LOGIN_URI"],
        )

    @extend_schema(
        methods=["GET"],
        summary="GitHub 로그인 페이지로 리다이렉트(백엔드 개발용)",
        description="사용자를 GitHub OAuth 로그인 페이지로 리다이렉트합니다. 'repo'와 'user:email' 스코프를 요청합니다.",
        tags=["auth"],
    )
    def get(self, request):
        context = {"scope": "repo user:email"}
        return redirect(self.gh.social_login(context))


class GithubLoginCallback(generics.GenericAPIView):
    serializer_class = EmptySerializer
    permission_classes = [AllowAny]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ghc = SocialLoginCallbackService(
            client_id=GITHUB_CONFIG["CLIENT_ID"],
            client_secret=GITHUB_CONFIG["CLIENT_SECRETS"],
            token_uri=GITHUB_CONFIG["TOKEN_URI"],
            profile_uri=GITHUB_CONFIG["PROFILE_URI"],
            redirect_uri=GITHUB_CONFIG["REDIRECT_URI"],
        )

    @extend_schema(
        methods=["POST"],
        tags=["auth"],
        summary="GitHub OAuth 콜백 처리",
        description="GitHub OAuth 인증 후 콜백을 처리합니다. 사용자 정보를 받아 회원가입 또는 로그인을 수행합니다.",
        request=OpenApiTypes.OBJECT,
        responses={
            status.HTTP_200_OK: OpenApiTypes.OBJECT,
            status.HTTP_201_CREATED: OpenApiTypes.OBJECT,
            status.HTTP_400_BAD_REQUEST: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                "Token Request",
                summary="GitHub OAuth Token Request",
                description="Request body for GitHub OAuth token",
                value={"code": "string"},
                request_only=True,
            ),
            OpenApiExample(
                "Successful Login",
                summary="Successful Login Response",
                description="Response for successful login",
                value={
                    "message": "Login successful",
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "user_id": 3,
                    "user_nickname": "gamja",
                },
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                "Successful Signup and Login",
                summary="Successful Signup and Login Response",
                description="Response for successful signup and login",
                value={
                    "message": "Login successful",
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "user_id": 3,
                    "user_username": "gamja",
                    "user_nickname": "gamja",
                },
                response_only=True,
                status_codes=["201"],
            ),
            OpenApiExample(
                "Bad Request",
                summary="Bad Request Response",
                description="Response for bad request",
                value={"error": "Invalid authorization code"},
                response_only=True,
                status_codes=["400"],
            ),
        ],
    )
    def post(self, request):
        token_request_data = self.ghc.create_token_request_data(
            code=request.data.get("code", None)
        )
        try:
            access_token = self.ghc.get_access_token(
                token_request_data=token_request_data
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        auth_headers = {"Authorization": f"Bearer {access_token}"}
        try:
            user_data = self.ghc.get_user_info(auth_headers=auth_headers)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # 사용자 생성/업데이트 및 로그인
        username = user_data.get("login")
        if not username:
            # 깃허브 계정에 username 없는 경우
            return Response(
                {"err_msg": "failed to signup"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(username=username)
            created = False
        except User.DoesNotExist:
            email = user_data.get("email") or None
            user = User.objects.create_user(
                username=username,
                profile_url=user_data.get("avatar_url"),
                github_id=user_data.get("login"),
                nickname=user_data.get("login"),
                email=email,
                github_access_token=access_token,
            )
            created = True

        # 프로필 이미지 업데이트
        # 깃허브 액세스토큰 업데이트
        user.profile_url = user_data.get("avatar_url", user.profile_url)
        user.github_access_token = access_token
        user.last_login = timezone.now()
        user.save()

        jwt_tokens = GamjaAuthClass.set_auth_tokens_for_user(user)

        response_data = {
            "message": "Login successful",
            "access_token": jwt_tokens["access"],
            "user_id": user.id,
            "user_username": user.username,
            "user_nickname": user.nickname,
        }
        response = Response(data=response_data)

        if not created:  # 기존 회원인 경우
            response.status_code = status.HTTP_200_OK
        else:  # 신규 회원인 경우
            response.status_code = status.HTTP_201_CREATED

        response = GamjaAuthClass().set_jwt_auth_cookie(
            response=response, jwt_tokens=jwt_tokens
        )
        logger.info(f"/api/auth/google/receiver: {user}")
        return response


class UserTokenVerifyView(generics.GenericAPIView):
    serializer_class = EmptySerializer
    permission_classes = [AllowAny]

    @extend_schema(
        methods=["POST"],
        tags=["auth"],
        summary="토큰 verify",
        description="액세스 토큰의 유효성을 검증합니다.",
        responses={
            200: OpenApiResponse(description="토큰이 유효함"),
            400: OpenApiResponse(description="쿠키에 액세스 토큰이 없음"),
            401: OpenApiResponse(description="유효하지 않은 토큰"),
        },
    )
    def post(self, request, *args, **kwargs):
        logger.info("POST /api/auth/token/verify")
        token = request.COOKIES.get("gamja_access")
        if not token:
            logger.error("/api/auth/token/verify: Access token not found in cookies")
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            AccessToken(token)
            logger.info("/api/auth/token/verify: Access token is valid")
            return Response(status=status.HTTP_200_OK)
        except (InvalidToken, TokenError):
            logger.error("/api/auth/token/verify: Invalid access token")
            return Response(status=status.HTTP_401_UNAUTHORIZED)


class UserTokenRefreshView(generics.GenericAPIView):
    serializer_class = UserTokenRefreshSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        methods=["POST"],
        tags=["auth"],
        summary="토큰 refresh",
        description="리프레시 토큰을 사용하여 새로운 액세스 토큰을 발급받습니다.",
        request=None,
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="새로운 액세스 토큰 발급 성공",
                examples=[
                    OpenApiExample(
                        "Successful Token Refresh",
                        value={
                            "access": "new_access_token",
                            "message": "Token refreshed successfully",
                        },
                        status_codes=["200"],
                    )
                ],
            ),
            400: OpenApiResponse(description="리프레시 토큰이 쿠키에 없음"),
            401: OpenApiResponse(description="유효하지 않은 리프레시 토큰"),
            500: OpenApiResponse(description="서버 내부 오류"),
        },
    )
    def post(self, request, *args, **kwargs):
        logger.info("POST /api/auth/token/refresh")
        refresh_token = request.COOKIES.get("gamja_refresh")

        if not refresh_token:
            logger.error("/api/auth/token/refresh: Refresh token not found in cookies")
            return Response(
                {"detail": "Refresh token not found in cookies"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data={"refresh_token": refresh_token})
        serializer.is_valid(raise_exception=True)

        try:
            access_token = GamjaAuthClass.new_access_token_for_user(
                refresh_token=serializer.validated_data["refresh_token"]
            )
        except (InvalidToken, TokenError) as e:
            logger.error(f"/api/auth/token/refresh: {e}")
            return Response(
                data={"error occurs": "UserTokenRefreshView", "detail": str(e)},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        response = Response(
            data={"access": access_token, "message": "Token refreshed successfully"}
        )
        try:
            GamjaAuthClass.set_cookie_attributes(
                response=response, key="gamja_access", token=access_token
            )
        except ValueError:
            logger.error("/api/auth/token/refresh: Failed to set access token cookie")
            return Response(
                {"error occurs": "UserTokenRefreshView"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        logger.info("/api/auth/token/refresh: Token refreshed successfully")
        return response


class UserLogoutView(generics.GenericAPIView):
    serializer_class = UserLogoutSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        methods=["POST"],
        tags=["auth"],
        summary="로그아웃",
        description="사용자를 로그아웃 처리하고 토큰을 블랙리스트에 추가합니다.",
        request=None,
        responses={
            200: OpenApiResponse(description="로그아웃 성공"),
            400: OpenApiResponse(description="유효하지 않은 리프레시 토큰"),
            500: OpenApiResponse(description="서버 내부 오류"),
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data={"refresh_token": request.COOKIES.get("gamja_refresh")}
        )
        serializer.is_valid(raise_exception=True)

        try:
            refresh_token = serializer.validated_data["refresh_token"]
            with transaction.atomic():
                refresh_token.blacklist()
            response = Response(status=status.HTTP_200_OK)
            response.delete_cookie(
                "gamja_access", domain=os.getenv("COOKIE_DOMAIN"), path="/"
            )
            response.delete_cookie(
                "gamja_refresh", domain=os.getenv("COOKIE_DOMAIN"), path="/"
            )
            logger.info("/api/auth/logout: Logout successful")
            return response
        except (InvalidToken, TokenError) as e:
            logger.error(f"/api/auth/logout: {e}")
            return Response(
                data={"message": "Invalid refresh token", "error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            logger.error(f"/api/auth/logout: {str(e)}")
            return Response(
                {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# 유저 회원 탈퇴 뷰
class UserDeleteView(generics.GenericAPIView):
    serializer_class = EmptySerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        methods=["DELETE"],
        tags=["auth"],
        summary="회원탈퇴",
        description="사용자 계정을 삭제하고 관련 토큰을 블랙리스트에 추가합니다.",
        responses={
            204: OpenApiResponse(description="회원탈퇴 성공"),
            400: OpenApiResponse(
                description="리프레시 토큰이 쿠키에 없거나 유효하지 않음"
            ),
            500: OpenApiResponse(description="서버 내부 오류"),
        },
    )
    def delete(self, request, *args, **kwargs):
        logger.info(f"DELETE /api/auth/delete for user: {request.user.username}")

        # refresh_token을 쿠키에서 가져옴
        refresh_token = request.COOKIES.get("gamja_refresh")
        if not refresh_token:
            logger.error("Refresh token not found in cookies")
            return Response(
                {"detail": "Refresh token not found in cookies"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # 현재 로그인된 유저 정보 사용
            user = request.user
            with transaction.atomic():
                user.delete()
                # refresh_token 블랙리스트 처리
                RefreshToken(refresh_token).blacklist()

            # 쿠키에서 JWT 삭제
            response = Response(status=status.HTTP_204_NO_CONTENT)
            response.delete_cookie(
                "gamja_access", domain=os.getenv("COOKIE_DOMAIN"), path="/"
            )
            response.delete_cookie(
                "gamja_refresh", domain=os.getenv("COOKIE_DOMAIN"), path="/"
            )

            logger.info(f"User {user.username} deleted successfully")
            return response

        except (InvalidToken, TokenError) as e:
            logger.error(f"Invalid refresh token: {e}")
            return Response(
                {"detail": "Invalid refresh token", "error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            logger.error(f"Error during user deletion: {str(e)}")
            return Response(
                {"detail": "An error occurred", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
