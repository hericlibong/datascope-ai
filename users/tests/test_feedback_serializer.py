import pytest
from types import SimpleNamespace

from django.contrib.auth import get_user_model
from analysis.models import Article, Analysis
from users.serializers import FeedbackSerializer

User = get_user_model()
LONG_TEXT = "word " * 220   # > 200 mots


@pytest.fixture
def author(db):
    return User.objects.create_user(
        username="carol",
        email="carol@example.com",
        password="S@cret123",
    )


@pytest.fixture
def analysis(author):
    """Crée un Article + Analysis minimal pour rattacher les feedbacks."""
    article = Article.objects.create(
        user=author,
        content=LONG_TEXT,
        language="fr",
    )
    return Analysis.objects.create(
        article=article,
        score=8.5,
        profile_label="High potential",
    )


def _make_serializer(user, data):
    """Helper pour instancier FeedbackSerializer avec un faux request.user."""
    fake_request = SimpleNamespace(user=user)
    return FeedbackSerializer(data=data, context={"request": fake_request})


# ---------- CAS 1 : notes complètes -> OK ----------
@pytest.mark.django_db
def test_feedback_all_ratings_valid(author, analysis):
    data = {
        "analysis": analysis.id,
        "relevance": 5,
        "angles": 4,
        "sources": 5,
        "reusability": 4,
        "message": "Great insights!",
    }
    serializer = _make_serializer(author, data)
    assert serializer.is_valid(), serializer.errors

    # ⬇️ on fournit l’auteur, comme la vue le ferait
    feedback = serializer.save(user=author)

    assert feedback.user == author
    assert feedback.analysis == analysis


# ---------- CAS 2 : note partielle -> invalide ----------
@pytest.mark.django_db
def test_feedback_partial_ratings_invalid(author, analysis):
    data = {
        "analysis": analysis.id,
        "relevance": 5,          # une seule note
        "message": "Incomplete ratings",
    }
    serializer = _make_serializer(author, data)
    assert not serializer.is_valid()
    # Le validate() du serializer renvoie non_field_errors
    assert "non_field_errors" in serializer.errors


# ---------- CAS 3 : message seul -> OK ----------
@pytest.mark.django_db
def test_feedback_message_only_valid(author, analysis):
    data = {
        "analysis": analysis.id,
        "message": "Just a comment, no ratings.",
    }
    serializer = _make_serializer(author, data)
    assert serializer.is_valid(), serializer.errors
