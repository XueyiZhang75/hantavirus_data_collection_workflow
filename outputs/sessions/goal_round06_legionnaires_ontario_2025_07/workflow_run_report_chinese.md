# data collection workflow Run Report

## 1. 输入任务

Collect Legionnaires' disease cases, deaths, dates, locations, source URLs, source types, and evidence quotes for Ontario from 2025-07-01 to 2025-07-31.

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
- Search-derived source candidates: `37`
- Iterative source discovery: `True`
- Iterative search iterations: `2`
- Iterative stop decision: `stop_sufficient`
- Iterative stop reason: `Max iterations reached (2/2). Evidence coverage is sufficient: confirmed case counts at multiple dated snapshots (43 cases/1 death at outbreak declaration ~July 8–11; 66 cases/2 deaths as of July 14; 70 cases/2 deaths as of July 29; outbreak declared over with 70 confirmed cases spanning July 8–August 6), locality (London, Ontario; Middlesex-London Health Unit; southeast London; Victoria Hospital cooling towers), authoritative sources (healthunit.com, publichealthontario.ca, lhsc.on.ca, crisis24.com, ctvnews.ca, cbc.ca, beaconbio.org), and the PHO 2025 annual surveillance PDF as the primary structured evidence source. All target fields (disease, country, subnational_location, locality, date_reported, cases_confirmed, deaths, source_url, source_type, evidence_quote) have candidate evidence. The re-declaration figure (94 cases/4 deaths) and the YouTube CTV clip (August 27, 2025) are post-July but provide final-count context. No further queries are warranted within the allowed bounds.`
- Source credibility assessed sources: `37`
- Source credibility role counts: `{'collection_support': 4, 'collection': 2, 'excluded': 4, 'context': 16, 'validation': 9, 'search_endpoint': 2}`
- Source identity assessed sources: `37`
- Source identity type counts: `{'official_public_health_agency': 12, 'social_media': 5, 'news_media': 11, 'structured_database': 1, 'unknown': 6, 'secondary_aggregator': 1, 'national_public_health_agency': 1}`
- Source identity warning counts: `{'search_provider_not_publisher': 37, 'publisher_from_search_metadata_unverified': 37, 'actual_publisher_unknown': 35, 'direct_target_official_fast_path_skips_source_identity': 37}`
- Source discovery method: `live_search_only`
- Disease relevance target: `Legionnaires' disease`
- Disease relevance source status counts: `{'ambiguous_disease': 19, 'target_disease_match': 8, 'insufficient_text': 10}`
- Disease relevance chunk status counts: `{'target_disease_match': 144, 'insufficient_text': 6, 'ambiguous_disease': 51, 'unrelated_disease': 2}`
- Disease relevance record status counts: `{'compatible': 66}`
- Rejected incompatible record count: `0`
- Final route: `finalize`

## 2.5 Run quality status

