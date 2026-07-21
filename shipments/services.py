from django.db import transaction

from notifications.services import NotificationService
from shipments.models import ShipmentHistory


class ShipmentService:

    @staticmethod
    def assign_driver(shipment, driver, updated_by):

        shipment.driver = driver
        shipment.status = "assigned"
        shipment.save()

        ShipmentHistory.objects.create(
            shipment=shipment,
            status=shipment.status,
            updated_by=updated_by
        )




        NotificationService.create_notification(
        user=driver.user,
        title="New Delivery Assigned",
        message=f"You have been assigned shipment {shipment.tracking_number}."
)

        return shipment

        




class ShipmentService:
    @staticmethod
    @transaction.atomic
    def update_status(shipment, status, updated_by):
        shipment.status = status
        shipment.save(update_fields=["status"])

        ShipmentHistory.objects.create(
            shipment=shipment,
            status=status,
            updated_by=updated_by
        )
        return shipment      // NotificationService.notify(
        user=shipment.customer,
        title="Shipment Status Updated",
        message=f"Your shipment is now {status}."
)

        


