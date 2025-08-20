# Audit des incohérences - Angles → Datasets

Ce système d'audit permet de vérifier la cohérence entre les angles éditoriaux générés par l'IA et les jeux de données suggérés pour chaque angle.

## Vue d'ensemble

L'audit vérifie automatiquement:

1. **Angles sans datasets** - Détecte les angles éditoriaux qui n'ont aucun dataset associé
2. **Pertinence mots-clés/datasets** - Vérifie si les datasets suggérés contiennent au moins un mot-clé de l'angle
3. **Doublons de datasets** - Identifie les datasets suggérés pour plusieurs angles
4. **Qualité des métadonnées** - Valide la complétude des informations (titre, description, URL, formats)

## Utilisation

### Exécution via script autonome

```bash
# Depuis la racine du projet
python scripts/run_audit.py
```

### Exécution via pytest

```bash
# Test complet d'audit
USE_SQLITE_FOR_TESTS=1 python -m pytest ai_engine/tests/test_audit_angles_datasets.py::test_audit_angles_datasets_consistency -v -s

# Tous les tests d'audit
USE_SQLITE_FOR_TESTS=1 python -m pytest ai_engine/tests/test_audit_angles_datasets.py -v
```

## Résultats

L'audit génère un rapport détaillé incluant:

```
================================================================================
RAPPORT D'AUDIT - COHÉRENCE ANGLES → DATASETS
================================================================================
Articles testés: 10
Angles générés: 30
Datasets suggérés: 58
Incohérences détectées: 14

⚠️  Incohérences mots-clés/datasets: 2
   - Dataset 'Dataset complètement non pertinent' ne contient aucun mot-clé...

⚠️  Datasets dupliqués: 10
   - Dataset dupliqué https://... trouvé dans: Angle 0, Angle 1, Angle 2

⚠️  Problèmes de métadonnées: 2
   - Formats manquants pour: 'Dataset X'
   - URL source invalide pour: 'Dataset Y'
```

## Articles de test

Le système teste sur 10 articles représentatifs couvrant différents domaines:

1. **Environnement** - Émissions CO₂ secteur aérien
2. **Économie** - Taux de chômage aux US
3. **Transport** - Accidents de la route en France
4. **Agriculture** - Prix alimentaires mondiaux
5. **Santé** - Dépenses santé publique Europe
6. **Énergie** - Énergies renouvelables
7. **Emploi** - Chômage des jeunes en Espagne
8. **Immobilier** - Prix logement au Canada
9. **Environnement** - Biodiversité marine Méditerranée
10. **Technologie** - Transformation digitale entreprises

## Types d'incohérences détectées

### 1. Angles sans datasets
- **Problème**: Un angle n'a aucun dataset associé
- **Impact**: L'utilisateur ne peut pas explorer cet angle
- **Solution**: Améliorer les connecteurs ou les mots-clés

### 2. Datasets non pertinents
- **Problème**: Dataset ne contient aucun mot-clé de l'angle
- **Impact**: Suggestions non utiles pour le journaliste
- **Solution**: Améliorer l'algorithme de matching

### 3. Doublons inappropriés
- **Problème**: Même dataset suggéré pour plusieurs angles
- **Impact**: Redondance, manque de diversité
- **Solution**: Système de déduplication intelligent

### 4. Métadonnées incomplètes
- **Problème**: Titre, description, URL ou formats manquants
- **Impact**: Expérience utilisateur dégradée
- **Solution**: Validation côté connecteurs

## Intégration continue

Ce système d'audit peut être intégré dans:

- **Tests automatisés** - Validation en continu
- **Pipeline CI/CD** - Blocage si dégradation qualité
- **Monitoring** - Alertes sur seuils d'incohérences
- **Rapports qualité** - Suivi d'amélioration

## Extension

Le système peut être étendu pour auditer:

- Pertinence des visualisations suggérées
- Qualité des sources LLM vs connecteurs
- Cohérence linguistique (FR/EN)
- Performance des différents connecteurs
- Évolution qualité dans le temps