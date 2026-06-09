# Post-acceptance Repair 6 Report: Full HTML/report dynamic cleanup

## 1. Repair goal

Clean up the dynamic Markdown report, HTML workflow console, and console summary
JSON so they describe the current data collection workflow session artifacts
instead of carrying hard-coded New Mexico/Hantavirus success-demo language.

This repair is not Stage 14 and does not implement a new workflow stage.

## 2. Scope

Implemented only report/console output cleanup:

- Dynamic task fields in report/console/summary.
- Dynamic user-facing run status from run-quality artifacts.
- Clear separation of technical workflow completion from accepted final dataset
  success.
- Final dataset, pre-quality, quarantined, pending-review, and post-review
  counts in Markdown and HTML outputs.
- Source critic, disease relevance, validation compatibility, localized planning,
  and artifact-path panels in the HTML console.
- Latest alias consistency after configured workflow runs.

## 3. Summary of changes

- Reworked `scripts/build_workflow_run_console.py` to build an HTML payload from
  current run artifacts rather than static demo wording.
- Added dynamic task recovery from `task_intake_summary`, structured task fields,
  and package metadata, with an explicit unavailable placeholder when missing.
- Added `user_facing_run_status()` for consistent report/console status wording.
- Updated console summary JSON with top-level task, run-quality, validation
  compatibility, source critic, localized planning, and dataset-count fields.
- Updated `scripts/run_hdc_workflow_configured.py` Markdown report export to show
  accepted final dataset counts separately from normalized/pre-quality records.
- Added a no-accepted-records message for technically completed runs that produce
  zero quality-gated accepted records.
- Added docs for maintaining dynamic report/console behavior.
- Added Repair 6 tests covering Shanghai/no-accepted-records and New Mexico
  compatibility behavior.

## 4. Files changed

- `scripts/build_workflow_run_console.py`
- `scripts/run_hdc_workflow_configured.py`
- `tests/test_report_console_dynamic_cleanup.py`
- `docs/report_console_dynamic_cleanup.md`
- `docs/stage_reports/POST_ACCEPTANCE_REPAIR_6_REPORT.md`

## 5. New or updated tests

Added `tests/test_report_console_dynamic_cleanup.py` with coverage for:

- No hard-coded New Mexico/NMDOH/CDC success labels in non-New-Mexico sessions.
- Missing collection spec uses `collection_spec unavailable in artifacts`.
- Quality-gated accepted/pre-quality/quarantined/pending/post-review counts.
- Validation source compatibility display.
- Source critic, disease relevance, and localized planning display.
- Markdown report wording for technically completed runs with zero accepted
  records.
- Markdown report counts for accepted and quarantined records.
- New Mexico compatibility still allows New Mexico to appear when it is the
  current task.
- No `HantavirusRecord`-only wording in current console source.

## 6. Commands run

