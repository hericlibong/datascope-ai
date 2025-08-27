# backend/ai_engine/tests/test_theme_filter.py
from types import SimpleNamespace
import pytest

from ai_engine import pipeline
from ai_engine.schemas import DatasetSuggestion, LLMSourceSuggestion


def _angle_result_one():
    class _A:
        title = "Moustique tigre en France"
        rationale = "Surveillance et présence d'Aedes albopictus"
    class _AR:
        angles = [_A()]
    return _AR()


@pytest.mark.django_db
def test_theme_filter_soft_prioritizes_on_theme(settings, monkeypatch):
    """
    Soft mode: l'item sur-thème (Aedes/moustique tigre) doit remonter devant l'hors-thème (volcan El Tigre).
    Aucun filtrage/suppression en soft.
    """
    # Neutraliser l'impact "trusted" pour isoler le test thématique
    settings.TRUSTED_DOMAINS = []
    settings.TRUSTED_SOFT_WEIGHT = 0.0

    # Paramètres filtre thématique
    settings.THEME_FILTER_SOFT_PENALTY = 0.20
    settings.THEME_FILTER_MIN_UNIGRAM_HITS = 2
    settings.THEME_FILTER_STRICT_DEFAULT = False  # soft par défaut

    # Stubs légers
    monkeypatch.setattr(pipeline, "compute_score", lambda *a, **k: 7.0)
    monkeypatch.setattr(pipeline.extraction, "run", lambda *a, **k: SimpleNamespace())
    monkeypatch.setattr(pipeline.angles, "run", lambda *a, **k: _angle_result_one())

    # keywords.run -> sets[0].keywords exploités par le filtre
    kw_stub = [SimpleNamespace(sets=[SimpleNamespace(angle_title="Moustique tigre", keywords=["moustique", "tigre", "aedes", "albopictus"])])]
    monkeypatch.setattr(pipeline.keywords, "run", lambda *a, **k: kw_stub)

    # Pas de viz pour ce test
    monkeypatch.setattr(pipeline.viz, "run", lambda *a, **k: [[]])

    # Pas de datasets côté connecteurs pour ce test
    monkeypatch.setattr(pipeline, "run_connectors", lambda *a, **k: [[]])

    # Deux sources LLM : 1 hors-thème (volcan), 1 sur-thème (aedes)
    def _llm_sources_stub(*a, **k):
        off = LLMSourceSuggestion(
            title="El Tigre volcano eruption dataset",
            description="eruption indicators and lava flow",
            link="https://example.com/eltigre",
            source="Other",
            angle_idx=0,
        )
        on = LLMSourceSuggestion(
            title="Surveillance Aedes albopictus (moustique tigre)",
            description="cartographie et données de présence",
            link="https://example.com/aedes-albopictus",
            source="Health",
            angle_idx=0,
        )
        return [[off, on]]
    monkeypatch.setattr(pipeline.llm_sources, "run", _llm_sources_stub)

    # Mémoire + packaging no-op
    monkeypatch.setattr(pipeline, "package", lambda *a, **k: (SimpleNamespace(), "md"))
    monkeypatch.setattr(pipeline, "get_memory", lambda *a, **k: SimpleNamespace(save_context=lambda *x, **y: None))

    # Exécution (soft: theme_strict=False)
    _, _, _, angle_resources = pipeline.run(
        "Texte article FR sur moustique tigre",
        user_id="u1",
        validate_urls=False,
        theme_strict=False,
    )

    ar = angle_resources[0]

    # SOURCES : l'item sur-thème doit être en premier
    src_titles = [s.title for s in ar.sources]
    assert src_titles[0].lower().startswith("surveillance aedes albopictus")
    assert any("volcano" in t.lower() for t in src_titles)  # présent mais après

    # DATASETS (issus du LLM via _llm_to_ds) : même ordre attendu
    ds_titles = [d.title for d in ar.datasets]
    assert ds_titles[0].lower().startswith("surveillance aedes albopictus")
    assert any("volcano" in t.lower() for t in ds_titles)


