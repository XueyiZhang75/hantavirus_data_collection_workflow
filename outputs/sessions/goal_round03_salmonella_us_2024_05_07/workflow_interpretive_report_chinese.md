# 数据收集结果解释报告

## 1. 本次任务

- disease: `Salmonella`
- location: `United States`
- date range: `2024-05-01 to 2024-07-31`
- target fields: cases, deaths, dates, locations, source URLs, source types, evidence quotes
- collection mode: `task_aware_quality_gated_records`
- session id: `goal_round03_salmonella_us_2024_05_07`
- live search: `True`
- live fetch: `True`
- LLM stages: `True`
- search provider: `tavily`

## 2. 一句话结论

本次 workflow 产生了 5 条通过质量门的 primary case dataset records；这些记录仍需结合来源身份、跨源印证状态和人工审核结果判断是否适合最终使用。

## 3. 最终数据状态

| Field | Value |
| --- | --- |
| final_case_dataset_count | 5 |
| global_outbreak_event_dataset_count | 0 |
| regional_surveillance_dataset_count | 0 |
| country_year_aggregate_dataset_count | 0 |
| official_alert_dataset_count | 0 |
| task_aware_data_product_count | 5 |
| final_dataset_count | 8 |
| final_dataset_pre_quality_gate_count | 15 |
| zero_case_statement_count | 0 |
| exposure_monitoring_record_count | 0 |
| surveillance_summary_record_count | 5 |
| outbreak_summary_record_count | 0 |
| context_record_count | 0 |
| unclassified_observation_count | 3 |
| non_primary_observation_count | 4 |
| quarantined_record_count | 6 |
| pending_review_record_count | 1 |
| final_dataset_post_review_count | 8 |
| run_quality_status | partial_with_quarantined_records |
| primary_case_dataset_status | primary_case_records_present |
| suitable_as_final_epidemiological_dataset | False |

## 3.1 Coverage / extraction 状态

- coverage_status: `target_official_source_accepted`
- source verification chain: predicted=1, discovered=1, fetched=1, fetch_failed=1, parsed=1, unusable=1, chunks=415, records=15, extracted=1, accepted=1
- official_extraction_failure_reasons: `{'must_fetch_source_not_attempted_for_extraction': 7, 'must_fetch_source_partially_skipped_due_to_chunk_cap': 13}`

## 4. Primary case dataset 结果

- disease=Salmonellosis (non-typhoidal Salmonella); location=United States of America; date=2024-07-31; hospitalizations=24.0; source=Reoccurring Salmonella Cotham Outbreak Linked to Pet Bearded Dragons — United States, 2024  | MMWR; publisher=Centers for Disease Control and Prevention; url=https://www.cdc.gov/mmwr/volumes/74/wr/mm7431a1.htm?ACSTrackingID=USCDC_921-DM149359&ACSTrackingLabel=Week+in+MMWR%3A+Vol.+74%2C+August+21%2C+2025&deliveryName=USCDC_921-DM149359; corroboration_status=conflicting_claims; independent_source_count=3; evidence=| ****Hospitalization (n = 24)**** | |
- disease=Salmonellosis (non-typhoidal Salmonella); location=United States of America; date=2024-07-31; cases_unspecified=551.0; source=Outbreak Investigation of Salmonella: Cucumbers (June 2024) - FDA; publisher=unknown publisher; url=https://www.fda.gov/food/outbreaks-foodborne-illness/outbreak-investigation-salmonella-cucumbers-june-2024; corroboration_status=conflicting_claims; independent_source_count=3; evidence=Total Illnesses: 551
- disease=Salmonellosis (non-typhoidal Salmonella); location=United States of America; date=2024-07-31; hospitalizations=155.0; source=Outbreak Investigation of Salmonella: Cucumbers (June 2024) - FDA; publisher=unknown publisher; url=https://www.fda.gov/food/outbreaks-foodborne-illness/outbreak-investigation-salmonella-cucumbers-june-2024; corroboration_status=conflicting_claims; independent_source_count=3; evidence=Hospitalizations: 155
- disease=Salmonellosis (non-typhoidal Salmonella); location=United States of America; date=2024-07-31; cases_confirmed=7314.0, cases_unspecified=9219.0; source=FoodNet 2024 Preliminary Data | FoodNet | CDC; publisher=Centers for Disease Control and Prevention; url=https://www.cdc.gov/foodnet/reports/preliminary-data.html; corroboration_status=conflicting_claims; independent_source_count=3; evidence=Among 9,219 *Salmonella* infections reported, 7,314 (79%) infections had positive culture results.
- disease=Salmonellosis (non-typhoidal Salmonella); location=United States of America; date=2024-07-31; cases_unspecified=6066.0; source=FoodNet 2024 Preliminary Data | FoodNet | CDC; publisher=Centers for Disease Control and Prevention; url=https://www.cdc.gov/foodnet/reports/preliminary-data.html; corroboration_status=conflicting_claims; independent_source_count=3; evidence=Among the positive culture results, laboratories fully serotyped 6,066 (83%) isolates. The most common serotypes detected were

## 5. Global/task-aware dataset views

没有生成 global/task-aware dataset view。

## 5. 非病例但有用的公共卫生观察

- surveillance_summary_records: 5 条。surveillance summary 可能是 aggregate，不一定是 individual case record。
- unclassified_observation_records: 3 条。unclassified observation 需要人工判断。
- non_primary_observations: 4 条。non-primary observations 保留为非主病例证据视图。

## 6. 跨来源印证结果

- claim_count: `16`
- claim_comparison_count: `120`
- corroborated_event_count: `2`
- corroborated_primary_case_event_count: `0`
- conflicting_claim_count: `8`
- single_source_unverified_count: `1`
这些字段表示 evidence support / single-source unverified / conflict 状态，不表示 automatic truth determination。

## 7. 数据源质量与可信度

- source_candidate_count: `32`
- fetched_document_count: `28`
- source_identity_assessed_count: `32`
- actual_publisher_unknown_count: `10`
- source_type_counts: `{'national_public_health_agency': 15, 'official_public_health_agency': 7, 'academic_or_peer_reviewed_source': 5, 'social_media': 1, 'news_media': 3, 'structured_database': 1}`
- source_critic_assessed_count: `0`
只有 source identity artifacts 支持时，报告才把来源解释为 official、news、context-only 或 unknown。

## 8. Validation 状态

- validation_source_compatibility_status: `validation_source_empty`
- validation_mode: `diagnostic_only`
- active_validation_record_count: `0`
- inactive_validation_record_count: `0`
- validation_limited: `False`

## 9. 被排除 / quarantined 的内容

- quarantined_record_count: `6`
- pending_review_record_count: `1`
这些内容没有进入 primary case dataset。需要查看 quarantined_records 和 record_inclusion_decisions 理解排除原因。

## 10. Human review 重点

- human_review_item_count: `45`
- 优先检查：是否有 source scope mismatch、validation limitation、publisher uncertainty、single-source unverified claims。
- review_source_credibility_src_search_5851bdcbd35f: missing_publisher
- review_source_src_search_5851bdcbd35f: Source classified as data_source; both screening and critic agree to include for content fetch.
- review_source_credibility_src_search_33733b13ba13: missing_publisher
- review_source_src_search_33733b13ba13: Source classified as data_source; both screening and critic agree to include for content fetch.
- review_source_credibility_src_search_3faf6631782d: missing_publisher

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
