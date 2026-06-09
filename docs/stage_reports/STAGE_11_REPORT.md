# Stage 11 Report: Anomaly Detection + Human Review Decision Application

## 1. Stage goal

Stage 11 adds deterministic anomaly detection and explicit human review decision application to the **data collection workflow**. The goal is to flag suspicious records, validation results, event clusters, and source-level conflicts; route those issues to human review with evidence; apply only explicit structured human decisions; and preserve a complete before/after audit trail.

## 2. Summary of changes

- Added anomaly models, summaries, rule metadata, and review-routing payloads.
- Added deterministic anomaly rules for count errors, missing scope fields, validation conflicts, out-of-scope records, count semantics issues, rate issues, spikes, and aggregate mismatches.
- Added human review decision input, applied/rejected decision, audit trail, and application summary models.
- Added decision loading from state/config/file/env with JSON and JSONL support.
- Added deterministic decision application for records, clusters, validation results, anomalies, and source registry entries where supported.
- Added post-review dataset outputs while preserving original records and diagnostics.
- Updated finalization/export/runtime config/runner/console artifacts for anomaly and human review application outputs.
- Preserved COVID-19, dengue, and Hantavirus/New Mexico compatibility.

## 3. Files created or modified

Created:

- `docs/anomaly_human_review_application.md`
- `docs/stage_reports/STAGE_11_REPORT.md`
- `src/hdc_workflow/anomaly_detection.py`
- `src/hdc_workflow/human_review_application.py`
- `src/hdc_workflow/resources/human_review_decision_fixtures/covid19_review_decisions.json`
- `src/hdc_workflow/resources/human_review_decision_fixtures/dengue_review_decisions.json`
- `src/hdc_workflow/resources/human_review_decision_fixtures/stage11_mixed_review_decisions.json`
- `configs/examples/covid19_new_york_2024_fixture_review_application_task.jsonc`
- `configs/examples/dengue_florida_2025_fixture_review_application_task.jsonc`
- `configs/examples/covid19_new_york_2024_live_review_smoke.jsonc`
- `configs/examples/dengue_florida_2025_live_review_smoke.jsonc`
- `tests/test_anomaly_human_review_application.py`

Modified for Stage 11:

- `src/hdc_workflow/models.py`
- `src/hdc_workflow/state.py`
- `src/hdc_workflow/nodes/linking_validation.py`
- `src/hdc_workflow/nodes/human_review.py`
- `src/hdc_workflow/nodes/finalization.py`
- `src/hdc_workflow/resources/final_package_policy.json`
- `src/hdc_workflow/export.py`
- `src/hdc_workflow/runtime_profile.py`
- `scripts/run_hdc_workflow_configured.py`
- `scripts/build_workflow_run_console.py`

The working tree also contains earlier Stage 1-10 changes and outputs that were already present before this Stage 11 repair pass.

## 4. Functional changes made

Code inspection findings before editing:

- `graph.py` already had a serial node sequence with a conditional edge after `quality_gate_routing`; no topology change was needed.
- `human_review.py` built review packets but did not apply decisions to workflow objects.
- `linking_validation.py` already had Stage 10 validation outputs, making `quality_gate_routing` the right place to attach deterministic anomaly detection.
- `finalization.py` converted records into `PublicHealthRecord`, so Stage 11 fields had to be added to models to avoid being dropped.
- `export.py`, `run_hdc_workflow_configured.py`, and `build_workflow_run_console.py` needed artifact/report/console coverage for post-review outputs.

Changes:

- `anomaly_detection.py`: implements deterministic anomaly rules and review item creation.
- `human_review.py`: still builds review packets and now invokes decision application when explicit input exists.
- `finalization.py`: includes anomaly results, applied/rejected decisions, audit trail, application summary, and post-review dataset.
- `export.py`: writes Stage 11 JSON/CSV artifacts.
- `runtime_profile.py`: adds config/env support for decision paths, decision application, reviewer policy, and anomaly thresholds.
- `run_hdc_workflow_configured.py`: auto-exports diagnostics, readable report sections, summary counts, and artifact paths.
- `build_workflow_run_console.py`: loads and displays Stage 11 counts and artifacts.
- `tests/test_anomaly_human_review_application.py`: covers anomaly rules, decision application, exports, and fixture graph smokes.

