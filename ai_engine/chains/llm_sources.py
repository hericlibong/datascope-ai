# Import du module Path depuis pathlib pour gérer les chemins de fichiers
from pathlib import Path
# Import du décorateur lru_cache depuis functools pour mettre en cache les résultats de fonctions
from functools import lru_cache
# Import du module ai_engine personnalisé
import ai_engine
# Import du modèle de chat OpenAI depuis le package langchain_openai
from langchain_openai import ChatOpenAI
# Import de la classe PromptTemplate depuis le package langchain.prompts pour créer des templates de prompts
from langchain.prompts import PromptTemplate
# Import du parser de sortie Pydantic depuis langchain.output_parsers pour parser les réponses
from langchain.output_parsers import PydanticOutputParser

from ai_engine.schemas import AngleResult, LLMSourceSuggestion, LLMSourceSuggestionList
from ai_engine.retries import llm_retry

BASE_DIR = Path(__file__).resolve().parent.parent
PROMPT_PATH = BASE_DIR / "prompts" / "generate_llm_datasources.j2"


@lru_cache
def _tmpl() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")

# ------------------------------------------------------------------
@llm_retry
def run(angle_result: AngleResult) -> list[LLMSourceSuggestion]:
    """
    Retourne une liste de LLMSourceSuggestion (et jamais de tuples/dicts).
    """
    parser = PydanticOutputParser(pydantic_object=LLMSourceSuggestionList)

    prompt = PromptTemplate.from_template(
        _tmpl(),
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    chat = ChatOpenAI(
        model=ai_engine.OPENAI_MODEL,
        temperature=0.7,
        timeout=40,
        openai_api_key=ai_engine.OPENAI_API_KEY,
    )

    chain = prompt | chat | parser
    suggestions: list[LLMSourceSuggestion] = []

    for angle in angle_result.angles:
        parsed = chain.invoke({
            "angle_title": angle.title,
            "angle_desc": angle.rationale,
        })

        # --- récupère la liste quel que soit le conteneur -------------
        if hasattr(parsed, "__root__"):          # ancien schéma
            suggestions.extend(parsed.__root__)
        elif hasattr(parsed, "datasets"):        # schéma actuel
            suggestions.extend(parsed.datasets)
        elif isinstance(parsed, list):           # LLM renvoie déjà une liste
            suggestions.extend(parsed)
        else:                                    # cas improbable : un seul objet
            suggestions.append(parsed)


    return suggestions
