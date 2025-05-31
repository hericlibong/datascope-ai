# ai_engine/tests/test_data_gouv.py

import responses
import json
from ai_engine.connectors.data_gouv import search, DGDataset

MOCK_API_RESPONSE = {
    "data": [
        {
            "id": "mock-id-123",
            "title": "Densité de médecins",
            "slug": "densite-medecins",
            "page": "https://www.data.gouv.fr/fr/datasets/mock-id-123",
            "organization": {"name": "Ministère de la santé"},
            "resources": [
                {"format": "csv", "url": "https://example.com/data.csv"}
            ]
        }
    ],
    "next_page": False
}


@responses.activate
def test_search_returns_dataset_list():
    keyword = "sante"
    api_url = "https://www.data.gouv.fr/api/1/datasets"

    responses.add(
        responses.GET,
        api_url,
        json=MOCK_API_RESPONSE,
        status=200
    )

    # Exécute la fonction de recherche
    results = list(search(keyword))

    assert len(results) == 1
    dataset = results[0]
    assert isinstance(dataset, DGDataset)
    assert dataset.title == "Densité de médecins"
    assert dataset.formats == ["csv"]
    assert dataset.organization == "Ministère de la santé"
