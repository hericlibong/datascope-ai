#!/usr/bin/env python3
"""
Test complet du pipeline DataScope avec logs détaillés
Teste l'ensemble de la chaîne de traitement IA de bout en bout
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire parent au PYTHONPATH pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from playground_debug_mode.logger import debug_logger, timer_decorator
from ai_engine.pipeline import run as pipeline_run
from ai_engine.utils import token_len
import ai_engine
import json


@timer_decorator(debug_logger)
def test_full_pipeline(sample_file: str, user_id: str = "playground_test"):
    """Teste le pipeline complet sur un échantillon d'article"""
    debug_logger.separator(f"Test pipeline complet - {sample_file}", "=", 80)
    
    # Charger l'échantillon
    sample_path = Path(__file__).parent / "samples" / sample_file
    if not sample_path.exists():
        debug_logger.error(f"Fichier échantillon non trouvé", file=str(sample_path))
        return None
    
    with open(sample_path, 'r', encoding='utf-8') as f:
        article_text = f.read()
    
    debug_logger.info(f"Article chargé", 
                     length=len(article_text), 
                     tokens=token_len(article_text, model=ai_engine.OPENAI_MODEL))
    
    try:
        debug_logger.info("🚀 Démarrage du pipeline complet...")
        
        # Exécuter le pipeline complet
        packaged, markdown, score_10, angle_resources = pipeline_run(article_text, user_id)
        
        debug_logger.success("✅ Pipeline exécuté avec succès!")
        
        # === ANALYSE DES RÉSULTATS ===
        debug_logger.separator("Analyse des résultats", "-", 60)
        
        # Métriques générales
        debug_logger.metrics("Résultats généraux",
                           score=f"{score_10}/10",
                           angles_count=len(angle_resources),
                           markdown_length=len(markdown))
        
        # Analyse de l'extraction
        if hasattr(packaged, 'extraction'):
            extraction = packaged.extraction
            debug_logger.metrics("Extraction",
                               language=extraction.language,
                               persons=len(extraction.persons),
                               organizations=len(extraction.organizations),
                               locations=len(extraction.locations),
                               dates=len(extraction.dates))
            
            if extraction.persons:
                debug_logger.info("Personnes extraites", entities=extraction.persons[:5])
            if extraction.organizations:
                debug_logger.info("Organisations extraites", entities=extraction.organizations[:5])
        
        # Analyse des angles et ressources
        total_datasets = 0
        total_sources = 0
        total_visualizations = 0
        
        for i, angle_resource in enumerate(angle_resources):
            debug_logger.info(f"📐 Angle {i+1}: {angle_resource.title}")
            debug_logger.debug(f"Description angle {i+1}", 
                             content=angle_resource.description[:100] + "..." if len(angle_resource.description) > 100 else angle_resource.description)
            
            datasets_count = len(angle_resource.datasets)
            sources_count = len(angle_resource.sources)
            viz_count = len(angle_resource.visualizations)
            
            total_datasets += datasets_count
            total_sources += sources_count
            total_visualizations += viz_count
            
            debug_logger.metrics(f"Ressources angle {i+1}",
                               datasets=datasets_count,
                               sources=sources_count,
                               visualizations=viz_count,
                               keywords=len(angle_resource.keywords))
            
            # Afficher quelques datasets trouvés
            if angle_resource.datasets:
                debug_logger.info(f"Datasets pour angle {i+1}")
                for j, dataset in enumerate(angle_resource.datasets[:3]):  # Max 3 pour éviter spam
                    debug_logger.debug(f"  📊 Dataset {j+1}",
                                     title=dataset.title[:50] + "..." if len(dataset.title) > 50 else dataset.title,
                                     found_by=dataset.found_by,
                                     source=dataset.source_name)
        
        # Métriques globales des ressources
        debug_logger.metrics("Ressources totales",
                           total_datasets=total_datasets,
                           total_sources=total_sources,
                           total_visualizations=total_visualizations,
                           avg_datasets_per_angle=f"{total_datasets/len(angle_resources):.1f}" if angle_resources else 0)
        
        # Analyse de la diversité des sources
        dataset_sources = set()
        connector_datasets = 0
        llm_datasets = 0
        
        for angle_resource in angle_resources:
            for dataset in angle_resource.datasets:
                if dataset.source_name:
                    dataset_sources.add(dataset.source_name)
                if dataset.found_by == "CONNECTOR":
                    connector_datasets += 1
                elif dataset.found_by == "LLM":
                    llm_datasets += 1
        
        debug_logger.metrics("Diversité des sources",
                           unique_sources=len(dataset_sources),
                           connector_datasets=connector_datasets,
                           llm_datasets=llm_datasets)
        
        # === SAUVEGARDE DES RÉSULTATS ===
        debug_logger.separator("Sauvegarde", "-", 40)
        
        # Préparer les données pour JSON
        pipeline_results = {
            "sample_file": sample_file,
            "user_id": user_id,
            "article_stats": {
                "length": len(article_text),
                "token_count": token_len(article_text, model=ai_engine.OPENAI_MODEL)
            },
            "general_results": {
                "score": score_10,
                "angles_count": len(angle_resources),
                "markdown_length": len(markdown)
            },
            "extraction_results": {
                "language": extraction.language if hasattr(packaged, 'extraction') else None,
                "persons_count": len(extraction.persons) if hasattr(packaged, 'extraction') else 0,
                "organizations_count": len(extraction.organizations) if hasattr(packaged, 'extraction') else 0,
                "locations_count": len(extraction.locations) if hasattr(packaged, 'extraction') else 0,
                "dates_count": len(extraction.dates) if hasattr(packaged, 'extraction') else 0
            },
            "resources_stats": {
                "total_datasets": total_datasets,
                "total_sources": total_sources,
                "total_visualizations": total_visualizations,
                "unique_dataset_sources": len(dataset_sources),
                "connector_datasets": connector_datasets,
                "llm_datasets": llm_datasets
            },
            "angles": [
                {
                    "index": angle.index,
                    "title": angle.title,
                    "description": angle.description,
                    "keywords_count": len(angle.keywords),
                    "datasets_count": len(angle.datasets),
                    "sources_count": len(angle.sources),
                    "visualizations_count": len(angle.visualizations)
                }
                for angle in angle_resources
            ]
        }
        
        # Sauvegarder les résultats JSON
        debug_logger.save_json(pipeline_results, f"pipeline_results_{sample_file.split('.')[0]}")
        
        # Sauvegarder le markdown généré
        markdown_path = Path(__file__).parent / "outputs" / f"markdown_{sample_file.split('.')[0]}.md"
        with open(markdown_path, 'w', encoding='utf-8') as f:
            f.write(markdown)
        debug_logger.info("Markdown sauvegardé", file=str(markdown_path))
        
        return {
            "packaged": packaged,
            "markdown": markdown,
            "score": score_10,
            "angle_resources": angle_resources,
            "stats": pipeline_results
        }
        
    except Exception as e:
        debug_logger.error("❌ Erreur dans le pipeline", error=e)
        import traceback
        debug_logger.debug("Stack trace", trace=traceback.format_exc())
        return None


