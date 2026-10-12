import logging

import redis
from django.conf import settings
from django.db import connection
from django.http import JsonResponse

logger = logging.getLogger(__name__)


def health_check(request):
    database_status = "ok"
    redis_status = "ok"

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:
        database_status = "error"
        logger.exception("Database health check failed.")

    try:
        client = redis.from_url(
            settings.REDIS_URL,
            socket_connect_timeout=2,
            socket_timeout=2,
        )
        client.ping()
        client.close()
    except Exception:
        redis_status = "error"
        logger.exception("Redis health check failed.")

    healthy = (
        database_status == "ok"
        and redis_status == "ok"
    )

    response = {
        "status": "ok" if healthy else "degraded",
        "database": database_status,
        "redis": redis_status,
    }

    return JsonResponse(
        response,
        status=200 if healthy else 503,
    )