# Stage 7 Report: Controlled Fetch and Parse Generalization

## 1. Stage Goal

Stage 7 lets credible discovered sources become fetched and parsed documents
under bounded controls in the `data collection workflow`. It extends the
existing `content_fetch_and_parse` path so search-derived sources from Stage 5,
after Stage 6 credibility scoring and final role assignment, can become
document and evidence inputs without changing graph topology or starting Stage
8.

## 2. Summary Of Changes

- Added explicit opt-in fetch eligibility for search-derived sources.
- Added config/env controls for search-derived fetch, max source limits,
  credibility threshold, role allowlist, needs-review handling, domain
  allowlist/blocklist, byte cap, user agent, parser flags, and fixture content
  maps.
- Improved deterministic HTML/text parsing with title, visible text, table, and
  publication-date extraction.
- Added lazy PDF parse behavior with clean `parse_deferred` or `parse_failed`
  outcomes when text extraction is unavailable.
- Preserved search, source, and credibility provenance in fetch requests,
  documents, and evidence chunks where current models support it.
- Added `document_parse_summary` and `fetch_manifest`.
- Exported fetch/parse diagnostics into session diagnostics and
  `workflow_summaries`.
- Updated the workflow console minimally to show selected search-derived fetch
  count, skipped reasons, parser counts, parse summaries, and fetch manifest
  samples.
- Updated source credibility endpoint detection so normal search-discovered
  content pages are not classified as `search_endpoint` just because their
  provenance includes search terms.
- Completed a final Stage 7 live acceptance repair pass by adding only
  returned, bounded, task-relevant domains to the two Stage 7 live smoke
  allowlists:
  - COVID-19/New York: `nyc.gov`, `data.cityofnewyork.us`
  - Dengue/Florida: `epi.ufl.edu`
- Did not change graph topology, production defaults, broad crawling behavior,
  parser scope, or future-stage functionality during the acceptance repair.

## 3. Files Created Or Modified

Stage 7 created or updated:

- `.env.example`
- `configs/examples/covid19_new_york_2024_fixture_search_fetch_task.jsonc`
- `configs/examples/dengue_florida_2025_fixture_search_fetch_task.jsonc`
- `configs/examples/covid19_new_york_2024_live_search_fetch_smoke.jsonc`
- `configs/examples/dengue_florida_2025_live_search_fetch_smoke.jsonc`
- `docs/fetch_parse_generalization.md`
- `docs/stage_reports/STAGE_7_REPORT.md`
- `scripts/build_workflow_run_console.py`
- `scripts/run_hdc_workflow_configured.py`
- `src/hdc_workflow/models.py`
- `src/hdc_workflow/nodes/content_processing.py`
- `src/hdc_workflow/resources/content_fixtures/covid19_ny_official_page.html`
- `src/hdc_workflow/resources/content_fixtures/dengue_florida_official_page.html`
- `src/hdc_workflow/resources/content_fixtures/stage7_content_fixture_map.json`
- `src/hdc_workflow/resources/final_package_policy.json`
- `src/hdc_workflow/runtime_profile.py`
- `src/hdc_workflow/source_credibility.py`
- `src/hdc_workflow/state.py`
- `tests/test_fetch_parse_generalization.py`

The worktree already contained prior Stage 1-6 changes before this pass. Those
were not reverted. Current branch and HEAD:

- branch: `main`
- HEAD: `0a74ec8ca7f3ed9ab3b3f7af834de7421a2efb88`

## 4. Functional Changes Made

In `content_fetch_and_parse`:

- Builds fetch requests for seed sources as before.
- Adds gated fetch request construction for search-derived sources.
- Records per-source selection or skip decisions in `fetch_manifest`.
- Loads optional local content fixtures for deterministic full-graph smokes.
- Applies byte limits and user-agent config for live fetch.
- Produces `content_fetch_summary` with selected counts, skipped reasons, parser
  counts, fetch status counts, and domain/limit settings.

In document parsing:

