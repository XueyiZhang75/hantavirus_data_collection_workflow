# Goal Round 05 Diagnosis Report

## goal_round05_west_nile_california_2024_08
- status: completed
- run_quality_status: partial_with_quarantined_records
- primary_case_dataset_status: primary_case_records_present
- documents/raw/normalized: 34 / 37 / 37
- final/final_case/quarantined/pending: 16 / 14 / 11 / 10
- coverage: target_official_source_accepted (complete_target_coverage)
- top blocking reasons: {'record_period_semantics_not_exact_for_task_window': 12, 'source_role_final_excluded': 10, 'source_trust_requires_human_review': 10, 'primary_case_dataset_eligible_false': 5, 'not_primary_case_record': 5, 'claim_observation_type_zero_case_statement': 5, 'no_corroborated_primary_case_event': 5, 'validation_outside_scope': 3}

## goal_round05_cholera_haiti_2024_full_year
- status: completed
- run_quality_status: failed_quality_gate
- primary_case_dataset_status: no_corroborated_primary_case_events
- documents/raw/normalized: 41 / 2 / 2
- final/final_case/quarantined/pending: 0 / 0 / 2 / 0
- coverage: best_available_only (no_target_coverage)
- top blocking reasons: {'ambiguous_metric_column_semantics': 2}

## goal_round05_legionnaires_nyc_2025_08
- status: completed
- run_quality_status: partial_with_quarantined_records
- primary_case_dataset_status: no_primary_case_dataset_records
- documents/raw/normalized: 22 / 33 / 33
- final/final_case/quarantined/pending: 1 / 0 / 11 / 21
- coverage: edge_metric_only (no_target_coverage)
- top blocking reasons: {'source_trust_requires_human_review': 21, 'record_event_period_outside_task_window': 8, 'record_as_of_date_outside_task_window': 4, 'record_date_outside_task_window': 4, 'primary_case_dataset_eligible_false': 2, 'not_primary_case_record': 2, 'claim_observation_type_ambiguous_public_health_observation': 2, 'no_corroborated_primary_case_event': 2}

## 01-20 Node Matrix

