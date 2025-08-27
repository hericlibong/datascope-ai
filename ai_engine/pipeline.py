import ai_engine
import inspect
import re  # NEW THEME: tokenisation simple
from ai_engine.utils import token_len
from ai_engine.chains import extraction, angles
from ai_engine.formatter import package
from ai_engine.schemas import AnalysisPackage, DatasetSuggestion, KeywordsResult, LLMSourceSuggestion, AngleResources
from ai_engine.scoring import compute_score
from ai_engine.chains import keywords, viz, llm_sources
from ai_engine.memory import get_memory

from ai_engine.connectors.data_gouv import DataGouvClient
from ai_engine.connectors.data_gov import DataGovClient
from ai_engine.connectors.data_canada import CanadaGovClient
from ai_engine.connectors.data_uk import UKGovClient
from ai_engine.connectors.hdx_data import HdxClient

# --- NEW imports
from django.conf import settings
from ai_engine.services import validate_url
from urllib.parse import urlparse  # NEW TRUSTED

MAX_TOKENS = 8_000


def _validate(text: str) -> None:
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
    """
    Interroge les connecteurs open-data pour CHAQUE angle et renvoie
    une liste de listes alignée sur l’ordre des angles.

    Chaque DatasetSuggestion sort avec :
        • found_by  = "CONNECTOR"
        • angle_idx = index de l’angle parent
    """

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


# ------------------------------------------------------------------
def _llm_to_ds(item: LLMSourceSuggestion, *, angle_idx: int) -> DatasetSuggestion:
    """Convertit une LLMSourceSuggestion en DatasetSuggestion standardisé."""
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
# ------------------------------------------------------------------


