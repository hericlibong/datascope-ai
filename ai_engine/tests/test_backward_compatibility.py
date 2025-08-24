"""
Test backward compatibility - connectors work without locations
"""

import pytest
from unittest.mock import Mock, patch

from ai_engine.connectors.data_gouv import DataGouvClient


class TestBackwardCompatibility:
    """Test that connectors work with and without location parameters"""
    
    @patch('ai_engine.connectors.data_gouv.requests.get')
    def test_connector_works_without_locations(self, mock_get):
        """Test connector works with just keyword (backward compatibility)"""
        # Mock the API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": [],
            "next_page": None
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        client = DataGouvClient()
        
        # Test search without locations (original behavior)
        list(client.search("climate", page_size=5))
        
        # Verify the request was made
        mock_get.assert_called()
        call_args = mock_get.call_args
        assert "q" in call_args[1]["params"]
    
    @patch('ai_engine.connectors.data_gouv.requests.get')
    def test_connector_works_with_none_locations(self, mock_get):
        """Test connector works with explicit None locations"""
        # Mock the API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": [],
            "next_page": None
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        client = DataGouvClient()
        
        # Test search with explicit None locations
        list(client.search("climate", page_size=5, locations=None))
        
        # Verify the request was made
        mock_get.assert_called()
        call_args = mock_get.call_args
        assert "q" in call_args[1]["params"]
    
    @patch('ai_engine.connectors.data_gouv.requests.get')
    def test_connector_works_with_empty_locations(self, mock_get):
        """Test connector works with empty locations list"""
        # Mock the API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": [],
            "next_page": None
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        client = DataGouvClient()
        
        # Test search with empty locations list
        list(client.search("climate", page_size=5, locations=[]))
        
        # Verify the request was made
        mock_get.assert_called()
        call_args = mock_get.call_args
        assert "q" in call_args[1]["params"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])