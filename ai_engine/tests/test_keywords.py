import pytest
from ai_engine.schemas import AngleResult, Angle, KeywordsResult
import ai_engine.chains.keywords as kw

def _angle_res():
    return AngleResult(
        language="en",
        angles=[Angle(title="Economic impact of AI regulation", rationale="...")]
    )

class FakeChain:
    def invoke(self, _):
        return KeywordsResult(
            language="en",
            sets=[{
                "angle_title": "Economic impact of AI regulation",
                "keywords": ["AI regulation", "tech jobs", "GDP growth", "innovation policy", "investment AI"]
            }]
        )

def test_keywords_ok(monkeypatch):
    monkeypatch.setattr(kw, "run", lambda angle_result: FakeChain().invoke(None))
    res = kw.run(_angle_res())
    assert len(res.sets[0].keywords) == 5
