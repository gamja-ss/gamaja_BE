"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 5.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

import os
from datetime import timedelta
from pathlib import Path

from celery.schedules import crontab
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv()


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    "0.0.0.0",
    "localhost",
    "127.0.0.1",
    "13.125.223.30",
    ".gamjass.xyz",
    "api.gamjass.xyz",
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost",
    "http://127.0.0.1:5173",
    "http://localhost:5173",
    "https://gamjass.xyz",
    "https://api.gamjass.xyz",
    "http://13.125.223.30",
]

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

CORS_ALLOW_CREDENTIALS = True  # 쿠키 등 credential 정보 허용
CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "cache-control",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost",
    "http://127.0.0.1:5173",
    "https://gamjass.xyz",
    "https://api.gamjass.xyz",
]

AUTH_USER_MODEL = "users.User"

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "channels",
    "common.apps.CommonConfig",
    "articles.apps.ArticlesConfig",
    "attendances.apps.AttendancesConfig",
    "baekjoons.apps.BaekjoonsConfig",
    "challenges.apps.ChallengesConfig",
    "follows.apps.FollowsConfig",
    "githubs.apps.GithubsConfig",
    "guestbooks.apps.GuestbooksConfig",
    "items.apps.ItemsConfig",
    "notifications.apps.NotificationsConfig",
    "potatoes.apps.PotatoesConfig",
    "programmers.apps.ProgrammersConfig",
    "stacks.apps.StacksConfig",
    "users.apps.UsersConfig",
    "coins.apps.CoinsConfig",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "drf_spectacular",
    "django_cryptography",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
}

SPECTACULAR_SETTINGS = {
    "TITLE": "감자쓰 API",
    "DESCRIPTION": "감자쓰의 API 문서입니다.",
    "SWAGGER_UI_SETTINGS": {
        "dom_id": "#swagger-ui",
        "layout": "BaseLayout",
        "deepLinking": True,
        "displayOperationId": True,
        "filter": True,
    },
    "SECURITY": [
        {
            "name": "Authorization",
            "type": "http",
            "scheme": "Bearer",
            "bearerFormat": "JWT",
        },
    ],
    "LICENSE": {
        "name": "MIT License",
    },
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SWAGGER_UI_DIST": "https://cdn.jsdelivr.net/npm/swagger-ui-dist@latest",
}

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": os.environ.get("RDS_HOSTNAME"),
        "NAME": os.environ.get("RDS_DB_NAME"),
        "USER": os.environ.get("RDS_USERNAME"),
        "PASSWORD": os.environ.get("RDS_PASSWORD"),
        "PORT": os.environ.get("RDS_DB_PORT", 5432),
        "TEST": {
            "NAME": "test_postgres",
        },
        "OPTIONS": {
            "client_encoding": "UTF8",  # UTF-8 문자셋 설정
        },
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

GITHUB_CONFIG = {
    # key
    "CLIENT_ID": os.getenv("GITHUB_CLIENT_ID"),
    "CLIENT_SECRETS": os.getenv("GITHUB_CLIENT_SECRETS"),
    # uri
    "LOGIN_URI": "https://github.com/login/oauth/authorize",
    "TOKEN_URI": "https://github.com/login/oauth/access_token",
    "PROFILE_URI": "https://api.github.com/user",
    "REDIRECT_URI": os.getenv("GITHUB_REDIRECT_URI"),
    # type
    "GRANT_TYPE": "authorization_code",
    "CONTENT_TYPE": "application/x-www-form-urlencoded;charset=utf-8",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),  # 액세스 토큰 만료 시간
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),  # 리프레시 토큰 만료 시간
    "ROTATE_REFRESH_TOKENS": False,  # 리프레시 토큰 순환 사용 여부
    "BLACKLIST_AFTER_ROTATION": False,  # 순환 사용 시 이전 리프레시 토큰 블랙리스트 등록 여부
    "AUTH_HEADER_TYPES": ("Bearer",),  # 인증 헤더 타입
    "USER_ID_FIELD": "id",  # 기본 Django 사용자 모델의 ID 필드
    "USER_ID_CLAIM": "user_id",
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",  # JWT 서명에 “HS256” 알고리즘을 사용
    "AUTH_TOKEN_CLASSES": (
        "rest_framework_simplejwt.tokens.AccessToken",
    ),  # 기본적으로 AccessToken 클래스를 사용
    "TOKEN_TYPE_CLAIM": "token_type",  # JWT에서 토큰 유형을 token_type 클레임으로 저장
}

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Seoul"

USE_I18N = True

USE_TZ = True

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", "")
CELERY_BROKER_URL = f"redis://:{REDIS_PASSWORD}@redis:6379/0"
CELERY_RESULT_BACKEND = f"redis://:{REDIS_PASSWORD}@redis:6379/0"

CELERY_BEAT_SCHEDULE = {
    "update-github-commits-every-30-minutes": {
        "task": "githubs.tasks.update_all_users_github_commits",
        "schedule": 30 * 60,  # 30분마다
    },
    "update-github-commits-at-23-55": {
        "task": "githubs.tasks.update_all_users_github_commits",
        "schedule": crontab(hour=23, minute=55),
    },
    "update-github-commits-at-23-58": {
        "task": "githubs.tasks.update_all_users_github_commits",
        "schedule": crontab(hour=23, minute=58),
    },
    "update-github-commits-at-00-00": {
        "task": "githubs.tasks.update_all_users_github_commits",
        "schedule": crontab(hour=0, minute=0),
    },
    "update_user_baekjoon_info-every-30-minutes": {
        "task": "baekjoons.tasks.update_all_users_baekjoon_info",
        "schedule": 30 * 60,
    },
    "update_user_baekjoon_info-at-23-55": {
        "task": "baekjoons.tasks.update_all_users_baekjoon_info",
        "schedule": crontab(hour=23, minute=55),
    },
    "update_user_baekjoon_info-at-23-58": {
        "task": "baekjoons.tasks.update_all_users_baekjoon_info",
        "schedule": crontab(hour=23, minute=58),
    },
    "update_user_baekjoon_info-at-00-00": {
        "task": "baekjoons.tasks.update_all_users_baekjoon_info",
        "schedule": crontab(hour=0, minute=0),
    },
    "update_user_programmers_info-every-30-minutes": {
        "task": "programmers.tasks.update_all_users_programmers_info",
        "schedule": 30 * 60,
    },
    "update_user_programmers_info-at-23-55": {
        "task": "programmers.tasks.update_all_users_programmers_info",
        "schedule": crontab(hour=23, minute=55),
    },
    "update_user_programmers_info-at-23-58": {
        "task": "programmers.tasks.update_all_users_programmers_info",
        "schedule": crontab(hour=23, minute=58),
    },
    "update_user_programmers_info-at-00-00": {
        "task": "programmers.tasks.update_all_users_programmers_info",
        "schedule": crontab(hour=0, minute=0),
    },
}

# 웹소켓 처리 layers
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [f"redis://:{REDIS_PASSWORD}@redis:6379/0"],  # Redis URL에 인증 정보 포함
        },
    },
}

# s3 setting
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = os.environ.get("AWS_S3_REGION_NAME")
AWS_QUERYSTRING_AUTH = False

DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
STATICFILES_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

STATIC_URL = (
    f"https://{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com/static/"
)
MEDIA_URL = (
    f"https://{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com/media/"
)
