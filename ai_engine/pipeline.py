import ai_engine
from ai_engine.utils import token_len
from ai_engine.chains import extraction, angles
from ai_engine.formatter import package
from ai_engine.schemas import AnalysisPackage
from ai_engine.scoring import compute_score
from ai_engine.chains import keywords
from ai_engine.chains import viz
from ai_engine.memory import get_memory

from ai_engine.schemas import DatasetSuggestion
from ai_engine.connectors.data_gouv import DataGouvClient
from ai_engine.connectors.data_gov import DataGovClient
from ai_engine.connectors.data_canada import CanadaGovClient
from ai_engine.connectors.data_uk import UKGovClient
from ai_engine.connectors.hdx_data import HdxClient

from ai_engine.schemas import KeywordsResult

MAX_TOKENS = 8_000


def _validate(text: str) -> None:
    if token_len(text, model=ai_engine.OPENAI_MODEL) > MAX_TOKENS:
        raise ValueError("Article trop long")


def _score(extr) -> int:
    """Très simple : +10 points par personne ou org, max 100."""
    raw = (len(extr.persons) + len(extr.organizations)) * 10
    return min(raw, 100)


def run_connectors(keywords_result: KeywordsResult, max_per_keyword: int = 2, max_total: int = 25) -> list[DatasetSuggestion]:
    """
    Appelle tous les connecteurs configurés pour récupérer des datasets
    en fonction des mots-clés générés à partir des angles éditoriaux.
    """
    connectors = [
        DataGouvClient(),
        DataGovClient(),
        CanadaGovClient(),
        UKGovClient(),
        HdxClient(),
        
    ]

    seen_urls = set()  # pour éviter les doublons
    suggestions = []

    # Parcours de chaque ensemble de mots-clés générés par angle
    for kw_set in keywords_result.sets:
        for keyword in kw_set.keywords:
            for connector in connectors:
                try:
                    # Appel du connecteur avec le mot-clé donné
                    results = connector.search(keyword, max_results=max_per_keyword)
                    for ds in results:
                        # Évite les doublons en testant sur le lien
                        if ds.source_url not in seen_urls:
                            suggestions.append(ds)
                            seen_urls.add(ds.source_url)
                        if len(suggestions) >= max_total:
                            return suggestions
                except Exception:
                    # Si un connecteur échoue, on passe silencieusement (robustesse)
                    continue

    return suggestions


def run(article_text: str, user_id: str = "anon") -> tuple[AnalysisPackage, str, int]:
    """
    Orchestration complète, sans LCEL :
    - validation longueur
    - extraction
    - scoring
    - angles
    - packaging (JSON + markdown)
    Retourne : (package_json, markdown, score)
    """
    _validate(article_text)

    extraction_result = extraction.run(article_text)
    score_10 = compute_score(extraction_result, article_text, model=ai_engine.OPENAI_MODEL)
    score_10 = round(score_10, 1)
    angle_result = angles.run(article_text)

    # TODO : exposer keywords_result et viz_result dans AnalysisPackage quand validé

    keywords_result = keywords.run(angle_result)
    datasets = run_connectors(keywords_result)
    viz_result = viz.run(angle_result)

    packaged, markdown = package(extraction_result, angle_result)

    memory = get_memory(user_id)
    
    output_text = f"[score={score_10}] Angles: {[a.title for a in angle_result.angles]}"

    memory.save_context(
        {"article": article_text},
        {"summary": output_text}
)

    return packaged, markdown, score_10, datasets

