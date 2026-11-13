from django.shortcuts import get_object_or_404

from shipments.models import Shipment

from .models import DriverLocation


class TrackingService:

    @staticmethod
    def update_location(
        driver,
        latitude,
        longitude,
        shipment=None,
    ):
        """
        Save a driver's location.
        A shipment is optional.
        """

        if shipment is not None and shipment.driver_id != driver.pk:
            raise ValueError(
                "This shipment is not assigned to the driver."
            )

        return DriverLocation.objects.create(
            driver=driver,
            shipment=shipment,
            latitude=latitude,
            longitude=longitude,
        )

    @staticmethod
    def get_latest_location(tracking_number):
        """
        Retrieve the latest location associated with a shipment.
        """

        shipment = get_object_or_404(
            Shipment.objects.select_related("driver"),
            tracking_number=tracking_number,
        )

        if shipment.driver_id is None:
            return None

        return shipment.tracking_locations.first()