"""
Tests unitaires pour AngleChain (ai_engine.chains.angles)
"""

import pytest
from ai_engine.schemas import AngleResult
import ai_engine.chains.angles as angles


# --------------------------------------------------------------------------- #
# Helpers                                                                     #
# --------------------------------------------------------------------------- #
class _FakeChain:
    """Chaîne factice dont invoke() renvoie un JSON prédéfini."""

    def __init__(self, fake_json: str):
        self._fake_json = fake_json

    def invoke(self, _):
        return AngleResult.model_validate_json(self._fake_json)


def _patch_chain(monkeypatch, fake_json: str):
    """Remplace angles._build_chain par un FakeChain."""
    monkeypatch.setattr(angles, "_build_chain", lambda: _FakeChain(fake_json))


# --------------------------------------------------------------------------- #
# Tests                                                                       #
# --------------------------------------------------------------------------- #
def test_fr_angle_ok(monkeypatch):
    fake_json = """
    {
      "language": "fr",
      "angles": [
        { "title": "Angle 1", "rationale": "Justification courte." },
        { "title": "Angle 2", "rationale": "Une autre piste." }
      ]
    }
    """
    _patch_chain(monkeypatch, fake_json)
    result = angles.run("dummy article")
    assert result.language == "fr"
    assert 2 <= len(result.angles) <= 5
    assert all(a.title and a.rationale for a in result.angles)


def test_en_angle_ok(monkeypatch):
    fake_json = """
    {
      "language": "en",
      "angles": [
        { "title": "Title 1", "rationale": "Short rationale." },
        { "title": "Title 2", "rationale": "Another point." },
        { "title": "Title 3", "rationale": "Third option." }
      ]
    }
    """
    _patch_chain(monkeypatch, fake_json)
    result = angles.run("dummy article")
    assert result.language == "en"
    assert 3 == len(result.angles)
    assert result.angles[0].title.startswith("Title")


def test_empty_article(monkeypatch):
    fake_json = """
    {
      "language": "fr",
      "angles": []
    }
    """
    _patch_chain(monkeypatch, fake_json)
    result = angles.run("")
    assert result.language == "fr"
    assert result.angles == []


def test_too_long_article(monkeypatch):
    long_text = "a " * 9001   # >8 000 tokens

    def _raise(*_args, **_kwargs):
        raise ValueError("Article too long")

    # chaîne qui lève directement l’erreur
    monkeypatch.setattr(
        angles, "_build_chain",
        lambda: type("ErrChain", (), {"invoke": _raise})()
    )

    with pytest.raises(ValueError):
        angles.run(long_text)
