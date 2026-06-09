# Post-Acceptance Repair 5 Report: Run-Quality-Gated Final Dataset Redesign

## 1. Repair goal

Repair 5 makes `final_dataset` represent quality-gated accepted records instead
of every normalized or pre-review record the workflow produced. Candidate
records are still preserved, but accepted output is now separated from
pre-quality-gate, quarantined, pending-review, and post-review output views.

## 2. Failure case being addressed

A technical workflow run can complete while data quality fails. The Shanghai
hantavirus run showed why unsafe, wrong-disease, source-incompatible, or
out-of-scope records must not appear as accepted final data.

Repairs 1-4 reduced upstream failures: disease mismatch gating, live source
critic routing, task-compatible validation source selection, and localized
Shanghai/HFRS source planning. Repair 5 adds explicit final output semantics so
users can distinguish a successful run with accepted records from a completed
run with no reliable task-relevant accepted records.

## 3. Files created or modified

Created in Repair 5:

- `src/hdc_workflow/run_quality_gates.py`
- `tests/test_run_quality_gated_final_dataset.py`
- `docs/run_quality_gated_final_dataset.md`
- `docs/stage_reports/POST_ACCEPTANCE_REPAIR_5_REPORT.md`

Modified in Repair 5:

- `src/hdc_workflow/models.py`
- `src/hdc_workflow/state.py`
- `src/hdc_workflow/nodes/finalization.py`
- `src/hdc_workflow/export.py`
- `src/hdc_workflow/resources/final_package_policy.json`
- `scripts/run_hdc_workflow_configured.py`
- `scripts/build_workflow_run_console.py`

The working tree also contains previous Repair 1-4 changes. They were not
reverted.

## 4. Functional changes made

- Added deterministic `apply_run_quality_gates`.
- Added record-level inclusion decisions for every normalized/candidate-final
  record.
- Changed `final_dataset` to include only accepted quality-gated records.
- Added `final_dataset_pre_quality_gate` to preserve all normalized records.
- Added `quarantined_records` for hard quality-gate failures.
- Added `pending_review_records` for unresolved blocking review cases.
- Changed default `final_dataset_post_review` behavior: when no explicit human
  review decisions exist, it matches the quality-gated `final_dataset`.
- Preserved explicit Stage 11 human review reject behavior in accepted and
  post-review outputs.
- Added `run_quality_summary`, `final_dataset_quality_summary`, and
  `record_inclusion_decisions` to final package, state, diagnostics, collection
  exports, and workflow summaries.
- Added minimal report and console visibility for run-quality status and counts.

## 5. Record inclusion behavior

- `accepted`: record passed deterministic run-quality gates.
- `accepted_with_warnings`: record passed gates but has non-blocking warnings.
- `pending_human_review`: record requires blocking human review before
  acceptance.
- `quarantined_disease_mismatch`: record disease/pathogen is incompatible with
  the active task disease.
- `quarantined_source_not_task_relevant`: source was excluded, source-critic
  blocked, search-endpoint-only, or not task relevant.
- `quarantined_document_not_task_relevant`: source document is not task relevant
  or not extractable for the task disease.
- `quarantined_chunk_not_task_relevant`: supporting evidence chunk is unrelated
  or not target data.
- `quarantined_outside_scope`: validation marked the record outside requested
  disease/geography/time scope.
- `quarantined_validation_conflict`: comparable trusted/held-out validation
  conflicts block acceptance.
- `quarantined_critical_anomaly`: high or critical record-level anomalies block
  acceptance.
- `excluded_by_human_review`: explicit human review reject decision excludes the
  record.
- `accepted_after_human_review` and `corrected_after_human_review`: supported
  human review decisions can allow a record only after it passes quality gates.

Ordinary cross-source review items remain auditable human-review items; they do
not automatically empty `final_dataset` unless they are hard validation failures
or critical record-level blockers.

## 6. Run quality status behavior

- `passed`: accepted records exist with no hard failures.
- `passed_with_review`: accepted records exist with non-blocking warnings or
  limitations.
- `partial_with_quarantined_records`: at least one record was accepted and at
  least one was quarantined.
- `no_records_extracted`: no normalized records were produced.
- `no_task_relevant_records`: evidence or summaries indicate no extractable
  target-disease records.
- `failed_quality_gate`: normalized records existed but no record passed final
  gates.
- `validation_limited_no_compatible_source`: validation is limited by lack of
  compatible held-out validation source; this is a warning/limitation, not an
  automatic record rejection.

