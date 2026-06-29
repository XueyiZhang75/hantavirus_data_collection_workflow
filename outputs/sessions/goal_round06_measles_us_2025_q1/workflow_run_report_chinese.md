# data collection workflow Run Report

## 1. 输入任务

Collect Measles cases, deaths, dates, locations, source URLs, source types, and evidence quotes for United States from 2025-01-01 to 2025-03-31.

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
- Search-derived source candidates: `48`
- Iterative source discovery: `True`
- Iterative search iterations: `2`
- Iterative stop decision: `stop_sufficient`
- Iterative stop reason: `Max iterations (2) reached and evidence coverage is substantively sufficient across all target fields and required source-type categories for the Q1 2025 window.`
- Source credibility assessed sources: `48`
- Source credibility role counts: `{'context': 15, 'collection': 19, 'validation': 12, 'collection_support': 2}`
- Source identity assessed sources: `48`
- Source identity type counts: `{'national_public_health_agency': 7, 'official_public_health_agency': 11, 'social_media': 2, 'academic_or_peer_reviewed_source': 4, 'secondary_aggregator': 1, 'international_public_health_agency': 8, 'structured_database': 3, 'unknown': 6, 'news_media': 3, 'state_or_local_public_health_agency': 2, 'background_fact_sheet': 1}`
- Source identity warning counts: `{'search_provider_not_publisher': 48, 'publisher_from_search_metadata_unverified': 48, 'direct_target_official_fast_path_skips_source_identity': 48, 'actual_publisher_unknown': 24}`
- Source discovery method: `live_search_only`
- Disease relevance target: `Measles`
- Disease relevance source status counts: `{'target_disease_match': 47, 'insufficient_text': 1}`
- Disease relevance chunk status counts: `{'target_disease_match': 931, 'ambiguous_disease': 67, 'related_context_only': 5}`
- Disease relevance record status counts: `{'compatible': 218}`
- Rejected incompatible record count: `0`
- Final route: `finalize`

## 2.5 Run quality status

