"""
Debug wrapper for the AI pipeline with enhanced logging and tracing.
"""

import time
from typing import Optional, Tuple, List
try:
    from ai_engine import pipeline
    PIPELINE_AVAILABLE = True
except Exception as e:
    PIPELINE_AVAILABLE = False
    PIPELINE_ERROR = str(e)
from ai_engine.schemas import AnalysisPackage, AngleResources
from .debug_utils import DebugLogger, debug_trace


class DebugPipeline:
    """Debug wrapper for the DataScope AI pipeline with detailed logging."""
    
    def __init__(self, log_file: Optional[str] = None):
        self.logger = DebugLogger("debug_pipeline", log_file)
        
        if not PIPELINE_AVAILABLE:
            self.logger.log_error(Exception(PIPELINE_ERROR), "PIPELINE IMPORT")
            self.logger.log_step("INIT", "DebugPipeline initialized (pipeline unavailable)")
        else:
            self.logger.log_step("INIT", "DebugPipeline initialized")
    
    @debug_trace
    def run(
        self,
        article_text: str,
        user_id: str = "debug_user",
    ) -> Tuple[AnalysisPackage, str, float, List[AngleResources]]:
        """
        Run the AI pipeline with enhanced debugging and logging.
        
        Args:
            article_text: The article text to analyze
            user_id: User identifier for this analysis
            
        Returns:
            Tuple of (analysis_package, markdown, score, angle_resources)
        """
        if not PIPELINE_AVAILABLE:
            self.logger.log_error(Exception(f"Pipeline not available: {PIPELINE_ERROR}"), "RUN")
            raise Exception(f"AI pipeline is not available. Error: {PIPELINE_ERROR}")
        
        self.logger.log_step("PIPELINE START", {
            "article_length": len(article_text),
            "user_id": user_id,
            "article_preview": article_text[:200] + "..." if len(article_text) > 200 else article_text
        })
        
        start_time = time.time()
        
        try:
            # Call the original pipeline with debugging
            result = pipeline.run(article_text, user_id)
            
            total_duration = time.time() - start_time
            self.logger.log_timing("COMPLETE PIPELINE", total_duration)
            
            # Log detailed results
            analysis_package, markdown, score, angle_resources = result
            
            self.logger.log_step("PIPELINE RESULTS", {
                "score": score,
                "num_angles": len(angle_resources),
                "markdown_length": len(markdown),
                "analysis_summary": {
                    "num_persons": len(analysis_package.extraction.persons) if hasattr(analysis_package, 'extraction') else 0,
                    "num_organizations": len(analysis_package.extraction.organizations) if hasattr(analysis_package, 'extraction') else 0,
                    "num_angles": len(analysis_package.angles.angles) if hasattr(analysis_package, 'angles') else 0,
                }
            })
            
            # Log each angle's resources
            for i, angle_resource in enumerate(angle_resources):
                self.logger.log_step(f"ANGLE {i}", {
                    "title": angle_resource.title,
                    "num_keywords": len(angle_resource.keywords),
                    "num_datasets": len(angle_resource.datasets),
                    "num_sources": len(angle_resource.sources),
                    "num_visualizations": len(angle_resource.visualizations),
                })
            
            self.logger.log_step("PIPELINE SUCCESS", "Analysis completed successfully")
            return result
            
        except Exception as e:
            total_duration = time.time() - start_time
            self.logger.log_timing("FAILED PIPELINE", total_duration)
            self.logger.log_error(e, "PIPELINE RUN")
            raise
    
    def debug_step_by_step(
        self,
        article_text: str,
        user_id: str = "debug_user",
        stop_after: Optional[str] = None
    ) -> dict:
        """
        Run pipeline step by step for detailed debugging.
        
        Args:
            article_text: The article text to analyze
            user_id: User identifier
            stop_after: Stop after this step (e.g., 'extraction', 'angles', 'keywords')
            
        Returns:
            Dictionary with intermediate results from each step
        """
        if not PIPELINE_AVAILABLE:
            self.logger.log_error(Exception(f"Pipeline not available: {PIPELINE_ERROR}"), "STEP_BY_STEP")
            return {"error": f"AI pipeline is not available. Error: {PIPELINE_ERROR}"}
        
        from ai_engine.chains import extraction, angles, keywords
        from ai_engine.scoring import compute_score
        import ai_engine
        
        results = {}
        self.logger.log_step("STEP-BY-STEP DEBUG START", {"stop_after": stop_after})
        
        try:
            # Step 1: Validation
            self.logger.log_step("STEP 1: VALIDATION")
            start_time = time.time()
            pipeline._validate(article_text)
            duration = time.time() - start_time
            self.logger.log_timing("validation", duration)
            results["validation"] = "passed"
            
            if stop_after == "validation":
                return results
            
            # Step 2: Extraction
            self.logger.log_step("STEP 2: EXTRACTION")
            start_time = time.time()
            extraction_result = extraction.run(article_text)
            duration = time.time() - start_time
            self.logger.log_timing("extraction", duration)
            self.logger.log_result("extraction", extraction_result)
            results["extraction"] = extraction_result
            
            if stop_after == "extraction":
                return results
            
            # Step 3: Scoring
            self.logger.log_step("STEP 3: SCORING")
            start_time = time.time()
            score_10 = round(
                compute_score(extraction_result, article_text, model=ai_engine.OPENAI_MODEL),
                1,
            )
            duration = time.time() - start_time
            self.logger.log_timing("scoring", duration)
            self.logger.log_result("scoring", score_10)
            results["score"] = score_10
            
            if stop_after == "scoring":
                return results
            
            # Step 4: Angles
            self.logger.log_step("STEP 4: ANGLES")
            start_time = time.time()
            angle_result = angles.run(article_text)
            duration = time.time() - start_time
            self.logger.log_timing("angles", duration)
            self.logger.log_result("angles", angle_result)
            results["angles"] = angle_result
            
            if stop_after == "angles":
                return results
            
            # Step 5: Keywords
            self.logger.log_step("STEP 5: KEYWORDS")
            start_time = time.time()
            keywords_per_angle = keywords.run(angle_result)
            duration = time.time() - start_time
            self.logger.log_timing("keywords", duration)
            self.logger.log_result("keywords", keywords_per_angle)
            results["keywords"] = keywords_per_angle
            
            if stop_after == "keywords":
                return results
            
            self.logger.log_step("STEP-BY-STEP DEBUG COMPLETE")
            return results
            
        except Exception as e:
            self.logger.log_error(e, "STEP-BY-STEP DEBUG")
            results["error"] = str(e)
            return results