# data collection workflow Run Report

## 1. 输入任务

Collect Salmonella cases, deaths, dates, locations, source URLs, source types, and evidence quotes for United States from 2024-05-01 to 2024-07-31.

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
- Source search executed queries: `6`
- Search-derived source candidates: `32`
- Iterative source discovery: `True`
- Iterative search iterations: `2`
- Iterative stop decision: `stop_sufficient`
- Iterative stop reason: `max_iterations reached (iteration 2 of 2); sufficient authoritative source candidates identified across primary target fields for the May–July 2024 window; additional searches would exceed the max_iterations bound and are unlikely to materially change the evidentiary record given the high duplicate rate (50% in iteration 2) already observed`
- Source credibility assessed sources: `32`
- Source credibility role counts: `{'context': 24, 'collection': 6, 'collection_support': 1, 'excluded': 1}`
- Source identity assessed sources: `32`
- Source identity type counts: `{'national_public_health_agency': 15, 'official_public_health_agency': 7, 'academic_or_peer_reviewed_source': 5, 'social_media': 1, 'news_media': 3, 'structured_database': 1}`
- Source identity warning counts: `{'search_provider_not_publisher': 32, 'publisher_from_search_metadata_unverified': 32, 'direct_target_official_fast_path_skips_source_identity': 32, 'actual_publisher_unknown': 11}`
- Source discovery method: `live_search_only`
- Disease relevance target: `Salmonella`
- Disease relevance source status counts: `{'target_disease_match': 25, 'ambiguous_disease': 6, 'insufficient_text': 1}`
- Disease relevance chunk status counts: `{'target_disease_match': 328, 'ambiguous_disease': 79, 'unrelated_disease': 8}`
- Disease relevance record status counts: `{'compatible': 45}`
- Rejected incompatible record count: `0`
- Final route: `finalize`

## 2.5 Run quality status

- User-facing run status: `PARTIAL: accepted records produced, but some records were quarantined.`
- Technical execution status: `completed`
- Run quality status: `partial_with_quarantined_records`
- Final dataset mode: `task_aware_quality_gated_records`
- Accepted final dataset count: `8`
- Final case dataset count: `5`
- Zero-case statement count: `0`
- Exposure-monitoring record count: `0`
- Surveillance summary record count: `5`
- Outbreak summary record count: `0`
- Context record count: `0`
- Unclassified observation count: `3`
- Observation dataset view counts: `{'final_case_dataset': 5, 'global_outbreak_event_dataset': 0, 'regional_surveillance_dataset': 0, 'country_year_aggregate_dataset': 0, 'official_alert_dataset': 0, 'probable_case_dataset': 0, 'suspected_case_dataset': 0, 'unspecified_case_dataset': 5, 'death_dataset': 1, 'hospitalization_dataset': 2, 'zero_case_statements': 0, 'exposure_monitoring_records': 0, 'surveillance_summary_records': 5, 'outbreak_summary_records': 0, 'context_records': 0, 'non_primary_observations': 7, 'unclassified_observation_records': 3}`
- Pre-quality-gate record count: `15`
- Quarantined record count: `6`
- Pending review record count: `1`
- Non-primary observation count: `4`
- Final dataset post-review count: `8`
- Primary-case dataset status: `primary_case_records_present`
- Recommended primary dataset message: `Primary case dataset records are available in final_case_dataset.`
- Primary-case eligible accepted count: `5`
- Corroborated primary case event count: `0`
- Recommended user message: `Review final_dataset and warnings before use.`

Workflow technically completed and produced quality-gated accepted records.

## 3. Workflow 运行过程

Graph is executed as a mostly serial workflow. The only conditional branch is after `quality_gate_routing`: the run enters `human_review` when quality or validation checks require review, then still builds the final data package. In this run, the graph route is shown above; validation comparison review flags are reported separately in Section 8.

