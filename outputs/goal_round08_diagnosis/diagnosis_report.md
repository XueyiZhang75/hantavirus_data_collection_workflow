# Goal Round08 Diagnosis Report

## Session Outcomes
### goal_round08_measles_us_2025_q1
- Task: Measles / United States / 2025-01-01 to 2025-03-31
- Workflow: completed, duration_ms=894398
- Documents/raw/normalized: 28 / 88 / 88
- Quality: no_primary_case_dataset_records; primary_case_dataset_status=no_primary_case_dataset_records
- Final/final_case/quarantined/pending: 0 / 0 / 15 / 73
- Coverage: records_quarantined; official_source_record_count=0; official_extraction_failure_count=18
- Bad duration final IDs: []
- Bad count+percent final IDs: []
- Top blocking reasons: {'source_trust_requires_human_review': 73, 'record_period_semantics_not_exact_for_task_window': 60, 'record_as_of_date_outside_task_window': 23, 'record_period_too_broad_for_task_window': 8, 'record_geography_broader_than_task': 4, 'primary_case_dataset_eligible_false': 2, 'not_primary_case_record': 2, 'no_corroborated_primary_case_event': 2}
- Final examples: none
- Candidate diagnosis:
  - no_new_generic_defect_identified: no code change

### goal_round08_flu_united_states_2024_09_29_2024_10_05
- Task: Influenza / United States / 2024-09-29 to 2024-10-05
- Workflow: completed, duration_ms=330537
- Documents/raw/normalized: 3 / 14 / 14
- Quality: partial_with_quarantined_records; primary_case_dataset_status=no_primary_case_dataset_records
- Final/final_case/quarantined/pending: 5 / 0 / 7 / 2
- Coverage: target_official_source_accepted; official_source_record_count=5; official_extraction_failure_count=0
- Bad duration final IDs: []
- Bad count+percent final IDs: []
- Top blocking reasons: {'record_period_semantics_not_exact_for_task_window': 6, 'record_date_outside_task_window': 6, 'record_period_outside_task_window': 3, 'ambiguous_metric_column_semantics_requires_human_review': 2, 'non_seasonal_influenza_subtype': 1}
- Final examples:
  - rec_src_search_ff1cee7a6f74_001: Number of specimens tested = 53699.0 count [lab_test_count; surveillance_summary; accepted_with_warnings]
  - rec_src_search_ff1cee7a6f74_003: Number of positive specimens = 380.0 count [lab_positive_count; surveillance_summary; accepted_with_warnings]
  - rec_src_search_ff1cee7a6f74_004: Percent positive specimens = 0.7 percent [lab_positivity_percent; surveillance_summary; accepted_with_warnings]
  - rec_src_search_ff1cee7a6f74_007: influenza-associated pediatric deaths = 0.0 count [death_count; death_record; accepted_with_warnings]
  - rec_src_search_ff1cee7a6f74_009: percentage of ED visits with discharge diagnosis of influenza (NSSP) = 0.2 percent [ed_visit_percent; surveillance_summary; accepted_with_warnings]
- Candidate diagnosis:
  - positive_control_passed: valid FluView count/percent indicators remained accepted

### goal_round08_dengue_brazil_2024_q1
- Task: Dengue / Brazil / 2024-01-01 to 2024-03-31
- Workflow: completed, duration_ms=693727
- Documents/raw/normalized: 37 / 27 / 26
- Quality: no_primary_case_dataset_records; primary_case_dataset_status=no_primary_case_dataset_records
- Final/final_case/quarantined/pending: 0 / 0 / 11 / 15
- Coverage: records_quarantined; official_source_record_count=0; official_extraction_failure_count=22
- Bad duration final IDs: []
- Bad count+percent final IDs: []
- Top blocking reasons: {'record_period_semantics_not_exact_for_task_window': 22, 'record_as_of_date_outside_task_window': 15, 'source_trust_requires_human_review': 15, 'abrupt_spike_simple_threshold': 5, 'record_geography_broader_than_task': 5, 'record_geography_inherited_without_source_evidence': 5, 'record_period_too_broad_for_task_window': 4, 'validation_outside_scope': 2}
- Final examples: none
- Candidate diagnosis:
  - no_new_generic_defect_identified: no code change

## 01-20 Node Matrix

See `node_matrix.csv`. Summary: nodes 01-17 and 20 completed in all sessions; human review remained pending by design.

## Cross-Session Findings
- All Round08 sessions completed nodes 01-17 and node 20; human review stayed pending by design.
- No duration-metric or count-category-with-percent-unit records entered final_dataset in any Round08 session.
- FluView positive control accepted 5 official records: lab test count, lab positive count, lab positivity percent, pediatric deaths count, and ED visit percent.
- Measles and Dengue produced no final case dataset under strict gates because remaining candidates were outside exact window, cumulative/broad, or source-trust pending; this is conservative behavior, not a safe generic code fix.

## Loop Decision
Round08 introduced no new safe generic code fix. The loop converged for this pass.
