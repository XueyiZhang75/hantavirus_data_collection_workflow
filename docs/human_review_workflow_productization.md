# Human Review Workflow Productization

## 1. Purpose

The `data collection workflow` now turns the existing human review queue into prioritized, actionable review artifacts. The goal is to help a reviewer decide what to inspect first, which evidence and source files to open, and how to prepare an explicit decision file when a human has actually made a decision.

## 2. Why this was needed

Stage 11 added explicit structured human review decision application and audit trails. That made the workflow capable of applying human decisions safely, but live runs can still produce many review items. A user needs a priority summary, top review items, decision templates, prefilled non-applying decision files, and clear instructions before applying anything.

The Virginia hantavirus live run is the motivating case: the workflow completed search, fetch, extraction, validation, claim corroboration, observation splitting, interpretive reporting, and human review queue generation, but no primary case dataset records passed the final quality gate. The next question is not "what did the workflow decide as truth?" but "what should a human inspect next?"

## 3. Review artifacts

Each completed run can now include a `human_review/` folder with:

- `human_review_priority_summary.json`: machine-readable priority summary and counts.
- `human_review_priority_summary.md`: human-readable review status, priority counts, top items, and next steps.
- `top_review_items.csv`: spreadsheet-friendly list of prioritized review items.
- `top_review_items.json`: full structured priority output.
- `review_decision_template.json`: short decision template for top review items.
- `review_decision_prefill.json`: non-applying prefilled decision file for all prioritized items.
- `review_decision_prefill.csv`: spreadsheet-friendly prefill companion.
- `review_packet_index.json`: index from review IDs to target IDs and relevant artifact paths.
- `review_action_guide.md`: manual instructions for inspecting evidence and applying explicit decisions.

Copies of the priority summary and top review items are also written to `collection/` and `diagnostics/` for audit convenience.

## 4. Prioritization logic

Prioritization is deterministic and artifact-only. It reads existing review items, records, claims, source identity outputs, validation summaries, anomaly outputs, quality-gate summaries, and interpretive summaries.

Priority levels:

- `P0_critical`: may directly affect primary case dataset inclusion, primary case existence interpretation, claim conflicts, or high-risk evidence blockers.
- `P1_high`: likely affects quarantined records, source identity, source critic blocks, validation limitations, outside-scope decisions, or single-source primary claims.
- `P2_medium`: usually affects non-primary observation classification, context-only classification, duplicate/event cluster uncertainty, or moderate anomalies.
- `P3_low`: informational review, metadata cleanup, or general limitations that do not directly change record inclusion.

Issue categories include:

- `primary_case_dataset_blocker`
- `possible_primary_case_evidence`
- `non_primary_observation_review`
- `zero_case_statement_review`
- `exposure_monitoring_review`
- `source_identity_review`
- `source_credibility_review`
- `source_critic_block_review`
- `claim_corroboration_review`
- `conflicting_claims_review`
- `validation_limited_review`
- `validation_conflict_review`
- `outside_scope_review`
- `anomaly_review`
- `duplicate_or_event_cluster_review`
- `missing_required_fields_review`
- `provenance_review`
- `human_decision_application_review`
- `context_only_review`
- `general_review`

Validation-limited review items are never treated as automatic evidence that no case exists. They only mean the reviewer should inspect whether a task-compatible validation source is available or should be configured.

## 5. Decision templates

Decision templates are suggestions only.

Every generated decision has:

- `apply_decision=false` by default
- placeholder `reviewer_id`
- placeholder `decided_at`
- reason/notes placeholders or explanatory text
- target IDs filled when the target is known from artifacts
- decision types restricted to decision types already supported by the existing Stage 11 decision application mechanism

The templates do not approve records, reject records, correct values, resolve conflicts, or determine truth. A human reviewer must copy the prefill file, edit it, and explicitly set `apply_decision=true` before the existing application mechanism can affect post-review outputs.

## 6. How to apply decisions

Use the existing decision application path. Do not edit generated template files in place.

Typical flow:

1. Open `human_review/top_review_items.csv`.
2. Inspect P0/P1 rows first.
3. Open the files listed in `recommended_artifacts_to_open`.
4. Copy `human_review/review_decision_prefill.json` to a separate working decision file.
5. Edit `reviewer_id`, `decided_at`, `decision_type`, `target_ids`, `reason`, `notes`, and any safe patch fields.
6. Set `apply_decision=true` only for explicit human decisions.
7. Re-run the workflow with the edited decision file using the existing `human_review.decisions_path` or CLI decision-path option.
8. Inspect `final_dataset_post_review`, `applied_human_review_decisions`, `rejected_human_review_decisions`, and `human_review_audit_trail`.

## 7. Safety boundaries

The human review productization layer:

- does not determine truth
- does not provide medical advice
- does not make an official surveillance conclusion
- does not call LLMs
- does not run search
- does not fetch webpages
- does not approve, reject, correct, or apply decisions automatically
- does not change graph topology
- does not change extraction, validation, source discovery, claim corroboration, anomaly, or quality-gate logic

It only reads completed run artifacts and writes review guidance artifacts.

## 8. Limitations

This is not an interactive review UI. It is not workflow visualization. It does not replace expert review. Review quality depends on upstream search, source identity, extraction, claim corroboration, validation, anomaly detection, and quality-gate artifacts. Users must manually inspect evidence and explicitly edit decision files before any post-review change can occur.
