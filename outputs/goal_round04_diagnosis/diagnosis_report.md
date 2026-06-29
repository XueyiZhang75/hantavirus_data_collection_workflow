# Goal Round 04 Diagnosis Report

## goal_round04_west_nile_california_2024_08
- status: completed
- run_quality_status: partial_with_quarantined_records
- primary_case_dataset_status: primary_case_records_present
- documents/raw/normalized: 30 / 23 / 23
- final/final_case/quarantined/pending: 7 / 7 / 11 / 5
- coverage: target_official_source_accepted (complete_target_coverage)
- top blocking reasons: {'record_period_semantics_not_exact_for_task_window': 9, 'validation_outside_scope': 5, 'source_trust_requires_human_review': 5, 'primary_case_dataset_eligible_false': 4, 'not_primary_case_record': 4, 'claim_observation_type_zero_case_statement': 4, 'no_corroborated_primary_case_event': 4, 'record_event_period_outside_task_window': 1}

## goal_round04_cholera_haiti_2024_q4
- status: completed
- run_quality_status: human_review_required
- primary_case_dataset_status: no_corroborated_primary_case_events
- documents/raw/normalized: 37 / 6 / 6
- final/final_case/quarantined/pending: 0 / 0 / 4 / 2
- coverage: records_quarantined (no_target_coverage)
- top blocking reasons: {'record_period_too_broad_for_task_window': 4, 'source_role_final_excluded': 2, 'source_trust_requires_human_review': 2}

## goal_round04_norovirus_us_2024_12_2025_02
- status: completed
- run_quality_status: partial_with_quarantined_records
- primary_case_dataset_status: no_primary_case_dataset_records
- documents/raw/normalized: 37 / 17 / 17
- final/final_case/quarantined/pending: 1 / 0 / 4 / 12
- coverage: target_official_source_accepted (complete_target_coverage)
- top blocking reasons: {'source_trust_requires_human_review': 12, 'primary_case_dataset_eligible_false': 2, 'not_primary_case_record': 2, 'claim_observation_type_ambiguous_public_health_observation': 2, 'no_corroborated_primary_case_event': 2, 'ambiguous_metric_column_semantics': 2, 'record_date_outside_task_window': 2, 'record_period_semantics_not_exact_for_task_window': 1}

## 01-20 Node Matrix

