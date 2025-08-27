Here’s the short doc (in **English**) to close **#73 — 4bis.6 \[LLM+DOC] Unified Output (LLM-only)**.
Drop it at: `backend/docs/api_unified_output.md`.

---

# API Changelog — Unified Output (LLM-only)

**Issue:** `#73 — 4bis.6 [LLM+DOC] Normalize results (unified output)`
**Milestone:** `4bis – Fast deployment (Reliable LLM + Documentation)`
**Goal (revised):** Deliver a clean, **LLM-only** API output with a **unified shape** across items; silence connector logs.

---

## 1) Scope & Non-Goals

**In scope**

* Disable connectors at runtime (LLM-only results).
* Always expose `link`, `source`, and optional `validation` fields for items returned by the API.
* Replace noisy `print` traces with structured logging (silent by default).

**Out of scope**

* DB schema changes (none required).
* Re-enabling/rewriting connectors (post-4bis).

---

## 2) Settings

`datascope_backend/settings.py`

```python
CONNECTORS_ENABLED = False          # LLM-only mode by default
DATASCOPE_LOG_LEVEL = "WARNING"     # Optional; set to "DEBUG" for local traces
```

* Flip `CONNECTORS_ENABLED=True` to restore historical connector calls (for later phases).

---

## 3) Pipeline behavior

**File:** `ai_engine/pipeline.py`

* **Connectors bypass**

  ```python
  if CONNECTORS_ENABLED:
      connectors_sets = run_connectors(...)
  else:
      connectors_sets = [[] for _ in range(len(keywords_per_angle))]
  ```

  → `datasets` now contain **LLM-derived** items only.

* **Logging**

  * `print(...)` replaced by `logger.debug(...)` under `datascope.ai_engine`.
  * With default `WARNING`, there’s **no output** in production.

* Existing quality gates still apply: **URL validation**, **Trusted re-rank**, **Thematic filter**.

---

## 4) Unified serializers (API contract)

**File:** `analysis/serializers.py`

### Datasets

`DatasetSuggestionSerializer` now guarantees:

* `link` (unified) — prefers `source_url`, falls back to `link`.
* `source` (unified) — prefers `source_name`, falls back to `source`.
* `validation` (optional) — surfaced when `?validate=true` was used.

Returned fields (excerpt):

```json
{
  "title": "...",
  "description": "...",
  "link": "https://…",          // unified
  "source": "INSEE",            // unified
  "validation": {               // optional
    "status": "ok|redirected|not_found|error",
    "http_status": 200,
    "final_url": "https://…",
    "error": null
  },
  "found_by": "LLM",
  "formats": [],
  "organisation": null,
  "licence": null,
  "last_modified": "",
  "richness": 0
}
```

### Sources (LLM)

`LLMSuggestionSerializer` keeps native fields **and** adds mirrors for legacy UIs:

* `link`, `source` (native)
* `source_url` (mirror of `link`)
* `source_name` (mirror of `source`)
* `validation` (optional)

Example:

```json
{
  "title": "…",
  "description": "…",
  "link": "https://…",
  "source": "OECD",
  "source_url": "https://…",   // mirror
  "source_name": "OECD",       // mirror
  "validation": { ... }        // optional
}
```

### Angle resources structure (unchanged)

```json
{
  "index": 0,
  "title": "…",
  "description": "…",
  "keywords": ["…"],
  "datasets": [ /* LLM-only items with unified fields */ ],
  "sources":  [ /* LLM sources with mirrors + validation */ ],
  "visualizations": [ /* unchanged */ ]
}
```

---

## 5) Backward compatibility

* No DB migrations.
* Legacy keys for sources (`source_url`, `source_name`) are **mirrored**.
* Datasets now expose `link`/`source` **consistently**; older consumers reading only `link`/`source` are covered.

---

## 6) Tests (light)

* A minimal smoke test can assert that with `CONNECTORS_ENABLED=False`:

  * No connector items appear in `datasets`.
  * `datasets[i]` and `sources[i]` include **`link`** and **`source`**.
  * `validation` appears when `?validate=true` is used.

---

## 7) Definition of Done

* `CONNECTORS_ENABLED=False` by default → **LLM-only** outputs.
* Serializers return **unified fields** (`link`, `source`, optional `validation`).
* Connector `print` logs no longer appear; pipeline uses `logger.debug` (silent by default).
* Existing quality controls (validation/trusted/theme) remain active.

---
