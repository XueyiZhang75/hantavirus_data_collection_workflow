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
- Search-derived source candidates: `43`
- Iterative source discovery: `True`
- Iterative search iterations: `2`
- Iterative stop decision: `stop_sufficient`
- Iterative stop reason: `Maximum iteration limit reached (2/2). All five August 2024 epidemiological week Arbobulletins (weeks 31–35) have been identified by URL and snippet. Primary source coverage is sufficient for the task's core target fields. Hospitalization data is structurally absent from CDPH Arbobulletins and is unlikely to be surfaced by further web search within the allowed bounds.`
- Source credibility assessed sources: `43`
- Source credibility role counts: `{'context': 14, 'collection': 1, 'excluded': 19, 'collection_support': 1, 'validation': 8}`
- Source identity assessed sources: `43`
- Source identity type counts: `{'official_public_health_agency': 21, 'social_media': 4, 'structured_database': 1, 'national_public_health_agency': 3, 'unknown': 5, 'news_media': 6, 'state_or_local_public_health_agency': 2, 'academic_or_peer_reviewed_source': 1}`
- Source identity warning counts: `{'search_provider_not_publisher': 43, 'publisher_from_search_metadata_unverified': 43, 'actual_publisher_unknown': 36, 'direct_target_official_fast_path_skips_source_identity': 43}`
- Source discovery method: `live_search_only`
- Disease relevance target: `West Nile virus`
- Disease relevance source status counts: `{'insufficient_text': 24, 'target_disease_match': 2, 'ambiguous_disease': 17}`
- Disease relevance chunk status counts: `{'target_disease_match': 344, 'related_context_only': 2, 'ambiguous_disease': 143, 'unrelated_disease': 16}`
- Disease relevance record status counts: `{'ambiguous_disease': 42, 'compatible': 93}`
- Rejected incompatible record count: `0`
- Final route: `finalize`

## 2.5 Run quality status

