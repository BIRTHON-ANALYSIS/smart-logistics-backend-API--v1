from shipments.models import Shipment

from .models import DriverLocation


class TrackingService:

    @staticmethod
    def update_location(driver, latitude, longitude):

        return DriverLocation.objects.create(
            driver=driver,
            latitude=latitude,
            longitude=longitude,
        )
    
    from shipments.models import Shipment


    def get_latest_location(tracking_number):

        shipment = Shipment.objects.get(
            tracking_number=tracking_number
        )

        if shipment.driver is None:
            return None

        return shipment.driver.locations.first()