## 5. Anomaly detection behavior

Anomaly units:

- `record`
- `event_cluster`
- `aggregate`
- `validation_result`
- `source`
- `workflow_run`

Severity levels:

- `info`
- `low`
- `medium`
- `high`
- `critical`

Rules:

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

Thresholds/config:

- `HDC_ANOMALY_MAX_CASES_THRESHOLD`
- `HDC_ANOMALY_MAX_DEATHS_THRESHOLD`
- `HDC_ANOMALY_SPIKE_MULTIPLIER`
- `HDC_ANOMALY_MIN_PRIOR_RECORDS`

Review routing is conservative: anomaly detection only creates anomaly results and review items. It does not correct, delete, merge, split, or override records.

## 6. Human review decision input behavior

Supported input sources:

- `human_review_decisions` in state
- `human_review_decisions_path` in state
- runtime config `human_review.decisions_path`
- environment variable `HDC_HUMAN_REVIEW_DECISIONS_PATH`
- JSON/JSONL fixture files

Required decision fields include `decision_id`, `review_id`, `decision_type`, `reviewer_id`, `decided_at`, `target_type`, `target_ids`, `reason`, optional notes/patch/corrected fields/confidence, and `apply_decision`.

Decision application from config/file is disabled unless the config/env application gate is enabled. Each decision must also have `apply_decision: true`. Invalid schema, missing reviewer ID, missing target IDs, missing targets, unsupported combinations, or unsafe patches are rejected and preserved in `rejected_human_review_decisions`.

## 7. Human review decision application behavior

Record decisions support accept, reject, correct, requires-review, resolved, countable/non-countable, and duplicate/not-duplicate status changes.

Countability/duplicate decisions update explicit record fields such as `countable`, `event_member_status`, `duplicate_of_record_id`, or `representative_record_id` when provided.

Cluster decisions support minimal `merge_records_or_clusters` and `split_cluster` status/representative updates when explicit cluster targets exist.

Validation decisions update validation status fields without rewriting underlying facts unless a record patch is explicitly provided separately.

Anomaly decisions update anomaly status only.

Source decisions can approve, override, exclude, or mark source roles for review when the source exists and the role is allowed.

Unsafe patches such as direct `record_id` mutation are rejected. Every successful field change creates an audit entry.

## 8. Audit trail behavior

Audit entries include decision metadata, target IDs, field name, before value, after value, apply status, rejection reason when applicable, reason, notes, and deterministic provenance.

Original records are preserved in diagnostics. `reject_record` marks a record as excluded from `final_dataset_post_review` but does not delete it from normalized records, raw diagnostics, or audit artifacts.

Post-review outputs:

- `applied_human_review_decisions`
- `rejected_human_review_decisions`
- `human_review_audit_trail`
- `human_review_application_summary`
- `final_dataset_post_review`
- `records_excluded_by_human_review`

## 9. Disease-specific examples

### COVID-19 / New York / 2024

- Normalized record count: `2`
- Validation result count: `7`
- Anomaly result count: `0`
- Anomaly severity counts: `{}`
- Human review item count: `5`
- Decisions provided: `3`
- Decisions applied: `2`
- Decisions rejected: `1`
- Final dataset post-review count: `1`
- Example anomaly: none in the fixture smoke; rule coverage is tested directly in unit tests.
- Example applied decision: `covid19_decision_correct_001`, `correct_fields`, target `rec_src_search_6dca14491140_002`, audit IDs `audit_001,audit_002`.

### Dengue / Florida / 2025

- Normalized record count: `2`
- Validation result count: `7`
- Anomaly result count: `0`
- Anomaly severity counts: `{}`
- Human review item count: `5`
- Decisions provided: `2`
- Decisions applied: `2`
- Decisions rejected: `0`
- Final dataset post-review count: `2`
- Example anomaly: none in the fixture smoke; rule coverage is tested directly in unit tests.
- Example applied decision: `dengue_decision_non_countable_001`, `mark_non_countable`, target `rec_src_search_2f25694b3ca0_001`, audit IDs `audit_001,audit_002`.

### Hantavirus / New Mexico compatibility

