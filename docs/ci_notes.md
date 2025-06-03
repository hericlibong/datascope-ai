Parfait. Voici un encart clair à placer dans `docs/ci_notes.md` pour documenter la gestion des tests d’intégration via `pytest.mark.integration`.

---

### ✅ Gestion des tests unitaires vs tests d’intégration (CI/CD)

Dans ce projet, certains tests (comme les appels aux APIs open data) sont marqués comme **tests d’intégration** avec le décorateur suivant :

```python
@pytest.mark.integration
def test_xyz():
    ...
```

---

### 🧪 Lancer uniquement les tests unitaires (par défaut dans CI/CD)

Pour **exclure** les tests d’intégration (par ex. dans GitHub Actions, GitLab CI, Render, etc.) :

```bash
pytest -m "not integration"
```

---

### 🔄 Lancer **tous les tests** (unitaires + intégration)

En local ou pour une exécution complète :

```bash
pytest
```

---

### 📝 Rappel : déclaration des marqueurs personnalisés

Pour éviter les warnings du type `PytestUnknownMarkWarning`, ajouter dans le fichier `pytest.ini` (déjà présent à la racine du projet) :

```ini
[pytest]
markers =
    integration: test nécessitant un appel réseau ou dépendant d’un service externe
```

---

Souhaites-tu que je génère ce fichier maintenant dans `docs/ci_notes.md` ?
