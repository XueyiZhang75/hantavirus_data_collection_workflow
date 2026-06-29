# 数据收集结果解释报告

## 1. 本次任务

- disease: `hantavirus`
- location: `New Mexico`
- date range: `2020 to 2026`
- target fields: cases, deaths, dates, locations, source URLs, source types, evidence quotes
- collection mode: `task_aware_quality_gated_records`
- session id: `test_session`
- live search: `True`
- live fetch: `False`
- LLM stages: `False`
- search provider: `tavily`

## 2. 一句话结论

本次 workflow 技术上完成了真实搜索、抓取、抽取、筛选和导出流程，但没有产生通过质量门的 primary case dataset records；因此不能把本次输出解释为已确认的目标地区病例数据集。

## 3. 最终数据状态

| Field | Value |
| --- | --- |
| final_case_dataset_count | 0 |
| global_outbreak_event_dataset_count | 0 |
| regional_surveillance_dataset_count | 0 |
| country_year_aggregate_dataset_count | 0 |
| official_alert_dataset_count | 0 |
| task_aware_data_product_count | 0 |
| final_dataset_count | 0 |
| final_dataset_pre_quality_gate_count | 0 |
| zero_case_statement_count | 0 |
| exposure_monitoring_record_count | 0 |
| surveillance_summary_record_count | 0 |
| outbreak_summary_record_count | 0 |
| context_record_count | 0 |
| unclassified_observation_count | 0 |
| non_primary_observation_count | 0 |
| quarantined_record_count | 0 |
| pending_review_record_count | 0 |
| final_dataset_post_review_count | 0 |
| run_quality_status | no_task_relevant_records |
| primary_case_dataset_status | unknown_no_claim_outputs |
| suitable_as_final_epidemiological_dataset | False |

## 3.1 Coverage / extraction 状态

- coverage_status: `parsed_no_records`
- source verification chain: predicted=6, discovered=2, fetched=2, fetch_failed=0, parsed=2, unusable=0, chunks=0, records=0, extracted=0, accepted=0
- failure_stage: `no_chunks`.
- 2 个官方目标来源已经 discovered/fetched/parsed，但没有产出 extracted records。

## 4. Primary case dataset 结果

没有产生通过质量门的 primary case dataset records。
本次发现的证据需要查看 zero-case、exposure monitoring、context、quarantined 等视图；这些证据有解释价值，但不直接回答 primary case-data 问题。

## 5. Global/task-aware dataset views

没有生成 global/task-aware dataset view。

## 5. 非病例但有用的公共卫生观察

没有非病例观察视图包含记录。

## 6. 跨来源印证结果

- claim_count: `0`
- claim_comparison_count: `0`
- corroborated_event_count: `0`
- corroborated_primary_case_event_count: `0`
- conflicting_claim_count: `0`
- single_source_unverified_count: `0`
这些字段表示 evidence support / single-source unverified / conflict 状态，不表示 automatic truth determination。

## 7. 数据源质量与可信度

- source_candidate_count: `20`
- fetched_document_count: `5`
- source_identity_assessed_count: `20`
- actual_publisher_unknown_count: `4`
- source_type_counts: `{'state_or_local_public_health_agency': 5, 'national_public_health_agency': 4, 'international_public_health_agency': 6, 'search_endpoint': 3, 'unknown': 1, 'news_media': 1}`
- source_critic_assessed_count: `0`
只有 source identity artifacts 支持时，报告才把来源解释为 official、news、context-only 或 unknown。

## 8. Validation 状态

- validation_source_compatibility_status: `live_validation_pending`
- validation_mode: `live_cross_source`
- active_validation_record_count: `0`
- inactive_validation_record_count: `0`
- validation_limited: `True`
Live cross-source validation was limited because this run did not find a task-compatible validation source. This does not prove absence of cases; it means the live search/fetch set did not include enough independent validation evidence.

## 9. 被排除 / quarantined 的内容

- quarantined_record_count: `0`
- pending_review_record_count: `0`
这些内容没有进入 primary case dataset。需要查看 quarantined_records 和 record_inclusion_decisions 理解排除原因。

## 10. Human review 重点

- human_review_item_count: `0`
- 优先检查：是否有 source scope mismatch、validation limitation、publisher uncertainty、single-source unverified claims。

## 11. 可否作为最终流行病学数据集使用？

- suitable_as_final_epidemiological_dataset: `False`
如果该值为 false，说明当前输出不应直接作为最终病例数据集使用；它仍可作为 evidence audit 和人工复核输入。

## 12. 下一步建议

- 不要把本次 run 当作最终 primary case dataset 使用。
- 先查看 final_case_dataset，再决定是否使用任何病例计数字段。
- 查看 quarantined_records 和 record_inclusion_decisions，理解哪些证据被排除以及原因。
- 查看 source_identity_summary 和 source_identity_assessments，确认 publisher 是否清楚。
- 查看 corroboration_summary，确认 primary case claims 是否有跨来源支持。
- 如有需要，在单独的人审步骤中应用 human review decision file。
- Add or discover task-compatible live validation sources for cross-source validation.

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
