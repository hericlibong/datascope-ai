from pathlib import Path
from functools import lru_cache
import ai_engine

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.schema.runnable import Runnable
from ai_engine.schemas import AngleResult
from ai_engine.retries import llm_retry



BASE_DIR = Path(__file__).resolve().parent.parent
PROMPT_PATH = BASE_DIR / "prompts" / "generate_angles.j2"


@lru_cache
def _load_template() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def _build_chain() -> Runnable:
    parser = PydanticOutputParser(pydantic_object=AngleResult)

    prompt = PromptTemplate.from_template(
        _load_template(),
        partial_variables={
            "format_instructions": parser.get_format_instructions(),
        },
    )

    chat = ChatOpenAI(
        model=ai_engine.OPENAI_MODEL,
       # temperature=0.7,
        timeout=40,                  # un peu de créativité
        openai_api_key=ai_engine.OPENAI_API_KEY,
    )

    return prompt | chat | parser

@llm_retry
def run(article: str) -> AngleResult:
    return _build_chain().invoke({"article": article})
