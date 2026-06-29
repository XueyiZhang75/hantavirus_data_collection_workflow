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
- Search-derived source candidates: `41`
- Iterative source discovery: `True`
- Iterative search iterations: `2`
- Iterative stop decision: `stop_sufficient`
- Iterative stop reason: `All target fields are covered by high-quality, authoritative source candidates identified across two iterations. The maximum iteration bound (max_iterations=2) has been reached, and the evidence base is comprehensive enough to populate all required data fields without further searching.`
- Source credibility assessed sources: `41`
- Source credibility role counts: `{'excluded': 4, 'collection_support': 7, 'collection': 2, 'context': 17, 'validation': 11}`
- Source identity assessed sources: `41`
- Source identity type counts: `{'official_public_health_agency': 13, 'social_media': 9, 'news_media': 11, 'unknown': 4, 'structured_database': 1, 'national_public_health_agency': 3}`
- Source identity warning counts: `{'search_provider_not_publisher': 41, 'publisher_from_search_metadata_unverified': 41, 'actual_publisher_unknown': 37, 'direct_target_official_fast_path_skips_source_identity': 41}`
- Source discovery method: `live_search_only`
- Disease relevance target: `Legionnaires' disease`
- Disease relevance source status counts: `{'ambiguous_disease': 29, 'target_disease_match': 4, 'insufficient_text': 8}`
- Disease relevance chunk status counts: `{'target_disease_match': 104, 'ambiguous_disease': 125, 'unrelated_disease': 4}`
- Disease relevance record status counts: `{'compatible': 85, 'ambiguous_disease': 14}`
- Rejected incompatible record count: `0`
- Final route: `finalize`

## 2.5 Run quality status

