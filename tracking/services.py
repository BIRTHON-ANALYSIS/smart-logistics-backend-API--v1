from django.db.migrations import serializer
from django.shortcuts import get_object_or_404
from shipments.models import Shipment

from .models import DriverLocation


class TrackingService:

    @staticmethod
    def update_location(driver, latitude, shipment,longitude):
        TrackingService.update_location(
    driver=driver,
    shipment=shipment,
    latitude=serializer.validated_data["latitude"],
    longitude=serializer.validated_data["longitude"],
)
        return DriverLocation.objects.create(
            driver=driver,
            latitude=latitude,
            longitude=longitude,
            shipment=shipment
        )
        
    from shipments.models import Shipment


    def get_latest_location(tracking_number):
        shipment = get_object_or_404(
    Shipment,
        id=serializer.validated_data["shipment"].id,  driver=serializer.validated_data["driver"]
)

        shipment = Shipment.objects.get(
            tracking_number=tracking_number
        )

        if shipment.driver is None:
            return None

        return shipment.driver.locations.first()