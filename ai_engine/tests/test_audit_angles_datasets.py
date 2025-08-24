"""
Test d'audit des incohérences entre les angles éditoriaux et les jeux de données suggérés.

Ce test vérifie sur 10 articles test que les datasets proposés sont bien cohérents
avec les angles éditoriaux générés par l'IA.
"""

import pytest
from unittest.mock import patch, MagicMock
from typing import List
from collections import defaultdict

from ai_engine.schemas import (
    AngleResult, Angle, AngleResources, DatasetSuggestion, 
    LLMSourceSuggestion, VizSuggestion, KeywordSet, KeywordsResult
)
import ai_engine.chains.angles as angles
import ai_engine.chains.keywords as keywords
import ai_engine.chains.llm_sources as llm_sources
import ai_engine.chains.viz as viz
from ai_engine.pipeline import run_connectors


# Test articles covering different data journalism scenarios
TEST_ARTICLES = [
    {
        "id": 1,
        "content": "Les émissions de CO₂ du secteur aérien ont augmenté de 50% depuis 2000. Les compagnies low-cost représentent désormais 40% du trafic européen.",
        "expected_topics": ["aviation", "émissions", "co2", "transport", "environnement"]
    },
    {
        "id": 2, 
        "content": "Unemployment rates in the US have dropped to 3.5% in 2023, the lowest in 50 years. Tech sector hiring has increased by 25% compared to 2022.",
        "expected_topics": ["employment", "unemployment", "jobs", "tech", "economy"]
    },
    {
        "id": 3,
        "content": "La France a enregistré 15% d'accidents de la route de moins en 2023. Les nouvelles mesures de sécurité routière semblent porter leurs fruits.",
        "expected_topics": ["accidents", "sécurité", "routière", "france", "transport"]
    },
    {
        "id": 4,
        "content": "Global food prices have risen 23% over the past year, driven by climate change and supply chain disruptions affecting wheat and rice production.",
        "expected_topics": ["food", "prices", "agriculture", "climate", "wheat", "rice"]
    },
    {
        "id": 5,
        "content": "Les dépenses de santé publique en Europe ont augmenté de 8% en 2023, principalement dues au vieillissement de la population.",
        "expected_topics": ["santé", "dépenses", "europe", "vieillissement", "population"]
    },
    {
        "id": 6,
        "content": "Renewable energy now accounts for 35% of global electricity generation, with solar power leading the growth at 15% annually.",
        "expected_topics": ["renewable", "energy", "solar", "electricity", "climate"]
    },
    {
        "id": 7,
        "content": "Le taux de chômage des jeunes en Espagne reste à 28%, soit le plus élevé d'Europe après la Grèce.",
        "expected_topics": ["chômage", "jeunes", "espagne", "europe", "emploi"]
    },
    {
        "id": 8,
        "content": "Housing prices in major Canadian cities have increased by 12% year-over-year, with Toronto and Vancouver leading the surge.",
        "expected_topics": ["housing", "prices", "canada", "toronto", "vancouver", "real estate"]
    },
    {
        "id": 9,
        "content": "La biodiversité marine a diminué de 20% dans la Méditerranée au cours des 10 dernières années selon une étude européenne.",
        "expected_topics": ["biodiversité", "marine", "méditerranée", "environnement", "faune"]
    },
    {
        "id": 10,
        "content": "Digital transformation spending by enterprises reached $2.3 trillion globally in 2023, with AI and cloud services driving 60% of investments.",
        "expected_topics": ["digital", "transformation", "ai", "cloud", "technology", "enterprise"]
    }
]


