# Goal Round06 Diagnosis Report

## Session Outcomes
### goal_round06_measles_us_2025_q1
- Task: Measles / United States / 2025-01-01 to 2025-03-31
- Workflow: completed, duration_ms=916439
- Documents/raw/normalized: 45 / 73 / 72
- Quality: partial_with_quarantined_records; primary_case_dataset_status=no_primary_case_dataset_records
- Final/final_case/quarantined/pending: 1 / 0 / 17 / 54
- Coverage: target_official_source_accepted; official_source_record_count=1; official_extraction_failure_count=31
- Top blocking reasons: {'record_period_semantics_not_exact_for_task_window': 56, 'source_trust_requires_human_review': 54, 'record_as_of_date_outside_task_window': 18, 'record_period_too_broad_for_task_window': 5, 'record_geography_broader_than_task': 4, 'primary_case_dataset_eligible_false': 3, 'not_primary_case_record': 3, 'no_corroborated_primary_case_event': 3}
- Final examples:
  - rec_src_search_4e73f2d0f38f_006: Days from rash onset to hospital admission (median) = 2.0 days [other; ambiguous_public_health_observation; accepted_with_warnings]
- Candidate diagnosis:
  - descriptive_duration_metric_accepted: duration/median hospital process metric was treated as direct public-health metric because text contained hospital/admission tokens; repair=TDD fix added in run_quality_gates duration metric guard
  - accepted_non_primary_when_no_case_dataset: accepted non-primary observation requires field-level metric semantics review; repair=covered by descriptive duration metric guard when metric is duration-only

### goal_round06_dengue_brazil_2024_q1
- Task: Dengue / Brazil / 2024-01-01 to 2024-03-31
- Workflow: completed, duration_ms=690461
- Documents/raw/normalized: 38 / 18 / 18
- Quality: no_primary_case_dataset_records; primary_case_dataset_status=no_primary_case_dataset_records
- Final/final_case/quarantined/pending: 0 / 0 / 6 / 12
- Coverage: records_quarantined; official_source_record_count=0; official_extraction_failure_count=25
- Top blocking reasons: {'record_period_semantics_not_exact_for_task_window': 14, 'source_trust_requires_human_review': 12, 'record_as_of_date_outside_task_window': 6, 'record_period_too_broad_for_task_window': 4, 'validation_outside_scope': 2, 'abrupt_spike_simple_threshold': 2, 'record_geography_inherited_without_source_evidence': 2, 'source_role_final_excluded': 2}
- Final examples: none
- Candidate diagnosis:
  - no_safe_generic_fix_identified: source trust or provenance required human review; repair=documented only; no threshold relaxation applied

### goal_round06_legionnaires_ontario_2025_07
- Task: Legionnaires' disease / Ontario / 2025-07-01 to 2025-07-31
- Workflow: completed, duration_ms=693120
- Documents/raw/normalized: 22 / 22 / 22
- Quality: no_primary_case_dataset_records; primary_case_dataset_status=no_primary_case_dataset_records
- Final/final_case/quarantined/pending: 0 / 0 / 3 / 19
- Coverage: records_quarantined; official_source_record_count=0; official_extraction_failure_count=11
- Top blocking reasons: {'source_trust_requires_human_review': 19, 'validation_outside_scope': 9, 'record_period_semantics_not_exact_for_task_window': 8, 'primary_case_dataset_eligible_false': 3, 'not_primary_case_record': 3, 'claim_observation_type_ambiguous_public_health_observation': 3, 'no_corroborated_primary_case_event': 3, 'record_geography_inherited_without_source_evidence': 2}
- Final examples: none
- Candidate diagnosis:
  - no_safe_generic_fix_identified: source trust or provenance required human review; repair=documented only; no threshold relaxation applied

## 01-20 Node Matrix

See `node_matrix.csv` for the complete per-session matrix. Summary: nodes 01-17 and 20 completed in all sessions; node 18/19 human review is pending by design because no manual review decisions were supplied.

## Cross-Session Findings
- All three sessions completed nodes 01-17 and node 20; human_review remained pending by design because no manual decisions were supplied.
- Only the Measles session emitted a final_dataset record, and that record was a descriptive duration metric rather than a case/death/hospitalization count.
- Dengue Brazil and Legionnaires Ontario produced no final records because candidates were mostly cumulative/outside-window, insufficiently trusted, or non-primary observations; no safe threshold relaxation was applied.

## TDD Repair
- Defect: official descriptive hospital-delay duration metric accepted into final_dataset
- RED test: `tests/test_run_quality_gated_final_dataset.py::test_direct_collection_quarantines_descriptive_hospital_delay_metric`
- Implementation: `src/hdc_workflow/run_quality_gates.py duration metric guard for direct-collection public health metric semantics`
- Status: RED observed, GREEN observed, targeted neighbor regression passed, file-level suite passed, full pytest suite passed (`796 passed, 1 warning`).
