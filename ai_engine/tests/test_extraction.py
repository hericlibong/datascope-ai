import pytest
from pydantic import ValidationError
from ai_engine.schemas import ExtractionResult
import ai_engine.chains.extraction as extraction


# ---------- utilitaires de patch ------------
class FakeChain:
    def __init__(self, fake_json):
        self._fake_json = fake_json

    def invoke(self, _):
        # Simule la validation Pydantic comme le vrai OutputParser
        return ExtractionResult.model_validate_json(self._fake_json)


def patch_chain(monkeypatch, fake_json):
    """Remplace extraction._build_chain par un FakeChain."""
    monkeypatch.setattr(
        extraction,
        "_build_chain",
        lambda *_args, **_kwargs: FakeChain(fake_json),
    )


# ---------- tests ---------------------------

def test_fr_extraction_ok(monkeypatch):
    fake_json = """
    {
      "language": "fr",
      "persons": ["Emmanuel Macron"],
      "organizations": [],
      "locations": ["Strasbourg"],
      "dates": ["2024-03-12"],
      "numbers": []
    }
    """
    patch_chain(monkeypatch, fake_json)
    result = extraction.run("dummy")
    assert result.language == "fr"
    assert "Emmanuel Macron" in result.persons


def test_en_extraction_ok(monkeypatch):
    fake_json = """
    {
      "language": "en",
      "persons": ["Joe Biden"],
      "organizations": ["NASA"],
      "locations": [],
      "dates": ["2024-07-04"],
      "numbers": []
    }
    """
    patch_chain(monkeypatch, fake_json)
    result = extraction.run("dummy")
    assert result.language == "en"
    assert "Joe Biden" in result.persons
    assert "NASA" in result.organizations


def test_empty_article(monkeypatch):
    fake_json = """
    {
      "language": "fr",
      "persons": [],
      "organizations": [],
      "locations": [],
      "dates": [],
      "numbers": []
    }
    """
    patch_chain(monkeypatch, fake_json)
    result = extraction.run("")
    # toutes les listes doivent être vides
    assert all(len(getattr(result, field)) == 0
               for field in ["persons", "organizations", "locations", "dates", "numbers"])


def test_too_long_article(monkeypatch):
    long_text = "a " * 9001  # > 8K tokens

    def _raise(*_args, **_kwargs):          # ← accepte self + input
        raise ValueError("Article too long")


    monkeypatch.setattr(extraction, "_build_chain", lambda *_a, **_k: type(
        "ErrChain", (), {"invoke": _raise}
    )())

    with pytest.raises(ValueError):
        extraction.run(long_text)
