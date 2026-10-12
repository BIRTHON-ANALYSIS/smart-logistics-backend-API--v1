from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import generics
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated

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
    queryset = Shipment.objects.all()
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


class ShipmentStatusUpdateView(generics.UpdateAPIView):
    queryset = Shipment.objects.all()
    serializer_class = ShipmentStatusSerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        ShipmentService.update_status(
            shipment=serializer.instance,
            status=serializer.validated_data["status"],
            updated_by=self.request.user,
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