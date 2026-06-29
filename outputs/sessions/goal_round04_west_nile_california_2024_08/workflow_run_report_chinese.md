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
- Source search executed queries: `8`
- Search-derived source candidates: `36`
- Iterative source discovery: `True`
- Iterative search iterations: `2`
- Iterative stop decision: `stop_limits_reached`
- Iterative stop reason: `max_iterations reached (bound: 2); primary authoritative source candidates (westnile.ca.gov Arbobulletins, CDC historic data, LA County DPH) have been identified across two iterations; further search cannot resolve the remaining time-fit and field-completeness gaps without page fetching, which is outside scope`
- Source credibility assessed sources: `36`
- Source credibility role counts: `{'excluded': 11, 'context': 13, 'validation': 11, 'collection_support': 1}`
- Source identity assessed sources: `36`
- Source identity type counts: `{'official_public_health_agency': 21, 'social_media': 6, 'national_public_health_agency': 2, 'news_media': 5, 'state_or_local_public_health_agency': 2}`
- Source identity warning counts: `{'search_provider_not_publisher': 36, 'publisher_from_search_metadata_unverified': 36, 'actual_publisher_unknown': 32, 'direct_target_official_fast_path_skips_source_identity': 36}`
- Source discovery method: `live_search_only`
- Disease relevance target: `West Nile virus`
- Disease relevance source status counts: `{'insufficient_text': 16, 'ambiguous_disease': 16, 'target_disease_match': 4}`
- Disease relevance chunk status counts: `{'target_disease_match': 332, 'related_context_only': 2, 'ambiguous_disease': 97, 'unrelated_disease': 4, 'insufficient_text': 3}`
- Disease relevance record status counts: `{'ambiguous_disease': 25, 'compatible': 44}`
- Rejected incompatible record count: `0`
- Final route: `finalize`

## 2.5 Run quality status

- User-facing run status: `PARTIAL: accepted records produced, but some records were quarantined.`
- Technical execution status: `completed`
- Run quality status: `partial_with_quarantined_records`
- Final dataset mode: `task_aware_quality_gated_records`
- Accepted final dataset count: `7`
- Final case dataset count: `7`
- Zero-case statement count: `16`
- Exposure-monitoring record count: `0`
- Surveillance summary record count: `0`
- Outbreak summary record count: `0`
- Context record count: `1`
- Unclassified observation count: `0`
- Observation dataset view counts: `{'final_case_dataset': 7, 'global_outbreak_event_dataset': 0, 'regional_surveillance_dataset': 0, 'country_year_aggregate_dataset': 0, 'official_alert_dataset': 0, 'probable_case_dataset': 0, 'suspected_case_dataset': 0, 'unspecified_case_dataset': 7, 'death_dataset': 0, 'hospitalization_dataset': 0, 'zero_case_statements': 16, 'exposure_monitoring_records': 0, 'surveillance_summary_records': 0, 'outbreak_summary_records': 0, 'context_records': 1, 'non_primary_observations': 13, 'unclassified_observation_records': 0}`
- Pre-quality-gate record count: `23`
- Quarantined record count: `11`
- Pending review record count: `5`
- Non-primary observation count: `4`
- Final dataset post-review count: `7`
- Primary-case dataset status: `primary_case_records_present`
- Recommended primary dataset message: `Primary case dataset records are available in final_case_dataset.`
- Primary-case eligible accepted count: `7`
- Corroborated primary case event count: `0`
- Recommended user message: `Review final_dataset and warnings before use.`

Workflow technically completed and produced quality-gated accepted records.

## 3. Workflow 运行过程

Graph is executed as a mostly serial workflow. The only conditional branch is after `quality_gate_routing`: the run enters `human_review` when quality or validation checks require review, then still builds the final data package. In this run, the graph route is shown above; validation comparison review flags are reported separately in Section 8.

