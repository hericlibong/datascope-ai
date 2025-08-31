# ai_engine/search_provider.py
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from django.conf import settings

logger = logging.getLogger("datascope.search")

# ---------------------------------------------------------------------------
# HTTP session résiliente (retries + timeouts)
# ---------------------------------------------------------------------------

_TAVILY_TIMEOUT_S: int = int(getattr(settings, "TAVILY_TIMEOUT_SECONDS", 20) or 20)
_TAVILY_MAX_RETRIES: int = int(getattr(settings, "TAVILY_MAX_RETRIES", 2) or 2)

_session = requests.Session()
_retry = Retry(
    total=_TAVILY_MAX_RETRIES,
    backoff_factor=0.6,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET", "POST"],
    raise_on_status=False,
)
_session.mount("https://", HTTPAdapter(max_retries=_retry))
_session.mount("http://", HTTPAdapter(max_retries=_retry))


# ---------------------------------------------------------------------------
# Helpers URL
# ---------------------------------------------------------------------------

def _normalize_url(u: str) -> str:
    try:
        p = urlparse(u)
        scheme = (p.scheme or "http").lower()
        netloc = (p.netloc or "").lower()
        path = (p.path or "/")
        if path != "/" and path.endswith("/"):
            path = path[:-1]
        qs = f"?{p.query}" if p.query else ""
        return f"{scheme}://{netloc}{path}{qs}"
    except Exception:
        return u


def _is_near_root(u: str) -> bool:
    try:
        p = urlparse(u)
        segs = [s for s in (p.path or "").split("/") if s]
        # root ou une profondeur (ex: /fr). On traite aussi '/datasets' sans query comme near-root.
        if len(segs) <= 1 and not p.query:
            return True
        if (p.path or "").rstrip("/").endswith("/datasets") and not p.query:
            return True
        return False
    except Exception:
        return False


def _source_domain(u: str) -> str:
    try:
        return (urlparse(u).netloc or "").lower()
    except Exception:
        return ""


# ---------------------------------------------------------------------------
# Tavily wrapper
# ---------------------------------------------------------------------------

def _tavily_search_one(
    query: str,
    k: int,
    timeout: int,
    include_domains: Optional[List[str]] = None,
    exclude_domains: Optional[List[str]] = None,
    search_depth: str = "basic",
) -> List[Dict[str, Any]]:
    """
    Appel minimal à Tavily. Retourne des dicts {url, title, snippet}.
    - include_domains / exclude_domains : filtres optionnels par domaine
    - search_depth: "basic" (par défaut) ou "advanced"
    """
    api_key = getattr(settings, "TAVILY_API_KEY", "") or ""
    if not api_key:
        logger.warning("TAVILY_API_KEY missing; returning empty results.")
        return []

    payload: Dict[str, Any] = {
        "api_key": api_key,  # conservé pour compat avec votre implémentation
        "query": query,
        "max_results": int(k),
        "search_depth": search_depth if search_depth in ("basic", "advanced") else "basic",
        "include_answer": False,
        "include_images": False,
        "include_raw_content": False,
    }
    if include_domains:
        payload["include_domains"] = include_domains
    if exclude_domains:
        payload["exclude_domains"] = exclude_domains

    try:
        r = _session.post(
            "https://api.tavily.com/search",
            json=payload,
            timeout=timeout,
        )
        r.raise_for_status()
        data = r.json() or {}
        items = data.get("results") or []
        out: List[Dict[str, Any]] = []
        for it in items:
            url = it.get("url") or ""
            if not url:
                continue
            out.append(
                {
                    "url": url,
                    "title": it.get("title") or None,
                    "snippet": it.get("content") or it.get("snippet") or None,
                }
            )
        return out
    except requests.RequestException as e:
        logger.warning("Tavily request failed: %r", e)
        return []
    except Exception as e:
        logger.warning("Tavily unexpected error: %r", e)
        return []


# ---------------------------------------------------------------------------
# Recherche batch + back-off optionnel
# ---------------------------------------------------------------------------

