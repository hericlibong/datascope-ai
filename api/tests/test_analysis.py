# api/tests/test_analysis.py
import pytest
from rest_framework import status
from django.contrib.auth import get_user_model
from analysis.models import Article, Analysis

User = get_user_model()
LONG_TEXT = "word " * 210


# ---------- Fixtures ----------
@pytest.fixture
def analysis_user(db, user):
    """Article + Analysis appartenant à `user`."""
    article = Article.objects.create(
        user=user,
        content=LONG_TEXT,
        language="fr",
    )
    return Analysis.objects.create(
        article=article,
        score=7.5,
        profile_label="Medium",
    )


@pytest.fixture
def other_user(db):
    return User.objects.create_user(
        username="other",
        email="other@example.com",
        password="Other123",
    )


@pytest.fixture
def analysis_other(db, other_user):
    """Article + Analysis appartenant à `other_user`."""
    article = Article.objects.create(
        user=other_user,
        content=LONG_TEXT,
        language="fr",
    )
    return Analysis.objects.create(
        article=article,
        score=6.0,
        profile_label="Low",
    )


# ---------- Tests ----------
@pytest.mark.django_db
def test_detail_requires_authentication(api_client, analysis_user):
    url = f"/api/analysis/{analysis_user.id}/"
    resp = api_client.get(url)  # aucune auth
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_detail_owner_vs_other(api_client, auth_headers, analysis_user, analysis_other):
    # 1) owner accès OK
    url_owner = f"/api/analysis/{analysis_user.id}/"
    resp_owner = api_client.get(url_owner, headers=auth_headers)
    assert resp_owner.status_code == status.HTTP_200_OK
    assert resp_owner.data["id"] == analysis_user.id

    # 2) autre user -> 404
    token_resp = api_client.post(
        "/api/token/",
        {"username": "other", "password": "Other123"},
        format="json",
    )
    other_headers = {"Authorization": f"Bearer {token_resp.data['access']}"}

    url_other = f"/api/analysis/{analysis_user.id}/"
    resp_other = api_client.get(url_other, headers=other_headers)
    assert resp_other.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_history_returns_only_user_analyses(api_client, auth_headers, analysis_user, analysis_other):
    resp = api_client.get("/api/history/", headers=auth_headers)
    assert resp.status_code == status.HTTP_200_OK

    # Réponse paginée : les données sont dans resp.data["results"]
    assert resp.data["count"] == 1
    assert resp.data["results"][0]["id"] == analysis_user.id

