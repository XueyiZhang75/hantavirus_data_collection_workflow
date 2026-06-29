# Data Collection Result Interpretation Report

## 1. Task

- disease: `Legionnaires' disease`
- location: `New York City`
- date range: `2025-08-01 to 2025-08-31`
- target fields: cases, deaths, dates, locations, source URLs, source types, evidence quotes
- collection mode: `task_aware_quality_gated_records`
- session id: `goal_round03_legionnaires_nyc_2025_08`
- live search: `True`
- live fetch: `True`
- LLM stages: `True`
- search provider: `tavily`

## 2. One-sentence conclusion

The workflow produced 2 accepted primary case dataset records; these records still require expert review of source identity, corroboration status, and human review outcomes before final use.

## 3. Final data status

| Field | Value |
| --- | --- |
| final_case_dataset_count | 2 |
| global_outbreak_event_dataset_count | 0 |
| regional_surveillance_dataset_count | 0 |
| country_year_aggregate_dataset_count | 0 |
| official_alert_dataset_count | 0 |
| task_aware_data_product_count | 2 |
| final_dataset_count | 2 |
| final_dataset_pre_quality_gate_count | 43 |
| zero_case_statement_count | 0 |
| exposure_monitoring_record_count | 0 |
| surveillance_summary_record_count | 0 |
| outbreak_summary_record_count | 0 |
| context_record_count | 9 |
| unclassified_observation_count | 4 |
| non_primary_observation_count | 4 |
| quarantined_record_count | 9 |
| pending_review_record_count | 32 |
| final_dataset_post_review_count | 2 |
| run_quality_status | partial_with_quarantined_records |
| primary_case_dataset_status | primary_case_records_present |
| suitable_as_final_epidemiological_dataset | False |

## 3.1 Coverage and extraction status

- coverage_status: `records_quarantined`
- source verification chain: predicted=1, discovered=1, fetched=1, fetch_failed=1, parsed=1, unusable=1, chunks=218, records=45, extracted=1, accepted=0
- failure_stage: `records_quarantined`.
- official_extraction_failure_reasons: `{'must_fetch_source_partially_skipped_due_to_chunk_cap': 3, 'must_fetch_source_not_attempted_for_extraction': 5}`

## 4. Primary case dataset findings

- disease=Legionnaires' disease; location=United States of America; date=2025-08-29; cases_unspecified=114.0, deaths=7.0, hospitalizations=90.0; source=New York City Health Department Closes Investigation of Central Harlem Legionnaires’ Disease Cluster - NYC Health; publisher=unknown publisher; url=https://www.nyc.gov/site/doh/about/press/pr2025/health-department-closes-investigation-central-harlem-legionnaires-cluster.page; corroboration_status=conflicting_claims; independent_source_count=6; evidence=![NYC](/assets/home/images/global/nyc_white.png) ![](/assets/home/images/global/upper-header-divider.gif) ![](/assets/home/images/global/upper-header-divider.gif) ![NYC Health](/assets/doh/images/content/header/logo.p...
- disease=Legionnaires' disease; location=United States of America; date=2025-08-29; cases_unspecified=104.0; source=New York City Health Department Closes Investigation of Central Harlem Legionnaires’ Disease Cluster - NYC Health; publisher=unknown publisher; url=https://www.nyc.gov/site/doh/about/press/pr2025/health-department-closes-investigation-central-harlem-legionnaires-cluster.page; corroboration_status=conflicting_claims; independent_source_count=6; evidence=![NYC](/assets/home/images/global/nyc_white.png) ![](/assets/home/images/global/upper-header-divider.gif) ![](/assets/home/images/global/upper-header-divider.gif) ![NYC Health](/assets/doh/images/content/header/logo.p...

## 5. Global/task-aware dataset views

No global/task-aware dataset view contains records.

## 5. Useful non-case public-health observations

- context/background records: 9. These are useful public-health observations but not confirmed cases unless separately accepted as primary case records.
- unclassified observations: 4. These are useful public-health observations but not confirmed cases unless separately accepted as primary case records.
- non-primary observations: 4. These are useful public-health observations but not confirmed cases unless separately accepted as primary case records.
Zero-case and exposure-monitoring observations are not confirmed cases; context/background evidence is useful but not a case count.

## 6. Cross-source corroboration

- claim_count: `60`
- claim_comparison_count: `1770`
- corroborated_event_count: `6`
- corroborated_primary_case_event_count: `0`
- conflicting_claim_count: `41`
- single_source_unverified_count: `2`
These fields describe cross-source support, single-source unverified evidence, or conflicts. They do not establish automatic truth determination.

## 7. Source quality and credibility

- source_candidate_count: `45`
- fetched_document_count: `27`
- source_identity_assessed_count: `45`
- actual_publisher_unknown_count: `36`
- source_type_counts: `{'official_public_health_agency': 18, 'social_media': 7, 'academic_or_peer_reviewed_source': 1, 'news_media': 10, 'structured_database': 1, 'national_public_health_agency': 5, 'state_or_local_public_health_agency': 1, 'background_fact_sheet': 1, 'secondary_aggregator': 1}`
- source_critic_assessed_count: `0`
Sources are described as official, news, context-only, or unknown only when the source identity artifacts support that label.

## 8. Validation status

- validation_source_compatibility_status: `validation_source_empty`
- validation_mode: `diagnostic_only`
- active_validation_record_count: `0`
- inactive_validation_record_count: `0`
- validation_limited: `False`

## 9. Excluded / quarantined evidence

- quarantined_record_count: `9`
- pending_review_record_count: `32`
These records did not enter the primary case dataset. Inspect quarantined_records and record_inclusion_decisions for exclusion reasons.

## 10. Human review priorities

- human_review_item_count: `88`
- Review source scope mismatch, validation limitation, publisher uncertainty, and single-source unverified claims first.
- review_source_credibility_src_search_b74bccc017c5: missing_publisher
- review_source_src_search_b74bccc017c5: Source classified as data_source; both screening and critic agree to include for content fetch.
- review_source_credibility_src_search_1596aec16d67: missing_publisher
- review_source_src_search_1596aec16d67: Source classified as data_source; both screening and critic agree to include for content fetch.
- review_source_credibility_src_search_743df961a25b: missing_publisher

## 11. Can this be used as a final epidemiological dataset?

- suitable_as_final_epidemiological_dataset: `False`
If false, the output should not be used directly as a final case dataset. It can still be used for evidence audit and expert review.

## 12. Recommended next steps

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
