# Stage 3 Report: Generic Profile/Schema Setup

## Stage Goal

Implement generic profile/schema setup for the **data collection workflow** so non-hantavirus tasks no longer use the static hantavirus profile and static hantavirus collection schema as active workflow resources.

Stage 3 keeps hantavirus/New Mexico backward compatibility while generating active profile/schema/source-strategy resources from `disease_intelligence` and `collection_spec` for COVID-19, dengue, and unknown diseases.

## Summary of Changes

- Added `profile_and_schema_setup` as the active graph node after `disease_intelligence_builder`.
- Kept `hantavirus_profile_and_schema_setup` as a backward-compatible callable alias.
- Preserved the legacy hantavirus profile/schema/source-strategy path for hantavirus/HPS tasks.
- Added disease-intelligence-generated profile/schema/source-strategy generation for non-hantavirus tasks.
- Added `profile_schema_summary` to state, Studio initial state, configured-run diagnostics, and final package `workflow_summaries`.
- Updated stale warning behavior:
  - Removed `profile_schema_not_yet_generalized` for non-hantavirus tasks.
  - Removed `non_hantavirus_task_with_hantavirus_profile_resources` for non-hantavirus tasks.
  - Preserved `source_discovery_not_yet_disease_generic`.
  - Added/kept extraction-model warnings: `extraction_record_model_still_hantavirus_named` and `extraction_record_schema_not_yet_disease_generic`.
- Updated query strategy inputs indirectly because `query_strategy_builder` now receives disease-aware active `disease_profile`, `collection_schema`, and `source_strategy`.
- Added Stage 3 tests for hantavirus compatibility, COVID-19 generated profile/schema, dengue generated profile/schema, full graph smoke, query terms, target field preservation, and final-package summary export.
- Added `docs/profile_schema_setup.md`.
- Updated README and Stage 1/2 docs minimally to point at the new active setup layer.

## Files Changed

- `README.md`
- `configs/examples/covid19_new_york_2024_task.jsonc`
- `configs/examples/dengue_florida_2025_task.jsonc`
- `docs/disease_intelligence_layer.md`
- `docs/profile_schema_setup.md`
- `docs/stage_reports/STAGE_3_REPORT.md`
- `docs/structured_task_input.md`
- `scripts/run_hdc_workflow_configured.py`
- `src/hdc_workflow/graph.py`
- `src/hdc_workflow/nodes/__init__.py`
- `src/hdc_workflow/nodes/task_scope.py`
- `src/hdc_workflow/resources/final_package_policy.json`
- `src/hdc_workflow/runtime_profile.py`
- `src/hdc_workflow/state.py`
- `tests/test_disease_intelligence.py`
- `tests/test_graph_smoke.py`
- `tests/test_profile_schema_setup.py`
- `tests/test_structured_task_input.py`

## Code Inspection Findings

- `docs/final_product_target.md` identifies disease-generic task handling and disease-dependent source/schema behavior as required final functionality.
- `docs/current_state_audit.md` documented `hantavirus_profile_and_schema_setup` as a disease-specific blocker that loaded `hantavirus_profile.json`, `hantavirus_collection_schema.json`, and `source_strategy.json`.
- `docs/structured_task_input.md` previously reflected Stage 1 limitations and needed a minimal update after Stage 3.
- `docs/disease_intelligence_layer.md` correctly introduced disease intelligence but still pointed to the old profile/schema node name.
- `docs/stage_reports/STAGE_1_REPORT.md` and `STAGE_2_REPORT.md` confirmed that profile/schema generalization was intentionally not implemented before Stage 3.
- `src/hdc_workflow/models.py` already had compatible `DiseaseProfile`, `CollectionSchema`, `SourceStrategy`, `ScreeningCriteria`, and `DataFieldSpec` models, so Stage 3 did not need new Pydantic models.
- `HantavirusRecord` is still the extraction/final-dataset record model. Stage 3 records this as an explicit warning instead of replacing or renaming it.
- `src/hdc_workflow/state.py` lacked `profile_schema_summary`; it is now added.
- `src/hdc_workflow/resources/final_package_policy.json` lacked `profile_schema_summary` in `workflow_summary_fields`; it is now exported.
- The existing static `source_strategy.json` contains hantavirus/HPS screening language. Stage 3 keeps it only for the legacy hantavirus path and generates disease-neutral criteria for non-hantavirus tasks.
- `tests/test_structured_task_input.py` and `tests/test_disease_intelligence.py` had truthful Stage 1/2 warning assertions that became stale after Stage 3 and were updated.

