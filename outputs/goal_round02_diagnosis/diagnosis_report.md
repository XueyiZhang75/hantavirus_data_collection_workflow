# Goal Round 02 Diagnosis

## Session Summary
### goal_round02_west_nile_california_2024_08
- status: completed; duration_sec: 816.7; events: 193
- quality: no_primary_case_dataset_records; primary_case_dataset_status: no_primary_case_dataset_records
- search: candidates=41, executed_queries=7, raw_results=56, verified_targets=0
- documents=33; usable_task_docs=8; coverage=records_quarantined / no_target_coverage
- extraction: chunks=540, extractable=434, llm_calls=30, empty=16, raw=50, normalized=49
- records: pre_quality=49, final=0, quarantine=0, pending=49, rejected=1
- inclusion statuses: `{'pending_human_review': 49}`
- accepted metrics: `{}`
- blocking: `{'source_trust_requires_human_review': 49, 'record_period_too_broad_for_task_window': 3, 'source_role_final_excluded': 35, 'record_period_semantics_not_exact_for_task_window': 15, 'chunk_not_extractable_for_task_disease': 2, 'validation_outside_scope': 7, 'record_as_of_date_outside_task_window': 2}`

### goal_round02_mpox_drc_2024_08
- status: completed; duration_sec: 789.1; events: 172
- quality: partial_with_quarantined_records; primary_case_dataset_status: no_primary_case_dataset_records
- search: candidates=29, executed_queries=4, raw_results=30, verified_targets=0
- documents=26; usable_task_docs=6; coverage=target_official_source_accepted / complete_target_coverage
- extraction: chunks=1213, extractable=907, llm_calls=30, empty=18, raw=35, normalized=35
- records: pre_quality=35, final=5, quarantine=11, pending=19, rejected=0
- inclusion statuses: `{'quarantined_exposure_monitoring': 2, 'pending_human_review': 19, 'quarantined_outside_scope': 5, 'accepted_with_warnings': 5, 'quarantined_schema_invalid': 2, 'quarantined_chunk_not_task_relevant': 2}`
- accepted metrics: `{'outbreak_count': 1, 'other': 2, 'lab_positivity_percent': 2}`
- blocking: `{'primary_case_dataset_eligible_false': 4, 'exposure_monitoring_language': 2, 'not_primary_case_record': 4, 'claim_observation_type_surveillance_summary': 2, 'no_corroborated_primary_case_event': 4, 'record_geography_broader_than_task': 3, 'source_trust_requires_human_review': 19, 'record_as_of_date_outside_task_window': 5, 'record_period_outside_task_window': 5, 'missing_direct_collection_metric': 2, 'claim_observation_type_outbreak_summary': 2, 'record_period_semantics_not_exact_for_task_window': 5, 'chunk_not_extractable_for_task_disease': 2, 'record_period_too_broad_for_task_window': 6, 'record_geography_inherited_without_source_evidence': 4, 'validation_outside_scope': 1, 'record_date_outside_task_window': 4}`

### goal_round02_salmonella_us_2024_05_07
- status: completed; duration_sec: 696.9; events: 217
- quality: partial_with_quarantined_records; primary_case_dataset_status: primary_case_records_present
- search: candidates=50, executed_queries=8, raw_results=64, verified_targets=0
- documents=45; usable_task_docs=15; coverage=target_official_source_accepted / complete_target_coverage
- extraction: chunks=820, extractable=720, llm_calls=30, empty=21, raw=19, normalized=19
- records: pre_quality=19, final=5, quarantine=4, pending=10, rejected=0
- inclusion statuses: `{'accepted_with_warnings': 5, 'quarantined_outside_scope': 4, 'pending_human_review': 10}`
- accepted metrics: `{'case_count': 2, 'hospitalization_count': 1, 'death_count': 2}`
- blocking: `{'record_as_of_date_outside_task_window': 4, 'source_trust_requires_human_review': 10, 'source_role_final_excluded': 1}`

