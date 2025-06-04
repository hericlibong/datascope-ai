"""
Connecteur HDX (Humanitarian Data Exchange)
-------------------------------------------
– Conforme à ConnectorInterface
– Utilise l'API CKAN de data.humdata.org
– Pas besoin de clé API
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

BASE_URL = "https://data.humdata.org"
VALID_FORMATS = {"csv", "xls", "xlsx", "json", "geojson", "xml", "zip", "pdf"}

# ------------------------------------------------------------------ #
# Modèle brut HDX                                                    #
# ------------------------------------------------------------------ #
class HdxDataset(BaseModel):
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
class HdxClient(ConnectorInterface):
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(1, 1, 4))
    def _get(self, path: str, params: dict) -> dict:
        r = requests.get(f"{BASE_URL}{path}", params=params, timeout=10)
        r.raise_for_status()
        return r.json()

    def search(self, keyword: str, page_size: int = 10) -> Iterator[HdxDataset]:
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
                fmt_list = [
                    f for r in raw.get("resources", [])
                    if (f := get_format(r, VALID_FORMATS))
                ]
                if not fmt_list:
                    continue

                org_raw = raw.get("organization")
                org_name = org_raw.get("title") if isinstance(org_raw, dict) else None

                yield HdxDataset(
                    id=raw["id"],
                    title=raw.get("title"),
                    description=raw.get("notes"),
                    url=f"{BASE_URL}/dataset/{raw['name']}",
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

    def hdx_to_suggestion(self, ds: HdxDataset) -> DatasetSuggestion:
        sugg = DatasetSuggestion(
            title=ds.title,
            description=ds.description,
            source_name="data.humdata.org",
            source_url=ds.url,
            formats=ds.formats,
            organization=ds.organization,
            license=ds.license,
            last_modified=ds.last_modified,
        )
        sugg.richness = richness_score(sugg)
        return sugg

__all__ = ["HdxDataset", "HdxClient"]