- User-facing run status: `PARTIAL: accepted records produced, but some records were quarantined.`
- Technical execution status: `completed`
- Run quality status: `partial_with_quarantined_records`
- Final dataset mode: `task_aware_quality_gated_records`
- Accepted final dataset count: `1`
- Final case dataset count: `0`
- Zero-case statement count: `4`
- Exposure-monitoring record count: `0`
- Surveillance summary record count: `1`
- Outbreak summary record count: `0`
- Context record count: `13`
- Unclassified observation count: `3`
- Observation dataset view counts: `{'final_case_dataset': 0, 'global_outbreak_event_dataset': 0, 'regional_surveillance_dataset': 0, 'country_year_aggregate_dataset': 0, 'official_alert_dataset': 0, 'probable_case_dataset': 0, 'suspected_case_dataset': 0, 'unspecified_case_dataset': 0, 'death_dataset': 0, 'hospitalization_dataset': 0, 'zero_case_statements': 4, 'exposure_monitoring_records': 0, 'surveillance_summary_records': 1, 'outbreak_summary_records': 0, 'context_records': 13, 'non_primary_observations': 19, 'unclassified_observation_records': 3}`
- Pre-quality-gate record count: `33`
- Quarantined record count: `11`
- Pending review record count: `21`
- Non-primary observation count: `4`
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
2. `disease_intelligence_builder` - Built disease intelligence from LLM output (Legionnaires' disease).
3. `profile_and_schema_setup` - Built active disease profile, collection schema, and source strategy (Legionnaires' disease, generation_method=diseas...
4. `executable_source_planning` - Built executable source plan with 10 planned queries; no searches were executed.
5. `query_strategy_builder` - Built 10 direct_collection search queries from the LLM evidence strategy plan.
6. `source_discovery` - Discovered 41 source candidates using live_search_only.
7. `source_dedup_and_registry` - Built source registry with 41 entries (0 duplicates dropped).
8. `source_screening` - Screened 41 sources using deterministic policy.
9. `source_critic_and_uncertainty_routing` - Critic reviewed 41 sources; 22 ready for fetch, 0 deferred, 29 flagged for human review.
10. `content_fetch_and_parse` - Built 22 fetch requests, produced 22 documents (live_fetch_enabled=True, fixture_documents_enabled=False, fixtures_lo...
11. `document_quality_check` - Quality-checked 22 documents: 21 usable, 0 partial, 0 offline stub, 0 parse deferred, 1 unusable.
12. `evidence_chunking_and_data_presence_flagging` - Chunked 21/22 documents into 233 evidence chunks (200 flagged as containing target data).
13. `structured_extraction` - Built 33 raw records (extraction_mode=llm_structured_output, llm_enabled=True).
14. `schema_validation_and_repair` - Validated 33 raw records: 33 validated (0 need review), 0 rejected.
15. `record_normalization` - Normalized 33/33 records (0 need review).
16. `record_linking` - Linked 33/33 normalized records into 20 candidate events.
17. `cross_source_consistency_check` - Checked 12 multi-record events; found 1 new conflicts and 87 validation results (0 events need review).
18. `quality_gate_routing` - Human review disabled; preserving review flags as audit metadata and routing to final_data_package_builder.
19. `final_data_package_builder` - Assembled hardened FinalDataPackage from current state.

## 4. 数据源分工

| Role | Source ID | Publisher / title | Credibility | Final decision | Fetch ready |
|---|---|---|---|---|---|
| context_only | src_search_842f34417a13 | / Instagram | high (0.4768) | include_for_content_fetch | False |
| context_only | src_search_8ca119dddbda | / Two NYC buildings were sources of Legionnaires’ disease outbreak in Harlem - Healthbeat | needs_review (0.4335) | needs_human_review | False |
| context_only | src_search_c480a6694da2 | / New York City declares Harlem legionnaire's disease outbreak over | needs_review (0.4335) | needs_human_review | False |
| context_only | src_search_55902341c014 | / For most people, Legionnaires’ disease... - Health Maximalist | low (0.328) | needs_human_review | False |
| context_only | src_search_2d165d3a4d7e | / Outbreak of Legionnaires' Disease Associated with Cooling Tower ... | needs_review (0.344) | needs_human_review | False |
| context_only | src_search_b5d35a763cb2 | / Final cooling tower to be cleaned amid 4th death in Legionnaires' outbreak | low (0.344) | needs_human_review | False |
| context_only | src_search_d7abef8536a2 | / NYC legionnaires' outbreak: Officials identify 10 buildings tied to Harlem outbreak, including hospital; 4th death announced - ABC7 New... | low (0.4151) | needs_human_review | False |
| context_only | src_search_1596aec16d67 | / New York City Health Department Closes Investigation of Central Harlem Legionnaires’ Disease Cluster - NYC Health | low (0.5423) | needs_human_review | False |
| context_only | src_search_e1ed8475f6ab | / Update on NYC Legionnaires' disease outbreak / Full News Conference | medium (0.5527) | needs_human_review | False |
| context_only | src_search_f4d05ea78792 | / Central Harlem Legionnaires' outbreak: 3 dead, 90 diagnosed with Legionnaires' Disease, NYC Health Department says - ABC7 New York | low (0.4151) | needs_human_review | False |
| context_only | src_search_ade8b70e4990 | / NYC Legionnaires' disease: Death toll climbs to 5 from the outbreak | low (0.4335) | needs_human_review | False |
| context_only | src_search_2a116853cc42 | / Legionnaires' disease case total in Central Harlem rises to 73, officials say | low (0.344) | needs_human_review | False |
| context_only | src_search_6fd0f55c1c05 | / NYC Health + Hospitals - Facebook | low (0.5367) | needs_human_review | False |
| context_only | src_search_31a704d793a7 | / Legionnaires' disease—a serious type of pneumonia caused by ... | medium (0.6608) | needs_human_review | False |
| context_only | src_search_fec52be8f139 | / NYC investigates Legionnaires’ disease cases at Bronx condos | low (0.4151) | needs_human_review | False |
| context_only | src_search_3a310a531aa5 | / Legionnaires’ disease reported in Bronx after Harlem outbreak – NBC New York | low (0.344) | needs_human_review | False |
| context_only | src_search_82f83b77a6d8 | / Legionnaires' disease reported at Bronx apartment building, NYC health officials say - CBS New York | low (0.4151) | needs_human_review | False |
| context_only | src_search_5819ad1d30fd | / An investigation is underway for Legionnaires' disease at one of ... | low (0.3991) | needs_human_review | False |
| context_only | src_search_2db27965c0f8 | / Two cases of Legionnaires' disease under investigation at Bronx ... | low (0.344) | needs_human_review | False |
| context_only | src_search_f1f4266d2f42 | / 6th Death Reported in Harlem Legionnaires' Outbreak as Bronx ... | low (0.344) | needs_human_review | False |
| other | src_search_c6833da45d7d | / Legionnaires' Disease Outbreak in New York City / RT | excluded (0.6823) | include_for_content_fetch | True |
| other | src_search_b74bccc017c5 | / 2025 Legionnaires’ Disease Community Cluster in New York City: Ongoing Public Health Investigation - Goldberg Segalla | high (0.6823) | include_for_content_fetch | True |
| other | src_search_ee3c4e1dc1cd | / Three Deaths, 67 People in NYC Diagnosed With Legionnaires' Disease - Infectious Disease Advisor | high (0.8639) | include_for_content_fetch | True |
| other | src_search_9d8411eba09d | / NYC Legionnaires Outbreak 6 Deaths 112 Cases - Powers Health | high (0.8823) | include_for_content_fetch | True |
| other | src_search_b4917c664acb | / NY State EP Alert 8.15.25 / Legionnaires' Disease Update / NYS Health Care Providers | excluded (0.6639) | include_for_content_fetch | True |
| other | src_search_743df961a25b | / NYC Legionnaires' Outbreak: Fourth Death Confirmed, 101 Sickened - Vaccine Advisor | high (0.6639) | include_for_content_fetch | True |
| other | src_search_5b7e6dfb326c | / New York City Health Department Provides Update on Community Cluster of Legionnaires' Disease - NYC Health | high (0.6823) | include_for_content_fetch | True |
| other | src_search_f0add2a7316b | / NYC reports fourth death in Legionnaires' outbreak, IDs buildings ... | medium (0.6343) | include_for_content_fetch | True |
| other | src_search_8572f55d7887 | National Center for Biotechnology Information / Legionnaires’ Disease Outbreaks and Cooling Towers, New York City, New York, USA | medium (0.6727) | include_for_content_fetch | True |
| other | src_search_259ad39d29b4 | / Legionnaires' Disease - NYC Health | medium (0.6607) | include_for_content_fetch | True |
| other | src_search_72af26a33522 | / Legionnaires’ outbreak kills five and infects over 100 in New York | high (0.5448) | include_for_content_fetch | True |
| other | src_search_ee903f91c827 | Centers for Disease Control and Prevention / Legionellosis Surveillance and Trends / Legionella / CDC | high (0.8176) | include_for_content_fetch | True |
| other | src_search_b8ca758c1979 | Centers for Disease Control and Prevention / Legionnaires Disease Associated with a Private-Use Hot Tub in a Vacation Rental Property — N... | medium (0.6092) | include_for_content_fetch | True |
| other | src_search_5501ac241962 | Centers for Disease Control and Prevention / Under Pressure, CDC Unraveled This Mysterious Outbreak / MedPage Today | high (0.4362) | include_for_content_fetch | True |
| other | src_search_eaa906b768dd | Centers for Disease Control and Prevention / MMWR Home Page / MMWR | medium (0.5748) | include_for_content_fetch | True |
| other | src_search_f72980cd3634 | / NYC Health Department Provides Update on Community Cluster of Legionnaires' Disease in Central Harlem - NYC Health | high (0.6823) | include_for_content_fetch | True |
| other | src_search_c72bcb75c75a | / NYC Health Department Investigating a Community Cluster of Legionnaires' Disease in Central Harlem - NYC Health | high (0.6823) | include_for_content_fetch | True |
| other | src_search_fd4c39b5e976 | / NYC Health Department Provides Update on Legionnaires' Disease Community Cluster in Central Harlem - NYC Health | high (0.6823) | include_for_content_fetch | True |
| other | src_search_a9306f6e1687 | / Transcript: First Deputy Mayor Mastro, NYC Health + Hospitals, and NYC Health Department Provides Update on Central Harlem Legionnaires... | high (0.6823) | include_for_content_fetch | True |
| other | src_search_90be6a027c41 | / Public Health Alert: Legionnaires' Disease Outbreak / Manhattan Borough President | excluded (0.6639) | include_for_content_fetch | True |
| other | src_search_b7d3f18e0f1a | / Making NYC Healthier / Manhattan Borough President | excluded (0.6479) | include_for_content_fetch | True |

## 5. 真实网页抓取结果

- Documents fetched/parsed: `22`
- Search-derived sources selected for fetch: `22`
- Search-derived skipped by reason: `{}`
- Fetch status counts: `fetched=22`
- External fetch enabled: `True`
- Fetch provider counts: `tavily_extract=22`
- External fetch failure counts: `none`
- Selected fetch bucket counts: `target_official_authority=22`
- Parser status counts: `parsed_text=22`
- Parser used counts: `text_parser=22`
- Quality status counts: `unusable=1, usable=21`
- Validation-reserved skipped from fetch: `[]`

| Source ID | Provider | Fetch status | HTTP | Parse | Parser | Quality | Text chars | Tables |
|---|---|---|---|---|---|---|---|---|
| src_search_9d8411eba09d | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 2372 | 0 |
| src_search_ee3c4e1dc1cd | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 5805 | 0 |
| src_search_c6833da45d7d | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 12667 | 0 |
| src_search_f72980cd3634 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 3426 | 0 |
| src_search_b74bccc017c5 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 6907 | 0 |
| src_search_c72bcb75c75a | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 3318 | 0 |
| src_search_fd4c39b5e976 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 3114 | 0 |
| src_search_a9306f6e1687 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 38910 | 0 |
| src_search_5b7e6dfb326c | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 5886 | 0 |
| src_search_b4917c664acb | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 4851 | 0 |
| src_search_743df961a25b | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 5701 | 0 |
| src_search_90be6a027c41 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 2861 | 0 |
| src_search_b7d3f18e0f1a | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 3268 | 0 |
| src_search_842f34417a13 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 15591 | 0 |
| src_search_ee903f91c827 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 2628 | 0 |
| src_search_8572f55d7887 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 62218 | 0 |
| src_search_259ad39d29b4 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 3424 | 0 |
| src_search_f0add2a7316b | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 12917 | 0 |
| src_search_72af26a33522 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 33306 | 0 |
| src_search_b8ca758c1979 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 28337 | 0 |
| src_search_eaa906b768dd | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 3239 | 0 |
| src_search_5501ac241962 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 6866 | 0 |

## 6. 三个 LLM 环节调用结果

### 6.1 LLM Source Planning

- Status: `success`
- Plan generation method: `llm_executable_source_plan`
- Plan execution status: `planned_not_executed`
- Planned query count: `10`
- Planned source category count: `8`
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
- Stop reason: `All target fields are covered by high-quality, authoritative source candidates identified across two iterations. The maximum iteration bound (max_iterations=2) has been reached, and the evidence base is comprehensive enough to populate all required data fields without further searching.`
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
- Final role counts: `collection=2, collection_support=7, context=17, excluded=4, validation=11`
- Risk flag counts: `ambiguous_disease=37, ambiguous_disease_signal_in_source_metadata=29, ambiguous_disease_signal_in_source_metadata_contradicts_explicit_title=1, ambiguous_location=1, authority_below_primary_collection_threshold=1, authority_score_likely_underestimated:evidence.nejm.org_is_high_authority_peer_reviewed_domain=1, collection_window_future_or_near_future:article_may_be_preliminary_or_preprint=1, complete_source_provenance=4, content_not_accessible_for_verification=1, context_or_background_only=4, data_granularity_unknown:cannot_confirm_original_case_counts_vs_synthesis_without_access=1, data_may_be_extractable_but_unverified_at_content_level=1, data_signal_in_source_metadata=41, deterministic_disease_relevance_score_likely_underestimated_title_contains_explicit_disease_name=1, disease_relevance_score_critically_low_despite_title_match=1, disease_relevance_unclear=8, disease_term_extraction_failure:title_contains_target_disease_but_zero_terms_found_in_metadata=1, doi_structure_consistent_with_peer_reviewed_article:EVIDpha_prefix_suggests_public_health_or_pharmacoepidemiology_article=1, geographic_granularity_unclear=1, independence_unclear=17, independence_unclear:relationship_to_primary_surveillance_data_unknown=1, independence_unclear_may_cite_nyc_dohmh_as_primary_source=1, international_organization_authority=4, local_or_subnational_granularity=27, local_or_subnational_granularity_harlem_nyc=1, local_source_matches_task_location=27, location_match_from_planned_query=11, location_relevance_unclear=1, low_authority_score=1, low_independence_score=1, machine_readable_or_structured=5, missing_publisher=37, missing_publisher:metadata_incomplete_but_domain_identity_is_unambiguous=1, missing_publisher_field_but_domain_is_well_known=1, missing_publisher_unresolved_provenance=1, national_or_international_context=2, national_or_international_granularity=13, no_extractable_case_data_signal=1, no_target_disease_terms_found_in_metadata_index=1, not_suitable_for_primary_data_extraction=1, null_publisher_field=1, null_snippet_prevented_full_text_disease_term_matching=1, official_public_health_authority=20, outbreak_declared_over_article_may_contain_final_cumulative_case_counts_suitable_for_extraction=1, primary_or_authoritative_source=24, role_may_be_undersold_as_context_if_quantitative_data_present=1, screening_and_critic_disagree=20, screening_and_critic_disagree:internal_pipeline_conflict_requires_human_adjudication=1, screening_and_critic_disagree_requires_resolution=1, secondary_news_or_media_source=16, secondary_news_or_media_source_not_authoritative_for_case_counts=1, social_media_platform_domain=1, source_disease_relevance:ambiguous_disease=29, source_disease_relevance:insufficient_text=8, source_disease_relevance:target_disease_match=4, source_metadata_matches_requested_disease=4, source_time_matches_requested_window=14, source_type_likely_misclassified:peer_reviewed_literature_assigned_as_news_and_situation_report=1, source_type_mismatch_social_media_classified_as_news=1, standard_web_page=36, structured_data_source=2, time_window_match_from_planned_query=27, unverified_publisher_identity=1, zero_disease_relevant_terms_detected=1`
- LLM assessed count: `4`
- LLM failure count: `0`
- Needs review count: `10`

### 6.3.5 Source Identity / Publisher Assessment

- Identity assessed source count: `41`
- LLM identity assessed source count: `0`
- Post-fetch identity assessed source count: `22`
- Unknown publisher count: `36`
- Source type counts: `national_public_health_agency=3, news_media=11, official_public_health_agency=13, social_media=9, structured_database=1, unknown=4`
- Claim support role counts: `context_only=8, corroboration_support=11, insufficient_information=13, primary_case_claim_support=9`
- Fetch use counts: `fetch_for_context=8, fetch_for_extraction=20, fetch_only_after_review=13`
- Warning counts: `actual_publisher_unknown=37, direct_target_official_fast_path_skips_source_identity=41, publisher_from_search_metadata_unverified=41, search_provider_not_publisher=41`

### 6.4 LLM Structured Extraction

- Extraction mode: `llm_structured_output`
- Eligible chunk count: `223`
- LLM call count: `30`
- LLM success count: `30`
- LLM error count: `0`
- Raw record count: `33`

## 7. 最终抽取 records

- Normalized record count: `33`
- Run quality status: `partial_with_quarantined_records`
- Final dataset mode: `task_aware_quality_gated_records`
- Quality-gated accepted final dataset count: `1`
- Final case dataset count: `0`
- Zero-case statement count: `4`
- Exposure-monitoring record count: `0`
- Surveillance summary record count: `1`
- Outbreak summary record count: `0`
- Context record count: `13`
- Unclassified observation count: `3`
- Observation dataset view counts: `{'final_case_dataset': 0, 'global_outbreak_event_dataset': 0, 'regional_surveillance_dataset': 0, 'country_year_aggregate_dataset': 0, 'official_alert_dataset': 0, 'probable_case_dataset': 0, 'suspected_case_dataset': 0, 'unspecified_case_dataset': 0, 'death_dataset': 0, 'hospitalization_dataset': 0, 'zero_case_statements': 4, 'exposure_monitoring_records': 0, 'surveillance_summary_records': 1, 'outbreak_summary_records': 0, 'context_records': 13, 'non_primary_observations': 19, 'unclassified_observation_records': 3}`
- Pre-quality-gate record count: `33`
- Quarantined record count: `11`
- Pending review record count: `21`
- Non-primary observation count: `4`
- Final dataset post-review count: `1`
- Primary-case dataset status: `no_primary_case_dataset_records`
- Recommended primary dataset message: `No primary case dataset records were accepted; inspect zero-case, exposure-monitoring, context, and other observation views.`
- Primary-case eligible accepted count: `0`
- Corroborated primary case event count: `0`
- Record inclusion status counts: `{'pending_human_review': 21, 'accepted_with_warnings': 1, 'quarantined_ambiguous_non_primary_observation': 2, 'quarantined_schema_invalid': 1, 'quarantined_outside_scope': 8}`
- Run quality warnings: `['no_primary_case_dataset_records', 'no_corroborated_primary_case_events']`
- Accepted source counts: `src_search_5b7e6dfb326c=1`

| Record ID | Date / period | Location | Cases | Deaths | Source | LLM used |
|---|---|---|---|---|---|---|
| rec_src_search_5b7e6dfb326c_001 | 2025-08-01 to 2025-08-31 | New York City | none | none | src_search_5b7e6dfb326c | True |

## 8. Validation 对比

### Claim-level corroboration

- Claim count: `47`
- Claim comparison count: `1081`
- Corroborated event count: `5`
- Corroborated primary case event count: `0`
- Observation type counts: `ambiguous_public_health_observation=3, confirmed_case_record=7, death_record=22, hospitalization_record=7, unspecified_case_record=8`
- Corroboration status counts: `conflicting_claims=3, single_source_unverified=2`

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

- Human review item count: `72`
- Evaluation review flag count: `0`
- Anomaly review item count: `9`

| Review ID | Type | Related IDs | Reason |
|---|---|---|---|
| review_source_credibility_src_search_b74bccc017c5 | source_credibility | src_search_b74bccc017c5 | missing_publisher |
| review_source_src_search_b74bccc017c5 | source_screening | src_search_b74bccc017c5 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_ee3c4e1dc1cd | source_credibility | src_search_ee3c4e1dc1cd | missing_publisher |
| review_source_src_search_ee3c4e1dc1cd | source_screening | src_search_ee3c4e1dc1cd | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_9d8411eba09d | source_credibility | src_search_9d8411eba09d | missing_publisher |
| review_source_src_search_9d8411eba09d | source_screening | src_search_9d8411eba09d | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_src_search_842f34417a13 | source_screening | src_search_842f34417a13 | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_credibility_src_search_743df961a25b | source_credibility | src_search_743df961a25b | missing_publisher |
| review_source_src_search_743df961a25b | source_screening | src_search_743df961a25b | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_5b7e6dfb326c | source_credibility | src_search_5b7e6dfb326c | missing_publisher |
| review_source_src_search_5b7e6dfb326c | source_screening | src_search_5b7e6dfb326c | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_8ca119dddbda | source_credibility | src_search_8ca119dddbda | This source is a news/media article from healthbeat.org, a health-focused journalism outlet. While it scores highly on local relevance (0... |

## 9.5 Stage 11 anomaly detection and review application

- Anomaly result count: `21`
- Anomaly severity counts: `high=2, low=12, medium=7`
- Anomaly needs-human-review count: `9`
- Decisions provided: `0`
- Decisions applied: `0`
- Decisions rejected: `0`
- Audit entries: `0`
- Final dataset post-review count: `1`
- Records excluded by review: `0`

| Anomaly ID | Type | Severity | Target | Reason |
|---|---|---|---|---|
| anom_001 | deaths_without_case_reference | low | rec_src_search_9d8411eba09d_002 | deaths present but no comparable case count is available |
| anom_002 | deaths_without_case_reference | low | rec_src_search_ee3c4e1dc1cd_002 | deaths present but no comparable case count is available |
| anom_003 | deaths_without_case_reference | low | rec_src_search_743df961a25b_002 | deaths present but no comparable case count is available |
| anom_004 | deaths_without_case_reference | low | rec_src_search_b74bccc017c5_002 | deaths present but no comparable case count is available |
| anom_005 | deaths_without_case_reference | low | rec_src_search_f0add2a7316b_002 | deaths present but no comparable case count is available |
| anom_006 | deaths_without_case_reference | low | rec_src_search_f0add2a7316b_004 | deaths present but no comparable case count is available |
| anom_007 | deaths_without_case_reference | low | rec_src_search_72af26a33522_002 | deaths present but no comparable case count is available |
| anom_008 | deaths_without_case_reference | low | rec_src_search_9d8411eba09d_004 | deaths present but no comparable case count is available |
| anom_009 | deaths_without_case_reference | low | rec_src_search_ee3c4e1dc1cd_004 | deaths present but no comparable case count is available |
| anom_010 | deaths_without_case_reference | low | rec_src_search_f72980cd3634_002 | deaths present but no comparable case count is available |
| anom_011 | deaths_without_case_reference | low | rec_src_search_c72bcb75c75a_002 | deaths present but no comparable case count is available |
| anom_012 | deaths_without_case_reference | low | rec_src_search_fd4c39b5e976_002 | deaths present but no comparable case count is available |

| Applied decision | Type | Target | Audit IDs | Reason |
|---|---|---|---|---|

## 10. 输出文件

- Run output directory: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_legionnaires_nyc_2025_08`
- Collection final dataset: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_legionnaires_nyc_2025_08\collection\final_dataset.csv`
- Collection final case dataset: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_legionnaires_nyc_2025_08\collection\final_case_dataset.csv`
- Collection zero-case statements: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_legionnaires_nyc_2025_08\collection\zero_case_statements.csv`
- Collection exposure-monitoring records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_legionnaires_nyc_2025_08\collection\exposure_monitoring_records.csv`
- Collection surveillance summaries: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_legionnaires_nyc_2025_08\collection\surveillance_summary_records.csv`
- Collection outbreak summaries: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_legionnaires_nyc_2025_08\collection\outbreak_summary_records.csv`
- Collection context records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_legionnaires_nyc_2025_08\collection\context_records.csv`
- Collection unclassified observations: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_legionnaires_nyc_2025_08\collection\unclassified_observation_records.csv`
- Collection observation dataset summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_legionnaires_nyc_2025_08\collection\observation_type_dataset_summary.json`
- Collection pre-quality-gate records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_legionnaires_nyc_2025_08\collection\final_dataset_pre_quality_gate.csv`
- Collection quarantined records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_legionnaires_nyc_2025_08\collection\quarantined_records.csv`
- Collection pending review records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_legionnaires_nyc_2025_08\collection\pending_review_records.csv`
- Collection non-primary observations: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_legionnaires_nyc_2025_08\collection\non_primary_observations.csv`
- Collection record inclusion decisions: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_legionnaires_nyc_2025_08\collection\record_inclusion_decisions.json`
- Collection final dataset post-review: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_legionnaires_nyc_2025_08\collection\final_dataset_post_review.csv`
- Collection anomaly results: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_legionnaires_nyc_2025_08\collection\anomaly_results.json`
- Collection human review audit trail: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_legionnaires_nyc_2025_08\collection\human_review_audit_trail.json`
- Collection source registry: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_legionnaires_nyc_2025_08\collection\source_registry.json`
- Validation mode: `diagnostic_only`
- Validation records source: `state`
- Validation records output: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_legionnaires_nyc_2025_08\validation\ground_truth_records.csv`
- Inactive validation records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_legionnaires_nyc_2025_08\validation\inactive_validation_records.csv`
- Validation compatibility summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_legionnaires_nyc_2025_08\validation\validation_source_compatibility_summary.json`
- Evaluation report CSV: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_legionnaires_nyc_2025_08\evaluation\evaluation_report.csv`
- Human-readable report: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_legionnaires_nyc_2025_08\workflow_run_report_chinese.md`

## 11. 当前结论

This workflow run executed the configured data collection workflow through the exported graph and artifact pipeline. The user-facing run status is: PARTIAL: accepted records produced, but some records were quarantined.
The run completed technically and produced quality-gated accepted records in the final dataset.

- Package metadata says LLM used: `True`
- Contains synthetic fixture data: `False`
- Generated at UTC: `2026-06-25T20:08:40.830959+00:00`

## 12. Workflow visualization artifacts

- Workflow visualization index: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_legionnaires_nyc_2025_08\workflow_visualization\index.html`
- Workflow timeline: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_legionnaires_nyc_2025_08\workflow_visualization\workflow_timeline.html`
- Evidence flow graph: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_legionnaires_nyc_2025_08\workflow_visualization\evidence_flow_graph.html`
- Claim comparison cards: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_legionnaires_nyc_2025_08\workflow_visualization\claim_comparison_cards.html`
- Dataset decision flow: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_legionnaires_nyc_2025_08\workflow_visualization\dataset_decision_flow.html`
- Human review workflow visualization: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_legionnaires_nyc_2025_08\workflow_visualization\human_review_workflow.html`
- Visualization summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_legionnaires_nyc_2025_08\workflow_visualization\workflow_visualization_summary.json`
