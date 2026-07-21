from django.core.mail import send_mail
from django.conf import settings


class EmailService:

    @staticmethod

    


    def send_notification_email(user, subject, message):

        if not user.email:
            return

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )