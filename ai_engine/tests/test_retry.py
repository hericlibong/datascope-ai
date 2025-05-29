import pytest
from ai_engine.retries import llm_retry

counter = {"calls": 0}

@llm_retry
def flaky():
    counter["calls"] += 1
    raise RuntimeError("boom")

def test_retry_runs_three_times(monkeypatch):
    # MAX_ATTEMPTS=3 ⇒ 3 appels puis exception
    with pytest.raises(RuntimeError):
        flaky()
    assert counter["calls"] == 3
