# Professor Demo Walkthrough — Stage 2D

## 1. Demo objective

This meeting demo shows the implemented LangGraph-backed workflow and the deterministic masked validation pilot. It focuses on auditable workflow behavior, provenance, source masking, validation comparison, and human review flags. It does not claim real-world epidemiological accuracy.

## 2. Recommended 30-45 minute flow

### Part A — Project framing

- Purpose: Position the work as an auditable agentic public health data collection workflow.
- Command or artifact to show: `docs/current_project_status_stage2c.md`.
- Expected output: Clear distinction between the workflow contribution and LangGraph as the orchestration backbone.
- What to say: The project is not a LangGraph-only demo. LangGraph gives us explicit nodes and state, but the contribution is the provenance-preserving data collection and validation pattern.
- Chinese speaking note: 可以说："LangGraph 是骨架，真正的贡献是可审计的数据收集、证据保留、masked validation 和 human review 机制。"
- What it proves: The project has a coherent technical framing.
- What it does not prove: It does not prove epidemiological correctness.

### Part B — Graph backbone and nodes

- Purpose: Show that the workflow is an explicit state graph.
- Command or artifact to show: `python scripts/check_studio_app.py`.
- Expected output: `CompiledStateGraph`, final package exists, 17 trace nodes in the default offline run.
- What to say: The graph runs through source discovery, screening, content processing, extraction, validation, normalization, linking, consistency checking, routing, and final package building.
- Chinese speaking note: 可以强调："每一步都有 node boundary 和 state trace，所以后续可以审计到底是哪一步产生了某个结果。"
- What it proves: The backbone compiles and runs locally.
- What it does not prove: The default run does not extract records because it intentionally uses offline metadata stubs.

### Part C — Deterministic baseline test

- Purpose: Establish that the current repo is in a passing state.
- Command or artifact to show: `python -m pytest -q`.
- Expected output: `179 passed`.
- What to say: The deterministic tests cover the graph, source routing, fixture extraction, source masking, masked validation reporting, and export behavior.
- Chinese speaking note: 可以说："先证明工程状态是稳定的，再进入 demo artifact。"
- What it proves: The implementation is reproducible under the current deterministic test suite.
- What it does not prove: Tests are not a substitute for real-world validation.

### Part D — Standard fixture run

- Purpose: Show a non-empty end-to-end run without internet or LLM.
- Command or artifact to show: `python scripts/run_fixture_workflow_demo.py`.
- Expected output: 5 loaded fixture documents, 4 records, 1 linked event, 1 conflict, 1 human review item.
- What to say: Fixture data are synthetic and intentionally contain disagreement so the consistency checker produces a human review packet.
- Chinese speaking note: 可以说："这个 demo 的目标不是展示真实疫情数据，而是展示 workflow 在有证据文本时如何抽取、链接、发现冲突、生成 review packet。"
- What it proves: Extraction, normalization, linking, conflict detection, review routing, and provenance export work end to end.
- What it does not prove: It does not prove real public health accuracy.

### Part E — Final package artifact inspection

- Purpose: Show inspectable artifacts rather than only terminal logs.
- Command or artifact to show: `outputs/fixture_final_package/final_dataset.csv`, `conflicts.json`, `human_review_items.json`, `provenance_manifest.json`.
- Expected output: 4 records with source URLs, evidence quotes, supporting chunk IDs, linked event IDs; 1 high-severity conflict; 1 review packet.
- What to say: Every record keeps the evidence needed for an expert to inspect it.
- Chinese speaking note: 可以说："教授如果问结果从哪里来，我们可以直接指到 source_url、evidence_quote 和 supporting_chunk_id。"
- What it proves: The workflow preserves provenance.
- What it does not prove: The system does not automatically resolve conflicts.

### Part F — Masked validation run

- Purpose: Demonstrate held-out source masking and evaluation output.
- Command or artifact to show: `python scripts/run_masked_validation_pilot.py`.
- Expected output: collection records `1`, validation ground truth records `3`, evaluation rows `1`, masking compliance `passed`, human review flagged rows `1`.
- What to say: CDC/ECDC/WHO reserved sources are blocked from collection, while the non-held-out PAHO fixture creates the collection-side record.
- Chinese speaking note: 可以说："collection 阶段不能偷看 reserved sources，validation 阶段才单独用它们做比较。"
- What it proves: Source masking and deterministic evaluation artifacts are implemented.
- What it does not prove: It is not live validation and not automated ground-truth scraping.

### Part G — Evaluation report inspection

- Purpose: Inspect the row-level comparison table and professor-facing Markdown.
- Command or artifact to show: `outputs/masked_validation_pilot/evaluation/evaluation_report.csv`, `evaluation_summary.json`, `professor_demo_report.md`.
- Expected output: 1 row with PAHO collection evidence, CDC/ECDC validation evidence, `partial_match_not_comparable`, `human_review_flag=true`.
- What to say: The collection side reports 12 cases and 2 deaths. The validation side has 12, 13, and 30 cases and 2 deaths, so the case count is not comparable as a single clean value.
- Chinese speaking note: 可以说："系统没有强行说 match，而是保守地说 partial_match_not_comparable，并要求人工 review。"
- What it proves: The evaluation layer can compare evidence and avoid overclaiming.
- What it does not prove: It does not decide the correct epidemiological number.

### Part H — Human-in-the-loop interpretation

- Purpose: Explain why review flags are desirable.
- Command or artifact to show: `outputs/fixture_final_package/human_review_items.json` and `outputs/masked_validation_pilot/evaluation/professor_demo_report.md`.
- Expected output: A conflict review packet and a validation row flagged for human review.
- What to say: The system routes uncertainty to people instead of pretending uncertain numbers are resolved.
- Chinese speaking note: 可以说："human review 不是失败，而是高风险 public health 数据里应该有的安全阀。"
- What it proves: The workflow is conservative by design.
- What it does not prove: Human adjudication decisions are not yet applied back into records.