- User-facing run status: `PARTIAL: accepted records produced, but some records were quarantined.`
- Technical execution status: `completed`
- Run quality status: `partial_with_quarantined_records`
- Final dataset mode: `task_aware_quality_gated_records`
- Accepted final dataset count: `1`
- Final case dataset count: `0`
- Zero-case statement count: `0`
- Exposure-monitoring record count: `0`
- Surveillance summary record count: `3`
- Outbreak summary record count: `7`
- Context record count: `6`
- Unclassified observation count: `7`
- Observation dataset view counts: `{'final_case_dataset': 0, 'global_outbreak_event_dataset': 0, 'regional_surveillance_dataset': 0, 'country_year_aggregate_dataset': 0, 'official_alert_dataset': 0, 'probable_case_dataset': 0, 'suspected_case_dataset': 0, 'unspecified_case_dataset': 0, 'death_dataset': 0, 'hospitalization_dataset': 0, 'zero_case_statements': 0, 'exposure_monitoring_records': 0, 'surveillance_summary_records': 3, 'outbreak_summary_records': 7, 'context_records': 6, 'non_primary_observations': 21, 'unclassified_observation_records': 7}`
- Pre-quality-gate record count: `72`
- Quarantined record count: `17`
- Pending review record count: `54`
- Non-primary observation count: `13`
- Final dataset post-review count: `1`
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
2. `disease_intelligence_builder` - Built disease intelligence from LLM output (Measles).
3. `profile_and_schema_setup` - Built active disease profile, collection schema, and source strategy (Measles, generation_method=disease_intelligence...
4. `executable_source_planning` - Built executable source plan with 10 planned queries; no searches were executed.
5. `query_strategy_builder` - Built 10 direct_collection search queries from the LLM evidence strategy plan.
6. `source_discovery` - Discovered 48 source candidates using live_search_only.
7. `source_dedup_and_registry` - Built source registry with 48 entries (0 duplicates dropped).
8. `source_screening` - Screened 48 sources using deterministic policy.
9. `source_critic_and_uncertainty_routing` - Critic reviewed 48 sources; 45 ready for fetch, 0 deferred, 23 flagged for human review.
10. `content_fetch_and_parse` - Built 45 fetch requests, produced 45 documents (live_fetch_enabled=True, fixture_documents_enabled=False, fixtures_lo...
11. `document_quality_check` - Quality-checked 45 documents: 41 usable, 0 partial, 0 offline stub, 0 parse deferred, 4 unusable.
12. `evidence_chunking_and_data_presence_flagging` - Chunked 41/45 documents into 1003 evidence chunks (955 flagged as containing target data).
13. `structured_extraction` - Built 73 raw records (extraction_mode=llm_structured_output, llm_enabled=True).
14. `schema_validation_and_repair` - Validated 73 raw records: 72 validated (0 need review), 1 rejected.
15. `record_normalization` - Normalized 72/72 records (1 need review).
16. `record_linking` - Linked 72/72 normalized records into 53 candidate events.
17. `cross_source_consistency_check` - Checked 14 multi-record events; found 2 new conflicts and 198 validation results (1 events need review).
18. `quality_gate_routing` - Human review disabled; preserving review flags as audit metadata and routing to final_data_package_builder.
19. `final_data_package_builder` - Assembled hardened FinalDataPackage from current state.

## 4. 数据源分工

| Role | Source ID | Publisher / title | Credibility | Final decision | Fetch ready |
|---|---|---|---|---|---|
| context_only | src_search_2eb069f08192 | / Clinician Update on Measles Cases and Outbreaks in the ... - YouTube | medium (0.6928) | include_for_content_fetch | False |
| context_only | src_search_1639787c4334 | / Communicating About the Ongoing Measles Outbreak - Public Health Communications Collaborative | needs_review (0.6712) | needs_human_review | False |
| context_only | src_search_95e36ab59cc7 | CIDRAP / US exceeds 1,900 measles cases as outbreaks expand / CIDRAP | medium (0.5811) | include_for_content_fetch | True |
| context_only | src_search_296bf3da1bef | / 2025 measles cases highest since 1991 - AAP Publications | needs_review (0.5024) | needs_human_review | False |
| context_only | src_search_eec8c3f3b772 | National Center for Biotechnology Information / Measles resurgence in the United States: epidemiological and ... | medium (0.7151) | needs_human_review | False |
| context_only | src_search_497d92fe2060 | / Texas Measles Status 3/14/2025 (261 total cases, +36 since last ... | high (0.7823) | include_for_content_fetch | True |
| context_only | src_search_270d5e6d3895 | / The New Mexico Department of Health announced a Lea County ... | high (0.3314) | include_for_content_fetch | False |
| other | src_search_fec37a5bcdfb | Centers for Disease Control and Prevention / Expanding Measles Outbreak in the United States and Guidance for the Upcoming Travel Season... | high (0.8759) | include_for_content_fetch | True |
| other | src_search_cd5fb2750261 | Centers for Disease Control and Prevention / CDC Records Two New Measles Outbreaks — As 2026 Already Outpaces 2025 | high (0.8706) | include_for_content_fetch | True |
| other | src_search_3109afb35d90 | Centers for Disease Control and Prevention / Measles Update — United States, January 1–April 17, 2025 / MMWR | high (0.8943) | include_for_content_fetch | True |
| other | src_search_62409e4d2cf9 | / US Measles Cases Near 2,000 in 2025 as Multi-State Outbreaks ... | high (0.8823) | include_for_content_fetch | True |
| other | src_search_7cb311dd75e6 | / U.S. Measles Tracker / International Vaccine Access Center | high (0.8314) | include_for_content_fetch | True |
| other | src_search_283a8bed6a9d | Centers for Disease Control and Prevention / Measles Cases and Outbreaks | high (0.8642) | include_for_content_fetch | True |
| other | src_search_4b282ae73985 | CIDRAP / CDC social media silence during 2025 measles outbreak left void filled by news media, study suggests / CIDRAP | high (0.8826) | include_for_content_fetch | True |
| other | src_search_14e93bfe3eec | / 2025 Southwest United States measles outbreak - Wikipedia | high (0.8823) | include_for_content_fetch | True |
| other | src_search_4250b5c89dbb | World Health Organization / Measles - United States of America | high (0.8735) | include_for_content_fetch | True |
| other | src_search_74152a4ae4ab | / U.S. Measles Outbreak 2025 - Public Health - MSK Library Guides at Memorial Sloan Kettering Cancer Center | high (0.8823) | include_for_content_fetch | True |
| other | src_search_1931fc9fea85 | National Center for Biotechnology Information / Measles Update — United States, January 1–April 17, 2025 | high (0.8943) | include_for_content_fetch | True |
| other | src_search_9570e9e8018b | / 2025 Measles Outbreak / South Carolina Department of Public Health | high (0.8823) | include_for_content_fetch | True |
| other | src_search_3e232b5b243d | / Measles Outbreak – August 12, 2025 / Texas DSHS | high (0.8823) | include_for_content_fetch | True |
| other | src_search_4847d41afdb8 | CIDRAP / US measles outbreak approaches 1,500 cases / CIDRAP | high (0.8759) | include_for_content_fetch | True |
| other | src_search_e7c041eca759 | Pan American Health Organization / Ten countries in the Americas report measles outbreaks in 2025 - PAHO/WHO / Pan American Health Organi... | high (0.8232) | include_for_content_fetch | True |
| other | src_search_8242cbb785a1 | Pan American Health Organization / Situation Report #2: Measles in the Americas Region - PAHO/WHO / Pan American Health Organization | high (0.8048) | include_for_content_fetch | True |
| other | src_search_5155d9022c8b | / Over 2K measles cases reported in US in 2025 as ongoing ... - ABC7 | high (0.8594) | include_for_content_fetch | True |
| other | src_search_62040490ce12 | Centers for Disease Control and Prevention / [PDF] MEASLES – THE AMERICAS 2025 - Yale Health | medium (0.724) | include_for_content_fetch | True |
| other | src_search_6e578fc529e9 | Pan American Health Organization / Situation Report #1: Measles in the Americas Region - PAHO/WHO / Pan American Health Organization | high (0.8048) | include_for_content_fetch | True |
| other | src_search_1bd67ca5631e | / PAHO calls for regional action as the Americas lose measles elimination status - World / ReliefWeb | high (0.8202) | include_for_content_fetch | True |
| other | src_search_c2292d934097 | National Center for Biotechnology Information / Sustained increase in measles cases prompts the Americas to strengthen surveillance, rapi... | high (0.877) | include_for_content_fetch | True |
| other | src_search_4e73f2d0f38f | Centers for Disease Control and Prevention / Characteristics of Patients Hospitalized with Measles During an Outbreak — West Texas, Janua... | high (0.8943) | include_for_content_fetch | True |
| other | src_search_9d3a148dc974 | Centers for Disease Control and Prevention / Measles Outbreak in a Child Care Facility — Lubbock, Texas, March–April 2025 / MMWR | high (0.8943) | include_for_content_fetch | True |
| other | src_search_3b88e198ee65 | / Measles death of unvaccinated child in Texas outbreak is 1st fatality in US in a decade - ABC7 New York | high (0.8639) | include_for_content_fetch | True |
| other | src_search_831265159816 | / Texas Declares Measles Outbreak 'Over' After 762 Cases, Two Child ... | high (0.8823) | include_for_content_fetch | True |
| other | src_search_50fedea73302 | / 2nd child with measles dies in Texas, according to state health officials - ABC News | high (0.6266) | include_for_content_fetch | True |
| other | src_search_cf354551481b | New Mexico Department of Health / 2025 Measles Outbreak - New Mexico Department of Health | high (0.6778) | include_for_content_fetch | True |
| other | src_search_ef917f9b28c7 | New Mexico Department of Health / Measles - New Mexico Department of Health | high (0.6386) | include_for_content_fetch | True |
| other | src_search_2e1655bc0f11 | / New Mexico (USA) measles outbreak case counts as of 22 Apr 2025 | high (0.8823) | include_for_content_fetch | True |
| other | src_search_3d2f6cacf3f7 | CIDRAP / As US measles cases top 1,300, report details last year’s outbreak in New Mexico / CIDRAP | high (0.8759) | include_for_content_fetch | True |
| other | src_search_104eec370092 | Centers for Disease Control and Prevention / [PDF] Measles Outbreak — New Mexico, 2025 - CDC | high (0.8183) | include_for_content_fetch | True |
| other | src_search_035d67976d9a | Centers for Disease Control and Prevention / Measles Outbreak — New Mexico, 2025 / MMWR | high (0.8943) | include_for_content_fetch | True |
| other | src_search_69d20bdba5cb | Centers for Disease Control and Prevention / Tracking Measles in the U.S.: Latest Maps and Cases - The New York Times | high (0.6658) | include_for_content_fetch | True |
| other | src_search_5ca479a49f5f | Pan American Health Organization / PAHO issues epidemiological alert amid continued measles transmission in the Americas and urges streng... | high (0.8048) | include_for_content_fetch | True |
| other | src_search_b9c871cc4117 | Pan American Health Organization / [PDF] Epidemiological Update Measles in the Americas Region - PAHO | medium (0.7264) | include_for_content_fetch | True |
| other | src_search_8f5d473e2e2f | Pan American Health Organization / [PDF] Epidemiological Alert Measles in the Americas Region | medium (0.708) | include_for_content_fetch | True |
| other | src_search_fdf4513eb148 | Pan American Health Organization / Epidemiological Alert Measles in the Americas Region - 3 February 2026 - PAHO/WHO / Pan American Healt... | high (0.8048) | include_for_content_fetch | True |
| other | src_search_aabc350f7aa0 | Centers for Disease Control and Prevention / [PDF] MEASLES – THE AMERICAS 2025 - 2026 - Yale Health | medium (0.724) | include_for_content_fetch | True |
| other | src_search_97d0b1208f3d | / U.S. Measles Cases Hit Highest Level Since Declared Eliminated in ... | high (0.6879) | include_for_content_fetch | True |
| other | src_search_b285c8bbed4b | / Measles Cases Surge in 2025: Key Facts and Prevention Tips - PHM | medium (0.6879) | include_for_content_fetch | True |
| other | src_search_7af26f33a470 | / Measles 2025 / New England Journal of Medicine | high (0.6879) | include_for_content_fetch | True |

## 5. 真实网页抓取结果

- Documents fetched/parsed: `45`
- Search-derived sources selected for fetch: `45`
- Search-derived skipped by reason: `{}`
- Fetch status counts: `fetch_failed=1, fetched=44`
- External fetch enabled: `True`
- Fetch provider counts: `native_requests=1, tavily_extract=44`
- External fetch failure counts: `native_requests=1, tavily_extract=1`
- Selected fetch bucket counts: `target_official_authority=45`
- Parser status counts: `parsed_html=1, parsed_text=44`
- Parser used counts: `html_stdlib_parser=1, text_parser=44`
- Quality status counts: `unusable=4, usable=41`
- Validation-reserved skipped from fetch: `[]`

| Source ID | Provider | Fetch status | HTTP | Parse | Parser | Quality | Text chars | Tables |
|---|---|---|---|---|---|---|---|---|
| src_search_4e73f2d0f38f | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 26745 | 0 |
| src_search_3109afb35d90 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 28035 | 0 |
| src_search_9d3a148dc974 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 20505 | 0 |
| src_search_4b282ae73985 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 13887 | 0 |
| src_search_62409e4d2cf9 | native_requests | fetch_failed | 403 | parsed_html | html_stdlib_parser | unusable | 16 | 0 |
| src_search_831265159816 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 32393 | 0 |
| src_search_fec37a5bcdfb | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 5852 | 0 |
| src_search_cd5fb2750261 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 7862 | 0 |
| src_search_283a8bed6a9d | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 57418 | 0 |
| src_search_3b88e198ee65 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 9275 | 0 |
| src_search_7cb311dd75e6 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 13445 | 0 |
| src_search_497d92fe2060 | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 40454 | 0 |
| src_search_2eb069f08192 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 17346 | 0 |
| src_search_50fedea73302 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 10915 | 0 |
| src_search_1931fc9fea85 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 44364 | 0 |
| src_search_035d67976d9a | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 21132 | 0 |
| src_search_14e93bfe3eec | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 24119 | 0 |
| src_search_2e1655bc0f11 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 6422 | 0 |
| src_search_74152a4ae4ab | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 23059 | 0 |
| src_search_9570e9e8018b | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 8435 | 0 |
| src_search_3e232b5b243d | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 5152 | 0 |
| src_search_3d2f6cacf3f7 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 15330 | 0 |
| src_search_4847d41afdb8 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 12565 | 0 |
| src_search_4250b5c89dbb | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 26003 | 0 |
| src_search_104eec370092 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 21530 | 0 |
| src_search_cf354551481b | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 26285 | 0 |
| src_search_69d20bdba5cb | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 7326 | 0 |
| src_search_ef917f9b28c7 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 32077 | 0 |
| src_search_270d5e6d3895 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 8380 | 0 |
| src_search_c2292d934097 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 19372 | 0 |
| src_search_5155d9022c8b | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 6378 | 0 |
| src_search_e7c041eca759 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 12521 | 0 |
| src_search_1bd67ca5631e | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 7172 | 0 |
| src_search_5ca479a49f5f | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 11388 | 0 |
| src_search_8242cbb785a1 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 6145 | 0 |
| src_search_fdf4513eb148 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 6035 | 0 |
| src_search_6e578fc529e9 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 6288 | 0 |
| src_search_b9c871cc4117 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 27649 | 0 |
| src_search_62040490ce12 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 30963 | 0 |
| src_search_aabc350f7aa0 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 33109 | 0 |
| src_search_8f5d473e2e2f | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 59555 | 0 |
| src_search_97d0b1208f3d | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 11125 | 0 |
| src_search_b285c8bbed4b | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 5092 | 0 |
| src_search_7af26f33a470 | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 134535 | 0 |
| src_search_95e36ab59cc7 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 11578 | 0 |

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
- Stop reason: `Max iterations (2) reached and evidence coverage is substantively sufficient across all target fields and required source-type categories for the Q1 2025 window.`
- Query source counts: `{'iterative_llm_initial_search_plan': 4, 'iterative_llm_refinement': 4}`
- Iteration query counts: `{'1': 4, '2': 4}`

### 6.2 LLM Source Critic

- Attempted source count: `0`
- Assessed source count: `0`
- Skipped source count: `48`
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
- Assessed source count: `48`
- Final role counts: `collection=19, collection_support=2, context=15, validation=12`
- Risk flag counts: `ambiguous_disease=1, ambiguous_location=5, authority_score_may_underweight_institutional_domain=1, complete_source_provenance=24, context_or_background_only=8, context_role_only_not_suitable_for_primary_case_count_extraction=1, contradictory_role_flags: simultaneously flagged as both primary_or_authoritative_source and secondary_news_or_media_source — source nature is ambiguous and requires human adjudication=1, data_granularity_gap: score=0.68 indicates source likely provides aggregate or narrative epidemiological content rather than discrete extractable fields (confirmed cases, hospitalizations, deaths by date/subnational location) required by collection spec=1, data_signal_in_source_metadata=48, data_values_require_corroboration_with_cdc_nndss=1, disease_relevance_unclear=1, extraction_schema_warning: task_input_warnings flag that extraction_record_model_still_hantavirus_named — verify Measles field mapping is active before attempting extraction from this source=1, geographic_granularity_unclear=5, independence_unclear=4, independence_unclear_institutional_editorial_voice=1, international_organization_authority=4, local_or_subnational_granularity=24, local_source_matches_task_location=31, location_match_from_planned_query=12, location_relevance_unclear=5, low_authority_relevant_source=5, low_authority_score_inconsistent_with_aap_domain_reputation=1, low_geographic_granularity: score 0.58 — source unlikely to provide subnational or locality-level case data required by collection spec=1, low_machine_readability=5, machine_readable_or_structured=1, missing_publisher=24, missing_publisher: organizational identity and editorial accountability cannot be fully verified from metadata alone=1, missing_publisher_field_inferable_as_aap=1, named_publisher=1, national_or_international_granularity=12, news_article_not_primary_surveillance_data=1, official_public_health_authority=39, pdf_or_report_likely_medium_readability=5, primary_or_authoritative_source=43, provisional_data_risk: any case counts cited in this article for Q1 2025 should be flagged as provisional unless the article explicitly states final counts; cross-validate against CDC NNDSS=1, publication_lag_risk: PMC12825560 is a very high PMC ID suggesting very recent indexing; Q1 2025 peer-reviewed analyses are unlikely to be finalized and may be preliminary or preprint-stage=1, publisher_missing_authority_unclear=3, risk_penalty_applied: deterministic penalty of 0.14 applied, depressing overall credibility score — underlying flags warrant scrutiny=1, role_hint_context_only: both role_hint and deterministic role assignment classify this as context, not collection — use for background framing only=1, role_hint_override: role_hint was collection_support but deterministic layer assigned context — LLM advisory concurs with context assignment; do not use as primary extraction source=1, rubella_conflation_risk: MMR-related reporting context may introduce rubella references — ensure extracted evidence quotes are specific to rubeola (measles), not rubella=1, screening_and_critic_disagree=7, screening_and_critic_disagree: deterministic layers are not in consensus — LLM advisory review triggered as intended; downstream curator should reconcile=1, screening_and_critic_disagree: deterministic pipeline internal disagreement detected — credibility classification may be unreliable without human review=1, secondary_news_or_media_source=4, snapshot_date_required: if accessed for extraction, record access date alongside source_url per disease intelligence guidance on CDC and PMC sources updated continuously=1, source_disease_relevance:insufficient_text=1, source_disease_relevance:target_disease_match=47, source_metadata_matches_requested_disease=47, source_time_matches_requested_window=29, source_type_lowest_priority: news_and_situation_report is the lowest-priority source type in the collection spec hierarchy — should only be used if higher-priority sources are unavailable or incomplete=1, source_type_mismatch: tagged as news_and_situation_report but hosted on PMC — verify whether this is a peer-reviewed article, preprint, or editorial; reclassify source_type accordingly before ingestion=1, standard_web_page=42, task_location_granularity=7, time_window_match_from_planned_query=19, url_path_indicates_communications_guidance: path segment 'communication-tools' strongly suggests this is a messaging/communications resource, not a surveillance or case data report — quantitative extraction risk is high=1`
- LLM assessed count: `3`
- LLM failure count: `0`
- Needs review count: `8`

### 6.3.5 Source Identity / Publisher Assessment

- Identity assessed source count: `48`
- LLM identity assessed source count: `0`
- Post-fetch identity assessed source count: `45`
- Unknown publisher count: `20`
- Source type counts: `academic_or_peer_reviewed_source=4, background_fact_sheet=1, international_public_health_agency=8, national_public_health_agency=7, news_media=3, official_public_health_agency=11, secondary_aggregator=1, social_media=2, state_or_local_public_health_agency=2, structured_database=3, unknown=6`
- Claim support role counts: `context_only=1, corroboration_support=4, insufficient_information=12, primary_case_claim_support=31`
- Fetch use counts: `fetch_for_context=1, fetch_for_extraction=35, fetch_only_after_review=12`
- Warning counts: `actual_publisher_unknown=24, direct_target_official_fast_path_skips_source_identity=48, publisher_from_search_metadata_unverified=48, search_provider_not_publisher=48`

### 6.4 LLM Structured Extraction

- Extraction mode: `llm_structured_output`
- Eligible chunk count: `913`
- LLM call count: `30`
- LLM success count: `30`
- LLM error count: `0`
- Raw record count: `73`

## 7. 最终抽取 records

- Normalized record count: `72`
- Run quality status: `partial_with_quarantined_records`
- Final dataset mode: `task_aware_quality_gated_records`
- Quality-gated accepted final dataset count: `1`
- Final case dataset count: `0`
- Zero-case statement count: `0`
- Exposure-monitoring record count: `0`
- Surveillance summary record count: `3`
- Outbreak summary record count: `7`
- Context record count: `6`
- Unclassified observation count: `7`
- Observation dataset view counts: `{'final_case_dataset': 0, 'global_outbreak_event_dataset': 0, 'regional_surveillance_dataset': 0, 'country_year_aggregate_dataset': 0, 'official_alert_dataset': 0, 'probable_case_dataset': 0, 'suspected_case_dataset': 0, 'unspecified_case_dataset': 0, 'death_dataset': 0, 'hospitalization_dataset': 0, 'zero_case_statements': 0, 'exposure_monitoring_records': 0, 'surveillance_summary_records': 3, 'outbreak_summary_records': 7, 'context_records': 6, 'non_primary_observations': 21, 'unclassified_observation_records': 7}`
- Pre-quality-gate record count: `72`
- Quarantined record count: `17`
- Pending review record count: `54`
- Non-primary observation count: `13`
- Final dataset post-review count: `1`
- Primary-case dataset status: `no_primary_case_dataset_records`
- Recommended primary dataset message: `No primary case dataset records were accepted; inspect zero-case, exposure-monitoring, context, and other observation views.`
- Primary-case eligible accepted count: `0`
- Corroborated primary case event count: `0`
- Record inclusion status counts: `{'quarantined_outside_scope': 14, 'pending_human_review': 54, 'quarantined_schema_invalid': 2, 'accepted_with_warnings': 1, 'quarantined_non_primary_observation': 1}`
- Run quality warnings: `['no_primary_case_dataset_records', 'no_corroborated_primary_case_events']`
- Accepted source counts: `src_search_4e73f2d0f38f=1`

| Record ID | Date / period | Location | Cases | Deaths | Source | LLM used |
|---|---|---|---|---|---|---|
| rec_src_search_4e73f2d0f38f_006 | January–March 2025 | West Texas | none | none | src_search_4e73f2d0f38f | True |

## 8. Validation 对比

### Claim-level corroboration

- Claim count: `82`
- Claim comparison count: `3321`
- Corroborated event count: `15`
- Corroborated primary case event count: `0`
- Observation type counts: `ambiguous_public_health_observation=6, confirmed_case_record=15, death_record=9, hospitalization_record=17, outbreak_summary=7, unspecified_case_record=28`
- Corroboration status counts: `conflicting_claims=1, insufficient_information=1, single_source_unverified=13`

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

- Human review item count: `115`
- Evaluation review flag count: `0`
- Anomaly review item count: `9`

| Review ID | Type | Related IDs | Reason |
|---|---|---|---|
| review_source_credibility_src_search_cd5fb2750261 | source_credibility | src_search_cd5fb2750261 | missing_publisher |
| review_source_src_search_cd5fb2750261 | source_screening | src_search_cd5fb2750261 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_src_search_2eb069f08192 | source_screening | src_search_2eb069f08192 | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_credibility_src_search_62409e4d2cf9 | source_credibility | src_search_62409e4d2cf9 | missing_publisher |
| review_source_src_search_62409e4d2cf9 | source_screening | src_search_62409e4d2cf9 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_7cb311dd75e6 | source_credibility | src_search_7cb311dd75e6 | missing_publisher |
| review_source_src_search_7cb311dd75e6 | source_screening | src_search_7cb311dd75e6 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_14e93bfe3eec | source_credibility | src_search_14e93bfe3eec | missing_publisher |
| review_source_src_search_14e93bfe3eec | source_screening | src_search_14e93bfe3eec | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_74152a4ae4ab | source_credibility | src_search_74152a4ae4ab | missing_publisher |
| review_source_src_search_74152a4ae4ab | source_screening | src_search_74152a4ae4ab | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_9570e9e8018b | source_credibility | src_search_9570e9e8018b | missing_publisher |

## 9.5 Stage 11 anomaly detection and review application

- Anomaly result count: `14`
- Anomaly severity counts: `high=4, low=5, medium=5`
- Anomaly needs-human-review count: `9`
- Decisions provided: `0`
- Decisions applied: `0`
- Decisions rejected: `0`
- Audit entries: `0`
- Final dataset post-review count: `1`
- Records excluded by review: `0`

| Anomaly ID | Type | Severity | Target | Reason |
|---|---|---|---|---|
| anom_001 | deaths_without_case_reference | low | rec_src_search_8242cbb785a1_002 | deaths present but no comparable case count is available |
| anom_002 | deaths_without_case_reference | low | rec_src_search_4e73f2d0f38f_003 | deaths present but no comparable case count is available |
| anom_003 | deaths_without_case_reference | low | rec_src_search_831265159816_011 | deaths present but no comparable case count is available |
| anom_004 | deaths_without_case_reference | low | rec_src_search_831265159816_018 | deaths present but no comparable case count is available |
| anom_005 | deaths_without_case_reference | low | rec_src_search_831265159816_028 | deaths present but no comparable case count is available |
| anom_006 | out_of_scope_count_bearing_record | high | event_049 | Stage 10 validation marked record outside requested scope: outside_time_window |
| anom_007 | out_of_scope_count_bearing_record | high | event_050 | Stage 10 validation marked record outside requested scope: outside_time_window |
| anom_008 | validation_conflict_anomaly | high | event_007 | Validation result is a conflict: Sources report substantially different numeric values for the same linked event. |
| anom_009 | validation_conflict_anomaly | high | event_019 | Validation result is a conflict: Sources may use different case definitions or reporting categories. |
| anom_010 | aggregate_member_mismatch | medium | event_001 | event cluster canonical count differs from sum of comparable countable members |
| anom_011 | aggregate_member_mismatch | medium | event_007 | event cluster canonical count differs from sum of comparable countable members |
| anom_012 | aggregate_member_mismatch | medium | event_018 | event cluster canonical count differs from sum of comparable countable members |

| Applied decision | Type | Target | Audit IDs | Reason |
|---|---|---|---|---|

## 10. 输出文件

- Run output directory: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_measles_us_2025_q1`
- Collection final dataset: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_measles_us_2025_q1\collection\final_dataset.csv`
- Collection final case dataset: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_measles_us_2025_q1\collection\final_case_dataset.csv`
- Collection zero-case statements: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_measles_us_2025_q1\collection\zero_case_statements.csv`
- Collection exposure-monitoring records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_measles_us_2025_q1\collection\exposure_monitoring_records.csv`
- Collection surveillance summaries: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_measles_us_2025_q1\collection\surveillance_summary_records.csv`
- Collection outbreak summaries: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_measles_us_2025_q1\collection\outbreak_summary_records.csv`
- Collection context records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_measles_us_2025_q1\collection\context_records.csv`
- Collection unclassified observations: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_measles_us_2025_q1\collection\unclassified_observation_records.csv`
- Collection observation dataset summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_measles_us_2025_q1\collection\observation_type_dataset_summary.json`
- Collection pre-quality-gate records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_measles_us_2025_q1\collection\final_dataset_pre_quality_gate.csv`
- Collection quarantined records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_measles_us_2025_q1\collection\quarantined_records.csv`
- Collection pending review records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_measles_us_2025_q1\collection\pending_review_records.csv`
- Collection non-primary observations: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_measles_us_2025_q1\collection\non_primary_observations.csv`
- Collection record inclusion decisions: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_measles_us_2025_q1\collection\record_inclusion_decisions.json`
- Collection final dataset post-review: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_measles_us_2025_q1\collection\final_dataset_post_review.csv`
- Collection anomaly results: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_measles_us_2025_q1\collection\anomaly_results.json`
- Collection human review audit trail: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_measles_us_2025_q1\collection\human_review_audit_trail.json`
- Collection source registry: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_measles_us_2025_q1\collection\source_registry.json`
- Validation mode: `diagnostic_only`
- Validation records source: `state`
- Validation records output: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_measles_us_2025_q1\validation\ground_truth_records.csv`
- Inactive validation records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_measles_us_2025_q1\validation\inactive_validation_records.csv`
- Validation compatibility summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_measles_us_2025_q1\validation\validation_source_compatibility_summary.json`
- Evaluation report CSV: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_measles_us_2025_q1\evaluation\evaluation_report.csv`
- Human-readable report: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_measles_us_2025_q1\workflow_run_report_chinese.md`

## 11. 当前结论

This workflow run executed the configured data collection workflow through the exported graph and artifact pipeline. The user-facing run status is: PARTIAL: accepted records produced, but some records were quarantined.
The run completed technically and produced quality-gated accepted records in the final dataset.

- Package metadata says LLM used: `True`
- Contains synthetic fixture data: `False`
- Generated at UTC: `2026-06-25T20:39:50.619345+00:00`

## 12. Workflow visualization artifacts

- Workflow visualization index: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_measles_us_2025_q1\workflow_visualization\index.html`
- Workflow timeline: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_measles_us_2025_q1\workflow_visualization\workflow_timeline.html`
- Evidence flow graph: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_measles_us_2025_q1\workflow_visualization\evidence_flow_graph.html`
- Claim comparison cards: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_measles_us_2025_q1\workflow_visualization\claim_comparison_cards.html`
- Dataset decision flow: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_measles_us_2025_q1\workflow_visualization\dataset_decision_flow.html`
- Human review workflow visualization: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_measles_us_2025_q1\workflow_visualization\human_review_workflow.html`
- Visualization summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_measles_us_2025_q1\workflow_visualization\workflow_visualization_summary.json`
