# ai_engine/chains/llm_queries.py
from __future__ import annotations

from pathlib import Path
from functools import lru_cache
from typing import List, Literal

import ai_engine
from django.conf import settings
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from ai_engine.schemas import AngleResult
from ai_engine.retries import llm_retry


BASE_DIR = Path(__file__).resolve().parent.parent
PROMPT_PATH = BASE_DIR / "prompts" / "generate_llm_queries.j2"


class QuerySpec(BaseModel):
    text: str = Field(..., description="Search query text (FR/EN). No domain restrictions.")
    intent: Literal["dataset", "source"] = Field(..., description="Target type for ranking.")
    lang: Literal["fr", "en", "auto"] = Field("auto", description="Language hint.")
    time_hint: str | None = Field(None, description='Optional time range, e.g. "2010..2024".')
    must_terms: List[str] | None = Field(None, description="Terms that must be present.")
    should_terms: List[str] | None = Field(None, description="Optional enrichment terms.")


class QuerySpecList(BaseModel):
    queries: List[QuerySpec] = Field(..., min_items=3, max_items=6)


@lru_cache
def _tmpl() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


SYSTEM_PROMPT = (
    "You craft focused web search queries for one editorial angle. "
    "Queries must be specific, data-oriented, and cover both intents: dataset & source."
)


@llm_retry
def run(angle_result: AngleResult) -> list[list[QuerySpec]]:
    """
    For each editorial angle, return 3..6 QuerySpec items produced by the LLM.
    Output shape: [[QuerySpec, ...],  # angle 0
                   [QuerySpec, ...],  # angle 1
                   ...]
    """
    parser = PydanticOutputParser(pydantic_object=QuerySpecList)

    human_template = _tmpl()
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("human", human_template),
        ]
    ).partial(format_instructions=parser.get_format_instructions())

    # IMPORTANT: omit temperature to support models that only allow default (e.g., gpt-5-mini)
    chat = ChatOpenAI(
        model=ai_engine.OPENAI_MODEL,
        timeout=int(getattr(settings, "SEARCH_TIMEOUT", 35) or 35),
        openai_api_key=ai_engine.OPENAI_API_KEY,
    )

    chain = prompt | chat | parser

    all_queries: list[list[QuerySpec]] = []
    for angle in angle_result.angles:
        parsed = chain.invoke(
            {
                "angle_title": angle.title,
                "angle_desc": angle.rationale,
            }
        )
        if hasattr(parsed, "queries") and isinstance(parsed.queries, list):
            all_queries.append(parsed.queries)
        else:
            # Fallback: wrap into list if parser returns a single QuerySpec
            all_queries.append([parsed] if isinstance(parsed, QuerySpec) else [])
    return all_queries
