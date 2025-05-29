from collections import defaultdict
from langchain.memory import ConversationBufferMemory

# Dictionnaire {user_id: ConversationBufferMemory()}
_MEMORY_POOL = defaultdict(lambda: ConversationBufferMemory(
    memory_key="history",
    input_key="article",          # ou "question" selon la chaîne
    return_messages=True,
))

def get_memory(user_id: str | int = "anonymous") -> ConversationBufferMemory:
    """
    Retourne (ou crée) une mémoire tampon pour l'utilisateur donné.
    For MVP, on garde tout en RAM.
    """
    return _MEMORY_POOL[user_id]
