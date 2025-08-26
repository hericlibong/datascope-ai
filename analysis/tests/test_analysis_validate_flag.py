# backend/analysis/tests/test_analysis_validate_flag.py

from unittest.mock import patch
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from ai_engine.schemas import AngleResources, DatasetSuggestion


def _dummy_packaged():
    # Objet minimal pour satisfaire la vue (boucles d'entités/angles)
    class _Extr:
        persons = []
        organizations = []
        locations = []
        dates = []
        numbers = []
    class _AngObj:
        title = "Angle A"
        rationale = "Rationale A"
    class _Ang:
        angles = [_AngObj()]
    class _Pack:
        extraction = _Extr()
        angles = _Ang()
    return _Pack()


def _make_angle_resources(include_404: bool):
    ds_ok = DatasetSuggestion(
        title="OK dataset",
        description="",
        source_name="data.gouv.fr",
        source_url="https://example.org/ok",
        found_by="LLM",
        angle_idx=0,
        formats=[],
        organization=None,
        license=None,
        last_modified="",
        richness=0,
    )
    ds_404 = DatasetSuggestion(
        title="Missing dataset",
        description="",
        source_name="data.gouv.fr",
        source_url="https://example.org/404",
        found_by="LLM",
        angle_idx=0,
        formats=[],
        organization=None,
        license=None,
        last_modified="",
        richness=0,
    )
    datasets = [ds_ok, ds_404] if include_404 else [ds_ok]

    ar = AngleResources(
        index=0,
        title="Angle A",
        description="Rationale A",
        keywords=["k1", "k2"],
        datasets=datasets,
        sources=[],
        visualizations=[],
    )
    return [ar]


def test_post_analysis_with_validate_true_filters_404(db, settings):
    """
    Vérifie que :
    - la vue transmet validate_urls=True au pipeline
    - la réponse ne contient plus le dataset 404 (filtré par le pipeline quand validate=True)
    """
    settings.URL_VALIDATION_FILTER_404 = True

    User = get_user_model()
    user = User.objects.create_user(username="toto", password="pwd")
    client = APIClient()
    client.force_authenticate(user=user)

    # Stub du pipeline : renvoie des datasets différents selon validate_urls
    def _stub_pipeline(article_text, user_id="anon", validate_urls=False, filter_404=None):
        packaged = _dummy_packaged()
        markdown = "md"
        score = 7.5
        angle_resources = _make_angle_resources(include_404=not validate_urls)
        return packaged, markdown, score, angle_resources

    with patch("analysis.views.run_pipeline", side_effect=_stub_pipeline) as mocked:
        # Appel avec ?validate=true
        resp = client.post("/api/analysis/?validate=true", {"text": "Un contenu d'article suffisant."}, format="multipart")
        assert resp.status_code == 201

        # Le pipeline a bien été appelé avec validate_urls=True
        assert mocked.call_args.kwargs.get("validate_urls") is True

        # Le dataset 404 ne doit PAS être présent dans la réponse
        payload = resp.json()
        datasets = payload["angle_resources"][0]["datasets"]
        urls = [d.get("source_url") or d.get("link") for d in datasets]
        assert "https://example.org/404" not in urls
        assert "https://example.org/ok" in urls
