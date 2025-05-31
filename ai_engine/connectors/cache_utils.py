# ai_engine/connectors/cache_utils.py

import os
from diskcache import Cache
import pickle
from collections.abc import Generator

CACHE_DIR = os.path.join(os.path.dirname(__file__), '..', '..', '.cache')
os.makedirs(CACHE_DIR, exist_ok=True)
cache = Cache(CACHE_DIR)

def cache_response(ttl_seconds=3600):
    """
    Cache decorator with TTL.
    - Converts generator results into a list for caching.
    - Automatically returns an iterable (via iter()) if a cached list is found.
    - Skips cache if the object is not pickle-serializable.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            key = (func.__name__, args, tuple(sorted(kwargs.items())))
            if key in cache:
                result = cache[key]
                # ✅ Si c’était un générateur, on renvoie un itérable à nouveau
                return iter(result) if isinstance(result, list) else result
            result = func(*args, **kwargs)
            try:
                if isinstance(result, Generator):
                    result = list(result)
                    cache.set(key, result, expire=ttl_seconds)
                    return iter(result)  # ✅ reconverti en itérable !
                else:
                    pickle.dumps(result)
                    cache.set(key, result, expire=ttl_seconds)
            except Exception:
                pass
            return result
        return wrapper
    return decorator
