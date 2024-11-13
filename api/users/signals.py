from django.db.models.signals import post_save
from django.dispatch import receiver
from githubs.utils import set_initial_github_commits

from .models import User


@receiver(post_save, sender=User)
def initialize_github_commit_info(sender, instance, created, **kwargs):
    if created and instance.github_access_token and instance.github_username:
        set_initial_github_commits(instance)
