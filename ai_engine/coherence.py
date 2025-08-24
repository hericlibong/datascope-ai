"""
Moteur de cohérence pour évaluer la correspondance entre angles éditoriaux et datasets.

Ce module implémente:
- Scoring de correspondance angle ↔ dataset (#4.3.1)
- Règles de mapping améliorées angle.topic ↔ dataset.tags (#4.3.2)  
- Stratégie de fallback pour datasets LLM incohérents (#4.3.3)
"""

import re
import requests
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from ai_engine.schemas import DatasetSuggestion, Angle
import logging

logger = logging.getLogger(__name__)

@dataclass
class CoherenceScore:
    """Score de cohérence entre un angle et un dataset."""
    score: float  # 0.0 à 1.0
    confidence: float  # 0.0 à 1.0
    reasoning: List[str]  # Justifications du score
    issues: List[str]  # Problèmes détectés

class CoherenceEngine:
    """Moteur de cohérence pour évaluer la correspondance angle-dataset."""
    
    def __init__(self):
        self.keyword_weights = {
            'exact_match': 0.4,      # Correspondance exacte mot-clé
            'semantic_match': 0.3,   # Correspondance sémantique  
            'topic_relevance': 0.2,  # Pertinence thématique
            'metadata_quality': 0.1  # Qualité des métadonnées
        }
        
    def compute_angle_dataset_score(
        self, 
        angle: Angle, 
        dataset: DatasetSuggestion,
        keywords: List[str] = None
    ) -> CoherenceScore:
        """
        Calcule le score de cohérence entre un angle éditorial et un dataset.
        
        Args:
            angle: Angle éditorial avec titre et justification
            dataset: Dataset suggéré avec métadonnées
            keywords: Mots-clés extraits pour l'angle (optionnel)
            
        Returns:
            CoherenceScore: Score avec justifications et problèmes détectés
        """
        reasoning = []
        issues = []
        
        # 1. Score de correspondance des mots-clés
        keyword_score = self._compute_keyword_match(angle, dataset, keywords or [])
        if keyword_score > 0.7:
            reasoning.append(f"Forte correspondance mots-clés ({keyword_score:.2f})")
        elif keyword_score < 0.3:
            issues.append(f"Faible correspondance mots-clés ({keyword_score:.2f})")
            
        # 2. Score de pertinence thématique
        topic_score = self._compute_topic_relevance(angle, dataset)
        if topic_score > 0.6:
            reasoning.append(f"Bonne pertinence thématique ({topic_score:.2f})")
        elif topic_score < 0.3:
            issues.append(f"Pertinence thématique faible ({topic_score:.2f})")
            
        # 3. Score de qualité des métadonnées
        metadata_score = self._compute_metadata_quality(dataset)
        if metadata_score < 0.5:
            issues.append(f"Métadonnées de qualité insuffisante ({metadata_score:.2f})")
            
        # 4. Score global pondéré
        total_score = (
            keyword_score * self.keyword_weights['exact_match'] +
            topic_score * self.keyword_weights['topic_relevance'] +
            metadata_score * self.keyword_weights['metadata_quality']
        )
        
        # 5. Calcul de la confiance basé sur la disponibilité des données
        confidence = self._compute_confidence(dataset, len(reasoning), len(issues))
        
        return CoherenceScore(
            score=min(total_score, 1.0),
            confidence=confidence,
            reasoning=reasoning,
            issues=issues
        )
    
    def _compute_keyword_match(
        self, 
        angle: Angle, 
        dataset: DatasetSuggestion, 
        keywords: List[str]
    ) -> float:
        """
        Calcule la correspondance entre les mots-clés de l'angle et les métadonnées du dataset.
        Amélioration des règles de mapping (#4.3.2).
        """
        # Texte à analyser du dataset
        dataset_text = f"{dataset.title} {dataset.description or ''}"
        dataset_text = dataset_text.lower()
        
        # Mots-clés de l'angle
        angle_text = f"{angle.title} {angle.rationale}".lower()
        all_keywords = keywords + self._extract_keywords_from_text(angle_text)
        
        if not all_keywords:
            return 0.0
        
        # Améliorations du matching (#4.3.2)
        exact_matches = 0
        partial_matches = 0
        
        for keyword in all_keywords:
            keyword_lower = keyword.lower()
            
            # Correspondance exacte (poids 1.0)
            if keyword_lower in dataset_text:
                exact_matches += 1
            # Correspondance partielle/racine (poids 0.5)  
            elif len(keyword_lower) > 4:
                # Cherche les racines de mots (ex: "économ" dans "économique")
                root = keyword_lower[:5]
                if root in dataset_text:
                    partial_matches += 1
                    
        # Score pondéré
        total_score = (exact_matches + partial_matches * 0.5) / len(all_keywords)
        return min(total_score, 1.0)
    
    def _compute_topic_relevance(self, angle: Angle, dataset: DatasetSuggestion) -> float:
        """Évalue la pertinence thématique entre l'angle et le dataset."""
        # Analyse simple basée sur les domaines thématiques
        angle_topics = self._extract_topics(f"{angle.title} {angle.rationale}")
        dataset_topics = self._extract_topics(f"{dataset.title} {dataset.description or ''}")
        
        if not angle_topics or not dataset_topics:
            return 0.5  # Score neutre si pas assez d'informations
            
        # Intersection des topics
        common_topics = set(angle_topics) & set(dataset_topics)
        relevance = len(common_topics) / max(len(angle_topics), len(dataset_topics))
        
        return min(relevance, 1.0)
    
    def _compute_metadata_quality(self, dataset: DatasetSuggestion) -> float:
        """Évalue la qualité des métadonnées du dataset."""
        score = 0.0
        
        # Présence de titre (obligatoire)
        if dataset.title and len(dataset.title.strip()) > 5:
            score += 0.3
            
        # Présence de description
        if dataset.description and len(dataset.description.strip()) > 20:
            score += 0.3
            
        # Présence de formats
        if dataset.formats and len(dataset.formats) > 0:
            score += 0.2
            
        # Présence d'organisation
        if dataset.organization and len(dataset.organization.strip()) > 0:
            score += 0.1
            
        # Date de modification récente (bonus)
        if dataset.last_modified:
            score += 0.1
            
        return min(score, 1.0)
    
    def _compute_confidence(self, dataset: DatasetSuggestion, reasoning_count: int, issues_count: int) -> float:
        """Calcule le niveau de confiance du score."""
        confidence = 0.5  # Base
        
        # Plus de justifications = plus de confiance
        confidence += min(reasoning_count * 0.1, 0.3)
        
        # Moins de problèmes = plus de confiance
        confidence -= min(issues_count * 0.1, 0.3)
        
        # URL valide augmente la confiance
        if self._is_valid_url(dataset.source_url):
            confidence += 0.2
        else:
            confidence -= 0.3
            
        return max(0.0, min(confidence, 1.0))
    
    def _extract_keywords_from_text(self, text: str) -> List[str]:
        """Extrait des mots-clés simples d'un texte."""
        # Supprime la ponctuation et split
        clean_text = re.sub(r'[^\w\s]', ' ', text.lower())
        words = clean_text.split()
        
        # Filtre les mots courts et les stop words basiques
        stop_words = {'le', 'la', 'les', 'de', 'du', 'des', 'et', 'ou', 'un', 'une', 'pour', 'sur', 'avec', 'dans'}
        keywords = [w for w in words if len(w) > 3 and w not in stop_words]
        
        return list(set(keywords))  # Déduplique
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extrait des topics/domaines thématiques d'un texte."""
        # Mapping amélioré de mots-clés vers des domaines (#4.3.2)
        topic_mapping = {
            'santé': ['santé', 'médical', 'hôpital', 'médicament', 'patient', 'vaccination', 'épidémie', 'maladie', 'soins'],
            'économie': ['économie', 'finance', 'budget', 'entreprise', 'chômage', 'pib', 'croissance', 'inflation', 'marché'],
            'environnement': ['environnement', 'climat', 'pollution', 'énergie', 'écologie', 'carbone', 'renouvelable', 'biodiversité'],
            'transport': ['transport', 'route', 'train', 'avion', 'mobilité', 'métro', 'bus', 'vélo', 'circulation'],
            'éducation': ['éducation', 'école', 'université', 'étudiant', 'formation', 'enseignement', 'apprentissage', 'diplôme'],
            'démographie': ['population', 'démographie', 'habitant', 'recensement', 'naissance', 'mortalité', 'migration'],
            'sécurité': ['sécurité', 'crime', 'police', 'justice', 'délinquance', 'tribunal', 'prison', 'violence'],
            'logement': ['logement', 'immobilier', 'construction', 'habitation', 'loyer', 'propriété', 'hlm'],
            'emploi': ['emploi', 'travail', 'salarié', 'télétravail', 'métier', 'profession', 'carrière', 'stage'],
            'technologie': ['technologie', 'numérique', 'internet', 'ia', 'artificielle', 'données', 'digital', 'tech'],
            'culture': ['culture', 'musée', 'théâtre', 'cinéma', 'livre', 'art', 'patrimoine', 'festival'],
            'social': ['social', 'famille', 'jeunesse', 'senior', 'handicap', 'solidarité', 'aide', 'allocation'],
            'gouvernance': ['gouvernement', 'politique', 'élu', 'mairie', 'conseil', 'administration', 'public', 'collectivité']
        }
        
        text_lower = text.lower()
        detected_topics = []
        
        for topic, keywords in topic_mapping.items():
            # Score de correspondance pour chaque topic
            matches = sum(1 for keyword in keywords if keyword in text_lower)
            if matches > 0:
                detected_topics.append((topic, matches))
                
        # Trie par nombre de matches décroissant et retourne les topics
        detected_topics.sort(key=lambda x: x[1], reverse=True)
        return [topic for topic, _ in detected_topics[:5]]  # Max 5 topics les plus pertinents
    
    def _is_valid_url(self, url: str) -> bool:
        """Vérifie rapidement si une URL semble valide (sans faire de requête HTTP)."""
        if not url or not isinstance(url, str):
            return False
            
        # Vérification basique du format
        url_pattern = re.compile(
            r'^https?://'  # http:// ou https://
            r'[a-zA-Z0-9.-]+'  # nom de domaine
            r'[.][a-zA-Z]{2,}'  # extension
        )
        
        return bool(url_pattern.match(url))

    def validate_dataset_link(self, dataset: DatasetSuggestion, timeout: int = 5) -> Tuple[bool, Optional[str]]:
        """
        Stratégie de fallback: valide qu'un lien de dataset est accessible.
        
        Returns:
            (is_valid, error_message)
        """
        if not self._is_valid_url(dataset.source_url):
            return False, "URL format invalide"
            
        try:
            response = requests.head(dataset.source_url, timeout=timeout, allow_redirects=True)
            if response.status_code == 200:
                return True, None
            else:
                return False, f"HTTP {response.status_code}"
        except requests.RequestException as e:
            return False, f"Erreur réseau: {str(e)}"
    
    def filter_datasets_by_coherence(
        self, 
        angle: Angle, 
        datasets: List[DatasetSuggestion],
        keywords: List[str] = None,
        min_score: float = 0.3
    ) -> List[Tuple[DatasetSuggestion, CoherenceScore]]:
        """
        Filtre une liste de datasets selon leur score de cohérence avec un angle.
        
        Returns:
            Liste de (dataset, score) triée par score décroissant
        """
        scored_datasets = []
        
        for dataset in datasets:
            score = self.compute_angle_dataset_score(angle, dataset, keywords)
            if score.score >= min_score:
                scored_datasets.append((dataset, score))
                
        # Trie par score décroissant
        scored_datasets.sort(key=lambda x: x[1].score, reverse=True)
        
        return scored_datasets


# Instance globale pour utilisation dans le pipeline
coherence_engine = CoherenceEngine()