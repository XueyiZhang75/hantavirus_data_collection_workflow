# Goal Round06 Repair Summary

## Root Cause
The Measles session accepted a CDC MMWR descriptive duration metric (`Days from rash onset to hospital admission`, unit `days`, category `other`) into `final_dataset` because the direct-collection metric gate treated hospital/admission text as a strong public-health metric.

## TDD Evidence
- RED: `python -m pytest tests\test_run_quality_gated_final_dataset.py::test_direct_collection_quarantines_descriptive_hospital_delay_metric -q` failed because the record appeared in `final_dataset`.
- GREEN: the same test passed after adding a descriptive duration metric guard.
- Neighbor regression: six targeted direct-collection tests passed after the fix.

## Code Change
- Added `_is_descriptive_duration_metric` in `src/hdc_workflow/run_quality_gates.py`.
- Applied the guard in `_has_public_health_metric` and `_has_direct_collection_count_semantics`.

## Verification
- Targeted neighbor regression: `6 passed`.
- Quality-gate test file: `82 passed`.
- Full suite: `796 passed, 1 warning`.
- Warning: existing Starlette/FastAPI deprecation warning in `test_langflow_demo_adapter.py`, no failure.
