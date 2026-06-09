# Stage 13 Report: Multi-disease Live Acceptance + Release Readiness

## 1. Stage goal

Stage 13 is the final acceptance stage proving that **data collection workflow**
runs across Hantavirus / New Mexico / 2020-2026, COVID-19 / New York / 2024,
and Dengue / Florida / 2025 as a local package / CLI / skill-like workflow. The
stage focuses on multi-disease acceptance, final documentation hardening, CLI
readiness, workflow console readiness, and release-readiness evidence.

## 2. Summary of changes

- Added a reusable Stage 13 acceptance matrix helper and export script.
- Exported the final multi-disease acceptance matrix as JSON and CSV.
- Added final multi-disease acceptance tests.
- Hardened README wording so the project is presented as the **data collection workflow**, not as a single-disease project.
- Updated the user guide with explicit troubleshooting coverage.
- Added a release-readiness checklist.
- Fixed a CLI wrapper behavior: `collect --print-config-only` and normal config-driven runs now preserve an existing config `user_request` unless explicit structured CLI overrides are supplied.
- Ran offline fixture acceptance, real Tavily live acceptance, Hantavirus/New Mexico compatibility checks, CLI inspect/review/export checks, regression tests, full pytest, and secret scan.
- Live acceptance status: PASSED for COVID-19 and Dengue after running with network permission.

No new core source discovery algorithm, extraction schema, validation logic,
duplicate clustering logic, anomaly rule set, interactive UI, hosted service,
scheduler, broad crawler, browser automation, JavaScript rendering, OCR, or
graph topology change was implemented.

## 3. Files created or modified

Created:

- `src/hdc_workflow/acceptance.py`
- `scripts/build_stage13_acceptance_matrix.py`
- `tests/test_multidisease_acceptance.py`
- `docs/release_readiness_checklist.md`
- `docs/stage_reports/STAGE_13_REPORT.md`
- `outputs/stage13_multidisease_acceptance_matrix.json`
- `outputs/stage13_multidisease_acceptance_matrix.csv`
- `outputs/stage13_generated_dengue_config.jsonc`

Modified:

- `README.md`
- `docs/user_guide.md`
- `src/hdc_workflow/cli.py`

Acceptance output sessions / exports created:

- `outputs/sessions/stage13_covid19_fixture_acceptance`
- `outputs/sessions/stage13_dengue_fixture_acceptance`
- `outputs/sessions/stage13_covid19_live_acceptance`
- `outputs/sessions/stage13_covid19_live_acceptance_escalated`
- `outputs/sessions/stage13_dengue_live_acceptance_escalated`
- `outputs/sessions/stage13_hantavirus_cli_acceptance_no_llm`
- `outputs/sessions/stage13_hantavirus_cli_acceptance_no_llm_escalated`
- `outputs/sessions/stage13_hantavirus_runner_acceptance_no_llm`
- `outputs/exports/stage13_covid19_fixture_acceptance`

The worktree already contained many Stage 1-12 changes before Stage 13. Stage
13 did not revert them.

## 4. Code and documentation inspection findings

- `README.md`: the top section still framed the package as a Hantavirus public-health case study. It was updated to describe the disease-generic **data collection workflow**, with Hantavirus/New Mexico as the compatibility case study and COVID-19/Dengue as multi-disease examples.
- `docs/user_guide.md`: already covered install, CLI, configs, fixture runs, live runs, LLM setup, human review files, output artifacts, and workflow console. It lacked an explicit troubleshooting section, which was added.
- `docs/final_product_target.md`: already stated that the final target is not a Hantavirus-only workflow and should emit auditable package artifacts with human review rather than automatic truth claims.
- `docs/current_state_audit.md`: remains a historical audit. Some old limitations are now superseded by later stages, so Stage 13 treats it as historical context rather than the current product state.
- Stage 7 report: controlled fetch/parse generalization, bounded live fetch, fixture content maps, parser diagnostics, and Hantavirus/New Mexico compatibility were already documented.
- Stage 8 report: generic `PublicHealthRecord` support was added while preserving `HantavirusRecord` compatibility.
- Stage 9 report: event clustering and duplicate detection were added.
- Stage 10 report: validation was refactored into auditable validation cases/results and Hantavirus compatibility was preserved.
- Stage 11 report: anomaly detection and explicit human review decision application were added.
- Stage 12 report: CLI/package/notebook/workflow-console UX was added, and a Hantavirus CLI compatibility run showed `document_count=5` but `normalized_record_count=0`.
- `src/hdc_workflow/cli.py`: CLI help already exposed the required commands. Stage 13 found and fixed one config fidelity issue: the CLI generated a new `user_request` from structured fields even when the config already provided one.
- `scripts/run_hdc_workflow_configured.py`: already writes sessionized run summaries, diagnostics, readable report, final package, and workflow console outputs.
- `scripts/build_workflow_run_console.py`: already uses generic `PublicHealthRecord` wording and includes validation, anomaly, human review, and post-review dataset summaries.
- `src/hdc_workflow/graph.py`: graph topology was left unchanged.
- Runtime/config/export files: already support config-driven environment mapping, final package export, post-review dataset, validation, anomaly, and human review artifacts.
- Example configs: COVID-19 and Dengue fixture/live configs were present and usable; Hantavirus/New Mexico config remains the compatibility profile.
- Tests: Stage 8-12 behavior had broad coverage; Stage 13 added a final acceptance matrix/CLI/doc readiness test file.

