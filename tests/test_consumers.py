
import pytest

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.test import override_settings
from django.urls import re_path

from tracking.consumers import ShipmentTrackingConsumer


class InjectUserMiddleware:
    """Provide a test user in the WebSocket scope."""

    def __init__(self, app, user):
        self.app = app
        self.user = user

    async def __call__(self, scope, receive, send):
        scope = dict(scope)
        scope["user"] = self.user
        await self.app(scope, receive, send)


def make_user(role, user_id=10, authenticated=True):
    return SimpleNamespace(
        pk=user_id,
        role=role,
        is_authenticated=authenticated,
    )


def make_snapshot(can_publish=False):
    return {
        "id": 123,
        "tracking_number": "SHIP-123",
        "status": "in_transit",
        "pickup_address": "Pickup",
        "delivery_address": "Dropoff",
        "driver": "driver1",
        "location_status": "awaiting_first_update",
        "current_location": None,
        "last_location_update": None,
        "can_publish": can_publish,
    }


@pytest.fixture
def consumer_app():
    async def create_app(user):
        app = InjectUserMiddleware(
            URLRouter([
                re_path(
                    r"^ws/shipments/(?P<tracking_number>[^/]+)/$",
                    ShipmentTrackingConsumer.as_asgi(),
                )
            ]),
            user,
        )
        return app

    return create_app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.django_db(transaction=True)
@override_settings(
    CHANNEL_LAYERS={
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer",
        }
    }
)
@pytest.mark.asyncio
async def test_customer_can_connect_and_receive_snapshot(consumer_app):
    user = make_user("customer")
    app = await consumer_app(user)

    with patch(
        "tracking.consumers.get_shipment_snapshot",
        new=AsyncMock(return_value=make_snapshot()),
    ):
        communicator = WebsocketCommunicator(
            app,
            "/ws/shipments/SHIP-123/",
        )
        connected, _ = await communicator.connect()

        assert connected

        message = await communicator.receive_json_from()

        assert message["type"] == "tracking_snapshot"
        assert message["shipment"]["tracking_number"] == "SHIP-123"
        assert "can_publish" not in message["shipment"]

        await communicator.disconnect()


@pytest.mark.django_db(transaction=True)
@override_settings(
    CHANNEL_LAYERS={
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer",
        }
    }
)
@pytest.mark.asyncio
async def test_unauthenticated_user_is_rejected(consumer_app):
    user = make_user("customer", authenticated=False)
    app = await consumer_app(user)

    with patch(
        "tracking.consumers.get_shipment_snapshot",
        new=AsyncMock(return_value=make_snapshot()),
    ):
        communicator = WebsocketCommunicator(
            app,
            "/ws/shipments/SHIP-123/",
        )
        connected, _ = await communicator.connect()

        assert not connected
        await communicator.wait()


@pytest.mark.django_db(transaction=True)
@override_settings(
    CHANNEL_LAYERS={
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer",
        }
    }
)
@pytest.mark.asyncio
async def test_user_without_shipment_access_is_rejected(consumer_app):
    user = make_user("customer")
    app = await consumer_app(user)

    with patch(
        "tracking.consumers.get_shipment_snapshot",
        new=AsyncMock(return_value=None),
    ):
        communicator = WebsocketCommunicator(
            app,
            "/ws/shipments/SHIP-123/",
        )
        connected, _ = await communicator.connect()

        assert not connected
        await communicator.wait()


@pytest.mark.django_db(transaction=True)
@override_settings(
    CHANNEL_LAYERS={
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer",
        }
    }
)
@pytest.mark.asyncio
async def test_customer_cannot_publish_location(consumer_app):
    user = make_user("customer")
    app = await consumer_app(user)

    with patch(
        "tracking.consumers.get_shipment_snapshot",
        new=AsyncMock(return_value=make_snapshot(can_publish=False)),
    ):
        communicator = WebsocketCommunicator(
            app,
            "/ws/shipments/SHIP-123/",
        )
        connected, _ = await communicator.connect()

        assert connected

        await communicator.receive_json_from()
        await communicator.send_json_to({
            "type": "location_update",
            "latitude": 6.5,
            "longitude": 3.4,
        })

        message = await communicator.receive_json_from()

        assert message["type"] == "error"
        assert "assigned driver" in message["message"]

        await communicator.disconnect()


@pytest.mark.django_db(transaction=True)
@override_settings(
    CHANNEL_LAYERS={
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer",
        }
    }
)
@pytest.mark.asyncio
async def test_assigned_driver_can_publish_location(consumer_app):
    user = make_user("driver", user_id=20)
    app = await consumer_app(user)

    location = {
        "latitude": "6.500000",
        "longitude": "3.400000",
        "recorded_at": "2026-01-01T10:00:00+00:00",
        "shipment_id": 123,
    }

    with (
        patch(
            "tracking.consumers.get_shipment_snapshot",
            new=AsyncMock(return_value=make_snapshot(can_publish=True)),
        ),
        patch(
            "tracking.consumers.save_driver_location",
            new=AsyncMock(return_value={"location": location}),
        ) as save_location,
    ):
        communicator = WebsocketCommunicator(
            app,
            "/ws/shipments/SHIP-123/",
        )
        connected, _ = await communicator.connect()

        assert connected

        await communicator.receive_json_from()
        await communicator.send_json_to({
            "type": "location_update",
            "latitude": 6.5,
            "longitude": 3.4,
        })

        message = await communicator.receive_json_from()

        assert message["type"] == "location_updated"
        assert message["location"] == location
        save_location.assert_awaited_once()

        await communicator.disconnect()


@pytest.mark.django_db(transaction=True)
@override_settings(
    CHANNEL_LAYERS={
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer",
        }
    }
)
@pytest.mark.asyncio
async def test_invalid_coordinates_are_rejected_without_saving(consumer_app):
    user = make_user("driver", user_id=20)
    app = await consumer_app(user)

    with (
        patch(
            "tracking.consumers.get_shipment_snapshot",
            new=AsyncMock(return_value=make_snapshot(can_publish=True)),
        ),
        patch(
            "tracking.consumers.save_driver_location",
            new=AsyncMock(),
        ) as save_location,
    ):
        communicator = WebsocketCommunicator(
            app,
            "/ws/shipments/SHIP-123/",
        )
        connected, _ = await communicator.connect()

        assert connected

        await communicator.receive_json_from()
        await communicator.send_json_to({
            "type": "location_update",
            "latitude": 91,
            "longitude": 3.4,
        })

        message = await communicator.receive_json_from()

        assert message["type"] == "error"
        assert message["message"] == "Invalid GPS coordinates."
        save_location.assert_not_awaited()

        await communicator.disconnect()


@pytest.mark.django_db(transaction=True)
@override_settings(
    CHANNEL_LAYERS={
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer",
        }
    }
)
@pytest.mark.asyncio
async def test_unknown_event_is_rejected(consumer_app):
    user = make_user("customer")
    app = await consumer_app(user)

    with patch(
        "tracking.consumers.get_shipment_snapshot",
        new=AsyncMock(return_value=make_snapshot()),
    ):
        communicator = WebsocketCommunicator(
            app,
            "/ws/shipments/SHIP-123/",
        )
        connected, _ = await communicator.connect()

        assert connected

        await communicator.receive_json_from()
        await communicator.send_json_to({"type": "something_else"})

        message = await communicator.receive_json_from()

        assert message["type"] == "error"
        assert message["message"] == "Unsupported WebSocket event."

        await communicator.disconnect()
