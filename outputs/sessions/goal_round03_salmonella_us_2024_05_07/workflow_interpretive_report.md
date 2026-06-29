# Data Collection Result Interpretation Report

## 1. Task

- disease: `Salmonella`
- location: `United States`
- date range: `2024-05-01 to 2024-07-31`
- target fields: cases, deaths, dates, locations, source URLs, source types, evidence quotes
- collection mode: `task_aware_quality_gated_records`
- session id: `goal_round03_salmonella_us_2024_05_07`
- live search: `True`
- live fetch: `True`
- LLM stages: `True`
- search provider: `tavily`

## 2. One-sentence conclusion

The workflow produced 5 accepted primary case dataset records; these records still require expert review of source identity, corroboration status, and human review outcomes before final use.

## 3. Final data status

| Field | Value |
| --- | --- |
| final_case_dataset_count | 5 |
| global_outbreak_event_dataset_count | 0 |
| regional_surveillance_dataset_count | 0 |
| country_year_aggregate_dataset_count | 0 |
| official_alert_dataset_count | 0 |
| task_aware_data_product_count | 5 |
| final_dataset_count | 8 |
| final_dataset_pre_quality_gate_count | 15 |
| zero_case_statement_count | 0 |
| exposure_monitoring_record_count | 0 |
| surveillance_summary_record_count | 5 |
| outbreak_summary_record_count | 0 |
| context_record_count | 0 |
| unclassified_observation_count | 3 |
| non_primary_observation_count | 4 |
| quarantined_record_count | 6 |
| pending_review_record_count | 1 |
| final_dataset_post_review_count | 8 |
| run_quality_status | partial_with_quarantined_records |
| primary_case_dataset_status | primary_case_records_present |
| suitable_as_final_epidemiological_dataset | False |

## 3.1 Coverage and extraction status

- coverage_status: `target_official_source_accepted`
- source verification chain: predicted=1, discovered=1, fetched=1, fetch_failed=1, parsed=1, unusable=1, chunks=415, records=15, extracted=1, accepted=1
- official_extraction_failure_reasons: `{'must_fetch_source_not_attempted_for_extraction': 7, 'must_fetch_source_partially_skipped_due_to_chunk_cap': 13}`

## 4. Primary case dataset findings

- disease=Salmonellosis (non-typhoidal Salmonella); location=United States of America; date=2024-07-31; hospitalizations=24.0; source=Reoccurring Salmonella Cotham Outbreak Linked to Pet Bearded Dragons — United States, 2024  | MMWR; publisher=Centers for Disease Control and Prevention; url=https://www.cdc.gov/mmwr/volumes/74/wr/mm7431a1.htm?ACSTrackingID=USCDC_921-DM149359&ACSTrackingLabel=Week+in+MMWR%3A+Vol.+74%2C+August+21%2C+2025&deliveryName=USCDC_921-DM149359; corroboration_status=conflicting_claims; independent_source_count=3; evidence=| ****Hospitalization (n = 24)**** | |
- disease=Salmonellosis (non-typhoidal Salmonella); location=United States of America; date=2024-07-31; cases_unspecified=551.0; source=Outbreak Investigation of Salmonella: Cucumbers (June 2024) - FDA; publisher=unknown publisher; url=https://www.fda.gov/food/outbreaks-foodborne-illness/outbreak-investigation-salmonella-cucumbers-june-2024; corroboration_status=conflicting_claims; independent_source_count=3; evidence=Total Illnesses: 551
- disease=Salmonellosis (non-typhoidal Salmonella); location=United States of America; date=2024-07-31; hospitalizations=155.0; source=Outbreak Investigation of Salmonella: Cucumbers (June 2024) - FDA; publisher=unknown publisher; url=https://www.fda.gov/food/outbreaks-foodborne-illness/outbreak-investigation-salmonella-cucumbers-june-2024; corroboration_status=conflicting_claims; independent_source_count=3; evidence=Hospitalizations: 155
- disease=Salmonellosis (non-typhoidal Salmonella); location=United States of America; date=2024-07-31; cases_confirmed=7314.0, cases_unspecified=9219.0; source=FoodNet 2024 Preliminary Data | FoodNet | CDC; publisher=Centers for Disease Control and Prevention; url=https://www.cdc.gov/foodnet/reports/preliminary-data.html; corroboration_status=conflicting_claims; independent_source_count=3; evidence=Among 9,219 *Salmonella* infections reported, 7,314 (79%) infections had positive culture results.
- disease=Salmonellosis (non-typhoidal Salmonella); location=United States of America; date=2024-07-31; cases_unspecified=6066.0; source=FoodNet 2024 Preliminary Data | FoodNet | CDC; publisher=Centers for Disease Control and Prevention; url=https://www.cdc.gov/foodnet/reports/preliminary-data.html; corroboration_status=conflicting_claims; independent_source_count=3; evidence=Among the positive culture results, laboratories fully serotyped 6,066 (83%) isolates. The most common serotypes detected were

## 5. Global/task-aware dataset views

No global/task-aware dataset view contains records.

## 5. Useful non-case public-health observations

- surveillance summaries: 5. These are useful public-health observations but not confirmed cases unless separately accepted as primary case records.
- unclassified observations: 3. These are useful public-health observations but not confirmed cases unless separately accepted as primary case records.
- non-primary observations: 4. These are useful public-health observations but not confirmed cases unless separately accepted as primary case records.
Zero-case and exposure-monitoring observations are not confirmed cases; context/background evidence is useful but not a case count.

## 6. Cross-source corroboration

- claim_count: `16`
- claim_comparison_count: `120`
- corroborated_event_count: `2`
- corroborated_primary_case_event_count: `0`
- conflicting_claim_count: `8`
- single_source_unverified_count: `1`
These fields describe cross-source support, single-source unverified evidence, or conflicts. They do not establish automatic truth determination.

## 7. Source quality and credibility

- source_candidate_count: `32`
- fetched_document_count: `28`
- source_identity_assessed_count: `32`
- actual_publisher_unknown_count: `10`
- source_type_counts: `{'national_public_health_agency': 15, 'official_public_health_agency': 7, 'academic_or_peer_reviewed_source': 5, 'social_media': 1, 'news_media': 3, 'structured_database': 1}`
- source_critic_assessed_count: `0`
Sources are described as official, news, context-only, or unknown only when the source identity artifacts support that label.

## 8. Validation status

- validation_source_compatibility_status: `validation_source_empty`
- validation_mode: `diagnostic_only`
- active_validation_record_count: `0`
- inactive_validation_record_count: `0`
- validation_limited: `False`

## 9. Excluded / quarantined evidence

- quarantined_record_count: `6`
- pending_review_record_count: `1`
These records did not enter the primary case dataset. Inspect quarantined_records and record_inclusion_decisions for exclusion reasons.

## 10. Human review priorities

- human_review_item_count: `45`
- Review source scope mismatch, validation limitation, publisher uncertainty, and single-source unverified claims first.
- review_source_credibility_src_search_5851bdcbd35f: missing_publisher
- review_source_src_search_5851bdcbd35f: Source classified as data_source; both screening and critic agree to include for content fetch.
- review_source_credibility_src_search_33733b13ba13: missing_publisher
- review_source_src_search_33733b13ba13: Source classified as data_source; both screening and critic agree to include for content fetch.
- review_source_credibility_src_search_3faf6631782d: missing_publisher

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
