import pytest

from shipments.models import Shipment, ShipmentHistory


SHIPMENTS_URL = "/api/shipments/"


@pytest.mark.django_db
def test_customer_can_create_shipment(api_client, customer_user):
    api_client.force_authenticate(user=customer_user)

    response = api_client.post(
        SHIPMENTS_URL,
        {
            "sender_name": "Test Sender",
            "receiver_name": "Test Receiver",
            "pickup_address": "Ikeja, Lagos",
            "delivery_address": "Victoria Island, Lagos",
        },
        format="json",
    )

    assert response.status_code == 201

    shipment = Shipment.objects.get(
        tracking_number=response.data["tracking_number"]
    )

    assert shipment.customer == customer_user
    assert shipment.tracking_number
    assert shipment.status == "pending"

    # A newly created shipment should start its history.
    assert ShipmentHistory.objects.filter(
        shipment=shipment,
        status="pending",
    ).exists()


@pytest.mark.django_db
def test_customer_only_sees_own_shipments(
    api_client,
    customer_user,
    second_customer,
):
    own_shipment = Shipment.objects.create(
        customer=customer_user,
        sender_name="Sender One",
        receiver_name="Receiver One",
        pickup_address="Address One",
        delivery_address="Address Two",
    )

    Shipment.objects.create(
        customer=second_customer,
        sender_name="Sender Two",
        receiver_name="Receiver Two",
        pickup_address="Address Three",
        delivery_address="Address Four",
    )

    api_client.force_authenticate(user=customer_user)

    response = api_client.get(SHIPMENTS_URL)

    assert response.status_code == 200

    results = (
        response.data["results"]
        if isinstance(response.data, dict)
        and "results" in response.data
        else response.data
    )

    tracking_numbers = [
        item["tracking_number"] for item in results
    ]

    assert tracking_numbers == [own_shipment.tracking_number]


@pytest.mark.django_db
def test_customer_cannot_view_another_customers_shipment(
    api_client,
    customer_user,
    second_customer,
):
    other_shipment = Shipment.objects.create(
        customer=second_customer,
        sender_name="Other Sender",
        receiver_name="Other Receiver",
        pickup_address="Address One",
        delivery_address="Address Two",
    )

    api_client.force_authenticate(user=customer_user)

    response = api_client.get(
        f"{SHIPMENTS_URL}{other_shipment.pk}/"
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_customer_cannot_assign_driver(
    api_client,
    customer_user,
    shipment,
    driver_profile,
):
    api_client.force_authenticate(user=customer_user)

    response = api_client.patch(
        f"{SHIPMENTS_URL}{shipment.pk}/assign-driver/",
        {"driver": driver_profile.pk},
        format="json",
    )

    assert response.status_code == 403
    shipment.refresh_from_db()
    assert shipment.driver is None


@pytest.mark.django_db
def test_customer_cannot_change_shipment_status(
    api_client,
    customer_user,
    shipment,
):
    api_client.force_authenticate(user=customer_user)

    response = api_client.patch(
        f"{SHIPMENTS_URL}{shipment.pk}/status/",
        {"status": "cancelled"},
        format="json",
    )

    assert response.status_code == 403

    shipment.refresh_from_db()
    assert shipment.status == "pending"


@pytest.mark.django_db
def test_invalid_shipment_status_transition_is_rejected(
    api_client,
    dispatcher_user,
    shipment,
):
    api_client.force_authenticate(user=dispatcher_user)

    response = api_client.patch(
        f"{SHIPMENTS_URL}{shipment.pk}/status/",
        {"status": "delivered"},
        format="json",
    )

    assert response.status_code == 400

    shipment.refresh_from_db()
    assert shipment.status == "pending"