## New/Updated Tests

Added `tests/test_profile_schema_setup.py`:

- `test_hantavirus_profile_schema_setup_backward_compatible`
- `test_covid19_generated_profile_schema_is_not_hantavirus_active_resource`
- `test_dengue_generated_profile_schema_is_not_hantavirus_active_resource`
- `test_full_graph_covid19_exports_profile_schema_summary_and_active_resources`
- `test_full_graph_dengue_exports_profile_schema_summary_and_active_resources`
- `test_query_strategy_receives_disease_aware_profile_terms`
- `test_covid19_hospitalizations_target_field_preserved_or_warned`
- `test_final_package_policy_includes_profile_schema_summary`

Updated:

- `tests/test_structured_task_input.py`
  - Non-hantavirus task warnings now assert that stale profile/schema warnings are absent and remaining future-stage warnings are present.
- `tests/test_disease_intelligence.py`
  - Full graph COVID-19/dengue assertions now include `profile_schema_summary`.
- `tests/test_graph_smoke.py`
  - Major workflow summaries now include `profile_schema_summary`.

## Commands Run

```powershell
python -m pytest tests\test_profile_schema_setup.py -q
python -m pytest tests\test_profile_schema_setup.py tests\test_structured_task_input.py tests\test_disease_intelligence.py tests\test_graph_smoke.py::test_workflow_summaries_include_major_steps -q
python -m pytest tests\test_profile_schema_setup.py tests\test_structured_task_input.py tests\test_disease_intelligence.py tests\test_workflow_run_config.py -q
python -m pytest -q
python scripts\run_hdc_workflow_configured.py --config configs\hdc_workflow_run_config.jsonc --disable-all-llm --session-id stage3_hantavirus_live_compat_no_llm
python scripts\run_hdc_workflow_configured.py --config configs\hdc_workflow_run_config.jsonc --disable-all-llm --session-id stage3_hantavirus_live_compat_no_llm_rerun
python scripts\run_hdc_workflow_configured.py --config configs\examples\covid19_new_york_2024_task.jsonc --session-id stage3_covid19_offline_smoke
python scripts\run_hdc_workflow_configured.py --config configs\examples\dengue_florida_2025_task.jsonc --session-id stage3_dengue_offline_smoke
```

## Test Results

- Stage 3 tests: 8 passed.
- Stage 1/2/3 targeted tests: 26 passed.
- Full test suite: 230 passed.

## Example Command or Fixture Run

Offline COVID-19/New York smoke:

```powershell
python scripts\run_hdc_workflow_configured.py --config configs\examples\covid19_new_york_2024_task.jsonc --session-id stage3_covid19_offline_smoke
```

Result:

- `trace_node_count`: 18
- `current_route`: `finalize`
- `document_count`: 6
- `normalized_record_count`: 0
- `human_review_item_count`: 1
- `llm_source_planning_status`: `disabled`
- `llm_structured_extraction_call_count`: 0
- Active schema: `covid_19_public_health_collection_schema`
- `profile_generation_method`: `disease_intelligence_generated_profile_schema`

Offline dengue/Florida smoke:

```powershell
python scripts\run_hdc_workflow_configured.py --config configs\examples\dengue_florida_2025_task.jsonc --session-id stage3_dengue_offline_smoke
```

Result:

- `trace_node_count`: 18
- `current_route`: `finalize`
- `document_count`: 6
- `normalized_record_count`: 0
- `human_review_item_count`: 1
- `llm_source_planning_status`: `disabled`
- `llm_structured_extraction_call_count`: 0
- Active schema: `dengue_public_health_collection_schema`
- `profile_generation_method`: `disease_intelligence_generated_profile_schema`

