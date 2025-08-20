"""
Connecteur Data.gouv (France)
-----------------------------
– Conforme à ConnectorInterface
– Recherche paginée avec fallback minimum
– Conversion vers DatasetSuggestion
"""

from __future__ import annotations

import time
from typing import Iterator, List, Optional

import requests
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential

from ai_engine.connectors.interface import ConnectorInterface
from ai_engine.connectors.helpers import sanitize_keyword
from ai_engine.connectors.format_utils import get_format
from ai_engine.connectors.richness import richness_score
from ai_engine.connectors.location_utils import (
    enhance_query_with_locations, 
    filter_and_sort_by_location_relevance
)
from ai_engine.schemas import DatasetSuggestion

BASE_URL = "https://www.data.gouv.fr/api/1"
VALID_FORMATS = {"csv", "xls", "xlsx", "json", "geojson", "xml", "shp", "zip", "pdf"}

# ------------------------------------------------------------------ #
# Modèle brut Data.gouv                                              #
# ------------------------------------------------------------------ #
class FRDataset(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    url: str
    organization: Optional[str] = None
    formats: List[str] = []
    license: Optional[str] = None
    last_modified: Optional[str] = None

# ------------------------------------------------------------------ #
# Client conforme à ConnectorInterface                               #
# ------------------------------------------------------------------ #
class DataGouvClient(ConnectorInterface):
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(1, 1, 4))
    def _get(self, path: str, params: dict) -> dict:
        r = requests.get(f"{BASE_URL}{path}", params=params, timeout=10)
        r.raise_for_status()
        return r.json()

    def search(self, keyword: str, *, page_size: int = 10, locations: Optional[List[str]] = None) -> Iterator[FRDataset]:
        # Enhance query with location information if available
        enhanced_keyword = enhance_query_with_locations(keyword, locations)
        enhanced_keyword = sanitize_keyword(enhanced_keyword)
        
        page = 1
        max_results = 2  # ← sécurité temporaire, évite de tout renvoyer
        all_datasets = []  # Collect datasets for location-based sorting

        yielded = 0
        while yielded < max_results:
            data = self._get("/datasets", {"q": enhanced_keyword, "page": page, "page_size": page_size})
            results = data.get("data", [])
            if not results:
                break

            page_datasets = []
            for raw in results:
                # Récupération des formats valides
                fmt_list = [
                    f for r in raw.get("resources", [])
                    if (f := get_format(r, VALID_FORMATS))
                ]
                if not fmt_list:
                    continue

                org_raw = raw.get("organization")
                org_name = org_raw.get("name") or org_raw.get("title") if isinstance(org_raw, dict) else None

                license_ = raw.get("license")
                if isinstance(license_, dict):
                    license_ = license_.get("title") or license_.get("id")

                dataset = FRDataset(
                    id=raw["id"],
                    title=raw["title"],
                    description=raw.get("slug"),
                    url=raw["page"],
                    organization=org_name,
                    formats=list(set(fmt_list)),
                    license=license_,
                    last_modified=raw.get("metadata_modified")
                        or raw.get("modified")
                        or raw.get("last_modified"),
                )
                page_datasets.append(dataset)

            # Apply location-based sorting to this page
            if locations:
                page_datasets = filter_and_sort_by_location_relevance(page_datasets, locations)
            
            # Yield datasets up to max_results
            for dataset in page_datasets:
                if yielded >= max_results:
                    break
                yield dataset
                yielded += 1

            if not data.get("next_page") or yielded >= max_results:
                break

            page += 1
            time.sleep(0.2)

    def fr_to_suggestion(self, ds: FRDataset) -> DatasetSuggestion:
        sugg = DatasetSuggestion(
            title=ds.title,
            description=ds.description,
            source_name="data.gouv.fr",
            source_url=ds.url,
            formats=ds.formats,
            organization=ds.organization,
            license=ds.license,
            last_modified=ds.last_modified,
        )
        sugg.richness = richness_score(sugg)
        return sugg

# ------------------------------------------------------------------ #
# Exports                                                            #
# ------------------------------------------------------------------ #
__all__ = ["FRDataset", "DataGouvClient"]
