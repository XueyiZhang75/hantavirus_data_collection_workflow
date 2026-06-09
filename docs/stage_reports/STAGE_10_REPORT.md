# Stage 10 Report: Validation Refactor / Trusted-Source + Cross-Source Validation

## 1. Stage goal

Stage 10 makes validation explicit and auditable for the data collection workflow. It adds trusted-source / held-out comparison, cross-source support and conflict checks, scope validation, and count semantics comparability while preserving existing `conflicts` and `cross_source_consistency_summary`.

The user-facing project name remains `data collection workflow`. The internal package name remains `hdc_workflow`.

## 2. Summary of changes

- Added validation models for cases, comparisons, results, comparability assessment, and validation summaries.
- Added graph-native validation outputs: `validation_cases`, `validation_comparisons`, `validation_results`, `validation_summary`, `trusted_source_validation_summary`, and `cross_source_validation_summary`.
- Reused and upgraded the existing `cross_source_consistency_check` node without changing graph topology.
- Added trusted-source / held-out validation against `validation_records`.
- Added cross-source validation using Stage 9 `event_clusters` and independent source support.
- Added scope validation for disease, geography, time window, and insufficient scope information.
- Added count semantics comparability checks to avoid unsafe cumulative/new/annual/weekly comparisons.
- Added validation-related human review items without applying review decisions.
- Updated final package, collection exports, diagnostics, and console summary payloads.

## 3. Files created or modified

Created:

- `docs/validation_refactor.md`
- `docs/stage_reports/STAGE_10_REPORT.md`
- `tests/test_validation_refactor.py`

Modified for Stage 10:

- `src/hdc_workflow/models.py`
- `src/hdc_workflow/state.py`
- `src/hdc_workflow/nodes/linking_validation.py`
- `src/hdc_workflow/nodes/finalization.py`
- `src/hdc_workflow/resources/final_package_policy.json`
- `src/hdc_workflow/runtime_profile.py`
- `src/hdc_workflow/export.py`
- `scripts/run_hdc_workflow_configured.py`
- `scripts/build_workflow_run_console.py`

The working tree also contains earlier Stage 1-9 changes. They were not reverted.

## 4. Functional changes made

`cross_source_consistency_check` now creates explicit validation artifacts while keeping the existing `conflicts` output. It performs scope checks, cross-source support checks, trusted-source / held-out comparisons, count-semantics checks, aggregate comparisons, and conflict routing.

Validation result creation records left/right records, sources, fields, values, disease, location, period, count semantics, comparability status, match status, validation status, confidence, reason, evidence summary, review flag, and warnings.

Conflict output remains backward-compatible. Cross-source conflicts still populate `conflicts`; validation conflicts also create validation results and validation review items.

Human review queue now includes validation review items for scope issues, trusted-source conflicts, missing collection counterparts, incompatible count semantics, and cross-source conflicts. Review decisions are not applied.

Finalization includes validation cases, comparisons, results, and summaries in `FinalDataPackage`.

Diagnostics now export validation JSON files and include validation summaries in `workflow_summaries.json`.

Configured runner now injects configured ground-truth validation records into graph state before invocation, so held-out validation is graph-native. Existing evaluation helper outputs remain available.

## 5. Validation model behavior

Added or formalized:

- `ValidationCase`
- `ValidationComparison`
- `ValidationResult`
- `ValidationUnit`
- `ComparabilityAssessment`
- `TrustedSourceValidationResult`
- `CrossSourceValidationResult`

Validation types:

- `trusted_source_comparison`
- `held_out_source_comparison`
- `cross_source_support`
- `cross_source_conflict`
- `event_cluster_support`
- `aggregate_comparison`
- `scope_check`
- `count_semantics_check`
- `provenance_check`

Validation units:

- `record`
- `event_cluster`
- `aggregate`
- `field`
- `source`
- `scope`

Comparability statuses:

