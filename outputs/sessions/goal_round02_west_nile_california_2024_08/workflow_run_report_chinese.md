# data collection workflow Run Report

## 1. 输入任务

Collect West Nile virus cases, deaths, dates, locations, source URLs, source types, and evidence quotes for California from 2024-08-01 to 2024-08-31.

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
- Source search executed queries: `7`
- Search-derived source candidates: `41`
- Iterative source discovery: `True`
- Iterative search iterations: `2`
- Iterative stop decision: `stop_sufficient`
- Iterative stop reason: `Max iterations reached (2/2). Sufficient authoritative source candidates identified across state, county, and federal tiers to populate the required target fields. Remaining gaps (August-specific weekly report date anchoring, hospitalizations) are structural limitations of how CDPH publishes data — not addressable by further web search within these bounds.`
- Source credibility assessed sources: `41`
- Source credibility role counts: `{'excluded': 9, 'context': 15, 'collection': 1, 'validation': 11, 'collection_support': 5}`
- Source identity assessed sources: `41`
- Source identity type counts: `{'official_public_health_agency': 21, 'social_media': 7, 'state_or_local_public_health_agency': 1, 'structured_database': 1, 'national_public_health_agency': 3, 'news_media': 6, 'academic_or_peer_reviewed_source': 1, 'secondary_aggregator': 1}`
- Source identity warning counts: `{'search_provider_not_publisher': 41, 'publisher_from_search_metadata_unverified': 41, 'actual_publisher_unknown': 35, 'direct_target_official_fast_path_skips_source_identity': 41}`
- Source discovery method: `live_search_only`
- Disease relevance target: `West Nile virus`
- Disease relevance source status counts: `{'insufficient_text': 17, 'target_disease_match': 7, 'ambiguous_disease': 17}`
- Disease relevance chunk status counts: `{'insufficient_text': 4, 'target_disease_match': 384, 'ambiguous_disease': 137, 'unrelated_disease': 13, 'related_context_only': 2}`
- Disease relevance record status counts: `{'compatible': 104, 'ambiguous_disease': 43, 'incompatible_disease': 2}`
- Rejected incompatible record count: `1`
- Final route: `finalize`

## 2.5 Run quality status

- User-facing run status: `COMPLETED WITH NO PRIMARY CASE DATASET RECORDS: workflow completed, but no primary case records were accepted into final_dataset.`
- Technical execution status: `completed`
- Run quality status: `no_primary_case_dataset_records`
- Final dataset mode: `task_aware_quality_gated_records`
- Accepted final dataset count: `0`
- Final case dataset count: `0`
- Zero-case statement count: `2`
- Exposure-monitoring record count: `0`
- Surveillance summary record count: `0`
- Outbreak summary record count: `0`
- Context record count: `0`
- Unclassified observation count: `2`
- Observation dataset view counts: `{'final_case_dataset': 0, 'global_outbreak_event_dataset': 0, 'regional_surveillance_dataset': 0, 'country_year_aggregate_dataset': 0, 'official_alert_dataset': 0, 'probable_case_dataset': 0, 'suspected_case_dataset': 0, 'unspecified_case_dataset': 0, 'death_dataset': 0, 'hospitalization_dataset': 0, 'zero_case_statements': 2, 'exposure_monitoring_records': 0, 'surveillance_summary_records': 0, 'outbreak_summary_records': 0, 'context_records': 0, 'non_primary_observations': 4, 'unclassified_observation_records': 2}`
- Pre-quality-gate record count: `49`
- Quarantined record count: `0`
- Pending review record count: `49`
- Non-primary observation count: `4`
- Final dataset post-review count: `0`
- Primary-case dataset status: `no_primary_case_dataset_records`
- Recommended primary dataset message: `No primary case dataset records were accepted; inspect zero-case, exposure-monitoring, context, and other observation views.`
- Primary-case eligible accepted count: `0`
- Corroborated primary case event count: `1`
- Recommended user message: `Workflow completed, but no primary case records were accepted; non-primary observations were preserved separately.`

