# ai_engine/search_provider.py
from __future__ import annotations

import logging
from typing import Any, Dict, List
from urllib.parse import urlparse

import requests
from django.conf import settings

logger = logging.getLogger("datascope.search")


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
        # root or one-level like /fr ; treat '/datasets/' without query as near-root too
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


def _tavily_search_one(query: str, k: int, timeout: int) -> List[Dict[str, Any]]:
    """
    Minimal Tavily wrapper. No domain restriction. Returns raw dicts with keys:
    url, title, snippet (if available).
    """
    api_key = getattr(settings, "TAVILY_API_KEY", "") or ""
    if not api_key:
        logger.warning("TAVILY_API_KEY missing; returning empty results.")
        return []

    try:
        resp = requests.post(
            "https://api.tavily.com/search",
            json={
                "api_key": api_key,
                "query": query,
                "max_results": int(k),
                "search_depth": "basic",
                "include_answer": False,
                "include_images": False,
                "include_raw_content": False,
            },
            timeout=timeout,
        )
        resp.raise_for_status()
        data = resp.json() or {}
        items = data.get("results") or []
        out: List[Dict[str, Any]] = []
        for it in items:
            url = it.get("url") or ""
            title = it.get("title") or None
            snippet = it.get("content") or it.get("snippet") or None
            if not url:
                continue
            out.append({"url": url, "title": title, "snippet": snippet})
        return out
    except Exception as e:
        logger.warning("Tavily request failed: %r", e)
        return []


def search_many(queries: List[dict], k: int = 10) -> List[Dict[str, Any]]:
    """
    Execute a batch of queries with the configured provider (default Tavily).
    queries: list of QuerySpec-like dicts having keys: text, intent, lang, ...
    Returns a flat list of SearchResult-like dicts:
        {url, title, snippet, source_domain, intent, score}
    """
    provider = (getattr(settings, "SEARCH_PROVIDER", "tavily") or "tavily").lower()
    timeout = int(getattr(settings, "SEARCH_TIMEOUT", 8) or 8)

    seen: set[str] = set()
    results: List[Dict[str, Any]] = []

    for q in queries:
        text = (q or {}).get("text") or ""
        intent = (q or {}).get("intent") or "dataset"
        if not text:
            continue

        raw_items: List[Dict[str, Any]] = []
        if provider == "tavily":
            raw_items = _tavily_search_one(text, k=k, timeout=timeout)
        else:
            # Fallback to Tavily for now
            raw_items = _tavily_search_one(text, k=k, timeout=timeout)

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
                    "score": None,  # provider-native score not used for now
                }
            )

    logger.debug("search_many: returned %d unique urls", len(results))
    return results
