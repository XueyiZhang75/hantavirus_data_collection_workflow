# data collection workflow User Guide

This guide explains how to operate the **data collection workflow** from the
command line, how to keep runs deterministic by default, how to enable optional
live search or LLM stages, and how to inspect the output artifacts.

## 1. What This Workflow Does

The workflow takes a structured public-health collection task, discovers or
loads candidate sources, screens and routes sources, fetches eligible content,
chunks evidence, extracts records, normalizes records, links related records
into events, compares collection records against reserved validation sources,
detects anomalies, routes uncertain items to human review, and exports an
auditable final package.

The current case-study source set is Hantavirus / New Mexico. The same workflow
also supports disease-generic structured tasks and deterministic fixture runs
for COVID-19 / New York and dengue / Florida.

## 2. Normal user path: interactive real workflow

For a normal user run, start from the interactive script. It asks for the task
inputs and then runs the full real workflow with live search, live fetch, and
LLM stages enabled by default.

The interactive and visual entrypoints default to `direct_collection`. This is
the normal data-collection path: official public-health sources, task coverage,
and task-compatible surveillance or aggregate records are prioritized for
`collection/final_dataset.*`. The older full-audit behavior remains available
from the interactive script with `--audit-mode`.

```powershell
cd "C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow"
$env:PYTHONPATH = "src"
$env:TAVILY_API_KEY = [Environment]::GetEnvironmentVariable("TAVILY_API_KEY", "User")
$env:ANTHROPIC_API_KEY = [Environment]::GetEnvironmentVariable("ANTHROPIC_API_KEY", "User")
python scripts\run_interactive_workflow.py
```

The script prompts for:

- disease / virus
- location
- start year/date
- end year/date
- session id, with an auto-generated default

Record fields are fixed by the workflow schema. Normal users do not choose
columns during the interactive run; the workflow always extracts the maintained
standard record fields for cases, deaths, dates, locations, source URLs, source
types, and evidence quotes.

Example direct run without prompts:

```powershell
python scripts\run_interactive_workflow.py --disease "hantavirus" --location "New Mexico" --start-date 2020 --end-date 2026 --session-id hantavirus_nm_real
```

Default behavior for this entrypoint:

- live Tavily source search enabled
- live page fetch enabled
- search-derived source fetch enabled
- fixture documents disabled
- LLM source planning, source critic, source credibility, disease intelligence,
  and structured extraction enabled
- API keys read from environment variables
- missing API keys stop the run instead of falling back to fixture data
- session report, workflow console, JSON, and CSV artifacts are exported
- `direct_collection` is the default result mode; audit validation and human
  review diagnostics are written but do not block the primary final dataset

Use `--print-config-only` to preview the generated config without running live
search, live fetch, or LLM calls:

```powershell
python scripts\run_interactive_workflow.py --disease "COVID-19" --location "New York" --start-date 2024 --end-date 2024 --session-id covid19_ny_preview --print-config-only
```

## 3. Installation and CLI commands for developers

The lower-level CLI remains available for validation, fixture tests, inspecting
sessions, review summaries, exports, and generated config templates. Install the
package in editable mode once:

```powershell
python -m pip install -e .
python -m hdc_workflow.cli --help
```

If installed as a package, the console script is:

```powershell
data-collection-workflow --help
```

For a temporary source-tree run without installation:

```powershell
$env:PYTHONPATH = "src"
python -m hdc_workflow.cli --help
```

The CLI exposes:

- `collect`: run the workflow from a config file.
- `validate-config`: check a config before a run.
- `inspect-run`: summarize a completed session.
- `review-summary`: summarize review items and applied decisions.
- `export`: export readable JSON/CSV artifacts from a session.
- `init-config`: generate a safe starter config.

## 4. Config-First Operation

Config-first operation is now mainly for development, repeatable acceptance
checks, and advanced users. The workflow is controlled by JSON/JSONC config
files. The default compatibility config is:

```text
configs/hdc_workflow_run_config.jsonc
```

The CLI reads the config first, then applies any explicit one-run CLI
overrides. This keeps normal operation reproducible while still allowing quick
smoke tests.

Useful preview commands:

