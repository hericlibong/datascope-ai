import pytest

from ai_engine.connectors.data_gov import DataGovClient
from ai_engine.connectors.data_gouv import DataGouvClient
from ai_engine.connectors.data_canada import CanadaGovClient
from ai_engine.connectors.hdx_data import HdxClient
from ai_engine.connectors.data_uk import UKGovClient
from ai_engine.schemas import DatasetSuggestion

clients = [DataGovClient(), DataGouvClient(), CanadaGovClient(), HdxClient(), UKGovClient()]

@pytest.mark.integration
def test_connectors_implement_interface():
    for client in clients:
        results = client.search("climate", page_size=5)
        for i, ds in enumerate(results):
            if i >= 1:  # ← limite temporaire : 1 seul résultat
                break
            if "GovClient" in client.__class__.__name__:
                suggestion = client.us_to_suggestion(ds)
            else:
                suggestion = client.fr_to_suggestion(ds)

            assert isinstance(suggestion, DatasetSuggestion)
            assert suggestion.title
            assert suggestion.source_url.startswith("https://")
            assert 0 <= suggestion.richness <= 100
