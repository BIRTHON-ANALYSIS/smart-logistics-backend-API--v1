from .models import Notification
from .tasks import create_notification
from .email_tasks import send_notification_email_task


class NotificationService:

    @staticmethod
    def notify(user, title, message):

        create_notification.delay(
            user.id,
            title,
            message,
        )

        send_notification_email_task.delay(
            user.id,
            title,
            message,
        )
