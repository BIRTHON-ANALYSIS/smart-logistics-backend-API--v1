

from rest_framework.routers import DefaultRouter, path
from .views import DriverShipmentListView, DriverViewSet

router = DefaultRouter()
router.register(r"", DriverViewSet, basename="driver")

urlpatterns = router.urls
path( "me/shipments/",
    DriverShipmentListView.as_view(),
    name="driver-shipments",
)