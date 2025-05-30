import requests, time
from typing import Iterator
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential

BASE_URL = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0"

class EurostatDataset(BaseModel):
    code: str
    title: str
    url: str

# ----------- retry HTTP -----------
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=4))
def _get(path: str, params: dict) -> dict:
    r = requests.get(f"{BASE_URL}{path}", params=params, timeout=10)
    r.raise_for_status()
    return r.json()

# ----------- wrapper --------------
def search(keyword: str, lang: str = "en") -> Iterator[EurostatDataset]:
    """
    Recherche de jeux de données Eurostat via l’endpoint /dataflow.
    """
    data = _get(
        "/dataflow",
        {
            "searchText": keyword,
            "filters": f"language:{lang}",
            "format": "JSON",
        },
    )

    for flow in data.get("dataflows", []):
        yield EurostatDataset(
            code=flow["id"],
            title=flow["name"],
            url=f"https://ec.europa.eu/eurostat/databrowser/view/{flow['id']}/default/table",
        )
        time.sleep(0.1)          # micro-pause anti-DOS