- `comparable`
- `partially_comparable`
- `not_comparable`
- `insufficient_information`
- `needs_human_review`

Match statuses and validation statuses explicitly distinguish matched, conflict, missing validation, missing collection, not comparable, outside scope, needs review, and unvalidated cases.

## 6. Trusted-source validation behavior

Held-out validation records enter graph state through `validation_records`. Configured runs load these from the validation ground-truth CSV before invoking LangGraph.

Validation-reserved sources remain separated from collection sources. They are used as right-side comparison evidence, not extraction input.

Comparable records are compared field by field using disease, location, time/period, statistical count type, and count semantics. Missing counterparts are explicit:

- `missing_validation` when collection has no comparable held-out record
- `missing_collection` when held-out validation has no comparable collection record
- `not_comparable` when disease/location/time/count semantics make comparison unsafe

Aggregate comparison uses Stage 9 `countable=true` records only. Non-countable duplicate records are excluded from aggregate left values.

## 7. Cross-source validation behavior

Cross-source validation uses `event_clusters` and normalized records. It records whether each event cluster has independent support.

Independent support is based on distinct source URLs or source IDs. Same-URL duplicates do not inflate support counts. Duplicate records do not inflate countable aggregate values.

Official sources plus independent secondary or news support can validate an event cluster. Conflicting values create `cross_source_conflict` validation results and backward-compatible `conflicts`.

## 8. Scope and count semantics validation behavior

Scope validation checks:

- task disease vs record disease
- task geography vs record geography
- task start/end year vs record date/reporting period
- missing date/location for count-bearing records

Outside-scope records are not deleted. They receive validation results and review reasons.

Count semantics validation prevents unsafe matches for:

- cumulative vs annual
- cumulative vs newly reported
- annual vs weekly/daily
- newly reported vs historical total
- unknown/unspecified count semantics when comparability is unclear

## 9. Human review routing

Validation-related review items are created for:

- trusted-source conflicts
- missing collection counterparts
- cross-source conflicts
- outside requested time window
- outside requested geography
- disease mismatch
- insufficient scope information
- unclear or incompatible count semantics
- aggregate conflicts

Review item payloads include validation result ID, validation case ID, event cluster ID when available, record IDs, source IDs, source URLs, compared field, left/right values, reason, suggested action, and evidence summary.

Human review decision application was not implemented.

## 10. Disease-specific examples

### COVID-19 / New York / 2024

Fixture validation smoke:

- Normalized record count: 2
- Event cluster count: 2
- Validation result count: 7
- Trusted-source validation count: 3
- Cross-source validation count: 2
- Scope-check count: 2
- Conflict count: 0
- Needs-review validation count: 2
- Example validation result: `val_result_001`, `scope_check`, `matched`, `validated`, reason `record is within requested task scope`

Live validation smoke:

- Normalized record count: 3
- Event cluster count: 3
- Validation result count: 10
- Trusted-source validation count: 4
- Cross-source validation count: 3
- Scope-check count: 3
- Conflict count: 0
- Needs-review validation count: 6

### Dengue / Florida / 2025

Fixture validation smoke:

- Normalized record count: 2
- Event cluster count: 2
- Validation result count: 7
- Trusted-source validation count: 3
- Cross-source validation count: 2
- Scope-check count: 2
- Conflict count: 0
- Needs-review validation count: 2
- Disease remained `Dengue`.

Live validation smoke:

- Normalized record count: 6
- Event cluster count: 5
- Validation result count: 19
- Trusted-source validation count: 7
- Cross-source validation count: 6
- Scope-check count: 6
- Conflict count: 1
- Needs-review validation count: 10

### Hantavirus / New Mexico compatibility

- Normalized record count: 5
- Validation result count: 17
- Held-out validation source behavior: configured ground-truth CSV entered graph state as `validation_records`; validation-reserved source remained separated from collection.
- Existing conflicts compatibility: `conflicts` and `cross_source_consistency_summary` remain available.
- Compatibility status: PASSED with all LLM stages disabled.

