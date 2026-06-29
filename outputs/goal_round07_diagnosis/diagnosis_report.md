# Goal Round07 Diagnosis Report

## Session Outcomes
### goal_round07_measles_us_2025_q1
- Task: Measles / United States / 2025-01-01 to 2025-03-31
- Workflow: completed, duration_ms=848068
- Documents/raw/normalized: 39 / 51 / 51
- Quality: partial_with_quarantined_records; primary_case_dataset_status=primary_case_records_present
- Final/final_case/quarantined/pending: 3 / 0 / 26 / 22
- Coverage: target_official_source_accepted; official_source_record_count=3; official_extraction_failure_count=24
- Top blocking reasons: {'record_period_semantics_not_exact_for_task_window': 32, 'source_trust_requires_human_review': 22, 'record_as_of_date_outside_task_window': 11, 'record_period_too_broad_for_task_window': 11, 'record_period_outside_task_window': 8, 'record_geography_broader_than_task': 4, 'ambiguous_metric_column_semantics': 1, 'record_event_period_outside_task_window': 1}
- Final examples:
  - rec_src_search_283a8bed6a9d_012: Percent of Age Group Hospitalized - Under 5 years = 52.0 percent [hospitalization_count; hospitalization_record; accepted_with_warnings]
  - rec_src_search_283a8bed6a9d_013: Percent of Age Group Hospitalized - 5-19 years = 25.0 percent [hospitalization_count; hospitalization_record; accepted_with_warnings]
  - rec_src_search_283a8bed6a9d_014: Percent of Age Group Hospitalized - 20+ years = 39.0 percent [hospitalization_count; hospitalization_record; accepted_with_warnings]
- Candidate diagnosis:
  - count_metric_with_percent_unit_accepted: TDD guard added after Round07

### goal_round07_west_nile_california_2024_08
- Task: West Nile virus / California / 2024-08-01 to 2024-08-31
- Workflow: completed, duration_ms=684488
- Documents/raw/normalized: 37 / 13 / 13
- Quality: no_primary_case_dataset_records; primary_case_dataset_status=no_primary_case_dataset_records
- Final/final_case/quarantined/pending: 0 / 0 / 8 / 5
- Coverage: records_quarantined; official_source_record_count=0; official_extraction_failure_count=25
- Top blocking reasons: {'record_period_semantics_not_exact_for_task_window': 6, 'source_trust_requires_human_review': 5, 'validation_outside_scope': 4, 'record_event_period_outside_task_window': 4, 'record_geography_inherited_without_source_evidence': 1, 'record_as_of_date_outside_task_window': 1}
- Final examples: none
- Candidate diagnosis:
  - no_new_safe_generic_fix_identified: documented only

### goal_round07_dengue_brazil_2024_q1
- Task: Dengue / Brazil / 2024-01-01 to 2024-03-31
- Workflow: completed, duration_ms=563100
- Documents/raw/normalized: 20 / 27 / 27
- Quality: no_primary_case_dataset_records; primary_case_dataset_status=no_primary_case_dataset_records
- Final/final_case/quarantined/pending: 0 / 0 / 11 / 16
- Coverage: records_quarantined; official_source_record_count=0; official_extraction_failure_count=9
- Top blocking reasons: {'record_period_semantics_not_exact_for_task_window': 22, 'source_trust_requires_human_review': 16, 'record_as_of_date_outside_task_window': 8, 'record_period_too_broad_for_task_window': 6, 'record_geography_inherited_without_source_evidence': 4, 'validation_outside_scope': 3, 'record_geography_broader_than_task': 2, 'ambiguous_metric_column_semantics': 2}
- Final examples: none
- Candidate diagnosis:
  - no_new_safe_generic_fix_identified: documented only

## 01-20 Node Matrix

See `node_matrix.csv`. Summary: nodes 01-17 and 20 completed in all sessions; human review remained pending by design.

## Cross-Session Findings
- All three sessions completed nodes 01-17 and node 20; node 18/19 human review stayed pending by design.
- Round06 duration-metric bug did not recur in Round07 Measles final records.
- Round07 exposed a new metric-unit consistency defect: hospitalization_count records with percent units were accepted.
- West Nile and Dengue produced no final records in this run because available records were outside exact task window, cumulative/YTD, or required source trust review; no safe source-threshold relaxation was applied.

## TDD Repair
- Defect: count metric with percent/rate unit accepted as final count metric
- RED test: `tests/test_run_quality_gated_final_dataset.py::test_direct_collection_quarantines_count_metric_with_percent_unit`
- Implementation: `src/hdc_workflow/run_quality_gates.py _has_inconsistent_count_metric_unit guard`
- Verification: RED observed; GREEN observed; targeted 7 passed; quality-gate file 83 passed; full suite 797 passed, 1 warning
