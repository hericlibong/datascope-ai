# backend/ai_engine/tests/test_trusted_rerank.py

from types import SimpleNamespace
from unittest.mock import patch # noqa: F401
import pytest

from ai_engine import OPENAI_MODEL # noqa: F401
from ai_engine.schemas import DatasetSuggestion, LLMSourceSuggestion
from ai_engine import pipeline


def _angle_result_one():
    class _A:
        title = "Angle A"
        rationale = "Rationale A"
    class _AR:
        angles = [_A()]
    return _AR()


@pytest.mark.django_db
def test_trusted_rerank_soft_orders_trusted_first(settings, monkeypatch):
    """
    Vérifie que le tri 'soft' place les domaines trusted (ex: oecd.org)
    avant les non-trusted, sans supprimer les autres items.
    """
    # --- Config de test (trusted soft) ---
    settings.TRUSTED_DOMAINS = ["oecd.org", "insee.fr"]
    settings.TRUSTED_SOFT_WEIGHT = 0.2
    settings.URL_VALIDATION_FILTER_404 = True  # n'affecte pas ce test

    # --- Stubs légers pour alléger le pipeline ---
    monkeypatch.setattr(pipeline, "compute_score", lambda *a, **k: 7.0)
    monkeypatch.setattr(pipeline.extraction, "run", lambda *a, **k: SimpleNamespace())
    monkeypatch.setattr(pipeline.angles, "run", lambda *a, **k: _angle_result_one())

    # keywords.run → structure minimale : kw_result.sets[0].keywords
    kw_stub = [SimpleNamespace(sets=[SimpleNamespace(angle_title="Angle A", keywords=["k1"])])]
    monkeypatch.setattr(pipeline.keywords, "run", lambda *a, **k: kw_stub)

    # viz.run → liste vide
    monkeypatch.setattr(pipeline.viz, "run", lambda *a, **k: [[]])

    # Connectors → 2 datasets (non-trusted + trusted)
    def _run_connectors_stub(*a, **k):
        ds1 = DatasetSuggestion(
            title="NonTrusted",
            description="",
            source_name="Example",
            source_url="https://example.com/data1",
            found_by="CONNECTOR",
            angle_idx=0,
            formats=[],
            organization=None,
            license=None,
            last_modified="",
            richness=0,
        )
        ds2 = DatasetSuggestion(
            title="TrustedINSEE",
            description="",
            source_name="INSEE",
            source_url="https://insee.fr/dataset",
            found_by="CONNECTOR",
            angle_idx=0,
            formats=[],
            organization=None,
            license=None,
            last_modified="",
            richness=0,
        )
        return [[ds1, ds2]]
    monkeypatch.setattr(pipeline, "run_connectors", _run_connectors_stub)

    # LLM sources → 2 liens (non-trusted + trusted)
    def _llm_sources_stub(*a, **k):
        s1 = LLMSourceSuggestion(
            title="Other",
            description="",
            link="https://example.com/x",
            source="Other",
            angle_idx=0,
        )
        s2 = LLMSourceSuggestion(
            title="OECD",
            description="",
            link="https://oecd.org/y",
            source="OECD",
            angle_idx=0,
        )
        return [[s1, s2]]
    monkeypatch.setattr(pipeline.llm_sources, "run", _llm_sources_stub)

    # Mémoire + packaging → no-op
    monkeypatch.setattr(pipeline, "package", lambda *a, **k: (SimpleNamespace(), "md"))
    monkeypatch.setattr(pipeline, "get_memory", lambda *a, **k: SimpleNamespace(save_context=lambda *x, **y: None))

    # --- Exécution ---
    packaged, md, score, angle_resources = pipeline.run(
        "Some article",
        user_id="u1",
        validate_urls=False,   # on n'active pas la validation ici
    )

    # --- Asserts ---
    ar = angle_resources[0]
    # Datasets : INSEE (trusted) doit passer avant example.com
    ds_urls = [d.source_url for d in ar.datasets]
    assert "https://insee.fr/dataset" in ds_urls
    assert "https://example.com/data1" in ds_urls
    # trusted d'abord
    assert ds_urls.index("https://insee.fr/dataset") < ds_urls.index("https://example.com/data1")

    # Sources : OECD (trusted) doit passer avant example.com
    src_urls = [s.link for s in ar.sources]
    assert "https://oecd.org/y" in src_urls and "https://example.com/x" in src_urls
    assert src_urls.index("https://oecd.org/y") < src_urls.index("https://example.com/x")


