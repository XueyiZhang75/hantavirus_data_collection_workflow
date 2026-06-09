# Stage 8 Report: Generic Record Schema + Disease-Generic Structured Extraction

## 1. Stage goal

Stage 8 adds generic public-health record extraction so the data collection workflow can represent COVID-19, dengue, hantavirus, and future diseases without forcing all extracted data through `HantavirusRecord` semantics.

The user-facing project name remains `data collection workflow`. The internal Python package name remains `hdc_workflow`.

## 2. Summary of changes

- Added `PublicHealthRecord`, a disease-generic public-health record model that extends the legacy `HantavirusRecord` field set.
- Updated deterministic extraction to use task disease, disease intelligence, evidence text, source metadata, and target fields.
- Updated optional LLM structured extraction policy to target generic records while remaining disabled by default and mocked in tests.
- Updated schema validation/repair to validate generic records, reject invalid provenance/negative counts, and route uncertain records to review.
- Updated normalization to preserve COVID-19, Dengue, and Hantavirus disease names instead of normalizing all diseases to Hantavirus.
- Updated final package exports, field order, summaries, provenance manifests, and diagnostics for generic record counts and disease counts.
- Preserved Hantavirus/New Mexico backward compatibility.

## 3. Files created or modified

Created:

- `docs/generic_structured_extraction.md`
- `docs/stage_reports/STAGE_8_REPORT.md`
- `tests/test_generic_structured_extraction.py`
- `configs/examples/covid19_new_york_2024_fixture_search_fetch_extract_task.jsonc`
- `configs/examples/dengue_florida_2025_fixture_search_fetch_extract_task.jsonc`
- `configs/examples/covid19_new_york_2024_live_search_fetch_extract_smoke.jsonc`
- `configs/examples/dengue_florida_2025_live_search_fetch_extract_smoke.jsonc`

Modified for Stage 8:

- `src/hdc_workflow/models.py`
- `src/hdc_workflow/nodes/extraction.py`
- `src/hdc_workflow/nodes/normalization.py`
- `src/hdc_workflow/nodes/finalization.py`
- `src/hdc_workflow/resources/structured_extraction_policy.json`
- `src/hdc_workflow/resources/llm_structured_extraction_policy.json`
- `src/hdc_workflow/resources/record_normalization_policy.json`
- `src/hdc_workflow/resources/final_package_policy.json`
- `scripts/run_hdc_workflow_configured.py`
- `tests/test_models.py`

The working tree also contains earlier Stage 1-7 changes and generated session outputs. They were not reverted.

## 4. Functional changes made

Extraction:

- Builds disease-aware extraction context from `structured_task`, `collection_spec`, and `disease_intelligence`.
- Supports COVID-19, SARS-CoV-2, dengue, DENV, dengue virus, hantavirus, HPS, and Sin Nombre matching.
- Extracts table and narrative records into `PublicHealthRecord`.
- Adds hospitalization parsing for table and narrative evidence.
- Preserves source, search, document, chunk, source role, and credibility provenance.

Schema validation/repair:

- Validates generic records through `PublicHealthRecord`.
- Rejects negative count values.
- Rejects records missing core source provenance.
- Flags count-bearing records with missing location/date for review.
- Exports `schema_validation_summary` and `rejected_records` diagnostics.

Normalization:

- Normalizes disease names to COVID-19, Dengue, or Hantavirus disease according to active evidence and aliases.
- Normalizes country aliases and selected subnational aliases including New York, New York City, NYC, and Florida.
- Normalizes numeric strings for old and new count fields.
- Preserves raw disease, location, date, and source fields.

Finalization:

- `final_dataset` now accepts `PublicHealthRecord`.
- The final package metadata name is `data_collection_workflow_final_package`.
- Final summaries include generic record counts, legacy hantavirus counts, disease counts, source type counts, and extraction method counts.
- Final field order keeps legacy fields and adds generic disease/location/date/count/provenance/review fields.

