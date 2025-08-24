# ai_engine/assistant/verified_sources.py
"""
LLM Assistant for suggesting verified sources beyond just datasets.
This includes articles, reports, studies, official documentation, etc.
"""
from pathlib import Path
from functools import lru_cache
import ai_engine

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser

from ai_engine.schemas import AngleResult, VerifiedSource, VerifiedSourceList
from ai_engine.retries import llm_retry

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #
BASE_DIR = Path(__file__).resolve().parent.parent
PROMPT_PATH = BASE_DIR / "prompts" / "generate_verified_sources.j2"


@lru_cache
def _tmpl() -> str:
    """Load the Jinja2 prompt template (cached, read from disk only once)."""
    return PROMPT_PATH.read_text(encoding="utf-8")


# --------------------------------------------------------------------------- #
# Main function: verified sources per angle
# --------------------------------------------------------------------------- #
@llm_retry
def run(angle_result: AngleResult, model_name: str = None) -> list[list[VerifiedSource]]:
    """
    For each editorial angle, query the LLM and return a list of verified sources
    (articles, reports, studies, documentation) marked with angle_idx.

    Args:
        angle_result: The result containing editorial angles
        model_name: Optional model name override for this request

    Returns:
        [
            [VerifiedSource, ...],   # angle_idx = 0
            [VerifiedSource, ...],   # angle_idx = 1
            ...
        ]
    """
    # Use specified model or default assistant model
    model = model_name or ai_engine.ASSISTANT_MODEL
    model_config = ai_engine.get_model_config(model)
    
    parser = PydanticOutputParser(pydantic_object=VerifiedSourceList)
    prompt_tmpl = PromptTemplate.from_template(
        _tmpl(),
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    chat = ChatOpenAI(
        model=model,
        temperature=ai_engine.ASSISTANT_TEMPERATURE,
        max_tokens=ai_engine.ASSISTANT_MAX_TOKENS,
        timeout=40,
        openai_api_key=ai_engine.OPENAI_API_KEY,
    )

    chain = prompt_tmpl | chat | parser
    sources_per_angle: list[list[VerifiedSource]] = []

    for idx, angle in enumerate(angle_result.angles):
        try:
            parsed = chain.invoke(
                {
                    "angle_title": angle.title,
                    "angle_desc": angle.rationale,
                    "language": angle_result.language,
                }
            )

            # Normalize response to list
            if hasattr(parsed, "sources"):
                suggestions = parsed.sources
            elif hasattr(parsed, "__root__"):
                suggestions = parsed.__root__
            elif isinstance(parsed, list):
                suggestions = parsed
            else:
                suggestions = [parsed]

            # Mark with parent angle index
            for source in suggestions:
                source.angle_idx = idx

            sources_per_angle.append(suggestions)

        except Exception as e:
            print(f"Error generating verified sources for angle {idx}: {e}")
            # Return empty list for this angle in case of error
            sources_per_angle.append([])

    return sources_per_angle


def get_assistant_info() -> dict:
    """Return information about the current LLM assistant configuration."""
    return {
        "model": ai_engine.ASSISTANT_MODEL,
        "temperature": ai_engine.ASSISTANT_TEMPERATURE,
        "max_tokens": ai_engine.ASSISTANT_MAX_TOKENS,
        "model_config": ai_engine.get_model_config(),
        "available_models": ai_engine.AVAILABLE_MODELS,
    }