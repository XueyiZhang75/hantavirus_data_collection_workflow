# Run-Quality-Gated Final Dataset

## 1. Purpose

`final_dataset` now means quality-gated accepted records. It is no longer a
mirror of every raw, validated, or normalized record the data collection
workflow saw during a run.

The workflow still preserves all intermediate records for audit. The accepted
dataset is only the subset that passes deterministic final run-quality gates.

## 2. Failure mode

A workflow run can technically complete while data quality still fails. For
example, a live Shanghai hantavirus/HFRS run may complete search, fetch,
extraction, validation, anomaly detection, and routing while still finding no
reliable task-relevant records.

Wrong-disease, out-of-scope, unsupported, validation-conflicting, or
high-anomaly records must not appear as accepted final data. The Shanghai
hantavirus run motivated this repair because product users need a completed run
to distinguish "no reliable accepted records" from "successful collection."

## 3. Dataset views

- `collection/final_dataset.csv` and `collection/final_dataset.json`: accepted
  quality-gated records only.
- `collection/final_dataset_pre_quality_gate.csv` and
  `collection/final_dataset_pre_quality_gate.json`: all normalized records
  before final quality gating, with quality-gate fields added.
- `collection/quarantined_records.csv` and
  `collection/quarantined_records.json`: records excluded by hard quality
  gates.
- `collection/pending_review_records.csv` and
  `collection/pending_review_records.json`: records not accepted because
  unresolved review is required.
- `collection/final_dataset_post_review.csv` and
  `collection/final_dataset_post_review.json`: accepted records after explicit
  human review decisions are applied. If no decisions are applied, this matches
  the quality-gated `final_dataset`.
- `diagnostics/normalized_records.json`: all normalized records remain
  available for audit and debugging.

## 4. Record inclusion rules

Accepted records must pass deterministic checks across the current workflow
state:

- Disease relevance gates: incompatible disease/pathogen records are
  quarantined.
- Source critic and fetch gates: source-critic-blocked, excluded, or
  search-endpoint records are quarantined.
- Document and chunk gates: not-task-relevant documents or evidence chunks are
  quarantined.
- Schema and normalization gates: invalid schema, rejected normalization, and
  failed provenance are quarantined.
- Validation gates: outside-scope records and comparable trusted-source
  conflicts are quarantined.
- Anomaly gates: high or critical record-level anomalies are quarantined.
- Human review decisions: explicit `reject_record` decisions exclude records
  from accepted and post-review datasets.

Non-blocking limitations, such as no compatible validation source,
single-source-only evidence, missing validation counterpart, or low/medium
review warnings, are reported as warnings rather than automatic rejection.

## 5. Run quality status

`run_quality_summary.run_quality_status` may be:

- `passed`: accepted records exist and no hard quality failures were found.
- `passed_with_review`: accepted records exist with non-blocking warnings or
  review limitations.
- `partial_with_quarantined_records`: some records were accepted and some were
  quarantined.
- `no_records_extracted`: no normalized records were produced.
- `no_task_relevant_records`: workflow evidence indicates no target-disease
  extractable records.
- `failed_quality_gate`: normalized records existed, but none passed quality
  gates.
- `validation_limited_no_compatible_source`: validation is limited because no
  compatible held-out validation source is available.

## 6. What changes for users

- `final_dataset.csv` may be empty even when the workflow ran successfully.
- Check `diagnostics/run_quality_summary.json` first.
- Use `quarantined_records` and `record_inclusion_decisions` to understand why
  candidate records were excluded.
- No compatible validation source is a limitation, not automatic failure.
- Expert review remains required before using outputs for public-health
  decisions.

## 7. What is still not fixed

- Full HTML/report dynamic cleanup is not fixed in Repair 5.
- This repair does not improve source discovery or search ranking.
- This repair does not guarantee that official sources exist or are indexed.
- This repair does not make automatic truth determinations.

