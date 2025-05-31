import requests, os, time
from typing import Iterator
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential
from ai_engine.schemas import DatasetSuggestion
from ai_engine.connectors.cache_utils import cache_response
import re


BASE_URL = "https://www.data.gouv.fr/api/1"
VALID_FORMATS = {"csv", "xls", "xlsx", "json", "geojson", "xml", "shp", "zip", "pdf"}

# Fonction robuste pour extraire le format d'une ressource
def get_format(resource: dict) -> str | None:
    # 1. Format déclaré (csv, json, etc.)
    fmt = resource.get("format", "").lower()
    if fmt in VALID_FORMATS:
        return fmt

    # 2. Mime type
    mime = (resource.get("mime") or resource.get("mimetype") or "").lower()
    if "csv" in mime:
        return "csv"
    if "excel" in mime or "spreadsheet" in mime or "xls" in mime:
        return "xls"
    if "json" in mime:
        return "json"
    if "geojson" in mime:
        return "geojson"
    if "xml" in mime:
        return "xml"
    if "shp" in mime:
        return "shp"
    if "zip" in mime:
        return "zip"
    if "pdf" in mime:
        return "pdf"

    # 3. Extension du fichier dans l'URL
    url = resource.get("url", "")
    ext = re.search(r"\.([a-z0-9]{2,5})(?:[\?#]|$)", url)
    if ext:
        ext = ext.group(1).lower()
        if ext in VALID_FORMATS:
            return ext

    return None



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
@cache_response(ttl_seconds=3600)
def search(keyword: str, page_size: int = 20) -> Iterator[DGDataset]:
    """Yield DGDataset results for the given keyword (handles pagination)."""
    page = 1
    while True:
        data = _get("/datasets", {"q": keyword, "page": page, "page_size": page_size})
        for j in data["data"]:
            formats = list({
                get_format(r)
                for r in j.get("resources", [])
                if get_format(r)
            })
            yield DGDataset(
                id=j["id"],
                title=j["title"],
                description=j.get("slug"),
                page=j["page"],
                organization=j.get("organization", {}).get("name"),
                formats=formats,
            )
        if not data["next_page"]:      # API renvoie False si fin
            break
        page += 1
        time.sleep(0.2)  # petite pause anti-dos


def dg_to_suggestion(dataset: DGDataset) -> DatasetSuggestion:
    return DatasetSuggestion(
        title=dataset.title,
        description=dataset.description,
        source_name="data.gouv.fr",
        source_url=dataset.url,
        formats=dataset.formats,
        organization=dataset.organization,
        license=None  # l'API data.gouv ne fournit pas toujours ça directement
    )
