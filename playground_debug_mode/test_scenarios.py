"""
Test scenarios for the debug playground.

This module provides various test scenarios to exercise the AI pipeline
with different types of input and debugging configurations.
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from playground_debug_mode.debug_utils import setup_debug_logging

# Conditional imports to avoid API key requirements for basic functionality
try:
    from playground_debug_mode.debug_pipeline import DebugPipeline
    PIPELINE_IMPORT_ERROR = None
except Exception as e:
    DebugPipeline = None
    PIPELINE_IMPORT_ERROR = str(e)


class TestScenarios:
    """Collection of test scenarios for debugging the AI pipeline."""
    
    # Sample articles for testing
    SAMPLE_ARTICLES = {
        "short_politics": """
        Le gouvernement français a annoncé aujourd'hui de nouvelles mesures 
        pour lutter contre l'inflation. Le ministre de l'Économie Bruno Le Maire 
        a présenté un plan d'aide aux ménages les plus modestes.
        """,
        
        "tech_article": """
        OpenAI a lancé une nouvelle version de ChatGPT qui intègre des capacités 
        de raisonnement avancées. Cette technologie d'intelligence artificielle 
        promet de révolutionner les interactions homme-machine. Les entreprises 
        tech comme Microsoft et Google investissent massivement dans ce secteur.
        """,
        
        "climate_article": """
        Le rapport du GIEC publié cette semaine tire la sonnette d'alarme sur 
        le réchauffement climatique. Les scientifiques appellent à une action 
        urgente pour réduire les émissions de gaz à effet de serre. L'Organisation 
        météorologique mondiale confirme que 2023 a été l'année la plus chaude 
        jamais enregistrée.
        """,
        
        "economic_article": """
        La Banque centrale européenne a décidé de maintenir ses taux d'intérêt 
        directeurs inchangés lors de sa dernière réunion. L'inflation dans la 
        zone euro continue de ralentir, atteignant 2,4% en décembre. Les analystes 
        de Goldman Sachs anticipent une baisse des taux au premier trimestre 2024.
        """
    }
    
    def __init__(self):
        self.logger = setup_debug_logging()
        
        if DebugPipeline is None:
            self.logger.log_error(Exception(f"Pipeline import failed: {PIPELINE_IMPORT_ERROR}"), "INIT")
            self.debug_pipeline = None
        else:
            self.debug_pipeline = DebugPipeline()
    
    def run_basic_test(self, article_key: str = "short_politics"):
        """Run a basic test with one of the sample articles."""
        print(f"\n🧪 Running basic test with '{article_key}' article...")
        
        if self.debug_pipeline is None:
            print(f"❌ Pipeline not available: {PIPELINE_IMPORT_ERROR}")
            return None
        
        if article_key not in self.SAMPLE_ARTICLES:
            print(f"❌ Article '{article_key}' not found. Available: {list(self.SAMPLE_ARTICLES.keys())}")
            return None
        
        article_text = self.SAMPLE_ARTICLES[article_key].strip()
        
        try:
            result = self.debug_pipeline.run(article_text, f"test_user_{article_key}")
            print("✅ Basic test completed successfully!")
            return result
        except Exception as e:
            print(f"❌ Basic test failed: {e}")
            return None
    
    def run_step_by_step_test(self, article_key: str = "tech_article", stop_after: str = None):
        """Run step-by-step debugging test."""
        print(f"\n🔍 Running step-by-step test with '{article_key}' article...")
        
        if self.debug_pipeline is None:
            print(f"❌ Pipeline not available: {PIPELINE_IMPORT_ERROR}")
            return None
        
        if article_key not in self.SAMPLE_ARTICLES:
            print(f"❌ Article '{article_key}' not found. Available: {list(self.SAMPLE_ARTICLES.keys())}")
            return None
        
        article_text = self.SAMPLE_ARTICLES[article_key].strip()
        
        try:
            result = self.debug_pipeline.debug_step_by_step(
                article_text, 
                f"step_test_user_{article_key}",
                stop_after=stop_after
            )
            print("✅ Step-by-step test completed!")
            return result
        except Exception as e:
            print(f"❌ Step-by-step test failed: {e}")
            return None
    
    def run_all_scenarios(self):
        """Run all test scenarios."""
        print("🚀 Running all test scenarios...")
        
        results = {}
        
        # Test each article type
        for article_key in self.SAMPLE_ARTICLES.keys():
            print(f"\n{'='*50}")
            print(f"Testing with {article_key}")
            print('='*50)
            
            # Basic test
            basic_result = self.run_basic_test(article_key)
            results[f"{article_key}_basic"] = basic_result is not None
            
            # Step-by-step test (just extraction and angles)
            step_result = self.run_step_by_step_test(article_key, stop_after="angles")
            results[f"{article_key}_steps"] = step_result is not None
        
        # Summary
        print(f"\n{'='*50}")
        print("TEST SUMMARY")
        print('='*50)
        passed = sum(results.values())
        total = len(results)
        
        for test_name, passed_test in results.items():
            status = "✅ PASSED" if passed_test else "❌ FAILED"
            print(f"{test_name:30} {status}")
        
        print(f"\nOverall: {passed}/{total} tests passed")
        return results


def main():
    """Main function to run debug tests."""
    print("🎮 DataScope AI Debug Playground")
    print("================================")
    
    # Check if we have environment variables needed
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  Warning: OPENAI_API_KEY not set. Some tests may fail.")
    
    # Create test scenarios
    scenarios = TestScenarios()
    
    # Run a quick test first
    print("\n1. Quick test with short article...")
    scenarios.run_basic_test("short_politics")
    
    print("\n2. Step-by-step test...")
    scenarios.run_step_by_step_test("tech_article", stop_after="extraction")
    
    # Uncomment to run all scenarios (takes longer)
    # print("\n3. All scenarios...")
    # scenarios.run_all_scenarios()
    
    print("\n🎉 Debug playground session complete!")


if __name__ == "__main__":
    main()