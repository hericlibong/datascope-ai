# ai_engine/coherence.py
"""
Module d'analyse de cohérence entre angles éditoriaux et suggestions de données.

Ce module implémente la fonctionnalité pour la sous-issue #4.1.1:
Audit des incohérences courantes (angles → jeux de données).
"""

from typing import List, Dict, Set
import re
from ai_engine.schemas import (
    ExtractionResult, 
    AngleResources, 
    CoherenceMetrics, 
    AnalysisCoherence,
    DatasetSuggestion
)


def compute_location_match_score(
    extracted_locations: List[str], 
    dataset_suggestions: List[DatasetSuggestion]
) -> float:
    """
    Calcule un score de correspondance géographique entre les lieux 
    extraits de l'article et les datasets suggérés.
    
    Returns:
        float: Score entre 0 et 1
    """
    if not extracted_locations or not dataset_suggestions:
        return 0.0
    
    location_keywords = {loc.lower() for loc in extracted_locations}
    matches = 0
    total_datasets = len(dataset_suggestions)
    
    for dataset in dataset_suggestions:
        # Cherche des correspondances dans le titre et la description
        dataset_text = (dataset.title + " " + (dataset.description or "")).lower()
        
        # Vérifie si au moins un lieu extrait apparaît dans le dataset
        for location in location_keywords:
            if location in dataset_text:
                matches += 1
                break
    
    return matches / total_datasets if total_datasets > 0 else 0.0


def compute_theme_match_score(
    extracted_themes: List[str],
    angle_title: str,
    dataset_suggestions: List[DatasetSuggestion]
) -> float:
    """
    Calcule un score de correspondance thématique entre les thèmes
    extraits et les datasets suggérés pour un angle donné.
    
    Returns:
        float: Score entre 0 et 1
    """
    if not extracted_themes and not dataset_suggestions:
        return 1.0  # Cohérent si aucun thème ni dataset
    
    if not extracted_themes:
        return 0.5  # Score neutre si pas de thèmes extraits mais datasets présents
    
    if not dataset_suggestions:
        return 0.0
    
    theme_keywords = {theme.lower() for theme in extracted_themes}
    angle_keywords = set(angle_title.lower().split())
    all_keywords = theme_keywords.union(angle_keywords)
    
    matches = 0
    total_datasets = len(dataset_suggestions)
    
    for dataset in dataset_suggestions:
        dataset_text = (dataset.title + " " + (dataset.description or "")).lower()
        
        # Vérifie si au moins un thème ou mot-clé d'angle apparaît
        for keyword in all_keywords:
            if len(keyword) > 3 and keyword in dataset_text:  # Évite les mots trop courts
                matches += 1
                break
    
    return matches / total_datasets if total_datasets > 0 else 0.0


def analyze_angle_coherence(
    angle_resources: AngleResources,
    extraction_result: ExtractionResult
) -> CoherenceMetrics:
    """
    Analyse la cohérence d'un angle éditorial avec ses suggestions de données.
    """
    location_score = compute_location_match_score(
        extraction_result.locations,
        angle_resources.datasets
    )
    
    theme_score = compute_theme_match_score(
        extraction_result.themes,
        angle_resources.title,
        angle_resources.datasets
    )
    
    # Score global pondéré (géo 40%, thématique 60%)
    overall_coherence = 0.4 * location_score + 0.6 * theme_score
    
    return CoherenceMetrics(
        angle_index=angle_resources.index,
        angle_title=angle_resources.title,
        location_match_score=location_score,
        theme_match_score=theme_score,
        overall_coherence=overall_coherence,
        dataset_count=len(angle_resources.datasets)
    )


def analyze_article_coherence(
    extraction_result: ExtractionResult,
    angle_resources_list: List[AngleResources],
    article_id: str = None
) -> AnalysisCoherence:
    """
    Analyse la cohérence globale d'un article et de ses angles/datasets.
    """
    angle_metrics = []
    
    for angle_resources in angle_resources_list:
        metrics = analyze_angle_coherence(angle_resources, extraction_result)
        angle_metrics.append(metrics)
    
    # Calcul du score global
    if angle_metrics:
        overall_score = sum(m.overall_coherence for m in angle_metrics) / len(angle_metrics)
    else:
        overall_score = 0.0
    
    # Identification du lieu dominant (le plus fréquent)
    dominant_location = None
    if extraction_result.locations:
        location_counts = {}
        for loc in extraction_result.locations:
            location_counts[loc] = location_counts.get(loc, 0) + 1
        dominant_location = max(location_counts.items(), key=lambda x: x[1])[0]
    
    # Génération de recommandations
    recommendations = generate_recommendations(overall_score, angle_metrics, extraction_result)
    
    return AnalysisCoherence(
        article_id=article_id,
        overall_score=overall_score,
        angle_metrics=angle_metrics,
        dominant_location=dominant_location,
        dominant_themes=extraction_result.themes[:3],  # Top 3 thèmes
        recommendations=recommendations
    )


def generate_recommendations(
    overall_score: float,
    angle_metrics: List[CoherenceMetrics],
    extraction_result: ExtractionResult
) -> List[str]:
    """
    Génère des recommandations d'amélioration basées sur l'analyse de cohérence.
    """
    recommendations = []
    
    if overall_score < 0.3:
        recommendations.append("Score de cohérence faible. Revoir la pertinence des datasets suggérés.")
    
    # Analyse par angle
    for metrics in angle_metrics:
        if metrics.location_match_score < 0.2 and extraction_result.locations:
            recommendations.append(
                f"Angle '{metrics.angle_title}': Améliorer la correspondance géographique "
                f"avec les lieux identifiés ({', '.join(extraction_result.locations[:2])})"
            )
        
        if metrics.theme_match_score < 0.3 and extraction_result.themes:
            recommendations.append(
                f"Angle '{metrics.angle_title}': Améliorer la correspondance thématique "
                f"avec les sujets principaux ({', '.join(extraction_result.themes[:2])})"
            )
        
        if metrics.dataset_count == 0:
            recommendations.append(
                f"Angle '{metrics.angle_title}': Aucun dataset suggéré. "
                "Vérifier les connecteurs et mots-clés."
            )
    
    return recommendations[:5]  # Limite à 5 recommandations