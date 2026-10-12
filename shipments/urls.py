from django.urls import path

from .views import (
    AssignDriverView,
    ShipmentDetailView,
    ShipmentHistoryView,
    ShipmentListCreateView,
    ShipmentListView,
    ShipmentStatusUpdateView,
    ShipmentUpdateView,
    TrackShipmentView,
)


urlpatterns = [
    # Customer shipments
    path(
        "",
        ShipmentListCreateView.as_view(),
        name="shipment-list-create",
    ),

    path(
        "all/",
        ShipmentListView.as_view(),
        name="shipment-list",
    ),

    path(
        "<int:pk>/",
        ShipmentDetailView.as_view(),
        name="shipment-detail",
    ),

    path(
        "<int:pk>/update/",
        ShipmentUpdateView.as_view(),
        name="shipment-update",
    ),

    # Shipment lifecycle
    path(
        "<int:pk>/status/",
        ShipmentStatusUpdateView.as_view(),
        name="shipment-status-update",
    ),

    # Driver assignment
    path(
        "<int:pk>/assign-driver/",
        AssignDriverView.as_view(),
        name="assign-driver",
    ),

    # Tracking
    path(
        "track/<str:tracking_number>/",
        TrackShipmentView.as_view(),
        name="track-shipment",
    ),

    # History
    path(
        "track/<str:tracking_number>/history/",
        ShipmentHistoryView.as_view(),
        name="shipment-history",
    ),
]