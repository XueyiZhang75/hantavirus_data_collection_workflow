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
- Search-derived source candidates: `41`
- Iterative source discovery: `True`
- Iterative search iterations: `2`
- Iterative stop decision: `stop_sufficient`
- Iterative stop reason: `Maximum iteration limit reached (max_iterations=2) and the two completed iterations have surfaced a sufficient set of authoritative candidate sources covering the primary target fields. Further searching is not permitted within the stated bounds.`
- Source credibility assessed sources: `41`
- Source credibility role counts: `{'excluded': 20, 'context': 17, 'collection_support': 3, 'collection': 1}`
- Source identity assessed sources: `41`
- Source identity type counts: `{'official_public_health_agency': 23, 'national_public_health_agency': 4, 'social_media': 6, 'news_media': 4, 'academic_or_peer_reviewed_source': 1, 'secondary_aggregator': 1, 'structured_database': 2}`
- Source identity warning counts: `{'search_provider_not_publisher': 41, 'publisher_from_search_metadata_unverified': 41, 'actual_publisher_unknown': 34, 'direct_target_official_fast_path_skips_source_identity': 41}`
- Source discovery method: `live_search_only`
- Disease relevance target: `West Nile virus`
- Disease relevance source status counts: `{'insufficient_text': 20, 'ambiguous_disease': 17, 'target_disease_match': 4}`
- Disease relevance chunk status counts: `{'ambiguous_disease': 144, 'target_disease_match': 513, 'related_context_only': 2, 'unrelated_disease': 16}`
- Disease relevance record status counts: `{'ambiguous_disease': 41, 'compatible': 70}`
- Rejected incompatible record count: `0`
- Final route: `finalize`

## 2.5 Run quality status

