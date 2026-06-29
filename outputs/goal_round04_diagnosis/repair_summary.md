# Goal Round 04 Repair Summary

## Policy changes implemented before Round 04

- Limited official `.org` trust was added for mosquito/vector-control district sources when the source claims public-health agency identity and the title/source identity text supports a local vector-control district.
- Official public-health sources that were marked `source_role_final=excluded` by machine triage can now be rescued when they are supported official sources, direct_collection is enabled, the source was not excluded by human review, and a task-aware public-health metric was extracted.

## Round 04 sessions

- `goal_round04_west_nile_california_2024_08`: completed; 7 final records, 7 final case records, 11 quarantined records, 5 pending review records. This is a major improvement from the previous 0-final West Nile runs.
- `goal_round04_cholera_haiti_2024_q4`: completed; 0 final records, 4 quarantined records, 2 pending review records. The main official WHO records were annual/broader-than-Q4 and were correctly blocked as `record_period_too_broad_for_task_window`.
- `goal_round04_norovirus_us_2024_12_2025_02`: completed; 1 final record, 4 quarantined records, 12 pending review records. Most pending records came from secondary/news sources quoting CDC data.

## TDD repair: historical comparator metric rows

Observed failure:

- After official-source rescue was enabled, West Nile final records included rows such as `No. Human Cases (prior year comparator)` and `same point last year`.
- These are historical comparator rows from official bulletins, not task-window observations, even when the extraction filled `metric_period_start`/`metric_period_end` with the task window.

RED test added:

- `test_direct_collection_quarantines_prior_year_comparator_metric_row`

Fix:

- `_record_period_semantics_block(...)` now includes `metric_name`, source/metric column labels, and table header text in period semantics analysis.
- The direct-collection task-window guard now treats `prior year`, `previous year`, `last year`, `same point`, `same time last year`, `historical comparator`, and `comparator` as non-exact current-period semantics.

## Verification

- RED test failed before implementation.
- Targeted related tests passed after implementation.
- `python -m pytest tests\test_run_quality_gated_final_dataset.py -q`: 80 passed.
- `$env:PYTHONIOENCODING='utf-8'; python -m pytest -q`: 794 passed, 1 existing `StarletteDeprecationWarning`.

