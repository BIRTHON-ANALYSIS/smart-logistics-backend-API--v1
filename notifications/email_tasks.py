from celery import shared_task

from accounts.models import User
from .email_service import EmailService


@shared_task
def send_notification_email_task(user_id, subject, message):

    user = User.objects.get(id=user_id)
    
    EmailService.send_notification_email(
        user=user,
        subject=subject,
        message=message,
    )