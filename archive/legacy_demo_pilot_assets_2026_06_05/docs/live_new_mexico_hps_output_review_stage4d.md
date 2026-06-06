# Live New Mexico HPS Output Review - Stage 4D

## 1. Purpose

Stage 4D audits the Stage 4C New Mexico HPS live outputs before changing extraction logic. It does not rerun live fetch, does not call LLMs, does not change workflow code, and does not modify the source overlays or ground truth.

## 2. Stage 4C summary

Stage 4C completed a controlled real-source masked validation pilot:

- `live_fetch_enabled`: `true`
- `broad_web_search_used`: `false`
- `llm_extraction_enabled`: `false`
- `collection_record_count`: `5`
- `validation_ground_truth_record_count`: `1`
- `evaluation_row_count`: `5`
- `overall_match_status_counts`: `missing_validation_record=4`, `missing_collection_record=1`
- `masking_compliance_status_counts`: `passed=5`
- `reserved_source_leakage_count`: `0`
- `context_only_record_count`: `0`

All required Stage 4C artifacts were present during this audit.

## 3. Source masking audit

The validation-reserved source is `src_nmdoh_hps_cases_by_county_1975_2025_pdf`.

Audit result:

- It appears in `collection/source_registry.json`.
- `source_role=validation_reserved`.
- `final_screening_decision=reserved_for_validation`.
- `ready_for_content_fetch=false`.
- It does not appear in `collection/final_dataset.csv`.
- `reserved_source_leakage_count=0`.
- `technical_masking_status=passed`.

The context-only sources `src_nmdoh_hps_overview_1975_2025` and `src_cdc_hantavirus_reported_cases_through_2023` were fetched for context, but produced no structured collection records.

## 4. Live fetch audit

The pilot allowlist contained six source IDs:

- `src_nmdoh_hps_2024_first_case`
- `src_nmdoh_hps_2025_first_case_death`
- `src_nmdoh_hps_2026_first_case_prior_year_summary`
- `src_nmdoh_hps_overview_1975_2025`
- `src_cdc_hantavirus_reported_cases_through_2023`
- `src_nmdoh_hps_cases_by_county_1975_2025_pdf`

Five sources were requested and fetched:

- `src_nmdoh_hps_2024_first_case`
- `src_nmdoh_hps_2025_first_case_death`
- `src_nmdoh_hps_2026_first_case_prior_year_summary`
- `src_nmdoh_hps_overview_1975_2025`
- `src_cdc_hantavirus_reported_cases_through_2023`

All five fetched pages were `html`, `fetched`, and `usable`. No fetched source was access- or quality-limited. The held-out validation source was blocked from collection and listed in `skipped_validation_reserved_source_ids`.

## 5. Collection record audit

The five final collection records came from three NMDOH collection sources:

| record_id | source_id | date_anchor | reporting_period | statistical_count_type | cases_unspecified | deaths | supporting_chunk_id | human review |
|---|---|---:|---|---|---|---|---|---|
| `rec_src_nmdoh_hps_2024_first_case_001` | `src_nmdoh_hps_2024_first_case` | `2024` | blank | `annual` | blank | blank | `chunk_src_nmdoh_hps_2024_first_case_001` | `False` |
| `rec_src_nmdoh_hps_2024_first_case_002` | `src_nmdoh_hps_2024_first_case` | `2024` | blank | blank | blank | blank | `chunk_src_nmdoh_hps_2024_first_case_003` | `True` |
| `rec_src_nmdoh_hps_2025_first_case_death_001` | `src_nmdoh_hps_2025_first_case_death` | `2026` | blank | `cumulative` | blank | blank | `chunk_src_nmdoh_hps_2025_first_case_death_001` | `False` |
| `rec_src_nmdoh_hps_2025_first_case_death_002` | `src_nmdoh_hps_2025_first_case_death` | `2024` | blank | `annual` | blank | blank | `chunk_src_nmdoh_hps_2025_first_case_death_002` | `False` |
| `rec_src_nmdoh_hps_2026_first_case_prior_year_summary_001` | `src_nmdoh_hps_2026_first_case_prior_year_summary` | `2026` | blank | `annual` | blank | blank | `chunk_src_nmdoh_hps_2026_first_case_prior_year_summary_001` | `False` |

