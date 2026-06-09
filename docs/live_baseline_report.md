# Live Baseline Report

## 1. Environment snapshot

- Date/time: 2026-06-07, escalated live run generated at `2026-06-07T18:32:29.734779+00:00`.
- Git branch: `main`
- Git commit hash: `0a74ec8ca7f3ed9ab3b3f7af834de7421a2efb88`
- Python version: `Python 3.12.2`
- Operating system: `Windows-11-10.0.26100-SP0`
- Python executable: `D:\py\Python3\python.exe`
- Virtual environment active: `False`
- Network appears available: yes when the runner was re-executed with network permission; the first sandboxed attempt produced HTTP fetch failures and Anthropic `APIConnectionError`.
- API key environment variables:
  - `ANTHROPIC_API_KEY`: present
  - `OPENAI_API_KEY`: absent
- Relevant shell environment variables before config resolution:
  - `HDC_ENABLE_LIVE_FETCH`: absent
  - `HDC_ENABLE_LLM_EXTRACTION`: absent
  - `HDC_ENABLE_LLM_SOURCE_PLANNING`: absent
  - `HDC_ENABLE_LLM_SOURCE_CRITIC`: absent
  - `HDC_SOURCE_ID_ALLOWLIST`: absent
  - `HDC_LLM_MAX_CHUNKS`: absent
  - `HDC_LLM_PROVIDER`: present
  - `HDC_LLM_MODEL`: present
- Relevant resolved runtime-profile flags from `python scripts\run_hdc_workflow_configured.py --print-config`:
  - `HDC_ENABLE_LIVE_FETCH=true`
  - `HDC_ENABLE_LLM_EXTRACTION=true`
  - `HDC_ENABLE_LLM_SOURCE_PLANNING=true`
  - `HDC_ENABLE_LLM_SOURCE_CRITIC=true`
  - `HDC_SOURCE_ID_ALLOWLIST=src_nmdoh_hps_2024_first_case,src_nmdoh_hps_2025_first_case_death,src_nmdoh_hps_2026_first_case_prior_year_summary,src_nmdoh_hps_overview_1975_2025,src_cdc_hantavirus_reported_cases_through_2023,src_nmdoh_hps_cases_by_county_1975_2025_pdf`
  - `HDC_LLM_MAX_CHUNKS=8`
  - provider/model: `anthropic` / `claude-sonnet-4-6`

No API key values were printed.

## 2. Available run scripts

Current top-level scripts under `scripts/`:

- `build_workflow_run_console.py`
- `check_studio_app.py`
- `print_studio_initial_state.py`
- `run_hdc_workflow_configured.py`
- `start_hdc_workflow_studio.py`

Identified roles:

- Configured workflow runner: `scripts/run_hdc_workflow_configured.py`
- Current live-source LLM runner: `scripts/run_hdc_workflow_configured.py` using `configs/hdc_workflow_run_config.jsonc`
- Export/report runner: `scripts/build_workflow_run_console.py` and the report/export logic inside `scripts/run_hdc_workflow_configured.py`
- LangGraph Studio launcher: `scripts/start_hdc_workflow_studio.py`

The older `run_live_source_llm_pilot.py` exists only under `archive/legacy_demo_pilot_assets_2026_06_05/scripts/`, not in the current active `scripts/` directory.

## 3. Offline regression test

Command:

```powershell
python -m pytest -q
```

Result:

```text
206 passed in 4.89s
```

No failures were observed. Stage 0 made no runtime changes before this test.

## 4. Current configured live baseline attempt

The current repository's active live/configured runner is:

```powershell
python scripts\run_hdc_workflow_configured.py --session-id stage0_baseline_20260607_utc
```

First sandboxed attempt:

- Result: completed, but live fetch and LLM network calls failed.
- Output directory: `outputs/sessions/stage0_baseline_20260607_utc`
- Fetch status: 5 attempted documents, all `fetch_failed`
- LLM source planning: failed with `APIConnectionError`
- Normalized records: 0
- Human review items: 1

Because the failure mode indicated environment network restrictions, the same existing runner was re-executed with network permission:

```powershell
python scripts\run_hdc_workflow_configured.py --session-id stage0_baseline_20260607_utc_escalated
```

Escalated live baseline result:

- Output directory: `outputs/sessions/stage0_baseline_20260607_utc_escalated`
- Provider/model: `anthropic` / `claude-sonnet-4-6`
- API key: present
- Live fetch: enabled
- Fixture documents: disabled
- All three LLM stages enabled: true
- Trace node count: 17
- Current route: `finalize`
- Source registry count: 20
- Document count: 5
- Normalized record count: 9
- Evaluation row count: 8
- Human review item count: 8
- LLM source planning status: success
- LLM source critic assessed source count: 6
- LLM structured extraction call count: 7

## 5. Baseline output artifacts

Escalated run artifacts:

- Final package JSON: `outputs/sessions/stage0_baseline_20260607_utc_escalated/collection/final_package.json`
- Final dataset CSV: `outputs/sessions/stage0_baseline_20260607_utc_escalated/collection/final_dataset.csv`
- Source registry JSON: `outputs/sessions/stage0_baseline_20260607_utc_escalated/collection/source_registry.json`
- Linked events JSON: `outputs/sessions/stage0_baseline_20260607_utc_escalated/collection/linked_events.json`
- Conflicts JSON: `outputs/sessions/stage0_baseline_20260607_utc_escalated/collection/conflicts.json`
- Human review items JSON: `outputs/sessions/stage0_baseline_20260607_utc_escalated/collection/human_review_items.json`
- Collection trace JSON: `outputs/sessions/stage0_baseline_20260607_utc_escalated/collection/collection_trace.json`
- Workflow summaries JSON: `outputs/sessions/stage0_baseline_20260607_utc_escalated/collection/workflow_summaries.json`
- Package metadata JSON: `outputs/sessions/stage0_baseline_20260607_utc_escalated/collection/package_metadata.json`
- Provenance manifest JSON: `outputs/sessions/stage0_baseline_20260607_utc_escalated/collection/provenance_manifest.json`
- Validation ground truth CSV: `outputs/sessions/stage0_baseline_20260607_utc_escalated/validation/ground_truth_records.csv`
- Validation source registry JSON: `outputs/sessions/stage0_baseline_20260607_utc_escalated/validation/validation_source_registry.json`
- Evaluation report CSV: `outputs/sessions/stage0_baseline_20260607_utc_escalated/evaluation/evaluation_report.csv`
- Evaluation summary JSON: `outputs/sessions/stage0_baseline_20260607_utc_escalated/evaluation/evaluation_summary.json`
- Readable evaluation report: `outputs/sessions/stage0_baseline_20260607_utc_escalated/evaluation/readable_evaluation_report.md`
- Live fetch summary: `outputs/sessions/stage0_baseline_20260607_utc_escalated/diagnostics/live_fetch_summary.json`
- Source split summary: `outputs/sessions/stage0_baseline_20260607_utc_escalated/diagnostics/source_split_summary.json`
- LLM stage summary: `outputs/sessions/stage0_baseline_20260607_utc_escalated/diagnostics/llm_stage_summary.json`
- Human-readable run report: `outputs/sessions/stage0_baseline_20260607_utc_escalated/workflow_run_report_chinese.md`
- HTML workflow console: `outputs/sessions/stage0_baseline_20260607_utc_escalated/workflow_console/hdc_workflow_console.html`
- HTML console summary JSON: `outputs/sessions/stage0_baseline_20260607_utc_escalated/workflow_console/hdc_workflow_console_summary.json`

Latest aliases were also updated under:

- `outputs/workflow_runs/latest_workflow_run_report_chinese.md`
- `outputs/workflow_runs/latest_workflow_run_summary.json`
- `outputs/workflow_console/hdc_workflow_console.html`

## 6. Baseline real-source summary

Escalated live baseline:

- Source candidates: 21
- Source registry entries after deduplication: 20
- Sources selected/requested for fetch: 5
- Real URLs fetched: 5
- Successful fetches: 5
- Fetch failures: 0
- Parse-deferred PDFs: 0
- Usable documents: 5
- Evidence chunks: 16
- Target-data chunks: 7
- Context-only chunks: 9
- Extracted raw records: 9
- Validated records: 9
- Normalized records: 9
- Linked events: 8
- Conflicts: 0
- Evaluation rows: 8
- Human review items: 8

Fetched public source IDs and URLs:

- `src_nmdoh_hps_2024_first_case`: `https://www.nmhealth.org/news/safety/2024/2?view=2065`
- `src_nmdoh_hps_2025_first_case_death`: `https://www.nmhealth.org/news/awareness/2025/3?view=2189`
- `src_nmdoh_hps_2026_first_case_prior_year_summary`: `https://www.nmhealth.org/news/safety/2026/3?view=2322`
- `src_nmdoh_hps_overview_1975_2025`: `https://www.nmhealth.org/about/erd/ideb/zdp/hps`
- `src_cdc_hantavirus_reported_cases_through_2023`: `https://www.cdc.gov/hantavirus/data-research/cases/index.html`

Validation-reserved sources skipped from collection fetch included:

- `src_nmdoh_hps_cases_by_county_1975_2025_pdf`
- `src_who_hantavirus_fact_sheet`
- `src_ecdc_surveillance_updates`
- `src_ecdc_annual_report_2023`

## 7. Current limitations observed from live baseline

- Source discovery still used `offline_seed_catalog`; it did not perform broad real web search.
- LLM source planning succeeded and generated 8 proposed queries, but those queries were advisory and did not execute a search provider.
- Source fetch remained constrained to a fixed `HDC_SOURCE_ID_ALLOWLIST`.
- The disease input was effectively hantavirus/New Mexico-specific through the config and static resources.
- Search queries did not drive new source discovery in this run.
- Validation used a held-out ground truth CSV and source-role split, but it is not yet a generic graph-native validation subsystem.
- Evaluation produced 8 rows; 7 were `missing_validation_record` and 1 was `partial_match_not_comparable`.
- All 8 evaluation rows were flagged for human review.
- The output artifacts are auditable, but many outputs are still CSV/JSON/report artifacts rather than an integrated public-health user interface.
- Human review decisions were not applied to modify final data.
- `package_metadata.web_search_used` was `false`, which confirms that current live capability is real fetch from registered sources, not real source discovery.

## 8. Stage 0 live acceptance status

PASSED: offline tests passed and at least one real live-web baseline run completed with real source fetches and auditable outputs.

Important qualification: this is a baseline pass for the current scoped implementation. It does not mean the final data collection workflow target is already implemented. The baseline still uses fixed catalog discovery, a New Mexico HPS profile, allowlisted live fetching, and manually curated validation records.