def search_many(queries: List[dict], k: int = 10) -> List[Dict[str, Any]]:
    """
    Exécute un lot de requêtes via le provider (Tavily par défaut).

    Input attendu (par élément de `queries`) — aligné avec QuerySpec:
      { "text": str, "intent": "dataset"|"source", "lang": "fr|en|...", 
        "include_domains": [..] (optionnel),
        "exclude_domains": [..] (optionnel),
        "search_depth": "basic"|"advanced" (optionnel)
      }

    Sortie: liste aplatie de dicts SearchResult-like:
      { "url", "title", "snippet", "source_domain", "intent", "score": None }
    """
    provider = (getattr(settings, "SEARCH_PROVIDER", "tavily") or "tavily").lower()
    timeout = int(getattr(settings, "SEARCH_TIMEOUT", _TAVILY_TIMEOUT_S) or _TAVILY_TIMEOUT_S)

    # Back-off params (lecture settings)
    backoff_min_ds = int(getattr(settings, "SEARCH_BACKOFF_MIN_DATASETS", 3) or 3)
    backoff_domains: List[str] = list(getattr(settings, "SEARCH_BACKOFF_INCLUDE_DOMAINS", []) or [])
    backoff_depth = str(getattr(settings, "SEARCH_BACKOFF_SEARCH_DEPTH", "advanced") or "advanced")

    exclude_domains_default: List[str] = list(getattr(settings, "SEARCH_EXCLUDE_DOMAINS", []) or [])

    seen: set[str] = set()
    results: List[Dict[str, Any]] = []

    # --- 1) Passe normale
    for q in queries:
        text = (q or {}).get("text") or ""
        intent = (q or {}).get("intent") or "dataset"
        include_domains_q: Optional[List[str]] = (q or {}).get("include_domains")
        exclude_domains_q: List[str] = (q or {}).get("exclude_domains") or []
        search_depth_q: str = (q or {}).get("search_depth") or "basic"

        if not text:
            continue

        raw_items: List[Dict[str, Any]] = []
        if provider == "tavily":
            raw_items = _tavily_search_one(
                text,
                k=k,
                timeout=timeout,
                include_domains=include_domains_q,
                exclude_domains=(exclude_domains_q or exclude_domains_default) or None,
                search_depth=search_depth_q,
            )
        else:
            # Fallback : Tavily
            raw_items = _tavily_search_one(
                text,
                k=k,
                timeout=timeout,
                include_domains=include_domains_q,
                exclude_domains=(exclude_domains_q or exclude_domains_default) or None,
                search_depth=search_depth_q,
            )

        for it in raw_items:
            url = _normalize_url(it.get("url") or "")
            if not url or _is_near_root(url):
                continue
            if url in seen:
                continue
            seen.add(url)
            results.append(
                {
                    "url": url,
                    "title": it.get("title"),
                    "snippet": it.get("snippet"),
                    "source_domain": _source_domain(url),
                    "intent": intent,
                    "score": None,  # pas de score natif exploité
                }
            )

    # --- 2) Back-off datasets si on est trop “court”
    if backoff_domains:
        ds_count = sum(1 for r in results if (r.get("intent") or "dataset") == "dataset")
        if ds_count < backoff_min_ds:
            logger.info(
                "search_many: back-off datasets (have=%d < min=%d) via include_domains=%s",
                ds_count, backoff_min_ds, backoff_domains,
            )
            for q in queries:
                if (q or {}).get("intent") != "dataset":
                    continue
                text = (q or {}).get("text") or ""
                if not text:
                    continue

                # Requête identique mais forcée sur domaines + depth avancée
                raw_items = _tavily_search_one(
                    text,
                    k=k,
                    timeout=timeout,
                    include_domains=backoff_domains,
                    exclude_domains=exclude_domains_default or None,
                    search_depth=backoff_depth,
                )
                for it in raw_items:
                    url = _normalize_url(it.get("url") or "")
                    if not url or _is_near_root(url):
                        continue
                    if url in seen:
                        continue
                    seen.add(url)
                    results.append(
                        {
                            "url": url,
                            "title": it.get("title"),
                            "snippet": it.get("snippet"),
                            "source_domain": _source_domain(url),
                            "intent": "dataset",
                            "score": None,
                        }
                    )

    logger.debug("search_many: returned %d unique urls", len(results))
    return results
