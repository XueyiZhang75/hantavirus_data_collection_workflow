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
- Search-derived source candidates: `46`
- Iterative source discovery: `True`
- Iterative search iterations: `2`
- Iterative stop decision: `stop_limits_reached`
- Iterative stop reason: `Maximum iteration limit (max_iterations: 2) has been reached. Both planned iterations have been fully executed (8 queries total, within the 10-query cap). The accumulated candidate set is sufficiently rich to support field extraction for the Q1 2025 task window, and further searching is not permitted under the stated bounds.`
- Source credibility assessed sources: `46`
- Source credibility role counts: `{'collection': 18, 'context': 16, 'validation': 12}`
- Source identity assessed sources: `46`
- Source identity type counts: `{'academic_or_peer_reviewed_source': 3, 'national_public_health_agency': 6, 'official_public_health_agency': 13, 'social_media': 5, 'secondary_aggregator': 1, 'international_public_health_agency': 6, 'unknown': 5, 'structured_database': 2, 'state_or_local_public_health_agency': 1, 'news_media': 4}`
- Source identity warning counts: `{'search_provider_not_publisher': 46, 'publisher_from_search_metadata_unverified': 46, 'direct_target_official_fast_path_skips_source_identity': 46, 'actual_publisher_unknown': 28}`
- Source discovery method: `live_search_only`
- Disease relevance target: `Measles`
- Disease relevance source status counts: `{'target_disease_match': 46}`
- Disease relevance chunk status counts: `{'target_disease_match': 898, 'ambiguous_disease': 75, 'related_context_only': 10}`
- Disease relevance record status counts: `{'compatible': 153}`
- Rejected incompatible record count: `0`
- Final route: `finalize`

## 2.5 Run quality status

