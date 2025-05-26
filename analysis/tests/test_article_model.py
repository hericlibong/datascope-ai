# analysis/tests/test_article_serializer.py
import pytest
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from analysis.serializers import ArticleSerializer
from types import SimpleNamespace

User = get_user_model()
LONG_TEXT = "word " * 210
SHORT_TEXT = "word " * 50


@pytest.fixture
def author(db):
    return User.objects.create_user(
        username="bob",
        email="bob@example.com",
        password="S@cret123",
    )



def test_serializer_rejects_short_article(author):
    data = {"content": SHORT_TEXT, "language": "fr"}
    fake_request = SimpleNamespace(user=author)           # ← objet minimal
    serializer = ArticleSerializer(data=data, context={"request": fake_request})

    assert not serializer.is_valid()
    assert "content" in serializer.errors


def test_serializer_creates_title_and_article(author):
    content = "Un super titre généré automatiquement pour vérifier la logique " + LONG_TEXT
    data = {"content": content, "language": "fr"}
    serializer = ArticleSerializer(
        data=data,
        context={"request": type("obj", (), {"user": author})},
    )
    assert serializer.is_valid(), serializer.errors
    article = serializer.save(user=author)

    expected_title = " ".join(content.split()[:10])
    assert article.title == expected_title
