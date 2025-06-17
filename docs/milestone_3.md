Voici les mêmes tableaux **avec les labels GitHub directement intégrés**, prêts à être utilisés pour ton backlog. Chaque ligne peut être copiée telle quelle dans une issue ou une carte GitHub Project.

---

## 🎨 Milestone 3 — Frontend React (2 à 3 semaines)

### 🔹 Issue #3.1 – Initialisation avec Vite/React + Tailwind + Shadcn UI

| Sous-issue | Description                                                           | Labels                          |
| ---------- | --------------------------------------------------------------------- | ------------------------------- |
| #3.1.1     | Création projet avec Vite.js (`npm create vite@latest`) + TypeScript  | `frontend`, `initialisation`    |
| #3.1.2     | Configuration Tailwind CSS + PostCSS                                  | `frontend`, `style`, `tailwind` |
| #3.1.3     | Intégration Shadcn UI (`npx shadcn-ui@latest init`)                   | `frontend`, `ui`, `shadcn`      |
| #3.1.4     | Création des premiers composants de base (`Layout`, `Card`, `Button`) | `frontend`, `ui`, `components`  |
| #3.1.5     | Configuration du routing (`react-router-dom`)                         | `frontend`, `routing`           |

---

### 🔹 Issue #3.2 – Écran d’analyse (saisie ou upload)

| Sous-issue | Description                                                    | Labels                                     |
| ---------- | -------------------------------------------------------------- | ------------------------------------------ |
| #3.2.1     | Création formulaire principal d’analyse (textarea + fichier)   | `frontend`, `formulaire`, `analyse`        |
| #3.2.2     | Sélecteur de langue (`fr` ou `en`) avec icône + switch         | `frontend`, `lang`, `ui`                   |
| #3.2.3     | Intégration du bouton “Analyser” avec état de chargement       | `frontend`, `ui`, `loader`                 |
| #3.2.4     | Appel au backend via API REST (`/api/analyze`)                 | `frontend`, `api`, `integration`           |
| #3.2.5     | Gestion des erreurs (requête vide, mauvaise extension fichier) | `frontend`, `error-handling`, `formulaire` |

---

### 🔹 Issue #3.3 – Page résultats

| Sous-issue | Description                                                                | Labels                                     |
| ---------- | -------------------------------------------------------------------------- | ------------------------------------------ |
| #3.3.1     | Affichage score de “datafication” sous forme de badge ou jauge             | `frontend`, `score`, `visualisation`       |
| #3.3.2     | Section “Entités identifiées” sous forme de tags ou chips                  | `frontend`, `nlp`, `ui`                    |
| #3.3.3     | Liste des “Angles éditoriaux” générés                                      | `frontend`, `suggestions`, `ui`            |
| #3.3.4     | Suggestions de datasets en tableau avec lien direct                        | `frontend`, `datasets`, `api`              |
| #3.3.5     | Placeholder pour les visualisations recommandées (mock ou Flourish iframe) | `frontend`, `visualisation`, `placeholder` |

---

### 🔹 Issue #3.4 – Système de feedback interactif

| Sous-issue | Description                                             | Labels                        |
| ---------- | ------------------------------------------------------- | ----------------------------- |
| #3.4.1     | Composant “feedback” type emoji/slider ou message libre | `frontend`, `feedback`, `ui`  |
| #3.4.2     | Connexion au backend pour POST feedback utilisateur     | `frontend`, `api`, `feedback` |
| #3.4.3     | Message de remerciement ou accusé de réception feedback | `frontend`, `feedback`, `ux`  |

---

### 🔹 Issue #3.5 – Authentification