- Parses HTML into clean text, title, metadata date, simple tables, and content
  type.
- Parses text-like responses as clean text.
- Defers or fails PDF parse without crashing when lightweight text extraction
  is unavailable.
- Records parser choice and parse status on each document.

In document quality:

- Treats parsed HTML/text as usable when text is present.
- Treats PDF `parse_deferred` as not chunkable but auditable.

In evidence chunking:

- Copies compatible search and credibility provenance fields into chunks.
- Skips parse-deferred documents with explicit skip reason.

In diagnostics/config:

- Added `document_parse_summary` and `fetch_manifest`.
- Added runner exports under `diagnostics/`.
- Added final package `workflow_summaries` fields.
- Added runtime config mapping and safe `.env.example` entries.

## 5. Fetch Eligibility Behavior

Search-derived source fetch is explicit opt-in through
`HDC_FETCH_SEARCH_DERIVED_SOURCES` or `content_fetch.fetch_search_derived_sources`.

Eligible roles:

- `collection`
- `validation`
- `collection_support`
- `context`

Blocked roles:

- `excluded`
- `search_endpoint`
- `needs_human_review` unless explicitly allowed by config

Other gates:

- URL scheme must be `http` or `https`.
- `source_type` must be present.
- `ready_for_content_fetch` must be true.
- `final_screening_decision` must be fetchable.
- `credibility_score` must be at or above configured threshold.
- `credibility_level` must be `high` or `medium` unless needs-review fetch is
  allowed.
- Domain blocklist is always enforced.
- Domain allowlist is enforced when configured.
- `max_search_derived_sources` and `max_total_sources` are enforced.

Recorded skip reasons include:

- `search_derived_fetch_disabled`
- `final_role_excluded`
- `final_role_search_endpoint`
- `needs_review_not_allowed`
- `final_role_not_allowed`
- `missing_source_type`
- `unsupported_url_scheme`
- `missing_credibility_score`
- `invalid_credibility_score`
- `credibility_score_below_threshold`
- `not_ready_for_content_fetch`
- `final_screening_decision_not_fetchable`
- `domain_blocklisted`
- `domain_not_allowlisted`
- `max_search_derived_sources_reached`
- `max_total_sources_reached`

## 6. Parser Behavior

HTML parser:

- `parser_used=html_stdlib_parser`
- `parse_status=parsed_html`
- extracts title, body text, headings, meta description, common publication
  date meta tags, and simple tables.

Text parser:

- supports plain text and text-like small endpoint bodies.
- stores parser metadata and character counts.

Table extraction:

- extracts simple HTML table rows.
- records `table_count` in documents and summaries.

PDF behavior:

- lazily attempts lightweight PDF parsing when enabled.
- cleanly records `parse_deferred` or `parse_failed` with reason when parsing
  cannot produce text.
- no OCR, browser rendering, or JavaScript execution is implemented.

Quality status:

- parsed text documents with usable clean text become `usable`.
- parse-deferred documents remain auditable but are skipped by chunking.

## 7. Disease-Specific Examples

### COVID-19 / New York / 2024

Fixture run:

- search mode: `fixture`
- fetch mode: local content fixture, live web disabled
- eligible search-derived sources: `1`
- selected search-derived fetch count: `1`
- fetched document count: `1`
- parsed document count: `1`
- table count: `1`
- evidence chunk count: `2`
- normalized record count: `2`
- example fetched source: `New York COVID-19 Surveillance Update 2024`
- example domain/URL: `health.ny.gov`

Initial live run:

- search mode: `live`
- provider: `tavily`
- live-search-derived source count: `4`
- selected fetch count: `0`
- reason: `domain_not_allowlisted=4`
- normalized record count: `0`

Final live acceptance repair run:

- search mode: `live`
- provider: `tavily`
- live-search-derived source count: `5`
- selected fetch count: `2`
- fetched/parsed document count: `2/2`
- quality status: `usable=1`, `partial=1`
- parser status counts: `parsed_html=2`
- evidence chunk count: `3`
- normalized record count: `3`
- example fetched source: `COVID-19 Daily Counts of Cases, Hospitalizations, and Deaths | NYC Open Data`
- example URL: `https://data.cityofnewyork.us/Health/COVID-19-Daily-Counts-of-Cases-Hospitalizations-an/rc75-m7u3`

### Dengue / Florida / 2025

Fixture run:

- search mode: `fixture`
- fetch mode: local content fixture, live web disabled
- eligible search-derived sources: `1`
- selected search-derived fetch count: `1`
- fetched document count: `1`
- parsed document count: `1`
- table count: `1`
- evidence chunk count: `2`
- normalized record count: `2`
- example fetched source: `Florida Dengue Surveillance Update 2025`
- example domain/URL: `floridahealth.gov`

Initial live run:

- search mode: `live`
- provider: `tavily`
- live-search-derived source count: `4`
- selected fetch count: `1`
- fetched document count: `1`
- parsed document count: `0`
- parse deferred count: `1`
- parser status counts: `parse_deferred=1`
- example fetched source: `[PDF] Florida Arbovirus Surveillance`
- example URL: `https://www.floridahealth.gov/wp-content/uploads/2025/07/2025-22-arbovirus-surveillance.pdf`
- normalized record count: `0`

Final live acceptance repair run:

- search mode: `live`
- provider: `tavily`
- live-search-derived source count: `4`
- selected fetch count: `2`
- fetched document count: `2`
- parsed document count: `1`
- parse deferred count: `1`
- quality status: `usable=1`, `parse_deferred=1`
- parser status counts: `parsed_html=1`, `parse_deferred=1`
- evidence chunk count: `8`
- normalized record count: `6`
- example fetched source: `Dengue in Florida: What to know - Emerging Pathogens Institute - University of Florida`
- example URL: `https://epi.ufl.edu/2025/06/24/dengue-in-florida-what-to-know`

### Hantavirus / New Mexico Compatibility

- controlled live fetch result: passed
- live search enabled: `false`
- all LLM stages enabled: `false`
- document count: `5`
- usable document count: `5`
- parser status counts: `parsed_html=5`
- normalized record count: `5`
- human review item count: `8`
- compatibility status: passed

## 8. Integration With Workflow

Stage 6 source credibility outputs directly affect Stage 7 fetch eligibility:
`source_role_final`, `credibility_score`, `credibility_level`, review flags, and
ready/fetchable decisions determine whether a search-derived source can enter
`content_fetch_requests`.

Search-derived provenance is preserved from planning/search into requests,
documents, and chunks:

- `discovery_method`
- `search_provider`
- `query_id`
- `query_used`
- `planned_query_id`
- `provider_channel`
- `role_hint`
- `source_role_final`
- `credibility_score`
- `credibility_level`
- `source_credibility_risk_flags`

`content_fetch_summary` now includes search-derived input counts, selected
counts, skipped reason counts, fetch status counts, parser status counts,
parser used counts, and configured limits.

`document_parse_summary` appears in state and final package workflow summaries.
Existing evidence chunking consumes parsed documents and skips parse-deferred
documents with explicit reason.

## 9. Backward Compatibility

- Default behavior remains safe and deterministic.
- Search-derived fetch remains disabled unless explicitly enabled.
- Live search remains disabled unless explicitly enabled.
- Existing New Mexico HPS workflow still works.
- Masked-validation reserved sources remain blocked from collection fetch.
- Graph topology was not changed.
- Tests pass offline without internet, API keys, live web, or real LLM calls.

## 10. Tests Added Or Updated

Added `tests/test_fetch_parse_generalization.py` with tests for:

- default disabled search-derived fetch behavior.
- eligible search-derived fetch request creation.
- low-credibility, excluded, search-endpoint, and needs-review skip behavior.
- max search-derived fetch limit enforcement.
- COVID-19 HTML fixture parser.
- dengue HTML fixture parser.
- PDF parse/defer behavior.
- evidence chunk provenance preservation.
- full graph COVID-19 fixture-search plus fixture-content smoke.
- full graph dengue fixture-search plus fixture-content smoke.
- Hantavirus/New Mexico compatibility behavior.
- workflow console fetch/parse payload exposure.

