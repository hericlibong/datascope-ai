# ai_engine/connectors/richness.py
from __future__ import annotations
import datetime as dt
from datetime import datetime, timezone
from typing import List

from ai_engine.schemas import DatasetSuggestion



# ---------------------------------------------------------------------------
# Helper unique pour l'horloge ⇒ facilement monkeypatchable dans les tests
# ---------------------------------------------------------------------------
def _utcnow() -> dt.datetime:
    """Renvoie maintenant (UTC) – timezone aware, sans warning."""
    return dt.datetime.now(dt.timezone.utc)


# ----------------------- barèmes ---------------------------------- #
FMT_POINTS           = 25          # maxi pour la diversité de formats
METADATA_POINTS      = 25          # licence + org + desc
FRESHNESS_POINTS_MAX = 20          # date < 1 mois
SIZE_POINTS          = 30          # placeholder : nbre ressources, etc.

VALID_OPEN_FORMATS = {"csv", "xls", "xlsx", "json", "geojson", "xml", "shp"}

# ------------------------------------------------------------------ #
# 1. Diversité de formats                                            #
# ------------------------------------------------------------------ #
def _score_formats(formats: List[str]) -> int:
    if not formats:
        return 0
    pts = 0
    uniques = set(f.lower() for f in formats)

    # +5 pts par format « ouvert »
    pts += 5 * len(uniques & VALID_OPEN_FORMATS)

    # bonus +5 s’il y a au moins 3 formats différents
    if len(uniques) >= 3:
        pts += 5
    return min(pts, FMT_POINTS)

# ------------------------------------------------------------------ #
# 2. Métadonnées                                                     #
# ------------------------------------------------------------------ #
def _score_metadata(ds: DatasetSuggestion) -> int:
    pts = 0
    if ds.license:
        pts += 10
    if ds.organization:
        pts += 10
    if ds.description:
        pts += 5
    return min(pts, METADATA_POINTS)

# ------------------------------------------------------------------ #
# 3. Fraîcheur (ISO 8601)                                            #
# ------------------------------------------------------------------ #
def _score_freshness(last_modified: str | None) -> int:
    if not last_modified:
        return 0
    try:
        # "Z" → "+00:00" pour fromisoformat
        iso = last_modified.replace("Z", "+00:00")
        dt = datetime.fromisoformat(iso)
    except ValueError:
        return 0

    # on force UTC pour comparer à un datetime aware
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
   # now = datetime.now(timezone.utc)
    now = _utcnow()
    age_days = (now - dt).days

    if age_days < 30:          # < 1 mois
        return 20
    elif age_days < 180:       # < 6 mois
        return 15
    elif age_days < 365:       # < 1 an
        return 10
    elif age_days < 730:       # < 2 ans
        return 5
    return 0

# ------------------------------------------------------------------ #
# 4. Taille / nb ressources (placeholder)                            #
# ------------------------------------------------------------------ #
def _score_size(n_resources: int) -> int:
    if n_resources >= 5:
        return 30
    elif n_resources >= 3:
        return 20
    elif n_resources >= 1:
        return 10
    return 0

# ------------------------------------------------------------------ #
# 5. Score global                                                    #
# ------------------------------------------------------------------ #
def richness_score(ds: DatasetSuggestion) -> int:
    scores = {
        "formats"   : _score_formats(ds.formats),
        "metadata"  : _score_metadata(ds),
        "freshness" : _score_freshness(ds.last_modified),
        "size"      : _score_size(len(ds.formats)),  # simpliste : 1 ressource ↔ 1 format
    }
    total = sum(scores.values())
    # On borne à 100
    return min(total, 100)
    
