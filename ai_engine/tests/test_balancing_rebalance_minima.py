from ai_engine.balancing import rebalance_minima
from ai_engine.url_utils import is_dataset_like_url


def _mk(url: str):
    return {"link": url}


def _unique(lst):
    seen = set()
    for it in lst:
        u = it.get("link") or it.get("source_url")
        assert u not in seen, f"duplicate URL detected: {u}"
        seen.add(u)


def test_rebalance_moves_dataset_like_from_sources():
    # datasets: 1 item only
    datasets = [
        _mk("https://site.org/page"),  # source-like
    ]
    # sources: 5 items (3 dataset-like, 2 non)
    sources = [
        _mk("https://portal.org/datasets/energy"),         # dataset-like
        _mk("https://portal.org/about"),                    # non dataset-like
        _mk("https://portal.org/catalog/search?q=energy"),  # dataset-like
        _mk("https://portal.org/"),                         # homepage
        _mk("https://portal.org/statistics/energy"),        # dataset-like
    ]

    rebalance_minima(datasets, sources, 3, 3, is_dataset_like_url)

    # Vérifie les tailles finales 3/3
    assert len(datasets) == 3
    assert len(sources) == 3

    # Les deux premiers mouvements doivent être les dataset-like rencontrés en priorité
    moved_urls = {"https://portal.org/datasets/energy", "https://portal.org/catalog/search?q=energy", "https://portal.org/statistics/energy"}
    # Deux de ces trois doivent maintenant se trouver dans datasets
    assert sum(1 for it in datasets if it["link"] in moved_urls) >= 2

    # Pas de doublon entre listes
    _unique(datasets)
    _unique(sources)


def test_rebalance_prefers_source_like_from_datasets():
    # datasets surabondant, sources insuffisant
    datasets = [
        _mk("https://foo.org/data/datasets/a"),   # dataset-like
        _mk("https://foo.org/info"),              # source-like
        _mk("https://foo.org/statistics/b"),      # dataset-like
        _mk("https://foo.org/about"),             # source-like
        _mk("https://foo.org/download/c"),        # dataset-like
    ]
    sources = [
        _mk("https://bar.org/"),  # homepage
    ]

    rebalance_minima(datasets, sources, 3, 3, is_dataset_like_url)

    # On doit atteindre au moins 3 sources sans descendre sous 3 datasets
    assert len(sources) >= 3
    assert len(datasets) >= 3

    # Les éléments non dataset-like ont été déplacés en priorité
    moved_to_sources = {it["link"] for it in sources}
    assert "https://foo.org/info" in moved_to_sources
    assert "https://foo.org/about" in moved_to_sources

    # Pas de doublon
    _unique(datasets)
    _unique(sources)