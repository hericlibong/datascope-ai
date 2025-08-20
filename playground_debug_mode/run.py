#!/usr/bin/env python3
"""
Runner principal pour le playground debug mode
Permet de lancer facilement les différents tests avec des options
"""

import sys
import os
from pathlib import Path
import argparse

# Ajouter le répertoire parent au PYTHONPATH pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from playground_debug_mode.logger import debug_logger


def run_extraction_tests():
    """Lance les tests d'extraction"""
    debug_logger.info("🚀 Lancement des tests d'extraction...")
    try:
        from playground_debug_mode.test_extraction import main as extraction_main
        extraction_main()
        return True
    except Exception as e:
        debug_logger.error("Erreur lors des tests d'extraction", error=e)
        return False


def run_angles_tests():
    """Lance les tests de génération d'angles"""
    debug_logger.info("🚀 Lancement des tests d'angles...")
    try:
        from playground_debug_mode.test_angles import main as angles_main
        angles_main()
        return True
    except Exception as e:
        debug_logger.error("Erreur lors des tests d'angles", error=e)
        return False


def run_connectors_tests():
    """Lance les tests de connecteurs"""
    debug_logger.info("🚀 Lancement des tests de connecteurs...")
    try:
        from playground_debug_mode.test_connectors import main as connectors_main
        connectors_main()
        return True
    except Exception as e:
        debug_logger.error("Erreur lors des tests de connecteurs", error=e)
        return False


def run_pipeline_tests():
    """Lance les tests du pipeline complet"""
    debug_logger.info("🚀 Lancement des tests de pipeline...")
    try:
        from playground_debug_mode.test_pipeline import main as pipeline_main
        pipeline_main()
        return True
    except Exception as e:
        debug_logger.error("Erreur lors des tests de pipeline", error=e)
        return False


def run_demo():
    """Lance la démonstration sans réseau"""
    debug_logger.info("🚀 Lancement de la démonstration...")
    try:
        from playground_debug_mode.demo import main as demo_main
        demo_main()
        return True
    except Exception as e:
        debug_logger.error("Erreur lors de la démonstration", error=e)
        return False


def run_all_tests():
    """Lance tous les tests dans l'ordre"""
    debug_logger.separator("🧪 Exécution complète - Playground Debug Mode", "=", 100)
    debug_logger.info("Démarrage de tous les tests du playground")
    
    tests = [
        ("Extraction", run_extraction_tests),
        ("Angles", run_angles_tests),
        ("Connecteurs", run_connectors_tests),
        ("Pipeline", run_pipeline_tests),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        debug_logger.separator(f"Test {test_name}", "-", 60)
        success = test_func()
        results[test_name] = success
        
        if success:
            debug_logger.success(f"✅ Test {test_name} terminé avec succès")
        else:
            debug_logger.error(f"❌ Test {test_name} échoué")
    
    # Résumé final
    debug_logger.separator("Résumé des tests", "=", 100)
    
    successful_tests = sum(1 for success in results.values() if success)
    total_tests = len(results)
    
    debug_logger.metrics("Résultats finaux",
                        tests_reussis=successful_tests,
                        tests_totaux=total_tests,
                        taux_reussite=f"{(successful_tests/total_tests*100):.1f}%")
    
    for test_name, success in results.items():
        status = "✅ RÉUSSI" if success else "❌ ÉCHOUÉ"
        debug_logger.info(f"{test_name}: {status}")
    
    if successful_tests == total_tests:
        debug_logger.success("🎉 Tous les tests sont réussis!")
    else:
        debug_logger.warning(f"⚠️ {total_tests - successful_tests} test(s) ont échoué")
    
    debug_logger.info("📁 Consultez le dossier 'outputs' pour les détails des résultats")


def check_environment():
    """Vérifie que l'environnement est correctement configuré"""
    debug_logger.separator("Vérification de l'environnement", "-", 50)
    
    # Vérifier la clé API OpenAI
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        debug_logger.success("Clé API OpenAI configurée", key_length=len(openai_key))
    else:
        debug_logger.warning("⚠️ Clé API OpenAI non trouvée")
        debug_logger.info("Pour utiliser l'IA, définissez OPENAI_API_KEY dans votre environnement")
        debug_logger.info("export OPENAI_API_KEY='votre_clé_ici'")
    
    # Vérifier les dépendances importantes
    try:
        import ai_engine
        debug_logger.success("Module ai_engine disponible")
    except ImportError as e:
        debug_logger.error("Module ai_engine non disponible", error=e)
    
    try:
        from langchain import __version__ as langchain_version
        debug_logger.success("LangChain disponible", version=langchain_version)
    except ImportError as e:
        debug_logger.error("LangChain non disponible", error=e)
    
    # Vérifier le dossier de sortie
    outputs_dir = Path(__file__).parent / "outputs"
    if outputs_dir.exists():
        debug_logger.success("Dossier outputs disponible", path=str(outputs_dir))
    else:
        debug_logger.warning("Dossier outputs manquant, tentative de création...")
        try:
            outputs_dir.mkdir(exist_ok=True)
            debug_logger.success("Dossier outputs créé")
        except Exception as e:
            debug_logger.error("Impossible de créer le dossier outputs", error=e)


def main():
    """Fonction principale avec gestion des arguments de ligne de commande"""
    parser = argparse.ArgumentParser(
        description="Playground Debug Mode - DataScope AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python run.py --all              # Lance tous les tests
  python run.py --extraction       # Tests d'extraction seulement
  python run.py --angles           # Tests d'angles seulement
  python run.py --connectors       # Tests de connecteurs seulement
  python run.py --pipeline         # Tests de pipeline seulement
  python run.py --check            # Vérification de l'environnement
  python run.py --demo             # Démonstration sans réseau
        """
    )
    
    parser.add_argument("--all", action="store_true", 
                       help="Lance tous les tests")
    parser.add_argument("--extraction", action="store_true",
                       help="Lance les tests d'extraction")
    parser.add_argument("--angles", action="store_true",
                       help="Lance les tests de génération d'angles")
    parser.add_argument("--connectors", action="store_true",
                       help="Lance les tests de connecteurs")
    parser.add_argument("--pipeline", action="store_true",
                       help="Lance les tests du pipeline complet")
    parser.add_argument("--check", action="store_true",
                       help="Vérifie l'environnement de développement")
    parser.add_argument("--demo", action="store_true",
                       help="Lance une démonstration sans réseau")
    
    args = parser.parse_args()
    
    # Si aucun argument, afficher l'aide
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    # Vérification de l'environnement si demandée
    if args.check:
        check_environment()
        return
    
    # Démonstration si demandée
    if args.demo:
        run_demo()
        return
    
    # Lancement des tests selon les arguments
    if args.all:
        run_all_tests()
    else:
        if args.extraction:
            run_extraction_tests()
        
        if args.angles:
            run_angles_tests()
        
        if args.connectors:
            run_connectors_tests()
        
        if args.pipeline:
            run_pipeline_tests()


if __name__ == "__main__":
    main()