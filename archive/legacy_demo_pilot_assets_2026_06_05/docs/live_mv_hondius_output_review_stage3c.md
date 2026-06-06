# Live MV Hondius Output Review - Stage 3C

## 1. Purpose

Stage 3C reviews the Stage 3B live MV Hondius masked-validation outputs before choosing the next experimental path. This stage does not modify workflow code, tests, graph topology, source overlays, live scripts, or source-role policy files. It does not rerun live fetch or call an external LLM.

## 2. Stage 3B Output Summary

All expected Stage 3B artifacts were present under `outputs/live_masked_validation_mv_hondius/`.

Key results:

- Collection records: 2.
- Validation ground truth records: 1.
- Evaluation rows: 2.
- `overall_match_status_counts`: `missing_collection_record=1`, `missing_validation_record=1`.
- `masking_compliance_status_counts`: `passed=2`.
- `reserved_source_leakage_count`: 0.
- `human_review_flagged_row_count`: 2.
- LLM extraction: disabled.
- Broad web search: not used.

## 3. Source Masking Audit

WHO DON600 source masking passed at the technical source-ID level.

- `src_who_don600_mv_hondius_2026` appears in `collection/source_registry.json`.
- WHO `source_role` is `validation_reserved`.
- WHO `final_screening_decision` is `reserved_for_validation`.
- WHO `ready_for_content_fetch` is `false`.
- WHO does not appear in `collection/final_dataset.csv`.
- `diagnostics/source_leakage_check.json` reports `reserved_source_leakage_count=0`.
- `evaluation/evaluation_summary.json` also reports `reserved_source_leakage_count=0`.

The leakage diagnostics and evaluation summary agree.

## 4. Live Fetch Quality Audit

Requested source IDs:

- `src_reuters_mv_hondius_2026_05_27`
- `src_vdh_hantavirus_mv_hondius_context`

Fetched/responded source IDs:

- `src_reuters_mv_hondius_2026_05_27`
- `src_vdh_hantavirus_mv_hondius_context`

Usable fetched source IDs:

- `src_vdh_hantavirus_mv_hondius_context`

Access/quality-limited source IDs:

- `src_reuters_mv_hondius_2026_05_27`

Reuters returned `http_status_code=401`, `parse_status=parsed_html`, and `quality_status=unusable` with `insufficient_clean_text`. This should be interpreted as an access/quality limitation. No access-control bypass was attempted.

VDH returned `http_status_code=200`, `parse_status=parsed_html`, and `quality_status=usable`.

No source failed due to network in the final Stage 3B output. Reuters responded but did not yield usable article text.

## 5. Collection Record Audit

Both collection records came from VDH, not Reuters.

### `rec_src_vdh_hantavirus_mv_hondius_context_001`

- `source_id`: `src_vdh_hantavirus_mv_hondius_context`
- `source_type`: `official_public_health_agency`
- `source_url`: `https://www.vdh.virginia.gov/hantavirus`
- `disease`: `Hantavirus disease`
- `virus_or_syndrome`: `HPS`
- `country`: blank
- `geographic_scope`: blank
- `subnational_location`: blank
- `date_reported`: `2026`
- `date_anchor`: `2026`
- `reporting_period`: blank
- `statistical_count_type`: blank
- `cases_unspecified`, `cases_confirmed`, `cases_probable`, `deaths`: blank
- `evidence_quote` preview: VDH page text says WHO was notified on May 2, 2026 of a possible MV Hondius outbreak and that multiple cases, including fatal cases, had been reported.
- `supporting_chunk_id`: `chunk_src_vdh_hantavirus_mv_hondius_context_001`
- `linked_event_id`: `event_001`
- `requires_human_review`: `True`
- `normalization_warnings`: `missing_geography`
- `record_linking_warnings`: `existing_record_requires_human_review`

### `rec_src_vdh_hantavirus_mv_hondius_context_002`

- `source_id`: `src_vdh_hantavirus_mv_hondius_context`
- `source_type`: `official_public_health_agency`
- `source_url`: `https://www.vdh.virginia.gov/hantavirus`
- `disease`: `Hantavirus disease`
- `virus_or_syndrome`: `HPS`
- `country`: blank
- `geographic_scope`: blank
- `subnational_location`: blank
- `date_reported`: `2026`
- `date_anchor`: `2026`
- `reporting_period`: blank
- `statistical_count_type`: blank
- `cases_unspecified`, `cases_confirmed`, `cases_probable`, `deaths`: blank
- `evidence_quote` preview: VDH page text describes HPS symptoms, fatality risk, and lists WHO/CDC/VDH resources.
- `supporting_chunk_id`: `chunk_src_vdh_hantavirus_mv_hondius_context_003`
- `linked_event_id`: `event_001`
- `requires_human_review`: `True`
- `normalization_warnings`: `missing_geography`
- `record_linking_warnings`: `existing_record_requires_human_review`

Answers:

- No collection record came from Reuters.
- Both collection records came from VDH.
- The VDH records are likely context-derived false positives or weak context-derived extraction artifacts, not robust case-count collection records.
- No collection record aligns with the WHO ground truth event key.
- Blocking fields include virus/syndrome (`HPS` vs `Andes virus`), date (`2026` vs `2026-05-08`), geographic scope (blank vs `Multi-country / MV Hondius cruise ship`), reporting period, statistical count type, and absent numeric case/death counts.

