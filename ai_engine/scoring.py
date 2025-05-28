from ai_engine.schemas import ExtractionResult
from ai_engine.utils import token_len

DENSITY_SCALE = 500 

def compute_score(extr: ExtractionResult, article_text: str, *, model: str | None = None) -> int:
    """Score 0-100 basé sur densité et diversité, normalisé par la longueur réelle de l’article."""
    nb_tokens = token_len(article_text, model=model)
    nb_entities = sum(map(len, [
        extr.persons, extr.organizations, extr.locations, extr.dates, extr.numbers
    ]))

    densite = (nb_entities / max(nb_tokens, 1)) * DENSITY_SCALE
    densite = min(densite, 100)

    diversite = len([lst for lst in
                     [extr.persons, extr.organizations, extr.locations,
                      extr.dates, extr.numbers] if lst]) / 5 * 100

    return round(0.7 * densite + 0.3 * diversite)

