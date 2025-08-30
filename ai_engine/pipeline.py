from __future__ import annotations

import ai_engine
import inspect
import logging
from typing import Optional

from django.conf import settings

from ai_engine.utils import token_len
from ai_engine.chains import extraction, angles
from ai_engine.formatter import package
from ai_engine.schemas import (
    AnalysisPackage,  
    DatasetSuggestion,
    KeywordsResult,
    LLMSourceSuggestion,
    AngleResources,
)
from ai_engine.scoring import compute_score
from ai_engine.chains import keywords, viz # llm_sources
from ai_engine.chains import llm_sources_collect  # NEW
from ai_engine.memory import get_memory

from ai_engine.connectors.data_gouv import DataGouvClient
from ai_engine.connectors.data_gov import DataGovClient
from ai_engine.connectors.data_canada import CanadaGovClient
from ai_engine.connectors.data_uk import UKGovClient
from ai_engine.connectors.hdx_data import HdxClient

from ai_engine.services import validate_url

# Modular imports
from ai_engine.url_utils import (
    get_url, set_url, set_validation, pick_url_for_weight, url_key_for_dedupe, is_dataset_like_url,
)
from ai_engine.theme_filter import build_angle_signature, theme_weight_and_flag
from ai_engine.trust import trusted_weight_from_url as _trusted_weight_from_url
from ai_engine.ranking import (
    homepage_soft_weight as _homepage_soft_weight,
    datasets_path_soft_boost as _datasets_path_soft_boost,
    final_weight as _compose_final_weight,
)
from ai_engine.balancing import rebalance_minima

logger = logging.getLogger("datascope.ai_engine")

MAX_TOKENS = 8_000


def _validate_length(text: str) -> None:
    if token_len(text, model=ai_engine.OPENAI_MODEL) > MAX_TOKENS:
        raise ValueError("Article trop long")


def _score(extr) -> int:
    raw = (len(extr.persons) + len(extr.organizations)) * 10
    return min(raw, 100)


def run_connectors(
    keywords_per_angle: list[KeywordsResult],
    max_per_keyword: int = 2,
    max_total_per_angle: int = 5,
) -> list[list[DatasetSuggestion]]:
    connectors = [
        DataGouvClient(),
        DataGovClient(),
        CanadaGovClient(),
        UKGovClient(),
        HdxClient(),
    ]

    all_angles: list[list[DatasetSuggestion]] = []

    for idx, kw_result in enumerate(keywords_per_angle):
        print(f"\n=== [ANGLE {idx}] {kw_result.sets[0].angle_title} ===")
        seen_urls: set[str] = set()
        angle_suggestions: list[DatasetSuggestion] = []

        for kw_set in kw_result.sets:
            for keyword in kw_set.keywords:
                print(f"→ keyword='{keyword}'")
                for connector in connectors:
                    sig = inspect.signature(connector.search).parameters
                    print(f"   ↳ {connector.__class__.__name__}.search … ", end="")
                    try:
                        if "max_results" in sig:
                            raw_results = connector.search(keyword, max_results=max_per_keyword)
                        elif "page_size" in sig:
                            raw_results = connector.search(keyword, page_size=max_per_keyword)
                        else:
                            raw_results = connector.search(keyword)
                    except Exception as e:
                        print(f"ERREUR : {e!r}")
                        continue
                    else:
                        print("ok")

                    for raw_ds in raw_results:
                        suggestion: DatasetSuggestion | None = None

                        if hasattr(connector, "to_suggestion"):
                            try:
                                suggestion = connector.to_suggestion(raw_ds)
                            except Exception as err:
                                print("      ⚠️  to_suggestion KO :", err)

                        if suggestion is None:
                            for fn in (
                                "us_to_suggestion",
                                "fr_to_suggestion",
                                "ca_to_suggestion",
                                "uk_to_suggestion",
                                "hdx_to_suggestion",
                            ):
                                if hasattr(connector, fn):
                                    try:
                                        suggestion = getattr(connector, fn)(raw_ds)
                                    except Exception as conv_err:
                                        print(f"      ↳ échec {fn} : {conv_err!r}")
                                        suggestion = None
                                    break

                        if suggestion is None and isinstance(raw_ds, DatasetSuggestion):
                            suggestion = raw_ds

                        if suggestion is None:
                            print("      ⚠️  ignoré (non convertible)")
                            continue

                        if suggestion.source_url in seen_urls:
                            print("      ⏩ doublon")
                            continue

                        suggestion.found_by  = "CONNECTOR"
                        suggestion.angle_idx = idx

                        angle_suggestions.append(suggestion)
                        seen_urls.add(suggestion.source_url)

                        print(f"      ✅ ajouté : {suggestion.title[:60]}")

                        if len(angle_suggestions) >= max_total_per_angle:
                            print("      🔘 limite par angle atteinte")
                            break

                    if len(angle_suggestions) >= max_total_per_angle:
                        break
                if len(angle_suggestions) >= max_total_per_angle:
                    break

        print(f"→ total datasets angle {idx} : {len(angle_suggestions)}")
        all_angles.append(angle_suggestions)

    return all_angles


