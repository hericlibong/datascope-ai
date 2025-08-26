# backend/ai_engine/services.py

from __future__ import annotations

from typing import Optional, Dict
from urllib.parse import urlparse, urlunparse

import requests
from django.conf import settings


def _normalize_url(url: str) -> str:
    """
    Minimal normalization:
    - If no scheme and it looks like a domain (or starts with 'www.'), default to https.
    - Otherwise, return as-is (we keep this function intentionally simple for MVP).
    """
    if not url:
        return url
    parsed = urlparse(url)
    if not parsed.scheme:
        # domain present without scheme
        if parsed.netloc:
            return urlunparse(parsed._replace(scheme="https"))
        # "www.example.com" case is often parsed as path
        if parsed.path.startswith("www."):
            return "https://" + url
    return url


def validate_url(url: str, timeout: Optional[float] = None) -> Dict[str, object]:
    """
    Lightweight HTTP link validator for dataset/documentation URLs.

    Behavior (MVP, no heavy machinery):
    - Try HEAD with redirects enabled; fallback to GET when HEAD is not allowed (405/403) or fails.
    - Follow redirects and return the final resolved URL.
    - Classify into:
        * "ok"         -> final status is 2xx and no redirect history
        * "redirected" -> final status is 2xx and there was at least one redirect
        * "not_found"  -> final status is 404 or 410
        * "error"      -> any other status or network-level error (timeouts, TLS, invalid URL)
    - Keep it synchronous and side-effect free (no DB writes).
    - Do NOT download bodies: GET uses stream=True to avoid reading content.

    Returns:
        {
          "input_url":  <str original>,
          "status":     "ok"|"redirected"|"not_found"|"error",
          "http_status": <int or None>,
          "final_url":  <str or None>,
          "error":      <str or None>
        }
    """
    ua = getattr(settings, "URL_VALIDATION_USER_AGENT", "DatascopeAI/validator")
    to = timeout if timeout is not None else getattr(settings, "URL_VALIDATION_TIMEOUT", 5)
    headers = {"User-Agent": ua, "Accept": "*/*"}

    original = url or ""
    normalized = _normalize_url(original)

    def _result(status: str, http_status: Optional[int], final_url: Optional[str], error: Optional[str] = None):
        return {
            "input_url": original,
            "status": status,
            "http_status": http_status,
            "final_url": final_url,
            "error": error,
        }

    if not normalized:
        return _result("error", None, None, "EmptyURL")

    try:
        # First try HEAD (cheap). Some servers block it (405/403) -> fallback GET.
        resp = requests.head(
            normalized,
            allow_redirects=True,
            timeout=to,
            headers=headers,
        )

        if resp.status_code in (405, 403):
            # HEAD not allowed -> try a lightweight GET without consuming body
            resp = requests.get(
                normalized,
                allow_redirects=True,
                timeout=to,
                headers=headers,
                stream=True,
            )

        final_url = resp.url
        history_present = bool(resp.history) or (final_url and final_url != normalized)

        # Classify
        if resp.status_code in (404, 410):
            return _result("not_found", resp.status_code, final_url)
        elif 200 <= resp.status_code < 300:
            return _result("redirected" if history_present else "ok", resp.status_code, final_url)
        elif 300 <= resp.status_code < 400:
            # Should be rare with allow_redirects=True; treat as redirected anyway
            return _result("redirected", resp.status_code, final_url)
        else:
            # 4xx (except 404/410) or 5xx -> error
            return _result("error", resp.status_code, final_url, f"HTTP {resp.status_code}")

    except requests.exceptions.Timeout:
        return _result("error", None, None, "Timeout")
    except requests.exceptions.InvalidURL:
        return _result("error", None, None, "InvalidURL")
    except requests.exceptions.SSLError:
        return _result("error", None, None, "SSLError")
    except requests.exceptions.ConnectionError:
        return _result("error", None, None, "ConnectionError")
    except Exception as exc:
        # Keep it minimal and safe for MVP
        return _result("error", None, None, exc.__class__.__name__)
