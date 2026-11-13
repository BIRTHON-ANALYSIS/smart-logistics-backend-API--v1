from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def broadcast_shipment_status(shipment):
    """Send a status change to clients tracking this shipment."""
    channel_layer = get_channel_layer()

    if channel_layer is None:
        return

    async_to_sync(channel_layer.group_send)(
        f"shipment_{shipment.pk}",
        {
            "type": "shipment_status_updated",
            "shipment": {
                "id": shipment.pk,
                "tracking_number": shipment.tracking_number,
                "status": shipment.status,
            },
        },
    )