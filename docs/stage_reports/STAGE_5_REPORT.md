# Stage 5 Report: Real Source Discovery / Search Provider Execution

## 1. Stage goal

Stage 5 executes planned queries from `agentic_source_plan` through controlled fixture/live search providers to create source candidates beyond the fixed catalog. The **data collection workflow** keeps fixed catalogs as seeds, fallbacks, fixtures, and guardrails, but they are no longer the only source discovery mechanism when source search is explicitly enabled.

## 2. Summary of changes

- Added a search provider abstraction with normalized search result/response models.
- Added deterministic `FixtureSearchProvider`.
- Added a bounded Tavily live search adapter.
- Updated Tavily live authentication to use `Authorization: Bearer ...`.
- Added `source_search` config/env flags.
- Integrated planned-query execution into `source_discovery` without changing graph topology.
- Added search-derived source candidates with stable `src_search_...` IDs and provenance.
- Added URL validation, canonicalization, deduplication, rejection reasons, and query/result limits.
- Added search diagnostics export, final-package summary exposure, and minimal report/HTML console visibility.

## 3. Files created or modified

Stage 5 files created:

- `src/hdc_workflow/search_providers.py`
- `src/hdc_workflow/resources/search_fixtures/example_search_results.json`
- `src/hdc_workflow/resources/search_fixtures/covid19_new_york_search_results.json`
- `src/hdc_workflow/resources/search_fixtures/dengue_florida_search_results.json`
- `configs/examples/covid19_new_york_2024_fixture_search_task.jsonc`
- `configs/examples/dengue_florida_2025_fixture_search_task.jsonc`
- `configs/examples/covid19_new_york_2024_live_search_smoke.jsonc`
- `configs/examples/dengue_florida_2025_live_search_smoke.jsonc`
- `tests/test_real_source_discovery.py`
- `docs/real_source_discovery.md`
- `docs/stage_reports/STAGE_5_REPORT.md`

Stage 5 files modified:

- `.env.example`
- `README.md`
- `configs/hdc_workflow_run_config.jsonc`
- `scripts/build_workflow_run_console.py`
- `scripts/run_hdc_workflow_configured.py`
- `src/hdc_workflow/models.py`
- `src/hdc_workflow/nodes/finalization.py`
- `src/hdc_workflow/nodes/source_discovery.py`
- `src/hdc_workflow/resources/final_package_policy.json`
- `src/hdc_workflow/runtime_profile.py`
- `src/hdc_workflow/state.py`

The worktree also contains earlier Stage 0-4 dirty files. Those were not reverted.

## 4. Functional changes made

`source_discovery` now supports three modes:

- `disabled`: no provider call, offline seed catalog only.
- `fixture`: execute planned queries against local JSON fixture results.
- `live`: execute planned queries against a live provider only when live search is explicitly enabled.

Search execution returns metadata only. It does not fetch discovered page bodies and does not crawl recursively.

## 5. Search provider behavior

- Interface: `SearchProvider.search(planned_query, max_results, timeout_seconds)`.
- Models: `SearchResult` and `SearchProviderResponse`.
- Fixture provider: reads local JSON fixtures; deterministic; no internet/API key.
- Live provider: `TavilySearchProvider`, using `TAVILY_API_KEY` from the environment and Tavily's `Authorization: Bearer ...` request header.
- Provider selection: `fixture` mode uses `FixtureSearchProvider`; `live` mode uses configured provider, currently Tavily.
- Modes: `disabled`, `fixture`, `live`.
- Limits: `max_queries`, `max_results_per_query`, `max_total_results`, `timeout_seconds`.
- Channel allowlist: default allows `web_search`, `official_site_search`, `news_search`, `literature_api`, and `database_search`.
- Provider errors: recorded in `query_execution_records` and `provider_error_count`; the graph can continue with seed catalog candidates when combined mode is enabled.
- Fallback: fixed seed catalog remains available whenever `combine_with_seed_catalog=true` or search is disabled.

## 6. Source discovery behavior

