#!/usr/bin/env python3
"""
Test de la chaîne d'extraction avec logs détaillés
Teste l'extraction d'entités (personnes, organisations, lieux, dates, etc.)
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire parent au PYTHONPATH pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from playground_debug_mode.logger import debug_logger, timer_decorator
from ai_engine.chains import extraction
from ai_engine.utils import token_len
import ai_engine


@timer_decorator(debug_logger)
def test_extraction_with_sample(sample_file: str):
    """Teste l'extraction sur un échantillon d'article"""
    debug_logger.separator(f"Test extraction - {sample_file}")
    
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
        # Exécuter l'extraction
        debug_logger.info("Lancement de l'extraction...")
        result = extraction.run(article_text)
        
        # Analyser les résultats
        debug_logger.success("Extraction terminée avec succès")
        debug_logger.metrics("Résultats extraction",
                           language=result.language,
                           persons_count=len(result.persons),
                           organizations_count=len(result.organizations),
                           locations_count=len(result.locations),
                           dates_count=len(result.dates),
                           numbers_count=len(result.numbers))
        
        # Détails des entités extraites
        if result.persons:
            debug_logger.info("Personnes détectées", entities=result.persons)
        
        if result.organizations:
            debug_logger.info("Organisations détectées", entities=result.organizations)
        
        if result.locations:
            debug_logger.info("Lieux détectés", entities=result.locations)
        
        if result.dates:
            debug_logger.info("Dates détectées", entities=result.dates)
        
        if result.numbers:
            debug_logger.info("Nombres détectés", entities=result.numbers)
        
        # Sauvegarder les résultats
        output_data = {
            "sample_file": sample_file,
            "article_length": len(article_text),
            "token_count": token_len(article_text, model=ai_engine.OPENAI_MODEL),
            "extraction_result": {
                "language": result.language,
                "persons": result.persons,
                "organizations": result.organizations,
                "locations": result.locations,
                "dates": result.dates,
                "numbers": result.numbers
            }
        }
        
        debug_logger.save_json(output_data, f"extraction_result_{sample_file.split('.')[0]}")
        
        return result
        
    except Exception as e:
        debug_logger.error("Erreur lors de l'extraction", error=e)
        return None


@timer_decorator(debug_logger)
def test_extraction_edge_cases():
    """Teste l'extraction sur des cas limites"""
    debug_logger.separator("Tests cas limites")
    
    test_cases = [
        ("Article vide", ""),
        ("Article très court", "Bonjour monde."),
        ("Texte sans entités", "Ceci est un texte simple sans aucune entité notable."),
        ("Texte avec caractères spéciaux", "L'année 2024 était spéciale! @#$%^&*()"),
    ]
    
    for case_name, test_text in test_cases:
        debug_logger.info(f"Test: {case_name}")
        try:
            result = extraction.run(test_text)
            debug_logger.success(f"Cas '{case_name}' traité",
                               language=result.language,
                               total_entities=len(result.persons) + len(result.organizations) + len(result.locations))
        except Exception as e:
            debug_logger.warning(f"Cas '{case_name}' échoué", error=str(e))


def main():
    """Fonction principale - exécute tous les tests d'extraction"""
    debug_logger.separator("🧪 Tests d'extraction - Playground Debug Mode", "=", 100)
    debug_logger.info("Démarrage des tests d'extraction")
    debug_logger.metrics("Configuration", 
                        model=ai_engine.OPENAI_MODEL,
                        max_tokens=8000)
    
    # Test avec échantillons français et anglais
    sample_files = ["sample_fr.txt", "sample_en.txt"]
    
    for sample_file in sample_files:
        result = test_extraction_with_sample(sample_file)
        if result:
            debug_logger.success(f"Test {sample_file} réussi")
        else:
            debug_logger.error(f"Test {sample_file} échoué")
    
    # Tests cas limites
    test_extraction_edge_cases()
    
    debug_logger.separator("Tests d'extraction terminés", "=", 100)
    debug_logger.success("Tous les tests d'extraction sont terminés. Consultez les fichiers de sortie pour plus de détails.")


if __name__ == "__main__":
    main()