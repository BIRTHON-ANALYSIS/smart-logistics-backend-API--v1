from django.urls import path
from .views import  GeocodeAddressView,   UpdateLocationView

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
]
    