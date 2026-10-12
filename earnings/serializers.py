from decimal import Decimal

from rest_framework import serializers

from shipments.models import Shipment

from .models import DriverEarning


class DriverEarningSerializer(serializers.ModelSerializer):
    driver_username = serializers.CharField(
        source="driver.user.username",
        read_only=True,
    )

    shipment_tracking_number = serializers.CharField(
        source="shipment.tracking_number",
        read_only=True,
    )

    class Meta:
        model = DriverEarning
        fields = [
            "id",
            "driver",
            "driver_username",
            "shipment",
            "shipment_tracking_number",
            "distance_km",
            "rate_per_km",
            "amount",
            "status",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "driver",
            "amount",
            "status",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        shipment = attrs["shipment"]

        if shipment.driver is None:
            raise serializers.ValidationError(
                "This shipment has no assigned driver."
            )

        if shipment.status != "delivered":
            raise serializers.ValidationError(
                "An earning can only be created for a delivered shipment."
            )

        if DriverEarning.objects.filter(
            shipment=shipment
        ).exists():
            raise serializers.ValidationError(
                "An earning already exists for this shipment."
            )

        if attrs["distance_km"] <= 0:
            raise serializers.ValidationError(
                {"distance_km": "Distance must be greater than zero."}
            )

        if attrs["rate_per_km"] <= 0:
            raise serializers.ValidationError(
                {"rate_per_km": "Rate per kilometer must be greater than zero."}
            )

        return attrs

    def create(self, validated_data):
        shipment = validated_data["shipment"]
        driver = shipment.driver

        amount = (
            Decimal(validated_data["distance_km"])
            * Decimal(validated_data["rate_per_km"])
        )

        return DriverEarning.objects.create(
            driver=driver,
            shipment=shipment,
            distance_km=validated_data["distance_km"],
            rate_per_km=validated_data["rate_per_km"],
            amount=amount,
        )


class DriverEarningStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverEarning
        fields = ["status"]

    def validate_status(self, value):
        current_status = self.instance.status

        allowed_transitions = {
            "pending": ["payable"],
            "payable": ["processing"],
            "processing": ["paid", "failed"],
            "failed": ["processing"],
            "paid": [],
        }

        if value not in allowed_transitions[current_status]:
            raise serializers.ValidationError(
                f"Cannot change earning from "
                f"{current_status} to {value}."
            )

        return value