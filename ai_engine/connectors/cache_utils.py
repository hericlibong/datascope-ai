# ai_engine/connectors/cache_utils.py

import os
from diskcache import Cache
import pickle
from collections.abc import Generator

CACHE_DIR = os.path.join(os.path.dirname(__file__), '..', '..', '.cache')
os.makedirs(CACHE_DIR, exist_ok=True)
cache = Cache(CACHE_DIR)

# ai_engine/connectors/cache_utils.py
def cache_response(ttl_seconds: int = 3600):
    """
    Décorateur compatible avec les fonctions qui renvoient un itérable.
    On matérialise la liste pour la stocker, puis on renvoie
    à chaque appel un nouvel itérateur sur cette liste.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            key = (func.__name__, args, tuple(sorted(kwargs.items())))
            if key in cache:
                data = cache[key]          # déjà une liste
            else:
                data = list(func(*args, **kwargs))
                cache.set(key, data, expire=ttl_seconds)
            return iter(data)              # toujours un itérateur frais
        return wrapper
    return decorator

