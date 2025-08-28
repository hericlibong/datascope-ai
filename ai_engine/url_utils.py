from __future__ import annotations
from urllib.parse import urlparse
from typing import Any, Optional

# -----------------------------
# URL helpers & classification
# -----------------------------

def normalize_url(u: Optional[str]) -> Optional[str]:
    if not u:
        return None
    try:
        p = urlparse(u)
        scheme = (p.scheme or "http").lower()
        host = (p.netloc or "").lower()
        path = (p.path or "/").rstrip("/") or "/"
        return f"{scheme}://{host}{path}"
    except Exception:
        return u


def get_url(obj: Any) -> Optional[str]:
    if obj is None:
        return None
    if isinstance(obj, dict):
        return obj.get("source_url") or obj.get("link")
    return getattr(obj, "source_url", None) or getattr(obj, "link", None)


def set_url(obj: Any, new_url: str) -> None:
    if obj is None:
        return
    if isinstance(obj, dict):
        if "source_url" in obj:
            obj["source_url"] = new_url
        if "link" in obj:
            obj["link"] = new_url
    else:
        if hasattr(obj, "source_url"):
            setattr(obj, "source_url", new_url)
        if hasattr(obj, "link"):
            setattr(obj, "link", new_url)


def set_validation(obj: Any, payload: dict) -> None:
    if obj is None:
        return
    if isinstance(obj, dict):
        obj["validation"] = payload
    else:
        setattr(obj, "validation", payload)


def pick_url_for_weight(obj: Any) -> Optional[str]:
    v = getattr(obj, "validation", None)
    if isinstance(v, dict) and v.get("final_url"):
        return v["final_url"]
    return get_url(obj)


def url_key_for_dedupe(obj: Any) -> Optional[str]:
    u = pick_url_for_weight(obj) or get_url(obj)
    return normalize_url(u)


def _is_homepage_like_path(path: str) -> bool:
    p = path.strip("/")
    return p == "" or "/" not in p


def is_dataset_like_url(url: Optional[str]) -> bool:
    """
    Unified heuristic (FR/EN) to decide if a URL looks dataset-oriented.
    - Reject obvious home/portal pages (path length <= 1 segment)
    - Accept if path hints at datasets/catalog/search/statistics/data/API/download/table
    """
    if not url:
        return False
    try:
        p = urlparse(url)
        path = (p.path or "").lower()
        if _is_homepage_like_path(path):
            return False
        hints = (
            "/datasets", "/dataset", "datastore", "/data",
            "statistics", "statistiques", "statistique",
            "search", "recherche",
            "catalog", "catalogue",
            "table", "api", "download",
        )
        return any(h in path for h in hints)
    except Exception:
        return False
    