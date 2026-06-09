# HDC Workflow Run Report

## 1. 输入任务

Collect hantavirus cases, deaths, dates, locations, source URLs, source types, and evidence quotes for shanghai from 2024-1-1 to 2026-6-9.

## 2. 本次运行模式

- Live webpage fetch: `True`
- Fixture documents: `False`
- Provider: `anthropic`
- Model: `claude-sonnet-4-6`
- API key present: `True`
- LLM source planning: `True`
- LLM source critic: `True`
- LLM structured extraction: `True`
- Source search mode: `live`
- Source search provider: `tavily`
- Source search executed queries: `3`
- Search-derived source candidates: `13`
- Source credibility assessed sources: `13`
- Source credibility role counts: `{'collection': 9, 'context': 1, 'validation': 3}`
- Source discovery method: `live_search_only`
- Final route: `human_review`

## 3. Workflow 运行过程

Graph is executed as a mostly serial workflow. The only conditional branch is after `quality_gate_routing`: the run enters `human_review` when quality or validation checks require review, then still builds the final data package. In this run, the graph route is shown above; validation comparison review flags are reported separately in Section 8.

1. `task_intake_and_scope_planning` - Built CollectionSpec from structured task input.
2. `disease_intelligence_builder` - Built disease intelligence from LLM output (Hantavirus disease).
3. `profile_and_schema_setup` - Built active disease profile, collection schema, and source strategy (Hantavirus disease, generation_method=legacy_ha...
4. `executable_source_planning` - Built executable source plan with 10 planned queries; no searches were executed.
5. `query_strategy_builder` - Built 103 search queries across 5 source categories (executable_source_plan_present=True).
6. `source_discovery` - Discovered 13 source candidates using live_search_only.
7. `source_dedup_and_registry` - Built source registry with 13 entries (0 duplicates dropped).
8. `source_screening` - Screened 13 sources using deterministic policy.
9. `source_critic_and_uncertainty_routing` - Critic reviewed 13 sources; 13 ready for fetch, 0 deferred, 6 flagged for human review.
10. `content_fetch_and_parse` - Built 5 fetch requests, produced 5 documents (live_fetch_enabled=True, fixture_documents_enabled=False, fixtures_load...
11. `document_quality_check` - Quality-checked 5 documents: 1 usable, 1 partial, 0 offline stub, 1 parse deferred, 2 unusable.
12. `evidence_chunking_and_data_presence_flagging` - Chunked 2/5 documents into 6 evidence chunks (5 flagged as containing target data).
13. `structured_extraction` - Built 6 raw records (extraction_mode=llm_structured_output, llm_enabled=True).
14. `schema_validation_and_repair` - Validated 6 raw records: 6 validated (0 need review), 0 rejected.
15. `record_normalization` - Normalized 6/6 records (0 need review).
16. `record_linking` - Linked 6/6 normalized records into 6 candidate events.
17. `cross_source_consistency_check` - Checked 0 multi-record events; found 0 new conflicts and 19 validation results (0 events need review).
18. `quality_gate_routing` - Human review required: 30 item(s) in human_review_queue.
19. `human_review` - Processed 30 review item(s): 30 pending, 0 reviewed, 0 follow-up, 0 deferred, 0 decision(s) applied.
20. `final_data_package_builder` - Assembled hardened FinalDataPackage from current state.

## 4. 数据源分工

| Role | Source ID | Publisher / title | Credibility | Final decision | Fetch ready |
|---|---|---|---|---|---|
| other | src_search_08cf20494fd9 | Tavily / WHO chief: 10 cases of hantavirus confirmed, 3 deaths. - CGTN | high (0.8943) | include_for_content_fetch | True |
| other | src_search_501c9c481a0c | Tavily / Number of reported cases of hantavirus rises to 12, 3 reported deaths: WHO-Xinhua | high (0.8943) | include_for_content_fetch | True |
| other | src_search_477f248340c2 | Tavily / Hantavirus.com / Health News and Prevention Updates | high (0.8943) | include_for_content_fetch | True |
| other | src_search_116ea8be024e | Tavily / 2026 Hantavirus Outbreak: Testing for Potential Infection / HAN - CDC | high (0.8943) | include_for_content_fetch | True |
| other | src_search_d2c95c97786f | Tavily / 2026 Multi-country Hantavirus Cluster Linked to Cruise Ship - CDC | high (0.8943) | include_for_content_fetch | True |
| other | src_search_033a69706576 | Tavily / Shanghai Has Recorded More Than 130,000 Covid Cases—and No ... | high (0.8943) | include_for_content_fetch | True |
| other | src_search_898dc88a55b7 | Tavily / Are cause of death data for Shanghai fit for purpose? A retrospective ... | high (0.8943) | include_for_content_fetch | True |
| other | src_search_06be6be13693 | Tavily / [PDF] Persistence HFRS Infection Risk Among Migrant Outdoor Labours in ... | high (0.8183) | include_for_content_fetch | True |
| other | src_search_0a2ee30734f3 | Tavily / EXPLAINER-Shanghai death numbers raise questions over its ... | high (0.8943) | include_for_content_fetch | True |
| other | src_search_c155b4affddf | Tavily / Shanghai reports first COVID deaths amid sweeping lockdowns | high (0.8943) | include_for_content_fetch | True |
| other | src_search_2b117627a7d9 | Tavily / Hantavirus: Diagnosis, Surveillance, and 2026 Outbreak Updates | high (0.8831) | include_for_content_fetch | True |
| other | src_search_cf7456cc310b | Tavily / [PDF] Vol. 6 No. 36 Sept. 6, 2024 - China CDC Weekly | high (0.8071) | include_for_content_fetch | True |
| other | src_search_c9772c2d0cc4 | Tavily / Epidemic Reports - National Disease Control and Prevention ... | high (0.8831) | include_for_content_fetch | True |

## 5. 真实网页抓取结果

- Documents fetched/parsed: `5`
- Search-derived sources selected for fetch: `5`
- Search-derived skipped by reason: `{'needs_review_not_allowed': 6, 'max_search_derived_sources_reached': 2}`
- Fetch status counts: `fetch_failed=2, fetched=3`
- Parser status counts: `parse_deferred=1, parsed_html=4`
- Parser used counts: `html_stdlib_parser=4, pdf_parse_deferred=1`
- Quality status counts: `parse_deferred=1, partial=1, unusable=2, usable=1`
- Validation-reserved skipped from fetch: `[]`

| Source ID | Fetch status | HTTP | Parse | Parser | Quality | Text chars | Tables |
|---|---|---|---|---|---|---|---|
| src_search_06be6be13693 | fetched | 200 | parse_deferred | pdf_parse_deferred | parse_deferred | 0 | 0 |
| src_search_0a2ee30734f3 | fetched | 200 | parsed_html | html_stdlib_parser | usable | 7509 | 0 |
| src_search_898dc88a55b7 | fetched | 200 | parsed_html | html_stdlib_parser | partial | 165 | 0 |
| src_search_c155b4affddf | fetch_failed | 403 | parsed_html | html_stdlib_parser | unusable | 46 | 0 |
| src_search_2b117627a7d9 | fetch_failed | 403 | parsed_html | html_stdlib_parser | unusable | 599 | 0 |

## 6. 三个 LLM 环节调用结果

### 6.1 LLM Source Planning

- Status: `success`
- Plan generation method: `llm_executable_source_plan`
- Plan execution status: `planned_not_executed`
- Planned query count: `10`
- Planned source category count: `5`
- Provider channel counts: `database_search=2, literature_api=2, news_search=2, official_site_search=4`
- Agent query count: `10`
- Agent query added count: `10`
- Candidate hint count: `0`

### 6.2 LLM Source Critic

- Attempted source count: `0`
- Assessed source count: `0`
- Skipped source count: `13`
- Max sources: `6`
- Review blocks fetch: `False`
- Failure count: `0`
- Semantic leakage count: `0`
- Human review recommended count: `0`

### 6.3 Optional LLM Source Credibility Advisory

- Enabled: `True`
- Assessed source count: `13`
- Final role counts: `collection=9, context=1, validation=3`
- Risk flag counts: `CRITICAL_DISEASE_MISMATCH: Article covers COVID-19, not hantavirus/HFRS — zero disease-relevant content for collection task=1, CRITICAL_SOURCE_TYPE_MISCLASSIFICATION: wsj.com is a commercial news outlet, not an official_public_health_agency — source_type field is factually incorrect=1, CRITICAL_TIME_WINDOW_MISMATCH: Article publication date (~April 2022 based on URL epoch timestamp) falls entirely outside required collection window 2024-01-01 to 2026-06-09=1, DETERMINISTIC_SCORING_FAILURE: Deterministic scorer awarded high scores for authority, disease relevance, timeliness, and source type — all are false positives for this source in this task context=1, FALSE_POSITIVE_RISK_FLAGS: All positive deterministic risk flags (official_public_health_authority, source_metadata_matches_requested_disease, source_time_matches_requested_window, etc.) are incorrect and should be disregarded=1, PUBLISHER_METADATA_ANOMALY: Publisher listed as 'Tavily' (a search API intermediary), not the actual publisher (Wall Street Journal) — provenance_score of 1.0 is not warranted=1, SNIPPET_NULL: No snippet available to verify any content relevance; title alone confirms COVID-19 subject matter, not hantavirus=1, SOURCE_PRIORITY_TIER_DEMOTION: Even if content were relevant, wsj.com qualifies only as news_and_situation_report — the lowest priority tier per collection_spec source_priority hierarchy=1, authority_score_and_credibility_level_likely_inflated_due_to_misclassification=1, authority_score_inflation_risk: deterministic authority_score of 0.95 reflects assumed official agency status; if reclassified as news media, authority score should be reduced to approximately 0.55–0.65=1, authority_score_unsupported: 0.95 authority score is not justified by any recognized institutional affiliation in the metadata=1, collection_role_blocked: source must not be used for primary case/outbreak data collection=1, collection_role_provisional_pending_content_verification=1, complete_source_provenance=13, context_or_background_only=3, data_signal_in_source_metadata=13, deterministic_local_relevance_score_likely_inflated=1, deterministic_local_relevance_score_likely_overestimated=1, deterministic_risk_flags_are_positive_signals_not_genuine_risk_indicators=1, deterministic_scores_inconsistent_with_role_downgrade: credibility scored 0.89/high despite role being downgraded to context=1, disease_named_commercial_domain: 'hantavirus.com' matches a pattern common to low-authority or commercial health content sites=1, future_url_date_flag: URL date of 2026-05-15 is within collection window but should be verified as a real published article and not a placeholder or misdated result=1, geographic_granularity_unconfirmed_no_snippet_to_verify_shanghai_specificity=1, geographic_mismatch_title_vs_task_location=1, geographic_mismatch_us_cdc_vs_shanghai_target=1, geographic_scope_unverified: title references WHO chief statement with no explicit confirmation that case/death counts are Shanghai-specific rather than national or global=1, han_notice_is_us_domestic_alert_format_not_china_surveillance=1, human_review_marked_false_despite_multiple_unresolved_metadata_concerns=1, international_organization_authority=3, local_or_subnational_granularity=13, local_source_matches_task_location=13, low_machine_readability=2, multi_country_framing_inconsistent_with_subnational_shanghai_data_need=1, no_institutional_affiliation_confirmed: no link to CDC, WHO, NHC, Shanghai CDC, or any recognized health authority=1, null_snippet: no content has been verified from this source; all scores are based on metadata only=1, null_snippet_content_unverifiable=1, null_snippet_prevents_evidence_quote_and_required_field_validation=1, official_public_health_authority=10, pdf_or_report_likely_medium_readability=2, pipeline_misclassification_risk: downstream collection steps may incorrectly treat this source as official if credibility score is not corrected=1, possible_hallucinated_or_fabricated_url_from_search_tool=1, primary_or_authoritative_source=13, primary_source_absent: this is a secondary news report of a WHO statement — a primary WHO Disease Outbreak News or NHC bulletin should be sought to corroborate=1, publisher_field_reflects_discovery_tool_not_content_originator=1, publisher_is_search_aggregator: Tavily is a web search/retrieval service, not a primary publisher=1, publisher_is_search_aggregator_not_direct_origin=1, publisher_is_search_intermediary_not_primary_source=1, publisher_metadata_inconsistency: publisher field lists 'Tavily' (a search tool) rather than CGTN — provenance chain is incomplete=1, query_result_alignment_suspicious_us_source_for_china_query=1, secondary_reporting_of_who_data_primary_source_not_directly_accessed=1, snippet_null: no evidence quote available to verify content relevance, geographic scope, or data granularity=1, snippet_null_no_content_verified=1, source_may_not_contain_required_fields_for_task=1, source_metadata_matches_requested_disease=13, source_time_matches_requested_window=13, source_type_misclassification: domain is news.cgtn.com (state media broadcaster), not an official_public_health_agency — reclassify as news_and_situation_report=1, source_type_misclassification_suspected: domain 'hantavirus.com' is not a recognized official public health agency=1, source_type_misclassified_news_wire_tagged_as_official_public_health_agency=1, standard_web_page=11, state_media_editorial_risk: CGTN is a Chinese state-owned international broadcaster; editorial framing may reflect official government positions and may omit or delay unfavorable epidemiological detail=1, title_indicates_cruise_ship_cluster_not_shanghai_surveillance=1, title_references_2026_outbreak_requires_verification=1`
- LLM assessed count: `6`
- LLM failure count: `0`
- Needs review count: `0`

### 6.4 LLM Structured Extraction

- Extraction mode: `llm_structured_output`
- Eligible chunk count: `5`
- LLM call count: `5`
- LLM success count: `5`
- LLM error count: `0`
- Raw record count: `6`

## 7. 最终抽取 records

- Normalized record count: `6`
- Source counts: `src_search_0a2ee30734f3=6`

| Record ID | Date / period | Location | Cases | Deaths | Source | LLM used |
|---|---|---|---|---|---|---|
| rec_src_search_0a2ee30734f3_001 | Since April 17, 2022 | Shanghai | 500000.0 | 285.0 | src_search_0a2ee30734f3 | True |
| rec_src_search_0a2ee30734f3_002 | Since April 17 | Shanghai | 500000.0 | 285.0 | src_search_0a2ee30734f3 | True |
| rec_src_search_0a2ee30734f3_003 | Since February | Hong Kong | 1200000.0 | 9000.0 | src_search_0a2ee30734f3 | True |
| rec_src_search_0a2ee30734f3_004 | 2019-01-01 | Wuhan and surrounding Hubei province | none | 4600.0 | src_search_0a2ee30734f3 | True |
| rec_src_search_0a2ee30734f3_005 | 2020-06-01 | Wuhan | none | 36000.0 | src_search_0a2ee30734f3 | True |
| rec_src_search_0a2ee30734f3_006 | 2022-04-20 | Shanghai | none | none | src_search_0a2ee30734f3 | True |

## 8. Validation 对比

- Validation record count: `1`
- Evaluation row count: `7`
- Evaluation rows flagged for human review: `7`
- Overall match status counts: `missing_collection_record=1, missing_validation_record=6`
- Masking compliance status counts: `passed=7`
- Reserved source leakage count: `0`

| Eval row | Status | Collection cases | Validation cases | Human review | Reason |
|---|---|---|---|---|---|
| eval_001 | missing_validation_record | none | none | True | Collection record could not be validated against held-out records. |
| eval_002 | missing_collection_record | none | 7 | True | Held-out validation record had no collection counterpart. |
| eval_003 | missing_validation_record | 500000 | none | True | Collection record could not be validated against held-out records. |
| eval_004 | missing_validation_record | 1200000 | none | True | Collection record could not be validated against held-out records. |
| eval_005 | missing_validation_record | 500000 | none | True | Collection record could not be validated against held-out records. |
| eval_006 | missing_validation_record | none | none | True | Collection record could not be validated against held-out records. |
| eval_007 | missing_validation_record | none | none | True | Collection record could not be validated against held-out records. |

## 9. Human review queue

- Human review item count: `37`
- Evaluation review flag count: `7`
- Anomaly review item count: `6`

| Review ID | Type | Related IDs | Reason |
|---|---|---|---|
| review_validation_eval_001 | masked_validation | eval_001, event_005 | Collection record could not be validated against held-out records. |
| review_validation_eval_002 | masked_validation | eval_002, event_new_mexico_hps_2025 | Held-out validation record had no collection counterpart. |
| review_validation_eval_003 | masked_validation | eval_003, event_006 | Collection record could not be validated against held-out records. |
| review_validation_eval_004 | masked_validation | eval_004, event_001 | Collection record could not be validated against held-out records. |
| review_validation_eval_005 | masked_validation | eval_005, event_002 | Collection record could not be validated against held-out records. |
| review_validation_eval_006 | masked_validation | eval_006, event_004 | Collection record could not be validated against held-out records. |
| review_validation_eval_007 | masked_validation | eval_007, event_003 | Collection record could not be validated against held-out records. |
| review_source_src_search_033a69706576 | source_screening | src_search_033a69706576 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_src_search_08cf20494fd9 | source_screening | src_search_08cf20494fd9 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_src_search_116ea8be024e | source_screening | src_search_116ea8be024e | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_src_search_477f248340c2 | source_screening | src_search_477f248340c2 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_src_search_501c9c481a0c | source_screening | src_search_501c9c481a0c | Source classified as data_source; both screening and critic agree to include for content fetch. |

## 9.5 Stage 11 anomaly detection and review application

- Anomaly result count: `8`
- Anomaly severity counts: `high=5, low=2, medium=1`
- Anomaly needs-human-review count: `6`
- Decisions provided: `0`
- Decisions applied: `0`
- Decisions rejected: `0`
- Audit entries: `0`
- Final dataset post-review count: `6`
- Records excluded by review: `0`

| Anomaly ID | Type | Severity | Target | Reason |
|---|---|---|---|---|
| anom_001 | abrupt_spike_simple_threshold | medium | rec_src_search_0a2ee30734f3_003 | case count exceeds configured simple anomaly threshold |
| anom_002 | deaths_without_case_reference | low | rec_src_search_0a2ee30734f3_004 | deaths present but no comparable case count is available |
| anom_003 | deaths_without_case_reference | low | rec_src_search_0a2ee30734f3_005 | deaths present but no comparable case count is available |
| anom_004 | out_of_scope_count_bearing_record | high | event_006 | Stage 10 validation marked record outside requested scope: outside_time_window |
| anom_005 | out_of_scope_count_bearing_record | high | event_001 | Stage 10 validation marked record outside requested scope: insufficient_scope_information;outside_geography |
| anom_006 | out_of_scope_count_bearing_record | high | event_003 | Stage 10 validation marked record outside requested scope: outside_geography;outside_time_window |
| anom_007 | out_of_scope_count_bearing_record | high | event_004 | Stage 10 validation marked record outside requested scope: outside_geography;outside_time_window |
| anom_008 | out_of_scope_count_bearing_record | high | event_005 | Stage 10 validation marked record outside requested scope: outside_time_window |

| Applied decision | Type | Target | Audit IDs | Reason |
|---|---|---|---|---|

## 10. 输出文件

- Run output directory: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\hantavirus_shanghai_2024_1_1_2026_6_9_20260609_141441_utc`
- Collection final dataset: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\hantavirus_shanghai_2024_1_1_2026_6_9_20260609_141441_utc\collection\final_dataset.csv`
- Collection final dataset post-review: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\hantavirus_shanghai_2024_1_1_2026_6_9_20260609_141441_utc\collection\final_dataset_post_review.csv`
- Collection anomaly results: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\hantavirus_shanghai_2024_1_1_2026_6_9_20260609_141441_utc\collection\anomaly_results.json`
- Collection human review audit trail: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\hantavirus_shanghai_2024_1_1_2026_6_9_20260609_141441_utc\collection\human_review_audit_trail.json`
- Collection source registry: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\hantavirus_shanghai_2024_1_1_2026_6_9_20260609_141441_utc\collection\source_registry.json`
- Validation ground truth: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\hantavirus_shanghai_2024_1_1_2026_6_9_20260609_141441_utc\validation\ground_truth_records.csv`
- Evaluation report CSV: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\hantavirus_shanghai_2024_1_1_2026_6_9_20260609_141441_utc\evaluation\evaluation_report.csv`
- Human-readable report: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\hantavirus_shanghai_2024_1_1_2026_6_9_20260609_141441_utc\workflow_run_report_chinese.md`

## 11. 当前结论

This workflow run executes the HDC workflow end to end: a user request enters the LangGraph state, the graph fetches controlled real web sources, calls all three LLM stages, separates collection and validation sources, extracts structured records, compares against held-out validation evidence, and flags unresolved validation rows for human review.

- Package metadata says LLM used: `True`
- Contains synthetic fixture data: `False`
- Generated at UTC: `2026-06-09T14:19:12.497836+00:00`