### Part I — LangGraph vs Codex/Claude Code framing

- Purpose: Answer why LangGraph matters when coding agents can build workflows.
- Command or artifact to show: `src/hdc_workflow/graph.py` for node names only, and `outputs/fixture_final_package/collection_trace.json`.
- Expected output: Explicit node list and traceable workflow state.
- What to say: Codex or Claude Code can help build and operate the system; LangGraph provides the persistent state machine and inspectable execution structure.
- Chinese speaking note: 可以说："Codex/Claude Code 是开发和执行助手，LangGraph 是 workflow runtime。论文贡献不是工具本身，而是这个可审计 workflow pattern。"
- What it proves: The design can separate orchestration, implementation, and scientific contribution.
- What it does not prove: LangGraph itself is not novel science.

### Part J — Limitations and next steps

- Purpose: Close without overclaiming.
- Command or artifact to show: `outputs/professor_demo_package/meeting_talking_points.md`.
- Expected output: Clear limitations and a Stage 3A recommendation.
- What to say: The next step should be a live masked validation case study with real non-held-out collection sources, while preserving held-out validation sources.
- Chinese speaking note: 可以说："下一步不是扩大口号，而是设计一个小而干净的 live masked validation case study。"
- What it proves: The project has a credible next experimental slice.
- What it does not prove: The current deterministic package is not a production surveillance system.

## 3. Exact command sequence

```bash
python -m pytest -q
python scripts/run_workflow_demo.py
python scripts/run_fixture_workflow_demo.py
python scripts/export_fixture_final_package.py
python scripts/run_masked_validation_pilot.py
python scripts/check_studio_app.py
python scripts/print_studio_initial_state.py
```

## 4. Exact artifact opening sequence

1. `outputs/fixture_final_package/final_dataset.csv` — inspect extracted records, source URLs, evidence quotes, supporting chunk IDs, and linked event IDs.
2. `outputs/fixture_final_package/conflicts.json` — inspect the high-severity case-count disagreement.
3. `outputs/fixture_final_package/human_review_items.json` — inspect the review packet for the conflict.
4. `outputs/fixture_final_package/provenance_manifest.json` — inspect provenance completeness counts.
5. `outputs/masked_validation_pilot/collection/final_dataset.csv` — inspect the non-held-out PAHO collection record.
6. `outputs/masked_validation_pilot/collection/source_registry.json` — inspect `validation_reserved` CDC/ECDC/WHO entries and blocked collection status.
7. `outputs/masked_validation_pilot/validation/ground_truth_records.csv` — inspect held-out validation records.
8. `outputs/masked_validation_pilot/evaluation/evaluation_report.csv` — inspect row-level collection-versus-validation comparison.
9. `outputs/masked_validation_pilot/evaluation/evaluation_summary.json` — inspect summary counts and compliance status.
10. `outputs/masked_validation_pilot/evaluation/professor_demo_report.md` — inspect professor-facing row preview and limitations.

## 5. How to explain the key masked validation result

- The collection source is the non-held-out PAHO fixture: `src_paho_hantavirus_americas_guidelines`.
- The validation sources are held-out CDC/ECDC fixtures: `src_cdc_reported_cases`, `src_ecdc_surveillance_updates`, and `src_ecdc_annual_report_2023`.
- The collection side has 12 cases and 2 deaths.
- The validation side has internally inconsistent case counts: 12, 13, and 30, with 2 deaths.
- Therefore the row is `partial_match_not_comparable`.
- `human_review_flag=true` is expected and desirable because the validation evidence is not a single clean comparable case count.
- `masking_compliance_status=passed` proves no reserved source leaked into the collection final dataset.

## 6. Expected professor questions and suggested answers

### Why is the collection source synthetic?

Because Stage 2D is a deterministic meeting package. Synthetic fixture data let us demonstrate masking, provenance, evaluation, and review behavior without internet, LLM calls, or unstable live source content.

### Does this prove real-world accuracy?

No. It proves workflow behavior and auditability. Real-world accuracy requires a later live masked validation case study.

### Why is overall status not match?

The death count matches, and one held-out source matches the collection case count, but the validation sources disagree internally on case count: 12, 13, and 30. The conservative status is `partial_match_not_comparable`.

### How do you know CDC/ECDC/WHO did not leak into collection?

The masked collection `final_dataset.csv` contains only `src_paho_hantavirus_americas_guidelines`, while `source_registry.json` marks reserved CDC/ECDC/WHO sources as `validation_reserved` and blocked from collection. The evaluation summary also reports `masking_compliance_status_counts: passed=1`.

### Why use LangGraph if Codex/Claude Code can build agents?

Codex and Claude Code can help implement and operate the system. LangGraph provides the inspectable state graph, node boundaries, conditional routing, and persistent execution trace. The contribution is the auditable workflow pattern, not LangGraph alone.

### Where does human review happen?

The workflow creates review packets for conflicts and flags validation rows that are mismatched or not cleanly comparable. Human decisions are not yet fully applied back into final records.

### What is the next real-data validation experiment?

Stage 3A should design a small live masked validation case study using real non-held-out collection sources, while keeping CDC/ECDC/WHO reserved for held-out comparison.

### What exactly should be shown in the final paper?

Show the workflow pattern, source masking protocol, provenance-preserving extraction, row-level validation report, human review logic, and a clear limitation boundary between fixture validation and live epidemiological validation.
