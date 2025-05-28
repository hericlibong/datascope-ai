from pathlib import Path
from functools import lru_cache
import ai_engine

from langchain_openai import ChatOpenAI      # <-- plus de warning
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.schema.runnable import Runnable
from ai_engine.schemas import ExtractionResult


BASE_DIR = Path(__file__).resolve().parent.parent
PROMPT_PATH = BASE_DIR / "prompts" / "extract_entities.j2"


@lru_cache   # lit le fichier une seule fois par process
def _load_template() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def _build_chain(model_name: str = "gpt-4o-mini") -> Runnable:
    parser = PydanticOutputParser(pydantic_object=ExtractionResult)

    prompt = PromptTemplate.from_template(          # 🟢 on NE PASSE QUE le template
        _load_template(),
        partial_variables={                         # format_instructions injecté ici
            "format_instructions": parser.get_format_instructions(),
        },
    )

    chat = ChatOpenAI(model=ai_engine.OPENAI_MODEL, temperature=0, openai_api_key=ai_engine.OPENAI_API_KEY)
    return prompt | chat | parser


def run(article: str, *, model_name: str = "gpt-4o-mini") -> ExtractionResult:
    """Exécute la chaîne et renvoie l’objet ExtractionResult."""
    chain = _build_chain(model_name)   # récup. depuis cache si déjà construit
    return chain.invoke({"article": article})