- User-facing run status: `PARTIAL: accepted records produced, but some records were quarantined.`
- Technical execution status: `completed`
- Run quality status: `partial_with_quarantined_records`
- Final dataset mode: `task_aware_quality_gated_records`
- Accepted final dataset count: `16`
- Final case dataset count: `14`
- Zero-case statement count: `27`
- Exposure-monitoring record count: `0`
- Surveillance summary record count: `0`
- Outbreak summary record count: `0`
- Context record count: `0`
- Unclassified observation count: `2`
- Observation dataset view counts: `{'final_case_dataset': 14, 'global_outbreak_event_dataset': 0, 'regional_surveillance_dataset': 0, 'country_year_aggregate_dataset': 0, 'official_alert_dataset': 0, 'probable_case_dataset': 0, 'suspected_case_dataset': 0, 'unspecified_case_dataset': 14, 'death_dataset': 2, 'hospitalization_dataset': 0, 'zero_case_statements': 27, 'exposure_monitoring_records': 0, 'surveillance_summary_records': 0, 'outbreak_summary_records': 0, 'context_records': 0, 'non_primary_observations': 19, 'unclassified_observation_records': 2}`
- Pre-quality-gate record count: `37`
- Quarantined record count: `11`
- Pending review record count: `10`
- Non-primary observation count: `8`
- Final dataset post-review count: `16`
- Primary-case dataset status: `primary_case_records_present`
- Recommended primary dataset message: `Primary case dataset records are available in final_case_dataset.`
- Primary-case eligible accepted count: `16`
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
6. `source_discovery` - Discovered 41 source candidates using live_search_only.
7. `source_dedup_and_registry` - Built source registry with 41 entries (0 duplicates dropped).
8. `source_screening` - Screened 41 sources using deterministic policy.
9. `source_critic_and_uncertainty_routing` - Critic reviewed 41 sources; 34 ready for fetch, 0 deferred, 16 flagged for human review.
10. `content_fetch_and_parse` - Built 34 fetch requests, produced 34 documents (live_fetch_enabled=True, fixture_documents_enabled=False, fixtures_lo...
11. `document_quality_check` - Quality-checked 34 documents: 30 usable, 0 partial, 0 offline stub, 0 parse deferred, 4 unusable.
12. `evidence_chunking_and_data_presence_flagging` - Chunked 30/34 documents into 675 evidence chunks (608 flagged as containing target data).
13. `structured_extraction` - Built 37 raw records (extraction_mode=llm_structured_output, llm_enabled=True).
14. `schema_validation_and_repair` - Validated 37 raw records: 37 validated (11 need review), 0 rejected.
15. `record_normalization` - Normalized 37/37 records (11 need review).
16. `record_linking` - Linked 37/37 normalized records into 30 candidate events.
17. `cross_source_consistency_check` - Checked 7 multi-record events; found 7 new conflicts and 111 validation results (5 events need review).
18. `quality_gate_routing` - Human review disabled; preserving review flags as audit metadata and routing to final_data_package_builder.
19. `final_data_package_builder` - Assembled hardened FinalDataPackage from current state.

## 4. 数据源分工

| Role | Source ID | Publisher / title | Credibility | Final decision | Fetch ready |
|---|---|---|---|---|---|
| context_only | src_search_7b25eaafb554 | / Public Health has confirmed the first death due to West Nile virus for ... | high (0.5112) | include_for_content_fetch | False |
| context_only | src_search_0d4e7ec87258 | / Health officials report 3 West Nile virus deaths; warn of mosquito ... | needs_review (0.484) | needs_human_review | False |
| context_only | src_search_c95b5eedc56a | CIDRAP / West Nile death reported in California / CIDRAP | high (0.4411) | include_for_content_fetch | True |
| context_only | src_search_bd6a1ec7a68e | / West Nile Virus 2024: Cases Are On The Rise, What Experts Say | needs_review (0.3624) | needs_human_review | False |
| context_only | src_search_08a8384dc2e1 | / Health officials have confirmed the first West Nile virus related death ... | needs_review (0.344) | needs_human_review | False |
| context_only | src_search_03944a8a91ef | / According to the Center for Disease Control, West Nile cases have ... | high (0.4928) | include_for_content_fetch | False |
| context_only | src_search_f859287d8321 | Centers for Disease Control and Prevention / Kern County Public Health reports first human West Nile ... - YouTube | high (0.3314) | include_for_content_fetch | False |
| context_only | src_search_fbdec1bc87c7 | / Fresno County is among nine counties... - ABC30 Action News | high (0.5479) | include_for_content_fetch | False |
| context_only | src_search_72f7f1561150 | / The patient, a resident of... - Inland Valley Daily Bulletin | needs_review (0.328) | needs_human_review | False |
| context_only | src_search_44edf79f1ad4 | / West Nile virus-associated hospitalizations by admission month (A ... | low (0.344) | needs_human_review | False |
| context_only | src_search_f58646b293ec | / 2 people die from West Nile virus in New Jersey, bringing number of ... | low (0.3624) | needs_human_review | False |
| context_only | src_search_1a64fab86f8e | National Center for Biotechnology Information / West Nile Virus Lineage 2 Neuroinvasive Infection Presenting as Intraparenchimal Cerebral... | medium (0.6648) | needs_human_review | False |
| other | src_search_a39e4fa28013 | / [PDF] WEEKLY UPDATE - California West Nile Virus | excluded (0.5719) | include_for_content_fetch | True |
| other | src_search_5d796f40b9b1 | / West Nile Virus Activity 2024 | excluded (0.6112) | include_for_content_fetch | True |
| other | src_search_ccc444806280 | / [PDF] WEEKLY UPDATE - California West Nile Virus | excluded (0.5719) | include_for_content_fetch | True |
| other | src_search_4f8e542dc010 | / West Nile Virus Activity - Alameda County Mosquito Abatement District | excluded (0.5768) | include_for_content_fetch | True |
| other | src_search_c6a2c8c95e83 | / West Nile Virus Data | excluded (0.5768) | include_for_content_fetch | True |
| other | src_search_fc3322f3069f | / California West Nile Virus Website: Westnile.ca.gov | excluded (0.6479) | include_for_content_fetch | True |
| other | src_search_2e488c45a73e | / West Nile Virus Activity in California - Nevada County | excluded (0.6479) | include_for_content_fetch | True |
| other | src_search_33137ddb1958 | Centers for Disease Control and Prevention / Current Year Data (2026) / West Nile Virus - CDC | medium (0.6048) | include_for_content_fetch | True |
| other | src_search_0d3f07c7ed93 | Centers for Disease Control and Prevention / [PDF] West Nile Virus Update | excluded (0.5008) | include_for_content_fetch | True |
| other | src_search_0a4aa71e9362 | Centers for Disease Control and Prevention / [PDF] West Nile Virus Surveillance and Control Guidelines / CDC | medium (0.7472) | include_for_content_fetch | True |
| other | src_search_d879ecf59b5b | Centers for Disease Control and Prevention / Historic Data (1999-2025) / West Nile Virus - CDC | medium (0.6048) | include_for_content_fetch | True |
| other | src_search_d2d74c964ac6 | Centers for Disease Control and Prevention / Data and Maps for West Nile / West Nile Virus / CDC | medium (0.5888) | include_for_content_fetch | True |
| other | src_search_99932da268a1 | Centers for Disease Control and Prevention / 2024 Mosquito-Borne Disease Year In Review | high (0.6112) | include_for_content_fetch | True |
| other | src_search_c302835aa323 | Centers for Disease Control and Prevention / West Nile Virus in USA States - ArcGIS Experience Builder | excluded (0.5768) | include_for_content_fetch | True |
| other | src_search_9c5e68f4bb67 | / West Nile Virus and Other Nationally Notifiable Arboviral Diseases ... | excluded (0.5768) | include_for_content_fetch | True |
| other | src_search_3bebe5502dfd | / L.A. County reports first West Nile virus death this year - LA Times | excluded (0.6823) | include_for_content_fetch | True |
| other | src_search_57a4e03b15a3 | / First Illinois West Nile Virus Death of 2024 is Reported by IDPH in ... | high (0.6112) | include_for_content_fetch | True |
| other | src_search_14d0fc5d0793 | / Westnile.ca.gov / California West Nile Virus Website | excluded (0.6479) | include_for_content_fetch | True |
| other | src_search_b9348b953aaa | / [PDF] WEEKLY UPDATE - California West Nile Virus | excluded (0.5719) | include_for_content_fetch | True |
| other | src_search_be93a6fa0503 | / [PDF] WEEKLY UPDATE - California West Nile Virus | excluded (0.5719) | include_for_content_fetch | True |
| other | src_search_a666cd39412c | / What to know about West Nile Virus as cases increase in Northern ... | excluded (0.6639) | include_for_content_fetch | True |
| other | src_search_5e24365aa18c | / West Nile Fever in 2024: A Persistent Public Health Challenge in the ... | excluded (0.6112) | include_for_content_fetch | True |
| other | src_search_48efdee7f0d3 | / USA reports 1981 West Nile virus (WNV) cases in 2025 ... - BEACON | high (0.7928) | include_for_content_fetch | True |
| other | src_search_f2e10d64654f | / West Nile virus in the United States - Wikipedia | excluded (0.5768) | include_for_content_fetch | True |
| other | src_search_2fc9cc9ad3e4 | / 3 cases of West Nile Virus confirmed in Fresno County - ABC30 | excluded (0.4474) | include_for_content_fetch | True |
| other | src_search_d62c02026783 | / First Human Case of West Nile Virus Confirmed in Kern County This ... | high (0.4474) | include_for_content_fetch | True |
| other | src_search_479cf500244c | / West Nile Virus - dhs.saccounty.net - Sacramento County | high (0.4314) | include_for_content_fetch | True |
| other | src_search_c0d70a141aca | / West Nile virus, spread by mosquitoes, claims a third life in the San Joaquin Valley - The Intersection | excluded (0.4314) | include_for_content_fetch | True |
| other | src_search_a6b527d2a146 | National Center for Biotechnology Information / Characterizing Areas with Increased Burden of West Nile Virus ... | excluded (0.4434) | include_for_content_fetch | True |

## 5. 真实网页抓取结果

- Documents fetched/parsed: `34`
- Search-derived sources selected for fetch: `34`
- Search-derived skipped by reason: `{}`
- Fetch status counts: `fetch_failed=1, fetched=33`
- External fetch enabled: `True`
- Fetch provider counts: `native_requests=1, tavily_extract=33`
- External fetch failure counts: `native_requests=1, tavily_extract=1`
- Selected fetch bucket counts: `target_official_authority=34`
- Parser status counts: `parsed_html=1, parsed_text=33`
- Parser used counts: `html_stdlib_parser=1, text_parser=33`
- Quality status counts: `unusable=4, usable=30`
- Validation-reserved skipped from fetch: `[]`

| Source ID | Provider | Fetch status | HTTP | Parse | Parser | Quality | Text chars | Tables |
|---|---|---|---|---|---|---|---|---|
| src_search_a666cd39412c | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 20773 | 0 |
| src_search_fc3322f3069f | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 10078 | 0 |
| src_search_2e488c45a73e | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 18714 | 0 |
| src_search_5d796f40b9b1 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 6296 | 0 |
| src_search_33137ddb1958 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 1581 | 0 |
| src_search_4f8e542dc010 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 4638 | 0 |
| src_search_c6a2c8c95e83 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 6448 | 0 |
| src_search_a39e4fa28013 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 7399 | 0 |
| src_search_b9348b953aaa | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 6910 | 0 |
| src_search_ccc444806280 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 4631 | 0 |
| src_search_be93a6fa0503 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 24817 | 0 |
| src_search_48efdee7f0d3 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 12079 | 0 |
| src_search_0a4aa71e9362 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 140637 | 0 |
| src_search_5e24365aa18c | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 21948 | 0 |
| src_search_99932da268a1 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 16035 | 0 |
| src_search_d879ecf59b5b | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 2251 | 0 |
| src_search_d2d74c964ac6 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 2067 | 0 |
| src_search_c302835aa323 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 887 | 0 |
| src_search_f2e10d64654f | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 16943 | 0 |
| src_search_9c5e68f4bb67 | native_requests | fetch_failed | 403 | parsed_html | html_stdlib_parser | unusable | 16 | 0 |
| src_search_0d3f07c7ed93 | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 13846 | 0 |
| src_search_03944a8a91ef | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 7130 | 0 |
| src_search_3bebe5502dfd | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 21172 | 0 |
| src_search_14d0fc5d0793 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 10048 | 0 |
| src_search_57a4e03b15a3 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 7769 | 0 |
| src_search_fbdec1bc87c7 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 13181 | 0 |
| src_search_7b25eaafb554 | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 25080 | 0 |
| src_search_2fc9cc9ad3e4 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 7263 | 0 |
| src_search_d62c02026783 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 22303 | 0 |
| src_search_a6b527d2a146 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 64726 | 0 |
| src_search_479cf500244c | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 3455 | 0 |
| src_search_c0d70a141aca | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 6248 | 0 |
| src_search_f859287d8321 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 4194 | 0 |
| src_search_c95b5eedc56a | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 11876 | 0 |

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
- Stop reason: `Maximum iteration limit reached (max_iterations=2) and the two completed iterations have surfaced a sufficient set of authoritative candidate sources covering the primary target fields. Further searching is not permitted within the stated bounds.`
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
- Final role counts: `collection=1, collection_support=3, context=17, excluded=20`
- Risk flag counts: `ambiguous_disease=37, ambiguous_disease_relevance_no_target_terms_found_in_metadata=1, ambiguous_disease_signal_in_source_metadata=17, ambiguous_disease_signal_no_target_disease_terms_found=1, ambiguous_location=6, canonical_url_should_be_newspaper_domain_not_social_media=1, complete_source_provenance=7, context_or_background_only=7, data_figures_if_present_require_primary_source_verification_before_use=1, data_not_extractable_from_social_media_post_directly=1, data_signal_in_source_metadata=41, data_signal_only_in_url_path_not_verified_text=1, data_signal_present_but_unverifiable_without_content_access=1, death_count_in_title_unverified_as_california_august_2024_specific=1, disease_relevance_critically_low=1, disease_relevance_insufficient_zero_terms_detected=1, disease_relevance_unclear=20, facebook_domain_not_citable_for_epidemiological_data=1, geographic_granularity_insufficient_for_subnational_california_collection=1, geographic_granularity_unclear=6, independence_unclear=6, independence_unclear_data_likely_derived_from_primary_sources=1, inherited_task_warning_extraction_record_model_may_still_be_hantavirus_named=1, inherited_task_warning_source_discovery_not_yet_disease_generic=1, local_or_subnational_granularity=11, local_source_matches_task_location=11, location_match_from_planned_query=24, location_relevance_unclear=6, low_authority_domain_for_public_health_data=1, low_authority_relevant_source=1, low_authority_score_0.48=1, low_independence_score_0.42=1, low_independence_score_suggests_aggregated_or_paraphrased_official_data=1, low_machine_readability=6, lowest_priority_source_type_per_collection_spec=1, missing_publisher=34, missing_publisher_weakens_provenance=1, named_publisher=1, national_or_international_granularity=24, national_or_international_granularity_mismatch_for_california_target=1, national_url_path_suggests_non_california_specific_framing=1, null_publisher_field_prevents_authority_verification=1, null_publisher_institutional_identity_unconfirmed=1, null_publisher_unverified_outlet=1, null_snippet_no_extractable_evidence_quote=1, null_snippet_no_extractable_text_available=1, official_public_health_authority=34, pdf_or_report_likely_medium_readability=6, pointer_value_only_underlying_official_source_not_yet_identified=1, possible_misconfigured_search_pipeline_inherited_hantavirus_warnings=1, primary_or_authoritative_source=34, provenance_chain_weak_social_post_to_surveillance_data=1, risk_penalty_nontrivial_0.22=1, screening_and_critic_disagree=12, screening_and_critic_disagree_internal_model_conflict=1, screening_and_critic_disagree_internal_pipeline_inconsistency=1, screening_and_critic_disagree_on_role=1, screening_and_critic_disagree_requires_advisory_review=1, secondary_news_or_media_source=8, social_media_domain_not_official_publication_channel=1, social_media_post_no_archival_stability=1, source_disease_relevance:ambiguous_disease=17, source_disease_relevance:insufficient_text=20, source_disease_relevance:target_disease_match=4, source_metadata_matches_requested_disease=4, source_time_matches_requested_window=9, source_type_mismatch_social_media_tagged_as_news_situation_report=1, standard_web_page=35, time_window_match_from_planned_query=32`
- LLM assessed count: `4`
- LLM failure count: `0`
- Needs review count: `7`

### 6.3.5 Source Identity / Publisher Assessment

- Identity assessed source count: `41`
- LLM identity assessed source count: `0`
- Post-fetch identity assessed source count: `34`
- Unknown publisher count: `30`
- Source type counts: `academic_or_peer_reviewed_source=1, national_public_health_agency=4, news_media=4, official_public_health_agency=23, secondary_aggregator=1, social_media=6, structured_database=2`
- Claim support role counts: `corroboration_support=5, insufficient_information=7, primary_case_claim_support=29`
- Fetch use counts: `fetch_for_extraction=34, fetch_only_after_review=7`
- Warning counts: `actual_publisher_unknown=34, direct_target_official_fast_path_skips_source_identity=41, publisher_from_search_metadata_unverified=41, search_provider_not_publisher=41`

### 6.4 LLM Structured Extraction

- Extraction mode: `llm_structured_output`
- Eligible chunk count: `624`
- LLM call count: `30`
- LLM success count: `30`
- LLM error count: `0`
- Raw record count: `37`

## 7. 最终抽取 records

- Normalized record count: `37`
- Run quality status: `partial_with_quarantined_records`
- Final dataset mode: `task_aware_quality_gated_records`
- Quality-gated accepted final dataset count: `16`
- Final case dataset count: `14`
- Zero-case statement count: `27`
- Exposure-monitoring record count: `0`
- Surveillance summary record count: `0`
- Outbreak summary record count: `0`
- Context record count: `0`
- Unclassified observation count: `2`
- Observation dataset view counts: `{'final_case_dataset': 14, 'global_outbreak_event_dataset': 0, 'regional_surveillance_dataset': 0, 'country_year_aggregate_dataset': 0, 'official_alert_dataset': 0, 'probable_case_dataset': 0, 'suspected_case_dataset': 0, 'unspecified_case_dataset': 14, 'death_dataset': 2, 'hospitalization_dataset': 0, 'zero_case_statements': 27, 'exposure_monitoring_records': 0, 'surveillance_summary_records': 0, 'outbreak_summary_records': 0, 'context_records': 0, 'non_primary_observations': 19, 'unclassified_observation_records': 2}`
- Pre-quality-gate record count: `37`
- Quarantined record count: `11`
- Pending review record count: `10`
- Non-primary observation count: `8`
- Final dataset post-review count: `16`
- Primary-case dataset status: `primary_case_records_present`
- Recommended primary dataset message: `Primary case dataset records are available in final_case_dataset.`
- Primary-case eligible accepted count: `16`
- Corroborated primary case event count: `0`
- Record inclusion status counts: `{'quarantined_zero_case_statement': 4, 'quarantined_outside_scope': 5, 'accepted_with_warnings': 16, 'pending_human_review': 10, 'quarantined_chunk_not_task_relevant': 2}`
- Run quality warnings: `['no_corroborated_primary_case_events']`
- Accepted source counts: `src_search_a39e4fa28013=8, src_search_b9348b953aaa=8`

| Record ID | Date / period | Location | Cases | Deaths | Source | LLM used |
|---|---|---|---|---|---|---|
| rec_src_search_b9348b953aaa_001 | current week | California | 2.0 | none | src_search_b9348b953aaa | True |
| rec_src_search_b9348b953aaa_002 | current week | Fresno, California | 1.0 | none | src_search_b9348b953aaa | True |
| rec_src_search_b9348b953aaa_003 | current week | Yolo, California | 1.0 | none | src_search_b9348b953aaa | True |
| rec_src_search_b9348b953aaa_004 | 2024 | California | 112.0 | none | src_search_b9348b953aaa | True |
| rec_src_search_b9348b953aaa_005 | 2024 | California | 86.0 | none | src_search_b9348b953aaa | True |
| rec_src_search_b9348b953aaa_006 | 2024 | California | none | 11.0 | src_search_b9348b953aaa | True |
| rec_src_search_b9348b953aaa_007 | 2024 | California | 16.0 | none | src_search_b9348b953aaa | True |
| rec_src_search_b9348b953aaa_008 | 2024-08-01 to 2024-08-31 | California | 324.0 | none | src_search_b9348b953aaa | True |
| rec_src_search_a39e4fa28013_001 | 2024-08-01 to 2024-08-31 | California | 9.0 | none | src_search_a39e4fa28013 | True |
| rec_src_search_a39e4fa28013_002 | 2024-08-01 to 2024-08-31 | Kern County, California | 4.0 | none | src_search_a39e4fa28013 | True |
| rec_src_search_a39e4fa28013_003 | 2024-08-01 to 2024-08-31 | Los Angeles County, California | 2.0 | none | src_search_a39e4fa28013 | True |
| rec_src_search_a39e4fa28013_004 | 2024-08-01 to 2024-08-31 | Sacramento County, California | 2.0 | none | src_search_a39e4fa28013 | True |

## 8. Validation 对比

### Claim-level corroboration

- Claim count: `43`
- Claim comparison count: `903`
- Corroborated event count: `9`
- Corroborated primary case event count: `0`
- Observation type counts: `ambiguous_public_health_observation=2, confirmed_case_record=1, death_record=9, unspecified_case_record=25, zero_case_statement=6`
- Corroboration status counts: `conflicting_claims=3, single_source_unverified=6`

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

- Human review item count: `125`
- Evaluation review flag count: `0`
- Anomaly review item count: `15`

| Review ID | Type | Related IDs | Reason |
|---|---|---|---|
| review_source_credibility_src_search_99932da268a1 | source_credibility | src_search_99932da268a1 | missing_publisher |
| review_source_src_search_99932da268a1 | source_screening | src_search_99932da268a1 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_57a4e03b15a3 | source_credibility | src_search_57a4e03b15a3 | missing_publisher |
| review_source_src_search_57a4e03b15a3 | source_screening | src_search_57a4e03b15a3 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_src_search_7b25eaafb554 | source_screening | src_search_7b25eaafb554 | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_credibility_src_search_0d4e7ec87258 | source_credibility | src_search_0d4e7ec87258 | This source is abcnews.com, a major U.S. broadcast news outlet with generally reliable editorial standards, but it is a secondary news/me... |
| review_source_src_search_0d4e7ec87258 | source_screening | src_search_0d4e7ec87258 | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_src_search_c95b5eedc56a | source_screening | src_search_c95b5eedc56a | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_credibility_src_search_bd6a1ec7a68e | source_credibility | src_search_bd6a1ec7a68e | This source is a general-audience consumer news article published on today.com, a mainstream entertainment and lifestyle media outlet. Wh... |
| review_source_src_search_bd6a1ec7a68e | source_screening | src_search_bd6a1ec7a68e | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_credibility_src_search_08a8384dc2e1 | source_credibility | src_search_08a8384dc2e1 | This source is a Facebook post from the account "SYMVCD" (likely Sutter-Yolo Mosquito & Vector Control District, a local California vecto... |
| review_source_src_search_08a8384dc2e1 | source_screening | src_search_08a8384dc2e1 | Screening and critic disagree on this source; routing to human review for resolution. |

## 9.5 Stage 11 anomaly detection and review application

- Anomaly result count: `18`
- Anomaly severity counts: `high=10, low=3, medium=5`
- Anomaly needs-human-review count: `15`
- Decisions provided: `0`
- Decisions applied: `0`
- Decisions rejected: `0`
- Audit entries: `0`
- Final dataset post-review count: `16`
- Records excluded by review: `0`

| Anomaly ID | Type | Severity | Target | Reason |
|---|---|---|---|---|
| anom_001 | abrupt_spike_simple_threshold | medium | rec_src_search_b9348b953aaa_004 | case count is a simple-threshold spike over prior comparable records |
| anom_002 | deaths_without_case_reference | low | rec_src_search_b9348b953aaa_006 | deaths present but no comparable case count is available |
| anom_003 | deaths_without_case_reference | low | rec_src_search_a39e4fa28013_008 | deaths present but no comparable case count is available |
| anom_004 | deaths_without_case_reference | low | rec_src_search_a666cd39412c_003 | deaths present but no comparable case count is available |
| anom_005 | abrupt_spike_simple_threshold | medium | rec_src_search_fc3322f3069f_002 | case count is a simple-threshold spike over prior comparable records |
| anom_006 | out_of_scope_count_bearing_record | high | event_010 | Stage 10 validation marked record outside requested scope: outside_time_window |
| anom_007 | out_of_scope_count_bearing_record | high | event_010 | Stage 10 validation marked record outside requested scope: outside_time_window |
| anom_008 | out_of_scope_count_bearing_record | high | event_009 | Stage 10 validation marked record outside requested scope: outside_time_window |
| anom_009 | validation_conflict_anomaly | high | event_001 | Validation result is a conflict: Sources report different numeric values for the same linked event. |
| anom_010 | validation_conflict_anomaly | high | event_010 | Validation result is a conflict: Sources report different numeric values for the same linked event. |
| anom_011 | validation_conflict_anomaly | high | event_010 | Validation result is a conflict: Sources may use different case definitions or reporting categories. |
| anom_012 | validation_conflict_anomaly | high | event_012 | Validation result is a conflict: Sources report substantially different numeric values for the same linked event. |

| Applied decision | Type | Target | Audit IDs | Reason |
|---|---|---|---|---|

## 10. 输出文件

- Run output directory: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_west_nile_california_2024_08`
- Collection final dataset: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_west_nile_california_2024_08\collection\final_dataset.csv`
- Collection final case dataset: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_west_nile_california_2024_08\collection\final_case_dataset.csv`
- Collection zero-case statements: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_west_nile_california_2024_08\collection\zero_case_statements.csv`
- Collection exposure-monitoring records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_west_nile_california_2024_08\collection\exposure_monitoring_records.csv`
- Collection surveillance summaries: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_west_nile_california_2024_08\collection\surveillance_summary_records.csv`
- Collection outbreak summaries: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_west_nile_california_2024_08\collection\outbreak_summary_records.csv`
- Collection context records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_west_nile_california_2024_08\collection\context_records.csv`
- Collection unclassified observations: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_west_nile_california_2024_08\collection\unclassified_observation_records.csv`
- Collection observation dataset summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_west_nile_california_2024_08\collection\observation_type_dataset_summary.json`
- Collection pre-quality-gate records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_west_nile_california_2024_08\collection\final_dataset_pre_quality_gate.csv`
- Collection quarantined records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_west_nile_california_2024_08\collection\quarantined_records.csv`
- Collection pending review records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_west_nile_california_2024_08\collection\pending_review_records.csv`
- Collection non-primary observations: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_west_nile_california_2024_08\collection\non_primary_observations.csv`
- Collection record inclusion decisions: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_west_nile_california_2024_08\collection\record_inclusion_decisions.json`
- Collection final dataset post-review: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_west_nile_california_2024_08\collection\final_dataset_post_review.csv`
- Collection anomaly results: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_west_nile_california_2024_08\collection\anomaly_results.json`
- Collection human review audit trail: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_west_nile_california_2024_08\collection\human_review_audit_trail.json`
- Collection source registry: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_west_nile_california_2024_08\collection\source_registry.json`
- Validation mode: `diagnostic_only`
- Validation records source: `state`
- Validation records output: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_west_nile_california_2024_08\validation\ground_truth_records.csv`
- Inactive validation records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_west_nile_california_2024_08\validation\inactive_validation_records.csv`
- Validation compatibility summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_west_nile_california_2024_08\validation\validation_source_compatibility_summary.json`
- Evaluation report CSV: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_west_nile_california_2024_08\evaluation\evaluation_report.csv`
- Human-readable report: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_west_nile_california_2024_08\workflow_run_report_chinese.md`

## 11. 当前结论

This workflow run executed the configured data collection workflow through the exported graph and artifact pipeline. The user-facing run status is: PARTIAL: accepted records produced, but some records were quarantined.
The run completed technically and produced quality-gated accepted records in the final dataset.

- Package metadata says LLM used: `True`
- Contains synthetic fixture data: `False`
- Generated at UTC: `2026-06-25T19:48:46.946413+00:00`

## 12. Workflow visualization artifacts

- Workflow visualization index: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_west_nile_california_2024_08\workflow_visualization\index.html`
- Workflow timeline: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_west_nile_california_2024_08\workflow_visualization\workflow_timeline.html`
- Evidence flow graph: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_west_nile_california_2024_08\workflow_visualization\evidence_flow_graph.html`
- Claim comparison cards: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_west_nile_california_2024_08\workflow_visualization\claim_comparison_cards.html`
- Dataset decision flow: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_west_nile_california_2024_08\workflow_visualization\dataset_decision_flow.html`
- Human review workflow visualization: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_west_nile_california_2024_08\workflow_visualization\human_review_workflow.html`
- Visualization summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_west_nile_california_2024_08\workflow_visualization\workflow_visualization_summary.json`
