# ai_engine/tests/test_assistant_integration.py
"""Integration tests for the LLM Assistant in the pipeline."""

import pytest
from unittest.mock import patch, MagicMock
from ai_engine.schemas import AngleResult, Angle, VerifiedSource


def test_pipeline_imports_verified_sources():
    """Test that the pipeline can import the verified sources module."""
    try:
        from ai_engine.assistant import verified_sources
        from ai_engine.pipeline import run
        assert verified_sources is not None
        assert run is not None
    except ImportError as e:
        pytest.fail(f"Failed to import verified sources: {e}")


def test_verified_source_in_schema():
    """Test that VerifiedSource is properly defined in schemas."""
    from ai_engine.schemas import VerifiedSource, AngleResources
    
    # Test creating a VerifiedSource
    source = VerifiedSource(
        title="Test Source",
        description="Test description",
        link="https://example.com",
        source="Test Org",
        source_type="report",
        angle_idx=0
    )
    
    # Test that AngleResources accepts verified_sources
    resources = AngleResources(
        index=0,
        title="Test Angle",
        description="Test description",
        keywords=["test"],
        datasets=[],
        sources=[],
        verified_sources=[source],
        visualizations=[]
    )
    
    assert len(resources.verified_sources) == 1
    assert resources.verified_sources[0].title == "Test Source"


def test_assistant_configuration():
    """Test that assistant configuration is available."""
    import ai_engine
    
    # Test that assistant configuration variables exist
    assert hasattr(ai_engine, 'ASSISTANT_MODEL')
    assert hasattr(ai_engine, 'ASSISTANT_TEMPERATURE')
    assert hasattr(ai_engine, 'ASSISTANT_MAX_TOKENS')
    assert hasattr(ai_engine, 'AVAILABLE_MODELS')
    assert hasattr(ai_engine, 'get_model_config')
    
    # Test get_model_config function
    config = ai_engine.get_model_config()
    assert isinstance(config, dict)
    assert "provider" in config
    
    # Test with specific model
    config_specific = ai_engine.get_model_config("gpt-4o-mini")
    assert config_specific["provider"] == "openai"


def test_available_models_structure():
    """Test that available models have the expected structure."""
    import ai_engine
    
    for model_name, config in ai_engine.AVAILABLE_MODELS.items():
        assert isinstance(model_name, str)
        assert isinstance(config, dict)
        assert "provider" in config
        assert "cost" in config
        assert "speed" in config


def test_pipeline_imports_verified_sources_module():
    """Test that the pipeline properly imports the verified sources module."""
    import ai_engine.pipeline
    
    # Check that the import exists in the pipeline module
    pipeline_source = ai_engine.pipeline.__file__
    with open(pipeline_source, 'r') as f:
        content = f.read()
        assert 'from ai_engine.assistant import verified_sources' in content
        
    # Check that verified_sources is used in the pipeline
    assert 'verified_sources.run' in content