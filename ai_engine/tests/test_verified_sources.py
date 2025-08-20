# ai_engine/tests/test_verified_sources.py
"""Tests for the LLM Assistant verified sources functionality."""

import pytest
from unittest.mock import patch, MagicMock
from ai_engine.assistant.verified_sources import get_assistant_info
from ai_engine.schemas import AngleResult, Angle, VerifiedSource


@pytest.fixture
def sample_angle_result():
    """Sample angle result for testing."""
    return AngleResult(
        language="fr",
        angles=[
            Angle(
                title="Impact du changement climatique sur l'agriculture",
                rationale="Analyser les effets du réchauffement climatique sur les rendements agricoles en France."
            ),
            Angle(
                title="Politiques d'adaptation climatique",
                rationale="Examiner les mesures gouvernementales pour s'adapter au changement climatique."
            )
        ]
    )


def test_get_assistant_info():
    """Test that assistant info is returned correctly."""
    info = get_assistant_info()
    
    assert "model" in info
    assert "temperature" in info
    assert "max_tokens" in info
    assert "model_config" in info
    assert "available_models" in info
    
    # Check that available models contain expected keys
    assert "gpt-4o-mini" in info["available_models"]
    assert info["available_models"]["gpt-4o-mini"]["provider"] == "openai"


def test_verified_source_schema():
    """Test that VerifiedSource schema works correctly."""
    source = VerifiedSource(
        title="Test Report",
        description="A test report for validation",
        link="https://example.com/report",
        source="Test Organization",
        source_type="report",
        credibility_score=8,
        publication_date="2024",
        language="fr",
        angle_idx=0
    )
    
    assert source.title == "Test Report"
    assert source.credibility_score == 8
    assert source.source_type == "report"
    assert source.angle_idx == 0


def test_verified_source_schema_defaults():
    """Test that VerifiedSource schema defaults work correctly."""
    source = VerifiedSource(
        title="Test Report",
        description="A test report",
        link="https://example.com",
        source="Test Org",
        source_type="report",
        angle_idx=0
    )
    
    # Check defaults
    assert source.credibility_score == 5  # default value
    assert source.language == "fr"  # default value
    assert source.publication_date is None  # optional field


def test_verified_source_credibility_validation():
    """Test that credibility score validation works."""
    # Valid scores
    for score in [1, 5, 10]:
        source = VerifiedSource(
            title="Test",
            description="Test",
            link="https://example.com",
            source="Test",
            source_type="report",
            credibility_score=score,
            angle_idx=0
        )
        assert source.credibility_score == score


def test_verified_source_types():
    """Test different source types are supported."""
    valid_types = ['report', 'article', 'study', 'documentation', 'official']
    
    for source_type in valid_types:
        source = VerifiedSource(
            title="Test",
            description="Test",
            link="https://example.com",
            source="Test",
            source_type=source_type,
            angle_idx=0
        )
        assert source.source_type == source_type


@patch('ai_engine.assistant.verified_sources.llm_retry')
def test_verified_sources_function_structure(mock_retry, sample_angle_result):
    """Test that the run function has the correct structure."""
    from ai_engine.assistant.verified_sources import run
    
    # Mock the decorated function to return empty results
    mock_retry.return_value = lambda *args, **kwargs: [[], []]
    
    # This tests that the function can be called with the expected parameters
    result = run(sample_angle_result)
    
    # Should return a list for each angle
    assert isinstance(result, list)
    assert len(result) == 2  # Two angles in sample data