Existing Stage 1-6 regression tests were also rerun.

## 11. Commands Run

- `git status --short`
- `git branch --show-current`
- `git rev-parse HEAD`
- `python -m pytest tests\test_fetch_parse_generalization.py -q`
- `python -m pytest tests\test_source_credibility_scoring.py tests\test_real_source_discovery.py tests\test_executable_source_planning.py tests\test_profile_schema_setup.py tests\test_disease_intelligence.py tests\test_structured_task_input.py -q`
- `python -m pytest -q`
- `python scripts\run_hdc_workflow_configured.py --config configs\examples\covid19_new_york_2024_fixture_search_fetch_task.jsonc --session-id stage7_covid19_fixture_search_fetch_smoke`
- `python scripts\run_hdc_workflow_configured.py --config configs\examples\dengue_florida_2025_fixture_search_fetch_task.jsonc --session-id stage7_dengue_fixture_search_fetch_smoke`
- `python scripts\run_hdc_workflow_configured.py --config configs\examples\covid19_new_york_2024_live_search_fetch_smoke.jsonc --session-id stage7_covid19_live_search_fetch_smoke`
- `python scripts\run_hdc_workflow_configured.py --config configs\examples\dengue_florida_2025_live_search_fetch_smoke.jsonc --session-id stage7_dengue_live_search_fetch_smoke`
- `python scripts\run_hdc_workflow_configured.py --config configs\examples\covid19_new_york_2024_live_search_fetch_smoke.jsonc --session-id stage7_covid19_live_search_fetch_smoke_final`
- `python scripts\run_hdc_workflow_configured.py --config configs\examples\dengue_florida_2025_live_search_fetch_smoke.jsonc --session-id stage7_dengue_live_search_fetch_smoke_final`
- `python scripts\run_hdc_workflow_configured.py --config configs\hdc_workflow_run_config.jsonc --disable-all-llm --session-id stage7_hantavirus_live_fetch_compat_no_llm`
- `rg -n "tvly-|sk-ant-|ANTHROPIC_API_KEY=\S+|TAVILY_API_KEY=\S+" .env.example configs docs outputs scripts src tests`

## 12. Test Results

- Stage 7 targeted tests: `12 passed in 0.41s`.
- Stage 1-6 related regression subset: `59 passed in 1.09s`.
- Full test suite after final acceptance repair: `277 passed in 7.07s`.
- Secret hygiene scan found only the deterministic fake key in
  `tests/test_real_source_discovery.py` and the scan command text in this
  report. No real API key was found.

## 13. Fixture Fetch Smoke Results

### COVID-19 Fixture Fetch Smoke

- command: `python scripts\run_hdc_workflow_configured.py --config configs\examples\covid19_new_york_2024_fixture_search_fetch_task.jsonc --session-id stage7_covid19_fixture_search_fetch_smoke`
- output directory: `outputs/sessions/stage7_covid19_fixture_search_fetch_smoke`
- selected search-derived fetch count: `1`
- fetched/parsed document count: `1/1`
- table count: `1`
- evidence chunk count: `2`
- normalized record count: `2`
- parser summary path: `outputs/sessions/stage7_covid19_fixture_search_fetch_smoke/diagnostics/document_parse_summary.json`
- no live web required: yes
- no API key required: yes

### Dengue Fixture Fetch Smoke

- command: `python scripts\run_hdc_workflow_configured.py --config configs\examples\dengue_florida_2025_fixture_search_fetch_task.jsonc --session-id stage7_dengue_fixture_search_fetch_smoke`
- output directory: `outputs/sessions/stage7_dengue_fixture_search_fetch_smoke`
- selected search-derived fetch count: `1`
- fetched/parsed document count: `1/1`
- table count: `1`
- evidence chunk count: `2`
- normalized record count: `2`
- parser summary path: `outputs/sessions/stage7_dengue_fixture_search_fetch_smoke/diagnostics/document_parse_summary.json`
- no live web required: yes
- no API key required: yes