## 5. Final multi-disease acceptance matrix

Full matrix files:

- `outputs/stage13_multidisease_acceptance_matrix.json`
- `outputs/stage13_multidisease_acceptance_matrix.csv`

Concise matrix:

| case_name | source_search_mode | live_search_enabled | live_fetch_enabled | document_count | usable_partial_document_count | evidence_chunk_count | normalized_record_count | validation_result_count | anomaly_result_count | human_review_item_count | final_dataset_count | final_dataset_post_review_count | acceptance_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Hantavirus / New Mexico / 2020-2026 | disabled | False | True | 5 | 5 | 16 | 5 | 17 | 1 | 18 | 5 | 5 | PASSED |
| COVID-19 / New York / 2024 | live | True | True | 2 | 2 | 3 | 3 | 10 | 3 | 16 | 3 | 3 | PASSED |
| Dengue / Florida / 2025 | live | True | True | 2 | 1 | 8 | 6 | 19 | 7 | 32 | 6 | 6 | PASSED |

Disease values in normalized records:

- Hantavirus row: `{"Hantavirus disease": 5}`
- COVID-19 row: `{"COVID-19": 3}`
- Dengue row: `{"Dengue": 6}`

## 6. Offline fixture acceptance results

COVID-19 fixture command:

```powershell
$env:PYTHONPATH='src'; python -m hdc_workflow.cli collect --config configs\examples\covid19_new_york_2024_fixture_review_application_task.jsonc --session-id stage13_covid19_fixture_acceptance --disable-all-llm
```

Result:

- Exit status: 0
- Live search: false
- Live fetch: false
- Source search mode/provider: `fixture` / `fixture`
- Source registry count: 1
- Document count: 1
- Normalized record count: 2
- Validation result count: 7
- Anomaly result count: 0
- Human review item count: 5
- Applied decision count: 2
- Final dataset post-review count: 1
- Final package and workflow console exist.

Dengue fixture command:

```powershell
$env:PYTHONPATH='src'; python -m hdc_workflow.cli collect --config configs\examples\dengue_florida_2025_fixture_review_application_task.jsonc --session-id stage13_dengue_fixture_acceptance --disable-all-llm
```

Result:

- Exit status: 0
- Live search: false
- Live fetch: false
- Source search mode/provider: `fixture` / `fixture`
- Source registry count: 1
- Document count: 1
- Normalized record count: 2
- Validation result count: 7
- Anomaly result count: 0
- Human review item count: 5
- Applied decision count: 2
- Final dataset post-review count: 2
- Final package and workflow console exist.

## 7. Live acceptance results

Status: PASSED.

The first COVID-19 live command inside the restricted sandbox exited 0 but all
Tavily queries returned `provider_error:URLError`, so it was not counted as
live acceptance. The same bounded command was rerun with network permission and
passed.

COVID-19 live command:

```powershell
$env:PYTHONPATH='src'; python -m hdc_workflow.cli collect --config configs\examples\covid19_new_york_2024_live_review_smoke.jsonc --session-id stage13_covid19_live_acceptance_escalated
```

Result:

- Exit status: 0
- Tavily key presence was reported only as present; key value was not printed.
- Live search: true
- Live fetch: true
- Source registry count: 5
- Selected fetch count: 2
- Document count: 2
- Usable/partial document count: 2
- Candidate from search count: 5
- Normalized record count: 3
- Disease values: `{"COVID-19": 3}`
- Validation result count: 10
- Anomaly result count: 3
- Human review item count: 16
- Workflow console exists.

