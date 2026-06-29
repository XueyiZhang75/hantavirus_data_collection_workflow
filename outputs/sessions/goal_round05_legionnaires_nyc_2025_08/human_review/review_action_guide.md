# Human Review Action Guide

## 1. What to open first

Start with `human_review/top_review_items.csv`. Review `P0_critical` and `P1_high` items first.

## 2. How to inspect evidence

Use each row's `recommended_artifacts_to_open` field to inspect source identity, record inclusion decisions, claims, corroborated events, anomaly results, validation results, and quarantined/context records.

## 3. How to edit a decision file

Copy `human_review/review_decision_prefill.json` to a new working file. For each decision you actually want to apply, edit `reviewer_id`, `decided_at`, `decision_type`, `target_ids`, `reason`, `notes`, and any safe `patch` or `corrected_fields` values.

Set `apply_decision=true` only after a human reviewer has made an explicit decision. Generated template and prefill files intentionally keep `apply_decision=false`.

## 4. How to apply decisions

Use the existing workflow decision-application mechanism by providing the edited decision file through the configured `human_review.decisions_path` or CLI decision path and enabling decision application. Do not edit generated template files in place.

## 5. Post-review outputs to inspect

- `collection/final_dataset_post_review.json`
- `collection/records_excluded_by_human_review.json`
- `collection/applied_human_review_decisions.json`
- `collection/rejected_human_review_decisions.json`
- `collection/human_review_audit_trail.json`

## 6. Current run summary

- Run quality status: `partial_with_quarantined_records`
- Primary case dataset status: `no_primary_case_dataset_records`
- Review item count: `79`
- Prioritized item count: `79`
- Final case dataset count: `0`
- Quarantined record count: `11`

## 7. Safety boundary

This guide does not determine truth, provide medical advice, or make an official surveillance conclusion. It only helps a human reviewer act on existing workflow artifacts.
