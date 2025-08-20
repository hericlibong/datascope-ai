"""
Validation utilities for dataset suggestions and URLs.
Implements fallback strategy for inconsistent or broken LLM suggestions.
"""

import logging
import re
from typing import List, Optional
from urllib.parse import urlparse
import requests
from requests.exceptions import RequestException, Timeout

from ai_engine.schemas import LLMSourceSuggestion, DatasetSuggestion

logger = logging.getLogger("ai_engine.validation")

# URL validation timeout (seconds)
URL_VALIDATION_TIMEOUT = 5

# Basic patterns for known data portals
TRUSTED_DOMAINS = {
    'data.gouv.fr',
    'data.gov',
    'open.canada.ca',
    'data.gov.uk',
    'data.europa.eu',
    'data.humdata.org',
    'worldbank.org',
    'kaggle.com',
    'github.com',
    'figshare.com',
    'zenodo.org'
}

def is_valid_url(url: str) -> bool:
    """
    Check if URL has valid format.
    
    Args:
        url: URL string to validate
        
    Returns:
        True if URL format is valid, False otherwise
    """
    if not url or not isinstance(url, str):
        return False
        
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def is_trusted_domain(url: str) -> bool:
    """
    Check if URL belongs to a trusted data portal.
    
    Args:
        url: URL string to check
        
    Returns:
        True if domain is trusted, False otherwise
    """
    if not is_valid_url(url):
        return False
        
    try:
        domain = urlparse(url).netloc.lower()
        # Remove www. prefix
        domain = domain.replace('www.', '')
        
        # Check if domain or any parent domain is trusted
        for trusted in TRUSTED_DOMAINS:
            if domain == trusted or domain.endswith('.' + trusted):
                return True
                
        return False
    except Exception:
        return False

def is_reachable_url(url: str, timeout: int = URL_VALIDATION_TIMEOUT) -> bool:
    """
    Check if URL is reachable with HEAD request.
    
    Args:
        url: URL to check
        timeout: Request timeout in seconds
        
    Returns:
        True if URL is reachable, False otherwise
    """
    if not is_valid_url(url):
        return False
        
    try:
        # Use HEAD request to avoid downloading content
        response = requests.head(
            url, 
            timeout=timeout,
            allow_redirects=True,
            headers={'User-Agent': 'DataScope-AI/1.0'}
        )
        return response.status_code < 400
    except (RequestException, Timeout):
        return False
    except Exception as e:
        logger.warning(f"Unexpected error checking URL {url}: {e}")
        return False

def validate_llm_suggestion(suggestion: LLMSourceSuggestion) -> tuple[bool, List[str]]:
    """
    Validate an LLM source suggestion for consistency and quality.
    
    Args:
        suggestion: LLM source suggestion to validate
        
    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues = []
    
    # Check required fields
    if not suggestion.title or len(suggestion.title.strip()) < 3:
        issues.append("Title missing or too short")
        
    if not suggestion.description or len(suggestion.description.strip()) < 10:
        issues.append("Description missing or too short")
        
    if not suggestion.source or len(suggestion.source.strip()) < 3:
        issues.append("Source missing or too short")
        
    # Validate URL
    if not suggestion.link:
        issues.append("Link missing")
    elif not is_valid_url(suggestion.link):
        issues.append("Link has invalid format")
    
    # Check for obviously fake or placeholder content
    title_lower = (suggestion.title or "").lower()
    desc_lower = (suggestion.description or "").lower()
    
    suspicious_patterns = [
        'placeholder', 'example', 'sample', 'test', 'dummy',
        'lorem ipsum', 'fake', 'mock', 'xxx', 'todo'
    ]
    
    for pattern in suspicious_patterns:
        if pattern in title_lower or pattern in desc_lower:
            issues.append(f"Contains suspicious content: {pattern}")
            break
    
    # Check if title and description are too similar (possible duplication)
    if suggestion.title and suggestion.description:
        title_words = set(suggestion.title.lower().split())
        desc_words = set(suggestion.description.lower().split())
        if len(title_words) > 3 and len(desc_words) > 3:
            overlap = len(title_words & desc_words) / min(len(title_words), len(desc_words))
            if overlap > 0.8:
                issues.append("Title and description are too similar")
    
    return len(issues) == 0, issues

def validate_and_filter_llm_suggestions(
    suggestions: List[LLMSourceSuggestion],
    check_urls: bool = False
) -> tuple[List[LLMSourceSuggestion], List[LLMSourceSuggestion]]:
    """
    Validate and filter LLM suggestions, separating valid from invalid ones.
    
    Args:
        suggestions: List of LLM suggestions to validate
        check_urls: Whether to perform URL reachability checks (slower)
        
    Returns:
        Tuple of (valid_suggestions, invalid_suggestions)
    """
    valid = []
    invalid = []
    
    for suggestion in suggestions:
        is_valid, issues = validate_llm_suggestion(suggestion)
        
        # Additional URL check if requested
        if is_valid and check_urls and suggestion.link:
            if not is_reachable_url(suggestion.link):
                is_valid = False
                issues.append("URL is not reachable")
        
        if is_valid:
            valid.append(suggestion)
        else:
            invalid.append(suggestion)
            logger.debug(f"Invalid LLM suggestion '{suggestion.title}': {', '.join(issues)}")
    
    if invalid:
        logger.info(f"Filtered out {len(invalid)} invalid LLM suggestions out of {len(suggestions)}")
    
    return valid, invalid

def enhance_dataset_suggestion_reliability(ds: DatasetSuggestion) -> DatasetSuggestion:
    """
    Enhance a dataset suggestion with reliability indicators.
    
    Args:
        ds: Dataset suggestion to enhance
        
    Returns:
        Enhanced dataset suggestion with reliability score
    """
    # Calculate reliability score based on various factors
    reliability_score = 0
    
    # URL validation
    if ds.source_url:
        if is_valid_url(ds.source_url):
            reliability_score += 20
            if is_trusted_domain(ds.source_url):
                reliability_score += 30
        
    # Content quality indicators
    if ds.title and len(ds.title) > 10:
        reliability_score += 15
    
    if ds.description and len(ds.description) > 50:
        reliability_score += 15
    
    if ds.source_name:
        reliability_score += 10
    
    if ds.formats:
        reliability_score += 5
    
    if ds.organization:
        reliability_score += 5
    
    # Cap at 100
    reliability_score = min(reliability_score, 100)
    
    # Update richness with reliability score
    ds.richness = max(ds.richness or 0, reliability_score)
    
    return ds