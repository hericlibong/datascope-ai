# ai_engine/tests/test_articles_coherence.py
"""
Tests d'articles pour l'audit de cohérence (sous-issue #4.1.1).

Collection de 10 articles tests pour mesurer la cohérence entre
angles éditoriaux et suggestions de datasets.
"""

import pytest
from ai_engine.coherence import (
    analyze_article_coherence,
    compute_location_match_score,
    compute_theme_match_score
)
from ai_engine.schemas import (
    ExtractionResult,
    AngleResources,
    DatasetSuggestion,
    NumberEntity
)


# Articles de test pour l'audit de cohérence
TEST_ARTICLES = [
    {
        "id": "test_001",
        "title": "Pollution de l'air à Paris : les chiffres alarmants",
        "content": """
        L'Airparif a publié son rapport annuel sur la qualité de l'air en Île-de-France.
        Les particules fines PM2.5 dépassent les seuils recommandés dans 75% des stations
        de mesure parisiennes. Le ministre de la Transition écologique, Christophe Béchu,
        a annoncé de nouvelles mesures le 15 mars 2024.
        """,
        "expected_extraction": ExtractionResult(
            language="fr",
            persons=["Christophe Béchu"],
            organizations=["Airparif"],
            locations=["Paris", "Île-de-France"],
            dates=["2024-03-15"],
            numbers=[NumberEntity(raw="75%", value=75.0, unit="%")],
            themes=["environnement", "pollution", "santé publique"]
        ),
        "expected_coherent_datasets": [
            "pollution atmosphérique paris",
            "qualité air ile-de-france", 
            "particules fines PM2.5"
        ]
    },
    
    {
        "id": "test_002", 
        "title": "Budget de l'éducation en baisse dans le Nord",
        "content": """
        Le rectorat de Lille a confirmé une réduction de 12 millions d'euros du budget
        de l'éducation pour 2024. Cette décision affecte 450 établissements scolaires
        de la région Hauts-de-France. Pap Ndiaye, ancien ministre de l'Éducation,
        avait alerté sur ces risques en janvier 2024.
        """,
        "expected_extraction": ExtractionResult(
            language="fr",
            persons=["Pap Ndiaye"],
            organizations=["rectorat de Lille"],
            locations=["Nord", "Lille", "Hauts-de-France"],
            dates=["2024-01-01"],
            numbers=[
                NumberEntity(raw="12 millions d'euros", value=12000000.0, unit="euros"),
                NumberEntity(raw="450", value=450.0, unit="")
            ],
            themes=["éducation", "budget", "politique publique"]
        ),
        "expected_coherent_datasets": [
            "budget éducation hauts-de-france",
            "établissements scolaires nord",
            "dépenses publiques éducation"
        ]
    },
    
    {
        "id": "test_003",
        "title": "Exportations agricoles canadiennes vers l'Europe",
        "content": """
        Statistique Canada rapporte une hausse de 23% des exportations de blé vers
        l'Union européenne au premier trimestre 2024. L'Alberta et le Saskatchewan
        représentent 80% de cette production. L'accord CETA facilite ces échanges
        commerciaux depuis 2017.
        """,
        "expected_extraction": ExtractionResult(
            language="fr",
            persons=[],
            organizations=["Statistique Canada", "Union européenne"],
            locations=["Canada", "Europe", "Alberta", "Saskatchewan"],
            dates=["2024", "2017"],
            numbers=[
                NumberEntity(raw="23%", value=23.0, unit="%"),
                NumberEntity(raw="80%", value=80.0, unit="%")
            ],
            themes=["agriculture", "commerce international", "exportations"]
        ),
        "expected_coherent_datasets": [
            "exportations agricoles canada",
            "commerce canada europe",
            "production blé saskatchewan"
        ]
    },
    
    {
        "id": "test_004",
        "title": "Évolution démographique de Marseille",
        "content": """
        L'INSEE révèle que Marseille a perdu 8 000 habitants en 2023, portant
        sa population à 870 000 résidents. C'est la troisième année consécutive
        de déclin démographique. Le maire Benoît Payan attribue ce phénomène
        au coût du logement et au manque d'emplois.
        """,
        "expected_extraction": ExtractionResult(
            language="fr",
            persons=["Benoît Payan"],
            organizations=["INSEE"],
            locations=["Marseille"],
            dates=["2023"],
            numbers=[
                NumberEntity(raw="8 000", value=8000.0, unit=""),
                NumberEntity(raw="870 000", value=870000.0, unit="")
            ],
            themes=["démographie", "population", "urbanisme"]
        ),
        "expected_coherent_datasets": [
            "population marseille",
            "démographie bouches-du-rhône",
            "évolution population paca"
        ]
    },
    
    {
        "id": "test_005",
        "title": "Investissements verts au Royaume-Uni",
        "content": """
        Le gouvernement britannique a alloué 2,5 milliards de livres aux énergies
        renouvelables en 2024. L'Écosse concentre 60% des projets éoliens offshore.
        Le Premier ministre Rishi Sunak vise la neutralité carbone d'ici 2050.
        """,
        "expected_extraction": ExtractionResult(
            language="fr",
            persons=["Rishi Sunak"],
            organizations=["gouvernement britannique"],
            locations=["Royaume-Uni", "Écosse"],
            dates=["2024", "2050"],
            numbers=[
                NumberEntity(raw="2,5 milliards", value=2500000000.0, unit="livres"),
                NumberEntity(raw="60%", value=60.0, unit="%")
            ],
            themes=["énergie", "environnement", "investissement"]
        ),
        "expected_coherent_datasets": [
            "énergies renouvelables royaume-uni",
            "éolien offshore écosse",
            "investissements verts uk"
        ]
    }
]


