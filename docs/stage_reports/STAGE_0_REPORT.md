# Stage 0 Report: Project Target Lock + Current Repository Audit + Live Baseline

## 1. Stage goal

Stage 0 locked the final target for the data collection workflow, audited the current repository state, identified current hantavirus/New Mexico/fixed-catalog assumptions, and verified the current offline and live baseline without implementing new runtime behavior.

## 2. Summary of actions completed

- Documented the final disease-generic public-health data collection workflow target.
- Audited the current repository structure and implemented capabilities.
- Identified current hantavirus-specific assumptions.
- Identified current fixed-catalog and non-searching assumptions.
- Documented current live-web and LLM capabilities.
- Documented current validation, UX, and visualization limitations.
- Ran the offline regression suite.
- Attempted a current configured live baseline run.
- Re-ran the live baseline with network permission after the first sandboxed attempt showed connection failures.
- Documented live baseline artifacts and results.

## 3. Files created or modified

Created:

- `docs/final_product_target.md`
- `docs/current_state_audit.md`
- `docs/live_baseline_report.md`
- `docs/stage_reports/STAGE_0_REPORT.md`

Modified:

- `README.md` with a minimal Stage 0 scope note and links.

Runtime outputs created by the existing runner:

- `outputs/sessions/stage0_baseline_20260607_utc/`
- `outputs/sessions/stage0_baseline_20260607_utc_escalated/`
- latest aliases under `outputs/workflow_runs/` and `outputs/workflow_console/`

## 4. Functional changes

No functional runtime changes were made.

No graph topology, Python package imports, node logic, model behavior, LLM behavior, fetch behavior, validation behavior, or runtime configuration behavior was changed.

## 5. Current-state findings

- Current hantavirus-specific assumptions: task intake, profile/schema setup, resource loading, `HantavirusRecord`, extraction guardrails, seed sources, New Mexico HPS runtime config, and tests remain hantavirus/New Mexico/HPS-specific.
- Current fixed-catalog assumptions: `source_discovery` uses `offline_seed_catalog`; LLM source planning is advisory-only; live fetch uses source ID allowlists; current case-study overlays are hand curated.
- Current LLM planning limitations: LLM source planning can propose queries and candidate hints, but cannot execute search or add fetched search results as new sources.
- Current live-web capability: real HTML/text fetch works when `HDC_ENABLE_LIVE_FETCH=true` and network is available; PDF parsing remains deferred.
- Current validation limitations: validation uses in-graph cross-source consistency plus configured held-out CSV evaluation, but not a general trusted-source validation subsystem; LLM validation is not implemented.
- Current output/UX limitations: configured scripts and generated Markdown/HTML reports exist, but the user experience is still script/config/report oriented.

## 6. Live baseline summary

Offline tests passed.

The first sandboxed live baseline completed but failed all live HTTP fetches and failed Anthropic source planning with connection errors. This was treated as an environment/network restriction signal, not as a final product baseline result.

The escalated live baseline completed successfully:

- Command: `python scripts\run_hdc_workflow_configured.py --session-id stage0_baseline_20260607_utc_escalated`
- Output directory: `outputs/sessions/stage0_baseline_20260607_utc_escalated`
- Provider/model: `anthropic` / `claude-sonnet-4-6`
- Source registry entries: 20
- Documents fetched: 5
- Successful fetches: 5
- Usable documents: 5
- Evidence chunks: 16
- Target-data chunks: 7
- LLM source planning: success
- LLM source critic assessed sources: 6
- LLM structured extraction calls: 7
- Raw/validated/normalized records: 9 / 9 / 9
- Linked events: 8
- Conflicts: 0
- Evaluation rows: 8
- Human review items: 8

Stage 0 live acceptance status: PASSED for the current scoped baseline, with the qualification that broad real source discovery and disease-generic operation are not yet implemented.

## 7. Tests and commands run

Repository status:

```powershell
git status --short
git branch --show-current
git rev-parse HEAD
```

File inventory:

```powershell
rg --files
```

Hard-code audit:

```powershell
rg -n "Hantavirus|hantavirus|HPS|New Mexico|new_mexico|load_hantavirus|HantavirusRecord|hantavirus_profile_and_schema_setup" README.md configs src scripts tests docs
```

Fixed-catalog / no-search audit:

```powershell
rg -n "offline_seed_catalog|seed catalog|no network|Do not perform broad web search|fixed|allowlist|SOURCE_ID_ALLOWLIST|validation_reserved|source_role_policy_overlay" README.md configs src scripts tests docs
```

Live script audit:

```powershell
Get-ChildItem -Force scripts | Format-Table Mode,Length,Name -AutoSize
rg -n "LIVE|live|HDC_ENABLE_LIVE_FETCH|HDC_ENABLE_LLM_EXTRACTION|run_live" scripts src configs README.md
```

Environment/config:

```powershell
python --version
python -c "import platform, sys, os; print('platform=' + platform.platform()); print('executable=' + sys.executable); print('venv_active=' + str(bool(os.environ.get('VIRTUAL_ENV'))));"
python scripts\run_hdc_workflow_configured.py --print-config
```

Offline test:

```powershell
python -m pytest -q
```

Live baseline:

```powershell
python scripts\run_hdc_workflow_configured.py --session-id stage0_baseline_20260607_utc
python scripts\run_hdc_workflow_configured.py --session-id stage0_baseline_20260607_utc_escalated
```

Artifact inspection:

```powershell
Get-Content -Raw outputs\sessions\stage0_baseline_20260607_utc_escalated\workflow_run_summary.json
Get-Content -Raw outputs\sessions\stage0_baseline_20260607_utc_escalated\diagnostics\live_fetch_summary.json
Get-Content -Raw outputs\sessions\stage0_baseline_20260607_utc_escalated\diagnostics\llm_stage_summary.json
Get-Content -Raw outputs\sessions\stage0_baseline_20260607_utc_escalated\evaluation\evaluation_summary.json
Get-Content -Raw outputs\sessions\stage0_baseline_20260607_utc_escalated\collection\workflow_summaries.json
```

## 8. Test results

Offline regression:

```text
206 passed in 4.89s
```

Live baseline:

- Sandboxed attempt: completed but live network/API calls failed.
- Escalated attempt: completed with successful live fetches, LLM planning, LLM source critic, LLM extraction, exported artifacts, and generated HTML console.

## 9. Known limitations

- The current active workflow remains hantavirus/New Mexico/HPS-specific.
- Source discovery is still an offline seed catalog, not broad live source discovery.
- LLM source planning is advisory and does not execute search.
- Configured source sets and validation sets are fixed by profile.
- PDF parsing/OCR is not implemented.
- Validation is not yet a generic graph-native trusted-source validation layer.
- Duplicate detection is event-key linking, not full duplicate/event clustering.
- Anomaly detection is not implemented.
- Human review decisions do not modify final records/conflicts.
- The user experience remains script/config/report oriented.

## 10. Future-stage items explicitly NOT implemented

- Disease generalization
- Disease intelligence layer
- Executable source planning
- Real search provider
- Source credibility scoring
- Validation refactor
- Duplicate clustering improvements
- Anomaly detection
- Human review decision application
- CLI/notebook/product UI

## 11. Review checklist

- [x] User-facing name is "data collection workflow"
- [x] No new project name was invented
- [x] Hantavirus is documented as current case study/default implementation, not final product boundary
- [x] Final target is documented as disease-generic
- [x] Final target requires LLM-driven source planning
- [x] Final target requires real source discovery beyond fixed catalogs
- [x] Fixed catalogs are documented as seeds/fallbacks/guardrails only
- [x] Current hard-coded disease assumptions are audited
- [x] Current fixed-catalog assumptions are audited
- [x] Current live baseline was attempted
- [x] Live baseline result is honestly marked PASSED/PARTIAL/FAILED
- [x] Offline tests were run
- [x] No API keys or secrets were printed
- [x] No functional runtime changes were made
- [x] No future-stage features were implemented

Ready to move to Stage 1: yes, after review of the Stage 0 target/audit documents.
