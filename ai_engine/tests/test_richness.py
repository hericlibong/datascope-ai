"""
Issue 2.5.3 – tests unitaires de richness_score
On vérifie simplement que la note produite est bornée dans [0-100].
"""

import datetime as dt
from ai_engine.schemas import DatasetSuggestion as DS
from ai_engine.connectors.richness import richness_score


def test_richness_score_in_bounds():
    # ------------------------------------------------------------------
    # 1) Jeu de données factice : date calculée par rapport à "maintenant"
    # ------------------------------------------------------------------
    now_utc = dt.datetime.now(dt.timezone.utc)
    sugg = DS(
        title="Jeu de données de test",
        source_name="data.gouv.fr",
        source_url="https://example.com/dataset",
        formats=["csv", "json"],
        organization="INSEE",
        license="ETALAB",
        last_modified=(now_utc - dt.timedelta(days=10)).isoformat(),
        description="Jeu très complet et bien documenté.",
    )

    # ------------------------------------------------------------------
    # 2) Calcul & assertion – on ne fait **qu’un** contrôle fonctionnel
    # ------------------------------------------------------------------
    score = richness_score(sugg)
    assert 0 <= score <= 100, "Le score doit toujours être borné dans [0 ; 100]"

