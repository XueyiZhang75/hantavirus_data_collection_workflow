# data collection workflow Run Report

## 1. 输入任务

Collect COVID-19 cases, deaths, dates, locations, source URLs, source types, and evidence quotes for New York from 2024-01-01 to 2024-01-07.

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
- Search-derived source candidates: `35`
- Iterative source discovery: `True`
- Iterative search iterations: `2`
- Iterative stop decision: `stop_sufficient`
- Iterative stop reason: `Maximum iterations (2) reached. All planned queries across both iterations have been executed (8 of 10 max total queries used). The search has successfully identified the authoritative source domains and specific dataset candidates across all three primary reporting channels (CDC federal, NYSDOH state, NYC DOHMH city) that are most likely to contain COVID-19 case, death, and hospitalization data for New York for the week of 2024-01-01 to 2024-01-07. No numeric values have been confirmed in snippets (snippets are landing-page metadata only, not row-level data), but the correct source candidates for downstream data extraction have been identified. Further search is unlikely to surface new authoritative sources not already represented in the candidate set, and the iteration and query bounds prohibit additional searches.`
- Source credibility assessed sources: `35`
- Source credibility role counts: `{'collection': 12, 'context': 16, 'excluded': 7}`
- Source identity assessed sources: `35`
- Source identity type counts: `{'state_or_local_public_health_agency': 6, 'official_public_health_agency': 11, 'social_media': 2, 'national_public_health_agency': 10, 'structured_database': 1, 'news_media': 2, 'international_public_health_agency': 1, 'secondary_aggregator': 2}`
- Source identity warning counts: `{'search_provider_not_publisher': 35, 'publisher_from_search_metadata_unverified': 35, 'direct_target_official_fast_path_skips_source_identity': 35, 'actual_publisher_unknown': 17}`
- Source discovery method: `live_search_only`
- Disease relevance target: `COVID-19`
- Disease relevance source status counts: `{'target_disease_match': 25, 'insufficient_text': 6, 'ambiguous_disease': 4}`
- Disease relevance chunk status counts: `{'target_disease_match': 407, 'ambiguous_disease': 87, 'insufficient_text': 1}`
- Disease relevance record status counts: `{}`
- Rejected incompatible record count: `0`
- Final route: `finalize`

## 2.5 Run quality status

- User-facing run status: `COMPLETED WITH NO RECORDS: workflow completed but no records were extracted.`
- Technical execution status: `completed`
- Run quality status: `no_records_extracted`
- Final dataset mode: `task_aware_quality_gated_records`
- Accepted final dataset count: `0`
- Final case dataset count: `0`
- Zero-case statement count: `0`
- Exposure-monitoring record count: `0`
- Surveillance summary record count: `0`
- Outbreak summary record count: `0`
- Context record count: `0`
- Unclassified observation count: `0`
- Observation dataset view counts: `{'final_case_dataset': 0, 'global_outbreak_event_dataset': 0, 'regional_surveillance_dataset': 0, 'country_year_aggregate_dataset': 0, 'official_alert_dataset': 0, 'probable_case_dataset': 0, 'suspected_case_dataset': 0, 'unspecified_case_dataset': 0, 'death_dataset': 0, 'hospitalization_dataset': 0, 'zero_case_statements': 0, 'exposure_monitoring_records': 0, 'surveillance_summary_records': 0, 'outbreak_summary_records': 0, 'context_records': 0, 'non_primary_observations': 0, 'unclassified_observation_records': 0}`
- Pre-quality-gate record count: `0`
- Quarantined record count: `0`
- Pending review record count: `0`
- Non-primary observation count: `0`
- Final dataset post-review count: `0`
- Primary-case dataset status: `unknown_no_claim_outputs`
- Recommended primary dataset message: `No primary case dataset records were accepted; inspect zero-case, exposure-monitoring, context, and other observation views.`
- Primary-case eligible accepted count: `0`
- Corroborated primary case event count: `0`
- Recommended user message: `No reliable task-relevant records were accepted; inspect search, fetch, extraction, and quarantine diagnostics.`

workflow technically completed, but no quality-gated accepted records were produced.
本次 workflow 技术上完成，但没有产生通过质量门的 accepted records。

