# ai_engine/connectors/format_utils.py
from __future__ import annotations
import re
from pathlib import Path
from typing import Optional, Set

def get_format(resource: dict | None, valid_set: Set[str]) -> Optional[str]:
    """Tente de déduire le format (‘csv’, ‘json’, …) à partir d’un dict CKAN/ODP."""
    if not resource:
        return None

    # 1) Champ "format"
    raw = resource.get("format", "")
    if isinstance(raw, str) and raw.strip():
        fmt = raw.lower().strip()
        if fmt in valid_set:
            return fmt

    # 2) Mime-type
    mime = (resource.get("mime") or resource.get("mimetype") or "")
    if isinstance(mime, str):
        mime = mime.lower()
        for token in valid_set:
            if token in mime:
                return token

    # 3) Extension de l’URL
    url = resource.get("url") or resource.get("path") or ""
    if isinstance(url, str) and url:
        ext = Path(url.split("?", 1)[0]).suffix.lower().lstrip(".")
        if ext == "zip":                                    # cas geojson.zip
            inner = re.search(r"\.(\w+)\.zip$", url, re.I)
            ext = inner.group(1).lower() if inner else ext
        if ext in valid_set:
            return ext
    return None
