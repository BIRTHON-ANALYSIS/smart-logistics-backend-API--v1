import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def customer_user(db, django_user_model):
    return django_user_model.objects.create_user(
        username="customer_test",
        email="customer@example.com",
        password="TestPassword_2026!",
        role="customer",
    )


@pytest.fixture
def dispatcher_user(db, django_user_model):
    return django_user_model.objects.create_user(
        username="dispatcher_test",
        email="dispatcher@example.com",
        password="TestPassword_2026!",
        role="dispatcher",
    )


@pytest.fixture
def driver_user(db, django_user_model):
    return django_user_model.objects.create_user(
        username="driver_test",
        email="driver@example.com",
        password="TestPassword_2026!",
        role="driver",
    )












import pytest

from drivers.models import Driver
from shipments.models import Shipment


@pytest.fixture
def second_customer(db, django_user_model):
    return django_user_model.objects.create_user(
        username="customer_two",
        email="customer2@example.com",
        password="TestPassword_2026!",
        role="customer",
    )


@pytest.fixture
def driver_profile(db, driver_user):
    return Driver.objects.create(
        user=driver_user,
        vehicle_type="car",
        phone_number="08012345678",
        license_number="TEST-LIC-001",
        is_available=True,
    )


@pytest.fixture
def shipment(db, customer_user):
    return Shipment.objects.create(
        customer=customer_user,
        sender_name="Test Sender",
        receiver_name="Test Receiver",
        pickup_address="Ikeja, Lagos",
        delivery_address="Victoria Island, Lagos",
    )