- User-facing run status: `COMPLETED WITH NO PRIMARY CASE DATASET RECORDS: workflow completed, but no primary case records were accepted into final_dataset.`
- Technical execution status: `completed`
- Run quality status: `no_primary_case_dataset_records`
- Final dataset mode: `task_aware_quality_gated_records`
- Accepted final dataset count: `0`
- Final case dataset count: `0`
- Zero-case statement count: `3`
- Exposure-monitoring record count: `0`
- Surveillance summary record count: `4`
- Outbreak summary record count: `1`
- Context record count: `4`
- Unclassified observation count: `19`
- Observation dataset view counts: `{'final_case_dataset': 0, 'global_outbreak_event_dataset': 0, 'regional_surveillance_dataset': 0, 'country_year_aggregate_dataset': 0, 'official_alert_dataset': 0, 'probable_case_dataset': 0, 'suspected_case_dataset': 0, 'unspecified_case_dataset': 0, 'death_dataset': 0, 'hospitalization_dataset': 0, 'zero_case_statements': 3, 'exposure_monitoring_records': 0, 'surveillance_summary_records': 4, 'outbreak_summary_records': 1, 'context_records': 4, 'non_primary_observations': 21, 'unclassified_observation_records': 19}`
- Pre-quality-gate record count: `22`
- Quarantined record count: `3`
- Pending review record count: `19`
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
2. `disease_intelligence_builder` - Built disease intelligence from LLM output (Legionnaires' disease).
3. `profile_and_schema_setup` - Built active disease profile, collection schema, and source strategy (Legionnaires' disease, generation_method=diseas...
4. `executable_source_planning` - Built executable source plan with 10 planned queries; no searches were executed.
5. `query_strategy_builder` - Built 10 direct_collection search queries from the LLM evidence strategy plan.
6. `source_discovery` - Discovered 37 source candidates using live_search_only.
7. `source_dedup_and_registry` - Built source registry with 37 entries (0 duplicates dropped).
8. `source_screening` - Screened 37 sources using deterministic policy.
9. `source_critic_and_uncertainty_routing` - Critic reviewed 37 sources; 22 ready for fetch, 0 deferred, 23 flagged for human review.
10. `content_fetch_and_parse` - Built 22 fetch requests, produced 22 documents (live_fetch_enabled=True, fixture_documents_enabled=False, fixtures_lo...
11. `document_quality_check` - Quality-checked 22 documents: 17 usable, 2 partial, 0 offline stub, 0 parse deferred, 3 unusable.
12. `evidence_chunking_and_data_presence_flagging` - Chunked 19/22 documents into 203 evidence chunks (173 flagged as containing target data).
13. `structured_extraction` - Built 22 raw records (extraction_mode=llm_structured_output, llm_enabled=True).
14. `schema_validation_and_repair` - Validated 22 raw records: 22 validated (0 need review), 0 rejected.
15. `record_normalization` - Normalized 22/22 records (0 need review).
16. `record_linking` - Linked 22/22 normalized records into 19 candidate events.
17. `cross_source_consistency_check` - Checked 3 multi-record events; found 0 new conflicts and 63 validation results (0 events need review).
18. `quality_gate_routing` - Human review disabled; preserving review flags as audit metadata and routing to final_data_package_builder.
19. `final_data_package_builder` - Assembled hardened FinalDataPackage from current state.

## 4. 数据源分工

| Role | Source ID | Publisher / title | Credibility | Final decision | Fetch ready |
|---|---|---|---|---|---|
| context_only | src_search_39e5b4e8aa9a | / Legionnaires' death reported, outbreak declared - YouTube | high (0.4928) | include_for_content_fetch | False |
| context_only | src_search_7894f931c313 | / Legionnaires' death reported, outbreak declared - CTV News | needs_review (0.344) | needs_human_review | False |
| context_only | src_search_ec872f8c24d9 | / Outbreak of legionnaires' disease redeclared in London, Ont., as ... | needs_review (0.4151) | needs_human_review | False |
| context_only | src_search_71006fc2e2b8 | National Center for Biotechnology Information / Community Legionella outbreak linked to a cooling tower, 2022 - PMC | needs_review (0.4648) | needs_human_review | False |
| context_only | src_search_69a4caba1b97 | / Legionellosis (Legionnaires' disease and Pontiac fever) - Canada.ca | low (0.4632) | needs_human_review | False |
| context_only | src_search_c21e01a20d22 | / Legionnaires' Disease Cases Doubled in Catawba County in 2025 ... | low (0.5) | needs_human_review | False |
| context_only | src_search_6321a50ee67f | / Officials re-declare Legionnaires outbreak in London | high (0.3474) | include_for_content_fetch | False |
| context_only | src_search_6350976bf51f | / 1 dead, over 40 sick as legionnaires' outbreak spreads in southeast ... | low (0.4151) | needs_human_review | False |
| context_only | src_search_b0ff495f502f | / London's deadly legionnaires' disease outbreak is over: Health ... | low (0.344) | needs_human_review | False |
| context_only | src_search_ffc47415e121 | / 1 dead, over 40 sick as legionnaires' outbreak spreads in southeast ... | low (0.344) | needs_human_review | False |
| context_only | src_search_ad461a409c17 | / Another person dead in London, Ont., legionnaires' outbreak / CBC ... | low (0.4151) | needs_human_review | False |
| context_only | src_search_c6054669fb49 | / CTV News London at Six for Tuesday, July 8, 2025 - YouTube | low (0.3624) | needs_human_review | False |
| context_only | src_search_320d9f857020 | / Legionnaires Outbreak Caused by Cooling Towers / Siskinds LLP | low (0.1986) | needs_human_review | False |
| context_only | src_search_241dbed400bd | / Middlesex-London Health Unit Redeclares Legionnaires' Disease ... | low (0.1826) | needs_human_review | False |
| context_only | src_search_c6aa4b1fae2f | / Ontario food manufacturer's cooling tower likely source of deadly ... | low (0.4175) | needs_human_review | False |
| context_only | src_search_1f78ac04c6db | / Legionnaires' disease outbreak re-declared in London, Ontario, after ... | low (0.4151) | needs_human_review | False |
| context_only | src_search_f379fe5937ae | / by Olivia Gomm London, Ont., public health officials have declared ... | low (0.2914) | needs_human_review | False |
| other | src_search_a828b4a066a7 | / Legionnaires' Disease Outbreak Status Update – July 14, 2025 | high (0.6112) | include_for_content_fetch | True |
| other | src_search_610d6ac3f5c7 | / [PDF] Legionellosis in Ontario: January 1, 2025 to December 31, 2025 | high (0.8063) | include_for_content_fetch | True |
| other | src_search_46a7561fccd4 | / Nine cases of Legionnaires' disease reported in Toronto, Ontario ... | excluded (0.6639) | include_for_content_fetch | True |
| other | src_search_c49cc412423d | / Canada: Confirmed Legionnaires' Disease Cases Reported in the ... | excluded (0.5928) | include_for_content_fetch | True |
| other | src_search_a07f1791e64f | / Legionella Investigation Reference Document | excluded (0.5903) | include_for_content_fetch | True |
| other | src_search_219b6b429550 | / Legionellosis, Canada - BEACON | medium (0.772) | include_for_content_fetch | True |
| other | src_search_95d26b86ff72 | / What to know about legionnaires' disease amid recent outbreaks in ... | high (0.5768) | include_for_content_fetch | True |
| other | src_search_e7d83ba11768 | / Ontario Reports 319 Legionellosis Cases in 2025 / ERIS posted on ... | high (0.8343) | include_for_content_fetch | True |
| other | src_search_a22d5d58de73 | / [PDF] Legionellosis in Ontario: January 1 to June 16, 2026 | medium (0.7759) | include_for_content_fetch | True |
| other | src_search_1094c38124ed | / 2025 Legionellosis Testing and Public Health Recommendations | high (0.824) | include_for_content_fetch | True |
| other | src_search_fed061e9489b | / Legionellosis (Legionella, Legionnaires Disease) / Public Health Ontario | high (0.8559) | include_for_content_fetch | True |
| other | src_search_b19fa2456b72 | / [PDF] Legionellosis in Ontario: January 1, 2024 to December 31, 2024 | medium (0.7759) | include_for_content_fetch | True |
| other | src_search_e78ed28655c4 | / Legionella - National Collaborating Centre for Environmental Health | medium (0.5656) | include_for_content_fetch | True |
| other | src_search_9c275dbf6b30 | Centers for Disease Control and Prevention / Legionnaires' disease cluster investigated in Hamilton, Ontario | medium (0.6527) | include_for_content_fetch | True |
| other | src_search_602d7af72b1a | / News - Middlesex-London Health Unit | high (0.3026) | include_for_content_fetch | True |
| other | src_search_8918c0ff9fe6 | / News - Middlesex-London Health Unit | high (0.2842) | include_for_content_fetch | True |
| other | src_search_be076f02faa9 | / Positive result for Legionella bacteria at London Health Sciences ... | high (0.4314) | include_for_content_fetch | True |
| other | src_search_7f4a1fa9b25c | / An outbreak of Legionnaires' disease was declared in London ... | excluded (0.4474) | include_for_content_fetch | True |
| other | src_search_d780ac567d3d | / Legionnaires outbreak sparks reminder for healthcare providers | high (0.4474) | include_for_content_fetch | True |
| other | src_search_9b99a2fc64df | Centers for Disease Control and Prevention / New Endemic Legionella pneumophila Serogroup I Clones, Ontario ... | medium (0.6482) | include_for_content_fetch | True |

## 5. 真实网页抓取结果

- Documents fetched/parsed: `22`
- Search-derived sources selected for fetch: `22`
- Search-derived skipped by reason: `{}`
- Fetch status counts: `fetched=22`
- External fetch enabled: `True`
- Fetch provider counts: `native_requests=2, tavily_extract=20`
- External fetch failure counts: `tavily_extract=2`
- Selected fetch bucket counts: `target_official_authority=22`
- Parser status counts: `parsed_html=2, parsed_text=20`
- Parser used counts: `html_stdlib_parser=2, text_parser=20`
- Quality status counts: `partial=2, unusable=3, usable=17`
- Validation-reserved skipped from fetch: `[]`

| Source ID | Provider | Fetch status | HTTP | Parse | Parser | Quality | Text chars | Tables |
|---|---|---|---|---|---|---|---|---|
| src_search_610d6ac3f5c7 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 16109 | 0 |
| src_search_219b6b429550 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 2124 | 0 |
| src_search_46a7561fccd4 | native_requests | fetched | 200 | parsed_html | html_stdlib_parser | partial | 129 | 0 |
| src_search_a828b4a066a7 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 10067 | 0 |
| src_search_c49cc412423d | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 14551 | 0 |
| src_search_a07f1791e64f | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 70944 | 0 |
| src_search_95d26b86ff72 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 9736 | 0 |
| src_search_39e5b4e8aa9a | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 5070 | 0 |
| src_search_7f4a1fa9b25c | native_requests | fetched | 200 | parsed_html | html_stdlib_parser | partial | 129 | 0 |
| src_search_d780ac567d3d | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 22396 | 0 |
| src_search_be076f02faa9 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 5162 | 0 |
| src_search_6321a50ee67f | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 1869 | 0 |
| src_search_602d7af72b1a | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 8492 | 0 |
| src_search_8918c0ff9fe6 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 7669 | 0 |
| src_search_fed061e9489b | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 5206 | 0 |
| src_search_e7d83ba11768 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 40203 | 0 |
| src_search_1094c38124ed | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 10554 | 0 |
| src_search_a22d5d58de73 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 15525 | 0 |
| src_search_b19fa2456b72 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 16887 | 0 |
| src_search_9b99a2fc64df | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 48848 | 0 |
| src_search_9c275dbf6b30 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 3218 | 0 |
| src_search_e78ed28655c4 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 27133 | 0 |

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
- Stop decision: `stop_sufficient`
- Stop reason: `Max iterations reached (2/2). Evidence coverage is sufficient: confirmed case counts at multiple dated snapshots (43 cases/1 death at outbreak declaration ~July 8–11; 66 cases/2 deaths as of July 14; 70 cases/2 deaths as of July 29; outbreak declared over with 70 confirmed cases spanning July 8–August 6), locality (London, Ontario; Middlesex-London Health Unit; southeast London; Victoria Hospital cooling towers), authoritative sources (healthunit.com, publichealthontario.ca, lhsc.on.ca, crisis24.com, ctvnews.ca, cbc.ca, beaconbio.org), and the PHO 2025 annual surveillance PDF as the primary structured evidence source. All target fields (disease, country, subnational_location, locality, date_reported, cases_confirmed, deaths, source_url, source_type, evidence_quote) have candidate evidence. The re-declaration figure (94 cases/4 deaths) and the YouTube CTV clip (August 27, 2025) are post-July but provide final-count context. No further queries are warranted within the allowed bounds.`
- Query source counts: `{'iterative_llm_initial_search_plan': 4, 'iterative_llm_refinement': 4}`
- Iteration query counts: `{'1': 4, '2': 4}`

### 6.2 LLM Source Critic

- Attempted source count: `0`
- Assessed source count: `0`
- Skipped source count: `37`
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
- Assessed source count: `37`
- Final role counts: `collection=2, collection_support=4, context=16, excluded=4, search_endpoint=2, validation=9`
- Risk flag counts: `ambiguous_disease=29, ambiguous_disease_signal:zero_target_disease_terms_found_in_metadata=1, ambiguous_disease_signal_in_source_metadata=19, ambiguous_disease_signal_in_source_metadata — title is on-topic but no target disease terms detected in screened metadata text fields; body content unverified=1, ambiguous_location=9, authority_score_suppressed_relative_to_domain_provenance:phac_not_ontario_reporting_authority=1, complete_source_provenance=2, context_or_background_only=1, data_extractability_unconfirmed_no_snippet_available=1, data_signal_in_source_metadata=35, data_signal_present_but_unverified — one data signal detected in metadata; extractable quantitative fields (cases, deaths, hospitalizations) unconfirmed without body access=1, deterministic_disease_term_detection_likely_failed_title_contains_explicit_disease_name=1, disease_relevance_score_critically_low (0.20) — despite on-topic title, disease relevance scoring did not confirm target disease terminology in screened fields=1, disease_relevance_score_critically_low:0.20=1, disease_relevance_unclear=10, dual_contradictory_flags:official_public_health_authority_and_secondary_news_or_media_source_both_present=1, geographic_granularity_unclear=9, geographic_granularity_unconfirmed:ontario_specificity_not_verified=1, independence_unclear=15, independence_unclear — article likely synthesizes PHU or PHO statements; any extracted figures are derivative and must be cross-validated against official source tier=1, independence_unclear:federal_background_page_does_not_validate_ontario_phu_data=1, international_organization_authority=3, local_or_subnational_granularity=13, local_source_matches_task_location=14, local_source_matches_task_location — London, Ontario is within Ontario geographic scope; high local relevance (0.95) is a positive signal but does not compensate for data derivativeness=1, location_match_from_planned_query=14, location_relevance_unclear=9, low_authority_relevant_source=1, low_machine_readability=2, machine_readable_or_structured=5, missing_publisher=35, missing_publisher — publisher field is null; reduces provenance traceability=1, missing_publisher_metadata=1, national_or_international_granularity=14, national_scope_incompatible_with_ontario_subnational_collection_target=1, news_may_precede_official_phu_confirmation_treat_as_provisional=1, news_reports_may_precede_official_PHU_confirmation — per disease intelligence summary, treat any figures as provisional until validated against official PHU or PHO source=1, no_case_count_or_surveillance_data_expected_from_this_page_type=1, no_extractable_2025_data:collection_window_july_2025_cannot_be_satisfied=1, not_directly_extractable_search_endpoint=2, official_phu_source_may_be_cited_within_article_not_yet_surfaced=1, official_public_health_authority=19, pdf_or_report_likely_medium_readability=2, primary_or_authoritative_source=22, screening_and_critic_disagree=17, screening_and_critic_disagree — internal pipeline disagreement on source role/credibility elevates uncertainty and warrants human adjudication=1, screening_and_critic_disagree:internal_flag_conflict_requires_resolution=1, screening_and_critic_disagree:likely_domain_authority_vs_task_utility_conflict=1, screening_and_critic_disagree_warrants_manual_reconciliation=1, secondary_news_or_media_source=16, source_disease_relevance:ambiguous_disease=19, source_disease_relevance:insufficient_text=10, source_disease_relevance:target_disease_match=8, source_likely_not_extractable=2, source_metadata_matches_requested_disease=8, source_time_matches_requested_window=9, source_type_label_mismatch:tagged_as_news_and_situation_report_but_is_static_background_page=1, source_type_misclassification:pmc_peer_reviewed_article_tagged_as_news_and_situation_report=1, standard_web_page=30, standard_web_page_no_structured_data_format=1, structured_data_source=3, task_location_granularity=1, temporal_mismatch:article_documents_2022_outbreak_not_2025=1, temporal_mismatch:standing_reference_page_cannot_contain_july_2025_outbreak_data=1, time_window_match_from_planned_query=28, time_window_match_unconfirmed — timeliness score 0.72 is acceptable but article date within 2025-07-01 to 2025-07-31 window should be verified by human reviewer=1`
- LLM assessed count: `4`
- LLM failure count: `0`
- Needs review count: `7`

### 6.3.5 Source Identity / Publisher Assessment

- Identity assessed source count: `37`
- LLM identity assessed source count: `0`
- Post-fetch identity assessed source count: `22`
- Unknown publisher count: `34`
- Source type counts: `national_public_health_agency=1, news_media=11, official_public_health_agency=12, secondary_aggregator=1, social_media=5, structured_database=1, unknown=6`
- Claim support role counts: `context_only=6, corroboration_support=12, insufficient_information=11, primary_case_claim_support=8`
- Fetch use counts: `fetch_for_context=6, fetch_for_extraction=20, fetch_only_after_review=11`
- Warning counts: `actual_publisher_unknown=35, direct_target_official_fast_path_skips_source_identity=37, publisher_from_search_metadata_unverified=37, search_provider_not_publisher=37`

### 6.4 LLM Structured Extraction

- Extraction mode: `llm_structured_output`
- Eligible chunk count: `180`
- LLM call count: `30`
- LLM success count: `30`
- LLM error count: `0`
- Raw record count: `22`

## 7. 最终抽取 records

- Normalized record count: `22`
- Run quality status: `no_primary_case_dataset_records`
- Final dataset mode: `task_aware_quality_gated_records`
- Quality-gated accepted final dataset count: `0`
- Final case dataset count: `0`
- Zero-case statement count: `3`
- Exposure-monitoring record count: `0`
- Surveillance summary record count: `4`
- Outbreak summary record count: `1`
- Context record count: `4`
- Unclassified observation count: `19`
- Observation dataset view counts: `{'final_case_dataset': 0, 'global_outbreak_event_dataset': 0, 'regional_surveillance_dataset': 0, 'country_year_aggregate_dataset': 0, 'official_alert_dataset': 0, 'probable_case_dataset': 0, 'suspected_case_dataset': 0, 'unspecified_case_dataset': 0, 'death_dataset': 0, 'hospitalization_dataset': 0, 'zero_case_statements': 3, 'exposure_monitoring_records': 0, 'surveillance_summary_records': 4, 'outbreak_summary_records': 1, 'context_records': 4, 'non_primary_observations': 21, 'unclassified_observation_records': 19}`
- Pre-quality-gate record count: `22`
- Quarantined record count: `3`
- Pending review record count: `19`
- Non-primary observation count: `7`
- Final dataset post-review count: `0`
- Primary-case dataset status: `no_primary_case_dataset_records`
- Recommended primary dataset message: `No primary case dataset records were accepted; inspect zero-case, exposure-monitoring, context, and other observation views.`
- Primary-case eligible accepted count: `0`
- Corroborated primary case event count: `0`
- Record inclusion status counts: `{'quarantined_outside_scope': 3, 'pending_human_review': 19}`
- Run quality warnings: `['no_primary_case_dataset_records', 'no_corroborated_primary_case_events']`
- Accepted source counts: `none`

No quality-gated records are available to list.
Candidate records, if any, are recorded in the pre-quality, quarantined, and pending-review artifacts.

| Record ID | Date / period | Location | Cases | Deaths | Source | LLM used |
|---|---|---|---|---|---|---|

## 8. Validation 对比

### Claim-level corroboration

- Claim count: `24`
- Claim comparison count: `276`
- Corroborated event count: `4`
- Corroborated primary case event count: `0`
- Observation type counts: `ambiguous_public_health_observation=6, confirmed_case_record=3, death_record=5, outbreak_summary=1, unspecified_case_record=9`
- Corroboration status counts: `conflicting_claims=1, insufficient_information=1, single_source_unverified=2`

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

- Human review item count: `67`
- Evaluation review flag count: `0`
- Anomaly review item count: `12`

| Review ID | Type | Related IDs | Reason |
|---|---|---|---|
| review_source_credibility_src_search_a828b4a066a7 | source_credibility | src_search_a828b4a066a7 | missing_publisher |
| review_source_src_search_a828b4a066a7 | source_screening | src_search_a828b4a066a7 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_610d6ac3f5c7 | source_credibility | src_search_610d6ac3f5c7 | missing_publisher |
| review_source_src_search_610d6ac3f5c7 | source_screening | src_search_610d6ac3f5c7 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_219b6b429550 | source_credibility | src_search_219b6b429550 | missing_publisher |
| review_source_src_search_219b6b429550 | source_screening | src_search_219b6b429550 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_95d26b86ff72 | source_credibility | src_search_95d26b86ff72 | missing_publisher |
| review_source_src_search_95d26b86ff72 | source_screening | src_search_95d26b86ff72 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_src_search_39e5b4e8aa9a | source_screening | src_search_39e5b4e8aa9a | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_credibility_src_search_7894f931c313 | source_credibility | src_search_7894f931c313 | CTV News (ctvnews.ca) is a well-established Canadian broadcast news organization with regional bureaus, including London, Ontario. The ar... |
| review_source_src_search_7894f931c313 | source_screening | src_search_7894f931c313 | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_credibility_src_search_ec872f8c24d9 | source_credibility | src_search_ec872f8c24d9 | The Globe and Mail is a nationally recognized Canadian newspaper with editorial standards, but as a secondary news source it carries inhe... |

## 9.5 Stage 11 anomaly detection and review application

- Anomaly result count: `15`
- Anomaly severity counts: `high=9, low=3, medium=3`
- Anomaly needs-human-review count: `12`
- Decisions provided: `0`
- Decisions applied: `0`
- Decisions rejected: `0`
- Audit entries: `0`
- Final dataset post-review count: `0`
- Records excluded by review: `0`

| Anomaly ID | Type | Severity | Target | Reason |
|---|---|---|---|---|
| anom_001 | abrupt_spike_simple_threshold | medium | rec_src_search_610d6ac3f5c7_001 | case count is a simple-threshold spike over prior comparable records |
| anom_002 | deaths_without_case_reference | low | rec_src_search_c49cc412423d_002 | deaths present but no comparable case count is available |
| anom_003 | deaths_without_case_reference | low | rec_src_search_95d26b86ff72_002 | deaths present but no comparable case count is available |
| anom_004 | test_positivity_or_rate_invalid | medium | rec_src_search_b19fa2456b72_005 | positivity_rate is outside expected proportion bounds |
| anom_005 | deaths_without_case_reference | low | rec_src_search_95d26b86ff72_004 | deaths present but no comparable case count is available |
| anom_006 | out_of_scope_count_bearing_record | high | event_006 | Stage 10 validation marked record outside requested scope: outside_time_window |
| anom_007 | out_of_scope_count_bearing_record | high | event_019 | Stage 10 validation marked record outside requested scope: outside_time_window |
| anom_008 | out_of_scope_count_bearing_record | high | event_013 | Stage 10 validation marked record outside requested scope: outside_time_window |
| anom_009 | out_of_scope_count_bearing_record | high | event_015 | Stage 10 validation marked record outside requested scope: outside_time_window |
| anom_010 | out_of_scope_count_bearing_record | high | event_012 | Stage 10 validation marked record outside requested scope: outside_time_window |
| anom_011 | out_of_scope_count_bearing_record | high | event_011 | Stage 10 validation marked record outside requested scope: outside_time_window |
| anom_012 | out_of_scope_count_bearing_record | high | event_016 | Stage 10 validation marked record outside requested scope: outside_time_window |

| Applied decision | Type | Target | Audit IDs | Reason |
|---|---|---|---|---|

## 10. 输出文件

- Run output directory: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_legionnaires_ontario_2025_07`
- Collection final dataset: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_legionnaires_ontario_2025_07\collection\final_dataset.csv`
- Collection final case dataset: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_legionnaires_ontario_2025_07\collection\final_case_dataset.csv`
- Collection zero-case statements: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_legionnaires_ontario_2025_07\collection\zero_case_statements.csv`
- Collection exposure-monitoring records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_legionnaires_ontario_2025_07\collection\exposure_monitoring_records.csv`
- Collection surveillance summaries: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_legionnaires_ontario_2025_07\collection\surveillance_summary_records.csv`
- Collection outbreak summaries: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_legionnaires_ontario_2025_07\collection\outbreak_summary_records.csv`
- Collection context records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_legionnaires_ontario_2025_07\collection\context_records.csv`
- Collection unclassified observations: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_legionnaires_ontario_2025_07\collection\unclassified_observation_records.csv`
- Collection observation dataset summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_legionnaires_ontario_2025_07\collection\observation_type_dataset_summary.json`
- Collection pre-quality-gate records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_legionnaires_ontario_2025_07\collection\final_dataset_pre_quality_gate.csv`
- Collection quarantined records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_legionnaires_ontario_2025_07\collection\quarantined_records.csv`
- Collection pending review records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_legionnaires_ontario_2025_07\collection\pending_review_records.csv`
- Collection non-primary observations: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_legionnaires_ontario_2025_07\collection\non_primary_observations.csv`
- Collection record inclusion decisions: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_legionnaires_ontario_2025_07\collection\record_inclusion_decisions.json`
- Collection final dataset post-review: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_legionnaires_ontario_2025_07\collection\final_dataset_post_review.csv`
- Collection anomaly results: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_legionnaires_ontario_2025_07\collection\anomaly_results.json`
- Collection human review audit trail: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_legionnaires_ontario_2025_07\collection\human_review_audit_trail.json`
- Collection source registry: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_legionnaires_ontario_2025_07\collection\source_registry.json`
- Validation mode: `diagnostic_only`
- Validation records source: `state`
- Validation records output: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_legionnaires_ontario_2025_07\validation\ground_truth_records.csv`
- Inactive validation records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_legionnaires_ontario_2025_07\validation\inactive_validation_records.csv`
- Validation compatibility summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_legionnaires_ontario_2025_07\validation\validation_source_compatibility_summary.json`
- Evaluation report CSV: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_legionnaires_ontario_2025_07\evaluation\evaluation_report.csv`
- Human-readable report: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_legionnaires_ontario_2025_07\workflow_run_report_chinese.md`

## 11. 当前结论

This workflow run executed the configured data collection workflow through the exported graph and artifact pipeline. The user-facing run status is: COMPLETED WITH NO PRIMARY CASE DATASET RECORDS: workflow completed, but no primary case records were accepted into final_dataset.
The run completed technically, but it should not be read as a successful data collection result because no quality-gated accepted records were produced.

- Package metadata says LLM used: `True`
- Contains synthetic fixture data: `False`
- Generated at UTC: `2026-06-25T21:03:32.410684+00:00`

## 12. Workflow visualization artifacts

- Workflow visualization index: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_legionnaires_ontario_2025_07\workflow_visualization\index.html`
- Workflow timeline: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_legionnaires_ontario_2025_07\workflow_visualization\workflow_timeline.html`
- Evidence flow graph: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_legionnaires_ontario_2025_07\workflow_visualization\evidence_flow_graph.html`
- Claim comparison cards: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_legionnaires_ontario_2025_07\workflow_visualization\claim_comparison_cards.html`
- Dataset decision flow: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_legionnaires_ontario_2025_07\workflow_visualization\dataset_decision_flow.html`
- Human review workflow visualization: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_legionnaires_ontario_2025_07\workflow_visualization\human_review_workflow.html`
- Visualization summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_legionnaires_ontario_2025_07\workflow_visualization\workflow_visualization_summary.json`
