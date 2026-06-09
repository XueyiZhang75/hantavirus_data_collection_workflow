# Masked Validation Evaluation Report

This report summarizes the workflow's collection output against held-out validation evidence. It is an audit-oriented workflow evaluation report, not a full epidemiological benchmark.

## Collection Summary

- Collection record count: 6
- Validation record count: 1
- Evaluation row count: 7
- Rows with collection evidence: 6
- Rows with validation evidence: 1
- Rows with both collection and validation evidence: 0
- Masking compliance summary: passed=7
- Human review flagged row count: 7

## Held-Out Source Policy

- Reserved source IDs: src_nmdoh_hps_cases_by_county_1975_2025_pdf
- Reserved sources were blocked from collection and used only for validation comparison.

## Evaluation Status Counts

- Overall match status counts: missing_collection_record=1, missing_validation_record=6
- Masking compliance status counts: passed=7
- Provenance completeness status counts: complete=6, not_applicable_no_collection_record=1

## Evaluation Row Preview

- eval_001: location/date=China / 2022-04-20; collection_case_count=none; collection_death_count=none; collection_source_ids=src_search_0a2ee30734f3; collection_evidence_quote_preview="arency, everything is just a guess," said He. "It's a reasonable guess, it's an educated guess, but it is still a guess." The Shanghai government did not imm..."; validation_case_count=none; validation_death_count=none; validation_source_ids=none; validation_evidence_quote_preview="none"; overall_match_status=missing_validation_record; human_review_flag=true; review_reason=Collection record could not be validated against held-out records.
- eval_002: location/date=United States of America / 2025; collection_case_count=none; collection_death_count=none; collection_source_ids=none; collection_evidence_quote_preview="none"; validation_case_count=7; validation_death_count=none; validation_source_ids=src_nmdoh_hps_cases_by_county_1975_2025_pdf; validation_evidence_quote_preview="HPS Cases in New Mexico by County, 2025, Total = 7."; overall_match_status=missing_collection_record; human_review_flag=true; review_reason=Held-out validation record had no collection counterpart.
- eval_003: location/date=China / 2022-03-01; collection_case_count=500000; collection_death_count=285; collection_source_ids=src_search_0a2ee30734f3; collection_evidence_quote_preview="China's biggest COVID-19 outbreak, in Shanghai, has again raised questions about the country's official data - especially a death rate that despite a recent..."; validation_case_count=none; validation_death_count=none; validation_source_ids=none; validation_evidence_quote_preview="none"; overall_match_status=missing_validation_record; human_review_flag=true; review_reason=Collection record could not be validated against held-out records.
- eval_004: location/date=China / 2022-02-01; collection_case_count=1200000; collection_death_count=9000; collection_source_ids=src_search_0a2ee30734f3; collection_evidence_quote_preview="March. But deaths suddenly started to creep up over the past 11 days. The city of 25 million people has now reported 285 COVID-related fatalities since April..."; validation_case_count=none; validation_death_count=none; validation_source_ids=none; validation_evidence_quote_preview="none"; overall_match_status=missing_validation_record; human_review_flag=true; review_reason=Collection record could not be validated against held-out records.
- eval_005: location/date=China / 2022-04-17; collection_case_count=500000; collection_death_count=285; collection_source_ids=src_search_0a2ee30734f3; collection_evidence_quote_preview="March. But deaths suddenly started to creep up over the past 11 days. The city of 25 million people has now reported 285 COVID-related fatalities since April..."; validation_case_count=none; validation_death_count=none; validation_source_ids=none; validation_evidence_quote_preview="none"; overall_match_status=missing_validation_record; human_review_flag=true; review_reason=Collection record could not be validated against held-out records.
- eval_006: location/date=China / 2020-06-01; collection_case_count=none; collection_death_count=36000; collection_source_ids=src_search_0a2ee30734f3; collection_evidence_quote_preview="March. But deaths suddenly started to creep up over the past 11 days. The city of 25 million people has now reported 285 COVID-related fatalities since April..."; validation_case_count=none; validation_death_count=none; validation_source_ids=none; validation_evidence_quote_preview="none"; overall_match_status=missing_validation_record; human_review_flag=true; review_reason=Collection record could not be validated against held-out records.
- eval_007: location/date=China / 2019-01-01; collection_case_count=none; collection_death_count=4600; collection_source_ids=src_search_0a2ee30734f3; collection_evidence_quote_preview="March. But deaths suddenly started to creep up over the past 11 days. The city of 25 million people has now reported 285 COVID-related fatalities since April..."; validation_case_count=none; validation_death_count=none; validation_source_ids=none; validation_evidence_quote_preview="none"; overall_match_status=missing_validation_record; human_review_flag=true; review_reason=Collection record could not be validated against held-out records.

## Human Review Rows

- eval_001: China / 2022-04-20; status=missing_validation_record; reason=Collection record could not be validated against held-out records.
- eval_002: United States of America / 2025; status=missing_collection_record; reason=Held-out validation record had no collection counterpart.
- eval_003: China / 2022-03-01; status=missing_validation_record; reason=Collection record could not be validated against held-out records.
- eval_004: China / 2022-02-01; status=missing_validation_record; reason=Collection record could not be validated against held-out records.
- eval_005: China / 2022-04-17; status=missing_validation_record; reason=Collection record could not be validated against held-out records.
- eval_006: China / 2020-06-01; status=missing_validation_record; reason=Collection record could not be validated against held-out records.
- eval_007: China / 2019-01-01; status=missing_validation_record; reason=Collection record could not be validated against held-out records.

## Limitations

- Local test mode is synthetic.
- Broad web search is not implemented.
- Live validation is not implemented in the current workflow.
- External LLM use depends on the runtime profile.
- Missing collection records can occur when only held-out validation sources contain extractable data.
