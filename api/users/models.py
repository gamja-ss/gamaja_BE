from common.models import TimeStampModel
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, username, email=None, **extra_fields):
        if not username:
            raise ValueError("The username must be provided")

        if email:
            email = self.normalize_email(email)
        user = self.model(username=username, **extra_fields)
        user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)

        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin, TimeStampModel):
    # 로그인 관련 필드
    username = models.CharField(max_length=255, null=False, unique=True)
    github_access_token = models.CharField(max_length=255, null=True, blank=True)

    # 프로필 관련 필드
    email = models.EmailField(max_length=255, null=True)
    profile_url = models.CharField(max_length=255, null=True)
    github_id = models.CharField(max_length=255, null=True)
    baekjoon_id = models.CharField(max_length=255, null=True)
    programmers_id = models.CharField(max_length=255, null=True)
    nickname = models.CharField(max_length=255, null=False)

    # 감자 관련 필드
    user_level = models.PositiveIntegerField(null=False, default=1)
    user_exp = models.PositiveIntegerField(null=False, default=0)
    total_coins = models.PositiveIntegerField(default=0)

    # Permissions Mixin : 유저의 권한 관리
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    # 유저를 생성 및 관리 (유저를 구분해서 관리하기 위해 - 관리자계정, 일반계정)
    objects = UserManager()

    def __str__(self):
        return self.username