## Live Acceptance Result

PASSED for current hantavirus/New Mexico live-fetch compatibility with all LLM stages disabled.

Command:

```powershell
python scripts\run_hdc_workflow_configured.py --config configs\hdc_workflow_run_config.jsonc --disable-all-llm --session-id stage3_hantavirus_live_compat_no_llm_rerun
```

Result:

- `trace_node_count`: 19
- `current_route`: `human_review`
- `document_count`: 5
- `normalized_record_count`: 5
- `evaluation_row_count`: 5
- `human_review_item_count`: 8
- `llm_source_planning_status`: `disabled`
- `llm_source_critic_assessed_source_count`: 0
- `llm_structured_extraction_call_count`: 0
- `live_fetch_enabled`: true
- `fetch_status_counts`: `{"fetched": 5}`
- `quality_status_counts`: `{"usable": 5}`
- `profile_generation_method`: `legacy_hantavirus_profile_schema`
- Output report: `outputs/sessions/stage3_hantavirus_live_compat_no_llm_rerun/workflow_run_report_chinese.md`
- Live fetch summary: `outputs/sessions/stage3_hantavirus_live_compat_no_llm_rerun/diagnostics/live_fetch_summary.json`

No LLM prompt or webpage evidence was sent to an API during this live compatibility check.

## Output Artifacts Created

- `docs/profile_schema_setup.md`
- `docs/stage_reports/STAGE_3_REPORT.md`
- `outputs/sessions/stage3_covid19_offline_smoke/`
- `outputs/sessions/stage3_dengue_offline_smoke/`
- `outputs/sessions/stage3_hantavirus_live_compat_no_llm/`
- `outputs/sessions/stage3_hantavirus_live_compat_no_llm_rerun/`

## Known Limitations

- Stage 3 does not execute search or create real source candidates from generated query terms.
- `source_discovery` still uses the existing fixed catalog/overlays.
- The extraction/final-dataset record model is still named `HantavirusRecord`.
- Non-hantavirus generated schemas may retain target fields such as `hospitalizations`, but the current extraction record model does not yet fully support disease-generic output fields.
- Configured COVID-19/dengue offline runs may still produce empty final datasets because real source discovery and disease-generic extraction are not implemented.
- Validation remains tied to the current configured evaluation helpers and case-study ground-truth files.
- Human review decisions are still recorded but not applied to modify records or conflicts.

## Future-Stage Items Not Implemented

- Real web search.
- Search provider integration.
- Broad source discovery.
- Executable source discovery from query terms.
- Executable LLM source planning.
- Source URL generation or ingestion from LLM output.
- Disease-generic extraction record replacement.
- Mass rename of `HantavirusRecord`.
- Validation refactor.
- Duplicate/event clustering changes.
- Anomaly detection.
- Human review decision application.
- Final product CLI.
- Notebook redesign.
- UI redesign.
- Package/import mass rename.
- Uncontrolled web scraping.

## Review Checklist

- [x] User-facing project name remains **data collection workflow**.
- [x] Internal package name `hdc_workflow` unchanged.
- [x] Hantavirus/New Mexico backward compatibility preserved.
- [x] COVID-19/New York receives disease-aware active profile/schema resources.
- [x] Dengue/Florida receives disease-aware active profile/schema resources.
- [x] Non-hantavirus active schemas are not `hantavirus_human_case_outbreak_schema`.
- [x] Non-hantavirus screening criteria no longer use HPS/hantavirus-specific language.
- [x] `profile_schema_summary` is present in state and final package workflow summaries.
- [x] Stale profile/schema warnings removed for non-hantavirus tasks.
- [x] Remaining future-stage warnings preserved.
- [x] Tests do not require internet access, API keys, live web, or real LLM calls.
- [x] Current hantavirus live-fetch compatibility check passed with all LLM stages disabled.
- [x] Full test suite passed.