- Normalized record count: `5`
- Anomaly result count: `1`
- Human review item count: `18`
- Decisions applied count: `0`
- Compatibility status: PASSED with live fetch enabled, live search disabled, and all LLM stages disabled.
- Example anomaly: `anom_001`, `out_of_scope_count_bearing_record`, high severity, validation result `val_result_002`, reason `outside_geography`.

## 10. Integration with workflow

Anomaly detection runs in `quality_gate_routing` after normalization, clustering, validation, and conflict checks. Review-worthy anomaly results are converted into `human_review_queue` items. If review items or decision input exist, the graph routes to `human_review`; otherwise it finalizes.

Decisions are loaded and applied in `human_review`. Finalization exports the original and post-review views together. Validation, event clusters, conflicts, review packets, and original diagnostics remain available.

Graph topology was unchanged.

## 11. Backward compatibility

Default runs with no explicit decisions keep existing outputs and add empty/default anomaly and human review application summaries. Existing human review packets remain available. Hantavirus/New Mexico live-fetch compatibility passed with all LLM stages disabled. Validation, event clusters, conflicts, and final package outputs remain available.

## 12. Tests added or updated

Added:

- `tests/test_anomaly_human_review_application.py`

Coverage includes:

- Stage 11 model importability
- deaths greater than cases
- negative counts
- missing date/location
- disease mismatch
- outside scope validation anomaly
- count semantics conflict
- validation conflict anomaly
- high credibility source conflict
- spike threshold and invalid rate
- aggregate member mismatch
- decision disabled by `apply_decision: false`
- record correction and audit trail
- reject record with original preservation
- unsafe decision rejection
- countability, validation, anomaly, and source decisions
- export artifacts
- COVID-19 fixture graph smoke
- dengue fixture graph smoke
- Hantavirus/New Mexico compatibility

## 13. Commands run

- `git status --short`
- `git branch --show-current`
- `git rev-parse HEAD`
- `python -m pytest tests\test_anomaly_human_review_application.py -q`
- `python -m pytest tests\test_validation_refactor.py tests\test_duplicate_event_clustering.py tests\test_generic_structured_extraction.py tests\test_fetch_parse_generalization.py tests\test_source_credibility_scoring.py tests\test_real_source_discovery.py tests\test_executable_source_planning.py tests\test_profile_schema_setup.py tests\test_disease_intelligence.py tests\test_structured_task_input.py -q`
- `python -m pytest -q`
- `python scripts\run_hdc_workflow_configured.py --config configs\examples\covid19_new_york_2024_fixture_review_application_task.jsonc --session-id stage11_covid19_fixture_review_application_smoke`
- `python scripts\run_hdc_workflow_configured.py --config configs\examples\dengue_florida_2025_fixture_review_application_task.jsonc --session-id stage11_dengue_fixture_review_application_smoke`
- `python scripts\run_hdc_workflow_configured.py --config configs\examples\covid19_new_york_2024_live_review_smoke.jsonc --session-id stage11_covid19_live_anomaly_smoke`
- `python scripts\run_hdc_workflow_configured.py --config configs\examples\dengue_florida_2025_live_review_smoke.jsonc --session-id stage11_dengue_live_anomaly_smoke`
- `python scripts\run_hdc_workflow_configured.py --config configs\hdc_workflow_run_config.jsonc --disable-all-llm --session-id stage11_hantavirus_live_fetch_compat_no_llm`
- Sanitized secret scan equivalent to `rg -n "tvly-|sk-ant-|ANTHROPIC_API_KEY=\S+|TAVILY_API_KEY=\S+" .env.example configs docs outputs scripts src tests`, with key-like values masked before printing.

Git context:

- Branch: `main`
- HEAD: `0a74ec8ca7f3ed9ab3b3f7af834de7421a2efb88`

## 14. Test results

- Targeted Stage 11 tests: `20 passed in 0.48s`
- Regression subset: `118 passed in 2.12s`
- Full test suite: `344 passed in 9.12s`; final rerun after documentation changes: `344 passed in 8.35s`
- Final sanitized secret scan: `SECRET_SCAN_MATCH_COUNT=9`, limited to documented scan-command text in stage reports and mocked `tvly-***` test placeholders; no real secret value was printed.

