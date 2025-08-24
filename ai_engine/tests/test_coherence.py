"""
Tests unitaires pour le moteur de cohérence (ai_engine.coherence)
"""

import pytest
from ai_engine.coherence import CoherenceEngine, CoherenceScore
from ai_engine.schemas import Angle, DatasetSuggestion


class TestCoherenceEngine:
    
    def setup_method(self):
        """Setup pour chaque test."""
        self.engine = CoherenceEngine()
        
        # Angle test
        self.test_angle = Angle(
            title="Impact économique du télétravail",
            rationale="Analyser les effets du télétravail sur l'économie française"
        )
        
        # Dataset fortement cohérent
        self.good_dataset = DatasetSuggestion(
            title="Statistiques télétravail économie France 2024",
            description="Données officielles sur l'impact économique du télétravail en France",
            source_name="INSEE",
            source_url="https://www.insee.fr/teletr-eco-2024",
            formats=["CSV", "JSON"],
            organization="INSEE",
            found_by="CONNECTOR"
        )
        
        # Dataset peu cohérent
        self.poor_dataset = DatasetSuggestion(
            title="Météo pluviométrie",
            description="Données de précipitations en Bretagne",
            source_name="MeteoFrance", 
            source_url="https://meteo.fr/pluie-bretagne",
            formats=["XML"],
            organization="Météo France",
            found_by="LLM"
        )
        
    def test_compute_angle_dataset_score_high_relevance(self):
        """Test avec un dataset très pertinent."""
        keywords = ["télétravail", "économie", "impact", "france"]
        
        score = self.engine.compute_angle_dataset_score(
            self.test_angle, self.good_dataset, keywords
        )
        
        assert isinstance(score, CoherenceScore)
        assert score.score > 0.6  # Score élevé attendu
        assert score.confidence > 0.5
        assert len(score.reasoning) > 0
        assert "Forte correspondance mots-clés" in " ".join(score.reasoning) or "Bonne pertinence thématique" in " ".join(score.reasoning)

    def test_compute_angle_dataset_score_low_relevance(self):
        """Test avec un dataset peu pertinent."""
        keywords = ["télétravail", "économie", "impact", "france"]
        
        score = self.engine.compute_angle_dataset_score(
            self.test_angle, self.poor_dataset, keywords
        )
        
        assert isinstance(score, CoherenceScore)
        assert score.score < 0.4  # Score faible attendu
        assert len(score.issues) > 0

    def test_keyword_match_exact(self):
        """Test de correspondance exacte des mots-clés."""
        keywords = ["télétravail", "économie"]
        
        match_score = self.engine._compute_keyword_match(
            self.test_angle, self.good_dataset, keywords
        )
        
        assert 0.0 <= match_score <= 1.0
        assert match_score > 0.3  # Devrait avoir une correspondance raisonnable

    def test_metadata_quality_good(self):
        """Test qualité métadonnées avec dataset complet."""
        quality = self.engine._compute_metadata_quality(self.good_dataset)
        
        assert quality > 0.7  # Bon dataset avec titre, description, formats, org

    def test_metadata_quality_poor(self):
        """Test qualité métadonnées avec dataset minimal."""
        minimal_dataset = DatasetSuggestion(
            title="Test",
            source_name="Test",
            source_url="http://test.com",
            found_by="LLM"
        )
        
        quality = self.engine._compute_metadata_quality(minimal_dataset)
        
        assert quality < 0.5  # Métadonnées insuffisantes

    def test_topic_extraction(self):
        """Test extraction de topics thématiques."""
        text = "économie finance budget entreprise santé médical transport"
        topics = self.engine._extract_topics(text)
        
        assert "économie" in topics
        assert "santé" in topics
        assert "transport" in topics

    def test_url_validation_valid(self):
        """Test validation d'URL valide."""
        valid_url = "https://www.example.com/data"
        assert self.engine._is_valid_url(valid_url) == True

    def test_url_validation_invalid(self):
        """Test validation d'URL invalide."""
        invalid_urls = [
            "not-a-url",
            "ftp://invalid",
            "",
            None
        ]
        for url in invalid_urls:
            assert self.engine._is_valid_url(url) == False

    def test_filter_datasets_by_coherence(self):
        """Test filtrage des datasets par score de cohérence."""
        datasets = [self.good_dataset, self.poor_dataset]
        keywords = ["télétravail", "économie"]
        
        filtered = self.engine.filter_datasets_by_coherence(
            self.test_angle, datasets, keywords, min_score=0.4
        )
        
        # Doit retourner une liste de tuples (dataset, score)
        assert len(filtered) >= 1  # Au moins le bon dataset
        assert all(isinstance(item, tuple) and len(item) == 2 for item in filtered)
        assert all(isinstance(item[1], CoherenceScore) for item in filtered)
        
        # Vérifie que c'est trié par score décroissant
        scores = [item[1].score for item in filtered]
        assert scores == sorted(scores, reverse=True)

    def test_coherence_score_structure(self):
        """Test structure du CoherenceScore."""
        score = self.engine.compute_angle_dataset_score(
            self.test_angle, self.good_dataset, []
        )
        
        assert hasattr(score, 'score')
        assert hasattr(score, 'confidence')
        assert hasattr(score, 'reasoning')
        assert hasattr(score, 'issues')
        
        assert 0.0 <= score.score <= 1.0
        assert 0.0 <= score.confidence <= 1.0
        assert isinstance(score.reasoning, list)
        assert isinstance(score.issues, list)

    def test_validate_dataset_link_timeout(self):
        """Test validation avec timeout très court (simulation)."""
        # URL fictive qui ne devrait pas répondre
        fake_dataset = DatasetSuggestion(
            title="Test",
            source_name="Test", 
            source_url="https://httpbin.org/delay/10",  # Délai long
            found_by="LLM"
        )
        
        is_valid, error_msg = self.engine.validate_dataset_link(fake_dataset, timeout=1)
        
        # Doit échouer à cause du timeout
        assert is_valid == False
        assert error_msg is not None

    def test_empty_keywords_handling(self):
        """Test comportement avec mots-clés vides."""
        score = self.engine.compute_angle_dataset_score(
            self.test_angle, self.good_dataset, []
        )
        
        # Doit fonctionner même sans mots-clés
        assert isinstance(score, CoherenceScore)
        assert 0.0 <= score.score <= 1.0