import pytest
from ai_engine.connectors.data_gouv import DataGouvClient, FRDataset
from ai_engine.schemas import DatasetSuggestion

@pytest.fixture
def client():
    return DataGouvClient()

def test_search_returns_iterator(client):
    results = client.search("santé", page_size=5)
    assert hasattr(results, '__iter__')

def test_search_returns_datasets(client):
    results = list(client.search("santé", page_size=5))
    assert all(isinstance(ds, FRDataset) for ds in results)
    assert len(results) <= 2  # max_results=2 dans l’implémentation actuelle

def test_fr_to_suggestion_fields(client):
    results = list(client.search("santé", page_size=5))
    if results:
        suggestion = client.fr_to_suggestion(results[0])
        assert isinstance(suggestion, DatasetSuggestion)
        assert suggestion.title
        assert suggestion.source_url.startswith("https://")
        assert isinstance(suggestion.richness, int)
        assert 0 <= suggestion.richness <= 100
