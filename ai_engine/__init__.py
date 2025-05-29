from decouple import config
from pathlib import Path
# from langchain.cache import SQLiteCache
from langchain_community.cache import SQLiteCache
from langchain.globals import set_llm_cache


OPENAI_API_KEY = config("OPENAI_API_KEY")
OPENAI_MODEL = config("OPENAI_MODEL", default="gpt-4o-mini")
CACHE_DIR = Path(".cache")
CACHE_DIR.mkdir(exist_ok=True)
# set_llm_cache(SQLiteCache(database_path=CACHE_DIR / "langchain.db"))
set_llm_cache(SQLiteCache(database_path=".cache/langchain.db"))