- Reads `agentic_source_plan.planned_queries`.
- Executes planned queries only when mode is `fixture`, or mode is `live` with `HDC_ENABLE_LIVE_SEARCH=true`.
- Skips unsupported channels, invalid/empty/raw URL-only queries, query-limit overflow, and total-result-limit overflow.
- Converts accepted results into `SourceCandidate` dictionaries with search provenance.
- Combines seed candidates and search candidates when configured.
- Deduplicates search results by canonical URL before creating candidates.
- Rejects missing URLs, invalid URLs, unsupported schemes, duplicates, empty title/snippet results, and results beyond total limit.
- `source_dedup_and_registry` preserves search provenance into registry entries.

## 7. Disease-specific examples

### COVID-19 / New York / 2024

- Search mode: `fixture`
- Provider: `fixture`
- Executed query count: `3`
- Raw search result count: `15`
- Search-derived candidate count: `1`
- Source registry search-derived entry count: `1`
- Example discovered title/domain: `New York COVID-19 surveillance update 2024` / `health.ny.gov`
- Fixed catalog also used: `true`

### Dengue / Florida / 2025

- Search mode: `fixture`
- Provider: `fixture`
- Executed query count: `3`
- Raw search result count: `15`
- Search-derived candidate count: `1`
- Source registry search-derived entry count: `1`
- Example discovered title/domain: `Florida dengue surveillance update 2025` / `floridahealth.gov`
- Fixed catalog also used: `true`

### Hantavirus / New Mexico compatibility

- Live fetch compatibility: ran successfully.
- Search mode: `disabled`.
- Controlled New Mexico HPS source set still works.
- Documents fetched: `5`
- Normalized records: `5`

## 8. Integration with workflow

- Source search happens inside the existing `source_discovery` node.
- Graph topology was not changed.
- `source_discovery_summary` now includes search mode/provider and search/seed candidate counts.
- `source_search_execution_summary` appears in state and final package `workflow_summaries`.
- Configured runs export:
  - `diagnostics/source_search_execution_summary.json`
  - `diagnostics/search_results_manifest.json`
  - `diagnostics/source_discovery_summary.json`
  - `diagnostics/workflow_summaries.json` with `source_search_execution_summary`
- `source_dedup_and_registry` consumes search-derived candidates like any other source candidate.
- Existing source screening consumes search-derived registry entries through the same screening/routing path.

## 9. Backward compatibility

- Default source search remains disabled.
- Default offline seed catalog behavior remains available.
- Existing tests pass.
- Hantavirus/New Mexico live-fetch compatibility remains available.
- Live search is disabled by default and requires explicit config plus provider credentials.

## 10. Tests added or updated

Added `tests/test_real_source_discovery.py` with coverage for:

- provider abstraction existence
- disabled/offline seed catalog behavior
- fixture planned-query execution
- COVID-19 disease-specific fixture candidates
- dengue disease-specific fixture candidates
- URL validation and deduplication
- query/result limits
- source candidate and registry provenance
- full graph COVID-19 fixture-search smoke
- full graph dengue fixture-search smoke
- live provider not called in disabled/fixture modes
- mocked live provider execution
- Tavily live adapter uses Bearer authorization and does not put the API key in the JSON payload

## 11. Commands run

```powershell
git status --short
git branch --show-current
git rev-parse HEAD

python -m pytest tests\test_real_source_discovery.py -q
python -m pytest tests\test_executable_source_planning.py tests\test_profile_schema_setup.py tests\test_disease_intelligence.py tests\test_structured_task_input.py -q
python -m pytest -q

python scripts\run_hdc_workflow_configured.py --config configs\examples\covid19_new_york_2024_fixture_search_task.jsonc --session-id stage5_covid19_fixture_search_smoke
python scripts\run_hdc_workflow_configured.py --config configs\examples\dengue_florida_2025_fixture_search_task.jsonc --session-id stage5_dengue_fixture_search_smoke
python scripts\run_hdc_workflow_configured.py --config configs\examples\covid19_new_york_2024_live_search_smoke.jsonc --session-id stage5_covid19_live_search_smoke
python scripts\run_hdc_workflow_configured.py --config configs\examples\dengue_florida_2025_live_search_smoke.jsonc --session-id stage5_dengue_live_search_smoke
python scripts\run_hdc_workflow_configured.py --config configs\hdc_workflow_run_config.jsonc --disable-all-llm --session-id stage5_hantavirus_live_fetch_compat_no_llm

python -m pytest tests\test_real_source_discovery.py::test_tavily_provider_uses_bearer_authorization_header -q
python -m pytest tests\test_real_source_discovery.py -q

$env:TAVILY_API_KEY = [Environment]::GetEnvironmentVariable('TAVILY_API_KEY','User'); python scripts\run_hdc_workflow_configured.py --config configs\examples\covid19_new_york_2024_live_search_smoke.jsonc --session-id stage5_covid19_live_search_smoke_rerun
$env:TAVILY_API_KEY = [Environment]::GetEnvironmentVariable('TAVILY_API_KEY','User'); python scripts\run_hdc_workflow_configured.py --config configs\examples\dengue_florida_2025_live_search_smoke.jsonc --session-id stage5_dengue_live_search_smoke_rerun
```