```powershell
python -m hdc_workflow.cli validate-config --config configs/examples/covid19_new_york_2024_fixture_review_application_task.jsonc
python -m hdc_workflow.cli collect --config configs/examples/covid19_new_york_2024_fixture_review_application_task.jsonc --print-config-only
python -m hdc_workflow.cli collect --config configs/examples/covid19_new_york_2024_fixture_review_application_task.jsonc --dry-run
```

`--print-config-only` and `--dry-run` do not invoke the graph.

## 5. Running offline fixture examples

Offline fixture examples are deterministic and do not require internet access,
`TAVILY_API_KEY`, `ANTHROPIC_API_KEY`, or `OPENAI_API_KEY`. They are for
development and testing, not the default user path.

COVID-19 / New York:

```powershell
python -m hdc_workflow.cli collect --config configs/examples/covid19_new_york_2024_fixture_review_application_task.jsonc --session-id guide_covid19_fixture --disable-all-llm
```

dengue / Florida:

```powershell
python -m hdc_workflow.cli collect --config configs/examples/dengue_florida_2025_fixture_review_application_task.jsonc --session-id guide_dengue_fixture --disable-all-llm
```

Each run writes to:

```text
outputs/sessions/<session_id>/
```

## 6. Running live search examples

Live search is optional and searches metadata through a configured search
provider. The current live provider adapter is Tavily.

Set the key in the shell or user environment. Do not store it in a config file:

```powershell
$env:TAVILY_API_KEY = [Environment]::GetEnvironmentVariable("TAVILY_API_KEY", "User")
```

Then validate and run a bounded live-search smoke config:

```powershell
python -m hdc_workflow.cli validate-config --config configs/examples/covid19_new_york_2024_live_review_smoke.jsonc
python -m hdc_workflow.cli collect --config configs/examples/covid19_new_york_2024_live_review_smoke.jsonc --session-id guide_covid19_live_search --disable-all-llm
```

Live search returns source metadata. Fetching page bodies is controlled
separately by the config field `live_web.enabled` and the content-fetch
settings.

## 7. Environment variables and optional LLM stages

LLM stages are opt-in. The workflow can use the configured model for source
planning, source critic, source credibility, and structured extraction when
those stages are enabled.

For Anthropic:

```powershell
$env:ANTHROPIC_API_KEY = [Environment]::GetEnvironmentVariable("ANTHROPIC_API_KEY", "User")
python -m hdc_workflow.cli collect --config configs/hdc_workflow_run_config.jsonc --provider anthropic --model claude-sonnet-4-6
```

For OpenAI:

```powershell
$env:OPENAI_API_KEY = [Environment]::GetEnvironmentVariable("OPENAI_API_KEY", "User")
python -m hdc_workflow.cli collect --config configs/hdc_workflow_run_config.jsonc --provider openai --model gpt-4.1
```

The CLI reports only whether a key is present. It does not print key values.

## 8. Human review decision files

Human review items are generated during the run. A decision file can be supplied
when the operator wants to apply explicit decisions in an auditable way:

```powershell
python -m hdc_workflow.cli collect --config configs/examples/dengue_florida_2025_fixture_review_application_task.jsonc --human-review-decisions-path src/hdc_workflow/resources/human_review_decision_fixtures/dengue_review_decisions.json --apply-review-decisions --session-id guide_dengue_review
```

Decision application writes applied decisions, rejected decisions, and an audit
trail. It does not silently overwrite source evidence.

## 9. Workflow console

Every configured run can automatically build an HTML workflow console:

```text
outputs/sessions/<session_id>/workflow_console/hdc_workflow_console.html
```

The console is a readable inspection view over a completed run. It shows node
trace, source registry, fetch/parse summaries, evidence chunks, extracted
records, validation results, anomaly results, and human-review status.

The runner also writes live runtime event files while the graph is executing:

```text
outputs/sessions/<session_id>/diagnostics/run_events.ndjson
outputs/sessions/<session_id>/diagnostics/run_status.json
outputs/sessions/<session_id>/diagnostics/node_status.json
```

`--live-status` is enabled by default and shows a Rich terminal panel when the
terminal supports it. Use `--no-live-status` to disable the terminal panel while
still writing the event files.

For an optional browser dashboard:

```powershell
python -m pip install -e .[visualization]
streamlit run scripts/live_workflow_dashboard.py -- --session-dir outputs/sessions/<session_id>
```

