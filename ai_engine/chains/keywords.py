from pathlib import Path
from functools import lru_cache
import ai_engine

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from ai_engine.schemas import AngleResult, KeywordsResult
from ai_engine.retries import llm_retry

BASE_DIR = Path(__file__).resolve().parent.parent
PROMPT_PATH = BASE_DIR / "prompts" / "generate_keywords.j2"

@lru_cache
def _tmpl() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")

# --------------------------------------------------------------------------- #
# ⬇️  Fonction corrigée : renvoie 1 KeywordsResult PAR angle
# --------------------------------------------------------------------------- #
@llm_retry
def run(angle_result: AngleResult) -> list[KeywordsResult]:
    """
    Génère des mots-clés séparément pour chaque angle éditorial et
    renvoie une liste de `KeywordsResult` alignée sur `angle_result.angles`.
    """
    parser = PydanticOutputParser(pydantic_object=KeywordsResult)
    template_str = _tmpl()

    chat = ChatOpenAI(
        model=ai_engine.OPENAI_MODEL,
        temperature=0.3,          # plus stable
        timeout=40,
        openai_api_key=ai_engine.OPENAI_API_KEY,
    )

    out: list[KeywordsResult] = []

    for idx, angle in enumerate(angle_result.angles, 1):
        # Un seul angle → bloc d’une ligne
        angles_block = f"{idx}. {angle.title}"

        prompt = PromptTemplate.from_template(
            template_str,
            partial_variables={
                "format_instructions": parser.get_format_instructions(),
            },
        )

        chain = prompt | chat | parser
        result: KeywordsResult = chain.invoke({"angles_block": angles_block})

        out.append(result)

    return out
