from django.shortcuts import render

# Create your views here.
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Shipment
from .serializers import ShipmentSerializer


class ShipmentListCreateView(generics.ListCreateAPIView):

    serializer_class = ShipmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Shipment.objects.filter(
            customer=self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(
            customer=self.request.user
        )


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

    serializer_class = ShipmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Shipment.objects.filter(
            customer=self.request.user
        )  