# Anomaly Detection and Human Review Decision Application

This document describes the Stage 11 trust layer in the **data collection workflow**. The internal Python package remains `hdc_workflow`.

## Purpose

Stage 11 adds two deterministic capabilities:

- anomaly detection for records, event clusters, validation results, source conflicts, and workflow-level trust checks
- explicit human review decision application with before/after audit trails

The trust layer does not decide truth automatically. It flags suspicious outputs and only changes post-review views when a structured human review decision explicitly says to apply a change.

## Where It Runs

The graph topology remains unchanged.

- `quality_gate_routing` calls deterministic anomaly detection after validation and clustering outputs exist.
- anomaly results that need review are appended to `human_review_queue`.
- `human_review` still builds review packets, and now also loads and applies explicit review decisions when provided.
- `final_data_package_builder` exports both the original final dataset view and the post-review dataset view.

## Anomaly Outputs

The workflow now emits:

- `anomaly_results`
- `anomaly_summary`
- `anomaly_review_items`

Each anomaly includes provenance-oriented fields such as:

- `anomaly_id`
- `anomaly_type`
- `anomaly_unit`
- `severity`
- `record_id`
- `event_cluster_id`
- `validation_result_id`
- `source_id`
- `source_ids`
- `source_urls`
- `compared_field`
- `observed_value`
- `expected_or_reference_value`
- `threshold`
- `reason`
- `recommended_action`
- `needs_human_review`
- `human_review_reason`
- `detection_method`
- `warnings`

Severity values are `info`, `low`, `medium`, `high`, and `critical`. Anomaly units are `record`, `event_cluster`, `aggregate`, `validation_result`, `source`, and `workflow_run`.

## Deterministic Rules

Implemented anomaly rules are conservative and transparent:

- `deaths_greater_than_cases`
- `negative_count_value`
- `missing_date_for_count_bearing_record`
- `missing_location_for_count_bearing_record`
- `disease_mismatch_or_unknown_for_count_bearing_record`
- `out_of_scope_count_bearing_record`
- `count_semantics_conflict`
- `validation_conflict_anomaly`
- `high_credibility_source_conflict`
- `abrupt_spike_simple_threshold`
- `test_positivity_or_rate_invalid`
- `aggregate_member_mismatch`

Simple spike thresholds are configurable through environment/config-derived values:

- `HDC_ANOMALY_MAX_CASES_THRESHOLD`
- `HDC_ANOMALY_MAX_DEATHS_THRESHOLD`
- `HDC_ANOMALY_SPIKE_MULTIPLIER`
- `HDC_ANOMALY_MIN_PRIOR_RECORDS`

These are not epidemiological models. They are guardrails for suspicious extracted or normalized values.

## Human Review Decision Inputs

Review decisions can come from:

- `state["human_review_decisions"]`
- `state["human_review_decisions_path"]`
- runtime config `human_review.decisions_path`
- environment variable `HDC_HUMAN_REVIEW_DECISIONS_PATH`
- JSON or JSONL fixture files under `src/hdc_workflow/resources/human_review_decision_fixtures/`

Decision files are applied only when the config/env path is explicit and `HDC_HUMAN_REVIEW_APPLY_DECISIONS` is enabled by config, or when decisions are supplied directly in state. Each individual decision must still include `apply_decision: true`.

Required decision fields include:

- `decision_id`
- `review_id`
- `decision_type`
- `reviewer_id`
- `decided_at`
- `target_type`
- `target_ids`
- `reason`
- `notes`
- `patch` or `corrected_fields`
- `confidence`
- `apply_decision`

Invalid decisions are not applied. They are recorded in `rejected_human_review_decisions` with a reason.

## Supported Decision Families

Record decisions:

- `accept_as_is`
- `reject_record`
- `correct_fields`
- `mark_requires_review`
- `mark_review_resolved`

Countability and duplicate decisions:

- `mark_duplicate`
- `mark_not_duplicate`
- `mark_countable`
- `mark_non_countable`
- `merge_records_or_clusters`
- `split_cluster`

Validation decisions:

- `accept_validation_result`
- `mark_validation_result_not_applicable`
- `override_validation_status`
- `confirm_conflict`
- `resolve_conflict_as_left`
- `resolve_conflict_as_right`
- `mark_needs_more_evidence`

Source decisions:

- `approve_source_role`
- `override_source_role`
- `exclude_source`
- `mark_source_needs_review`

Anomaly decisions:

- `accept_anomaly`
- `dismiss_anomaly`
- `confirm_anomaly`
- `mark_anomaly_resolved`
- `mark_anomaly_needs_more_evidence`

General decisions:

- `needs_more_evidence`
- `defer_decision`

Unsupported target/decision combinations are rejected with an explicit reason.

## Audit Trail

Applied decisions create:

- `applied_human_review_decisions`
- `human_review_audit_trail`
- `human_review_application_summary`
- `final_dataset_post_review`
- `records_excluded_by_human_review`

Rejected decisions create:

- `rejected_human_review_decisions`

Audit entries include:

- `audit_id`
- `decision_id`
- `review_id`
- `reviewer_id`
- `decided_at`
- `applied_at`
- `decision_type`
- `target_type`
- `target_ids`
- `field_name`
- `before_value`
- `after_value`
- `apply_status`
- `rejection_reason`
- `reason`
- `notes`
- `provenance`

Original normalized records, validation results, anomaly results, and source registry entries remain available in diagnostics. Rejected records are excluded only from the post-review dataset view; they are not deleted from raw or diagnostic artifacts.

## Output Artifacts

Per-session outputs now include Stage 11 files in both `collection/` and `diagnostics/`, including:

- `anomaly_results.json`
- `anomaly_results.csv`
- `anomaly_summary.json`
- `human_review_decisions.json`
- `applied_human_review_decisions.json`
- `rejected_human_review_decisions.json`
- `human_review_audit_trail.json`
- `human_review_application_summary.json`
- `final_dataset_post_review.json`
- `final_dataset_post_review.csv`
- `records_excluded_by_human_review.json`

The configured runner also writes these into the readable run report and the workflow console payload.

## Boundaries

Stage 11 does not implement:

- final product CLI
- notebook redesign
- UI redesign
- interactive human review web app
- automatic truth determination
- advanced epidemiological anomaly models
- uncontrolled crawling or search
- browser automation
- OCR
- API key storage or printing

