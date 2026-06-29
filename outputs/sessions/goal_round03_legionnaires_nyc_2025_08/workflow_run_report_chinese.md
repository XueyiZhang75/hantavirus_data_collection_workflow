# data collection workflow Run Report

## 1. 输入任务

Collect Legionnaires' disease cases, deaths, dates, locations, source URLs, source types, and evidence quotes for New York City from 2025-08-01 to 2025-08-31.

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
- Search-derived source candidates: `45`
- Iterative source discovery: `True`
- Iterative search iterations: `2`
- Iterative stop decision: `stop_sufficient`
- Iterative stop reason: `Maximum iteration budget (2 iterations, 8 queries, ~45 accepted candidates across both rounds) has been reached, and the evidence base is comprehensively sufficient for all target fields. No further search is warranted.`
- Source credibility assessed sources: `45`
- Source credibility role counts: `{'excluded': 6, 'collection_support': 8, 'context': 19, 'validation': 12}`
- Source identity assessed sources: `45`
- Source identity type counts: `{'official_public_health_agency': 18, 'social_media': 7, 'academic_or_peer_reviewed_source': 1, 'news_media': 10, 'structured_database': 1, 'national_public_health_agency': 5, 'state_or_local_public_health_agency': 1, 'background_fact_sheet': 1, 'secondary_aggregator': 1}`
- Source identity warning counts: `{'search_provider_not_publisher': 45, 'publisher_from_search_metadata_unverified': 45, 'actual_publisher_unknown': 37, 'direct_target_official_fast_path_skips_source_identity': 45}`
- Source discovery method: `live_search_only`
- Disease relevance target: `Legionnaires' disease`
- Disease relevance source status counts: `{'ambiguous_disease': 27, 'insufficient_text': 12, 'target_disease_match': 6}`
- Disease relevance chunk status counts: `{'target_disease_match': 95, 'ambiguous_disease': 99, 'insufficient_text': 4, 'unrelated_disease': 19, 'related_context_only': 1}`
- Disease relevance record status counts: `{'compatible': 123, 'ambiguous_disease': 10}`
- Rejected incompatible record count: `0`
- Final route: `finalize`

## 2.5 Run quality status

- User-facing run status: `PARTIAL: accepted records produced, but some records were quarantined.`
- Technical execution status: `completed`
- Run quality status: `partial_with_quarantined_records`
- Final dataset mode: `task_aware_quality_gated_records`
- Accepted final dataset count: `2`
- Final case dataset count: `2`
- Zero-case statement count: `0`
- Exposure-monitoring record count: `0`
- Surveillance summary record count: `0`
- Outbreak summary record count: `0`
- Context record count: `9`
- Unclassified observation count: `4`
- Observation dataset view counts: `{'final_case_dataset': 2, 'global_outbreak_event_dataset': 0, 'regional_surveillance_dataset': 0, 'country_year_aggregate_dataset': 0, 'official_alert_dataset': 0, 'probable_case_dataset': 0, 'suspected_case_dataset': 0, 'unspecified_case_dataset': 2, 'death_dataset': 1, 'hospitalization_dataset': 1, 'zero_case_statements': 0, 'exposure_monitoring_records': 0, 'surveillance_summary_records': 0, 'outbreak_summary_records': 0, 'context_records': 9, 'non_primary_observations': 9, 'unclassified_observation_records': 4}`
- Pre-quality-gate record count: `43`
- Quarantined record count: `9`
- Pending review record count: `32`
- Non-primary observation count: `4`
- Final dataset post-review count: `2`
- Primary-case dataset status: `primary_case_records_present`
- Recommended primary dataset message: `Primary case dataset records are available in final_case_dataset.`
- Primary-case eligible accepted count: `2`
- Corroborated primary case event count: `0`
- Recommended user message: `Review final_dataset and warnings before use.`

Workflow technically completed and produced quality-gated accepted records.

## 3. Workflow 运行过程

Graph is executed as a mostly serial workflow. The only conditional branch is after `quality_gate_routing`: the run enters `human_review` when quality or validation checks require review, then still builds the final data package. In this run, the graph route is shown above; validation comparison review flags are reported separately in Section 8.