No final collection record included a numeric case count. No final collection record included a death count. No record used `reporting_period=2025`. No record aligned with the validation key `New Mexico / HPS / 2025 / annual / cases=7`.

The main blocking fields were `cases_unspecified`, `deaths`, `reporting_period`, and `date_anchor`. The 2026 NMDOH source contained a prior-year 2025 sentence, but the record remained anchored to 2026 and did not store the annual count.

## 6. Evidence/chunk audit

Evidence and chunk content were not exported as separate `documents` or `evidence_chunks` arrays in `collection/final_package.json`, but the final records preserve `supporting_chunk_id` and `evidence_quote`, and workflow diagnostics preserve evidence counts.

Diagnostics:

- `total_chunk_count=16`
- `target_data_chunk_count=7`
- `extractable_chunk_count=7`
- `raw_record_count=5`
- `field_detection_counts.cases_unspecified=0`
- `field_detection_counts.deaths=0`
- `data_type_counts.case_count=5`
- `data_type_counts.death_count=1`
- `skipped_context_only_chunk_count=7`

The relevant 2025 annual phrase is present in fetched evidence from `src_nmdoh_hps_2026_first_case_prior_year_summary`, specifically in `chunk_src_nmdoh_hps_2026_first_case_prior_year_summary_001`: "seven cases in 2025" and "three of them fatal." This means the issue was not missing fetch and not missing chunking. The likely failure occurred when deterministic extraction did not convert spelled-out annual count/death phrases into structured fields, and normalization/linking kept the record anchored to the 2026 press release event.

## 7. Validation ground truth audit

The validation record is manually curated:

- `linked_event_id`: `event_new_mexico_hps_2025`
- `disease`: `Hantavirus disease`
- `virus_or_syndrome`: `HPS`
- `geographic_scope`: `subnational`
- `subnational_location`: `New Mexico`
- `date_anchor`: `2025`
- `date_anchor_field`: `reporting_period`
- `reporting_period`: `2025`
- `statistical_count_type`: `annual`
- `cases_unspecified`: `7`
- `deaths`: blank
- `source_id`: `src_nmdoh_hps_cases_by_county_1975_2025_pdf`
- `ground_truth_role`: `held_out_validation`

The ground truth source is held out, not mixed into collection, and PDF/OCR is not automated in this workflow.

## 8. Evaluation report audit

Evaluation row outcomes:

- Four rows were `missing_validation_record`: collection produced 2024/2026 event-level records without matching held-out validation records.
- One row was `missing_collection_record`: held-out 2025 annual validation record had no collection counterpart with `reporting_period=2025` and `cases_unspecified=7`.
- All five rows had `masking_compliance_status=passed`.
- All five rows had `human_review_flag=true`.

This is not a source masking failure. The reserved source never entered collection records. The mismatch is an extraction and statistical-scope issue: fetched collection text contains relevant annual language, but deterministic extraction did not structure the 2025 annual case count, and evaluation compared annual validation against event-level collection records.

## 9. Diagnosis

The most likely failure chain is:

1. Real NMDOH HTML was fetched successfully.
2. Relevant text was present in clean text and supporting evidence.
3. Chunking retained the relevant prior-year 2025 annual sentence.
4. Data presence detected case-count and death-count signals.
5. Deterministic extraction produced records but did not populate numeric case/death fields.
6. Normalization/linking anchored the prior-year sentence to a 2026 press-release record, not to a 2025 annual validation key.
7. Evaluation correctly reported no comparable collection record.

## 10. What Stage 4C proves

Stage 4C proves that controlled real-source live fetch can run with explicit source-id allowlisting, context-only guardrails, and held-out validation masking. It also proves the evaluation layer can detect a failed match without leaking the validation source into collection.

## 11. What Stage 4C does not prove

Stage 4C does not prove extraction accuracy for real NMDOH HTML. It does not prove annual surveillance count extraction. It does not prove PDF/OCR support. It does not prove that event-level press releases are directly comparable to annual county/year validation records.

## 12. Recommended next step

Recommended next technical stage: `Stage 4E - Controlled LLM extraction on already-fetched New Mexico HTML text`.

This recommendation is conditional and conservative: use only already-fetched/allowlisted NMDOH HTML text, do not rerun broad web search, do not fetch validation-reserved PDF, and compare LLM extraction against deterministic output. In parallel, keep deterministic pattern updates as a follow-up path for annual phrases such as spelled-out counts and fatality summaries.
