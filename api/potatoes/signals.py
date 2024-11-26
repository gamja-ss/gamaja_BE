from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Potato


# 새로운 사용자가 생성될 때 기본 감자 객체를 자동으로 생성합니다.
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_potato(sender, instance, created, **kwargs):
    if created:
        Potato.objects.create(user=instance)