- User-facing run status: `PARTIAL: accepted records produced, but some records were quarantined.`
- Technical execution status: `completed`
- Run quality status: `partial_with_quarantined_records`
- Final dataset mode: `task_aware_quality_gated_records`
- Accepted final dataset count: `3`
- Final case dataset count: `0`
- Zero-case statement count: `0`
- Exposure-monitoring record count: `1`
- Surveillance summary record count: `11`
- Outbreak summary record count: `6`
- Context record count: `6`
- Unclassified observation count: `1`
- Observation dataset view counts: `{'final_case_dataset': 0, 'global_outbreak_event_dataset': 0, 'regional_surveillance_dataset': 0, 'country_year_aggregate_dataset': 0, 'official_alert_dataset': 0, 'probable_case_dataset': 0, 'suspected_case_dataset': 0, 'unspecified_case_dataset': 0, 'death_dataset': 0, 'hospitalization_dataset': 3, 'zero_case_statements': 0, 'exposure_monitoring_records': 1, 'surveillance_summary_records': 11, 'outbreak_summary_records': 6, 'context_records': 6, 'non_primary_observations': 18, 'unclassified_observation_records': 1}`
- Pre-quality-gate record count: `51`
- Quarantined record count: `26`
- Pending review record count: `22`
- Non-primary observation count: `8`
- Final dataset post-review count: `3`
- Primary-case dataset status: `primary_case_records_present`
- Recommended primary dataset message: `No primary case dataset records were accepted; inspect zero-case, exposure-monitoring, context, and other observation views.`
- Primary-case eligible accepted count: `3`
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
6. `source_discovery` - Discovered 46 source candidates using live_search_only.
7. `source_dedup_and_registry` - Built source registry with 46 entries (0 duplicates dropped).
8. `source_screening` - Screened 46 sources using deterministic policy.
9. `source_critic_and_uncertainty_routing` - Critic reviewed 46 sources; 39 ready for fetch, 0 deferred, 29 flagged for human review.
10. `content_fetch_and_parse` - Built 39 fetch requests, produced 39 documents (live_fetch_enabled=True, fixture_documents_enabled=False, fixtures_lo...
11. `document_quality_check` - Quality-checked 39 documents: 35 usable, 0 partial, 0 offline stub, 0 parse deferred, 4 unusable.
12. `evidence_chunking_and_data_presence_flagging` - Chunked 35/39 documents into 983 evidence chunks (879 flagged as containing target data).
13. `structured_extraction` - Built 51 raw records (extraction_mode=llm_structured_output, llm_enabled=True).
14. `schema_validation_and_repair` - Validated 51 raw records: 51 validated (0 need review), 0 rejected.
15. `record_normalization` - Normalized 51/51 records (0 need review).
16. `record_linking` - Linked 51/51 normalized records into 33 candidate events.
17. `cross_source_consistency_check` - Checked 10 multi-record events; found 8 new conflicts and 142 validation results (4 events need review).
18. `quality_gate_routing` - Human review disabled; preserving review flags as audit metadata and routing to final_data_package_builder.
19. `final_data_package_builder` - Assembled hardened FinalDataPackage from current state.

## 4. 数据源分工

| Role | Source ID | Publisher / title | Credibility | Final decision | Fetch ready |
|---|---|---|---|---|---|
| context_only | src_search_2eb069f08192 | / Clinician Update on Measles Cases and Outbreaks in the United States - Sept 11 2025 | high (0.7823) | include_for_content_fetch | False |
| context_only | src_search_c6c6c612320d | / Measles cases climb in the U.S. after 2025 was worst year in decades | medium (0.7) | needs_human_review | False |
| context_only | src_search_4250b5c89dbb | World Health Organization / Measles - United States of America | medium (0.7335) | include_for_content_fetch | True |
| context_only | src_search_4e73f2d0f38f | Centers for Disease Control and Prevention / Characteristics of Patients Hospitalized with Measles During an Outbreak — West Texas, Janua... | medium (0.7543) | include_for_content_fetch | True |
| context_only | src_search_eec8c3f3b772 | National Center for Biotechnology Information / Measles resurgence in the United States: epidemiological and ... | medium (0.7151) | needs_human_review | False |
| context_only | src_search_ac2170651876 | / An unvaccinated child has died in the Texas measles outbreak, Lubbock health officials say | high (0.5474) | include_for_content_fetch | False |
| context_only | src_search_642c004e56cf | CIDRAP / Texas measles outbreak climbs to 124 cases / CIDRAP | high (0.3646) | include_for_content_fetch | True |
| context_only | src_search_20b2c5ecff8b | / How Texas measles outbreak spread outside of Mennonite community | needs_review (0.3386) | needs_human_review | False |
| context_only | src_search_933f09adbe25 | / The rapid spread of measles in Gaines, Texas - Reuters | needs_review (0.5471) | needs_human_review | False |
| context_only | src_search_8d237fa2e9fb | / The Measles Outbreak in West Texas and Beyond / Johns Hopkins | low (0.357) | needs_human_review | False |
| context_only | src_search_b23316ccaad4 | / The Mennonite population being affected by a measles outbreak in ... | low (0.3386) | needs_human_review | False |
| context_only | src_search_5b3b94cad94b | / Texas measles outbreak hardened Mennonites against vaccines | low (0.357) | needs_human_review | False |
| other | src_search_d1d6036be2f6 | CIDRAP / CDC confirms 23 more US measles cases as 2025 total tops 1,500 / CIDRAP | high (0.8943) | include_for_content_fetch | True |
| other | src_search_fec37a5bcdfb | Centers for Disease Control and Prevention / Expanding Measles Outbreak in the United States and Guidance for ... | high (0.8759) | include_for_content_fetch | True |
| other | src_search_3109afb35d90 | Centers for Disease Control and Prevention / Measles Update — United States, January 1–April 17, 2025 / MMWR | high (0.8943) | include_for_content_fetch | True |
| other | src_search_7acdcc881c7b | / Red Book Online Outbreaks: Measles - AAP Publications | medium (0.772) | include_for_content_fetch | True |
| other | src_search_7cb311dd75e6 | / U.S. Measles Tracker / International Vaccine Access Center | high (0.8431) | include_for_content_fetch | True |
| other | src_search_283a8bed6a9d | Centers for Disease Control and Prevention / Measles Cases and Outbreaks | high (0.8759) | include_for_content_fetch | True |
| other | src_search_c912e73d8e7e | Centers for Disease Control and Prevention / Global Measles Outbreaks - CDC | high (0.8551) | include_for_content_fetch | True |
| other | src_search_74152a4ae4ab | / Public Health: U.S. Measles Outbreak 2025 - MSK Library Guides | high (0.8823) | include_for_content_fetch | True |
| other | src_search_14e93bfe3eec | / 2025 Southwest United States measles outbreak - Wikipedia | high (0.8823) | include_for_content_fetch | True |
| other | src_search_3e232b5b243d | / Measles Outbreak – August 12, 2025 / Texas DSHS | high (0.8823) | include_for_content_fetch | True |
| other | src_search_62409e4d2cf9 | / US Measles Cases Near 2,000 in 2025 as Multi-State Outbreaks ... | high (0.8823) | include_for_content_fetch | True |
| other | src_search_9570e9e8018b | / 2025 Measles Outbreak / South Carolina Department of Public Health | high (0.8823) | include_for_content_fetch | True |
| other | src_search_78fdd46eb63c | / 2025-2026 US Measles Map | high (0.8951) | include_for_content_fetch | True |
| other | src_search_b9c871cc4117 | Pan American Health Organization / [PDF] Epidemiological Update Measles in the Americas Region | medium (0.7264) | include_for_content_fetch | True |
| other | src_search_8242cbb785a1 | Pan American Health Organization / Situation Report #2: Measles in the Americas Region - PAHO/WHO | high (0.8048) | include_for_content_fetch | True |
| other | src_search_01a036ecf63d | World Health Organization / Measles – Region of the Americas | high (0.8024) | include_for_content_fetch | True |
| other | src_search_3f4cf9d46ec9 | / Over 2K measles cases reported in US in 2025 as ongoing ... | high (0.8594) | include_for_content_fetch | True |
| other | src_search_1cb88aa8426c | / Ten countries in the Americas report measles outbreaks in 2025 | high (0.8) | include_for_content_fetch | True |
| other | src_search_cd5fb2750261 | Centers for Disease Control and Prevention / Measles Cases This Year Are Outpacing 2025 - Forbes | high (0.8) | include_for_content_fetch | True |
| other | src_search_0132cfa4f779 | / 2025-2026 Measles Outbreaks: Where Are We Now? Resources and Updates for Local Health Departments | high (0.8) | include_for_content_fetch | True |
| other | src_search_9d3a148dc974 | Centers for Disease Control and Prevention / Measles Outbreak in a Child Care Facility — Lubbock, Texas, March–April 2025 / MMWR | high (0.8943) | include_for_content_fetch | True |
| other | src_search_87bd434eacdf | / Texas measles in Gaines County surpass 100 cases, officials urge ... | high (0.6658) | include_for_content_fetch | True |
| other | src_search_c62c62e520ae | / Texas measles cases remain steady at 750. Track the spread here. - The Texas Tribune | high (0.6658) | include_for_content_fetch | True |
| other | src_search_da86b7826545 | / Texas measles outbreak tops 500 cases across 10 counties / PBS News | high (0.6474) | include_for_content_fetch | True |
| other | src_search_3b88e198ee65 | / Measles death of unvaccinated child in Texas outbreak is 1st fatality ... | high (0.6474) | include_for_content_fetch | True |
| other | src_search_ef917f9b28c7 | New Mexico Department of Health / Measles | high (0.6386) | include_for_content_fetch | True |
| other | src_search_69d20bdba5cb | Centers for Disease Control and Prevention / Tracking U.S. Measles Outbreaks - ny times | high (0.645) | include_for_content_fetch | True |
| other | src_search_4344744ea569 | Centers for Disease Control and Prevention / Measles Death New Mexico - Infectious Disease Special Edition | high (0.8639) | include_for_content_fetch | True |
| other | src_search_a9abbaac7c0e | CIDRAP / Kansas, New Mexico, New York report more measles cases - CIDRAP | high (0.6594) | include_for_content_fetch | True |
| other | src_search_d3d9a2e23a80 | / Southwest Kansas Measles Outbreak Declared Over and MMR ... | high (0.8639) | include_for_content_fetch | True |
| other | src_search_322beeaf24f0 | Pan American Health Organization / [PDF] Epidemiological Update Measles in the Americas Region | medium (0.7264) | include_for_content_fetch | True |
| other | src_search_6e578fc529e9 | Pan American Health Organization / Situation Report #1: Measles in the Americas Region - PAHO/WHO | high (0.8048) | include_for_content_fetch | True |
| other | src_search_62040490ce12 | Centers for Disease Control and Prevention / [PDF] MEASLES – THE AMERICAS 2025 - Yale Health | medium (0.724) | include_for_content_fetch | True |
| other | src_search_c2292d934097 | National Center for Biotechnology Information / Sustained increase in measles cases prompts the Americas ... - PMC | high (0.8642) | include_for_content_fetch | True |

## 5. 真实网页抓取结果

- Documents fetched/parsed: `39`
- Search-derived sources selected for fetch: `39`
- Search-derived skipped by reason: `{}`
- Fetch status counts: `fetch_failed=1, fetched=38`
- External fetch enabled: `True`
- Fetch provider counts: `native_requests=2, tavily_extract=37`
- External fetch failure counts: `native_requests=1, tavily_extract=2`
- Selected fetch bucket counts: `target_official_authority=39`
- Parser status counts: `parsed_html=2, parsed_text=37`
- Parser used counts: `html_stdlib_parser=2, text_parser=37`
- Quality status counts: `unusable=4, usable=35`
- Validation-reserved skipped from fetch: `[]`

| Source ID | Provider | Fetch status | HTTP | Parse | Parser | Quality | Text chars | Tables |
|---|---|---|---|---|---|---|---|---|
| src_search_9d3a148dc974 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 20505 | 0 |
| src_search_d1d6036be2f6 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 19169 | 0 |
| src_search_3109afb35d90 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 28035 | 0 |
| src_search_fec37a5bcdfb | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 5852 | 0 |
| src_search_283a8bed6a9d | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 57418 | 0 |
| src_search_c912e73d8e7e | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 3230 | 0 |
| src_search_7cb311dd75e6 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 13445 | 0 |
| src_search_2eb069f08192 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 17346 | 0 |
| src_search_7acdcc881c7b | native_requests | fetch_failed | 403 | parsed_html | html_stdlib_parser | unusable | 16 | 0 |
| src_search_87bd434eacdf | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 5006 | 0 |
| src_search_c62c62e520ae | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 27977 | 0 |
| src_search_da86b7826545 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 7112 | 0 |
| src_search_3b88e198ee65 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 9275 | 0 |
| src_search_ac2170651876 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 3753 | 0 |
| src_search_78fdd46eb63c | native_requests | fetched | 200 | parsed_html | html_stdlib_parser | unusable | 35 | 0 |
| src_search_74152a4ae4ab | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 23059 | 0 |
| src_search_14e93bfe3eec | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 24119 | 0 |
| src_search_3e232b5b243d | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 5152 | 0 |
| src_search_62409e4d2cf9 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 210128 | 0 |
| src_search_9570e9e8018b | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 8435 | 0 |
| src_search_4344744ea569 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 29037 | 0 |
| src_search_d3d9a2e23a80 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 10975 | 0 |
| src_search_a9abbaac7c0e | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 20045 | 0 |
| src_search_69d20bdba5cb | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 7326 | 0 |
| src_search_ef917f9b28c7 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 32077 | 0 |
| src_search_c2292d934097 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 19372 | 0 |
| src_search_3f4cf9d46ec9 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 6403 | 0 |
| src_search_8242cbb785a1 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 6145 | 0 |
| src_search_6e578fc529e9 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 6288 | 0 |
| src_search_01a036ecf63d | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 71472 | 0 |
| src_search_1cb88aa8426c | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 5404 | 0 |
| src_search_cd5fb2750261 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 7862 | 0 |
| src_search_0132cfa4f779 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 41938 | 0 |
| src_search_b9c871cc4117 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 27649 | 0 |
| src_search_322beeaf24f0 | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 47510 | 0 |
| src_search_62040490ce12 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 30963 | 0 |
| src_search_4e73f2d0f38f | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 26745 | 0 |
| src_search_4250b5c89dbb | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 26003 | 0 |
| src_search_642c004e56cf | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 24045 | 0 |

## 6. 三个 LLM 环节调用结果

### 6.1 LLM Source Planning

- Status: `success`
- Plan generation method: `llm_executable_source_plan`
- Plan execution status: `planned_not_executed`
- Planned query count: `10`
- Planned source category count: `7`
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
- Stop decision: `stop_limits_reached`
- Stop reason: `Maximum iteration limit (max_iterations: 2) has been reached. Both planned iterations have been fully executed (8 queries total, within the 10-query cap). The accumulated candidate set is sufficiently rich to support field extraction for the Q1 2025 task window, and further searching is not permitted under the stated bounds.`
- Query source counts: `{'iterative_llm_initial_search_plan': 4, 'iterative_llm_refinement': 4}`
- Iteration query counts: `{'1': 4, '2': 4}`

### 6.2 LLM Source Critic

- Attempted source count: `0`
- Assessed source count: `0`
- Skipped source count: `46`
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
- Assessed source count: `46`
- Final role counts: `collection=18, context=16, validation=12`
- Risk flag counts: `ambiguous_location=13, ambiguous_location_limits_locality_extraction=1, authority_score_likely_inflated_due_to_source_type_misclassification=1, cannot_confirm_video_producer_or_editorial_standards=1, case_definition_alignment_unknown: peer-reviewed literature may use case definitions that differ from CDC national surveillance standards — definitional discrepancies must be noted in evidence_quote=1, complete_source_provenance=18, context_or_background_only=6, data_extraction_not_recommended_without_official_corroboration=1, data_signal_in_source_metadata=46, evidence_quote_verbatim_extraction_unreliable_from_video=1, evidence_quotes_must_be_verbatim_not_paraphrased_from_visual_or_graphic_elements=1, geographic_granularity_insufficient_for_subnational_field_population=1, geographic_granularity_unclear=13, graphics_or_interactive_url_format_may_contain_structured_extractable_data=1, independence_score_low_all_figures_require_upstream_source_verification=1, independence_unclear=5, independence_unclear_possible_secondary_aggregation=1, international_organization_authority=6, local_or_subnational_granularity=20, local_source_matches_task_location=22, location_match_from_planned_query=11, location_relevance_unclear=13, low_authority_relevant_source=6, low_authority_score_for_public_health_data_collection=1, low_data_granularity: score 0.68 suggests article may aggregate or summarize surveillance data rather than provide field-level case counts, hospitalization splits, or subnational breakdowns required by collection spec=1, low_machine_readability=3, machine_readable_or_structured=2, mennonite_community_cluster_data_may_not_be_replicated_in_national_cdc_totals_yet=1, missing_publisher=28, missing_publisher:cannot_verify_broadcaster_or_editorial_accountability=1, missing_publisher_field_despite_unambiguous_domain=1, missing_publisher_prevents_authority_confirmation=1, named_publisher=1, national_or_international_granularity=11, news_media_tier_source_masquerading_as_international_organization=1, news_source_lowest_priority_tier_in_collection_spec=1, no_data_signal_in_metadata: source_disease_relevance_data_signal_count=0 — no structured epidemiological figures detected in available metadata or snippet=1, no_structured_epidemiological_data_extractable_from_video_format=1, official_public_health_authority=34, pdf_or_report_likely_medium_readability=3, primary_or_authoritative_source=40, provenance_chain_unverifiable_without_publisher_or_transcript=1, publication_lag_risk: peer-reviewed articles covering Q1 2025 events may reflect data available at manuscript submission, not end of collection window — timeliness score 0.72 reflects this=1, reuters_data_journalism_piece_may_synthesize_official_figures_without_direct_citation=1, risk_penalty_elevated_at_0.26=1, role_hint_validation_inappropriate_for_unverified_media_video=1, role_may_be_upgradeable_to_collection_support_if_verbatim_official_figures_present=1, screening_and_critic_disagree=12, screening_and_critic_disagree: internal pipeline disagreement on source role warrants LLM advisory review=1, screening_and_critic_disagree:requires_human_adjudication=1, screening_and_critic_disagree_requires_adjudication=1, screening_and_critic_disagree_requires_resolution=1, secondary_aggregator_risk: PMC article likely cites CDC or state health department data as primary sources — extraction should trace figures back to original surveillance source=1, secondary_news_or_media_source=9, source_disease_relevance:target_disease_match=46, source_metadata_matches_requested_disease=46, source_priority_mismatch:should_be_news_and_situation_report_not_international_organization_report=1, source_time_matches_requested_window=26, source_type_critically_misclassified:labeled_international_organization_report_but_domain_is_youtube.com=1, source_type_label_mismatch: tagged as news_and_situation_report but domain is peer-reviewed PMC literature — actual article type must be verified before role finalization=1, standard_web_page=41, task_location_granularity=2, time_window_match_from_planned_query=20, truncated_title: title ends with ellipsis, full scope and article type cannot be confirmed from metadata alone — full article review required before data extraction=1, video_format_not_machine_readable_for_structured_field_extraction=1, youtube_is_video_hosting_platform_not_authoritative_public_health_source=1, youtube_platform_no_publisher_identified=1`
- LLM assessed count: `4`
- LLM failure count: `0`
- Needs review count: `9`

### 6.3.5 Source Identity / Publisher Assessment

- Identity assessed source count: `46`
- LLM identity assessed source count: `0`
- Post-fetch identity assessed source count: `39`
- Unknown publisher count: `24`
- Source type counts: `academic_or_peer_reviewed_source=3, international_public_health_agency=6, national_public_health_agency=6, news_media=4, official_public_health_agency=13, secondary_aggregator=1, social_media=5, state_or_local_public_health_agency=1, structured_database=2, unknown=5`
- Claim support role counts: `context_only=2, corroboration_support=5, insufficient_information=13, primary_case_claim_support=26`
- Fetch use counts: `fetch_for_context=2, fetch_for_extraction=31, fetch_only_after_review=13`
- Warning counts: `actual_publisher_unknown=28, direct_target_official_fast_path_skips_source_identity=46, publisher_from_search_metadata_unverified=46, search_provider_not_publisher=46`

### 6.4 LLM Structured Extraction

- Extraction mode: `llm_structured_output`
- Eligible chunk count: `819`
- LLM call count: `30`
- LLM success count: `30`
- LLM error count: `0`
- Raw record count: `51`

## 7. 最终抽取 records

- Normalized record count: `51`
- Run quality status: `partial_with_quarantined_records`
- Final dataset mode: `task_aware_quality_gated_records`
- Quality-gated accepted final dataset count: `3`
- Final case dataset count: `0`
- Zero-case statement count: `0`
- Exposure-monitoring record count: `1`
- Surveillance summary record count: `11`
- Outbreak summary record count: `6`
- Context record count: `6`
- Unclassified observation count: `1`
- Observation dataset view counts: `{'final_case_dataset': 0, 'global_outbreak_event_dataset': 0, 'regional_surveillance_dataset': 0, 'country_year_aggregate_dataset': 0, 'official_alert_dataset': 0, 'probable_case_dataset': 0, 'suspected_case_dataset': 0, 'unspecified_case_dataset': 0, 'death_dataset': 0, 'hospitalization_dataset': 3, 'zero_case_statements': 0, 'exposure_monitoring_records': 1, 'surveillance_summary_records': 11, 'outbreak_summary_records': 6, 'context_records': 6, 'non_primary_observations': 18, 'unclassified_observation_records': 1}`
- Pre-quality-gate record count: `51`
- Quarantined record count: `26`
- Pending review record count: `22`
- Non-primary observation count: `8`
- Final dataset post-review count: `3`
- Primary-case dataset status: `primary_case_records_present`
- Recommended primary dataset message: `No primary case dataset records were accepted; inspect zero-case, exposure-monitoring, context, and other observation views.`
- Primary-case eligible accepted count: `3`
- Corroborated primary case event count: `0`
- Record inclusion status counts: `{'pending_human_review': 22, 'quarantined_outside_scope': 25, 'quarantined_schema_invalid': 1, 'accepted_with_warnings': 3}`
- Run quality warnings: `['no_corroborated_primary_case_events']`
- Accepted source counts: `src_search_283a8bed6a9d=3`

| Record ID | Date / period | Location | Cases | Deaths | Source | LLM used |
|---|---|---|---|---|---|---|
| rec_src_search_283a8bed6a9d_012 | 2025 | United States | none | none | src_search_283a8bed6a9d | True |
| rec_src_search_283a8bed6a9d_013 | 2025 | United States | none | none | src_search_283a8bed6a9d | True |
| rec_src_search_283a8bed6a9d_014 | 2025 | United States | none | none | src_search_283a8bed6a9d | True |

## 8. Validation 对比

### Claim-level corroboration

- Claim count: `59`
- Claim comparison count: `1711`
- Corroborated event count: `13`
- Corroborated primary case event count: `0`
- Observation type counts: `ambiguous_public_health_observation=1, confirmed_case_record=13, death_record=9, hospitalization_record=6, outbreak_summary=6, unspecified_case_record=24`
- Corroboration status counts: `conflicting_claims=2, single_source_unverified=11`

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

- Human review item count: `129`
- Evaluation review flag count: `0`
- Anomaly review item count: `26`

| Review ID | Type | Related IDs | Reason |
|---|---|---|---|
| review_source_credibility_src_search_7acdcc881c7b | source_credibility | src_search_7acdcc881c7b | missing_publisher |
| review_source_src_search_7acdcc881c7b | source_screening | src_search_7acdcc881c7b | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_src_search_2eb069f08192 | source_screening | src_search_2eb069f08192 | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_credibility_src_search_7cb311dd75e6 | source_credibility | src_search_7cb311dd75e6 | missing_publisher |
| review_source_src_search_7cb311dd75e6 | source_screening | src_search_7cb311dd75e6 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_74152a4ae4ab | source_credibility | src_search_74152a4ae4ab | missing_publisher |
| review_source_src_search_74152a4ae4ab | source_screening | src_search_74152a4ae4ab | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_14e93bfe3eec | source_credibility | src_search_14e93bfe3eec | missing_publisher |
| review_source_src_search_14e93bfe3eec | source_screening | src_search_14e93bfe3eec | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_3e232b5b243d | source_credibility | src_search_3e232b5b243d | missing_publisher |
| review_source_src_search_3e232b5b243d | source_screening | src_search_3e232b5b243d | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_62409e4d2cf9 | source_credibility | src_search_62409e4d2cf9 | missing_publisher |

## 9.5 Stage 11 anomaly detection and review application

- Anomaly result count: `29`
- Anomaly severity counts: `high=22, low=3, medium=4`
- Anomaly needs-human-review count: `26`
- Decisions provided: `0`
- Decisions applied: `0`
- Decisions rejected: `0`
- Audit entries: `0`
- Final dataset post-review count: `3`
- Records excluded by review: `0`

| Anomaly ID | Type | Severity | Target | Reason |
|---|---|---|---|---|
| anom_001 | deaths_without_case_reference | low | rec_src_search_3e232b5b243d_002 | deaths present but no comparable case count is available |
| anom_002 | deaths_without_case_reference | low | rec_src_search_283a8bed6a9d_016 | deaths present but no comparable case count is available |
| anom_003 | deaths_without_case_reference | low | rec_src_search_283a8bed6a9d_017 | deaths present but no comparable case count is available |
| anom_004 | out_of_scope_count_bearing_record | high | event_006 | Stage 10 validation marked record outside requested scope: outside_time_window |
| anom_005 | out_of_scope_count_bearing_record | high | event_014 | Stage 10 validation marked record outside requested scope: outside_time_window |
| anom_006 | out_of_scope_count_bearing_record | high | event_013 | Stage 10 validation marked record outside requested scope: outside_time_window |
| anom_007 | out_of_scope_count_bearing_record | high | event_007 | Stage 10 validation marked record outside requested scope: outside_time_window |
| anom_008 | out_of_scope_count_bearing_record | high | event_007 | Stage 10 validation marked record outside requested scope: outside_time_window |
| anom_009 | out_of_scope_count_bearing_record | high | event_018 | Stage 10 validation marked record outside requested scope: outside_time_window |
| anom_010 | out_of_scope_count_bearing_record | high | event_005 | Stage 10 validation marked record outside requested scope: outside_time_window |
| anom_011 | out_of_scope_count_bearing_record | high | event_005 | Stage 10 validation marked record outside requested scope: outside_time_window |
| anom_012 | out_of_scope_count_bearing_record | high | event_017 | Stage 10 validation marked record outside requested scope: outside_time_window |

| Applied decision | Type | Target | Audit IDs | Reason |
|---|---|---|---|---|

## 10. 输出文件

- Run output directory: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_measles_us_2025_q1`
- Collection final dataset: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_measles_us_2025_q1\collection\final_dataset.csv`
- Collection final case dataset: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_measles_us_2025_q1\collection\final_case_dataset.csv`
- Collection zero-case statements: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_measles_us_2025_q1\collection\zero_case_statements.csv`
- Collection exposure-monitoring records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_measles_us_2025_q1\collection\exposure_monitoring_records.csv`
- Collection surveillance summaries: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_measles_us_2025_q1\collection\surveillance_summary_records.csv`
- Collection outbreak summaries: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_measles_us_2025_q1\collection\outbreak_summary_records.csv`
- Collection context records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_measles_us_2025_q1\collection\context_records.csv`
- Collection unclassified observations: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_measles_us_2025_q1\collection\unclassified_observation_records.csv`
- Collection observation dataset summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_measles_us_2025_q1\collection\observation_type_dataset_summary.json`
- Collection pre-quality-gate records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_measles_us_2025_q1\collection\final_dataset_pre_quality_gate.csv`
- Collection quarantined records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_measles_us_2025_q1\collection\quarantined_records.csv`
- Collection pending review records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_measles_us_2025_q1\collection\pending_review_records.csv`
- Collection non-primary observations: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_measles_us_2025_q1\collection\non_primary_observations.csv`
- Collection record inclusion decisions: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_measles_us_2025_q1\collection\record_inclusion_decisions.json`
- Collection final dataset post-review: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_measles_us_2025_q1\collection\final_dataset_post_review.csv`
- Collection anomaly results: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_measles_us_2025_q1\collection\anomaly_results.json`
- Collection human review audit trail: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_measles_us_2025_q1\collection\human_review_audit_trail.json`
- Collection source registry: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_measles_us_2025_q1\collection\source_registry.json`
- Validation mode: `diagnostic_only`
- Validation records source: `state`
- Validation records output: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_measles_us_2025_q1\validation\ground_truth_records.csv`
- Inactive validation records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_measles_us_2025_q1\validation\inactive_validation_records.csv`
- Validation compatibility summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_measles_us_2025_q1\validation\validation_source_compatibility_summary.json`
- Evaluation report CSV: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_measles_us_2025_q1\evaluation\evaluation_report.csv`
- Human-readable report: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_measles_us_2025_q1\workflow_run_report_chinese.md`

## 11. 当前结论

This workflow run executed the configured data collection workflow through the exported graph and artifact pipeline. The user-facing run status is: PARTIAL: accepted records produced, but some records were quarantined.
The run completed technically and produced quality-gated accepted records in the final dataset.

- Package metadata says LLM used: `True`
- Contains synthetic fixture data: `False`
- Generated at UTC: `2026-06-25T21:26:48.189479+00:00`

## 12. Workflow visualization artifacts

- Workflow visualization index: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_measles_us_2025_q1\workflow_visualization\index.html`
- Workflow timeline: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_measles_us_2025_q1\workflow_visualization\workflow_timeline.html`
- Evidence flow graph: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_measles_us_2025_q1\workflow_visualization\evidence_flow_graph.html`
- Claim comparison cards: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_measles_us_2025_q1\workflow_visualization\claim_comparison_cards.html`
- Dataset decision flow: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_measles_us_2025_q1\workflow_visualization\dataset_decision_flow.html`
- Human review workflow visualization: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_measles_us_2025_q1\workflow_visualization\human_review_workflow.html`
- Visualization summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_measles_us_2025_q1\workflow_visualization\workflow_visualization_summary.json`
