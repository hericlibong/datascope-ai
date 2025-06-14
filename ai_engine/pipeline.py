import ai_engine
import inspect
from ai_engine.utils import token_len
from ai_engine.chains import extraction, angles
from ai_engine.formatter import package
from ai_engine.schemas import AnalysisPackage, DatasetSuggestion, KeywordsResult
from ai_engine.scoring import compute_score
from ai_engine.chains import keywords, viz
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
    keywords_result: KeywordsResult,
    max_per_keyword: int = 2,
    max_total: int = 25,
) -> list[DatasetSuggestion]:
    """
    Interroge les connecteurs open-data et renvoie des `DatasetSuggestion` normalisés,
    en loggant chaque étape pour diagnostiquer les conversions et les déduplications.
    """

    connectors = [
        DataGouvClient(),
        DataGovClient(),
        CanadaGovClient(),
        UKGovClient(),
        HdxClient(),
    ]

    seen_urls: set[str] = set()
    suggestions: list[DatasetSuggestion] = []

    for kw_set in keywords_result.sets:
        for keyword in kw_set.keywords:
            for connector in connectors:
                sig = inspect.signature(connector.search).parameters
                try:
                    if "max_results" in sig:
                        raw_results = connector.search(
                            keyword, max_results=max_per_keyword
                        )
                    elif "page_size" in sig:
                        raw_results = connector.search(
                            keyword, page_size=max_per_keyword
                        )
                    else:
                        raw_results = connector.search(keyword)
                except Exception as e:
                    print(f"[{connector.__class__.__name__}] ERREUR réseau : {e!r}")
                    continue

                for raw_ds in raw_results:
                    # --- LOG 1 : objet brut reçu ------------------------------------
                    print(
                        f"[{connector.__class__.__name__}] RAW → {type(raw_ds).__name__}"
                    )

                    # ---------------------------------------------------------------
                    # Conversion vers DatasetSuggestion
                    suggestion: DatasetSuggestion | None = None

                    # 1/ Méthode canonique
                    if hasattr(connector, "to_suggestion"):
                        try:
                            suggestion = connector.to_suggestion(raw_ds)
                        except Exception as conv_err:
                            print("   ↳ échec to_suggestion :", conv_err)

                    # 2/ Méthodes héritées / spécifiques
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
                                    print(f"   ↳ échec {fn} :", conv_err)
                                    suggestion = None
                                break

                    # 3/ Cas où l’objet brut est déjà du bon type
                    if suggestion is None and isinstance(raw_ds, DatasetSuggestion):
                        suggestion = raw_ds

                    # --- LOG 2 : résultat de la conversion -------------------------
                    if suggestion is None:
                        print("   ⚠️  ignoré (pas convertible)")
                        continue
                    else:
                        print("   ✅ OK →", suggestion.title[:60])

                    # Déduplication
                    if suggestion.source_url in seen_urls:
                        print("   ⏩ doublon, ignoré")
                        continue

                    suggestions.append(suggestion)
                    seen_urls.add(suggestion.source_url)

                    # Limite globale
                    if len(suggestions) >= max_total:
                        print("## Limite max_total atteinte — retour anticipé ##")
                        return suggestions

    return suggestions



def run(
    article_text: str,
    user_id: str = "anon",
) -> tuple[
    AnalysisPackage, str, float, KeywordsResult, list[DatasetSuggestion]
]:
    """Pipeline principal DataScope."""

    _validate(article_text)

    # 1. Extraction
    extraction_result = extraction.run(article_text)

    # 2. Scoring
    score_10 = compute_score(
        extraction_result, article_text, model=ai_engine.OPENAI_MODEL
    )
    score_10 = round(score_10, 1)

    # 3. Angles
    angle_result = angles.run(article_text)

    # 4. Keywords
    keywords_result = keywords.run(angle_result)
    print("[DEBUG] keywords_result =", keywords_result.sets[0].keywords[:5])

    # 5. Datasets via connecteurs
    datasets = run_connectors(keywords_result)

    # 6. Visualisation (placeholder)
    _ = viz.run(angle_result)

    # 7. Packaging
    packaged, markdown = package(extraction_result, angle_result)

    # 8. Mémorisation utilisateur
    memory = get_memory(user_id)
    output_text = f"[score={score_10}] Angles: {[a.title for a in angle_result.angles]}"
    memory.save_context({"article": article_text}, {"summary": output_text})

    return packaged, markdown, score_10, keywords_result, datasets
