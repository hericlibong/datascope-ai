## 📅 Phase 0 : Préparation & Conception (1 semaine)

🔹 **Milestone : `0-preparation`**

| Issue | Description                                                                | Labels                     | Durée   |
| ----- | -------------------------------------------------------------------------- | -------------------------- | ------- |
| #0.1  | Rédaction du cahier des charges technique et fonctionnel                   | `specs`, `planning`        | 2 jours |
| #0.2  | Choix des technologies (versions Django, React, LangChain, DB, stockage)   | `architecture`, `decision` | 1 jour  |
| #0.3  | Définition des entités métier (modèle `Article`, `Analysis`, `User`, etc.) | `database`, `models`       | 2 jours |
| #0.4  | Organisation du nouveau repo GitHub + tableau projet                       | `setup`, `project-board`   | 1 jour  |

---

## ⚙️ Phase 1 : Backend API Django (2 à 3 semaines)

🔹 **Milestone : `1-backend-api`**

| Issue | Description                                                         | Labels                 | Durée   |
| ----- | ------------------------------------------------------------------- | ---------------------- | ------- |
| #1.1  | Initialisation du projet Django + apps (`analysis`, `users`, `api`) | `setup`, `django`      | 2 jours |
| #1.2  | Modèles de données : articles, résultats, feedbacks, utilisateurs   | `models`, `database`   | 2 jours |
| #1.3  | API REST avec DRF : analyse, upload, résultats                      | `api`, `upload`, `DRF` | 4 jours |
| #1.4  | Authentification sécurisée (token ou session + rôle admin)          | `auth`, `security`     | 2 jours |
| #1.5  | Intégration tests backend (pytest + coverage)                       | `tests`, `qa`          | 2 jours |

🔸 Option bonus : Swagger/OpenAPI auto-documentation.

---

## 🧠 Phase 2 : Intégration LangChain IA (2 semaines)

🔹 **Milestone : `2-langchain-engine`**

| Issue | Description                                                           | Labels                                  | Durée   |
| ----- | --------------------------------------------------------------------- | --------------------------------------- | ------- |
| #2.1  | Création des chaînes LangChain : extraction, prompt, résultats        | `langchain`, `LLM`, `pipeline`          | 3 jours |
| #2.2  | Pipeline complet IA : extractions + angles + datasets + visualisation | `NLP`, `generation`, `OpenAI`, `agents` | 5 jours |
| #2.3  | Mémoire et cache de résultats (redis/sqlite/chroma ?)                 | `memory`, `cache`, `optimization`       | 2 jours |
| #2.4  | Connecteurs vers bases ouvertes (Data.gouv, Eurostat, etc.)           | `API`, `datasource`, `scraper`          | 3 jours |

---

## 🎨 Phase 3 : Frontend React (2 à 3 semaines)

🔹 **Milestone : `3-frontend-ui`**

| Issue | Description                                              | Labels                        | Durée   |
| ----- | -------------------------------------------------------- | ----------------------------- | ------- |
| #3.1  | Initialisation avec Vite/React + Tailwind + Shadcn UI    | `frontend`, `setup`           | 2 jours |
| #3.2  | Écran d’analyse (input texte ou fichier, options langue) | `form`, `upload`, `UX`        | 3 jours |
| #3.3  | Page résultats : score, entités, angles, visualisations  | `result`, `data-viz`, `react` | 4 jours |
| #3.4  | Système de feedback interactif                           | `feedback`, `form`            | 2 jours |
| #3.5  | Authentification (JWT / session)                         | `auth`, `routing`, `context`  | 2 jours |

---

## 📦 Phase 4 : Export, historique, feedbacks (1 à 1,5 semaine)

🔹 **Milestone : `4-features-extension`**

| Issue | Description                                      | Labels                    | Durée   |
| ----- | ------------------------------------------------ | ------------------------- | ------- |
| #4.1  | Export Markdown / JSON des analyses              | `export`, `download`      | 2 jours |
| #4.2  | Affichage historique utilisateur (dashboard)     | `dashboard`, `user`       | 2 jours |
| #4.3  | Feedback utilisateur structuré et administration | `feedback`, `admin`, `UX` | 3 jours |

---

## 🚀 Phase 5 : Déploiement scalable & CI/CD (1 semaine)

🔹 **Milestone : `5-deployment`**

| Issue | Description                                             | Labels                          | Durée   |
| ----- | ------------------------------------------------------- | ------------------------------- | ------- |
| #5.1  | Dockerisation backend + frontend (images séparées)      | `docker`, `build`               | 2 jours |
| #5.2  | Déploiement sur Render ou autre (VPS, GCP, AWS)         | `deployment`, `render`, `cloud` | 2 jours |
| #5.3  | Pipeline GitHub Actions : lint, tests, déploiement auto | `CI/CD`, `workflow`, `test`     | 2 jours |
| #5.4  | Monitoring, logs, alertes (Sentry, UptimeRobot, etc.)   | `monitoring`, `logs`            | 1 jour  |

---

## 🧪 Phase 6 : Tests utilisateurs & itérations finales (1 semaine)

🔹 **Milestone : `6-testing-and-polish`**

| Issue | Description                                          | Labels                      | Durée   |
| ----- | ---------------------------------------------------- | --------------------------- | ------- |
| #6.1  | Tests utilisateurs ciblés (journalistes, rédactions) | `test`, `ux`                | 2 jours |
| #6.2  | Ajustements interface & feedbacks                    | `refactor`, `ux`, `minor`   | 2 jours |
| #6.3  | Communication publique : page projet, documentation  | `release`, `docs`, `public` | 2 jours |

---
