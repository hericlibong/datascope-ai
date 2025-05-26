# api/tests/confest.py
import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def api_client():
    """Client DRF sans authentification (utilisable partout)."""
    return APIClient()


@pytest.fixture
def user(db):
    """Utilisateur de base pour les appels protégés."""
    return User.objects.create_user(
        username="apitester",
        email="apitester@example.com",
        password="S@cret123",
    )


@pytest.fixture
def auth_headers(api_client, user):
    """
    Retourne l'en-tête Authorization: Bearer <access>
    à partir d'un POST /api/token/.
    """
    token_url = "/api/token/"
    resp = api_client.post(
        token_url,
        {"username": user.username, "password": "S@cret123"},
        format="json",
    )
    access = resp.data["access"]
    return {"Authorization": f"Bearer {access}"}