| Sous-issue | Description                                                   | Labels                        |
| ---------- | ------------------------------------------------------------- | ----------------------------- |
| #3.5.1     | Page Login simple avec appel API `/auth/token/`               | `frontend`, `auth`, `api`     |
| #3.5.2     | Stockage du token JWT dans `localStorage` ou `sessionStorage` | `frontend`, `auth`, `jwt`     |
| #3.5.3     | Redirection + protection des routes avec `PrivateRoute`       | `frontend`, `auth`, `routing` |
| #3.5.4     | Ajout d’un menu utilisateur avec bouton de déconnexion        | `frontend`, `auth`, `ui`      |

---

Souhaites-tu que je t’exporte tout cela en `.md` prêt à déposer dans ton dépôt GitHub ou ton gestionnaire de tâches ?


### 📑 Chapitre – Issue #3.3.4 : « Fusion des suggestions LLM / connecteurs & champ `found_by` manquant »

---

#### 1. Situation avant correction

| Élément                                            | État initial                                                                                                                        | Conséquence                                                                      |
| -------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| **Pipeline** (`ai_engine/pipeline.py`)             | – Fusionne les datasets des connecteurs avec ceux générés par le LLM.  <br>– Appelle `_llm_to_ds()` qui renseigne `found_by="LLM"`. | OK côté pipeline.                                                                |
| **Schéma Pydantic** (`ai_engine/schemas.py`)       | `DatasetSuggestion` **ne contenait pas** de champ `found_by`.                                                                       | L’attribut était ignoré → inaccessible plus tard.                                |
| **Vue Django** (`analysis/views.py`)               | Lors du `DatasetSuggestion.objects.create(...)`, on faisait `found_by = ds.found_by`.                                               | Levait `AttributeError: 'DatasetSuggestion' object has no attribute 'found_by'`. |
| **Base PostgreSQL** (`analysis_datasetsuggestion`) | La colonne `found_by` existait (VARCHAR 10).                                                                                        | Valeur jamais renseignée → incohérence.                                          |

---

#### 2. Fichiers modifiés

| Fichier                 | Lignes clés                                                                         |                                              |
| ----------------------- | ----------------------------------------------------------------------------------- | -------------------------------------------- |
| `ai_engine/schemas.py`  | Ajout du champ :<br>\`\`\`python<br>found\_by: str                                  | None = None  # "LLM" / "CONNECTOR"<br>\`\`\` |
| `ai_engine/pipeline.py` | Dans `run_connectors()` :<br>`python<br>suggestion.found_by = "CONNECTOR"<br>`      |                                              |
| `analysis/views.py`     | Lors de la création ORM :<br>`python<br>found_by = ds.found_by or "CONNECTOR",<br>` |                                              |

---

#### 3. Étapes de résolution détaillées

1. **Détection de l’erreur**

   * Traceback 500 : `AttributeError: 'DatasetSuggestion' object has no attribute 'found_by'`.

2. **Ajout du champ manquant**

   * Extension du schéma `DatasetSuggestion` pour inclure `found_by`.
   * Aucun impact DB : c’est côté Pydantic uniquement.

3. **Valorisation systématique**

   * Dans `_llm_to_ds()` : `found_by="LLM"` inchangé.
   * Dans `run_connectors()` : attribution explicite `"CONNECTOR"` à chaque suggestion issue d’un connecteur.

4. **Persistance fiable**

   * Vue Django : on lit maintenant `ds.found_by` (toujours présent) et on met une valeur par défaut de secours.

5. **Tests**

   * POST `/api/analysis/` ⇒ JSON renvoie les deux types :

     ```json
     { "found_by": "LLM",        ... }
     { "found_by": "CONNECTOR", ... }
     ```
   * Insertion en base vérifiée (champ non-nul, ≤ 10 car.).

---

#### 4. Résultat

* Plus aucune erreur 500.
* Les suggestions LLM sont correctement taguées et différenciables côté front-end.
* Préparation pour un futur filtrage ou affichage par provenance.

---

> **Prochaine étape** : finaliser l’affichage card-front (badges “AI” / “API”) puis passer à l’implémentation des visualisations (#3.3.5).