- 01 task_intake_and_scope_planning: goal_round05_west_nile_california_2024_08: completed (2 ms); goal_round05_cholera_haiti_2024_full_year: completed (2 ms); goal_round05_legionnaires_nyc_2025_08: completed (5 ms)
- 02 disease_intelligence_builder: goal_round05_west_nile_california_2024_08: completed (57323 ms); goal_round05_cholera_haiti_2024_full_year: completed (53393 ms); goal_round05_legionnaires_nyc_2025_08: completed (46714 ms)
- 03 profile_and_schema_setup: goal_round05_west_nile_california_2024_08: completed (4 ms); goal_round05_cholera_haiti_2024_full_year: completed (5 ms); goal_round05_legionnaires_nyc_2025_08: completed (5 ms)
- 04 executable_source_planning: goal_round05_west_nile_california_2024_08: completed (63184 ms); goal_round05_cholera_haiti_2024_full_year: completed (59793 ms); goal_round05_legionnaires_nyc_2025_08: completed (59089 ms)
- 05 query_strategy_builder: goal_round05_west_nile_california_2024_08: completed (9 ms); goal_round05_cholera_haiti_2024_full_year: completed (11 ms); goal_round05_legionnaires_nyc_2025_08: completed (10 ms)
- 06 source_discovery: goal_round05_west_nile_california_2024_08: completed (199142 ms); goal_round05_cholera_haiti_2024_full_year: completed (208429 ms); goal_round05_legionnaires_nyc_2025_08: completed (199114 ms)
- 07 source_dedup_and_registry: goal_round05_west_nile_california_2024_08: completed (21 ms); goal_round05_cholera_haiti_2024_full_year: completed (22 ms); goal_round05_legionnaires_nyc_2025_08: completed (20 ms)
- 08 source_screening: goal_round05_west_nile_california_2024_08: completed (28 ms); goal_round05_cholera_haiti_2024_full_year: completed (31 ms); goal_round05_legionnaires_nyc_2025_08: completed (27 ms)
- 09 source_critic_and_uncertainty_routing: goal_round05_west_nile_california_2024_08: completed (72820 ms); goal_round05_cholera_haiti_2024_full_year: completed (14890 ms); goal_round05_legionnaires_nyc_2025_08: completed (62484 ms)
- 10 content_fetch_and_parse: goal_round05_west_nile_california_2024_08: completed (46233 ms); goal_round05_cholera_haiti_2024_full_year: completed (22328 ms); goal_round05_legionnaires_nyc_2025_08: completed (4519 ms)
- 11 document_quality_check: goal_round05_west_nile_california_2024_08: completed (1075 ms); goal_round05_cholera_haiti_2024_full_year: completed (1168 ms); goal_round05_legionnaires_nyc_2025_08: completed (426 ms)
- 12 evidence_chunking_and_data_presence_flagging: goal_round05_west_nile_california_2024_08: completed (1734 ms); goal_round05_cholera_haiti_2024_full_year: completed (1716 ms); goal_round05_legionnaires_nyc_2025_08: completed (623 ms)
- 13 structured_extraction: goal_round05_west_nile_california_2024_08: completed (302463 ms); goal_round05_cholera_haiti_2024_full_year: completed (139857 ms); goal_round05_legionnaires_nyc_2025_08: completed (283590 ms)
- 14 schema_validation_and_repair: goal_round05_west_nile_california_2024_08: completed (299 ms); goal_round05_cholera_haiti_2024_full_year: completed (113 ms); goal_round05_legionnaires_nyc_2025_08: completed (182 ms)
- 15 record_normalization: goal_round05_west_nile_california_2024_08: completed (182 ms); goal_round05_cholera_haiti_2024_full_year: completed (101 ms); goal_round05_legionnaires_nyc_2025_08: completed (286 ms)
- 16 record_linking: goal_round05_west_nile_california_2024_08: completed (125 ms); goal_round05_cholera_haiti_2024_full_year: completed (94 ms); goal_round05_legionnaires_nyc_2025_08: completed (101 ms)
- 17 cross_source_consistency_check: goal_round05_west_nile_california_2024_08: completed (144 ms); goal_round05_cholera_haiti_2024_full_year: completed (98 ms); goal_round05_legionnaires_nyc_2025_08: completed (131 ms)
- 18 quality_gate_routing: goal_round05_west_nile_california_2024_08: completed (148 ms); goal_round05_cholera_haiti_2024_full_year: completed (97 ms); goal_round05_legionnaires_nyc_2025_08: completed (116 ms)
- 19 human_review: goal_round05_west_nile_california_2024_08: pending; goal_round05_cholera_haiti_2024_full_year: pending; goal_round05_legionnaires_nyc_2025_08: pending
- 20 final_data_package_builder: goal_round05_west_nile_california_2024_08: completed (526 ms); goal_round05_cholera_haiti_2024_full_year: completed (165 ms); goal_round05_legionnaires_nyc_2025_08: completed (297 ms)

## Cross-session Findings
- blocking_reason_counts_total: {'source_trust_requires_human_review': 31, 'record_period_semantics_not_exact_for_task_window': 14, 'source_role_final_excluded': 10, 'record_event_period_outside_task_window': 8, 'primary_case_dataset_eligible_false': 7, 'not_primary_case_record': 7, 'no_corroborated_primary_case_event': 7, 'claim_observation_type_zero_case_statement': 5, 'record_as_of_date_outside_task_window': 5, 'record_date_outside_task_window': 5, 'validation_outside_scope': 3, 'ambiguous_metric_column_semantics': 3}
- warning_counts_total: {'accepted_task_aware_non_primary_observation': 36, 'accepted_direct_collection_official_aggregate': 36, 'source_trust_requires_human_review': 31, 'accepted_with_review_warning': 11, 'validation_outside_scope_audit_only': 1}
