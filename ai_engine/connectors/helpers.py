# ai_engine/connectors/helpers.py
import re
import unicodedata

def sanitize_keyword(keyword: str) -> str:
    """
    Remove accents, trim spaces, collapse multiple spaces -> '+'
    >>> sanitize_keyword("  Énergie   renouvelable   ")
    'energie+renouvelable'
    """
    # 1. trim + collapse spaces
    kw = re.sub(r"\s+", " ", keyword.strip())
    # 2. remove accents
    kw_ascii = (
        unicodedata.normalize("NFKD", kw)
        .encode("ascii", "ignore")
        .decode()
    )
    # 3. lower + replace spaces with +
    return kw_ascii.lower().replace(" ", "+")
