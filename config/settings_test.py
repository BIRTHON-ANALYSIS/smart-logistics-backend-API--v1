from .settings import *

# Run Celery tasks synchronously during tests.
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_TASK_STORE_EAGER_RESULT = False

# Keep test emails in memory.
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"