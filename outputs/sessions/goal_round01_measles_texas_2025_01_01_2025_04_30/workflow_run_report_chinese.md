# data collection workflow Run Report

## 1. 输入任务

Collect measles cases, deaths, dates, locations, source URLs, source types, and evidence quotes for Texas from 2025-01-01 to 2025-04-30.

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
- Source search executed queries: `8`
- Search-derived source candidates: `44`
- Iterative source discovery: `True`
- Iterative search iterations: `2`
- Iterative stop decision: `stop_sufficient`
- Iterative stop reason: `Max iterations (2) reached and evidence coverage is sufficient. All critical target fields are populated by authoritative, corroborated, time-window-appropriate sources. The two Texas deaths within the task window are documented by discrete DSHS press release URLs. Multiple dated case count milestones are available from DSHS and CDC MMWR. Hospitalization data is available from MMWR. Locality detail (Gaines County, South Plains, Lubbock, Harris County) is well-documented. No additional search queries would materially improve coverage beyond what is already captured in the 44 accepted candidates across both iterations.`
- Source credibility assessed sources: `44`
- Source credibility role counts: `{'context': 21, 'collection': 11, 'validation': 6, 'excluded': 5, 'collection_support': 1}`
- Source identity assessed sources: `44`
- Source identity type counts: `{'national_public_health_agency': 9, 'official_public_health_agency': 13, 'structured_database': 1, 'secondary_aggregator': 1, 'international_public_health_agency': 4, 'unknown': 1, 'academic_or_peer_reviewed_source': 3, 'news_media': 9, 'social_media': 3}`
- Source identity warning counts: `{'search_provider_not_publisher': 44, 'publisher_from_search_metadata_unverified': 44, 'direct_target_official_fast_path_skips_source_identity': 44, 'actual_publisher_unknown': 27}`
- Source discovery method: `live_search_only`
- Disease relevance target: `Measles`
- Disease relevance source status counts: `{'target_disease_match': 37, 'insufficient_text': 5, 'ambiguous_disease': 2}`
- Disease relevance chunk status counts: `{'target_disease_match': 569, 'ambiguous_disease': 468, 'related_context_only': 4, 'unrelated_disease': 11, 'insufficient_text': 4}`
- Disease relevance record status counts: `{'compatible': 71}`
- Rejected incompatible record count: `0`
- Final route: `finalize`

## 2.5 Run quality status

- User-facing run status: `PARTIAL: accepted records produced, but some records were quarantined.`
- Technical execution status: `completed`
- Run quality status: `partial_with_quarantined_records`
- Final dataset mode: `task_aware_quality_gated_records`
- Accepted final dataset count: `8`
- Final case dataset count: `6`
- Zero-case statement count: `0`
- Exposure-monitoring record count: `0`
- Surveillance summary record count: `0`
- Outbreak summary record count: `0`
- Context record count: `4`
- Unclassified observation count: `5`
- Observation dataset view counts: `{'final_case_dataset': 6, 'global_outbreak_event_dataset': 0, 'regional_surveillance_dataset': 0, 'country_year_aggregate_dataset': 0, 'official_alert_dataset': 0, 'probable_case_dataset': 0, 'suspected_case_dataset': 0, 'unspecified_case_dataset': 0, 'death_dataset': 2, 'hospitalization_dataset': 2, 'zero_case_statements': 0, 'exposure_monitoring_records': 0, 'surveillance_summary_records': 0, 'outbreak_summary_records': 0, 'context_records': 4, 'non_primary_observations': 9, 'unclassified_observation_records': 5}`
- Pre-quality-gate record count: `23`
- Quarantined record count: `12`
- Pending review record count: `3`
- Non-primary observation count: `3`
- Final dataset post-review count: `8`
- Primary-case dataset status: `primary_case_records_present`
- Recommended primary dataset message: `Primary case dataset records are available in final_case_dataset.`
- Primary-case eligible accepted count: `6`
- Corroborated primary case event count: `0`
- Recommended user message: `Review final_dataset and warnings before use.`

Workflow technically completed and produced quality-gated accepted records.

## 3. Workflow 运行过程

