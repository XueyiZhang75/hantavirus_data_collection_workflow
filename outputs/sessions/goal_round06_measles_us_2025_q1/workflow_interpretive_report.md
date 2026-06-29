# Data Collection Result Interpretation Report

## 1. Task

- disease: `Measles`
- location: `United States`
- date range: `2025-01-01 to 2025-03-31`
- target fields: cases, deaths, dates, locations, source URLs, source types, evidence quotes
- collection mode: `task_aware_quality_gated_records`
- session id: `goal_round06_measles_us_2025_q1`
- live search: `True`
- live fetch: `True`
- LLM stages: `True`
- search provider: `tavily`

## 2. One-sentence conclusion

The workflow technically completed search, fetch, extraction, filtering, and export steps, but no accepted primary case dataset records were found; therefore the output is not suitable as a final epidemiological dataset for the target location.

## 3. Final data status

| Field | Value |
| --- | --- |
| final_case_dataset_count | 0 |
| global_outbreak_event_dataset_count | 0 |
| regional_surveillance_dataset_count | 0 |
| country_year_aggregate_dataset_count | 0 |
| official_alert_dataset_count | 0 |
| task_aware_data_product_count | 0 |
| final_dataset_count | 1 |
| final_dataset_pre_quality_gate_count | 72 |
| zero_case_statement_count | 0 |
| exposure_monitoring_record_count | 0 |
| surveillance_summary_record_count | 3 |
| outbreak_summary_record_count | 7 |
| context_record_count | 6 |
| unclassified_observation_count | 7 |
| non_primary_observation_count | 13 |
| quarantined_record_count | 17 |
| pending_review_record_count | 54 |
| final_dataset_post_review_count | 1 |
| run_quality_status | partial_with_quarantined_records |
| primary_case_dataset_status | no_primary_case_dataset_records |
| suitable_as_final_epidemiological_dataset | False |

## 3.1 Coverage and extraction status

- coverage_status: `target_official_source_accepted`
- source verification chain: predicted=1, discovered=1, fetched=1, fetch_failed=1, parsed=1, unusable=1, chunks=1003, records=73, extracted=1, accepted=1
- official_extraction_failure_reasons: `{'must_fetch_source_not_attempted_for_extraction': 27, 'must_fetch_source_partially_skipped_due_to_chunk_cap': 4}`

## 4. Primary case dataset findings

No accepted primary case dataset records were produced.
Evidence found in zero-case, exposure monitoring, context, quarantined, or other views may be useful, but it does not directly answer the primary case-data question.

## 5. Global/task-aware dataset views

No global/task-aware dataset view contains records.

## 5. Useful non-case public-health observations

- surveillance summaries: 3. These are useful public-health observations but not confirmed cases unless separately accepted as primary case records.
- outbreak summaries: 7. These are useful public-health observations but not confirmed cases unless separately accepted as primary case records.
- context/background records: 6. These are useful public-health observations but not confirmed cases unless separately accepted as primary case records.
- unclassified observations: 7. These are useful public-health observations but not confirmed cases unless separately accepted as primary case records.
- non-primary observations: 13. These are useful public-health observations but not confirmed cases unless separately accepted as primary case records.
Zero-case and exposure-monitoring observations are not confirmed cases; context/background evidence is useful but not a case count.

## 6. Cross-source corroboration

- claim_count: `82`
- claim_comparison_count: `3321`
- corroborated_event_count: `15`
- corroborated_primary_case_event_count: `0`
- conflicting_claim_count: `9`
- single_source_unverified_count: `13`
These fields describe cross-source support, single-source unverified evidence, or conflicts. They do not establish automatic truth determination.

## 7. Source quality and credibility

- source_candidate_count: `48`
- fetched_document_count: `45`
- source_identity_assessed_count: `48`
- actual_publisher_unknown_count: `20`
- source_type_counts: `{'national_public_health_agency': 7, 'official_public_health_agency': 11, 'social_media': 2, 'academic_or_peer_reviewed_source': 4, 'secondary_aggregator': 1, 'international_public_health_agency': 8, 'structured_database': 3, 'unknown': 6, 'news_media': 3, 'state_or_local_public_health_agency': 2, 'background_fact_sheet': 1}`
- source_critic_assessed_count: `0`
Sources are described as official, news, context-only, or unknown only when the source identity artifacts support that label.

## 8. Validation status

- validation_source_compatibility_status: `validation_source_empty`
- validation_mode: `diagnostic_only`
- active_validation_record_count: `0`
- inactive_validation_record_count: `0`
- validation_limited: `False`

## 9. Excluded / quarantined evidence

- quarantined_record_count: `17`
- pending_review_record_count: `54`
These records did not enter the primary case dataset. Inspect quarantined_records and record_inclusion_decisions for exclusion reasons.

## 10. Human review priorities

- human_review_item_count: `115`
- Review source scope mismatch, validation limitation, publisher uncertainty, and single-source unverified claims first.
- review_source_credibility_src_search_cd5fb2750261: missing_publisher
- review_source_src_search_cd5fb2750261: Source classified as data_source; both screening and critic agree to include for content fetch.
- review_source_src_search_2eb069f08192: Screening and critic disagree on this source; routing to human review for resolution.
- review_source_credibility_src_search_62409e4d2cf9: missing_publisher
- review_source_src_search_62409e4d2cf9: Source classified as data_source; both screening and critic agree to include for content fetch.

## 11. Can this be used as a final epidemiological dataset?

- suitable_as_final_epidemiological_dataset: `False`
If false, the output should not be used directly as a final case dataset. It can still be used for evidence audit and expert review.

## 12. Recommended next steps

- Do not treat this run as a final primary case dataset.
- Inspect final_case_dataset before using any case-count output.
- Review quarantined_records and record_inclusion_decisions for excluded evidence.
- Review source_identity_summary and source_identity_assessments for publisher uncertainty.
- Review corroboration_summary before treating any claim as cross-source supported.
- Apply human review decisions in a separate review pass if needed.

## 13. Key artifact index

- `workflow_interpretive_report_chinese.md`
- `workflow_interpretive_report.md`
- `workflow_interpretive_report_summary.json`
- `workflow_run_report_chinese.md`
- `workflow_run_summary.json`
- `collection/final_case_dataset.csv`
- `collection/final_case_dataset.json`
- `collection/global_outbreak_event_dataset.csv`
- `collection/regional_surveillance_dataset.csv`
- `collection/country_year_aggregate_dataset.csv`
- `collection/official_alert_dataset.csv`
- `collection/final_dataset.csv`
- `collection/final_dataset_pre_quality_gate.csv`
- `collection/zero_case_statements.csv`
- `collection/exposure_monitoring_records.csv`
- `collection/context_records.csv`
- `collection/quarantined_records.csv`
- `diagnostics/run_quality_summary.json`
- `diagnostics/corroboration_summary.json`
- `diagnostics/source_identity_summary.json`
- `diagnostics/validation_source_compatibility_summary.json`

## 14. Important disclaimer

Note: This report interprets evidence collected by the workflow. It is not an official surveillance conclusion, medical advice, or automatic truth determination. Expert review is still required.