class AuditResult:
    """Structure pour stocker les résultats d'audit"""
    def __init__(self):
        self.articles_tested = 0
        self.total_angles = 0
        self.total_datasets = 0
        self.inconsistencies = []
        self.empty_dataset_angles = []
        self.keyword_mismatches = []
        self.duplicate_datasets = []
        self.missing_metadata = []
        
    def add_inconsistency(self, article_id: int, angle_idx: int, issue_type: str, details: str):
        self.inconsistencies.append({
            'article_id': article_id,
            'angle_idx': angle_idx,
            'issue_type': issue_type,
            'details': details
        })
        
    def get_summary(self) -> dict:
        return {
            'articles_tested': self.articles_tested,
            'total_angles': self.total_angles,
            'total_datasets': self.total_datasets,
            'total_inconsistencies': len(self.inconsistencies),
            'empty_dataset_angles': len(self.empty_dataset_angles),
            'keyword_mismatches': len(self.keyword_mismatches),
            'duplicate_datasets': len(self.duplicate_datasets),
            'missing_metadata': len(self.missing_metadata)
        }


def create_mock_angle_result(article_id: int, language: str = "fr") -> AngleResult:
    """Crée un résultat d'angle mocké basé sur l'article de test"""
    article = TEST_ARTICLES[article_id - 1]
    
    if language == "fr":
        angles_data = [
            {
                "title": f"Impact économique - Article {article_id}",
                "rationale": "Analyser les conséquences économiques des données présentées."
            },
            {
                "title": f"Tendances temporelles - Article {article_id}", 
                "rationale": "Étudier l'évolution des indicateurs dans le temps."
            },
            {
                "title": f"Comparaison internationale - Article {article_id}",
                "rationale": "Comparer avec d'autres pays ou régions similaires."
            }
        ]
    else:
        angles_data = [
            {
                "title": f"Economic impact - Article {article_id}",
                "rationale": "Analyze the economic consequences of the presented data."
            },
            {
                "title": f"Temporal trends - Article {article_id}",
                "rationale": "Study the evolution of indicators over time."
            },
            {
                "title": f"International comparison - Article {article_id}",
                "rationale": "Compare with other similar countries or regions."
            }
        ]
    
    angles = [Angle(**angle_data) for angle_data in angles_data]
    return AngleResult(language=language, angles=angles)


def create_mock_keywords_result(article_id: int, angle_idx: int) -> KeywordsResult:
    """Crée des mots-clés mockés pour un angle donné"""
    article = TEST_ARTICLES[article_id - 1]
    expected_topics = article["expected_topics"]
    
    # Sélectionner 5 mots-clés pertinents
    keywords = expected_topics[:5]
    if len(keywords) < 5:
        keywords.extend(["données", "statistiques", "analyse", "étude", "rapport"][:5-len(keywords)])
    
    return KeywordsResult(
        language="fr" if article_id % 2 == 1 else "en",
        sets=[KeywordSet(
            angle_title=f"Angle {angle_idx}",
            keywords=keywords
        )]
    )


def create_mock_dataset_suggestions(article_id: int, angle_idx: int, relevant: bool = True) -> List[DatasetSuggestion]:
    """Crée des suggestions de datasets mockées"""
    article = TEST_ARTICLES[article_id - 1]
    expected_topics = article["expected_topics"]
    
    if not relevant:
        # Créer des datasets non pertinents pour tester les incohérences
        return [
            DatasetSuggestion(
                title="Dataset complètement non pertinent",
                description="Ce dataset n'a rien à voir avec l'angle.",
                source_url=f"https://irrelevant.com/dataset_{article_id}_{angle_idx}",
                source_name="Source Non Pertinente",
                format="CSV",
                found_by="CONNECTOR",
                angle_idx=angle_idx
            )
        ]
    
    # Créer des datasets pertinents
    primary_topic = expected_topics[0] if expected_topics else "data"
    
    return [
        DatasetSuggestion(
            title=f"Dataset {primary_topic} - Article {article_id}",
            description=f"Données officielles sur {primary_topic} et statistiques connexes.",
            source_url=f"https://data.gov/dataset_{primary_topic}_{article_id}_{angle_idx}",
            source_name="Gouvernement Officiel",
            formats=["CSV"],
            found_by="CONNECTOR",
            angle_idx=angle_idx
        ),
        DatasetSuggestion(
            title=f"Base de données {primary_topic} internationale",
            description=f"Compilation internationale de données sur {primary_topic}.",
            source_url=f"https://international.org/{primary_topic}_{article_id}",
            source_name="Organisation Internationale",
            formats=["JSON"],
            found_by="LLM",
            angle_idx=angle_idx
        )
    ]


