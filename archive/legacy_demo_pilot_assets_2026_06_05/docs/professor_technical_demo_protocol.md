# Professor Technical Demo Protocol

## 1. Demo Goal

The demo goal is to show how the current LangGraph backbone runs locally and how the implemented deterministic masked validation pilot works. This is not a rewrite of the workflow. It is a technical workshop showing node boundaries, state growth, deterministic fixture behavior, conflict detection, human review routing, final package export, and held-out source validation with source masking.

## 2. What the Professors Asked For

The requested direction can be summarized as:

- Show how the project runs locally.
- Show how the agent or node workflow is set up.
- Show serial flow, conditional branching, and human review paths.
- Show how collected records can be compared against held-out ground truth.
- Show a table with location, date, cases, deaths, source URLs, evidence text, validation result, and human review flag.
- Keep the system design conservative, with human oversight at key stages.
- Frame the project as an agentic public health data collection framework, not as a LangGraph-only demonstration.

## 3. Demo Narrative

### Part A: Repo Orientation

- Purpose: Establish that the repo already contains a working LangGraph workflow.
- Command or artifact to show: `README.md`, `src/hdc_workflow/graph.py`, `src/hdc_workflow/models.py`.
- What to say: The project is structured around a typed state graph, policy files, Pydantic schemas, deterministic defaults, optional live fetch, and optional LLM extraction.
- Expected output: Professors see the graph node list and core package layout.
- What this proves: The project is already an implemented workflow, not only a proposal.
- What it does not prove: It does not prove real-world epidemiological accuracy.

### Part B: Offline Default Run

- Purpose: Show safe default behavior with no internet and no LLM.
- Command or artifact to show: `python scripts/run_workflow_demo.py`.
- What to say: The workflow discovers and screens sources, creates offline metadata stubs, then stops before evidence extraction because stubs are not real source content.
- Expected output: 15 source candidates, 15 registry entries, 10 offline documents, 0 records, route `finalize`.
- What this proves: The graph runs end to end deterministically.
- What it does not prove: It does not test extraction from real source text.

### Part C: Fixture Run

- Purpose: Show a non-empty end-to-end run without internet or LLM.
- Command or artifact to show: `python scripts/run_fixture_workflow_demo.py`.
- What to say: Fixture data are synthetic and intentionally include source disagreement.
- Expected output: 5 loaded fixture documents, 4 records, 1 linked event, 1 conflict, 1 human review item.
- What this proves: The graph can extract, normalize, link, detect conflict, route review, and export provenance.
- What it does not prove: It does not prove real public health accuracy.

### Part D: Final Package Artifact Inspection

- Purpose: Show auditable outputs instead of only terminal logs.
- Command or artifact to show: `outputs/fixture_final_package/final_dataset.csv`, `conflicts.json`, `human_review_items.json`, `provenance_manifest.json`.
- What to say: Each record keeps source URL, evidence quote, supporting chunk ID, and linked event ID.
- Expected output: CSV and JSON files with record, event, conflict, review, and provenance fields.
- What this proves: The system preserves traceable evidence.
- What it does not prove: It does not resolve conflicts automatically.

### Part E: LangGraph Studio Walkthrough

- Purpose: Show explicit nodes, state inspection, and conditional routing.
- Command or artifact to show: `python scripts/check_studio_app.py`; optionally `python scripts/print_studio_initial_state.py` for Studio input.
- What to say: LangGraph is useful because the workflow is a state machine with inspectable node outputs.
- Expected output: `CompiledStateGraph`, final package exists, ordered trace.
- What this proves: The graph is Studio-compatible.
- What it does not prove: Studio is not the scientific contribution by itself.

### Part F: Controlled Live-Source Pilot Explanation

- Purpose: Explain the live pilot without running it during the deterministic demo.
- Command or artifact to show: `scripts/run_live_source_llm_pilot.py`.
- What to say: The current live pilot fetches a small allowlist and may call an LLM only when credentials are explicitly configured.
- Expected output if run separately: live-source export under `outputs/live_source_llm_pilot/`.
- What this proves: The architecture has a controlled live path.
- What it does not prove: It is not broad web search and not an evaluation benchmark.

### Part G: Masked Validation Pilot

