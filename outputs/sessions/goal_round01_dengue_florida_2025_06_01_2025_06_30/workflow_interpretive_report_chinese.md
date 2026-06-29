# 数据收集结果解释报告

## 1. 本次任务

- disease: `Dengue`
- location: `Florida`
- date range: `2025-06-01 to 2025-06-30`
- target fields: cases, deaths, dates, locations, source URLs, source types, evidence quotes
- collection mode: `task_aware_quality_gated_records`
- session id: `goal_round01_dengue_florida_2025_06_01_2025_06_30`
- live search: `True`
- live fetch: `True`
- LLM stages: `True`
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
| final_dataset_pre_quality_gate_count | 43 |
| zero_case_statement_count | 16 |
| exposure_monitoring_record_count | 16 |
| surveillance_summary_record_count | 16 |
| outbreak_summary_record_count | 0 |
| context_record_count | 16 |
| unclassified_observation_count | 0 |
| non_primary_observation_count | 32 |
| quarantined_record_count | 0 |
| pending_review_record_count | 43 |
| final_dataset_post_review_count | 0 |
| run_quality_status | no_primary_case_dataset_records |
| primary_case_dataset_status | no_primary_case_dataset_records |
| suitable_as_final_epidemiological_dataset | False |

## 3.1 Coverage / extraction 状态

- coverage_status: `records_quarantined`
- source verification chain: predicted=1, discovered=1, fetched=1, fetch_failed=0, parsed=1, unusable=1, chunks=399, records=43, extracted=1, accepted=0
- failure_stage: `records_quarantined`.
- official_extraction_failure_reasons: `{'must_fetch_source_partially_skipped_due_to_chunk_cap': 14, 'must_fetch_source_not_attempted_for_extraction': 7}`

## 4. Primary case dataset 结果

没有产生通过质量门的 primary case dataset records。
本次发现的证据需要查看 zero-case、exposure monitoring、context、quarantined 等视图；这些证据有解释价值，但不直接回答 primary case-data 问题。

## 5. Global/task-aware dataset views

没有生成 global/task-aware dataset view。

## 5. 非病例但有用的公共卫生观察

- zero_case_statements: 16 条。zero-case statement 不是 confirmed case record。
- exposure_monitoring_records: 16 条。exposure monitoring 不是 confirmed/probable/suspected case record。
- surveillance_summary_records: 16 条。surveillance summary 可能是 aggregate，不一定是 individual case record。
- context_records: 16 条。context/background evidence 有背景价值，但不是 case count。
- non_primary_observations: 32 条。non-primary observations 保留为非主病例证据视图。

## 6. 跨来源印证结果

- claim_count: `43`
- claim_comparison_count: `903`
- corroborated_event_count: `7`
- corroborated_primary_case_event_count: `0`
- conflicting_claim_count: `17`
- single_source_unverified_count: `5`
这些字段表示 evidence support / single-source unverified / conflict 状态，不表示 automatic truth determination。

## 7. 数据源质量与可信度

- source_candidate_count: `40`
- fetched_document_count: `31`
- source_identity_assessed_count: `40`
- actual_publisher_unknown_count: `12`
- source_type_counts: `{'official_public_health_agency': 5, 'state_or_local_public_health_agency': 14, 'international_public_health_agency': 6, 'national_public_health_agency': 5, 'structured_database': 2, 'secondary_aggregator': 1, 'news_media': 5, 'background_fact_sheet': 1, 'social_media': 1}`
- source_critic_assessed_count: `0`
只有 source identity artifacts 支持时，报告才把来源解释为 official、news、context-only 或 unknown。

## 8. Validation 状态

- validation_source_compatibility_status: `validation_source_empty`
- validation_mode: `diagnostic_only`
- active_validation_record_count: `0`
- inactive_validation_record_count: `0`
- validation_limited: `False`

## 9. 被排除 / quarantined 的内容

- quarantined_record_count: `0`
- pending_review_record_count: `43`
这些内容没有进入 primary case dataset。需要查看 quarantined_records 和 record_inclusion_decisions 理解排除原因。

## 10. Human review 重点

- human_review_item_count: `103`
- 优先检查：是否有 source scope mismatch、validation limitation、publisher uncertainty、single-source unverified claims。
- review_source_credibility_src_search_53763309bf94: missing_publisher
- review_source_src_search_53763309bf94: Source classified as data_source; both screening and critic agree to include for content fetch.
- review_source_credibility_src_search_538a1d433fd1: This source is a PAHO/WHO international organization report on dengue epidemiology in the Americas, which carries very high institutional authority (authority_score=0.95) and strong disease relevance (disease_relevance_score=0.95). However, several compounding factors reduce its effective utility for this specific collection task and warrant careful advisory flags:

1. **Critical temporal mismatch**: The document URL explicitly references "Epidemiological Week 20, 2026," while the collection window is June 2025 (approximately Epi Weeks 22–26, 2025). This is a one-year discrepancy. The document either belongs to a future reporting cycle entirely outside the target window, or the URL metadata is erroneous. Either way, this is a serious mismatch that the deterministic assessment did not flag as a risk.

2. **Geographic granularity gap**: PAHO situation reports for the Americas aggregate data at the national or regional level. Florida-specific subnational data is unlikely to be explicitly named or disaggregated in this report. The geographic_granularity_score (0.58) and local_relevance_score (0.68) reflect this limitation. Even if U.S. national dengue counts appear, Florida attribution cannot be assumed without explicit confirmation in the document text.

3. **Screening and critic disagreement flag**: The presence of the `screening_and_critic_disagree` risk flag in the deterministic output is a meaningful signal that internal pipeline assessments diverged on this source. This warrants LLM-layer scrutiny.

4. **No snippet available**: With a null snippet, there is no direct textual evidence that this document contains Florida-specific or June 2025-specific data. The disease intelligence summary explicitly warns: "If PAHO or WHO situation reports reference U.S. dengue counts, confirm whether Florida is explicitly named before attributing counts to this geography."

5. **Role hint as validation is appropriate but limited**: PAHO reports can serve as regional validation context, but should not be used as a primary data source for Florida-level case counts. The validation role is correctly assigned, but the temporal mismatch severely limits even that utility.

6. **Query-URL year mismatch**: The query used was "PAHO WHO dengue situation report United States Florida June 2025," but the returned URL references 2026. This suggests a possible search result artifact, stale index entry, or URL construction error — none of which can be resolved without human review of the actual document.
- review_source_src_search_538a1d433fd1: Screening and critic disagree on this source; routing to human review for resolution.
- review_source_credibility_src_search_304300adfbfc: This source is a Substack-hosted article from "Outbreak News Today," a secondary news/media outlet rather than an official public health agency. The deterministic assessment correctly identifies it as medium credibility (0.57). Several factors warrant careful advisory consideration:

1. **Authority gap**: The authority score (0.48) is notably low. Substack is a self-publishing platform with no editorial gatekeeping at the platform level. "Outbreak News Today" is a known infectious disease news aggregator with a reasonable track record, but it is not an authoritative primary source. Its content is typically derivative of official agency releases (e.g., FDOH, CDC), which is reflected in the `possible_derivative_or_syndicated_source` flag.

2. **Missing publisher metadata**: The `publisher` field is null. For a Substack publication, the author/operator identity is critical to assessing credibility. Without confirmed publisher attribution, the source cannot be fully vetted.

3. **Independence concern**: The independence score (0.35) is low, reinforcing that this source likely re-reports from primary official sources rather than generating original surveillance data. Any case counts or dates extracted from this article should be traced back to the cited primary source (likely FDOH or CDC) before being recorded as collection data.

4. **Screening/critic disagreement flag**: The `screening_and_critic_disagree` risk flag is present, indicating internal pipeline tension about this source's role. This warrants advisory caution even though the deterministic layer did not escalate to human review.

5. **Role assignment**: The deterministic layer assigned `context` role, which is appropriate. This source should NOT be used as a primary data collection source. It may serve as a pointer or corroborating signal to locate the underlying official FDOH report, which should then be the actual collection source.

6. **Data signal present but unverified**: The title references "1st dengue local transmission case of 2025" — this is a specific, extractable claim. However, given the derivative nature of the source, this claim must be verified against the original FDOH arbovirus surveillance report before populating `cases_confirmed` or `cases_unspecified` fields.

7. **Time window alignment**: Timeliness (0.95) and local relevance (0.95) scores are strong, confirming the article is topically and temporally aligned with the collection task. This makes it a useful discovery artifact even if not a primary data source.

**Advisory recommendation**: Retain as `context` role. Use this source only to identify and navigate to the underlying official FDOH or CDC source. Do not extract case counts directly from this article for primary collection records without first confirming the original official source document. Human review is not urgently required but is advisable if no official FDOH primary source can be independently located to corroborate the claim.

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
