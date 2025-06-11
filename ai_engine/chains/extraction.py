from functools import lru_cache
from pathlib import Path
import ai_engine

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.schema.runnable import Runnable
from ai_engine.schemas import ExtractionResult
from ai_engine.retries import llm_retry


BASE_DIR = Path(__file__).resolve().parent.parent
PROMPT_PATH = BASE_DIR / "prompts" / "extract_entities.j2"


@lru_cache
def _load_template() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def _build_chain(model_name: str = ai_engine.OPENAI_MODEL) -> Runnable:
    parser = PydanticOutputParser(pydantic_object=ExtractionResult)

    prompt = PromptTemplate.from_template(
        _load_template(),
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    chat = ChatOpenAI(
        model=ai_engine.OPENAI_MODEL,
        temperature=0,
        timeout=40,
        openai_api_key=ai_engine.OPENAI_API_KEY,
    )

    return prompt | chat | parser


@llm_retry
def run(article: str, *, model_name: str = ai_engine.OPENAI_MODEL) -> ExtractionResult:
    chain = _build_chain(model_name)
    return chain.invoke({"article": article})
