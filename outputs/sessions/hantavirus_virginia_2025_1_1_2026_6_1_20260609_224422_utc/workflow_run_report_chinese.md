# data collection workflow Run Report

## 1. 输入任务

Collect hantavirus cases, deaths, dates, locations, source URLs, source types, and evidence quotes for virginia from 2025-1-1 to 2026-6-1.

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
- Search-derived source candidates: `12`
- Source credibility assessed sources: `12`
- Source credibility role counts: `{'collection': 6, 'collection_support': 2, 'excluded': 2, 'validation': 2}`
- Source discovery method: `live_search_only`
- Disease relevance target: `Hantavirus disease`
- Disease relevance source status counts: `{'target_disease_match': 8, 'ambiguous_disease': 4}`
- Disease relevance chunk status counts: `{'target_disease_match': 10, 'ambiguous_disease': 1}`
- Disease relevance record status counts: `{'compatible': 24}`
- Rejected incompatible record count: `0`
- Final route: `human_review`

## 2.5 Run quality status

- User-facing run status: `PARTIAL: accepted records produced, but some records were quarantined. Held-out validation was limited because no task-compatible validation source was available.`
- Technical execution status: `completed`
- Run quality status: `partial_with_quarantined_records`
- Final dataset mode: `quality_gated_accepted_records`
- Accepted final dataset count: `2`
- Pre-quality-gate record count: `8`
- Quarantined record count: `6`
- Pending review record count: `0`
- Final dataset post-review count: `2`
- Recommended user message: `Review final_dataset and warnings before use.`

Workflow technically completed and produced quality-gated accepted records.

Held-out validation was limited because no task-compatible validation source was available.
未找到与本次任务兼容的 held-out validation source；这不是自动失败，但 validation 有局限。

## 3. Workflow 运行过程

Graph is executed as a mostly serial workflow. The only conditional branch is after `quality_gate_routing`: the run enters `human_review` when quality or validation checks require review, then still builds the final data package. In this run, the graph route is shown above; validation comparison review flags are reported separately in Section 8.

