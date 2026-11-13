import pytest
from django.urls import reverse

from notifications.models import Notification


@pytest.mark.django_db
def test_user_sees_only_their_notifications(
    api_client,
    customer_user,
    second_customer,
):
    own_notification = Notification.objects.create(
        user=customer_user,
        title="Shipment Update",
        message="Your shipment has been assigned.",
    )

    Notification.objects.create(
        user=second_customer,
        title="Private Notification",
        message="This belongs to another customer.",
    )

    api_client.force_authenticate(user=customer_user)

    response = api_client.get(
        reverse("notification-list")
    )

    assert response.status_code == 200

    results = (
        response.data["results"]
        if isinstance(response.data, dict)
        and "results" in response.data
        else response.data
    )

    notification_ids = [
        item["id"] for item in results
    ]

    assert notification_ids == [own_notification.pk]

@pytest.mark.django_db
def test_user_can_mark_own_notification_as_read(
    client,
    customer_user,
):
    notification = Notification.objects.create(
        user=customer_user,
        title="Shipment Update",
        message="Your shipment is in transit.",
    )

    client.force_login(customer_user)

    response = client.post(
        reverse(
            "mark-notification-read",
            args=[notification.pk],
        ),
    )

    assert response.status_code == 302

    notification.refresh_from_db()
    assert notification.is_read is True


@pytest.mark.django_db
def test_user_cannot_mark_another_users_notification_as_read(
    client,
    customer_user,
    second_customer,
):
    notification = Notification.objects.create(
        user=second_customer,
        title="Private",
        message="Another user's notification.",
    )

    client.force_login(customer_user)

    response = client.post(
        reverse(
            "mark-notification-read",
            args=[notification.pk],
        ),
    )

    assert response.status_code == 404

    notification.refresh_from_db()
    assert notification.is_read is False