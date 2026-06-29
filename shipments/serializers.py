
from rest_framework import serializers
from .models import Shipment


class ShipmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Shipment
        fields = ['status']
        read_only_fields = (
            'tracking_number',
            'customer',
            'created_at',
            'updated_at'
        )