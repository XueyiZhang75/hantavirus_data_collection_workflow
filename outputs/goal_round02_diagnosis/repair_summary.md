# Goal Round 02 Repair Summary

## Sessions reviewed

- `goal_round02_west_nile_california_2024_08`: completed; 49 pending review records, 0 strict final records. Main blocker was `source_trust_requires_human_review` on official `.gov` public-health records with missing publisher metadata and low machine score.
- `goal_round02_mpox_drc_2024_08`: completed; 5 final records, 11 quarantined records, 19 pending review records.
- `goal_round02_salmonella_us_2024_05_07`: completed; 5 final records, 4 quarantined records, 10 pending review records. One accepted record had an explicit November 2024 event start while the task window was 2024-05-01 to 2024-07-31.

## Node diagnosis

All three sessions completed nodes 01-18 and node 20. Node 19 remained pending by design because records were queued for human review. The workflow orchestration itself did not crash; the main defects were strict-final quality-gate decisions.

## TDD repair 1: supported official `.gov` sources

Observed failure:

- Fresno County `.gov` West Nile Virus PDF records had `source_type=official_public_health_agency`, `source_role_final=collection`, and `credibility_level=high`.
- Because publisher metadata was missing and the machine credibility score was `0.5352`, the strict gate added `source_trust_requires_human_review`.
- This pushed task-compatible official public-health data into pending review instead of strict final.

RED test added:

- `test_direct_collection_accepts_supported_official_gov_source_despite_low_machine_score`

Fix:

- Added `_source_has_supported_official_public_health_identity(...)`.
- If a source claims public-health agency identity and the host supports that identity, such as `.gov`, the low numeric machine score alone no longer forces human review.
- Explicit low/excluded/needs-review credibility levels, secondary/social domains, unknown source types, and other hard source risks still route to review or quarantine.

## TDD repair 2: explicit event dates outside task window

Observed failure:

- A Salmonella FDA November 2024 outbreak record had `event_start_date=2024-11-01`.
- The task window was 2024-05-01 to 2024-07-31.
- Because `date_reported` and metric period were filled inside the task window, the record entered strict final even though the explicit event was outside scope.

RED test added:

- `test_direct_collection_quarantines_explicit_event_start_after_task_window`

Fix:

- Added `_record_event_period_scope_block(...)`.
- Explicit `event_start_date`/`event_end_date` is now checked independently against the requested task window before mixed metric-period fallback logic can mask it.
- Outside-window explicit event periods now receive `record_event_period_outside_task_window` and are quarantined.

## Verification

- RED tests failed before implementation.
- Targeted tests passed after implementation.
- Related source-trust and date/period regression tests passed.
- `python -m pytest tests\test_run_quality_gated_final_dataset.py -q`: 77 passed.
- `$env:PYTHONIOENCODING='utf-8'; python -m pytest -q`: 791 passed, 1 existing `StarletteDeprecationWarning`.

