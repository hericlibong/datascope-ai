# ai_engine/chains/viz.py
from pathlib import Path
from functools import lru_cache
import ai_engine

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser

from ai_engine.schemas import AngleResult, VizResult, VizSuggestion
from ai_engine.retries import llm_retry

BASE_DIR   = Path(__file__).resolve().parent.parent
PROMPT_PATH = BASE_DIR / "prompts" / "generate_viz.j2"


@lru_cache
def _tmpl() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


@llm_retry
def run(angle_result: AngleResult) -> list[list[VizSuggestion]]:
    """
    Retourne une liste de listes : une entrée par angle,
    contenant les VizSuggestion correspondantes.
    """
    parser = PydanticOutputParser(pydantic_object=VizResult)

    prompt = PromptTemplate.from_template(
        _tmpl(),
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    chat = ChatOpenAI(
        model=ai_engine.OPENAI_MODEL,
        temperature=0.5,
        timeout=40,
        openai_api_key=ai_engine.OPENAI_API_KEY,
    )

    chain = prompt | chat | parser

    viz_per_angle: list[list[VizSuggestion]] = []

    for angle in angle_result.angles:
        parsed: VizResult = chain.invoke(
            {
                "angle_title": angle.title,
                "angle_desc": angle.rationale or "",
            }
        )
        viz_per_angle.append(parsed.suggestions)

    return viz_per_angle
