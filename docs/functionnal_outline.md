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

## 📌 4. Technical Architecture (Planned)

### 🧠 AI/NLP Pipeline
- **LangChain**-orchestrated chains
  - Entity extraction
  - Prompt generation for angles, datasets, visualizations
- **LLM Provider**: OpenAI (GPT-4), possible fallback later
- **Cache**: Optional (to avoid reprocessing similar texts)
- **Memory**: LangChain memory object or DB-layer persistence

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

## 📌 5. External Integrations

- **Open Data APIs**:
  - `data.gouv.fr`
  - `eurostat`
  - (others to be added later)
- **Dataset connectors**:
  - Dynamically query endpoints with generated keywords
  - Parse and present direct links to matching datasets

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