Diagnostics:

- `scripts/run_hdc_workflow_configured.py` now exports raw, validated, rejected, and normalized record diagnostics plus extraction, schema validation, and normalization summaries.

Configs:

- Added COVID-19/New York and dengue/Florida fixture extraction smoke configs.
- Added COVID-19/New York and dengue/Florida live search/fetch/extraction smoke configs.
- No API keys are stored in configs.

Tests:

- Added offline deterministic Stage 8 tests for model validation, table extraction, narrative extraction, provenance, schema validation, LLM mock success/failure, full graph fixture smokes, and hantavirus compatibility.
- Updated policy-name assertions in `tests/test_models.py`.

## 5. Generic record schema behavior

`PublicHealthRecord` extends `HantavirusRecord` instead of replacing it. This preserves existing fields while adding generic public-health fields.

Core fields include disease identity, disease standard name, disease alias, pathogen/syndrome, target population, geography, date/time, counts, count semantics, source/provenance, extraction metadata, review metadata, and compatibility metadata.

Required behavior:

- Disease must be present for extracted records.
- Source provenance must include `source_id` or `source_url`.
- Evidence provenance should include `evidence_quote` or `supporting_chunk_id`.
- Numeric count fields must be non-negative.
- Missing values remain `null` instead of being fabricated.

Relationship to `HantavirusRecord`:

- `HantavirusRecord` remains available.
- `PublicHealthRecord` inherits legacy fields for backward compatibility.
- Hantavirus records can carry `legacy_record_type = "HantavirusRecord"`.
- Non-hantavirus records carry `record_schema = "generic_public_health_record"` and do not receive hantavirus disease labels.

## 6. Deterministic extraction behavior

Table extraction:

- Parses simple table-like chunks.
- Detects columns for date, location, cases, deaths, and hospitalizations.
- Produces generic records with source and chunk provenance.

Narrative extraction:

- Parses simple public-health sentences such as reported cases, deaths, hospitalizations, years, and known locations.
- Uses active task disease and disease intelligence terms to decide disease relevance.

Disease term matching:

- COVID-19/New York evidence remains COVID-19 or SARS-CoV-2.
- Dengue/Florida evidence remains Dengue, DENV, or dengue virus.
- Hantavirus/New Mexico evidence remains Hantavirus disease or HPS-compatible.

Count parsing:

- Supports `cases_unspecified`, deaths, hospitalizations, and selected generic numeric fields.
- Preserves or infers `statistical_count_type` and `count_semantics` when possible.
- Uses `unspecified` and warnings when the evidence is not clear.

Warnings/review flags:

- Missing location/date for count-bearing records.
- Missing source provenance.
- Ambiguous table columns.
- Unclear count semantics.
- Extraction-level sanity issues such as deaths greater than cases.

## 7. Optional LLM extraction behavior

LLM structured extraction was updated to target the generic schema through `llm_structured_extraction_policy.json`.

Behavior:

- Disabled by default unless `HDC_ENABLE_LLM_EXTRACTION=true`.
- Does not browse, fetch, search, or invent source URLs.
- Uses evidence text and provenance already in workflow state.
- Validates LLM output against generic record models.
- Falls back to deterministic extraction when configured and LLM output fails.
- Tests mock LLM success and failure; no test calls a real LLM.

Live LLM status:

- Stage 8 live smokes kept LLM extraction disabled.
- `llm_structured_extraction_call_count` was 0 in the fixture and live smoke runs.

## 8. Disease-specific examples

### COVID-19 / New York / 2024

Fixture smoke:

- Evidence chunk count: 2
- Raw generic record count: 2
- Validated record count: 2
- Normalized record count: 2
- Disease values: `{"COVID-19": 2}`
- Count fields extracted: cases, deaths, hospitalizations
- Source provenance: source ID, source URL, supporting chunk ID, fixture search provider, query ID, credibility score

Example record:

```json
{
  "record_id": "rec_src_search_6dca14491140_002",
  "disease": "COVID-19",
  "subnational_location": "New York",
  "date_reported": "2024-06-01",
  "cases_unspecified": 1250.0,
  "deaths": 18.0,
  "hospitalizations": 74.0,
  "source_id": "src_search_6dca14491140",
  "source_url": "https://health.ny.gov/example/covid-19-surveillance-2024",
  "supporting_chunk_id": "chunk_src_search_6dca14491140_002",
  "discovery_method": "fixture_search_result",
  "search_provider": "fixture",
  "record_schema": "generic_public_health_record"
}
```

Live smoke example:

```json
{
  "record_id": "rec_src_search_af2355dda632_001",
  "disease": "COVID-19",
  "subnational_location": "New York City",
  "date_reported": "2025",
  "cases_unspecified": 19.0,
  "source_url": "https://www.nyc.gov/site/doh/covid/covid-19-data-totals.page",
  "discovery_method": "live_search_result",
  "search_provider": "tavily",
  "record_schema": "generic_public_health_record"
}
```

### Dengue / Florida / 2025

Fixture smoke:

- Evidence chunk count: 2
- Raw generic record count: 2
- Validated record count: 2
- Normalized record count: 2
- Disease values: `{"Dengue": 2}`
- Count fields extracted: cases, deaths
- Source provenance: source ID, source URL, supporting chunk ID, fixture search provider, query ID, credibility score

Example record:

```json
{
  "record_id": "rec_src_search_2f25694b3ca0_002",
  "disease": "Dengue",
  "subnational_location": "Florida",
  "date_reported": "2025-08-01",
  "cases_unspecified": 42.0,
  "deaths": 0.0,
  "source_id": "src_search_2f25694b3ca0",
  "source_url": "https://www.floridahealth.gov/example/dengue-surveillance-2025",
  "supporting_chunk_id": "chunk_src_search_2f25694b3ca0_002",
  "discovery_method": "fixture_search_result",
  "search_provider": "fixture",
  "record_schema": "generic_public_health_record"
}
```

Live smoke example:

```json
{
  "record_id": "rec_src_search_53763309bf94_001",
  "disease": "Dengue",
  "subnational_location": "Florida",
  "date_reported": "2025",
  "cases_unspecified": 13.0,
  "source_url": "https://epi.ufl.edu/2025/06/24/dengue-in-florida-what-to-know",
  "discovery_method": "live_search_result",
  "search_provider": "tavily",
  "record_schema": "generic_public_health_record"
}
```

### Hantavirus / New Mexico compatibility

- Legacy record count: 5
- Generic-adapted record count: 5
- Normalized record count: 5
- Disease values: `{"Hantavirus disease": 5}`
- Compatibility status: passed in the configured New Mexico live-fetch compatibility run with all LLM stages disabled.

## 9. Integration with workflow

Evidence chunks feed `structured_extraction`, which now builds disease-aware context and emits `PublicHealthRecord` dictionaries.

Generic records then feed:

- `schema_validation_and_repair` for validation, rejection, and review flags.
- `record_normalization` for disease, location, date, source, numeric, and count-semantics normalization.
- `record_linking` and existing consistency nodes using the retained legacy fields plus generic metadata.
- `finalize_data_package` for final dataset export, provenance manifest, workflow summaries, and diagnostics.

`workflow_summaries` now exposes:

- `generic_record_count`
- `legacy_hantavirus_record_count`
- `disease_counts`
- `source_type_counts`
- `extraction_method_counts`
- `rejected_record_count`
- `review_required_record_count`
- `unsupported_target_field_count`
- `warnings`

Graph topology was not changed.

## 10. Backward compatibility

- `HantavirusRecord` remains available.
- Existing New Mexico/Hantavirus tests continue to pass.
- The New Mexico/Hantavirus configured compatibility run completed with 5 normalized records.
- Existing final dataset fields are retained.
- New generic fields are appended to final output policy rather than removing old fields.
- `legacy_record_type` allows downstream consumers to recognize hantavirus-compatible records.

