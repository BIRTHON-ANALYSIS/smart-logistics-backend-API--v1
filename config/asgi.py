"""
ASGI config for config project.

It exposes the ASGI callable as a im-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""



import os

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings",
)

from django.core.asgi import get_asgi_application

# Initialize Django first.
django_asgi_app = get_asgi_application()

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

from tracking.routing import websocket_urlpatterns


application = ProtocolTypeRouter({
    # Normal HTTP requests.
    "http": django_asgi_app,

    # WebSocket requests.
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    ),
})


# ==========================================
# DJANGO CHANNELS - ASGI CONFIGURATION
# ==========================================

ASGI_APPLICATION = "config.asgi.application"


# ==========================================
# REDIS CHANNEL LAYER
# ==========================================

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [
                os.environ.get(
                    "CHANNEL_REDIS_URL",
                    "redis://127.0.0.1:6379/1",
                )
            ],
        },
    },
}