- User-facing run status: `COMPLETED WITH NO PRIMARY CASE DATASET RECORDS: workflow completed, but no primary case records were accepted into final_dataset.`
- Technical execution status: `completed`
- Run quality status: `no_primary_case_dataset_records`
- Final dataset mode: `task_aware_quality_gated_records`
- Accepted final dataset count: `0`
- Final case dataset count: `0`
- Zero-case statement count: `35`
- Exposure-monitoring record count: `0`
- Surveillance summary record count: `0`
- Outbreak summary record count: `0`
- Context record count: `10`
- Unclassified observation count: `0`
- Observation dataset view counts: `{'final_case_dataset': 0, 'global_outbreak_event_dataset': 0, 'regional_surveillance_dataset': 0, 'country_year_aggregate_dataset': 0, 'official_alert_dataset': 0, 'probable_case_dataset': 0, 'suspected_case_dataset': 0, 'unspecified_case_dataset': 0, 'death_dataset': 0, 'hospitalization_dataset': 0, 'zero_case_statements': 35, 'exposure_monitoring_records': 0, 'surveillance_summary_records': 0, 'outbreak_summary_records': 0, 'context_records': 10, 'non_primary_observations': 35, 'unclassified_observation_records': 0}`
- Pre-quality-gate record count: `45`
- Quarantined record count: `0`
- Pending review record count: `45`
- Non-primary observation count: `7`
- Final dataset post-review count: `0`
- Primary-case dataset status: `no_primary_case_dataset_records`
- Recommended primary dataset message: `No primary case dataset records were accepted; inspect zero-case, exposure-monitoring, context, and other observation views.`
- Primary-case eligible accepted count: `0`
- Corroborated primary case event count: `0`
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
6. `source_discovery` - Discovered 43 source candidates using live_search_only.
7. `source_dedup_and_registry` - Built source registry with 43 entries (0 duplicates dropped).
8. `source_screening` - Screened 43 sources using deterministic policy.
9. `source_critic_and_uncertainty_routing` - Critic reviewed 43 sources; 36 ready for fetch, 0 deferred, 13 flagged for human review.
10. `content_fetch_and_parse` - Built 36 fetch requests, produced 36 documents (live_fetch_enabled=True, fixture_documents_enabled=False, fixtures_lo...
11. `document_quality_check` - Quality-checked 36 documents: 26 usable, 0 partial, 0 offline stub, 0 parse deferred, 10 unusable.
12. `evidence_chunking_and_data_presence_flagging` - Chunked 26/36 documents into 505 evidence chunks (441 flagged as containing target data).
13. `structured_extraction` - Built 45 raw records (extraction_mode=llm_structured_output, llm_enabled=True).
14. `schema_validation_and_repair` - Validated 45 raw records: 45 validated (11 need review), 0 rejected.
15. `record_normalization` - Normalized 45/45 records (11 need review).
16. `record_linking` - Linked 45/45 normalized records into 40 candidate events.
17. `cross_source_consistency_check` - Checked 4 multi-record events; found 1 new conflicts and 130 validation results (1 events need review).
18. `quality_gate_routing` - Human review disabled; preserving review flags as audit metadata and routing to final_data_package_builder.
19. `final_data_package_builder` - Assembled hardened FinalDataPackage from current state.

## 4. 数据源分工

| Role | Source ID | Publisher / title | Credibility | Final decision | Fetch ready |
|---|---|---|---|---|---|
| context_only | src_search_75f2c3795fd4 | / West Nile death reported in California The death, in a county where high numbers of West Nile virus-positive mosquitoes and dead birds... | medium (0.5639) | include_for_content_fetch | False |
| context_only | src_search_c4aae9b8565d | / California on Friday reported the state's first death from the West Nile ... | medium (0.5639) | include_for_content_fetch | False |
| context_only | src_search_d2a24a52e44f | / Public Health Department statement on the year's first human cases ... | needs_review (0.4528) | needs_human_review | False |
| context_only | src_search_5c954f0581ec | / First West Nile Virus Death of 2024 Reported in LA County | needs_review (0.4712) | needs_human_review | False |
| context_only | src_search_7b25eaafb554 | / Public Health has confirmed the first death due to West Nile virus for ... | needs_review (0.4712) | needs_human_review | False |
| context_only | src_search_72cc102cfdf4 | / The West Nile Virus has reared its head in two heavily ... - Facebook | high (0.4768) | include_for_content_fetch | False |
| context_only | src_search_cb36ac8997e4 | / Riverside County Reports First Human Case of West Nile this Year | needs_review (0.344) | needs_human_review | False |
| context_only | src_search_9c58b1b39168 | / California's First West Nile virus death confirmed | low (0.4151) | needs_human_review | False |
| context_only | src_search_c95b5eedc56a | CIDRAP / West Nile death reported in California / CIDRAP | high (0.4411) | include_for_content_fetch | True |
| context_only | src_search_57a4e03b15a3 | / First Illinois West Nile Virus Death of 2024 is Reported by IDPH in Lake County | low (0.4712) | needs_human_review | False |
| context_only | src_search_4f8e542dc010 | / West Nile Virus Activity - Alameda County Mosquito Abatement District | low (0.328) | needs_human_review | False |
| other | src_search_26c03daad21f | Centers for Disease Control and Prevention / West Nile Virus - Antelope Valley Mosquito and Vector Control District | medium (0.5768) | include_for_content_fetch | True |
| other | src_search_0d4e7ec87258 | / Health officials report 3 West Nile virus deaths; warn of mosquito ... | high (0.7928) | include_for_content_fetch | True |
| other | src_search_164bef3ca516 | / Placer County confirms first West Nile virus death of season | excluded (0.5928) | include_for_content_fetch | True |
| other | src_search_fc3322f3069f | / California West Nile Virus Website: Westnile.ca.gov | excluded (0.6479) | include_for_content_fetch | True |
| other | src_search_14d0fc5d0793 | / Westnile.ca.gov / California West Nile Virus Website | excluded (0.6479) | include_for_content_fetch | True |
| other | src_search_bb741f174261 | National Center for Biotechnology Information / West Nile Virus (Orthoflavivirus nilense) RNA concentrations in ... | excluded (0.5888) | include_for_content_fetch | True |
| other | src_search_d879ecf59b5b | Centers for Disease Control and Prevention / Historic Data (1999-2025) / West Nile Virus - CDC | medium (0.6048) | include_for_content_fetch | True |
| other | src_search_a39e4fa28013 | / Arbobulletin_2024_29.pdf | excluded (0.5192) | include_for_content_fetch | True |
| other | src_search_b9348b953aaa | / Arbobulletin_2024_32.pdf | excluded (0.5192) | include_for_content_fetch | True |
| other | src_search_5d796f40b9b1 | / West Nile Virus Activity 2024 | excluded (0.6112) | include_for_content_fetch | True |
| other | src_search_2e488c45a73e | / West Nile Virus Activity in California | excluded (0.6479) | include_for_content_fetch | True |
| other | src_search_99932da268a1 | Centers for Disease Control and Prevention / 2024 Mosquito-Borne Disease Year In Review | high (0.6112) | include_for_content_fetch | True |
| other | src_search_67a72fbb98c5 | / West Nile Virus Information - Placer Mosquito Vector Control District | medium (0.5768) | include_for_content_fetch | True |
| other | src_search_0d3f07c7ed93 | Centers for Disease Control and Prevention / West Nile Virus Update | medium (0.5896) | include_for_content_fetch | True |
| other | src_search_5e24365aa18c | / West Nile Fever in 2024: A Persistent Public Health Challenge in the ... | medium (0.624) | include_for_content_fetch | True |
| other | src_search_c302835aa323 | Centers for Disease Control and Prevention / West Nile Virus in USA States - ArcGIS Experience Builder | high (0.5288) | include_for_content_fetch | True |
| other | src_search_33137ddb1958 | Centers for Disease Control and Prevention / Current Year Data (2026) / West Nile Virus | medium (0.6176) | include_for_content_fetch | True |
| other | src_search_d2d74c964ac6 | Centers for Disease Control and Prevention / Data and Maps for West Nile - CDC | medium (0.6016) | include_for_content_fetch | True |
| other | src_search_e84ec9daa553 | / West Nile virus deaths up by 32% in 2025 / American Medical Association | medium (0.7448) | include_for_content_fetch | True |
| other | src_search_ddb9f068e5b4 | / [PDF] WEEKLY UPDATE - California West Nile Virus | excluded (0.5719) | include_for_content_fetch | True |
| other | src_search_1901d64d67f4 | / [PDF] WEEKLY UPDATE - California West Nile Virus | excluded (0.5719) | include_for_content_fetch | True |
| other | src_search_44f369c89252 | / [PDF] WEEKLY UPDATE - California West Nile Virus | excluded (0.5719) | include_for_content_fetch | True |
| other | src_search_6b6518ebb14c | / [PDF] WEEKLY UPDATE - California West Nile Virus | excluded (0.5719) | include_for_content_fetch | True |
| other | src_search_f45924fda44f | / [PDF] WEEKLY UPDATE - California West Nile Virus | excluded (0.5719) | include_for_content_fetch | True |
| other | src_search_79b452c2acfa | / [PDF] WEEKLY UPDATE - California West Nile Virus Website | excluded (0.5719) | include_for_content_fetch | True |
| other | src_search_257153519fda | / [PDF] WEEKLY UPDATE - California West Nile Virus | excluded (0.5719) | include_for_content_fetch | True |
| other | src_search_5a1a77be26b3 | / [PDF] WEEKLY UPDATE - California West Nile Virus | excluded (0.5719) | include_for_content_fetch | True |
| other | src_search_e43a4ee8bb58 | publichealth.santaclaracounty.gov / Public Health Department statement on the year's first human cases ... | excluded (0.6048) | include_for_content_fetch | True |
| other | src_search_c0d70a141aca | / West Nile virus, spread by mosquitoes, claims a third life in the San ... | excluded (0.5768) | include_for_content_fetch | True |
| other | src_search_2b62f29f59b5 | / Westnile.ca.gov / California West Nile Virus Website | excluded (0.6479) | include_for_content_fetch | True |
| other | src_search_29301bcfe202 | Centers for Disease Control and Prevention / West Nile Virus Maps Show Cases in US This Year - Newsweek | high (0.5048) | include_for_content_fetch | True |
| other | src_search_5beb758bea7f | doh.wa.gov / West Nile Virus Data / Washington State Department of Health | medium (0.6016) | include_for_content_fetch | True |

## 5. 真实网页抓取结果

- Documents fetched/parsed: `36`
- Search-derived sources selected for fetch: `36`
- Search-derived skipped by reason: `{}`
- Fetch status counts: `fetch_failed=1, fetched=35`
- External fetch enabled: `True`
- Fetch provider counts: `native_requests=1, tavily_extract=35`
- External fetch failure counts: `native_requests=1, tavily_extract=1`
- Selected fetch bucket counts: `target_official_authority=36`
- Parser status counts: `parsed_html=1, parsed_text=35`
- Parser used counts: `html_stdlib_parser=1, text_parser=35`
- Quality status counts: `unusable=10, usable=26`
- Validation-reserved skipped from fetch: `[]`

| Source ID | Provider | Fetch status | HTTP | Parse | Parser | Quality | Text chars | Tables |
|---|---|---|---|---|---|---|---|---|
| src_search_0d4e7ec87258 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 7034 | 0 |
| src_search_fc3322f3069f | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 10078 | 0 |
| src_search_14d0fc5d0793 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 10048 | 0 |
| src_search_d879ecf59b5b | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 2251 | 0 |
| src_search_164bef3ca516 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 2988 | 0 |
| src_search_bb741f174261 | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 67201 | 0 |
| src_search_26c03daad21f | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 9038 | 0 |
| src_search_ddb9f068e5b4 | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 18321 | 0 |
| src_search_1901d64d67f4 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 25005 | 0 |
| src_search_44f369c89252 | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 25777 | 0 |
| src_search_6b6518ebb14c | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 20845 | 0 |
| src_search_f45924fda44f | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 24857 | 0 |
| src_search_79b452c2acfa | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 20432 | 0 |
| src_search_257153519fda | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 22109 | 0 |
| src_search_5a1a77be26b3 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 51649 | 0 |
| src_search_75f2c3795fd4 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 23597 | 0 |
| src_search_2b62f29f59b5 | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 66523 | 0 |
| src_search_2e488c45a73e | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 18714 | 0 |
| src_search_5d796f40b9b1 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 6296 | 0 |
| src_search_99932da268a1 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 16035 | 0 |
| src_search_e43a4ee8bb58 | native_requests | fetch_failed | 403 | parsed_html | html_stdlib_parser | unusable | 870 | 0 |
| src_search_c0d70a141aca | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 6248 | 0 |
| src_search_67a72fbb98c5 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 2979 | 0 |
| src_search_c4aae9b8565d | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 11240 | 0 |
| src_search_a39e4fa28013 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 7399 | 0 |
| src_search_b9348b953aaa | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 6910 | 0 |
| src_search_72cc102cfdf4 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 14746 | 0 |
| src_search_e84ec9daa553 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 13937 | 0 |
| src_search_5e24365aa18c | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 21948 | 0 |
| src_search_33137ddb1958 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 1581 | 0 |
| src_search_5beb758bea7f | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 5396 | 0 |
| src_search_d2d74c964ac6 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 2067 | 0 |
| src_search_0d3f07c7ed93 | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 13846 | 0 |
| src_search_c302835aa323 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 887 | 0 |
| src_search_29301bcfe202 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 3914 | 0 |
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
- Stop reason: `Maximum iteration limit reached (2/2). All five August 2024 epidemiological week Arbobulletins (weeks 31–35) have been identified by URL and snippet. Primary source coverage is sufficient for the task's core target fields. Hospitalization data is structurally absent from CDPH Arbobulletins and is unlikely to be surfaced by further web search within the allowed bounds.`
- Query source counts: `{'iterative_llm_initial_search_plan': 4, 'iterative_llm_refinement': 4}`
- Iteration query counts: `{'1': 4, '2': 4}`

### 6.2 LLM Source Critic

- Attempted source count: `0`
- Assessed source count: `0`
- Skipped source count: `43`
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
- Assessed source count: `43`
- Final role counts: `collection=1, collection_support=1, context=14, excluded=19, validation=8`
- Risk flag counts: `access_restriction_risk_login_wall_or_deletion=1, ambiguous_disease=41, ambiguous_disease_signal_in_source_metadata=17, complete_source_provenance=7, context_or_background_only=5, contradictory_risk_flags:official_public_health_authority_and_secondary_news_or_media_source_cannot_both_apply=1, contradictory_risk_flags_official_authority_and_secondary_media_simultaneously_assigned=1, data_granularity_insufficient_for_required_fields=1, data_signal_in_source_metadata=43, deterministic_disease_relevance_score_anomaly_vs_title_content=1, disease_relevance_score_is_artifact_of_null_snippet_not_true_irrelevance=1, disease_relevance_score_likely_underestimated_by_pipeline=1, disease_relevance_score_may_be_underestimated:title_contains_explicit_wnv_human_case_reference=1, disease_relevance_unclear=24, domain_suggests_official_county_health_agency_unconfirmed=1, extraction_schema_miscalibration_risk_hantavirus_named_model=1, first_human_case_language_suggests_low_case_count_verify_completeness_for_august_window=1, geographic_granularity_flag_misfiring:county_level_source_flagged_as_national_or_international_granularity=1, independence_unclear=6, local_or_subnational_granularity=16, local_source_matches_task_location=16, location_match_from_planned_query=27, low_machine_readability=10, machine_readable_or_structured=8, missing_publisher=36, missing_publisher_field_despite_known_official_domain=1, missing_publisher_metadata=1, missing_snippet:disease_relevance_scoring_may_be_based_on_incomplete_metadata=1, named_publisher=1, national_or_international_granularity=27, official_account_on_non_official_platform=1, official_public_health_authority=36, page_content_unverified_due_to_null_snippet=1, pdf_or_report_likely_medium_readability=10, post_may_reference_upstream_primary_source_not_yet_collected=1, primary_or_authoritative_source=36, provisional_data_risk_early_season_report=1, publisher_field_missing_suppressing_authority_score=1, report_date_not_confirmed_within_2024_08_01_to_2024_08_31_window=1, role_downgrade_may_be_unwarranted:collection_support_or_collection_primary_more_appropriate_than_context=1, role_downgrade_to_context_may_be_incorrect_given_direct_death_report_in_title=1, role_may_be_undersold_if_extractable_required_fields_present=1, screening_and_critic_disagree=11, screening_and_critic_disagree:internal_deterministic_conflict_unresolved=1, screening_and_critic_disagree_flag_requires_human_adjudication=1, screening_and_critic_disagree_flag_unresolved=1, screening_and_critic_disagree_on_source_type=1, secondary_news_or_media_source=9, social_media_platform_instability=1, source_disease_relevance:ambiguous_disease=17, source_disease_relevance:insufficient_text=24, source_disease_relevance:target_disease_match=2, source_metadata_matches_requested_disease=2, source_time_matches_requested_window=8, source_type_likely_misclassified:official_phd_statement_tagged_as_news_and_situation_report=1, source_type_likely_mislabeled_as_news_should_be_official_press_release=1, source_type_may_be_misclassified_as_news_if_official_ruhs_release=1, standard_web_page=25, structured_data_source=3, task_input_warning_source_discovery_not_yet_disease_generic_may_have_caused_term_match_failure=1, time_window_match_from_planned_query=35, title_explicitly_names_target_disease_and_death_event_contradicting_low_disease_score=1, url_uses_http_not_https_verify_accessibility_and_redirect_behavior=1`
- LLM assessed count: `4`
- LLM failure count: `0`
- Needs review count: `5`

### 6.3.5 Source Identity / Publisher Assessment

- Identity assessed source count: `43`
- LLM identity assessed source count: `0`
- Post-fetch identity assessed source count: `36`
- Unknown publisher count: `31`
- Source type counts: `academic_or_peer_reviewed_source=1, national_public_health_agency=3, news_media=6, official_public_health_agency=21, social_media=4, state_or_local_public_health_agency=2, structured_database=1, unknown=5`
- Claim support role counts: `context_only=8, corroboration_support=6, insufficient_information=10, primary_case_claim_support=19`
- Fetch use counts: `fetch_for_context=8, fetch_for_extraction=25, fetch_only_after_review=10`
- Warning counts: `actual_publisher_unknown=36, direct_target_official_fast_path_skips_source_identity=43, publisher_from_search_metadata_unverified=43, search_provider_not_publisher=43`

### 6.4 LLM Structured Extraction

- Extraction mode: `llm_structured_output`
- Eligible chunk count: `421`
- LLM call count: `30`
- LLM success count: `30`
- LLM error count: `0`
- Raw record count: `45`

## 7. 最终抽取 records

- Normalized record count: `45`
- Run quality status: `no_primary_case_dataset_records`
- Final dataset mode: `task_aware_quality_gated_records`
- Quality-gated accepted final dataset count: `0`
- Final case dataset count: `0`
- Zero-case statement count: `35`
- Exposure-monitoring record count: `0`
- Surveillance summary record count: `0`
- Outbreak summary record count: `0`
- Context record count: `10`
- Unclassified observation count: `0`
- Observation dataset view counts: `{'final_case_dataset': 0, 'global_outbreak_event_dataset': 0, 'regional_surveillance_dataset': 0, 'country_year_aggregate_dataset': 0, 'official_alert_dataset': 0, 'probable_case_dataset': 0, 'suspected_case_dataset': 0, 'unspecified_case_dataset': 0, 'death_dataset': 0, 'hospitalization_dataset': 0, 'zero_case_statements': 35, 'exposure_monitoring_records': 0, 'surveillance_summary_records': 0, 'outbreak_summary_records': 0, 'context_records': 10, 'non_primary_observations': 35, 'unclassified_observation_records': 0}`
- Pre-quality-gate record count: `45`
- Quarantined record count: `0`
- Pending review record count: `45`
- Non-primary observation count: `7`
- Final dataset post-review count: `0`
- Primary-case dataset status: `no_primary_case_dataset_records`
- Recommended primary dataset message: `No primary case dataset records were accepted; inspect zero-case, exposure-monitoring, context, and other observation views.`
- Primary-case eligible accepted count: `0`
- Corroborated primary case event count: `0`
- Record inclusion status counts: `{'pending_human_review': 45}`
- Run quality warnings: `['no_primary_case_dataset_records', 'no_corroborated_primary_case_events']`
- Accepted source counts: `none`

No quality-gated records are available to list.
Candidate records, if any, are recorded in the pre-quality, quarantined, and pending-review artifacts.

| Record ID | Date / period | Location | Cases | Deaths | Source | LLM used |
|---|---|---|---|---|---|---|

## 8. Validation 对比

### Claim-level corroboration

- Claim count: `57`
- Claim comparison count: `1596`
- Corroborated event count: `9`
- Corroborated primary case event count: `0`
- Observation type counts: `confirmed_case_record=3, death_record=15, unspecified_case_record=30, zero_case_statement=9`
- Corroboration status counts: `conflicting_claims=3, insufficient_information=1, single_source_unverified=5`

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

- Human review item count: `116`
- Evaluation review flag count: `0`
- Anomaly review item count: `10`

| Review ID | Type | Related IDs | Reason |
|---|---|---|---|
| review_source_credibility_src_search_0d4e7ec87258 | source_credibility | src_search_0d4e7ec87258 | missing_publisher |
| review_source_src_search_0d4e7ec87258 | source_screening | src_search_0d4e7ec87258 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_src_search_75f2c3795fd4 | source_screening | src_search_75f2c3795fd4 | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_src_search_c4aae9b8565d | source_screening | src_search_c4aae9b8565d | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_credibility_src_search_99932da268a1 | source_credibility | src_search_99932da268a1 | missing_publisher |
| review_source_src_search_99932da268a1 | source_screening | src_search_99932da268a1 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_d2a24a52e44f | source_credibility | src_search_d2a24a52e44f | The deterministic scorer assigned a low credibility score (0.45) primarily driven by a very low disease relevance score (0.20) and a risk... |
| review_source_src_search_d2a24a52e44f | source_screening | src_search_d2a24a52e44f | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_credibility_src_search_5c954f0581ec | source_credibility | src_search_5c954f0581ec | The deterministic scorer assigned a low credibility score (0.47) primarily driven by a very low disease relevance score (0.20) and a risk... |
| review_source_src_search_5c954f0581ec | source_screening | src_search_5c954f0581ec | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_credibility_src_search_7b25eaafb554 | source_credibility | src_search_7b25eaafb554 | This source is a Facebook post from the official LA County Department of Public Health account (@lapublichealth), which carries genuine i... |
| review_source_src_search_7b25eaafb554 | source_screening | src_search_7b25eaafb554 | Screening and critic disagree on this source; routing to human review for resolution. |

## 9.5 Stage 11 anomaly detection and review application

- Anomaly result count: `15`
- Anomaly severity counts: `high=8, low=5, medium=2`
- Anomaly needs-human-review count: `10`
- Decisions provided: `0`
- Decisions applied: `0`
- Decisions rejected: `0`
- Audit entries: `0`
- Final dataset post-review count: `0`
- Records excluded by review: `0`

| Anomaly ID | Type | Severity | Target | Reason |
|---|---|---|---|---|
| anom_001 | deaths_without_case_reference | low | rec_src_search_29301bcfe202_001 | deaths present but no comparable case count is available |
| anom_002 | deaths_without_case_reference | low | rec_src_search_b9348b953aaa_006 | deaths present but no comparable case count is available |
| anom_003 | deaths_without_case_reference | low | rec_src_search_a39e4fa28013_008 | deaths present but no comparable case count is available |
| anom_004 | abrupt_spike_simple_threshold | medium | rec_src_search_fc3322f3069f_001 | case count is a simple-threshold spike over prior comparable records |
| anom_005 | deaths_without_case_reference | low | rec_src_search_14d0fc5d0793_002 | deaths present but no comparable case count is available |
| anom_006 | deaths_without_case_reference | low | rec_src_search_1901d64d67f4_004 | deaths present but no comparable case count is available |
| anom_007 | out_of_scope_count_bearing_record | high | event_008 | Stage 10 validation marked record outside requested scope: outside_geography |
| anom_008 | out_of_scope_count_bearing_record | high | event_008 | Stage 10 validation marked record outside requested scope: outside_geography |
| anom_009 | out_of_scope_count_bearing_record | high | event_012 | Stage 10 validation marked record outside requested scope: outside_time_window |
| anom_010 | out_of_scope_count_bearing_record | high | event_016 | Stage 10 validation marked record outside requested scope: outside_time_window |
| anom_011 | out_of_scope_count_bearing_record | high | event_010 | Stage 10 validation marked record outside requested scope: outside_time_window |
| anom_012 | out_of_scope_count_bearing_record | high | event_007 | Stage 10 validation marked record outside requested scope: outside_geography;outside_time_window |

| Applied decision | Type | Target | Audit IDs | Reason |
|---|---|---|---|---|

## 10. 输出文件

- Run output directory: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_west_nile_california_2024_08`
- Collection final dataset: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_west_nile_california_2024_08\collection\final_dataset.csv`
- Collection final case dataset: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_west_nile_california_2024_08\collection\final_case_dataset.csv`
- Collection zero-case statements: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_west_nile_california_2024_08\collection\zero_case_statements.csv`
- Collection exposure-monitoring records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_west_nile_california_2024_08\collection\exposure_monitoring_records.csv`
- Collection surveillance summaries: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_west_nile_california_2024_08\collection\surveillance_summary_records.csv`
- Collection outbreak summaries: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_west_nile_california_2024_08\collection\outbreak_summary_records.csv`
- Collection context records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_west_nile_california_2024_08\collection\context_records.csv`
- Collection unclassified observations: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_west_nile_california_2024_08\collection\unclassified_observation_records.csv`
- Collection observation dataset summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_west_nile_california_2024_08\collection\observation_type_dataset_summary.json`
- Collection pre-quality-gate records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_west_nile_california_2024_08\collection\final_dataset_pre_quality_gate.csv`
- Collection quarantined records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_west_nile_california_2024_08\collection\quarantined_records.csv`
- Collection pending review records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_west_nile_california_2024_08\collection\pending_review_records.csv`
- Collection non-primary observations: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_west_nile_california_2024_08\collection\non_primary_observations.csv`
- Collection record inclusion decisions: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_west_nile_california_2024_08\collection\record_inclusion_decisions.json`
- Collection final dataset post-review: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_west_nile_california_2024_08\collection\final_dataset_post_review.csv`
- Collection anomaly results: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_west_nile_california_2024_08\collection\anomaly_results.json`
- Collection human review audit trail: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_west_nile_california_2024_08\collection\human_review_audit_trail.json`
- Collection source registry: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_west_nile_california_2024_08\collection\source_registry.json`
- Validation mode: `diagnostic_only`
- Validation records source: `state`
- Validation records output: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_west_nile_california_2024_08\validation\ground_truth_records.csv`
- Inactive validation records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_west_nile_california_2024_08\validation\inactive_validation_records.csv`
- Validation compatibility summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_west_nile_california_2024_08\validation\validation_source_compatibility_summary.json`
- Evaluation report CSV: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_west_nile_california_2024_08\evaluation\evaluation_report.csv`
- Human-readable report: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_west_nile_california_2024_08\workflow_run_report_chinese.md`

## 11. 当前结论

This workflow run executed the configured data collection workflow through the exported graph and artifact pipeline. The user-facing run status is: COMPLETED WITH NO PRIMARY CASE DATASET RECORDS: workflow completed, but no primary case records were accepted into final_dataset.
The run completed technically, but it should not be read as a successful data collection result because no quality-gated accepted records were produced.

- Package metadata says LLM used: `True`
- Contains synthetic fixture data: `False`
- Generated at UTC: `2026-06-25T16:01:42.471648+00:00`

## 12. Workflow visualization artifacts

- Workflow visualization index: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_west_nile_california_2024_08\workflow_visualization\index.html`
- Workflow timeline: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_west_nile_california_2024_08\workflow_visualization\workflow_timeline.html`
- Evidence flow graph: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_west_nile_california_2024_08\workflow_visualization\evidence_flow_graph.html`
- Claim comparison cards: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_west_nile_california_2024_08\workflow_visualization\claim_comparison_cards.html`
- Dataset decision flow: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_west_nile_california_2024_08\workflow_visualization\dataset_decision_flow.html`
- Human review workflow visualization: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_west_nile_california_2024_08\workflow_visualization\human_review_workflow.html`
- Visualization summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_west_nile_california_2024_08\workflow_visualization\workflow_visualization_summary.json`
