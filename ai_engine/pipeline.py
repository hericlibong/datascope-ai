import ai_engine
import inspect
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
    max_total_per_angle: int = 10,
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

    # ---------------- boucle sur les angles ---------------------------- #
    for idx, kw_result in enumerate(keywords_per_angle):
        print(f"\n=== [ANGLE {idx}] {kw_result.sets[0].angle_title} ===")  # 🖨️ début angle
        seen_urls: set[str] = set()
        angle_suggestions: list[DatasetSuggestion] = []

        # ---> boucle sur les 5 mots-clés proposés pour CET angle
        for kw_set in kw_result.sets:                       # (normalement 1 set)
            for keyword in kw_set.keywords:                 # les 5 mots-clés
                print(f"→ keyword='{keyword}'")

                # ----> boucle sur chaque connecteur
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
                        print("ok")   # appel réussi

                    for raw_ds in raw_results:
                        # ---------- conversion vers DatasetSuggestion -------------------------------------
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
                                        print(f"      ↳ échec {fn} : {conv_err!r}")  # ⬅️ log détaillé
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

                        # ---------- marquage et stockage ---------------------------
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
        source_url   = item.link,          # <-- champ correct
        found_by     = "LLM",
        angle_idx    = angle_idx,          # marquage de l’angle parent
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
) -> tuple[
    AnalysisPackage,        # extraction + angles « brut »
    str,                    # markdown
    float,                  # score_10
    list[AngleResources],   # ressources détaillées par angle
]:
    """Orchestre l’ensemble du workflow DataScope et regroupe les ressources
    par angle éditorial dans des objets `AngleResources`."""

    # -- validation longueur -------------------------------------------------
    _validate(article_text)

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

    # -- 5. Datasets via connecteurs (liste par angle) ----------------------
    connectors_sets = run_connectors(keywords_per_angle)

    # 6. Sources LLM par angle  ------------------------------
    llm_sources_sets = llm_sources.run(angle_result)

    # 7. Suggestions de visus  -------------------------------
    viz_sets = viz.run(angle_result)

    # 8. Fusion et construction AngleResources ---------------
    angle_resources: list[AngleResources] = []
    for idx, angle in enumerate(angle_result.angles):
        kw_set   = keywords_per_angle[idx] if idx < len(keywords_per_angle) else None
        conn_ds  = connectors_sets[idx]    if idx < len(connectors_sets)    else []

        # ---- conversion LLM -> DatasetSuggestion
        llm_raw   = llm_sources_sets[idx]  if idx < len(llm_sources_sets)   else []
        llm_ds    = [_llm_to_ds(obj, angle_idx=idx) for obj in llm_raw]

        viz_list  = viz_sets[idx]          if idx < len(viz_sets)           else []

        # ---- fusion + déduplication (URL) ------------------
        seen_urls = {d.source_url for d in conn_ds}
        merged_ds = conn_ds[:]
        for ds in llm_ds:
            if ds.source_url not in seen_urls:
                merged_ds.append(ds)
                seen_urls.add(ds.source_url)

        angle_resources.append(
            AngleResources(
                index          = idx,
                title          = angle.title,
                description    = angle.rationale,
                keywords       = kw_set.sets[0].keywords if kw_set else [],
                datasets       = merged_ds,
                sources        = llm_ds,
                visualizations = viz_list,
            )
        )


    # -- 9. Packaging « historique » (extraction + angles) -------------------
    packaged, markdown = package(extraction_result, angle_result)

    # -- 10. Mémoire utilisateur --------------------------------------------
    get_memory(user_id).save_context(
        {"article": article_text},
        {"summary": f"[score={score_10}] Angles: {[a.title for a in angle_result.angles]}"},
    )

    return packaged, markdown, score_10, angle_resources

