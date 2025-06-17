# ai_engine/chains/llm_sources.py
from pathlib import Path
from functools import lru_cache
import ai_engine

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser

from ai_engine.schemas import (
    AngleResult,
    LLMSourceSuggestion,
    LLMSourceSuggestionList,   # conteneur Pydantic (déjà existant)
)
from ai_engine.retries import llm_retry

# --------------------------------------------------------------------------- #
# Constantes
# --------------------------------------------------------------------------- #
BASE_DIR   = Path(__file__).resolve().parent.parent
PROMPT_PATH = BASE_DIR / "prompts" / "generate_llm_datasources.j2"


@lru_cache
def _tmpl() -> str:
    """Charge le prompt Jinja2 en cache (lecture disque une seule fois)."""
    return PROMPT_PATH.read_text(encoding="utf-8")

# --------------------------------------------------------------------------- #
# Fonction principale : une liste PAR angle
# --------------------------------------------------------------------------- #
@llm_retry
def run(angle_result: AngleResult) -> list[list[LLMSourceSuggestion]]:
    """
    Pour chaque angle éditorial, interroge le LLM et renvoie
    une liste de suggestions (LLMSourceSuggestion) **marquées angle_idx**.

    Retour :
        [
            [LLMSourceSuggestion, ...],   # angle_idx = 0
            [LLMSourceSuggestion, ...],   # angle_idx = 1
            ...
        ]
    """
    parser  = PydanticOutputParser(pydantic_object=LLMSourceSuggestionList)
    prompt_tmpl = PromptTemplate.from_template(
        _tmpl(),
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    chat = ChatOpenAI(
        model=ai_engine.OPENAI_MODEL,
        temperature=0.4,
        timeout=40,
        openai_api_key=ai_engine.OPENAI_API_KEY,
    )

    chain = prompt_tmpl | chat | parser
    sources_per_angle: list[list[LLMSourceSuggestion]] = []

    for idx, angle in enumerate(angle_result.angles):
        parsed = chain.invoke(
            {
                "angle_title": angle.title,
                "angle_desc": angle.rationale,
            }
        )

        # ------------- normalisation en liste -------------------------
        if hasattr(parsed, "datasets"):         # schéma actuel
            suggestions = parsed.datasets
        elif hasattr(parsed, "__root__"):       # ancien schéma éventuel
            suggestions = parsed.__root__
        elif isinstance(parsed, list):
            suggestions = parsed
        else:
            suggestions = [parsed]              # fallback improbable

        # ------------- marquer l’angle parent ------------------------
        for s in suggestions:
            s.angle_idx = idx

        sources_per_angle.append(suggestions)

    return sources_per_angle
