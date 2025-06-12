from ai_engine.schemas import ExtractionResult
from ai_engine.utils import token_len

# DENSITY_SCALE = 500 

# def compute_score(extr: ExtractionResult, article_text: str, *, model: str | None = None) -> int:
#     """Score 0-100 basé sur densité et diversité, normalisé par la longueur réelle de l’article."""
#     nb_tokens = token_len(article_text, model=model)
#     nb_entities = sum(map(len, [
#         extr.persons, extr.organizations, extr.locations, extr.dates, extr.numbers
#     ]))

#     densite = (nb_entities / max(nb_tokens, 1)) * DENSITY_SCALE
#     densite = min(densite, 100)

#     diversite = len([lst for lst in
#                      [extr.persons, extr.organizations, extr.locations,
#                       extr.dates, extr.numbers] if lst]) / 5 * 100

#     return round(0.7 * densite + 0.3 * diversite)

# ai_engine/scoring.py

from ai_engine.schemas import ExtractionResult
from ai_engine.utils import token_len

def compute_score(extr: ExtractionResult, article_text: str, *, model: str | None = None) -> int:
    """
    Nouveau score sur 10 basé sur des critères éditoriaux explicites.
    - Pondère la présence de chiffres, dates, entités nommées, densité.
    - Vise à refléter le potentiel de datafication d’un article.
    """
    score = 0
    justifications = []

    word_count = len(article_text.split())
    nb_persons = len(extr.persons)
    nb_orgs = len(extr.organizations)
    nb_locations = len(extr.locations)
    nb_dates = len(extr.dates)
    nb_numbers = len(extr.numbers)

    total_structured = nb_persons + nb_orgs + nb_locations + nb_dates + nb_numbers

    if nb_numbers >= 2:
        score += 3
        justifications.append("Plusieurs données chiffrées détectées")

    if nb_dates >= 1:
        score += 2
        justifications.append("Date(s) clairement identifiée(s)")

    if (nb_persons + nb_orgs + nb_locations) >= 2:
        score += 2
        justifications.append("Entités nommées multiples (personnes, organisations, lieux)")

    density = total_structured / word_count if word_count else 0

    if density < 0.01:
        score = max(score - 2, 0)
        justifications.append("Faible densité d'information pour la longueur du texte")

    return min(score, 10)