## 7. Dataset views

- `final_dataset`: quality-gated accepted records only.
- `final_dataset_pre_quality_gate`: all normalized records before final gating,
  with quality-gate fields added.
- `quarantined_records`: records blocked by hard gates.
- `pending_review_records`: records held out for unresolved blocking review.
- `final_dataset_post_review`: accepted records after explicit human review
  decisions; equals `final_dataset` when no explicit decisions are applied.
- `diagnostics/normalized_records.json`: original normalized diagnostics remain
  available.

## 8. Shanghai regression behavior

Shanghai live smoke was run with:

```powershell
python scripts\run_hdc_workflow_configured.py --config outputs\generated_configs\hantavirus_shanghai_2024_1_1_2026_6_9_20260609_141441_utc.json --session-id repair5_hantavirus_shanghai_run_quality_gate
```

Observed result:

- Session: `outputs/sessions/repair5_hantavirus_shanghai_run_quality_gate`
- Live search: enabled, Tavily provider
- LLM stages: all three enabled
- Source search executed queries: `2`
- Search-derived candidates: `6`
- Source critic assessed sources: `6`
- Source critic blocked fetch count: `2`
- Documents fetched: `0`
- Normalized records: `0`
- Accepted `final_dataset` count: `0`
- Quarantined records: `0`
- Pending review records: `0`
- `run_quality_status`: `no_task_relevant_records`
- `validation_limited`: `true`
- New Mexico validation active records for Shanghai: `0`
- Inactive New Mexico validation records: `1`

Answers:

- `final_dataset` does not look successful when no reliable records exist.
- No wrong-disease records were accepted.
- `run_quality_status` clearly reports no task-relevant accepted records.
- New Mexico validation records are inactive for Shanghai.

## 9. Backward compatibility

- COVID-19 fixture records remain accepted in the new Repair 5 tests.
- Dengue fixture records remain accepted in the new Repair 5 tests.
- Hantavirus/New Mexico compatibility was rerun:
  - Session: `outputs/sessions/repair5_hantavirus_new_mexico_quality_gate_compat_no_llm`
  - Normalized records: `5`
  - Accepted records: `4`
  - Quarantined records: `1`
  - Pending records: `0`
  - `run_quality_status`: `partial_with_quarantined_records`
  - The quarantined record was blocked by `validation_outside_scope`; HPS
    records were not all incorrectly quarantined.
- Repair 1-4 tests still pass.

## 10. Tests added or updated

Added `tests/test_run_quality_gated_final_dataset.py` with coverage for:

- Clean records accepted.
- Disease mismatch records quarantined.
- Source critic blocked records quarantined.
- Document/chunk not-task-relevant records quarantined.
- Outside-scope validation blocks accepted output.
- Comparable trusted-source validation conflict blocks accepted output.
- No compatible validation source warns but does not reject clean records.
- High/critical anomalies quarantine records.
- Explicit human review reject excludes accepted and post-review datasets.
- Post-review equals quality-gated final dataset when no decisions exist.
- Shanghai failure-style wrong-disease records do not look successful.
- No-record runs get explicit run-quality status.
- Final package and collection export all quality dataset views.
- Clean COVID-19, dengue, and Hantavirus records remain accepted.

## 11. Commands run

Git/state inspection:

```powershell
git status --short
git branch --show-current
git rev-parse HEAD
```

Targeted Repair 5 tests:

```powershell
python -m pytest tests\test_run_quality_gated_final_dataset.py -q
```

Repair 1-4 regression:

```powershell
python -m pytest tests\test_disease_relevance_gating.py tests\test_source_critic_live_integration.py tests\test_task_compatible_validation_sources.py tests\test_localized_multilingual_source_planning.py -q
```

Finalization/export/regression subset:

```powershell
python -m pytest tests\test_anomaly_human_review_application.py tests\test_validation_refactor.py tests\test_generic_structured_extraction.py tests\test_fetch_parse_generalization.py tests\test_graph_smoke.py tests\test_workflow_run_config.py -q
```

Full suite:

```powershell
python -m pytest -q
```

Hantavirus/New Mexico compatibility:

```powershell
python scripts\run_hdc_workflow_configured.py --config configs\hdc_workflow_run_config.jsonc --disable-all-llm --session-id repair5_hantavirus_new_mexico_quality_gate_compat_no_llm
```

Shanghai live smoke:

```powershell
python scripts\run_hdc_workflow_configured.py --config outputs\generated_configs\hantavirus_shanghai_2024_1_1_2026_6_9_20260609_141441_utc.json --session-id repair5_hantavirus_shanghai_run_quality_gate
```

