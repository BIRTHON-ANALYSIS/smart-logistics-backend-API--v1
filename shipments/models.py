from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings
import uuid
from drivers.models import Driver

class Shipment(models.Model):

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('assigned', 'Assigned'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )

    tracking_number = models.CharField(
        max_length=50,
        unique=True,
        editable=False
    )

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='shipments'
    )

    sender_name = models.CharField(max_length=100)
    receiver_name = models.CharField(max_length=100)

    pickup_address = models.TextField()
    delivery_address = models.TextField()



    driver = models.ForeignKey (Driver,on_delete=models.SET_NULL, null=True, blank=True,  related_name='shipments')


    status = models.CharField(max_length=20,  choices=STATUS_CHOICES,   default='pending' )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.tracking_number:
            self.tracking_number = str(uuid.uuid4()).split('-')[0].upper()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.tracking_number
    






    