# Live MV Hondius Context-Only Guardrail - Stage 3D

## 1. Purpose

Stage 3D implements and verifies a context-only extraction guardrail for the MV Hondius masked-validation pilot.

The immediate problem from Stage 3C was that `src_vdh_hantavirus_mv_hondius_context` was configured as context-only in the case overlay, but deterministic source screening and extraction still allowed VDH text to produce weak structured records. This created context-derived false positives without indicating a WHO masking failure.

Stage 3D keeps the existing graph topology unchanged and adds enforcement at the source-routing, document/chunk, and extraction layers.

## 2. Implementation Summary

Implemented source-level context-only override:

- `src/hdc_workflow/nodes/source_screening.py`
- `context_only_source_ids` from the source-role policy overlay are now enforced after validation-reserved masking.
- Context-only sources are routed as `source_role=context_source`.
- Their final decision becomes `include_for_context_fetch`.
- `ready_for_content_fetch` remains true so the source can still be fetched for context grounding.
- Routing flags include `context_only` and `blocked_from_structured_extraction`.
- Routing summary now reports `context_only_source_count` and `context_only_source_ids`.

Implemented document and chunk guardrail:

- `src/hdc_workflow/nodes/content_processing.py`
- Context-only fetch requests are forced to `fetch_purpose=context_grounding`.
- Source routing metadata is copied into document metadata.
- Context-only documents may still be fetched and chunked.
- Context-only chunks are never marked `contains_target_data=true`.
- Data types are suppressed for context-only chunks, while context-type annotations remain available.

Implemented extraction guardrail:

- `src/hdc_workflow/nodes/extraction.py`
- Deterministic extraction skips context-only chunks.
- LLM extraction path also has a context-only skip for safety, although LLM extraction was not used in this stage.
- Structured extraction summary now reports skipped context-only chunks and source IDs.

Updated live pilot diagnostics:

- `scripts/run_mv_hondius_live_masked_pilot.py`
- Adds context-only guardrail fields to live fetch, collection diagnostics, extraction diagnostics, evaluation summary, and professor summary output.

## 3. Context-Only Behavior After Implementation

In the final Stage 3D MV Hondius run:

- `src_vdh_hantavirus_mv_hondius_context` was fetched.
- VDH returned HTTP 200 and was considered usable.
- VDH was routed as `context_source`.
- VDH final screening decision was `include_for_context_fetch`.
- VDH fetch purpose was `context_grounding`.
- VDH produced 4 evidence chunks.
- All 4 VDH chunks were treated as context-only chunks.
- `target_data_chunk_count` was 0.
- `context_only_target_data_suppressed_count` was 4.
- `skipped_context_only_chunk_count` was 4.
- VDH structured record count after guardrail was 0.

This is the desired behavior: the source can inform context but cannot produce collection records.

## 4. MV Hondius Rerun Result

Final controlled live command:

`python scripts/run_mv_hondius_live_masked_pilot.py --allow-live-fetch`

Final live fetch result:

- Requested collection source IDs: `src_reuters_mv_hondius_2026_05_27`, `src_vdh_hantavirus_mv_hondius_context`.
- Successfully fetched source IDs: both Reuters and VDH.
- Usable source IDs: `src_vdh_hantavirus_mv_hondius_context`.
- Reuters HTTP status: 401.
- Reuters quality status: unusable.
- VDH HTTP status: 200.
- VDH quality status: usable.

Final collection/evaluation result:

- Collection record count: 0.
- Validation ground truth record count: 1.
- Evaluation row count: 1.
- `overall_match_status_counts`: `missing_collection_record=1`.
- `human_review_flagged_row_count`: 1.

Interpretation: after the guardrail, the previous VDH false positives are removed. Reuters still does not provide usable article text, so the live pilot remains a technical masking and guardrail demonstration rather than a successful independent epidemiological validation.

## 5. Source Masking Audit After Rerun

WHO DON600 remained blocked from collection:

- WHO source ID: `src_who_don600_mv_hondius_2026`.
- WHO `source_role`: `validation_reserved`.
- WHO `final_screening_decision`: `reserved_for_validation`.
- WHO `ready_for_content_fetch`: `false`.
- WHO listed in skipped validation-reserved source IDs: yes.
- Reserved source leakage count: 0.
- Technical masking status: passed.

The guardrail does not weaken masking. It adds an additional policy boundary for context-only sources.

## 6. Evaluation Interpretation

The evaluation now has one row:

- The held-out WHO validation record has no collection counterpart.
- Masking compliance passed.
- Provenance completeness is not applicable because there is no collection record.
- Human review is required because the held-out validation event was not recovered from collection-accessible sources.

This is a negative/diagnostic result, not a workflow failure:

- Technical source masking passed.
- Context-only enforcement passed.
- Reuters remains access/quality-limited.
- No independent accessible collection source produced an aligned MV Hondius record.

## 7. Tests Added

Added `tests/test_context_only_guardrail.py`.

Covered scenarios:

- MV Hondius VDH source routes to context fetch when listed in `context_only_source_ids`.
- Context-only documents can be chunked but cannot be marked as target-data chunks.
- Structured extraction skips a context-only chunk even if a malformed upstream state marks it as target data.

Full test result:

- `python -m pytest -q`
- `189 passed`

## 8. Command Results

Commands run during Stage 3D verification:

- `python -m pytest tests/test_context_only_guardrail.py -q`: passed, 3 tests.
- `python -m pytest tests/test_mv_hondius_stage3b.py -q`: passed, 7 tests.
- `python -m pytest -q`: passed, 189 tests.
- `python scripts/run_workflow_demo.py`: passed.
- `python scripts/run_fixture_workflow_demo.py`: passed.
- `python scripts/export_fixture_final_package.py`: passed.
- `python scripts/run_masked_validation_pilot.py`: passed.
- `python scripts/run_mv_hondius_live_masked_pilot.py --allow-live-fetch`: passed.

The first non-escalated live attempt was blocked by local socket permissions. The same allowed live command was rerun with network permission and produced the final diagnostic output summarized here.

## 9. Backward Compatibility And Safety

No graph topology was changed.

Files intentionally not modified:

- `src/hdc_workflow/graph.py`
- `README.md`
- `scripts/run_live_source_llm_pilot.py`
- `scripts/build_langgraph_demo_report.py`

Safety properties preserved:

- Source masking was not weakened.
- WHO ground truth values were not changed.
- No external LLM was called.
- No broad web search was used.
- Reuters access limits were not bypassed.
- Offline tests remain deterministic.

## 10. Limitations

Stage 3D does not prove independent live epidemiological validation.

Remaining limitations:

- Reuters is still access/quality-limited.
- Reuters also has semantic leakage risk because it cites WHO.
- VDH is useful as context but is not an independent structured event-count source for this pilot.
- The validation ground truth is manually curated from the held-out WHO source.
- Broad web search, PDF/OCR, and LLM extraction are still outside this run.

## 11. Recommended Next Stage

Recommended next stage:

Stage 3E - review the guarded MV Hondius output with the professor and decide between two paths:

- Find another accessible, collection-allowed MV Hondius source that does not depend on WHO.
- Switch to the New Mexico backup case for a cleaner live validation demonstration.

Do not add LLM extraction yet. The next useful improvement is better source availability, not a more powerful extractor over an inaccessible or context-only source.