@pytest.mark.django_db
def test_theme_filter_strict_drops_off_theme_llm_but_keeps_connectors(settings, monkeypatch):
    """
    Strict mode: les items LLM hors-thème sont supprimés,
    mais les datasets des CONNECTORS restent (même s'ils sont hors-thème).
    """
    # Neutraliser "trusted"
    settings.TRUSTED_DOMAINS = []
    settings.TRUSTED_SOFT_WEIGHT = 0.0

    # Filtre thématique strict
    settings.THEME_FILTER_SOFT_PENALTY = 0.20
    settings.THEME_FILTER_MIN_UNIGRAM_HITS = 2
    settings.THEME_FILTER_STRICT_DEFAULT = False  # on forcera via paramètre

    monkeypatch.setattr(pipeline, "compute_score", lambda *a, **k: 7.0)
    monkeypatch.setattr(pipeline.extraction, "run", lambda *a, **k: SimpleNamespace())
    monkeypatch.setattr(pipeline.angles, "run", lambda *a, **k: _angle_result_one())
    kw_stub = [SimpleNamespace(sets=[SimpleNamespace(angle_title="Moustique tigre", keywords=["moustique", "tigre", "aedes", "albopictus"])])]
    monkeypatch.setattr(pipeline.keywords, "run", lambda *a, **k: kw_stub)
    monkeypatch.setattr(pipeline.viz, "run", lambda *a, **k: [[]])

    # CONNECTOR dataset (hors-thème exprès) — doit rester en strict
    def _run_connectors_stub(*a, **k):
        ds_conn = DatasetSuggestion(
            title="Crime data Los Angeles",
            description="off-topic on purpose",
            source_name="Example",
            source_url="https://example.com/crime-la",
            found_by="CONNECTOR",
            angle_idx=0,
            formats=[],
            organization=None,
            license=None,
            last_modified="",
            richness=0,
        )
        return [[ds_conn]]
    monkeypatch.setattr(pipeline, "run_connectors", _run_connectors_stub)

    # LLM : 1 hors-thème (volcan) + 1 sur-thème
    def _llm_sources_stub(*a, **k):
        off = LLMSourceSuggestion(
            title="El Tigre volcano eruption dataset",
            description="eruption indicators and lava flow",
            link="https://example.com/eltigre",
            source="Other",
            angle_idx=0,
        )
        on = LLMSourceSuggestion(
            title="Surveillance Aedes albopictus (moustique tigre)",
            description="cartographie et données de présence",
            link="https://example.com/aedes-albopictus",
            source="Health",
            angle_idx=0,
        )
        return [[off, on]]
    monkeypatch.setattr(pipeline.llm_sources, "run", _llm_sources_stub)

    # Mémoire + packaging no-op
    monkeypatch.setattr(pipeline, "package", lambda *a, **k: (SimpleNamespace(), "md"))
    monkeypatch.setattr(pipeline, "get_memory", lambda *a, **k: SimpleNamespace(save_context=lambda *x, **y: None))

    # Exécution en mode strict
    _, _, _, angle_resources = pipeline.run(
        "Texte article FR sur moustique tigre",
        user_id="u1",
        validate_urls=False,
        theme_strict=True,  # <- strict
    )

    ar = angle_resources[0]

    # SOURCES : l'hors-thème (volcan) doit avoir été supprimé
    src_titles = [s.title for s in ar.sources]
    assert all("volcano" not in t.lower() for t in src_titles)
    assert any("aedes" in t.lower() for t in src_titles)

    # DATASETS : le dataset CONNECTOR hors-thème DOIT rester (non filtré)
    ds_titles = [d.title.lower() for d in ar.datasets]
    assert any("crime data los angeles" in t for t in ds_titles)  # présent
    # Le dataset LLM hors-thème ne doit pas être présent
    assert all("volcano" not in t for t in ds_titles)