Dengue live command:

```powershell
$env:PYTHONPATH='src'; python -m hdc_workflow.cli collect --config configs\examples\dengue_florida_2025_live_review_smoke.jsonc --session-id stage13_dengue_live_acceptance_escalated
```

Result:

- Exit status: 0
- Tavily key presence was reported only as present; key value was not printed.
- Live search: true
- Live fetch: true
- Source registry count: 3
- Selected fetch count: 2
- Document count: 2
- Usable/partial document count: 1
- Candidate from search count: 3
- Normalized record count: 6
- Disease values: `{"Dengue": 6}`
- Validation result count: 19
- Anomaly result count: 7
- Human review item count: 32
- Workflow console exists.

No live result was faked with fixture output.

## 8. Hantavirus/New Mexico compatibility

Initial CLI run:

```powershell
$env:PYTHONPATH='src'; python -m hdc_workflow.cli collect --config configs\hdc_workflow_run_config.jsonc --disable-all-llm --session-id stage13_hantavirus_cli_acceptance_no_llm
```

Result:

- Exit status: 0
- Live fetch: true
- Live search: false
- All LLM stages disabled: true
- Document count: 5
- Normalized record count: 0
- `diagnostics/live_fetch_summary.json`: all 5 documents had `fetch_failed`.

Runner comparison:

```powershell
python scripts\run_hdc_workflow_configured.py --config configs\hdc_workflow_run_config.jsonc --disable-all-llm --session-id stage13_hantavirus_runner_acceptance_no_llm
```

Result:

- Exit status: 0
- Live fetch: true
- Live search: false
- All LLM stages disabled: true
- Document count: 5
- Usable document count: 5
- Normalized record count: 5
- Validation result count: 17
- Anomaly result count: 1
- Human review item count: 18
- Final dataset post-review count: 5

Resolution rerun under the same network condition:

```powershell
$env:PYTHONPATH='src'; python -m hdc_workflow.cli collect --config configs\hdc_workflow_run_config.jsonc --disable-all-llm --session-id stage13_hantavirus_cli_acceptance_no_llm_escalated
```

Result:

- Exit status: 0
- Live fetch: true
- Live search: false
- All LLM stages disabled: true
- Document count: 5
- Usable document count: 5
- Normalized record count: 5
- Validation result count: 17
- Anomaly result count: 1
- Human review item count: 18
- Final dataset count: 5
- Final dataset post-review count: 5
- Workflow console exists.

Final discrepancy resolution:

- The Stage 12 mismatch was reproduced in the restricted CLI environment.
- Root cause was not a graph or extraction regression: CLI documents were all `fetch_failed` in the restricted environment.
- When CLI was rerun with network access, it matched the runner core counts.
- Stage 13 also fixed a separate CLI config fidelity issue so config-provided `user_request` text is preserved unless explicit structured CLI overrides are supplied.

## 9. CLI and package readiness

Verified:

- `python -m hdc_workflow.cli --help`
- `collect`
- `validate-config`
- `inspect-run`
- `review-summary`
- `export`
- `init-config`
- `python -m hdc_workflow.cli` source-tree support with `PYTHONPATH=src`

CLI help showed:

```text
{collect,validate-config,inspect-run,review-summary,export,init-config}
```

Config template command:

```powershell
$env:PYTHONPATH='src'; python -m hdc_workflow.cli init-config --disease dengue --location Florida --start-date 2025 --end-date 2025 --target-field cases_unspecified --target-field deaths --mode fixture-search --output outputs\stage13_generated_dengue_config.jsonc
```

The generated config validated successfully.

## 10. Documentation readiness

- README now presents the project as **data collection workflow** and describes Hantavirus/New Mexico as the compatibility case study, with COVID-19/New York and Dengue/Florida as multi-disease examples.
- README quickstart includes CLI commands, API key guidance, fixture/live examples, and key artifacts.
- `docs/user_guide.md` covers installation, CLI commands, offline fixture examples, live examples, environment variables, human review decision files, inspect/export/review-summary, output artifacts, workflow console, safety/limitations, and troubleshooting.
- Notebook-style quickstart exists at `examples/notebooks/data_collection_workflow_quickstart.md`.
- API key guidance says keys belong in environment variables, not config files.
- `docs/release_readiness_checklist.md` was added.

## 11. Workflow console readiness

- Console script uses generic `PublicHealthRecord` wording.
- No stale console text was found for Hantavirus-only extraction, unimplemented search execution, placeholder-only validation, or unapplied human review decisions.
- Console sessions were generated for all acceptance runs.
- Console summaries include validation, anomaly, human review application, and final post-review dataset artifacts.

