# api/tests/test_feedbacks.py
import pytest
from rest_framework import status
from django.contrib.auth import get_user_model
from analysis.models import Article, Analysis

User = get_user_model()
LONG_TEXT = "word " * 210


# ---------- fixtures spécifiques ----------
@pytest.fixture
def analysis_for_user(db, user):
    """Article + Analysis appartenant au fixture `user` (venant de conftest)."""
    article = Article.objects.create(
        user=user,
        content=LONG_TEXT,
        language="fr",
    )
    return Analysis.objects.create(
        article=article,
        score=9.0,
        profile_label="High",
    )


@pytest.fixture
def other_user(db):
    return User.objects.create_user(
        username="otherfb",
        email="otherfb@example.com",
        password="Other123",
    )


@pytest.mark.django_db
def test_post_feedback_valid(api_client, auth_headers, analysis_for_user):
    """Tous les ratings fournis → 201."""
    payload = {
        "analysis": analysis_for_user.id,
        "relevance": 5,
        "angles": 5,
        "sources": 4,
        "reusability": 5,
        "message": "Great job!",
    }
    resp = api_client.post(
        "/api/feedbacks/", payload, format="json", headers=auth_headers
    )
    assert resp.status_code == status.HTTP_201_CREATED
    assert resp.data["analysis"] == analysis_for_user.id
    assert resp.data["relevance"] == 5


@pytest.mark.django_db
def test_post_feedback_partial_ratings(api_client, auth_headers, analysis_for_user):
    """Notes incomplètes → 400 + erreur."""
    payload = {
        "analysis": analysis_for_user.id,
        "relevance": 5,       # une seule note
        "message": "Missing ratings",
    }
    resp = api_client.post(
        "/api/feedbacks/", payload, format="json", headers=auth_headers
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert "non_field_errors" in resp.data


@pytest.mark.django_db
def test_feedback_list_isolated(api_client, auth_headers, analysis_for_user, other_user):
    """Chaque utilisateur ne voit que ses feedbacks."""
    # 1) user crée un feedback
    api_client.post(
        "/api/feedbacks/",
        {
            "analysis": analysis_for_user.id,
            "relevance": 5,
            "angles": 5,
            "sources": 5,
            "reusability": 5,
        },
        format="json",
        headers=auth_headers,
    )

    # 2) list pour user -> 1 résultat
    resp_user = api_client.get("/api/feedbacks/", headers=auth_headers)
    assert resp_user.status_code == status.HTTP_200_OK
    assert resp_user.data["count"] == 1

    # 3) list pour other_user -> 0 résultat
    token_resp = api_client.post(
        "/api/token/",
        {"username": "otherfb", "password": "Other123"},
        format="json",
    )
    other_headers = {"Authorization": f"Bearer {token_resp.data['access']}"}
    resp_other = api_client.get("/api/feedbacks/", headers=other_headers)
    assert resp_other.status_code == status.HTTP_200_OK
    assert resp_other.data["count"] == 0
