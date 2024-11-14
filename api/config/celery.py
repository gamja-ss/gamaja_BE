from __future__ import absolute_import, unicode_literals

import os

from celery import Celery

# Django 설정 모듈을 Celery의 기본으로 설정
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")

# Django 설정 파일에서 Celery 관련 설정을 불러옵니다.
app.config_from_object("django.conf:settings", namespace="CELERY")
app.conf.broker_connection_retry_on_startup = True

# 등록된 Django 앱 설정에서 task를 불러옵니다.
app.autodiscover_tasks()

app.conf.timezone = "Asia/Seoul"
