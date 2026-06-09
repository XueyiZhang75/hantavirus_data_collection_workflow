# Stage 12 Report: Package / CLI / Notebook / Workflow Console / User-facing UX

## Stage goal

Package the **data collection workflow** so a user can configure, run, inspect,
review, and export workflow sessions through a stable CLI and clear user-facing
documentation, while preserving the existing offline deterministic default
behavior.

## Summary of changes

- Added `hdc_workflow.cli`, a user-facing command layer with:
  - `collect`
  - `validate-config`
  - `inspect-run`
  - `review-summary`
  - `export`
  - `init-config`
- Added a `data-collection-workflow` console-script entry point in
  `pyproject.toml`.
- Extended package metadata and package-data globs so nested workflow resources
  are included in package builds.
- Added safe config preview / dry-run behavior that reports whether API keys are
  present without printing key values.
- Added safe starter config generation with comments pointing users to
  environment variables, not embedded secrets.
- Reused the existing configured workflow runner for actual `collect` runs.
  Stage 12 did not create a separate demo-only workflow branch.
- Added run inspection, human-review summary, and export helpers over completed
  session directories.
- Updated workflow console copy to use generic public-health record wording
  instead of stale `HantavirusRecord`-only wording.
- Added a user guide and notebook-style quickstart.
- Updated README quickstart to show the package/CLI workflow, offline fixture
  examples, live search key setup, and LLM key setup.

## Files changed

- `src/hdc_workflow/cli.py`
- `pyproject.toml`
- `scripts/build_workflow_run_console.py`
- `README.md`
- `docs/user_guide.md`
- `examples/notebooks/data_collection_workflow_quickstart.md`
- `tests/test_cli_and_user_experience.py`
- `docs/stage_reports/STAGE_12_REPORT.md`

## New/updated tests

New test file:

- `tests/test_cli_and_user_experience.py`

Test coverage added for:

- CLI help and subcommand list.
- Config validation for COVID-19 fixture, dengue fixture, COVID-19 live smoke,
  and dengue live smoke configs.
- Secret-safe config preview with fake `TAVILY_API_KEY` and fake
  `ANTHROPIC_API_KEY` values.
- Dry-run structured task overrides without graph invocation.
- Offline fixture `collect`, followed by `inspect-run`, `review-summary`, and
  `export`.
- Safe config template generation and validation.
- Generic workflow console wording.
- README, user guide, and quickstart coverage.

## Commands run

Red test:

```powershell
python -m pytest tests\test_cli_and_user_experience.py -q
```

Targeted and regression verification:

```powershell
python -m pytest tests\test_cli_and_user_experience.py -q
python -m pytest tests\test_anomaly_human_review_application.py tests\test_validation_refactor.py tests\test_duplicate_event_clustering.py tests\test_generic_structured_extraction.py tests\test_fetch_parse_generalization.py tests\test_source_credibility_scoring.py tests\test_real_source_discovery.py tests\test_executable_source_planning.py tests\test_profile_schema_setup.py tests\test_disease_intelligence.py tests\test_structured_task_input.py -q
python -m pytest -q
```

CLI smoke commands:

```powershell
$env:PYTHONPATH='src'; python -m hdc_workflow.cli --help
$env:PYTHONPATH='src'; python -m hdc_workflow.cli validate-config --config configs/examples/covid19_new_york_2024_fixture_review_application_task.jsonc
$env:PYTHONPATH='src'; python -m hdc_workflow.cli validate-config --config configs/examples/dengue_florida_2025_fixture_review_application_task.jsonc
$env:PYTHONPATH='src'; python -m hdc_workflow.cli validate-config --config configs/examples/covid19_new_york_2024_live_review_smoke.jsonc
$env:PYTHONPATH='src'; python -m hdc_workflow.cli validate-config --config configs/examples/dengue_florida_2025_live_review_smoke.jsonc
$env:PYTHONPATH='src'; python -m hdc_workflow.cli init-config --disease dengue --location Florida --start-date 2025 --end-date 2025 --target-field cases_unspecified --target-field deaths --mode fixture-search --output outputs\stage12_generated_dengue_config.jsonc
$env:PYTHONPATH='src'; python -m hdc_workflow.cli validate-config --config outputs\stage12_generated_dengue_config.jsonc
$env:PYTHONPATH='src'; python -m hdc_workflow.cli collect --config configs\examples\covid19_new_york_2024_fixture_review_application_task.jsonc --session-id stage12_cli_covid19_fixture_collect --disable-all-llm
$env:PYTHONPATH='src'; python -m hdc_workflow.cli collect --config configs\examples\dengue_florida_2025_fixture_review_application_task.jsonc --session-id stage12_cli_dengue_fixture_collect --disable-all-llm
$env:PYTHONPATH='src'; python -m hdc_workflow.cli inspect-run --session-dir outputs\sessions\stage12_cli_covid19_fixture_collect
$env:PYTHONPATH='src'; python -m hdc_workflow.cli review-summary --session-dir outputs\sessions\stage12_cli_covid19_fixture_collect
$env:PYTHONPATH='src'; python -m hdc_workflow.cli export --session-dir outputs\sessions\stage12_cli_covid19_fixture_collect --output-dir outputs\exports\stage12_cli_covid19_fixture_collect --format both
$env:PYTHONPATH='src'; python -m hdc_workflow.cli collect --config configs\hdc_workflow_run_config.jsonc --session-id stage12_hantavirus_cli_compat_no_llm --disable-all-llm
```

Live search smoke:

```powershell
$env:PYTHONPATH='src'; python -m hdc_workflow.cli collect --config configs\examples\covid19_new_york_2024_live_review_smoke.jsonc --session-id stage12_cli_covid19_live_search_smoke --disable-all-llm
$env:PYTHONPATH='src'; python -m hdc_workflow.cli collect --config configs\examples\covid19_new_york_2024_live_review_smoke.jsonc --session-id stage12_cli_covid19_live_search_smoke_escalated --disable-all-llm
```

Secret scan:

```powershell
rg -l "sk-ant-|tvly-|OPENAI_API_KEY=.*[A-Za-z0-9_-]{20,}|ANTHROPIC_API_KEY=.*[A-Za-z0-9_-]{20,}" --glob "!.env" --glob "!.git/**" --glob "!.pytest_cache/**"
rg -l 'tvly-test-key|sk-ant-test-key' tests src docs README.md examples configs --glob '!.env' --glob '!.git/**'
```

## Test results

- Initial red test: 8 failing tests, mainly missing `hdc_workflow.cli`, stale
  console wording, and missing UX docs.
- Targeted Stage 12 tests after implementation: `8 passed`.
- Regression subset: `138 passed`.
- Full test suite: `352 passed`.
- Final targeted rerun after small CLI output cleanup: `8 passed`.
- Final full test suite rerun: `352 passed`.

## Example command or fixture run

Offline fixture COVID-19:

```powershell
$env:PYTHONPATH='src'; python -m hdc_workflow.cli collect --config configs\examples\covid19_new_york_2024_fixture_review_application_task.jsonc --session-id stage12_cli_covid19_fixture_collect --disable-all-llm
```

Observed summary:

- `source_search_mode`: `fixture`
- `source_search_provider`: `fixture`
- `normalized_record_count`: `2`
- `human_review_item_count`: `5`
- `human_review_decisions_applied_count`: `2`
- `human_review_decisions_rejected_count`: `1`
- `final_dataset_post_review_count`: `1`

Offline fixture dengue:

- `source_search_mode`: `fixture`
- `source_search_provider`: `fixture`
- `normalized_record_count`: `2`
- `human_review_item_count`: `5`
- `human_review_decisions_applied_count`: `2`
- `human_review_decisions_rejected_count`: `0`
- `final_dataset_post_review_count`: `2`

Hantavirus / New Mexico compatibility no-LLM run:

- `source_search_mode`: `disabled`
- `source_registry_count`: `20`
- `document_count`: `5`
- `normalized_record_count`: `0`
- `human_review_item_count`: `2`
- `all_three_llm_stages_enabled`: `false`

## Live search smoke result

The first live Tavily smoke inside the default restricted sandbox completed the
workflow but search calls returned `provider_error:URLError`.

After running the same bounded command with network permission, the live Tavily
path succeeded:

- `search_provider`: `tavily`
- `executed_query_count`: `2`
- `raw_search_result_count`: `6`
- `deduplicated_search_result_count`: `5`
- `candidate_from_search_count`: `5`
- `provider_error_count`: `0`
- `normalized_record_count`: `3`
- `anomaly_result_count`: `3`
- `human_review_item_count`: `16`

This confirms the CLI can drive the existing live-search path when a key and
network access are available. Live search remains optional and is not required
for tests.

## Output artifacts created

Stage 12 smoke artifacts:

- `outputs/sessions/stage12_cli_covid19_fixture_collect/`
- `outputs/sessions/stage12_cli_dengue_fixture_collect/`
- `outputs/sessions/stage12_hantavirus_cli_compat_no_llm/`
- `outputs/sessions/stage12_cli_covid19_live_search_smoke/`
- `outputs/sessions/stage12_cli_covid19_live_search_smoke_escalated/`
- `outputs/exports/stage12_cli_covid19_fixture_collect/`
- `outputs/stage12_generated_dengue_config.jsonc`

Each completed session includes:

- `workflow_run_report_chinese.md`
- `workflow_run_summary.json`
- `applied_workflow_config.json`
- `collection/final_package.json`
- `collection/final_dataset.csv`
- `collection/final_dataset_post_review.json`
- `diagnostics/source_search_execution_summary.json`
- `diagnostics/live_fetch_summary.json`
- `diagnostics/llm_stage_summary.json`
- `diagnostics/anomaly_results.json`
- `diagnostics/human_review_audit_trail.json`
- `workflow_console/hdc_workflow_console.html`

## Known limitations

- Running `python -m hdc_workflow.cli` directly from a source checkout requires
  either `python -m pip install -e .` or a temporary `PYTHONPATH=src` setting.
- The CLI wraps the existing configured runner. It does not replace LangGraph
  Studio and does not add an interactive hosted UI.
- The `collect` command writes a temporary applied config into the runner, then
  writes the sanitized final config used by the CLI to
  `applied_workflow_config.json` in the session directory.
- Live search depends on `TAVILY_API_KEY` and network access.
- LLM stages depend on provider keys and explicit config/CLI enablement.
- The workflow console is generated after a completed run. It is not a
  continuously streaming UI.
- Console-script verification through `data-collection-workflow` was added in
  package metadata, but the local smoke used `PYTHONPATH=src` instead of
  installing the package during this stage.

## Explicit future-stage items NOT implemented

Stage 12 did not implement:

- New source/search provider logic.
- New live crawling behavior.
- JavaScript rendering, OCR, paywall bypass, or captcha handling.
- New extraction, validation, duplicate detection, anomaly detection, or
  human-review decision semantics.
- Interactive web UI or hosted service.
- Background jobs or scheduling.
- Truth determination.
- Key storage or key printing.
- Graph topology changes.
- Mass package renaming.
- Stage 13 functionality.

## Review checklist

- [x] User-facing project name remains `data collection workflow`.
- [x] Internal package name remains `hdc_workflow`.
- [x] Stage 12 stayed focused on packaging, CLI, notebook/docs, and console UX.
- [x] Default tests remain offline and deterministic.
- [x] No real API keys were printed or committed.
- [x] New behavior has tests.
- [x] `pytest -q` was run and passed.
- [x] CLI dry-run / print-config paths avoid graph execution.
- [x] CLI output reports key presence only.
- [x] Workflow console copy no longer presents the workflow as
  HantavirusRecord-only extraction.
- [x] Generated runs include auditable session artifacts and sanitized config
  metadata.
- [x] Future-stage items were not implemented.
