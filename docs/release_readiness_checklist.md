# Release Readiness Checklist

Project name: **data collection workflow**

This checklist records whether the current local package / CLI / workflow
console is ready for review as a reproducible, auditable workflow.

## Scope

- Multi-disease acceptance covers Hantavirus / New Mexico / 2020-2026,
  COVID-19 / New York / 2024, and Dengue / Florida / 2025.
- Hantavirus / New Mexico is retained as the compatibility case study.
- COVID-19 and dengue are supported through the same generic workflow path.
- Default tests and fixture runs remain offline and deterministic.
- Live search/fetch and LLM calls remain opt-in and key-driven.

## Operator Readiness

- [x] CLI exposes `collect`, `validate-config`, `inspect-run`,
  `review-summary`, `export`, and `init-config`.
- [x] Config-first operation is documented.
- [x] API keys are read from environment variables, not config files.
- [x] CLI output reports key presence only and does not print secret values.
- [x] Offline fixture commands exist for COVID-19 and dengue.
- [x] Live smoke configs exist for COVID-19 and dengue.
- [x] Hantavirus/New Mexico compatibility config remains available.
- [x] Generated config templates are safe starter files.

## Artifact Readiness

- [x] Session output is written under `outputs/sessions/<session_id>/`.
- [x] `workflow_run_summary.json` is created.
- [x] `collection/final_package.json` is created.
- [x] `collection/final_dataset.csv` is created when records exist.
- [x] `diagnostics/final_dataset_post_review.json` is created.
- [x] Validation results and summaries are exported.
- [x] Anomaly results and summaries are exported.
- [x] Human review queue, decisions, and audit trail artifacts are exported.
- [x] Workflow console HTML and summary JSON are created.
- [x] Stage 13 acceptance matrix is exported as JSON and CSV.

## Documentation Readiness

- [x] README presents the project as the **data collection workflow**.
- [x] README no longer frames the whole project as only a Hantavirus case study.
- [x] User guide covers installation, CLI usage, configs, fixture runs, live
  runs, environment variables, review files, inspect/export commands, outputs,
  workflow console, safety limits, and troubleshooting.
- [x] Notebook-style quickstart exists.
- [x] Stage 13 report records acceptance evidence and limitations.

## Safety Readiness

- [x] No real API key is stored in tracked config examples.
- [x] No live acceptance result is faked with fixture output.
- [x] No automatic truth determination is claimed.
- [x] Human review remains explicit and auditable.
- [x] The workflow is documented as not medical advice and not official
  public-health surveillance.
- [x] Live search/fetch limitations are documented.

## Remaining Optional Product Work

- [ ] Interactive human review UI.
- [ ] Hosted service or deployment packaging.
- [ ] Larger curated disease intelligence library.
- [ ] Stronger parsing for dashboards, PDFs, and JavaScript-rendered pages.
- [ ] Advanced epidemiological anomaly models.
- [ ] User studies and publication-facing materials.