## Node Matrix
| # | node | west_nile_ca | mpox_drc | salmonella_us |
|---:|---|---|---|---|
| 1 | `task_intake_and_scope_planning` | completed (4ms) | completed (2ms) | completed (4ms) |
| 2 | `disease_intelligence_builder` | completed (52614ms) | completed (60178ms) | completed (57005ms) |
| 3 | `profile_and_schema_setup` | completed (5ms) | completed (3ms) | completed (4ms) |
| 4 | `executable_source_planning` | completed (61309ms) | completed (61132ms) | completed (59952ms) |
| 5 | `query_strategy_builder` | completed (9ms) | completed (10ms) | completed (11ms) |
| 6 | `source_discovery` | completed (186976ms) | completed (150267ms) | completed (176696ms) |
| 7 | `source_dedup_and_registry` | completed (21ms) | completed (18ms) | completed (21ms) |
| 8 | `source_screening` | completed (32ms) | completed (23ms) | completed (31ms) |
| 9 | `source_critic_and_uncertainty_routing` | completed (76091ms) | completed (62490ms) | completed (79438ms) |
| 10 | `content_fetch_and_parse` | completed (35226ms) | completed (78770ms) | completed (61786ms) |
| 11 | `document_quality_check` | completed (678ms) | completed (2392ms) | completed (2115ms) |
| 12 | `evidence_chunking_and_data_presence_flagging` | completed (1048ms) | completed (3512ms) | completed (3189ms) |
| 13 | `structured_extraction` | completed (401305ms) | completed (368342ms) | completed (255294ms) |
| 14 | `schema_validation_and_repair` | completed (300ms) | completed (289ms) | completed (166ms) |
| 15 | `record_normalization` | completed (184ms) | completed (284ms) | completed (179ms) |
| 16 | `record_linking` | completed (112ms) | completed (111ms) | completed (131ms) |
| 17 | `cross_source_consistency_check` | completed (144ms) | completed (134ms) | completed (157ms) |
| 18 | `quality_gate_routing` | completed (113ms) | completed (128ms) | completed (144ms) |
| 19 | `human_review` | pending | pending | pending |
| 20 | `final_data_package_builder` | completed (327ms) | completed (740ms) | completed (330ms) |

## Cross-session Totals
- run_quality_status_counts: `{'no_primary_case_dataset_records': 1, 'partial_with_quarantined_records': 2}`
- primary_case_dataset_status_counts: `{'no_primary_case_dataset_records': 2, 'primary_case_records_present': 1}`
- blocking_reason_counts_total: `{'source_trust_requires_human_review': 78, 'record_period_too_broad_for_task_window': 9, 'source_role_final_excluded': 36, 'record_period_semantics_not_exact_for_task_window': 20, 'chunk_not_extractable_for_task_disease': 4, 'validation_outside_scope': 8, 'record_as_of_date_outside_task_window': 11, 'primary_case_dataset_eligible_false': 4, 'exposure_monitoring_language': 2, 'not_primary_case_record': 4, 'claim_observation_type_surveillance_summary': 2, 'no_corroborated_primary_case_event': 4, 'record_geography_broader_than_task': 3, 'record_period_outside_task_window': 5, 'missing_direct_collection_metric': 2, 'claim_observation_type_outbreak_summary': 2, 'record_geography_inherited_without_source_evidence': 4, 'record_date_outside_task_window': 4}`
- warning_counts_total: `{'accepted_task_aware_non_primary_observation': 73, 'accepted_direct_collection_official_aggregate': 73, 'source_trust_requires_human_review': 78, 'validation_outside_scope_audit_only': 12, 'accepted_with_review_warning': 16, 'metric_period_partially_overlaps_task_window': 1}`
- source_role_counts_seen_in_records: `{'collection': 134, 'excluded': 72}`
- metric_category_counts_seen_in_records: `{'case_count': 134, 'death_count': 30, 'other': 8, 'outbreak_count': 6, 'lab_positivity_percent': 10, 'lab_positive_count': 2, 'lab_test_count': 4, 'hospitalization_count': 10, 'hospitalization_rate': 2}`