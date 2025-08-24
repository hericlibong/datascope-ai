"""
Simple test script for basic playground functionality without requiring API keys.
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from playground_debug_mode.config import DebugConfig, print_debug_info
from playground_debug_mode.debug_utils import setup_debug_logging, DebugLogger


def test_basic_functionality():
    """Test basic functionality without requiring API keys."""
    print("🧪 Testing basic playground functionality...")
    
    # Test configuration
    print("\n1. Testing configuration...")
    try:
        DebugConfig.setup_directories()
        env_status = DebugConfig.check_environment()
        print(f"   ✅ Configuration loaded")
        print(f"   📁 Logs dir: {DebugConfig.LOGS_DIR}")
        print(f"   📁 Output dir: {DebugConfig.OUTPUT_DIR}")
    except Exception as e:
        print(f"   ❌ Configuration failed: {e}")
        return False
    
    # Test logging
    print("\n2. Testing debug logging...")
    try:
        logger = setup_debug_logging()
        logger.log_step("TEST_STEP", {"test": "data"})
        logger.log_timing("test_operation", 1.23)
        logger.log_result("test_result", "success")
        print("   ✅ Debug logging works")
    except Exception as e:
        print(f"   ❌ Debug logging failed: {e}")
        return False
    
    # Test environment status
    print("\n3. Testing environment status...")
    try:
        env_status = DebugConfig.check_environment()
        print(f"   📍 Required missing: {env_status['required_missing']}")
        print(f"   📍 Optional missing: {env_status['optional_missing']}")
        print(f"   📍 Available: {list(env_status['available'].keys())}")
        if env_status['warnings']:
            print(f"   ⚠️  Warnings: {len(env_status['warnings'])}")
        print("   ✅ Environment status check works")
    except Exception as e:
        print(f"   ❌ Environment status failed: {e}")
        return False
    
    # Test directory creation
    print("\n4. Testing file operations...")
    try:
        log_file = DebugConfig.create_log_file("test")
        output_file = DebugConfig.create_output_file("test", "txt")
        print(f"   📄 Test log file: {Path(log_file).name}")
        print(f"   📄 Test output file: {Path(output_file).name}")
        print("   ✅ File operations work")
    except Exception as e:
        print(f"   ❌ File operations failed: {e}")
        return False
    
    return True


def main():
    """Main test function."""
    print("🎮 Playground Debug Mode - Basic Test")
    print("=" * 50)
    
    success = test_basic_functionality()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ All basic tests passed!")
        print("\n📋 Next steps:")
        print("   1. Set OPENAI_API_KEY environment variable")
        print("   2. Run: python playground_debug_mode/run_debug.py --scenario config")
        print("   3. Run: python playground_debug_mode/run_debug.py --scenario basic")
    else:
        print("❌ Some tests failed!")
    
    # Show configuration info regardless
    print("\n" + "=" * 50)
    print("📊 Configuration Information:")
    print_debug_info()


if __name__ == "__main__":
    main()