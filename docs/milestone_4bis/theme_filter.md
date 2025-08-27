Voici la documentation prête à déposer dans `backend/docs/theme_filter.md` (en **anglais**).

---

# Thematic Coherence Filter — LLM Outputs

**Issue:** `#69 — 4bis.3 [LLM] Add a thematic coherence filter`
**Milestone:** `4bis – Fast deployment (Reliable LLM + Documentation)`
**Final objective:** Ensure LLM-proposed datasets & sources are **on-topic** with the angle (title + keywords), reducing false positives (e.g., *“moustique tigre” → El Tigre volcano*, *crime data LA* for a French employment angle) **without heavy machinery**.

---

## 1) Scope & Non-Goals

**In scope**

* Lightweight **local** scoring (no external calls, no models) to detect off-topic LLM suggestions.
* **Soft penalization** by default; optional **strict** mode to drop off-topic LLM items.
* Works for:

  * **LLM datasets** (i.e., datasets built via `_llm_to_ds(...)` → `found_by == "LLM"`),
  * **LLM sources** (documentation/links block).

**Out of scope**

* Any changes to CONNECTOR outputs (kept intact in this issue).
* Embeddings/semantic search/LLM classifiers.
* DB schema changes or background jobs.

---

## 2) Settings

Add (or confirm) in `datascope_backend/settings.py`:

```python
THEME_FILTER_SOFT_PENALTY = 0.15      # multiplicative penalty for off-topic (soft mode)
THEME_FILTER_STRICT_DEFAULT = False   # if True, drop off-topic LLM items by default
THEME_FILTER_MIN_UNIGRAM_HITS = 2     # minimum unigram overlaps if no bigram match
```

Tuning:

* Increase `THEME_FILTER_SOFT_PENALTY` (e.g., 0.20–0.30) to push off-topic items further down.
* Adjust `THEME_FILTER_MIN_UNIGRAM_HITS` if topics are too broad/narrow.

---

## 3) Design Overview

**Where:** `backend/ai_engine/pipeline.py`, inside `run(...)`, **per angle**, after the URL validation hook and before assembling `AngleResources(...)`.

### Angle signature (theme)

* Build a **token signature** from:

  * `angle.title`
  * the first keywords set: `keywords_per_angle[idx].sets[0].keywords`
* Tokenization: lowercase, split on `\W+`, keep tokens `len >= 3`.
* Construct:

  * `angle_unigrams`: set of tokens,
  * `angle_bigrams`: adjacent pairs of tokens.

### Item scoring

For each LLM item (datasets from LLM + sources):

* Gather text: `title + description + source_name + organization + tokens from URL path`.
* Tokenize and build item unigrams/bigrams.
* An item is **off-topic** if:

  * **no bigram** overlap with angle **AND**
  * `unigram_hits < THEME_FILTER_MIN_UNIGRAM_HITS`.

### Weights & ranking

* **Soft**: off-topic → `theme_weight = 1.0 - THEME_FILTER_SOFT_PENALTY`; on-topic → `1.0`.
* **Strict**: if enabled → off-topic LLM items are **dropped** (CONNECTOR items are never dropped/penalized here).
* Combine with Trusted re-ranking (issue #68):

  * `final_weight = trusted_weight * theme_weight`
  * Stable sort by `final_weight` (descending).

**Notes**

* If URL validation is enabled, the trusted re-rank already uses the `final_url` when present.
* The thematic filter is **purely local** (regex tokenization), fast, and deterministic.

---

## 4) Pipeline Changes (minimal)

**Signature (extended):**

```python
def run(
    article_text: str,
    user_id: str = "anon",
    validate_urls: bool = False,
    filter_404: bool | None = None,
    theme_strict: bool | None = None,   # NEW (optional)
) -> tuple[AnalysisPackage, str, float, list[AngleResources]]:
```

**Behavior:**

* If `theme_strict is None`, it falls back to `THEME_FILTER_STRICT_DEFAULT`.
* Builds the angle signature (`unigrams` + `bigrams`).
* For each LLM item, computes `(theme_weight, off_theme)` and:

  * **Soft**: multiplies the item’s trusted weight by `theme_weight`.
  * **Strict**: drops the item when `off_theme is True`.
* Final ordering: stable sort by the **combined** weight.

CONNECTOR items remain untouched (weight `1.0` for the theme filter), as the biggest incoherences from connectors will be addressed separately.

---

## 5) Public API

* No new endpoint or query param was added for this issue.
* `theme_strict` can be controlled **programmatically** when calling `pipeline.run(...)`.
* Default behavior is **soft penalization** (no hard filtering).

*(If needed later, we can expose `?theme_strict=true` in `analysis/views.py` with the same pattern used for `?validate=true`.)*

---

## 6) Tests (unit, fast)

**File:** `backend/ai_engine/tests/test_theme_filter.py`

We verify:

1. **Soft mode:** an on-topic item (e.g., *“Aedes albopictus (moustique tigre)”*) is ranked **before** an off-topic item (e.g., *“El Tigre volcano…”*). No deletions occur in soft mode.
2. **Strict mode:** off-topic **LLM** items are **removed** from outputs; CONNECTOR datasets (even if off-topic) remain as-is (not filtered by this issue).

All tests pass.

---

## 7) Interaction with Other Features

* **URL Validator (4bis.1):** independent, but complementary; you can combine `?validate=true` with the thematic filter for maximum quality.
* **Trusted Sources (4bis.2):** weights are **multiplied**; an item both trusted and on-topic remains highly ranked, while off-topic items are pushed down.

---

## 8) Files Touched

* `ai_engine/pipeline.py` → extended `run(...)` and added local helpers (tokenization, scoring, weighting, sort).
* Tests: `ai_engine/tests/test_theme_filter.py`

No migrations. No new dependencies. No DB writes.

---

## 9) Definition of Done

* Thematic filter live in `pipeline.run(...)`:

  * On-topic/off-topic scoring applied to **LLM datasets** and **LLM sources**.
  * Soft penalization by default; strict mode available in code.
  * Combined with Trusted re-ranking for final order.
* Unit tests green (soft ordering; strict removal of off-topic LLM results).
* No changes required to API/DB for this issue.

---

*(Optional future work: expose `?theme_strict=true` in the API; allow lightweight language-aware boosts if needed.)*
