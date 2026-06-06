# Stage 4F Annual Summary Alignment Review

## 1. Purpose

Stage 4F fixes a masked-validation evaluation alignment issue for annual
summary records. Stage 4E already extracted the relevant New Mexico HPS annual
summary record, but the evaluator split the collection and validation records
because it compared the collection publication date against the validation
annual reporting period.

## 2. Problem after Stage 4E

The LLM replay produced a 2025 annual New Mexico HPS record from
`src_nmdoh_hps_2026_first_case_prior_year_summary` with
`cases_unspecified=7`, `deaths=3`, `statistical_count_type=annual`, and
`reporting_period=2025`.

The held-out validation record from
`src_nmdoh_hps_cases_by_county_1975_2025_pdf` had the same annual reporting
period and case count, but its `date_anchor` was `2025` while the collection
record kept the source publication date `2026-03-12`. The previous evaluator
used `date_anchor` before `reporting_period`, so the annual records did not
share the same comparison key.

## 3. Annual comparison rule

For evaluation comparison only, annual records use `reporting_period` as the
temporal comparison anchor when:

- `statistical_count_type == "annual"`
- `reporting_period` is present

The original `date_reported`, `date_anchor`, and `date_anchor_field` values are
preserved in the output rows. This rule does not apply to `newly_reported`,
`cumulative`, as-of, outbreak cumulative, or records without a reporting
period.

## 4. What code changed

`src/hdc_workflow/evaluation_report_builder.py` now uses an internal
`_comparison_date_anchor(record)` helper inside `_comparison_key(record)`.
The helper returns `reporting_period` only for annual records with a present
reporting period; otherwise it keeps the previous fallback order:
`date_anchor`, `date_reported`, then `reporting_period`.

`scripts/run_new_mexico_hps_llm_extraction_replay.py` now supports
`--reevaluate-existing`, which reads existing Stage 4E replay records and
regenerates evaluation/comparison artifacts without calling an LLM and without
live fetch.

## 5. Re-evaluation result

Before alignment, Stage 4E evaluation produced 3 rows:

- `missing_collection_record=1`
- `missing_validation_record=2`
- rows with both collection and validation evidence: 0

After alignment, Stage 4F re-evaluation produced 2 rows:

- `partial_match_not_comparable=1`
- `missing_validation_record=1`
- rows with both collection and validation evidence: 1
- reserved source leakage count: 0

The annual row now contains both the collection source and the held-out
validation source. Its field-level status is
`case_count_match;death_count_not_comparable` because the validation ground
truth has the 2025 case count but does not include a comparable death count.

## 6. What this proves

This proves the Stage 4E LLM extraction recovered the intended annual New
Mexico HPS count, and that the masked-validation evaluator can now compare an
annual record reported later against a held-out annual ground-truth record for
the same reporting period.

## 7. What this does not prove

This does not prove broad autonomous web search, validation PDF/OCR support,
or general LLM extraction quality across diseases and sources. It also does
not prove the death count against the held-out validation source because that
validation record only contains the case-count ground truth.

## 8. Remaining limitations

- The re-evaluation uses existing Stage 4E replay outputs.
- No live fetch was rerun.
- No external LLM was called in Stage 4F.
- The validation record remains manually curated.
- Human review remains appropriate for partial or not-comparable fields.

## 9. Recommended next step

Stage 4G should prepare the professor meeting package with the full Stage
0-4F narrative, including the distinction between real-source collection,
controlled LLM extraction, annual alignment, and remaining validation limits.
