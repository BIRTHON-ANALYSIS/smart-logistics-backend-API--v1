from django.shortcuts import render

# Create your views here.
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsAdminOrDispatcher

from .models import DriverEarning
from .serializers import (
    DriverEarningSerializer,
    DriverEarningStatusSerializer,
)


class DriverEarningListCreateView(generics.ListCreateAPIView):
    serializer_class = DriverEarningSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        queryset = DriverEarning.objects.select_related(
            "driver__user",
            "shipment",
        )

        if user.role == "driver":
            queryset = queryset.filter(
                driver__user=user
            )

        elif user.role in ["admin", "dispatcher"]:
            pass

        else:
            queryset = queryset.none()

        status = self.request.query_params.get("status")

        if status:
            queryset = queryset.filter(status=status)

        return queryset

    def perform_create(self, serializer):
        if self.request.user.role not in [
            "admin",
            "dispatcher",
        ]:
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied(
                "Only admins and dispatchers can create driver earnings."
            )

        serializer.save()


class DriverEarningDetailView(generics.RetrieveAPIView):
    serializer_class = DriverEarningSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        queryset = DriverEarning.objects.select_related(
            "driver__user",
            "shipment",
        )

        if user.role == "driver":
            return queryset.filter(
                driver__user=user
            )

        if user.role in ["admin", "dispatcher"]:
            return queryset

        return queryset.none()


class DriverEarningStatusUpdateView(generics.UpdateAPIView):
    serializer_class = DriverEarningStatusSerializer
    queryset = DriverEarning.objects.all()
    permission_classes = [IsAdminOrDispatcher]



