import pytest
from django.urls import reverse
from tracking.models import DriverLocation


@pytest.mark.django_db
def test_driver_can_update_location(
    api_client,
    driver_user,
    driver_profile,
):
    api_client.force_authenticate(user=driver_user)

    response = api_client.post(
        reverse("update-location"),
        {
            "latitude": 6.5244,
            "longitude": 3.3792,
        },
        format="json",
    )

    assert response.status_code == 201

    assert DriverLocation.objects.filter(
        driver=driver_profile
    ).exists()


@pytest.mark.django_db
def test_user_without_driver_profile_cannot_update_location(
    api_client,
    driver_user,
):
    api_client.force_authenticate(user=driver_user)

    response = api_client.post(
        reverse("update-location"),
        {
            "latitude": 6.5244,
            "longitude": 3.3792,
        },
        format="json",
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_unauthenticated_user_cannot_update_location(api_client):
    response = api_client.post(
        reverse("update-location"),
        {
            "latitude": 6.5244,
            "longitude": 3.3792,
        },
        format="json",
    )

    assert response.status_code in (401, 403)



@pytest.mark.django_db
def test_customer_can_track_own_shipment(
    api_client,
    customer_user,
    shipment,
    driver_profile,
):
    shipment.driver = driver_profile
    shipment.save()

    DriverLocation.objects.create(
        driver=driver_profile,
        shipment=shipment,
        latitude=6.524400,
        longitude=3.379200,
    )

    api_client.force_authenticate(user=customer_user)

    response = api_client.get(
        reverse(
            "shipment-tracking",
            kwargs={
                "tracking_number": shipment.tracking_number
            },
        )
    )

    assert response.status_code == 200

    assert response.data["tracking_number"] == shipment.tracking_number

    assert response.data["current_location"]["latitude"] == "6.524400"
    assert response.data["current_location"]["longitude"] == "3.379200"



@pytest.mark.django_db
def test_customer_cannot_track_another_customers_shipment(
    api_client,
    second_customer,
    shipment,
):
    api_client.force_authenticate(user=second_customer)

    response = api_client.get(
        reverse(
            "shipment-tracking",
            kwargs={
                "tracking_number": shipment.tracking_number
            },
        )
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_tracking_returns_null_when_no_location_exists(
    api_client,
    customer_user,
    shipment,
):
    api_client.force_authenticate(user=customer_user)

    response = api_client.get(
        reverse(
            "shipment-tracking",
            kwargs={
                "tracking_number": shipment.tracking_number
            },
        )
    )

    assert response.status_code == 200
    assert response.data["current_location"] is None