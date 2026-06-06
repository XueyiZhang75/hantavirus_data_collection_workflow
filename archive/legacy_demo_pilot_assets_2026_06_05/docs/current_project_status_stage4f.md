# Current Project Status After Stage 4F

## 1. One-sentence framing

This is an auditable hybrid agentic workflow for hantavirus public health data collection, using LangGraph as orchestration backbone, LLM agents for selected advisory reasoning/extraction tasks, deterministic guardrails for safety, and human review for uncertainty.

## 2. Implemented workflow capabilities

- LangGraph node backbone for staged public-health data collection.
- Offline deterministic default for safe local execution.
- Synthetic fixture regression tests for workflow sanity checks.
- Source registry and deterministic source screening.
- Source masking with `validation_reserved` sources blocked from collection.
- Context-only guardrail for sources that should support background only.
- Live source overlays for controlled real-source pilots.
- Real webpage live fetch via explicit allowlist and explicit live-fetch flag.
- LLM Source Planning Agent for structured advisory source strategy.
- LLM Source Critic Agent for semantic leakage and human-review risk checks.
- Controlled LLM extraction replay on already-fetched collection evidence.
- Schema/provenance validation after extraction.
- Normalization, record linking, and masked-validation evaluation.
- Annual reporting-period alignment for `statistical_count_type=annual`.
- Human review flags for missing, partial, mismatched, or not-comparable rows.
- Professor-facing reports and artifact packages.

## 3. Current best demonstration chain

New Mexico HPS is now the strongest demo chain. The LLM Source Planning Agent selected a design-supported New Mexico official-source direction. Stage 4C then fetched real NMDOH and CDC webpages while blocking the held-out validation source. The deterministic extractor produced records but missed the annual count embedded in prose. Stage 4E ran a controlled LLM extraction replay only on collection-side evidence and recovered the sentence-level result: 2025 annual New Mexico HPS `cases=7` and `deaths=3`. Stage 4F then aligned annual records by `reporting_period`, allowing comparison with held-out annual validation ground truth. The case count matched; the death count remained not comparable because the validation ground truth lacks deaths. Human review remains required.

## 4. Current key results

- Latest full test result: `python -m pytest -q` -> `220 passed`.
- Stage 4C `collection_record_count=5`.
- Stage 4C `validation_ground_truth_record_count=1`.
- Stage 4C `reserved_source_leakage_count=0`.
- Stage 4E LLM replay `raw_record_count=2`, `validated_record_count=2`, `normalized_record_count=2`.
- Stage 4E LLM extracted 2025 annual `cases=7` and `deaths=3`.
- Stage 4F `rows_with_both_collection_and_validation_evidence_count=1`.
- Stage 4F annual row field-level status: `case_count_match;death_count_not_comparable`.
- Stage 4F annual row overall status: `partial_match_not_comparable`.
- Stage 4F `reserved_source_leakage_count=0`.
- Stage 4F `human_review_flagged_row_count=2`.

## 5. What this proves

- The real webpage collection path works under explicit allowlist and live-fetch controls.
- Held-out source masking works for the New Mexico HPS case study.
- Context-only guardrails can prevent context sources from becoming extraction records.
- LLM source planning can generate a structured source strategy.
- LLM source critic can assess source risk and human-review needs.
- Controlled LLM extraction can recover structured counts missed by deterministic extraction.
- Evaluation can compare collection evidence to held-out validation evidence.
- Human review is correctly triggered for the non-comparable death field.

## 6. What this does not prove

- It is not broad autonomous web search.
- It is not production surveillance.
- It is not automated PDF/OCR.
- It is not automated ground-truth scraping.
- It is not proof of general extraction accuracy.
- It is not final epidemiological truth.
- It is not fully independent validation because the ground truth is manually curated.
- It has not yet been demonstrated across all diseases or all source types.

## 7. Immediate next decision

- Prepare the professor meeting and pause implementation.
- Add deterministic pattern support for spelled-out annual counts.
- Add validation PDF/OCR support later.
- Expand to another real-source hantavirus scenario.
- Add LLM extraction into the full live workflow only after supervisor approval.
