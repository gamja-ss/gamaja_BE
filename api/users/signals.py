from baekjoons.utils import set_initial_baekjoon_info
from django.db.models.signals import post_save
from django.dispatch import receiver
from githubs.utils import set_initial_github_commits
from programmers.utils import set_initial_programmers_info

from .models import User


@receiver(post_save, sender=User)
def initialize_github_commit_info(sender, instance, created, **kwargs):
    if created and instance.github_access_token and instance.username:
        set_initial_github_commits(instance)


@receiver(post_save, sender=User)
def handle_new_programmers_info(sender, instance, created, **kwargs):
    if not created and instance.programmers_id and instance.programmers_password:
        if instance.programmers_initial_date is None:
            set_initial_programmers_info(instance)


@receiver(post_save, sender=User)
def handle_new_programmers_info(sender, instance, created, **kwargs):
    if not created and instance.baekjoon_id:
        if instance.baekjoon_initial_date is None:
            set_initial_baekjoon_info(instance)