- 01 task_intake_and_scope_planning: goal_round04_west_nile_california_2024_08: completed (3 ms); goal_round04_cholera_haiti_2024_q4: completed (3 ms); goal_round04_norovirus_us_2024_12_2025_02: completed (2 ms)
- 02 disease_intelligence_builder: goal_round04_west_nile_california_2024_08: completed (52592 ms); goal_round04_cholera_haiti_2024_q4: completed (51262 ms); goal_round04_norovirus_us_2024_12_2025_02: completed (59138 ms)
- 03 profile_and_schema_setup: goal_round04_west_nile_california_2024_08: completed (4 ms); goal_round04_cholera_haiti_2024_q4: completed (4 ms); goal_round04_norovirus_us_2024_12_2025_02: completed (5 ms)
- 04 executable_source_planning: goal_round04_west_nile_california_2024_08: completed (61177 ms); goal_round04_cholera_haiti_2024_q4: completed (59960 ms); goal_round04_norovirus_us_2024_12_2025_02: completed (59517 ms)
- 05 query_strategy_builder: goal_round04_west_nile_california_2024_08: completed (11 ms); goal_round04_cholera_haiti_2024_q4: completed (8 ms); goal_round04_norovirus_us_2024_12_2025_02: completed (10 ms)
- 06 source_discovery: goal_round04_west_nile_california_2024_08: completed (177014 ms); goal_round04_cholera_haiti_2024_q4: completed (185362 ms); goal_round04_norovirus_us_2024_12_2025_02: completed (169518 ms)
- 07 source_dedup_and_registry: goal_round04_west_nile_california_2024_08: completed (22 ms); goal_round04_cholera_haiti_2024_q4: completed (55 ms); goal_round04_norovirus_us_2024_12_2025_02: completed (21 ms)
- 08 source_screening: goal_round04_west_nile_california_2024_08: completed (30 ms); goal_round04_cholera_haiti_2024_q4: completed (26 ms); goal_round04_norovirus_us_2024_12_2025_02: completed (27 ms)
- 09 source_critic_and_uncertainty_routing: goal_round04_west_nile_california_2024_08: completed (74529 ms); goal_round04_cholera_haiti_2024_q4: completed (54211 ms); goal_round04_norovirus_us_2024_12_2025_02: completed (54169 ms)
- 10 content_fetch_and_parse: goal_round04_west_nile_california_2024_08: completed (19240 ms); goal_round04_cholera_haiti_2024_q4: completed (57266 ms); goal_round04_norovirus_us_2024_12_2025_02: completed (133237 ms)
- 11 document_quality_check: goal_round04_west_nile_california_2024_08: completed (748 ms); goal_round04_cholera_haiti_2024_q4: completed (1185 ms); goal_round04_norovirus_us_2024_12_2025_02: completed (1202 ms)
- 12 evidence_chunking_and_data_presence_flagging: goal_round04_west_nile_california_2024_08: completed (930 ms); goal_round04_cholera_haiti_2024_q4: completed (1726 ms); goal_round04_norovirus_us_2024_12_2025_02: completed (1835 ms)
- 13 structured_extraction: goal_round04_west_nile_california_2024_08: completed (295530 ms); goal_round04_cholera_haiti_2024_q4: completed (170204 ms); goal_round04_norovirus_us_2024_12_2025_02: completed (259926 ms)
- 14 schema_validation_and_repair: goal_round04_west_nile_california_2024_08: completed (247 ms); goal_round04_cholera_haiti_2024_q4: completed (113 ms); goal_round04_norovirus_us_2024_12_2025_02: completed (163 ms)
- 15 record_normalization: goal_round04_west_nile_california_2024_08: completed (134 ms); goal_round04_cholera_haiti_2024_q4: completed (104 ms); goal_round04_norovirus_us_2024_12_2025_02: completed (151 ms)
- 16 record_linking: goal_round04_west_nile_california_2024_08: completed (105 ms); goal_round04_cholera_haiti_2024_q4: completed (96 ms); goal_round04_norovirus_us_2024_12_2025_02: completed (122 ms)
- 17 cross_source_consistency_check: goal_round04_west_nile_california_2024_08: completed (117 ms); goal_round04_cholera_haiti_2024_q4: completed (103 ms); goal_round04_norovirus_us_2024_12_2025_02: completed (129 ms)
- 18 quality_gate_routing: goal_round04_west_nile_california_2024_08: completed (110 ms); goal_round04_cholera_haiti_2024_q4: completed (96 ms); goal_round04_norovirus_us_2024_12_2025_02: completed (122 ms)
- 19 human_review: goal_round04_west_nile_california_2024_08: pending; goal_round04_cholera_haiti_2024_q4: pending; goal_round04_norovirus_us_2024_12_2025_02: pending
- 20 final_data_package_builder: goal_round04_west_nile_california_2024_08: completed (230 ms); goal_round04_cholera_haiti_2024_q4: completed (190 ms); goal_round04_norovirus_us_2024_12_2025_02: completed (269 ms)

## Cross-session Findings
- blocking_reason_counts_total: {'source_trust_requires_human_review': 19, 'record_period_semantics_not_exact_for_task_window': 10, 'primary_case_dataset_eligible_false': 6, 'not_primary_case_record': 6, 'no_corroborated_primary_case_event': 6, 'validation_outside_scope': 5, 'claim_observation_type_zero_case_statement': 4, 'record_period_too_broad_for_task_window': 4, 'record_event_period_outside_task_window': 2, 'source_role_final_excluded': 2, 'claim_observation_type_ambiguous_public_health_observation': 2, 'ambiguous_metric_column_semantics': 2}
- warning_counts_total: {'accepted_task_aware_non_primary_observation': 24, 'accepted_direct_collection_official_aggregate': 24, 'source_trust_requires_human_review': 19, 'accepted_with_review_warning': 7, 'validation_outside_scope_audit_only': 5}
