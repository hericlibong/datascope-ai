from collections import defaultdict
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import ChatMessageHistory

import warnings
from langchain_core._api.deprecation import LangChainDeprecationWarning

warnings.filterwarnings(
    "ignore",
    category=LangChainDeprecationWarning,
    message="Please see the migration guide at: https://python.langchain.com/docs/versions/migrating_memory/"
)

# Dictionnaire {user_id: ConversationBufferMemory()}
_MEMORY_POOL = defaultdict(lambda: ConversationBufferMemory(
    memory_key="history",
    input_key="article",          # ou "question" selon la chaîne
    output_key="summary",
    return_messages=True,
    chat_memory=ChatMessageHistory()
))

def get_memory(user_id: str | int = "anonymous") -> ConversationBufferMemory:
    """
    Retourne (ou crée) une mémoire tampon pour l'utilisateur donné.
    For MVP, on garde tout en RAM.
    """
    return _MEMORY_POOL[user_id]
