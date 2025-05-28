"""
Utilitaires généraux pour l’app ai_engine.
"""

from typing import Optional

try:
    from tiktoken import encoding_for_model, get_encoding
except ImportError:  # sécurité si tiktoken n’est pas installé / importé ailleurs
    encoding_for_model = None
    get_encoding = None


def token_len(text: str, model: Optional[str] = None) -> int:
    """
    Retourne le nombre de tokens d’un texte selon l’encodage OpenAI.
    - Si tiktoken est dispo et qu’un modèle est fourni ➜ encodage exact.
    - Sinon ➜ heuristique simple : nb de mots (≈ bonne approximation pour 8 000-token gate).
    """
    if encoding_for_model and model:
        try:
            enc = encoding_for_model(model)
        except KeyError:
            enc = get_encoding("cl100k_base")
        return len(enc.encode(text))
    # fallback : 1 token ≈ 1 mot
    return len(text.split())
