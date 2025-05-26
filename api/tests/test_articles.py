# api/tests/test_articles.py
import pytest
from rest_framework import status
from django.contrib.auth import get_user_model

LONG_TEXT = "word " * 210       # ≥ 200 mots
SHORT_TEXT = "word " * 50       # < 200 mots
User = get_user_model()


@pytest.fixture
def other_user(db):
    """Un second utilisateur pour vérifier l'isolation des données."""
    return User.objects.create_user(
        username="other",
        email="other@example.com",
        password="Other123"
    )


@pytest.mark.django_db
def test_post_article_valid(api_client, auth_headers):
    """POST valide : 201 + titre généré."""
    data = {"content": LONG_TEXT, "language": "fr"}
    resp = api_client.post("/api/articles/", data, format="json", headers=auth_headers)

    assert resp.status_code == status.HTTP_201_CREATED
    assert resp.data["id"] > 0
    assert resp.data["title"] != ""               # titre auto
    assert resp.data["language"] == "fr"


@pytest.mark.django_db
def test_post_article_too_short(api_client, auth_headers):
    """POST < 200 mots : 400."""
    data = {"content": SHORT_TEXT, "language": "fr"}
    resp = api_client.post("/api/articles/", data, format="json", headers=auth_headers)

    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert "content" in resp.data


@pytest.mark.django_db
def test_get_articles_isolated(api_client, auth_headers, user, other_user):
    """
    Chaque utilisateur ne voit que ses articles.
    - create article as 'user'
    - check list for 'user' returns 1
    - check list for 'other_user' returns 0
    """
    # 1) user crée un article
    api_client.post(
        "/api/articles/", {"content": LONG_TEXT, "language": "fr"},
        format="json", headers=auth_headers
    )

    # 2) GET liste pour user
    resp_list = api_client.get("/api/articles/", headers=auth_headers)
    assert resp_list.status_code == status.HTTP_200_OK
    assert resp_list.data["count"] == 1

    # 3) Obtenir token de other_user
    token_resp = api_client.post(
        "/api/token/",
        {"username": other_user.username, "password": "Other123"},
        format="json",
    )
    other_headers = {"Authorization": f"Bearer {token_resp.data['access']}"}

    # 4) Liste pour other_user → vide
    resp_other = api_client.get("/api/articles/", headers=other_headers)
    assert resp_other.status_code == status.HTTP_200_OK
    assert resp_other.data["count"] == 0
