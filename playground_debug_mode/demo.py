#!/usr/bin/env python3
"""
Démo simple du playground debug mode sans appels réseau
Montre les capacités de logging et de structuration des tests
"""

import sys
from pathlib import Path

# Ajouter le répertoire parent au PYTHONPATH pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from playground_debug_mode.logger import debug_logger, timer_decorator


@timer_decorator(debug_logger)
def demo_logging_features():
    """Démontre les différentes fonctionnalités du logger"""
    debug_logger.info("Démarrage de la démonstration des fonctionnalités de logging")
    
    # Messages de différents niveaux
    debug_logger.success("Message de succès avec données", count=42, status="active")
    debug_logger.warning("Message d'avertissement", reason="test_mode")
    debug_logger.error("Message d'erreur de test", error=Exception("Erreur simulée"))
    debug_logger.debug("Message de debug avec beaucoup de détails", 
                       data={"key1": "value1", "key2": [1, 2, 3, 4, 5]})
    
    # Métriques
    debug_logger.metrics("Performance simulée",
                        execution_time="0.42s",
                        memory_usage="128MB",
                        operations_count=1337)
    
    return {"demo": "completed", "features_shown": 5}


@timer_decorator(debug_logger)
def demo_file_operations():
    """Démontre les opérations sur fichiers"""
    debug_logger.info("Test des opérations sur fichiers")
    
    # Lire un fichier échantillon
    sample_path = Path(__file__).parent / "samples" / "sample_fr.txt"
    if sample_path.exists():
        with open(sample_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        debug_logger.success("Fichier échantillon lu", 
                           file=str(sample_path),
                           size=len(content),
                           lines=content.count('\n') + 1)
        
        # Analyser le contenu
        words = content.split()
        debug_logger.metrics("Analyse du contenu",
                           word_count=len(words),
                           char_count=len(content),
                           avg_word_length=f"{sum(len(w) for w in words) / len(words):.1f}")
        
        # Sauvegarder une analyse JSON
        analysis_data = {
            "filename": sample_path.name,
            "word_count": len(words),
            "char_count": len(content),
            "first_50_chars": content[:50] + "..." if len(content) > 50 else content
        }
        
        debug_logger.save_json(analysis_data, "demo_file_analysis")
        
        return analysis_data
    else:
        debug_logger.warning("Fichier échantillon non trouvé", expected_path=str(sample_path))
        return None


def demo_error_handling():
    """Démontre la gestion d'erreurs avec logging"""
    debug_logger.separator("Test gestion d'erreurs", "-", 50)
    
    try:
        # Simuler une opération qui échoue
        debug_logger.info("Tentative d'opération risquée...")
        result = 10 / 0  # Division par zéro intentionnelle
    except ZeroDivisionError as e:
        debug_logger.error("Division par zéro capturée", error=e, operation="10/0")
        debug_logger.info("Récupération gracieuse de l'erreur")
        return False
    except Exception as e:
        debug_logger.error("Erreur inattendue", error=e)
        return False
    
    return True


def main():
    """Fonction principale de la démonstration"""
    debug_logger.separator("🎪 Démonstration Playground Debug Mode", "=", 80)
    debug_logger.info("Bienvenue dans la démonstration du mode debug!")
    debug_logger.info("Cette démo fonctionne sans accès réseau ni clés API")
    
    # Démonstration des fonctionnalités de logging
    debug_logger.separator("Fonctionnalités de logging", "-", 60)
    result1 = demo_logging_features()
    
    # Démonstration des opérations sur fichiers
    debug_logger.separator("Opérations sur fichiers", "-", 60)
    result2 = demo_file_operations()
    
    # Démonstration de la gestion d'erreurs
    demo_error_handling()
    
    # Résumé
    debug_logger.separator("Résumé de la démonstration", "=", 80)
    debug_logger.success("Démonstration terminée avec succès!")
    debug_logger.metrics("Résultats",
                        logging_demo=bool(result1),
                        file_ops_demo=bool(result2),
                        features_demonstrated=["colored_logging", "metrics", "json_export", "error_handling"])
    
    debug_logger.info("📁 Consultez le dossier 'outputs' pour voir les fichiers générés")
    debug_logger.info("🎯 Pour tester avec l'IA, configurez OPENAI_API_KEY et utilisez les autres scripts")


if __name__ == "__main__":
    main()