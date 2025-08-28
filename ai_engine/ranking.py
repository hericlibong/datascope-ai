from __future__ import annotations
from urllib.parse import urlparse
from typing import Callable, Any


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