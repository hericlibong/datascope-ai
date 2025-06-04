# ai_engine/tests/test_data_canada_client.py

import pytest
from ai_engine.connectors.data_canada import CanadaGovClient, CADataset
from ai_engine.schemas import DatasetSuggestion

@pytest.fixture
def client():
    return CanadaGovClient()

def test_search_returns_iterator(client):
    results = client.search("énergie", page_size=5)
    assert hasattr(results, '__iter__')

def test_search_returns_datasets(client):
    results = list(client.search("énergie", page_size=5))
    assert all(isinstance(ds, CADataset) for ds in results)
    assert len(results) <= 2  # max_results

def test_ca_to_suggestion_fields(client):
    results = list(client.search("énergie", page_size=5))
    if results:
        suggestion = client.ca_to_suggestion(results[0])
        assert isinstance(suggestion, DatasetSuggestion)
        assert suggestion.title
        assert suggestion.source_url.startswith("https://")
        assert isinstance(suggestion.richness, int)
        assert 0 <= suggestion.richness <= 100
