# Live New Mexico HPS LLM Extraction Replay - Stage 4E

## 1. Purpose

Stage 4E runs a controlled LLM extraction replay on already-fetched New Mexico HPS collection evidence from Stage 4C. It tests whether the optional LLM extraction path can recover the 2025 annual HPS summary that deterministic extraction missed.

This is an extraction replay, not a new collection run.

## 2. Why LLM extraction is justified after Stage 4D

Stage 4D confirmed that the key 2025 annual phrase exists in local Stage 4C evidence. The relevant sentence appears in `src_nmdoh_hps_2026_first_case_prior_year_summary`, supporting chunk `chunk_src_nmdoh_hps_2026_first_case_prior_year_summary_001`, and includes phrases such as "seven cases in 2025" and "three of them fatal."

Because text fetch and chunking succeeded, it is reasonable to test whether LLM extraction can structure the annual summary fields that deterministic extraction missed.

## 3. What input text is used

The replay reads local Stage 4C artifacts under `outputs/live_masked_validation_new_mexico_hps`.

If full `evidence_chunks` are unavailable in `final_package.json`, the replay reconstructs limited chunks from `collection/final_dataset.csv` fields:

- `evidence_quote`
- `supporting_chunk_id`
- `source_id`
- `source_url`
- `source_type`

Selected replay inputs are written to:

- `outputs/live_masked_validation_new_mexico_hps_llm_replay/inputs/selected_chunks.json`
- `outputs/live_masked_validation_new_mexico_hps_llm_replay/inputs/selected_chunks.csv`

## 4. Source safety rules

Eligible extraction source IDs:

- `src_nmdoh_hps_2024_first_case`
- `src_nmdoh_hps_2025_first_case_death`
- `src_nmdoh_hps_2026_first_case_prior_year_summary`

Excluded source IDs:

- validation-reserved: `src_nmdoh_hps_cases_by_county_1975_2025_pdf`
- context-only: `src_nmdoh_hps_overview_1975_2025`
- context-only: `src_cdc_hantavirus_reported_cases_through_2023`

The script always sets `HDC_ENABLE_LIVE_FETCH=false` and does not run broad web search.

## 5. How to run dry-run

```bash
python scripts/run_new_mexico_hps_llm_extraction_replay.py --dry-run
```

Dry-run prints planned paths, source IDs, selected chunk IDs, and safety settings. It does not call an LLM.

## 6. How to run controlled LLM extraction replay

```bash
python scripts/run_new_mexico_hps_llm_extraction_replay.py --allow-llm-extraction --provider anthropic --model claude-sonnet-4-6 --target-source-id src_nmdoh_hps_2026_first_case_prior_year_summary
```

This command calls an LLM only on selected local collection evidence. It does not fetch live pages.

## 7. What outputs are generated

Default output directory:

- `outputs/live_masked_validation_new_mexico_hps_llm_replay`

Generated outputs include:

- `inputs/selected_chunks.json`
- `inputs/selected_chunks.csv`
- `llm_extraction/raw_records.json`
- `llm_extraction/validated_records.csv`
- `llm_extraction/normalized_records.csv`
- `llm_extraction/final_package.json`
- `evaluation/evaluation_report.csv`
- `evaluation/evaluation_summary.json`
- `evaluation/professor_demo_report.md`
- `comparison/deterministic_vs_llm_summary.json`
- `comparison/deterministic_vs_llm_report.md`
- `diagnostics/llm_extraction_replay_summary.json`
- `diagnostics/source_role_safety_check.json`
- `diagnostics/selected_chunk_audit.md`
- `diagnostics/llm_extraction_diagnostics.md`

## 8. How to compare deterministic vs LLM extraction

Inspect:

- `comparison/deterministic_vs_llm_summary.json`
- `comparison/deterministic_vs_llm_report.md`

Key checks:

- deterministic records with case counts;
- LLM records with case counts;
- whether LLM extracted `2025 annual cases=7`;
- whether LLM extracted `2025 deaths=3`;
- whether evaluation improved from `missing_collection_record`;
- whether provenance fields are complete.

## 9. Limitations

- This is a controlled replay, not autonomous collection.
- It uses already-fetched collection evidence, not newly fetched pages.
- If full chunk text is not available, replay input is limited to final record evidence quotes.
- It does not parse or OCR the validation PDF.
- It does not prove general extraction quality.
- Human review remains required.
- Results depend on model behavior and prompt/schema quality.

## 10. Next decision

If LLM extraction recovers the 2025 annual summary, the next stage should review the LLM output and prepare the professor meeting package. If it fails, the next stage should improve the LLM extraction prompt/schema and consider deterministic pattern support for reproducibility.