## 11. Integration with workflow

Normalized records and event clusters feed the existing `cross_source_consistency_check` node. The node now emits validation artifacts and still emits conflicts.

Validation results feed the human review queue through validation review items. Final records and clusters are not automatically modified by validation.

Final package exports validation cases, comparisons, results, summaries, conflicts, and review items. Diagnostics export validation JSON files and workflow summary fields.

## 12. Backward compatibility

- `conflicts` remains available.
- `cross_source_consistency_summary` remains available.
- Hantavirus/New Mexico behavior remains compatible.
- `linked_events` and `event_clusters` remain compatible.
- Graph topology was not changed.
- Existing evaluation review items remain first in configured runner exports for compatibility with earlier evaluation tests.

## 13. Tests added or updated

Added:

- `tests/test_validation_refactor.py`

Coverage includes:

- validation models are importable
- scope validation outside time window
- disease mismatch
- outside geography
- insufficient scope information
- trusted-source match
- trusted-source conflict
- missing validation counterpart
- missing collection counterpart
- incompatible count semantics are not falsely matched
- cross-source independent support
- duplicate records do not inflate support
- cross-source conflict review routing
- aggregate validation uses countable records only
- audit fields are present on validation results
- final package exports validation artifacts
- COVID-19 fixture validation smoke
- Dengue fixture validation smoke
- Hantavirus/New Mexico validation compatibility

## 14. Commands run

Repository:

```powershell
git status --short
git branch --show-current
git rev-parse HEAD
```

Targeted tests:

```powershell
python -m pytest tests\test_validation_refactor.py -q
```

Regression subset:

```powershell
python -m pytest tests\test_duplicate_event_clustering.py tests\test_generic_structured_extraction.py tests\test_fetch_parse_generalization.py tests\test_source_credibility_scoring.py tests\test_real_source_discovery.py tests\test_executable_source_planning.py tests\test_profile_schema_setup.py tests\test_disease_intelligence.py tests\test_structured_task_input.py -q
```

Full suite:

```powershell
python -m pytest -q
```

Fixture validation smokes:

```powershell
python scripts\run_hdc_workflow_configured.py --config configs\examples\covid19_new_york_2024_fixture_search_fetch_extract_task.jsonc --session-id stage10_covid19_fixture_validation_smoke
python scripts\run_hdc_workflow_configured.py --config configs\examples\dengue_florida_2025_fixture_search_fetch_extract_task.jsonc --session-id stage10_dengue_fixture_validation_smoke
```

Live validation smokes:

```powershell
python scripts\run_hdc_workflow_configured.py --config configs\examples\covid19_new_york_2024_live_search_fetch_extract_smoke.jsonc --session-id stage10_covid19_live_validation_smoke
python scripts\run_hdc_workflow_configured.py --config configs\examples\dengue_florida_2025_live_search_fetch_extract_smoke.jsonc --session-id stage10_dengue_live_validation_smoke
```

Hantavirus/New Mexico compatibility:

```powershell
python scripts\run_hdc_workflow_configured.py --config configs\hdc_workflow_run_config.jsonc --disable-all-llm --session-id stage10_hantavirus_live_fetch_compat_no_llm
```

Secret scan:

```powershell
rg -n "tvly-|sk-ant-|ANTHROPIC_API_KEY=\S+|TAVILY_API_KEY=\S+" .env.example configs docs outputs scripts src tests
```

## 15. Test results

Targeted Stage 10 tests:

```text
19 passed in 0.51s
```

Regression subset:

```text
99 passed in 1.71s
```

Full pytest:

```text
324 passed in 7.88s
```

Secret scan:

```text
17 sanitized matches; matches were limited to documented configuration or scan examples and mocked test keys. No real API key was found or printed.
```

## 16. Fixture validation smoke results

### COVID-19 fixture validation smoke

