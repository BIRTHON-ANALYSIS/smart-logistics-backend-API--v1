from decimal import Decimal

import pytest
from django.urls import reverse

from earnings.models import DriverEarning
from shipments.models import Shipment


@pytest.fixture
def delivered_shipment(shipment, driver_profile):
    shipment.driver = driver_profile
    shipment.status = "delivered"
    shipment.save()

    return shipment


@pytest.mark.django_db
def test_dispatcher_can_create_earning(
    api_client,
    dispatcher_user,
    delivered_shipment,
    driver_profile,
):
    api_client.force_authenticate(user=dispatcher_user)

    response = api_client.post(
        reverse("earning-list"),
        {
            "shipment": delivered_shipment.pk,
            "distance_km": "12.50",
            "rate_per_km": "20.00",
        },
        format="json",
    )

    assert response.status_code == 201

    earning = DriverEarning.objects.get(
        shipment=delivered_shipment
    )

    assert earning.driver == driver_profile
    assert earning.amount == Decimal("250.00")
    assert earning.status == "pending"


@pytest.mark.django_db
def test_customer_cannot_create_earning(
    api_client,
    customer_user,
    delivered_shipment,
):
    api_client.force_authenticate(user=customer_user)

    response = api_client.post(
        reverse("earning-list"),
        {
            "shipment": delivered_shipment.pk,
            "distance_km": "10.00",
            "rate_per_km": "15.00",
        },
        format="json",
    )

    assert response.status_code == 403

    assert not DriverEarning.objects.filter(
        shipment=delivered_shipment
    ).exists()


@pytest.mark.django_db
def test_driver_can_only_see_own_earnings(
    api_client,
    driver_user,
    delivered_shipment,
    driver_profile,
):
    earning = DriverEarning.objects.create(
        driver=driver_profile,
        shipment=delivered_shipment,
        distance_km=Decimal("10.00"),
        rate_per_km=Decimal("15.00"),
        amount=Decimal("150.00"),
    )

    api_client.force_authenticate(user=driver_user)

    response = api_client.get(
        reverse("earning-list")
    )

    assert response.status_code == 200

    results = (
        response.data["results"]
        if isinstance(response.data, dict)
        and "results" in response.data
        else response.data
    )

    assert [item["id"] for item in results] == [
        earning.pk
    ]


@pytest.mark.django_db
def test_earning_status_can_transition_to_payable(
    api_client,
    dispatcher_user,
    delivered_shipment,
    driver_profile,
):
    earning = DriverEarning.objects.create(
        driver=driver_profile,
        shipment=delivered_shipment,
        distance_km=Decimal("10.00"),
        rate_per_km=Decimal("15.00"),
        amount=Decimal("150.00"),
        status="pending",
    )

    api_client.force_authenticate(user=dispatcher_user)

    response = api_client.patch(
        reverse(
            "earning-status-update",
            args=[earning.pk],
        ),
        {"status": "payable"},
        format="json",
    )

    assert response.status_code == 200

    earning.refresh_from_db()
    assert earning.status == "payable"