## 12. Tests added or updated

Added:

- `tests/test_multidisease_acceptance.py`

Covered behavior:

- Stage 13 acceptance matrix extraction from session artifacts.
- Acceptance matrix JSON/CSV export.
- CLI preservation of config-provided `user_request`.
- CLI structured-task override behavior when explicit overrides are supplied.
- README/user guide/notebook final release wording expectations.

Updated indirectly through implementation:

- `src/hdc_workflow/acceptance.py`
- `src/hdc_workflow/cli.py`

## 13. Commands run

Repository status:

```powershell
git status --short
git branch --show-current
git rev-parse HEAD
```

Recorded branch / HEAD:

- branch: `main`
- HEAD: `0a74ec8ca7f3ed9ab3b3f7af834de7421a2efb88`

Targeted tests:

```powershell
python -m pytest tests\test_multidisease_acceptance.py -q
python -m pytest tests\test_multidisease_acceptance.py tests\test_cli_and_user_experience.py -q
```

Regression subset:

```powershell
python -m pytest tests\test_real_source_discovery.py tests\test_source_credibility_scoring.py tests\test_fetch_parse_generalization.py tests\test_generic_structured_extraction.py tests\test_duplicate_event_clustering.py tests\test_validation_refactor.py tests\test_anomaly_human_review_application.py -q
```

Full test suite:

```powershell
python -m pytest -q
```

Offline fixture acceptance:

```powershell
$env:PYTHONPATH='src'; python -m hdc_workflow.cli collect --config configs\examples\covid19_new_york_2024_fixture_review_application_task.jsonc --session-id stage13_covid19_fixture_acceptance --disable-all-llm
$env:PYTHONPATH='src'; python -m hdc_workflow.cli collect --config configs\examples\dengue_florida_2025_fixture_review_application_task.jsonc --session-id stage13_dengue_fixture_acceptance --disable-all-llm
```

Live acceptance:

```powershell
$env:PYTHONPATH='src'; python -m hdc_workflow.cli collect --config configs\examples\covid19_new_york_2024_live_review_smoke.jsonc --session-id stage13_covid19_live_acceptance
$env:PYTHONPATH='src'; python -m hdc_workflow.cli collect --config configs\examples\covid19_new_york_2024_live_review_smoke.jsonc --session-id stage13_covid19_live_acceptance_escalated
$env:PYTHONPATH='src'; python -m hdc_workflow.cli collect --config configs\examples\dengue_florida_2025_live_review_smoke.jsonc --session-id stage13_dengue_live_acceptance_escalated
```

Hantavirus CLI / runner compatibility:

```powershell
$env:PYTHONPATH='src'; python -m hdc_workflow.cli collect --config configs\hdc_workflow_run_config.jsonc --disable-all-llm --session-id stage13_hantavirus_cli_acceptance_no_llm
python scripts\run_hdc_workflow_configured.py --config configs\hdc_workflow_run_config.jsonc --disable-all-llm --session-id stage13_hantavirus_runner_acceptance_no_llm
$env:PYTHONPATH='src'; python -m hdc_workflow.cli collect --config configs\hdc_workflow_run_config.jsonc --disable-all-llm --session-id stage13_hantavirus_cli_acceptance_no_llm_escalated
```

Inspect/review/export:

```powershell
$env:PYTHONPATH='src'; python -m hdc_workflow.cli inspect-run --session-dir outputs\sessions\stage13_covid19_fixture_acceptance
$env:PYTHONPATH='src'; python -m hdc_workflow.cli review-summary --session-dir outputs\sessions\stage13_covid19_fixture_acceptance
$env:PYTHONPATH='src'; python -m hdc_workflow.cli export --session-dir outputs\sessions\stage13_covid19_fixture_acceptance --output-dir outputs\exports\stage13_covid19_fixture_acceptance --format both
```

Config readiness:

```powershell
$env:PYTHONPATH='src'; python -m hdc_workflow.cli validate-config --config configs\examples\covid19_new_york_2024_fixture_review_application_task.jsonc
$env:PYTHONPATH='src'; python -m hdc_workflow.cli init-config --disease dengue --location Florida --start-date 2025 --end-date 2025 --target-field cases_unspecified --target-field deaths --mode fixture-search --output outputs\stage13_generated_dengue_config.jsonc
$env:PYTHONPATH='src'; python -m hdc_workflow.cli validate-config --config outputs\stage13_generated_dengue_config.jsonc
```

