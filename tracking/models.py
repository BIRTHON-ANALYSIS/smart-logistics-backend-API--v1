from django.db import models
from django.db import models
from drivers.models import Driver


class DriverLocation(models.Model):
    driver = models.ForeignKey(
        Driver,
        on_delete=models.CASCADE,
        related_name="locations"
    )

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6
    )

    recorded_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-recorded_at"]

    def __str__(self):
        return f"{self.driver.user.username} @ {self.recorded_at}"
# Create your models here.
