import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_login_page_loads(client):
    response = client.get(reverse("login"))

    assert response.status_code == 200


@pytest.mark.django_db
def test_dashboard_requires_login(client):
    response = client.get(reverse("dashboard"))

    assert response.status_code == 302
    assert reverse("login") in response.url


@pytest.mark.django_db
def test_customer_can_open_dashboard(
    client,
    customer_user,
):
    client.force_login(customer_user)

    response = client.get(reverse("dashboard"))

    assert response.status_code == 200


@pytest.mark.django_db
def test_earnings_page_requires_login(client):
    response = client.get(reverse("earnings"))

    assert response.status_code == 302
    assert reverse("login") in response.url