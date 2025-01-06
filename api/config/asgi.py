"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from challenges.consumers import ChallengeConsumer
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import path
from notifications.consumers import NotificationConsumer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(
            URLRouter(
                [
                    path("ws/notifications/", NotificationConsumer.as_asgi()),
                    path(
                        "ws/challenges/<int:challenge_id>/", ChallengeConsumer.as_asgi()
                    ),
                ]
            )
        ),
    }
)
