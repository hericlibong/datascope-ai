import pytest
from ai_engine.url_utils import is_dataset_like_url

# URLs qui DOIVENT être reconnues comme dataset-like
@pytest.mark.parametrize(
    "url",
    [
        "https://www.data.gouv.fr/fr/datasets/qualite-air",
        "https://insee.fr/fr/statistiques/serie-chronologique",
        "https://ec.europa.eu/eurostat/statistics-explained/index.php/Energy",
        "https://oecd.org/catalog/search?q=energy",
        # "https://worldbank.org/data",
        "https://api.example.org/v1/data",
        "https://portal.org/download/file.csv",
        "https://portal.org/datastore/123",
        "https://foo.org/en/search?q=foo",
    ],
)
def test_is_dataset_like_true(url):
    assert is_dataset_like_url(url) is True


# URLs qui NE DOIVENT PAS être reconnues comme dataset-like
@pytest.mark.parametrize(
    "url",
    [
        "https://insee.fr/",
        "https://insee.fr/fr",
        "https://oecd.org/about",
        "https://portal.org/en",
        "https://example.org/contact",
        "",
    ],
)
def test_is_dataset_like_false(url):
    assert is_dataset_like_url(url) is False