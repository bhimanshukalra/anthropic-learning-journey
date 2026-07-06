# Prep Exercise 3 — Build a Structured Data Extraction Pipeline

> **Source:** Official Claude Certified Architect – Foundations Exam Guide (v0.2, Jun 30 2026), *Preparation Exercises*, pp. 32–33. Content unchanged from v0.1.
> This file records the exercise **verbatim**. Our deeper build guide is
> [`03-structured-data-extraction.md`](03-structured-data-extraction.md).
> **Domains reinforced:** 4 (Prompt Engineering & Structured Output), 5 (Context & Reliability).

## Objective (verbatim)
Practice designing JSON schemas, using `tool_use` for structured output, implementing validation-retry
loops, and designing batch processing strategies.

## Steps (verbatim)
1. **Define an extraction tool** with a JSON schema containing required and optional fields, an enum
   with an "other" + detail string pattern, and nullable fields for information that may not exist in
   source documents. Process documents where some fields are absent and verify the model returns
   `null` rather than fabricating values.
2. **Implement a validation-retry loop:** when Pydantic or JSON schema validation fails, send a
   follow-up request including the document, the failed extraction, and the specific validation error.
   Track which errors are resolvable via retry (format mismatches) versus which are not (information
   absent from source).
3. **Add few-shot examples** demonstrating extraction from documents with varied formats (e.g., inline
   citations vs bibliographies, narrative descriptions vs structured tables) and verify improved
   handling of structural variety.
4. **Design a batch processing strategy:** submit a batch of 100 documents using the Message Batches
   API, handle failures by `custom_id`, resubmit failed documents with modifications (e.g., chunking
   oversized documents), and calculate total processing time relative to SLA constraints.
5. **Implement a human review routing strategy:** have the model output field-level confidence scores,
   route low-confidence extractions to human review, and analyze accuracy by document type and field to
   verify consistent performance.

## How these official steps map to our build
| Official step | Our build (`03-structured-data-extraction.md`) |
|---------------|------------------------------------------------|
| 1 — schema w/ nullable + "other"+detail | `tool_use` schema design, null vs fabrication |
| 2 — validation-retry loop | Pydantic validation + targeted retry |
| 3 — few-shot for format variety | Few-shot examples across document shapes |
| 4 — batch of 100 via Batches API | Batch strategy, `custom_id` failure handling |
| 5 — confidence-based human routing | Field-level confidence → human review |