## 11. Tests added or updated

Added:

- `tests/test_generic_structured_extraction.py`

Updated:

- `tests/test_models.py`

Stage 8 test coverage includes:

- Generic COVID-19 model fields.
- Generic dengue model fields.
- Deterministic COVID-19 table extraction.
- Deterministic dengue table extraction.
- COVID-19 narrative extraction.
- Dengue narrative extraction.
- Non-hantavirus disease preservation.
- Provenance preservation.
- Schema validation rejection/review behavior.
- Optional LLM generic extraction success with mock.
- Optional LLM failure fallback with mock.
- Full graph COVID-19 fixture smoke.
- Full graph dengue fixture smoke.
- Hantavirus compatibility.

## 12. Commands run

Repository inspection:

```powershell
git status --short
git branch --show-current
git rev-parse HEAD
```

Repository inspection result:

- Branch: `main`
- HEAD: `0a74ec8ca7f3ed9ab3b3f7af834de7421a2efb88`
- `git status --short`: non-clean working tree with Stage 1-8 tracked changes, untracked docs/configs/fixtures/tests, and generated outputs; no unrelated user changes were reverted.

Test commands:

```powershell
python -m pytest tests\test_generic_structured_extraction.py -q
python -m pytest tests\test_fetch_parse_generalization.py tests\test_source_credibility_scoring.py tests\test_real_source_discovery.py tests\test_executable_source_planning.py tests\test_profile_schema_setup.py tests\test_disease_intelligence.py tests\test_structured_task_input.py -q
python -m pytest -q
```

Fixture extraction smokes:

```powershell
python scripts\run_hdc_workflow_configured.py --config configs\examples\covid19_new_york_2024_fixture_search_fetch_extract_task.jsonc --session-id stage8_covid19_fixture_extract_smoke
python scripts\run_hdc_workflow_configured.py --config configs\examples\dengue_florida_2025_fixture_search_fetch_extract_task.jsonc --session-id stage8_dengue_fixture_extract_smoke
```

Live extraction smokes:

```powershell
python scripts\run_hdc_workflow_configured.py --config configs\examples\covid19_new_york_2024_live_search_fetch_extract_smoke.jsonc --session-id stage8_covid19_live_extract_smoke
python scripts\run_hdc_workflow_configured.py --config configs\examples\dengue_florida_2025_live_search_fetch_extract_smoke.jsonc --session-id stage8_dengue_live_extract_smoke
```

Hantavirus/New Mexico compatibility:

```powershell
python scripts\run_hdc_workflow_configured.py --config configs\hdc_workflow_run_config.jsonc --disable-all-llm --session-id stage8_hantavirus_live_fetch_compat_no_llm
```

Secret scan:

```powershell
rg -n "tvly-|sk-ant-|ANTHROPIC_API_KEY=\S+|TAVILY_API_KEY=\S+" .env.example configs docs outputs scripts src tests
```

Secret scan result:

- No real API key values found.
- Matches were limited to the mocked `tvly-test-key` in tests and the documented scan pattern in stage reports.

## 13. Test results

Targeted Stage 8 tests:

```text
14 passed in 0.39s
```

Regression subset:

```text
71 passed in 1.24s
```

Full pytest:

```text
291 passed in 7.00s
```

## 14. Fixture extraction smoke results

### COVID-19 fixture extraction smoke

- Status: PASSED
- Command: `python scripts\run_hdc_workflow_configured.py --config configs\examples\covid19_new_york_2024_fixture_search_fetch_extract_task.jsonc --session-id stage8_covid19_fixture_extract_smoke`
- Output directory: `outputs/sessions/stage8_covid19_fixture_extract_smoke`
- Evidence chunk count: 2
- Raw record count: 2
- Validated record count: 2
- Rejected record count: 0
- Normalized record count: 2
- Disease values: `{"COVID-19": 2}`
- Example record: `rec_src_search_6dca14491140_002`, COVID-19, New York, 2024-06-01, 1250 cases, 18 deaths, 74 hospitalizations
- No live web required.
- No API key required.

