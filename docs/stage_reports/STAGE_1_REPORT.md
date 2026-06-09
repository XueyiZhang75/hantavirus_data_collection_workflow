# Stage 1 Report: Structured Task Input + Disease Decoupling

## Stage Goal

Implement a structured task input layer for the **data collection workflow** so disease, location, time window, target fields, source preferences, collection mode, task text, and run label can be passed as machine-readable state/config fields instead of being inferred only from a legacy free-text `user_request`.

## Summary of Changes

- Added `StructuredTaskInput` to represent task-level inputs.
- Extended `CollectionSpec` with structured task metadata while preserving existing fields.
- Updated `task_intake_and_scope_planning` so explicit structured task fields take priority over legacy `user_request` inference.
- Preserved the backward-compatible default hantavirus/New Mexico behavior.
- Added `structured_task` to centralized runtime config and LangGraph Studio initial state generation.
- Added example structured task configs for COVID-19/New York and dengue/Florida without implementing future-stage disease-generic source discovery.
- Added explicit non-hantavirus warning metadata: `non_hantavirus_task_with_hantavirus_profile_resources`, `profile_schema_not_yet_generalized`, and `source_discovery_not_yet_disease_generic`.
- Added `task_intake_summary` to exported `workflow_summaries` so these warnings appear in full graph output artifacts.
- Removed the duplicate `workflow_initial_state_from_config` definition from `runtime_profile.py`; there is now one canonical definition.
- Added `docs/structured_task_input.md`.
- Added tests covering structured task model creation, structured-over-legacy priority, non-hantavirus preservation, downstream not-yet-generalized warnings, exported task-intake summary auditability, backward compatibility, centralized config initial state, and full graph offline non-hantavirus smoke behavior.

## Files Changed

- `src/hdc_workflow/models.py`
- `src/hdc_workflow/state.py`
- `src/hdc_workflow/nodes/task_scope.py`
- `src/hdc_workflow/runtime_profile.py`
- `src/hdc_workflow/workflow_run_config.py`
- `src/hdc_workflow/resources/final_package_policy.json`
- `configs/hdc_workflow_run_config.jsonc`
- `configs/examples/covid19_new_york_2024_task.jsonc`
- `configs/examples/dengue_florida_2025_task.jsonc`
- `docs/structured_task_input.md`
- `tests/test_structured_task_input.py`
- `tests/test_workflow_run_config.py`
- `README.md`
- `docs/stage_reports/STAGE_1_REPORT.md`

## Code Inspection Findings

- `task_intake_and_scope_planning` previously hard-coded `disease="Hantavirus disease"` and only inferred geography/time from `user_request`.
- `CollectionSpec` had no dedicated fields for user-facing structured task inputs such as `start_date`, `end_date`, `target_fields`, `source_preferences`, `collection_mode`, or `run_label`.
- The runtime config helper is `src/hdc_workflow/runtime_profile.py`; there is no separate `runtime_config.py`.
- `workflow_initial_state_from_config` was previously defined twice in `runtime_profile.py`; the repair pass removed the duplicate and left a single canonical definition.
- `configs/hdc_workflow_run_config.jsonc` controlled runtime settings but did not previously include machine-readable task fields.
- Existing source overlays, source roles, validation records, and graph topology remain tied to the current hantavirus/New Mexico case study.

## New/Updated Tests

- Added `tests/test_structured_task_input.py`
  - `test_structured_task_model_accepts_required_fields`
  - `test_task_intake_structured_fields_override_legacy_user_request`
  - `test_task_intake_preserves_distinct_dengue_task`
  - `test_non_hantavirus_task_emits_downstream_not_generalized_warnings`
  - `test_final_package_policy_includes_task_intake_summary_for_audit`
  - `test_task_intake_default_remains_hantavirus_compatible`
  - `test_workflow_initial_state_from_config_includes_structured_task`
  - `test_full_graph_offline_covid19_new_york_preserves_task_metadata`
  - `test_full_graph_offline_dengue_florida_preserves_task_metadata`