For a local visual workflow entrypoint, use the optional Langflow visual demo:

```powershell
python -m pip install -e .[langflow-demo]
python scripts\start_langflow_demo.py
```

This starts only the local HDC demo API and Langflow. The existing HDC
LangGraph workflow still performs source discovery, fetching, extraction,
validation, human-review routing, and final package export, while Langflow is
the primary visual interface for running and inspecting it.

The startup script waits for both local services to be ready, auto-imports the
bundled flow, and opens the flow page. If auto-import fails, import:

```text
integrations/langflow/flows/hdc_deep_visual_demo_flow.json
```

Use `HDC Workflow Runner` for the free-text `User Request` plus disease,
location, date range, provider, and model, but start the visual demo by
pressing Play on `HDC Final Results - Run Full Workflow`. That final node builds
the whole Langflow chain once. Each `HDC Workflow Node Inspector` waits for its
matching real workflow node to complete before returning, then exposes real
status, real duration, input/output summaries, recent events, tool summary, LLM
summary, artifact URLs, and optional trace links. The node Message output is a
readable detail report. Langflow card timing is component build timing; use
Node Details and the Final Timeline for real HDC workflow timing.

For the primary interactive visual path:

```powershell
python scripts\run_visual_workflow.py
```

This prompts for disease, location, exact dates such as `2024-5-1` to
`2024-5-3`, session id, and user request. It opens a newly imported,
session-specific prefilled Langflow flow; use that newly opened URL instead of
older Langflow tabs, then press Play on `HDC Final Results - Run Full Workflow`
to start and watch the real workflow chain. Dates are normalized to ISO dates before the run is submitted. Add
`--quick-test-mode` for fast smoke tests with lower search, fetch, and LLM
budgets while leaving normal full-run defaults unchanged.

### Deep visual demo

For optional LangSmith/LangGraph Studio tracing, start the local demo API,
Langflow, Studio, and LangSmith tracing together:

```powershell
python -m pip install -e .[langflow-deep-demo]
$env:LANGSMITH_API_KEY = [Environment]::GetEnvironmentVariable("LANGSMITH_API_KEY", "User")
python scripts\start_langflow_deep_demo.py
```

This mode requires `LANGSMITH_API_KEY`. It sets `LANGSMITH_TRACING=true`,
defaults `LANGSMITH_PROJECT` to `hdc-workflow-demo`, and sets
`LANGCHAIN_CALLBACKS_BACKGROUND=false` so traces are flushed before the workflow
process exits. If your LangSmith account needs a workspace or regional endpoint,
set `LANGSMITH_WORKSPACE_ID` or `LANGSMITH_ENDPOINT` in the shell before
starting the script.

This is optional for cloud trace/debug work. The normal Langflow visual demo
does not require LangSmith. In the deep mode, use:

- `HDC Final Results - Run Full Workflow` to build the whole visual chain once.
- `HDC Workflow Runner` to create or reuse the backend HDC LangGraph workflow.
- `HDC Workflow Node Inspector` components to mirror each workflow node and
  query node status, payload summaries, tool summaries, LLM summaries, and trace
  links for the active `session_id`.
- `HDC Final Results - Run Full Workflow` to open optional Studio/LangSmith trace links plus the
  workflow console, workflow visualization, reports, and exported datasets.

The bundled Langflow blueprint is:

```text
integrations/langflow/flows/hdc_deep_visual_demo_flow.json
```

LangGraph Studio shows the real graph structure and reproducible graph entry
point. LangSmith stores the deep trace. Full debug tracing can include prompts,
LLM responses, source snippets, search/fetch summaries, and tool span
summaries, so use this mode only for data you are comfortable sending to
LangSmith.

For a replay notebook suitable for research review or supplementary material,
add `--write-run-notebook` to the configured or interactive run. The notebook is
written to:

```text
outputs/sessions/<session_id>/workflow_replay_notebook.ipynb
```

## 10. Inspecting, reviewing, and exporting runs

After a run:

```powershell
python -m hdc_workflow.cli inspect-run --session-dir outputs/sessions/guide_covid19_fixture
python -m hdc_workflow.cli review-summary --session-dir outputs/sessions/guide_covid19_fixture
```