1. `task_intake_and_scope_planning` - Built CollectionSpec from structured task input.
2. `disease_intelligence_builder` - Built disease intelligence from LLM output (Salmonellosis (non-typhoidal Salmonella)).
3. `profile_and_schema_setup` - Built active disease profile, collection schema, and source strategy (Salmonellosis (non-typhoidal Salmonella), gener...
4. `executable_source_planning` - Built executable source plan with 10 planned queries; no searches were executed.
5. `query_strategy_builder` - Built 10 direct_collection search queries from the LLM evidence strategy plan.
6. `source_discovery` - Discovered 32 source candidates using live_search_only.
7. `source_dedup_and_registry` - Built source registry with 32 entries (0 duplicates dropped).
8. `source_screening` - Screened 32 sources using deterministic policy.
9. `source_critic_and_uncertainty_routing` - Critic reviewed 32 sources; 28 ready for fetch, 0 deferred, 19 flagged for human review.
10. `content_fetch_and_parse` - Built 28 fetch requests, produced 28 documents (live_fetch_enabled=True, fixture_documents_enabled=False, fixtures_lo...
11. `document_quality_check` - Quality-checked 28 documents: 25 usable, 0 partial, 0 offline stub, 0 parse deferred, 3 unusable.
12. `evidence_chunking_and_data_presence_flagging` - Chunked 25/28 documents into 415 evidence chunks (386 flagged as containing target data).
13. `structured_extraction` - Built 15 raw records (extraction_mode=llm_structured_output, llm_enabled=True).
14. `schema_validation_and_repair` - Validated 15 raw records: 15 validated (0 need review), 0 rejected.
15. `record_normalization` - Normalized 15/15 records (0 need review).
16. `record_linking` - Linked 15/15 normalized records into 11 candidate events.
17. `cross_source_consistency_check` - Checked 3 multi-record events; found 2 new conflicts and 43 validation results (0 events need review).
18. `quality_gate_routing` - Human review disabled; preserving review flags as audit metadata and routing to final_data_package_builder.
19. `final_data_package_builder` - Assembled hardened FinalDataPackage from current state.

## 4. 数据源分工

| Role | Source ID | Publisher / title | Credibility | Final decision | Fetch ready |
|---|---|---|---|---|---|
| context_only | src_search_1aa919b25056 | / FOX 26 Houston - There are 173 new cases and 50 new... | medium (0.5639) | include_for_content_fetch | False |
| context_only | src_search_15fc5f8d47e2 | / Food for Thought 2025 - PIRG | needs_review (0.344) | needs_human_review | False |
| context_only | src_search_793a8dd9911b | / Outbreak Investigation of Salmonella: Cucumbers (November 2024) / FDA | needs_review (0.6712) | needs_human_review | False |
| context_only | src_search_420c4a0f3bfd | Centers for Disease Control and Prevention / CDC warns of a Salmonella outbreak linked to cucumbers | medium (0.7543) | include_for_content_fetch | True |
| context_only | src_search_58ef4c36918e | / Food Recalls in 2024: Revealing the Statistics - FSNS | needs_review (0.3624) | needs_human_review | False |
| context_only | src_search_14427d356566 | National Center for Biotechnology Information / Regulatory responses to foodborne illness outbreaks in the United States and their implic... | needs_review (0.5199) | needs_human_review | False |
| context_only | src_search_95a418d2f831 | CIDRAP / Salmonella outbreak linked to backyard poultry grows to 104 illnesses, 1 death / CIDRAP | medium (0.5811) | include_for_content_fetch | True |
| context_only | src_search_6d137cd3f82a | CIDRAP / Egg-linked Salmonella outbreak sickens nearly 100 in 18 states | medium (0.5811) | include_for_content_fetch | True |
| context_only | src_search_230f50d16406 | Centers for Disease Control and Prevention / Investigation Update: Salmonella Outbreak, February 2026 / Salmonella Infection / CDC | medium (0.7359) | include_for_content_fetch | True |
| context_only | src_search_00ed618d1c38 | CIDRAP / New state reports push Salmonella outbreak count to 383 - CIDRAP | medium (0.5811) | include_for_content_fetch | True |
| context_only | src_search_69331015856f | Centers for Disease Control and Prevention / CDC announces Salmonella outbreak in 13 states linked to ... | medium (0.7359) | include_for_content_fetch | True |
| context_only | src_search_081ac510741f | CIDRAP / Salmonella outbreaks linked to backyard poultry send 54 to the hospital / CIDRAP | medium (0.5811) | include_for_content_fetch | True |
| other | src_search_29acec08996b | Centers for Disease Control and Prevention / Salmonella Outbreak Linked to Eggs - September 2024 - CDC | high (0.8826) | include_for_content_fetch | True |
| other | src_search_d978f9d93b3b | Centers for Disease Control and Prevention / Investigation Update: Salmonella Outbreak, Cucumbers, November 2024 / Salmonella Infection /... | high (0.8826) | include_for_content_fetch | True |
| other | src_search_341f243cf7df | Centers for Disease Control and Prevention / Investigation Update: Salmonella Outbreak, Backyard Poultry - May 2024 / Salmonella Infectio... | high (0.8826) | include_for_content_fetch | True |
| other | src_search_c8cadc78e2a8 | Centers for Disease Control and Prevention / Salmonella Outbreak Linked to Charcuterie Meats, January 2024 | high (0.8826) | include_for_content_fetch | True |
| other | src_search_a5bc6c5400a7 | Centers for Disease Control and Prevention / Investigation Update: Salmonella Outbreak, Eggs - September 2024 | high (0.8826) | include_for_content_fetch | True |
| other | src_search_10ccb06f620d | Centers for Disease Control and Prevention / Reoccurring Salmonella Cotham Outbreak Linked to Pet Bearded Dragons — United States, 2024 /... | high (0.8943) | include_for_content_fetch | True |
| other | src_search_051378e10a24 | Centers for Disease Control and Prevention / Summary of Possible Multistate Enteric (Intestinal) Disease Outbreaks in 2024 / Foodborne Ou... | medium (0.6943) | include_for_content_fetch | True |
| other | src_search_57e9dfd2a4f6 | Centers for Disease Control and Prevention / Salmonella Outbreak Linked to Fresh Basil, April 2024 - CDC | high (0.8826) | include_for_content_fetch | True |
| other | src_search_5851bdcbd35f | Centers for Disease Control and Prevention / E. coli, Salmonella, Listeria Oh My! / Marler Blog | medium (0.772) | include_for_content_fetch | True |
| other | src_search_057e55c5d693 | Centers for Disease Control and Prevention / Investigation Update: Salmonella Outbreak, July 2025 - CDC | high (0.8759) | include_for_content_fetch | True |
| other | src_search_33733b13ba13 | / Outbreak Investigation of Salmonella: Cucumbers (June 2024) - FDA | high (0.8112) | include_for_content_fetch | True |
| other | src_search_3faf6631782d | / Hospitalizations, Deaths Caused by Foodborne Illnesses More Than Doubled in 2024 / Food Safety Magazine | high (0.8823) | include_for_content_fetch | True |
| other | src_search_85d5f7f41e48 | Centers for Disease Control and Prevention / Investigation Update: Salmonella Outbreaks, May 2025 - CDC | high (0.8759) | include_for_content_fetch | True |
| other | src_search_5bda1b341f55 | / Salmonella Outbreak Linked to Cucumbers - AAP Publications | high (0.7928) | include_for_content_fetch | True |
| other | src_search_31b14f5b949d | / 18 Food Outbreaks that have kept me busy in 2024 - Marler Blog | high (0.6823) | include_for_content_fetch | True |
| other | src_search_8207a084046e | CIDRAP / Report: Illnesses from contaminated food increased in 2024, severe ... | excluded (0.6943) | include_for_content_fetch | True |
| other | src_search_fdcb0a062e7e | / Salmonella By the Numbers / Food Safety and Inspection Service | high (0.8431) | include_for_content_fetch | True |
| other | src_search_23155caef955 | / Illnesses and deaths from food outbreaks skyrocketed in 2024 ... | high (0.8823) | include_for_content_fetch | True |
| other | src_search_3b86862864f7 | Centers for Disease Control and Prevention / FoodNet 2024 Preliminary Data / FoodNet / CDC | high (0.8826) | include_for_content_fetch | True |
| other | src_search_e0c58bcf769a | Centers for Disease Control and Prevention / Salmonella Outbreak Linked to Cucumbers - June 2024 - CDC | high (0.8826) | include_for_content_fetch | True |

## 5. 真实网页抓取结果

- Documents fetched/parsed: `28`
- Search-derived sources selected for fetch: `28`
- Search-derived skipped by reason: `{}`
- Fetch status counts: `fetch_failed=1, fetched=27`
- External fetch enabled: `True`
- Fetch provider counts: `native_requests=1, tavily_extract=27`
- External fetch failure counts: `native_requests=1, tavily_extract=1`
- Selected fetch bucket counts: `target_official_authority=28`
- Parser status counts: `parsed_html=1, parsed_text=27`
- Parser used counts: `html_stdlib_parser=1, text_parser=27`
- Quality status counts: `unusable=3, usable=25`
- Validation-reserved skipped from fetch: `[]`

| Source ID | Provider | Fetch status | HTTP | Parse | Parser | Quality | Text chars | Tables |
|---|---|---|---|---|---|---|---|---|
| src_search_10ccb06f620d | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 24845 | 0 |
| src_search_29acec08996b | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 1869 | 0 |
| src_search_d978f9d93b3b | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 15217 | 0 |
| src_search_341f243cf7df | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 20820 | 0 |
| src_search_3b86862864f7 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 26675 | 0 |
| src_search_c8cadc78e2a8 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 2046 | 0 |
| src_search_a5bc6c5400a7 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 10534 | 0 |
| src_search_e0c58bcf769a | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 2494 | 0 |
| src_search_57e9dfd2a4f6 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 1947 | 0 |
| src_search_3faf6631782d | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 13118 | 0 |
| src_search_057e55c5d693 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 9859 | 0 |
| src_search_85d5f7f41e48 | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 23998 | 0 |
| src_search_33733b13ba13 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 14729 | 0 |
| src_search_5bda1b341f55 | native_requests | fetch_failed | 403 | parsed_html | html_stdlib_parser | unusable | 16 | 0 |
| src_search_5851bdcbd35f | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 11698 | 0 |
| src_search_051378e10a24 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 23080 | 0 |
| src_search_23155caef955 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 8902 | 0 |
| src_search_fdcb0a062e7e | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 8796 | 0 |
| src_search_8207a084046e | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 15762 | 0 |
| src_search_31b14f5b949d | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 15280 | 0 |
| src_search_1aa919b25056 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 19967 | 0 |
| src_search_420c4a0f3bfd | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 2148 | 0 |
| src_search_230f50d16406 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 9790 | 0 |
| src_search_69331015856f | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 2352 | 0 |
| src_search_95a418d2f831 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 16841 | 0 |
| src_search_6d137cd3f82a | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 14997 | 0 |
| src_search_00ed618d1c38 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 13984 | 0 |
| src_search_081ac510741f | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 11067 | 0 |

## 6. 三个 LLM 环节调用结果

### 6.1 LLM Source Planning

- Status: `success`
- Plan generation method: `llm_executable_source_plan`
- Plan execution status: `planned_not_executed`
- Planned query count: `10`
- Planned source category count: `10`
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
- Total queries executed: `6`
- Stop decision: `stop_sufficient`
- Stop reason: `max_iterations reached (iteration 2 of 2); sufficient authoritative source candidates identified across primary target fields for the May–July 2024 window; additional searches would exceed the max_iterations bound and are unlikely to materially change the evidentiary record given the high duplicate rate (50% in iteration 2) already observed`
- Query source counts: `{'iterative_llm_initial_search_plan': 4, 'iterative_llm_refinement': 4}`
- Iteration query counts: `{'1': 4, '2': 4}`

### 6.2 LLM Source Critic

- Attempted source count: `0`
- Assessed source count: `0`
- Skipped source count: `32`
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
- Assessed source count: `32`
- Final role counts: `collection=6, collection_support=1, context=24, excluded=1`
- Risk flag counts: `advocacy_organization_source=1, ambiguous_disease=7, ambiguous_disease_signal_in_source_metadata=6, commercial_domain_non_governmental=1, complete_source_provenance=21, content_focus_regulatory_policy_not_epidemiological_case_data=1, context_or_background_only=15, contradictory_risk_flags_in_deterministic_output_screening_and_critic_disagree=1, cross_validation_required_before_any_data_use=1, cross_validation_required_before_any_figure_use=1, data_not_primary_surveillance=1, data_signal_in_source_metadata=32, data_signal_present_but_disease_unconfirmed=1, disease_relevance_unclear=1, disease_relevance_unconfirmed_zero_target_terms_found=1, geographic_granularity_low: score 0.58 suggests national-level aggregation; subnational and locality required fields may not be satisfiable from this source=1, independence_below_threshold=1, independence_unclear=2, local_or_subnational_granularity=18, local_source_matches_task_location=26, location_match_from_planned_query=6, low_authority_relevant_source=4, low_disease_relevance_score=1, missing_publisher=11, missing_publisher: null publisher field introduces minor provenance gap despite unambiguous domain=1, named_publisher=4, national_or_international_granularity=6, national_or_international_granularity_only=1, no_snippet_available: data signals detected in metadata but page content unverified; case counts, dates, and locations cannot be confirmed pre-retrieval=1, no_snippet_available_content_unverifiable=1, no_target_disease_terms_found_in_metadata=1, official_public_health_authority=26, potential_selective_framing_from_advocacy_origin=1, primary_or_authoritative_source=26, recall_linked_case_count_lag_risk: FDA recall/outbreak pages may lag epidemiological case counts per disease intelligence warnings — cross-validate with CDC DFWED=1, recall_statistics_not_epidemiological_case_data=1, required_fields_unlikely_to_be_populated_from_this_source=1, role_assignment_conflict: context role assigned despite fda.gov authority score of 0.95 — role may need upgrade pending content review=1, screening_and_critic_disagree=12, screening_and_critic_disagree: deterministic flags contain both official_public_health_authority and secondary_news_or_media_source simultaneously=1, secondary_news_or_media_source=11, source_disease_relevance:ambiguous_disease=6, source_disease_relevance:insufficient_text=1, source_disease_relevance:target_disease_match=25, source_disease_relevance_status_insufficient_text=1, source_metadata_matches_requested_disease=25, source_time_matches_requested_window=18, source_type_label_likely_incorrect_probable_peer_reviewed_review_article=1, source_type_likely_misclassified: fda.gov outbreak investigation pages are official_public_health_agency outputs, not news_and_situation_report=1, standard_web_page=32, task_location_granularity=8, temporal_coverage_of_article_data_unknown=1, temporal_mismatch_suspected: page title indicates November 2024; collection window closes 2024-07-31 — overlap unconfirmed without content retrieval=1, time_window_match_from_planned_query=14, title_year_mismatch_with_collection_window=1, zero_target_disease_terms_found_in_metadata=1`
- LLM assessed count: `4`
- LLM failure count: `0`
- Needs review count: `5`

### 6.3.5 Source Identity / Publisher Assessment

- Identity assessed source count: `32`
- LLM identity assessed source count: `0`
- Post-fetch identity assessed source count: `28`
- Unknown publisher count: `10`
- Source type counts: `academic_or_peer_reviewed_source=5, national_public_health_agency=15, news_media=3, official_public_health_agency=7, social_media=1, structured_database=1`
- Claim support role counts: `corroboration_support=3, insufficient_information=6, primary_case_claim_support=23`
- Fetch use counts: `fetch_for_extraction=26, fetch_only_after_review=6`
- Warning counts: `actual_publisher_unknown=11, direct_target_official_fast_path_skips_source_identity=32, publisher_from_search_metadata_unverified=32, search_provider_not_publisher=32`

### 6.4 LLM Structured Extraction

- Extraction mode: `llm_structured_output`
- Eligible chunk count: `269`
- LLM call count: `30`
- LLM success count: `30`
- LLM error count: `0`
- Raw record count: `15`

## 7. 最终抽取 records

- Normalized record count: `15`
- Run quality status: `partial_with_quarantined_records`
- Final dataset mode: `task_aware_quality_gated_records`
- Quality-gated accepted final dataset count: `8`
- Final case dataset count: `5`
- Zero-case statement count: `0`
- Exposure-monitoring record count: `0`
- Surveillance summary record count: `5`
- Outbreak summary record count: `0`
- Context record count: `0`
- Unclassified observation count: `3`
- Observation dataset view counts: `{'final_case_dataset': 5, 'global_outbreak_event_dataset': 0, 'regional_surveillance_dataset': 0, 'country_year_aggregate_dataset': 0, 'official_alert_dataset': 0, 'probable_case_dataset': 0, 'suspected_case_dataset': 0, 'unspecified_case_dataset': 5, 'death_dataset': 1, 'hospitalization_dataset': 2, 'zero_case_statements': 0, 'exposure_monitoring_records': 0, 'surveillance_summary_records': 5, 'outbreak_summary_records': 0, 'context_records': 0, 'non_primary_observations': 7, 'unclassified_observation_records': 3}`
- Pre-quality-gate record count: `15`
- Quarantined record count: `6`
- Pending review record count: `1`
- Non-primary observation count: `4`
- Final dataset post-review count: `8`
- Primary-case dataset status: `primary_case_records_present`
- Recommended primary dataset message: `Primary case dataset records are available in final_case_dataset.`
- Primary-case eligible accepted count: `5`
- Corroborated primary case event count: `0`
- Record inclusion status counts: `{'quarantined_outside_scope': 5, 'accepted_with_warnings': 8, 'quarantined_schema_invalid': 1, 'pending_human_review': 1}`
- Run quality warnings: `['no_corroborated_primary_case_events']`
- Accepted source counts: `src_search_051378e10a24=1, src_search_10ccb06f620d=1, src_search_33733b13ba13=3, src_search_3b86862864f7=3`

| Record ID | Date / period | Location | Cases | Deaths | Source | LLM used |
|---|---|---|---|---|---|---|
| rec_src_search_10ccb06f620d_002 | 2024 | United States | none | none | src_search_10ccb06f620d | True |
| rec_src_search_3b86862864f7_001 | 2024 preliminary | United States | 7314.0 | none | src_search_3b86862864f7 | True |
| rec_src_search_3b86862864f7_002 | 2024 preliminary | United States | none | none | src_search_3b86862864f7 | True |
| rec_src_search_3b86862864f7_003 | 2024 preliminary | United States | 6066.0 | none | src_search_3b86862864f7 | True |
| rec_src_search_33733b13ba13_001 | 2024-05-01 to 2024-07-31 | United States | 551.0 | none | src_search_33733b13ba13 | True |
| rec_src_search_33733b13ba13_002 | 2024-05-01 to 2024-07-31 | United States | none | none | src_search_33733b13ba13 | True |
| rec_src_search_33733b13ba13_003 | 2024-05-01 to 2024-07-31 | United States | none | 0.0 | src_search_33733b13ba13 | True |
| rec_src_search_051378e10a24_002 | 2024 | United States | none | none | src_search_051378e10a24 | True |

## 8. Validation 对比

### Claim-level corroboration

- Claim count: `16`
- Claim comparison count: `120`
- Corroborated event count: `2`
- Corroborated primary case event count: `0`
- Observation type counts: `ambiguous_public_health_observation=3, confirmed_case_record=3, death_record=1, hospitalization_record=3, probable_case_record=1, unspecified_case_record=5`
- Corroboration status counts: `conflicting_claims=1, single_source_unverified=1`

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

- Human review item count: `45`
- Evaluation review flag count: `0`
- Anomaly review item count: `4`

| Review ID | Type | Related IDs | Reason |
|---|---|---|---|
| review_source_credibility_src_search_5851bdcbd35f | source_credibility | src_search_5851bdcbd35f | missing_publisher |
| review_source_src_search_5851bdcbd35f | source_screening | src_search_5851bdcbd35f | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_33733b13ba13 | source_credibility | src_search_33733b13ba13 | missing_publisher |
| review_source_src_search_33733b13ba13 | source_screening | src_search_33733b13ba13 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_3faf6631782d | source_credibility | src_search_3faf6631782d | missing_publisher |
| review_source_src_search_3faf6631782d | source_screening | src_search_3faf6631782d | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_5bda1b341f55 | source_credibility | src_search_5bda1b341f55 | missing_publisher |
| review_source_src_search_5bda1b341f55 | source_screening | src_search_5bda1b341f55 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_31b14f5b949d | source_credibility | src_search_31b14f5b949d | missing_publisher |
| review_source_src_search_31b14f5b949d | source_screening | src_search_31b14f5b949d | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_fdcb0a062e7e | source_credibility | src_search_fdcb0a062e7e | missing_publisher |
| review_source_src_search_fdcb0a062e7e | source_screening | src_search_fdcb0a062e7e | Source classified as data_source; both screening and critic agree to include for content fetch. |

## 9.5 Stage 11 anomaly detection and review application

- Anomaly result count: `5`
- Anomaly severity counts: `high=3, low=1, medium=1`
- Anomaly needs-human-review count: `4`
- Decisions provided: `0`
- Decisions applied: `0`
- Decisions rejected: `0`
- Audit entries: `0`
- Final dataset post-review count: `8`
- Records excluded by review: `0`

| Anomaly ID | Type | Severity | Target | Reason |
|---|---|---|---|---|
| anom_001 | abrupt_spike_simple_threshold | medium | rec_src_search_3b86862864f7_001 | case count is a simple-threshold spike over prior comparable records |
| anom_002 | deaths_without_case_reference | low | rec_src_search_33733b13ba13_003 | deaths present but no comparable case count is available |
| anom_003 | out_of_scope_count_bearing_record | high | event_002 | Stage 10 validation marked record outside requested scope: outside_time_window |
| anom_004 | validation_conflict_anomaly | high | event_003 | Validation result is a conflict: Sources may use different case definitions or reporting categories. |
| anom_005 | validation_conflict_anomaly | high | event_009 | Validation result is a conflict: Sources may use different case definitions or reporting categories. |

| Applied decision | Type | Target | Audit IDs | Reason |
|---|---|---|---|---|

## 10. 输出文件

- Run output directory: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_salmonella_us_2024_05_07`
- Collection final dataset: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_salmonella_us_2024_05_07\collection\final_dataset.csv`
- Collection final case dataset: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_salmonella_us_2024_05_07\collection\final_case_dataset.csv`
- Collection zero-case statements: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_salmonella_us_2024_05_07\collection\zero_case_statements.csv`
- Collection exposure-monitoring records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_salmonella_us_2024_05_07\collection\exposure_monitoring_records.csv`
- Collection surveillance summaries: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_salmonella_us_2024_05_07\collection\surveillance_summary_records.csv`
- Collection outbreak summaries: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_salmonella_us_2024_05_07\collection\outbreak_summary_records.csv`
- Collection context records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_salmonella_us_2024_05_07\collection\context_records.csv`
- Collection unclassified observations: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_salmonella_us_2024_05_07\collection\unclassified_observation_records.csv`
- Collection observation dataset summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_salmonella_us_2024_05_07\collection\observation_type_dataset_summary.json`
- Collection pre-quality-gate records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_salmonella_us_2024_05_07\collection\final_dataset_pre_quality_gate.csv`
- Collection quarantined records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_salmonella_us_2024_05_07\collection\quarantined_records.csv`
- Collection pending review records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_salmonella_us_2024_05_07\collection\pending_review_records.csv`
- Collection non-primary observations: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_salmonella_us_2024_05_07\collection\non_primary_observations.csv`
- Collection record inclusion decisions: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_salmonella_us_2024_05_07\collection\record_inclusion_decisions.json`
- Collection final dataset post-review: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_salmonella_us_2024_05_07\collection\final_dataset_post_review.csv`
- Collection anomaly results: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_salmonella_us_2024_05_07\collection\anomaly_results.json`
- Collection human review audit trail: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_salmonella_us_2024_05_07\collection\human_review_audit_trail.json`
- Collection source registry: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_salmonella_us_2024_05_07\collection\source_registry.json`
- Validation mode: `diagnostic_only`
- Validation records source: `state`
- Validation records output: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_salmonella_us_2024_05_07\validation\ground_truth_records.csv`
- Inactive validation records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_salmonella_us_2024_05_07\validation\inactive_validation_records.csv`
- Validation compatibility summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_salmonella_us_2024_05_07\validation\validation_source_compatibility_summary.json`
- Evaluation report CSV: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_salmonella_us_2024_05_07\evaluation\evaluation_report.csv`
- Human-readable report: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_salmonella_us_2024_05_07\workflow_run_report_chinese.md`

## 11. 当前结论

This workflow run executed the configured data collection workflow through the exported graph and artifact pipeline. The user-facing run status is: PARTIAL: accepted records produced, but some records were quarantined.
The run completed technically and produced quality-gated accepted records in the final dataset.

- Package metadata says LLM used: `True`
- Contains synthetic fixture data: `False`
- Generated at UTC: `2026-06-25T16:15:37.928496+00:00`

## 12. Workflow visualization artifacts

- Workflow visualization index: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_salmonella_us_2024_05_07\workflow_visualization\index.html`
- Workflow timeline: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_salmonella_us_2024_05_07\workflow_visualization\workflow_timeline.html`
- Evidence flow graph: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_salmonella_us_2024_05_07\workflow_visualization\evidence_flow_graph.html`
- Claim comparison cards: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_salmonella_us_2024_05_07\workflow_visualization\claim_comparison_cards.html`
- Dataset decision flow: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_salmonella_us_2024_05_07\workflow_visualization\dataset_decision_flow.html`
- Human review workflow visualization: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_salmonella_us_2024_05_07\workflow_visualization\human_review_workflow.html`
- Visualization summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round03_salmonella_us_2024_05_07\workflow_visualization\workflow_visualization_summary.json`
