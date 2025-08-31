from __future__ import annotations

import ai_engine
import inspect
import logging
from typing import Optional, List

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
from ai_engine.chains import keywords, viz  # llm_sources
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
    is_pdf_url, has_data_path_token, has_data_format_signal, is_dataset_root_listing,
)
from ai_engine.theme_filter import build_angle_signature, theme_weight_and_flag
from ai_engine import theme_filter  # pour matches_current_theme si dispo
from ai_engine.trust import trusted_weight_from_url as _trusted_weight_from_url
from ai_engine.ranking import (
    homepage_soft_weight as _homepage_soft_weight,
    datasets_path_soft_boost as _datasets_path_soft_boost,
    final_weight as _compose_final_weight,
    apply_additional_weights as _apply_additional_weights,
)
from ai_engine.balancing import rebalance_minima

logger = logging.getLogger("datascope.ai_engine")

MAX_TOKENS = 8_000

# --- Compatibility shim for new ranking.rebalance_minima signature ---
def _rebalance_minima_shim(ds: list, src: list, min_ds: int | None = None, min_src: int | None = None):
    """
    Adapte l'ancien appel (rebalance_minima(ds, src)) à la nouvelle signature:
      rebalance_minima(ds, src, min_ds, min_src, is_dataset_like_url, to_dataset, to_source)
    """
    try:
        from django.conf import settings  # type: ignore
    except Exception:
        settings = None  # pyright: ignore

    # valeurs par défaut configurables
    min_ds = min_ds if min_ds is not None else int(getattr(settings, "RESULTS_MIN_DATASETS", 3) or 3)
    min_src = min_src if min_src is not None else int(getattr(settings, "RESULTS_MIN_SOURCES", 2) or 2)

    # heuristiques réutilisant les helpers déjà testés dans url_utils
    from .url_utils import has_data_path_token, has_data_format_signal, is_pdf_url

    def is_dataset_like_url(u: str) -> bool:
        if not isinstance(u, str) or not u:
            return False
        # dataset-like si chemin/token data **ou** signal de format… et pas PDF
        return (has_data_path_token(u) or has_data_format_signal(u)) and not is_pdf_url(u)

    def to_dataset(item: dict) -> dict:
        if isinstance(item, dict):
            item["intent"] = "dataset"
        return item

    def to_source(item: dict) -> dict:
        if isinstance(item, dict):
            item["intent"] = "source"
        return item

    # on importe ici pour éviter tout import circulaire au chargement du module
    from .ranking import rebalance_minima as _rebalance_minima

    return _rebalance_minima(
        ds,
        src,
        min_ds,
        min_src,
        is_dataset_like_url,
        to_dataset,
        to_source,
    )



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


# --- light helpers (local) ---

def _classify_type(url: str, title: str = "", snippet: str = "") -> str:
    """
    Return 'dataset' or 'source' avec des règles simples et précises.
    - PDF => Source
    - Tokens dataset/data/api/download/geonetwork/catalog/search ou formats csv/json/geojson/API => Dataset
    - Sinon Source (le rebalance pourra encore intervenir plus tard)
    """
    if is_pdf_url(url):
        return "source"
    if has_data_path_token(url) or has_data_format_signal(url, f"{title} {snippet}"):
        return "dataset"
    return "source"


