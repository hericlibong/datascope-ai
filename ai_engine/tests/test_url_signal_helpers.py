import pytest

# Les fonctions sont à implémenter côté ai_engine.url_utils
from ai_engine.url_utils import (
    is_pdf_url,
    has_data_path_token,
    has_data_format_signal,
    is_dataset_root_listing,
)


@pytest.mark.parametrize(
    "url,expected",
    [
        ("https://site.fr/doc.pdf", True),
        ("https://site.fr/DOC.PDF", True),
        ("https://site.fr/doc.pdf?download=1", True),
        ("https://site.fr/fichier.pdf#page=2", True),
        ("https://site.fr/fichierpdf", False),
        ("https://site.fr/fichier.pdfx", False),
        ("https://site.fr/?format=pdf", False),
    ],
)
def test_is_pdf_url(url, expected):
    """PDF detection should be case-insensitive and robust to query/fragment."""
    assert is_pdf_url(url) is expected


@pytest.mark.parametrize(
    "url,expected",
    [
        # vrais tokens "data-like"
        ("https://data.gouv.fr/fr/datasets/qualite-air", True),
        ("https://example.org/dataset/air-quality", True),
        ("https://example.org/datastore/search?q=moustique", True),
        ("https://example.org/statistics/incidence", True),
        ("https://example.org/api/3/action/package_search?q=albopictus", True),
        ("https://example.org/download/air.csv", True),
        ("https://example.org/geonetwork/srv/fre/catalog.search", True),
        ("https://example.org/catalog/datasets?q=heat", True),
        ("https://example.org/search?dataset=moustique", True),

        # faux positifs à éviter : "metadata" ne doit pas matcher "data"
        ("https://example.org/mediation/dossier", False),

        # neutres
        ("https://example.org/blog/post", False),
        ("https://example.org/about", False),
    ],
)
def test_has_data_path_token(url, expected):
    """
    Detect 'dataset-like' paths or query tokens.
    Must use token boundaries to avoid matching 'metadata'.
    """
    assert has_data_path_token(url) is expected


@pytest.mark.parametrize(
    "url,expected",
    [
        ("https://example.org/resource.csv", True),
        ("https://example.org/resource.CSV", True),
        # un simple format=json dans l’URL n’est pas un signal suffisant
        ("https://example.org/dl?format=json", False),
        ("https://example.org/geo/data.geojson?x=1", True),
        ("https://example.org/file.parquet", True),
        ("https://example.org/wfs?service=WFS&request=GetCapabilities", True),
        ("https://example.org/wms?SERVICE=WMS", True),
        ("https://example.org/api/endpoint", True),  # signal "API" générique

        ("https://example.org/file.txt", False),
        ("https://example.org/page?fmt=jsn", False),
        ("https://example.org/", False),
    ],
)
def test_has_data_format_signal(url, expected):
    """
    Detect file-format signals or data services in URL/query.
    Supported: csv/json/geojson/parquet + wfs/wms + '/api'.
    """
    assert has_data_format_signal(url) is expected


@pytest.mark.parametrize(
    "url,expected",
    [
        # Root listings: doivent être vraies
        ("https://www.data.gouv.fr/fr/datasets/", True),
        ("https://www.data.gouv.fr/datasets", True),
        ("https://catalog.example.org/datasets/", True),
        ("https://catalog.example.org/datasets", True),

        # Listings dynamiques : doivent AUSSI être considérés comme root listings
        ("https://www.data.gouv.fr/fr/datasets/qualite-air", False),
        ("https://www.data.gouv.fr/fr/datasets/?q=moustique", True),
        ("https://www.data.gouv.fr/fr/datasets?page=2", True),
        ("https://catalog.example.org/dataset/heat-risk", False),
    ],
)
def test_is_dataset_root_listing(url, expected):
    """
    Detect '/datasets' listings (root or dynamic search pages).
    They are listings to downrank, not concrete datasets.
    """
    assert is_dataset_root_listing(url) is expected

