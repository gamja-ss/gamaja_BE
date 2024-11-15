from celery import shared_task
from django.contrib.auth import get_user_model

from .utils import update_user_baekjoon_info

User = get_user_model()


@shared_task
def update_all_users_baekjoon_info():
    for user in User.objects.all():
        update_user_baekjoon_info(user)
