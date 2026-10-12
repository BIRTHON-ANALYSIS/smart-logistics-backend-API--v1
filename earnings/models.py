from django.db import models

# Create your models here.
from django.db import models

from drivers.models import Driver
from shipments.models import Shipment


class DriverEarning(models.Model):

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("payable", "Payable"),
        ("processing", "Processing"),
        ("paid", "Paid"),
        ("failed", "Failed"),
    )

    driver = models.ForeignKey(
        Driver,
        on_delete=models.CASCADE,
        related_name="earnings",
    )

    shipment = models.OneToOneField(
        Shipment,
        on_delete=models.CASCADE,
        related_name="driver_earning",
    )

    distance_km = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    rate_per_km = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"{self.driver.user.username} - "
            f"{self.shipment.tracking_number} - "
            f"{self.amount}"
        )