def run(
    article_text: str,
    user_id: str = "anon",
    validate_urls: bool = False,        # NEW
    filter_404: bool | None = None,     # NEW
    theme_strict: bool | None = None,   # NEW THEME (optionnel)
) -> tuple[
    AnalysisPackage,
    str,
    float,
    list[AngleResources],
]:
    """Orchestre l’ensemble du workflow DataScope et regroupe les ressources
    par angle éditorial dans des objets `AngleResources`."""

    # -- validation longueur -------------------------------------------------
    _validate(article_text)

    if filter_404 is None:
        filter_404 = getattr(settings, "URL_VALIDATION_FILTER_404", True)

    # --- NEW THEME: paramètres du filtre thématique -------------------------
    if theme_strict is None:
        theme_strict = bool(getattr(settings, "THEME_FILTER_STRICT_DEFAULT", False))
    _THEME_MIN_HITS = int(getattr(settings, "THEME_FILTER_MIN_UNIGRAM_HITS", 2))
    _THEME_PENALTY  = float(getattr(settings, "THEME_FILTER_SOFT_PENALTY", 0.15) or 0.0)
    # -----------------------------------------------------------------------

    # Small per-run cache to avoid validating the same URL multiple times
    _url_validation_cache: dict[str, dict] = {}

    def _validate_once(url: str) -> dict:
        if not url:
            return {"input_url": "", "status": "error", "http_status": None, "final_url": None, "error": "EmptyURL"}
        cached = _url_validation_cache.get(url)
        if cached:
            return cached
        res = validate_url(url)
        _url_validation_cache[url] = res
        return res

    def _get_url(obj):
        if isinstance(obj, dict):
            return obj.get("source_url") or obj.get("link")
        return getattr(obj, "source_url", None) or getattr(obj, "link", None)

    def _set_url(obj, new_url: str):
        if isinstance(obj, dict):
            if "source_url" in obj:
                obj["source_url"] = new_url
            if "link" in obj:
                obj["link"] = new_url
        else:
            if hasattr(obj, "source_url"):
                obj.source_url = new_url
            if hasattr(obj, "link"):
                obj.link = new_url

    def _set_validation(obj, payload: dict):
        if isinstance(obj, dict):
            obj["validation"] = payload
        else:
            setattr(obj, "validation", payload)

    # --- NEW TRUSTED: helpers re-rank qualitatif ---------------------------
    def _host(u: str | None) -> str:
        if not u:
            return ""
        try:
            return urlparse(u).netloc.lower()
        except Exception:
            return ""

    def _is_trusted(host: str) -> bool:
        for d in getattr(settings, "TRUSTED_DOMAINS", []):
            d = str(d).lower().strip()
            if not d:
                continue
            if host == d or host.endswith("." + d):
                return True
        return False

    def _trusted_weight_from_url(u: str | None) -> float:
        base = 1.0
        boost = float(getattr(settings, "TRUSTED_SOFT_WEIGHT", 0.15) or 0.0)
        return base + boost if _is_trusted(_host(u)) else base

    def _pick_url_for_weight(obj) -> str | None:
        v = getattr(obj, "validation", None)
        if isinstance(v, dict) and v.get("final_url"):
            return v["final_url"]
        return getattr(obj, "source_url", None) or getattr(obj, "link", None)
    # -----------------------------------------------------------------------

    # --- NEW THEME: helpers filtre thématique ------------------------------
    _re_split = re.compile(r"\W+", flags=re.UNICODE)

    def _tokenize(s: str | None) -> list[str]:
        if not s:
            return []
        return [t for t in _re_split.split(s.lower()) if len(t) >= 3]

    def _bigrams(tokens: list[str]) -> set[tuple[str, str]]:
        return set(zip(tokens, tokens[1:])) if len(tokens) >= 2 else set()

    def _url_path_tokens(u: str | None) -> list[str]:
        if not u:
            return []
        try:
            path = urlparse(u).path or ""
            path = path.replace("-", " ").replace("_", " ").replace(".", " ")
            return _tokenize(path)
        except Exception:
            return []

    def _item_text_tokens(obj) -> tuple[set[str], set[tuple[str, str]]]:
        parts = []
        parts.append(getattr(obj, "title", "") or "")
        parts.append(getattr(obj, "description", "") or "")
        parts.append(getattr(obj, "source_name", "") or getattr(obj, "source", "") or "")
        parts.append(getattr(obj, "organization", "") or "")
        u = _pick_url_for_weight(obj)
        toks = _tokenize(" ".join(parts)) + _url_path_tokens(u)
        uni = set(toks)
        bi = _bigrams(toks)
        return uni, bi

    def _theme_weight_and_flag(obj, angle_unigrams: set[str], angle_bigrams: set[tuple[str, str]]) -> tuple[float, bool]:
        """
        Retourne (poids, is_off_theme).
        - poids = 1.0 si OK, 1.0 - _THEME_PENALTY si hors-thème (soft).
        - is_off_theme True si aucun bigram et hits unigrams < seuil.
        """
        item_uni, item_bi = _item_text_tokens(obj)
        unigram_hits = len(angle_unigrams.intersection(item_uni))
        bigram_match = bool(angle_bigrams.intersection(item_bi))
        off_theme = (not bigram_match) and (unigram_hits < _THEME_MIN_HITS)
        return (1.0 if not off_theme else 1.0 - _THEME_PENALTY), off_theme
    # -----------------------------------------------------------------------

    # -- 1. Extraction -------------------------------------------------------
    extraction_result = extraction.run(article_text)

    # -- 2. Scoring ----------------------------------------------------------
    score_10 = round(
        compute_score(extraction_result, article_text, model=ai_engine.OPENAI_MODEL),
        1,
    )

    # -- 3. Angles -----------------------------------------------------------
    angle_result = angles.run(article_text)
    print(f"[DEBUG] {len(angle_result.angles)} angles générés")

    # -- 4. Keywords (liste alignée) ----------------------------------------
    keywords_per_angle = keywords.run(angle_result)

    angle_resources: list[AngleResources] = []
    # -- 5. Datasets via connecteurs (liste par angle) ----------------------
    connectors_sets = run_connectors(keywords_per_angle)

    # 6. Sources LLM par angle  ------------------------------
    llm_sources_sets = llm_sources.run(angle_result)

    # 7. Suggestions de visus  -------------------------------
    viz_sets = viz.run(angle_result)

    # 8. Fusion et construction AngleResources ---------------
    for idx, angle in enumerate(angle_result.angles):
        kw_set   = keywords_per_angle[idx] if idx < len(keywords_per_angle) else None
        conn_ds  = connectors_sets[idx]    if idx < len(connectors_sets)    else []

        llm_raw   = llm_sources_sets[idx] if idx < len(llm_sources_sets) else []
        llm_ds    = [_llm_to_ds(obj, angle_idx=idx) for obj in llm_raw]

        viz_list  = viz_sets[idx]          if idx < len(viz_sets)           else []

        # ---- fusion + déduplication (URL) ------------------
        seen_urls = {d.source_url for d in conn_ds}
        merged_ds = conn_ds[:]
        for ds in llm_ds:
            if ds.source_url not in seen_urls:
                merged_ds.append(ds)
                seen_urls.add(ds.source_url)

        # --- URL validation hook (Step 3) ----------------------------------
        if validate_urls:
            validated_datasets = []
            for ds in merged_ds:
                url = _get_url(ds)
                res = _validate_once(url)
                _set_validation(ds, res)

                if res.get("status") in ("ok", "redirected") and res.get("final_url"):
                    _set_url(ds, res["final_url"])

                if not (filter_404 and res.get("status") == "not_found"):
                    validated_datasets.append(ds)
            merged_ds = validated_datasets

            validated_sources = []
            for src in llm_raw:
                url = _get_url(src)
                res = _validate_once(url)
                _set_validation(src, res)

                if res.get("status") in ("ok", "redirected") and res.get("final_url"):
                    _set_url(src, res["final_url"])

                if not (filter_404 and res.get("status") == "not_found"):
                    validated_sources.append(src)
            llm_raw = validated_sources
        # -------------------------------------------------------------------

        # --- NEW THEME: signature thématique de l’angle ----------------------
        angle_text = angle.title or ""
        if kw_set and getattr(kw_set, "sets", None):
            angle_text += " " + " ".join(kw_set.sets[0].keywords or [])
        _ang_tokens = _tokenize(angle_text)
        _ANG_UNI = set(_ang_tokens)
        _ANG_BI  = _bigrams(_ang_tokens)
        # ---------------------------------------------------------------------

        # --- NEW THEME: calcul des poids + strict (LLM only) -----------------
        _theme_w: dict[int, float] = {}

        themed_datasets = []
        for ds in merged_ds:
            if getattr(ds, "found_by", "") == "LLM":
                w, off = _theme_weight_and_flag(ds, _ANG_UNI, _ANG_BI)
                if theme_strict and off:
                    continue  # drop en mode strict (LLM only)
                _theme_w[id(ds)] = w
            else:
                _theme_w[id(ds)] = 1.0  # CONNECTOR inchangé
            themed_datasets.append(ds)
        merged_ds = themed_datasets

        themed_sources = []
        for src in llm_raw:
            w, off = _theme_weight_and_flag(src, _ANG_UNI, _ANG_BI)
            if theme_strict and off:
                continue
            _theme_w[id(src)] = w
            themed_sources.append(src)
        llm_raw = themed_sources
        # ---------------------------------------------------------------------

        # --- Trusted re-ranking (soft) × Theme weight ------------------------
        def _final_weight(obj) -> float:
            return _trusted_weight_from_url(_pick_url_for_weight(obj)) * _theme_w.get(id(obj), 1.0)

        merged_ds.sort(key=_final_weight, reverse=True)
        llm_raw.sort(key=_final_weight, reverse=True)
        # --------------------------------------------------------------------

        angle_resources.append(
            AngleResources(
                index          = idx,
                title          = angle.title,
                description    = angle.rationale,
                keywords       = kw_set.sets[0].keywords if kw_set else [],
                datasets       = merged_ds,
                sources        = llm_raw,
                visualizations = viz_list,
            )
        )

    # -- 9. Packaging « historique » ----------------------------------------
    packaged, markdown = package(extraction_result, angle_result)

    # -- 10. Mémoire utilisateur --------------------------------------------
    get_memory(user_id).save_context(
        {"article": article_text},
        {"summary": f"[score={score_10}] Angles: {[a.title for a in angle_result.angles]}"},
    )

    return packaged, markdown, score_10, angle_resources
