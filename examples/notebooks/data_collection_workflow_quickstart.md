# data collection workflow Quickstart Notebook

This notebook-style walkthrough uses repository commands that can be copied into
PowerShell cells or run from a terminal. It starts with deterministic offline
fixture runs and then shows where live search and LLM stages can be enabled.

The workflow is not medical advice. It collects, structures, validates, and
audits public-health source evidence for review.

## Cell 1. Show the CLI

```powershell
python -m hdc_workflow.cli --help
```

Expected result: the help text lists `collect`, `validate-config`,
`inspect-run`, `review-summary`, `export`, and `init-config`.

## Cell 2. Validate the COVID-19 Fixture Config

```powershell
python -m hdc_workflow.cli validate-config --config configs/examples/covid19_new_york_2024_fixture_review_application_task.jsonc
```

Expected result: `valid: true`.

## Cell 3. Run Offline Fixture COVID-19

```powershell
python -m hdc_workflow.cli collect --config configs/examples/covid19_new_york_2024_fixture_review_application_task.jsonc --session-id notebook_covid19_fixture --disable-all-llm
```

Expected result: a new session folder:

```text
outputs/sessions/notebook_covid19_fixture/
```

## Cell 4. Inspect the COVID-19 Run

```powershell
python -m hdc_workflow.cli inspect-run --session-dir outputs/sessions/notebook_covid19_fixture
python -m hdc_workflow.cli review-summary --session-dir outputs/sessions/notebook_covid19_fixture
```

Look for `final_dataset_count`, `anomaly_count`,
`human_review_item_count`, `decisions_applied_count`, and
`audit_trail_count`.

## Cell 5. Run Offline Fixture Dengue

```powershell
python -m hdc_workflow.cli collect --config configs/examples/dengue_florida_2025_fixture_review_application_task.jsonc --session-id notebook_dengue_fixture --disable-all-llm
```

Expected result: a new session folder:

```text
outputs/sessions/notebook_dengue_fixture/
```

## Cell 6. Export a Run

```powershell
python -m hdc_workflow.cli export --session-dir outputs/sessions/notebook_covid19_fixture --output-dir outputs/exports/notebook_covid19_fixture --format both
```

Open these exported files first:

```text
outputs/exports/notebook_covid19_fixture/final_dataset.csv
outputs/exports/notebook_covid19_fixture/final_dataset_post_review.json
outputs/exports/notebook_covid19_fixture/validation_results.json
outputs/exports/notebook_covid19_fixture/anomaly_results.json
outputs/exports/notebook_covid19_fixture/human_review_audit_trail.json
outputs/exports/notebook_covid19_fixture/hdc_workflow_console.html
```

## Cell 7. Preview a Config Without Running

```powershell
python -m hdc_workflow.cli collect --config configs/examples/covid19_new_york_2024_fixture_review_application_task.jsonc --dry-run
```

Expected result: sanitized config and structured task preview. The graph is not
invoked.

## Cell 8. Optional Live Search Setup

Live search uses Tavily metadata search. Keep the key in the environment, not
in a config file:

```powershell
$env:TAVILY_API_KEY = [Environment]::GetEnvironmentVariable("TAVILY_API_KEY", "User")
python -m hdc_workflow.cli validate-config --config configs/examples/covid19_new_york_2024_live_review_smoke.jsonc
```

Then run a bounded live-search smoke:

```powershell
python -m hdc_workflow.cli collect --config configs/examples/covid19_new_york_2024_live_review_smoke.jsonc --session-id notebook_covid19_live_search --disable-all-llm
```

## Cell 9. Optional LLM Setup

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

The CLI prints whether the key is present but does not print the secret value.

## Cell 10. Generate a New Config Template

```powershell
python -m hdc_workflow.cli init-config --disease dengue --location Florida --start-date 2025 --end-date 2025 --target-field cases_unspecified --target-field deaths --mode fixture-search --output configs/local_notebook_dengue_fixture.jsonc
python -m hdc_workflow.cli validate-config --config configs/local_notebook_dengue_fixture.jsonc
```

The generated config is safe to commit if it contains no local paths or secrets.
