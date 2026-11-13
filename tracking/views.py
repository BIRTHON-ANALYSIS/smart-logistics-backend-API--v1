from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from drivers.models import Driver
from shipments.models import Shipment
from tests.conftest import shipment

from .serializers import DriverLocationSerializer
from .services import TrackingService


class UpdateLocationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        # 1. Identify the authenticated driver
        try:
            driver = Driver.objects.get(user=request.user)

        except Driver.DoesNotExist:
            return Response(
                {"error": "Driver profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 2. Validate GPS coordinates
        serializer = DriverLocationSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        # 3. Associate location with a shipment when supplied
        shipment = None
        shipment_id = request.data.get("shipment_id")

        if shipment_id:
            try:
                shipment = Shipment.objects.get(
                    pk=shipment_id,
                    driver=driver,
                )

            except (
                Shipment.DoesNotExist,
                ValueError,
                TypeError,
            ):
                return Response(
                    {
                        "error": (
                            "Shipment not found or not "
                            "assigned to this driver."
                        )
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

        # 4. Save the driver's location
        try:
            location = TrackingService.update_location(
                driver=driver,
                latitude=serializer.validated_data["latitude"],
                longitude=serializer.validated_data["longitude"],
                shipment=shipment,
            )

        except ValueError as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 5. Return the saved location
        return Response(
            DriverLocationSerializer(location).data,
            status=status.HTTP_201_CREATED,
        )


class GeocodeAddressView(APIView):
    """
    Google Maps geocoding is currently disabled.
    GPS tracking continues to work independently.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(
            {
                "message": (
                    "Address geocoding is currently disabled. "
                    "GPS coordinate tracking remains available."
                )
            },
            status=status.HTTP_501_NOT_IMPLEMENTED,
        )


from tracking.models import DriverLocation  

class ShipmentTrackingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, tracking_number):
        try:
            shipment = Shipment.objects.get(
                tracking_number=tracking_number,
                customer=request.user,
            )
        except Shipment.DoesNotExist:
            return Response(
                {"error": "Shipment not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        location = DriverLocation.objects.filter(
            shipment=shipment
        ).order_by("-recorded_at").first()

        current_location = None

        if location:
            current_location = {
                "latitude": str(location.latitude),
                "longitude": str(location.longitude),
            }

        return Response({
            "tracking_number": shipment.tracking_number,
            "current_location": current_location,
        })


class ShipmentTrackingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, tracking_number):

        # Customers can only track their own shipments.
        shipment = (
            Shipment.objects
            .select_related("driver__user", "customer")
            .filter(
                tracking_number=tracking_number,
                customer=request.user,
            )
            .first()
        )

        if shipment is None:
            return Response(
                {"error": "Shipment not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Retrieve the most recent location for this shipment.
        location = shipment.tracking_locations.first()

        current_location = None

        if location:
            current_location = {
                "latitude": str(location.latitude),
                "longitude": str(location.longitude),
                "recorded_at": location.recorded_at.isoformat(),
            }

        driver = shipment.driver

        return Response(
            {
                "tracking_number": shipment.tracking_number,
                "status": shipment.status,
                "pickup_address": shipment.pickup_address,
                "delivery_address": shipment.delivery_address,

                "driver": (
                    {
                        "username": driver.user.username,
                    }
                    if driver else None
                ),

                "current_location": current_location,
            },
            status=status.HTTP_200_OK,
        )
