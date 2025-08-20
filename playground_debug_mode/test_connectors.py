#!/usr/bin/env python3
"""
Test des connecteurs open data avec logs détaillés
Teste la connectivité et les performances des différents connecteurs
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire parent au PYTHONPATH pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from playground_debug_mode.logger import debug_logger, timer_decorator
from ai_engine.connectors.data_gouv import DataGouvClient
from ai_engine.connectors.data_gov import DataGovClient
from ai_engine.connectors.data_canada import CanadaGovClient
from ai_engine.connectors.data_uk import UKGovClient
from ai_engine.connectors.hdx_data import HdxClient


@timer_decorator(debug_logger)
def test_connector(connector_class, connector_name: str, test_keywords: list):
    """Teste un connecteur spécifique avec une liste de mots-clés"""
    debug_logger.separator(f"Test connecteur - {connector_name}")
    
    try:
        # Initialiser le connecteur
        connector = connector_class()
        debug_logger.info(f"Connecteur {connector_name} initialisé")
        
        total_results = 0
        successful_searches = 0
        failed_searches = 0
        
        for keyword in test_keywords:
            debug_logger.info(f"Recherche avec mot-clé: '{keyword}'")
            
            try:
                # Effectuer la recherche
                results = connector.search(keyword, max_results=3)
                result_count = len(results) if results else 0
                total_results += result_count
                successful_searches += 1
                
                debug_logger.success(f"Recherche réussie", 
                                   keyword=keyword, 
                                   results_count=result_count)
                
                # Analyser les premiers résultats
                if results and len(results) > 0:
                    first_result = results[0]
                    debug_logger.debug("Premier résultat",
                                     type=type(first_result).__name__,
                                     has_title=hasattr(first_result, 'title'),
                                     has_url=hasattr(first_result, 'url') or hasattr(first_result, 'landing_page'))
                    
                    # Tester la conversion en DatasetSuggestion
                    try:
                        if hasattr(connector, 'to_suggestion'):
                            suggestion = connector.to_suggestion(first_result)
                            debug_logger.success("Conversion to_suggestion réussie",
                                               title_length=len(suggestion.title) if suggestion.title else 0)
                        else:
                            debug_logger.info("Pas de méthode to_suggestion disponible")
                    except Exception as conv_error:
                        debug_logger.warning("Erreur conversion to_suggestion", error=str(conv_error))
                
            except Exception as search_error:
                failed_searches += 1
                debug_logger.error(f"Erreur recherche", 
                                 keyword=keyword, 
                                 error=str(search_error))
        
        # Métriques finales du connecteur
        debug_logger.metrics(f"Résultats {connector_name}",
                           total_results=total_results,
                           successful_searches=successful_searches,
                           failed_searches=failed_searches,
                           success_rate=f"{(successful_searches/(successful_searches+failed_searches)*100):.1f}%" if (successful_searches+failed_searches) > 0 else "N/A")
        
        return {
            "connector_name": connector_name,
            "total_results": total_results,
            "successful_searches": successful_searches,
            "failed_searches": failed_searches,
            "success_rate": successful_searches/(successful_searches+failed_searches) if (successful_searches+failed_searches) > 0 else 0
        }
        
    except Exception as e:
        debug_logger.error(f"Erreur initialisation connecteur {connector_name}", error=e)
        return None


@timer_decorator(debug_logger)
def test_all_connectors():
    """Teste tous les connecteurs disponibles"""
    debug_logger.separator("Test de tous les connecteurs")
    
    # Configuration des connecteurs à tester
    connectors_config = [
        (DataGouvClient, "Data.gouv.fr", ["santé", "éducation", "transport"]),
        (DataGovClient, "Data.gov (US)", ["health", "education", "climate"]),
        (CanadaGovClient, "Canada Open Data", ["health", "economy", "environment"]),
        (UKGovClient, "UK Gov Data", ["healthcare", "economy", "transport"]),
        (HdxClient, "HDX Humanitarian", ["refugees", "food", "health"]),
    ]
    
    results = []
    
    for connector_class, name, keywords in connectors_config:
        result = test_connector(connector_class, name, keywords)
        if result:
            results.append(result)
        else:
            debug_logger.warning(f"Connecteur {name} non testé")
    
    # Analyse comparative
    if results:
        debug_logger.separator("Analyse comparative", "-", 60)
        
        # Trier par taux de succès
        results.sort(key=lambda x: x['success_rate'], reverse=True)
        
        debug_logger.info("Classement par performance:")
        for i, result in enumerate(results, 1):
            debug_logger.metrics(f"#{i} {result['connector_name']}",
                               success_rate=f"{result['success_rate']*100:.1f}%",
                               total_results=result['total_results'])
        
        # Métriques globales
        total_searches = sum(r['successful_searches'] + r['failed_searches'] for r in results)
        total_successes = sum(r['successful_searches'] for r in results)
        global_success_rate = total_successes / total_searches if total_searches > 0 else 0
        
        debug_logger.metrics("Performance globale",
                           total_connectors=len(results),
                           total_searches=total_searches,
                           global_success_rate=f"{global_success_rate*100:.1f}%")
        
        # Sauvegarder les résultats
        debug_logger.save_json({
            "connectors_results": results,
            "global_metrics": {
                "total_connectors": len(results),
                "total_searches": total_searches,
                "global_success_rate": global_success_rate
            }
        }, "connectors_test_results")
    
    return results


@timer_decorator(debug_logger)
def test_connector_robustness():
    """Teste la robustesse des connecteurs avec des cas limites"""
    debug_logger.separator("Test de robustesse")
    
    # Mots-clés difficiles pour tester la robustesse
    edge_case_keywords = [
        "",  # Mot-clé vide
        "   ",  # Espaces seulement
        "ñáéíóú",  # Caractères accentués
        "covid-19",  # Tirets
        "AI/ML",  # Slash
        "test123456789012345678901234567890",  # Très long
    ]
    
    debug_logger.info("Test avec mots-clés difficiles")
    
    # Test avec Data.gouv seulement pour la robustesse
    try:
        connector = DataGouvClient()
        robust_count = 0
        
        for keyword in edge_case_keywords:
            debug_logger.info(f"Test robustesse: '{keyword}'")
            try:
                results = connector.search(keyword, max_results=1)
                robust_count += 1
                debug_logger.success("Test robustesse réussi", keyword=repr(keyword))
            except Exception as e:
                debug_logger.warning("Test robustesse échoué", keyword=repr(keyword), error=str(e))
        
        debug_logger.metrics("Robustesse",
                           tested_cases=len(edge_case_keywords),
                           successful_cases=robust_count,
                           robustness_score=f"{(robust_count/len(edge_case_keywords)*100):.1f}%")
        
    except Exception as e:
        debug_logger.error("Erreur test robustesse", error=e)


def main():
    """Fonction principale - exécute tous les tests de connecteurs"""
    debug_logger.separator("🔌 Tests connecteurs - Playground Debug Mode", "=", 100)
    debug_logger.info("Démarrage des tests de connecteurs open data")
    
    # Test de tous les connecteurs
    results = test_all_connectors()
    
    # Test de robustesse
    test_connector_robustness()
    
    debug_logger.separator("Tests connecteurs terminés", "=", 100)
    
    if results:
        best_connector = max(results, key=lambda x: x['success_rate'])
        debug_logger.success("Tests terminés",
                           best_connector=best_connector['connector_name'],
                           best_success_rate=f"{best_connector['success_rate']*100:.1f}%")
    else:
        debug_logger.warning("Aucun connecteur testé avec succès")
    
    debug_logger.info("Consultez les fichiers de sortie pour plus de détails.")


if __name__ == "__main__":
    main()