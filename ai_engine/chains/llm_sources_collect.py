# ai_engine/chains/llm_sources_collect.py
from __future__ import annotations

from typing import List
from django.conf import settings

from ai_engine.schemas import AngleResult, LLMSourceSuggestion
from ai_engine.chains.llm_queries import run as run_llm_queries
from ai_engine.search_provider import search_many


def _fallback_title(url: str, title: str | None) -> str:
    if title and title.strip():
        return title.strip()
    # fallback simple depuis l’URL
    try:
        from urllib.parse import urlparse
        p = urlparse(url)
        last = (p.path or "/").rstrip("/").split("/")[-1] or p.netloc
        return last.replace("-", " ").replace("_", " ").strip() or p.netloc
    except Exception:
        return url


def _domain_from_url(url: str) -> str:
    try:
        from urllib.parse import urlparse
        return (urlparse(url).netloc or "").lower()
    except Exception:
        return ""


def run(angle_result: AngleResult) -> List[List[LLMSourceSuggestion]]:
    """
    Deux passes par angle :
      1) génération de 3..6 requêtes (LLM)
      2) recherche web *par intent* (dataset puis source)
      3) conversion en LLMSourceSuggestion (le pipeline fera split/ranking/validation)
    Retour: [[LLMSourceSuggestion, ...], ...] aligné sur les angles.
    """
    per_angle_suggestions: List[List[LLMSourceSuggestion]] = []

    # Bornes souples
    max_keep = int(getattr(settings, "SEARCH_RESULTS_PER_ANGLE", 18) or 18)
    k_per_query = int(getattr(settings, "SEARCH_MAX_RESULTS", 10) or 10)

    all_queries = run_llm_queries(angle_result)  # [[QuerySpec,...], ...]
    for idx, angle in enumerate(angle_result.angles):
        queries = all_queries[idx] if idx < len(all_queries) else []

        # Split des requêtes par intent
        ds_q = [q for q in queries if getattr(q, "intent", None) == "dataset"]
        src_q = [q for q in queries if getattr(q, "intent", None) == "source"]

        # Appels provider séparés (datasets d'abord)
        ds_raw = search_many([q.model_dump() for q in ds_q], k=k_per_query) if ds_q else []
        src_raw = search_many([q.model_dump() for q in src_q], k=k_per_query) if src_q else []

        # Agrégation avec dé-duplication simple par URL normalisée
        seen = set()

        def _norm(u: str) -> str:
            try:
                from urllib.parse import urlparse
                p = urlparse(u or "")
                path = (p.path or "/").rstrip("/")
                return f"{p.scheme}://{p.netloc}{path}?{p.query}" if p.scheme and p.netloc else (u or "").strip()
            except Exception:
                return (u or "").strip()

        merged = []
        for r in ds_raw + src_raw:
            url = r.get("url") or ""
            key = _norm(url).lower()
            if not url or key in seen:
                continue
            seen.add(key)
            merged.append(r)
            if len(merged) >= max_keep:
                break

        # Conversion minimale -> LLMSourceSuggestion
        items: List[LLMSourceSuggestion] = []
        for r in merged:
            url = r.get("url") or ""
            title = _fallback_title(url, r.get("title"))
            desc = (r.get("snippet") or "").strip()
            source = r.get("source_domain") or _domain_from_url(url)

            items.append(
                LLMSourceSuggestion(
                    title=title,
                    description=desc,
                    link=url,
                    source=source,
                    angle_idx=idx,
                )
            )

        per_angle_suggestions.append(items)

    return per_angle_suggestions
