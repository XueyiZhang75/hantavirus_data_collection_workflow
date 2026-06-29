# data collection workflow Run Report

## 1. 输入任务

Collect FLU cases, deaths, dates, locations, source URLs, source types, and evidence quotes for UNITED STATES from 2024-09-29 to 2024-10-05.

## 2. 本次运行模式

- Live webpage fetch: `True`
- Fixture documents: `False`
- Provider: `anthropic`
- Model: `claude-sonnet-4-6`
- API key present: `True`
- LLM source planning: `True`
- LLM source critic: `True`
- LLM source identity assessed sources: `0`
- LLM structured extraction: `True`
- Source search mode: `live`
- Source search provider: `tavily`
- Source search executed queries: `5`
- Search-derived source candidates: `33`
- Iterative source discovery: `True`
- Iterative search iterations: `2`
- Iterative stop decision: `stop_sufficient`
- Iterative stop reason: `Max iterations (2) reached per bounds constraint. The stop condition is also independently satisfied: the primary CDC FluView Week 40 source (week ending October 5, 2024) is confirmed, the Mississippi state PDF is confirmed for the exact task window, and additional state-level and international candidates appeared in iteration 2 results. Further searching would not be permitted under the stated bounds and is not needed given the confirmed primary source coverage.`
- Source credibility assessed sources: `33`
- Source credibility role counts: `{'context': 19, 'collection': 4, 'excluded': 2, 'validation': 7, 'collection_support': 1}`
- Source identity assessed sources: `33`
- Source identity type counts: `{'national_public_health_agency': 15, 'official_public_health_agency': 6, 'academic_or_peer_reviewed_source': 1, 'international_public_health_agency': 5, 'unknown': 1, 'state_or_local_public_health_agency': 1, 'secondary_aggregator': 1, 'social_media': 1, 'news_media': 2}`
- Source identity warning counts: `{'search_provider_not_publisher': 33, 'publisher_from_search_metadata_unverified': 33, 'direct_target_official_fast_path_skips_source_identity': 33, 'actual_publisher_unknown': 11}`
- Source discovery method: `live_search_only`
- Disease relevance target: `FLU`
- Disease relevance source status counts: `{'target_disease_match': 29, 'ambiguous_disease': 3, 'insufficient_text': 1}`
- Disease relevance chunk status counts: `{'target_disease_match': 37, 'ambiguous_disease': 3}`
- Disease relevance record status counts: `{'compatible': 39}`
- Rejected incompatible record count: `0`
- Final route: `finalize`

## 2.5 Run quality status

- User-facing run status: `PARTIAL: accepted records produced, but some records were quarantined.`
- Technical execution status: `completed`
- Run quality status: `partial_with_quarantined_records`
- Final dataset mode: `task_aware_quality_gated_records`
- Accepted final dataset count: `5`
- Final case dataset count: `0`
- Zero-case statement count: `0`
- Exposure-monitoring record count: `0`
- Surveillance summary record count: `13`
- Outbreak summary record count: `0`
- Context record count: `0`
- Unclassified observation count: `3`
- Observation dataset view counts: `{'final_case_dataset': 0, 'global_outbreak_event_dataset': 0, 'regional_surveillance_dataset': 0, 'country_year_aggregate_dataset': 0, 'official_alert_dataset': 0, 'probable_case_dataset': 0, 'suspected_case_dataset': 0, 'unspecified_case_dataset': 0, 'death_dataset': 1, 'hospitalization_dataset': 0, 'zero_case_statements': 0, 'exposure_monitoring_records': 0, 'surveillance_summary_records': 13, 'outbreak_summary_records': 0, 'context_records': 0, 'non_primary_observations': 13, 'unclassified_observation_records': 3}`
- Pre-quality-gate record count: `13`
- Quarantined record count: `6`
- Pending review record count: `2`
- Non-primary observation count: `8`
- Final dataset post-review count: `5`
- Primary-case dataset status: `no_primary_case_dataset_records`
- Recommended primary dataset message: `No primary case dataset records were accepted; inspect zero-case, exposure-monitoring, context, and other observation views.`
- Primary-case eligible accepted count: `0`
- Corroborated primary case event count: `0`
- Recommended user message: `Review final_dataset and warnings before use.`

