from ai_engine.schemas import ExtractionResult, NumberEntity
from ai_engine.scoring import compute_score

def _extr(p=0, o=0, l=0, d=0, n=0):
    return ExtractionResult(
        language="fr",
        persons=["P"] * p,
        organizations=["O"] * o,
        locations=["L"] * l,
        dates=["2025-01-01"] * d,
        numbers=[NumberEntity(raw="42", value=42, unit="")] * n
    )

def test_score_low():
    extr = _extr()
    article = "Ceci est un texte sans information factuelle ni entité nommée."
    assert compute_score(extr, article) == 0

def test_score_medium():
    extr = _extr(p=2, d=1)
    article = "Le Sénat et l'Assemblée Nationale ont adopté une loi sur l'IA le 12 mai 2025. Le Conseil Constitutionnel a ensuite ratifié cette loi. Le président du Conseil, Laurent Fabius l'a confirmé aux médias le 13 mai 2025"
    assert 20 <= compute_score(extr, article) <= 60

def test_score_high():
    extr = _extr(p=4, o=3, l=2, d=2, n=5)
    article = "Emmanuel Macron et Ursula von der Leyen se sont réunis à Paris avec les représentants de l’ONU, de l’OMS et d’Interpol le 10 avril 2025. Un budget de 2,5 milliards a été annoncé."
    assert compute_score(extr, article) >= 70

