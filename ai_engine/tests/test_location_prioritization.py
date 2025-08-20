"""
Test location-based prioritization for connectors
"""

import pytest
from unittest.mock import Mock, patch

from ai_engine.connectors.location_utils import (
    calculate_location_relevance,
    enhance_query_with_locations,
    filter_and_sort_by_location_relevance
)
from ai_engine.connectors.data_gouv import DataGouvClient
from ai_engine.schemas import DatasetSuggestion


class TestLocationUtils:
    """Test location utility functions"""
    
    def test_calculate_location_relevance_no_locations(self):
        """Test relevance calculation with no locations"""
        metadata = {"title": "Some dataset", "description": "Some data"}
        relevance = calculate_location_relevance(metadata, [])
        assert relevance == 0.0
    
    def test_calculate_location_relevance_exact_match(self):
        """Test relevance calculation with exact location match"""
        metadata = {
            "title": "Paris Climate Data", 
            "description": "Temperature data from Paris"
        }
        locations = ["Paris"]
        relevance = calculate_location_relevance(metadata, locations)
        assert relevance > 0.0
    
    def test_calculate_location_relevance_partial_match(self):
        """Test relevance calculation with partial location match"""
        metadata = {
            "title": "New York Traffic Data", 
            "description": "Traffic patterns in New York City"
        }
        locations = ["New York", "London"]
        relevance = calculate_location_relevance(metadata, locations)
        assert relevance > 0.0
    
    def test_calculate_location_relevance_no_match(self):
        """Test relevance calculation with no location match"""
        metadata = {
            "title": "Random Dataset", 
            "description": "Some unrelated data"
        }
        locations = ["Paris", "London"]
        relevance = calculate_location_relevance(metadata, locations)
        assert relevance == 0.0
    
    def test_enhance_query_with_locations_no_locations(self):
        """Test query enhancement with no locations"""
        enhanced = enhance_query_with_locations("climate", None)
        assert enhanced == "climate"
    
    def test_enhance_query_with_locations_with_locations(self):
        """Test query enhancement with locations"""
        enhanced = enhance_query_with_locations("climate", ["Paris", "London"])
        assert "climate" in enhanced
        assert "Paris" in enhanced
        assert "London" in enhanced
    
    def test_filter_and_sort_by_location_relevance(self):
        """Test sorting datasets by location relevance"""
        # Create mock datasets
        datasets = [
            {"title": "Random Data", "description": "Unrelated"},
            {"title": "Paris Climate", "description": "Weather in Paris"},
            {"title": "London Traffic", "description": "Traffic in London"},
        ]
        
        locations = ["Paris"]
        sorted_datasets = filter_and_sort_by_location_relevance(datasets, locations)
        
        # Paris dataset should be first
        assert "Paris" in sorted_datasets[0]["title"]


class TestLocationConnectorIntegration:
    """Test location parameter integration with connectors"""
    
    def test_data_gouv_client_search_with_locations(self):
        """Test DataGouv client search method accepts locations parameter"""
        client = DataGouvClient()
        
        # Verify the method accepts the locations parameter
        import inspect
        sig = inspect.signature(client.search)
        assert "locations" in sig.parameters
        assert sig.parameters["locations"].default is None
    
    @patch('ai_engine.connectors.data_gouv.requests.get')
    def test_data_gouv_client_enhanced_search(self, mock_get):
        """Test DataGouv client uses enhanced query with locations"""
        # Mock the API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": [],
            "next_page": None
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        client = DataGouvClient()
        
        # Test search with locations
        list(client.search("climate", page_size=5, locations=["Paris"]))
        
        # Verify the request was made with enhanced query
        mock_get.assert_called()
        call_args = mock_get.call_args
        assert "q" in call_args[1]["params"]
        # The query should include the location
        query = call_args[1]["params"]["q"]
        assert "climate" in query.lower()
        assert "paris" in query.lower()


class TestLocationPipelineIntegration:
    """Test location integration with the main pipeline"""
    
    def test_run_connectors_signature_accepts_locations(self):
        """Test run_connectors function accepts locations parameter"""
        from ai_engine.pipeline import run_connectors
        import inspect
        
        sig = inspect.signature(run_connectors)
        assert "locations" in sig.parameters
        assert sig.parameters["locations"].default is None