# 🧪 Playground Debug Mode

Espace de test séparé pour tester la chaîne IA DataScope avec des logs détaillés.

## 📁 Structure

```
playground_debug_mode/
├── __init__.py           # Init du module
├── README.md            # Cette documentation
├── .gitignore           # Exclusions git (cache, logs)
├── logger.py            # Utilitaires de logging avancé
├── demo.py              # Démonstration sans réseau
├── run.py               # Runner CLI principal
├── test_extraction.py   # Test de la chaîne d'extraction
├── test_angles.py       # Test de la génération d'angles
├── test_connectors.py   # Test des connecteurs open data
├── test_pipeline.py     # Test du pipeline complet
├── samples/             # Exemples d'articles pour tests
│   ├── sample_fr.txt
│   └── sample_en.txt
└── outputs/             # Sorties de debug (logs, json)
    └── .gitkeep
```

## 🚀 Utilisation

### Démarrage rapide avec la démonstration
```bash
cd playground_debug_mode

# Démonstration sans réseau (recommandé pour découvrir)
python run.py --demo

# Vérifier l'environnement
python run.py --check
```

### Méthode recommandée : Script runner
```bash
# Tester un composant spécifique
python run.py --extraction   # Tests d'extraction d'entités
python run.py --angles       # Tests de génération d'angles
python run.py --connectors   # Tests des connecteurs open data
python run.py --pipeline     # Test du pipeline complet

# Lancer tous les tests
python run.py --all
```

### Méthode directe : Scripts individuels
```bash
python test_extraction.py
python test_angles.py
python test_connectors.py
python test_pipeline.py
```

### Variables d'environnement requises
```bash
export OPENAI_API_KEY="your_openai_api_key"
export SECRET_KEY="your_django_secret_key"
export DB_NAME="your_db_name"
export DB_USER="your_db_user"
export DB_PASSWORD="your_db_password"
# Pour les tests, utiliser SQLite en mémoire :
export USE_SQLITE_FOR_TESTS=1
```

## ⚠️ Notes importantes

- **Démonstration** : `python run.py --demo` fonctionne sans réseau ni clés API
- **Tests IA** : Les autres tests nécessitent une clé OpenAI valide et un accès réseau
- **Environnement** : Utilisez `python run.py --check` pour valider la configuration

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