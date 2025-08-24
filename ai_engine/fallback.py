"""
ai_engine.fallback
~~~~~~~~~~~~~~~~~

Fallback strategy implementation for DataScope AI.

Provides validation, quality assessment and fallback mechanisms for:
- LLM dataset suggestions with broken/invalid links
- Inconsistent or malformed LLM responses
- Connector failures with intelligent failover

Strategy:
1. Validate LLM suggestions (URL checks, required fields)
2. Assess quality of LLM results  
3. Fallback to connectors when LLM quality is poor
4. Intelligent connector failover on individual failures
"""

import logging
import re
from typing import List, Optional, Tuple
from urllib.parse import urlparse

import httpx

from ai_engine.schemas import DatasetSuggestion, LLMSourceSuggestion

logger = logging.getLogger("ai_engine.fallback")

# URL patterns for known data portals
TRUSTED_DOMAINS = {
    "data.gouv.fr",
    "data.gov", 
    "open.canada.ca",
    "data.gov.uk",
    "data.humdata.org",
    "eurostat.ec.europa.eu",
    "datacatalog.worldbank.org",
}

# Minimum quality thresholds
MIN_SUGGESTIONS_PER_ANGLE = 2
MIN_VALID_URL_RATIO = 0.6
MIN_DESCRIPTION_LENGTH = 20


def validate_url(url: str, timeout: float = 5.0) -> Tuple[bool, Optional[str]]:
    """
    Validate if a URL is reachable and returns a proper response.
    
    Args:
        url: URL to validate
        timeout: Request timeout in seconds
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not url or not isinstance(url, str):
        return False, "Empty or invalid URL"
        
    # Basic URL format validation
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False, "Invalid URL format"
    except Exception as e:
        return False, f"URL parsing error: {e}"
    
    # Check for trusted domains (skip HTTP check for known good domains)
    domain = parsed.netloc.lower()
    if any(trusted in domain for trusted in TRUSTED_DOMAINS):
        return True, None
    
    # For unknown domains, do a quick HTTP check
    try:
        with httpx.Client(timeout=timeout) as client:
            response = client.head(url, follow_redirects=True)
            if response.status_code < 400:
                return True, None
            else:
                return False, f"HTTP {response.status_code}"
    except httpx.TimeoutException:
        return False, "Request timeout"
    except Exception as e:
        return False, f"Connection error: {e}"


def validate_llm_suggestion(suggestion: LLMSourceSuggestion) -> Tuple[bool, List[str]]:
    """
    Validate an individual LLM dataset suggestion.
    
    Args:
        suggestion: LLM suggestion to validate
        
    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues = []
    
    # Check required fields
    if not suggestion.title or len(suggestion.title.strip()) < 3:
        issues.append("Missing or too short title")
        
    if not suggestion.description or len(suggestion.description.strip()) < MIN_DESCRIPTION_LENGTH:
        issues.append(f"Missing or too short description (< {MIN_DESCRIPTION_LENGTH} chars)")
        
    if not suggestion.link:
        issues.append("Missing link")
    else:
        # Validate URL format and accessibility
        is_valid_url, url_error = validate_url(suggestion.link)
        if not is_valid_url:
            issues.append(f"Invalid or unreachable URL: {url_error}")
            
    if not suggestion.source or len(suggestion.source.strip()) < 3:
        issues.append("Missing or too short source")
    
    return len(issues) == 0, issues


def assess_llm_quality(suggestions_per_angle: List[List[LLMSourceSuggestion]]) -> Tuple[float, dict]:
    """
    Assess the overall quality of LLM suggestions across all angles.
    
    Args:
        suggestions_per_angle: List of suggestion lists, one per angle
        
    Returns:
        Tuple of (quality_score, quality_details)
        quality_score: 0.0 to 1.0 (higher is better)
        quality_details: Dictionary with assessment details
    """
    total_suggestions = 0
    valid_suggestions = 0
    total_issues = []
    angle_qualities = []
    
    for angle_idx, suggestions in enumerate(suggestions_per_angle):
        angle_issues = []
        angle_valid = 0
        
        if len(suggestions) < MIN_SUGGESTIONS_PER_ANGLE:
            angle_issues.append(f"Too few suggestions ({len(suggestions)} < {MIN_SUGGESTIONS_PER_ANGLE})")
        
        for suggestion in suggestions:
            total_suggestions += 1
            is_valid, issues = validate_llm_suggestion(suggestion)
            
            if is_valid:
                valid_suggestions += 1
                angle_valid += 1
            else:
                angle_issues.extend([f"Suggestion '{suggestion.title[:30]}...': {issue}" for issue in issues])
                
        angle_quality = angle_valid / max(len(suggestions), 1)
        angle_qualities.append(angle_quality)
        total_issues.extend([f"Angle {angle_idx}: {issue}" for issue in angle_issues])
    
    # Calculate overall quality score
    if total_suggestions == 0:
        overall_quality = 0.0
    else:
        valid_ratio = valid_suggestions / total_suggestions
        avg_angle_quality = sum(angle_qualities) / max(len(angle_qualities), 1)
        sufficient_suggestions = all(len(suggs) >= MIN_SUGGESTIONS_PER_ANGLE for suggs in suggestions_per_angle)
        
        # Combine factors for overall score
        overall_quality = (valid_ratio * 0.6 + avg_angle_quality * 0.3 + (1.0 if sufficient_suggestions else 0.0) * 0.1)
    
    quality_details = {
        "total_suggestions": total_suggestions,
        "valid_suggestions": valid_suggestions, 
        "valid_ratio": valid_suggestions / max(total_suggestions, 1),
        "angle_qualities": angle_qualities,
        "issues": total_issues,
        "sufficient_per_angle": all(len(suggs) >= MIN_SUGGESTIONS_PER_ANGLE for suggs in suggestions_per_angle)
    }
    
    return overall_quality, quality_details


def should_fallback_to_connectors(quality_score: float, quality_details: dict) -> Tuple[bool, str]:
    """
    Determine if we should fallback to connectors based on LLM quality.
    
    Args:
        quality_score: Quality score from assess_llm_quality
        quality_details: Quality details from assess_llm_quality
        
    Returns:
        Tuple of (should_fallback, reason)
    """
    # Fallback thresholds
    MIN_QUALITY_THRESHOLD = 0.5
    MIN_VALID_RATIO_THRESHOLD = 0.4
    
    if quality_score < MIN_QUALITY_THRESHOLD:
        return True, f"Overall quality too low ({quality_score:.2f} < {MIN_QUALITY_THRESHOLD})"
        
    if quality_details["valid_ratio"] < MIN_VALID_RATIO_THRESHOLD:
        return True, f"Too many invalid suggestions ({quality_details['valid_ratio']:.2f} < {MIN_VALID_RATIO_THRESHOLD})"
        
    if not quality_details["sufficient_per_angle"]:
        return True, "Insufficient suggestions per angle"
        
    return False, "Quality acceptable"


def log_fallback_decision(should_fallback: bool, reason: str, quality_details: dict):
    """Log the fallback decision with relevant details."""
    if should_fallback:
        logger.warning(f"LLM fallback triggered: {reason}")
        logger.warning(f"Quality details: {quality_details['valid_suggestions']}/{quality_details['total_suggestions']} valid, issues: {len(quality_details['issues'])}")
        for issue in quality_details['issues'][:5]:  # Log first 5 issues
            logger.warning(f"  - {issue}")
    else:
        logger.info(f"LLM quality acceptable: {reason}")
        logger.debug(f"Quality score: {quality_details['valid_suggestions']}/{quality_details['total_suggestions']} valid")