from rest_framework import serializers
from .models import Shipment, ShipmentHistory


class ShipmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Shipment
        fields = "__all__"
        read_only_fields = (
            "tracking_number",
            "customer",
            "created_at",
            "updated_at",
        )


class ShipmentUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Shipment
        fields = [
            "sender_name",
            "receiver_name",
            "pickup_address",
            "delivery_address",
            "driver",
            "status",
        ]


class ShipmentStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = Shipment
        fields = ["status"]


       

    def validate_status(self, value):

        current_status = self.instance.status

        allowed_transitions = {
            "pending": ["assigned", "cancelled"],
            "assigned": ["in_transit", "cancelled"],
            "in_transit": ["delivered"],
            "delivered": [],
            "cancelled": []
        }

        if value not in allowed_transitions[current_status]:
            raise serializers.ValidationError(
                f"Cannot change shipment from "
                f"{current_status} to {value}."
            )

        return value



from drivers.models import Driver


class AssignDriverSerializer(serializers.ModelSerializer):

    class Meta:
        model = Shipment
        fields = ["driver"]












class ShipmentHistorySerializer(serializers.ModelSerializer):

    updated_by = serializers.CharField(
        source="updated_by.username",
        read_only=True
    )

    class Meta:
        model = ShipmentHistory
        fields = [
            "status",
            "updated_by",
            "created_at",
        ] 


