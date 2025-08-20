# ai_engine/tests/test_coherence_integration.py
"""
Test d'intégration pour les fonctionnalités de cohérence.
"""

import pytest
from ai_engine.coherence import analyze_article_coherence
from ai_engine.connectors.geo_filtering import enhance_connector_search
from ai_engine.schemas import ExtractionResult, AngleResources, DatasetSuggestion, NumberEntity


def test_coherence_integration():
    """Test d'intégration de l'analyse de cohérence."""
    
    # Données d'extraction simulées
    extraction = ExtractionResult(
        language="fr",
        persons=["Emmanuel Macron"],
        organizations=["INSEE"],
        locations=["Paris", "France"],
        dates=["2024-03-15"],
        numbers=[NumberEntity(raw="75%", value=75.0, unit="%")],
        themes=["économie", "emploi", "statistiques"]
    )
    
    # Angles avec datasets cohérents et incohérents
    angles = [
        AngleResources(
            index=0,
            title="Analyse économique parisienne",
            description="Situation économique à Paris",
            keywords=["économie", "paris"],
            datasets=[
                DatasetSuggestion(
                    title="Emploi en Île-de-France",
                    description="Statistiques INSEE sur l'emploi en région parisienne",
                    source_name="data.gouv.fr",
                    source_url="http://example.com/emploi-idf"
                ),
                DatasetSuggestion(
                    title="PIB régional France",
                    description="Données économiques par région",
                    source_name="insee.fr", 
                    source_url="http://example.com/pib-france"
                )
            ],
            sources=[],
            visualizations=[]
        ),
        AngleResources(
            index=1,
            title="Sports et loisirs",
            description="Activités sportives",
            keywords=["sport", "loisirs"],
            datasets=[
                DatasetSuggestion(
                    title="Championnat football australien",
                    description="Résultats sports Australie",
                    source_name="sport.au",
                    source_url="http://example.com/sport-au"
                )
            ],
            sources=[],
            visualizations=[]
        )
    ]
    
    # Analyse de cohérence
    coherence = analyze_article_coherence(extraction, angles, "test_001")
    
    # Vérifications
    assert coherence.article_id == "test_001"
    assert 0.0 <= coherence.overall_score <= 1.0
    assert len(coherence.angle_metrics) == 2
    assert coherence.dominant_location == "Paris"  # Premier lieu identifié
    assert len(coherence.dominant_themes) <= 3
    
    # Le premier angle devrait être plus cohérent que le second
    assert coherence.angle_metrics[0].overall_coherence > coherence.angle_metrics[1].overall_coherence
    
    # Vérification des scores individuels
    first_angle = coherence.angle_metrics[0]
    assert first_angle.location_match_score > 0.0  # Correspondance avec Paris/France
    assert first_angle.theme_match_score > 0.0     # Correspondance avec économie
    
    second_angle = coherence.angle_metrics[1]
    assert second_angle.location_match_score == 0.0  # Pas de correspondance géographique
    # Le score thématique peut être > 0 si le titre de l'angle correspond au contenu du dataset
    # Dans ce cas, "sports" apparaît dans les deux


def test_geo_filtering_integration():
    """Test d'intégration du filtrage géographique."""
    
    # Mock connector simple pour les tests
    class MockConnector:
        def search(self, keyword, page_size=10):
            datasets = [
                DatasetSuggestion(
                    title=f"Dataset {keyword} Paris",
                    description=f"Données {keyword} en Île-de-France",
                    source_name="data.gouv.fr",
                    source_url=f"http://example.com/{keyword}-paris"
                ),
                DatasetSuggestion(
                    title=f"Dataset {keyword} Bretagne",
                    description=f"Données {keyword} en Bretagne",
                    source_name="data.gouv.fr",
                    source_url=f"http://example.com/{keyword}-bretagne"
                ),
                DatasetSuggestion(
                    title=f"Dataset {keyword} global",
                    description=f"Données {keyword} nationales",
                    source_name="insee.fr",
                    source_url=f"http://example.com/{keyword}-national"
                )
            ]
            return iter(datasets)
    
    connector = MockConnector()
    locations = ["Paris"]
    
    # Test avec filtrage géographique
    filtered_results = list(enhance_connector_search(
        connector, "emploi", locations, page_size=3
    ))
    
    assert len(filtered_results) <= 3
    
    # Le premier résultat devrait mentionner Paris (score géographique plus élevé)
    first_result = filtered_results[0]
    text = (first_result.title + " " + first_result.description).lower()
    assert "paris" in text or "ile-de-france" in text


def test_themes_extraction_integration():
    """Test d'intégration de l'extraction de thèmes."""
    
    # Test que la nouvelle structure ExtractionResult fonctionne
    extraction = ExtractionResult(
        language="fr",
        persons=[],
        organizations=["ADEME"],
        locations=["France"],
        dates=["2024"],
        numbers=[],
        themes=["environnement", "énergie renouvelable", "transition écologique"]
    )
    
    # Vérifications
    assert hasattr(extraction, 'themes')
    assert len(extraction.themes) == 3
    assert "environnement" in extraction.themes
    assert extraction.themes == ["environnement", "énergie renouvelable", "transition écologique"]


@pytest.mark.parametrize("location,expected_keywords", [
    ("Paris", ["paris", "ile-de-france"]),
    ("France", ["france", "français"]),
    ("Canada", ["canada", "canadian"]),
    ("Lyon", ["lyon"])  # Ville non mappée, utilise le nom tel quel
])
def test_geo_keywords_mapping_integration(location, expected_keywords):
    """Test paramétrisé de mapping des mots-clés géographiques."""
    from ai_engine.connectors.geo_filtering import get_geo_keywords
    
    keywords = get_geo_keywords([location])
    
    # Vérifie qu'au moins un des mots-clés attendus est présent
    assert any(expected in keywords for expected in expected_keywords)


def test_coherence_recommendations():
    """Test de génération de recommandations de cohérence."""
    
    # Article avec extraction mais angles peu cohérents
    extraction = ExtractionResult(
        language="fr",
        persons=[],
        organizations=[],
        locations=["Paris"],
        dates=[],
        numbers=[],
        themes=["santé", "médecine"]
    )
    
    # Angle totalement incohérent (sport en Australie vs santé à Paris)
    angles = [
        AngleResources(
            index=0,
            title="Sports aquatiques australiens",
            description="Compétitions de surf",
            keywords=["sport", "surf"],
            datasets=[
                DatasetSuggestion(
                    title="Météorologie marine Océanie",
                    description="Conditions météo côtes australiennes",
                    source_name="weather.au",
                    source_url="http://example.com"
                )
            ],
            sources=[],
            visualizations=[]
        )
    ]
    
    coherence = analyze_article_coherence(extraction, angles)
    
    # Score faible attendu car aucune correspondance thématique ni géographique
    assert coherence.overall_score < 0.5
    
    # Recommandations générées
    assert len(coherence.recommendations) > 0
    
    # Au moins une recommandation sur la correspondance géographique ou thématique
    recommendations_text = " ".join(coherence.recommendations).lower()
    assert any(keyword in recommendations_text for keyword in 
               ["correspondance", "géographique", "thématique", "cohérence"])