Workflow technically completed and produced quality-gated accepted records.

Workflow technically completed, but no primary case dataset records were accepted. Non-primary observations were preserved separately and should not be read as final epidemiological case data.

## 3. Workflow 运行过程

Graph is executed as a mostly serial workflow. The only conditional branch is after `quality_gate_routing`: the run enters `human_review` when quality or validation checks require review, then still builds the final data package. In this run, the graph route is shown above; validation comparison review flags are reported separately in Section 8.

1. `task_intake_and_scope_planning` - Built CollectionSpec from structured task input.
2. `disease_intelligence_builder` - Built disease intelligence from LLM output (Influenza (Seasonal)).
3. `profile_and_schema_setup` - Built active disease profile, collection schema, and source strategy (Influenza (Seasonal), generation_method=disease...
4. `executable_source_planning` - Built executable source plan with 10 planned queries; no searches were executed.
5. `query_strategy_builder` - Built 10 direct_collection search queries from the LLM evidence strategy plan.
6. `source_discovery` - Discovered 34 source candidates using live_search_only.
7. `source_dedup_and_registry` - Built source registry with 33 entries (1 duplicates dropped).
8. `source_screening` - Screened 33 sources using deterministic policy.
9. `source_critic_and_uncertainty_routing` - Critic reviewed 33 sources; 17 ready for fetch, 0 deferred, 20 flagged for human review.
10. `content_fetch_and_parse` - Built 1 fetch requests, produced 1 documents (live_fetch_enabled=True, fixture_documents_enabled=False, fixtures_load...
11. `document_quality_check` - Quality-checked 1 documents: 1 usable, 0 partial, 0 offline stub, 0 parse deferred, 0 unusable.
12. `evidence_chunking_and_data_presence_flagging` - Chunked 1/1 documents into 40 evidence chunks (40 flagged as containing target data).
13. `structured_extraction` - Built 13 raw records (extraction_mode=llm_structured_output, llm_enabled=True).
14. `schema_validation_and_repair` - Validated 13 raw records: 13 validated (0 need review), 0 rejected.
15. `record_normalization` - Normalized 13/13 records (0 need review).
16. `record_linking` - Linked 13/13 normalized records into 6 candidate events.
17. `cross_source_consistency_check` - Checked 5 multi-record events; found 1 new conflicts and 33 validation results (0 events need review).
18. `quality_gate_routing` - Human review disabled; preserving review flags as audit metadata and routing to final_data_package_builder.
19. `final_data_package_builder` - Assembled hardened FinalDataPackage from current state.

## 4. 数据源分工

| Role | Source ID | Publisher / title | Credibility | Final decision | Fetch ready |
|---|---|---|---|---|---|
| context_only | src_search_88387812c274 | Centers for Disease Control and Prevention / Weekly US Influenza Surveillance Report: Key Updates for Week 51, ending December 21, 2024 /... | high (0.7826) | needs_human_review | False |
| context_only | src_search_a3695468387b | Centers for Disease Control and Prevention / Weekly US Influenza Surveillance Report: Key Updates for ... - CDC | high (0.7826) | needs_human_review | False |
| context_only | src_search_1cb29ce91f47 | Centers for Disease Control and Prevention / Weekly US Influenza Surveillance Report: Key Updates for Week 45, ending November 8, 2025 /... | medium (0.7642) | needs_human_review | False |
| context_only | src_search_7edb5942f160 | Centers for Disease Control and Prevention / Weekly US Influenza Surveillance Report: Key Updates for Week 51, ending December 20, 2025 /... | medium (0.7642) | needs_human_review | False |
| context_only | src_search_0a7b36e413fd | Centers for Disease Control and Prevention / Weekly US Influenza Surveillance Report: Key Updates for Week 40, ending October 4, 2025 / F... | medium (0.7642) | needs_human_review | False |
| context_only | src_search_0fff1ff8aec5 | Centers for Disease Control and Prevention / Weekly US Influenza Surveillance Report: Key Updates for Week 53, ending January 3, 2026 / F... | medium (0.7642) | needs_human_review | False |
| context_only | src_search_a0e8401d0c66 | Centers for Disease Control and Prevention / Weekly US Influenza Surveillance Report: Key Updates for Week 26, ending June 28, 2025 / Flu... | medium (0.7642) | needs_human_review | False |
| context_only | src_search_6bdc29e2c410 | World Health Organization / [PDF] Influenza weekly bulletin Week 13-2025 | medium (0.6176) | needs_human_review | False |
| context_only | src_search_5b8e18366c05 | / [PDF] The flu activity code for CDC week 41 ending October 15, 2005 is 1 ... | medium (0.6762) | needs_human_review | False |
| context_only | src_search_7c93d846b7e6 | Centers for Disease Control and Prevention / Weekly US Influenza Surveillance Report: Key Updates for ... - CDC | medium (0.7642) | needs_human_review | False |
| context_only | src_search_a413156d78b1 | Centers for Disease Control and Prevention / Weekly US Influenza Surveillance Report: Key Updates for ... - CDC | medium (0.7642) | needs_human_review | False |
| context_only | src_search_1db831c204ad | Centers for Disease Control and Prevention / Weekly US Influenza Surveillance Report: Key Updates for Week 15, ending April 12, 2025 / Fl... | medium (0.7642) | needs_human_review | False |
| context_only | src_search_0ecd29cced03 | / 2024–2025 United States flu season - Wikipedia | medium (0.5735) | needs_human_review | False |
| context_only | src_search_ab285e09d5d1 | / US flu map update for 2024-25 season - Facebook | medium (0.5618) | needs_human_review | False |
| context_only | src_search_50b73d583e75 | / US CDC says 2025-26 flu season 'moderately severe' as cases hit ... | low (0.5434) | needs_human_review | False |
| context_only | src_search_1597eeb7830a | / Flu hospitalization rate in 2024-25 highest in more than a decade / AHA News | low (0.5024) | needs_human_review | False |
| other | src_search_ff1cee7a6f74 | Centers for Disease Control and Prevention / Weekly US Influenza Surveillance Report: Key Updates for Week 40, ending October 5, 2024 / F... | high (0.8826) | include_for_content_fetch | True |
| other | src_search_c95c26c7b200 | / [PDF] 2024-2025 Influenza Surveillance Report Week 40 | medium (0.7352) | include_for_content_fetch | True |
| other | src_search_39cef9614d66 | Centers for Disease Control and Prevention / FluView - CDC | high (0.8434) | include_for_content_fetch | True |
| other | src_search_539f7fa2e3a0 | / Microsoft Word - Wk 40 2023-2024 | excluded (0.5352) | include_for_content_fetch | True |
| other | src_search_7813d28aa66e | / Week%2010%202024-2025.pdf | excluded (0.5352) | include_for_content_fetch | True |
| other | src_search_3ca7d0dccaf3 | CIDRAP / US data highlight severity of 2024-25 flu season / CIDRAP | high (0.8826) | include_for_content_fetch | True |
| other | src_search_56ae1d93a391 | Centers for Disease Control and Prevention / 2024–2025 Influenza Season Summary: Severity, Disease Burden, and Burden Prevented / Flu Bur... | high (0.8826) | include_for_content_fetch | True |
| other | src_search_e0370422d92f | Centers for Disease Control and Prevention / Influenza Activity in the United States during the 2024–25 Season ... | high (0.8943) | include_for_content_fetch | True |
| other | src_search_56888319c899 | / 2024 to 2025 US Influenza Season Sets Record Hospitalization Rate | high (0.8706) | include_for_content_fetch | True |
| other | src_search_4fcd8a7806fd | Centers for Disease Control and Prevention / Influenza Activity in the United States during the 2023–2024 Season and Composition of the 2... | high (0.8943) | include_for_content_fetch | True |
| other | src_search_329a386dc3ea | Pan American Health Organization / [PDF] Epidemiological Alert Seasonal Influenza in the Americas Region: | medium (0.708) | include_for_content_fetch | True |
| other | src_search_5295f90ea0dd | Pan American Health Organization / Current Seasonal Influenza Situation and Public Health Recommendations in the Americas - PAHO/WHO / Pa... | high (0.784) | include_for_content_fetch | True |
| other | src_search_a528d9bf475d | Pan American Health Organization / Regional Update, Influenza and Other Respiratory Viruses ... | high (0.8322) | include_for_content_fetch | True |
| other | src_search_79e3303d15e2 | Pan American Health Organization / Influenza, SARS-CoV-2, RSV and other Respiratory Viruses Regional Situation - PAHO/WHO / Pan American... | high (0.7842) | include_for_content_fetch | True |
| other | src_search_6f32d2cabad1 | / National Flu Activity Map - FFF Enterprises | medium (0.7608) | include_for_content_fetch | True |
| other | src_search_913d37203900 | health.ny.gov / 2024-10-26_flu_report.pdf | needs_review (0.6018) | include_for_content_fetch | True |
| other | src_search_915efec17eac | / [PDF] Respiratory Viruses Update | needs_review (0.5602) | include_for_content_fetch | True |

## 5. 真实网页抓取结果

- Documents fetched/parsed: `1`
- Search-derived sources selected for fetch: `1`
- Search-derived skipped by reason: `{}`
- Fetch status counts: `fetched=1`
- External fetch enabled: `True`
- Fetch provider counts: `tavily_extract=1`
- External fetch failure counts: `none`
- Selected fetch bucket counts: `target_official_authority=1`
- Parser status counts: `parsed_text=1`
- Parser used counts: `text_parser=1`
- Quality status counts: `usable=1`
- Validation-reserved skipped from fetch: `[]`

| Source ID | Provider | Fetch status | HTTP | Parse | Parser | Quality | Text chars | Tables |
|---|---|---|---|---|---|---|---|---|
| src_search_ff1cee7a6f74 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 31357 | 0 |

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

### 6.1.5 LLM Iterative Source Discovery

- Enabled: `True`
- LLM iterative planning enabled: `True`
- Search iteration count: `2`
- LLM refinement call count: `2`
- Total queries planned: `8`
- Total queries executed: `5`
- Stop decision: `stop_sufficient`
- Stop reason: `Max iterations (2) reached per bounds constraint. The stop condition is also independently satisfied: the primary CDC FluView Week 40 source (week ending October 5, 2024) is confirmed, the Mississippi state PDF is confirmed for the exact task window, and additional state-level and international candidates appeared in iteration 2 results. Further searching would not be permitted under the stated bounds and is not needed given the confirmed primary source coverage.`
- Query source counts: `{'iterative_llm_initial_search_plan': 1, 'iterative_llm_refinement': 4}`
- Iteration query counts: `{'1': 1, '2': 4}`

### 6.2 LLM Source Critic

- Attempted source count: `0`
- Assessed source count: `0`
- Skipped source count: `33`
- Blocked fetch count: `0`
- Allowed fetch count: `0`
- Context-only count: `0`
- Needs review count: `0`
- Max sources: `4`
- Review blocks fetch: `False`
- Failure count: `0`
- Semantic leakage count: `0`
- Human review recommended count: `0`
- Critic decision counts: `none`
- Fetch recommendation counts: `none`
- Risk flag counts: `none`
- Selected source IDs: ``

### 6.3 Optional LLM Source Credibility Advisory

- Enabled: `True`
- Assessed source count: `33`
- Final role counts: `collection=4, collection_support=1, context=19, excluded=2, validation=7`
- Risk flag counts: `ambiguous_disease=3, ambiguous_disease_signal_in_source_metadata=3, ambiguous_location=1, complete_source_provenance=22, context_or_background_only=15, data_signal_in_source_metadata=33, disease_relevance_unclear=1, geographic_granularity_unclear=1, independence_unclear=4, international_organization_authority=3, local_or_subnational_granularity=3, local_source_matches_task_location=24, location_match_from_planned_query=8, location_relevance_unclear=1, low_authority_relevant_source=4, low_machine_readability=8, missing_publisher=11, national_or_international_granularity=8, official_public_health_authority=26, pdf_or_report_likely_medium_readability=8, primary_or_authoritative_source=29, screening_and_critic_disagree=16, secondary_news_or_media_source=4, source_disease_relevance:ambiguous_disease=3, source_disease_relevance:insufficient_text=1, source_disease_relevance:target_disease_match=29, source_metadata_matches_requested_disease=29, source_time_matches_requested_window=15, standard_web_page=25, task_location_granularity=21, time_window_match_from_planned_query=18`
- LLM assessed count: `0`
- LLM failure count: `0`
- Needs review count: `2`

### 6.3.5 Source Identity / Publisher Assessment

- Identity assessed source count: `33`
- LLM identity assessed source count: `0`
- Post-fetch identity assessed source count: `1`
- Unknown publisher count: `11`
- Source type counts: `academic_or_peer_reviewed_source=1, international_public_health_agency=5, national_public_health_agency=15, news_media=2, official_public_health_agency=6, secondary_aggregator=1, social_media=1, state_or_local_public_health_agency=1, unknown=1`
- Claim support role counts: `corroboration_support=3, insufficient_information=3, primary_case_claim_support=27`
- Fetch use counts: `fetch_for_extraction=30, fetch_only_after_review=3`
- Warning counts: `actual_publisher_unknown=11, direct_target_official_fast_path_skips_source_identity=33, publisher_from_search_metadata_unverified=33, search_provider_not_publisher=33`

### 6.4 LLM Structured Extraction

- Extraction mode: `llm_structured_output`
- Eligible chunk count: `19`
- LLM call count: `3`
- LLM success count: `3`
- LLM error count: `0`
- Raw record count: `13`

## 7. 最终抽取 records

- Normalized record count: `13`
- Run quality status: `partial_with_quarantined_records`
- Final dataset mode: `task_aware_quality_gated_records`
- Quality-gated accepted final dataset count: `5`
- Final case dataset count: `0`
- Zero-case statement count: `0`
- Exposure-monitoring record count: `0`
- Surveillance summary record count: `13`
- Outbreak summary record count: `0`
- Context record count: `0`
- Unclassified observation count: `3`
- Observation dataset view counts: `{'final_case_dataset': 0, 'global_outbreak_event_dataset': 0, 'regional_surveillance_dataset': 0, 'country_year_aggregate_dataset': 0, 'official_alert_dataset': 0, 'probable_case_dataset': 0, 'suspected_case_dataset': 0, 'unspecified_case_dataset': 0, 'death_dataset': 1, 'hospitalization_dataset': 0, 'zero_case_statements': 0, 'exposure_monitoring_records': 0, 'surveillance_summary_records': 13, 'outbreak_summary_records': 0, 'context_records': 0, 'non_primary_observations': 13, 'unclassified_observation_records': 3}`
- Pre-quality-gate record count: `13`
- Quarantined record count: `6`
- Pending review record count: `2`
- Non-primary observation count: `8`
- Final dataset post-review count: `5`
- Primary-case dataset status: `no_primary_case_dataset_records`
- Recommended primary dataset message: `No primary case dataset records were accepted; inspect zero-case, exposure-monitoring, context, and other observation views.`
- Primary-case eligible accepted count: `0`
- Corroborated primary case event count: `0`
- Record inclusion status counts: `{'accepted_with_warnings': 5, 'quarantined_outside_scope': 6, 'pending_human_review': 2}`
- Run quality warnings: `['no_primary_case_dataset_records', 'no_corroborated_primary_case_events']`
- Accepted source counts: `src_search_ff1cee7a6f74=5`

| Record ID | Date / period | Location | Cases | Deaths | Source | LLM used |
|---|---|---|---|---|---|---|
| rec_src_search_ff1cee7a6f74_001 | MMWR week 40, 2024 | United States | none | none | src_search_ff1cee7a6f74 | False |
| rec_src_search_ff1cee7a6f74_003 | MMWR week 40, 2024 | United States | none | none | src_search_ff1cee7a6f74 | False |
| rec_src_search_ff1cee7a6f74_004 | MMWR week 40, 2024 | United States | none | none | src_search_ff1cee7a6f74 | False |
| rec_src_search_ff1cee7a6f74_007 | Week 40, ending October 5, 2024 | United States | none | 0.0 | src_search_ff1cee7a6f74 | True |
| rec_src_search_ff1cee7a6f74_008 | Week 40, ending October 5, 2024 | United States | none | none | src_search_ff1cee7a6f74 | True |

## 8. Validation 对比

### Claim-level corroboration

- Claim count: `13`
- Claim comparison count: `78`
- Corroborated event count: `1`
- Corroborated primary case event count: `0`
- Observation type counts: `ambiguous_public_health_observation=3, death_record=2, surveillance_summary=8`
- Corroboration status counts: `insufficient_information=1`

- Validation source compatibility status: `validation_source_empty`
- Active / inactive / raw validation records: `0` / `0` / `0`
- Validation record count: `0`
- Evaluation row count: `0`
- Evaluation rows flagged for human review: `0`
- Overall match status counts: `none`
- Masking compliance status counts: `none`
- Reserved source leakage count: `0`

| Eval row | Status | Collection cases | Validation cases | Human review | Reason |
|---|---|---|---|---|---|

## 9. Human review queue

- Human review item count: `31`
- Evaluation review flag count: `0`
- Anomaly review item count: `1`

| Review ID | Type | Related IDs | Reason |
|---|---|---|---|
| review_source_credibility_src_search_c95c26c7b200 | source_credibility | src_search_c95c26c7b200 | missing_publisher |
| review_source_src_search_c95c26c7b200 | source_screening | src_search_c95c26c7b200 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_src_search_88387812c274 | source_screening | src_search_88387812c274 | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_src_search_a3695468387b | source_screening | src_search_a3695468387b | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_src_search_1cb29ce91f47 | source_screening | src_search_1cb29ce91f47 | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_src_search_7edb5942f160 | source_screening | src_search_7edb5942f160 | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_src_search_0a7b36e413fd | source_screening | src_search_0a7b36e413fd | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_credibility_src_search_56888319c899 | source_credibility | src_search_56888319c899 | missing_publisher |
| review_source_src_search_56888319c899 | source_screening | src_search_56888319c899 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_src_search_0fff1ff8aec5 | source_screening | src_search_0fff1ff8aec5 | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_src_search_a0e8401d0c66 | source_screening | src_search_a0e8401d0c66 | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_src_search_6bdc29e2c410 | source_screening | src_search_6bdc29e2c410 | Screening and critic disagree on this source; routing to human review for resolution. |

## 9.5 Stage 11 anomaly detection and review application

- Anomaly result count: `3`
- Anomaly severity counts: `high=1, low=2`
- Anomaly needs-human-review count: `1`
- Decisions provided: `0`
- Decisions applied: `0`
- Decisions rejected: `0`
- Audit entries: `0`
- Final dataset post-review count: `5`
- Records excluded by review: `0`

| Anomaly ID | Type | Severity | Target | Reason |
|---|---|---|---|---|
| anom_001 | deaths_without_case_reference | low | rec_src_search_ff1cee7a6f74_007 | deaths present but no comparable case count is available |
| anom_002 | deaths_without_case_reference | low | rec_src_search_ff1cee7a6f74_009 | deaths present but no comparable case count is available |
| anom_003 | validation_conflict_anomaly | high | event_005 | Validation result is a conflict: Sources may use different case definitions or reporting categories. |

| Applied decision | Type | Target | Audit IDs | Reason |
|---|---|---|---|---|

## 10. 输出文件

- Run output directory: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\flu_united_states_2024_09_29_2024_10_05_20260626_181250_utc`
- Collection final dataset: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\flu_united_states_2024_09_29_2024_10_05_20260626_181250_utc\collection\final_dataset.csv`
- Collection final case dataset: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\flu_united_states_2024_09_29_2024_10_05_20260626_181250_utc\collection\final_case_dataset.csv`
- Collection zero-case statements: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\flu_united_states_2024_09_29_2024_10_05_20260626_181250_utc\collection\zero_case_statements.csv`
- Collection exposure-monitoring records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\flu_united_states_2024_09_29_2024_10_05_20260626_181250_utc\collection\exposure_monitoring_records.csv`
- Collection surveillance summaries: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\flu_united_states_2024_09_29_2024_10_05_20260626_181250_utc\collection\surveillance_summary_records.csv`
- Collection outbreak summaries: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\flu_united_states_2024_09_29_2024_10_05_20260626_181250_utc\collection\outbreak_summary_records.csv`
- Collection context records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\flu_united_states_2024_09_29_2024_10_05_20260626_181250_utc\collection\context_records.csv`
- Collection unclassified observations: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\flu_united_states_2024_09_29_2024_10_05_20260626_181250_utc\collection\unclassified_observation_records.csv`
- Collection observation dataset summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\flu_united_states_2024_09_29_2024_10_05_20260626_181250_utc\collection\observation_type_dataset_summary.json`
- Collection pre-quality-gate records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\flu_united_states_2024_09_29_2024_10_05_20260626_181250_utc\collection\final_dataset_pre_quality_gate.csv`
- Collection quarantined records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\flu_united_states_2024_09_29_2024_10_05_20260626_181250_utc\collection\quarantined_records.csv`
- Collection pending review records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\flu_united_states_2024_09_29_2024_10_05_20260626_181250_utc\collection\pending_review_records.csv`
- Collection non-primary observations: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\flu_united_states_2024_09_29_2024_10_05_20260626_181250_utc\collection\non_primary_observations.csv`
- Collection record inclusion decisions: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\flu_united_states_2024_09_29_2024_10_05_20260626_181250_utc\collection\record_inclusion_decisions.json`
- Collection final dataset post-review: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\flu_united_states_2024_09_29_2024_10_05_20260626_181250_utc\collection\final_dataset_post_review.csv`
- Collection anomaly results: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\flu_united_states_2024_09_29_2024_10_05_20260626_181250_utc\collection\anomaly_results.json`
- Collection human review audit trail: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\flu_united_states_2024_09_29_2024_10_05_20260626_181250_utc\collection\human_review_audit_trail.json`
- Collection source registry: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\flu_united_states_2024_09_29_2024_10_05_20260626_181250_utc\collection\source_registry.json`
- Validation mode: `diagnostic_only`
- Validation records source: `state`
- Validation records output: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\flu_united_states_2024_09_29_2024_10_05_20260626_181250_utc\validation\ground_truth_records.csv`
- Inactive validation records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\flu_united_states_2024_09_29_2024_10_05_20260626_181250_utc\validation\inactive_validation_records.csv`
- Validation compatibility summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\flu_united_states_2024_09_29_2024_10_05_20260626_181250_utc\validation\validation_source_compatibility_summary.json`
- Evaluation report CSV: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\flu_united_states_2024_09_29_2024_10_05_20260626_181250_utc\evaluation\evaluation_report.csv`
- Human-readable report: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\flu_united_states_2024_09_29_2024_10_05_20260626_181250_utc\workflow_run_report_chinese.md`

## 11. 当前结论

This workflow run executed the configured data collection workflow through the exported graph and artifact pipeline. The user-facing run status is: PARTIAL: accepted records produced, but some records were quarantined.
The run completed technically and produced quality-gated accepted records in the final dataset.

- Package metadata says LLM used: `True`
- Contains synthetic fixture data: `False`
- Generated at UTC: `2026-06-26T18:18:46.492689+00:00`

## 12. Workflow visualization artifacts

- Workflow visualization index: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\flu_united_states_2024_09_29_2024_10_05_20260626_181250_utc\workflow_visualization\index.html`
- Workflow timeline: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\flu_united_states_2024_09_29_2024_10_05_20260626_181250_utc\workflow_visualization\workflow_timeline.html`
- Evidence flow graph: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\flu_united_states_2024_09_29_2024_10_05_20260626_181250_utc\workflow_visualization\evidence_flow_graph.html`
- Claim comparison cards: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\flu_united_states_2024_09_29_2024_10_05_20260626_181250_utc\workflow_visualization\claim_comparison_cards.html`
- Dataset decision flow: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\flu_united_states_2024_09_29_2024_10_05_20260626_181250_utc\workflow_visualization\dataset_decision_flow.html`
- Human review workflow visualization: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\flu_united_states_2024_09_29_2024_10_05_20260626_181250_utc\workflow_visualization\human_review_workflow.html`
- Visualization summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\flu_united_states_2024_09_29_2024_10_05_20260626_181250_utc\workflow_visualization\workflow_visualization_summary.json`
