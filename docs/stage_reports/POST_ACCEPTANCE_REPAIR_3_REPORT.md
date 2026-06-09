# Post-Acceptance Repair 3 Report

## Stage goal

Implement task-compatible validation ground truth selection for the data
collection workflow. Held-out validation records are now enabled only when they
match the active task's disease, geography, and time window.

## Summary of changes

- Added deterministic validation-source compatibility resolution.
- Split loaded validation records into active and inactive sets.
- Updated graph validation to compare only active validation records.
- Prevented misleading evaluation rows when no task-compatible validation source
  is available.
- Added compatibility summaries to diagnostics, final package workflow
  summaries, run summaries, readable reports, and validation artifacts.
- Added a safe config/env override for diagnostic force-loading of incompatible
  explicit validation records.

## Files changed

- `.env.example`
- `configs/hdc_workflow_run_config.jsonc`
- `configs/examples/repair3_hantavirus_shanghai_validation_compat_offline.jsonc`
- `docs/task_compatible_validation_sources.md`
- `docs/user_guide.md`
- `scripts/build_workflow_run_console.py`
- `scripts/run_hdc_workflow_configured.py`
- `src/hdc_workflow/evaluation_report_builder.py`
- `src/hdc_workflow/nodes/linking_validation.py`
- `src/hdc_workflow/resources/final_package_policy.json`
- `src/hdc_workflow/runtime_profile.py`
- `src/hdc_workflow/state.py`
- `src/hdc_workflow/validation_source_compatibility.py`
- `tests/test_task_compatible_validation_sources.py`
- `tests/test_workflow_run_config.py`

Note: the working tree already contained uncommitted Repair 1 and Repair 2
changes. This repair did not revert them.

## New/updated tests

- Added `tests/test_task_compatible_validation_sources.py`.
- Updated `tests/test_workflow_run_config.py` for the validation override env.

The new tests cover:

- New Mexico HPS validation remains active for the New Mexico HPS task.
- New Mexico HPS validation is disabled for Shanghai hantavirus.
- New Mexico HPS validation is disabled for COVID-19/New York.
- New Mexico HPS validation is disabled for dengue/Florida.
- Explicit compatible validation CSVs load normally.
- Explicit incompatible validation CSVs are disabled by default.
- Override can force-load incompatible validation with a warning.
- Evaluation reports do not compare Shanghai collection records against New
  Mexico validation records.
- Graph validation uses active validation records only.
- A graph run with no compatible validation source still completes.
- Validation artifact writer exports active/inactive records and the summary.

## Commands run

- `python -m pytest tests\test_task_compatible_validation_sources.py -q`
- `python -m pytest tests\test_disease_relevance_gating.py tests\test_source_critic_live_integration.py tests\test_validation_refactor.py tests\test_new_mexico_hps_workflow_case.py tests\test_workflow_run_config.py tests\test_graph_smoke.py -q`
- `python -m pytest -q`
- `python scripts\run_hdc_workflow_configured.py --config configs\hdc_workflow_run_config.jsonc --disable-all-llm --disable-live-fetch --session-id repair3_hantavirus_new_mexico_validation_compat_no_llm`
- `python scripts\run_hdc_workflow_configured.py --config configs\examples\repair3_hantavirus_shanghai_validation_compat_offline.jsonc --session-id repair3_hantavirus_shanghai_validation_compat_offline`
- `rg -n "tvly-|sk-ant-|ANTHROPIC_API_KEY=\S+|TAVILY_API_KEY=\S+" .env.example configs docs scripts src tests outputs`
- `rg -n "sk-ant-[A-Za-z0-9_-]{20,}|tvly-[A-Za-z0-9_-]{20,}|ANTHROPIC_API_KEY\s*=\s*[A-Za-z0-9_-]{20,}|TAVILY_API_KEY\s*=\s*[A-Za-z0-9_-]{20,}" .env.example configs docs scripts src tests outputs`
- `git diff --check`

One attempted command using the old generated Shanghai real-run config timed
out because that config still had live search enabled. It was replaced by the
offline Repair 3 smoke config above; no Repair 3 behavior depended on the timed
out run.

## Test results

- Target Repair 3 tests: `11 passed`.
- Related regression subset: `179 passed`.
- Full suite: `394 passed`.
- `git diff --check`: exit 0; only CRLF normalization warnings were printed.
- Broad secret scan matched only mock test keys and documented scan-command text.
- Strict real-key scan returned no matches.

## Example command or fixture run

New Mexico compatibility smoke:

- Session: `outputs/sessions/repair3_hantavirus_new_mexico_validation_compat_no_llm`
- Compatibility status: `compatible`
- Active validation records: `1`
- Inactive validation records: `0`

Shanghai incompatibility smoke:

- Session: `outputs/sessions/repair3_hantavirus_shanghai_validation_compat_offline`
- Compatibility status: `incompatible_validation_source_disabled`
- Active validation records: `0`
- Inactive validation records: `1`
- Evaluation row count: `0`

## Output artifacts created

- `outputs/sessions/repair3_hantavirus_new_mexico_validation_compat_no_llm/`
- `outputs/sessions/repair3_hantavirus_shanghai_validation_compat_offline/`
- `validation/ground_truth_records.csv` now contains active validation records
  only for each session.
- `validation/inactive_validation_records.csv`
- `validation/inactive_validation_records.json`
- `validation/validation_source_compatibility_summary.json`
- `diagnostics/active_validation_records.json`
- `diagnostics/inactive_validation_records.json`
- `diagnostics/validation_source_compatibility_summary.json`

## Known limitations

- This repair does not discover new validation sources.
- The historical New Mexico HPS ground truth can still be the default candidate
  when a config omits a validation CSV path, but it is now disabled for
  incompatible tasks.
- Compatibility checks are deterministic and metadata-driven; sparse validation
  metadata may produce insufficient-metadata warnings.
- The old generated Shanghai real-run config still needs a separate live-search
  control path if it is used for networked smoke tests.

## Future-stage items NOT implemented

- No localized multilingual official-source planning.
- No search provider or discovery changes.
- No live search result ingestion changes.
- No run-quality final dataset redesign.
- No HTML/report redesign beyond surfacing compatibility fields.
- No duplicate, anomaly, or human-review semantic redesign.
- No CLI/UI redesign.
- No graph topology changes.
- No crawling, browser automation, OCR, captcha handling, or paywall handling.

## Review checklist

- [x] Project name remains data collection workflow.
- [x] Internal package name remains `hdc_workflow`.
- [x] Default offline deterministic tests do not require internet, API keys, live
  web, or real LLM calls.
- [x] New outputs include provenance-oriented task/config/status metadata.
- [x] Incompatible held-out validation records are preserved as inactive audit
  records.
- [x] No real API keys were printed or committed.
- [x] Full `pytest -q` passed.
- [x] Repair 4 was not started.