Git:

- Branch: `main`
- HEAD: `0a74ec8ca7f3ed9ab3b3f7af834de7421a2efb88`
- `git status --short`: dirty worktree with current Stage 5 changes and prior Stage 0-4 uncommitted files.

## 12. Test results

- `python -m pytest tests\test_real_source_discovery.py::test_tavily_provider_uses_bearer_authorization_header -q`: `1 passed in 0.07s`
- `python -m pytest tests\test_real_source_discovery.py -q`: `13 passed in 0.36s`
- Stage 1-4 targeted set: `31 passed in 0.72s`
- `python -m pytest -q`: `250 passed in 5.98s`

## 13. Fixture-search smoke results

### COVID-19 fixture-search smoke

- Command: `python scripts\run_hdc_workflow_configured.py --config configs\examples\covid19_new_york_2024_fixture_search_task.jsonc --session-id stage5_covid19_fixture_search_smoke`
- Output directory: `outputs/sessions/stage5_covid19_fixture_search_smoke/`
- Search mode: `fixture`
- Provider: `fixture`
- Executed query count: `3`
- Raw result count: `15`
- `candidate_from_search_count`: `1`
- `candidate_from_seed_count`: `21`
- Source registry search-derived count: `1`
- Discovery method: `fixture_search_plus_seed_catalog`
- Search result manifest path: `outputs/sessions/stage5_covid19_fixture_search_smoke/diagnostics/search_results_manifest.json`
- No live web required: `true`
- No API key required: `true`

### Dengue fixture-search smoke

- Command: `python scripts\run_hdc_workflow_configured.py --config configs\examples\dengue_florida_2025_fixture_search_task.jsonc --session-id stage5_dengue_fixture_search_smoke`
- Output directory: `outputs/sessions/stage5_dengue_fixture_search_smoke/`
- Search mode: `fixture`
- Provider: `fixture`
- Executed query count: `3`
- Raw result count: `15`
- `candidate_from_search_count`: `1`
- `candidate_from_seed_count`: `21`
- Source registry search-derived count: `1`
- Discovery method: `fixture_search_plus_seed_catalog`
- Search result manifest path: `outputs/sessions/stage5_dengue_fixture_search_smoke/diagnostics/search_results_manifest.json`
- No live web required: `true`
- No API key required: `true`

## 14. Live-search smoke results

PASSED.

Live search was rerun with a User-scope `TAVILY_API_KEY` available to the external runner. The key value was never printed. Before rerunning, the Tavily adapter was corrected to send credentials with the `Authorization: Bearer ...` header and a regression test was added.

### COVID-19 live search

