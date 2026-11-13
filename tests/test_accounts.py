import pytest

from django.contrib.auth import get_user_model
from django.urls import reverse


User = get_user_model()


@pytest.mark.django_db
def test_customer_registration(api_client):
    response = api_client.post(
        reverse("register"),
        {
            "username": "new_customer",
            "email": "newcustomer@example.com",
            "password": "StrongTestPassword_2026!",
            "phone_number": "08012345678",
        },
        format="json",
    )

    assert response.status_code == 201

    user = User.objects.get(username="new_customer")

    assert user.role == "customer"
    assert user.check_password("StrongTestPassword_2026!")
    assert "password" not in response.data


@pytest.mark.django_db
def test_duplicate_username_is_rejected(api_client, customer_user):
    response = api_client.post(
        reverse("register"),
        {
            "username": customer_user.username,
            "email": "another@example.com",
            "password": "AnotherStrongPassword_2026!",
            "phone_number": "08098765432",
        },
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_login_returns_jwt_tokens(api_client, customer_user):
    response = api_client.post(
        "/api/token/",
        {
            "username": "customer_test",
            "password": "TestPassword_2026!",
        },
        format="json",
    )

    assert response.status_code == 200
    assert "access" in response.data
    assert "refresh" in response.data


@pytest.mark.django_db
def test_invalid_password_is_rejected(api_client, customer_user):
    response = api_client.post(
        "/api/token/",
        {
            "username": "customer_test",
            "password": "WrongPassword",
        },
        format="json",
    )

    assert response.status_code == 401