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

@llm_retry
def run(angle_result: AngleResult) -> KeywordsResult:
    parser = PydanticOutputParser(pydantic_object=KeywordsResult)

    angles_block = "\n".join(
        f"{idx}. {a.title}"
        for idx, a in enumerate(angle_result.angles, 1)
    )

    # prompt = PromptTemplate.from_template(
    #     _tmpl(),
    #     partial_variables={
    #         "format_instructions": parser.get_format_instructions(),
    #     },
    #     input_variables=["angles_block"],
    # )
    prompt = PromptTemplate.from_template(
    _tmpl(),
    partial_variables={
        "format_instructions": parser.get_format_instructions(),
    }
)

    chat = ChatOpenAI(
        model=ai_engine.OPENAI_MODEL,
        temperature=0.3,
        timeout=40,
        openai_api_key=ai_engine.OPENAI_API_KEY,
    )

    chain = prompt | chat | parser
    return chain.invoke({"angles_block": angles_block})
