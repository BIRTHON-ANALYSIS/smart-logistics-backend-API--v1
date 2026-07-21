from django.db import models
from django.conf import settings


class Driver(models.Model):



    VEHICLE_CHOICES = [
        ("bike", "Bike"),
        ("car", "Car"),
        ("van", "Van"),
        ("truck", "Truck"),  ]

    vehicle_type = models.CharField(max_length=50, choices=[
        ('car', 'Car'),
        ('bike', 'Bike'),
        ('truck', 'Truck'), ])   

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name= "driver_profile" )

    phone_number = models.CharField(max_length=15)

    license_number = models.CharField(  max_length=50,  unique=True)

    is_available = models.BooleanField( default=True)

    created_at = models.DateTimeField( auto_now_add=True )

    def __str__(self):
        return self.user.username