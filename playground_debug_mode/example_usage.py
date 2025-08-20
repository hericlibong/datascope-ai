"""
Example script showing how to use the playground with API key.

This is for demonstration purposes only.
"""

import os
import sys
from pathlib import Path

# This would be set as an environment variable in production
# os.environ['OPENAI_API_KEY'] = 'your-api-key-here'
# os.environ['SECRET_KEY'] = 'your-django-secret-key-here'

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def demo_with_mock_key():
    """Demonstrate what the playground would look like with API keys."""
    print("🎮 DataScope AI Debug Playground - Example Usage")
    print("=" * 60)
    
    # Check if API key is actually set
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  This is a demo - no actual API key is set")
        print()
        print("📋 If you had an API key set, you could run:")
        print()
        print("1. Configuration check:")
        print("   python playground_debug_mode/run_debug.py --scenario config")
        print()
        print("2. Basic pipeline test:")
        print("   python playground_debug_mode/run_debug.py --scenario basic --article short_politics")
        print()
        print("3. Step-by-step debugging:")
        print("   python playground_debug_mode/run_debug.py --scenario step-by-step --article tech_article --stop-after extraction")
        print()
        print("4. All scenarios:")
        print("   python playground_debug_mode/run_debug.py --scenario all")
        print()
        print("📝 Sample articles available:")
        print("   - short_politics: Article politique court")
        print("   - tech_article: Article sur la technologie")
        print("   - climate_article: Article sur le climat")
        print("   - economic_article: Article économique")
        print()
        print("🔧 Debug features:")
        print("   - Detailed step-by-step logging")
        print("   - Performance timing for each step")
        print("   - Error tracking with full tracebacks")
        print("   - Intermediate result inspection")
        print("   - LangChain callback tracing")
        print()
        print("📁 Output directories:")
        print("   - logs/: Debug logs with timestamps")
        print("   - output/: Intermediate results and analysis")
        return
    
    # If API key is set, show actual functionality
    try:
        from playground_debug_mode.test_scenarios import TestScenarios
        
        print("✅ API key detected! Running quick demo...")
        
        scenarios = TestScenarios()
        print("\n🧪 Running basic test...")
        result = scenarios.run_basic_test("short_politics")
        
        if result:
            print("✅ Demo completed successfully!")
        else:
            print("❌ Demo encountered issues")
            
    except Exception as e:
        print(f"❌ Error during demo: {e}")


if __name__ == "__main__":
    demo_with_mock_key()