"""
ai_engine.connectors.data_gov
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Client léger pour interroger https://catalog.data.gov
et renvoyer des objets compatibles DatasetSuggestion.
"""

from __future__ import annotations

import time
from functools import lru_cache
from typing import Iterator, List, Optional

import requests
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential

from ai_engine.schemas import DatasetSuggestion
from ai_engine.connectors.format_utils import get_format
from ai_engine.connectors.helpers import sanitize_keyword
from ai_engine.connectors.richness import richness_score

# ----------------------------------------------------------------------------
# Constantes
# ----------------------------------------------------------------------------
BASE_URL           = "https://catalog.data.gov/api/3/action"
DEFAULT_PAGE_SIZE  = 20
VALID_FORMATS      = {
    "csv", "json", "xls", "xlsx", "geojson", "xml",
    "shp", "zip", "pdf", "txt", "parquet"
}
HEADERS            = {
    "Accept-Encoding": "gzip",
    "User-Agent": "DatascopeBot/0.1"
}

# ----------------------------------------------------------------------------
# 1. Modèle brut CKAN
# ----------------------------------------------------------------------------

class USDataset(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    url: str
    organization: Optional[str] = None
    formats: List[str] = []
    license: Optional[str] = None
    last_modified: Optional[str] = None


# ----------------------------------------------------------------------------
# 2. Appel HTTP résilient
# ----------------------------------------------------------------------------
@retry(stop=stop_after_attempt(3), wait=wait_exponential(1, 1, 4))
def _get(path: str, params: dict) -> dict:
    r = requests.get(
        f"{BASE_URL}{path}",
        headers=HEADERS,
        params=params,
        timeout=(5, 8)       # (connexion, lecture)
    )
    r.raise_for_status()
    return r.json()

# ----------------------------------------------------------------------------
# 3. Appel mémoïsé à /package_show  (enrichissement ponctuel)
# ----------------------------------------------------------------------------
@lru_cache(maxsize=256)
def _package_show(pkg_id: str) -> dict:
    return _get("/package_show", {"id": pkg_id})["result"]

# ----------------------------------------------------------------------------
# 4. Recherche paginée
# ----------------------------------------------------------------------------
def search(
    keyword: str,
    *,
    page_size: int = DEFAULT_PAGE_SIZE,
) -> Iterator[USDataset]:
    """
    Générateur de jeux de données enrichis.
    – Appel principal : /package_search (rapide, facets off)
    – Fallback : /package_show si org/licence/date ou formats manquants
    – Ignore les jeux SANS fichier.
    """
    keyword = sanitize_keyword(keyword)
    start   = 0

    while True:
        data = _get(
            "/package_search",
            {
                "q": keyword,
                "rows": page_size,
                "start": start,
                "facet": "false",
            },
        )["result"]

        for raw in data["results"]:
            # --  formats présents dans /package_search  --------------------
            fmt_list = [
                f for r in raw.get("resources", [])
                if (f := get_format(r, VALID_FORMATS))
            ]

            # --  métadonnées présentes (org peut être dict ou str ID) ------
            org_raw  = raw.get("organization")
            org_name = (
                org_raw.get("title") or org_raw.get("name")
                if isinstance(org_raw, dict) else None
            )
            license_ = raw.get("license_title")
            lastmod  = raw.get("metadata_modified")

            # --  Fallback package_show si une info manque -------------------
            need_fallback = (
                org_name is None or not license_ or not lastmod or not fmt_list
            )
            if need_fallback:
                detail = _package_show(raw["id"])
                # organisation
                if org_name is None and isinstance(detail.get("organization"), dict):
                    org = detail["organization"]
                    org_name = org.get("title") or org.get("name")
                # licence / date
                license_ = license_ or detail.get("license_title")
                lastmod  = lastmod  or detail.get("metadata_modified")
                # formats
                if not fmt_list:
                    fmt_list = [
                        f for r in detail.get("resources", [])
                        if (f := get_format(r, VALID_FORMATS))
                    ]

            # --  on ignore définitivement s'il n'y a toujours aucun fichier --
            if not fmt_list:
                continue

            yield USDataset(
                id            = raw["id"],
                title         = raw["title"],
                description   = raw.get("notes"),
                url           = f"https://catalog.data.gov/dataset/{raw['name']}",
                organization  = org_name,
                formats       = list(set(fmt_list)),
                license       = license_,
                last_modified = lastmod,
            )

        # --------- pagination ----------
        start += page_size
        if start >= data["count"]:
            break
        time.sleep(0.2)          # courtoisie

# ----------------------------------------------------------------------------
# 5. Mapping vers DatasetSuggestion
# ----------------------------------------------------------------------------
def us_to_suggestion(ds: USDataset) -> DatasetSuggestion:
    sugg = DatasetSuggestion(
        title         = ds.title,
        description   = ds.description,
        source_name   = "data.gov",
        source_url    = ds.url,
        formats       = ds.formats,
        organization  = ds.organization,
        license       = ds.license,
        last_modified = ds.last_modified,
    )
    sugg.richness = richness_score(sugg)
    return sugg

# ----------------------------------------------------------------------------
# 6. Exports
# ----------------------------------------------------------------------------
__all__ = ["search", "us_to_suggestion", "USDataset"]
