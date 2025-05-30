import requests, os, time
from typing import Iterator
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential

BASE_URL = "https://www.data.gouv.fr/api/1"

class DGDataset(BaseModel):
    id: str
    title: str
    description: str | None = None
    url: str = Field(alias="page")          # page HTML du jeu
    organization: str | None = None
    formats: list[str] = []

# -------- retry HTTP -----------
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=4))
def _get(path: str, params: dict) -> dict:
    r = requests.get(f"{BASE_URL}{path}", params=params, timeout=10)
    r.raise_for_status()
    return r.json()

# -------- API wrapper ----------
def search(keyword: str, page_size: int = 20) -> Iterator[DGDataset]:
    """Yield DGDataset results for the given keyword (handles pagination)."""
    page = 1
    while True:
        data = _get("/datasets", {"q": keyword, "page": page, "page_size": page_size})
        for j in data["data"]:
            yield DGDataset(
                id=j["id"],
                title=j["title"],
                description=j.get("slug"),
                page=j["page"],
                organization=j.get("organization", {}).get("name"),
                formats=[r["format"] for r in j.get("resources", [])],
            )
        if not data["next_page"]:      # API renvoie False si fin
            break
        page += 1
        time.sleep(0.2)  # petite pause anti-dos
