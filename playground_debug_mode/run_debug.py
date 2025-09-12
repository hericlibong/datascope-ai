#!/usr/bin/env python3
"""
Main entry point for the DataScope AI Debug Playground.

This script provides an interactive way to test and debug the AI pipeline
with enhanced logging and tracing capabilities.
"""

import os
import sys
import argparse
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from playground_debug_mode.config import DebugConfig, print_debug_info

# Conditional import to avoid API key requirements for config display
try:
    from playground_debug_mode.test_scenarios import TestScenarios
    SCENARIOS_AVAILABLE = True
except Exception as e:
    TestScenarios = None
    SCENARIOS_AVAILABLE = False
    SCENARIOS_ERROR = str(e)


def main():
    """Main entry point for debug playground."""
    parser = argparse.ArgumentParser(description="DataScope AI Debug Playground")
    parser.add_argument("--scenario", 
                       choices=["basic", "step-by-step", "all", "config"], 
                       default="config",
                       help="Which test scenario to run")
    parser.add_argument("--article", 
                       choices=["short_politics", "tech_article", "climate_article", "economic_article"],
                       default="short_politics",
                       help="Which sample article to use")
    parser.add_argument("--stop-after", 
                       choices=["validation", "extraction", "scoring", "angles", "keywords"],
                       help="Stop step-by-step execution after this step")
    parser.add_argument("--log-file", 
                       help="Custom log file path")
    
    args = parser.parse_args()
    
    print("🎮 DataScope AI Debug Playground")
    print("=" * 50)
    
    # Setup directories
    DebugConfig.setup_directories()
    
    if args.scenario == "config":
        print_debug_info()
        return
    
    # Check if scenarios are available
    if not SCENARIOS_AVAILABLE and args.scenario != "config":
        print(f"❌ Test scenarios not available: {SCENARIOS_ERROR}")
        print("\nThis usually means OPENAI_API_KEY is not set.")
        print("Please set the required environment variables and try again.")
        return
    
    # Check environment
    env_status = DebugConfig.check_environment()
    if env_status["required_missing"]:
        print("❌ Missing required environment variables:")
        for var in env_status["required_missing"]:
            print(f"   - {var}")
        print("\nPlease set the required environment variables and try again.")
        return
    
    if env_status["warnings"]:
        print("⚠️  Warnings:")
        for warning in env_status["warnings"]:
            print(f"   - {warning}")
        print()
    
    # Create test scenarios
    try:
        scenarios = TestScenarios()
        
        if args.scenario == "basic":
            print(f"🧪 Running basic test with '{args.article}' article...")
            result = scenarios.run_basic_test(args.article)
            if result:
                print("✅ Basic test completed successfully!")
            else:
                print("❌ Basic test failed!")
        
        elif args.scenario == "step-by-step":
            print(f"🔍 Running step-by-step test with '{args.article}' article...")
            if args.stop_after:
                print(f"   (stopping after: {args.stop_after})")
            result = scenarios.run_step_by_step_test(args.article, args.stop_after)
            if result:
                print("✅ Step-by-step test completed!")
                print(f"   Steps completed: {list(result.keys())}")
            else:
                print("❌ Step-by-step test failed!")
        
        elif args.scenario == "all":
            print("🚀 Running all test scenarios...")
            results = scenarios.run_all_scenarios()
            passed = sum(results.values())
            total = len(results)
            print(f"\nFinal result: {passed}/{total} tests passed")
    
    except Exception as e:
        print(f"❌ Error running playground: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🎉 Debug playground session complete!")


if __name__ == "__main__":
    main()