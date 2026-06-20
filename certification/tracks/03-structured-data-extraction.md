# Project 03 — Structured Data Extraction Pipeline

> **Maps to:** Exam Scenario 6 + official Preparation Exercise 3
> **Domains:** 4 (Prompt Engineering & Structured Output, 20%) · 5 (Context & Reliability, 15%)
> **Why it matters:** Domain 4 is 20% and this is where the schema/tool_use/validation/batch facts live.

## Objective
Extract structured data from messy unstructured documents (invoices, resumes, lab reports — pick one),
validate with JSON schema, retry intelligently, batch at volume, and route low-confidence cases to humans.

## Tech stack
- Claude API with **tool_use** for structured output. Pydantic (or zod) for validation.
- A folder of varied sample documents — deliberately include some with **missing fields** and some
  with **conflicting numbers**.

## Build steps

### 1. Schema + tool_use for guaranteed structure (Domain 4.3) ⭐
Define an extraction **tool whose input schema is your target schema**. The model "calls" it and you
read the structured args from the `tool_use` response.
- Mix **required** and **optional/nullable** fields.
- Add an **enum with `"other"` + a detail string** for extensible categories, and an `"unclear"` value
  for ambiguous cases.
- Make any field the source might lack **nullable** so the model returns `null` instead of fabricating.
> Key fact: tool_use + JSON schema eliminates **syntax** errors but **not semantic** ones (totals
> that don't sum, values in the wrong field).

### 2. tool_choice control (Domain 2.3 / 4.3)
- `tool_choice: "any"` when the document type/schema is unknown (guarantees *a* tool is called, not text).
- Forced `{"type":"tool","name":"extract_metadata"}` to ensure a specific extraction runs first,
  before enrichment steps in follow-up turns.
- Know `"auto"` lets the model return plain text — wrong when you require structure.

### 3. Validation → retry-with-error-feedback loop (Domain 4.4) ⭐
On validation failure, resend: **original document + the failed extraction + the specific validation
error**. Track outcomes:
- **Resolvable by retry:** format mismatches, structural output errors.
- **NOT resolvable:** the information is simply **absent from the source** (or lives in an external
  doc you didn't provide). Detect these and stop retrying — retries can't invent data.

### 4. Semantic self-validation (Domain 4.4)
Have the schema extract `calculated_total` alongside `stated_total` and flag discrepancies; add a
`conflict_detected` boolean for inconsistent source data; add a `detected_pattern` field so you can
later analyze which constructs cause false positives.

### 5. Few-shot for structural variety (Domain 4.2)
Add 2–4 few-shot examples covering **different document structures** (inline citations vs
bibliographies, narrative descriptions vs tables). This is the most effective fix for empty/null
extraction of fields that *do* exist but appear in an unusual layout. Put **format normalization
rules** in the prompt alongside the strict schema.

### 6. Batch processing strategy (Domain 4.5) ⭐
Submit ~100 docs via the **Message Batches API**:
- Internalize: **50% cheaper, up to 24h, no latency SLA, `custom_id` correlation, no multi-turn tool
  calling in a single request.**
- Use batch for overnight/weekly volume; use the **synchronous** API for anything blocking.
- Handle failures by **resubmitting only the failed `custom_id`s** (chunk oversized docs).
- Compute cadence vs SLA (e.g. 4h submission windows to guarantee a 30h SLA with 24h processing).
- Refine the prompt on a **small sample first** to maximize first-pass success.

### 7. Human review routing + calibration (Domain 5.5) ⭐
- Have the model output **field-level confidence**; calibrate thresholds on a **labeled validation set**.
- Route **low-confidence / ambiguous / contradictory** docs to human review.
- Measure quality with **stratified sampling** of high-confidence extractions.
- **Analyze accuracy by document type and field** — a 97% aggregate can hide a field that's 60%.
  Validate per-segment **before** reducing human review.

## Definition of done (self-check)
- [ ] Extraction returns schema-valid JSON via tool_use with zero syntax errors.
- [ ] Missing fields come back `null`, not fabricated.
- [ ] Retry loop fixes format errors and correctly *gives up* when info is absent.
- [ ] `calculated_total` vs `stated_total` discrepancy detection works.
- [ ] Few-shot improves extraction across varied document layouts.
- [ ] 100-doc batch run with `custom_id` failure resubmission.
- [ ] You can explain why a blocking workflow must NOT use the batch API.
- [ ] Field-level confidence routes low-confidence docs to review; per-field accuracy analyzed.

## Be able to answer
1. Why does tool_use + JSON schema not guarantee a *correct* extraction?
2. When is a retry guaranteed to fail, and how do you detect that case?
3. Why is a 97% aggregate accuracy number dangerous before automating?
4. Give the batch API's four defining constraints and one workflow it's wrong for.