- Status: PASSED
- Command: `python scripts\run_hdc_workflow_configured.py --config configs\examples\covid19_new_york_2024_fixture_search_fetch_extract_task.jsonc --session-id stage10_covid19_fixture_validation_smoke`
- Output directory: `outputs/sessions/stage10_covid19_fixture_validation_smoke`
- Normalized record count: 2
- Event cluster count: 2
- Validation result count: 7
- Cross-source validation count: 2
- Trusted-source validation count: 3
- Scope-check count: 2
- Conflict count: 0
- Needs-review count: 2
- Example validation result: `val_result_001`, `scope_check`, `matched`, `validated`
- No live web required.
- No API key required.

### Dengue fixture validation smoke

- Status: PASSED
- Command: `python scripts\run_hdc_workflow_configured.py --config configs\examples\dengue_florida_2025_fixture_search_fetch_extract_task.jsonc --session-id stage10_dengue_fixture_validation_smoke`
- Output directory: `outputs/sessions/stage10_dengue_fixture_validation_smoke`
- Normalized record count: 2
- Event cluster count: 2
- Validation result count: 7
- Cross-source validation count: 2
- Trusted-source validation count: 3
- Scope-check count: 2
- Conflict count: 0
- Needs-review count: 2
- Example validation result: `val_result_001`, `scope_check`, `matched`, `validated`
- No live web required.
- No API key required.

## 17. Live validation smoke results

### COVID-19 live validation smoke

- Status: PASSED
- Command: `python scripts\run_hdc_workflow_configured.py --config configs\examples\covid19_new_york_2024_live_search_fetch_extract_smoke.jsonc --session-id stage10_covid19_live_validation_smoke`
- Provider: Tavily
- API key present: true, value not printed
- Output directory: `outputs/sessions/stage10_covid19_live_validation_smoke`
- Live-search-derived source count: 5
- Usable/partial document count: 1 usable, 1 partial
- Normalized record count: 3
- Event cluster count: 3
- Validation result count: 10
- Cross-source validation count: 3
- Trusted-source validation count: 4
- Scope-check count: 3
- Conflict count: 0
- Needs-review validation count: 6
- Example validation result: `val_result_001`, `scope_check`, `needs_human_review`, reason `insufficient_scope_information`
- Disease stayed non-hantavirus: yes
- No API keys printed.

### Dengue live validation smoke

- Status: PASSED
- Command: `python scripts\run_hdc_workflow_configured.py --config configs\examples\dengue_florida_2025_live_search_fetch_extract_smoke.jsonc --session-id stage10_dengue_live_validation_smoke`
- Provider: Tavily
- API key present: true, value not printed
- Output directory: `outputs/sessions/stage10_dengue_live_validation_smoke`
- Live-search-derived source count: 4
- Usable/partial document count: 1 usable, 0 partial, 1 parse deferred
- Normalized record count: 6
- Event cluster count: 5
- Validation result count: 19
- Cross-source validation count: 6
- Trusted-source validation count: 7
- Scope-check count: 6
- Conflict count: 1
- Needs-review validation count: 10
- Example validation result: `val_result_001`, `scope_check`, `matched`, `validated`
- Disease stayed non-hantavirus: yes
- No API keys printed.

## 18. Hantavirus live-fetch compatibility

- Status: PASSED
- Command: `python scripts\run_hdc_workflow_configured.py --config configs\hdc_workflow_run_config.jsonc --disable-all-llm --session-id stage10_hantavirus_live_fetch_compat_no_llm`
- Output directory: `outputs/sessions/stage10_hantavirus_live_fetch_compat_no_llm`
- `live_fetch_enabled`: true
- `live_search_enabled`: false
- All LLM stages disabled: yes
- Document count: 5
- Usable document count: 5
- Normalized record count: 5
- Event cluster count: 4
- Validation result count: 17
- Conflict count: 0
- Human review item count: 17
- Compatibility notes: validation-reserved ground truth remained held out from collection, validation outputs were produced, and existing `conflicts` output remained available.
- No API keys printed.