- Updated `tests/test_workflow_run_config.py`
  - Verifies centralized config now emits `structured_task`.
  - Verifies CLI-style `user_request` override updates the structured task text without overwriting structured disease/location fields.

## Commands Run

```powershell
python -m pytest tests\test_structured_task_input.py -q
python -m pytest tests\test_structured_task_input.py tests\test_workflow_run_config.py -q
python -m pytest tests\test_workflow_run_config.py tests\test_graph_smoke.py -q
python scripts\run_hdc_workflow_configured.py --config configs\examples\covid19_new_york_2024_task.jsonc --session-id stage1_covid19_offline_smoke
python scripts\run_hdc_workflow_configured.py --config configs\examples\dengue_florida_2025_task.jsonc --session-id stage1_dengue_offline_smoke
python scripts\run_hdc_workflow_configured.py --config configs\hdc_workflow_run_config.jsonc --disable-all-llm --session-id stage1_hantavirus_live_compat_no_llm
python scripts\run_hdc_workflow_configured.py --config configs\hdc_workflow_run_config.jsonc --disable-all-llm --session-id stage1_hantavirus_live_compat_no_llm_escalated
python -m pytest -q
```

## Test Results

- `tests\test_structured_task_input.py`: 9 passed.
- Full graph offline COVID-19/New York and dengue/Florida acceptance tests are included in `tests\test_structured_task_input.py`.
- `tests\test_workflow_run_config.py tests\test_graph_smoke.py`: 132 passed.
- Full test suite: 215 passed in 4.92s.

## Example Command or Fixture Run

```powershell
python scripts\run_hdc_workflow_configured.py --config configs\hdc_workflow_run_config.jsonc
```

For offline task-input examples:

```powershell
python scripts\run_hdc_workflow_configured.py --config configs\examples\covid19_new_york_2024_task.jsonc
python scripts\run_hdc_workflow_configured.py --config configs\examples\dengue_florida_2025_task.jsonc
```

These example configs are intended to exercise structured task input only. They do not make downstream source discovery or extraction disease-generic.

## Full Graph Smoke Runs

### Non-Hantavirus Offline Smoke

Two non-hantavirus full graph offline smoke runs completed successfully without internet access, API keys, live web, or real LLM calls:

- `stage1_covid19_offline_smoke`
  - `trace_node_count`: 17
  - `current_route`: `finalize`
  - `document_count`: 6
  - `normalized_record_count`: 0
  - `human_review_item_count`: 1
  - `llm_source_planning_status`: `disabled`
  - `llm_structured_extraction_call_count`: 0
  - Output report: `outputs/sessions/stage1_covid19_offline_smoke/workflow_run_report_chinese.md`
  - Exported workflow summary: `outputs/sessions/stage1_covid19_offline_smoke/collection/workflow_summaries.json`

- `stage1_dengue_offline_smoke`
  - `trace_node_count`: 17
  - `current_route`: `finalize`
  - `document_count`: 6
  - `normalized_record_count`: 0
  - `human_review_item_count`: 1
  - `llm_source_planning_status`: `disabled`
  - `llm_structured_extraction_call_count`: 0
  - Output report: `outputs/sessions/stage1_dengue_offline_smoke/workflow_run_report_chinese.md`
  - Exported workflow summary: `outputs/sessions/stage1_dengue_offline_smoke/collection/workflow_summaries.json`

Both runs include these warnings in `collection_trace.json`, `final_package.json`, and `workflow_summaries.json`:

- `profile_schema_not_yet_generalized`
- `source_discovery_not_yet_disease_generic`
- `non_hantavirus_task_with_hantavirus_profile_resources`

## Live Acceptance Result

PASSED for live-fetch compatibility with LLM disabled.

### Current Hantavirus/New Mexico Live Compatibility

