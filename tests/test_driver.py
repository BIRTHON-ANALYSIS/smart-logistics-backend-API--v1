import pytest

from drivers.models import Driver


@pytest.mark.django_db
def test_driver_list_requires_authentication(api_client):
    response = api_client.get("/api/drivers/")

    assert response.status_code in (401, 403)


@pytest.mark.django_db
def test_dispatcher_can_list_drivers(
    api_client,
    dispatcher_user,
    driver_profile,
):
    api_client.force_authenticate(user=dispatcher_user)

    response = api_client.get("/api/drivers/")

    assert response.status_code == 200
    assert Driver.objects.filter(
        pk=driver_profile.pk
    ).exists()


@pytest.mark.django_db
def test_driver_profile_is_linked_to_driver_user(
    driver_user,
    driver_profile,
):
    assert driver_profile.user == driver_user
    assert driver_user.driver_profile == driver_profile