"""
Debug utilities for enhanced logging and tracing in the AI pipeline.
"""

import logging
import time
import traceback
from typing import Any, Dict, Optional
from functools import wraps
from pathlib import Path
import json


class DebugLogger:
    """Enhanced logger for debugging AI pipeline steps."""
    
    def __init__(self, name: str = "debug_pipeline", log_file: Optional[str] = None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            # Console handler with detailed format
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)
            console_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)
            
            # File handler if specified
            if log_file:
                file_handler = logging.FileHandler(log_file)
                file_handler.setLevel(logging.DEBUG)
                file_formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
                )
                file_handler.setFormatter(file_formatter)
                self.logger.addHandler(file_handler)
    
    def log_step(self, step_name: str, data: Any = None, **kwargs):
        """Log a pipeline step with optional data."""
        msg = f"🔧 STEP: {step_name}"
        if data is not None:
            msg += f" | Data: {self._format_data(data)}"
        if kwargs:
            msg += f" | Extra: {kwargs}"
        self.logger.info(msg)
    
    def log_timing(self, operation: str, duration: float):
        """Log timing information."""
        self.logger.info(f"⏱️  TIMING: {operation} took {duration:.2f}s")
    
    def log_error(self, error: Exception, context: str = ""):
        """Log error with full traceback."""
        error_msg = f"❌ ERROR in {context}: {str(error)}"
        self.logger.error(error_msg)
        self.logger.error(f"Traceback:\n{traceback.format_exc()}")
    
    def log_result(self, operation: str, result: Any):
        """Log operation results."""
        self.logger.info(f"✅ RESULT: {operation} -> {self._format_data(result)}")
    
    def _format_data(self, data: Any) -> str:
        """Format data for logging, truncating if too long."""
        if hasattr(data, '__dict__'):
            # For Pydantic models or objects with __dict__
            try:
                data_str = str(data.__dict__)
            except:
                data_str = str(data)
        elif isinstance(data, (list, dict)):
            try:
                data_str = json.dumps(data, default=str, indent=2)[:500]
            except:
                data_str = str(data)[:500]
        else:
            data_str = str(data)[:500]
        
        if len(data_str) >= 500:
            data_str += "... (truncated)"
        return data_str


def setup_debug_logging(log_file: Optional[str] = None) -> DebugLogger:
    """Setup debug logging for the playground."""
    if log_file is None:
        log_dir = Path(__file__).parent / "logs"
        log_dir.mkdir(exist_ok=True)
        log_file = str(log_dir / f"debug_{int(time.time())}.log")
    
    return DebugLogger(log_file=log_file)


def debug_trace(logger: DebugLogger):
    """Decorator to trace function calls with timing."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            func_name = func.__name__
            
            logger.log_step(f"ENTER {func_name}", {"args": len(args), "kwargs": list(kwargs.keys())})
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.log_timing(func_name, duration)
                logger.log_result(func_name, result)
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.log_timing(f"{func_name} (FAILED)", duration)
                logger.log_error(e, func_name)
                raise
        
        return wrapper
    return decorator