"""
Configuration for debug playground.

This module provides configuration settings for the debug playground,
including logging levels, test settings, and debug options.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional


class DebugConfig:
    """Configuration settings for debug playground."""
    
    # Base directory for logs and output
    BASE_DIR = Path(__file__).parent
    LOGS_DIR = BASE_DIR / "logs"
    OUTPUT_DIR = BASE_DIR / "output"
    
    # Logging configuration
    LOG_LEVEL = "DEBUG"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
    CONSOLE_LOG_LEVEL = "INFO"
    
    # Debug options
    ENABLE_STEP_TIMING = True
    ENABLE_DETAILED_LOGGING = True
    SAVE_INTERMEDIATE_RESULTS = True
    TRUNCATE_LOGS_AT = 500  # characters
    
    # Test configuration
    DEFAULT_USER_ID = "debug_user"
    TEST_TIMEOUT = 60  # seconds
    
    # Environment checks
    REQUIRED_ENV_VARS = ["OPENAI_API_KEY"]
    OPTIONAL_ENV_VARS = ["OPENAI_MODEL", "DEBUG", "SECRET_KEY"]
    
    @classmethod
    def setup_directories(cls):
        """Create necessary directories for debug output."""
        cls.LOGS_DIR.mkdir(exist_ok=True)
        cls.OUTPUT_DIR.mkdir(exist_ok=True)
    
    @classmethod
    def check_environment(cls) -> Dict[str, Any]:
        """Check environment variables and return status."""
        env_status = {
            "required_missing": [],
            "optional_missing": [],
            "available": {},
            "warnings": []
        }
        
        # Check required environment variables
        for var in cls.REQUIRED_ENV_VARS:
            value = os.getenv(var)
            if value:
                env_status["available"][var] = "✓ Set"
            else:
                env_status["required_missing"].append(var)
        
        # Check optional environment variables
        for var in cls.OPTIONAL_ENV_VARS:
            value = os.getenv(var)
            if value:
                env_status["available"][var] = "✓ Set"
            else:
                env_status["optional_missing"].append(var)
        
        # Add warnings
        if "OPENAI_API_KEY" in env_status["required_missing"]:
            env_status["warnings"].append("OpenAI API key not set - AI pipeline will fail")
        
        if "SECRET_KEY" in env_status["optional_missing"]:
            env_status["warnings"].append("Django SECRET_KEY not set - Django functionality may be limited")
        
        return env_status
    
    @classmethod
    def get_debug_settings(cls) -> Dict[str, Any]:
        """Get current debug settings."""
        return {
            "base_dir": str(cls.BASE_DIR),
            "logs_dir": str(cls.LOGS_DIR),
            "output_dir": str(cls.OUTPUT_DIR),
            "log_level": cls.LOG_LEVEL,
            "enable_step_timing": cls.ENABLE_STEP_TIMING,
            "enable_detailed_logging": cls.ENABLE_DETAILED_LOGGING,
            "save_intermediate_results": cls.SAVE_INTERMEDIATE_RESULTS,
            "truncate_logs_at": cls.TRUNCATE_LOGS_AT,
            "default_user_id": cls.DEFAULT_USER_ID,
            "test_timeout": cls.TEST_TIMEOUT,
        }
    
    @classmethod
    def create_log_file(cls, prefix: str = "debug") -> str:
        """Create a new log file path."""
        import time
        cls.setup_directories()
        timestamp = int(time.time())
        return str(cls.LOGS_DIR / f"{prefix}_{timestamp}.log")
    
    @classmethod
    def create_output_file(cls, name: str, extension: str = "json") -> str:
        """Create a new output file path."""
        import time
        cls.setup_directories()
        timestamp = int(time.time())
        return str(cls.OUTPUT_DIR / f"{name}_{timestamp}.{extension}")


def print_debug_info():
    """Print debug configuration and environment information."""
    print("🔧 Debug Playground Configuration")
    print("=" * 40)
    
    # Environment status
    env_status = DebugConfig.check_environment()
    
    print("📍 Environment Variables:")
    for var, status in env_status["available"].items():
        print(f"  {var}: {status}")
    
    if env_status["required_missing"]:
        print("  ❌ Missing required:")
        for var in env_status["required_missing"]:
            print(f"    - {var}")
    
    if env_status["optional_missing"]:
        print("  ⚠️  Missing optional:")
        for var in env_status["optional_missing"]:
            print(f"    - {var}")
    
    if env_status["warnings"]:
        print("  ⚠️  Warnings:")
        for warning in env_status["warnings"]:
            print(f"    - {warning}")
    
    # Debug settings
    print("\n⚙️  Debug Settings:")
    settings = DebugConfig.get_debug_settings()
    for key, value in settings.items():
        print(f"  {key}: {value}")
    
    # Directories
    DebugConfig.setup_directories()
    print("\n📁 Directories:")
    print(f"  Logs: {DebugConfig.LOGS_DIR}")
    print(f"  Output: {DebugConfig.OUTPUT_DIR}")
    
    print("=" * 40)


if __name__ == "__main__":
    print_debug_info()