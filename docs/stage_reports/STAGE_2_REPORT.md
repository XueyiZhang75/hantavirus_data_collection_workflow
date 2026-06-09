# Stage 2 Report: Disease Intelligence Layer

## Stage Goal

Implement the Stage 2 disease intelligence layer for the **data collection workflow** so structured disease tasks can produce auditable disease-specific terminology, source needs, query terms, validation source categories, and warnings before downstream source planning.

Stage 2 was limited to the disease intelligence layer. It did not implement broad web search, executable source discovery, generic extraction schemas, validation refactors, duplicate handling, anomaly detection, human review decision application, CLI redesign, notebook redesign, or UI redesign.

## Summary of Changes

- Added a `DiseaseIntelligenceProfile` model.
- Added deterministic curated disease intelligence profiles for hantavirus, COVID-19, and dengue.
- Added a new LangGraph node named `disease_intelligence_builder` after `task_intake_and_scope_planning`.
- Added `disease_intelligence` and `disease_intelligence_summary` to workflow state and Studio initial state.
- Added deterministic fallback behavior for unknown diseases.
- Added an optional LLM disease-intelligence path controlled by `HDC_ENABLE_LLM_DISEASE_INTELLIGENCE`.
- Added LLM fallback warnings when model calls fail and curated/generic fallback is used.
- Updated query strategy generation so query terms can differ by task disease when disease intelligence is available.
- Added `disease_intelligence_summary` to final package workflow summaries.
- Added centralized config and `.env.example` controls for the new optional LLM stage.
- Added Stage 2 documentation at `docs/disease_intelligence_layer.md`.
- Preserved default offline deterministic behavior.

## Files Changed

- `.env.example`
- `README.md`
- `configs/hdc_workflow_run_config.jsonc`
- `docs/disease_intelligence_layer.md`
- `docs/stage_reports/STAGE_2_REPORT.md`
- `scripts/run_hdc_workflow_configured.py`
- `src/hdc_workflow/config.py`
- `src/hdc_workflow/graph.py`
- `src/hdc_workflow/llm_clients.py`
- `src/hdc_workflow/models.py`
- `src/hdc_workflow/nodes/__init__.py`
- `src/hdc_workflow/nodes/task_scope.py`
- `src/hdc_workflow/resources/disease_intelligence/hantavirus.json`
- `src/hdc_workflow/resources/disease_intelligence/covid19.json`
- `src/hdc_workflow/resources/disease_intelligence/dengue.json`
- `src/hdc_workflow/resources/final_package_policy.json`
- `src/hdc_workflow/runtime_profile.py`
- `src/hdc_workflow/state.py`
- `tests/test_disease_intelligence.py`
- `tests/test_graph_smoke.py`
- `tests/test_workflow_run_config.py`

## Code Inspection Findings

- `task_intake_and_scope_planning` now preserves structured task inputs from Stage 1, but downstream profile/schema resources were still hantavirus-specific.
- `hantavirus_profile_and_schema_setup` still loads the current hantavirus profile and collection schema. Stage 2 intentionally did not genericize this node.
- `query_strategy_builder` previously relied on the static hantavirus `DiseaseProfile.include_terms`, `syndrome_terms`, and `virus_terms`.
- The graph is serial. Stage 2 only inserted the approved `disease_intelligence_builder` node immediately after task intake.
- `final_package_policy.json` already exports workflow summaries, so `disease_intelligence_summary` could be added without changing final package structure.
- Existing LLM helpers already supported provider selection and structured-output fallback; Stage 2 added a separate feature flag for disease intelligence.

## New/Updated Tests

Added `tests/test_disease_intelligence.py`:

- `test_curated_hantavirus_disease_intelligence_terms`
- `test_curated_covid19_disease_intelligence_terms_not_hantavirus_primary`
- `test_curated_dengue_disease_intelligence_terms_not_hantavirus_primary`
- `test_full_graph_covid19_exports_disease_intelligence_summary`
- `test_full_graph_dengue_exports_disease_intelligence_summary`
- `test_llm_disease_intelligence_success_and_failure_fallback`
- `test_query_terms_differ_by_disease`

Updated:

- `tests/test_graph_smoke.py`
  - Verifies `disease_intelligence_summary` is included in major workflow summaries.
- `tests/test_workflow_run_config.py`
  - Verifies centralized config emits `HDC_ENABLE_LLM_DISEASE_INTELLIGENCE=false` by default.

These tests cover deterministic curated profiles, non-hantavirus tasks, query-term differentiation, full graph export, optional LLM success, optional LLM failure fallback, and default offline behavior.

## Commands Run

