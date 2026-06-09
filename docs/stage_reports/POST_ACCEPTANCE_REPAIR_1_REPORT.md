# Post-acceptance Repair 1 Report

## Stage goal

Add deterministic disease relevance hard gates to the data collection workflow so
evidence about an incompatible disease cannot be accepted as records for the
active task disease.

The motivating failure case was Shanghai COVID-19/SARS-CoV-2 evidence being
accepted as Hantavirus disease records. This repair prevents that path at source,
document, chunk, extraction, schema validation, normalization, final package, and
diagnostic export layers.

## Summary of changes

- Added `hdc_workflow.disease_relevance`, a deterministic helper for task-disease
  context building, disease term matching, source/document/chunk relevance
  assessment, record compatibility assessment, and summary generation.
- Added source-level disease relevance scoring in source credibility and forced
  clearly unrelated sources to `excluded` and not fetch-ready.
- Added document-level disease relevance quality gating. Usable parsed documents
  that name only an incompatible disease become `not_task_relevant`.
- Added chunk-level hard gating. Chunks with case/death/date/location signals are
  suppressed if they do not match the active task disease.
- Added structured extraction eligibility gates for both deterministic extraction
  and optional LLM extraction.
- Added schema validation rejection for incompatible raw records with machine
  readable `disease_mismatch` validation errors.
- Added normalization quarantine for incompatible validated records before they
  can enter `normalized_records`.
- Updated the optional LLM structured extraction policy to require target task
  disease matching and to return empty records for incompatible disease evidence.
- Exported `disease_relevance_summary` through configured-run diagnostics,
  workflow summaries, run summary, final package policy, and the HTML console
  summary.
- Added user documentation for disease relevance gating.

## Files changed

- `src/hdc_workflow/disease_relevance.py`
- `src/hdc_workflow/models.py`
- `src/hdc_workflow/state.py`
- `src/hdc_workflow/source_credibility.py`
- `src/hdc_workflow/nodes/content_processing.py`
- `src/hdc_workflow/nodes/extraction.py`
- `src/hdc_workflow/nodes/normalization.py`
- `src/hdc_workflow/resources/final_package_policy.json`
- `src/hdc_workflow/resources/llm_structured_extraction_policy.json`
- `scripts/run_hdc_workflow_configured.py`
- `scripts/build_workflow_run_console.py`
- `docs/disease_relevance_gating.md`
- `docs/user_guide.md`
- `tests/test_disease_relevance_gating.py`
- `docs/stage_reports/POST_ACCEPTANCE_REPAIR_1_REPORT.md`

## New/updated tests

Added `tests/test_disease_relevance_gating.py` with coverage for:

- Source relevance ignores `query_used` as disease proof.
- COVID-19 source/document evidence is marked unrelated for a Hantavirus task.
- COVID-19 chunks are suppressed even when they contain case/death signals.
- Structured extraction skips disease-mismatch chunks.
- Schema validation rejects LLM-style incompatible COVID records.
- Normalization quarantines incompatible validated records.
- Compatible Hantavirus evidence is accepted.
- LLM extraction policy contains target-disease and incompatible-disease rules.
- Final package includes `disease_relevance_summary`.

Regression coverage was run against generic structured extraction, fetch/parse,
source credibility, validation, human-review application, graph smoke, workflow
config, and the full suite.

## Commands run

```powershell
python -m pytest tests\test_disease_relevance_gating.py -q
python -m pytest tests\test_disease_relevance_gating.py tests\test_generic_structured_extraction.py tests\test_fetch_parse_generalization.py tests\test_source_credibility_scoring.py tests\test_validation_refactor.py tests\test_anomaly_human_review_application.py tests\test_graph_smoke.py tests\test_workflow_run_config.py -q
python -m pytest -q
python scripts\run_hdc_workflow_configured.py --disable-live-fetch --disable-all-llm --session-id repair1_hantavirus_new_mexico_compat_no_llm
rg -n "tvly-|sk-ant-|ANTHROPIC_API_KEY=\S+|TAVILY_API_KEY=\S+" .env.example configs docs examples notebooks scripts src tests outputs
rg -n 'sk-ant-[A-Za-z0-9_-]{20,}|tvly-[A-Za-z0-9_-]{20,}|ANTHROPIC_API_KEY\s*=\s*[A-Za-z0-9_-]{20,}|TAVILY_API_KEY\s*=\s*[A-Za-z0-9_-]{20,}' .env.example configs docs examples scripts src tests outputs
git diff --check
```

