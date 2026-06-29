# Goal Round 01 Diagnosis

## Session Summary
### goal_round01_covid19_new_york_2024_01_01_2024_01_07
- status: completed; duration_sec: 524.0; events: 189
- quality: no_records_extracted; primary_case_dataset_status: unknown_no_claim_outputs
- search: candidates=35, executed_queries=8, raw_results=58
- documents=31; usable_task_docs=10; coverage=parsed_no_records
- records: normalized=0, pre_quality=0, final=0, quarantine=0, pending=0
- final statuses: `{}`
- accepted metrics: `{}`
- blocking: `{}`

### goal_round01_dengue_florida_2025_06_01_2025_06_30
- status: completed; duration_sec: 635.2; events: 190
- quality: no_primary_case_dataset_records; primary_case_dataset_status: no_primary_case_dataset_records
- search: candidates=40, executed_queries=8, raw_results=64
- documents=31; usable_task_docs=9; coverage=records_quarantined
- records: normalized=43, pre_quality=43, final=0, quarantine=0, pending=43
- final statuses: `{'pending_human_review': 43}`
- accepted metrics: `{}`
- blocking: `{'source_role_final_excluded': 42, 'source_trust_requires_human_review': 43, 'validation_outside_scope': 4, 'record_period_too_broad_for_task_window': 15, 'ambiguous_metric_column_semantics': 9, 'record_period_semantics_not_exact_for_task_window': 5, 'record_as_of_date_outside_task_window': 5, 'record_date_outside_task_window': 4, 'record_period_outside_task_window': 4}`

### goal_round01_measles_texas_2025_01_01_2025_04_30
- status: completed; duration_sec: 692.0; events: 193
- quality: partial_with_quarantined_records; primary_case_dataset_status: primary_case_records_present
- search: candidates=44, executed_queries=8, raw_results=64
- documents=33; usable_task_docs=11; coverage=target_official_source_accepted
- records: normalized=23, pre_quality=23, final=8, quarantine=12, pending=3
- final statuses: `{'accepted_with_warnings': 8, 'pending_human_review': 3, 'quarantined_outside_scope': 10, 'quarantined_schema_invalid': 2}`
- accepted metrics: `{'case_count': 2, 'hospitalization_count': 3, 'death_count': 2, 'other': 1}`
- blocking: `{'source_trust_requires_human_review': 3, 'record_as_of_date_outside_task_window': 5, 'record_period_too_broad_for_task_window': 5, 'record_period_semantics_not_exact_for_task_window': 4, 'record_geography_broader_than_task': 5, 'missing_direct_collection_metric': 2, 'primary_case_dataset_eligible_false': 2, 'not_primary_case_record': 2, 'claim_observation_type_ambiguous_public_health_observation': 2, 'no_corroborated_primary_case_event': 2, 'record_period_outside_task_window': 3}`

## Node Matrix
| # | node | covid_ny | dengue_fl | measles_tx |
|---:|---|---|---|---|
| 1 | `task_intake_and_scope_planning` | completed (2ms) | completed (4ms) | completed (3ms) |
| 2 | `disease_intelligence_builder` | completed (38286ms) | completed (43677ms) | completed (74907ms) |
| 3 | `profile_and_schema_setup` | completed (5ms) | completed (4ms) | completed (3ms) |
| 4 | `executable_source_planning` | completed (56539ms) | completed (60119ms) | completed (62447ms) |
| 5 | `query_strategy_builder` | completed (8ms) | completed (9ms) | completed (9ms) |
| 6 | `source_discovery` | completed (194930ms) | completed (173464ms) | completed (187529ms) |
| 7 | `source_dedup_and_registry` | completed (24ms) | completed (22ms) | completed (23ms) |
| 8 | `source_screening` | completed (29ms) | completed (30ms) | completed (41ms) |
| 9 | `source_critic_and_uncertainty_routing` | completed (73667ms) | completed (70411ms) | completed (67694ms) |
| 10 | `content_fetch_and_parse` | completed (21553ms) | completed (12745ms) | completed (8741ms) |
| 11 | `document_quality_check` | completed (850ms) | completed (697ms) | completed (3427ms) |
| 12 | `evidence_chunking_and_data_presence_flagging` | completed (832ms) | completed (1018ms) | completed (3266ms) |
| 13 | `structured_extraction` | completed (135866ms) | completed (268033ms) | completed (282616ms) |
| 14 | `schema_validation_and_repair` | completed (242ms) | completed (1125ms) | completed (166ms) |
| 15 | `record_normalization` | completed (120ms) | completed (1026ms) | completed (165ms) |
| 16 | `record_linking` | completed (115ms) | completed (180ms) | completed (115ms) |
| 17 | `cross_source_consistency_check` | completed (132ms) | completed (300ms) | completed (129ms) |
| 18 | `quality_gate_routing` | completed (139ms) | completed (215ms) | completed (117ms) |
| 19 | `human_review` | pending | pending | pending |
| 20 | `final_data_package_builder` | completed (175ms) | completed (1491ms) | completed (326ms) |

## Cross-session Totals
- quality statuses: `{'no_records_extracted': 1, 'no_primary_case_dataset_records': 1, 'partial_with_quarantined_records': 1}`
- primary case statuses: `{'unknown_no_claim_outputs': 1, 'no_primary_case_dataset_records': 1, 'primary_case_records_present': 1}`
- blocking reasons: `{'source_role_final_excluded': 42, 'source_trust_requires_human_review': 46, 'validation_outside_scope': 4, 'record_period_too_broad_for_task_window': 20, 'ambiguous_metric_column_semantics': 9, 'record_period_semantics_not_exact_for_task_window': 9, 'record_as_of_date_outside_task_window': 10, 'record_date_outside_task_window': 4, 'record_period_outside_task_window': 7, 'record_geography_broader_than_task': 5, 'missing_direct_collection_metric': 2, 'primary_case_dataset_eligible_false': 2, 'not_primary_case_record': 2, 'claim_observation_type_ambiguous_public_health_observation': 2, 'no_corroborated_primary_case_event': 2}`
- warnings: `{'accepted_task_aware_non_primary_observation': 44, 'accepted_direct_collection_official_aggregate': 44, 'accepted_with_review_warning': 20, 'source_trust_requires_human_review': 46, 'metric_period_partially_overlaps_task_window': 2, 'validation_outside_scope_audit_only': 5}`