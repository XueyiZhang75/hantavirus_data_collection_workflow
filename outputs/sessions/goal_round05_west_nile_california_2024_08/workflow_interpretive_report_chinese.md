# 数据收集结果解释报告

## 1. 本次任务

- disease: `West Nile virus`
- location: `California`
- date range: `2024-08-01 to 2024-08-31`
- target fields: cases, deaths, dates, locations, source URLs, source types, evidence quotes
- collection mode: `task_aware_quality_gated_records`
- session id: `goal_round05_west_nile_california_2024_08`
- live search: `True`
- live fetch: `True`
- LLM stages: `True`
- search provider: `tavily`

## 2. 一句话结论

本次 workflow 产生了 14 条通过质量门的 primary case dataset records；这些记录仍需结合来源身份、跨源印证状态和人工审核结果判断是否适合最终使用。

## 3. 最终数据状态

| Field | Value |
| --- | --- |
| final_case_dataset_count | 14 |
| global_outbreak_event_dataset_count | 0 |
| regional_surveillance_dataset_count | 0 |
| country_year_aggregate_dataset_count | 0 |
| official_alert_dataset_count | 0 |
| task_aware_data_product_count | 14 |
| final_dataset_count | 16 |
| final_dataset_pre_quality_gate_count | 37 |
| zero_case_statement_count | 27 |
| exposure_monitoring_record_count | 0 |
| surveillance_summary_record_count | 0 |
| outbreak_summary_record_count | 0 |
| context_record_count | 0 |
| unclassified_observation_count | 2 |
| non_primary_observation_count | 8 |
| quarantined_record_count | 11 |
| pending_review_record_count | 10 |
| final_dataset_post_review_count | 16 |
| run_quality_status | partial_with_quarantined_records |
| primary_case_dataset_status | primary_case_records_present |
| suitable_as_final_epidemiological_dataset | False |

## 3.1 Coverage / extraction 状态

- coverage_status: `target_official_source_accepted`
- source verification chain: predicted=1, discovered=1, fetched=1, fetch_failed=1, parsed=1, unusable=1, chunks=675, records=37, extracted=1, accepted=1
- official_extraction_failure_reasons: `{'must_fetch_source_not_attempted_for_extraction': 17, 'must_fetch_source_partially_skipped_due_to_chunk_cap': 5}`

## 4. Primary case dataset 结果

- disease=West Nile Virus Disease; location=United States of America; date=2024-08-31; cases_unspecified=9.0; source=[PDF] WEEKLY UPDATE - California West Nile Virus; publisher=unknown publisher; url=https://westnile.ca.gov/download?download_id=5061; corroboration_status=conflicting_claims; independent_source_count=3; evidence=A total of 9 new human cases of West Nile virus (WNV) disease were reported this week from 4 counties:
- disease=West Nile Virus Disease; location=United States of America; date=2024-08-31; cases_unspecified=4.0; source=[PDF] WEEKLY UPDATE - California West Nile Virus; publisher=unknown publisher; url=https://westnile.ca.gov/download?download_id=5061; corroboration_status=conflicting_claims; independent_source_count=2; evidence=Kern (4), Los Angeles (2), Sacramento (2), and Tulare (1). This is the first WNV positive human case
- disease=West Nile Virus Disease; location=United States of America; date=2024-08-31; cases_unspecified=2.0; source=[PDF] WEEKLY UPDATE - California West Nile Virus; publisher=unknown publisher; url=https://westnile.ca.gov/download?download_id=5061; corroboration_status=single_source_unverified; independent_source_count=1; evidence=Kern (4), Los Angeles (2), Sacramento (2), and Tulare (1). This is the first WNV positive human case
- disease=West Nile Virus Disease; location=United States of America; date=2024-08-31; cases_unspecified=2.0; source=[PDF] WEEKLY UPDATE - California West Nile Virus; publisher=unknown publisher; url=https://westnile.ca.gov/download?download_id=5061; corroboration_status=single_source_unverified; independent_source_count=1; evidence=Kern (4), Los Angeles (2), Sacramento (2), and Tulare (1). This is the first WNV positive human case
- disease=West Nile Virus Disease; location=United States of America; date=2024-08-31; cases_unspecified=1.0; source=[PDF] WEEKLY UPDATE - California West Nile Virus; publisher=unknown publisher; url=https://westnile.ca.gov/download?download_id=5061; corroboration_status=conflicting_claims; independent_source_count=2; evidence=Kern (4), Los Angeles (2), Sacramento (2), and Tulare (1). This is the first WNV positive human case