## 19. Live acceptance result

PASSED.

Evidence:

- `pytest` passed.
- Fixture validation smokes passed.
- Live validation smokes for COVID-19 and dengue ran and produced validation outputs.
- Hantavirus/New Mexico compatibility passed.
- Validation results explicitly record what was compared with what.
- Incompatible count semantics are emitted as not comparable rather than false matches.
- Missing validation and missing collection counterparts are explicit.
- No API keys or secrets were printed.
- Stage 11 and future-stage features were not implemented.

## 20. Output artifacts

Documentation:

- `docs/validation_refactor.md`
- `docs/stage_reports/STAGE_10_REPORT.md`

Tests:

- `tests/test_validation_refactor.py`

Session directories:

- `outputs/sessions/stage10_covid19_fixture_validation_smoke`
- `outputs/sessions/stage10_dengue_fixture_validation_smoke`
- `outputs/sessions/stage10_covid19_live_validation_smoke`
- `outputs/sessions/stage10_dengue_live_validation_smoke`
- `outputs/sessions/stage10_hantavirus_live_fetch_compat_no_llm`

Diagnostics:

- `diagnostics/validation_cases.json`
- `diagnostics/validation_comparisons.json`
- `diagnostics/validation_results.json`
- `diagnostics/validation_summary.json`
- `diagnostics/trusted_source_validation_summary.json`
- `diagnostics/cross_source_validation_summary.json`
- `diagnostics/conflicts.json`
- `diagnostics/workflow_summaries.json`

Collection exports:

- `collection/validation_cases.json`
- `collection/validation_comparisons.json`
- `collection/validation_results.json`
- `collection/validation_results.csv`

## 21. Known limitations

- Anomaly detection module not implemented yet.
- Human review decision application not implemented yet.
- Automatic correction/removal of records not implemented yet.
- Validation remains deterministic and conservative.
- Live sources may not contain comparable trusted-source counterparts.
- External dashboards may expose count semantics that remain `not_comparable`.
- CLI/notebook/UI redesign not implemented yet.
- Some generic fixture runs use the default configured held-out CSV path, which can produce explicit not-comparable/missing counterpart validation results for non-hantavirus smoke runs.

## 22. Future-stage items explicitly NOT implemented

- anomaly detection
- human review decision application
- automatic record correction
- CLI/notebook/UI
- notebook redesign
- UI redesign
- uncontrolled crawling
- recursive crawling
- browser automation
- JavaScript rendering
- OCR

## 23. Review checklist

- [x] User-facing project name remains "data collection workflow"
- [x] Internal package name hdc_workflow was not mass-renamed
- [x] Graph topology unchanged unless documented
- [x] ValidationCase / ValidationComparison / ValidationResult models or equivalents exist
- [x] Validation results explicitly state what was compared with what
- [x] Trusted-source / held-out validation exists
- [x] Cross-source validation exists
- [x] Scope validation exists
- [x] Count semantics comparability exists
- [x] Incompatible count semantics are not falsely matched
- [x] Missing validation counterpart is explicit
- [x] Missing collection counterpart is explicit
- [x] Cross-source support uses independent sources, not duplicates
- [x] Duplicate records do not inflate source support
- [x] Validation conflicts route to human review
- [x] validation_summary is exported
- [x] trusted_source_validation_summary is exported
- [x] cross_source_validation_summary is exported
- [x] validation_results are exported
- [x] Existing conflicts remain available
- [x] Existing Hantavirus/New Mexico compatibility passes
- [x] Fixture COVID-19 validation smoke completed
- [x] Fixture dengue validation smoke completed
- [x] Live COVID-19 validation smoke attempted
- [x] Live dengue validation smoke attempted
- [x] pytest was run
- [x] No API keys or secrets were printed
- [x] No anomaly detection module was implemented
- [x] No human review decision application was implemented
- [x] No future-stage features were implemented
