"""
Connecteur Data.gouv
--------------------
– recherche paginée
– mapping vers le schéma interne
– calcul du score de richesse
"""
from __future__ import annotations

import re, time, requests
from pathlib import Path
from typing import Iterator, Optional

from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential

from ai_engine.schemas import DatasetSuggestion
from ai_engine.connectors.cache_utils import cache_response
from ai_engine.connectors.helpers import sanitize_keyword
from ai_engine.connectors.richness import richness_score   # ← score Richesse
from ai_engine.connectors.format_utils import get_format

BASE_URL = "https://www.data.gouv.fr/api/1"
VALID_FORMATS = {"csv","xls","xlsx","json","geojson","xml","shp","zip","pdf"}

# ------------------------------------------------------------------ #
# Modèle brut Data.gouv                                              #
# ------------------------------------------------------------------ #
class DGDataset(BaseModel):
    id: str
    title: str
    description: str | None = None
    url: str = Field(alias="page")              # page HTML officielle
    organization: str | None = None
    formats: list[str] = []
    license: str | None = None                  # ← ajouté
    last_modified: str | None = None            # ← ajouté (ISO-8601)


# ------------------------------------------------------------------ #
# GET with retry                                                     #
# ------------------------------------------------------------------ #
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=4))
def _get(path: str, params: dict) -> dict:
    r = requests.get(f"{BASE_URL}{path}", params=params, timeout=10)
    r.raise_for_status()
    return r.json()

# ------------------------------------------------------------------ #
# Recherche paginée                                                  #
# ------------------------------------------------------------------ #
@cache_response(ttl_seconds=3600)
def search(keyword: str, page_size: int = 20) -> Iterator[DGDataset]:
    """Itère sur tous les jeux répondant au mot-clé `keyword`."""
    keyword = sanitize_keyword(keyword)
    page = 1

    while True:
        data = _get("/datasets", {"q": keyword, "page": page, "page_size": page_size})

        for j in data["data"]:
            # formats uniques en filtrant les None
            formats = []
            for res in j.get("resources",[]):
                fmt = get_format(res, valid_set=VALID_FORMATS)
                if fmt:
                    formats.append(fmt)
            formats = list(set(formats))

            yield DGDataset(
                id            = j["id"],
                title         = j["title"],
                description   = j.get("slug"),
                page          = j["page"],
                organization  = (j.get("organization") or {}).get("name"),
                formats       = formats,
                license       = j.get("license"),
                last_modified = j.get("metadata_modified")
                                  or j.get("modified") or j.get("last_modified"),
            )

        if not data["next_page"]:
            break
        page += 1
        time.sleep(0.2)          # micro-pause pour ne pas spammer l’API

# ------------------------------------------------------------------ #
# Mapping vers le schéma interne                                     #
# ------------------------------------------------------------------ #
def dg_to_suggestion(dataset: DGDataset) -> DatasetSuggestion:
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
