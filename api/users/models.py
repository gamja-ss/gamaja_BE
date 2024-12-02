from common.models import TimeStampModel
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.exceptions import ValidationError
from django.db import models

from .encrypt_utils import decrypt, encrypt


class EncryptedCharField(models.CharField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # 암호화 처리
    def get_prep_value(self, value):
        if not value:
            return None
        try:
            return encrypt(value)
        except ValueError as e:
            raise ValidationError(str(e))

    # 복호화 처리
    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        try:
            return decrypt(value)
        except ValueError as e:
            raise ValidationError(str(e))


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
    nickname = models.CharField(max_length=255, null=False)
    followers_count = models.PositiveIntegerField(default=0)
    following_count = models.PositiveIntegerField(default=0)

    # 계정 관련 필드
    github_id = models.CharField(max_length=255, null=True)
    github_initial_commits = models.IntegerField(null=True, blank=True)
    github_initial_date = models.DateField(null=True, blank=True)
    baekjoon_id = models.CharField(max_length=255, null=True)
    baekjoon_initial_solved = models.IntegerField(null=True, blank=True)
    baekjoon_initial_score = models.IntegerField(null=True, blank=True)
    baekjoon_initial_date = models.DateField(null=True, blank=True)
    programmers_id = models.CharField(max_length=255, null=True)
    programmers_password = EncryptedCharField(max_length=255, null=True)
    programmers_initial_solved = models.IntegerField(null=True, blank=True)
    programmers_initial_score = models.IntegerField(null=True, blank=True)
    programmers_initial_date = models.DateField(null=True, blank=True)

    # 감자 관련 필드
    user_tier = models.CharField(max_length=25, null=False, default="Bronze5")
    user_exp = models.PositiveIntegerField(null=False, default=0)
    total_coins = models.PositiveIntegerField(default=0)

    def increase_exp(self, amount):
        self.user_exp += amount
        self.user_tier = calculate_user_tier(self.user_exp)
        self.save()

    def update_total_coins(self):
        self.total_coins = self.coins.aggregate(total=models.Sum("coins"))["total"] or 0
        self.save()

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
