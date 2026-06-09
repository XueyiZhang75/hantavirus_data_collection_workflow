# Post-Acceptance Repair 2 Report

## Repair Goal

Integrate the LLM source critic into live-search-derived source routing and enforce critic-driven fetch blocking inside the data collection workflow.

This repair does not rename the project, does not change graph topology, and does not implement validation ground-truth repair, multilingual official-source planning, final-dataset redesign, or UI/CLI redesign.

## Summary of Changes

- Repaired source critic candidate selection so live-search-derived candidates are prioritized before seed catalog entries.
- Repaired source critic allowlist semantics: empty allowlist now means no explicit critic allowlist, not fallback to New Mexico seed IDs.
- Added source-level critic audit fields to `SourceRegistryEntry`.
- Added critic decision normalization for common model aliases such as `exclude` -> `not_task_relevant`.
- Added critic risk-to-routing policy that can block content fetch before the fetch node.
- Added `source_critic_blocked_source` human review items when critic blocks a source.
- Added `source_critic_results` workflow state output.
- Added standalone diagnostics exports:
  - `diagnostics/source_critic_summary.json`
  - `diagnostics/source_critic_results.json`
- Updated the source critic prompt to prohibit browsing/searching and to avoid treating search queries as source-content evidence.
- Updated readable report and console summary visibility for source critic blocked/allowed/review counts.
- Added bounded live smoke config for source critic verification.

## Files Changed

Repair 2 files:

- `configs/hdc_workflow_run_config.jsonc`
- `configs/examples/repair2_live_source_critic_smoke.jsonc`
- `docs/source_critic_live_integration.md`
- `docs/stage_reports/POST_ACCEPTANCE_REPAIR_2_REPORT.md`
- `scripts/build_workflow_run_console.py`
- `scripts/run_hdc_workflow_configured.py`
- `src/hdc_workflow/agents/source_critic_agent.py`
- `src/hdc_workflow/models.py`
- `src/hdc_workflow/nodes/source_screening.py`
- `src/hdc_workflow/resources/source_critic_agent_prompt.json`
- `src/hdc_workflow/runtime_profile.py`
- `src/hdc_workflow/state.py`
- `tests/test_source_critic_live_integration.py`

Repair 1 files remain present in the same working tree and were not reverted.

## New/Updated Tests

- Added `tests/test_source_critic_live_integration.py`
- Coverage includes:
  - empty critic allowlist means no explicit allowlist
  - explicit non-empty critic allowlist is respected
  - live-search candidates are prioritized over seed sources
  - critic disease mismatch blocks fetch and creates review
  - no-extractable-data/context-only critic outcome blocks collection fetch
  - relevant official source remains fetchable
  - critic failure does not crash workflow
  - disabled critic does not call LLM
  - source critic fields persist into final package registry
  - Shanghai-like COVID source regression
  - runtime config no longer falls back critic allowlist to workflow IDs
  - critic decision alias normalization

## Commands Run

- `python -m pytest tests\test_source_critic_live_integration.py -q`
- `python -m pytest tests\test_disease_relevance_gating.py -q`
- `python -m pytest tests\test_real_source_discovery.py tests\test_source_credibility_scoring.py tests\test_source_critic_live_integration.py -q`
- `python -m pytest -q`
- `python scripts\run_hdc_workflow_configured.py --config configs\hdc_workflow_run_config.jsonc --disable-all-llm --session-id repair2_hantavirus_new_mexico_compat_no_llm`
- `python -c "import sys; sys.path.insert(0, r'src'); from hdc_workflow.cli import main; raise SystemExit(main(['validate-config', '--config', r'configs\\hdc_workflow_run_config.jsonc']))"`
- `python scripts\run_hdc_workflow_configured.py --config configs\examples\repair2_live_source_critic_smoke.jsonc --session-id repair2_live_source_critic_smoke`
- `rg -n "sk-ant-[A-Za-z0-9_-]{20,}|tvly-[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{35}" .`

## Test Results

- Initial targeted Repair 2 tests failed before implementation, as expected.
- Final targeted Repair 2 tests: `13 passed`
- Repair 1 disease relevance regression tests: `9 passed`
- Source-related regression tests: `40 passed`
- Full suite: `383 passed`
- Strict secret scan: no matches

## Example Runs

### Offline compatibility run

Command:

```powershell
python scripts\run_hdc_workflow_configured.py --config configs\hdc_workflow_run_config.jsonc --disable-all-llm --session-id repair2_hantavirus_new_mexico_compat_no_llm
```

Key result:

- `trace_node_count: 20`
- `document_count: 5`
- `normalized_record_count: 5`
- `llm_source_critic_assessed_source_count: 0`
- New diagnostics were exported:
  - `outputs/sessions/repair2_hantavirus_new_mexico_compat_no_llm/diagnostics/source_critic_summary.json`
  - `outputs/sessions/repair2_hantavirus_new_mexico_compat_no_llm/diagnostics/source_critic_results.json`

### Controlled live source critic smoke

Command:

```powershell
python scripts\run_hdc_workflow_configured.py --config configs\examples\repair2_live_source_critic_smoke.jsonc --session-id repair2_live_source_critic_smoke
```

Key result:

- `source_search_mode: live`
- `source_search_executed_query_count: 1`
- `search_derived_candidate_count: 3`
- `llm_source_critic_assessed_source_count: 2`
- `blocked_fetch_count: 2`
- `decision_counts: {"not_task_relevant": 2}`
- `fetch_recommendation_counts: {"block_fetch": 2}`
- content fetch skipped the two blocked sources with `final_role_excluded: 2`

## Output Artifacts Created

- `outputs/sessions/repair2_hantavirus_new_mexico_compat_no_llm/`
- `outputs/sessions/repair2_live_source_critic_smoke/`
- `outputs/sessions/repair2_live_source_critic_smoke/diagnostics/source_critic_summary.json`
- `outputs/sessions/repair2_live_source_critic_smoke/diagnostics/source_critic_results.json`
- `outputs/sessions/repair2_live_source_critic_smoke/workflow_run_report_chinese.md`
- `outputs/sessions/repair2_live_source_critic_smoke/workflow_console/hdc_workflow_console.html`

## Known Limitations

- The source critic still reviews metadata only; it does not inspect page content before fetch.
- If `max_sources` is smaller than the number of live candidates, unassessed candidates can still pass through deterministic routing and fetch policy.
- The live smoke depends on Tavily and Anthropic availability and can produce different search candidates over time.
- The current UI/HTML console exposes counts but is not a full interactive source-review workspace.

## Future-Stage Items Not Implemented

- Validation ground-truth compatibility repair
- Multilingual official-source planning
- New search provider or search ingestion algorithm
- Full source discovery redesign
- Final dataset quality redesign
- Dynamic HTML/report cleanup beyond minimal source critic visibility
- New graph topology
- New CLI/UI interaction model
- Duplicate/anomaly/human-review semantic redesign

## Review Checklist

- [x] Project name remains `data collection workflow`
- [x] Internal package name remains `hdc_workflow`
- [x] No graph topology change
- [x] Default offline deterministic tests pass
- [x] No real API keys printed or committed
- [x] Source critic decisions are auditable per source
- [x] Critic-blocked sources are blocked before content fetch
- [x] Human review queue receives critic-blocked source items
- [x] Diagnostics include source critic summary and per-source results
- [x] Repair 3 and future-stage items were not implemented