- `python -m pytest tests\test_report_console_dynamic_cleanup.py -q`
- `python -m pytest tests\test_disease_relevance_gating.py tests\test_source_critic_live_integration.py tests\test_task_compatible_validation_sources.py tests\test_localized_multilingual_source_planning.py tests\test_run_quality_gated_final_dataset.py tests\test_cli_and_user_experience.py -q`
- `python -m pytest tests\test_multidisease_acceptance.py tests\test_anomaly_human_review_application.py tests\test_validation_refactor.py tests\test_generic_structured_extraction.py tests\test_graph_smoke.py tests\test_workflow_run_config.py -q`
- `python -m pytest -q`
- `python scripts\run_hdc_workflow_configured.py --config outputs\generated_configs\hantavirus_shanghai_2024_1_1_2026_6_9_20260609_141441_utc.json --session-id repair6_hantavirus_shanghai_dynamic_report`
- `python scripts\run_hdc_workflow_configured.py --config configs\hdc_workflow_run_config.jsonc --disable-all-llm --session-id repair6_hantavirus_new_mexico_report_console_compat_no_llm`
- `rg -n "抽取 HantavirusRecord|live NMDOH/CDC webpage fetch|current successful product run|produced 5 collection records|LLM extraction.*2 normalized records|New Mexico HPS live LLM workflow run" scripts src docs README.md`
- `rg -n "live NMDOH/CDC webpage fetch|current successful product run|produced 5 collection records|LLM extraction.*2 normalized records|New Mexico HPS live LLM workflow run" outputs\workflow_console outputs\workflow_runs\latest_workflow_run_report_chinese.md outputs\workflow_runs\latest_workflow_run_summary.json outputs\sessions\repair6_hantavirus_shanghai_dynamic_report outputs\sessions\repair6_hantavirus_new_mexico_report_console_compat_no_llm`
- `rg -n "tvly-|sk-ant-|ANTHROPIC_API_KEY=\S+|TAVILY_API_KEY=\S+" .env.example configs docs scripts src tests outputs`
- `rg -n "sk-ant-[A-Za-z0-9_-]{20,}|tvly-[A-Za-z0-9_-]{20,}|ANTHROPIC_API_KEY\s*=\s*[A-Za-z0-9_-]{20,}|TAVILY_API_KEY\s*=\s*[A-Za-z0-9_-]{20,}" .env.example configs docs scripts src tests outputs`
- `git status --short`
- `git branch --show-current`
- `git rev-parse HEAD`

## 7. Test results

- Initial Repair 6 red test before implementation: `7 failed, 2 passed`.
- Final Repair 6 targeted tests: `9 passed in 0.62s`.
- Related regression set: `64 passed in 4.74s`.
- Acceptance/regression set: `189 passed in 7.22s`.
- Full test suite: `426 passed in 20.68s`.

## 8. Example runs

### Shanghai dynamic report session

Command:

```powershell
python scripts\run_hdc_workflow_configured.py --config outputs\generated_configs\hantavirus_shanghai_2024_1_1_2026_6_9_20260609_141441_utc.json --session-id repair6_hantavirus_shanghai_dynamic_report
```

Key result:

- `trace_node_count`: 20
- `source_search_mode`: live
- `source_search_executed_query_count`: 2
- `search_derived_candidate_count`: 6
- `document_count`: 0
- `normalized_record_count`: 0
- `run_quality_status`: `no_task_relevant_records`
- `final_dataset_count`: 0
- `human_review_item_count`: 10

The report now says:

- `workflow technically completed, but no quality-gated accepted records were produced.`
- `Held-out validation was limited because no task-compatible validation source was available.`

### New Mexico compatibility session

Command:

```powershell
python scripts\run_hdc_workflow_configured.py --config configs\hdc_workflow_run_config.jsonc --disable-all-llm --session-id repair6_hantavirus_new_mexico_report_console_compat_no_llm
```

Key result:

- `trace_node_count`: 20
- `source_search_mode`: disabled
- `document_count`: 5
- `normalized_record_count`: 5
- `run_quality_status`: `partial_with_quarantined_records`
- `final_dataset_count`: 4
- `quarantined_record_count`: 1
- `evaluation_row_count`: 4

The report and console still show New Mexico because it is the current task.

## 9. Output artifacts created

- `outputs/sessions/repair6_hantavirus_shanghai_dynamic_report/`
- `outputs/sessions/repair6_hantavirus_shanghai_dynamic_report/workflow_run_report_chinese.md`
- `outputs/sessions/repair6_hantavirus_shanghai_dynamic_report/workflow_console/hdc_workflow_console.html`
- `outputs/sessions/repair6_hantavirus_shanghai_dynamic_report/workflow_console/hdc_workflow_console_summary.json`
- `outputs/sessions/repair6_hantavirus_new_mexico_report_console_compat_no_llm/`
- `outputs/sessions/repair6_hantavirus_new_mexico_report_console_compat_no_llm/workflow_run_report_chinese.md`
- `outputs/sessions/repair6_hantavirus_new_mexico_report_console_compat_no_llm/workflow_console/hdc_workflow_console.html`
- `outputs/sessions/repair6_hantavirus_new_mexico_report_console_compat_no_llm/workflow_console/hdc_workflow_console_summary.json`
- `outputs/workflow_console/hdc_workflow_console.html`
- `outputs/workflow_console/hdc_workflow_console_summary.json`
- `outputs/workflow_runs/latest_workflow_run_report_chinese.md`
- `outputs/workflow_runs/latest_workflow_run_summary.json`

