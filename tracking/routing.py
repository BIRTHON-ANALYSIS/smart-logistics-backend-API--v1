from django.urls import re_path

from .consumers import ShipmentTrackingConsumer


websocket_urlpatterns = [
    re_path(
        r"^ws/shipments/(?P<tracking_number>[^/]+)/$",
        ShipmentTrackingConsumer.as_asgi(),
    ),
]