workflow technically completed, but no quality-gated accepted records were produced.
本次 workflow 技术上完成，但没有产生通过质量门的 accepted records。

Workflow technically completed, but no primary case dataset records were accepted. Non-primary observations were preserved separately and should not be read as final epidemiological case data.

## 3. Workflow 运行过程

Graph is executed as a mostly serial workflow. The only conditional branch is after `quality_gate_routing`: the run enters `human_review` when quality or validation checks require review, then still builds the final data package. In this run, the graph route is shown above; validation comparison review flags are reported separately in Section 8.

1. `task_intake_and_scope_planning` - Built CollectionSpec from structured task input.
2. `disease_intelligence_builder` - Built disease intelligence from LLM output (West Nile Virus Disease).
3. `profile_and_schema_setup` - Built active disease profile, collection schema, and source strategy (West Nile Virus Disease, generation_method=dise...
4. `executable_source_planning` - Built executable source plan with 10 planned queries; no searches were executed.
5. `query_strategy_builder` - Built 10 direct_collection search queries from the LLM evidence strategy plan.
6. `source_discovery` - Discovered 41 source candidates using live_search_only.
7. `source_dedup_and_registry` - Built source registry with 41 entries (0 duplicates dropped).
8. `source_screening` - Screened 41 sources using deterministic policy.
9. `source_critic_and_uncertainty_routing` - Critic reviewed 41 sources; 33 ready for fetch, 0 deferred, 20 flagged for human review.
10. `content_fetch_and_parse` - Built 33 fetch requests, produced 33 documents (live_fetch_enabled=True, fixture_documents_enabled=False, fixtures_lo...
11. `document_quality_check` - Quality-checked 33 documents: 29 usable, 1 partial, 0 offline stub, 0 parse deferred, 3 unusable.
12. `evidence_chunking_and_data_presence_flagging` - Chunked 30/33 documents into 540 evidence chunks (494 flagged as containing target data).
13. `structured_extraction` - Built 50 raw records (extraction_mode=llm_structured_output, llm_enabled=True).
14. `schema_validation_and_repair` - Validated 50 raw records: 49 validated (11 need review), 1 rejected.
15. `record_normalization` - Normalized 49/49 records (11 need review).
16. `record_linking` - Linked 49/49 normalized records into 39 candidate events.
17. `cross_source_consistency_check` - Checked 7 multi-record events; found 4 new conflicts and 141 validation results (4 events need review).
18. `quality_gate_routing` - Human review disabled; preserving review flags as audit metadata and routing to final_data_package_builder.
19. `final_data_package_builder` - Assembled hardened FinalDataPackage from current state.

## 4. 数据源分工

| Role | Source ID | Publisher / title | Credibility | Final decision | Fetch ready |
|---|---|---|---|---|---|
| context_only | src_search_53b59cfa3d96 | / CDPH Confirms First Human West Nile Virus Deaths ... | medium (0.7639) | include_for_content_fetch | False |
| context_only | src_search_fbdec1bc87c7 | / Fresno County is among nine counties in California reporting West ... | high (0.5479) | include_for_content_fetch | False |
| context_only | src_search_bd6a1ec7a68e | / West Nile Virus 2024: Cases Are On The Rise, What Experts Say | low (0.3624) | needs_human_review | False |
| context_only | src_search_5d796f40b9b1 | / West Nile Virus Activity 2024 | needs_review (0.3624) | needs_human_review | False |
| context_only | src_search_0d4e7ec87258 | / Health officials report 3 West Nile virus deaths; warn of mosquito ... | needs_review (0.484) | needs_human_review | False |
| context_only | src_search_c95b5eedc56a | CIDRAP / West Nile death reported in California - CIDRAP | high (0.4411) | include_for_content_fetch | True |
| context_only | src_search_03944a8a91ef | / According to the Center for Disease Control, West Nile cases have ... | needs_review (0.344) | needs_human_review | False |
| context_only | src_search_562949a04bda | Centers for Disease Control and Prevention / The CDC has confirmed 174 cases of West Nile this year ... | high (0.4928) | include_for_content_fetch | False |
| context_only | src_search_75f2c3795fd4 | / West Nile death reported in California - Facebook | medium (0.5639) | include_for_content_fetch | False |
| context_only | src_search_a645bfb8a3aa | / A dead bird with West Nile Virus was found in Fresno ... - Facebook | high (0.4768) | include_for_content_fetch | False |
| context_only | src_search_59c1e9439fee | / 2 states report first West Nile deaths of 2024 - WAFB | low (0.5024) | needs_human_review | False |
| context_only | src_search_d13acbb2adbe | / Los Angeles County has reported its first death of 2024 from West ... | low (0.3624) | needs_human_review | False |
| context_only | src_search_c302835aa323 | / West Nile Virus in USA States | low (0.328) | needs_human_review | False |
| context_only | src_search_57a4e03b15a3 | / First Illinois West Nile Virus Death of 2024 is Reported by IDPH in ... | low (0.4712) | needs_human_review | False |
| other | src_search_b9348b953aaa | / WEEKLY UPDATE - California West Nile Virus | excluded (0.6479) | include_for_content_fetch | True |
| other | src_search_ccc444806280 | / WEEKLY UPDATE - California West Nile Virus | excluded (0.6479) | include_for_content_fetch | True |
| other | src_search_a39e4fa28013 | / WEEKLY UPDATE - California West Nile Virus | excluded (0.6479) | include_for_content_fetch | True |
| other | src_search_14d0fc5d0793 | / Westnile.ca.gov / California West Nile Virus Website | excluded (0.6479) | include_for_content_fetch | True |
| other | src_search_fc3322f3069f | / Westnile.ca.gov / California West Nile Virus Website | excluded (0.6479) | include_for_content_fetch | True |
| other | src_search_3e81a7046115 | publichealth.lacounty.gov / Acute Communicable Disease Control | medium (0.5888) | include_for_content_fetch | True |
| other | src_search_20cc0cc9d540 | / 2025 declared West Nile virus (WNV) "outbreak year" | high (0.7928) | include_for_content_fetch | True |
| other | src_search_1ae425b278e3 | National Center for Biotechnology Information / Risk Factors for West Nile Neuroinvasive Disease and Mortality in ... | high (0.784) | include_for_content_fetch | True |
| other | src_search_d879ecf59b5b | Centers for Disease Control and Prevention / Historic Data (1999-2025) / West Nile Virus / CDC | medium (0.6048) | include_for_content_fetch | True |
| other | src_search_75c0cb5029d2 | / West Nile Neuroinvasive Disease and Mortality in the US | medium (0.772) | include_for_content_fetch | True |
| other | src_search_48efdee7f0d3 | / BEACON | medium (0.5768) | include_for_content_fetch | True |
| other | src_search_99932da268a1 | Centers for Disease Control and Prevention / 2024 Mosquito-Borne Disease Year In Review | medium (0.6112) | include_for_content_fetch | True |
| other | src_search_d2d74c964ac6 | Centers for Disease Control and Prevention / Data and Maps for West Nile / West Nile Virus / CDC | medium (0.5888) | include_for_content_fetch | True |
| other | src_search_33137ddb1958 | Centers for Disease Control and Prevention / Current Year Data (2026) / West Nile Virus | medium (0.6048) | include_for_content_fetch | True |
| other | src_search_3bebe5502dfd | / L.A. County reports first West Nile virus death this year - LA Times | excluded (0.6823) | include_for_content_fetch | True |
| other | src_search_2e488c45a73e | / West Nile Virus Activity in California - Nevada County | excluded (0.6479) | include_for_content_fetch | True |
| other | src_search_b05ef00eb3d0 | / West Nile Virus Activity 2026 - Greater Los Angeles County Vector Control District | medium (0.5928) | include_for_content_fetch | True |
| other | src_search_c0d70a141aca | / West Nile virus, spread by mosquitoes, claims a third life in the San ... | excluded (0.5768) | include_for_content_fetch | True |
| other | src_search_3c1199ba7402 | / West Nile Virus - LA West Vector | excluded (0.5768) | include_for_content_fetch | True |
| other | src_search_490621ff6473 | Centers for Disease Control and Prevention / Technical Documentation: West Nile Virus | high (0.5192) | include_for_content_fetch | True |
| other | src_search_e84ec9daa553 | / West Nile virus deaths up by 32% in 2025 / American Medical Association | high (0.7928) | include_for_content_fetch | True |
| other | src_search_f2e10d64654f | / West Nile virus in the United States - Wikipedia | medium (0.5768) | include_for_content_fetch | True |
| other | src_search_7ae413ceb126 | / [PDF] First Human Death Caused by West Nile Virus in Fresno County | high (0.5352) | include_for_content_fetch | True |
| other | src_search_e8849371789f | / [PDF] County of Fresno - Consolidated Mosquito Abatement District | high (0.5008) | include_for_content_fetch | True |
| other | src_search_87c273c59b72 | / First human death caused by West Nile Virus in Fresno County - KBAK | high (0.5928) | include_for_content_fetch | True |
| other | src_search_425783e5bf74 | / Sacramento Co. senior citizen is first West Nile death this year | high (0.5928) | include_for_content_fetch | True |
| other | src_search_d52309fadb48 | / West Nile virus death confirmed in Fresno County, California | high (0.6639) | include_for_content_fetch | True |

## 5. 真实网页抓取结果

- Documents fetched/parsed: `33`
- Search-derived sources selected for fetch: `33`
- Search-derived skipped by reason: `{}`
- Fetch status counts: `fetch_failed=2, fetched=31`
- External fetch enabled: `True`
- Fetch provider counts: `native_requests=3, tavily_extract=30`
- External fetch failure counts: `native_requests=2, tavily_extract=3`
- Selected fetch bucket counts: `target_official_authority=33`
- Parser status counts: `parsed_html=3, parsed_text=30`
- Parser used counts: `html_stdlib_parser=3, text_parser=30`
- Quality status counts: `partial=1, unusable=3, usable=29`
- Validation-reserved skipped from fetch: `[]`

| Source ID | Provider | Fetch status | HTTP | Parse | Parser | Quality | Text chars | Tables |
|---|---|---|---|---|---|---|---|---|
| src_search_20cc0cc9d540 | native_requests | fetched | 200 | parsed_html | html_stdlib_parser | partial | 129 | 0 |
| src_search_53b59cfa3d96 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 9539 | 0 |
| src_search_b9348b953aaa | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 6910 | 0 |
| src_search_ccc444806280 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 4631 | 0 |
| src_search_a39e4fa28013 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 7399 | 0 |
| src_search_14d0fc5d0793 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 10048 | 0 |
| src_search_fc3322f3069f | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 10078 | 0 |
| src_search_3e81a7046115 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 11200 | 0 |
| src_search_e84ec9daa553 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 13660 | 0 |
| src_search_1ae425b278e3 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 61442 | 0 |
| src_search_75c0cb5029d2 | native_requests | fetch_failed | 403 | parsed_html | html_stdlib_parser | unusable | 16 | 0 |
| src_search_99932da268a1 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 16035 | 0 |
| src_search_d879ecf59b5b | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 2251 | 0 |
| src_search_33137ddb1958 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 1581 | 0 |
| src_search_d2d74c964ac6 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 2067 | 0 |
| src_search_48efdee7f0d3 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 12079 | 0 |
| src_search_f2e10d64654f | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 16943 | 0 |
| src_search_490621ff6473 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 16541 | 0 |
| src_search_562949a04bda | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 21353 | 0 |
| src_search_3bebe5502dfd | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 21172 | 0 |
| src_search_d52309fadb48 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 6235 | 0 |
| src_search_2e488c45a73e | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 18714 | 0 |
| src_search_87c273c59b72 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 6230 | 0 |
| src_search_b05ef00eb3d0 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 5173 | 0 |
| src_search_425783e5bf74 | native_requests | fetch_failed | 403 | parsed_html | html_stdlib_parser | unusable | 318 | 0 |
| src_search_c0d70a141aca | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 6248 | 0 |
| src_search_3c1199ba7402 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 6025 | 0 |
| src_search_75f2c3795fd4 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 23597 | 0 |
| src_search_fbdec1bc87c7 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 13181 | 0 |
| src_search_7ae413ceb126 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 2769 | 0 |
| src_search_e8849371789f | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 2972 | 0 |
| src_search_a645bfb8a3aa | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 37078 | 0 |
| src_search_c95b5eedc56a | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 11876 | 0 |

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
- Total queries executed: `7`
- Stop decision: `stop_sufficient`
- Stop reason: `Max iterations reached (2/2). Sufficient authoritative source candidates identified across state, county, and federal tiers to populate the required target fields. Remaining gaps (August-specific weekly report date anchoring, hospitalizations) are structural limitations of how CDPH publishes data — not addressable by further web search within these bounds.`
- Query source counts: `{'iterative_llm_initial_search_plan': 4, 'iterative_llm_refinement': 4}`
- Iteration query counts: `{'1': 4, '2': 4}`

### 6.2 LLM Source Critic

- Attempted source count: `0`
- Assessed source count: `0`
- Skipped source count: `41`
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
- Assessed source count: `41`
- Final role counts: `collection=1, collection_support=5, context=15, excluded=9, validation=11`
- Risk flag counts: `ambiguous_disease=34, ambiguous_disease_signal_in_source_metadata=17, complete_source_provenance=6, consumer_health_explainer_format_not_case_report=1, content_not_machine_readable_or_structured=1, content_subject_to_deletion_or_editing_without_versioning=1, context_or_background_only=7, cumulative_vs_incident_ambiguity_high_for_august_2024_window=1, cumulative_vs_incident_count_ambiguity_high=1, cumulative_vs_incident_count_ambiguity_risk_if_extracted=1, data_signal_in_source_metadata=41, data_signal_present_but_unverifiable_without_content_access=1, disease_relevance_critically_low_score_0.20=1, disease_relevance_score_critically_low_at_0.20=1, disease_relevance_unclear=17, domain_likely_vector_control_district_not_public_health_agency=1, downstream_echo_of_primary_source_cite_cdc_directly=1, extraction_schema_warning_active_hantavirus_template_may_not_be_updated=1, geographic_granularity_unconfirmed_for_california=1, human_case_data_unlikely_primary_source_for_this_domain_type=1, independence_unclear=7, independence_unclear_likely_derivative_of_official_source=1, independence_unclear_possible_cdph_data_republication=1, local_or_subnational_granularity=12, local_source_matches_task_location=12, location_match_from_planned_query=29, low_authority_for_primary_epidemiological_data_collection=1, low_authority_relevant_source=2, low_machine_readability=3, missing_publisher=35, named_publisher=1, national_or_international_granularity=29, national_or_international_granularity_insufficient_for_california_collection=1, national_or_international_granularity_may_not_be_california_specific=1, national_or_international_granularity_may_not_satisfy_subnational_requirement=1, no_primary_surveillance_data_expected=1, no_target_disease_terms_found_in_metadata=2, null_publisher_provenance_gap=1, official_public_health_authority=33, page_title_activity_language_suggests_mosquito_or_environmental_surveillance_not_human_cases=1, pdf_or_report_likely_medium_readability=3, primary_or_authoritative_source=33, publisher_identity_unverified_null_metadata=1, publisher_metadata_null=1, publisher_null_organizational_identity_unconfirmed=1, risk_of_conflating_vector_surveillance_with_human_case_data=1, screening_and_critic_disagree=14, screening_and_critic_disagree_internal_pipeline_misalignment=1, screening_and_critic_disagree_role_hint_overridden=1, secondary_news_or_media_source=9, social_media_platform_domain=1, source_disease_relevance:ambiguous_disease=17, source_disease_relevance:insufficient_text=17, source_disease_relevance:target_disease_match=7, source_metadata_matches_requested_disease=7, source_time_matches_requested_window=9, standard_web_page=38, time_window_and_location_match_from_query_not_confirmed_in_content=1, time_window_match_from_planned_query=32, upstream_primary_source_citation_unverified=1, zero_target_disease_terms_in_metadata=1`
- LLM assessed count: `4`
- LLM failure count: `0`
- Needs review count: `8`

### 6.3.5 Source Identity / Publisher Assessment

- Identity assessed source count: `41`
- LLM identity assessed source count: `0`
- Post-fetch identity assessed source count: `33`
- Unknown publisher count: `32`
- Source type counts: `academic_or_peer_reviewed_source=1, national_public_health_agency=3, news_media=6, official_public_health_agency=21, secondary_aggregator=1, social_media=7, state_or_local_public_health_agency=1, structured_database=1`
- Claim support role counts: `corroboration_support=7, insufficient_information=8, primary_case_claim_support=26`
- Fetch use counts: `fetch_for_extraction=33, fetch_only_after_review=8`
- Warning counts: `actual_publisher_unknown=35, direct_target_official_fast_path_skips_source_identity=41, publisher_from_search_metadata_unverified=41, search_provider_not_publisher=41`

### 6.4 LLM Structured Extraction

- Extraction mode: `llm_structured_output`
- Eligible chunk count: `434`
- LLM call count: `30`
- LLM success count: `30`
- LLM error count: `0`
- Raw record count: `50`

## 7. 最终抽取 records

- Normalized record count: `49`
- Run quality status: `no_primary_case_dataset_records`
- Final dataset mode: `task_aware_quality_gated_records`
- Quality-gated accepted final dataset count: `0`
- Final case dataset count: `0`
- Zero-case statement count: `2`
- Exposure-monitoring record count: `0`
- Surveillance summary record count: `0`
- Outbreak summary record count: `0`
- Context record count: `0`
- Unclassified observation count: `2`
- Observation dataset view counts: `{'final_case_dataset': 0, 'global_outbreak_event_dataset': 0, 'regional_surveillance_dataset': 0, 'country_year_aggregate_dataset': 0, 'official_alert_dataset': 0, 'probable_case_dataset': 0, 'suspected_case_dataset': 0, 'unspecified_case_dataset': 0, 'death_dataset': 0, 'hospitalization_dataset': 0, 'zero_case_statements': 2, 'exposure_monitoring_records': 0, 'surveillance_summary_records': 0, 'outbreak_summary_records': 0, 'context_records': 0, 'non_primary_observations': 4, 'unclassified_observation_records': 2}`
- Pre-quality-gate record count: `49`
- Quarantined record count: `0`
- Pending review record count: `49`
- Non-primary observation count: `4`
- Final dataset post-review count: `0`
- Primary-case dataset status: `no_primary_case_dataset_records`
- Recommended primary dataset message: `No primary case dataset records were accepted; inspect zero-case, exposure-monitoring, context, and other observation views.`
- Primary-case eligible accepted count: `0`
- Corroborated primary case event count: `1`
- Record inclusion status counts: `{'pending_human_review': 49}`
- Run quality warnings: `['no_primary_case_dataset_records']`
- Accepted source counts: `none`

No quality-gated records are available to list.
Candidate records, if any, are recorded in the pre-quality, quarantined, and pending-review artifacts.

| Record ID | Date / period | Location | Cases | Deaths | Source | LLM used |
|---|---|---|---|---|---|---|

## 8. Validation 对比

### Claim-level corroboration

- Claim count: `61`
- Claim comparison count: `1830`
- Corroborated event count: `9`
- Corroborated primary case event count: `1`
- Observation type counts: `ambiguous_public_health_observation=2, confirmed_case_record=1, death_record=20, unspecified_case_record=36, zero_case_statement=2`
- Corroboration status counts: `conflicting_claims=3, corroborated=1, single_source_unverified=5`

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

- Human review item count: `154`
- Evaluation review flag count: `0`
- Anomaly review item count: `20`

| Review ID | Type | Related IDs | Reason |
|---|---|---|---|
| review_source_src_search_53b59cfa3d96 | source_screening | src_search_53b59cfa3d96 | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_credibility_src_search_20cc0cc9d540 | source_credibility | src_search_20cc0cc9d540 | missing_publisher |
| review_source_src_search_20cc0cc9d540 | source_screening | src_search_20cc0cc9d540 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_src_search_fbdec1bc87c7 | source_screening | src_search_fbdec1bc87c7 | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_src_search_bd6a1ec7a68e | source_screening | src_search_bd6a1ec7a68e | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_credibility_src_search_5d796f40b9b1 | source_credibility | src_search_5d796f40b9b1 | The domain glamosquito.org is consistent with a Greater Los Angeles County Vector Control District (GLACVCD) or similar regional mosquito... |
| review_source_src_search_5d796f40b9b1 | source_screening | src_search_5d796f40b9b1 | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_credibility_src_search_0d4e7ec87258 | source_credibility | src_search_0d4e7ec87258 | This source is an ABC News article (abcnews.com) reporting on West Nile virus deaths, discovered via live search. While ABC News is a nat... |
| review_source_src_search_0d4e7ec87258 | source_screening | src_search_0d4e7ec87258 | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_src_search_c95b5eedc56a | source_screening | src_search_c95b5eedc56a | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_credibility_src_search_03944a8a91ef | source_credibility | src_search_03944a8a91ef | This source is a Facebook post from a local TV news station (WTKR3) referencing CDC data on West Nile virus. Several compounding factors... |
| review_source_src_search_03944a8a91ef | source_screening | src_search_03944a8a91ef | Screening and critic disagree on this source; routing to human review for resolution. |

## 9.5 Stage 11 anomaly detection and review application

- Anomaly result count: `28`
- Anomaly severity counts: `high=16, low=8, medium=4`
- Anomaly needs-human-review count: `20`
- Decisions provided: `0`
- Decisions applied: `0`
- Decisions rejected: `0`
- Audit entries: `0`
- Final dataset post-review count: `0`
- Records excluded by review: `0`

| Anomaly ID | Type | Severity | Target | Reason |
|---|---|---|---|---|
| anom_001 | deaths_without_case_reference | low | rec_src_search_7ae413ceb126_002 | deaths present but no comparable case count is available |
| anom_002 | abrupt_spike_simple_threshold | medium | rec_src_search_7ae413ceb126_003 | case count is a simple-threshold spike over prior comparable records |
| anom_003 | deaths_without_case_reference | low | rec_src_search_7ae413ceb126_004 | deaths present but no comparable case count is available |
| anom_004 | deaths_without_case_reference | low | rec_src_search_7ae413ceb126_005 | deaths present but no comparable case count is available |
| anom_005 | deaths_without_case_reference | low | rec_src_search_b9348b953aaa_006 | deaths present but no comparable case count is available |
| anom_006 | deaths_without_case_reference | low | rec_src_search_d52309fadb48_001 | deaths present but no comparable case count is available |
| anom_007 | deaths_without_case_reference | low | rec_src_search_a39e4fa28013_008 | deaths present but no comparable case count is available |
| anom_008 | deaths_without_case_reference | low | rec_src_search_14d0fc5d0793_002 | deaths present but no comparable case count is available |
| anom_009 | deaths_without_case_reference | low | rec_src_search_14d0fc5d0793_003 | deaths present but no comparable case count is available |
| anom_010 | out_of_scope_count_bearing_record | high | event_003 | Stage 10 validation marked record outside requested scope: outside_time_window |
| anom_011 | out_of_scope_count_bearing_record | high | event_003 | Stage 10 validation marked record outside requested scope: outside_time_window |
| anom_012 | out_of_scope_count_bearing_record | high | event_024 | Stage 10 validation marked record outside requested scope: outside_time_window |

| Applied decision | Type | Target | Audit IDs | Reason |
|---|---|---|---|---|

## 10. 输出文件

- Run output directory: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_west_nile_california_2024_08`
- Collection final dataset: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_west_nile_california_2024_08\collection\final_dataset.csv`
- Collection final case dataset: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_west_nile_california_2024_08\collection\final_case_dataset.csv`
- Collection zero-case statements: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_west_nile_california_2024_08\collection\zero_case_statements.csv`
- Collection exposure-monitoring records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_west_nile_california_2024_08\collection\exposure_monitoring_records.csv`
- Collection surveillance summaries: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_west_nile_california_2024_08\collection\surveillance_summary_records.csv`
- Collection outbreak summaries: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_west_nile_california_2024_08\collection\outbreak_summary_records.csv`
- Collection context records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_west_nile_california_2024_08\collection\context_records.csv`
- Collection unclassified observations: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_west_nile_california_2024_08\collection\unclassified_observation_records.csv`
- Collection observation dataset summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_west_nile_california_2024_08\collection\observation_type_dataset_summary.json`
- Collection pre-quality-gate records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_west_nile_california_2024_08\collection\final_dataset_pre_quality_gate.csv`
- Collection quarantined records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_west_nile_california_2024_08\collection\quarantined_records.csv`
- Collection pending review records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_west_nile_california_2024_08\collection\pending_review_records.csv`
- Collection non-primary observations: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_west_nile_california_2024_08\collection\non_primary_observations.csv`
- Collection record inclusion decisions: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_west_nile_california_2024_08\collection\record_inclusion_decisions.json`
- Collection final dataset post-review: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_west_nile_california_2024_08\collection\final_dataset_post_review.csv`
- Collection anomaly results: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_west_nile_california_2024_08\collection\anomaly_results.json`
- Collection human review audit trail: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_west_nile_california_2024_08\collection\human_review_audit_trail.json`
- Collection source registry: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_west_nile_california_2024_08\collection\source_registry.json`
- Validation mode: `diagnostic_only`
- Validation records source: `state`
- Validation records output: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_west_nile_california_2024_08\validation\ground_truth_records.csv`
- Inactive validation records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_west_nile_california_2024_08\validation\inactive_validation_records.csv`
- Validation compatibility summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_west_nile_california_2024_08\validation\validation_source_compatibility_summary.json`
- Evaluation report CSV: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_west_nile_california_2024_08\evaluation\evaluation_report.csv`
- Human-readable report: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_west_nile_california_2024_08\workflow_run_report_chinese.md`

## 11. 当前结论

This workflow run executed the configured data collection workflow through the exported graph and artifact pipeline. The user-facing run status is: COMPLETED WITH NO PRIMARY CASE DATASET RECORDS: workflow completed, but no primary case records were accepted into final_dataset.
The run completed technically, but it should not be read as a successful data collection result because no quality-gated accepted records were produced.

- Package metadata says LLM used: `True`
- Contains synthetic fixture data: `False`
- Generated at UTC: `2026-06-25T15:06:56.786156+00:00`

## 12. Workflow visualization artifacts

- Workflow visualization index: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_west_nile_california_2024_08\workflow_visualization\index.html`
- Workflow timeline: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_west_nile_california_2024_08\workflow_visualization\workflow_timeline.html`
- Evidence flow graph: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_west_nile_california_2024_08\workflow_visualization\evidence_flow_graph.html`
- Claim comparison cards: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_west_nile_california_2024_08\workflow_visualization\claim_comparison_cards.html`
- Dataset decision flow: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_west_nile_california_2024_08\workflow_visualization\dataset_decision_flow.html`
- Human review workflow visualization: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_west_nile_california_2024_08\workflow_visualization\human_review_workflow.html`
- Visualization summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_west_nile_california_2024_08\workflow_visualization\workflow_visualization_summary.json`