```powershell
python -m pytest tests\test_disease_intelligence.py -q
python -m pytest tests\test_disease_intelligence.py tests\test_workflow_run_config.py -q
python -m pytest tests\test_graph_smoke.py -q
python -m pytest tests\test_disease_intelligence.py tests\test_structured_task_input.py tests\test_workflow_run_config.py -q
python -m pytest -q
```

Live LLM smoke commands were also run with a direct Python stdin snippet that:

- set `HDC_ENABLE_LLM_DISEASE_INTELLIGENCE=true`
- set all other LLM workflow stages to false
- set `HDC_ENABLE_LIVE_FETCH=false`
- used a COVID-19/New York structured task
- invoked only `task_intake_and_scope_planning` and `disease_intelligence_builder`
- printed only non-secret summary metadata

## Test Results

- Stage 2 tests: 7 passed.
- Stage 2 + workflow config targeted tests: 9 passed.
- Graph smoke tests: 130 passed.
- Stage 2 + Stage 1 structured task/config targeted tests: 18 passed.
- Full test suite: 222 passed.

## Live LLM Smoke Attempt

Stage 2 required a live LLM smoke attempt for the disease intelligence layer. No live web fetch was enabled, and no webpage evidence was sent.

First non-escalated attempt:

- Result: LLM connection failed inside the restricted sandbox.
- Failure class: `ValueError`
- Underlying cause: `APIConnectionError: Connection error`
- Workflow behavior: fell back to curated COVID-19 disease intelligence.
- Fallback summary:
  - `generation_method`: `llm_failed_curated_fallback`
  - `disease_standard_name`: `COVID-19`
  - `query_term_count`: 5
  - warnings included `llm_disease_intelligence_failed_curated_fallback` and `llm_failure_type:ValueError`

Escalated network rerun:

- Result: PASSED.
- Provider/model: `anthropic` / `claude-sonnet-4-6`
- `generation_method`: `llm_generated`
- `disease_standard_name`: `COVID-19`
- `query_term_count`: 10
- The returned warnings were disease/task-specific and included source-planning cautions such as not double-counting NYSDOH and NYC DOHMH reporting, checking 2024 reporting availability, verifying CDC framework transitions, and not inventing source URLs.

No API key was printed or committed.

## Example Command or Fixture Run

Offline deterministic Stage 2 verification:

```powershell
python -m pytest tests\test_disease_intelligence.py -q
```

Full workflow verification:

```powershell
python -m pytest -q
```

The tests invoke the full graph for COVID-19/New York and dengue/Florida example configs without internet access, API keys, live web, or real LLM calls.

## Output Artifacts Created

- `docs/disease_intelligence_layer.md`
- `docs/stage_reports/STAGE_2_REPORT.md`
- `src/hdc_workflow/resources/disease_intelligence/hantavirus.json`
- `src/hdc_workflow/resources/disease_intelligence/covid19.json`
- `src/hdc_workflow/resources/disease_intelligence/dengue.json`

No new session export directory was required for Stage 2. The live LLM smoke printed a safe summary only.

## Known Limitations

- The current `hantavirus_profile_and_schema_setup` node remains hantavirus-specific.
- The current extraction schema remains the existing hantavirus record schema.
- Non-hantavirus full graph runs still carry Stage 1 warnings that downstream source discovery and profile/schema setup are not yet generalized.
- Disease intelligence query terms are used to build query inventories, but they are not executed against any real search provider.
- Curated profiles are lightweight and should be expanded in later stages.
- Optional LLM disease intelligence depends on provider connectivity, installed provider packages, valid model access, and an API key.
- LLM disease intelligence is advisory only; it does not add source URLs or validate records.

## Future-Stage Items Not Implemented

- Broad real web search.
- Search provider integration.
- Executable source discovery from generated query terms.
- Generic disease profile/schema setup.
- Disease-generic extraction schema replacement.
- Validation source refactor.
- Duplicate clustering changes.
- Anomaly detection.
- Human review decision application.
- Human review UI.
- CLI, notebook, or UI redesign.
- Source credibility scoring.
- Source URL generation from an LLM.
- Graph topology changes beyond the approved `disease_intelligence_builder` node.
- Package/import mass rename.

## Review Checklist

- [x] User-facing project name remains **data collection workflow**.
- [x] Internal package name `hdc_workflow` unchanged.
- [x] Default offline deterministic behavior preserved.
- [x] Tests do not require internet access, API keys, live web, or real LLM calls.
- [x] Curated profiles exist for hantavirus, COVID-19, and dengue.
- [x] Unknown-disease fallback remains deterministic.
- [x] Optional LLM path is gated by an explicit environment flag.
- [x] LLM failure falls back with auditable warnings.
- [x] No broad real web search was implemented.
- [x] No source URLs are invented by the disease intelligence layer.
- [x] Final package workflow summaries include `disease_intelligence_summary`.
- [x] New behavior is covered by tests.
- [x] Full test suite passed.
