"""
Connecteur Open Canada
----------------------
– Conforme à ConnectorInterface
– API CKAN v3 : /api/3/action/package_search
– Métadonnées bilingues (fr/en) → fallback prévu
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
from ai_engine.schemas import DatasetSuggestion

BASE_URL = "https://open.canada.ca/data"
VALID_FORMATS = {"csv", "xls", "xlsx", "json", "geojson", "xml", "zip", "pdf"}

# ------------------------------------------------------------------ #
# Modèle brut Canada                                                 #
# ------------------------------------------------------------------ #
class CADataset(BaseModel):
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
class CanadaGovClient(ConnectorInterface):
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(1, 1, 4))
    def _get(self, path: str, params: dict) -> dict:
        r = requests.get(f"{BASE_URL}{path}", params=params, timeout=10)
        r.raise_for_status()
        return r.json()

    def search(self, keyword: str, page_size: int = 10) -> Iterator[CADataset]:
        keyword = sanitize_keyword(keyword)
        page = 0
        max_results = 2  # ← temporaire

        yielded = 0
        while yielded < max_results:
            data = self._get(
                "/api/3/action/package_search",
                {"q": keyword, "rows": page_size, "start": page * page_size}
            )

            results = data.get("result", {}).get("results", [])
            if not results:
                break

            for raw in results:
                # Formats disponibles
                fmt_list = [
                    f for r in raw.get("resources", [])
                    if (f := get_format(r, VALID_FORMATS))
                ]
                if not fmt_list:
                    continue

                org_raw = raw.get("organization")
                org_name = org_raw.get("title") if isinstance(org_raw, dict) else None

                title = raw.get("title_translated", {}).get("en") or raw.get("title")
                description = raw.get("notes_translated", {}).get("en") or raw.get("notes")

                yield CADataset(
                    id=raw["id"],
                    title=title,
                    description=description,
                    url=f"https://open.canada.ca/data/en/dataset/{raw['id']}",
                    organization=org_name,
                    formats=list(set(fmt_list)),
                    license=raw.get("license_title"),
                    last_modified=raw.get("metadata_modified")
                )
                yielded += 1
                if yielded >= max_results:
                    break

            page += 1
            time.sleep(0.2)

    def ca_to_suggestion(self, ds: CADataset) -> DatasetSuggestion:
        sugg = DatasetSuggestion(
            title=ds.title,
            description=ds.description,
            source_name="open.canada.ca",
            source_url=ds.url,
            formats=ds.formats,
            organization=ds.organization,
            license=ds.license,
            last_modified=ds.last_modified,
        )
        sugg.richness = richness_score(sugg)
        return sugg

__all__ = ["CADataset", "CanadaGovClient"]