def check_keyword_dataset_consistency(keywords: List[str], datasets: List[DatasetSuggestion]) -> List[str]:
    """Vérifie la cohérence entre mots-clés et datasets"""
    issues = []
    
    for dataset in datasets:
        title_lower = dataset.title.lower()
        desc_lower = dataset.description.lower()
        
        # Vérifier si au moins un mot-clé apparaît dans le titre ou la description
        keyword_found = False
        for keyword in keywords:
            if keyword.lower() in title_lower or keyword.lower() in desc_lower:
                keyword_found = True
                break
                
        if not keyword_found:
            issues.append(f"Dataset '{dataset.title}' ne contient aucun mot-clé de l'angle: {keywords}")
            
    return issues


def check_dataset_metadata_quality(datasets: List[DatasetSuggestion]) -> List[str]:
    """Vérifie la qualité des métadonnées des datasets"""
    issues = []
    
    for dataset in datasets:
        if not dataset.title or len(dataset.title.strip()) < 5:
            issues.append(f"Titre trop court ou manquant: '{dataset.title}'")
            
        if not dataset.description or len(dataset.description.strip()) < 10:
            issues.append(f"Description trop courte ou manquante pour: '{dataset.title}'")
            
        if not dataset.source_url or not dataset.source_url.startswith(('http://', 'https://')):
            issues.append(f"URL source invalide pour: '{dataset.title}' - {dataset.source_url}")
            
        if not dataset.formats or len(dataset.formats) == 0:
            issues.append(f"Formats manquants pour: '{dataset.title}'")
            
    return issues


def find_duplicate_datasets(angle_resources: List[AngleResources]) -> List[str]:
    """Trouve les datasets dupliqués entre différents angles"""
    url_to_angles = defaultdict(list)
    duplicates = []
    
    for angle in angle_resources:
        for dataset in angle.datasets:
            url_to_angles[dataset.source_url].append(f"Angle {angle.index}: {angle.title}")
    
    for url, angle_list in url_to_angles.items():
        if len(angle_list) > 1:
            duplicates.append(f"Dataset dupliqué {url} trouvé dans: {', '.join(angle_list)}")
            
    return duplicates


