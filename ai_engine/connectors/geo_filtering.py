# ai_engine/connectors/geo_filtering.py
"""
Module de filtrage géo-sémantique pour les connecteurs.

Implémente la fonctionnalité pour la sous-issue #4.1.3:
Forcer les connecteurs à se baser en priorité sur le lieu identifié.
"""

from typing import List, Dict, Iterator, Optional
from ai_engine.schemas import DatasetSuggestion
from ai_engine.connectors.interface import ConnectorInterface


# Mapping des lieux vers des mots-clés de recherche spécifiques
GEOGRAPHIC_KEYWORDS = {
    # France
    "france": ["france", "français", "fr", "national"],
    "paris": ["paris", "ile-de-france", "idf", "région parisienne"],
    "lyon": ["lyon", "rhône", "auvergne-rhône-alpes"],
    "marseille": ["marseille", "bouches-du-rhône", "paca", "provence"],
    "toulouse": ["toulouse", "haute-garonne", "occitanie"],
    "lille": ["lille", "nord", "hauts-de-france"],
    "bordeaux": ["bordeaux", "gironde", "nouvelle-aquitaine"],
    "nantes": ["nantes", "loire-atlantique", "pays de la loire"],
    "strasbourg": ["strasbourg", "bas-rhin", "alsace", "grand est"],
    "montpellier": ["montpellier", "hérault", "occitanie"],
    
    # Europe
    "europe": ["europe", "européen", "eu", "ue"],
    "allemagne": ["allemagne", "deutschland", "german", "de"],
    "italie": ["italie", "italia", "italian", "it"],
    "espagne": ["espagne", "españa", "spanish", "es"],
    "royaume-uni": ["royaume-uni", "uk", "britain", "british"],
    
    # Monde
    "canada": ["canada", "canadian", "ca"],
    "états-unis": ["états-unis", "usa", "united states", "us", "american"],
    "chine": ["chine", "china", "chinese", "cn"],
    "japon": ["japon", "japan", "japanese", "jp"],
}


def normalize_location(location: str) -> str:
    """Normalise un nom de lieu pour la recherche."""
    return location.lower().strip()


def get_geo_keywords(locations: List[str]) -> List[str]:
    """
    Retourne les mots-clés géographiques associés aux lieux identifiés.
    """
    geo_keywords = []
    
    for location in locations:
        normalized_loc = normalize_location(location)
        
        # Recherche directe dans le mapping
        if normalized_loc in GEOGRAPHIC_KEYWORDS:
            geo_keywords.extend(GEOGRAPHIC_KEYWORDS[normalized_loc])
        else:
            # Recherche partielle pour les variantes
            for geo_key, keywords in GEOGRAPHIC_KEYWORDS.items():
                if normalized_loc in geo_key or geo_key in normalized_loc:
                    geo_keywords.extend(keywords)
                    break
            else:
                # Si pas trouvé, utilise le lieu tel quel
                geo_keywords.append(normalized_loc)
    
    return list(set(geo_keywords))  # Supprime les doublons


def build_geo_enhanced_query(original_keyword: str, locations: List[str]) -> str:
    """
    Construit une requête enrichie géographiquement.
    """
    if not locations:
        return original_keyword
    
    geo_keywords = get_geo_keywords(locations)
    
    # Priorise le lieu principal (premier dans la liste) ou utilise tous si peu nombreux
    if geo_keywords:
        if len(locations) == 1:
            primary_geo = geo_keywords[0]
        else:
            # Pour plusieurs lieux, prend le premier lieu original
            primary_geo = normalize_location(locations[0])
        return f"{original_keyword} {primary_geo}"
    
    return original_keyword


def filter_datasets_by_geo_relevance(
    datasets: Iterator[DatasetSuggestion],
    locations: List[str],
    max_results: int = 10
) -> List[DatasetSuggestion]:
    """
    Filtre et classe les datasets par pertinence géographique.
    """
    if not locations:
        # Si pas de lieu identifié, retourne les premiers résultats
        return list(datasets)[:max_results]
    
    geo_keywords = get_geo_keywords(locations)
    geo_keywords_set = {kw.lower() for kw in geo_keywords}
    
    scored_datasets = []
    
    for dataset in datasets:
        score = calculate_geo_score(dataset, geo_keywords_set)
        scored_datasets.append((score, dataset))
    
    # Trie par score décroissant
    scored_datasets.sort(key=lambda x: x[0], reverse=True)
    
    # Retourne les datasets triés
    return [dataset for _, dataset in scored_datasets[:max_results]]


def calculate_geo_score(dataset: DatasetSuggestion, geo_keywords: set) -> float:
    """
    Calcule un score de pertinence géographique pour un dataset.
    """
    text_to_search = (
        dataset.title + " " + 
        (dataset.description or "") + " " + 
        (dataset.organization or "")
    ).lower()
    
    score = 0.0
    
    # Score basé sur les correspondances de mots-clés
    for keyword in geo_keywords:
        if keyword in text_to_search:
            score += 1.0
    
    # Bonus pour certaines sources géographiques spécifiques
    if dataset.source_name:
        source = dataset.source_name.lower()
        if "gouv.fr" in source and any(kw in ["france", "français", "fr"] for kw in geo_keywords):
            score += 2.0
        elif "canada" in source and "canada" in geo_keywords:
            score += 2.0
        elif "data.gov" in source and any(kw in ["usa", "us", "american"] for kw in geo_keywords):
            score += 2.0
    
    return score


class GeoEnhancedConnectorMixin:
    """
    Mixin pour ajouter les capacités de filtrage géo-sémantique aux connecteurs.
    """
    
    def search_with_geo_priority(
        self,
        keyword: str,
        locations: List[str],
        page_size: int = 10
    ) -> Iterator[DatasetSuggestion]:
        """
        Recherche avec priorité géographique.
        """
        # Si le connecteur hérite de cette classe, il doit avoir une méthode search
        if not hasattr(self, 'search'):
            raise NotImplementedError("Le connecteur doit implémenter la méthode search")
        
        # Enrichit la requête avec des mots-clés géographiques
        enhanced_query = build_geo_enhanced_query(keyword, locations)
        
        # Effectue la recherche avec la requête enrichie
        results = self.search(enhanced_query, page_size=page_size * 2)  # Plus de résultats pour filtrer
        
        # Filtre et classe par pertinence géographique
        geo_filtered = filter_datasets_by_geo_relevance(results, locations, page_size)
        
        # Retourne les résultats filtrés
        for dataset in geo_filtered:
            yield dataset


# Fonction utilitaire pour enrichir les recherches existantes
def enhance_connector_search(
    connector: ConnectorInterface,
    keyword: str,
    locations: List[str],
    page_size: int = 10
) -> Iterator[DatasetSuggestion]:
    """
    Fonction utilitaire pour améliorer n'importe quel connecteur existant
    avec le filtrage géographique.
    """
    enhanced_query = build_geo_enhanced_query(keyword, locations)
    results = connector.search(enhanced_query, page_size=page_size * 2)
    geo_filtered = filter_datasets_by_geo_relevance(results, locations, page_size)
    
    for dataset in geo_filtered:
        yield dataset