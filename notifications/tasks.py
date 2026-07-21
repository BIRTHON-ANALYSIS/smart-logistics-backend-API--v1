from celery import shared_task

from .models import Notification


@shared_task
def create_notification(user, title, message):

    Notification.objects.create(
        user_id=user,
        title=title,
        message=message,
    )