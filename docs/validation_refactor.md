# Validation Refactor

## 1. Purpose

Stage 10 makes validation explicit and auditable for the data collection workflow.
The workflow now records what was compared with what, whether the comparison was
valid, and why a record, field, event cluster, or aggregate did or did not pass
validation.

Validation is deterministic by default. It does not browse, fetch, call an LLM,
correct records, delete records, or apply human review decisions.

## 2. Inputs

Validation consumes workflow state already produced by earlier nodes:

- `structured_task` and `collection_spec`
- `normalized_records`
- `event_clusters`
- `duplicate_clusters`
- `linked_events`
- `source_registry`
- optional `validation_records` loaded from held-out ground truth CSVs
- existing `conflicts` and `human_review_queue`

Validation-reserved or held-out records are right-side comparison evidence. They
are not used as collection extraction records.

## 3. Outputs

Stage 10 adds:

- `validation_cases`
- `validation_comparisons`
- `validation_results`
- `validation_summary`
- `trusted_source_validation_summary`
- `cross_source_validation_summary`

Existing outputs remain available:

- `conflicts`
- `cross_source_consistency_summary`
- `human_review_queue`

Final package and configured runner exports include validation artifacts in
`collection/` and `diagnostics/`.

## 4. Validation Units

Record-level validation:

- checks one normalized record against task scope or a held-out record

Event-cluster-level validation:

- checks whether a Stage 9 event cluster has independent source support
- prevents duplicate records from inflating support counts

Aggregate-level validation:

- compares sums over Stage 9 `countable=true` records to trusted or held-out
  validation records
- excludes non-countable duplicates

Field-level validation:

- compares specific count, date, disease, and location fields

Scope validation:

- checks disease, location, and requested time window
- flags outside-scope and insufficient-scope-information records without
  removing them

## 5. Comparability Rules

Validation checks disease, location, time window, reporting period, source role,
and count semantics before comparing values.

The workflow does not compare incompatible quantities as matches or conflicts by
default:

- cumulative vs annual
- cumulative vs newly reported
- annual vs weekly or daily
- newly reported vs historical total
- different diseases
- different non-overlapping time periods
- incompatible geography levels without aggregate compatibility

If a comparison is not safe, the workflow emits a validation result with
`comparability_status = not_comparable` and an explicit reason.

## 6. Trusted-Source Validation

Trusted-source / held-out validation uses:

- `validation_records`
- `source_role_final = validation`
- `source_role = validation_reserved`
- `final_screening_decision = reserved_for_validation`
- configured validation source IDs

Comparable collection records are compared to validation records field by field.
When there is no comparable validation counterpart, the workflow emits
`missing_validation`. When a validation record has no collection counterpart, it
emits `missing_collection`.

Aggregate comparisons use only `countable=true` collection records.

## 7. Cross-Source Validation

Cross-source validation uses Stage 9 event clusters.

It asks:

- whether an event cluster has independent source support
- whether sources agree on comparable fields
- whether conflicting values require review
- whether apparent support comes from duplicates or same-source evidence

Independent support is based on distinct source URLs or source IDs. Duplicate
records do not inflate countable aggregates. Official plus independent secondary
support can validate an event cluster, but conflicts still route to review.

## 8. Human Review Routing

Stage 10 creates human review items for:

- trusted-source conflicts
- missing collection counterparts
- cross-source conflicts
- outside requested time window
- outside geography
- disease mismatch
- insufficient scope information
- unclear or incompatible count semantics
- aggregate conflicts

Human review items contain validation IDs, record IDs, source IDs, source URLs,
compared fields, left/right values, reasons, suggested actions, and evidence
summaries.

Stage 10 does not apply human review decisions.

## 9. Backward Compatibility

The graph topology is unchanged. The node name remains
`cross_source_consistency_check`.

Existing `conflicts` and `cross_source_consistency_summary` remain available.
Stage 10 adds validation outputs alongside them.

Hantavirus/New Mexico compatibility remains supported, and validation-reserved
sources remain separated from collection sources.

## 10. Not Implemented In Stage 10

Stage 10 does not implement:

- anomaly detection
- human review decision application
- automatic record correction
- automatic record deletion
- CLI redesign
- notebook redesign
- UI redesign
- uncontrolled crawling
- browser automation
- OCR
