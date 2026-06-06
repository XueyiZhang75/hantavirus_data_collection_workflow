# HDC Workflow Technical Workshop Checklist

## 1. Project Root

```powershell
cd "C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow"
```

## 2. Open The Workflow Runtime Profile

```text
configs/hdc_workflow_run_config.jsonc
```

Show these settings first:

| Setting | Config field |
|---|---|
| Graph | `workflow.graph_name` |
| Collection mode | `workflow.collection_mode` |
| Source overlay | `workflow.seed_source_overlay_path` |
| Source role policy | `workflow.source_role_policy_overlay_path` |
| Validation evidence | `workflow.validation_ground_truth_records_path` |
| User task | `user_request` |
| Real webpage fetch | `live_web.enabled` |
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

## 3. Enable API Key In This Terminal

```powershell
$env:ANTHROPIC_API_KEY = [Environment]::GetEnvironmentVariable("ANTHROPIC_API_KEY", "User")
```

Check key presence only:

```powershell
[bool]$env:ANTHROPIC_API_KEY
```

Expected:

```text
True
```

Do not print the key.

## 4. Preview Effective Workflow Config

```powershell
python scripts/start_hdc_workflow_studio.py --print-config-only
```

This prints:

- config path
- live fetch status
- three LLM stage switches
- provider/model
- API key presence
- sanitized workflow environment
- minimal Studio input

## 5. Start LangGraph Studio

```powershell
python scripts/start_hdc_workflow_studio.py
```

Open graph:

```text
hantavirus_data_collection_workflow
```

## 6. Studio User Request

Use the `user_request` from the config. To print the minimal payload:

```powershell
python scripts/print_studio_initial_state.py --minimal
```

Minimal JSON input:

```json
{
  "user_request": "Collect data on hantavirus from 2020 to 2026. For this workflow run, use the New Mexico HPS source set, keep collection sources and validation sources separated, extract cases, deaths, dates, locations, source URLs, source types, and evidence quotes, then route uncertain results to human review."
}
```

## 7. Submit And Inspect Nodes

Watch the Studio trace move through:

```text
task_intake_and_scope_planning
query_strategy_builder
source_critic_and_uncertainty_routing
content_fetch_and_parse
structured_extraction
quality_gate_routing
human_review
final_data_package_builder
```

Execution model:

```text
Mostly serial state pipeline.
Conditional branch occurs after quality_gate_routing.
If unresolved validation/comparison/review issues exist, route = human_review.
```

## 8. Export Human-Readable Report

```powershell
python scripts/run_hdc_workflow_configured.py
```

Main report:

```text
outputs/sessions/<timestamp>/workflow_run_report_chinese.md
outputs/workflow_runs/latest_workflow_run_report_chinese.md
```

Run output directory:

```text
outputs/sessions/<timestamp>/
```

## 9. Files To Show

```text
configs/hdc_workflow_run_config.jsonc
outputs/workflow_runs/latest_workflow_run_report_chinese.md
outputs/sessions/<timestamp>/collection/final_dataset.csv
outputs/sessions/<timestamp>/collection/source_registry.json
outputs/sessions/<timestamp>/validation/ground_truth_records.csv
outputs/sessions/<timestamp>/evaluation/evaluation_report.csv
outputs/sessions/<timestamp>/diagnostics/llm_stage_summary.json
outputs/sessions/<timestamp>/workflow_console/hdc_workflow_console.html
outputs/workflow_console/hdc_workflow_console.html
docs/workflow_runtime_profile_guide_chinese.md
```
