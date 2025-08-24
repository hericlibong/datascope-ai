#!/usr/bin/env python
"""
Script d'audit autonome pour vérifier la cohérence angles → datasets.

Usage:
    python scripts/run_audit.py

Ce script peut être utilisé indépendamment pour auditer la qualité
de la génération d'angles et de la suggestion de datasets.
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'datascope_backend.settings')
os.environ.setdefault('USE_SQLITE_FOR_TESTS', '1')

# Ajouter le répertoire racine au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

django.setup()

# Maintenant on peut importer les modules Django
import pytest
from pathlib import Path

def main():
    """Exécute l'audit complet des angles → datasets"""
    
    print("🔍 LANCEMENT DE L'AUDIT DES INCOHÉRENCES ANGLES → DATASETS")
    print("=" * 70)
    
    # Chemin vers le test d'audit
    audit_test_path = Path(__file__).parent.parent / "ai_engine" / "tests" / "test_audit_angles_datasets.py"
    
    if not audit_test_path.exists():
        print("❌ Erreur: Fichier de test d'audit non trouvé")
        print(f"   Recherché dans: {audit_test_path}")
        sys.exit(1)
    
    print(f"📋 Exécution du test d'audit: {audit_test_path.name}")
    print()
    
    # Exécuter uniquement le test principal d'audit avec sortie détaillée
    result = pytest.main([
        str(audit_test_path) + "::test_audit_angles_datasets_consistency",
        "-v", "-s", "--tb=short"
    ])
    
    print()
    print("=" * 70)
    
    if result == 0:
        print("✅ AUDIT TERMINÉ AVEC SUCCÈS")
        print("   Consultez le rapport ci-dessus pour les détails des incohérences détectées.")
    else:
        print("❌ ERREUR LORS DE L'AUDIT")
        print("   Vérifiez les messages d'erreur ci-dessus.")
    
    print("=" * 70)
    return result

if __name__ == "__main__":
    sys.exit(main())