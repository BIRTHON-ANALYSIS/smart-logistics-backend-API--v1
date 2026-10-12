from django.urls import path

from .views import (
    DriverEarningDetailView,
    DriverEarningListCreateView,
    DriverEarningStatusUpdateView,
)


urlpatterns = [
    path(
        "",
        DriverEarningListCreateView.as_view(),
        name="earning-list",
    ),
    path(
        "<int:pk>/",
        DriverEarningDetailView.as_view(),
        name="earning-detail",
    ),
    path(
        "<int:pk>/status/",
        DriverEarningStatusUpdateView.as_view(),
        name="earning-status-update",
    ),
]