# 🧪 Playground Debug Mode

Espace de test séparé pour tester la chaîne IA DataScope avec des logs détaillés.

## 📁 Structure

```
playground_debug_mode/
├── __init__.py           # Init du module
├── README.md            # Cette documentation
├── logger.py            # Utilitaires de logging avancé
├── test_pipeline.py     # Test du pipeline complet avec logs
├── test_extraction.py   # Test de la chaîne d'extraction
├── test_angles.py       # Test de la génération d'angles
├── test_connectors.py   # Test des connecteurs open data
├── samples/             # Exemples d'articles pour tests
│   ├── sample_fr.txt
│   └── sample_en.txt
└── outputs/             # Sorties de debug (logs, json)
    └── .gitkeep
```

## 🚀 Utilisation

### Test complet du pipeline
```bash
cd playground_debug_mode
python test_pipeline.py
```

### Test d'un composant spécifique
```bash
python test_extraction.py
python test_angles.py
python test_connectors.py
```

## 📊 Logging

Tous les tests utilisent un système de logging enrichi qui affiche :
- ✅ Succès des opérations
- ⚠️  Avertissements
- ❌ Erreurs détaillées
- 🔍 Debug traces avec timing
- 📊 Métriques (tokens, scores, etc.)

## 🎯 Objectifs

- **Debug** : Identifier rapidement les problèmes dans la chaîne IA
- **Test** : Valider les modifications avant intégration
- **Dev** : Développer et tester de nouvelles fonctionnalités
- **Monitoring** : Surveiller les performances des composants