def _postprocess_suggestions(angle_idx: int, raw_suggestions: List[LLMSourceSuggestion]):
    """
    1) Reclasse en datasets/sources avec règles légères.
    2) Applique des poids additionnels (pdf/near-root/dataset-signals).
    3) Respecte les minima via le rebalance existant.
    """
    ds: List[DatasetSuggestion] = []
    src: List[LLMSourceSuggestion] = []

    # Option : appliquer une pénalité thème plus stricte aux datasets
    theme_strict_ds = bool(getattr(settings, "THEME_FILTER_STRICT_FOR_DATASETS", False))

    for s in raw_suggestions:
        url = getattr(s, "url", "") or getattr(s, "link", "")
        title = getattr(s, "title", "") or ""
        snippet = getattr(s, "description", "") or getattr(s, "snippet", "")
        source_name = getattr(s, "source", "") or ""

        # 1) Type
        ty = _classify_type(url, title, snippet)

        # 2) Poids additionnels (non mutables)
        add_w = _apply_additional_weights(s)

        # 3) Base existante (si dispo) + additif
        base_w = getattr(s, "weight", 0.0) or getattr(s, "score", 0.0) or 0.0
        final_w = base_w + add_w

        # 4) Pénalité spéciale pour listings /dataset(s) sans slug
        if ty == "dataset" and is_dataset_root_listing(url):
            final_w -= float(getattr(settings, "DATASET_ROOT_LISTING_PENALTY", 0.15))

        # 5) Pénalité thème douce optionnelle pour datasets
        if theme_strict_ds and ty == "dataset":
            themed_ok = True
            try:
                themed_ok = theme_filter.matches_current_theme(
                    getattr(s, "keywords", []) or f"{title} {snippet}"
                )
            except Exception:
                # Si la fonction n'existe pas / autre signature : on passe
                themed_ok = True
            if not themed_ok:
                final_w -= float(getattr(settings, "THEME_FILTER_SOFT_PENALTY", 0.15))

        # 5bis) Essayer de persister le poids
        try:
            setattr(s, "weight", final_w)
        except Exception:
            pass

        # 6) Construire l'objet final
        if ty == "dataset":
            try:
                ds_item = DatasetSuggestion(
                    angle_idx=angle_idx,
                    title=title,
                    description=snippet,
                    source_name=source_name,
                    source_url=url,
                    found_by="LLM",
                    formats=[],
                    organization=None,
                    license=None,
                    last_modified="",
                    richness=0,
                )
                try:
                    setattr(ds_item, "weight", final_w)
                except Exception:
                    pass
                ds.append(ds_item)
            except Exception:
                # Fallback prudemment en source si schéma strict
                src_item = LLMSourceSuggestion(
                    angle_idx=angle_idx, title=title, description=snippet, link=url, source=source_name
                )
                try:
                    setattr(src_item, "weight", final_w)
                except Exception:
                    pass
                src.append(src_item)
        else:
            src_item = LLMSourceSuggestion(
                angle_idx=angle_idx, title=title, description=snippet, link=url, source=source_name
            )
            try:
                setattr(src_item, "weight", final_w)
            except Exception:
                pass
            src.append(src_item)

    # Dé-doublonnage + tri local (desc)
    ds = sorted({getattr(d, "source_url", None) or getattr(d, "link", None): d for d in ds}.values(),
                key=lambda x: getattr(x, "weight", 0.0), reverse=True)
    src = sorted({getattr(s, "link", None) or getattr(s, "source_url", None): s for s in src}.values(),
                 key=lambda x: getattr(x, "weight", 0.0), reverse=True)

    # Minima locaux (ça reste affiné plus loin après fusion avec les connecteurs)
    ds, src = _rebalance_minima_shim(ds, src)

    return ds, src


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

    # Recherche / collecte web
    if bool(getattr(settings, "SEARCH_ENABLED", False)):
        llm_sources_sets = llm_sources_collect.run(angle_result)
    else:
        llm_sources_sets = llm_sources_collect.run(angle_result)  # fallback LLM-only

    viz_sets = viz.run(angle_result)

    angle_resources: list[AngleResources] = []

    for idx, angle in enumerate(angle_result.angles):
        kw_set = keywords_per_angle[idx] if idx < len(keywords_per_angle) else None
        conn_ds = connectors_sets[idx] if idx < len(connectors_sets) else []
        llm_all = llm_sources_sets[idx] if idx < len(llm_sources_sets) else []
        viz_list = viz_sets[idx] if idx < len(viz_sets) else []

        # --- NOUVEAU : post-traitement LLM (reclassement + poids)
        llm_ds_proc, llm_src_proc = _postprocess_suggestions(idx, llm_all)

        # Merge & dedupe datasets (connecteurs + LLM)
        seen_urls = {d.source_url for d in conn_ds}
        merged_ds = conn_ds[:]
        for ds_it in llm_ds_proc:
            url = getattr(ds_it, "source_url", None)
            if url and url not in seen_urls:
                merged_ds.append(ds_it)
                seen_urls.add(url)

        # Validation (optionnelle)
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

            tmp_src = list(llm_src_proc)
            vs = []
            for src in tmp_src:
                res = _validate_once(get_url(src))
                set_validation(src, res)
                if res.get("status") in ("ok", "redirected") and res.get("final_url"):
                    set_url(src, res["final_url"])
                if not (filter_404 and res.get("status") == "not_found"):
                    vs.append(src)
            llm_src_proc = vs

        # De-dup sources vs datasets
        seen_dataset_links = {url_key_for_dedupe(d) for d in merged_ds if url_key_for_dedupe(d)}
        llm_src_proc = [s for s in llm_src_proc if url_key_for_dedupe(s) not in seen_dataset_links]

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
                w, off = theme_weight_and_flag(
                    ds, ANG_UNI, ANG_BI,
                    min_hits=_THEME_MIN_HITS, penalty=_THEME_PENALTY,
                    pick_url_for_weight=pick_url_for_weight,
                )
                if theme_strict and off:
                    continue
                theme_w[id(ds)] = w
            else:
                theme_w[id(ds)] = 1.0
            themed_datasets.append(ds)
        merged_ds = themed_datasets

        themed_sources = []
        for src in llm_src_proc:
            w, off = theme_weight_and_flag(
                src, ANG_UNI, ANG_BI,
                min_hits=_THEME_MIN_HITS, penalty=_THEME_PENALTY,
                pick_url_for_weight=pick_url_for_weight,
            )
            if theme_strict and off:
                continue
            theme_w[id(src)] = w
            themed_sources.append(src)
        llm_src_proc = themed_sources

        # Final weights = (trusted × theme × homepage × datasets-path) + poids additionnels
        def _final_weight(obj) -> float:
            base = _compose_final_weight(
                obj,
                theme_w=theme_w,
                pick_url_for_weight=pick_url_for_weight,
                trust_weight_fn=_trusted,
                homepage_weight_fn=_homepage,
                datasets_path_boost_fn=_datasets_boost,
            )
            # Ajout additif (pdf, near-root, dataset-signals)
            return base + _apply_additional_weights(obj)

        merged_ds.sort(key=_final_weight, reverse=True)
        llm_src_proc.sort(key=_final_weight, reverse=True)

        # Rebalance minima (3/3) — TYPE-SAFE (avec convertisseurs)
        rebalance_minima(
            merged_ds,
            llm_src_proc,
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
                sources=llm_src_proc,
                visualizations=viz_list,
            )
        )

    packaged, markdown = package(extraction_result, angle_result)

    get_memory(user_id).save_context(
        {"article": article_text},
        {"summary": f"[score={score_10}] Angles: {[a.title for a in angle_result.angles]}"},
    )

    return packaged, markdown, score_10, angle_resources
