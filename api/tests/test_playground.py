# api/tests/test_playground.py
import pytest
from django.test import override_settings
from django.urls import reverse

pytestmark = pytest.mark.django_db


@override_settings(PLAYGROUND_DEBUG_MODE=True)
def test_playground_history_exposed_with_flag_on(client):
    """
    Quand PLAYGROUND_DEBUG_MODE=1, le endpoint 'play-analysis-history' doit exister
    et répondre 200.
    """
    url = reverse("play-analysis-history")  # -> /api/playground/history/ si ton projet inclut api/ sous /api
    resp = client.get(url)
    assert resp.status_code == 200


@override_settings(PLAYGROUND_DEBUG_MODE=True)
def test_playground_history_injects_debug_when_param_present(client):
    """
    Avec ?debug=1, la réponse doit contenir le bloc `_debug` (injecté par PlaygroundDebugMixin).
    """
    url = reverse("play-analysis-history")
    resp = client.get(f"{url}?debug=1")
    assert resp.status_code == 200
    data = resp.json()
    # Le mixin n'injecte _debug que si la payload est un dict.
    # HistoryAPIView renvoie classiquement un dict { ... } => on vérifie la présence :
    assert isinstance(data, dict)
    assert "_debug" in data


@override_settings(PLAYGROUND_DEBUG_MODE=True)
def test_playground_history_no_debug_by_default(client):
    """
    Sans ?debug=1, aucun champ `_debug` ne doit être ajouté.
    """
    url = reverse("play-analysis-history")
    resp = client.get(url)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "_debug" not in data
