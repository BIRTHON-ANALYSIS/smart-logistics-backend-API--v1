from django.shortcuts import get_object_or_404, render
from accounts.permissions import IsAdminOrDispatcher
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from shipments.services import ShipmentService
from .models import Shipment
from .serializers import ShipmentHistorySerializer, ShipmentSerializer,ShipmentStatusSerializer, ShipmentUpdateSerializer,AssignDriverSerializer

from notifications.services import NotificationService
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend


class ShipmentListView(generics.ListAPIView):
    queryset = Shipment.objects.all()
    serializer_class = ShipmentSerializer

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

    def perform_create(self, serializer):

        shipment = serializer.save(customer=self.request.user
    )   # NotificationService.notify(user=self.request.user,title="Shipment Created",message=f"Shipment {shipment.tracking_number} has been created successfully."
         


class ShipmentUpdateView(generics.UpdateAPIView):

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
    
class TrackShipmentView(generics.RetrieveAPIView):

    serializer_class = ShipmentSerializer
    lookup_field = 'tracking_number'

    queryset = Shipment.objects.all()



class ShipmentStatusUpdateView(generics.UpdateAPIView):

    serializer_class = ShipmentStatusSerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        ShipmentService.update_status(
            shipment=serializer.instance,
            status=serializer.validated_data["status"],
            updated_by=self.request.user
        )
    




from .models import ShipmentHistory

class ShipmentStatusUpdateView(generics.UpdateAPIView):
    queryset = Shipment.objects.all()
    serializer_class = ShipmentStatusSerializer

    def perform_update(self, serializer):
        shipment = serializer.save()

        ShipmentHistory.objects.create(
            shipment=shipment,
            status=shipment.status,
            updated_by=self.request.user
        )


class AssignDriverView(generics.UpdateAPIView):
    serializer_class = AssignDriverSerializer
    permission_classes = [IsAdminOrDispatcher]

    queryset = Shipment.objects.all()

    def perform_update(self, serializer):
        shipment = serializer.save(status="assigned")

        if shipment.driver:
            shipment.driver.save()

            













class ShipmentHistoryView(generics.ListAPIView):
    serializer_class = ShipmentHistorySerializer

    def get_queryset(self):
        shipment = get_object_or_404(
            Shipment,
            tracking_number=self.kwargs["tracking_number"]
        )

        return shipment.history.all()
    


