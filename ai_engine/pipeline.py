import ai_engine
from ai_engine.utils import token_len
from ai_engine.chains import extraction, angles
from ai_engine.formatter import package
from ai_engine.schemas import AnalysisPackage
from ai_engine.scoring import compute_score
from ai_engine.chains import keywords
from ai_engine.chains import viz

MAX_TOKENS = 8_000


def _validate(text: str) -> None:
    if token_len(text, model=ai_engine.OPENAI_MODEL) > MAX_TOKENS:
        raise ValueError("Article trop long")


def _score(extr) -> int:
    """Très simple : +10 points par personne ou org, max 100."""
    raw = (len(extr.persons) + len(extr.organizations)) * 10
    return min(raw, 100)


def run(article_text: str) -> tuple[AnalysisPackage, str, int]:
    """
    Orchestration complète, sans LCEL :
    - validation longueur
    - extraction
    - scoring
    - angles
    - packaging (JSON + markdown)
    Retourne : (package_json, markdown, score)
    """
    # 1. validation
    _validate(article_text)

    # 2. extraction
    extraction_result = extraction.run(article_text)

    # 3. scoring
    score = compute_score(extraction_result, article_text, model=ai_engine.OPENAI_MODEL)

    # 4. angles
    angle_result = angles.run(article_text)

    # 5. keywors for datasets
    keywords_result = keywords.run(angle_result)

    # 6 vizulisations
    viz_result = viz.run(angle_result)

    # 7. packaging (JSON consolidé + markdown)
    packaged, markdown = package(extraction_result, angle_result)

    return packaged, markdown, score
