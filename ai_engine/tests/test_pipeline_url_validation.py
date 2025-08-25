# ai_engine/tests/test_pipeline_url_validation.py
import pytest
import responses
from unittest.mock import patch, MagicMock
from ai_engine.schemas import LLMSourceSuggestion, DatasetSuggestion
from ai_engine.url_validator import ValidationStatus


# Create a minimal test for pipeline integration without full Django setup
def test_llm_to_ds_url_validation():
    """Test that _llm_to_ds function integrates URL validation."""
    # Mock the URL validation to avoid network calls
    with patch('ai_engine.pipeline.validate_url') as mock_validate:
        # Setup mock return value
        mock_result = MagicMock()
        mock_result.status.value = "valid"
        mock_result.final_url = "https://example.com/dataset"
        mock_result.error_message = None
        mock_validate.return_value = mock_result
        
        # Import after patching to avoid environment variable issues
        from ai_engine.pipeline import _llm_to_ds
        
        # Create test input
        llm_suggestion = LLMSourceSuggestion(
            title="Test Dataset",
            description="A test dataset",
            link="https://example.com/dataset",
            source="Test Source",
            angle_idx=0
        )
        
        # Call the function
        result = _llm_to_ds(llm_suggestion, angle_idx=0)
        
        # Verify the result
        assert isinstance(result, DatasetSuggestion)
        assert result.title == "Test Dataset"
        assert result.source_url == "https://example.com/dataset"
        assert result.found_by == "LLM"
        assert result.url_validation_status == "valid"
        assert result.url_validation_error is None
        
        # Verify URL validation was called
        mock_validate.assert_called_once_with("https://example.com/dataset")


def test_llm_to_ds_url_validation_with_redirect():
    """Test _llm_to_ds with URL redirection."""
    with patch('ai_engine.pipeline.validate_url') as mock_validate:
        # Setup mock return value for redirect
        mock_result = MagicMock()
        mock_result.status.value = "redirected"
        mock_result.final_url = "https://example.com/new-dataset"
        mock_result.error_message = None
        mock_validate.return_value = mock_result
        
        from ai_engine.pipeline import _llm_to_ds
        
        llm_suggestion = LLMSourceSuggestion(
            title="Test Dataset",
            description="A test dataset",
            link="https://example.com/old-dataset",
            source="Test Source",
            angle_idx=0
        )
        
        result = _llm_to_ds(llm_suggestion, angle_idx=0)
        
        # Should use the final URL after redirect
        assert result.source_url == "https://example.com/new-dataset"
        assert result.url_validation_status == "redirected"
        assert result.final_url == "https://example.com/new-dataset"


def test_llm_to_ds_url_validation_with_error():
    """Test _llm_to_ds with URL validation error."""
    with patch('ai_engine.pipeline.validate_url') as mock_validate:
        # Setup mock return value for error
        mock_result = MagicMock()
        mock_result.status.value = "404"
        mock_result.final_url = None
        mock_result.error_message = "Resource not found (404)"
        mock_validate.return_value = mock_result
        
        from ai_engine.pipeline import _llm_to_ds
        
        llm_suggestion = LLMSourceSuggestion(
            title="Missing Dataset",
            description="A missing dataset",
            link="https://example.com/missing",
            source="Test Source",
            angle_idx=0
        )
        
        result = _llm_to_ds(llm_suggestion, angle_idx=0)
        
        # Should keep original URL but record the error
        assert result.source_url == "https://example.com/missing"
        assert result.url_validation_status == "404"
        assert result.url_validation_error == "Resource not found (404)"
        assert result.final_url is None