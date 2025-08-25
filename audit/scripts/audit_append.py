# scripts/audit_append.py
import json
import csv
import sys
from pathlib import Path
from urllib.parse import urlparse

def is_fr_domain(d: str) -> bool:
    if not d:
        return False
    if d.endswith(".gouv.fr"):
        return True
    return d in {"data.gouv.fr", "insee.fr"}  # ancrages minimaux

def domain(url: str) -> str:
    try:
        netloc = urlparse(url).netloc or url.split("/")[0]
        netloc = netloc.lower()
        if netloc.startswith("www."):
            netloc = netloc[4:]
        return netloc
    except Exception:
        return ""

def summarize(analysis: dict) -> dict:
    analysis_id = analysis.get("id")
    article = analysis.get("article") or {}
    article_id = article.get("id")
    title = (article.get("title") or "").strip()
    language = (article.get("language") or "").strip().lower()
    fr_applicable = (language == "fr")

    entities = analysis.get("entities") or []
    angles = analysis.get("angles") or []
    datasets = analysis.get("datasets") or []

    # NEW — keywords (tous angles confondus, max 5, uniques)
    angle_resources = analysis.get("angle_resources") or []
    kw_seen, kw_flat = set(), []
    for ar in angle_resources:
        for k in (ar.get("keywords") or []):
            k = (k or "").strip()
            if k and k not in kw_seen:
                kw_seen.add(k)
                kw_flat.append(k)
            if len(kw_flat) >= 5:
                break
        if len(kw_flat) >= 5:
            break
    keywords_sample = "|".join(kw_flat)  # ex: "sécheresse|Orne|restrictions d'eau"

    entities_count = len(entities)
    angles_count = len(angles)
    datasets_count = len(datasets)

    domains = {}
    for ds in datasets:
        d = domain((ds.get("link") or "").strip())
        if d:
            domains[d] = domains.get(d, 0) + 1

    if fr_applicable:
        fr_hits = sum(1 for ds in datasets if is_fr_domain(domain((ds.get("link") or "").strip())))
        nonfr_hits = max(datasets_count - fr_hits, 0)
        den = datasets_count if datasets_count > 0 else 0
        fr_ratio = f"{fr_hits}/{den}"
    else:
        fr_hits = ""
        nonfr_hits = ""
        fr_ratio = ""

    top_domains = "|".join([d for d, _ in sorted(domains.items(), key=lambda kv: kv[1], reverse=True)[:3]])

    locs = [e.get("value") for e in entities if e.get("type") == "LOC"]
    locs_sample = "|".join(sorted(set(locs))[:3])

    return {
        "analysis_id": analysis_id,
        "article_id": article_id,
        "title": title,
        "language": language,            # (déjà là)
        "fr_applicable": fr_applicable,  # (déjà là)
        "angles_count": angles_count,
        "entities_count": entities_count,
        "datasets_count": datasets_count,
        "fr_hits": fr_hits,
        "nonfr_hits": nonfr_hits,
        "fr_ratio": fr_ratio,
        "top_domains": top_domains,
        "locs_sample": locs_sample,
        "keywords_sample": keywords_sample,  # NEW
    }

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/audit_append.py <analysis_json_path> <summary_csv_path>")
        sys.exit(1)

    in_path = Path(sys.argv[1])
    out_csv = Path(sys.argv[2])

    data = json.loads(in_path.read_text(encoding="utf-8"))
    row = summarize(data)

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    write_header = not out_csv.exists()

    with out_csv.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(row.keys()))
        if write_header:
            w.writeheader()
        w.writerow(row)

    print(f"[OK] Ajouté: analysis #{row['analysis_id']} → {out_csv}")
