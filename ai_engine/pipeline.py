import ai_engine
from ai_engine.utils import token_len
from ai_engine.chains import extraction, angles
from ai_engine.formatter import package
from ai_engine.schemas import AnalysisPackage
from ai_engine.scoring import compute_score
from ai_engine.chains import keywords
from ai_engine.chains import viz
from ai_engine.memory import get_memory

MAX_TOKENS = 8_000


def _validate(text: str) -> None:
    if token_len(text, model=ai_engine.OPENAI_MODEL) > MAX_TOKENS:
        raise ValueError("Article trop long")


def _score(extr) -> int:
    """Très simple : +10 points par personne ou org, max 100."""
    raw = (len(extr.persons) + len(extr.organizations)) * 10
    return min(raw, 100)


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
    viz_result = viz.run(angle_result)

    packaged, markdown = package(extraction_result, angle_result)

    memory = get_memory(user_id)
    
    output_text = f"[score={score_10}] Angles: {[a.title for a in angle_result.angles]}"

    memory.save_context(
        {"article": article_text},
        {"summary": output_text}
)

    return packaged, markdown, score_10, keywords_result

