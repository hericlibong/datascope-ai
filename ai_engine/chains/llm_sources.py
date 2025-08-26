# ai_engine/chains/llm_sources.py
from pathlib import Path
from functools import lru_cache
import ai_engine

from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser

from ai_engine.schemas import (
    AngleResult,
    LLMSourceSuggestion,
    LLMSourceSuggestionList,   # conteneur Pydantic (déjà existant)
)
from ai_engine.retries import llm_retry

# NEW: message system + trusted list depuis settings
from django.conf import settings  # NEW
from langchain_core.prompts import ChatPromptTemplate  # NEW

# --------------------------------------------------------------------------- #
# Constantes
# --------------------------------------------------------------------------- #
BASE_DIR   = Path(__file__).resolve().parent.parent
PROMPT_PATH = BASE_DIR / "prompts" / "generate_llm_datasources.j2"


@lru_cache
def _tmpl() -> str:
    """Charge le prompt Jinja2 en cache (lecture disque une seule fois)."""
    return PROMPT_PATH.read_text(encoding="utf-8")


# NEW: petit helper pour un hint compact (évite de gonfler le prompt)
def _trusted_domains_hint(max_items: int = 10) -> str:  # NEW
    """
    Build a short, human-readable hint of trusted domains for the prompt.
    We cap to avoid token bloat; the full list stays in settings.TRUSTED_DOMAINS.
    """
    items = [str(d).strip() for d in getattr(settings, "TRUSTED_DOMAINS", []) if str(d).strip()]
    if not items:
        # fallback raisonnable si la liste est vide (rare)
        return "data.gouv.fr, insee.fr, ec.europa.eu (Eurostat), who.int, oecd.org, data.gov, cdc.gov, ons.gov.uk"
    shown = ", ".join(items[:max_items])
    return shown + ("…" if len(items) > max_items else "")


# NEW: SYSTEM PROMPT explicite (nudge qualitatif, bilingue)
SYSTEM_PROMPT = f"""You are an assistant that proposes authoritative open-data sources and documentation for journalists.

Soft preference (trusted institutional catalogues):
- Prefer links from trusted, institutional and stable catalogues whenever possible.
- Examples (not exhaustive): {_trusted_domains_hint()}.
- This is a soft preference (re-ranking), NOT a hard filter. Non-trusted domains may still appear if they are the best match.

Bilingual context:
- The platform is FR/EN. Adapt choices to the article language/context.
- For French content, prefer institutions authoritative in French contexts when available.
- For English content, prefer institutions authoritative in English/INTL contexts when available.

Link quality rules:
- Do not fabricate deep URLs. Prefer official dataset landing pages or canonical catalogue entries.
- If a dataset is only available via a portal page, return that portal page (not a random blog/mirror).
- When multiple candidates exist, pick the most official/maintained source.

Return the usual fields for each suggestion.
"""  # NEW


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
    parser = PydanticOutputParser(pydantic_object=LLMSourceSuggestionList)

    # NEW: on garde le .j2 comme "human", et on ajoute un vrai message "system"
    human_template = _tmpl()  # le template Jinja existant

    prompt = ChatPromptTemplate.from_messages([  # NEW
        ("system", SYSTEM_PROMPT),              # ← nudge qualitatif, bilingue
        ("human", human_template),              # ← ton template .j2 inchangé
    ]).partial(
        # variable utilisée dans le .j2 pour le parsing structuré
        format_instructions=parser.get_format_instructions()
    )

    chat = ChatOpenAI(
        model=ai_engine.OPENAI_MODEL,
        temperature=0.4,
        timeout=40,
        openai_api_key=ai_engine.OPENAI_API_KEY,
    )

    chain = prompt | chat | parser
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