def _llm_to_ds(item: LLMSourceSuggestion, *, angle_idx: int) -> DatasetSuggestion:
    return DatasetSuggestion(
        title        = item.title,
        description  = item.description,
        source_name  = item.source,
        source_url   = item.link,
        found_by     = "LLM",
        angle_idx    = angle_idx,
        formats      = [],
        organization = None,
        license      = None,
        last_modified= "",
        richness     = 0,
    )

def _ds_to_llm(item: DatasetSuggestion, *, angle_idx: int | None = None) -> LLMSourceSuggestion:
    ai = angle_idx if angle_idx is not None else getattr(item, "angle_idx", 0)
    return LLMSourceSuggestion(
        title       = item.title,
        description = item.description,
        link        = getattr(item, "source_url", None) or getattr(item, "link", None) or "",
        source      = getattr(item, "source_name", None) or getattr(item, "source", None) or "",
        angle_idx   = ai,
    )

    
# ------------------------------------------------------------------
# Main pipeline
# ------------------------------------------------------------------
def run(
article_text: str,
user_id: str = "anon",
validate_urls: bool = False,
filter_404: Optional[bool] = None,
theme_strict: Optional[bool] = None,
) -> tuple[AnalysisPackage, str, float, list[AngleResources]]:
    
    _validate_length(article_text)

    if filter_404 is None:
        filter_404 = bool(getattr(settings, "URL_VALIDATION_FILTER_404", True))

    if theme_strict is None:
        theme_strict = bool(getattr(settings, "THEME_FILTER_STRICT_DEFAULT", False))
    _THEME_MIN_HITS = int(getattr(settings, "THEME_FILTER_MIN_UNIGRAM_HITS", 2))
    _THEME_PENALTY  = float(getattr(settings, "THEME_FILTER_SOFT_PENALTY", 0.15) or 0.0)

    _url_validation_cache: dict[str, dict] = {}

    def _connectors_enabled() -> bool:
        return bool(getattr(settings, "CONNECTORS_ENABLED", False))

    def _validate_once(url: str) -> dict:
        if not url:
            return {"input_url": "", "status": "error", "http_status": None, "final_url": None, "error": "EmptyURL"}
        cached = _url_validation_cache.get(url)
        if cached:
            return cached
        res = validate_url(url)
        _url_validation_cache[url] = res
        return res

    # Read settings once for weights
    _TRUST_BOOST = float(getattr(settings, "TRUSTED_SOFT_WEIGHT", 0.15) or 0.0)
    _TRUST_DOMAINS = getattr(settings, "TRUSTED_DOMAINS", [])
    _HOMEPAGE_PENALTY = float(getattr(settings, "HOMEPAGE_SOFT_PENALTY", 0.20) or 0.0)
    _DATASETS_PATH_SOFT_BOOST = float(getattr(settings, "DATASETS_PATH_SOFT_BOOST", 0.05) or 0.0)

    def _trusted(u: str | None) -> float:
        return _trusted_weight_from_url(u, _TRUST_BOOST, _TRUST_DOMAINS)

    def _homepage(u: str | None) -> float:
        return _homepage_soft_weight(u, _HOMEPAGE_PENALTY)

    def _datasets_boost(u: str | None) -> float:
        return _datasets_path_soft_boost(u, _DATASETS_PATH_SOFT_BOOST)

    extraction_result = extraction.run(article_text)
    score_10 = round(
        compute_score(extraction_result, article_text, model=ai_engine.OPENAI_MODEL),
        1,
    )

    angle_result = angles.run(article_text)
    logger.debug("Angles générés: %s", len(angle_result.angles))

    keywords_per_angle = keywords.run(angle_result)

    if _connectors_enabled():
        connectors_sets = run_connectors(keywords_per_angle)
    else:
        connectors_sets = [[] for _ in range(len(keywords_per_angle))]

    # llm_sources_sets = llm_sources.run(angle_result)
    
    if bool(getattr(settings, "SEARCH_ENABLED", False)):
        llm_sources_sets = llm_sources_collect.run(angle_result)  # NEW: collecte via web search
    else:
        llm_sources_sets = llm_sources_collect.run(angle_result)  # fallback LLM-only
    
    viz_sets = viz.run(angle_result)

    angle_resources: list[AngleResources] = []

    for idx, angle in enumerate(angle_result.angles):
        kw_set = keywords_per_angle[idx] if idx < len(keywords_per_angle) else None
        conn_ds = connectors_sets[idx] if idx < len(connectors_sets) else []
        llm_all = llm_sources_sets[idx] if idx < len(llm_sources_sets) else []
        viz_list = viz_sets[idx] if idx < len(viz_sets) else []

        # Split LLM into dataset-like vs source-like
        llm_for_datasets, llm_for_sources = [], []
        for s in llm_all:
            (llm_for_datasets if is_dataset_like_url(get_url(s)) else llm_for_sources).append(s)

        llm_ds = [_llm_to_ds(obj, angle_idx=idx) for obj in llm_for_datasets]
        llm_raw = llm_for_sources

        # Merge & dedupe datasets
        seen_urls = {d.source_url for d in conn_ds}
        merged_ds = conn_ds[:]
        for ds in llm_ds:
            if ds.source_url not in seen_urls:
                merged_ds.append(ds)
                seen_urls.add(ds.source_url)

        # Validation (optional)
        if validate_urls:
            vd, vs = [], []
            for ds in merged_ds:
                res = _validate_once(get_url(ds))
                set_validation(ds, res)
                if res.get("status") in ("ok", "redirected") and res.get("final_url"):
                    set_url(ds, res["final_url"])
                if not (filter_404 and res.get("status") == "not_found"):
                    vd.append(ds)
            merged_ds = vd

            for src in llm_raw:
                res = _validate_once(get_url(src))
                set_validation(src, res)
                if res.get("status") in ("ok", "redirected") and res.get("final_url"):
                    set_url(src, res["final_url"])
                if not (filter_404 and res.get("status") == "not_found"):
                    vs.append(src)
            llm_raw = vs

        # De-dup sources against datasets
        seen_dataset_links = {url_key_for_dedupe(d) for d in merged_ds if url_key_for_dedupe(d)}
        llm_raw = [s for s in llm_raw if url_key_for_dedupe(s) not in seen_dataset_links]

        # Theme signature
        angle_title = getattr(angle, "title", "") or ""
        angle_rationale = getattr(angle, "rationale", "") or ""
        angle_keywords = (kw_set.sets[0].keywords if (kw_set and getattr(kw_set, "sets", None)) else [])
        ANG_UNI, ANG_BI = build_angle_signature(angle_title, angle_rationale, angle_keywords)

        # Theme weights
        theme_w: dict[int, float] = {}
        themed_datasets = []
        for ds in merged_ds:
            if getattr(ds, "found_by", "") == "LLM":
                w, off = theme_weight_and_flag(ds, ANG_UNI, ANG_BI, min_hits=_THEME_MIN_HITS, penalty=_THEME_PENALTY, pick_url_for_weight=pick_url_for_weight)
                if theme_strict and off:
                    continue
                theme_w[id(ds)] = w
            else:
                theme_w[id(ds)] = 1.0
            themed_datasets.append(ds)
        merged_ds = themed_datasets

        themed_sources = []
        for src in llm_raw:
            w, off = theme_weight_and_flag(src, ANG_UNI, ANG_BI, min_hits=_THEME_MIN_HITS, penalty=_THEME_PENALTY, pick_url_for_weight=pick_url_for_weight)
            if theme_strict and off:
                continue
            theme_w[id(src)] = w
            themed_sources.append(src)
        llm_raw = themed_sources

        # Final weights (trusted × theme × homepage × datasets-path)
        def _final_weight(obj) -> float:
            return _compose_final_weight(
                obj,
                theme_w=theme_w,
                pick_url_for_weight=pick_url_for_weight,
                trust_weight_fn=_trusted,
                homepage_weight_fn=_homepage,
                datasets_path_boost_fn=_datasets_boost,
            )

        merged_ds.sort(key=_final_weight, reverse=True)
        llm_raw.sort(key=_final_weight, reverse=True)

        # Rebalance minima (3/3) — TYPE-SAFE (avec convertisseurs)
        rebalance_minima(
            merged_ds,
            llm_raw,
            int(getattr(settings, "DATASETS_MIN_PER_ANGLE", 3) or 3),
            int(getattr(settings, "SOURCES_MIN_PER_ANGLE", 3) or 3),
            is_dataset_like_url,
            to_dataset=lambda it: _llm_to_ds(it, angle_idx=idx),
            to_source=lambda it: _ds_to_llm(it, angle_idx=idx),
            logger=logger,
        )

        angle_resources.append(
            AngleResources(
                index=idx,
                title=angle.title,
                description=angle.rationale,
                keywords=kw_set.sets[0].keywords if kw_set else [],
                datasets=merged_ds,
                sources=llm_raw,
                visualizations=viz_list,
            )
        )

    packaged, markdown = package(extraction_result, angle_result)

    get_memory(user_id).save_context(
        {"article": article_text},
        {"summary": f"[score={score_10}] Angles: {[a.title for a in angle_result.angles]}"},
    )

    return packaged, markdown, score_10, angle_resources