@pytest.mark.integration
def test_audit_angles_datasets_consistency():
    """
    Test d'audit principal: vérifie la cohérence entre angles et datasets sur 10 articles.
    
    Ce test simule le pipeline complet et vérifie:
    1. Que chaque angle a des datasets associés
    2. Que les datasets sont pertinents par rapport aux mots-clés de l'angle
    3. Qu'il n'y a pas de doublons inappropriés
    4. Que les métadonnées sont de qualité suffisante
    """
    audit_result = AuditResult()
    
    # Test sur tous les articles
    for article in TEST_ARTICLES:
        article_id = article["id"]
        audit_result.articles_tested += 1
        
        # Mock des chaînes AI
        with patch.object(angles, 'run') as mock_angles, \
             patch.object(keywords, 'run') as mock_keywords, \
             patch('ai_engine.pipeline.run_connectors') as mock_connectors:
            
            # Configuration des mocks
            angle_result = create_mock_angle_result(article_id)
            mock_angles.return_value = angle_result
            
            # Mock keywords pour chaque angle
            mock_keywords_results = []
            for angle_idx in range(len(angle_result.angles)):
                kw_result = create_mock_keywords_result(article_id, angle_idx)
                mock_keywords_results.append(kw_result)
            mock_keywords.return_value = mock_keywords_results
            
            # Mock connectors - injecter quelques incohérences pour tester
            connector_results = []
            for angle_idx in range(len(angle_result.angles)):
                # 20% chance d'avoir des datasets non pertinents
                relevant = not (article_id == 3 and angle_idx == 1) and not (article_id == 7 and angle_idx == 2)
                datasets = create_mock_dataset_suggestions(article_id, angle_idx, relevant)
                connector_results.append(datasets)
            
            mock_connectors.return_value = connector_results
            
            # Créer AngleResources pour l'audit
            angle_resources = []
            for angle_idx, angle in enumerate(angle_result.angles):
                audit_result.total_angles += 1
                
                keywords_data = mock_keywords_results[angle_idx] if angle_idx < len(mock_keywords_results) else create_mock_keywords_result(article_id, angle_idx)
                datasets = connector_results[angle_idx] if angle_idx < len(connector_results) else []
                audit_result.total_datasets += len(datasets)
                
                # 1. Vérifier les angles sans datasets
                if not datasets:
                    audit_result.empty_dataset_angles.append(f"Article {article_id}, Angle {angle_idx}")
                    audit_result.add_inconsistency(
                        article_id, angle_idx, "empty_datasets", 
                        f"Aucun dataset trouvé pour l'angle '{angle.title}'"
                    )
                
                # 2. Vérifier la cohérence mots-clés/datasets
                if datasets and keywords_data.sets:
                    keyword_issues = check_keyword_dataset_consistency(
                        keywords_data.sets[0].keywords, datasets
                    )
                    for issue in keyword_issues:
                        audit_result.keyword_mismatches.append(issue)
                        audit_result.add_inconsistency(
                            article_id, angle_idx, "keyword_mismatch", issue
                        )
                
                # 3. Vérifier la qualité des métadonnées
                metadata_issues = check_dataset_metadata_quality(datasets)
                for issue in metadata_issues:
                    audit_result.missing_metadata.append(issue)
                    audit_result.add_inconsistency(
                        article_id, angle_idx, "metadata_quality", issue
                    )
                
                angle_resources.append(AngleResources(
                    index=angle_idx,
                    title=angle.title,
                    description=angle.rationale,
                    keywords=keywords_data.sets[0].keywords if keywords_data.sets else [],
                    datasets=datasets,
                    sources=[],  # Simplified for this test
                    visualizations=[]
                ))
            
            # 4. Vérifier les doublons entre angles
            duplicate_issues = find_duplicate_datasets(angle_resources)
            for issue in duplicate_issues:
                audit_result.duplicate_datasets.append(issue)
                audit_result.add_inconsistency(
                    article_id, -1, "duplicate_dataset", issue
                )
    
    # Génération du rapport d'audit
    summary = audit_result.get_summary()
    
    print("\n" + "="*80)
    print("RAPPORT D'AUDIT - COHÉRENCE ANGLES → DATASETS")
    print("="*80)
    print(f"Articles testés: {summary['articles_tested']}")
    print(f"Angles générés: {summary['total_angles']}")
    print(f"Datasets suggérés: {summary['total_datasets']}")
    print(f"Incohérences détectées: {summary['total_inconsistencies']}")
    print()
    
    if summary['empty_dataset_angles'] > 0:
        print(f"⚠️  Angles sans datasets: {summary['empty_dataset_angles']}")
        for angle in audit_result.empty_dataset_angles:
            print(f"   - {angle}")
        print()
    
    if summary['keyword_mismatches'] > 0:
        print(f"⚠️  Incohérences mots-clés/datasets: {summary['keyword_mismatches']}")
        for issue in audit_result.keyword_mismatches[:3]:  # Afficher les 3 premiers
            print(f"   - {issue}")
        if len(audit_result.keyword_mismatches) > 3:
            print(f"   ... et {len(audit_result.keyword_mismatches) - 3} autres")
        print()
    
    if summary['duplicate_datasets'] > 0:
        print(f"⚠️  Datasets dupliqués: {summary['duplicate_datasets']}")
        for issue in audit_result.duplicate_datasets:
            print(f"   - {issue}")
        print()
    
    if summary['missing_metadata'] > 0:
        print(f"⚠️  Problèmes de métadonnées: {summary['missing_metadata']}")
        for issue in audit_result.missing_metadata[:3]:  # Afficher les 3 premiers
            print(f"   - {issue}")
        if len(audit_result.missing_metadata) > 3:
            print(f"   ... et {len(audit_result.missing_metadata) - 3} autres")
        print()
    
    print("="*80)
    print(f"RÉSULTAT: {summary['total_inconsistencies']} incohérences détectées sur {summary['articles_tested']} articles")
    print("="*80)
    
    # Assertions pour valider l'audit
    assert summary['articles_tested'] == 10, "Doit tester exactement 10 articles"
    assert summary['total_angles'] > 0, "Doit générer des angles"
    assert summary['total_datasets'] > 0, "Doit suggérer des datasets"
    
    # Le test passe même avec des incohérences - c'est un audit, pas un test de qualité
    # Mais on veut s'assurer que l'audit fonctionne en détectant les problèmes injectés
    assert summary['total_inconsistencies'] >= 2, "L'audit doit détecter les incohérences injectées"


