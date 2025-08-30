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
    Pour chaque angle :
      1) génère 3..6 requêtes (LLM)
      2) exécute la recherche web (provider configuré)
      3) convertit les résultats en LLMSourceSuggestion (sans split : le pipeline s’en charge)
    Retour: [[LLMSourceSuggestion, ...], ...] aligné sur les angles.
    """
    per_angle_suggestions: List[List[LLMSourceSuggestion]] = []

    # Paramètres légers (bornes) — facultatifs
    max_keep = int(getattr(settings, "SEARCH_RESULTS_PER_ANGLE", 18) or 18)
    k_per_query = int(getattr(settings, "SEARCH_MAX_RESULTS", 10) or 10)

    all_queries = run_llm_queries(angle_result)  # [[QuerySpec,...], ...]
    for idx, angle in enumerate(angle_result.angles):
        queries = all_queries[idx] if idx < len(all_queries) else []
        # Convertit QuerySpec -> dict pour le provider générique
        qdicts = [q.model_dump() if hasattr(q, "model_dump") else dict(q) for q in queries]

        raw = search_many(qdicts, k=k_per_query)  # [{url, title, snippet, source_domain, intent, score}, ...]

        # Conversion minimale -> LLMSourceSuggestion (le pipeline fera split + ranking + validation)
        items: List[LLMSourceSuggestion] = []
        for r in raw[: max_keep]:
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
                    angle_idx=idx,  # requis par le schéma
                )
            )

        per_angle_suggestions.append(items)

    return per_angle_suggestions