- Command: `$env:TAVILY_API_KEY = [Environment]::GetEnvironmentVariable('TAVILY_API_KEY','User'); python scripts\run_hdc_workflow_configured.py --config configs\examples\covid19_new_york_2024_live_search_smoke.jsonc --session-id stage5_covid19_live_search_smoke_rerun`
- Provider: `tavily`
- API key present: `true` in the external runner; value not printed
- Output directory: `outputs/sessions/stage5_covid19_live_search_smoke_rerun/`
- Search mode: `live`
- Planned query count: `10`
- Selected query count: `2`
- Executed query count: `2`
- Raw result count: `6`
- Deduplicated result count: `6`
- Rejected result count: `0`
- `candidate_from_search_count`: `6`
- `candidate_from_seed_count`: `21`
- Total candidate count: `27`
- Provider error count: `0`
- Source registry search-derived count: `6`
- Example accepted domains/titles:
  - `nyc.gov` / `COVID-19: Data Trends and Totals - NYC Health`
  - `data.cityofnewyork.us` / `COVID | NYC Open Data`
  - `coronavirus.health.ny.gov` / `COVID-19 Data in New York | Department of Health - NY.Gov`
- Search result manifest path: `outputs/sessions/stage5_covid19_live_search_smoke_rerun/diagnostics/search_results_manifest.json`
- Pages fetched by search provider: `false`; search provider returned metadata only
- Source discovery beyond fixed catalog: achieved

### Dengue live search

- Command: `$env:TAVILY_API_KEY = [Environment]::GetEnvironmentVariable('TAVILY_API_KEY','User'); python scripts\run_hdc_workflow_configured.py --config configs\examples\dengue_florida_2025_live_search_smoke.jsonc --session-id stage5_dengue_live_search_smoke_rerun`
- Provider: `tavily`
- API key present: `true` in the external runner; value not printed
- Output directory: `outputs/sessions/stage5_dengue_live_search_smoke_rerun/`
- Search mode: `live`
- Planned query count: `10`
- Selected query count: `2`
- Executed query count: `2`
- Raw result count: `6`
- Deduplicated result count: `3`
- Rejected result count: `3`
- Rejection reasons: `{"duplicate_url": 3}`
- `candidate_from_search_count`: `3`
- `candidate_from_seed_count`: `21`
- Total candidate count: `24`
- Provider error count: `0`
- Source registry search-derived count: `3`
- Example accepted domains/titles:
  - `floridahealth.gov` / `[PDF] Florida Arbovirus Surveillance`
  - `outbreaknewstoday.substack.com` / `Florida reports 1st dengue local transmission case of 2025`
  - `epi.ufl.edu` / `Dengue in Florida: What to know - Emerging Pathogens Institute`
- Search result manifest path: `outputs/sessions/stage5_dengue_live_search_smoke_rerun/diagnostics/search_results_manifest.json`
- Pages fetched by search provider: `false`; search provider returned metadata only
- Source discovery beyond fixed catalog: achieved

## 15. Hantavirus live-fetch compatibility

PASSED.

- Command: `python scripts\run_hdc_workflow_configured.py --config configs\hdc_workflow_run_config.jsonc --disable-all-llm --session-id stage5_hantavirus_live_fetch_compat_no_llm`
- Output directory: `outputs/sessions/stage5_hantavirus_live_fetch_compat_no_llm/`
- `live_fetch_enabled`: `true`
- `live_search_enabled`: `false`
- All LLM stages disabled: `true`
- Document count: `5`
- Usable document count: `5`
- Fetch status counts: `{"fetched": 5}`
- Quality status counts: `{"usable": 5}`
- Normalized record count: `5`
- Human review item count: `8`
- Source discovery mode: `offline_seed_catalog`
- No API keys printed: `true`

## 16. Live acceptance result

PASSED.

- Pytest passed.
- COVID-19 fixture-search smoke passed.
- Dengue fixture-search smoke passed.
- Hantavirus live-fetch compatibility passed.
- Tavily authentication regression test passed.
- COVID-19 real Tavily live-search smoke returned `6` search-derived candidates.
- Dengue real Tavily live-search smoke returned `3` accepted search-derived candidates and recorded `3` duplicate-URL rejections.
- No API key values were printed.

## 17. Output artifacts