1. `task_intake_and_scope_planning` - Built CollectionSpec from structured task input.
2. `disease_intelligence_builder` - Built disease intelligence from LLM output (Legionnaires' disease).
3. `profile_and_schema_setup` - Built active disease profile, collection schema, and source strategy (Legionnaires' disease, generation_method=diseas...
4. `executable_source_planning` - Built executable source plan with 10 planned queries; no searches were executed.
5. `query_strategy_builder` - Built 10 direct_collection search queries from the LLM evidence strategy plan.
6. `source_discovery` - Discovered 45 source candidates using live_search_only.
7. `source_dedup_and_registry` - Built source registry with 45 entries (0 duplicates dropped).
8. `source_screening` - Screened 45 sources using deterministic policy.
9. `source_critic_and_uncertainty_routing` - Critic reviewed 45 sources; 27 ready for fetch, 0 deferred, 28 flagged for human review.
10. `content_fetch_and_parse` - Built 27 fetch requests, produced 27 documents (live_fetch_enabled=True, fixture_documents_enabled=False, fixtures_lo...
11. `document_quality_check` - Quality-checked 27 documents: 23 usable, 0 partial, 0 offline stub, 0 parse deferred, 4 unusable.
12. `evidence_chunking_and_data_presence_flagging` - Chunked 23/27 documents into 218 evidence chunks (195 flagged as containing target data).
13. `structured_extraction` - Built 45 raw records (extraction_mode=llm_structured_output, llm_enabled=True).
14. `schema_validation_and_repair` - Validated 45 raw records: 43 validated (1 need review), 2 rejected.
15. `record_normalization` - Normalized 43/43 records (1 need review).
16. `record_linking` - Linked 43/43 normalized records into 28 candidate events.
17. `cross_source_consistency_check` - Checked 12 multi-record events; found 2 new conflicts and 116 validation results (0 events need review).
18. `quality_gate_routing` - Human review disabled; preserving review flags as audit metadata and routing to final_data_package_builder.
19. `final_data_package_builder` - Assembled hardened FinalDataPackage from current state.

## 4. 数据源分工

| Role | Source ID | Publisher / title | Credibility | Final decision | Fetch ready |
|---|---|---|---|---|---|
| context_only | src_search_55902341c014 | / For most people, Legionnaires' disease sounds like a rare ... | low (0.328) | needs_human_review | False |
| context_only | src_search_74ae67b4e657 | CIDRAP / Public Health Alerts: Outbreak of Legionnaires’ disease associated with cooling tower systems in Central Harlem / CIDRAP | high (0.4648) | include_for_content_fetch | True |
| context_only | src_search_d7abef8536a2 | / NYC legionnaires' outbreak: Officials identify 10 buildings tied to Harlem outbreak, including hospital; 4th death announced - ABC7 New... | needs_review (0.4151) | needs_human_review | False |
| context_only | src_search_58e8d27d8c67 | / What we learned from NYC's 2015 Legionnaires' outbreak about cooling towers and inspections - Healthbeat | needs_review (0.4335) | needs_human_review | False |
| context_only | src_search_8572f55d7887 | National Center for Biotechnology Information / Legionnaires’ Disease Outbreaks and Cooling Towers, New York City, New York, USA | needs_review (0.5199) | needs_human_review | False |
| context_only | src_search_a939cc062696 | / 7 things to know about New York City's Legionnaires' disease ... | low (0.4335) | needs_human_review | False |
| context_only | src_search_ee3c4e1dc1cd | / Three Deaths, 67 People in NYC Diagnosed With Legionnaires' Disease - Infectious Disease Advisor | medium (0.5551) | needs_human_review | False |
| context_only | src_search_77673ee49a41 | / I've issued the following statement on the New York City Department ... | low (0.3991) | needs_human_review | False |
| context_only | src_search_d3c242f1bd62 | / ProMED: Protecting Global Health, One Alert at a Time | low (0.328) | needs_human_review | False |
| context_only | src_search_acc7a5476d26 | / Instagram | high (0.3314) | include_for_content_fetch | False |
| context_only | src_search_2a116853cc42 | / Legionnaires' disease case total in Central Harlem rises to 73, officials say | low (0.344) | needs_human_review | False |
| context_only | src_search_f4d05ea78792 | / Central Harlem Legionnaires' outbreak: 3 dead, 90 diagnosed with Legionnaires' Disease, NYC Health Department says - ABC7 New York | low (0.4151) | needs_human_review | False |
| context_only | src_search_f479da1d3f17 | / Two people have died and at least 58 others have been diagnosed ... | low (0.484) | needs_human_review | False |
| context_only | src_search_259ad39d29b4 | / Legionnaires' Disease - NYC Health | low (0.5079) | needs_human_review | False |
| context_only | src_search_f1f4266d2f42 | / 6th Death Reported in Harlem Legionnaires' Outbreak as Bronx ... | low (0.344) | needs_human_review | False |
| context_only | src_search_2db27965c0f8 | / Two cases of Legionnaires' disease under investigation at Bronx ... | low (0.344) | needs_human_review | False |
| context_only | src_search_3a310a531aa5 | / Legionnaires' disease reported in Bronx after ... - NBC New York | low (0.344) | needs_human_review | False |
| context_only | src_search_82f83b77a6d8 | / Legionnaires' disease reported at Bronx apartment building, NYC ... | low (0.4151) | needs_human_review | False |
| context_only | src_search_b3a8cb483c3f | / Legionnaires' reported at Bronx apartment building, NYC ... - YouTube | low (0.4151) | needs_human_review | False |
| context_only | src_search_fec52be8f139 | / NYC investigates Legionnaires' disease cases at Bronx condos | low (0.4151) | needs_human_review | False |
| other | src_search_c6833da45d7d | / Legionnaires' Disease Outbreak in New York City / RT | excluded (0.6823) | include_for_content_fetch | True |
| other | src_search_b74bccc017c5 | / 2025 Legionnaires’ Disease Community Cluster in New York City: Ongoing Public Health Investigation - Goldberg Segalla | high (0.6823) | include_for_content_fetch | True |
| other | src_search_90be6a027c41 | / Public Health Alert: Legionnaires' Disease Outbreak / Manhattan Borough President | excluded (0.6639) | include_for_content_fetch | True |
| other | src_search_b4917c664acb | / NY State EP Alert 8.15.25 / Legionnaires' Disease Update | excluded (0.6639) | include_for_content_fetch | True |
| other | src_search_1596aec16d67 | / New York City Health Department Closes Investigation of Central Harlem Legionnaires’ Disease Cluster - NYC Health | high (0.6823) | include_for_content_fetch | True |
| other | src_search_743df961a25b | / NYC Legionnaires' Outbreak: Fourth Death Confirmed, 101 Sickened | high (0.6639) | include_for_content_fetch | True |
| other | src_search_8e86f33ccf00 | / Legionnaires' disease outbreak: Sixth person dies in Legionnaires' disease outbreak in Harlem as cases rise to 111 - ABC7 New York | excluded (0.6639) | include_for_content_fetch | True |
| other | src_search_72af26a33522 | / Legionnaires' outbreak kills five and infects over 100 in New York | excluded (0.5928) | include_for_content_fetch | True |
| other | src_search_d8125dd1590d | Centers for Disease Control and Prevention / Legionellosis: (Week 40) Weekly cases* of notifiable diseases ... | high (0.7908) | include_for_content_fetch | True |
| other | src_search_73e3075a7ac3 | Centers for Disease Control and Prevention / Methods for Legionnaires' Disease Surveillance / LD Investigations | high (0.7908) | include_for_content_fetch | True |
| other | src_search_372f68735b3d | Centers for Disease Control and Prevention / National Notifiable Diseases Surveillance System (NNDSS) - Health, United States | medium (0.5908) | include_for_content_fetch | True |
| other | src_search_9af2d47673f3 | Centers for Disease Control and Prevention / Surveillance Report 2020-2021 / Legionella / CDC | medium (0.5908) | include_for_content_fetch | True |
| other | src_search_5ec597ef7ab0 | health.ny.gov / Legionnaires' Disease & Legionella | medium (0.6482) | include_for_content_fetch | True |
| other | src_search_ee903f91c827 | Centers for Disease Control and Prevention / Legionellosis Surveillance and Trends / Legionella / CDC | high (0.7908) | include_for_content_fetch | True |
| other | src_search_1646de60acf0 | Centers for Disease Control and Prevention / Assessing Legionella Prevention Efforts - AIHA | high (0.4314) | include_for_content_fetch | True |
| other | src_search_e32cd9e88818 | / DOH Issues Advisory Regarding Legionellosis Surveillance and ... | high (0.8522) | include_for_content_fetch | True |
| other | src_search_f72980cd3634 | / NYC Health Department Provides Update on Community Cluster of Legionnaires' Disease in Central Harlem - NYC Health | high (0.6823) | include_for_content_fetch | True |
| other | src_search_fd4c39b5e976 | / NYC Health Department Provides Update on Legionnaires' Disease Community Cluster in Central Harlem - NYC Health | high (0.6823) | include_for_content_fetch | True |
| other | src_search_b5fd4616caee | / [PDF] 2025 Health Alert #4: Cluster of Legionnaires' Disease in Harlem | excluded (0.6063) | include_for_content_fetch | True |
| other | src_search_950d652e6d2a | / Transcript: Mayor Adams Makes Public Health-Related Announcement with DOHMH Commissioner Dr. Morse and NYC Health + Hospitals CEO Dr. K... | high (0.6663) | include_for_content_fetch | True |
| other | src_search_a9306f6e1687 | / Transcript: First Deputy Mayor Mastro, NYC Health + Hospitals, and ... | high (0.6663) | include_for_content_fetch | True |
| other | src_search_5b7e6dfb326c | / New York City Health Department Provides Update on Community ... | high (0.6663) | include_for_content_fetch | True |
| other | src_search_8ca119dddbda | / Two NYC buildings were sources of Legionnaires’ disease outbreak in Harlem - Healthbeat | medium (0.6823) | include_for_content_fetch | True |
| other | src_search_2d165d3a4d7e | / Outbreak of Legionnaires' Disease Associated with Cooling Tower ... | high (0.4474) | include_for_content_fetch | True |
| other | src_search_caf9b786a60e | / New York City Health Department declares Harlem Legionnaires ... | medium (0.6479) | include_for_content_fetch | True |

## 5. 真实网页抓取结果

- Documents fetched/parsed: `27`
- Search-derived sources selected for fetch: `27`
- Search-derived skipped by reason: `{}`
- Fetch status counts: `fetch_failed=2, fetched=25`
- External fetch enabled: `True`
- Fetch provider counts: `native_requests=2, tavily_extract=25`
- External fetch failure counts: `native_requests=2, tavily_extract=2`
- Selected fetch bucket counts: `target_official_authority=27`
- Parser status counts: `parsed_html=2, parsed_text=25`
- Parser used counts: `html_stdlib_parser=2, text_parser=25`
- Quality status counts: `unusable=4, usable=23`
- Validation-reserved skipped from fetch: `[]`

| Source ID | Provider | Fetch status | HTTP | Parse | Parser | Quality | Text chars | Tables |
|---|---|---|---|---|---|---|---|---|
| src_search_c6833da45d7d | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 12667 | 0 |
| src_search_f72980cd3634 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 3426 | 0 |
| src_search_b74bccc017c5 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 6907 | 0 |
| src_search_fd4c39b5e976 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 3114 | 0 |
| src_search_1596aec16d67 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 8081 | 0 |
| src_search_950d652e6d2a | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 24440 | 0 |
| src_search_a9306f6e1687 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 38910 | 0 |
| src_search_5b7e6dfb326c | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 5886 | 0 |
| src_search_90be6a027c41 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 2861 | 0 |
| src_search_b4917c664acb | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 4851 | 0 |
| src_search_743df961a25b | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 5701 | 0 |
| src_search_8e86f33ccf00 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 5699 | 0 |
| src_search_b5fd4616caee | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 4300 | 0 |
| src_search_72af26a33522 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 33306 | 0 |
| src_search_8ca119dddbda | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 13329 | 0 |
| src_search_caf9b786a60e | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 7015 | 0 |
| src_search_74ae67b4e657 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 12101 | 0 |
| src_search_2d165d3a4d7e | native_requests | fetch_failed | 403 | parsed_html | html_stdlib_parser | unusable | 16 | 0 |
| src_search_acc7a5476d26 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 15628 | 0 |
| src_search_e32cd9e88818 | native_requests | fetch_failed | 404 | parsed_html | html_stdlib_parser | unusable | 1467 | 0 |
| src_search_d8125dd1590d | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 13642 | 0 |
| src_search_73e3075a7ac3 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 4798 | 0 |
| src_search_ee903f91c827 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 2628 | 0 |
| src_search_5ec597ef7ab0 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 9649 | 0 |
| src_search_372f68735b3d | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 5565 | 0 |
| src_search_9af2d47673f3 | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 26749 | 0 |
| src_search_1646de60acf0 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 9574 | 0 |

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
- Stop reason: `Maximum iteration budget (2 iterations, 8 queries, ~45 accepted candidates across both rounds) has been reached, and the evidence base is comprehensively sufficient for all target fields. No further search is warranted.`
- Query source counts: `{'iterative_llm_initial_search_plan': 4, 'iterative_llm_refinement': 4}`
- Iteration query counts: `{'1': 4, '2': 4}`

### 6.2 LLM Source Critic

- Attempted source count: `0`
- Assessed source count: `0`
- Skipped source count: `45`
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
- Assessed source count: `45`
- Final role counts: `collection_support=8, context=19, excluded=6, validation=12`
- Risk flag counts: `ambiguous_disease=39, ambiguous_disease_data_content=1, ambiguous_disease_signal_in_source_metadata=27, ambiguous_location=3, complete_source_provenance=8, context_or_background_only=9, contradictory_risk_flags: official_public_health_authority_and_secondary_news_or_media_source_both_asserted_for_same_source=1, data_signal_in_source_metadata=45, death_count_and_building_list_require_official_corroboration_before_extraction=1, disease_relevance_critically_low=1, disease_relevance_score_likely_underestimated: title_explicitly_names_legionnaires_disease_and_nyc_but_snippet_absent_causing_zero_data_signal_count=1, disease_relevance_score_likely_underestimated_due_to_metadata_extraction_failure=1, disease_relevance_unclear=12, do_not_extract_case_counts_as_primary_data=1, general_audience_educational_or_opinion_content=1, geographic_granularity_unclear=3, historical_data_risk_if_extracted=1, independence_unclear=16, local_or_subnational_granularity=26, local_source_matches_task_location=28, location_match_from_planned_query=9, location_relevance_unclear=3, low_authority_relevant_source=2, low_machine_readability=1, lowest_priority_source_type_in_collection_spec=1, media_report_may_precede_official_confirmation=1, missing_publisher=37, missing_publisher_metadata_gap_not_genuine_provenance_concern_for_known_abc_affiliate=1, national_or_international_context=5, national_or_international_granularity=14, no_2025_case_data_extractable: article_predates_collection_period_by_approximately_8_years=1, no_case_count_data_expected=1, no_snippet_available_content_unverifiable=1, non_institutional_publisher=1, not_suitable_for_case_count_extraction=1, null_snippet: absence_of_snippet_prevents_text-level_disease_signal_verification=1, official_public_health_authority=29, pdf_or_report_likely_medium_readability=1, primary_or_authoritative_source=29, retrospective_content_in_target_window_publication=1, screening_and_critic_disagree=20, screening_and_critic_disagree: internal_deterministic_inconsistency_requires_resolution=1, screening_and_critic_disagree_warrants_human_review=1, secondary_news_or_media_source=19, secondary_or_derivative_content_likely=1, social_media_platform_domain=1, source_disease_relevance:ambiguous_disease=27, source_disease_relevance:insufficient_text=12, source_disease_relevance:target_disease_match=6, source_metadata_matches_requested_disease=6, source_time_matches_requested_window=12, source_type_label_mismatch_social_media_tagged_as_news_report=1, source_type_misclassified: tagged_as_news_and_situation_report_but_is_peer_reviewed_literature=1, standard_web_page=44, task_location_granularity=2, temporal_mismatch_critical: publication_circa_2017_incompatible_with_2025_08_collection_window=1, time_window_match_from_planned_query=33, title_references_2015_outbreak_not_2025=1, zero_disease_data_signal_terms_found=1, zero_target_disease_terms_in_metadata=1`
- LLM assessed count: `4`
- LLM failure count: `0`
- Needs review count: `11`

### 6.3.5 Source Identity / Publisher Assessment

- Identity assessed source count: `45`
- LLM identity assessed source count: `0`
- Post-fetch identity assessed source count: `27`
- Unknown publisher count: `36`
- Source type counts: `academic_or_peer_reviewed_source=1, background_fact_sheet=1, national_public_health_agency=5, news_media=10, official_public_health_agency=18, secondary_aggregator=1, social_media=7, state_or_local_public_health_agency=1, structured_database=1`
- Claim support role counts: `context_only=7, corroboration_support=11, insufficient_information=8, primary_case_claim_support=19`
- Fetch use counts: `fetch_for_context=7, fetch_for_extraction=30, fetch_only_after_review=8`
- Warning counts: `actual_publisher_unknown=37, direct_target_official_fast_path_skips_source_identity=45, publisher_from_search_metadata_unverified=45, search_provider_not_publisher=45`

### 6.4 LLM Structured Extraction

- Extraction mode: `llm_structured_output`
- Eligible chunk count: `184`
- LLM call count: `30`
- LLM success count: `30`
- LLM error count: `0`
- Raw record count: `45`

## 7. 最终抽取 records

- Normalized record count: `43`
- Run quality status: `partial_with_quarantined_records`
- Final dataset mode: `task_aware_quality_gated_records`
- Quality-gated accepted final dataset count: `2`
- Final case dataset count: `2`
- Zero-case statement count: `0`
- Exposure-monitoring record count: `0`
- Surveillance summary record count: `0`
- Outbreak summary record count: `0`
- Context record count: `9`
- Unclassified observation count: `4`
- Observation dataset view counts: `{'final_case_dataset': 2, 'global_outbreak_event_dataset': 0, 'regional_surveillance_dataset': 0, 'country_year_aggregate_dataset': 0, 'official_alert_dataset': 0, 'probable_case_dataset': 0, 'suspected_case_dataset': 0, 'unspecified_case_dataset': 2, 'death_dataset': 1, 'hospitalization_dataset': 1, 'zero_case_statements': 0, 'exposure_monitoring_records': 0, 'surveillance_summary_records': 0, 'outbreak_summary_records': 0, 'context_records': 9, 'non_primary_observations': 9, 'unclassified_observation_records': 4}`
- Pre-quality-gate record count: `43`
- Quarantined record count: `9`
- Pending review record count: `32`
- Non-primary observation count: `4`
- Final dataset post-review count: `2`
- Primary-case dataset status: `primary_case_records_present`
- Recommended primary dataset message: `Primary case dataset records are available in final_case_dataset.`
- Primary-case eligible accepted count: `2`
- Corroborated primary case event count: `0`
- Record inclusion status counts: `{'quarantined_source_not_task_relevant': 2, 'pending_human_review': 32, 'quarantined_outside_scope': 5, 'accepted_with_warnings': 2, 'quarantined_schema_invalid': 1, 'quarantined_ambiguous_non_primary_observation': 1}`
- Run quality warnings: `['no_corroborated_primary_case_events']`
- Accepted source counts: `src_search_1596aec16d67=2`

| Record ID | Date / period | Location | Cases | Deaths | Source | LLM used |
|---|---|---|---|---|---|---|
| rec_src_search_1596aec16d67_001 | As of August 28, 2025 | New York City, New York | 114.0 | 7.0 | src_search_1596aec16d67 | True |
| rec_src_search_1596aec16d67_002 | As of August 28, 2025 | New York City, New York | 104.0 | none | src_search_1596aec16d67 | True |

## 8. Validation 对比

### Claim-level corroboration

- Claim count: `60`
- Claim comparison count: `1770`
- Corroborated event count: `6`
- Corroborated primary case event count: `0`
- Observation type counts: `ambiguous_public_health_observation=4, confirmed_case_record=6, death_record=24, hospitalization_record=15, unspecified_case_record=11`
- Corroboration status counts: `conflicting_claims=2, insufficient_information=2, single_source_unverified=2`

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

- Human review item count: `88`
- Evaluation review flag count: `0`
- Anomaly review item count: `12`

| Review ID | Type | Related IDs | Reason |
|---|---|---|---|
| review_source_credibility_src_search_b74bccc017c5 | source_credibility | src_search_b74bccc017c5 | missing_publisher |
| review_source_src_search_b74bccc017c5 | source_screening | src_search_b74bccc017c5 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_1596aec16d67 | source_credibility | src_search_1596aec16d67 | missing_publisher |
| review_source_src_search_1596aec16d67 | source_screening | src_search_1596aec16d67 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_743df961a25b | source_credibility | src_search_743df961a25b | missing_publisher |
| review_source_src_search_743df961a25b | source_screening | src_search_743df961a25b | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_src_search_55902341c014 | source_screening | src_search_55902341c014 | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_src_search_74ae67b4e657 | source_screening | src_search_74ae67b4e657 | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_credibility_src_search_d7abef8536a2 | source_credibility | src_search_d7abef8536a2 | ABC7 New York (abc7ny.com) is a local ABC affiliate news outlet — a legitimate regional broadcaster, but a secondary media source rather... |
| review_source_src_search_d7abef8536a2 | source_screening | src_search_d7abef8536a2 | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_credibility_src_search_58e8d27d8c67 | source_credibility | src_search_58e8d27d8c67 | This source is a news/media article from healthbeat.org published on 2025-08-20, titled around "lessons learned" from NYC's **2015** Legi... |
| review_source_src_search_58e8d27d8c67 | source_screening | src_search_58e8d27d8c67 | Screening and critic disagree on this source; routing to human review for resolution. |

## 9.5 Stage 11 anomaly detection and review application

- Anomaly result count: `24`
- Anomaly severity counts: `high=2, low=12, medium=10`
- Anomaly needs-human-review count: `12`
- Decisions provided: `0`
- Decisions applied: `0`
- Decisions rejected: `0`
- Audit entries: `0`
- Final dataset post-review count: `2`
- Records excluded by review: `0`

| Anomaly ID | Type | Severity | Target | Reason |
|---|---|---|---|---|
| anom_001 | deaths_without_case_reference | low | rec_src_search_743df961a25b_002 | deaths present but no comparable case count is available |
| anom_002 | deaths_without_case_reference | low | rec_src_search_8e86f33ccf00_002 | deaths present but no comparable case count is available |
| anom_003 | deaths_without_case_reference | low | rec_src_search_b74bccc017c5_002 | deaths present but no comparable case count is available |
| anom_004 | deaths_without_case_reference | low | rec_src_search_caf9b786a60e_002 | deaths present but no comparable case count is available |
| anom_005 | deaths_without_case_reference | low | rec_src_search_72af26a33522_002 | deaths present but no comparable case count is available |
| anom_006 | deaths_without_case_reference | low | rec_src_search_f72980cd3634_002 | deaths present but no comparable case count is available |
| anom_007 | deaths_without_case_reference | low | rec_src_search_b74bccc017c5_005 | deaths present but no comparable case count is available |
| anom_008 | deaths_without_case_reference | low | rec_src_search_fd4c39b5e976_002 | deaths present but no comparable case count is available |
| anom_009 | deaths_without_case_reference | low | rec_src_search_b4917c664acb_003 | deaths present but no comparable case count is available |
| anom_010 | deaths_without_case_reference | low | rec_src_search_743df961a25b_004 | deaths present but no comparable case count is available |
| anom_011 | deaths_without_case_reference | low | rec_src_search_8e86f33ccf00_005 | deaths present but no comparable case count is available |
| anom_012 | deaths_without_case_reference | low | rec_src_search_caf9b786a60e_007 | deaths present but no comparable case count is available |

| Applied decision | Type | Target | Audit IDs | Reason |
|---|---|---|---|---|

## 10. 输出文件

- Run output directory: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_legionnaires_nyc_2025_08`
- Collection final dataset: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_legionnaires_nyc_2025_08\collection\final_dataset.csv`
- Collection final case dataset: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_legionnaires_nyc_2025_08\collection\final_case_dataset.csv`
- Collection zero-case statements: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_legionnaires_nyc_2025_08\collection\zero_case_statements.csv`
- Collection exposure-monitoring records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_legionnaires_nyc_2025_08\collection\exposure_monitoring_records.csv`
- Collection surveillance summaries: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_legionnaires_nyc_2025_08\collection\surveillance_summary_records.csv`
- Collection outbreak summaries: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_legionnaires_nyc_2025_08\collection\outbreak_summary_records.csv`
- Collection context records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_legionnaires_nyc_2025_08\collection\context_records.csv`
- Collection unclassified observations: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_legionnaires_nyc_2025_08\collection\unclassified_observation_records.csv`
- Collection observation dataset summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_legionnaires_nyc_2025_08\collection\observation_type_dataset_summary.json`
- Collection pre-quality-gate records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_legionnaires_nyc_2025_08\collection\final_dataset_pre_quality_gate.csv`
- Collection quarantined records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_legionnaires_nyc_2025_08\collection\quarantined_records.csv`
- Collection pending review records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_legionnaires_nyc_2025_08\collection\pending_review_records.csv`
- Collection non-primary observations: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_legionnaires_nyc_2025_08\collection\non_primary_observations.csv`
- Collection record inclusion decisions: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_legionnaires_nyc_2025_08\collection\record_inclusion_decisions.json`
- Collection final dataset post-review: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_legionnaires_nyc_2025_08\collection\final_dataset_post_review.csv`
- Collection anomaly results: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_legionnaires_nyc_2025_08\collection\anomaly_results.json`
- Collection human review audit trail: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_legionnaires_nyc_2025_08\collection\human_review_audit_trail.json`
- Collection source registry: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_legionnaires_nyc_2025_08\collection\source_registry.json`
- Validation mode: `diagnostic_only`
- Validation records source: `state`
- Validation records output: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_legionnaires_nyc_2025_08\validation\ground_truth_records.csv`
- Inactive validation records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_legionnaires_nyc_2025_08\validation\inactive_validation_records.csv`
- Validation compatibility summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_legionnaires_nyc_2025_08\validation\validation_source_compatibility_summary.json`
- Evaluation report CSV: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_legionnaires_nyc_2025_08\evaluation\evaluation_report.csv`
- Human-readable report: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_legionnaires_nyc_2025_08\workflow_run_report_chinese.md`

## 11. 当前结论

This workflow run executed the configured data collection workflow through the exported graph and artifact pipeline. The user-facing run status is: PARTIAL: accepted records produced, but some records were quarantined.
The run completed technically and produced quality-gated accepted records in the final dataset.

- Package metadata says LLM used: `True`
- Contains synthetic fixture data: `False`
- Generated at UTC: `2026-06-25T16:28:42.496612+00:00`

## 12. Workflow visualization artifacts

- Workflow visualization index: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_legionnaires_nyc_2025_08\workflow_visualization\index.html`
- Workflow timeline: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_legionnaires_nyc_2025_08\workflow_visualization\workflow_timeline.html`
- Evidence flow graph: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_legionnaires_nyc_2025_08\workflow_visualization\evidence_flow_graph.html`
- Claim comparison cards: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_legionnaires_nyc_2025_08\workflow_visualization\claim_comparison_cards.html`
- Dataset decision flow: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_legionnaires_nyc_2025_08\workflow_visualization\dataset_decision_flow.html`
- Human review workflow visualization: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_legionnaires_nyc_2025_08\workflow_visualization\human_review_workflow.html`
- Visualization summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_legionnaires_nyc_2025_08\workflow_visualization\workflow_visualization_summary.json`
