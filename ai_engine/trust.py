from __future__ import annotations
from urllib.parse import urlparse
from typing import Iterable


def host(u: str | None) -> str:
    if not u:
        return ""
    try:
        return urlparse(u).netloc.lower()
    except Exception:
        return ""


def is_trusted(hostname: str, domains: Iterable[str]) -> bool:
    h = (hostname or "").lower()
    for d in domains or []:
        d = str(d).lower().strip()
        if not d:
            continue
        if h == d or h.endswith("." + d):
            return True
    return False


def trusted_weight_from_url(u: str | None, boost: float, domains: Iterable[str]) -> float:
    base = 1.0
    return base + float(boost or 0.0) if is_trusted(host(u), domains) else base
