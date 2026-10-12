from rest_framework import serializers

from drivers.models import Driver
from .models import Shipment, ShipmentHistory
from  .services import ShipmentService

ALLOWED_TRANSITIONS = {
    "pending": [
        "assigned",
        "cancelled",
    ],
    "assigned": [
        "in_transit",
        "cancelled",
    ],
    "in_transit": [
        "delivered",
    ],
    "delivered": [],
    "cancelled": [],
}


class ShipmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Shipment
        fields = [
            "id",
            "tracking_number",
            "customer",
            "sender_name",
            "receiver_name",
            "pickup_address",
            "delivery_address",
            "driver",
            "status",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "tracking_number",
            "customer",
            "driver",
            "status",
            "created_at",
            "updated_at",
        ]


class ShipmentStatusSerializer(serializers.Serializer):

    status = serializers.ChoiceField(
        choices=Shipment.STATUS_CHOICES
    )

    def validate_status(self, value):
        shipment = self.instance

        if shipment is None:
            return value

        current_status = shipment.status

        allowed_statuses = ALLOWED_TRANSITIONS.get(
            current_status,
            [],
        )

        if value not in allowed_statuses:
            raise serializers.ValidationError(
                f"Shipment cannot move from "
                f"{current_status} to {value}."
            )

        return value


class AssignDriverSerializer(serializers.Serializer):

    driver = serializers.PrimaryKeyRelatedField(
        queryset=Driver.objects.all()
    )


class ShipmentHistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = ShipmentHistory
        fields = [
            "id",
            "shipment",
            "status",
            "updated_by",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "shipment",
            "status",
            "updated_by",
            "created_at",
        ]




class ShipmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Shipment
        fields = [
            "id",
            "tracking_number",
            "customer",
            "sender_name",
            "receiver_name",
            "pickup_address",
            "delivery_address",
            "driver",
            "status",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "tracking_number",
            "customer",
            "driver",
            "status",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        customer = self.context["request"].user

        return ShipmentService.create_shipment(
            customer=customer,
            sender_name=validated_data["sender_name"],
            receiver_name=validated_data["receiver_name"],
            pickup_address=validated_data["pickup_address"],
            delivery_address=validated_data["delivery_address"],
        )