@timer_decorator(debug_logger)
def compare_pipeline_results():
    """Compare les résultats du pipeline sur différents échantillons"""
    debug_logger.separator("Comparaison des résultats", "=", 80)
    
    sample_files = ["sample_fr.txt", "sample_en.txt"]
    results = {}
    
    for sample_file in sample_files:
        debug_logger.info(f"Test comparatif sur {sample_file}")
        result = test_full_pipeline(sample_file, f"compare_{sample_file.split('.')[0]}")
        if result:
            results[sample_file] = result['stats']
    
    if len(results) >= 2:
        debug_logger.separator("Analyse comparative", "-", 60)
        
        for metric in ['score', 'angles_count', 'total_datasets', 'total_sources']:
            values = {}
            for sample, stats in results.items():
                if metric in stats['general_results']:
                    values[sample] = stats['general_results'][metric]
                elif metric in stats['resources_stats']:
                    values[sample] = stats['resources_stats'][metric]
            
            if values:
                debug_logger.metrics(f"Comparaison {metric}", **values)
        
        # Sauvegarder la comparaison
        debug_logger.save_json({
            "comparison": results,
            "summary": {
                "samples_compared": list(results.keys()),
                "comparison_timestamp": str(debug_logger.output_dir)
            }
        }, "pipeline_comparison")


def main():
    """Fonction principale - exécute tous les tests de pipeline"""
    debug_logger.separator("🔄 Test Pipeline Complet - Playground Debug Mode", "=", 100)
    debug_logger.info("Démarrage du test du pipeline complet DataScope")
    debug_logger.metrics("Configuration système", 
                        model=ai_engine.OPENAI_MODEL,
                        max_tokens=8000)
    
    # Test sur échantillons individuels
    sample_files = ["sample_fr.txt", "sample_en.txt"]
    
    all_success = True
    for sample_file in sample_files:
        debug_logger.info(f"🧪 Test pipeline sur {sample_file}")
        result = test_full_pipeline(sample_file)
        if result:
            debug_logger.success(f"✅ Test {sample_file} réussi", 
                               score=f"{result['score']}/10",
                               angles=len(result['angle_resources']))
        else:
            debug_logger.error(f"❌ Test {sample_file} échoué")
            all_success = False
    
    # Comparaison des résultats
    debug_logger.info("🔍 Lancement de l'analyse comparative")
    compare_pipeline_results()
    
    debug_logger.separator("Tests pipeline terminés", "=", 100)
    
    if all_success:
        debug_logger.success("🎉 Tous les tests du pipeline sont réussis!")
    else:
        debug_logger.warning("⚠️ Certains tests du pipeline ont échoué")
    
    debug_logger.info("📁 Consultez le dossier 'outputs' pour les résultats détaillés")


if __name__ == "__main__":
    main()