Acceptance matrix export:

```powershell
$env:PYTHONPATH='src'; python scripts\build_stage13_acceptance_matrix.py
```

Secret scan:

```powershell
rg -n "tvly-|sk-ant-|ANTHROPIC_API_KEY=\S+|TAVILY_API_KEY=\S+" .env.example configs docs examples notebooks scripts src tests outputs
```

The scan matched only fake test keys, documented scan-command text in prior
stage reports, and known secret-prefix redaction code. It also reported that
the optional `notebooks` path does not exist. No real secret value was found or
printed.

## 14. Test results

Targeted Stage 13 + CLI/UX tests:

```text
12 passed in 4.68s
```

Regression subset:

```text
107 passed in 1.57s
```

Full pytest:

```text
356 passed in 13.16s
```

## 15. Output artifacts

Created or updated:

- `docs/release_readiness_checklist.md`
- `docs/stage_reports/STAGE_13_REPORT.md`
- `tests/test_multidisease_acceptance.py`
- `src/hdc_workflow/acceptance.py`
- `scripts/build_stage13_acceptance_matrix.py`
- `outputs/stage13_multidisease_acceptance_matrix.json`
- `outputs/stage13_multidisease_acceptance_matrix.csv`
- `outputs/stage13_generated_dengue_config.jsonc`
- `outputs/sessions/stage13_covid19_fixture_acceptance`
- `outputs/sessions/stage13_dengue_fixture_acceptance`
- `outputs/sessions/stage13_covid19_live_acceptance_escalated`
- `outputs/sessions/stage13_dengue_live_acceptance_escalated`
- `outputs/sessions/stage13_hantavirus_cli_acceptance_no_llm_escalated`
- `outputs/sessions/stage13_hantavirus_runner_acceptance_no_llm`
- `outputs/exports/stage13_covid19_fixture_acceptance`

## 16. Final acceptance result

PASSED.

Basis:

- `pytest -q` passed.
- Offline fixture acceptance passed for COVID-19 and Dengue.
- COVID-19 live acceptance passed with real Tavily live search and controlled live fetch.
- Dengue live acceptance passed with real Tavily live search and controlled live fetch.
- Hantavirus/New Mexico compatibility passed after CLI and runner were compared under the same network condition.
- CLI commands passed: help, collect, validate-config, inspect-run, review-summary, export, init-config.
- README, user guide, notebook quickstart, release checklist, and workflow console wording are current.
- No API keys or real secrets were printed or committed.
- No future-stage scope creep was implemented.

## 17. Known limitations

- The workflow is not official public-health surveillance.
- The workflow is not medical advice.
- Expert review is required before using outputs in reporting or decision-making.
- Live web/search depends on API keys, provider availability, target-site availability, network access, and configured query/fetch limits.
- Dashboards, PDFs, JavaScript-rendered pages, and low-text pages can still be hard to parse.
- There is no interactive human review UI.
- There is no hosted service.
- The workflow does not determine automatic truth.
- Disease intelligence is curated for a limited set of profiles.
- New diseases may need review of disease intelligence, source terms, search queries, validation sources, and extraction behavior.

## 18. Remaining future work

- Interactive review UI if desired.
- Hosted/deployment packaging if desired.
- Broader disease intelligence library.
- Stronger parser support for dashboards/PDFs if desired.
- Advanced epidemiological anomaly models if desired.
- User studies / documentation polish.
- Publication/reporting materials if desired.

## 19. Review checklist

- [x] User-facing project name remains "data collection workflow"
- [x] Internal package name hdc_workflow was not mass-renamed
- [x] Graph topology unchanged unless documented
- [x] COVID-19 fixture acceptance passed
- [x] Dengue fixture acceptance passed
- [x] COVID-19 live acceptance passed or honestly marked
- [x] Dengue live acceptance passed or honestly marked
- [x] Hantavirus/New Mexico compatibility passed
- [x] CLI collect works
- [x] CLI validate-config works
- [x] CLI inspect-run works
- [x] CLI review-summary works
- [x] CLI export works
- [x] CLI init-config works
- [x] README is current and not hantavirus-only
- [x] User guide exists and is current
- [x] Notebook-style quickstart exists
- [x] Workflow console wording is current
- [x] Acceptance matrix exported
- [x] Release readiness checklist exists
- [x] pytest was run
- [x] No API keys or secrets were printed
- [x] No future-stage features were implemented
