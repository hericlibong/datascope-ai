"""
ai_engine.connectors.data_gov
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Client léger pour interroger le portail https://catalog.data.gov
— compatible avec le schéma interne DatasetSuggestion.
"""

from __future__ import annotations

import time
from typing import Iterator, List, Optional

import requests
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential

from ai_engine.schemas import DatasetSuggestion
from ai_engine.connectors.format_utils import get_format           # ← déjà écrit pour data.gouv
from ai_engine.connectors.helpers import sanitize_keyword            # ← idem
from ai_engine.connectors.cache_utils import cache_response 
from ai_engine.connectors.richness import richness_score                # ← simple decorateur TTL

BASE_URL = "https://catalog.data.gov/api/3/action"
DEFAULT_PAGE_SIZE = 20
VALID_FORMATS = {
    "csv", "json", "xls", "xlsx", "geojson", "xml",
    "shp", "zip", "pdf", "txt", "parquet"
}

# --------------------------------------------------------------------------- #
# 1) Modèle brut CKAN (US) --------------------------------------------------- #
# --------------------------------------------------------------------------- #

class USDataset(BaseModel):
    id: str
    title: str
    description: Optional[str] = Field(None, alias="notes")
    url: str = Field(..., alias="url")                 # HTML page
    organization: Optional[str] = Field(
        None, alias="organization.title"
    )
    formats: List[str] = []
    license: Optional[str] = Field(None, alias="license_title")
    last_modified: Optional[str] = Field(
        None, alias="metadata_modified"
    )

# --------------------------------------------------------------------------- #
# 2) Appel HTTP résilient ---------------------------------------------------- #
# --------------------------------------------------------------------------- #

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=4))
def _get(path: str, params: dict) -> dict:
    r = requests.get(f"{BASE_URL}{path}", params=params, timeout=10)
    r.raise_for_status()
    return r.json()

# --------------------------------------------------------------------------- #
# 3) Recherche paginée ------------------------------------------------------- #
# --------------------------------------------------------------------------- #

@cache_response(ttl_seconds=3600)
def search(keyword: str, *, page_size: int = DEFAULT_PAGE_SIZE) -> Iterator[USDataset]:
    """
    Itère sur les jeux de données CKAN correspondant au mot-clé.
    Gère la pagination (`rows` + `start`).
    """
    keyword = sanitize_keyword(keyword)
    start = 0

    while True:
        data = _get(
            "/package_search",
            {
                "q": keyword,
                "rows": page_size,
                "start": start,
            },
        )["result"]

        for raw in data["results"]:
            formats = list({
                fmt
                for res in (raw.get("resources") or [])
                if (fmt := get_format(res, valid_set=VALID_FORMATS))
            })

            yield USDataset(
                id=raw["id"],
                title=raw["title"],
                notes=raw.get("notes"),
                url=f"https://catalog.data.gov/dataset/{raw['name']}",
                organization=(raw.get("organization") or {}).get("title"),
                formats=formats,
                license_title=raw.get("license_title"),
                metadata_modified=raw.get("metadata_modified"),
            )

        # Pagination
        start += page_size
        if start >= data["count"]:
            break
        time.sleep(0.2)   # courtoisie

# --------------------------------------------------------------------------- #
# 4) Transformation → DatasetSuggestion ------------------------------------- #
# --------------------------------------------------------------------------- #

def us_to_suggestion(dataset: USDataset) -> DatasetSuggestion:
    """Mappe un USDataset vers notre schéma commun."""
    sugg = DatasetSuggestion(
        title         = dataset.title,
        description   = dataset.description,
        source_name   = "data.gouv.fr",
        source_url    = dataset.url,
        formats       = dataset.formats,
        organization  = dataset.organization,
        license       = dataset.license,
        last_modified = dataset.last_modified,
    )
    sugg.richness = richness_score(sugg)
    return sugg

# --------------------------------------------------------------------------- #
# 5) Interface minimaliste pour l’import "étoilé" --------------------------- #
# --------------------------------------------------------------------------- #

__all__ = ["search", "us_to_suggestion", "USDataset"]
