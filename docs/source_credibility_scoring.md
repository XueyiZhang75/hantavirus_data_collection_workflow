# Source Credibility Scoring

This document describes the Stage 6 source credibility layer in the
data collection workflow.

## Goal

Every source registry entry is assigned a deterministic, auditable credibility
assessment and a final source role before downstream content fetch, extraction,
validation comparison, or human review.

The layer is task-aware: the score uses the current collection task, disease
intelligence profile, source strategy metadata, executable source plan metadata,
search provenance, and source metadata such as title, snippet, domain,
publisher, source type, URL, and discovery method.

## Default Behavior

The default path is deterministic and offline-safe.

- It does not require internet access.
- It does not require API keys.
- It does not call an LLM unless explicitly enabled.
- It preserves the existing internal `source_role` field for backward
  compatibility.
- It writes the new final role to `source_role_final`.

## Final Source Roles

`source_role_final` must be one of:

| Final role | Meaning |
|---|---|
| `collection` | Suitable for primary data collection and downstream extraction. |
| `validation` | Held out from collection and reserved for validation comparison. |
| `context` | Useful background, definition, or context source, but not a direct extraction source. |
| `collection_support` | Secondary or supportive source that may help discovery or interpretation but is not ideal as a primary collection source. |
| `search_endpoint` | A search/API endpoint or placeholder source, not a direct extraction target. |
| `excluded` | Not suitable for this task based on disease, location, provenance, or policy. |
| `needs_human_review` | Potentially relevant but ambiguous enough to require source-level review. |

## Score Components

Each assessment contains these component scores:

- `authority_score`
- `local_relevance_score`
- `disease_relevance_score`
- `timeliness_score`
- `geographic_granularity_score`
- `data_granularity_score`
- `machine_readability_score`
- `independence_score`
- `provenance_score`
- `risk_penalty`

The final `credibility_score` is a weighted score from 0 to 1 after applying
`risk_penalty`. The resulting `credibility_level` is one of `high`, `medium`,
`low`, `excluded`, or `needs_review`.

## Human Review Routing

Source-level human review is recommended when the source appears potentially
relevant but has unresolved ambiguity, for example:

- disease-relevant source with unclear location
- disease-relevant source with unclear time window
- low score but potentially relevant metadata
- missing publisher on a relevant source
- disagreement between screening and critic decisions
- explicit `needs_human_review` final role

Validation, context, search endpoint, and excluded sources are not automatically
sent to human review just because they are not collection sources. This avoids
breaking the default offline graph route and keeps source policy separation
explicit.

## Optional LLM Advisory

Optional LLM source credibility review is controlled by:

- `HDC_ENABLE_LLM_SOURCE_CREDIBILITY`
- `HDC_LLM_SOURCE_CREDIBILITY_MAX_SOURCES`
- `HDC_LLM_SOURCE_CREDIBILITY_SOURCE_ID_ALLOWLIST`

The centralized config block is:

```json
"llm": {
  "source_credibility": {
    "enabled": false,
    "max_sources": 6,
    "source_id_allowlist": []
  }
}
```

When enabled, the LLM receives source metadata and the deterministic
assessment. It is advisory only: it must not browse, fetch, create URLs, or
override the deterministic final role policy boundary. If the LLM call fails,
the deterministic assessment remains valid and the failure is recorded in
`warnings`, `llm_failed`, and `llm_error_type`.

## State Fields

Stage 6 adds these state fields:

- `source_credibility_assessments`: one assessment object per source registry entry
- `source_credibility_summary`: run-level counts and risk summaries

Each `source_registry` entry is enriched with:

- `source_role_recommendation`
- `source_role_final`
- `credibility_score`
- `credibility_level`
- component score fields
- `risk_flags`
- `human_review_recommended`
- `human_review_reason`
- `assessment_method`
- optional LLM advisory fields

## Exported Artifacts

Configured workflow runs export:

- `diagnostics/source_credibility_summary.json`
- `diagnostics/source_credibility_assessments.json`
- `diagnostics/workflow_summaries.json`, including `source_credibility_summary`
- `collection/source_registry.json`, with enriched source entries
- `workflow_run_summary.json`, with source credibility summary and artifact paths
- `workflow_console/hdc_workflow_console.html`, with source credibility visible in the run inspector

## Backward Compatibility

The internal `source_role` field remains unchanged for existing graph behavior:

- `data_source`
- `context_source`
- `validation_reserved`
- `search_endpoint`
- `placeholder_source`

Downstream content fetch and historical tests can continue using those internal
roles, while new Stage 6 outputs use `source_role_final` for auditable final
role assignment.

## Not Implemented In Stage 6

Stage 6 does not implement broad crawling, generalized fetch/parse support,
validation-method redesign, generic disease extraction schemas, duplicate
clustering, anomaly detection, human-review decision application, CLI redesign,
notebook redesign, UI redesign, or Stage 7 behavior.
