# 🎮 DataScope AI Debug Playground

Un espace de test dédié pour déboguer et analyser le pipeline d'IA DataScope avec des logs détaillés et du tracing avancé.

## 📋 Description

Le playground_debug_mode fournit :

- **Logging détaillé** : Traçage complet des étapes du pipeline
- **Tests par étapes** : Exécution step-by-step pour identifier les problèmes
- **Métriques de performance** : Temps d'exécution pour chaque étape
- **Scénarios de test** : Collection d'articles de test prédéfinis
- **Configuration flexible** : Paramètres de debug ajustables

## 🚀 Utilisation rapide

### Configuration de base
```bash
# Depuis la racine du projet
cd playground_debug_mode

# Vérifier la configuration
python run_debug.py --scenario config
```

### Tests simples
```bash
# Test de base avec un article court
python run_debug.py --scenario basic --article short_politics

# Test étape par étape
python run_debug.py --scenario step-by-step --article tech_article

# Arrêter après l'extraction
python run_debug.py --scenario step-by-step --article tech_article --stop-after extraction
```

### Tests complets
```bash
# Exécuter tous les scénarios de test
python run_debug.py --scenario all
```

## 📁 Structure

```
playground_debug_mode/
├── __init__.py              # Module principal
├── debug_utils.py           # Utilitaires de logging et debug
├── debug_pipeline.py        # Wrapper debug pour le pipeline
├── test_scenarios.py        # Scénarios de test prédéfinis
├── config.py               # Configuration du debug
├── run_debug.py            # Script principal d'exécution
├── README.md               # Cette documentation
├── logs/                   # Dossier des logs (auto-créé)
└── output/                 # Dossier des résultats (auto-créé)
```

## 🔧 Configuration

### Variables d'environnement requises
- `OPENAI_API_KEY` : Clé API OpenAI (obligatoire)

### Variables d'environnement optionnelles
- `OPENAI_MODEL` : Modèle OpenAI à utiliser
- `DEBUG` : Mode debug Django
- `SECRET_KEY` : Clé secrète Django

### Paramètres de debug

Les paramètres peuvent être modifiés dans `config.py` :

```python
# Logging
LOG_LEVEL = "DEBUG"
ENABLE_DETAILED_LOGGING = True
TRUNCATE_LOGS_AT = 500

# Performance
ENABLE_STEP_TIMING = True
SAVE_INTERMEDIATE_RESULTS = True

# Tests
TEST_TIMEOUT = 60
```

## 📊 Types de logs

### 🔧 Logs d'étapes
```
2024-01-20 10:30:15 - debug_pipeline - INFO - 🔧 STEP: PIPELINE START | Data: {...}
```

### ⏱️ Logs de performance
```
2024-01-20 10:30:20 - debug_pipeline - INFO - ⏱️ TIMING: extraction took 2.34s
```

### ✅ Logs de résultats
```
2024-01-20 10:30:25 - debug_pipeline - INFO - ✅ RESULT: scoring -> 7.5
```

### ❌ Logs d'erreurs
```
2024-01-20 10:30:30 - debug_pipeline - ERROR - ❌ ERROR in extraction: API timeout
```

## 🧪 Scénarios de test prédéfinis

### Articles disponibles
- `short_politics` : Article politique court
- `tech_article` : Article sur la technologie
- `climate_article` : Article sur le climat
- `economic_article` : Article économique

### Types de tests
- **basic** : Test complet du pipeline
- **step-by-step** : Exécution étape par étape
- **all** : Tous les scénarios avec tous les articles

## 📋 Étapes disponibles pour step-by-step

1. **validation** : Validation de la longueur du texte
2. **extraction** : Extraction d'entités (personnes, organisations)
3. **scoring** : Calcul du score de qualité
4. **angles** : Génération des angles éditoriaux
5. **keywords** : Extraction des mots-clés par angle

## 🔍 Exemples d'utilisation

### Test de debug complet
```python
from playground_debug_mode import DebugPipeline

# Créer le pipeline de debug
debug_pipeline = DebugPipeline()

# Analyser un article avec logs détaillés
article = "Votre article de test ici..."
result = debug_pipeline.run(article, user_id="test_user")
```

### Test étape par étape
```python
# Exécuter seulement jusqu'à l'extraction
results = debug_pipeline.debug_step_by_step(
    article, 
    stop_after="extraction"
)
print(f"Extraction result: {results['extraction']}")
```

### Logging personnalisé
```python
from playground_debug_mode.debug_utils import setup_debug_logging

# Créer un logger personnalisé
logger = setup_debug_logging("/path/to/custom.log")
logger.log_step("Custom step", {"data": "example"})
```

## 🛠️ Dépannage

### Erreur "No module named ai_engine"
Assurez-vous d'exécuter le script depuis la racine du projet ou que le PYTHONPATH inclut la racine.

### Erreur API OpenAI
Vérifiez que `OPENAI_API_KEY` est définie dans vos variables d'environnement.

### Erreur Django SECRET_KEY
Définissez `SECRET_KEY` dans vos variables d'environnement ou utilisez une valeur par défaut pour les tests.

## 📈 Métriques et monitoring

Le playground collecte automatiquement :
- Temps d'exécution pour chaque étape
- Taille des données à chaque étape
- Erreurs et exceptions
- Résultats intermédiaires

Les logs sont sauvegardés dans `logs/` avec timestamp pour analyse ultérieure.

## 🔗 Intégration avec le pipeline principal

Le playground utilise le pipeline principal (`ai_engine.pipeline`) sans modification, ajoutant seulement une couche de debug et de logging.

## 📝 Labels GitHub

Ce module correspond à l'issue avec les labels :
- `debug` : Fonctionnalités de débogage
- `devtools` : Outils de développement  
- `test` : Infrastructure de test