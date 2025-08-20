from langchain.callbacks import StdOutCallbackHandler
from langchain_core.callbacks import BaseCallbackHandler
from typing import Any, Dict, List, Optional
import logging


class DebugCallbackHandler(BaseCallbackHandler):
    """Enhanced callback handler for debug logging."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        super().__init__()
        self.logger = logger or logging.getLogger("langchain_debug")
    
    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        """Run when LLM starts running."""
        self.logger.debug(f"🤖 LLM Start: {serialized.get('name', 'Unknown')}")
        for i, prompt in enumerate(prompts):
            prompt_preview = prompt[:100] + "..." if len(prompt) > 100 else prompt
            self.logger.debug(f"📝 Prompt {i}: {prompt_preview}")
    
    def on_llm_end(self, response: Any, **kwargs: Any) -> None:
        """Run when LLM ends running."""
        self.logger.debug(f"✅ LLM End: Response received")
    
    def on_llm_error(
        self, error: Exception, **kwargs: Any
    ) -> None:
        """Run when LLM errors."""
        self.logger.error(f"❌ LLM Error: {error}")
    
    def on_chain_start(
        self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any
    ) -> None:
        """Run when chain starts running."""
        chain_name = serialized.get('name', 'Unknown Chain')
        self.logger.debug(f"🔗 Chain Start: {chain_name}")
    
    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        """Run when chain ends running."""
        self.logger.debug(f"✅ Chain End: Outputs received")
    
    def on_chain_error(
        self, error: Exception, **kwargs: Any
    ) -> None:
        """Run when chain errors."""
        self.logger.error(f"❌ Chain Error: {error}")


def with_tracing(config_name="default", debug_logger: Optional[logging.Logger] = None):
    """
    Create tracing configuration for LangChain operations.
    
    Args:
        config_name: Name for this tracing configuration
        debug_logger: Optional logger for debug output
        
    Returns:
        Dictionary with callbacks for LangChain
    """
    handlers = [StdOutCallbackHandler()]
    
    if debug_logger:
        handlers.append(DebugCallbackHandler(debug_logger))
    
    return {
        "callbacks": handlers,
        "run_name": config_name
    }


def with_debug_tracing(logger: logging.Logger, config_name="debug"):
    """
    Create enhanced debug tracing configuration.
    
    Args:
        logger: Logger instance for debug output
        config_name: Name for this tracing configuration
        
    Returns:
        Dictionary with enhanced debug callbacks
    """
    return {
        "callbacks": [DebugCallbackHandler(logger)],
        "run_name": config_name
    }