1. `task_intake_and_scope_planning` - Built CollectionSpec from structured task input.
2. `disease_intelligence_builder` - Built disease intelligence from LLM output (Hantavirus disease).
3. `profile_and_schema_setup` - Built active disease profile, collection schema, and source strategy (Hantavirus disease, generation_method=legacy_ha...
4. `executable_source_planning` - Built executable source plan with 10 planned queries; no searches were executed.
5. `query_strategy_builder` - Built 87 search queries across 5 source categories (executable_source_plan_present=True).
6. `source_discovery` - Discovered 12 source candidates using live_search_only.
7. `source_dedup_and_registry` - Built source registry with 12 entries (0 duplicates dropped).
8. `source_screening` - Screened 12 sources using deterministic policy.
9. `source_critic_and_uncertainty_routing` - Critic reviewed 12 sources; 9 ready for fetch, 0 deferred, 5 flagged for human review.
10. `content_fetch_and_parse` - Built 3 fetch requests, produced 3 documents (live_fetch_enabled=True, fixture_documents_enabled=False, fixtures_load...
11. `document_quality_check` - Quality-checked 3 documents: 2 usable, 0 partial, 0 offline stub, 0 parse deferred, 1 unusable.
12. `evidence_chunking_and_data_presence_flagging` - Chunked 2/3 documents into 11 evidence chunks (10 flagged as containing target data).
13. `structured_extraction` - Built 8 raw records (extraction_mode=llm_structured_output, llm_enabled=True).
14. `schema_validation_and_repair` - Validated 8 raw records: 8 validated (3 need review), 0 rejected.
15. `record_normalization` - Normalized 8/8 records (3 need review).
16. `record_linking` - Linked 8/8 normalized records into 8 candidate events.
17. `cross_source_consistency_check` - Checked 0 multi-record events; found 0 new conflicts and 16 validation results (0 events need review).
18. `quality_gate_routing` - Human review required: 37 item(s) in human_review_queue.
19. `human_review` - Processed 37 review item(s): 37 pending, 0 reviewed, 0 follow-up, 0 deferred, 0 decision(s) applied.
20. `final_data_package_builder` - Assembled hardened FinalDataPackage from current state.

## 4. 数据源分工

| Role | Source ID | Publisher / title | Credibility | Final decision | Fetch ready |
|---|---|---|---|---|---|
| other | src_search_b604b9f3bf56 | Tavily / Hantavirus - Hantavirus | high (0.8735) | include_for_content_fetch | True |
| other | src_search_d25ebe9350db | Tavily / What's going around? Hantavirus outbreak update: what Virginians ... | high (0.8943) | include_for_content_fetch | True |
| other | src_search_2c82cbb57185 | Tavily / Virginia monitors for possible hantavirus, report says - Facebook | high (0.8735) | include_for_content_fetch | True |
| other | src_search_328d9634735f | Tavily / 2026 Hantavirus Cases in America | high (0.8943) | include_for_content_fetch | True |
| other | src_search_b4e86545a452 | Tavily / HOMETOWN HEALTH: Hantavirus outbreak reaches 11 cases | high (0.8943) | include_for_content_fetch | True |
| other | src_search_51c8baee009e | Tavily / Virginia reports first child flu death of 2025-2026 season - Facebook | needs_review (0.6943) | exclude | False |
| other | src_search_71eb2fbf98fb | Tavily / Virginia reports first child flu death of 2025-2026 season - WVEC | medium (0.6943) | exclude | False |
| other | src_search_04ec3f646e9f | Tavily / Virginia at “high” flu-activity level as cases rise nationwide - WWBT | high (0.8943) | exclude | False |
| other | src_search_2b73fb537776 | Tavily / Virginia reports first child flu death of 2025-2026 season - YouTube | excluded (0.6943) | include_for_content_fetch | True |
| other | src_search_af9c0518dc0a | Tavily / VDH confirms 8th measles case of 2026, surpassing 2025 total | excluded (0.6943) | include_for_content_fetch | True |
| other | src_search_6aa749dc5e67 | Tavily / Hantavirus in Virginia 2026: Outbreak Status & Risk / Virus Watcher | high (0.8831) | include_for_content_fetch | True |
| other | src_search_2b117627a7d9 | Tavily / Hantavirus: Diagnosis, Surveillance, and 2026 Outbreak Updates / Today's Clinical Lab | high (0.8831) | include_for_content_fetch | True |

## 5. 真实网页抓取结果

- Documents fetched/parsed: `3`
- Search-derived sources selected for fetch: `3`
- Search-derived skipped by reason: `{'needs_review_not_allowed': 4, 'final_role_excluded': 5}`
- Fetch status counts: `fetch_failed=1, fetched=2`
- Parser status counts: `parsed_html=3`
- Parser used counts: `html_stdlib_parser=3`
- Quality status counts: `unusable=1, usable=2`
- Validation-reserved skipped from fetch: `[]`

| Source ID | Fetch status | HTTP | Parse | Parser | Quality | Text chars | Tables |
|---|---|---|---|---|---|---|---|
| src_search_b604b9f3bf56 | fetched | 200 | parsed_html | html_stdlib_parser | usable | 5286 | 0 |
| src_search_2b117627a7d9 | fetch_failed | 403 | parsed_html | html_stdlib_parser | unusable | 599 | 0 |
| src_search_6aa749dc5e67 | fetched | 200 | parsed_html | html_stdlib_parser | usable | 10172 | 0 |

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

- Attempted source count: `6`
- Assessed source count: `6`
- Skipped source count: `6`
- Blocked fetch count: `3`
- Allowed fetch count: `0`
- Context-only count: `0`
- Needs review count: `3`
- Max sources: `6`
- Review blocks fetch: `False`
- Failure count: `0`
- Semantic leakage count: `2`
- Human review recommended count: `3`
- Critic decision counts: `include_conditional=1, needs_human_review=2, not_task_relevant=3`
- Fetch recommendation counts: `block_fetch=3, fetch_only_after_human_review=3`
- Risk flag counts: `ambiguous_page_type_fact_sheet_vs_surveillance_data=1, context_only_risk_ambiguous_segment_format=1, context_only_risk_cannot_be_excluded_without_snippet=1, disease_mismatch=3, incorrect_publisher_attribution=1, incorrect_source_type_classification=1, low_credibility_domain=1, low_credibility_news_source_not_official_agency=1, missing_published_date=1, missing_snippet=1, news_source_not_official_public_health_agency=1, no_extractable_data=2, no_snippet_available=3, null_published_date=1, null_published_date_time_window_unverifiable=1, only_background_or_context=3, query_term_match_not_content_confirmed=1, query_terms_not_reflected_in_title=1, semantic_leakage_risk=2, semantic_leakage_risk_from_news_citing_authority=1, semantic_leakage_risk_news_cites_authority=1, social_media_domain=1, social_media_platform=1, source_type_misclassification=4, time_window_unverifiable=1`
- Selected source IDs: `src_search_51c8baee009e, src_search_b604b9f3bf56, src_search_71eb2fbf98fb, src_search_d25ebe9350db, src_search_04ec3f646e9f, src_search_2c82cbb57185`

### 6.3 Optional LLM Source Credibility Advisory

- Enabled: `True`
- Assessed source count: `12`
- Final role counts: `collection=6, collection_support=2, excluded=2, validation=2`
- Risk flag counts: `2025_window_data_may_not_yet_be_published_reporting_lag_risk=1, CRITICAL:publisher_is_discovery_tool — publisher listed as 'Tavily' (a search engine/API), not a health authority or news outlet; provenance is unverified=1, CRITICAL:source_type_misclassification — domain is facebook.com (social media), not an official_public_health_agency; authority_score=0.95 and credibility_score=0.87 are invalid artifacts of this error=1, HIGH:null_snippet — no content has been retrieved or verified; all relevance and data signal scores are based on metadata only, not actual source content=1, HIGH:secondary_news_source_misclassified — post originates from '12OnYourSide', a local TV news account; this is a news/media source, not a public health agency=1, HIGH:semantic_leakage_risk — any apparent authority derives from a news article citing a health agency, not from the agency itself; confirmed by flags llm_semantic_leakage_risk and llm_context_only_risk=1, HIGH:social_media_platform — facebook.com posts are not citable primary sources for epidemiological surveillance data; content is ephemeral, editable, and unverified=1, INFO:disease_term_match_is_title_only — 'hantavirus' found in title/URL metadata only; no body content verified due to null snippet=1, MEDIUM:data_granularity_low — data_granularity_score=0.68 and machine_readability_score=0.72 are below thresholds suitable for structured epidemiological data extraction=1, MEDIUM:no_data_signal_confirmed — source_disease_relevance_data_signal_count=0; no quantitative case, death, or hospitalization data has been detected in this source=1, MEDIUM:underlying_source_not_retrieved — the Facebook post likely references a VDH report or news article; that primary source has not been identified or assessed=1, ambiguous_disease=4, ambiguous_disease_signal_in_source_metadata=4, authority_score_inflation:0.95_inconsistent_with_facebook_tv_news_video=1, authority_score_inflation_due_to_misclassification=1, authority_score_likely_inflated_due_to_source_type_label_error=1, authorship_and_institutional_affiliation_unknown=1, collection_task_utility:none=1, complete_source_provenance=12, consumer_health_segment_format:whats_going_around_series=1, context_or_background_only=1, data_granularity_moderate_aggregate_counts_only_likely=1, data_signal_in_source_metadata=12, deterministic_scores_likely_reflect_assumed_not_verified_source_type=1, disease_mismatch:influenza_not_hantavirus=1, domain_is_user_generated_content_platform=1, false_positive_search_result:query_hps_virginia_returned_flu_content=1, forward_dated_title_raises_document_type_uncertainty=1, hantavirus_historically_rare_in_virginia_low_yield_expected=1, independence_score_likely_inflated_due_to_source_type_label_error=1, international_organization_authority=2, llm_context_only_risk=3, llm_context_only_risk:ambiguous_segment_format_limits_data_extractability=1, llm_context_only_risk_cannot_exclude_without_snippet=1, llm_semantic_leakage_risk=2, llm_semantic_leakage_risk:source_may_reference_authority_data_without_being_authoritative=1, llm_source_critic:context_only_risk_ambiguous_segment_format=1, llm_source_critic:context_only_risk_cannot_be_excluded_without_snippet=1, llm_source_critic:semantic_leakage_risk=2, llm_source_critic:semantic_leakage_risk_from_news_citing_authority=1, llm_source_critic:semantic_leakage_risk_news_cites_authority=1, local_or_subnational_granularity=12, local_source_matches_task_location=12, machine_readability_moderate_unstructured_html_likely=1, no_confirmed_virginia_case_level_data_signal=1, no_snippet_available:content_not_verified=1, no_snippet_available_content_unverified=1, no_snippet_no_extractable_evidence=1, null_snippet_no_content_level_verification=1, official_public_health_authority=10, outbreak_claim_requires_corroboration:11_hantavirus_cases_exceeds_historical_virginia_baseline=1, page_may_be_static_educational_content_not_surveillance_data=1, primary_or_authoritative_source=12, provenance_ambiguity:actual_publisher_unverified=1, publisher_field_is_search_api_not_actual_publisher:tavily=1, publisher_field_populated_by_discovery_tool_not_actual_publisher:tavily_listed_instead_of_wdbj7=1, publisher_field_reflects_search_intermediary_not_primary_source=1, publisher_is_discovery_tool_not_content_author=1, publisher_is_search_aggregator_not_primary_source=1, role_hint_collection_may_be_inappropriate_for_news_summary_source=1, secondary_source_risk:news_outlet_likely_cites_vdh_or_cdc_not_primary_data=1, snippet_null:content_not_available_for_verification=1, source_disease_relevance:ambiguous_disease=4, source_disease_relevance:target_disease_match=8, source_metadata_matches_requested_disease=8, source_priority_tier_should_be_news_and_situation_report_not_official_public_health_agency=1, source_time_matches_requested_window=12, source_type_classification_likely_inflated=1, source_type_metadata_error:misclassified_as_official_public_health_agency=1, source_type_misclassification:domain_is_local_tv_news_not_official_public_health_agency=1, source_type_misclassification:wsls.com_is_local_tv_news_not_official_public_health_agency=1, standard_web_page=12, storymaps_format_unlikely_to_support_structured_field_level_data=1, title_scope_is_national_not_virginia_specific=1, true_publisher_is_local_tv_news:13NewsNow=1, url_date_anomaly:article_dated_2026-05-13_requires_existence_verification=1, wrong_platform:social_media_video_facebook=1, zero_data_signal_count_in_source_metadata=1, zero_hantavirus_data_signals_in_title_or_metadata=1`
- LLM assessed count: `6`
- LLM failure count: `0`
- Needs review count: `1`

### 6.4 LLM Structured Extraction

- Extraction mode: `llm_structured_output`
- Eligible chunk count: `10`
- LLM call count: `8`
- LLM success count: `8`
- LLM error count: `0`
- Raw record count: `8`

## 7. 最终抽取 records

- Normalized record count: `8`
- Run quality status: `partial_with_quarantined_records`
- Final dataset mode: `quality_gated_accepted_records`
- Quality-gated accepted final dataset count: `2`
- Pre-quality-gate record count: `8`
- Quarantined record count: `6`
- Pending review record count: `0`
- Final dataset post-review count: `2`
- Record inclusion status counts: `{'quarantined_outside_scope': 6, 'accepted_with_warnings': 2}`
- Run quality warnings: `['geography_mismatch: geography mismatch', 'no task-compatible held-out validation source is active', 'no_task_compatible_validation_source', 'validation_limited_no_compatible_source']`
- Accepted source counts: `src_search_6aa749dc5e67=1, src_search_b604b9f3bf56=1`

| Record ID | Date / period | Location | Cases | Deaths | Source | LLM used |
|---|---|---|---|---|---|---|
| rec_src_search_b604b9f3bf56_002 | none | Virginia | none | none | src_search_b604b9f3bf56 | True |
| rec_src_search_6aa749dc5e67_002 | 2026-06-09 | Virginia | 0.0 | none | src_search_6aa749dc5e67 | True |

## 8. Validation 对比

- Validation source compatibility status: `incompatible_validation_source_disabled`
- Active / inactive / raw validation records: `0` / `1` / `1`
- Validation record count: `0`
- Evaluation row count: `0`
- Evaluation rows flagged for human review: `0`
- Overall match status counts: `none`
- Masking compliance status counts: `none`
- Reserved source leakage count: `0`

| Eval row | Status | Collection cases | Validation cases | Human review | Reason |
|---|---|---|---|---|---|

## 9. Human review queue

- Human review item count: `37`
- Evaluation review flag count: `0`
- Anomaly review item count: `8`

| Review ID | Type | Related IDs | Reason |
|---|---|---|---|
| review_record_rec_src_search_6aa749dc5e67_003 | record_schema_validation | rec_src_search_6aa749dc5e67_003 | Record requires review after schema validation: missing_review_trigger_fields: ['country', 'date'] |
| review_record_rec_src_search_6aa749dc5e67_006 | record_schema_validation | rec_src_search_6aa749dc5e67_006 | Record requires review after schema validation: missing_review_trigger_fields: ['date'] |
| review_record_rec_src_search_b604b9f3bf56_001 | record_schema_validation | rec_src_search_b604b9f3bf56_001 | Record requires review after schema validation: missing_review_trigger_fields: ['country'] |
| review_linking_event_001 | record_linking | rec_src_search_6aa749dc5e67_003 | Linked event requires review: regional_or_aggregate_geographic_scope, missing_date_anchor, existing_record_requires_human_review |
| review_linking_event_002 | record_linking | rec_src_search_6aa749dc5e67_006 | Linked event requires review: missing_date_anchor, existing_record_requires_human_review |
| review_linking_event_006 | record_linking | rec_src_search_b604b9f3bf56_001 | Linked event requires review: existing_record_requires_human_review |
| review_linking_event_008 | record_linking | rec_src_search_b604b9f3bf56_002 | Linked event requires review: missing_date_anchor |
| review_normalization_rec_src_search_6aa749dc5e67_003 | record_normalization | rec_src_search_6aa749dc5e67_003 | Record requires review after normalization: regional_or_aggregate_geographic_scope |
| review_normalization_rec_src_search_6aa749dc5e67_006 | record_normalization | rec_src_search_6aa749dc5e67_006 | Record requires review after normalization: unrecognized_country_name |
| review_normalization_rec_src_search_b604b9f3bf56_001 | record_normalization | rec_src_search_b604b9f3bf56_001 | Record requires review after normalization: unrecognized_virus_or_syndrome, unrecognized_case_definition |
| review_source_src_search_2c82cbb57185 | source_screening | src_search_2c82cbb57185 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_src_search_328d9634735f | source_screening | src_search_328d9634735f | Source classified as data_source; both screening and critic agree to include for content fetch. |

## 9.5 Stage 11 anomaly detection and review application

- Anomaly result count: `9`
- Anomaly severity counts: `high=6, low=1, medium=2`
- Anomaly needs-human-review count: `8`
- Decisions provided: `0`
- Decisions applied: `0`
- Decisions rejected: `0`
- Audit entries: `0`
- Final dataset post-review count: `2`
- Records excluded by review: `0`

| Anomaly ID | Type | Severity | Target | Reason |
|---|---|---|---|---|
| anom_001 | deaths_without_case_reference | low | rec_src_search_6aa749dc5e67_001 | deaths present but no comparable case count is available |
| anom_002 | missing_date_for_count_bearing_record | medium | rec_src_search_6aa749dc5e67_003 | count-bearing record has no usable date, reporting period, as-of date, or date anchor |
| anom_003 | missing_date_for_count_bearing_record | medium | rec_src_search_6aa749dc5e67_006 | count-bearing record has no usable date, reporting period, as-of date, or date anchor |
| anom_004 | out_of_scope_count_bearing_record | high | event_006 | Stage 10 validation marked record outside requested scope: outside_geography |
| anom_005 | out_of_scope_count_bearing_record | high | event_007 | Stage 10 validation marked record outside requested scope: outside_geography |
| anom_006 | out_of_scope_count_bearing_record | high | event_001 | Stage 10 validation marked record outside requested scope: insufficient_scope_information;outside_geography |
| anom_007 | out_of_scope_count_bearing_record | high | event_004 | Stage 10 validation marked record outside requested scope: outside_geography |
| anom_008 | out_of_scope_count_bearing_record | high | event_003 | Stage 10 validation marked record outside requested scope: outside_geography |
| anom_009 | out_of_scope_count_bearing_record | high | event_002 | Stage 10 validation marked record outside requested scope: insufficient_scope_information;outside_geography |

| Applied decision | Type | Target | Audit IDs | Reason |
|---|---|---|---|---|

## 10. 输出文件

- Run output directory: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\hantavirus_virginia_2025_1_1_2026_6_1_20260609_224422_utc`
- Collection final dataset: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\hantavirus_virginia_2025_1_1_2026_6_1_20260609_224422_utc\collection\final_dataset.csv`
- Collection pre-quality-gate records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\hantavirus_virginia_2025_1_1_2026_6_1_20260609_224422_utc\collection\final_dataset_pre_quality_gate.csv`
- Collection quarantined records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\hantavirus_virginia_2025_1_1_2026_6_1_20260609_224422_utc\collection\quarantined_records.csv`
- Collection pending review records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\hantavirus_virginia_2025_1_1_2026_6_1_20260609_224422_utc\collection\pending_review_records.csv`
- Collection record inclusion decisions: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\hantavirus_virginia_2025_1_1_2026_6_1_20260609_224422_utc\collection\record_inclusion_decisions.json`
- Collection final dataset post-review: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\hantavirus_virginia_2025_1_1_2026_6_1_20260609_224422_utc\collection\final_dataset_post_review.csv`
- Collection anomaly results: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\hantavirus_virginia_2025_1_1_2026_6_1_20260609_224422_utc\collection\anomaly_results.json`
- Collection human review audit trail: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\hantavirus_virginia_2025_1_1_2026_6_1_20260609_224422_utc\collection\human_review_audit_trail.json`
- Collection source registry: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\hantavirus_virginia_2025_1_1_2026_6_1_20260609_224422_utc\collection\source_registry.json`
- Validation ground truth: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\hantavirus_virginia_2025_1_1_2026_6_1_20260609_224422_utc\validation\ground_truth_records.csv`
- Inactive validation records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\hantavirus_virginia_2025_1_1_2026_6_1_20260609_224422_utc\validation\inactive_validation_records.csv`
- Validation compatibility summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\hantavirus_virginia_2025_1_1_2026_6_1_20260609_224422_utc\validation\validation_source_compatibility_summary.json`
- Evaluation report CSV: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\hantavirus_virginia_2025_1_1_2026_6_1_20260609_224422_utc\evaluation\evaluation_report.csv`
- Human-readable report: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\hantavirus_virginia_2025_1_1_2026_6_1_20260609_224422_utc\workflow_run_report_chinese.md`

## 11. 当前结论

This workflow run executed the configured data collection workflow through the exported graph and artifact pipeline. The user-facing run status is: PARTIAL: accepted records produced, but some records were quarantined. Held-out validation was limited because no task-compatible validation source was available.
The run completed technically and produced quality-gated accepted records in the final dataset.

- Package metadata says LLM used: `True`
- Contains synthetic fixture data: `False`
- Generated at UTC: `2026-06-09T22:50:45.756641+00:00`