## 15. Fixture review application smoke results

### COVID-19 fixture review application smoke

- Command: `python scripts\run_hdc_workflow_configured.py --config configs\examples\covid19_new_york_2024_fixture_review_application_task.jsonc --session-id stage11_covid19_fixture_review_application_smoke`
- Output directory: `outputs/sessions/stage11_covid19_fixture_review_application_smoke`
- Normalized record count: `2`
- Anomaly result count: `0`
- Human review item count: `5`
- Decisions provided: `3`
- Decisions applied: `2`
- Decisions rejected: `1`
- Audit entry count: `7`
- Final dataset post-review count: `1`
- Example applied decision: `covid19_decision_correct_001`
- No live web required: true
- No API key required: true

### Dengue fixture review application smoke

- Command: `python scripts\run_hdc_workflow_configured.py --config configs\examples\dengue_florida_2025_fixture_review_application_task.jsonc --session-id stage11_dengue_fixture_review_application_smoke`
- Output directory: `outputs/sessions/stage11_dengue_fixture_review_application_smoke`
- Normalized record count: `2`
- Anomaly result count: `0`
- Human review item count: `5`
- Decisions provided: `2`
- Decisions applied: `2`
- Decisions rejected: `0`
- Audit entry count: `4`
- Final dataset post-review count: `2`
- Example applied decision: `dengue_decision_non_countable_001`
- No live web required: true
- No API key required: true

## 16. Live anomaly smoke results

PASSED.

COVID-19 live anomaly smoke:

- Command: `python scripts\run_hdc_workflow_configured.py --config configs\examples\covid19_new_york_2024_live_review_smoke.jsonc --session-id stage11_covid19_live_anomaly_smoke`
- Provider: `tavily`
- API key present/absent: present, value not printed
- Output directory: `outputs/sessions/stage11_covid19_live_anomaly_smoke`
- Live-search-derived source count: `5`
- Usable/partial document count: `2`
- Normalized record count: `3`
- Validation result count: `10`
- Anomaly result count: `3`
- Anomaly severity counts: `{"medium":1,"high":2}`
- Human review item count: `16`
- Decisions applied count: `0`
- Example anomaly: `anom_001`, `missing_date_for_count_bearing_record`, medium severity, target record `rec_src_search_650359dcfc71_001`
- No API keys printed: true

Dengue live anomaly smoke:

- Command: `python scripts\run_hdc_workflow_configured.py --config configs\examples\dengue_florida_2025_live_review_smoke.jsonc --session-id stage11_dengue_live_anomaly_smoke`
- Provider: `tavily`
- API key present/absent: present, value not printed
- Output directory: `outputs/sessions/stage11_dengue_live_anomaly_smoke`
- Live-search-derived source count: `3`
- Usable/partial document count: `2`
- Normalized record count: `6`
- Validation result count: `19`
- Anomaly result count: `7`
- Anomaly severity counts: `{"medium":3,"high":4}`
- Human review item count: `32`
- Decisions applied count: `0`
- Example anomaly: `anom_001`, `missing_location_for_count_bearing_record`, medium severity, target record `rec_src_search_53763309bf94_002`
- No API keys printed: true

## 17. Hantavirus live-fetch compatibility

PASSED.

- Command: `python scripts\run_hdc_workflow_configured.py --config configs\hdc_workflow_run_config.jsonc --disable-all-llm --session-id stage11_hantavirus_live_fetch_compat_no_llm`
- Output directory: `outputs/sessions/stage11_hantavirus_live_fetch_compat_no_llm`
- live_fetch_enabled: `true`
- live_search_enabled: `false`
- all LLM stages disabled: true
- Normalized record count: `5`
- Validation result count: `17`
- Anomaly result count: `1`
- Human review item count: `18`
- Decisions applied count: `0`
- Compatibility notes: existing New Mexico live-fetch flow still runs, produces validation and review artifacts, and now includes Stage 11 anomaly/application summaries.
- No API keys printed: true

## 18. Live acceptance result

PASSED:

