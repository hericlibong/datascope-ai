# tests/test_llm_sources_collect_two_pass.py
import types
from ai_engine.chains import llm_sources_collect as mod

class DummyAngle:
    def __init__(self, title, rationale):
        self.title, self.rationale = title, rationale

class DummyAngleResult:
    def __init__(self):
        self.angles = [DummyAngle("A1", "R"), DummyAngle("A2", "R")]

class Q:
    def __init__(self, text, intent):
        self.text, self.intent = text, intent
    def model_dump(self):
        return {"text": self.text, "intent": self.intent}

# monkeypatch run_llm_queries -> 2 intents par angle
mod.run_llm_queries = lambda ar: [
    [Q("q1d", "dataset"), Q("q1s", "source")],
    [Q("q2d", "dataset"), Q("q2s", "source")],
]

# monkeypatch search_many -> marque l'intent dans l'URL
def fake_search_many(qs, k=10):
    out = []
    for q in qs:
        out.append({"url": f"https://ex/{q['intent']}/{q['text']}", "title": q['text'], "snippet": q['text'], "source_domain": "ex", "intent": q['intent']})
    return out
mod.search_many = fake_search_many

res = mod.run(DummyAngleResult())
flat = [x.link for x in res[0]]
assert flat[0].startswith("https://ex/dataset/")  # dataset d'abord