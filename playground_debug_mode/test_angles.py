#!/usr/bin/env python3
"""
Test de la génération d'angles éditoriaux avec logs détaillés
Teste la capacité de l'IA à générer des angles journalistiques pertinents
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire parent au PYTHONPATH pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from playground_debug_mode.logger import debug_logger, timer_decorator
from ai_engine.chains import angles
from ai_engine.utils import token_len
import ai_engine


@timer_decorator(debug_logger)
def test_angles_generation(sample_file: str):
    """Teste la génération d'angles sur un échantillon d'article"""
    debug_logger.separator(f"Test génération d'angles - {sample_file}")
    
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
        # Exécuter la génération d'angles
        debug_logger.info("Lancement de la génération d'angles...")
        result = angles.run(article_text)
        
        # Analyser les résultats
        debug_logger.success("Génération d'angles terminée avec succès")
        debug_logger.metrics("Résultats angles",
                           angles_count=len(result.angles),
                           total_characters=sum(len(angle.title) + len(angle.rationale) for angle in result.angles))
        
        # Détails des angles générés
        for i, angle in enumerate(result.angles):
            debug_logger.info(f"Angle {i+1}",
                            title=angle.title,
                            rationale_length=len(angle.rationale))
            
            # Afficher le rationale tronqué pour le debug
            rationale_preview = angle.rationale[:100] + "..." if len(angle.rationale) > 100 else angle.rationale
            debug_logger.debug(f"Rationale {i+1}", content=rationale_preview)
        
        # Évaluation qualitative des angles
        debug_logger.separator("Évaluation qualitative", "-", 50)
        
        # Vérifier la diversité des angles
        titles = [angle.title.lower() for angle in result.angles]
        unique_words = set()
        for title in titles:
            unique_words.update(title.split())
        
        diversity_score = len(unique_words) / max(len(titles), 1)
        debug_logger.metrics("Diversité des angles", 
                           unique_words_count=len(unique_words),
                           diversity_score=f"{diversity_score:.2f}")
        
        # Vérifier la pertinence (longueur des rationales)
        avg_rationale_length = sum(len(angle.rationale) for angle in result.angles) / len(result.angles)
        debug_logger.metrics("Qualité des rationales",
                           avg_length=f"{avg_rationale_length:.1f}",
                           min_length=min(len(angle.rationale) for angle in result.angles),
                           max_length=max(len(angle.rationale) for angle in result.angles))
        
        # Sauvegarder les résultats
        output_data = {
            "sample_file": sample_file,
            "article_length": len(article_text),
            "token_count": token_len(article_text, model=ai_engine.OPENAI_MODEL),
            "angles_result": {
                "angles_count": len(result.angles),
                "angles": [
                    {
                        "title": angle.title,
                        "rationale": angle.rationale,
                        "title_length": len(angle.title),
                        "rationale_length": len(angle.rationale)
                    }
                    for angle in result.angles
                ]
            },
            "quality_metrics": {
                "diversity_score": diversity_score,
                "avg_rationale_length": avg_rationale_length,
                "unique_words_count": len(unique_words)
            }
        }
        
        debug_logger.save_json(output_data, f"angles_result_{sample_file.split('.')[0]}")
        
        return result
        
    except Exception as e:
        debug_logger.error("Erreur lors de la génération d'angles", error=e)
        return None


@timer_decorator(debug_logger)
def test_angles_consistency():
    """Teste la cohérence de la génération d'angles"""
    debug_logger.separator("Test de cohérence")
    
    # Article de test simple
    test_article = """
    Le gouvernement français annonce un nouveau plan de relance économique de 100 milliards d'euros.
    Ce plan, présenté par le Premier ministre à l'Assemblée nationale, vise à soutenir les entreprises
    et à créer des emplois dans les secteurs verts et numériques.
    """
    
    debug_logger.info("Test de cohérence sur 3 générations successives")
    
    results = []
    for i in range(3):
        debug_logger.info(f"Génération {i+1}/3")
        try:
            result = angles.run(test_article)
            results.append(result)
            debug_logger.success(f"Génération {i+1} réussie", angles_count=len(result.angles))
        except Exception as e:
            debug_logger.error(f"Génération {i+1} échouée", error=e)
            results.append(None)
    
    # Analyser la cohérence
    if all(r is not None for r in results):
        debug_logger.info("Analyse de cohérence...")
        
        # Comparer le nombre d'angles
        angles_counts = [len(r.angles) for r in results]
        debug_logger.metrics("Cohérence - Nombre d'angles",
                           counts=angles_counts,
                           consistent=len(set(angles_counts)) == 1)
        
        # Analyser la similarité des titres
        all_titles = []
        for result in results:
            all_titles.extend([angle.title.lower() for angle in result.angles])
        
        unique_titles = set(all_titles)
        similarity_ratio = len(unique_titles) / len(all_titles) if all_titles else 0
        
        debug_logger.metrics("Cohérence - Similarité des titres",
                           total_titles=len(all_titles),
                           unique_titles=len(unique_titles),
                           similarity_ratio=f"{similarity_ratio:.2f}")
    else:
        debug_logger.warning("Impossible d'analyser la cohérence à cause d'échecs")


def main():
    """Fonction principale - exécute tous les tests d'angles"""
    debug_logger.separator("🎯 Tests génération d'angles - Playground Debug Mode", "=", 100)
    debug_logger.info("Démarrage des tests de génération d'angles")
    debug_logger.metrics("Configuration", 
                        model=ai_engine.OPENAI_MODEL,
                        max_tokens=8000)
    
    # Test avec échantillons français et anglais
    sample_files = ["sample_fr.txt", "sample_en.txt"]
    
    for sample_file in sample_files:
        result = test_angles_generation(sample_file)
        if result:
            debug_logger.success(f"Test {sample_file} réussi")
        else:
            debug_logger.error(f"Test {sample_file} échoué")
    
    # Test de cohérence
    test_angles_consistency()
    
    debug_logger.separator("Tests génération d'angles terminés", "=", 100)
    debug_logger.success("Tous les tests d'angles sont terminés. Consultez les fichiers de sortie pour plus de détails.")


if __name__ == "__main__":
    main()