A current hantavirus/New Mexico compatibility run was executed with live fetch enabled and all LLM stages explicitly disabled:

```powershell
python scripts\run_hdc_workflow_configured.py --config configs\hdc_workflow_run_config.jsonc --disable-all-llm --session-id stage1_hantavirus_live_compat_no_llm_escalated
```

Result:

- `live_fetch_enabled`: true
- `all_three_llm_stages_enabled`: false
- `trace_node_count`: 18
- `current_route`: `human_review`
- `document_count`: 5
- `usable_document_count`: 5
- `normalized_record_count`: 5
- `evaluation_row_count`: 5
- `human_review_item_count`: 8
- `fetch_status_counts`: `{"fetched": 5}`
- `quality_status_counts`: `{"usable": 5}`
- `llm_call_count`: 0
- `llm_structured_extraction_call_count`: 0
- Output report: `outputs/sessions/stage1_hantavirus_live_compat_no_llm_escalated/workflow_run_report_chinese.md`
- Live fetch summary: `outputs/sessions/stage1_hantavirus_live_compat_no_llm_escalated/diagnostics/live_fetch_summary.json`

The first non-escalated live compatibility attempt completed the graph but had `fetch_failed=5`, consistent with restricted network access. The escalated rerun fetched all five allowed live documents successfully. No LLM prompt or webpage evidence was sent to an API in either compatibility run.

## Output Artifacts Created

- `configs/examples/covid19_new_york_2024_task.jsonc`
- `configs/examples/dengue_florida_2025_task.jsonc`
- `docs/structured_task_input.md`
- `docs/stage_reports/STAGE_1_REPORT.md`
- `outputs/sessions/stage1_covid19_offline_smoke/`
- `outputs/sessions/stage1_dengue_offline_smoke/`
- `outputs/sessions/stage1_hantavirus_live_compat_no_llm/`
- `outputs/sessions/stage1_hantavirus_live_compat_no_llm_escalated/`

## Known Limitations

- Non-hantavirus structured tasks are preserved in state and `CollectionSpec`, but downstream disease profile, schema, source overlays, and extraction record model still use the current hantavirus/New Mexico implementation.
- Non-hantavirus outputs intentionally include warnings that downstream resources are not disease-generic yet.
- No disease intelligence layer yet.
- No generic disease profile/schema setup yet.
- No executable LLM source planning yet.
- No real source discovery/search provider yet.
- No source credibility scoring overhaul yet.
- No validation refactor yet.
- No duplicate clustering overhaul yet.
- No anomaly detection yet.
- No human review decision application yet.
- No CLI/notebook/UI redesign yet.
- `source_preferences` are recorded and reflected in `CollectionSpec.source_priority`; they do not yet trigger broad web search or source provider selection.
- `target_fields` are task-level requested fields; they do not replace the existing extraction schema.
- Existing runtime config still uses the New Mexico HPS source set as the default case-study profile.
- No real web, API key, or live LLM call is required by Stage 1 tests.

## Future-Stage Items Not Implemented

- Disease intelligence or dynamic disease profiles.
- Dynamic source overlays generated from disease/location/time inputs.
- Broad web search or search provider integration.
- Validation source refactor.
- Duplicate handling changes.
- Anomaly detection.
- Human review decision application.
- CLI, notebook, or UI redesign.
- Graph topology changes.
- Package/import mass rename.
- Disease-generic extraction schema.

## Review Checklist

- [x] User-facing project name remains **data collection workflow**.
- [x] Internal package name `hdc_workflow` unchanged.
- [x] Graph topology unchanged.
- [x] Default offline deterministic behavior preserved.
- [x] Structured fields take priority over legacy free text.
- [x] Legacy `user_request` behavior remains backward-compatible.
- [x] Tests do not require internet access, API keys, live web, or real LLM calls.
- [x] New behavior covered by tests.
- [x] Full test suite passed.
