from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drivers.models import Driver
from .serializers import DriverLocationSerializer
from .services import TrackingService


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