## 10. Output artifact checks

- Shanghai console summary:
  - `task_location`: `shanghai`
  - `accepted_record_count`: 0
  - `user_facing_run_status`: completed with no task-relevant records
  - `validation_source_compatibility_summary.compatibility_status`:
    `incompatible_validation_source_disabled`
- New Mexico console summary:
  - `task_location`: `New Mexico`
  - `accepted_record_count`: 4
  - `pre_quality_record_count`: 5
  - `quarantined_record_count`: 1
  - `post_review_record_count`: 4
- Latest aliases now point to the New Mexico compatibility session generated in
  this repair pass.

## 11. Secret scan results

Broad scan matched only mocked test keys and historical documented scan commands:

- `tvly-test-key`
- `sk-ant-test-key`
- documented `rg` command text in stage reports

Strict key-shaped scan returned no matches for real-looking Anthropic or Tavily
keys.

No real API keys were printed or committed by this repair.

## 12. Stale wording scan results

No matches in current source/docs for:

- `抽取 HantavirusRecord`
- `live NMDOH/CDC webpage fetch`
- `current successful product run`
- `produced 5 collection records`
- `LLM extraction.*2 normalized records`
- `New Mexico HPS live LLM workflow run`

No matches in latest aliases or Repair 6 session artifacts for the stale fixed
demo wording.

Historical archived outputs under older `outputs/workflow_runs/.../sessions/...`
still contain old generated HTML text. Those are prior run artifacts and were
not rewritten in this repair.

## 13. Known limitations

- The HTML console is still a static rebuilt artifact, not a live-updating
  browser stream while the graph is executing.
- Old historical output sessions are not rewritten retroactively.
- Some existing config comments still show mojibake from prior files; this repair
  only cleaned the report/console surfaces touched by the requested task.
- The Shanghai run found live search candidates but produced no usable fetched
  documents, so it validates no-accepted-record display rather than successful
  extraction display.

## 14. Future-stage items not implemented

- No graph topology changes.
- No new crawling or search-provider behavior.
- No source discovery/planning/extraction algorithm changes.
- No validation comparison redesign.
- No human-review UI redesign.
- No LangGraph Studio live interaction redesign.
- No broad project rename or package rename.
- No retroactive rewrite of all historical output sessions.

## 15. Review checklist

- [x] Report title no longer says `HDC Workflow Run Report`.
- [x] Console no longer uses hard-coded New Mexico/NMDOH/CDC success demo text.
- [x] Console summary includes task disease/location/time window.
- [x] Console summary includes accepted/pre-quality/quarantined/pending/post-review
      counts.
- [x] Markdown report distinguishes technical completion from accepted final
      dataset success.
- [x] Markdown report lists accepted final records from `final_dataset`, not all
      normalized records.
- [x] Validation source compatibility is visible in report/console outputs.
- [x] Source critic, disease relevance, and localized planning summaries are
      visible in the console.
- [x] Latest alias artifacts are regenerated by workflow runs.
- [x] Targeted and full tests pass.
- [x] Secret scan completed without real key leakage.

## 16. Git context

- Branch: `main`
- HEAD: `6d1faebebf643375e270106c8d91119662bb6578`
- Working tree contained earlier uncommitted project changes before this repair.
  This repair did not revert or rewrite those unrelated changes.