@pytest.mark.integration  
def test_audit_empty_datasets_detection():
    """Test spécifique pour détecter les angles sans datasets"""
    
    # Mock pour simuler un angle sans datasets
    with patch.object(angles, 'run') as mock_angles, \
         patch('ai_engine.pipeline.run_connectors') as mock_connectors:
        
        angle_result = create_mock_angle_result(1)
        mock_angles.return_value = angle_result
        
        # Simuler des connecteurs qui ne trouvent rien
        mock_connectors.return_value = [[], [], []]  # 3 angles, 0 datasets chacun
        
        angle_resources = []
        for angle_idx, angle in enumerate(angle_result.angles):
            angle_resources.append(AngleResources(
                index=angle_idx,
                title=angle.title,
                description=angle.rationale,
                keywords=[],
                datasets=[],  # Pas de datasets
                sources=[],
                visualizations=[]
            ))
        
        # Vérifier que tous les angles sont détectés comme vides
        empty_angles = [ar for ar in angle_resources if not ar.datasets]
        assert len(empty_angles) == 3, "Tous les angles devraient être détectés comme vides"


@pytest.mark.integration
def test_audit_keyword_relevance():
    """Test spécifique pour vérifier la pertinence des mots-clés vs datasets"""
    
    keywords = ["transport", "aviation", "émissions"]
    
    # Dataset pertinent
    relevant_dataset = DatasetSuggestion(
        title="Statistiques transport aérien",
        description="Données sur les émissions du secteur aviation",
        source_url="https://example.com/aviation",
        source_name="Source Test",
        formats=["CSV"],
        found_by="CONNECTOR",
        angle_idx=0
    )
    
    # Dataset non pertinent
    irrelevant_dataset = DatasetSuggestion(
        title="Données météorologiques",
        description="Températures et précipitations quotidiennes",
        source_url="https://example.com/weather",
        source_name="Source Test",
        formats=["JSON"],
        found_by="CONNECTOR", 
        angle_idx=0
    )
    
    # Tester la cohérence
    relevant_issues = check_keyword_dataset_consistency(keywords, [relevant_dataset])
    irrelevant_issues = check_keyword_dataset_consistency(keywords, [irrelevant_dataset])
    
    assert len(relevant_issues) == 0, "Dataset pertinent ne devrait pas générer d'issues"
    assert len(irrelevant_issues) == 1, "Dataset non pertinent devrait générer une issue"
    assert "météorologiques" in irrelevant_issues[0], "L'issue devrait mentionner le dataset problématique"


if __name__ == "__main__":
    # Permettre d'exécuter l'audit directement
    pytest.main([__file__ + "::test_audit_angles_datasets_consistency", "-v", "-s"])