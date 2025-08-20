from decouple import config
from pathlib import Path
# from langchain.cache import SQLiteCache
from langchain_community.cache import SQLiteCache
from langchain.globals import set_llm_cache


OPENAI_API_KEY = config("OPENAI_API_KEY")
OPENAI_MODEL = config("OPENAI_MODEL", default="gpt-4o-mini")

# LLM Assistant configuration
ASSISTANT_MODEL = config("ASSISTANT_MODEL", default=OPENAI_MODEL)
ASSISTANT_TEMPERATURE = config("ASSISTANT_TEMPERATURE", default=0.3, cast=float)
ASSISTANT_MAX_TOKENS = config("ASSISTANT_MAX_TOKENS", default=2000, cast=int)

# Available models for the assistant
AVAILABLE_MODELS = {
    "gpt-4o-mini": {"provider": "openai", "cost": "low", "speed": "fast"},
    "gpt-4o": {"provider": "openai", "cost": "high", "speed": "medium"},
    "gpt-3.5-turbo": {"provider": "openai", "cost": "low", "speed": "fast"},
}

def get_model_config(model_name: str = None) -> dict:
    """Get configuration for the specified model or the default assistant model."""
    model = model_name or ASSISTANT_MODEL
    return AVAILABLE_MODELS.get(model, AVAILABLE_MODELS["gpt-4o-mini"])

CACHE_DIR = Path(".cache")
CACHE_DIR.mkdir(exist_ok=True)
# set_llm_cache(SQLiteCache(database_path=CACHE_DIR / "langchain.db"))
set_llm_cache(SQLiteCache(database_path=".cache/langchain.db"))

