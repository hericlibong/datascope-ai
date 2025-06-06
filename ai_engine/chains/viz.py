from pathlib import Path, PurePath
from functools import lru_cache
import ai_engine

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from ai_engine.schemas import AngleResult, VizResult
from ai_engine.retries import llm_retry

BASE_DIR = Path(__file__).resolve().parent.parent
PROMPT_PATH = BASE_DIR / "prompts" / "generate_viz.j2"

@lru_cache
def _tmpl() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")

@llm_retry
def run(angle_result: AngleResult) -> VizResult:
    parser = PydanticOutputParser(pydantic_object=VizResult)

    angles_block = "\n".join(f"{i}. {a.title}" for i, a in enumerate(angle_result.angles, 1))

    # prompt = PromptTemplate.from_template(
    #     _tmpl(),
    #     input_variables=["angles_block"],
    #     partial_variables={"format_instructions": parser.get_format_instructions()},
    # )
    prompt = PromptTemplate.from_template(
    _tmpl(),
    partial_variables={
        "format_instructions": parser.get_format_instructions(),
    }
)


    chat = ChatOpenAI(
        model=ai_engine.OPENAI_MODEL,
        temperature=0.5,
        timeout=40,
        openai_api_key=ai_engine.OPENAI_API_KEY,
    )

    chain = prompt | chat | parser
    return chain.invoke({"angles_block": angles_block})
