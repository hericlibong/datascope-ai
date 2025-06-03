import pytest
from ai_engine.connectors.data_gov import DataGovClient, USDataset
from ai_engine.schemas import DatasetSuggestion

client = DataGovClient()

def test_search_returns_usdataset():
    results = list(client.search("covid", max_results=1))
    assert len(results) == 1
    ds = results[0]
    assert isinstance(ds, USDataset)
    assert ds.title
    assert ds.formats
    assert ds.organization is not None
    assert ds.license is not None
    assert ds.last_modified is not None

def test_us_to_suggestion_conversion():
    results = list(client.search("covid", max_results=1))
    ds = results[0]
    sugg = client.us_to_suggestion(ds)
    assert isinstance(sugg, DatasetSuggestion)
    assert sugg.source_name == "data.gov"
    assert sugg.richness >= 0 and sugg.richness <= 100
