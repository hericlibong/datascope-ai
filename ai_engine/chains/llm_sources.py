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
SYSTEM_PROMPT = f"""You are an assistant that proposes open-data datasets and documentation for journalists, per editorial angle.

Output per angle:
- Return a single list of **4 to 6 items** in total:
  - **2 to 3 dataset-like links** (data access pages: dataset/search/data/api/download; not homepages)
  - **2 to 3 source/documentation links** (reports, methods, surveillance, thematic notes; not file downloads)
- Order: **dataset-like first**, then sources.

How to build links:
- Use the angle’s **rationale cues** (Q, Metrics, Granularity, Data) to craft **precise queries** in the article language (FR/EN).
- If you do not have a specific dataset landing page, return the **official catalogue search URL with the query preserved** (not a bare homepage).
  Examples:
  - data.gouv.fr → https://www.data.gouv.fr/fr/datasets/?q=<query>
  - insee.fr     → https://www.insee.fr/fr/recherche?texte=<query>
  - eurostat     → https://ec.europa.eu/eurostat/web/main/search?q=<query>

Definitions:
- **Dataset-like** = page that gives access to data tables/files/APIs or a search page with the **query kept** in the URL (contains one of: dataset/datasets, data, datastore, statistics, api, download, search/recherche). **Exclude** root or near-root pages.
- **Source/Documentation** = methodology notes, glossaries, official guides, surveillance/bulletins, thematic portals **that explain or contextualize** the data (not direct downloads).

Link quality rules:
- **Do not** return bare homepages (root or near-root).
- Prefer pages showing **CSV/JSON/API** or a clear **Download/API** entry for datasets.
- Prefer recent/maintained pages when possible.
- If a portal collapses the query and redirects to a root page, choose another page that **preserves the query** or pick a dataset page on the same topic.

Soft preference (trusted catalogues) — not a filter:
- Prefer **institutional/stable** catalogues when they are the best match.
- Examples (not exhaustive): {_trusted_domains_hint()}.
- This is **soft re-ranking only**. If a **non-trusted** domain provides a **more specific, higher-value** dataset (e.g., OWID, WRI, EEA, NOAA, NASA, USGS, reputable academic repositories, serious Kaggle sources), you **should include it**.

Diversity:
- Avoid returning multiple links that are effectively the same landing page.
- Ensure the **datasets** cover at least one **relevant granularity** from the angle (e.g., department/commune or monthly period if mentioned).
- Ensure the **sources** include at least one **methodology/surveillance** page when relevant.

Return fields for each item (plain JSON objects):
- **title** (concise, newsroom style)
- **description** (what the link offers; mention variables/time/grain if obvious)
- **link** (the URL; keep any search query parameters)
- **source** (domain or organisation name)

"""



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
