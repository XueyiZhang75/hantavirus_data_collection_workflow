# Stage 4 Report: LLM Executable Source Planning

## Stage Goal

Upgrade source planning in the **data collection workflow** from advisory-only LLM suggestions into an auditable executable source discovery plan.

Stage 4 creates source objectives, source role categories, provider-aware planned queries, risks, fallback behavior, and compact workflow summaries. It intentionally does not execute web search, call a search provider, ingest search results, or convert planned queries into source candidates.

## Summary of Changes

- Added structured executable source-planning Pydantic models:
  - `ExecutableSourcePlan`
  - `SourceDiscoveryObjective`
  - `PlannedSourceCategory`
  - `PlannedSearchQuery`
  - `SourcePlanningRisk`
- Added `executable_source_planning` after `profile_and_schema_setup` and before `query_strategy_builder`.
- Preserved graph topology otherwise; no Stage 5 graph changes were made.
- Refactored `query_strategy_builder` so it consumes `agentic_source_plan.planned_queries` instead of calling the LLM source planner directly.
- Added deterministic executable source-plan generation for offline/default runs.
- Added optional one-call LLM executable source planning via `llm_clients.run_pydantic_structured_llm(..., schema_model=ExecutableSourcePlan)`.
- Added deterministic fallback when LLM source planning fails.
- Added URL sanitization for LLM planned query text; LLM-proposed URLs are not inserted into `source_candidates`, `source_registry`, or fetch requests.
- Added/kept auditable state outputs:
  - `agentic_source_plan`
  - `executable_source_plan_summary`
  - enriched `source_planning_agent_summary`
- Updated final package `workflow_summaries`, configured-run diagnostics, configured-run report text, and HTML workflow console payloads to include executable source-planning results.
- Added a narrow Stage 4 LLM source-planning smoke config. It is not a final product CLI and does not execute search or fetch URLs.
- Fixed configured-run diagnostics so `diagnostics/workflow_summaries.json` includes source-discovery and downstream summaries needed for acceptance review.
- Fixed configured-run `diagnostics/live_fetch_summary.json` so `live_fetch_enabled` reflects the actual `content_fetch_summary.live_fetch_enabled` value instead of always reporting `true`.

## Files Changed

- `README.md`
- `configs/examples/stage4_llm_source_planning_smoke_task.jsonc`
- `docs/executable_source_planning.md`
- `docs/stage_reports/STAGE_4_REPORT.md`
- `scripts/build_workflow_run_console.py`
- `scripts/run_hdc_workflow_configured.py`
- `src/hdc_workflow/graph.py`
- `src/hdc_workflow/models.py`
- `src/hdc_workflow/nodes/__init__.py`
- `src/hdc_workflow/nodes/task_scope.py`
- `src/hdc_workflow/resources/final_package_policy.json`
- `src/hdc_workflow/runtime_profile.py`
- `src/hdc_workflow/state.py`
- `tests/test_agentic_llm_workflow_hooks.py`
- `tests/test_executable_source_planning.py`
- `tests/test_graph_smoke.py`
- `tests/test_profile_schema_setup.py`

## Code Inspection Findings

- `docs/final_product_target.md` requires LLM-driven source planning and executable search query generation, while real source discovery belongs to a later stage.
- `docs/current_state_audit.md` identified advisory source planning inside `query_strategy_builder` as a blocker.
- `docs/structured_task_input.md`, `docs/disease_intelligence_layer.md`, and `docs/profile_schema_setup.md` show the upstream task/disease/profile layers now provide disease-aware inputs for source planning.
- `docs/stage_reports/STAGE_1_REPORT.md`, `STAGE_2_REPORT.md`, and `STAGE_3_REPORT.md` confirm executable source planning had not been implemented earlier.
- `src/hdc_workflow/agents/source_planning_agent.py` remains a legacy advisory helper. Stage 4 keeps it available but moves graph source planning to the new executable node.
- `src/hdc_workflow/nodes/source_discovery.py` still uses the offline seed catalog. Stage 4 does not change this into live search.
- `src/hdc_workflow/resources/final_package_policy.json` needed `executable_source_plan_summary` so final outputs expose the new plan.
- Configured-run diagnostics needed `source_discovery_summary` and related summaries so acceptance artifacts clearly show `offline_seed_catalog` behavior.

## New/Updated Tests

Added/updated `tests/test_executable_source_planning.py`:

- `test_deterministic_executable_source_plan_is_auditable_and_not_executed`
- `test_executable_source_plan_is_disease_aware_for_covid_and_dengue`
- `test_llm_executable_source_plan_is_called_once_and_consumed_by_query_strategy`
- `test_llm_planned_urls_are_sanitized_and_not_ingested_as_sources`
- `test_final_package_exports_executable_source_plan_summary`
- `test_full_graph_covid19_exports_executable_source_plan_summary`
- `test_full_graph_dengue_exports_executable_source_plan_summary`

Updated:

- `tests/test_agentic_llm_workflow_hooks.py`
  - Default-off source planning now expects a deterministic executable plan.
  - LLM source planning mock now returns `ExecutableSourcePlan`.
  - LLM failure now expects one call and deterministic fallback.
- `tests/test_graph_smoke.py`
  - Major workflow summaries now include `executable_source_plan_summary`.
- `tests/test_profile_schema_setup.py`
  - Final package policy test now asserts `executable_source_plan_summary` is exported.

The COVID-19 and dengue full-graph tests verify:

- final package workflow summaries include `executable_source_plan_summary`
- executable source plan queries are present in `search_query_inventory`
- planned queries remain `planned_not_executed`
- source discovery remains `offline_seed_catalog`
- no source candidates or registry entries are created from executable source-plan execution

## Commands Run

```powershell
git status --short
git branch --show-current
git rev-parse HEAD

python -m pytest tests\test_executable_source_planning.py -q
python -m pytest -q

python scripts\run_hdc_workflow_configured.py --config configs\examples\covid19_new_york_2024_task.jsonc --session-id stage4_covid19_executable_plan_offline
python scripts\run_hdc_workflow_configured.py --config configs\examples\dengue_florida_2025_task.jsonc --session-id stage4_dengue_executable_plan_offline
python scripts\run_hdc_workflow_configured.py --config configs\examples\stage4_llm_source_planning_smoke_task.jsonc --session-id stage4_llm_source_planning_smoke_attempt
python scripts\run_hdc_workflow_configured.py --config configs\hdc_workflow_run_config.jsonc --disable-all-llm --session-id stage4_hantavirus_live_compat_no_llm
```

Git result summary:

- Branch: `main`
- HEAD: `0a74ec8ca7f3ed9ab3b3f7af834de7421a2efb88`
- `git status --short`: dirty worktree with modified and untracked Stage 0-4 files; no destructive cleanup or revert was performed.

## Test Results

- `tests/test_executable_source_planning.py`: 7 passed in 0.41s.
- Full suite: 237 passed in 5.54s.

## Offline Configured Smoke Runs

### COVID-19 / New York / 2024

Command:

```powershell
python scripts\run_hdc_workflow_configured.py --config configs\examples\covid19_new_york_2024_task.jsonc --session-id stage4_covid19_executable_plan_offline
```

Report:

- Output directory: `outputs/sessions/stage4_covid19_executable_plan_offline/`
- `trace_node_count`: 19
- `current_route`: `finalize`
- `package_metadata.disease`: `COVID-19`
- `package_metadata.geography`: `New York`
- `package_metadata.time_window`: `2024`
- `package_metadata.web_search_used`: `false`
- `executable_source_plan_summary.execution_status`: `planned_not_executed`
- `executable_source_plan_summary.planned_query_count`: 10
- `executable_source_plan_summary.planned_source_category_count`: 5
- `source_planning_agent_summary.status`: `deterministic_plan_created`
- `source_discovery_summary.discovery_method`: `offline_seed_catalog`
- `normalized_record_count`: 0
- `human_review_item_count`: 1
- `live_fetch_enabled`: `false`
- `fetch_status_counts`: `{"offline_stub": 6}`
- `quality_status_counts`: `{"offline_stub_pending_live_fetch": 6}`
- Planned queries were not executed.
- No search provider was used.
- No real LLM was required.

Artifacts:

- `outputs/sessions/stage4_covid19_executable_plan_offline/workflow_run_report_chinese.md`
- `outputs/sessions/stage4_covid19_executable_plan_offline/diagnostics/workflow_summaries.json`
- `outputs/sessions/stage4_covid19_executable_plan_offline/workflow_console/hdc_workflow_console.html`

### Dengue / Florida / 2025

Command:

```powershell
python scripts\run_hdc_workflow_configured.py --config configs\examples\dengue_florida_2025_task.jsonc --session-id stage4_dengue_executable_plan_offline
```

Report:

- Output directory: `outputs/sessions/stage4_dengue_executable_plan_offline/`
- `trace_node_count`: 19
- `current_route`: `finalize`
- `package_metadata.disease`: `dengue`
- `package_metadata.geography`: `Florida`
- `package_metadata.time_window`: `2025`
- `package_metadata.web_search_used`: `false`
- `executable_source_plan_summary.execution_status`: `planned_not_executed`
- `executable_source_plan_summary.planned_query_count`: 10
- `executable_source_plan_summary.planned_source_category_count`: 5
- `source_planning_agent_summary.status`: `deterministic_plan_created`
- `source_discovery_summary.discovery_method`: `offline_seed_catalog`
- `normalized_record_count`: 0
- `human_review_item_count`: 1
- `live_fetch_enabled`: `false`
- `fetch_status_counts`: `{"offline_stub": 6}`
- `quality_status_counts`: `{"offline_stub_pending_live_fetch": 6}`
- Planned queries were not executed.
- No search provider was used.
- No real LLM was required.

Artifacts:

- `outputs/sessions/stage4_dengue_executable_plan_offline/workflow_run_report_chinese.md`
- `outputs/sessions/stage4_dengue_executable_plan_offline/diagnostics/workflow_summaries.json`
- `outputs/sessions/stage4_dengue_executable_plan_offline/workflow_console/hdc_workflow_console.html`

## LLM Source Planning Smoke Attempt

PASSED.

Command:

```powershell
python scripts\run_hdc_workflow_configured.py --config configs\examples\stage4_llm_source_planning_smoke_task.jsonc --session-id stage4_llm_source_planning_smoke_attempt
```

Report:

- Output directory: `outputs/sessions/stage4_llm_source_planning_smoke_attempt/`
- Provider/model: `anthropic` / `claude-sonnet-4-6`
- API key present: `true`
- API key value printed: `false`
- `package_metadata.disease`: `hantavirus`
- `package_metadata.geography`: `New Mexico`
- `package_metadata.time_window`: `2020-2026`
- `generation_method`: `llm_executable_source_plan`
- `llm_enabled`: `true`
- `source_planning_agent_summary.status`: `success`
- `planned_query_count`: 10
- `planned_source_category_count`: 5
- `execution_status`: `planned_not_executed`
- `warnings`: `["source_plan_created_not_executed_stage4", "source_discovery_execution_not_implemented_stage4", "all_planned_queries_are_planned_not_executed_no_urls_fetched", "sin_nombre_virus_is_dominant_hantavirus_strain_in_new_mexico_queries_weighted_accordingly", "hfrs_less_likely_in_new_mexico_but_included_for_completeness"]`
- `url_sanitized_count`: 0
- Fallback used: `false`
- `source_discovery_summary.discovery_method`: `offline_seed_catalog`
- `package_metadata.web_search_used`: `false`
- `live_fetch_enabled`: `false`
- `fetch_status_counts`: `{"offline_stub": 6}`

This smoke enabled only LLM source planning. It did not enable live fetch, LLM source critic, LLM structured extraction, real search, or planned-query execution. No webpage evidence was sent to the LLM, and no LLM-proposed URL was inserted into `source_candidates` or `source_registry`.

Artifacts:

- `outputs/sessions/stage4_llm_source_planning_smoke_attempt/workflow_run_report_chinese.md`
- `outputs/sessions/stage4_llm_source_planning_smoke_attempt/diagnostics/workflow_summaries.json`
- `outputs/sessions/stage4_llm_source_planning_smoke_attempt/diagnostics/llm_stage_summary.json`
- `outputs/sessions/stage4_llm_source_planning_smoke_attempt/workflow_console/hdc_workflow_console.html`

## Hantavirus Live-Fetch Compatibility

PASSED.

Command:

```powershell
python scripts\run_hdc_workflow_configured.py --config configs\hdc_workflow_run_config.jsonc --disable-all-llm --session-id stage4_hantavirus_live_compat_no_llm
```

Report:

- Output directory: `outputs/sessions/stage4_hantavirus_live_compat_no_llm/`
- `live_fetch_enabled`: `true`
- All LLM stages disabled: `true`
- `document_count`: 5
- `usable_document_count`: 5
- `fetch_status_counts`: `{"fetched": 5}`
- `quality_status_counts`: `{"usable": 5}`
- `normalized_record_count`: 5
- `human_review_item_count`: 8
- `executable_source_plan_summary` present: `true`
- `executable_source_plan_summary.execution_status`: `planned_not_executed`
- `source_discovery_summary.discovery_method`: `offline_seed_catalog`
- `package_metadata.web_search_used`: `false`
- No search provider used: `true`
- No LLM prompt or webpage evidence was sent to an LLM API during this live compatibility run.

Artifacts:

- `outputs/sessions/stage4_hantavirus_live_compat_no_llm/workflow_run_report_chinese.md`
- `outputs/sessions/stage4_hantavirus_live_compat_no_llm/diagnostics/live_fetch_summary.json`
- `outputs/sessions/stage4_hantavirus_live_compat_no_llm/diagnostics/workflow_summaries.json`
- `outputs/sessions/stage4_hantavirus_live_compat_no_llm/workflow_console/hdc_workflow_console.html`

## Live Acceptance Result

PASSED.

Reason:

- `python -m pytest -q` passed: 237 tests passed in 5.54s.
- COVID-19/New York offline configured smoke passed.
- Dengue/Florida offline configured smoke passed.
- LLM source planning smoke completed successfully with actual LLM generation: `generation_method=llm_executable_source_plan`.
- Current hantavirus/New Mexico live-fetch compatibility ran successfully with all LLM stages disabled.
- Planned queries remained `planned_not_executed`.
- `source_discovery` remained `offline_seed_catalog`.
- No real search provider was implemented or used.
- No source candidates were created from executable source-plan execution.
- No LLM-proposed URLs were ingested into `source_candidates` or `source_registry`.

## Output Artifacts Created

- `docs/executable_source_planning.md`
- `docs/stage_reports/STAGE_4_REPORT.md`
- `configs/examples/stage4_llm_source_planning_smoke_task.jsonc`
- `outputs/sessions/stage4_covid19_executable_plan_offline/`
- `outputs/sessions/stage4_dengue_executable_plan_offline/`
- `outputs/sessions/stage4_llm_source_planning_smoke_attempt/`
- `outputs/sessions/stage4_hantavirus_live_compat_no_llm/`

## Known Limitations

- No real source discovery/search provider yet.
- Planned queries are not executed.
- Search result ingestion is not implemented.
- Converting planned queries into source candidates is not implemented.
- Source credibility scoring overhaul is not implemented.
- Fetch/parse generalization is not implemented.
- Disease-generic extraction record model is not implemented.
- Validation refactor is not implemented.
- Duplicate clustering is not implemented.
- Anomaly detection is not implemented.
- Human review decision application is not implemented.
- CLI/notebook/UI redesign is not implemented.

## Future-Stage Items Not Implemented

- Real source discovery/search provider.
- Search result ingestion.
- Converting planned queries into source candidates.
- Source credibility scoring overhaul.
- Fetch/parse/extraction generalization.
- Generic record schema.
- Validation refactor.
- Duplicate/event clustering.
- Anomaly detection.
- Human review decision application.
- CLI/notebook/UI.

## Review Checklist

- [x] User-facing project name remains "data collection workflow".
- [x] Internal package name `hdc_workflow` was not mass-renamed.
- [x] `executable_source_planning` node exists.
- [x] `agentic_source_plan` exists.
- [x] `executable_source_plan_summary` exists.
- [x] `source_planning_agent_summary` exists.
- [x] Planned queries have `execution_status = planned_not_executed`.
- [x] Query inventory consumes executable source plan queries.
- [x] COVID-19 source plan is COVID-19/New York/2024-specific.
- [x] Dengue source plan is dengue/Florida/2025-specific.
- [x] Hantavirus source plan remains backward-compatible.
- [x] LLM source planning is optional and has deterministic fallback.
- [x] LLM URL output is sanitized and not ingested.
- [x] Source discovery does not execute planned queries in Stage 4.
- [x] No source candidates are created from LLM-proposed URLs.
- [x] Full graph offline COVID-19 configured smoke run completed.
- [x] Full graph offline dengue configured smoke run completed.
- [x] Current hantavirus/New Mexico live-fetch compatibility was attempted.
- [x] LLM source planning smoke was attempted and passed.
- [x] `pytest` was run.
- [x] No API keys or secrets were printed.
- [x] No real search provider was implemented.
- [x] No real source discovery was implemented.
- [x] No future-stage features were implemented.
