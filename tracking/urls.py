from django.urls import path,include
from .views import  GeocodeAddressView, ShipmentTrackingView,   UpdateLocationView

urlpatterns = [
    path(
        "update-location/",
        UpdateLocationView.as_view(),
        name="update-location",
    ),
    path(
        "geocode/",
        GeocodeAddressView.as_view(),
            name="geocode-address",
        ),
    path(
        "shipments/<str:tracking_number>/",
        ShipmentTrackingView.as_view(),
        name="shipment-tracking",
    ),
    path(
    "shipments/<str:tracking_number>/",
    ShipmentTrackingView.as_view(),
    name="shipment-tracking",
),

]
    