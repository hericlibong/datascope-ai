import pytest

# Fonctions à implémenter (ou compléter) côté backend :
# - classify_kind_from_url : renvoie "dataset" ou "source" selon l'URL
# - dataset_root_soft_weight : renvoie un multiplicateur < 1.0 si '/datasets' nu
#
# Si tu préfères implémenter la classification ailleurs, adapte les imports.
from ai_engine.url_utils import classify_kind_from_url
from ai_engine.ranking import dataset_root_soft_weight


def test_pdf_is_always_source():
    """
    Reclassement : une URL PDF doit être considérée comme 'source' (documentation),
    même si l'URL contient des mots-clés 'data-like'.
    """
    url = "https://example.org/report/moustique_tigre_2024.pdf"
    assert classify_kind_from_url(url) == "source"


@pytest.mark.parametrize(
    "url",
    [
        "https://data.gouv.fr/fr/dataset/qualite-air",
        "https://catalog.example.org/dataset/aedes-albopictus",
        "https://portal.example.org/api/3/action/package_show?id=aedes",
        "https://portal.example.org/datastore/search?q=aedes",
    ],
)
def test_dataset_slug_or_api_is_dataset(url):
    """
    Reclassement : les URLs 'dataset-like' (slug CKAN, datastore, API package_show/search)
    doivent aboutir à 'dataset'.
    """
    assert classify_kind_from_url(url) == "dataset"


@pytest.mark.parametrize(
    "url,penalty,expected",
    [
        ("https://data.gouv.fr/fr/datasets/", 0.20, 0.80),
        ("https://catalog.example.org/datasets", 0.15, 0.85),
        # Pas une liste racine -> poids inchangé
        ("https://data.gouv.fr/fr/datasets/qualite-air", 0.20, 1.00),
        ("https://data.gouv.fr/fr/datasets/?q=aedes", 0.20, 1.00),
    ],
)
def test_root_datasets_listing_downrank(url, penalty, expected):
    """
    Downrank : une URL '/datasets' (sans slug ni query) doit subir une pénalité
    multiplicative (poids *= 1 - penalty). Les autres ne sont pas pénalisées.
    """
    w = dataset_root_soft_weight(url, penalty=penalty)
    assert pytest.approx(w, rel=1e-6) == expected
