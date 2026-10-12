from django.db import transaction

from earnings.services import EarningService
from notifications.services import NotificationService
from shipments.models import Shipment, ShipmentHistory


class ShipmentService:

    @staticmethod
    @transaction.atomic
    def create_shipment(
        *,
        customer,
        sender_name,
        receiver_name,
        pickup_address,
        delivery_address,
    ):
        shipment = Shipment.objects.create(
            customer=customer,
            sender_name=sender_name,
            receiver_name=receiver_name,
            pickup_address=pickup_address,
            delivery_address=delivery_address,
        )

        ShipmentHistory.objects.create(
            shipment=shipment,
            status="pending",
            updated_by=customer,
        )

        return shipment

    @staticmethod
    @transaction.atomic
    def assign_driver(shipment, driver, updated_by):
        shipment.driver = driver
        shipment.status = "assigned"

        shipment.save(
            update_fields=[
                "driver",
                "status",
                "updated_at",
            ]
        )

        ShipmentHistory.objects.create(
            shipment=shipment,
            status=shipment.status,
            updated_by=updated_by,
        )

        NotificationService.notify(
            user=driver.user,
            title="New Delivery Assigned",
            message=(
                f"You have been assigned shipment "
                f"{shipment.tracking_number}."
            ),
        )

        return shipment

    @staticmethod
    @transaction.atomic
    def update_status(shipment, status, updated_by):
        shipment.status = status

        shipment.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        ShipmentHistory.objects.create(
            shipment=shipment,
            status=status,
            updated_by=updated_by,
        )

        if shipment.customer:
            NotificationService.notify(
                user=shipment.customer,
                title="Shipment Status Updated",
                message=(
                    f"Your shipment "
                    f"{shipment.tracking_number} "
                    f"is now {status}."
                ),
            )

        if status == "delivered" and shipment.driver:
           from earnings.services import EarningService

        EarningService.create_earning(driver=shipment.driver,        shipment=shipment,
    )

        return shipment