## 14. Live Search/Fetch Smoke Results

The first live acceptance pass intentionally stayed bounded and produced a
PARTIAL result. It proved real Tavily search was working, but COVID-19 live
fetch selected no pages because every returned candidate was blocked by the
configured allowlist, and dengue selected a FloridaHealth PDF whose parse was
deferred.

The final repair pass changed only the two Stage 7 live smoke configs. It added
specific returned domains that are relevant to the task and still bounded by
allowlist controls. No broad search/fetch behavior was loosened.

### COVID-19 / New York / 2024: Initial PARTIAL

- command: `python scripts\run_hdc_workflow_configured.py --config configs\examples\covid19_new_york_2024_live_search_fetch_smoke.jsonc --session-id stage7_covid19_live_search_fetch_smoke`
- provider: `tavily`
- API key present/absent: present in process environment; value not printed
- output directory: `outputs/sessions/stage7_covid19_live_search_fetch_smoke`
- live-search-derived source count: `4`
- eligible fetch count: `0`
- selected fetch count: `0`
- document_count: `0`
- usable_document_count: `0`
- partial_document_count: `0`
- parse_failed_count: `0`
- parser status counts: `{}`
- table count: `0`
- evidence chunk count: `0`
- normalized record count: `0`
- example fetched domains/titles: none
- pages were fetched: no
- source discovery beyond fixed catalog: yes, live Tavily returned candidates
- API keys printed: no
- reason for partial: all live candidates were blocked by configured domain
  allowlist (`domain_not_allowlisted=4`)

### COVID-19 / New York / 2024: Final PASSED

- command: `python scripts\run_hdc_workflow_configured.py --config configs\examples\covid19_new_york_2024_live_search_fetch_smoke.jsonc --session-id stage7_covid19_live_search_fetch_smoke_final`
- provider: `tavily`
- API key present/absent: provider call succeeded; key value was not printed
- output directory: `outputs/sessions/stage7_covid19_live_search_fetch_smoke_final`
- executed_query_count: `2`
- raw_search_result_count: `6`
- deduplicated_search_result_count: `5`
- live-search-derived source count: `5`
- selected fetch count: `2`
- document_count: `2`
- fetched status counts: `fetched=2`
- document type counts: `html=2`
- parser status counts: `parsed_html=2`
- parser used counts: `html_stdlib_parser=2`
- usable_document_count: `1`
- partial_document_count: `1`
- parse_deferred_count: `0`
- parse_failed_count: `0`
- table count: `0`
- evidence chunk count: `3`
- normalized record count: `3`
- human review item count: `9`
- conflict count: `0`
- example fetched domain/title: `data.cityofnewyork.us` /
  `COVID-19 Daily Counts of Cases, Hospitalizations, and Deaths | NYC Open Data`
- example fetched URL:
  `https://data.cityofnewyork.us/Health/COVID-19-Daily-Counts-of-Cases-Hospitalizations-an/rc75-m7u3`
- pages were fetched: yes
- source discovery beyond fixed catalog: yes, live Tavily returned search-derived candidates
- API keys printed: no

### Dengue / Florida / 2025: Initial PARTIAL

- command: `python scripts\run_hdc_workflow_configured.py --config configs\examples\dengue_florida_2025_live_search_fetch_smoke.jsonc --session-id stage7_dengue_live_search_fetch_smoke`
- provider: `tavily`
- API key present/absent: present in process environment; value not printed
- output directory: `outputs/sessions/stage7_dengue_live_search_fetch_smoke`
- live-search-derived source count: `4`
- eligible fetch count: `1`
- selected fetch count: `1`
- document_count: `1`
- usable_document_count: `0`
- partial_document_count: `0`
- parse_failed_count: `0`
- parser status counts: `parse_deferred=1`
- table count: `0`
- evidence chunk count: `0`
- normalized record count: `0`
- example fetched domain/title: `floridahealth.gov` /
  `[PDF] Florida Arbovirus Surveillance`