@pytest.mark.django_db
def test_trusted_rerank_uses_final_url_when_validated(settings, monkeypatch):
    """
    Vérifie que si validate_urls=True et qu'une URL redirige vers un domaine trusted,
    le re-rank utilise bien le domaine final (final_url) pour le boost.
    """
    settings.TRUSTED_DOMAINS = ["who.int"]
    settings.TRUSTED_SOFT_WEIGHT = 0.3
    settings.URL_VALIDATION_FILTER_404 = True

    # Stubs pipeline "légers"
    monkeypatch.setattr(pipeline, "compute_score", lambda *a, **k: 7.0)
    monkeypatch.setattr(pipeline.extraction, "run", lambda *a, **k: SimpleNamespace())
    monkeypatch.setattr(pipeline.angles, "run", lambda *a, **k: _angle_result_one())
    kw_stub = [SimpleNamespace(sets=[SimpleNamespace(angle_title="Angle A", keywords=["k1"])])]
    monkeypatch.setattr(pipeline.keywords, "run", lambda *a, **k: kw_stub)
    monkeypatch.setattr(pipeline.viz, "run", lambda *a, **k: [[]])

    # Connectors → dataset qui redirige vers who.int (trusted)
    def _run_connectors_stub(*a, **k):
        ds_redirect = DatasetSuggestion(
            title="RedirectToWHO",
            description="",
            source_name="X",
            source_url="http://redirector.local/foo",  # non trusted à l'origine
            found_by="CONNECTOR",
            angle_idx=0,
            formats=[],
            organization=None,
            license=None,
            last_modified="",
            richness=0,
        )
        ds_other = DatasetSuggestion(
            title="Other",
            description="",
            source_name="Y",
            source_url="https://example.com/other",
            found_by="CONNECTOR",
            angle_idx=0,
            formats=[],
            organization=None,
            license=None,
            last_modified="",
            richness=0,
        )
        return [[ds_redirect, ds_other]]
    monkeypatch.setattr(pipeline, "run_connectors", _run_connectors_stub)

    # LLM sources vides pour simplifier ce test
    monkeypatch.setattr(pipeline.llm_sources, "run", lambda *a, **k: [[]])

    # Mémoire + packaging
    monkeypatch.setattr(pipeline, "package", lambda *a, **k: (SimpleNamespace(), "md"))
    monkeypatch.setattr(pipeline, "get_memory", lambda *a, **k: SimpleNamespace(save_context=lambda *x, **y: None))

    # Patch du validateur pour simuler une redirection vers who.int (trusted)
    def _fake_validate(url: str):
        if "redirector.local" in url:
            return {
                "input_url": url,
                "status": "redirected",
                "http_status": 200,
                "final_url": "https://who.int/datasets/xyz",
                "error": None,
            }
        return {
            "input_url": url,
            "status": "ok",
            "http_status": 200,
            "final_url": url,
            "error": None,
        }

    monkeypatch.setattr(pipeline, "validate_url", _fake_validate)

    # --- Exécution avec validation activée ---
    packaged, md, score, angle_resources = pipeline.run(
        "Some article",
        user_id="u1",
        validate_urls=True,   # important pour prendre en compte final_url
    )

    ar = angle_resources[0]
    urls = [d.source_url for d in ar.datasets]
    # On doit voir la final_url (who.int) ET elle doit remonter en tête
    assert urls[0].startswith("https://who.int/")
    assert "https://example.com/other" in urls
