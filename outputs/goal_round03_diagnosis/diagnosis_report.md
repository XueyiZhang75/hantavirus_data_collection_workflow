# Goal Round 03 Diagnosis Report

## goal_round03_west_nile_california_2024_08
- status: completed
- run_quality_status: no_primary_case_dataset_records
- primary_case_dataset_status: no_primary_case_dataset_records
- documents/raw/normalized: 36 / 45 / 45
- final/final_case/quarantined/pending: 0 / 0 / 0 / 45
- coverage: records_quarantined (no_target_coverage)
- top blocking reasons: {'source_trust_requires_human_review': 45, 'source_role_final_excluded': 39, 'record_period_semantics_not_exact_for_task_window': 17, 'record_event_period_outside_task_window': 3, 'record_geography_broader_than_task': 2, 'validation_outside_scope': 2}

## goal_round03_salmonella_us_2024_05_07
- status: completed
- run_quality_status: partial_with_quarantined_records
- primary_case_dataset_status: primary_case_records_present
- documents/raw/normalized: 28 / 15 / 15
- final/final_case/quarantined/pending: 8 / 5 / 6 / 1
- coverage: target_official_source_accepted (complete_target_coverage)
- top blocking reasons: {'record_period_too_broad_for_task_window': 4, 'record_date_outside_task_window': 2, 'record_event_period_outside_task_window': 1, 'missing_direct_collection_metric': 1, 'primary_case_dataset_eligible_false': 1, 'not_primary_case_record': 1}

## goal_round03_legionnaires_nyc_2025_08
- status: completed
- run_quality_status: partial_with_quarantined_records
- primary_case_dataset_status: primary_case_records_present
- documents/raw/normalized: 27 / 45 / 43
- final/final_case/quarantined/pending: 2 / 2 / 9 / 32
- coverage: records_quarantined (no_target_coverage)
- top blocking reasons: {'source_trust_requires_human_review': 32, 'source_role_final_excluded': 15, 'record_event_period_outside_task_window': 5, 'primary_case_dataset_eligible_false': 4, 'not_primary_case_record': 4, 'claim_observation_type_ambiguous_public_health_observation': 4}

## 01-20 Node Matrix

