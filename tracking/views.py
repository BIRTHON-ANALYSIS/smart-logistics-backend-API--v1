from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drivers.models import Driver
from .serializers import DriverLocationSerializer
from .services import TrackingService
from .google_maps import GoogleMapsService






class UpdateLocationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        try:
            driver = Driver.objects.get(user=request.user)

        except Driver.DoesNotExist:
            return Response(
                {"error": "Driver profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = DriverLocationSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        location = TrackingService.update_location(
            driver=driver,
            latitude=serializer.validated_data["latitude"],
            longitude=serializer.validated_data["longitude"],
        )

        return Response(
            DriverLocationSerializer(location).data,
            status=status.HTTP_201_CREATED,
        )


class GeocodeAddressView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        address = request.query_params.get("address")

        if not address:
            return Response(
                {"error": "address is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result = GoogleMapsService.geocode_address(
                address
            )

            return Response(result)

        except ValueError as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except RuntimeError as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )