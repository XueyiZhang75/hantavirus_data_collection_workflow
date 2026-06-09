# STAGE 6 REPORT

## Stage Goal

Stage 6 implements source credibility scoring and auditable final source-role
assignment for the data collection workflow.

The goal was to ensure every `source_registry` entry receives:

- deterministic credibility assessment by default
- a final role from the allowed Stage 6 role set
- provenance-rich scoring fields and reasons
- optional LLM credibility advisory behind explicit flags
- exported diagnostics and final-package summaries

This stage did not begin Stage 7.

## Summary Of Changes

- Added deterministic source credibility scoring in
  `src/hdc_workflow/source_credibility.py`.
- Added final source role assignment via `source_role_final` while preserving
  the existing internal `source_role` field for backward compatibility.
- Added task-aware scoring using collection spec, disease intelligence, source
  metadata, executable source-plan/search provenance, role hints, source type,
  domain, publisher, title, snippet, and query metadata.
- Added allowed final roles:
  `collection`, `validation`, `context`, `collection_support`,
  `search_endpoint`, `excluded`, `needs_human_review`.
- Added optional LLM source credibility advisory behind:
  `HDC_ENABLE_LLM_SOURCE_CREDIBILITY`,
  `HDC_LLM_SOURCE_CREDIBILITY_MAX_SOURCES`,
  `HDC_LLM_SOURCE_CREDIBILITY_SOURCE_ID_ALLOWLIST`.
- Added deterministic fallback behavior when optional LLM advisory fails.
- Added `source_credibility_assessments` and `source_credibility_summary` to
  workflow state and final package summaries.
- Exported:
  `diagnostics/source_credibility_summary.json`,
  `diagnostics/source_credibility_assessments.json`,
  and `source_credibility_summary` in `diagnostics/workflow_summaries.json`.
- Updated configured-run readable reports and workflow console summaries to
  display source credibility counts.
- Fixed a regression where official health department `/news/` press releases
  were incorrectly treated as secondary news sources instead of official
  collection sources.
- Added documentation in `docs/source_credibility_scoring.md`.

## Files Changed

Stage 6 relevant files:

- `.env.example`
- `configs/hdc_workflow_run_config.jsonc`
- `docs/source_credibility_scoring.md`
- `docs/stage_reports/STAGE_6_REPORT.md`
- `scripts/build_workflow_run_console.py`
- `scripts/run_hdc_workflow_configured.py`
- `scripts/start_hdc_workflow_studio.py`
- `src/hdc_workflow/llm_clients.py`
- `src/hdc_workflow/models.py`
- `src/hdc_workflow/nodes/source_screening.py`
- `src/hdc_workflow/resources/final_package_policy.json`
- `src/hdc_workflow/runtime_profile.py`
- `src/hdc_workflow/source_credibility.py`
- `src/hdc_workflow/state.py`
- `tests/test_new_mexico_hps_workflow_case.py`
- `tests/test_source_credibility_scoring.py`

Note: the worktree also contains earlier staged-work files from prior stages.
They were not reverted.

## New/Updated Tests

New Stage 6 test file:

- `tests/test_source_credibility_scoring.py`

Covered behavior:

- every registry entry receives credibility fields
- official health department sources score higher than low-quality sources
- official health department `/news/` URLs can remain collection sources
- COVID-19/New York fixture search scoring is disease-aware
- Dengue/Florida fixture search scoring is disease-aware
- context-only sources do not become collection sources
- search endpoints remain `search_endpoint`
- validation-reserved sources remain separated
- ambiguous sources trigger source-level review
- optional LLM source credibility success is mocked
- optional LLM source credibility failure falls back deterministically
- full graph COVID-19 fixture smoke includes source credibility output
- full graph Dengue fixture smoke includes source credibility output
- centralized config maps optional LLM source credibility controls to env vars
- workflow console payload exposes source credibility summary

Updated compatibility test:

- `tests/test_new_mexico_hps_workflow_case.py`

## Commands Run

Focused test/debug commands:

```powershell
python -m pytest tests\test_graph_smoke.py::test_step5_skip_summary_counts_are_granular tests\test_graph_smoke.py::test_default_offline_mode_has_no_conflicts -q
python -m pytest tests\test_graph_smoke.py tests\test_workflow_run_config.py -q
python -m pytest tests\test_source_credibility_scoring.py::test_config_maps_optional_llm_source_credibility_controls_to_env tests\test_source_credibility_scoring.py::test_console_stage_payload_exposes_source_credibility_summary -q
python -m pytest tests\test_source_credibility_scoring.py tests\test_new_mexico_hps_workflow_case.py::test_new_mexico_masked_routing_blocks_validation_pdf -q
python -m pytest tests\test_source_credibility_scoring.py::test_official_health_department_news_url_can_remain_collection -q
python -m pytest tests\test_evaluation_report_builder.py::test_configured_workflow_script_uses_config_without_runtime_confirmations -q
python -m pytest tests\test_source_credibility_scoring.py -q
```

Config check:

```powershell
python scripts\run_hdc_workflow_configured.py --print-config-only
```

Fixture smoke runs:

```powershell
python scripts\run_hdc_workflow_configured.py --config configs\examples\covid19_new_york_2024_fixture_search_task.jsonc --session-id stage6_covid19_fixture_search_credibility_smoke
python scripts\run_hdc_workflow_configured.py --config configs\examples\dengue_florida_2025_fixture_search_task.jsonc --session-id stage6_dengue_fixture_search_credibility_smoke
```

Live Tavily smoke runs:

```powershell
$env:TAVILY_API_KEY = [Environment]::GetEnvironmentVariable('TAVILY_API_KEY','User'); python scripts\run_hdc_workflow_configured.py --config configs\examples\covid19_new_york_2024_live_search_smoke.jsonc --session-id stage6_covid19_live_search_credibility_smoke_escalated
$env:TAVILY_API_KEY = [Environment]::GetEnvironmentVariable('TAVILY_API_KEY','User'); python scripts\run_hdc_workflow_configured.py --config configs\examples\dengue_florida_2025_live_search_smoke.jsonc --session-id stage6_dengue_live_search_credibility_smoke_escalated
```

Hantavirus/New Mexico compatibility smoke:

```powershell
python scripts\run_hdc_workflow_configured.py --config configs\hdc_workflow_run_config.jsonc --disable-all-llm --session-id stage6_hantavirus_live_fetch_compat_no_llm
```

Full suite:

```powershell
python -m pytest -q
```

Secret scans:

```powershell
# Printed counts only, never key values.
TAVILY_KEY_LITERAL_FILE_MATCHES=0
ANTHROPIC_KEY_LITERAL_FILE_MATCHES=0
```

## Test Results

- `tests/test_graph_smoke.py::test_step5_skip_summary_counts_are_granular`
  and `tests/test_graph_smoke.py::test_default_offline_mode_has_no_conflicts`:
  `2 passed`
- `tests/test_graph_smoke.py tests/test_workflow_run_config.py`:
  `132 passed`
- Stage 6 targeted config/console tests: `2 passed`
- Stage 6 plus New Mexico compatibility test: `15 passed`
- Official press release regression test:
  red first, then `1 passed` after the rule fix
- Runner compatibility regression:
  `1 passed`
- Full Stage 6 test file:
  `15 passed`
- Full suite:
  `265 passed in 6.80s`

## Example Command Or Fixture Run

Fixture example:

```powershell
python scripts\run_hdc_workflow_configured.py --config configs\examples\covid19_new_york_2024_fixture_search_task.jsonc --session-id stage6_covid19_fixture_search_credibility_smoke
```

Result summary:

- route: `finalize`
- source search mode: `fixture`
- executed queries: `3`
- search-derived candidates: `1`
- assessed sources: `21`
- search-derived assessed sources: `1`
- workflow console:
  `outputs/sessions/stage6_covid19_fixture_search_credibility_smoke/workflow_console/hdc_workflow_console.html`

## Output Artifacts Created

Stage 6 smoke sessions:

| Session | Mode | Queries | Search candidates | Assessed sources | Search-assessed | Documents | Records | Route |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `stage6_covid19_fixture_search_credibility_smoke` | fixture | 3 | 1 | 21 | 1 | 6 | 0 | finalize |
| `stage6_dengue_fixture_search_credibility_smoke` | fixture | 3 | 1 | 21 | 1 | 6 | 0 | finalize |
| `stage6_covid19_live_search_credibility_smoke_escalated` | live | 2 | 5 | 25 | 5 | 6 | 0 | finalize |
| `stage6_dengue_live_search_credibility_smoke_escalated` | live | 2 | 3 | 23 | 3 | 6 | 0 | finalize |
| `stage6_hantavirus_live_fetch_compat_no_llm` | disabled | 0 | 0 | 20 | 0 | 5 | 5 | human_review |

Important artifact paths:

- `outputs/sessions/stage6_hantavirus_live_fetch_compat_no_llm/diagnostics/source_credibility_summary.json`
- `outputs/sessions/stage6_hantavirus_live_fetch_compat_no_llm/diagnostics/source_credibility_assessments.json`
- `outputs/sessions/stage6_hantavirus_live_fetch_compat_no_llm/diagnostics/workflow_summaries.json`
- `outputs/sessions/stage6_hantavirus_live_fetch_compat_no_llm/collection/source_registry.json`
- `outputs/sessions/stage6_hantavirus_live_fetch_compat_no_llm/workflow_console/hdc_workflow_console.html`

Hantavirus/New Mexico compatibility source credibility summary:

- assessed sources: `20`
- final role counts:
  `collection=3`, `context=7`, `validation=4`, `search_endpoint=6`
- high/medium/low counts:
  `high=8`, `medium=11`, `low=1`
- optional LLM source credibility:
  `enabled=false`, `llm_assessed_count=0`, `llm_failure_count=0`

## Known Limitations

- Deterministic scoring is metadata-based. It does not read page bodies when
  assigning source credibility.
- Optional LLM source credibility is advisory only and was tested with mocks,
  not real LLM calls.
- Live Tavily smoke tests require a User-scope `TAVILY_API_KEY` and network
  access; in this run they required elevated execution because the normal
  sandbox could not read the User-scope key.
- The live search smoke configs still combine search-derived candidates with
  the existing seed catalog for bounded compatibility testing.
- Hantavirus/New Mexico compatibility used deterministic extraction only
  because the command explicitly disabled all LLM stages.
- `source_role` remains an internal backward-compatible field; consumers should
  use `source_role_final` for Stage 6 final role assignment.

## Future-Stage Items Not Implemented

The following were explicitly not implemented in Stage 6:

- Stage 7
- broad crawling
- fetch/parse generalization
- validation refactor
- generic extraction schema redesign
- duplicate clustering
- anomaly detection
- human-review decision application
- search-result ingestion beyond Stage 5 bounded source discovery
- CLI redesign
- notebook redesign
- UI redesign beyond exposing Stage 6 summaries in the existing console
- real LLM source credibility smoke calls

## Review Checklist

- [x] Project name preserved as data collection workflow.
- [x] Internal package name `hdc_workflow` preserved.
- [x] Graph topology unchanged.
- [x] Default offline deterministic behavior preserved.
- [x] Tests do not require internet, API keys, live web, or real LLM calls.
- [x] Optional LLM source credibility is behind explicit flags.
- [x] No real API keys printed or committed.
- [x] Every source registry entry receives `source_role_final`.
- [x] Every source registry entry receives score components and reasons.
- [x] Diagnostics and final package summaries include source credibility output.
- [x] Fixture smokes completed.
- [x] Live Tavily smokes completed with User-scope key.
- [x] Hantavirus/New Mexico compatibility smoke completed.
- [x] Full `pytest -q` completed successfully.
- [x] Stage 7 and future-stage items were not implemented.
