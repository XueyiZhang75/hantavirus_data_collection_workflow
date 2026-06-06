# New Mexico HPS Workflow Source Split

## Collection Sources

这些 source 允许进入真实网页抓取和 collection extraction。

| Source ID | Role | Source | Purpose | Workshop Output |
|---|---|---|---|---|
| `src_nmdoh_hps_2024_first_case` | `data_source` | NMDOH 2024 first HPS case news release | 2024 New Mexico HPS case information | Appears in live collection output |
| `src_nmdoh_hps_2025_first_case_death` | `data_source` | NMDOH 2025 Santa Fe County HPS death news release | 2025 first case/death and 2024 annual context | Appears in live collection output |
| `src_nmdoh_hps_2026_first_case_prior_year_summary` | `data_source` | NMDOH 2026 Santa Fe County resident HPS news release | 2026 first case and 2025 prior-year annual summary | Used for live collection and LLM extraction |

## Validation Comparison Source

这个 source 被 held out，不允许进入 collection extraction。它只用于 validation comparison。

| Source ID | Role | Source | Purpose | Workshop Output |
|---|---|---|---|---|
| `src_nmdoh_hps_cases_by_county_1975_2025_pdf` | `validation_reserved` | NMDOH HPS cases by county PDF/data page | Held-out validation ground truth for annual/county totals | `validation/ground_truth_records.csv` contains 2025 New Mexico `Total = 7` |

## Context Sources

这些 source 只用于背景、术语和范围说明，不能产生 collection records。

| Source ID | Role | Source | Guardrail |
|---|---|---|---|
| `src_nmdoh_hps_overview_1975_2025` | `context_source` | NMDOH HPS overview page | `blocked_from_structured_extraction` |
| `src_cdc_hantavirus_reported_cases_through_2023` | `context_source` | CDC reported hantavirus disease cases page | `blocked_from_structured_extraction` |

## Current Workflow Run Result

Live webpage collection:

```text
collection_record_count: 5
reserved_source_leakage_count: 0
access_or_quality_limited_source_ids: none
```

LLM extraction:

```text
llm_call_succeeded: True
normalized_record_count: 2
llm_extracted_2025_annual_cases_7: True
llm_extracted_2025_annual_deaths_3: True
```

Validation comparison:

| Row | Collection Record | Validation Record | Result |
|---|---|---|---|
| `eval_001` | 2025 New Mexico annual HPS record from LLM replay: `7 cases / 3 deaths` | Held-out NMDOH PDF: `2025 Total = 7` | `partial_match_not_comparable`; case count matches, death count not comparable |
| `eval_002` | 2026 Santa Fe County newly reported case: `1 confirmed case` | No matching held-out validation record | `missing_validation_record`; human review required |

## Source Separation Rule

Collection output is credible only if validation-reserved sources are blocked before extraction. In the current LLM extraction run, `source_role_safety_check.json` reports:

```json
{
  "validation_reserved_sources_excluded": true,
  "context_only_sources_excluded": true,
  "live_fetch_enabled": false,
  "api_key_printed": false
}
```
