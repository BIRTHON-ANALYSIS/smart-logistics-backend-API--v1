from django.shortcuts import render

# Create your views here.
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.models import User
from drivers.models import Driver
from earnings.models import DriverEarning
from notifications.models import Notification
from shipments.models import Shipment, ShipmentHistory
from shipments.services import ShipmentService

from .forms import (
    AssignDriverForm,
    LoginForm,
    ShipmentCreateForm,
    ShipmentStatusForm,
)


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    form = LoginForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data["username"],
            password=form.cleaned_data["password"],
        )

        if user is not None:
            login(request, user)
            return redirect("dashboard")

        form.add_error(
            None,
            "Invalid username or password.",
        )

    return render(
        request,
        "login.html",
        {"form": form},
    )


@login_required
def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def dashboard(request):
    user = request.user

    context = {
        "shipment_form": ShipmentCreateForm(),
        "status_form": ShipmentStatusForm(),
        "assign_driver_form": AssignDriverForm(),
        "notifications_count": Notification.objects.filter(
            user=user,
            is_read=False,
        ).count(),
    }

    if user.role == User.CUSTOMER:
        context["shipments"] = Shipment.objects.filter(
            customer=user
        ).select_related("driver")

    elif user.role == User.DRIVER:
        context["shipments"] = Shipment.objects.filter(
            driver__user=user
        ).select_related("customer", "driver")

        context["driver"] = getattr(
            user,
            "driver_profile",
            None,
        )

    elif user.role in [User.ADMIN, User.DISPATCHER]:
        context["shipments"] = Shipment.objects.all().select_related(
            "customer",
            "driver",
            "driver__user",
        )

        context["drivers"] = Driver.objects.select_related(
            "user"
        ).all()

    else:
        context["shipments"] = Shipment.objects.none()

    return render(
        request,
        "dashboard.html",
        context,
    )


@login_required
@require_POST
def create_shipment(request):
    if request.user.role != User.CUSTOMER:
        messages.error(
            request,
            "Only customers can create shipments.",
        )
        return redirect("dashboard")

    form = ShipmentCreateForm(request.POST)

    if form.is_valid():
        shipment = form.save(commit=False)
        shipment.customer = request.user

        with transaction.atomic():
            shipment.save()

            ShipmentHistory.objects.create(
                shipment=shipment,
                status=shipment.status,
                updated_by=request.user,
            )

        messages.success(
            request,
            f"Shipment {shipment.tracking_number} created successfully.",
        )

    else:
        messages.error(
            request,
            "Please correct the shipment form.",
        )

    return redirect("dashboard")


@login_required
def shipment_detail(request, pk):
    shipment = get_object_or_404(
        Shipment.objects.select_related(
            "customer",
            "driver",
            "driver__user",
        ).prefetch_related("history"),
        pk=pk,
    )

    user = request.user

    allowed = (
        user.role in [User.ADMIN, User.DISPATCHER]
        or shipment.customer == user
        or (
            shipment.driver
            and shipment.driver.user == user
        )
    )

    if not allowed:
        messages.error(
            request,
            "You are not allowed to view this shipment.",
        )
        return redirect("dashboard")

    return render(
        request,
        "shipment_detail.html",
        {
            "shipment": shipment,
            "history": shipment.history.all(),
            "assign_driver_form": AssignDriverForm(),
            "status_form": ShipmentStatusForm(
                initial={"status": shipment.status}
            ),
        },
    )


@login_required
@require_POST
def update_shipment_status(request, pk):
    shipment = get_object_or_404(
        Shipment,
        pk=pk,
    )

    user = request.user

    allowed = (
        user.role in [User.ADMIN, User.DISPATCHER]
        or (
            shipment.driver
            and shipment.driver.user == user
        )
    )

    if not allowed:
        messages.error(
            request,
            "You are not allowed to update this shipment.",
        )
        return redirect(
            "shipment-detail",
            pk=pk,
        )

    form = ShipmentStatusForm(request.POST)

    if form.is_valid():
        ShipmentService.update_status(
            shipment=shipment,
            status=form.cleaned_data["status"],
            updated_by=user,
        )

        messages.success(
            request,
            "Shipment status updated.",
        )

    return redirect(
        "shipment-detail",
        pk=pk,
    )


@login_required
@require_POST
def assign_driver(request, pk):
    if request.user.role not in [
        User.ADMIN,
        User.DISPATCHER,
    ]:
        messages.error(
            request,
            "You are not allowed to assign drivers.",
        )
        return redirect(
            "shipment-detail",
            pk=pk,
        )

    shipment = get_object_or_404(
        Shipment,
        pk=pk,
    )

    form = AssignDriverForm(request.POST)

    if form.is_valid():
        driver = form.cleaned_data["driver"]

        ShipmentService.assign_driver(
            shipment=shipment,
            driver=driver,
            updated_by=request.user,
        )

        messages.success(
            request,
            f"{driver.user.username} assigned successfully.",
        )

    return redirect(
        "shipment-detail",
        pk=pk,
    )


@login_required
def track_shipment(request):
    shipment = None
    tracking_number = ""

    if request.method == "GET":
        tracking_number = request.GET.get(
            "tracking_number",
            "",
        ).strip()

        if tracking_number:
            shipment = get_object_or_404(
                Shipment.objects.select_related(
                    "driver",
                    "driver__user",
                ).prefetch_related("history"),
                tracking_number=tracking_number,
            )

    return render(
        request,
        "track.html",
        {
            "shipment": shipment,
            "tracking_number": tracking_number,
        },
    )


@login_required
def notifications(request):
    notification_list = Notification.objects.filter(
        user=request.user
    )

    return render(
        request,
        "notifications.html",
        {
            "notifications": notification_list,
        },
    )


@login_required
@require_POST
def mark_notification_read(request, pk):
    notification = get_object_or_404(
        Notification,
        pk=pk,
        user=request.user,
    )

    notification.is_read = True
    notification.save(
        update_fields=["is_read"]
    )

    return redirect("notifications")


@login_required
@require_POST
def delete_notification(request, pk):
    notification = get_object_or_404(
        Notification,
        pk=pk,
        user=request.user,
    )

    notification.delete()

    return redirect("notifications")

@login_required
def earnings_view(request):
    user = request.user

    if user.role == "driver":
        earnings = DriverEarning.objects.filter(
            driver__user=user
        ).select_related(
            "driver__user",
            "shipment",
        )

    elif user.role in ["admin", "dispatcher"]:
        earnings = DriverEarning.objects.select_related(
            "driver__user",
            "shipment",
        )

    else:
        earnings = DriverEarning.objects.none()

    return render(
        request,
        "earnings.html",
        {
            "earnings": earnings,
        },
    )