## 6. Validation Ground Truth Audit

Manual validation record:

- `record_id`: `gt_who_don600_mv_hondius_2026_001`
- `linked_event_id`: `event_mv_hondius_2026`
- `disease`: `Hantavirus disease`
- `virus_or_syndrome`: `Andes virus`
- `geographic_scope`: `Multi-country / MV Hondius cruise ship`
- `date_anchor`: `2026-05-08`
- `reporting_period`: `as of 2026-05-08`
- `statistical_count_type`: `outbreak_cumulative_as_of_report_date`
- `cases_unspecified`: `8`
- `cases_confirmed`: `6`
- `cases_probable`: `2`
- `deaths`: `3`
- `source_id`: `src_who_don600_mv_hondius_2026`
- `evidence_quote` preview: "As of 8 May, eight cases including three deaths were reported."
- `curation_note`: Manual ground truth curated before automated evaluation; used only after collection output is exported.

Answers:

- The validation ground truth is manually curated.
- It is clearly marked `held_out_validation`.
- It is not mixed into collection output.
- Its comparison key does not align with either VDH collection record.

## 7. Evaluation Report Audit

### `eval_001`

- `overall_match_status`: `missing_collection_record`
- `masking_compliance_status`: `passed`
- `provenance_completeness_status`: `not_applicable_no_collection_record`
- `human_review_flag`: `true`
- `review_reason`: Held-out validation record had no collection counterpart.
- `collection_source_ids`: blank
- `validation_source_ids`: `src_who_don600_mv_hondius_2026`
- `collection_case_count`: blank
- `validation_case_count`: `6`
- `collection_death_count`: blank
- `validation_death_count`: `3`
- `field_level_match_status`: `case_count_not_comparable;death_count_not_comparable`

### `eval_002`

- `overall_match_status`: `missing_validation_record`
- `masking_compliance_status`: `passed`
- `provenance_completeness_status`: `complete`
- `human_review_flag`: `true`
- `review_reason`: Collection record could not be validated against held-out records.
- `collection_source_ids`: `src_vdh_hantavirus_mv_hondius_context`
- `validation_source_ids`: blank
- `collection_case_count`: blank
- `validation_case_count`: blank
- `collection_death_count`: blank
- `validation_death_count`: blank
- `field_level_match_status`: `case_count_not_comparable;death_count_not_comparable`

The missing collection row exists because WHO ground truth has no aligned collection counterpart. The missing validation row exists because VDH-derived collection records form a different comparison key and do not align with the manual WHO record.

This is not a source masking failure because reserved source leakage is zero and WHO was blocked from collection. It is an extraction/alignment limitation and is appropriate to present as a diagnostic pilot if framed conservatively.

## 8. Context-Only Extraction Diagnosis

The overlay configures `src_vdh_hantavirus_mv_hondius_context` as context-only through `context_only_source_ids`.

However, the current source-screening path does not enforce `context_only_source_ids` as an override. It only uses the source-role policy overlay for validation-reserved masking. In `source_screening.py`, metadata classification checks `expected_fields` and assigns `data_source` if any field is in `{cases, deaths, date, location}` before checking context fields. The VDH seed source includes `date` and `location`, so it was classified as `data_source`.

In `content_processing.py`, fetch purpose is based on `final_screening_decision`; because VDH was routed as `include_for_content_fetch`, it received `fetch_purpose=data_extraction`.

In evidence chunking, text from usable documents can be marked `contains_target_data` when it has enough deterministic data signals. VDH text contains terms such as outbreak, cases, fatal cases, date, and location.

In `extraction.py`, deterministic extraction filters by `contains_target_data`, `fetch_purpose`, chunk kind, and non-empty text. It does not filter out context-only source IDs.

Likely reason VDH produced collection records:

- VDH overlay metadata says context-only.
- The base deterministic classifier did not enforce that metadata.
- VDH expected fields include `date` and `location`, causing `data_source`.
- VDH page text contains outbreak/case/date/location signals.
- The extraction step then produced weak records without numeric case/death counts.

Best description: this is primarily a policy enforcement gap plus a semantic extraction false positive. It is not a source masking failure. It also creates a normalization/linking mismatch because the resulting records lack geography and exact event/date/count fields.

## 9. What Stage 3B Proves

- Case-specific overlays can be loaded without changing default deterministic behavior.
- WHO DON600 can be registered and blocked as held-out validation.
- Reserved-source leakage checking works.
- The live pilot can create collection, validation, evaluation, diagnostics, and professor-facing artifacts.
- The evaluation correctly refuses to claim a match and routes unresolved rows to human review.

## 10. What Stage 3B Does Not Prove

- It does not prove independent epidemiological validation.
- It does not prove Reuters extraction, because Reuters returned access/quality-limited text.
- It does not prove context-only policy enforcement.
- It does not prove broad web search.
- It does not prove automated WHO validation scraping.
- It does not prove LLM extraction quality.

## 11. Recommended Next Step

Recommended next implementation stage:

Stage 3D - implement a context-only extraction guardrail and rerun the MV Hondius pilot, if the next goal is to harden the current pipeline.

Conditional alternative:

If the professors prefer a cleaner live validation example with accessible non-held-out primary sources, Stage 3D should instead design and implement the New Mexico backup case.

Do not add LLM extraction yet. First close the context-only policy gap or explicitly present Stage 3B as a negative/diagnostic pilot.