### Dengue fixture extraction smoke

- Status: PASSED
- Command: `python scripts\run_hdc_workflow_configured.py --config configs\examples\dengue_florida_2025_fixture_search_fetch_extract_task.jsonc --session-id stage8_dengue_fixture_extract_smoke`
- Output directory: `outputs/sessions/stage8_dengue_fixture_extract_smoke`
- Evidence chunk count: 2
- Raw record count: 2
- Validated record count: 2
- Rejected record count: 0
- Normalized record count: 2
- Disease values: `{"Dengue": 2}`
- Example record: `rec_src_search_2f25694b3ca0_002`, Dengue, Florida, 2025-08-01, 42 cases, 0 deaths
- No live web required.
- No API key required.

## 15. Live extraction smoke results

### COVID-19 live extraction smoke

- Status: PASSED
- Command: `python scripts\run_hdc_workflow_configured.py --config configs\examples\covid19_new_york_2024_live_search_fetch_extract_smoke.jsonc --session-id stage8_covid19_live_extract_smoke`
- Provider: Tavily
- API key present: true, value not printed
- Output directory: `outputs/sessions/stage8_covid19_live_extract_smoke`
- Live-search-derived source count: 5
- Selected fetch count: 2
- Usable/partial document count: 2 usable, 0 partial
- Evidence chunk count: 3
- Raw generic record count: 3
- Validated record count: 3
- Rejected record count: 0
- Normalized record count: 3
- Example record: `rec_src_search_af2355dda632_001`, COVID-19, New York City, 2025, 19 cases, live Tavily provenance
- Disease stayed non-hantavirus: yes
- No API keys printed.

### Dengue live extraction smoke

- Status: PASSED
- Command: `python scripts\run_hdc_workflow_configured.py --config configs\examples\dengue_florida_2025_live_search_fetch_extract_smoke.jsonc --session-id stage8_dengue_live_extract_smoke`
- Provider: Tavily
- API key present: true, value not printed
- Output directory: `outputs/sessions/stage8_dengue_live_extract_smoke`
- Live-search-derived source count: 4
- Selected fetch count: 2
- Usable/partial document count: 1 usable, 0 partial, 1 parse deferred
- Evidence chunk count: 8
- Raw generic record count: 6
- Validated record count: 6
- Rejected record count: 0
- Normalized record count: 6
- Example record: `rec_src_search_53763309bf94_001`, Dengue, Florida, 2025, 13 cases, live Tavily provenance
- Disease stayed non-hantavirus: yes
- No API keys printed.

## 16. Hantavirus live-fetch compatibility

- Status: PASSED
- Command: `python scripts\run_hdc_workflow_configured.py --config configs\hdc_workflow_run_config.jsonc --disable-all-llm --session-id stage8_hantavirus_live_fetch_compat_no_llm`
- Output directory: `outputs/sessions/stage8_hantavirus_live_fetch_compat_no_llm`
- `live_fetch_enabled`: true
- `live_search_enabled`: false
- All LLM stages disabled: yes
- Document count: 5
- Usable document count: 5
- Raw record count: 5
- Normalized record count: 5
- Generic record count: 5
- Legacy hantavirus record count: 5
- Human review item count: 8
- Compatibility notes: New Mexico/HPS records remain `Hantavirus disease` and carry compatibility metadata.
- No API keys printed.

## 17. Live acceptance result

PASSED.

Evidence:

