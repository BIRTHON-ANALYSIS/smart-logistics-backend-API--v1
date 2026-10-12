from decimal import Decimal

from django.db import transaction

from tracking.distance import calculate_distance_km

from .models import DriverEarning


class EarningService:

    DEFAULT_RATE_PER_KM = Decimal("150.00")

    @staticmethod
    @transaction.atomic
    def create_earning(*, driver, shipment):

        distance_km = calculate_distance_km(
            driver,
            shipment,
        )

        earning, created = DriverEarning.objects.get_or_create(
            shipment=shipment,
            defaults={
                "driver": driver,
                "distance_km": Decimal(str(distance_km)),
                "rate_per_km": EarningService.DEFAULT_RATE_PER_KM,
                "amount": (
                    Decimal(str(distance_km))
                    * EarningService.DEFAULT_RATE_PER_KM
                ),
                "status": "payable",
            },
        )

        return earning