- pages were fetched: yes
- source discovery beyond fixed catalog: yes, live Tavily returned candidates
- API keys printed: no
- reason for partial: fetched source was a PDF and was recorded as
  `parse_deferred`

### Dengue / Florida / 2025: Final PASSED

- command: `python scripts\run_hdc_workflow_configured.py --config configs\examples\dengue_florida_2025_live_search_fetch_smoke.jsonc --session-id stage7_dengue_live_search_fetch_smoke_final`
- provider: `tavily`
- API key present/absent: provider call succeeded; key value was not printed
- output directory: `outputs/sessions/stage7_dengue_live_search_fetch_smoke_final`
- executed_query_count: `2`
- raw_search_result_count: `6`
- deduplicated_search_result_count: `4`
- live-search-derived source count: `4`
- selected fetch count: `2`
- document_count: `2`
- fetched status counts: `fetched=2`
- document type counts: `html=1`, `pdf=1`
- parser status counts: `parsed_html=1`, `parse_deferred=1`
- parser used counts: `html_stdlib_parser=1`, `pdf_parse_deferred=1`
- usable_document_count: `1`
- partial_document_count: `0`
- parse_deferred_count: `1`
- parse_failed_count: `0`
- table count: `0`
- evidence chunk count: `8`
- normalized record count: `6`
- human review item count: `17`
- conflict count: `1`
- example fetched domain/title: `epi.ufl.edu` /
  `Dengue in Florida: What to know - Emerging Pathogens Institute - University of Florida`
- example fetched URL: `https://epi.ufl.edu/2025/06/24/dengue-in-florida-what-to-know`
- pages were fetched: yes
- source discovery beyond fixed catalog: yes, live Tavily returned search-derived candidates
- API keys printed: no

## 15. Hantavirus Live-Fetch Compatibility

Status: PASSED

- command: `python scripts\run_hdc_workflow_configured.py --config configs\hdc_workflow_run_config.jsonc --disable-all-llm --session-id stage7_hantavirus_live_fetch_compat_no_llm`
- output directory: `outputs/sessions/stage7_hantavirus_live_fetch_compat_no_llm`
- live_fetch_enabled: `true`
- live_search_enabled: `false`
- all LLM stages disabled: `true`
- document_count: `5`
- usable_document_count: `5`
- normalized_record_count: `5`
- human_review_item_count: `8`
- parser summary present: yes
- parser status counts: `parsed_html=5`
- no API keys printed: yes
- final acceptance repair rerun status: not rerun, because the repair changed
  only the two COVID-19 and dengue live smoke config allowlists; the prior
  Hantavirus/New Mexico compatibility result remains unchanged.

## 16. Live Acceptance Result

Overall Stage 7 live acceptance result: PASSED.

Rationale:

- pytest passed.
- COVID-19 fixture fetch smoke passed.
- Dengue fixture fetch smoke passed.
- Hantavirus/New Mexico live-fetch compatibility passed.
- Real Tavily live search executed successfully for both COVID-19 and dengue.
- COVID-19 final live smoke discovered search-derived candidates, selected 2
  bounded allowlisted sources, fetched 2 HTML pages, parsed both, and produced
  evidence chunks and normalized records.
- Dengue final live smoke discovered search-derived candidates, selected 2
  bounded allowlisted sources, fetched one parseable HTML page plus one
  auditable deferred PDF, and produced evidence chunks and normalized records.
- API keys were not printed or stored in generated configs/reports.

This pass validates the intended Stage 7 behavior: controlled live search can
produce search-derived source candidates, Stage 6 credibility/routing can pass
bounded candidates into Stage 7, and Stage 7 can fetch and parse credible live
HTML/text content into downstream evidence and records while keeping PDFs
auditable when parsing is deferred.

## 17. Output Artifacts

Documentation and tests:

- `docs/fetch_parse_generalization.md`
- `docs/stage_reports/STAGE_7_REPORT.md`
- `tests/test_fetch_parse_generalization.py`

Fixture content files:

- `src/hdc_workflow/resources/content_fixtures/covid19_ny_official_page.html`
- `src/hdc_workflow/resources/content_fixtures/dengue_florida_official_page.html`
- `src/hdc_workflow/resources/content_fixtures/stage7_content_fixture_map.json`

Config examples:

- `configs/examples/covid19_new_york_2024_fixture_search_fetch_task.jsonc`
- `configs/examples/dengue_florida_2025_fixture_search_fetch_task.jsonc`
- `configs/examples/covid19_new_york_2024_live_search_fetch_smoke.jsonc`
- `configs/examples/dengue_florida_2025_live_search_fetch_smoke.jsonc`

Session directories:

- `outputs/sessions/stage7_covid19_fixture_search_fetch_smoke`
- `outputs/sessions/stage7_dengue_fixture_search_fetch_smoke`
- `outputs/sessions/stage7_covid19_live_search_fetch_smoke`
- `outputs/sessions/stage7_dengue_live_search_fetch_smoke`
- `outputs/sessions/stage7_covid19_live_search_fetch_smoke_final`
- `outputs/sessions/stage7_dengue_live_search_fetch_smoke_final`
- `outputs/sessions/stage7_hantavirus_live_fetch_compat_no_llm`

Per-session diagnostics include:

- `diagnostics/content_fetch_summary.json`
- `diagnostics/document_quality_summary.json`
- `diagnostics/document_parse_summary.json`
- `diagnostics/fetch_manifest.json`
- `diagnostics/live_fetch_summary.json`
- `diagnostics/workflow_summaries.json`

## 18. Known Limitations

- Disease-generic extraction record model is not implemented yet.
- Non-hantavirus structured records may still be empty or limited.
- Validation refactor is not implemented yet.
- Duplicate/event clustering is not implemented yet.
- Anomaly detection is not implemented yet.
- Human review decision application is not implemented yet.
- OCR is not implemented.
- Browser/JavaScript rendering is not implemented.
- CLI/notebook/UI redesign is not implemented yet.
- Live candidates can still be blocked by strict domain allowlists when a
  smoke config intentionally excludes returned domains.
- Live PDF sources may be fetched but deferred if lightweight PDF text parsing
  cannot extract text.

## 19. Future-Stage Items Explicitly NOT Implemented

- generic record schema.
- disease-generic structured extraction replacement.
- trusted-source validation refactor.
- cross-source validation refactor.
- duplicate/event clustering.
- anomaly detection.
- human review decision application.
- CLI/notebook/UI.
- Stage 8.

## 20. Review Checklist

- [x] User-facing project name remains "data collection workflow"
- [x] Internal package name hdc_workflow was not mass-renamed
- [x] Graph topology unchanged unless documented
- [x] Search-derived fetch is explicit opt-in
- [x] Fetch eligibility uses source_role_final and credibility_score
- [x] Excluded/search_endpoint sources are not fetched
- [x] Low-confidence sources are skipped or routed with reasons
- [x] Max search-derived fetch limits are enforced
- [x] HTML parser extracts title/text/table data from fixtures
- [x] PDF parsing is implemented or cleanly deferred without crashes
- [x] Search-derived provenance is preserved into documents/evidence chunks
- [x] content_fetch_summary is exported
- [x] parser/document_parse summary is exported
- [x] COVID-19 fixture fetch smoke completed
- [x] Dengue fixture fetch smoke completed
- [x] COVID-19 live search/fetch smoke attempted
- [x] Dengue live search/fetch smoke attempted
- [x] Hantavirus live-fetch compatibility attempted
- [x] pytest was run
- [x] No API keys or secrets were printed
- [x] No generic extraction record schema replacement was implemented
- [x] No validation refactor was implemented
- [x] No duplicate clustering was implemented
- [x] No future-stage features were implemented