Secret scans:

```powershell
rg -n "tvly-|sk-ant-|ANTHROPIC_API_KEY=\S+|TAVILY_API_KEY=\S+" .env.example configs docs examples notebooks scripts src tests outputs
rg -n "sk-ant-[A-Za-z0-9_-]{20,}|tvly-[A-Za-z0-9_-]{20,}|ANTHROPIC_API_KEY\s*=\s*[A-Za-z0-9_-]{20,}|TAVILY_API_KEY\s*=\s*[A-Za-z0-9_-]{20,}" .env.example configs docs scripts src tests outputs
```

Whitespace check:

```powershell
git diff --check
```

## 12. Test results

- Repair 5 targeted tests: `14 passed`
- Repair 1-4 regression tests: `42 passed`
- Finalization/export/regression subset: `197 passed`
- Full suite: `417 passed`
- Hantavirus/New Mexico compatibility run: completed
- Shanghai live smoke: completed
- Broad secret scan: matched only code constants, mocked test keys, documented
  scan-command text in reports, and the missing `notebooks` path warning.
- Strict long-token secret scan: no matches.
- `git diff --check`: exit 0; only Windows LF-to-CRLF working-copy warnings.

Branch and HEAD:

- Branch: `main`
- HEAD: `6d1faebebf643375e270106c8d91119662bb6578`

## 13. Live acceptance result

PASSED: pytest passed, Shanghai live rerun completed, and `final_dataset`
correctly represented zero accepted records for the Shanghai run. No unsafe
records were accepted. New Mexico validation was inactive for Shanghai. The New
Mexico compatibility smoke preserved accepted HPS records while quarantining one
outside-scope candidate.

## 14. Output artifacts

- `docs/run_quality_gated_final_dataset.md`
- `docs/stage_reports/POST_ACCEPTANCE_REPAIR_5_REPORT.md`
- `tests/test_run_quality_gated_final_dataset.py`
- `outputs/sessions/repair5_hantavirus_shanghai_run_quality_gate`
- `outputs/sessions/repair5_hantavirus_new_mexico_quality_gate_compat_no_llm`

New collection exports include:

- `collection/final_dataset.json`
- `collection/final_dataset_pre_quality_gate.csv`
- `collection/final_dataset_pre_quality_gate.json`
- `collection/quarantined_records.csv`
- `collection/quarantined_records.json`
- `collection/pending_review_records.csv`
- `collection/pending_review_records.json`
- `collection/record_inclusion_decisions.json`

New diagnostics exports include:

- `diagnostics/run_quality_summary.json`
- `diagnostics/final_dataset_quality_summary.json`
- `diagnostics/record_inclusion_decisions.json`
- `diagnostics/final_dataset_pre_quality_gate.json`
- `diagnostics/quarantined_records.json`
- `diagnostics/pending_review_records.json`

## 15. Known limitations

- Full HTML/report dynamic cleanup is not fixed in Repair 5.
- Repair 5 does not improve search ranking or source discovery.
- Repair 5 does not guarantee official source availability.
- Repair 5 does not make automatic truth determinations.
- Expert review remains required.
- Cross-source conflicts remain visible for human review, but only hard
  trusted-source validation conflicts or record-level high/critical anomalies
  block accepted final output.

## 16. Review checklist

- [x] User-facing project name remains "data collection workflow"
- [x] Internal package name hdc_workflow was not renamed
- [x] Graph topology unchanged
- [x] final_dataset is quality-gated accepted records
- [x] final_dataset_pre_quality_gate preserves all normalized records
- [x] quarantined_records are exported
- [x] pending_review_records are exported
- [x] final_dataset_post_review does not include unsafe records without explicit decisions
- [x] run_quality_summary is exported
- [x] final_dataset_quality_summary is exported
- [x] record_inclusion_decisions are exported
- [x] Disease mismatch records are quarantined
- [x] Source critic blocked records are quarantined
- [x] Outside-scope records are not accepted
- [x] High/critical anomaly records are not silently accepted
- [x] No compatible validation source is a warning, not automatic failure
- [x] Clean COVID-19 fixture records remain accepted
- [x] Clean dengue fixture records remain accepted
- [x] Hantavirus/New Mexico compatibility preserved
- [x] Repair 1-4 tests still pass
- [x] pytest was run
- [x] No API keys or secrets were printed
- [x] Repair 6 was not implemented