- Purpose: Show the implemented deterministic fixture-based held-out validation protocol.
- Command or artifact to show: `python scripts/run_masked_validation_pilot.py`, `docs/masked_validation_design_spec.md`, and `outputs/masked_validation_pilot/`.
- What to say: CDC/ECDC/WHO sources are registered but blocked from collection in `masked_validation` mode, then used separately for validation comparison.
- Expected output: collection records `1`, validation ground truth records `3`, evaluation rows `1`, masking compliance `passed`, overall status `partial_match_not_comparable`, human review flagged rows `1`.
- What this proves: The system can enforce source masking and produce a row-level comparison between collection evidence and held-out validation evidence.
- What it does not prove: It is still deterministic synthetic fixture validation, not live epidemiological validation.

### Part H: Professor-Facing Evaluation Report

- Purpose: Show the table the professors can inspect.
- Command or artifact to show: `outputs/masked_validation_pilot/evaluation/evaluation_report.csv`, `evaluation_summary.json`, and `professor_demo_report.md`.
- What to say: The comparison table includes location, date, cases, deaths, collection evidence, validation evidence, match status, and review flag.
- Expected output: one row comparing the PAHO collection fixture against held-out CDC/ECDC fixture evidence, with an evidence preview in the Markdown report.
- What this proves: The implementation now produces a concrete row-level evaluation artifact.
- What it does not prove: It does not replace expert review.

### Part I: Current Limitations and Next Steps

- Purpose: Avoid overclaiming.
- Command or artifact to show: README limitations and Stage 1 design docs.
- What to say: Broad search, PDF/OCR, automated ground-truth scraping, conflict resolution, and human-decision application are not yet implemented.
- Expected output: Agreement on the next implementation slice.
- What this proves: The project is scoped conservatively.
- What it does not prove: It is not a production surveillance system yet.

## 4. Exact Commands for Deterministic Demo

Safe commands that do not call external LLMs and do not access the internet:

```bash
python -m pytest -q
python scripts/run_workflow_demo.py
python scripts/run_fixture_workflow_demo.py
python scripts/export_fixture_final_package.py
python scripts/run_masked_validation_pilot.py
python scripts/check_studio_app.py
python scripts/print_studio_initial_state.py
```

Command purposes:

- `python -m pytest -q`: prove the current test suite passes.
- `python scripts/run_workflow_demo.py`: show default offline workflow behavior.
- `python scripts/run_fixture_workflow_demo.py`: show non-empty deterministic extraction, linking, conflict, and human review.
- `python scripts/export_fixture_final_package.py`: generate inspectable package artifacts.
- `python scripts/run_masked_validation_pilot.py`: generate masked collection, held-out validation, and evaluation artifacts.
- `python scripts/check_studio_app.py`: prove the Studio graph entry point imports and invokes.
- `python scripts/print_studio_initial_state.py`: provide JSON input for LangGraph Studio.

## 5. Artifacts to Open During Demo

- `outputs/fixture_final_package/final_dataset.csv`: extracted records with source and evidence fields.
- `outputs/fixture_final_package/source_registry.json`: screened source registry, routing decisions, source roles.
- `outputs/fixture_final_package/linked_events.json`: event grouping, source diversity, conflict IDs.
- `outputs/fixture_final_package/conflicts.json`: field-level conflict with record/source/evidence provenance.
- `outputs/fixture_final_package/human_review_items.json`: review packet containing conflict, linked event, and related records.
- `outputs/fixture_final_package/provenance_manifest.json`: counts of records with source URL, evidence quote, supporting chunk ID, and linked event ID.
- `outputs/fixture_final_package/package_metadata.json`: package version, synthetic fixture warning, LLM/web-search flags.
- `outputs/masked_validation_pilot/collection/final_dataset.csv`: masked collection output from the non-held-out PAHO fixture.
- `outputs/masked_validation_pilot/collection/source_registry.json`: reserved CDC/ECDC/WHO source roles and blocked collection status.
- `outputs/masked_validation_pilot/validation/ground_truth_records.csv`: held-out CDC/ECDC validation records.
- `outputs/masked_validation_pilot/evaluation/evaluation_report.csv`: row-level collection-versus-validation comparison.
- `outputs/masked_validation_pilot/evaluation/evaluation_summary.json`: summary counts, masking compliance, and review flags.
- `outputs/masked_validation_pilot/evaluation/professor_demo_report.md`: professor-facing Markdown preview.

## 6. How to Explain Fixture Demo

Fixture data are synthetic. The fixture demo is not an evaluation of real public health accuracy.

The purpose is to test:

- Graph topology.
- Deterministic extraction.
- Conflict detection.
- Human review routing.
- Provenance preservation.
- Final package export.

The fixture intentionally creates a numeric disagreement: three source documents report different case counts for the same synthetic event. This is meant to trigger the cross-source consistency checker and produce a human review packet.