## Test results

- `tests/test_disease_relevance_gating.py`: `9 passed`
- Related regression subset: `221 passed`
- Full test suite: `370 passed`
- Configured offline compatibility run: completed successfully
- Strict long-key secret scan: no matches
- Broad secret scan: matched only mocked test placeholders, documented scan
  command text in previous reports, and the `notebooks` path warning because
  that directory does not exist. No real API key value was found or printed.
- `git diff --check`: passed. Git reported existing LF-to-CRLF working-copy
  warnings on Windows.

## Example command or fixture run

```powershell
python scripts\run_hdc_workflow_configured.py --disable-live-fetch --disable-all-llm --session-id repair1_hantavirus_new_mexico_compat_no_llm
```

Key output:

- Session:
  `outputs/sessions/repair1_hantavirus_new_mexico_compat_no_llm`
- Trace node count: `20`
- Documents: `5`
- Source credibility assessed sources: `20`
- LLM structured extraction call count: `0`
- Normalized record count: `0`
- Current route: `human_review`

The run exported:

`outputs/sessions/repair1_hantavirus_new_mexico_compat_no_llm/diagnostics/disease_relevance_summary.json`

Summary excerpt:

```json
{
  "target_disease": "Hantavirus disease",
  "target_group": "hantavirus",
  "source_status_counts": {
    "target_disease_match": 20
  },
  "document_status_counts": {
    "target_disease_match": 5
  },
  "rejected_incompatible_record_count": 0,
  "normalized_incompatible_record_count": 0
}
```

## Output artifacts created

- `docs/disease_relevance_gating.md`
- `docs/stage_reports/POST_ACCEPTANCE_REPAIR_1_REPORT.md`
- `outputs/sessions/repair1_hantavirus_new_mexico_compat_no_llm/`
- `outputs/sessions/repair1_hantavirus_new_mexico_compat_no_llm/diagnostics/disease_relevance_summary.json`
- `outputs/sessions/repair1_hantavirus_new_mexico_compat_no_llm/workflow_console/hdc_workflow_console.html`
- `outputs/sessions/repair1_hantavirus_new_mexico_compat_no_llm/workflow_run_report_chinese.md`

## Known limitations

- The deterministic disease dictionary currently has explicit groups for
  Hantavirus, COVID-19, Dengue, and Ebola/Orthoebolavirus zairense. Other
  diseases rely on the task disease string and disease-intelligence aliases
  already present in state.
- If no active task disease is provided to a low-level node, disease gating is
  disabled to preserve backward-compatible direct node behavior. Normal configured
  workflow runs provide an active task disease.
- Sparse source metadata may be ambiguous at source screening time. The later
  document, chunk, validation, and normalization gates still apply after fetch.
- This repair does not add an LLM disease classifier. The hard gate remains
  deterministic and offline-testable.

## Future-stage items NOT implemented

- Did not start Stage 14.
- Did not implement Repair 2 or any later repair item.
- Did not change LangGraph topology.
- Did not add new live-search providers or provider ingestion behavior.
- Did not change the default offline deterministic test behavior.
- Did not perform a new live Shanghai web/API run in this repair pass.

## Review checklist

- [x] Project name remains `data collection workflow`.
- [x] Internal package name remains `hdc_workflow`.
- [x] Backward compatibility preserved for low-level direct node tests.
- [x] Default tests do not require internet access, API keys, live web, or real
      LLM calls.
- [x] Real API keys were not printed or committed.
- [x] Disease mismatch source/document/chunk/record paths are auditable.
- [x] `disease_relevance_summary` is exported in configured run artifacts.
- [x] `pytest -q` passes.
- [x] Stage 14 and later repair items were not started.

