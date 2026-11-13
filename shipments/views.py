from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from urllib3 import request

from accounts.permissions import IsAdminOrDispatcher

from .models import Shipment
from .serializers import (
    AssignDriverSerializer,
    ShipmentHistorySerializer,
    ShipmentSerializer,
    ShipmentStatusSerializer,
)
from .services import ShipmentService


class ShipmentListView(generics.ListAPIView):
    

    queryset = Shipment.objects.select_related(
    "customer",
    "driver",
).order_by("-created_at", "-pk")
    serializer_class = ShipmentSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
    ]

    filterset_fields = [
        "status",
        "driver",
    ]

    search_fields = [
        "tracking_number",
        "sender_name",
        "receiver_name",
    ]


class ShipmentListCreateView(generics.ListCreateAPIView):
    serializer_class = ShipmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Shipment.objects.filter(
            customer=self.request.user
        )



class ShipmentDetailView(generics.RetrieveAPIView):
    serializer_class = ShipmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Shipment.objects.filter(
            customer=self.request.user
        )


class ShipmentUpdateView(generics.UpdateAPIView):
    serializer_class = ShipmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Shipment.objects.filter(
            customer=self.request.user
        )


class TrackShipmentView(generics.RetrieveAPIView):
    serializer_class = ShipmentSerializer
    permission_classes = [IsAuthenticated]

    queryset = Shipment.objects.all()
    lookup_field = "tracking_number"


from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from shipments.models import Shipment
from shipments.serializers import ShipmentStatusSerializer
from shipments.services import ShipmentService


class ShipmentStatusUpdateView(generics.UpdateAPIView):
    queryset = Shipment.objects.select_related(
        "customer",
        "driver",
        "driver__user",
    )

    serializer_class = ShipmentStatusSerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        shipment = serializer.instance
        user = self.request.user

        # Admins and dispatchers can update shipment status.
        is_admin_or_dispatcher = user.role in (
            "admin",
            "dispatcher",
        )

        # A driver can update only their assigned shipment.
        is_assigned_driver = (
            user.role == "driver"
            and shipment.driver_id is not None
            and shipment.driver.user_id == user.id
        )

        # Reject unauthorized users BEFORE any service call.
        if not (
            is_admin_or_dispatcher
            or is_assigned_driver
        ):
            raise PermissionDenied(
                "You are not allowed to update this shipment's status."
            )

        # Only authorized users reach this point.
        ShipmentService.update_status(
            shipment=shipment,
            status=serializer.validated_data["status"],
            updated_by=user,
        )



       
class AssignDriverView(generics.UpdateAPIView):
    queryset = Shipment.objects.all()
    serializer_class = AssignDriverSerializer
    permission_classes = [IsAdminOrDispatcher]

    def perform_update(self, serializer):
        driver = serializer.validated_data["driver"]

        ShipmentService.assign_driver(
            shipment=self.get_object(),
            driver=driver,
            updated_by=self.request.user,
        )


class ShipmentHistoryView(generics.ListAPIView):
    serializer_class = ShipmentHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        shipment = get_object_or_404(
            Shipment,
            tracking_number=self.kwargs[
                "tracking_number"
            ],
        )

        return shipment.history.all()