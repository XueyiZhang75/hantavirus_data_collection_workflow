# Disease Relevance Gating

This document describes the deterministic disease relevance guardrail added to
the data collection workflow. The guardrail prevents evidence about an
incompatible disease from being accepted as records for the active task disease.

## Purpose

The workflow may search broad public web sources. A source can contain useful
case, death, date, or location signals while still describing the wrong disease.
For example, a Shanghai COVID-19 article can contain case and death counts, but
it must not become a Hantavirus disease record.

The guardrail adds disease checks at each existing workflow layer:

1. Source metadata screening
2. Document quality screening
3. Evidence chunk data-presence flagging
4. Structured extraction eligibility
5. Schema validation and repair
6. Record normalization
7. Final package and diagnostics export

No graph topology is changed. The checks are implemented inside existing nodes.

## Status Values

Disease relevance assessments use these main statuses:

| Status | Meaning |
|---|---|
| `target_disease_match` | The text explicitly matches the active task disease or one of its aliases. |
| `related_context_only` | The text has related context but should not directly generate records. |
| `ambiguous_disease` | The text mixes target and incompatible disease signals or lacks enough clarity. |
| `unrelated_disease` | The text primarily matches an incompatible disease and not the target disease. |
| `insufficient_text` | There is not enough text to assess disease relevance. |

Record compatibility uses:

| Status | Meaning |
|---|---|
| `compatible` | The record and evidence are compatible with the task disease. |
| `incompatible_disease` | The record or evidence names an incompatible disease. |
| `ambiguous_disease` | The record needs human review because disease evidence is unclear or mixed. |

## Source Gate

Source relevance uses only source metadata that comes from the source itself or
the search result, such as title, snippet, publisher, domain, URL, source type,
and notes.

It does not treat `query_used`, expected output fields, or user request text as
proof of disease relevance. This prevents a broad query such as `HFRS Shanghai`
from making a COVID-19 source appear relevant to a hantavirus task.

If the source metadata is clearly unrelated to the active disease, source
credibility sets the final source role to `excluded`, marks it not ready for
fetch, and records the reason.

## Document Gate

After fetch and parse, document text is assessed against the active task disease.
If a parsed document is otherwise usable but describes an incompatible disease,
the document quality status becomes `not_task_relevant`, and
`not_extractable_for_task_disease` is set to `true`.

## Chunk Gate

Evidence chunks are assessed before data-presence signals are allowed to drive
extraction. A chunk that contains counts, deaths, dates, or locations but names
only an incompatible disease is suppressed:

- `contains_target_data` becomes `false`
- `data_types` is cleared
- `extraction_eligible_for_task_disease` becomes `false`
- `disease_relevance_status` records the reason

## Extraction Gate

Structured extraction skips chunks unless they are eligible for the task disease.
This applies to both rule-based extraction and optional LLM structured
extraction.

The LLM extraction prompt also requires the model to return an empty records
list when the evidence names only an incompatible disease. The LLM is not
allowed to relabel incompatible evidence as the active task disease.

## Validation And Normalization Gates

Schema validation reassesses each raw record using the record fields and its
evidence quote. Incompatible records are rejected with:

- `record_disease_compatibility_status`
- `record_disease_compatibility_reason`
- `record_disease_compatibility_reject`
- `validation_errors` containing `disease_mismatch`

Normalization performs the same defensive check on validated records. If an
incompatible record reaches normalization, it is quarantined in
`disease_mismatch_records` and not included in `normalized_records`.

## Diagnostics

Each configured run exports:

`outputs/sessions/<session_id>/diagnostics/disease_relevance_summary.json`

The summary is also included in:

- `diagnostics/workflow_summaries.json`
- `workflow_run_summary.json`
- `collection/final_package.json`
- `workflow_console/hdc_workflow_console_summary.json`

Important fields include:

| Field | Meaning |
|---|---|
| `target_disease` | Active task disease used by the guardrail. |
| `target_group` | Internal disease group used for deterministic matching. |
| `source_status_counts` | Source-level disease relevance statuses. |
| `document_status_counts` | Document-level disease relevance statuses. |
| `chunk_status_counts` | Evidence chunk disease relevance statuses. |
| `record_compatibility_status_counts` | Record-level compatibility statuses. |
| `rejected_incompatible_record_count` | Raw records rejected for incompatible disease evidence. |
| `normalized_incompatible_record_count` | Incompatible records that reached normalized output. This should remain `0`. |

## Offline Determinism

The disease relevance guardrail does not require internet access, API keys, live
search, or real LLM calls. It is deterministic and covered by offline tests.