- 01 task_intake_and_scope_planning: goal_round03_west_nile_california_2024_08: completed (2 ms); goal_round03_salmonella_us_2024_05_07: completed (3 ms); goal_round03_legionnaires_nyc_2025_08: completed (11 ms)
- 02 disease_intelligence_builder: goal_round03_west_nile_california_2024_08: completed (46779 ms); goal_round03_salmonella_us_2024_05_07: completed (59819 ms); goal_round03_legionnaires_nyc_2025_08: completed (45779 ms)
- 03 profile_and_schema_setup: goal_round03_west_nile_california_2024_08: completed (2 ms); goal_round03_salmonella_us_2024_05_07: completed (6 ms); goal_round03_legionnaires_nyc_2025_08: completed (6 ms)
- 04 executable_source_planning: goal_round03_west_nile_california_2024_08: completed (60427 ms); goal_round03_salmonella_us_2024_05_07: completed (61174 ms); goal_round03_legionnaires_nyc_2025_08: completed (61920 ms)
- 05 query_strategy_builder: goal_round03_west_nile_california_2024_08: completed (10 ms); goal_round03_salmonella_us_2024_05_07: completed (10 ms); goal_round03_legionnaires_nyc_2025_08: completed (15 ms)
- 06 source_discovery: goal_round03_west_nile_california_2024_08: completed (180102 ms); goal_round03_salmonella_us_2024_05_07: completed (179294 ms); goal_round03_legionnaires_nyc_2025_08: completed (201007 ms)
- 07 source_dedup_and_registry: goal_round03_west_nile_california_2024_08: completed (19 ms); goal_round03_salmonella_us_2024_05_07: completed (25 ms); goal_round03_legionnaires_nyc_2025_08: completed (27 ms)
- 08 source_screening: goal_round03_west_nile_california_2024_08: completed (26 ms); goal_round03_salmonella_us_2024_05_07: completed (34 ms); goal_round03_legionnaires_nyc_2025_08: completed (37 ms)
- 09 source_critic_and_uncertainty_routing: goal_round03_west_nile_california_2024_08: completed (80245 ms); goal_round03_salmonella_us_2024_05_07: completed (282697 ms); goal_round03_legionnaires_nyc_2025_08: completed (71439 ms)
- 10 content_fetch_and_parse: goal_round03_west_nile_california_2024_08: completed (49414 ms); goal_round03_salmonella_us_2024_05_07: completed (15016 ms); goal_round03_legionnaires_nyc_2025_08: completed (48256 ms)
- 11 document_quality_check: goal_round03_west_nile_california_2024_08: completed (874 ms); goal_round03_salmonella_us_2024_05_07: completed (1368 ms); goal_round03_legionnaires_nyc_2025_08: completed (627 ms)
- 12 evidence_chunking_and_data_presence_flagging: goal_round03_west_nile_california_2024_08: completed (842 ms); goal_round03_salmonella_us_2024_05_07: completed (2036 ms); goal_round03_legionnaires_nyc_2025_08: completed (780 ms)
- 13 structured_extraction: goal_round03_west_nile_california_2024_08: completed (349008 ms); goal_round03_salmonella_us_2024_05_07: completed (215191 ms); goal_round03_legionnaires_nyc_2025_08: completed (335814 ms)
- 14 schema_validation_and_repair: goal_round03_west_nile_california_2024_08: completed (172 ms); goal_round03_salmonella_us_2024_05_07: completed (341 ms); goal_round03_legionnaires_nyc_2025_08: completed (344 ms)
- 15 record_normalization: goal_round03_west_nile_california_2024_08: completed (172 ms); goal_round03_salmonella_us_2024_05_07: completed (231 ms); goal_round03_legionnaires_nyc_2025_08: completed (226 ms)
- 16 record_linking: goal_round03_west_nile_california_2024_08: completed (112 ms); goal_round03_salmonella_us_2024_05_07: completed (164 ms); goal_round03_legionnaires_nyc_2025_08: completed (105 ms)
- 17 cross_source_consistency_check: goal_round03_west_nile_california_2024_08: completed (138 ms); goal_round03_salmonella_us_2024_05_07: completed (176 ms); goal_round03_legionnaires_nyc_2025_08: completed (135 ms)
- 18 quality_gate_routing: goal_round03_west_nile_california_2024_08: completed (116 ms); goal_round03_salmonella_us_2024_05_07: completed (191 ms); goal_round03_legionnaires_nyc_2025_08: completed (118 ms)
- 19 human_review: goal_round03_west_nile_california_2024_08: pending; goal_round03_salmonella_us_2024_05_07: pending; goal_round03_legionnaires_nyc_2025_08: pending
- 20 final_data_package_builder: goal_round03_west_nile_california_2024_08: completed (483 ms); goal_round03_salmonella_us_2024_05_07: completed (382 ms); goal_round03_legionnaires_nyc_2025_08: completed (365 ms)

## Cross-session Findings
- blocking_reason_counts_total: {'source_trust_requires_human_review': 78, 'source_role_final_excluded': 55, 'record_period_semantics_not_exact_for_task_window': 17, 'record_event_period_outside_task_window': 9, 'record_period_too_broad_for_task_window': 5, 'primary_case_dataset_eligible_false': 5, 'not_primary_case_record': 5, 'claim_observation_type_ambiguous_public_health_observation': 5, 'no_corroborated_primary_case_event': 5, 'record_date_outside_task_window': 4, 'missing_direct_collection_metric': 4, 'record_geography_broader_than_task': 2}
- warning_counts_total: {'source_trust_requires_human_review': 78, 'accepted_task_aware_non_primary_observation': 52, 'accepted_direct_collection_official_aggregate': 52, 'accepted_with_review_warning': 12, 'validation_outside_scope_audit_only': 6, 'metric_period_partially_overlaps_task_window': 2}
- Salmonella regression anchor improved: explicit outside-window event periods are now quarantined, and the previous November/2026 leakage pattern did not appear in strict final.
- West Nile still fails strict final because source trust now depends on broader source-policy questions: non-.gov vector-control district domains and upstream source_role_final=excluded on westnile.ca.gov PDFs despite extracted metrics.
- Legionnaires produced primary case records but still has a large pending-review tail driven by source trust and source_role exclusions.
