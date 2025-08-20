# Score de correspondance angle ↔ jeu de données

## Vue d'ensemble

Le système de scoring évalue la cohérence entre les angles éditoriaux et les jeux de données suggérés, permettant de filtrer automatiquement et d'alerter sur la pertinence des datasets.

## Fonctionnalités

### 1. Score de correspondance (0.0 - 1.0)

Le score est calculé en combinant trois critères :
- **Chevauchement des mots** (40%) : Mots significatifs communs entre l'angle et le dataset
- **Correspondance des mots-clés** (30%) : Présence des mots-clés extraits de l'angle
- **Analyse thématique** (30%) : Détection de patterns thématiques communs

### 2. Alertes visuelles

- ✅ **Excellente** (>= 0.7) : Correspondance forte
- ⚠️ **Modérée** (0.4-0.69) : Vérification recommandée
- ❌ **Faible** (< 0.4) : Dataset possiblement non pertinent

### 3. Filtrage automatique

Le pipeline applique automatiquement :
- **Seuil minimum** : Score >= 0.1 (configurable)
- **Limite par angle** : Maximum 10 datasets (configurable)
- **Tri par pertinence** : Datasets les mieux notés en premier

## Utilisation

### Dans le pipeline principal

Le scoring est intégré automatiquement :

```python
# Le pipeline calcule automatiquement les scores
packaged, markdown, score_10, angle_resources = run(article_text)

# Chaque dataset a maintenant un match_score
for angle_resource in angle_resources:
    for dataset in angle_resource.datasets:
        print(f"{dataset.title}: {dataset.match_score:.3f}")
```

### Utilisation directe

```python
from ai_engine.angle_dataset_scoring import (
    compute_angle_dataset_match_score,
    get_match_quality_alert,
    filter_datasets_by_quality
)

# Calculer un score
score = compute_angle_dataset_match_score(angle, dataset, keywords)

# Obtenir une alerte
alert = get_match_quality_alert(score)
print(f"{alert['icon']} {alert['message']}")

# Filtrer des datasets
kept, filtered = filter_datasets_by_quality(
    datasets, 
    min_score=0.3, 
    max_datasets=5
)
```

## Configuration

Les paramètres de filtrage peuvent être ajustés dans `pipeline.py` :

```python
MIN_MATCH_SCORE = 0.1  # Seuil minimum
MAX_DATASETS_PER_ANGLE = 10  # Limite par angle
```

## Base de données

Le champ `match_score` est persisté dans le modèle Django `DatasetSuggestion` et peut être utilisé pour :
- Tri dans l'interface utilisateur
- Analyses de qualité des suggestions
- Statistiques de performance du système