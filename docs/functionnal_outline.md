# 📑 Functional & Technical Outline — DataScope AI

This outline defines the structure and key functional/technical components of the DataScope AI platform. It serves as a lightweight specification document to guide development and maintain coherence across modules.

---

## 📌 1. Project Overview

- **Project Name**: DataScope AI
- **Goal**: Help journalists identify the data potential in articles using AI and NLP pipelines.
- **Target Users**: Journalists, editors, non-technical content creators.
- **Nature**: Internal tool (but structured like a real product).
- **Legacy**: This project is a full reimplementation of the MVP [datascope_project](https://github.com/hericlibong/datascope_project), built in Flask.

---

## 📌 2. Core Functionalities

### 🔍 Article Analysis Pipeline
- Paste or upload article (`.txt`, `.pdf`, `.docx`)
- Automatic language detection (FR/EN)
- Length validation (min/max word count)
- Extract key entities (named entities, dates, quantities)
- Compute datafication score
- Generate editorial angle suggestions
- Recommend open datasets relevant to article topic
- Propose possible data visualizations

### 📤 Export & Persistence
- Download analysis (Markdown / JSON)
- Store results per user (history page)
- Retrieve past analyses

### 🗣️ Feedback Module
- Structured feedback form (4 questions + free comment)
- Admin dashboard to view and export feedbacks

### 👤 User Management
- Simple account creation and login (email)
- Admin privileges (for feedback + user access)

---

## 📌 3. Multilingual Support

### Interface
- Full FR / EN switch via i18n (React-level)

### Content analysis
- Texts in French and English supported natively via LangChain
- Prompts adapted per language (but not hardcoded routing as in SpaCy)
- LLM handles multi-language input

---

## 📌 4. Backend Technical Architecture

The backend of DataScope AI is the backbone of its logic, orchestrating user management, article submission and processing, results storage, and communication with the AI engine.

#### ⚙️ Core Technologies

- **Framework**: Django
- **API Layer**: Django REST Framework (DRF)
- **Database**: PostgreSQL
- **Auth**: Token-based authentication (JWT or DRF tokens), with role-based access (standard user vs admin)
- **Deployment**: Dockerized, with GitHub Actions for CI/CD

#### 🧩 Application Structure

The Django project will be organized around modular apps:

- `users` — authentication, profile management, feedback rights
- `analysis` — submission, language detection, preprocessing, scoring
- `ai_engine` — connection to LangChain logic and LLM orchestration
- `history` — storage of results per user, export tracking
- `feedback` — feedback submission and admin view
- `api` — REST endpoints exposed to the frontend (React)

Optional apps may be added later for monitoring, advanced analytics, or admin dashboards.

#### 🔁 Article Analysis Flow

1. User submits article (text or file)
2. The backend validates length, language, and file type
3. The article is passed to the LangChain engine via an internal service layer (`ai_engine`)
4. Results are returned and stored in the database
5. The backend exposes results to the frontend via the API

#### 🔐 Authentication & Roles

- **Standard user**: can analyze articles, view history, send feedback
- **Admin user**: can access all feedbacks, download logs, manage users

#### 📦 Storage & File Handling

- Files are temporarily stored (if needed) using Django's file system
- Long-term data is kept in PostgreSQL
  - User credentials and profiles
  - Submitted articles and metadata
  - Analysis results (as JSON)
  - Feedback data

#### 🧪 Testing & Validation

- Backend testing will use `pytest-django` and/or Django’s test framework
- API endpoints will be covered with unit and integration tests
- Linting with `ruff` or `flake8`

### 🧱 Backend
- **Framework**: Django + Django REST Framework
- **Database**: PostgreSQL
- **API**: JSON RESTful, versioned
- **Auth**: Token-based or session-based, role-based permissions

### 🎨 Frontend
- **Framework**: React + Vite
- **Styling/UI**: TailwindCSS + Shadcn UI components
- **State Management**: React Context or Zustand
- **Features**: Article submission, results display, language switch, user auth, history, feedback

---

### 🧠 AI/NLP Pipeline — LangChain

The intelligent analysis engine of DataScope AI is orchestrated using **LangChain**, enabling modular, dynamic and multilingual processing of journalistic texts.

#### 🧩 General Workflow

The analysis process is composed of the following LangChain-driven steps:

1. **Input validation & language detection**
2. **Entity extraction via LLM-based prompt**
3. **Datafication scoring** (based on entity density and structure)
4. **Editorial angle generation**
5. **Dataset recommendation** (via keyword → dataset search)
6. **Visualization suggestion** (one per angle, optional)
7. **Packaging and export formatting**

Each step is handled through **dedicated LangChain chains** to maintain modularity and allow future fine-tuning.

#### 🌍 Multilingual Support (FR / EN)

* The pipeline supports both French and English articles transparently.
* Prompt templates are automatically adapted to match the detected language.
* No separate NLP models are required (unlike traditional NLP stacks such as spaCy).

#### 🧱 Chain Composition

| Step                        | LangChain Component             | Description                                          |
| --------------------------- | ------------------------------- | ---------------------------------------------------- |
| 1. Language detection       | External pre-check              | Handled before invoking LLM (e.g., `langdetect`)     |
| 2. Entity extraction        | `LLMChain`                      | Extracts named entities, dates, numbers, units, etc. |
| 3. Scoring logic            | Custom Python module            | Combines entity density + structure                  |
| 4. Angle generation         | `LLMChain` with prompt template | Produces 3–5 angles per article                      |
| 5. Dataset suggestion       | `LLMChain` + custom agent       | Generates keywords + triggers connector APIs         |
| 6. Visualization suggestion | `LLMChain`                      | Suggests chart types & narrative structure           |
| 7. Output packaging         | Python + LangChain OutputParser | Formats Markdown or JSON blocks for export           |

#### 🔁 Memory and Cache

* **Memory** (LangChain’s built-in Memory modules) may be used to:

  * Keep track of prior analyses for reuse or comparison
  * Improve result consistency within the same session

* **Cache** (optional) may store results of previous LLM calls (e.g., Redis or SQLite) to:

  * Avoid token overuse
  * Enable reproducibility

#### 📉 Cost and Token Optimization

* Prompt length will be optimized to minimize token usage
* Result filtering and trimming will be handled on the Python side after LLM completion
* OpenAI GPT-4 is the default model; fallback or switch possible in future

---


## 📌 5. External Integrations

### 🌐 Open Data API Connectors

A core feature of DataScope AI is the ability to suggest **relevant open datasets** based on the content and editorial angles extracted from a journalistic article. These dataset recommendations go beyond static lists by querying external sources programmatically and dynamically.

#### 🔁 Workflow Summary

1. **Editorial angle analysis**: LLM generates 3–5 refined angles per article.
2. **Keyword extraction**: LangChain extracts context-specific keywords for each angle.
3. **Query generation**: The keywords are used to form structured search queries.
4. **External API calls**: These queries are sent to open data providers.
5. **Filtering and formatting**: The top results are cleaned, ranked, and displayed.

#### 🔍 Targeted Open Data Platforms (Phase 1)

- [data.gouv.fr](https://www.data.gouv.fr) (France)
- [data.europa.eu / Eurostat](https://data.europa.eu)
- [catalog.data.gov](https://catalog.data.gov) (US)

Others may be added progressively.

#### ⚙️ Technical Approach

- Connectors will be implemented as **Python modules** or **LangChain tools**.
- Each connector handles:
  - Endpoint routing
  - API query parameter formatting
  - Response parsing and data transformation
  - Fallback strategy if the service is down or unavailable

#### 📦 Dataset Response Format

Each returned dataset will include:
- `title` (name of the dataset)
- `description` (short summary)
- `link` (direct URL to dataset)
- `source` (origin of the dataset)
- `language` (optional)
- `updated_at` (if provided by API)

These items will be rendered in the UI as interactive and collapsible blocks.

#### 📉 Cost and Latency Management

- A caching layer (optional) may store recent dataset lookups to reduce repeated API calls.
- Timeout and fallback handling will be implemented to prevent UI blocking.



---

## 📌 6. DevOps & CI/CD

- **Dockerized** backend + frontend
- **Deployment**: Render, Fly.io, or lightweight VPS
- **CI/CD**: GitHub Actions
  - Linting, testing, and deploy steps
- **Monitoring**: optional Sentry + logging to file or DB

---

## 🧪 Testing Strategy

- **Coverage Goal**: 80%+
- **Tools**:
  - Backend: Pytest + pytest-cov
  - Frontend: Vitest or Jest
  - Linting: Ruff / Flake8 (backend), ESLint (frontend)

---

## 📎 Notes

- Prompt design and chaining logic will be developed iteratively.
- UI/UX design will be aligned with feedback during Phase 6.