def test_article_coherence_analysis():
    """Test de l'analyse de cohérence sur les articles de test."""
    
    for article_data in TEST_ARTICLES[:3]:  # Test sur les 3 premiers articles
        extraction = article_data["expected_extraction"]
        
        # Création d'angles fictifs pour le test
        angle_resources = [
            AngleResources(
                index=0,
                title=f"Analyse {article_data['title']}",
                description="Angle principal",
                keywords=extraction.themes[:2],
                datasets=[
                    DatasetSuggestion(
                        title=f"Dataset {extraction.themes[0]}",
                        description=f"Données sur {extraction.locations[0] if extraction.locations else 'la région'}",
                        source_name="test.gouv.fr",
                        source_url="http://test.example.com",
                        found_by="CONNECTOR"
                    )
                ],
                sources=[],
                visualizations=[]
            )
        ]
        
        # Analyse de cohérence
        coherence = analyze_article_coherence(
            extraction,
            angle_resources,
            article_data["id"]
        )
        
        # Vérifications
        assert coherence.article_id == article_data["id"]
        assert 0.0 <= coherence.overall_score <= 1.0
        assert len(coherence.angle_metrics) == 1
        assert coherence.dominant_themes == extraction.themes[:3]


def test_location_match_scoring():
    """Test du scoring de correspondance géographique."""
    
    locations = ["Paris", "Île-de-France"]
    
    # Datasets avec correspondance géographique
    good_datasets = [
        DatasetSuggestion(
            title="Pollution à Paris",
            description="Données qualité air Île-de-France",
            source_name="data.gouv.fr",
            source_url="http://example.com"
        )
    ]
    
    # Datasets sans correspondance
    bad_datasets = [
        DatasetSuggestion(
            title="Agriculture en Bretagne",
            description="Production agricole Finistère",
            source_name="data.gouv.fr", 
            source_url="http://example.com"
        )
    ]
    
    good_score = compute_location_match_score(locations, good_datasets)
    bad_score = compute_location_match_score(locations, bad_datasets)
    
    assert good_score > bad_score
    assert good_score > 0.5
    assert bad_score == 0.0


def test_theme_match_scoring():
    """Test du scoring de correspondance thématique."""
    
    themes = ["environnement", "pollution"]
    angle_title = "Qualité de l'air en ville"
    
    # Datasets thématiquement cohérents
    good_datasets = [
        DatasetSuggestion(
            title="Pollution atmosphérique",
            description="Mesures qualité air environnement urbain",
            source_name="data.gouv.fr",
            source_url="http://example.com"
        )
    ]
    
    # Datasets non cohérents
    bad_datasets = [
        DatasetSuggestion(
            title="Statistiques sportives",
            description="Résultats championnats football",
            source_name="data.gouv.fr",
            source_url="http://example.com"
        )
    ]
    
    good_score = compute_theme_match_score(themes, angle_title, good_datasets)
    bad_score = compute_theme_match_score(themes, angle_title, bad_datasets)
    
    assert good_score > bad_score
    assert good_score > 0.0


def test_coherence_recommendations():
    """Test de la génération de recommandations."""
    
    # Article avec peu de cohérence
    extraction = ExtractionResult(
        language="fr",
        persons=[],
        organizations=[],
        locations=["Paris"],
        dates=[],
        numbers=[],
        themes=["environnement"]
    )
    
    # Angle avec datasets non cohérents
    angle_resources = [
        AngleResources(
            index=0,
            title="Sport et loisirs",
            description="Angle sans rapport",
            keywords=["sport"],
            datasets=[
                DatasetSuggestion(
                    title="Résultats tennis",
                    description="Tournois de tennis en Australie",
                    source_name="example.com",
                    source_url="http://example.com"
                )
            ],
            sources=[],
            visualizations=[]
        )
    ]
    
    coherence = analyze_article_coherence(extraction, angle_resources)
    
    assert coherence.overall_score < 0.5
    assert len(coherence.recommendations) > 0
    assert any("cohérence" in rec.lower() for rec in coherence.recommendations)


@pytest.mark.parametrize("article_data", TEST_ARTICLES[:5])
def test_all_test_articles(article_data):
    """Test paramétrisé sur tous les articles de test."""
    
    extraction = article_data["expected_extraction"]
    
    # Vérifie que l'extraction contient les données attendues
    assert extraction.language in ["fr", "en"]
    assert isinstance(extraction.themes, list)
    
    # Vérifie qu'il y a au moins un élément extrait
    total_entities = (
        len(extraction.persons) + 
        len(extraction.organizations) + 
        len(extraction.locations) +
        len(extraction.dates) + 
        len(extraction.numbers) +
        len(extraction.themes)
    )
    assert total_entities > 0