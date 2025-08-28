from __future__ import annotations
from urllib.parse import urlparse
import re
from typing import Iterable, List, Set, Tuple, Any

_re_split = re.compile(r"\W+", flags=re.UNICODE)


def tokenize(s: str | None) -> List[str]:
    if not s:
        return []
    return [t for t in _re_split.split(s.lower()) if len(t) >= 3]


def bigrams(tokens: List[str]) -> Set[Tuple[str, str]]:
    return set(zip(tokens, tokens[1:])) if len(tokens) >= 2 else set()


def url_path_tokens(u: str | None) -> List[str]:
    if not u:
        return []
    try:
        path = urlparse(u).path or ""
        path = path.replace("-", " ").replace("_", " ").replace(".", " ")
        return tokenize(path)
    except Exception:
        return []


def build_angle_signature(title: str, rationale: str, keywords: Iterable[str]) -> tuple[set[str], set[tuple[str, str]]]:
    angle_text = f"{title or ''} {rationale or ''}"
    if keywords:
        angle_text += " " + " ".join(list(keywords))
    toks = tokenize(angle_text)
    return set(toks), bigrams(toks)


def _item_text_tokens(obj: Any, pick_url_for_weight) -> tuple[set[str], set[tuple[str, str]]]:
    parts = [
        getattr(obj, "title", "") or "",
        getattr(obj, "description", "") or "",
        getattr(obj, "source_name", "") or getattr(obj, "source", "") or "",
        getattr(obj, "organization", "") or "",
    ]
    u = pick_url_for_weight(obj)
    toks = tokenize(" ".join(parts)) + url_path_tokens(u)
    uni = set(toks)
    bi = bigrams(toks)
    return uni, bi


def theme_weight_and_flag(obj: Any, angle_unigrams: set[str], angle_bigrams: set[tuple[str, str]], *, min_hits: int, penalty: float, pick_url_for_weight) -> tuple[float, bool]:
    """
    Returns (weight, is_off_theme).
    - weight = 1.0 if on-topic, else 1.0 - penalty (soft).
    - is_off_theme=True if no bigram match AND unigram overlap < min_hits.
    """
    item_uni, item_bi = _item_text_tokens(obj, pick_url_for_weight)
    unigram_hits = len(angle_unigrams.intersection(item_uni))
    bigram_match = bool(angle_bigrams.intersection(item_bi))
    off_theme = (not bigram_match) and (unigram_hits < min_hits)
    return (1.0 if not off_theme else 1.0 - penalty), off_theme