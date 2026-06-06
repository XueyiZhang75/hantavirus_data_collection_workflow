# HDC Workflow Technical Workshop Runbook

## Workshop Goal

Show a real HDC workflow run:

1. Open one workflow runtime profile.
2. Confirm API key presence without printing the key.
3. Start LangGraph Studio from that config.
4. Enter or submit the configured user request.
5. Inspect node execution in Studio.
6. Confirm collection, validation, and context source separation.
7. Confirm source planning, source critic, and structured extraction all call the configured LLM.
8. Export a human-readable run report.

## Workflow Runtime Profile

```text
configs/hdc_workflow_run_config.jsonc
```

This file controls:

| Setting | Config field |
|---|---|
| Graph | `workflow.graph_name` |
| Collection mode | `workflow.collection_mode` |
| Source overlay | `workflow.seed_source_overlay_path` |
| Source role policy | `workflow.source_role_policy_overlay_path` |
| Validation evidence | `workflow.validation_ground_truth_records_path` |
| User task | `user_request` |
| Live webpage fetch | `live_web.enabled` |
| Fetch timeout | `live_web.timeout_seconds` |
| Provider/model | `llm.provider`, `llm.model` |
| LLM source planning | `llm.source_planning_enabled` |
| LLM source critic | `llm.source_critic_enabled` |
| LLM structured extraction | `llm.structured_extraction_enabled` |
| Collection sources | `source_sets.collection_source_ids` |
| Validation sources | `source_sets.validation_reserved_source_ids` |
| Context sources | `source_sets.context_source_ids` |
| Output root | `output.run_output_root` |
| Session output | `output.sessionized` / `output.session_id` |
| Auto console export | `output.auto_build_console` |

## API Setup

```powershell
$env:ANTHROPIC_API_KEY = [Environment]::GetEnvironmentVariable("ANTHROPIC_API_KEY", "User")
```

Check key presence only:

```powershell
[bool]$env:ANTHROPIC_API_KEY
```

## Preview Config

```powershell
python scripts/start_hdc_workflow_studio.py --print-config-only
```

This prints the config path, sanitized workflow environment, provider/model, API key presence, and the minimal Studio input.

## Start Studio

```powershell
python scripts/start_hdc_workflow_studio.py
```

Use graph:

```text
hantavirus_data_collection_workflow
```

## Studio Input

Minimal input:

```json
{
  "user_request": "Collect data on hantavirus from 2020 to 2026. For this workflow run, use the New Mexico HPS source set, keep collection sources and validation sources separated, extract cases, deaths, dates, locations, source URLs, source types, and evidence quotes, then route uncertain results to human review."
}
```

To print it:

```powershell
python scripts/print_studio_initial_state.py --minimal
```

## Studio Inspection

Execution is mostly serial. Each node writes structured state for the next node. The conditional branch happens after `quality_gate_routing`.

| Node | What to inspect |
|---|---|
| `task_intake_and_scope_planning` | `collection_spec`, parsed disease/time/geography |
| `query_strategy_builder` | `source_planning_agent_summary`, `agentic_source_plan` |
| `source_critic_and_uncertainty_routing` | `source_critic_summary`, source roles, leakage flags |
| `content_fetch_and_parse` | live webpage fetch status |
| `structured_extraction` | `structured_extraction_summary`, `llm_extraction_summary`, raw records |
| `quality_gate_routing` | route decision |
| `human_review` | review packet |
| `final_data_package_builder` | final package |

## Source Roles

| Role | Behavior |
|---|---|
| `collection` | Fetchable and extractable |
| `context_only` | Fetchable for background, blocked from structured extraction |
| `validation_reserved` | Held out from collection, used only for validation comparison |

Key validation source:

```text
src_nmdoh_hps_cases_by_county_1975_2025_pdf
```

## Export Report

```powershell
python scripts/run_hdc_workflow_configured.py
```

Open:

```text
outputs/sessions/<timestamp>/workflow_run_report_chinese.md
outputs/workflow_runs/latest_workflow_run_report_chinese.md
```

Useful supporting files:

```text
outputs/sessions/<timestamp>/collection/final_dataset.csv
outputs/sessions/<timestamp>/collection/source_registry.json
outputs/sessions/<timestamp>/evaluation/evaluation_report.csv
outputs/sessions/<timestamp>/diagnostics/llm_stage_summary.json
outputs/sessions/<timestamp>/workflow_console/hdc_workflow_console.html
outputs/workflow_console/hdc_workflow_console.html
```

## Presenter Claim

This workflow run starts from a user request in Studio, executes the LangGraph workflow on real NMDOH/CDC webpages, calls all three LLM stages through the configured model, separates collection and validation sources, exports structured records and validation comparison, and routes unresolved evidence to human review.
