# ai_engine/ranking.py
from __future__ import annotations
from urllib.parse import urlparse
from typing import Callable, Any, List, Dict, Tuple
from django.conf import settings
from .url_utils import (
    is_pdf_url, has_data_path_token, has_data_format_signal,
    is_near_root, is_dataset_root_listing
)


def homepage_soft_weight(u: str | None, penalty: float) -> float:
    base = 1.0
    if not u:
        return base
    try:
        path = urlparse(u).path or ""
        segments = [s for s in path.split("/") if s]
        return base - float(penalty or 0.0) if len(segments) <= 1 else base
    except Exception:
        return base


def datasets_path_soft_boost(u: str | None, boost: float) -> float:
    """
    Returns a multiplicative boost (1+boost) if URL path contains
    '/datasets' (soft hint that it's likely a data catalogue page).
    """
    base = 1.0
    if not u:
        return base
    try:
        path = (urlparse(u).path or "").lower()
        return base + float(boost or 0.0) if "/datasets" in path else base
    except Exception:
        return base


# --- New reranking helpers (boosts / penalties) ---

def dataset_positive_signals_weight(url: str, title: str = "", snippet: str = "") -> float:
    """
    Lightweight, explainable boosts for dataset candidates.
    - +format boost if URL/text hints at csv/json/geojson/api/wfs/wms
    - +path boost if path includes dataset-like tokens (dataset/data/datastore/…)
    """
    fmt_boost = float(getattr(settings, "DATASET_FORMAT_BOOST", 0.25))
    path_boost = float(getattr(settings, "DATASET_PATH_BOOST", 0.15))
    w = 0.0
    if has_data_format_signal(url, f"{title} {snippet}"):
        w += fmt_boost
    if has_data_path_token(url):
        w += path_boost
    return w


def pdf_soft_penalty(url: str) -> float:
    """Apply a small negative weight to PDF pages (they're Sources, not Datasets)."""
    return -float(getattr(settings, "PDF_SOFT_PENALTY", 0.20)) if is_pdf_url(url) else 0.0


def near_root_penalty(url: str) -> float:
    """
    Stronger penalty for near-root pages and /datasets listings without a concrete slug.
    Complements the existing HOMEPAGE_SOFT_PENALTY.
    """
    base = float(getattr(settings, "HOMEPAGE_SOFT_PENALTY", 0.20))
    extra = float(getattr(settings, "DATASET_ROOT_LISTING_PENALTY", 0.15))
    if is_dataset_root_listing(url):
        return -(base + extra)
    return -base if is_near_root(url) else 0.0


def apply_additional_weights(sugg) -> float:
    """
    Returns an additive weight (can be negative) to be combined with the
    existing score/rank logic. Does not mutate the suggestion.
    - PDF penalty
    - Near-root penalty
    - Dataset positive signals (only if candidate is dataset-like)
    """
    url = getattr(sugg, "url", "") or getattr(sugg, "link", "")
    title = getattr(sugg, "title", "") or ""
    snippet = getattr(sugg, "description", "") or getattr(sugg, "snippet", "")
    add = 0.0
    add += pdf_soft_penalty(url)
    add += near_root_penalty(url)
    # dataset-like boost
    if has_data_path_token(url) or has_data_format_signal(url, f"{title} {snippet}"):
        add += dataset_positive_signals_weight(url, title, snippet)
    return add


def final_weight(
    item: Any,
    *,
    theme_w: dict[int, float],
    pick_url_for_weight: Callable[[Any], str | None],
    trust_weight_fn: Callable[[str | None], float],
    homepage_weight_fn: Callable[[str | None], float],
    datasets_path_boost_fn: Callable[[str | None], float],
) -> float:
    u = pick_url_for_weight(item)
    return (
        trust_weight_fn(u)
        * theme_w.get(id(item), 1.0)
        * homepage_weight_fn(u)
        * datasets_path_boost_fn(u)
    )


# ----------------------------
# Rebalancing (minima quotas)
# ----------------------------

def _url_of(item: Dict[str, Any]) -> str:
    if not isinstance(item, dict):
        return ""
    val = item.get("url") or item.get("link") or ""
    return str(val)


def _pop_first(items: List[Dict[str, Any]], pred: Callable[[Dict[str, Any]], bool]) -> Dict[str, Any] | None:
    """Retire et retourne le 1er élément qui satisfait pred, sinon None (ordre stable)."""
    for i, it in enumerate(items):
        try:
            if pred(it):
                return items.pop(i)
        except Exception:
            continue
    return None


def rebalance_minima(
    ds: List[Dict[str, Any]],
    src: List[Dict[str, Any]],
    min_ds: int,
    min_src: int,
    is_dataset_like_url: Callable[[str], bool],
    to_dataset: Callable[[Dict[str, Any]], Dict[str, Any]],
    to_source: Callable[[Dict[str, Any]], Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Garantit des minimums de liens côté datasets/sources en reclassant si besoin.
    - ds/src : listes d'items (dict) contenant au moins 'url' et éventuellement 'intent'
    - min_ds/min_src : quotas minimum
    - is_dataset_like_url : heuristique URL->bool (fournie par l'appelant)
    - to_dataset / to_source : fonctions de conversion (mutent 'intent' ou autres)

    Politique :
      1) D'abord déplacer des candidats plausibles (URL "dataset-like") depuis l'autre liste.
      2) En dernier recours, déplacer des éléments génériques (éviter d'envoyer des PDF vers datasets).
      3) Ordre stable conservé (pop du premier match).
    """
    ds_list = list(ds or [])
    src_list = list(src or [])

    if len(ds_list) >= min_ds and len(src_list) >= min_src:
        return ds_list, src_list

    # Besoin de +datasets ?
    if len(ds_list) < min_ds:
        deficit = min_ds - len(ds_list)

        # a) candidats plausibles dans src (URL dataset-like)
        while deficit > 0:
            moved = _pop_first(src_list, lambda it: is_dataset_like_url(_url_of(it)))
            if not moved:
                break
            ds_list.append(to_dataset(moved))
            deficit -= 1

        # b) fallback : éléments non-PDF
        while deficit > 0 and src_list:
            moved = _pop_first(src_list, lambda it: not is_pdf_url(_url_of(it)))
            if not moved:
                break
            ds_list.append(to_dataset(moved))
            deficit -= 1

    # Besoin de +sources ?
    if len(src_list) < min_src:
        deficit = min_src - len(src_list)

        # a) candidats "peu dataset-like" ou PDF depuis ds
        while deficit > 0:
            moved = _pop_first(
                ds_list,
                lambda it: not is_dataset_like_url(_url_of(it)) or is_pdf_url(_url_of(it)),
            )
            if not moved:
                break
            src_list.append(to_source(moved))
            deficit -= 1

        # b) fallback : n'importe quel élément restant
        while deficit > 0 and ds_list:
            moved = ds_list.pop(0)
            src_list.append(to_source(moved))
            deficit -= 1

    return ds_list, src_list