## 5. Global/task-aware dataset views

没有生成 global/task-aware dataset view。

## 5. 非病例但有用的公共卫生观察

- zero_case_statements: 27 条。zero-case statement 不是 confirmed case record。
- unclassified_observation_records: 2 条。unclassified observation 需要人工判断。
- non_primary_observations: 8 条。non-primary observations 保留为非主病例证据视图。

## 6. 跨来源印证结果

- claim_count: `43`
- claim_comparison_count: `903`
- corroborated_event_count: `9`
- corroborated_primary_case_event_count: `0`
- conflicting_claim_count: `31`
- single_source_unverified_count: `6`
这些字段表示 evidence support / single-source unverified / conflict 状态，不表示 automatic truth determination。

## 7. 数据源质量与可信度

- source_candidate_count: `41`
- fetched_document_count: `34`
- source_identity_assessed_count: `41`
- actual_publisher_unknown_count: `30`
- source_type_counts: `{'official_public_health_agency': 23, 'national_public_health_agency': 4, 'social_media': 6, 'news_media': 4, 'academic_or_peer_reviewed_source': 1, 'secondary_aggregator': 1, 'structured_database': 2}`
- source_critic_assessed_count: `0`
只有 source identity artifacts 支持时，报告才把来源解释为 official、news、context-only 或 unknown。

## 8. Validation 状态

- validation_source_compatibility_status: `validation_source_empty`
- validation_mode: `diagnostic_only`
- active_validation_record_count: `0`
- inactive_validation_record_count: `0`
- validation_limited: `False`

## 9. 被排除 / quarantined 的内容

- quarantined_record_count: `11`
- pending_review_record_count: `10`
这些内容没有进入 primary case dataset。需要查看 quarantined_records 和 record_inclusion_decisions 理解排除原因。

## 10. Human review 重点

- human_review_item_count: `125`
- 优先检查：是否有 source scope mismatch、validation limitation、publisher uncertainty、single-source unverified claims。
- review_source_credibility_src_search_99932da268a1: missing_publisher
- review_source_src_search_99932da268a1: Source classified as data_source; both screening and critic agree to include for content fetch.
- review_source_credibility_src_search_57a4e03b15a3: missing_publisher
- review_source_src_search_57a4e03b15a3: Source classified as data_source; both screening and critic agree to include for content fetch.
- review_source_src_search_7b25eaafb554: Screening and critic disagree on this source; routing to human review for resolution.

## 11. 可否作为最终流行病学数据集使用？

- suitable_as_final_epidemiological_dataset: `False`
如果该值为 false，说明当前输出不应直接作为最终病例数据集使用；它仍可作为 evidence audit 和人工复核输入。

## 12. 下一步建议

- 先查看 final_case_dataset，再决定是否使用任何病例计数字段。
- 查看 quarantined_records 和 record_inclusion_decisions，理解哪些证据被排除以及原因。
- 查看 source_identity_summary 和 source_identity_assessments，确认 publisher 是否清楚。
- 查看 corroboration_summary，确认 primary case claims 是否有跨来源支持。
- 如有需要，在单独的人审步骤中应用 human review decision file。

## 13. 关键文件索引

- `workflow_interpretive_report_chinese.md`
- `workflow_interpretive_report.md`
- `workflow_interpretive_report_summary.json`
- `workflow_run_report_chinese.md`
- `workflow_run_summary.json`
- `collection/final_case_dataset.csv`
- `collection/final_case_dataset.json`
- `collection/global_outbreak_event_dataset.csv`
- `collection/regional_surveillance_dataset.csv`
- `collection/country_year_aggregate_dataset.csv`
- `collection/official_alert_dataset.csv`
- `collection/final_dataset.csv`
- `collection/final_dataset_pre_quality_gate.csv`
- `collection/zero_case_statements.csv`
- `collection/exposure_monitoring_records.csv`
- `collection/context_records.csv`
- `collection/quarantined_records.csv`
- `diagnostics/run_quality_summary.json`
- `diagnostics/corroboration_summary.json`
- `diagnostics/source_identity_summary.json`
- `diagnostics/validation_source_compatibility_summary.json`

## 14. 重要声明

注意：本报告解释的是 workflow 收集到的证据及其一致性，不是官方监测结论，也不是医学建议。结果仍需公共卫生专家或项目研究者复核。
