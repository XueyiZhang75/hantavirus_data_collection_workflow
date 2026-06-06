# HDC Workflow Technical Workshop Materials

These materials explain how to present the HDC workflow runtime in a technical workshop.

## Main Workflow Flow

1. Open the workflow runtime profile: `configs/hdc_workflow_run_config.jsonc`.
2. Show that the profile contains the graph input, source overlays, live-web switch, provider/model, three LLM switches, source split, validation evidence, and output directory.
3. Confirm the API key exists without printing it.
4. Start LangGraph Studio from the runtime profile.
5. Submit the configured `user_request` in Studio and inspect node-by-node execution.
6. Export the human-readable report with the same config.

## Workflow Runtime Profile

```text
configs/hdc_workflow_run_config.jsonc
```

Most useful fields:

| Field | Purpose |
|---|---|
| `workflow.graph_name` | LangGraph graph to run |
| `workflow.collection_mode` | Collection/evaluation mode |
| `workflow.seed_source_overlay_path` | Source candidates used by this workflow profile |
| `workflow.source_role_policy_overlay_path` | Collection/context/validation source policy |
| `workflow.validation_ground_truth_records_path` | Held-out validation evidence |
| `user_request` | Task text submitted to LangGraph Studio |
| `live_web.enabled` | Turns real webpage fetch on/off |
| `live_web.timeout_seconds` | HTTP fetch timeout |
| `llm.provider` / `llm.model` | Model used by the LLM stages |
| `llm.source_planning_enabled` | Enables LLM source planning |
| `llm.source_critic_enabled` | Enables LLM source critic |
| `llm.structured_extraction_enabled` | Enables LLM structured extraction |
| `source_sets.collection_source_ids` | Sources allowed for collection/extraction |
| `source_sets.validation_reserved_source_ids` | Held-out validation sources |
| `source_sets.context_source_ids` | Context-only sources |
| `output.run_output_root` | Root for timestamped run sessions |
| `output.sessionized` | Whether each run writes to `sessions/<timestamp>/` |
| `output.auto_build_console` | Whether the runner automatically exports the HTML console |

## Core Workflow Commands

Preview the effective config without starting Studio:

```powershell
python scripts/start_hdc_workflow_studio.py --print-config-only
```

Start Studio using the config:

```powershell
python scripts/start_hdc_workflow_studio.py
```

Print the minimal Studio input:

```powershell
python scripts/print_studio_initial_state.py --minimal
```

Export report with the same workflow runtime profile:

```powershell
python scripts/run_hdc_workflow_configured.py
```

The runner reads live web, LLM, source, and output settings from `configs/hdc_workflow_run_config.jsonc`. CLI flags are optional one-run overrides only.

## Open These Files

| Step | File |
|---|---|
| Workflow runtime profile | `configs/hdc_workflow_run_config.jsonc` |
| Runtime profile guide | `docs/workflow_runtime_profile_guide_chinese.md` |
| Technical workshop script | `docs/technical_workshop/workflow_operator_script_chinese.md` |
| Command checklist | `docs/technical_workshop/workflow_command_checklist.md` |
| Source role split | `docs/technical_workshop/new_mexico_hps_source_split_table.md` |
| Current session output | `outputs/sessions/<timestamp>/` |
| Human-readable run report | `outputs/workflow_runs/latest_workflow_run_report_chinese.md` |
| Workflow run console | `outputs/workflow_console/hdc_workflow_console.html` |
| Operator runbook | `docs/workflow_technical_workshop_runbook.md` |

## Primary Outputs

| Output | Path |
|---|---|
| Session directory | `outputs/sessions/<timestamp>/` |
| Human-readable report | `outputs/workflow_runs/latest_workflow_run_report_chinese.md` |
| Final dataset | `outputs/sessions/<timestamp>/collection/final_dataset.csv` |
| Source registry | `outputs/sessions/<timestamp>/collection/source_registry.json` |
| Validation ground truth | `outputs/sessions/<timestamp>/validation/ground_truth_records.csv` |
| Evaluation report | `outputs/sessions/<timestamp>/evaluation/evaluation_report.csv` |
| LLM stage summary | `outputs/sessions/<timestamp>/diagnostics/llm_stage_summary.json` |

## Safety

- Do not print the API key.
- Validation-reserved sources are not collection sources.
- Context sources are not allowed to create structured records.
- Studio shows process; the report script exports readable results.
