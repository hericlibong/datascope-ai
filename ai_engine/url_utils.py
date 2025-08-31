from __future__ import annotations
from urllib.parse import urlparse, parse_qs
from typing import Any, Optional

# -----------------------------
# URL helpers & classification
# -----------------------------

# --- New helpers for dataset/source post-processing ---

DATA_PATH_TOKENS = {
    "dataset", "datasets", "data", "datastore", "statistics",
    "download", "api", "geonetwork", "catalog", "search"
}

DATA_FORMAT_EXTS = (".csv", ".json", ".geojson", ".parquet")
DATA_SERVICE_TOKENS = ("wfs", "wms", "api")


def url_path_depth(url: str) -> int:
    """Return the number of non-empty path segments."""
    try:
        p = urlparse(url)
        parts = [s for s in p.path.split("/") if s]
        return len(parts)
    except Exception:
        return 0


def is_pdf_url(url: str) -> bool:
    """True if URL clearly targets a PDF resource."""
    try:
        p = urlparse(url)
        path = (p.path or "").lower()
        if path.endswith(".pdf"):
            return True
        # some portals expose ?format=pdf or filename=....pdf
        q = "&".join([f"{k}={v}" for k, vals in parse_qs(p.query).items() for v in vals]).lower()
        return ".pdf" in q
    except Exception:
        return False


def is_near_root(url: str) -> bool:
    """Near-root = home or 1-segment path, often low-signal pages."""
    return url_path_depth(url) <= 1


def has_data_path_token(url: str) -> bool:
    """Heuristic: dataset-like path tokens present."""
    try:
        p = urlparse(url)
        path = (p.path or "").lower()
        return any(tok in path for tok in DATA_PATH_TOKENS)
    except Exception:
        return False


def has_data_format_signal(url: str, text: str = "") -> bool:
    """
    Heuristic: file/data format or service tokens found in URL or associated text.
    This positively hints at 'dataset' pages (CSV/JSON/GeoJSON/API/WFS/WMS).
    """
    low_url = (url or "").lower()
    low_txt = (text or "").lower()
    if any(ext in low_url or ext in low_txt for ext in DATA_FORMAT_EXTS):
        return True
    if any(tok in low_url or tok in low_txt for tok in DATA_SERVICE_TOKENS):
        return True
    return False


def is_dataset_root_listing(url: str) -> bool:
    """True for paths like '/dataset' or '/datasets' without a concrete slug."""
    try:
        p = urlparse(url)
        parts = [s for s in (p.path or "").split("/") if s]
        if not parts:
            return False
        last = parts[-1].lower()
        return last in {"dataset", "datasets"} and len(parts) <= 2
    except Exception:
        return False


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
