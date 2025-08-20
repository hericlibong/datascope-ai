# ai_engine/tests/test_angle_dataset_scoring.py
import pytest
from ai_engine.schemas import Angle, DatasetSuggestion
from ai_engine.angle_dataset_scoring import (
    compute_angle_dataset_match_score,
    should_filter_dataset,
    get_match_quality_label,
    get_match_quality_alert,
    filter_datasets_by_quality,
    _compute_word_overlap_score,
    _compute_keywords_score,
    _compute_thematic_score
)


def test_compute_word_overlap_score():
    """Test du calcul de score basé sur le chevauchement des mots."""
    angle_text = "économie française budget gouvernement"
    dataset_text = "données économie budget France"
    
    score = _compute_word_overlap_score(angle_text, dataset_text)
    assert 0.0 <= score <= 1.0
    assert score >= 0.5  # Devrait avoir un bon score avec "économie" et "budget" en commun


def test_compute_keywords_score():
    """Test du calcul de score basé sur les mots-clés."""
    keywords = ["économie", "budget", "France"]
    dataset_text = "données sur l'économie et le budget de la France"
    
    score = _compute_keywords_score(keywords, dataset_text)
    assert score == 1.0  # Tous les mots-clés sont présents dans le texte
    
    dataset_text_partial = "données sur l'économie française"
    score_partial = _compute_keywords_score(keywords, dataset_text_partial)
    assert 0.0 < score_partial < 1.0


def test_compute_thematic_score():
    """Test du calcul de score thématique."""
    angle_text = "analyse économique du marché français"
    dataset_text = "données économiques budget commercial"
    
    score = _compute_thematic_score(angle_text, dataset_text)
    assert 0.0 <= score <= 1.0
    assert score > 0.0  # Devrait détecter le thème économique


def test_compute_angle_dataset_match_score():
    """Test principal du calcul de score de correspondance angle-dataset."""
    # Cas de forte correspondance
    angle = Angle(
        title="Analyse du budget de l'éducation",
        rationale="Étudier l'évolution des dépenses éducatives en France"
    )
    dataset = DatasetSuggestion(
        title="Budget de l'éducation nationale",
        description="Données sur les dépenses d'éducation par région",
        source_name="data.gouv.fr",
        source_url="https://data.gouv.fr/education-budget"
    )
    keywords = ["éducation", "budget", "dépenses", "France"]
    
    score = compute_angle_dataset_match_score(angle, dataset, keywords)
    assert 0.0 <= score <= 1.0
    assert score > 0.6  # Devrait avoir un bon score
    
    # Cas de faible correspondance
    angle_different = Angle(
        title="Transport maritime",
        rationale="Analyser le trafic des ports français"
    )
    
    score_low = compute_angle_dataset_match_score(angle_different, dataset, ["transport", "maritime"])
    assert score_low < score  # Score plus faible pour un angle non lié


def test_should_filter_dataset():
    """Test de la fonction de filtrage."""
    assert should_filter_dataset(0.1) == True   # Score trop bas
    assert should_filter_dataset(0.5) == False  # Score acceptable
    assert should_filter_dataset(0.9) == False  # Excellent score
    
    # Test avec seuil personnalisé
    assert should_filter_dataset(0.3, threshold=0.4) == True
    assert should_filter_dataset(0.5, threshold=0.4) == False


def test_get_match_quality_label():
    """Test des labels de qualité."""
    assert get_match_quality_label(0.9) == "Excellente"
    assert get_match_quality_label(0.7) == "Bonne"
    assert get_match_quality_label(0.5) == "Moyenne"
    assert get_match_quality_label(0.1) == "Faible"


def test_get_match_quality_alert():
    """Test des alertes de qualité."""
    alert_excellent = get_match_quality_alert(0.9)
    assert alert_excellent["level"] == "success"
    assert "✅" in alert_excellent["icon"]
    
    alert_moderate = get_match_quality_alert(0.5)
    assert alert_moderate["level"] == "warning"
    assert "⚠️" in alert_moderate["icon"]
    
    alert_poor = get_match_quality_alert(0.1)
    assert alert_poor["level"] == "danger"
    assert "❌" in alert_poor["icon"]


def test_filter_datasets_by_quality():
    """Test du filtrage des datasets par qualité."""
    datasets = [
        DatasetSuggestion(
            title="Dataset 1", 
            source_name="test", 
            source_url="http://test1.com",
            match_score=0.8
        ),
        DatasetSuggestion(
            title="Dataset 2", 
            source_name="test", 
            source_url="http://test2.com",
            match_score=0.5
        ),
        DatasetSuggestion(
            title="Dataset 3", 
            source_name="test", 
            source_url="http://test3.com",
            match_score=0.1
        )
    ]
    
    # Test filtrage par score minimum
    kept, filtered = filter_datasets_by_quality(datasets, min_score=0.3)
    assert len(kept) == 2  # Datasets avec score >= 0.3
    assert len(filtered) == 1  # Dataset avec score < 0.3
    assert kept[0].match_score == 0.8  # Trié par score décroissant
    
    # Test limitation du nombre
    kept_limited, filtered_limited = filter_datasets_by_quality(datasets, min_score=0.0, max_datasets=2)
    assert len(kept_limited) == 2
    assert len(filtered_limited) == 1


def test_edge_cases():
    """Test des cas limites."""
    # Angle et dataset vides
    empty_angle = Angle(title="", rationale="")
    empty_dataset = DatasetSuggestion(
        title="",
        description="",
        source_name="test",
        source_url="https://test.com"
    )
    
    score = compute_angle_dataset_match_score(empty_angle, empty_dataset)
    assert score == 0.0
    
    # Dataset sans description
    angle = Angle(title="Test", rationale="Test rationale")
    dataset_no_desc = DatasetSuggestion(
        title="Test dataset",
        description=None,
        source_name="test",
        source_url="https://test.com"
    )
    
    score = compute_angle_dataset_match_score(angle, dataset_no_desc)
    assert 0.0 <= score <= 1.0