1. `task_intake_and_scope_planning` - Built CollectionSpec from structured task input.
2. `disease_intelligence_builder` - Built disease intelligence from LLM output (West Nile Virus Disease).
3. `profile_and_schema_setup` - Built active disease profile, collection schema, and source strategy (West Nile Virus Disease, generation_method=dise...
4. `executable_source_planning` - Built executable source plan with 10 planned queries; no searches were executed.
5. `query_strategy_builder` - Built 10 direct_collection search queries from the LLM evidence strategy plan.
6. `source_discovery` - Discovered 36 source candidates using live_search_only.
7. `source_dedup_and_registry` - Built source registry with 36 entries (0 duplicates dropped).
8. `source_screening` - Screened 36 sources using deterministic policy.
9. `source_critic_and_uncertainty_routing` - Critic reviewed 36 sources; 30 ready for fetch, 0 deferred, 13 flagged for human review.
10. `content_fetch_and_parse` - Built 30 fetch requests, produced 30 documents (live_fetch_enabled=True, fixture_documents_enabled=False, fixtures_lo...
11. `document_quality_check` - Quality-checked 30 documents: 26 usable, 0 partial, 0 offline stub, 0 parse deferred, 4 unusable.
12. `evidence_chunking_and_data_presence_flagging` - Chunked 26/30 documents into 438 evidence chunks (397 flagged as containing target data).
13. `structured_extraction` - Built 23 raw records (extraction_mode=llm_structured_output, llm_enabled=True).
14. `schema_validation_and_repair` - Validated 23 raw records: 23 validated (7 need review), 0 rejected.
15. `record_normalization` - Normalized 23/23 records (7 need review).
16. `record_linking` - Linked 23/23 normalized records into 23 candidate events.
17. `cross_source_consistency_check` - Checked 0 multi-record events; found 0 new conflicts and 69 validation results (0 events need review).
18. `quality_gate_routing` - Human review disabled; preserving review flags as audit metadata and routing to final_data_package_builder.
19. `final_data_package_builder` - Assembled hardened FinalDataPackage from current state.

## 4. 数据源分工

| Role | Source ID | Publisher / title | Credibility | Final decision | Fetch ready |
|---|---|---|---|---|---|
| context_only | src_search_c80ff754ee2c | / Los Angeles County reports first West Nile virus cases of the year | high (0.4928) | include_for_content_fetch | False |
| context_only | src_search_7247debaba21 | / Texas Leads the U.S. in 2024 West Nile Virus Outbreak | low (0.3624) | needs_human_review | False |
| context_only | src_search_bd6a1ec7a68e | / West Nile Virus 2024: Cases Are On The Rise, What Experts Say | needs_review (0.3624) | needs_human_review | False |
| context_only | src_search_abcdf3745880 | / First Human Cases of West Nile Virus Reported in Los Angeles ... | needs_review (0.4528) | needs_human_review | False |
| context_only | src_search_03944a8a91ef | / WTKR News 3 - According to the Center for Disease Control,... | high (0.4928) | include_for_content_fetch | False |
| context_only | src_search_7b25eaafb554 | / Public Health has confirmed the first death due to West Nile virus for ... | high (0.3658) | include_for_content_fetch | False |
| context_only | src_search_dfe2e58d052c | / Public Health is reporting the first West Nile virus death of 2025. The ... | high (0.3474) | include_for_content_fetch | False |
| context_only | src_search_dfab20334768 | / Officials said people planning to spend time outdoors this summer ... | high (0.3314) | include_for_content_fetch | False |
| context_only | src_search_8b3469eb4963 | publichealth.lacounty.gov / First West Nile Virus Death Reported in LA County | high (0.4648) | include_for_content_fetch | True |
| context_only | src_search_72f7f1561150 | / The patient, a resident of the San Fernando Valley, was hospitalized ... | needs_review (0.328) | needs_human_review | False |
| context_only | src_search_44edf79f1ad4 | / West Nile virus-associated hospitalizations by admission month (A ... | low (0.344) | needs_human_review | False |
| context_only | src_search_20cc0cc9d540 | / 2025 declared West Nile virus (WNV) "outbreak year" - BEACON | low (0.484) | needs_human_review | False |
| other | src_search_a39e4fa28013 | / Arbobulletin_2024_29.pdf | excluded (0.5192) | include_for_content_fetch | True |
| other | src_search_ccc444806280 | / Arbobulletin_2024_7.pdf | excluded (0.5192) | include_for_content_fetch | True |
| other | src_search_be93a6fa0503 | / [PDF] WEEKLY UPDATE - California West Nile Virus | excluded (0.5719) | include_for_content_fetch | True |
| other | src_search_2b62f29f59b5 | / Westnile.ca.gov / California West Nile Virus Website | excluded (0.6479) | include_for_content_fetch | True |
| other | src_search_fc3322f3069f | / Westnile.ca.gov / California West Nile Virus Website | excluded (0.6479) | include_for_content_fetch | True |
| other | src_search_b552e0f7c7dd | / West Nile virus activity 2025 - San Gabriel Valley MVCD | excluded (0.5928) | include_for_content_fetch | True |
| other | src_search_33137ddb1958 | Centers for Disease Control and Prevention / Current Year Data (2026) / West Nile Virus / CDC | medium (0.6048) | include_for_content_fetch | True |
| other | src_search_26c03daad21f | Centers for Disease Control and Prevention / West Nile Virus - Antelope Valley Mosquito and Vector Control District | medium (0.5768) | include_for_content_fetch | True |
| other | src_search_0d3f07c7ed93 | Centers for Disease Control and Prevention / West Nile Virus Update | medium (0.5768) | include_for_content_fetch | True |
| other | src_search_490621ff6473 | Centers for Disease Control and Prevention / [PDF] Technical Documentation: West Nile Virus - EPA | high (0.5192) | include_for_content_fetch | True |
| other | src_search_0d4e7ec87258 | / Health officials report 3 West Nile virus deaths; warn of mosquito-spread illnesses - ABC News | high (0.7928) | include_for_content_fetch | True |
| other | src_search_d879ecf59b5b | Centers for Disease Control and Prevention / Historic Data (1999-2025) / West Nile Virus / CDC | medium (0.6048) | include_for_content_fetch | True |
| other | src_search_c302835aa323 | Centers for Disease Control and Prevention / West Nile Virus in USA States | medium (0.5768) | include_for_content_fetch | True |
| other | src_search_48efdee7f0d3 | / BEACON | medium (0.5768) | include_for_content_fetch | True |
| other | src_search_3bebe5502dfd | / L.A. County reports first West Nile virus death this year - Los Angeles Times | excluded (0.6823) | include_for_content_fetch | True |
| other | src_search_5d796f40b9b1 | / West Nile Virus Activity 2024 | excluded (0.6112) | include_for_content_fetch | True |
| other | src_search_57a4e03b15a3 | / First Illinois West Nile Virus Death of 2024 is Reported by IDPH in Lake County | high (0.6112) | include_for_content_fetch | True |
| other | src_search_c6a2c8c95e83 | / West Nile Virus Data / Santa Barbara County, CA - Official Website | excluded (0.5768) | include_for_content_fetch | True |
| other | src_search_2e488c45a73e | / West Nile Virus Activity in California | excluded (0.6479) | include_for_content_fetch | True |
| other | src_search_14d0fc5d0793 | / Westnile.ca.gov / California West Nile Virus Website | excluded (0.6479) | include_for_content_fetch | True |
| other | src_search_5e24365aa18c | / West Nile Fever in 2024: A Persistent Public Health Challenge in the United States | high (0.8112) | include_for_content_fetch | True |
| other | src_search_99932da268a1 | Centers for Disease Control and Prevention / 2024 Mosquito-Borne Disease Year In Review | medium (0.6112) | include_for_content_fetch | True |
| other | src_search_e84ec9daa553 | / West Nile virus deaths up by 32% in 2025 | high (0.7928) | include_for_content_fetch | True |
| other | src_search_3e81a7046115 | publichealth.lacounty.gov / Department of Public Health - Acute Communicable Disease Control | high (0.4434) | include_for_content_fetch | True |

## 5. 真实网页抓取结果

- Documents fetched/parsed: `30`
- Search-derived sources selected for fetch: `30`
- Search-derived skipped by reason: `{}`
- Fetch status counts: `fetched=30`
- External fetch enabled: `True`
- Fetch provider counts: `native_requests=2, tavily_extract=28`
- External fetch failure counts: `tavily_extract=2`
- Selected fetch bucket counts: `target_official_authority=30`
- Parser status counts: `parsed_html=2, parsed_text=28`
- Parser used counts: `html_stdlib_parser=2, text_parser=28`
- Quality status counts: `unusable=4, usable=26`
- Validation-reserved skipped from fetch: `[]`

| Source ID | Provider | Fetch status | HTTP | Parse | Parser | Quality | Text chars | Tables |
|---|---|---|---|---|---|---|---|---|
| src_search_2b62f29f59b5 | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 66523 | 0 |
| src_search_fc3322f3069f | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 10078 | 0 |
| src_search_33137ddb1958 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 1581 | 0 |
| src_search_b552e0f7c7dd | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 17038 | 0 |
| src_search_be93a6fa0503 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 24817 | 0 |
| src_search_a39e4fa28013 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 7399 | 0 |
| src_search_ccc444806280 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 4631 | 0 |
| src_search_c80ff754ee2c | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 848 | 0 |
| src_search_5e24365aa18c | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 21948 | 0 |
| src_search_0d4e7ec87258 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 7034 | 0 |
| src_search_e84ec9daa553 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 13937 | 0 |
| src_search_99932da268a1 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 16035 | 0 |
| src_search_d879ecf59b5b | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 2251 | 0 |
| src_search_26c03daad21f | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 9038 | 0 |
| src_search_0d3f07c7ed93 | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 13846 | 0 |
| src_search_c302835aa323 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 887 | 0 |
| src_search_48efdee7f0d3 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 12079 | 0 |
| src_search_490621ff6473 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 16541 | 0 |
| src_search_03944a8a91ef | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 7130 | 0 |
| src_search_3bebe5502dfd | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 21172 | 0 |
| src_search_2e488c45a73e | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 18714 | 0 |
| src_search_14d0fc5d0793 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 10048 | 0 |
| src_search_5d796f40b9b1 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 6296 | 0 |
| src_search_57a4e03b15a3 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 7769 | 0 |
| src_search_c6a2c8c95e83 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 6448 | 0 |
| src_search_3e81a7046115 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 11200 | 0 |
| src_search_7b25eaafb554 | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 25080 | 0 |
| src_search_dfe2e58d052c | native_requests | fetched | 200 | parsed_html | html_stdlib_parser | usable | 375 | 0 |
| src_search_dfab20334768 | native_requests | fetched | 200 | parsed_html | html_stdlib_parser | usable | 302 | 0 |
| src_search_8b3469eb4963 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 5211 | 0 |

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
- Stop reason: `max_iterations reached (bound: 2); primary authoritative source candidates (westnile.ca.gov Arbobulletins, CDC historic data, LA County DPH) have been identified across two iterations; further search cannot resolve the remaining time-fit and field-completeness gaps without page fetching, which is outside scope`
- Query source counts: `{'iterative_llm_initial_search_plan': 4, 'iterative_llm_refinement': 4}`
- Iteration query counts: `{'1': 4, '2': 4}`

### 6.2 LLM Source Critic

- Attempted source count: `0`
- Assessed source count: `0`
- Skipped source count: `36`
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
- Assessed source count: `36`
- Final role counts: `collection_support=1, context=13, excluded=11, validation=11`
- Risk flag counts: `CRITICAL_year_mismatch: URL and title reference 2025; collection target is August 2024 — source is almost certainly out-of-scope for the target time window=1, ambiguous_disease=32, ambiguous_disease_relevance_score: disease_relevance_score=0.20 conflicts with explicit WNV title mention — likely a metadata/snippet gap artifact, not true irrelevance=1, ambiguous_disease_signal_in_source_metadata=16, ambiguous_disease_signal_no_target_terms_found_in_metadata=1, ambiguous_location=4, complete_source_provenance=4, context_or_background_only=6, context_or_background_only_not_suitable_as_primary_evidence_source=1, data_signal_in_source_metadata=36, disease_relevance_critically_low_no_wnv_terms_detected=1, disease_relevance_unclear=16, extraction_unreliable_without_verified_article_body=1, facebook_post_adds_indirection_from_original_article=1, geographic_granularity_unclear=4, geographic_mismatch_title_references_texas_not_california=1, independence_below_threshold=1, independence_score_below_threshold=1, independence_unclear=5, independence_unclear_possible_content_aggregator=1, local_mad_domain_may_lack_editorial_standards_for_surveillance_reporting=1, local_or_subnational_granularity=6, local_source_matches_task_location=6, location_match_from_planned_query=26, location_relevance_unclear=4, low_authority_relevant_source=1, low_authority_score_0.48_below_primary_source_threshold=1, low_disease_relevance_score_0.20_no_target_terms_confirmed=1, low_disease_relevance_score_in_metadata=1, low_machine_readability=4, lowest_priority_source_type_per_collection_spec=1, missing_publisher=32, missing_publisher: null publisher prevents automated authority chain verification=1, missing_publisher_reduces_provenance_confidence=1, missing_snippet: no snippet available to confirm case counts, dates, or disease term presence in body text=1, national_or_international_granularity=26, national_or_international_granularity_mismatch_for_california_county_scope=1, national_or_international_granularity_not_california_specific=1, null_publisher_reduces_provenance_traceability=1, official_public_health_authority=31, out_of_scope_time_window: do not use for 2024 case data extraction without explicit confirmation of date coverage=1, pdf_or_report_likely_medium_readability=4, pipeline_warning_active: extraction_record_model_still_hantavirus_named — verify schema is updated to WNV before any data entry from this or any source=1, pipeline_warning_active: source_discovery_not_yet_disease_generic — confirm CDPH WNV surveillance pages and ArboNET are in scope; this LA County source does not substitute for state-level CDPH data=1, primary_or_authoritative_source=31, publisher_null_unverified=1, screening_and_critic_disagree=12, screening_and_critic_disagree: conflicting internal flags (primary_or_authoritative_source vs. secondary_news_or_media_source) indicate unresolved scoring disagreement=1, screening_and_critic_disagree_flag_requires_human_adjudication=1, screening_and_critic_disagree_internal_pipeline_conflict=2, secondary_news_or_media_source=7, social_media_platform_not_primary_publication=1, source_disease_relevance:ambiguous_disease=16, source_disease_relevance:insufficient_text=16, source_disease_relevance:target_disease_match=4, source_metadata_matches_requested_disease=4, source_role_context_only_not_suitable_for_primary_data_extraction=1, source_time_matches_requested_window=11, source_type_may_be_misclassified: lacounty.gov domain suggests official public health agency press release or situation report, not generic news/media — reclassification to official_public_health_agency warranted if confirmed=1, standard_web_page=32, time_window_match_from_planned_query=25, title_only_data_signal_no_snippet_or_body_text=1, title_suggests_general_awareness_not_surveillance_data=1, unlikely_to_contain_required_structured_fields=1`
- LLM assessed count: `4`
- LLM failure count: `0`
- Needs review count: `4`

### 6.3.5 Source Identity / Publisher Assessment

- Identity assessed source count: `36`
- LLM identity assessed source count: `0`
- Post-fetch identity assessed source count: `30`
- Unknown publisher count: `27`
- Source type counts: `national_public_health_agency=2, news_media=5, official_public_health_agency=21, social_media=6, state_or_local_public_health_agency=2`
- Claim support role counts: `corroboration_support=5, insufficient_information=6, primary_case_claim_support=25`
- Fetch use counts: `fetch_for_extraction=30, fetch_only_after_review=6`
- Warning counts: `actual_publisher_unknown=32, direct_target_official_fast_path_skips_source_identity=36, publisher_from_search_metadata_unverified=36, search_provider_not_publisher=36`

### 6.4 LLM Structured Extraction

- Extraction mode: `llm_structured_output`
- Eligible chunk count: `411`
- LLM call count: `30`
- LLM success count: `30`
- LLM error count: `0`
- Raw record count: `23`

## 7. 最终抽取 records

- Normalized record count: `23`
- Run quality status: `partial_with_quarantined_records`
- Final dataset mode: `task_aware_quality_gated_records`
- Quality-gated accepted final dataset count: `7`
- Final case dataset count: `7`
- Zero-case statement count: `16`
- Exposure-monitoring record count: `0`
- Surveillance summary record count: `0`
- Outbreak summary record count: `0`
- Context record count: `1`
- Unclassified observation count: `0`
- Observation dataset view counts: `{'final_case_dataset': 7, 'global_outbreak_event_dataset': 0, 'regional_surveillance_dataset': 0, 'country_year_aggregate_dataset': 0, 'official_alert_dataset': 0, 'probable_case_dataset': 0, 'suspected_case_dataset': 0, 'unspecified_case_dataset': 7, 'death_dataset': 0, 'hospitalization_dataset': 0, 'zero_case_statements': 16, 'exposure_monitoring_records': 0, 'surveillance_summary_records': 0, 'outbreak_summary_records': 0, 'context_records': 1, 'non_primary_observations': 13, 'unclassified_observation_records': 0}`
- Pre-quality-gate record count: `23`
- Quarantined record count: `11`
- Pending review record count: `5`
- Non-primary observation count: `4`
- Final dataset post-review count: `7`
- Primary-case dataset status: `primary_case_records_present`
- Recommended primary dataset message: `Primary case dataset records are available in final_case_dataset.`
- Primary-case eligible accepted count: `7`
- Corroborated primary case event count: `0`
- Record inclusion status counts: `{'quarantined_zero_case_statement': 3, 'quarantined_outside_scope': 8, 'accepted_with_warnings': 6, 'accepted_with_review_warning': 1, 'pending_human_review': 5}`
- Run quality warnings: `['no_corroborated_primary_case_events']`
- Accepted source counts: `src_search_a39e4fa28013=2, src_search_be93a6fa0503=5`

| Record ID | Date / period | Location | Cases | Deaths | Source | LLM used |
|---|---|---|---|---|---|---|
| rec_src_search_a39e4fa28013_002 | 2023 to same point as Bulletin #29 | California | 98.0 | none | src_search_a39e4fa28013 | True |
| rec_src_search_a39e4fa28013_003 | Week (current week column) | California | 9.0 | none | src_search_a39e4fa28013 | True |
| rec_src_search_be93a6fa0503_001 | current week | California | 5.0 | none | src_search_be93a6fa0503 | True |
| rec_src_search_be93a6fa0503_002 | current week | Butte County, California | 1.0 | none | src_search_be93a6fa0503 | True |
| rec_src_search_be93a6fa0503_003 | current week | Kern County, California | 3.0 | none | src_search_be93a6fa0503 | True |
| rec_src_search_be93a6fa0503_004 | current week | Tulare County, California | 1.0 | none | src_search_be93a6fa0503 | True |
| rec_src_search_be93a6fa0503_008 | same point in 2024 | California | 27.0 | none | src_search_be93a6fa0503 | True |

## 8. Validation 对比

### Claim-level corroboration

- Claim count: `25`
- Claim comparison count: `300`
- Corroborated event count: `7`
- Corroborated primary case event count: `0`
- Observation type counts: `death_record=4, unspecified_case_record=17, zero_case_statement=4`
- Corroboration status counts: `conflicting_claims=1, single_source_unverified=6`

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

- Human review item count: `90`
- Evaluation review flag count: `0`
- Anomaly review item count: `11`

| Review ID | Type | Related IDs | Reason |
|---|---|---|---|
| review_source_src_search_c80ff754ee2c | source_screening | src_search_c80ff754ee2c | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_credibility_src_search_57a4e03b15a3 | source_credibility | src_search_57a4e03b15a3 | missing_publisher |
| review_source_src_search_57a4e03b15a3 | source_screening | src_search_57a4e03b15a3 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_src_search_7247debaba21 | source_screening | src_search_7247debaba21 | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_credibility_src_search_bd6a1ec7a68e | source_credibility | src_search_bd6a1ec7a68e | This source is a general-audience consumer health news article from today.com (NBC News/TODAY), a mainstream media outlet. While it is ti... |
| review_source_src_search_bd6a1ec7a68e | source_screening | src_search_bd6a1ec7a68e | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_credibility_src_search_abcdf3745880 | source_credibility | src_search_abcdf3745880 | This source is published on lacounty.gov, a high-authority official public health domain (authority_score=0.95), and the title explicitly... |
| review_source_src_search_abcdf3745880 | source_screening | src_search_abcdf3745880 | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_src_search_03944a8a91ef | source_screening | src_search_03944a8a91ef | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_src_search_7b25eaafb554 | source_screening | src_search_7b25eaafb554 | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_src_search_dfe2e58d052c | source_screening | src_search_dfe2e58d052c | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_src_search_dfab20334768 | source_screening | src_search_dfab20334768 | Screening and critic disagree on this source; routing to human review for resolution. |

## 9.5 Stage 11 anomaly detection and review application

- Anomaly result count: `13`
- Anomaly severity counts: `high=10, low=2, medium=1`
- Anomaly needs-human-review count: `11`
- Decisions provided: `0`
- Decisions applied: `0`
- Decisions rejected: `0`
- Audit entries: `0`
- Final dataset post-review count: `7`
- Records excluded by review: `0`

| Anomaly ID | Type | Severity | Target | Reason |
|---|---|---|---|---|
| anom_001 | deaths_without_case_reference | low | rec_src_search_0d4e7ec87258_002 | deaths present but no comparable case count is available |
| anom_002 | deaths_without_case_reference | low | rec_src_search_0d4e7ec87258_003 | deaths present but no comparable case count is available |
| anom_003 | abrupt_spike_simple_threshold | medium | rec_src_search_fc3322f3069f_001 | case count is a simple-threshold spike over prior comparable records |
| anom_004 | out_of_scope_count_bearing_record | high | event_020 | Stage 10 validation marked record outside requested scope: outside_time_window |
| anom_005 | out_of_scope_count_bearing_record | high | event_009 | Stage 10 validation marked record outside requested scope: outside_geography |
| anom_006 | out_of_scope_count_bearing_record | high | event_018 | Stage 10 validation marked record outside requested scope: outside_geography |
| anom_007 | out_of_scope_count_bearing_record | high | event_017 | Stage 10 validation marked record outside requested scope: outside_geography;outside_time_window |
| anom_008 | out_of_scope_count_bearing_record | high | event_019 | Stage 10 validation marked record outside requested scope: insufficient_scope_information;outside_geography |
| anom_009 | out_of_scope_count_bearing_record | high | event_006 | Stage 10 validation marked record outside requested scope: outside_time_window |
| anom_010 | out_of_scope_count_bearing_record | high | event_001 | Stage 10 validation marked record outside requested scope: outside_time_window |
| anom_011 | out_of_scope_count_bearing_record | high | event_003 | Stage 10 validation marked record outside requested scope: outside_time_window |
| anom_012 | out_of_scope_count_bearing_record | high | event_023 | Stage 10 validation marked record outside requested scope: outside_time_window |

| Applied decision | Type | Target | Audit IDs | Reason |
|---|---|---|---|---|

## 10. 输出文件

- Run output directory: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_west_nile_california_2024_08`
- Collection final dataset: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_west_nile_california_2024_08\collection\final_dataset.csv`
- Collection final case dataset: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_west_nile_california_2024_08\collection\final_case_dataset.csv`
- Collection zero-case statements: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_west_nile_california_2024_08\collection\zero_case_statements.csv`
- Collection exposure-monitoring records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_west_nile_california_2024_08\collection\exposure_monitoring_records.csv`
- Collection surveillance summaries: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_west_nile_california_2024_08\collection\surveillance_summary_records.csv`
- Collection outbreak summaries: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_west_nile_california_2024_08\collection\outbreak_summary_records.csv`
- Collection context records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_west_nile_california_2024_08\collection\context_records.csv`
- Collection unclassified observations: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_west_nile_california_2024_08\collection\unclassified_observation_records.csv`
- Collection observation dataset summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_west_nile_california_2024_08\collection\observation_type_dataset_summary.json`
- Collection pre-quality-gate records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_west_nile_california_2024_08\collection\final_dataset_pre_quality_gate.csv`
- Collection quarantined records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_west_nile_california_2024_08\collection\quarantined_records.csv`
- Collection pending review records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_west_nile_california_2024_08\collection\pending_review_records.csv`
- Collection non-primary observations: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_west_nile_california_2024_08\collection\non_primary_observations.csv`
- Collection record inclusion decisions: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_west_nile_california_2024_08\collection\record_inclusion_decisions.json`
- Collection final dataset post-review: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_west_nile_california_2024_08\collection\final_dataset_post_review.csv`
- Collection anomaly results: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_west_nile_california_2024_08\collection\anomaly_results.json`
- Collection human review audit trail: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_west_nile_california_2024_08\collection\human_review_audit_trail.json`
- Collection source registry: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_west_nile_california_2024_08\collection\source_registry.json`
- Validation mode: `diagnostic_only`
- Validation records source: `state`
- Validation records output: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_west_nile_california_2024_08\validation\ground_truth_records.csv`
- Inactive validation records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_west_nile_california_2024_08\validation\inactive_validation_records.csv`
- Validation compatibility summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_west_nile_california_2024_08\validation\validation_source_compatibility_summary.json`
- Evaluation report CSV: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_west_nile_california_2024_08\evaluation\evaluation_report.csv`
- Human-readable report: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_west_nile_california_2024_08\workflow_run_report_chinese.md`

## 11. 当前结论

This workflow run executed the configured data collection workflow through the exported graph and artifact pipeline. The user-facing run status is: PARTIAL: accepted records produced, but some records were quarantined.
The run completed technically and produced quality-gated accepted records in the final dataset.

- Package metadata says LLM used: `True`
- Contains synthetic fixture data: `False`
- Generated at UTC: `2026-06-25T19:07:31.045852+00:00`

## 12. Workflow visualization artifacts

- Workflow visualization index: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_west_nile_california_2024_08\workflow_visualization\index.html`
- Workflow timeline: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_west_nile_california_2024_08\workflow_visualization\workflow_timeline.html`
- Evidence flow graph: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_west_nile_california_2024_08\workflow_visualization\evidence_flow_graph.html`
- Claim comparison cards: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_west_nile_california_2024_08\workflow_visualization\claim_comparison_cards.html`
- Dataset decision flow: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_west_nile_california_2024_08\workflow_visualization\dataset_decision_flow.html`
- Human review workflow visualization: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_west_nile_california_2024_08\workflow_visualization\human_review_workflow.html`
- Visualization summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_west_nile_california_2024_08\workflow_visualization\workflow_visualization_summary.json`