Graph is executed as a mostly serial workflow. The only conditional branch is after `quality_gate_routing`: the run enters `human_review` when quality or validation checks require review, then still builds the final data package. In this run, the graph route is shown above; validation comparison review flags are reported separately in Section 8.

1. `task_intake_and_scope_planning` - Built CollectionSpec from structured task input.
2. `disease_intelligence_builder` - Built disease intelligence from LLM output (Measles).
3. `profile_and_schema_setup` - Built active disease profile, collection schema, and source strategy (Measles, generation_method=disease_intelligence...
4. `executable_source_planning` - Built executable source plan with 10 planned queries; no searches were executed.
5. `query_strategy_builder` - Built 10 direct_collection search queries from the LLM evidence strategy plan.
6. `source_discovery` - Discovered 44 source candidates using live_search_only.
7. `source_dedup_and_registry` - Built source registry with 44 entries (0 duplicates dropped).
8. `source_screening` - Screened 44 sources using deterministic policy.
9. `source_critic_and_uncertainty_routing` - Critic reviewed 44 sources; 33 ready for fetch, 0 deferred, 22 flagged for human review.
10. `content_fetch_and_parse` - Built 33 fetch requests, produced 33 documents (live_fetch_enabled=True, fixture_documents_enabled=False, fixtures_lo...
11. `document_quality_check` - Quality-checked 33 documents: 31 usable, 0 partial, 0 offline stub, 0 parse deferred, 2 unusable.
12. `evidence_chunking_and_data_presence_flagging` - Chunked 31/33 documents into 1056 evidence chunks (944 flagged as containing target data).
13. `structured_extraction` - Built 24 raw records (extraction_mode=llm_structured_output, llm_enabled=True).
14. `schema_validation_and_repair` - Validated 24 raw records: 23 validated (4 need review), 1 rejected.
15. `record_normalization` - Normalized 23/23 records (4 need review).
16. `record_linking` - Linked 23/23 normalized records into 14 candidate events.
17. `cross_source_consistency_check` - Checked 5 multi-record events; found 0 new conflicts and 60 validation results (0 events need review).
18. `quality_gate_routing` - Human review disabled; preserving review flags as audit metadata and routing to final_data_package_builder.
19. `final_data_package_builder` - Assembled hardened FinalDataPackage from current state.

## 4. 数据源分工

| Role | Source ID | Publisher / title | Credibility | Final decision | Fetch ready |
|---|---|---|---|---|---|
| context_only | src_search_c62c62e520ae | / Texas measles cases remain steady at 750. Track the spread here. - The Texas Tribune | needs_review (0.5735) | needs_human_review | False |
| context_only | src_search_34ae881076ba | / Texas declares its measles outbreak over / AHA News | needs_review (0.5735) | needs_human_review | False |
| context_only | src_search_8d237fa2e9fb | / The Measles Outbreak in West Texas and Beyond / Johns Hopkins | needs_review (0.5735) | needs_human_review | False |
| context_only | src_search_340ae0c9d09e | / First death in Texas measles outbreak is unvaccinated child | needs_review (0.5735) | needs_human_review | False |
| context_only | src_search_28bcce01426c | / A second school-aged child in West Texas has died from a measles ... | medium (0.5551) | needs_human_review | False |
| context_only | src_search_ef91136c088c | CIDRAP / Texas confirms measles outbreak as Georgia reports more cases / CIDRAP | medium (0.5811) | include_for_content_fetch | True |
| context_only | src_search_50fedea73302 | / 2nd child with measles dies in Texas, according to state health officials | low (0.5343) | needs_human_review | False |
| context_only | src_search_ac2170651876 | / An unvaccinated child has died in the Texas measles ... - YouTube | medium (0.5551) | needs_human_review | False |
| context_only | src_search_74152a4ae4ab | / U.S. Measles Outbreak 2025 - Public Health - MSK Library Guides at Memorial Sloan Kettering Cancer Center | medium (0.6712) | needs_human_review | False |
| context_only | src_search_d79bcfc122f2 | / [PDF] MEASLES OUTBREAK - SOUTHWEST U.S. - 2025 - AMP.org | low (0.4264) | needs_human_review | False |
| context_only | src_search_5b3b94cad94b | / Texas measles outbreak hardened Mennonites against vaccines | medium (0.5735) | needs_human_review | False |
| context_only | src_search_f771bc0ae4a3 | / As a measles outbreak centered in West Texas continues to grow, a ... | medium (0.5551) | needs_human_review | False |
| other | src_search_fede8be6ac1e | Centers for Disease Control and Prevention / Notes from the Field: Initial Public Health Response to a Measles Outbreak in a Close-Knit W... | high (0.8943) | include_for_content_fetch | True |
| other | src_search_470222e3d9fc | / Confirmed Case of Measles - January 2025 / Texas DSHS | high (0.8823) | include_for_content_fetch | True |
| other | src_search_4e73f2d0f38f | Centers for Disease Control and Prevention / Characteristics of Patients Hospitalized with Measles During an Outbreak — West Texas, Janua... | high (0.8943) | include_for_content_fetch | True |
| other | src_search_3e232b5b243d | / Measles Outbreak – August 12, 2025 / Texas DSHS | high (0.8823) | include_for_content_fetch | True |
| other | src_search_8bf36d4bffb4 | / Measles / Texas Children's | high (0.8431) | include_for_content_fetch | True |
| other | src_search_b69d58b16fda | National Center for Biotechnology Information / Measles resurgence in Texas: a public health wake-up call - PMC | high (0.8551) | include_for_content_fetch | True |
| other | src_search_d93e2ef153b0 | / Measles - Texas Epidemic Public Health Institute | high (0.8431) | include_for_content_fetch | True |
| other | src_search_14e93bfe3eec | / 2025 Southwest United States measles outbreak - Wikipedia | high (0.8112) | include_for_content_fetch | True |
| other | src_search_43fd7f744d6a | Centers for Disease Control and Prevention / CDC Science Clips | medium (0.5888) | include_for_content_fetch | True |
| other | src_search_fec37a5bcdfb | Centers for Disease Control and Prevention / Expanding Measles Outbreak in the United States and Guidance for the Upcoming Travel Season... | high (0.8048) | include_for_content_fetch | True |
| other | src_search_9d3a148dc974 | Centers for Disease Control and Prevention / Measles Outbreak in a Child Care Facility — Lubbock, Texas, March–April 2025 / MMWR | high (0.8826) | include_for_content_fetch | True |
| other | src_search_3109afb35d90 | Centers for Disease Control and Prevention / Measles Update — United States, January 1–April 17, 2025 / MMWR | high (0.8232) | include_for_content_fetch | True |
| other | src_search_babdba80f49a | Centers for Disease Control and Prevention / [PDF] Characteristics of Patients Hospitalized with Measles During ... - CDC | medium (0.708) | include_for_content_fetch | True |
| other | src_search_bf565a1a27b0 | Centers for Disease Control and Prevention / [PDF] Measles Outbreak in a Child Care Facility — Lubbock, Texas, March ... | high (0.7882) | include_for_content_fetch | True |
| other | src_search_4250b5c89dbb | World Health Organization / Measles - United States of America | high (0.8024) | include_for_content_fetch | True |
| other | src_search_8242cbb785a1 | Pan American Health Organization / Situation Report #2: Measles in the Americas Region - PAHO/WHO / Pan American Health Organization | high (0.8048) | include_for_content_fetch | True |
| other | src_search_c4a96c8b3aa2 | Centers for Disease Control and Prevention / [PDF] MEASLES OUTBREAK - SOUTHWEST U.S. - 2025 - Campus Health | medium (0.724) | include_for_content_fetch | True |
| other | src_search_322beeaf24f0 | Pan American Health Organization / [PDF] Epidemiological Update Measles in the Americas Region | medium (0.7264) | include_for_content_fetch | True |
| other | src_search_4ea030a47321 | CIDRAP / CDC: Only 1 in 10 hospital patients early in the West Texas measles outbreak had underlying conditions / CIDRAP | high (0.853) | include_for_content_fetch | True |
| other | src_search_6e578fc529e9 | Pan American Health Organization / Situation Report #1: Measles in the Americas Region - PAHO/WHO / Pan American Health Organization | high (0.8048) | include_for_content_fetch | True |
| other | src_search_7da7ceded0cf | Centers for Disease Control and Prevention / [PDF] SOUTH PLAINS PUBLIC HEALTH DISTRICT | excluded (0.5719) | include_for_content_fetch | True |
| other | src_search_65e6340a3a24 | / Texas announces second death in measles outbreak / Texas DSHS | high (0.8639) | include_for_content_fetch | True |
| other | src_search_4953f4055d66 | / [PDF] HHS System Coordinated Strategic Plan for 2021-2025 | excluded (0.6063) | include_for_content_fetch | True |
| other | src_search_deb9c3feab77 | / Texas Department of State Health Services (DSHS) | excluded (0.6479) | include_for_content_fetch | True |
| other | src_search_78633c13024a | / News & Alerts / Texas DSHS | high (0.6479) | include_for_content_fetch | True |
| other | src_search_49cffac7208c | / [PDF] Texas School Health Advisory Committee (TSHAC) Minutes 02-24-25 | excluded (0.5879) | include_for_content_fetch | True |
| other | src_search_91228c9653c7 | / [PDF] Self-Evaluation Report | excluded (0.5719) | include_for_content_fetch | True |
| other | src_search_1be284797a9b | Centers for Disease Control and Prevention / Map: Track measles outbreaks, cases and vaccination rates by state across the U.S. | high (0.7928) | include_for_content_fetch | True |
| other | src_search_bf53e3bb2a06 | CIDRAP / US measles cases top 1,500 as Texas outbreak grows / CIDRAP | high (0.8642) | include_for_content_fetch | True |
| other | src_search_7cb311dd75e6 | / U.S. Measles Tracker / International Vaccine Access Center | medium (0.772) | include_for_content_fetch | True |
| other | src_search_283a8bed6a9d | Centers for Disease Control and Prevention / Measles Cases and Outbreaks - CDC | high (0.8048) | include_for_content_fetch | True |
| other | src_search_0132cfa4f779 | / 2025-2026 Measles Outbreaks: Where Are We Now? Resources ... | high (0.8112) | include_for_content_fetch | True |

## 5. 真实网页抓取结果

- Documents fetched/parsed: `33`
- Search-derived sources selected for fetch: `33`
- Search-derived skipped by reason: `{}`
- Fetch status counts: `fetched=33`
- External fetch enabled: `True`
- Fetch provider counts: `tavily_extract=33`
- External fetch failure counts: `none`
- Selected fetch bucket counts: `target_official_authority=33`
- Parser status counts: `parsed_text=33`
- Parser used counts: `text_parser=33`
- Quality status counts: `unusable=2, usable=31`
- Validation-reserved skipped from fetch: `[]`

| Source ID | Provider | Fetch status | HTTP | Parse | Parser | Quality | Text chars | Tables |
|---|---|---|---|---|---|---|---|---|
| src_search_fede8be6ac1e | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 19689 | 0 |
| src_search_4e73f2d0f38f | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 26745 | 0 |
| src_search_9d3a148dc974 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 20505 | 0 |
| src_search_470222e3d9fc | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 13373 | 0 |
| src_search_3e232b5b243d | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 5152 | 0 |
| src_search_bf53e3bb2a06 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 13060 | 0 |
| src_search_65e6340a3a24 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 4174 | 0 |
| src_search_b69d58b16fda | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 34390 | 0 |
| src_search_8bf36d4bffb4 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 3510 | 0 |
| src_search_d93e2ef153b0 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 9553 | 0 |
| src_search_3109afb35d90 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 28035 | 0 |
| src_search_0132cfa4f779 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 41938 | 0 |
| src_search_14e93bfe3eec | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 24119 | 0 |
| src_search_fec37a5bcdfb | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 5852 | 0 |
| src_search_283a8bed6a9d | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 57418 | 0 |
| src_search_1be284797a9b | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 4231 | 0 |
| src_search_bf565a1a27b0 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 21791 | 0 |
| src_search_7cb311dd75e6 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 13445 | 0 |
| src_search_babdba80f49a | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 27082 | 0 |
| src_search_deb9c3feab77 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 5612 | 0 |
| src_search_78633c13024a | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 6188 | 0 |
| src_search_4953f4055d66 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 572945 | 0 |
| src_search_43fd7f744d6a | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 59810 | 0 |
| src_search_49cffac7208c | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 20663 | 0 |
| src_search_7da7ceded0cf | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 1305 | 0 |
| src_search_91228c9653c7 | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 837193 | 0 |
| src_search_4ea030a47321 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 12776 | 0 |
| src_search_8242cbb785a1 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 6145 | 0 |
| src_search_6e578fc529e9 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 6288 | 0 |
| src_search_4250b5c89dbb | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 26003 | 0 |
| src_search_322beeaf24f0 | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 47510 | 0 |
| src_search_c4a96c8b3aa2 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 29470 | 0 |
| src_search_ef91136c088c | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 21501 | 0 |

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
- Total queries executed: `8`
- Stop decision: `stop_sufficient`
- Stop reason: `Max iterations (2) reached and evidence coverage is sufficient. All critical target fields are populated by authoritative, corroborated, time-window-appropriate sources. The two Texas deaths within the task window are documented by discrete DSHS press release URLs. Multiple dated case count milestones are available from DSHS and CDC MMWR. Hospitalization data is available from MMWR. Locality detail (Gaines County, South Plains, Lubbock, Harris County) is well-documented. No additional search queries would materially improve coverage beyond what is already captured in the 44 accepted candidates across both iterations.`
- Query source counts: `{'iterative_llm_initial_search_plan': 4, 'iterative_llm_refinement': 4}`
- Iteration query counts: `{'1': 4, '2': 4}`

### 6.2 LLM Source Critic

- Attempted source count: `0`
- Assessed source count: `0`
- Skipped source count: `44`
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
- Assessed source count: `44`
- Final role counts: `collection=11, collection_support=1, context=21, excluded=5, validation=6`
- Risk flag counts: `ambiguous_disease=7, ambiguous_disease_signal_in_source_metadata=2, article_date_outside_collection_window_2025-08-18_vs_2025-01-01_to_2025-04-30=1, complete_source_provenance=17, context_or_background_only=9, corroboration_required_from_texas_dshs_or_cdc_before_any_numeric_extraction=1, data_figures_likely_unstructured_and_require_provenance_tracing=1, data_figures_require_primary_source_verification=1, data_figures_require_upstream_source_verification=1, data_granularity_moderate_0.68_may_lack_required_field_resolution=1, data_signal_in_source_metadata=44, disease_relevance_unclear=5, do_not_use_as_primary_collection_source=1, do_not_use_as_primary_collection_source_for_case_counts_or_deaths=1, double_counting_risk_if_dshs_also_collected=1, independence_score_low_0.42_data_likely_synthesized_from_dshs_or_cdc=1, independence_unclear=10, independence_unclear_aha_is_secondary_republisher_not_public_health_authority=1, independence_unclear_downstream_of_official_sources=1, international_organization_authority=2, live_tracker_format_retrieval_timestamp_critical=1, local_or_subnational_granularity=24, local_source_matches_task_location=28, location_match_from_planned_query=16, low_authority_for_primary_epidemiological_data=1, low_authority_relevant_source=11, low_authority_score_0.48_relative_to_task_priority_tier=1, low_machine_readability=9, missing_publisher=27, missing_publisher_field=1, missing_publisher_metadata=2, named_publisher=1, national_or_international_granularity=16, official_public_health_authority=31, pdf_or_report_likely_medium_readability=9, primary_or_authoritative_source=33, publisher_null_identity_ambiguous=1, retrospective_outbreak_closure_article_not_contemporaneous_situation_report=1, role_conflict_collection_support_vs_context=1, screening_and_critic_disagree=12, screening_and_critic_disagree_requires_human_adjudication=1, screening_and_critic_disagree_requires_resolution=1, screening_and_critic_disagree_upstream_conflict_detected=1, secondary_derivative_source_jhu_not_primary_surveillance_authority=1, secondary_news_or_media_source=12, source_disease_relevance:ambiguous_disease=2, source_disease_relevance:insufficient_text=5, source_disease_relevance:target_disease_match=37, source_metadata_matches_requested_disease=37, source_time_matches_requested_window=19, standard_web_page=35, task_location_granularity=4, time_window_match_from_planned_query=25`
- LLM assessed count: `4`
- LLM failure count: `0`
- Needs review count: `5`

### 6.3.5 Source Identity / Publisher Assessment

- Identity assessed source count: `44`
- LLM identity assessed source count: `0`
- Post-fetch identity assessed source count: `33`
- Unknown publisher count: `24`
- Source type counts: `academic_or_peer_reviewed_source=3, international_public_health_agency=4, national_public_health_agency=9, news_media=9, official_public_health_agency=13, secondary_aggregator=1, social_media=3, structured_database=1, unknown=1`
- Claim support role counts: `corroboration_support=10, insufficient_information=7, primary_case_claim_support=27`
- Fetch use counts: `fetch_for_extraction=37, fetch_only_after_review=7`
- Warning counts: `actual_publisher_unknown=27, direct_target_official_fast_path_skips_source_identity=44, publisher_from_search_metadata_unverified=44, search_provider_not_publisher=44`

### 6.4 LLM Structured Extraction

- Extraction mode: `llm_structured_output`
- Eligible chunk count: `1021`
- LLM call count: `30`
- LLM success count: `30`
- LLM error count: `0`
- Raw record count: `24`

## 7. 最终抽取 records

- Normalized record count: `23`
- Run quality status: `partial_with_quarantined_records`
- Final dataset mode: `task_aware_quality_gated_records`
- Quality-gated accepted final dataset count: `8`
- Final case dataset count: `6`
- Zero-case statement count: `0`
- Exposure-monitoring record count: `0`
- Surveillance summary record count: `0`
- Outbreak summary record count: `0`
- Context record count: `4`
- Unclassified observation count: `5`
- Observation dataset view counts: `{'final_case_dataset': 6, 'global_outbreak_event_dataset': 0, 'regional_surveillance_dataset': 0, 'country_year_aggregate_dataset': 0, 'official_alert_dataset': 0, 'probable_case_dataset': 0, 'suspected_case_dataset': 0, 'unspecified_case_dataset': 0, 'death_dataset': 2, 'hospitalization_dataset': 2, 'zero_case_statements': 0, 'exposure_monitoring_records': 0, 'surveillance_summary_records': 0, 'outbreak_summary_records': 0, 'context_records': 4, 'non_primary_observations': 9, 'unclassified_observation_records': 5}`
- Pre-quality-gate record count: `23`
- Quarantined record count: `12`
- Pending review record count: `3`
- Non-primary observation count: `3`
- Final dataset post-review count: `8`
- Primary-case dataset status: `primary_case_records_present`
- Recommended primary dataset message: `Primary case dataset records are available in final_case_dataset.`
- Primary-case eligible accepted count: `6`
- Corroborated primary case event count: `0`
- Record inclusion status counts: `{'accepted_with_warnings': 8, 'pending_human_review': 3, 'quarantined_outside_scope': 10, 'quarantined_schema_invalid': 2}`
- Run quality warnings: `['no_corroborated_primary_case_events']`
- Accepted source counts: `src_search_470222e3d9fc=1, src_search_4e73f2d0f38f=4, src_search_65e6340a3a24=3`

| Record ID | Date / period | Location | Cases | Deaths | Source | LLM used |
|---|---|---|---|---|---|---|
| rec_src_search_65e6340a3a24_001 | late January 2025 through April 4, 2025 | Texas | 481.0 | none | src_search_65e6340a3a24 | True |
| rec_src_search_65e6340a3a24_002 | late January 2025 through April 4, 2025 | Texas | none | none | src_search_65e6340a3a24 | True |
| rec_src_search_65e6340a3a24_003 | late January 2025 through April 4, 2025 | Texas | none | 2.0 | src_search_65e6340a3a24 | True |
| rec_src_search_4e73f2d0f38f_002 | January–March 2025 | Texas | none | none | src_search_4e73f2d0f38f | True |
| rec_src_search_4e73f2d0f38f_003 | January–March 2025 | Texas | none | none | src_search_4e73f2d0f38f | True |
| rec_src_search_4e73f2d0f38f_004 | January–March 2025 | Texas | none | 1.0 | src_search_4e73f2d0f38f | True |
| rec_src_search_4e73f2d0f38f_005 | January–March 2025 | Texas | none | none | src_search_4e73f2d0f38f | True |
| rec_src_search_470222e3d9fc_001 | January 2025 | Texas | 2.0 | none | src_search_470222e3d9fc | True |

## 8. Validation 对比

### Claim-level corroboration

- Claim count: `25`
- Claim comparison count: `300`
- Corroborated event count: `3`
- Corroborated primary case event count: `0`
- Observation type counts: `ambiguous_public_health_observation=5, confirmed_case_record=8, death_record=8, hospitalization_record=3, unspecified_case_record=1`
- Corroboration status counts: `conflicting_claims=1, single_source_unverified=2`

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

- Human review item count: `69`
- Evaluation review flag count: `0`
- Anomaly review item count: `7`

| Review ID | Type | Related IDs | Reason |
|---|---|---|---|
| review_source_credibility_src_search_470222e3d9fc | source_credibility | src_search_470222e3d9fc | missing_publisher |
| review_source_src_search_470222e3d9fc | source_screening | src_search_470222e3d9fc | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_3e232b5b243d | source_credibility | src_search_3e232b5b243d | missing_publisher |
| review_source_src_search_3e232b5b243d | source_screening | src_search_3e232b5b243d | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_8bf36d4bffb4 | source_credibility | src_search_8bf36d4bffb4 | missing_publisher |
| review_source_src_search_8bf36d4bffb4 | source_screening | src_search_8bf36d4bffb4 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_d93e2ef153b0 | source_credibility | src_search_d93e2ef153b0 | missing_publisher |
| review_source_src_search_d93e2ef153b0 | source_screening | src_search_d93e2ef153b0 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_14e93bfe3eec | source_credibility | src_search_14e93bfe3eec | missing_publisher |
| review_source_src_search_14e93bfe3eec | source_screening | src_search_14e93bfe3eec | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_c62c62e520ae | source_credibility | src_search_c62c62e520ae | The Texas Tribune is a well-established, nonprofit, nonpartisan investigative news outlet with a strong track record of public health rep... |
| review_source_src_search_c62c62e520ae | source_screening | src_search_c62c62e520ae | Screening and critic disagree on this source; routing to human review for resolution. |

## 9.5 Stage 11 anomaly detection and review application

- Anomaly result count: `13`
- Anomaly severity counts: `high=5, low=6, medium=2`
- Anomaly needs-human-review count: `7`
- Decisions provided: `0`
- Decisions applied: `0`
- Decisions rejected: `0`
- Audit entries: `0`
- Final dataset post-review count: `8`
- Records excluded by review: `0`

| Anomaly ID | Type | Severity | Target | Reason |
|---|---|---|---|---|
| anom_001 | deaths_without_case_reference | low | rec_src_search_65e6340a3a24_003 | deaths present but no comparable case count is available |
| anom_002 | deaths_without_case_reference | low | rec_src_search_3e232b5b243d_002 | deaths present but no comparable case count is available |
| anom_003 | deaths_without_case_reference | low | rec_src_search_8242cbb785a1_002 | deaths present but no comparable case count is available |
| anom_004 | deaths_without_case_reference | low | rec_src_search_6e578fc529e9_002 | deaths present but no comparable case count is available |
| anom_005 | deaths_without_case_reference | low | rec_src_search_fede8be6ac1e_004 | deaths present but no comparable case count is available |
| anom_006 | deaths_without_case_reference | low | rec_src_search_4e73f2d0f38f_004 | deaths present but no comparable case count is available |
| anom_007 | out_of_scope_count_bearing_record | high | event_001 | Stage 10 validation marked record outside requested scope: outside_geography |
| anom_008 | out_of_scope_count_bearing_record | high | event_001 | Stage 10 validation marked record outside requested scope: outside_geography |
| anom_009 | out_of_scope_count_bearing_record | high | event_010 | Stage 10 validation marked record outside requested scope: outside_geography |
| anom_010 | out_of_scope_count_bearing_record | high | event_010 | Stage 10 validation marked record outside requested scope: outside_geography |
| anom_011 | out_of_scope_count_bearing_record | high | event_011 | Stage 10 validation marked record outside requested scope: outside_geography |
| anom_012 | aggregate_member_mismatch | medium | event_001 | event cluster canonical count differs from sum of comparable countable members |

| Applied decision | Type | Target | Audit IDs | Reason |
|---|---|---|---|---|

## 10. 输出文件

- Run output directory: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_measles_texas_2025_01_01_2025_04_30`
- Collection final dataset: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_measles_texas_2025_01_01_2025_04_30\collection\final_dataset.csv`
- Collection final case dataset: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_measles_texas_2025_01_01_2025_04_30\collection\final_case_dataset.csv`
- Collection zero-case statements: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_measles_texas_2025_01_01_2025_04_30\collection\zero_case_statements.csv`
- Collection exposure-monitoring records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_measles_texas_2025_01_01_2025_04_30\collection\exposure_monitoring_records.csv`
- Collection surveillance summaries: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_measles_texas_2025_01_01_2025_04_30\collection\surveillance_summary_records.csv`
- Collection outbreak summaries: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_measles_texas_2025_01_01_2025_04_30\collection\outbreak_summary_records.csv`
- Collection context records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_measles_texas_2025_01_01_2025_04_30\collection\context_records.csv`
- Collection unclassified observations: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_measles_texas_2025_01_01_2025_04_30\collection\unclassified_observation_records.csv`
- Collection observation dataset summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_measles_texas_2025_01_01_2025_04_30\collection\observation_type_dataset_summary.json`
- Collection pre-quality-gate records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_measles_texas_2025_01_01_2025_04_30\collection\final_dataset_pre_quality_gate.csv`
- Collection quarantined records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_measles_texas_2025_01_01_2025_04_30\collection\quarantined_records.csv`
- Collection pending review records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_measles_texas_2025_01_01_2025_04_30\collection\pending_review_records.csv`
- Collection non-primary observations: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_measles_texas_2025_01_01_2025_04_30\collection\non_primary_observations.csv`
- Collection record inclusion decisions: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_measles_texas_2025_01_01_2025_04_30\collection\record_inclusion_decisions.json`
- Collection final dataset post-review: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_measles_texas_2025_01_01_2025_04_30\collection\final_dataset_post_review.csv`
- Collection anomaly results: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_measles_texas_2025_01_01_2025_04_30\collection\anomaly_results.json`
- Collection human review audit trail: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_measles_texas_2025_01_01_2025_04_30\collection\human_review_audit_trail.json`
- Collection source registry: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_measles_texas_2025_01_01_2025_04_30\collection\source_registry.json`
- Validation mode: `diagnostic_only`
- Validation records source: `state`
- Validation records output: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_measles_texas_2025_01_01_2025_04_30\validation\ground_truth_records.csv`
- Inactive validation records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_measles_texas_2025_01_01_2025_04_30\validation\inactive_validation_records.csv`
- Validation compatibility summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_measles_texas_2025_01_01_2025_04_30\validation\validation_source_compatibility_summary.json`
- Evaluation report CSV: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_measles_texas_2025_01_01_2025_04_30\evaluation\evaluation_report.csv`
- Human-readable report: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_measles_texas_2025_01_01_2025_04_30\workflow_run_report_chinese.md`

## 11. 当前结论

This workflow run executed the configured data collection workflow through the exported graph and artifact pipeline. The user-facing run status is: PARTIAL: accepted records produced, but some records were quarantined.
The run completed technically and produced quality-gated accepted records in the final dataset.

- Package metadata says LLM used: `True`
- Contains synthetic fixture data: `False`
- Generated at UTC: `2026-06-25T14:37:44.074376+00:00`

## 12. Workflow visualization artifacts

- Workflow visualization index: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_measles_texas_2025_01_01_2025_04_30\workflow_visualization\index.html`
- Workflow timeline: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_measles_texas_2025_01_01_2025_04_30\workflow_visualization\workflow_timeline.html`
- Evidence flow graph: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_measles_texas_2025_01_01_2025_04_30\workflow_visualization\evidence_flow_graph.html`
- Claim comparison cards: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_measles_texas_2025_01_01_2025_04_30\workflow_visualization\claim_comparison_cards.html`
- Dataset decision flow: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_measles_texas_2025_01_01_2025_04_30\workflow_visualization\dataset_decision_flow.html`
- Human review workflow visualization: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_measles_texas_2025_01_01_2025_04_30\workflow_visualization\human_review_workflow.html`
- Visualization summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_measles_texas_2025_01_01_2025_04_30\workflow_visualization\workflow_visualization_summary.json`
