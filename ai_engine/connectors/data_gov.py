"""
ai_engine.connectors.data_gov
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Connecteur léger pour https://catalog.data.gov
– Recherche paginée
– Fallback /package_show pour métadonnées manquantes
– Conversion vers DatasetSuggestion
"""

from __future__ import annotations

import time
from functools import lru_cache
from typing import Iterator, List, Optional

import requests
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential

from ai_engine.schemas import DatasetSuggestion
from ai_engine.connectors.format_utils import get_format
from ai_engine.connectors.helpers import sanitize_keyword
from ai_engine.connectors.richness import richness_score
from ai_engine.connectors.interface import ConnectorInterface

# --------------------------------------------------------------------------- #
# 0. Constantes                                                               #
# --------------------------------------------------------------------------- #
BASE_URL = "https://catalog.data.gov/api/3/action"
DEFAULT_PAGE_SIZE = 1
VALID_FORMATS = {
    "csv", "json", "xls", "xlsx", "geojson", "xml",
    "shp", "zip", "pdf", "txt", "parquet"
}
HEADERS = {
    "Accept-Encoding": "gzip",
    "User-Agent": "DatascopeBot/0.1"
}

# --------------------------------------------------------------------------- #
# 1. Modèle brut CKAN (après enrichissement éventuel)                         #
# --------------------------------------------------------------------------- #
class USDataset(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    url: str
    organization: Optional[str] = None
    formats: List[str] = []
    license: Optional[str] = None
    last_modified: Optional[str] = None


# --------------------------------------------------------------------------- #
# 2. Client orienté interface                                                 #
# --------------------------------------------------------------------------- #
class DataGovClient(ConnectorInterface):
    """Client haut-niveau conforme à ConnectorInterface."""

    # ----------- Helpers internes ------------------------------------------ #
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(1, 1, 4))
    def _get(self, path: str, params: dict) -> dict:
        r = requests.get(
            f"{BASE_URL}{path}",
            headers=HEADERS,
            params=params,
            timeout=(5, 8)
        )
        r.raise_for_status()
        return r.json()

    @lru_cache(maxsize=256)
    def _package_show(self, pkg_id: str) -> dict:
        """Mémoïse /package_show pour limiter les appels réseau."""
        return self._get("/package_show", {"id": pkg_id})["result"]

    # ----------- API publique --------------------------------------------- #
    def search(self, keyword: str, *, page_size: int = DEFAULT_PAGE_SIZE, max_results: Optional[int] = None, locations: Optional[List[str]] = None) -> Iterator[USDataset]:
        """
        Générateur de USDataset.

        - Appelle /package_search (pagination)
        - Appelle /package_show si org/licence/date/formats manquants
        - Ignore les jeux sans ressource exploitable
        - Interrompt si max_results atteint
        """
        keyword = sanitize_keyword(keyword)
        start = 0
        count = 0  # nombre total émis

        while True:
            page = self._get(
                "/package_search",
                {
                    "q": keyword,
                    "rows": page_size,
                    "start": start,
                    "facet": "false",
                },
            )["result"]

            for raw in page["results"]:
                if max_results is not None and count >= max_results:
                    return

                fmt_list = [
                    f for r in raw.get("resources", [])
                    if (f := get_format(r, VALID_FORMATS))
                ]

                org_raw = raw.get("organization")
                org_name = (
                    org_raw.get("title") or org_raw.get("name")
                    if isinstance(org_raw, dict) else None
                )
                license_ = raw.get("license_title")
                lastmod = raw.get("metadata_modified")

                if org_name is None or not license_ or not lastmod or not fmt_list:
                    detail = self._package_show(raw["id"])
                    if org_name is None and isinstance(detail.get("organization"), dict):
                        org = detail["organization"]
                        org_name = org.get("title") or org.get("name")
                    license_ = license_ or detail.get("license_title")
                    lastmod = lastmod or detail.get("metadata_modified")
                    if not fmt_list:
                        fmt_list = [
                            f for r in detail.get("resources", [])
                            if (f := get_format(r, VALID_FORMATS))
                        ]

                if not fmt_list:
                    continue

                yield USDataset(
                    id=raw["id"],
                    title=raw["title"],
                    description=raw.get("notes"),
                    url=f"https://catalog.data.gov/dataset/{raw['name']}",
                    organization=org_name,
                    formats=list(set(fmt_list)),
                    license=license_,
                    last_modified=lastmod,
                )
                count += 1

            start += page_size
            if start >= page["count"]:
                break
            time.sleep(0.2)


    def us_to_suggestion(self, ds: USDataset) -> DatasetSuggestion:
        sugg = DatasetSuggestion(
            title=ds.title,
            description=ds.description,
            source_name="data.gov",
            source_url=ds.url,
            formats=ds.formats,
            organization=ds.organization,
            license=ds.license,
            last_modified=ds.last_modified,
        )
        sugg.richness = richness_score(sugg)
        return sugg


# --------------------------------------------------------------------------- #
# 3. Exports                                                                  #
# --------------------------------------------------------------------------- #
__all__ = ["USDataset", "DataGovClient"]
