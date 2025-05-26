import pytest
from rest_framework import status


@pytest.mark.django_db
def test_obtain_and_refresh_token(api_client, user):
    # Obtain
    resp = api_client.post(
        "/api/token/",
        {"username": user.username, "password": "S@cret123"},
        format="json",
    )
    assert resp.status_code == status.HTTP_200_OK
    assert "access" in resp.data and "refresh" in resp.data

    # Refresh
    refresh = resp.data["refresh"]
    resp_refresh = api_client.post(
        "/api/token/refresh/",
        {"refresh": refresh},
        format="json",
    )
    assert resp_refresh.status_code == status.HTTP_200_OK
    assert "access" in resp_refresh.data


@pytest.mark.django_db
def test_login_bad_credentials(api_client):
    resp = api_client.post(
        "/api/token/",
        {"username": "wrong", "password": "bad"},
        format="json",
    )
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
