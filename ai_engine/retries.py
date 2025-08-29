"""
Décorateur de résilience pour tous les appels LLM.
- 3 tentatives par défaut (configurable via env).
- Back-off exponentiel : 1 s → 2 s → 4 s (max 10 s).
- Journalise chaque échec avant de réessayer.
"""

import logging
import os
from functools import wraps

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    RetryError,
)

logger = logging.getLogger("ai_engine.retry")

MAX_ATTEMPTS = int(os.getenv("LLM_MAX_RETRIES", 1))


def llm_retry(func):
    @retry(
        stop=stop_after_attempt(MAX_ATTEMPTS),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
        before_sleep=lambda retry_state: logger.warning(
            f"[LLM retry] {func.__name__} failed "
            f"(attempt {retry_state.attempt_number}/{MAX_ATTEMPTS}): "
            f"{retry_state.outcome.exception()}"
        ),
    )
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper




