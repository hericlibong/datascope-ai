Voici la documentation prête à déposer dans `backend/docs/trusted_sources.md` (en **anglais**).

---

# Trusted Sources — Soft Re-Ranking for LLM outputs

**Issue:** `#68 — 4bis.2 [LLM] Create a trusted list of catalogues`
**Milestone:** `4bis – Fast deployment (Reliable LLM + Documentation)`
**Final objective:** Prioritize **institutional, stable and authoritative** catalogues (e.g., INSEE, data.gouv.fr, Eurostat, WHO, OECD, data.gov, CDC, ONS/NHS) in LLM suggestions **without blocking** other valid sources.

---

## 1) Scope & Non-Goals

**In scope**

* Soft preference (re-ranking) for links whose domain is in a **trusted list**.
* Works for both **datasets** and **documentation sources**.
* Compatible with the URL validator (uses `final_url` if available).

**Out of scope (for this issue)**

* Strict filtering mode (hard exclude non-trusted).
* Language-aware boosts (FR vs EN) beyond prompt guidance.
* Any DB migration or background jobs.

---

## 2) Settings

Add or edit in `datascope_backend/settings.py`:

```python
TRUSTED_DOMAINS = [
    # FR/EU
    "data.gouv.fr", "insee.fr", "ec.europa.eu", "eurostat.ec.europa.eu",
    "santepubliquefrance.fr", "ecdc.europa.eu",
    # INTL
    "oecd.org", "who.int", "worldbank.org", "imf.org", "un.org", "unesco.org",
    # US/UK
    "data.gov", "cdc.gov", "data.gov.uk", "ons.gov.uk", "nhs.uk",
]
TRUSTED_SOFT_WEIGHT = 0.15  # small boost, not a hard filter
```

* **How to adjust:**

  * Add/remove domains directly in `TRUSTED_DOMAINS`.
  * Tune the impact via `TRUSTED_SOFT_WEIGHT` (typical range `0.1–0.3`).
* **No regional lock-in:** this list is **qualitative**, not geographic.

---

## 3) Prompt guidance (LLM nudge)

**File:** `backend/ai_engine/chains/llm_sources.py`

* A concise **system message** now instructs the LLM to *prefer trusted institutional catalogues* and to adapt to FR/EN context, **without excluding** other valid domains.
* The message displays a compact hint built from `TRUSTED_DOMAINS` (capped to avoid token bloat).

Result: the LLM naturally proposes more authoritative sources while keeping diversity when relevant.

---

## 4) Pipeline — Soft re-ranking

**File:** `backend/ai_engine/pipeline.py`
**Placement:** After URL validation hook (if enabled), before `AngleResources(...)`.

* Helpers:

  * `_host(url)`: parse netloc.
  * `_is_trusted(host)`: suffix match against `TRUSTED_DOMAINS` (handles subdomains).
  * `_trusted_weight_from_url(url)`: returns `1.0 + TRUSTED_SOFT_WEIGHT` if trusted, else `1.0`.
  * `_pick_url_for_weight(obj)`: prefers `validation.final_url` if present.
* Sorting:

  ```python
  merged_ds.sort(key=lambda ds: _trusted_weight_from_url(_pick_url_for_weight(ds)), reverse=True)
  llm_raw.sort(key=lambda src: _trusted_weight_from_url(_pick_url_for_weight(src)), reverse=True)
  ```
* Python’s sort is **stable** → trusted items move up slightly; others remain in order.

**Compatibility with validator:**
When `validate_urls=True`, a redirected item is weighted using the **final** domain.

---

## 5) Public API

* **No new endpoint or params** added for this issue.
* Behavior visible in `POST /api/analysis/` responses: trusted domains appear **earlier** in each list (`datasets`, `sources`).
* Combine with `?validate=true` to ensure links are valid and redirects resolved.

---

## 6) Tests (unit, fast)

**Files:**

* `backend/ai_engine/tests/test_trusted_rerank.py`

**What we verify:**

1. **Soft re-rank order:** trusted domains (e.g., `insee.fr`, `oecd.org`) appear **before** non-trusted (e.g., `example.com`), with no removals.
2. **Final URL usage:** with `validate_urls=True`, if an URL redirects to a trusted domain (e.g., → `who.int`), the trusted item gets the boost and moves up.

All tests pass.

---

## 7) Operational notes

* **Backward compatible:** If the list is empty or the weight is `0.0`, behavior is essentially unchanged.
* **Editable:** The trusted list can be updated iteratively based on editorial feedback.
* **No DB impact:** All logic is in-memory re-ranking.

---

## 8) Definition of Done

* Trusted list configured via settings.
* LLM nudged to prefer trusted institutional catalogues (bilingual guidance).
* Soft re-ranking applied to datasets & sources in the pipeline.
* Unit tests green: ordering and final-URL behavior validated.

---

*(Optional future work: a `trusted_strict` query flag and/or light language-aware boosts. Not required for #68.)*
