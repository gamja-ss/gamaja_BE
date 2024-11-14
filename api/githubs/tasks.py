from celery import shared_task
from django.contrib.auth import get_user_model

from .utils import update_user_github_commits

User = get_user_model()


@shared_task
def update_all_users_github_commits():
    for user in User.objects.all():
        update_user_github_commits(user)
