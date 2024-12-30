import os

import pytz
from django.conf import settings
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken


class GamjaAuthClass:
    """
    1. Generate ACCESS_TOKEN, REFRESH_TOKEN
    2. Cookie settings
    """

    def __init__(self):
        self._seoul_timezone = pytz.timezone("Asia/Seoul")

        self._access_expiration = (
            timezone.now() + settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"]
        ).astimezone(self._seoul_timezone)

        self._refresh_expiration = (
            timezone.now() + settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"]
        ).astimezone(self._seoul_timezone)

    def set_jwt_auth_cookie(self, response, jwt_tokens):
        """
        Access token, Refresh token 쿠키 설정 함수
        """
        response = self.set_cookie_attributes(
            response=response,
            key="gamja_access",
            token=jwt_tokens["access"],
        )
        response = self.set_cookie_attributes(
            response=response,
            key="gamja_refresh",
            token=jwt_tokens["refresh"],
        )

        return response

    @staticmethod
    def set_cookie_attributes(response, key, token):
        """
        Cookie 속성 설정 함수
        key: gamja_access or gamja_refresh
        token: jwt token
        """
        if key == "gamja_access":
            expires_at = GamjaAuthClass()._access_expiration
        elif key == "gamja_refresh":
            expires_at = GamjaAuthClass()._refresh_expiration
        else:
            raise ValueError("key should be 'gamja_access' or 'gamja_refresh'")

        # .env 값을 읽어와 쿠키 설정
        samesite = os.getenv("COOKIE_SAMESITE", "Lax")  # 기본값 "Lax"
        secure = os.getenv("COOKIE_SECURE", "False").lower() == "true"
        domain = os.getenv("COOKIE_DOMAIN", None)  # 기본값 None

        response.set_cookie(
            key=key,
            value=token,
            httponly=True,
            samesite="Lax",
            secure=False,
            expires=expires_at,
            path="/",
        )
        return response

    @staticmethod
    def new_access_token_for_user(refresh_token):
        """
        기존 Refresh token을 사용하여 새로운 access token을 생성하는 함수
        이때, 새로 생성된 access token에는, user_id이 정보가 없는데, 직접 payload에 추가해주어야함
        """
        token = RefreshToken(refresh_token)
        new_access_token = token.access_token
        new_access_token["user_id"] = token["user_id"]

        return str(new_access_token)

    @staticmethod
    def set_auth_tokens_for_user(user):
        """
        사용자 인증 전용 JWT 생성 함수
        """
        refresh = RefreshToken.for_user(user)
        refresh["user_id"] = user.id
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }
