"""
Debug playground for testing the DataScope AI chain with enhanced logging.

This module provides utilities for testing and debugging the AI pipeline
with detailed logging and tracing capabilities.
"""

from .debug_utils import setup_debug_logging, DebugLogger

# Conditional import of DebugPipeline to avoid API key requirements
def get_debug_pipeline(log_file=None):
    """Get DebugPipeline instance with conditional imports."""
    from .debug_pipeline import DebugPipeline
    return DebugPipeline(log_file)

__all__ = ["setup_debug_logging", "DebugLogger", "get_debug_pipeline"]