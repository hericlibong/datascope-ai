

---

# URL Validation — LLM Suggestions (Datasets & Sources)

**Issue:** `#66 — 4bis.1 [LLM] Implement a link validator (datasets/sources)`
**Milestone:** `4bis – Fast deployment (Reliable LLM + Documentation)`
**Final objective:** Ensure that links proposed by the LLM (datasets & documentation) are **valid and usable** by (1) validating HTTP reachability, (2) following redirects, and (3) removing 404s (or flagging errors) before exposing results to users.

---

## 1) Scope & Non-Goals

**In scope**

* Lightweight, synchronous URL validation for LLM outputs.
* Automatic redirect following and final URL replacement.
* Optional removal of `404/410` suggestions from API responses.
* Minimal changes; no DB schema change.

**Out of scope**

* Background jobs / queues (e.g., Celery).
* Persisting validation results to DB (runtime-only for MVP).
* Heavy retry/backoff strategies.

---

## 2) Design Overview

### New service

* **File:** `backend/ai_engine/services.py`
* **Fn:** `validate_url(url: str) -> dict`
* **Behavior:**

  * Try `HEAD` (`allow_redirects=True`); fallback to `GET` if `HEAD` is blocked (405/403).
  * Return a normalized payload:

    ```json
    {
      "input_url": "<original>",
      "status": "ok" | "redirected" | "not_found" | "error",
      "http_status": 200,
      "final_url": "<resolved or null>",
      "error": null
    }
    ```
  * Classification rules:

    * `ok`: 2xx, no redirect
    * `redirected`: 2xx with redirect(s)
    * `not_found`: 404 or 410
    * `error`: anything else (4xx/5xx), or network issues (timeout, SSL, etc.)

### Pipeline hook

* **File:** `backend/ai_engine/pipeline.py`
* **Signature (extended):**

  ```python
  run(article_text: str, user_id: str = "anon",
      validate_urls: bool = False, filter_404: bool | None = None)
  ```
* **When `validate_urls=True`:**

  * Annotate each dataset/source with `obj.validation = {...}` (runtime only).
  * If status is `redirected` and `final_url` exists, **replace** `source_url/link` with the final URL.
  * If `filter_404` is `True`, **drop** items whose validation status is `not_found`.

### API flag

* **File:** `backend/analysis/views.py`
* **Endpoint:** `POST /api/analysis/?validate=true`

  * Reads `validate` query param (`true/1/yes/on`) and passes `validate_urls=True` to the pipeline.
  * Response structure preserved; items may carry `validation` if serializers expose it.

### Optional serializer exposure

* **File:** `backend/analysis/serializers.py`
* Add `validation = SerializerMethodField(required=False)` to dataset/source serializers to **surface** validation details to the UI when present.
  *(Optional for MVP; filtering still works without exposing details.)*

---

## 3) Settings

Add to `datascope_backend/settings.py` (already done):

```python
URL_VALIDATION_TIMEOUT = 5
URL_VALIDATION_USER_AGENT = "DatascopeAI/validator"
URL_VALIDATION_FILTER_404 = True
```

* `URL_VALIDATION_FILTER_404`: If `True`, 404/410 items are removed from results when validation is enabled.

---

## 4) Public API Usage

### Request

```http
POST /api/analysis/?validate=true
Content-Type: multipart/form-data

text=<article content>  # or file=<.txt|.md>
```

### Response (excerpt)

```json
{
  "message": "Analyse réussie",
  "article_id": 123,
  "analysis_id": 456,
  "angle_resources": [
    {
      "index": 0,
      "title": "…",
      "datasets": [
        {
          "title": "…",
          "source_url": "https://final.resolved.url",
          "validation": {
            "status": "ok",
            "http_status": 200,
            "final_url": "https://final.resolved.url",
            "error": null
          }
        }
      ],
      "sources": [ /* same idea */ ]
    }
  ]
}
```

**Notes**

* If `validate=true` and filtering is enabled, `not_found` items are **absent** from `datasets`/`sources`.
* When exposed, `validation.status` can be used by the UI for badges/warnings.

---

## 5) Files touched (minimal)

* `ai_engine/services.py` → **added** `validate_url()`
* `ai_engine/pipeline.py` → **extended** `run(...)`, added validation hook
* `analysis/views.py` → **reads** `?validate=true` and forwards to pipeline
* `analysis/serializers.py` → *(optional)* expose `validation` to the UI

No DB migrations. No changes to routing.

---

## 6) Tests (unit, fast)

### Service

* **File:** `backend/ai_engine/tests/test_url_validator.py`
* Cases: `200`, `301→200`, `404`, `500`, `timeout`, and `HEAD 405 → GET 200` fallback (mocked with `responses`).

### API flag

* **File:** `backend/analysis/tests/test_analysis_validate_flag.py`
* Verifies that:

  1. `?validate=true` is passed as `validate_urls=True` to the pipeline.
  2. The JSON response **does not contain** 404 items when validation is enabled.

All tests pass.

---

## 7) Operational Notes

* **Backward compatible:** Without `?validate=true`, behavior is unchanged.
* **Performance:** Synchronous HTTP checks; a small per-run cache prevents re-validating duplicate URLs in the same pipeline call.
* **Future extensions (phase 2, optional):**

  * Persist `final_url` and/or `validation` in DB.
  * Add a batched management command or background queue.

---

## 8) Definition of Done

* URL validator service behaves as specified.
* Pipeline integrates validation and optional 404 filtering.
* API flag activates the feature.
* Unit tests green (service + API flag).
* (Optional) Validation details surfaced to UI via serializers.

---

