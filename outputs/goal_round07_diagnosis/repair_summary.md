# Goal Round07 Repair Summary

## Root Cause
Round07 Measles accepted three CDC records named `Percent of Age Group Hospitalized` into `final_dataset` with `metric_category=hospitalization_count` but `metric_unit=percent`. This lets a percentage masquerade as a count-like final metric.

## TDD Evidence
- RED: `python -m pytest tests\test_run_quality_gated_final_dataset.py::test_direct_collection_quarantines_count_metric_with_percent_unit -q` failed because the percent-unit record appeared in `final_dataset`.
- GREEN: the same test passed after adding an inconsistent count/unit guard.
- Neighbor regression: `7 passed`.
- Quality-gate test file: `83 passed`.
- Full suite: `797 passed, 1 warning`.

## Code Change
- Added `_has_inconsistent_count_metric_unit` in `src/hdc_workflow/run_quality_gates.py`.
- Applied the guard in `_has_public_health_metric`, `_has_direct_collection_count_semantics`, and `_is_task_aware_accepted_observation`.

## Loop Decision
A live Round08 validation is warranted because Round07 produced a new generic quality-gate fix.