- `pytest -q` passed.
- COVID-19 and dengue fixture review application smokes passed.
- COVID-19 and dengue live anomaly smokes ran successfully with Tavily key present.
- Hantavirus/New Mexico compatibility passed with all LLM stages disabled.
- No real API keys were printed.
- No CLI/notebook/UI redesign was implemented.
- No interactive review UI was implemented.
- No automatic truth determination was implemented.

## 19. Output artifacts

- `docs/anomaly_human_review_application.md`
- `docs/stage_reports/STAGE_11_REPORT.md`
- `tests/test_anomaly_human_review_application.py`
- `src/hdc_workflow/resources/human_review_decision_fixtures/covid19_review_decisions.json`
- `src/hdc_workflow/resources/human_review_decision_fixtures/dengue_review_decisions.json`
- `src/hdc_workflow/resources/human_review_decision_fixtures/stage11_mixed_review_decisions.json`
- `configs/examples/covid19_new_york_2024_fixture_review_application_task.jsonc`
- `configs/examples/dengue_florida_2025_fixture_review_application_task.jsonc`
- `configs/examples/covid19_new_york_2024_live_review_smoke.jsonc`
- `configs/examples/dengue_florida_2025_live_review_smoke.jsonc`
- `outputs/sessions/stage11_covid19_fixture_review_application_smoke`
- `outputs/sessions/stage11_dengue_fixture_review_application_smoke`
- `outputs/sessions/stage11_covid19_live_anomaly_smoke`
- `outputs/sessions/stage11_dengue_live_anomaly_smoke`
- `outputs/sessions/stage11_hantavirus_live_fetch_compat_no_llm`
- `diagnostics/anomaly_results.json`
- `diagnostics/anomaly_summary.json`
- `diagnostics/human_review_decisions.json`
- `diagnostics/applied_human_review_decisions.json`
- `diagnostics/rejected_human_review_decisions.json`
- `diagnostics/human_review_audit_trail.json`
- `diagnostics/human_review_application_summary.json`
- `diagnostics/final_dataset_post_review.json`
- `collection/anomaly_results.json`
- `collection/anomaly_results.csv`
- `collection/final_dataset_post_review.json`
- `collection/final_dataset_post_review.csv`

## 20. Known limitations

- Final product CLI not implemented yet.
- Notebook/UI redesign not implemented yet.
- Interactive human review UI not implemented yet.
- Automatic truth determination not implemented.
- Advanced epidemiological anomaly models not implemented.
- Human review decisions require explicit structured decision files or state input.
- Live runs may not naturally contain severe anomalies.
- Some decision types are supported only for specific target types.
- Fixture smoke runs may have zero natural anomalies; unit tests cover anomaly rules directly.

## 21. Future-stage items explicitly NOT implemented

- Final product CLI
- Notebook redesign
- UI redesign
- Interactive human review UI
- Advanced epidemiological models
- Automatic truth determination

## 22. Review checklist

- [x] User-facing project name remains "data collection workflow"
- [x] Internal package name hdc_workflow was not mass-renamed
- [x] Graph topology unchanged unless documented
- [x] AnomalyResult / anomaly_summary exists
- [x] deaths_greater_than_cases anomaly works
- [x] negative_count anomaly works
- [x] missing date/location anomaly works
- [x] validation conflict anomaly works
- [x] outside-scope count-bearing anomaly works
- [x] anomaly results route to human review
- [x] human review decision input model exists
- [x] decision application disabled by default unless explicit input/apply flag
- [x] reject_record decision works and preserves original diagnostics
- [x] correct_fields decision works with before/after audit trail
- [x] invalid/unsafe decisions are rejected with reasons
- [x] countable/duplicate decisions work
- [x] validation/anomaly/source decision application works where supported
- [x] human_review_audit_trail is exported
- [x] human_review_application_summary is exported
- [x] final_dataset_post_review is exported
- [x] Existing Hantavirus/New Mexico compatibility passes
- [x] Fixture COVID-19 review application smoke completed
- [x] Fixture dengue review application smoke completed
- [x] Live COVID-19 anomaly smoke attempted
- [x] Live dengue anomaly smoke attempted
- [x] pytest was run
- [x] No API keys or secrets were printed
- [x] No CLI/notebook/UI redesign was implemented
- [x] No future-stage features were implemented
