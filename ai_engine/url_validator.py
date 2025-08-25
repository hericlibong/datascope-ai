# ai_engine/url_validator.py
"""
URL Validator for LLM-generated datasource links.
Validates URLs, handles 404s, follows redirections, and reports errors.

This module is designed to be standalone and doesn't require Django or OpenAI setup.
"""

import requests
from typing import Dict, Optional, Tuple
from urllib.parse import urlparse
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ValidationStatus(Enum):
    """Status of URL validation."""
    VALID = "valid"
    NOT_FOUND = "404"
    REDIRECTED = "redirected"
    TIMEOUT = "timeout"
    CONNECTION_ERROR = "connection_error"
    INVALID_URL = "invalid_url"
    SERVER_ERROR = "server_error"


@dataclass
class ValidationResult:
    """Result of URL validation."""
    status: ValidationStatus
    final_url: Optional[str] = None
    error_message: Optional[str] = None
    status_code: Optional[int] = None
    redirected_from: Optional[str] = None


class URLValidator:
    """Validates URLs from LLM-generated sources."""
    
    def __init__(self, timeout: int = 10, max_redirects: int = 10):
        """
        Initialize URL validator.
        
        Args:
            timeout: Request timeout in seconds
            max_redirects: Maximum number of redirects to follow
        """
        self.timeout = timeout
        self.max_redirects = max_redirects
        self.session = requests.Session()
        
        # Set user agent to avoid blocking
        self.session.headers.update({
            'User-Agent': 'DataScope-AI/1.0 (+https://github.com/hericlibong/datascope-ai)'
        })
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL has valid format."""
        try:
            result = urlparse(url)
            return all([result.scheme in ('http', 'https'), result.netloc])
        except Exception:
            return False
    
    def validate_url(self, url: str) -> ValidationResult:
        """
        Validate a single URL.
        
        Args:
            url: URL to validate
            
        Returns:
            ValidationResult with status and details
        """
        if not url or not isinstance(url, str):
            return ValidationResult(
                status=ValidationStatus.INVALID_URL,
                error_message="URL is empty or not a string"
            )
        
        url = url.strip()
        if not self._is_valid_url(url):
            return ValidationResult(
                status=ValidationStatus.INVALID_URL,
                error_message="Invalid URL format"
            )
        
        try:
            response = self.session.head(
                url,
                timeout=self.timeout,
                allow_redirects=True,
                verify=True
            )
            
            final_url = response.url
            redirected = final_url != url
            
            if response.status_code == 200:
                status = ValidationStatus.REDIRECTED if redirected else ValidationStatus.VALID
                return ValidationResult(
                    status=status,
                    final_url=final_url,
                    status_code=response.status_code,
                    redirected_from=url if redirected else None
                )
            elif response.status_code == 404:
                return ValidationResult(
                    status=ValidationStatus.NOT_FOUND,
                    status_code=response.status_code,
                    error_message="Resource not found (404)"
                )
            elif response.status_code >= 500:
                return ValidationResult(
                    status=ValidationStatus.SERVER_ERROR,
                    status_code=response.status_code,
                    error_message=f"Server error ({response.status_code})"
                )
            else:
                # Other HTTP errors (403, 401, etc.)
                return ValidationResult(
                    status=ValidationStatus.VALID,  # Consider accessible but with restrictions
                    final_url=final_url,
                    status_code=response.status_code,
                    redirected_from=url if redirected else None
                )
                
        except requests.exceptions.Timeout:
            return ValidationResult(
                status=ValidationStatus.TIMEOUT,
                error_message=f"Request timeout after {self.timeout} seconds"
            )
        except requests.exceptions.ConnectionError as e:
            return ValidationResult(
                status=ValidationStatus.CONNECTION_ERROR,
                error_message=f"Connection error: {str(e)}"
            )
        except requests.exceptions.TooManyRedirects:
            return ValidationResult(
                status=ValidationStatus.CONNECTION_ERROR,
                error_message="Too many redirects"
            )
        except Exception as e:
            logger.exception(f"Unexpected error validating URL {url}")
            return ValidationResult(
                status=ValidationStatus.CONNECTION_ERROR,
                error_message=f"Unexpected error: {str(e)}"
            )
    
    def validate_urls(self, urls: list[str]) -> Dict[str, ValidationResult]:
        """
        Validate multiple URLs.
        
        Args:
            urls: List of URLs to validate
            
        Returns:
            Dictionary mapping URLs to ValidationResult
        """
        results = {}
        for url in urls:
            results[url] = self.validate_url(url)
        return results
    
    def is_url_accessible(self, url: str) -> bool:
        """
        Quick check if URL is accessible (returns True for valid, redirected, or accessible with restrictions).
        
        Args:
            url: URL to check
            
        Returns:
            True if URL is accessible, False otherwise
        """
        result = self.validate_url(url)
        return result.status in (ValidationStatus.VALID, ValidationStatus.REDIRECTED)


# Global validator instance
_validator = None


def get_validator() -> URLValidator:
    """Get the global URL validator instance."""
    global _validator
    if _validator is None:
        _validator = URLValidator()
    return _validator


def validate_url(url: str) -> ValidationResult:
    """Convenience function to validate a single URL."""
    return get_validator().validate_url(url)


def is_url_accessible(url: str) -> bool:
    """Convenience function to check if URL is accessible."""
    return get_validator().is_url_accessible(url)