## 7. How to Explain Live-Source Pilot

The current live pilot is controlled:

- It is not broad web search.
- It is not an evaluation benchmark.
- It tests live HTTP fetch, optional LLM extraction, downstream normalization/linking/checking, and export.
- It uses an allowlist of official sources by default.
- Because it uses official sources directly, it is not yet masked validation.

The live pilot should be described as an engineering pilot, not as a scientific evaluation result.

## 8. How to Explain Masked Validation Pilot

Current deterministic masked collection phase:

- CDC/ECDC/WHO sources are known to the system but blocked.
- `source_registry` preserves them as `validation_reserved`.
- Collection `final_dataset` contains no records from validation-reserved sources.
- Collection currently contains one synthetic non-held-out PAHO record.

Current deterministic validation phase:

- Held-out sources are used separately.
- A comparison report is generated.
- Validation records are not mixed into the collection dataset.
- Validation currently has three held-out fixture records from CDC/ECDC sources.
- The current evaluation row is `partial_match_not_comparable` because validation case counts disagree internally: `12`, `13`, and `30`.
- `masking_compliance_status=passed` means no reserved source leaked into collection.

Expected professor-facing table columns:

- Location.
- Date.
- Case count.
- Death count.
- Collection source URL.
- Collection evidence quote.
- Validation source URL.
- Validation evidence quote.
- Match status.
- Human review flag.

## 9. Human-in-the-Loop Explanation

Human review should not exist only at the very end. A conservative design places human oversight at multiple gates:

- Source planning / screening: review questionable sources.
- Content quality: review low-quality or partial documents.
- Extraction: review low-confidence or incomplete records.
- Consistency check: review conflicts.
- Validation: review mismatches and non-comparable rows.
- Final package: approve release.

The current implementation already builds final human review packets with conflict, linked event, and related record context. The next step should make review flags more explicit in the professor-facing evaluation report.

## 10. LangGraph Framing

LangGraph is the current orchestration backbone. The scientific contribution is not LangGraph itself.

The contribution is the auditable agentic workflow pattern for public health data collection:

- Explicit source planning.
- Traceable evidence extraction.
- Structured provenance.
- Conservative validation.
- Human review routing.
- Reproducible final packages.

The same framework could in principle be implemented with Codex, Claude Code, or a self-built multi-agent system. LangGraph is useful here because it provides explicit nodes, state management, conditional routing, traceability, exportable state, and human review routing.

## 11. Expected Questions and Suggested Answers

### Q: Why not just use Codex or Claude Code?

A: Codex or Claude Code can help implement and operate the workflow, but the workflow needs persistent state, node boundaries, repeatable execution, and auditable outputs. LangGraph provides a structured backbone for that. The agentic pattern is more important than the specific tool.

### Q: Is LangGraph the contribution?

A: No. LangGraph is the orchestration tool. The contribution is a conservative, provenance-preserving public health data collection and validation protocol.

### Q: Is this RAG?

A: Not primarily. The workflow collects, screens, fetches, chunks, extracts, normalizes, links, validates, and packages data. It may use retrieval-like pieces, but the main object is a structured, auditable data pipeline.

### Q: Does fixture demo prove real-world accuracy?

A: No. Fixture mode proves graph behavior, provenance preservation, conflict routing, and export shape. Real-world accuracy requires a separate validation experiment.

### Q: How do you prevent the model from cheating by reading CDC/ECDC/WHO?

A: In the masked validation pilot, those sources are registered but marked `validation_reserved`, blocked during collection fetch/extraction, and used only in a separate validation phase.

### Q: Where exactly does human review happen?

A: Currently the implemented human review node packages queued review items after quality-gate routing. Review items can come from schema validation, normalization, linking, and cross-source conflicts. The masked validation evaluation report also flags mismatch and non-comparable rows for review.

### Q: What is the next validation experiment?

A: Design the first live masked validation case study using real non-held-out collection sources, while keeping CDC/ECDC/WHO reserved for validation comparison.

### Q: What are current limitations?

A: Broad web search, automated CDC/ECDC/WHO ground truth scraping, PDF/OCR, dashboard UI, conflict resolution, credibility scoring, and human decision application are not yet implemented.

## 12. Demo Acceptance Checklist

- Deterministic tests pass.
- Fixture package export works.
- Professor can inspect `final_dataset.csv`.
- Professor can inspect conflict provenance.
- Professor can inspect `human_review_items.json`.
- Masked validation design spec and deterministic output artifacts exist.
- Next implementation plan is clear.
- No overclaiming about broad web search or real-world accuracy.
