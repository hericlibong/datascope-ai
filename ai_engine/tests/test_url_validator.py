# ai_engine/tests/test_url_validator.py
import pytest
import responses
from unittest.mock import patch
from ai_engine.url_validator import URLValidator, ValidationStatus, ValidationResult, validate_url, is_url_accessible


class TestURLValidator:
    """Tests for the URL validator."""
    
    def test_validator_initialization(self):
        """Test validator can be initialized with custom settings."""
        validator = URLValidator(timeout=5, max_redirects=5)
        assert validator.timeout == 5
        assert validator.max_redirects == 5
    
    def test_invalid_url_format(self):
        """Test validation of invalid URL formats."""
        validator = URLValidator()
        
        # Test empty URL
        result = validator.validate_url("")
        assert result.status == ValidationStatus.INVALID_URL
        assert "empty" in result.error_message.lower()
        
        # Test invalid URL format
        result = validator.validate_url("not-a-url")
        assert result.status == ValidationStatus.INVALID_URL
        assert "invalid url format" in result.error_message.lower()
        
        # Test URL without scheme
        result = validator.validate_url("example.com")
        assert result.status == ValidationStatus.INVALID_URL
    
    @responses.activate
    def test_valid_url_200(self):
        """Test validation of valid URL returning 200."""
        responses.add(
            responses.HEAD,
            "https://example.com/dataset",
            status=200
        )
        
        validator = URLValidator()
        result = validator.validate_url("https://example.com/dataset")
        
        assert result.status == ValidationStatus.VALID
        assert result.final_url == "https://example.com/dataset"
        assert result.status_code == 200
        assert result.error_message is None
    
    @responses.activate
    def test_url_404(self):
        """Test validation of URL returning 404."""
        responses.add(
            responses.HEAD,
            "https://example.com/missing",
            status=404
        )
        
        validator = URLValidator()
        result = validator.validate_url("https://example.com/missing")
        
        assert result.status == ValidationStatus.NOT_FOUND
        assert result.status_code == 404
        assert "404" in result.error_message
    
    @responses.activate
    def test_url_redirect(self):
        """Test validation of URL with redirects."""
        # Add redirect chain
        responses.add(
            responses.HEAD,
            "https://example.com/old",
            status=301,
            headers={"Location": "https://example.com/new"}
        )
        responses.add(
            responses.HEAD,
            "https://example.com/new",
            status=200
        )
        
        validator = URLValidator()
        result = validator.validate_url("https://example.com/old")
        
        assert result.status == ValidationStatus.REDIRECTED
        assert result.final_url == "https://example.com/new"
        assert result.redirected_from == "https://example.com/old"
        assert result.status_code == 200
    
    @responses.activate
    def test_url_server_error(self):
        """Test validation of URL returning server error."""
        responses.add(
            responses.HEAD,
            "https://example.com/error",
            status=500
        )
        
        validator = URLValidator()
        result = validator.validate_url("https://example.com/error")
        
        assert result.status == ValidationStatus.SERVER_ERROR
        assert result.status_code == 500
        assert "server error" in result.error_message.lower()
    
    @responses.activate
    def test_url_connection_timeout(self):
        """Test validation of URL with timeout."""
        responses.add(
            responses.HEAD,
            "https://example.com/slow",
            body=responses.ConnectionError("Timeout")
        )
        
        validator = URLValidator()
        result = validator.validate_url("https://example.com/slow")
        
        assert result.status == ValidationStatus.CONNECTION_ERROR
        assert "connection error" in result.error_message.lower()
    
    @responses.activate
    def test_url_other_status_codes(self):
        """Test validation of URL with other status codes (403, 401, etc.)."""
        responses.add(
            responses.HEAD,
            "https://example.com/restricted",
            status=403
        )
        
        validator = URLValidator()
        result = validator.validate_url("https://example.com/restricted")
        
        # Should still be considered valid but with restrictions
        assert result.status == ValidationStatus.VALID
        assert result.status_code == 403
        assert result.final_url == "https://example.com/restricted"
    
    @responses.activate
    def test_validate_multiple_urls(self):
        """Test validation of multiple URLs."""
        responses.add(responses.HEAD, "https://good.com", status=200)
        responses.add(responses.HEAD, "https://missing.com", status=404)
        responses.add(responses.HEAD, "https://redirect.com", status=301, headers={"Location": "https://new.com"})
        responses.add(responses.HEAD, "https://new.com", status=200)
        
        validator = URLValidator()
        urls = ["https://good.com", "https://missing.com", "https://redirect.com", "invalid-url"]
        results = validator.validate_urls(urls)
        
        assert len(results) == 4
        assert results["https://good.com"].status == ValidationStatus.VALID
        assert results["https://missing.com"].status == ValidationStatus.NOT_FOUND
        assert results["https://redirect.com"].status == ValidationStatus.REDIRECTED
        assert results["invalid-url"].status == ValidationStatus.INVALID_URL
    
    @responses.activate
    def test_is_url_accessible(self):
        """Test the accessibility check helper."""
        responses.add(responses.HEAD, "https://accessible.com", status=200)
        responses.add(responses.HEAD, "https://missing.com", status=404)
        responses.add(responses.HEAD, "https://redirect.com", status=301, headers={"Location": "https://final.com"})
        responses.add(responses.HEAD, "https://final.com", status=200)
        
        validator = URLValidator()
        
        assert validator.is_url_accessible("https://accessible.com") is True
        assert validator.is_url_accessible("https://missing.com") is False
        assert validator.is_url_accessible("https://redirect.com") is True
        assert validator.is_url_accessible("invalid-url") is False


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    @responses.activate
    def test_validate_url_function(self):
        """Test the standalone validate_url function."""
        responses.add(responses.HEAD, "https://test.com", status=200)
        
        result = validate_url("https://test.com")
        assert result.status == ValidationStatus.VALID
    
    @responses.activate
    def test_is_url_accessible_function(self):
        """Test the standalone is_url_accessible function."""
        responses.add(responses.HEAD, "https://test.com", status=200)
        responses.add(responses.HEAD, "https://missing.com", status=404)
        
        assert is_url_accessible("https://test.com") is True
        assert is_url_accessible("https://missing.com") is False