Use this before opening individual JSON/CSV files. It gives counts and paths for
the main artifacts.

## 11. Exporting Artifacts

To export readable JSON and CSV files:

```powershell
python -m hdc_workflow.cli export --session-dir outputs/sessions/guide_covid19_fixture --output-dir outputs/exports/guide_covid19_fixture --format both
```

The exported folder includes final dataset files, post-review dataset files,
source registry, validation results, anomaly results, human review audit files,
and a copy of the workflow console when present.

## 12. Output artifacts

Important session files:

- `workflow_run_report_chinese.md`: readable run report.
- `workflow_run_summary.json`: machine-readable run summary.
- `applied_workflow_config.json`: sanitized config used by the CLI run.
- `collection/final_package.json`: complete auditable final package.
- `collection/final_dataset.csv`: final dataset before review application.
- `collection/final_dataset_post_review.json`: final dataset after applied review decisions.
- `diagnostics/source_search_execution_summary.json`: search execution summary.
- `diagnostics/run_events.ndjson`: append-only live runtime event stream.
- `diagnostics/run_status.json`: compact latest run status.
- `diagnostics/node_status.json`: compact latest per-node status.
- `diagnostics/live_fetch_summary.json`: fetch and parse summary.
- `diagnostics/llm_stage_summary.json`: LLM stage status and call counts.
- `diagnostics/disease_relevance_summary.json`: source, document, chunk, and record disease-match guardrail summary.
- `diagnostics/validation_source_compatibility_summary.json`: held-out validation source compatibility status for this task.
- `validation/ground_truth_records.csv`: active held-out validation records used by this run.
- `validation/inactive_validation_records.csv`: loaded validation records disabled because they do not match this task.
- `diagnostics/anomaly_results.json`: anomaly review candidates.
- `diagnostics/human_review_audit_trail.json`: review decision audit trail.
- `workflow_replay_notebook.ipynb`: optional replay notebook when `--write-run-notebook` is used.
- `workflow_console/hdc_workflow_console.html`: visual run console.

## 13. Safety and limitations

The workflow is a data collection and evidence organization tool. It is not
medical advice, not a source of clinical guidance, and not a replacement for
official public-health reporting.

Current limitations:

- Default tests remain offline and deterministic.
- Live search requires an external search provider key.
- Live page fetch can fail because of site availability, robots policies,
  content changes, PDF parsing limits, or network conditions.
- LLM stages can fail, return incomplete data, or require human review.
- Human review decisions are explicit audit artifacts, not hidden edits.
- The workflow does not bypass paywalls, solve captchas, or run OCR.

## 14. Troubleshooting

- If `python -m hdc_workflow.cli` cannot import the package, run
  `python -m pip install -e .` once or set `$env:PYTHONPATH = "src"` from the
  repository root.
- If `python scripts\run_interactive_workflow.py` reports a missing key, set
  `TAVILY_API_KEY` and the configured LLM provider key in the shell or user
  environment. This interactive real-run entrypoint intentionally does not
  fall back to fixture data.
- If live search returns no results, verify that `TAVILY_API_KEY` is present in
  the shell, the config enables live search, and the query limits are not set to
  zero. The CLI reports key presence without printing the key value.
- If live fetch produces zero usable documents, inspect
  `diagnostics/live_fetch_summary.json` for HTTP status, quality status, parser
  status, and skipped-source reasons.
- If LLM stages do not run, confirm the provider/model settings and the relevant
  stage switches. API keys must be set through environment variables, not config
  files.
- If final records are routed to review, use `review-summary` first, then apply
  an explicit human review decision file only when the decision can be audited.

## 15. Creating a New Config

Generate a starter config:

```powershell
python -m hdc_workflow.cli init-config --disease dengue --location Florida --start-date 2025 --end-date 2025 --target-field cases_unspecified --target-field deaths --mode fixture-search --output configs/local_dengue_fixture.jsonc
```

Validate it:

```powershell
python -m hdc_workflow.cli validate-config --config configs/local_dengue_fixture.jsonc
```

Run it:

```powershell
python -m hdc_workflow.cli collect --config configs/local_dengue_fixture.jsonc --session-id local_dengue_fixture --disable-all-llm
```