Workflow technically completed, but no primary case dataset records were accepted. Non-primary observations were preserved separately and should not be read as final epidemiological case data.

## 3. Workflow 运行过程

Graph is executed as a mostly serial workflow. The only conditional branch is after `quality_gate_routing`: the run enters `human_review` when quality or validation checks require review, then still builds the final data package. In this run, the graph route is shown above; validation comparison review flags are reported separately in Section 8.

1. `task_intake_and_scope_planning` - Built CollectionSpec from structured task input.
2. `disease_intelligence_builder` - Built disease intelligence from LLM output (COVID-19).
3. `profile_and_schema_setup` - Built active disease profile, collection schema, and source strategy (COVID-19, generation_method=disease_intelligenc...
4. `executable_source_planning` - Built executable source plan with 10 planned queries; no searches were executed.
5. `query_strategy_builder` - Built 10 direct_collection search queries from the LLM evidence strategy plan.
6. `source_discovery` - Discovered 35 source candidates using live_search_only.
7. `source_dedup_and_registry` - Built source registry with 35 entries (0 duplicates dropped).
8. `source_screening` - Screened 35 sources using deterministic policy.
9. `source_critic_and_uncertainty_routing` - Critic reviewed 35 sources; 31 ready for fetch, 0 deferred, 15 flagged for human review.
10. `content_fetch_and_parse` - Built 31 fetch requests, produced 31 documents (live_fetch_enabled=True, fixture_documents_enabled=False, fixtures_lo...
11. `document_quality_check` - Quality-checked 31 documents: 28 usable, 0 partial, 0 offline stub, 0 parse deferred, 3 unusable.
12. `evidence_chunking_and_data_presence_flagging` - Chunked 28/31 documents into 495 evidence chunks (414 flagged as containing target data).
13. `structured_extraction` - Built 0 raw records (extraction_mode=llm_structured_output, llm_enabled=True).
14. `schema_validation_and_repair` - Validated 0 raw records: 0 validated (0 need review), 0 rejected.
15. `record_normalization` - Normalized 0/0 records (0 need review).
16. `record_linking` - Linked 0/0 normalized records into 0 candidate events.
17. `cross_source_consistency_check` - Checked 0 multi-record events; found 0 new conflicts and 0 validation results (0 events need review).
18. `quality_gate_routing` - Human review disabled; preserving review flags as audit metadata and routing to final_data_package_builder.
19. `final_data_package_builder` - Assembled hardened FinalDataPackage from current state.

## 4. 数据源分工

| Role | Source ID | Publisher / title | Credibility | Final decision | Fetch ready |
|---|---|---|---|---|---|
| context_only | src_search_6815a00063a1 | / Respiratory illnesses continue across New York State Widespread ... | high (0.5479) | include_for_content_fetch | False |
| context_only | src_search_b20ad52ed0ba | World Health Organization / Summary | high (0.4148) | include_for_content_fetch | True |
| context_only | src_search_9993790c8a7a | / COVID-19 pandemic in New York City - Wikipedia | needs_review (0.5551) | needs_human_review | False |
| context_only | src_search_b11655490f96 | / How did COVID-19 affect people in New York? / USAFacts | needs_review (0.5551) | needs_human_review | False |
| context_only | src_search_d5900bb8aa62 | / COVID-19 pandemic in the United States - Wikipedia | needs_review (0.484) | needs_human_review | False |
| context_only | src_search_f1a19efce8d2 | / New York State COVID update on Thursday, Jan. 20 - Facebook | needs_review (0.5551) | needs_human_review | False |
| other | src_search_fc41756dc833 | coronavirus.health.ny.gov / Weekly Hospitalization Summary / Department of Health - COVID-19 | high (0.8759) | include_for_content_fetch | True |
| other | src_search_66002ff28cf6 | coronavirus.health.ny.gov / COVID-19 Data in New York / Department of Health | high (0.8759) | include_for_content_fetch | True |
| other | src_search_af2355dda632 | / COVID-19: Data Trends and Totals - NYC Health | high (0.8639) | include_for_content_fetch | True |
| other | src_search_979be3c147ca | Centers for Disease Control and Prevention / Provisional COVID-19 Mortality Surveillance - CDC | high (0.8048) | include_for_content_fetch | True |
| other | src_search_478ca202141b | / United States COVID - Coronavirus Statistics - Worldometer | medium (0.772) | include_for_content_fetch | True |
| other | src_search_998b5385138b | National Center for Biotechnology Information / COVID-19–Associated Hospitalizations Among U.S. Adults Aged ≥18 Years — COVID-NET, 12 Sta... | high (0.8232) | include_for_content_fetch | True |
| other | src_search_288a7948a301 | Centers for Disease Control and Prevention / Weekly United States COVID-19 Cases and Deaths by State | high (0.8048) | include_for_content_fetch | True |
| other | src_search_d5598f1ff469 | / Respiratory Illness Surveillance Dashboard - ROC HEALTH DATA | excluded (0.6056) | include_for_content_fetch | True |
| other | src_search_34d583acab24 | Centers for Disease Control and Prevention / Surveillance and Data Analytics / Covid - CDC | high (0.8048) | include_for_content_fetch | True |
| other | src_search_68678448bb04 | / New York - COVID-19 Overview - Johns Hopkins | high (0.8522) | include_for_content_fetch | True |
| other | src_search_96c2ddef784f | / GitHub - nytimes/covid-19-data: A repository of data on coronavirus cases and deaths in the U.S. · GitHub | high (0.8522) | include_for_content_fetch | True |
| other | src_search_58fde24d715b | Centers for Disease Control and Prevention / Track Covid-19 in the U.S.: Latest Data and Maps - ny times | high (0.8522) | include_for_content_fetch | True |
| other | src_search_dab3e0ce9e53 | / Communicable Disease Dashboard / Chautauqua County, NY | excluded (0.6607) | include_for_content_fetch | True |
| other | src_search_11a00ee64fc6 | health.ny.gov / Data & Reports | excluded (0.6482) | include_for_content_fetch | True |
| other | src_search_a46f0d5cdbb8 | / Respiratory Illness Data Pages - NYC Health - NYC.gov | excluded (0.6362) | include_for_content_fetch | True |
| other | src_search_650359dcfc71 | / COVID-19 Daily Counts of Cases, Hospitalizations, and Deaths | high (0.7928) | include_for_content_fetch | True |
| other | src_search_0af03f2493e8 | / COVID-19 Daily Counts of Cases, Hospitalizations, and ... | high (0.8056) | include_for_content_fetch | True |
| other | src_search_cee4b8d36efc | Centers for Disease Control and Prevention / Weekly United States COVID-19 Cases and Deaths by County | high (0.8176) | include_for_content_fetch | True |
| other | src_search_a3324b683320 | Centers for Disease Control and Prevention / COVID-19 Case Surveillance Public Use Data - Data.CDC.gov | high (0.8048) | include_for_content_fetch | True |
| other | src_search_bdc592677e02 | Centers for Disease Control and Prevention / COVID-19 Case Surveillance Public Use Data with Geography | high (0.8048) | include_for_content_fetch | True |
| other | src_search_863941370c18 | Centers for Disease Control and Prevention / Provisional COVID-19 Deaths: Focus on Ages 0-18 Years / Data / Centers for Disease Control a... | high (0.8048) | include_for_content_fetch | True |
| other | src_search_11e90007c8a8 | Centers for Disease Control and Prevention / Data / Centers for Disease Control and Prevention | medium (0.5888) | include_for_content_fetch | True |
| other | src_search_b7e5843b362b | Centers for Disease Control and Prevention / Preliminary U.S. COVID-19 Burden Estimates - Data.CDC.gov | high (0.8048) | include_for_content_fetch | True |
| other | src_search_4772064b4e6b | Centers for Disease Control and Prevention / United States COVID-19 Community Levels by County - Data.CDC.gov | high (0.8048) | include_for_content_fetch | True |
| other | src_search_028efcabdb39 | health.data.ny.gov / [PDF] Managed Long-Term Care Performance Data 2024 - Measure ... | excluded (0.6954) | include_for_content_fetch | True |
| other | src_search_ed7cd13f8ae4 | health.data.ny.gov / [PDF] Hospital Inpatient Quality Indicators (SPARCS): Beginning 2009 | excluded (0.677) | include_for_content_fetch | True |
| other | src_search_7acb60a909d9 | health.data.ny.gov / [PDF] Hospital Patient Safety Indicators (SPARCS): Beginning 2009 | excluded (0.677) | include_for_content_fetch | True |
| other | src_search_5ce266c03958 | / COVID / NYC Open Data | high (0.8559) | include_for_content_fetch | True |
| other | src_search_000e4ff17a91 | / GitHub - nychealth/coronavirus-data: This repository contains data on Coronavirus Disease 2019 (COVID-19) in New York City (NYC), from... | high (0.8639) | include_for_content_fetch | True |

## 5. 真实网页抓取结果

- Documents fetched/parsed: `31`
- Search-derived sources selected for fetch: `31`
- Search-derived skipped by reason: `{}`
- Fetch status counts: `fetched=31`
- External fetch enabled: `True`
- Fetch provider counts: `tavily_extract=31`
- External fetch failure counts: `none`
- Selected fetch bucket counts: `target_official_authority=31`
- Parser status counts: `parsed_text=31`
- Parser used counts: `text_parser=31`
- Quality status counts: `unusable=3, usable=28`
- Validation-reserved skipped from fetch: `[]`

| Source ID | Provider | Fetch status | HTTP | Parse | Parser | Quality | Text chars | Tables |
|---|---|---|---|---|---|---|---|---|
| src_search_fc41756dc833 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 2398 | 0 |
| src_search_66002ff28cf6 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 4452 | 0 |
| src_search_af2355dda632 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 2653 | 0 |
| src_search_68678448bb04 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 27054 | 0 |
| src_search_96c2ddef784f | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 26333 | 0 |
| src_search_58fde24d715b | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 15527 | 0 |
| src_search_998b5385138b | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 47446 | 0 |
| src_search_cee4b8d36efc | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 4178 | 0 |
| src_search_288a7948a301 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 3723 | 0 |
| src_search_a3324b683320 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 4178 | 0 |
| src_search_bdc592677e02 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 4178 | 0 |
| src_search_34d583acab24 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 21125 | 0 |
| src_search_863941370c18 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 4178 | 0 |
| src_search_979be3c147ca | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 25842 | 0 |
| src_search_b7e5843b362b | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 4178 | 0 |
| src_search_4772064b4e6b | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 4178 | 0 |
| src_search_478ca202141b | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 38884 | 0 |
| src_search_028efcabdb39 | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 70818 | 0 |
| src_search_ed7cd13f8ae4 | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 155912 | 0 |
| src_search_7acb60a909d9 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 77942 | 0 |
| src_search_d5598f1ff469 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 5563 | 0 |
| src_search_11e90007c8a8 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 4216 | 0 |
| src_search_6815a00063a1 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 20761 | 0 |
| src_search_000e4ff17a91 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 37373 | 0 |
| src_search_5ce266c03958 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 8509 | 0 |
| src_search_0af03f2493e8 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 3913 | 0 |
| src_search_650359dcfc71 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 8743 | 0 |
| src_search_dab3e0ce9e53 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 20276 | 0 |
| src_search_11a00ee64fc6 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 16174 | 0 |
| src_search_a46f0d5cdbb8 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 10480 | 0 |
| src_search_b20ad52ed0ba | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 31095 | 0 |

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
- Stop reason: `Maximum iterations (2) reached. All planned queries across both iterations have been executed (8 of 10 max total queries used). The search has successfully identified the authoritative source domains and specific dataset candidates across all three primary reporting channels (CDC federal, NYSDOH state, NYC DOHMH city) that are most likely to contain COVID-19 case, death, and hospitalization data for New York for the week of 2024-01-01 to 2024-01-07. No numeric values have been confirmed in snippets (snippets are landing-page metadata only, not row-level data), but the correct source candidates for downstream data extraction have been identified. Further search is unlikely to surface new authoritative sources not already represented in the candidate set, and the iteration and query bounds prohibit additional searches.`
- Query source counts: `{'iterative_llm_initial_search_plan': 4, 'iterative_llm_refinement': 4}`
- Iteration query counts: `{'1': 4, '2': 4}`

### 6.2 LLM Source Critic

- Attempted source count: `0`
- Assessed source count: `0`
- Skipped source count: `35`
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
- Assessed source count: `35`
- Final role counts: `collection=12, context=16, excluded=7`
- Risk flag counts: `ambiguous_disease=10, ambiguous_disease_signal_in_source_metadata=4, complete_source_provenance=18, context_or_background_only=10, crowd_edited_content_not_citable_as_authoritative_evidence_quote_source=1, cumulative_vs_incident_count_ambiguity_risk=1, data_derived_from_unverified_editorial_synthesis=1, data_granularity_unlikely_to_support_required_weekly_structured_fields=1, data_signal_in_source_metadata=35, date_in_title_jan_20_outside_target_window_2024_01_01_to_2024_01_07=1, disease_relevance_unclear=6, domain_is_facebook_not_primary_publisher_domain=1, evidence_quote_verbatim_extraction_unlikely_from_social_media_post=1, geographic_granularity_insufficient_for_subnational_new_york_target=1, independence_unclear=4, independence_unclear_collaborative_editing_model=1, independence_unclear_data_at_least_one_step_removed_from_primary=1, independence_unclear_data_lineage_not_transparent=1, local_or_subnational_granularity=10, local_source_matches_task_location=18, location_match_from_planned_query=17, low_authority_for_primary_collection=1, low_authority_for_primary_data_extraction=1, low_authority_for_public_health_data_collection_hierarchy=1, low_authority_relevant_source=4, low_independence_score_0_42_data_likely_not_original=1, machine_readable_or_structured=9, missing_publisher=17, missing_publisher_metadata=1, missing_publisher_no_institutional_accountability=1, missing_publisher_reduces_traceability=1, named_publisher=1, national_or_international_granularity=17, national_or_international_granularity_mismatched_to_state_level_task=1, no_snippet_available_content_unassessable=1, null_publisher_field_unverifiable_from_metadata=1, official_public_health_authority=30, primary_or_authoritative_source=30, reference_list_may_surface_primary_sources_follow_citations=1, screening_and_critic_disagree=6, screening_and_critic_disagree_internal_pipeline_tension=1, screening_and_critic_disagree_warrants_advisory_review=2, secondary_aggregator_not_official_public_health_agency=1, secondary_derivative_source_likely_relays_official_data=1, secondary_news_or_media_source=5, secondary_or_tertiary_source_only=1, secondary_synthesized_source_not_suitable_for_direct_extraction=1, social_media_hosted_content=1, source_disease_relevance:ambiguous_disease=4, source_disease_relevance:insufficient_text=6, source_disease_relevance:target_disease_match=25, source_metadata_matches_requested_disease=25, source_time_matches_requested_window=2, source_type_lowest_priority_tier_in_collection_spec=1, standard_web_page=26, structured_data_source=1, task_location_granularity=8, temporal_granularity_risk_weekly_incident_data_may_not_be_available=1, temporal_mismatch_high_risk_for_direct_collection=1, time_window_match_from_planned_query=33, upstream_source_should_be_independently_verified=1, verbatim_evidence_quote_may_not_be_extractable_from_aggregated_display=1, weekly_incident_granularity_unlikely_available=1, wikipedia_not_authoritative_for_epidemiological_data_collection=1`
- LLM assessed count: `4`
- LLM failure count: `0`
- Needs review count: `4`

### 6.3.5 Source Identity / Publisher Assessment

- Identity assessed source count: `35`
- LLM identity assessed source count: `0`
- Post-fetch identity assessed source count: `31`
- Unknown publisher count: `16`
- Source type counts: `international_public_health_agency=1, national_public_health_agency=10, news_media=2, official_public_health_agency=11, secondary_aggregator=2, social_media=2, state_or_local_public_health_agency=6, structured_database=1`
- Claim support role counts: `corroboration_support=4, insufficient_information=2, primary_case_claim_support=29`
- Fetch use counts: `fetch_for_extraction=33, fetch_only_after_review=2`
- Warning counts: `actual_publisher_unknown=17, direct_target_official_fast_path_skips_source_identity=35, publisher_from_search_metadata_unverified=35, search_provider_not_publisher=35`

### 6.4 LLM Structured Extraction

- Extraction mode: `llm_structured_output`
- Eligible chunk count: `432`
- LLM call count: `30`
- LLM success count: `30`
- LLM error count: `0`
- Raw record count: `0`

## 7. 最终抽取 records

- Normalized record count: `0`
- Run quality status: `no_records_extracted`
- Final dataset mode: `task_aware_quality_gated_records`
- Quality-gated accepted final dataset count: `0`
- Final case dataset count: `0`
- Zero-case statement count: `0`
- Exposure-monitoring record count: `0`
- Surveillance summary record count: `0`
- Outbreak summary record count: `0`
- Context record count: `0`
- Unclassified observation count: `0`
- Observation dataset view counts: `{'final_case_dataset': 0, 'global_outbreak_event_dataset': 0, 'regional_surveillance_dataset': 0, 'country_year_aggregate_dataset': 0, 'official_alert_dataset': 0, 'probable_case_dataset': 0, 'suspected_case_dataset': 0, 'unspecified_case_dataset': 0, 'death_dataset': 0, 'hospitalization_dataset': 0, 'zero_case_statements': 0, 'exposure_monitoring_records': 0, 'surveillance_summary_records': 0, 'outbreak_summary_records': 0, 'context_records': 0, 'non_primary_observations': 0, 'unclassified_observation_records': 0}`
- Pre-quality-gate record count: `0`
- Quarantined record count: `0`
- Pending review record count: `0`
- Non-primary observation count: `0`
- Final dataset post-review count: `0`
- Primary-case dataset status: `unknown_no_claim_outputs`
- Recommended primary dataset message: `No primary case dataset records were accepted; inspect zero-case, exposure-monitoring, context, and other observation views.`
- Primary-case eligible accepted count: `0`
- Corroborated primary case event count: `0`
- Record inclusion status counts: `{}`
- Run quality warnings: `[]`
- Accepted source counts: `none`

No quality-gated records are available to list.
Candidate records, if any, are recorded in the pre-quality, quarantined, and pending-review artifacts.

| Record ID | Date / period | Location | Cases | Deaths | Source | LLM used |
|---|---|---|---|---|---|---|

## 8. Validation 对比

### Claim-level corroboration

- Claim count: `0`
- Claim comparison count: `0`
- Corroborated event count: `0`
- Corroborated primary case event count: `0`
- Observation type counts: `none`
- Corroboration status counts: `none`

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

- Human review item count: `28`
- Evaluation review flag count: `0`
- Anomaly review item count: `0`

| Review ID | Type | Related IDs | Reason |
|---|---|---|---|
| review_source_credibility_src_search_af2355dda632 | source_credibility | src_search_af2355dda632 | missing_publisher |
| review_source_src_search_af2355dda632 | source_screening | src_search_af2355dda632 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_src_search_6815a00063a1 | source_screening | src_search_6815a00063a1 | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_credibility_src_search_478ca202141b | source_credibility | src_search_478ca202141b | missing_publisher |
| review_source_src_search_478ca202141b | source_screening | src_search_478ca202141b | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_68678448bb04 | source_credibility | src_search_68678448bb04 | missing_publisher |
| review_source_src_search_68678448bb04 | source_screening | src_search_68678448bb04 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_96c2ddef784f | source_credibility | src_search_96c2ddef784f | missing_publisher |
| review_source_src_search_96c2ddef784f | source_screening | src_search_96c2ddef784f | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_58fde24d715b | source_credibility | src_search_58fde24d715b | missing_publisher |
| review_source_src_search_58fde24d715b | source_screening | src_search_58fde24d715b | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_650359dcfc71 | source_credibility | src_search_650359dcfc71 | missing_publisher |

## 9.5 Stage 11 anomaly detection and review application

- Anomaly result count: `0`
- Anomaly severity counts: `none`
- Anomaly needs-human-review count: `0`
- Decisions provided: `0`
- Decisions applied: `0`
- Decisions rejected: `0`
- Audit entries: `0`
- Final dataset post-review count: `0`
- Records excluded by review: `0`

| Anomaly ID | Type | Severity | Target | Reason |
|---|---|---|---|---|

| Applied decision | Type | Target | Audit IDs | Reason |
|---|---|---|---|---|

## 10. 输出文件

- Run output directory: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_covid19_new_york_2024_01_01_2024_01_07`
- Collection final dataset: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_covid19_new_york_2024_01_01_2024_01_07\collection\final_dataset.csv`
- Collection final case dataset: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_covid19_new_york_2024_01_01_2024_01_07\collection\final_case_dataset.csv`
- Collection zero-case statements: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_covid19_new_york_2024_01_01_2024_01_07\collection\zero_case_statements.csv`
- Collection exposure-monitoring records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_covid19_new_york_2024_01_01_2024_01_07\collection\exposure_monitoring_records.csv`
- Collection surveillance summaries: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_covid19_new_york_2024_01_01_2024_01_07\collection\surveillance_summary_records.csv`
- Collection outbreak summaries: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_covid19_new_york_2024_01_01_2024_01_07\collection\outbreak_summary_records.csv`
- Collection context records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_covid19_new_york_2024_01_01_2024_01_07\collection\context_records.csv`
- Collection unclassified observations: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_covid19_new_york_2024_01_01_2024_01_07\collection\unclassified_observation_records.csv`
- Collection observation dataset summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_covid19_new_york_2024_01_01_2024_01_07\collection\observation_type_dataset_summary.json`
- Collection pre-quality-gate records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_covid19_new_york_2024_01_01_2024_01_07\collection\final_dataset_pre_quality_gate.csv`
- Collection quarantined records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_covid19_new_york_2024_01_01_2024_01_07\collection\quarantined_records.csv`
- Collection pending review records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_covid19_new_york_2024_01_01_2024_01_07\collection\pending_review_records.csv`
- Collection non-primary observations: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_covid19_new_york_2024_01_01_2024_01_07\collection\non_primary_observations.csv`
- Collection record inclusion decisions: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_covid19_new_york_2024_01_01_2024_01_07\collection\record_inclusion_decisions.json`
- Collection final dataset post-review: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_covid19_new_york_2024_01_01_2024_01_07\collection\final_dataset_post_review.csv`
- Collection anomaly results: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_covid19_new_york_2024_01_01_2024_01_07\collection\anomaly_results.json`
- Collection human review audit trail: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_covid19_new_york_2024_01_01_2024_01_07\collection\human_review_audit_trail.json`
- Collection source registry: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_covid19_new_york_2024_01_01_2024_01_07\collection\source_registry.json`
- Validation mode: `diagnostic_only`
- Validation records source: `state`
- Validation records output: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_covid19_new_york_2024_01_01_2024_01_07\validation\ground_truth_records.csv`
- Inactive validation records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_covid19_new_york_2024_01_01_2024_01_07\validation\inactive_validation_records.csv`
- Validation compatibility summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_covid19_new_york_2024_01_01_2024_01_07\validation\validation_source_compatibility_summary.json`
- Evaluation report CSV: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_covid19_new_york_2024_01_01_2024_01_07\evaluation\evaluation_report.csv`
- Human-readable report: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_covid19_new_york_2024_01_01_2024_01_07\workflow_run_report_chinese.md`

## 11. 当前结论

This workflow run executed the configured data collection workflow through the exported graph and artifact pipeline. The user-facing run status is: COMPLETED WITH NO RECORDS: workflow completed but no records were extracted.
The run completed technically, but it should not be read as a successful data collection result because no quality-gated accepted records were produced.

- Package metadata says LLM used: `True`
- Contains synthetic fixture data: `False`
- Generated at UTC: `2026-06-25T14:14:07.962909+00:00`

## 12. Workflow visualization artifacts

- Workflow visualization index: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_covid19_new_york_2024_01_01_2024_01_07\workflow_visualization\index.html`
- Workflow timeline: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_covid19_new_york_2024_01_01_2024_01_07\workflow_visualization\workflow_timeline.html`
- Evidence flow graph: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_covid19_new_york_2024_01_01_2024_01_07\workflow_visualization\evidence_flow_graph.html`
- Claim comparison cards: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_covid19_new_york_2024_01_01_2024_01_07\workflow_visualization\claim_comparison_cards.html`
- Dataset decision flow: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_covid19_new_york_2024_01_01_2024_01_07\workflow_visualization\dataset_decision_flow.html`
- Human review workflow visualization: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_covid19_new_york_2024_01_01_2024_01_07\workflow_visualization\human_review_workflow.html`
- Visualization summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_covid19_new_york_2024_01_01_2024_01_07\workflow_visualization\workflow_visualization_summary.json`