- `python -m pytest -q` passed with 291 tests.
- COVID-19 fixture extraction smoke passed.
- Dengue fixture extraction smoke passed.
- Real live Tavily search/fetch/extraction smoke for COVID-19 passed.
- Real live Tavily search/fetch/extraction smoke for dengue passed.
- Hantavirus/New Mexico compatibility passed.
- Non-hantavirus records were not labeled `Hantavirus disease`.
- No API keys or secrets were printed.
- Stage 9 and future-stage features were not implemented.

## 18. Output artifacts

Documentation:

- `docs/generic_structured_extraction.md`
- `docs/stage_reports/STAGE_8_REPORT.md`

Tests:

- `tests/test_generic_structured_extraction.py`

Config examples:

- `configs/examples/covid19_new_york_2024_fixture_search_fetch_extract_task.jsonc`
- `configs/examples/dengue_florida_2025_fixture_search_fetch_extract_task.jsonc`
- `configs/examples/covid19_new_york_2024_live_search_fetch_extract_smoke.jsonc`
- `configs/examples/dengue_florida_2025_live_search_fetch_extract_smoke.jsonc`

Session directories:

- `outputs/sessions/stage8_covid19_fixture_extract_smoke`
- `outputs/sessions/stage8_dengue_fixture_extract_smoke`
- `outputs/sessions/stage8_covid19_live_extract_smoke`
- `outputs/sessions/stage8_dengue_live_extract_smoke`
- `outputs/sessions/stage8_hantavirus_live_fetch_compat_no_llm`

Diagnostics produced in the session directories:

- `diagnostics/raw_records.json`
- `diagnostics/validated_records.json`
- `diagnostics/rejected_records.json`
- `diagnostics/normalized_records.json`
- `diagnostics/structured_extraction_summary.json`
- `diagnostics/schema_validation_summary.json`
- `diagnostics/record_normalization_summary.json`

## 19. Known limitations

- Validation refactor not implemented yet.
- Trusted-source validation not implemented yet.
- Cross-source validation refactor not implemented yet.
- Duplicate/event clustering not implemented yet.
- Anomaly detection not implemented yet.
- Human review decision application not implemented yet.
- CLI/notebook/UI redesign not implemented yet.
- Extraction remains limited by parser quality and evidence availability.
- Some live pages expose dashboard text without structured tables, so deterministic extraction may produce reviewable low-count or context-heavy records.
- PDF parsing can still be deferred depending on the fetched document and parser support.
- LLM extraction may require provider key/model if enabled.

## 20. Future-stage items explicitly NOT implemented

- validation refactor
- trusted-source validation
- cross-source validation
- duplicate/event clustering
- anomaly detection
- human review decision application
- CLI/notebook/UI
- notebook redesign
- UI redesign
- uncontrolled crawling
- recursive crawling
- browser automation
- JavaScript rendering
- OCR

## 21. Review checklist

- [x] User-facing project name remains "data collection workflow"
- [x] Internal package name hdc_workflow was not mass-renamed
- [x] Graph topology unchanged unless documented
- [x] Generic public-health record model exists
- [x] HantavirusRecord compatibility preserved
- [x] COVID-19 extraction produces COVID-19 records
- [x] Dengue extraction produces dengue records
- [x] Non-hantavirus records are not labeled Hantavirus disease
- [x] Table extraction works for COVID-19 fixture
- [x] Table extraction works for dengue fixture
- [x] Narrative extraction works for COVID-19 and dengue fixtures
- [x] Source/evidence/search/credibility provenance is preserved
- [x] Schema validation/repair supports generic records
- [x] Normalization supports generic records
- [x] Final package includes generic record fields
- [x] Existing New Mexico/Hantavirus compatibility passes
- [x] Fixture COVID-19 extraction smoke completed
- [x] Fixture dengue extraction smoke completed
- [x] Live COVID-19 extraction smoke attempted
- [x] Live dengue extraction smoke attempted
- [x] pytest was run
- [x] No API keys or secrets were printed
- [x] No validation refactor was implemented
- [x] No duplicate clustering was implemented
- [x] No anomaly detection was implemented
- [x] No future-stage features were implemented
