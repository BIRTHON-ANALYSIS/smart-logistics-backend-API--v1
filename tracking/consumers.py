from decimal import Decimal, InvalidOperation
from datetime import timedelta

from django.utils import timezone

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from drivers.models import Driver
from shipments.models import Shipment
from .services import TrackingService


LOCATION_STALE_AFTER_SECONDS = 300


class ShipmentTrackingConsumer(AsyncJsonWebsocketConsumer):
    """
    Handles real-time shipment tracking.

    Driver:
        Publishes GPS updates for assigned shipments.

    Customer:
        Receives GPS updates for owned shipments.

    Dispatcher/Admin:
        Can observe shipment updates.
    """

    async def connect(self):
        user = self.scope.get("user")

        # 1. Authenticate the connection.
        if not user or not user.is_authenticated:
            await self.close(code=4401)
            return

        self.user_id = user.pk
        self.user_role = getattr(user, "role", None)

        self.tracking_number = self.scope[
            "url_route"
        ]["kwargs"]["tracking_number"]

        # 2. Verify shipment ownership or assignment.
        snapshot = await get_shipment_snapshot(
            self.user_id,
            self.user_role,
            self.tracking_number,
        )

        if snapshot is None:
            await self.close(code=4404)
            return

        self.shipment_id = snapshot["id"]
        self.can_publish = snapshot["can_publish"]

        # 3. Create a private group for this shipment.
        self.group_name = f"shipment_{self.shipment_id}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name,
        )

        # 4. Accept the connection.
        await self.accept()

        # 5. Send the initial tracking snapshot.
        snapshot.pop("can_publish", None)
        snapshot["current_location_status"] = snapshot.pop(
            "location_status"
        )

        await self.send_json({
            "type": "tracking_snapshot",
            "shipment": snapshot,
        })

    async def disconnect(self, close_code):
        # Remove the connection from its shipment group.
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name,
            )

    async def receive_json(self, content, **kwargs):
        """
        Receive messages from connected clients.

        Only assigned drivers can publish location updates.
        """

        event_type = content.get("type")

        if event_type != "location_update":
            await self.send_json({
                "type": "error",
                "message": "Unsupported WebSocket event.",
            })
            return

        # Customers and observers cannot publish GPS locations.
        if not self.can_publish:
            await self.send_json({
                "type": "error",
                "message": (
                    "Only the assigned driver can submit "
                    "shipment location updates."
                ),
            })
            return

        # 1. Validate coordinates.
        try:
            latitude = Decimal(
                str(content.get("latitude"))
            )

            longitude = Decimal(
                str(content.get("longitude"))
            )

            if not latitude.is_finite() or not longitude.is_finite():
                raise ValueError("Coordinates must be finite numbers.")

            if not Decimal("-90") <= latitude <= Decimal("90"):
                raise ValueError("Invalid latitude.")

            if not Decimal("-180") <= longitude <= Decimal("180"):
                raise ValueError("Invalid longitude.")

        except (
            InvalidOperation,
            TypeError,
            ValueError,
        ):
            await self.send_json({
                "type": "error",
                "message": "Invalid GPS coordinates.",
            })
            return

        # 2. Persist the location.
        result = await save_driver_location(
            user_id=self.user_id,
            tracking_number=self.tracking_number,
            latitude=latitude,
            longitude=longitude,
        )

        if result.get("error"):
            await self.send_json({
                "type": "error",
                "message": result["error"],
            })
            return

        # 3. Broadcast to everyone subscribed to this shipment.
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "tracking.location_updated",
                "location": result["location"],
            },
        )

    async def tracking_location_updated(self, event):
        """
        Deliver new GPS coordinates to connected customers
        and other authorised observers.
        """

        await self.send_json({
            "type": "location_updated",
            "location": event["location"],
            "location_status": "tracking_active",
        })

    async def shipment_status_updated(self, event):
        """
        Deliver shipment status changes to connected clients.
        """

        await self.send_json({
            "type": "shipment_status_changed",
            "shipment": event["shipment"],
        })


@database_sync_to_async
def get_shipment_snapshot(user_id, role, tracking_number):
    """
    Check permissions and retrieve the latest shipment information.
    """

    try:
        shipment = (
            Shipment.objects
            .select_related(
                "customer",
                "driver__user",
            )
            .get(tracking_number=tracking_number)
        )

    except Shipment.DoesNotExist:
        return None

    can_publish = False

    if role == "customer":
        allowed = shipment.customer_id == user_id

    elif role == "driver":
        allowed = (
            shipment.driver_id is not None
            and shipment.driver.user_id == user_id
        )
        can_publish = allowed

    elif role in ("admin", "dispatcher"):
        allowed = True

    else:
        allowed = False

    if not allowed:
        return None

    # Retrieve the latest GPS location for this shipment.
    location = shipment.tracking_locations.first()

    current_location = None
    location_status = "awaiting_first_update"
    last_location_update = None

    if location:
        last_location_update = location.recorded_at

        age = timezone.now() - location.recorded_at

        if age <= timedelta(
            seconds=LOCATION_STALE_AFTER_SECONDS
        ):
            location_status = "tracking_active"
        else:
            location_status = "location_stale"

        current_location = {
            "latitude": str(location.latitude),
            "longitude": str(location.longitude),
            "recorded_at": location.recorded_at.isoformat(),
        }

    return {
        "id": shipment.pk,
        "tracking_number": shipment.tracking_number,
        "status": shipment.status,
        "pickup_address": shipment.pickup_address,
        "delivery_address": shipment.delivery_address,
        "driver": (
            shipment.driver.user.username
            if shipment.driver_id
            else None
        ),
        "location_status": location_status,
        "current_location": current_location,
        "last_location_update": (
            last_location_update.isoformat()
            if last_location_update
            else None
        ),
        "can_publish": can_publish,
    }


@database_sync_to_async
def save_driver_location(
    user_id,
    tracking_number,
    latitude,
    longitude,
):
    """
    Verify driver assignment and save a new GPS location.
    """

    try:
        driver = Driver.objects.get(
            user_id=user_id
        )

        shipment = Shipment.objects.get(
            tracking_number=tracking_number,
            driver=driver,
        )

    except (
        Driver.DoesNotExist,
        Shipment.DoesNotExist,
    ):
        return {
            "error": "Driver or assigned shipment not found."
        }

    # Only accept live tracking updates during delivery.
    if shipment.status != "in_transit":
        return {
            "error": (
                "GPS updates are only permitted "
                "for shipments currently in transit."
            )
        }

    try:
        location = TrackingService.update_location(
            driver=driver,
            shipment=shipment,
            latitude=latitude,
            longitude=longitude,
        )

    except ValueError as exc:
        return {"error": str(exc)}

    return {
        "location": {
            "latitude": str(location.latitude),
            "longitude": str(location.longitude),
            "recorded_at": location.recorded_at.isoformat(),
            "shipment_id": shipment.pk,
        }
    }