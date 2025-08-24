# ai_engine/angle_dataset_scoring.py
"""
Module pour calculer le score de correspondance entre un angle éditorial et un jeu de données.
"""
from typing import List
import re
from ai_engine.schemas import Angle, DatasetSuggestion


def compute_angle_dataset_match_score(
    angle: Angle, 
    dataset: DatasetSuggestion,
    keywords: List[str] = None
) -> float:
    """
    Calcule un score de correspondance entre un angle éditorial et un jeu de données.
    
    Args:
        angle: L'angle éditorial
        dataset: Le jeu de données
        keywords: Mots-clés optionnels extraits pour cet angle
        
    Returns:
        Score entre 0.0 (aucune correspondance) et 1.0 (correspondance parfaite)
    """
    score = 0.0
    
    # Préparation des textes pour la comparaison
    angle_text = (angle.title + " " + angle.rationale).lower()
    dataset_text = (dataset.title + " " + (dataset.description or "")).lower()
    
    # 1. Score basé sur les mots communs (40% du score)
    word_overlap_score = _compute_word_overlap_score(angle_text, dataset_text)
    score += word_overlap_score * 0.4
    
    # 2. Score basé sur les mots-clés si disponibles (30% du score)
    if keywords:
        keywords_score = _compute_keywords_score(keywords, dataset_text)
        score += keywords_score * 0.3
    
    # 3. Score basé sur la pertinence thématique (30% du score)
    thematic_score = _compute_thematic_score(angle_text, dataset_text)
    score += thematic_score * 0.3
    
    return min(score, 1.0)


def _compute_word_overlap_score(angle_text: str, dataset_text: str) -> float:
    """Calcule le score basé sur le chevauchement des mots significatifs."""
    # Mots vides français et anglais courants
    stop_words = {
        'le', 'la', 'les', 'un', 'une', 'des', 'de', 'du', 'et', 'ou', 'est', 'sont',
        'dans', 'sur', 'avec', 'pour', 'par', 'ce', 'cette', 'ces', 'que', 'qui',
        'the', 'and', 'or', 'is', 'are', 'in', 'on', 'with', 'for', 'by', 'this',
        'that', 'these', 'what', 'which', 'of', 'to', 'a', 'an', 'from'
    }
    
    # Extraction des mots significatifs (> 3 caractères, pas de mots vides)
    angle_words = set(
        word for word in re.findall(r'\b\w{4,}\b', angle_text)
        if word not in stop_words
    )
    dataset_words = set(
        word for word in re.findall(r'\b\w{4,}\b', dataset_text)
        if word not in stop_words
    )
    
    if not angle_words or not dataset_words:
        return 0.0
    
    # Score basé sur l'intersection des mots
    common_words = angle_words & dataset_words
    return len(common_words) / min(len(angle_words), len(dataset_words))


def _compute_keywords_score(keywords: List[str], dataset_text: str) -> float:
    """Calcule le score basé sur la présence des mots-clés dans le dataset."""
    if not keywords:
        return 0.0
    
    dataset_text_lower = dataset_text.lower()
    found_keywords = 0
    for keyword in keywords:
        if keyword.lower() in dataset_text_lower:
            found_keywords += 1
    
    return found_keywords / len(keywords)


def _compute_thematic_score(angle_text: str, dataset_text: str) -> float:
    """
    Calcule un score thématique basé sur des patterns spécifiques.
    Cette fonction peut être enrichie avec des règles plus sophistiquées.
    """
    score = 0.0
    
    # Patterns thématiques communs
    thematic_patterns = {
        'economics': ['économi', 'finance', 'budget', 'coût', 'prix', 'marché', 'commercial'],
        'health': ['santé', 'médical', 'hôpital', 'patient', 'maladie', 'traitement'],
        'education': ['éducation', 'école', 'étudiant', 'formation', 'universitaire'],
        'environment': ['environnement', 'climat', 'pollution', 'écologie', 'énergie'],
        'demographics': ['population', 'démographi', 'habitant', 'âge', 'naissance'],
        'transport': ['transport', 'circulation', 'véhicule', 'route', 'mobilité']
    }
    
    # Détection des thèmes dans l'angle et le dataset
    angle_themes = set()
    dataset_themes = set()
    
    for theme, patterns in thematic_patterns.items():
        for pattern in patterns:
            if pattern in angle_text:
                angle_themes.add(theme)
            if pattern in dataset_text:
                dataset_themes.add(theme)
    
    # Score basé sur les thèmes communs
    if angle_themes and dataset_themes:
        common_themes = angle_themes & dataset_themes
        score = len(common_themes) / min(len(angle_themes), len(dataset_themes))
    
    return score


def should_filter_dataset(match_score: float, threshold: float = 0.2) -> bool:
    """
    Détermine si un dataset doit être filtré basé sur son score de correspondance.
    
    Args:
        match_score: Score de correspondance (0-1)
        threshold: Seuil en dessous duquel filtrer (défaut: 0.2)
        
    Returns:
        True si le dataset doit être filtré (score trop bas)
    """
    return match_score < threshold


def get_match_quality_label(match_score: float) -> str:
    """
    Retourne un label qualitatif pour le score de correspondance.
    
    Args:
        match_score: Score de correspondance (0-1)
        
    Returns:
        Label descriptif ("Excellente", "Bonne", "Moyenne", "Faible")
    """
    if match_score >= 0.8:
        return "Excellente"
    elif match_score >= 0.6:
        return "Bonne"  
    elif match_score >= 0.4:
        return "Moyenne"
    else:
        return "Faible"


def get_match_quality_alert(match_score: float) -> dict:
    """
    Retourne des informations d'alerte basées sur le score de correspondance.
    
    Args:
        match_score: Score de correspondance (0-1)
        
    Returns:
        Dictionnaire avec level ('success', 'warning', 'danger') et message
    """
    if match_score >= 0.7:
        return {
            "level": "success",
            "message": "Excellente correspondance avec l'angle éditorial",
            "icon": "✅"
        }
    elif match_score >= 0.4:
        return {
            "level": "warning", 
            "message": "Correspondance modérée - vérifiez la pertinence",
            "icon": "⚠️"
        }
    else:
        return {
            "level": "danger",
            "message": "Faible correspondance - dataset possiblement non pertinent",
            "icon": "❌"
        }


def filter_datasets_by_quality(
    datasets: List[DatasetSuggestion], 
    min_score: float = 0.2,
    max_datasets: int = None
) -> tuple[List[DatasetSuggestion], List[DatasetSuggestion]]:
    """
    Filtre les datasets par qualité de correspondance.
    
    Args:
        datasets: Liste des datasets à filtrer
        min_score: Score minimum pour conserver un dataset
        max_datasets: Nombre maximum de datasets à conserver (optionnel)
        
    Returns:
        Tuple (datasets_conservés, datasets_filtrés)
    """
    # Trier par score décroissant
    sorted_datasets = sorted(datasets, key=lambda d: d.match_score, reverse=True)
    
    # Filtrer par score minimum
    kept_datasets = [ds for ds in sorted_datasets if ds.match_score >= min_score]
    filtered_datasets = [ds for ds in sorted_datasets if ds.match_score < min_score]
    
    # Limiter le nombre si spécifié
    if max_datasets and len(kept_datasets) > max_datasets:
        additional_filtered = kept_datasets[max_datasets:]
        filtered_datasets.extend(additional_filtered)
        kept_datasets = kept_datasets[:max_datasets]
    
    return kept_datasets, filtered_datasets