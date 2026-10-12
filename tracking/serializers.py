from rest_framework import serializers
from .models import DriverLocation


class DriverLocationSerializer(serializers.ModelSerializer):
    driver = serializers.CharField(source="driver.user.username", read_only=True)
    vehicle_type = serializers.CharField(source="driver.vehicle_type", read_only=True)

    class Meta:
        model = DriverLocation
        fields = [
            "id",
            "driver",
            "vehicle_type",
            "latitude",
            "longitude",
            "recorded_at",
        ]

read_only_fields = [
    "id",'driver', "recorded_at"    ]