- `docs/real_source_discovery.md`
- `docs/stage_reports/STAGE_5_REPORT.md`
- `src/hdc_workflow/search_providers.py`
- `src/hdc_workflow/resources/search_fixtures/example_search_results.json`
- `src/hdc_workflow/resources/search_fixtures/covid19_new_york_search_results.json`
- `src/hdc_workflow/resources/search_fixtures/dengue_florida_search_results.json`
- `configs/examples/covid19_new_york_2024_fixture_search_task.jsonc`
- `configs/examples/dengue_florida_2025_fixture_search_task.jsonc`
- `configs/examples/covid19_new_york_2024_live_search_smoke.jsonc`
- `configs/examples/dengue_florida_2025_live_search_smoke.jsonc`
- `tests/test_real_source_discovery.py`
- `outputs/sessions/stage5_covid19_fixture_search_smoke/`
- `outputs/sessions/stage5_dengue_fixture_search_smoke/`
- `outputs/sessions/stage5_covid19_live_search_smoke/`
- `outputs/sessions/stage5_dengue_live_search_smoke/`
- `outputs/sessions/stage5_covid19_live_search_smoke_rerun/`
- `outputs/sessions/stage5_dengue_live_search_smoke_rerun/`
- `outputs/sessions/stage5_hantavirus_live_fetch_compat_no_llm/`
- `outputs/sessions/stage5_covid19_fixture_search_smoke/diagnostics/search_results_manifest.json`
- `outputs/sessions/stage5_dengue_fixture_search_smoke/diagnostics/search_results_manifest.json`
- `outputs/sessions/stage5_covid19_live_search_smoke/diagnostics/search_results_manifest.json`
- `outputs/sessions/stage5_dengue_live_search_smoke/diagnostics/search_results_manifest.json`
- `outputs/sessions/stage5_covid19_live_search_smoke_rerun/diagnostics/search_results_manifest.json`
- `outputs/sessions/stage5_dengue_live_search_smoke_rerun/diagnostics/search_results_manifest.json`

## 18. Known limitations

- Source credibility scoring overhaul not implemented yet.
- LLM source credibility overhaul not implemented yet.
- Fetch/parse generalization not implemented yet.
- Discovered pages are not deeply parsed in Stage 5 unless existing downstream live fetch is separately enabled.
- PDF parsing/OCR not implemented yet.
- Disease-generic extraction record model not implemented yet.
- Validation refactor not implemented yet.
- Duplicate clustering not implemented yet.
- Anomaly detection not implemented yet.
- Human review decision application not implemented yet.
- CLI/notebook/UI redesign not implemented yet.
- Live search now requires an external search provider key and network access when running live acceptance; offline tests remain deterministic and key-free.

## 19. Future-stage items explicitly NOT implemented

- Source credibility scoring overhaul
- LLM source credibility overhaul
- Fetch/parse/extraction generalization
- Generic record schema
- Trusted-source validation refactor
- Cross-source validation refactor
- Duplicate/event clustering
- Anomaly detection
- Human review decision application
- CLI/notebook/UI

## 20. Review checklist

- [x] User-facing project name remains "data collection workflow"
- [x] Internal package name `hdc_workflow` was not mass-renamed
- [x] Search provider interface exists
- [x] Fixture search provider exists
- [x] At least one real live search provider adapter exists
- [x] Live search is disabled by default
- [x] Tests do not require internet or API keys
- [x] Planned queries from `agentic_source_plan` are used for search execution when enabled
- [x] Search results become source candidates with provenance
- [x] Search-derived candidates have `discovery_method` distinct from `offline_seed_catalog`
- [x] Source registry preserves search provenance
- [x] URL validation and deduplication are implemented
- [x] Query/result limits are enforced
- [x] COVID-19 fixture-search smoke run completed
- [x] Dengue fixture-search smoke run completed
- [x] COVID-19 live-search smoke was attempted
- [x] Dengue live-search smoke was attempted
- [x] COVID-19 real Tavily live-search smoke returned search-derived candidates
- [x] Dengue real Tavily live-search smoke returned search-derived candidates
- [x] Tavily adapter uses Bearer authorization and does not put the API key in the JSON payload
- [x] Hantavirus live-fetch compatibility was attempted
- [x] Fixed catalogs remain available as seed/fallback/guardrail
- [x] Fixed catalogs are no longer the only source mechanism when search is enabled
- [x] No API keys or secrets were printed
- [x] No source credibility overhaul was implemented
- [x] No fetch/parse generalization was implemented
- [x] No validation refactor was implemented
- [x] No future-stage features were implemented
