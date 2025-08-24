# ai_engine/tests/test_geo_filtering.py
"""
Tests pour le filtrage géo-sémantique des connecteurs.
"""

import pytest
from ai_engine.connectors.geo_filtering import (
    get_geo_keywords,
    build_geo_enhanced_query,
    calculate_geo_score,
    filter_datasets_by_geo_relevance,
    normalize_location
)
from ai_engine.schemas import DatasetSuggestion


def test_normalize_location():
    """Test de normalisation des noms de lieux."""
    assert normalize_location("  Paris  ") == "paris"
    assert normalize_location("Île-de-France") == "île-de-france"
    assert normalize_location("LYON") == "lyon"


def test_get_geo_keywords():
    """Test de récupération des mots-clés géographiques."""
    # Test lieux français
    keywords = get_geo_keywords(["Paris"])
    assert "paris" in keywords
    assert "ile-de-france" in keywords
    
    # Test lieux multiples
    keywords = get_geo_keywords(["France", "Canada"])
    assert "france" in keywords
    assert "canada" in keywords
    
    # Test lieu non mappé
    keywords = get_geo_keywords(["Ville-Inconnue"])
    assert "ville-inconnue" in keywords


def test_build_geo_enhanced_query():
    """Test de construction de requêtes enrichies géographiquement."""
    # Avec lieu identifié
    query = build_geo_enhanced_query("pollution", ["Paris"])
    assert "pollution" in query
    # Paris est mappé vers des mots-clés géographiques, vérifie qu'au moins un est présent
    assert any(geo_term in query.lower() for geo_term in ["paris", "ile-de-france", "idf"])
    
    # Sans lieu
    query = build_geo_enhanced_query("économie", [])
    assert query == "économie"
    
    # Avec plusieurs lieux
    query = build_geo_enhanced_query("transport", ["Lyon", "Marseille"])
    assert "transport" in query
    # Doit contenir au moins un des lieux (Lyon est le premier, donc utilisé tel quel)
    assert "lyon" in query.lower()


def test_calculate_geo_score():
    """Test de calcul du score géographique."""
    geo_keywords = {"paris", "ile-de-france", "france"}
    
    # Dataset pertinent géographiquement
    relevant_dataset = DatasetSuggestion(
        title="Pollution à Paris",
        description="Qualité de l'air en Île-de-France",
        source_name="data.gouv.fr",
        source_url="http://example.com"
    )
    
    # Dataset non pertinent
    irrelevant_dataset = DatasetSuggestion(
        title="Agriculture en Bretagne",
        description="Production céréalière Finistère",
        source_name="other.org",
        source_url="http://example.com"
    )
    
    relevant_score = calculate_geo_score(relevant_dataset, geo_keywords)
    irrelevant_score = calculate_geo_score(irrelevant_dataset, geo_keywords)
    
    assert relevant_score > irrelevant_score
    assert relevant_score > 0
    
    # Test bonus pour source française
    assert relevant_score >= 3.0  # 2 mots-clés + bonus source


def test_filter_datasets_by_geo_relevance():
    """Test de filtrage par pertinence géographique."""
    
    datasets = [
        DatasetSuggestion(
            title="Transport Paris",
            description="Données RATP Île-de-France",
            source_name="data.gouv.fr",
            source_url="http://example.com/1"
        ),
        DatasetSuggestion(
            title="Agriculture Bretagne",
            description="Production Finistère",
            source_name="data.gouv.fr", 
            source_url="http://example.com/2"
        ),
        DatasetSuggestion(
            title="Démographie parisienne",
            description="Population Paris métropole",
            source_name="insee.fr",
            source_url="http://example.com/3"
        )
    ]
    
    # Filtrage pour Paris
    locations = ["Paris"]
    filtered = filter_datasets_by_geo_relevance(iter(datasets), locations, max_results=2)
    
    assert len(filtered) <= 2
    # Les premiers résultats doivent être les plus pertinents pour Paris
    assert any("paris" in ds.title.lower() or "paris" in (ds.description or "").lower() 
              for ds in filtered[:1])


def test_geo_filtering_edge_cases():
    """Test des cas limites du filtrage géographique."""
    
    # Pas de lieux identifiés
    datasets = [
        DatasetSuggestion(
            title="Dataset 1",
            description="Description 1",
            source_name="example.com",
            source_url="http://example.com/1"
        )
    ]
    
    filtered = filter_datasets_by_geo_relevance(iter(datasets), [], max_results=10)
    assert len(filtered) == 1  # Retourne tout si pas de filtrage géo
    
    # Pas de datasets
    filtered = filter_datasets_by_geo_relevance(iter([]), ["Paris"], max_results=10)
    assert len(filtered) == 0


def test_geo_keywords_mapping():
    """Test du mapping des mots-clés géographiques."""
    
    # Test France et variantes
    keywords = get_geo_keywords(["France"])
    assert "france" in keywords
    assert "français" in keywords
    
    # Test Canada
    keywords = get_geo_keywords(["Canada"])
    assert "canada" in keywords
    assert "canadian" in keywords
    
    # Test États-Unis et variantes
    keywords = get_geo_keywords(["États-Unis"])
    assert any(kw in keywords for kw in ["états-unis", "usa", "united states"])


def test_multiple_locations_priority():
    """Test de priorité avec plusieurs lieux."""
    
    datasets = [
        DatasetSuggestion(
            title="Données Paris-Lyon",
            description="Transport inter-villes",
            source_name="sncf.fr",
            source_url="http://example.com"
        ),
        DatasetSuggestion(
            title="Économie lyonnaise",
            description="PIB région Auvergne-Rhône-Alpes",
            source_name="insee.fr",
            source_url="http://example.com"
        ),
        DatasetSuggestion(
            title="Tourisme parisien",
            description="Fréquentation monuments Paris",
            source_name="paris.fr",
            source_url="http://example.com"
        )
    ]
    
    # Priorité Paris puis Lyon
    locations = ["Paris", "Lyon"]
    filtered = filter_datasets_by_geo_relevance(iter(datasets), locations)
    
    # Vérifie que le tri privilégie les datasets mentionnant les lieux
    assert len(filtered) == 3
    
    # Le premier dataset devrait mentionner au moins un des lieux
    first_dataset = filtered[0]
    text = (first_dataset.title + " " + (first_dataset.description or "")).lower()
    assert "paris" in text or "lyon" in text


def test_geographic_sources_bonus():
    """Test du bonus pour les sources géographiquement cohérentes."""
    
    # Dataset français sur source française
    fr_dataset = DatasetSuggestion(
        title="Données France",
        description="Statistiques nationales",
        source_name="data.gouv.fr",
        source_url="http://example.com"
    )
    
    # Dataset canadien sur source canadienne
    ca_dataset = DatasetSuggestion(
        title="Canadian data",
        description="Statistics Canada",
        source_name="open.canada.ca",
        source_url="http://example.com"
    )
    
    fr_keywords = {"france", "français"}
    ca_keywords = {"canada", "canadian"}
    
    fr_score = calculate_geo_score(fr_dataset, fr_keywords)
    ca_score = calculate_geo_score(ca_dataset, ca_keywords)
    
    # Les deux devraient avoir un bonus significatif
    assert fr_score >= 2.0  # Au moins le bonus source
    assert ca_score >= 2.0