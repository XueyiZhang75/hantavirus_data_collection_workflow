# data collection workflow Run Report

## 1. 输入任务

Collect Norovirus cases, deaths, dates, locations, source URLs, source types, and evidence quotes for United States from 2024-12-01 to 2025-02-28.

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
- Iterative stop decision: `stop_limits_reached`
- Iterative stop reason: `max_iterations reached (iteration_index=2, max_iterations=2); max_total_queries=10 also reached with 8 queries executed across 2 iterations; no further search permitted under task bounds`
- Source credibility assessed sources: `43`
- Source credibility role counts: `{'collection': 22, 'context': 18, 'collection_support': 3}`
- Source identity assessed sources: `43`
- Source identity type counts: `{'official_public_health_agency': 14, 'national_public_health_agency': 6, 'structured_database': 3, 'academic_or_peer_reviewed_source': 1, 'unknown': 6, 'social_media': 6, 'news_media': 5, 'state_or_local_public_health_agency': 2}`
- Source identity warning counts: `{'search_provider_not_publisher': 43, 'publisher_from_search_metadata_unverified': 43, 'actual_publisher_unknown': 31, 'direct_target_official_fast_path_skips_source_identity': 43}`
- Source discovery method: `live_search_only`
- Disease relevance target: `Norovirus`
- Disease relevance source status counts: `{'target_disease_match': 36, 'insufficient_text': 4, 'ambiguous_disease': 3}`
- Disease relevance chunk status counts: `{'ambiguous_disease': 50, 'target_disease_match': 660, 'related_context_only': 8}`
- Disease relevance record status counts: `{'compatible': 51}`
- Rejected incompatible record count: `0`
- Final route: `finalize`

## 2.5 Run quality status

- User-facing run status: `PARTIAL: accepted records produced, but some records were quarantined.`
- Technical execution status: `completed`
- Run quality status: `partial_with_quarantined_records`
- Final dataset mode: `task_aware_quality_gated_records`
- Accepted final dataset count: `1`
- Final case dataset count: `0`
- Zero-case statement count: `0`
- Exposure-monitoring record count: `2`
- Surveillance summary record count: `12`
- Outbreak summary record count: `1`
- Context record count: `0`
- Unclassified observation count: `15`
- Observation dataset view counts: `{'final_case_dataset': 0, 'global_outbreak_event_dataset': 0, 'regional_surveillance_dataset': 0, 'country_year_aggregate_dataset': 0, 'official_alert_dataset': 0, 'probable_case_dataset': 0, 'suspected_case_dataset': 0, 'unspecified_case_dataset': 0, 'death_dataset': 0, 'hospitalization_dataset': 0, 'zero_case_statements': 0, 'exposure_monitoring_records': 2, 'surveillance_summary_records': 12, 'outbreak_summary_records': 1, 'context_records': 0, 'non_primary_observations': 17, 'unclassified_observation_records': 15}`
- Pre-quality-gate record count: `17`
- Quarantined record count: `4`
- Pending review record count: `12`
- Non-primary observation count: `16`
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
2. `disease_intelligence_builder` - Built disease intelligence from LLM output (Norovirus Gastroenteritis).
3. `profile_and_schema_setup` - Built active disease profile, collection schema, and source strategy (Norovirus Gastroenteritis, generation_method=di...
4. `executable_source_planning` - Built executable source plan with 10 planned queries; no searches were executed.
5. `query_strategy_builder` - Built 10 direct_collection search queries from the LLM evidence strategy plan.
6. `source_discovery` - Discovered 43 source candidates using live_search_only.
7. `source_dedup_and_registry` - Built source registry with 43 entries (0 duplicates dropped).
8. `source_screening` - Screened 43 sources using deterministic policy.
9. `source_critic_and_uncertainty_routing` - Critic reviewed 43 sources; 37 ready for fetch, 0 deferred, 31 flagged for human review.
10. `content_fetch_and_parse` - Built 37 fetch requests, produced 37 documents (live_fetch_enabled=True, fixture_documents_enabled=False, fixtures_lo...
11. `document_quality_check` - Quality-checked 37 documents: 31 usable, 0 partial, 0 offline stub, 0 parse deferred, 6 unusable.
12. `evidence_chunking_and_data_presence_flagging` - Chunked 31/37 documents into 718 evidence chunks (639 flagged as containing target data).
13. `structured_extraction` - Built 17 raw records (extraction_mode=llm_structured_output, llm_enabled=True).
14. `schema_validation_and_repair` - Validated 17 raw records: 17 validated (0 need review), 0 rejected.
15. `record_normalization` - Normalized 17/17 records (0 need review).
16. `record_linking` - Linked 17/17 normalized records into 16 candidate events.
17. `cross_source_consistency_check` - Checked 1 multi-record events; found 0 new conflicts and 50 validation results (0 events need review).
18. `quality_gate_routing` - Human review disabled; preserving review flags as audit metadata and routing to final_data_package_builder.
19. `final_data_package_builder` - Assembled hardened FinalDataPackage from current state.

## 4. 数据源分工

| Role | Source ID | Publisher / title | Credibility | Final decision | Fetch ready |
|---|---|---|---|---|---|
| context_only | src_search_4674b69bd355 | / Minnesota Department of Health - Facebook | medium (0.5663) | include_for_content_fetch | False |
| context_only | src_search_926b43baa66c | / WDEF News 12 - "Outbreaks of norovirus are most common... | needs_review (0.5551) | needs_human_review | False |
| context_only | src_search_3b4e2043d3a5 | / Norovirus Surge May Be Driven by Ultra-Contagious Variant. Know These Signs | needs_review (0.5527) | needs_human_review | False |
| context_only | src_search_e119c616592e | / Norovirus cases are surging. Here's how to protect yourself. | needs_review (0.5735) | needs_human_review | False |
| context_only | src_search_40830ab6aa00 | / Cases of a highly contagious stomach virus, norovirus ... - Instagram | needs_review (0.5551) | needs_human_review | False |
| context_only | src_search_1508618df96d | / What to know about norovirus as cases surge across U.S. - YouTube | medium (0.5551) | needs_human_review | False |
| context_only | src_search_4b269588163c | Centers for Disease Control and Prevention / CaliciNet Data / Norovirus / CDC | medium (0.5632) | include_for_content_fetch | True |
| context_only | src_search_ef797e11ce78 | pinellas.floridahealth.gov / [PDF] EPI WATCH - Florida Department of Health in Pinellas County | high (0.3912) | include_for_content_fetch | True |
| context_only | src_search_20774518b571 | / CDC Data Shows Rising Number of Norovirus Outbreaks | low (0.5226) | needs_human_review | False |
| context_only | src_search_1d3abbf4b356 | Centers for Disease Control and Prevention / CDC Confirms 20th Cruise Ship Outbreak of 2025 - YouTube | medium (0.5823) | include_for_content_fetch | False |
| context_only | src_search_e700d6d1adfc | Centers for Disease Control and Prevention / Cruise ships hit by worst year for stomach bugs in over a decade ... | medium (0.6663) | include_for_content_fetch | True |
| context_only | src_search_db6dbac06000 | Centers for Disease Control and Prevention / The CDC said the outbreak happened... - Tampa Bay 28 - WFTS | medium (0.5823) | include_for_content_fetch | False |
| other | src_search_8d7dfb3aeace | Centers for Disease Control and Prevention / CDC: 2024-2025 seasonal norovirus outbreaks up from previous years / Contemporary Pediatrics | high (0.8706) | include_for_content_fetch | True |
| other | src_search_5b6be7bf0ee0 | / Highly Contagious Norovirus Cases Spike This Season - MDEdge | high (0.8522) | include_for_content_fetch | True |
| other | src_search_b9228859aa70 | Centers for Disease Control and Prevention / NoroSTAT Data / Norovirus / CDC | high (0.8434) | include_for_content_fetch | True |
| other | src_search_e6c676751454 | / Norovirus 2025: How To Stay Safe As Outbreaks Surge In US | high (0.8706) | include_for_content_fetch | True |
| other | src_search_0e2fe8a988c2 | Centers for Disease Control and Prevention / NoroSTAT Data / Norovirus - Restored CDC | high (0.8314) | include_for_content_fetch | True |
| other | src_search_db2c83f622cd | National Center for Biotechnology Information / Increasing Predominance of Norovirus GII.17 over GII.4, United States, 2022–2025 | high (0.8943) | include_for_content_fetch | True |
| other | src_search_c8f6e152147e | CIDRAP / US norovirus outbreaks are up, CDC data show - CIDRAP | high (0.8434) | include_for_content_fetch | True |
| other | src_search_c8beec2f9d8e | Centers for Disease Control and Prevention / NoroSTAT Data Table / Norovirus / CDC | high (0.8642) | include_for_content_fetch | True |
| other | src_search_111e84f03641 | / Sharp Rise in US Norovirus Cases in December 2024 | high (0.7943) | include_for_content_fetch | True |
| other | src_search_55c0da96c417 | National Center for Biotechnology Information / Norovirus Disease in the United States - PMC - NIH | high (0.8679) | include_for_content_fetch | True |
| other | src_search_6be93b583ffe | / Norovirus outbreaks reported across the USA, National Outbreak... | high (0.8159) | include_for_content_fetch | True |
| other | src_search_f0d04211eb5c | / Entering Peak Norovirus Season as Cases Rise Across the US | high (0.8159) | include_for_content_fetch | True |
| other | src_search_36288934cc79 | Centers for Disease Control and Prevention / Norovirus cases rise ahead of holiday season, CDC data shows - CBS News | medium (0.7759) | include_for_content_fetch | True |
| other | src_search_c26402b49d76 | / Flurry of Norovirus Outbreaks Tackled by Minnesota Public Health ... | high (0.8615) | include_for_content_fetch | True |
| other | src_search_d8b6d95ad369 | Centers for Disease Control and Prevention / Norovirus outbreaks rise across the U.S. / AHA News | high (0.8615) | include_for_content_fetch | True |
| other | src_search_9007d7feb130 | Centers for Disease Control and Prevention / As Norovirus cases rise, here’s what to know about this year’s spread — and how to protect y... | high (0.8823) | include_for_content_fetch | True |
| other | src_search_ec17d33f4f1d | Centers for Disease Control and Prevention / About the National Outbreak Reporting System (NORS) / NORS / CDC | high (0.8887) | include_for_content_fetch | True |
| other | src_search_b15c469d896c | Centers for Disease Control and Prevention / Norovirus Outbreaks - CDC | high (0.8679) | include_for_content_fetch | True |
| other | src_search_2acdad71566e | Centers for Disease Control and Prevention / Norovirus outbreaks surging across the US: CDC data - The Hill | high (0.7951) | include_for_content_fetch | True |
| other | src_search_a299322dc6e3 | Centers for Disease Control and Prevention / Resources / National Outbreak Reporting System (NORS) / CDC | high (0.8159) | include_for_content_fetch | True |
| other | src_search_c50a48405352 | / [PDF] 2025-2026 Norovirus Information for Schools | high (0.8063) | include_for_content_fetch | True |
| other | src_search_24d95efdd1f8 | doh.wa.gov / [PDF] Norovirus Infection - Washington State Department of Health | high (0.7975) | include_for_content_fetch | True |
| other | src_search_24eac4e3a15f | Centers for Disease Control and Prevention / Surge in Norovirus Incidents in 2025: A Crisis on the Rise | high (0.8823) | include_for_content_fetch | True |
| other | src_search_fb7ff50094aa | / Staying Healthy: Norovirus Infections Surge in 2025 - AllCare Health | high (0.8823) | include_for_content_fetch | True |
| other | src_search_1c70f6d6649a | / Norovirus outbreaks sweep California | high (0.8615) | include_for_content_fetch | True |
| other | src_search_c6fef11e96d5 | National Center for Biotechnology Information / A foodborne norovirus outbreak in a nursing home and spread to ... | high (0.8759) | include_for_content_fetch | True |
| other | src_search_1f728543018e | / Norovirus outbreak affects over 80 on Coral Princess as cruise ship cases surge in 2025 / Food Safety News | high (0.8823) | include_for_content_fetch | True |
| other | src_search_15ede2bf436b | / Cruise ship outbreaks 2025: 6 reported this year; here's what we know / FOX 35 Orlando | high (0.6823) | include_for_content_fetch | True |
| other | src_search_aedb884f5617 | Centers for Disease Control and Prevention / A Surge of Norovirus Outbreaks on Ships and on Land | high (0.8615) | include_for_content_fetch | True |
| other | src_search_8392b02e6a62 | Centers for Disease Control and Prevention / Norovirus outbreaks on cruise ships in 2025 / CruiseMapper | high (0.8823) | include_for_content_fetch | True |
| other | src_search_a071e9cc22ac | Centers for Disease Control and Prevention / Earlier Outbreaks on Cruise Ships in VSP's Jurisdiction / Vessel Sanitation Program / CDC | high (0.5197) | include_for_content_fetch | True |

## 5. 真实网页抓取结果

- Documents fetched/parsed: `37`
- Search-derived sources selected for fetch: `37`
- Search-derived skipped by reason: `{}`
- Fetch status counts: `fetch_failed=3, fetched=34`
- External fetch enabled: `True`
- Fetch provider counts: `native_requests=3, tavily_extract=34`
- External fetch failure counts: `native_requests=3, tavily_extract=3`
- Selected fetch bucket counts: `target_official_authority=37`
- Parser status counts: `fetch_failed=2, parsed_html=1, parsed_text=34`
- Parser used counts: `html_stdlib_parser=1, text_parser=34, unknown=2`
- Quality status counts: `unusable=6, usable=31`
- Validation-reserved skipped from fetch: `[]`

| Source ID | Provider | Fetch status | HTTP | Parse | Parser | Quality | Text chars | Tables |
|---|---|---|---|---|---|---|---|---|
| src_search_db2c83f622cd | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 17076 | 0 |
| src_search_8d7dfb3aeace | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 11459 | 0 |
| src_search_e6c676751454 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 29973 | 0 |
| src_search_c8beec2f9d8e | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 3493 | 0 |
| src_search_5b6be7bf0ee0 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 7447 | 0 |
| src_search_b9228859aa70 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 2074 | 0 |
| src_search_c8f6e152147e | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 12429 | 0 |
| src_search_0e2fe8a988c2 | native_requests | fetch_failed | none | fetch_failed | none | unusable | 0 | 0 |
| src_search_4b269588163c | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 2753 | 0 |
| src_search_ef797e11ce78 | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 7331 | 0 |
| src_search_ec17d33f4f1d | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 3630 | 0 |
| src_search_55c0da96c417 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 48677 | 0 |
| src_search_b15c469d896c | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 5244 | 0 |
| src_search_6be93b583ffe | native_requests | fetch_failed | 403 | parsed_html | html_stdlib_parser | unusable | 278 | 0 |
| src_search_f0d04211eb5c | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 207642 | 0 |
| src_search_a299322dc6e3 | native_requests | fetch_failed | none | fetch_failed | none | unusable | 0 | 0 |
| src_search_2acdad71566e | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 11261 | 0 |
| src_search_111e84f03641 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 5076 | 0 |
| src_search_36288934cc79 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 6161 | 0 |
| src_search_24eac4e3a15f | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 37831 | 0 |
| src_search_fb7ff50094aa | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 33297 | 0 |
| src_search_9007d7feb130 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 10266 | 0 |
| src_search_c6fef11e96d5 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 35564 | 0 |
| src_search_c26402b49d76 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 9363 | 0 |
| src_search_d8b6d95ad369 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 2986 | 0 |
| src_search_1c70f6d6649a | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 24272 | 0 |
| src_search_c50a48405352 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 14008 | 0 |
| src_search_24d95efdd1f8 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 7292 | 0 |
| src_search_4674b69bd355 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 7584 | 0 |
| src_search_1f728543018e | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 16030 | 0 |
| src_search_8392b02e6a62 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 60798 | 0 |
| src_search_aedb884f5617 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 8828 | 0 |
| src_search_15ede2bf436b | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 10781 | 0 |
| src_search_e700d6d1adfc | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 7999 | 0 |
| src_search_1d3abbf4b356 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 5347 | 0 |
| src_search_db6dbac06000 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 20418 | 0 |
| src_search_a071e9cc22ac | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 10696 | 0 |

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
- Stop decision: `stop_limits_reached`
- Stop reason: `max_iterations reached (iteration_index=2, max_iterations=2); max_total_queries=10 also reached with 8 queries executed across 2 iterations; no further search permitted under task bounds`
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
- Final role counts: `collection=22, collection_support=3, context=18`
- Risk flag counts: `advisory_digest_format_may_aggregate_without_citation=1, ambiguous_disease=7, ambiguous_disease_signal_in_source_metadata=3, authority_score_below_threshold=1, complete_source_provenance=12, consumer_health_framing_not_epidemiological_reporting=1, context_or_background_only=7, context_or_prevention_only=2, data_signal_in_source_metadata=41, disease_relevance_unclear=4, facebook_domain_not_original_publisher_domain=1, hedged_title_language_reduces_data_reliability=1, independence_score_below_threshold=1, independence_unclear=12, local_or_subnational_granularity=33, local_source_matches_task_location=42, location_match_from_planned_query=1, low_authority_for_numeric_field_extraction=1, low_authority_relevant_source=6, low_authority_score_0_48=1, low_independence_score_0_42=1, low_machine_readability=3, machine_readable_or_structured=9, missing_publisher=31, missing_publisher_metadata=1, missing_snippet_content_unverifiable=1, national_or_international_granularity=1, no_direct_data_extractability_from_social_post=1, no_editorial_or_institutional_accountability=1, not_suitable_for_direct_case_count_extraction_without_provenance_verification=1, not_suitable_for_primary_case_count_extraction=1, null_publisher_metadata_gap=1, numeric_claims_may_lack_primary_attribution=1, official_public_health_authority=31, pdf_or_report_likely_medium_readability=3, potential_health_misinformation_vector=1, primary_or_authoritative_source=31, publisher_unknown_null=1, reel_format_non_extractable_non_quotable=1, screening_and_critic_disagree=11, screening_and_critic_disagree_requires_resolution=1, secondary_news_or_media_source=10, secondary_relay_source_cdc_attributed_content=1, social_media_platform_as_canonical_url=1, social_media_platform_not_citable=1, source_disease_relevance:ambiguous_disease=3, source_disease_relevance:insufficient_text=4, source_disease_relevance:target_disease_match=36, source_is_pointer_only_not_primary_data=1, source_likely_not_extractable=2, source_metadata_matches_requested_disease=36, source_role_context_only_not_collection_primary=1, source_time_matches_requested_window=23, standard_web_page=31, structured_data_source=6, task_location_granularity=9, time_window_match_from_planned_query=20, upstream_source_citation_check_recommended=1`
- LLM assessed count: `4`
- LLM failure count: `0`
- Needs review count: `5`

### 6.3.5 Source Identity / Publisher Assessment

- Identity assessed source count: `43`
- LLM identity assessed source count: `0`
- Post-fetch identity assessed source count: `37`
- Unknown publisher count: `18`
- Source type counts: `academic_or_peer_reviewed_source=1, national_public_health_agency=6, news_media=5, official_public_health_agency=14, social_media=6, state_or_local_public_health_agency=2, structured_database=3, unknown=6`
- Claim support role counts: `corroboration_support=5, insufficient_information=13, primary_case_claim_support=25`
- Fetch use counts: `fetch_for_extraction=30, fetch_only_after_review=13`
- Warning counts: `actual_publisher_unknown=31, direct_target_official_fast_path_skips_source_identity=43, publisher_from_search_metadata_unverified=43, search_provider_not_publisher=43`

### 6.4 LLM Structured Extraction

- Extraction mode: `llm_structured_output`
- Eligible chunk count: `686`
- LLM call count: `30`
- LLM success count: `30`
- LLM error count: `0`
- Raw record count: `17`

## 7. 最终抽取 records

- Normalized record count: `17`
- Run quality status: `partial_with_quarantined_records`
- Final dataset mode: `task_aware_quality_gated_records`
- Quality-gated accepted final dataset count: `1`
- Final case dataset count: `0`
- Zero-case statement count: `0`
- Exposure-monitoring record count: `2`
- Surveillance summary record count: `12`
- Outbreak summary record count: `1`
- Context record count: `0`
- Unclassified observation count: `15`
- Observation dataset view counts: `{'final_case_dataset': 0, 'global_outbreak_event_dataset': 0, 'regional_surveillance_dataset': 0, 'country_year_aggregate_dataset': 0, 'official_alert_dataset': 0, 'probable_case_dataset': 0, 'suspected_case_dataset': 0, 'unspecified_case_dataset': 0, 'death_dataset': 0, 'hospitalization_dataset': 0, 'zero_case_statements': 0, 'exposure_monitoring_records': 2, 'surveillance_summary_records': 12, 'outbreak_summary_records': 1, 'context_records': 0, 'non_primary_observations': 17, 'unclassified_observation_records': 15}`
- Pre-quality-gate record count: `17`
- Quarantined record count: `4`
- Pending review record count: `12`
- Non-primary observation count: `16`
- Final dataset post-review count: `1`
- Primary-case dataset status: `no_primary_case_dataset_records`
- Recommended primary dataset message: `No primary case dataset records were accepted; inspect zero-case, exposure-monitoring, context, and other observation views.`
- Primary-case eligible accepted count: `0`
- Corroborated primary case event count: `0`
- Record inclusion status counts: `{'accepted_with_warnings': 1, 'pending_human_review': 12, 'quarantined_ambiguous_non_primary_observation': 2, 'quarantined_schema_invalid': 2}`
- Run quality warnings: `['no_primary_case_dataset_records', 'no_corroborated_primary_case_events']`
- Accepted source counts: `src_search_b15c469d896c=1`

| Record ID | Date / period | Location | Cases | Deaths | Source | LLM used |
|---|---|---|---|---|---|---|
| rec_src_search_b15c469d896c_001 | annual (approximate) | United States | none | none | src_search_b15c469d896c | True |

## 8. Validation 对比

### Claim-level corroboration

- Claim count: `17`
- Claim comparison count: `136`
- Corroborated event count: `9`
- Corroborated primary case event count: `0`
- Observation type counts: `ambiguous_public_health_observation=15, outbreak_summary=1, unspecified_case_record=1`
- Corroboration status counts: `insufficient_information=8, single_source_unverified=1`

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

- Human review item count: `69`
- Evaluation review flag count: `0`
- Anomaly review item count: `1`

| Review ID | Type | Related IDs | Reason |
|---|---|---|---|
| review_source_credibility_src_search_8d7dfb3aeace | source_credibility | src_search_8d7dfb3aeace | missing_publisher |
| review_source_src_search_8d7dfb3aeace | source_screening | src_search_8d7dfb3aeace | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_5b6be7bf0ee0 | source_credibility | src_search_5b6be7bf0ee0 | missing_publisher |
| review_source_src_search_5b6be7bf0ee0 | source_screening | src_search_5b6be7bf0ee0 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_e6c676751454 | source_credibility | src_search_e6c676751454 | missing_publisher |
| review_source_src_search_e6c676751454 | source_screening | src_search_e6c676751454 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_0e2fe8a988c2 | source_credibility | src_search_0e2fe8a988c2 | missing_publisher |
| review_source_src_search_0e2fe8a988c2 | source_screening | src_search_0e2fe8a988c2 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_111e84f03641 | source_credibility | src_search_111e84f03641 | secondary_source_reports_possible_case_data; missing_publisher |
| review_source_src_search_111e84f03641 | source_screening | src_search_111e84f03641 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_6be93b583ffe | source_credibility | src_search_6be93b583ffe | missing_publisher |
| review_source_src_search_6be93b583ffe | source_screening | src_search_6be93b583ffe | Source classified as data_source; both screening and critic agree to include for content fetch. |

## 9.5 Stage 11 anomaly detection and review application

- Anomaly result count: `1`
- Anomaly severity counts: `medium=1`
- Anomaly needs-human-review count: `1`
- Decisions provided: `0`
- Decisions applied: `0`
- Decisions rejected: `0`
- Audit entries: `0`
- Final dataset post-review count: `1`
- Records excluded by review: `0`

| Anomaly ID | Type | Severity | Target | Reason |
|---|---|---|---|---|
| anom_001 | test_positivity_or_rate_invalid | medium | rec_src_search_f0d04211eb5c_001 | positivity_rate is outside expected proportion bounds |

| Applied decision | Type | Target | Audit IDs | Reason |
|---|---|---|---|---|

## 10. 输出文件

- Run output directory: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_norovirus_us_2024_12_2025_02`
- Collection final dataset: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_norovirus_us_2024_12_2025_02\collection\final_dataset.csv`
- Collection final case dataset: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_norovirus_us_2024_12_2025_02\collection\final_case_dataset.csv`
- Collection zero-case statements: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_norovirus_us_2024_12_2025_02\collection\zero_case_statements.csv`
- Collection exposure-monitoring records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_norovirus_us_2024_12_2025_02\collection\exposure_monitoring_records.csv`
- Collection surveillance summaries: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_norovirus_us_2024_12_2025_02\collection\surveillance_summary_records.csv`
- Collection outbreak summaries: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_norovirus_us_2024_12_2025_02\collection\outbreak_summary_records.csv`
- Collection context records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_norovirus_us_2024_12_2025_02\collection\context_records.csv`
- Collection unclassified observations: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_norovirus_us_2024_12_2025_02\collection\unclassified_observation_records.csv`
- Collection observation dataset summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_norovirus_us_2024_12_2025_02\collection\observation_type_dataset_summary.json`
- Collection pre-quality-gate records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_norovirus_us_2024_12_2025_02\collection\final_dataset_pre_quality_gate.csv`
- Collection quarantined records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_norovirus_us_2024_12_2025_02\collection\quarantined_records.csv`
- Collection pending review records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_norovirus_us_2024_12_2025_02\collection\pending_review_records.csv`
- Collection non-primary observations: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_norovirus_us_2024_12_2025_02\collection\non_primary_observations.csv`
- Collection record inclusion decisions: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_norovirus_us_2024_12_2025_02\collection\record_inclusion_decisions.json`
- Collection final dataset post-review: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_norovirus_us_2024_12_2025_02\collection\final_dataset_post_review.csv`
- Collection anomaly results: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_norovirus_us_2024_12_2025_02\collection\anomaly_results.json`
- Collection human review audit trail: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_norovirus_us_2024_12_2025_02\collection\human_review_audit_trail.json`
- Collection source registry: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_norovirus_us_2024_12_2025_02\collection\source_registry.json`
- Validation mode: `diagnostic_only`
- Validation records source: `state`
- Validation records output: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_norovirus_us_2024_12_2025_02\validation\ground_truth_records.csv`
- Inactive validation records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_norovirus_us_2024_12_2025_02\validation\inactive_validation_records.csv`
- Validation compatibility summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_norovirus_us_2024_12_2025_02\validation\validation_source_compatibility_summary.json`
- Evaluation report CSV: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_norovirus_us_2024_12_2025_02\evaluation\evaluation_report.csv`
- Human-readable report: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_norovirus_us_2024_12_2025_02\workflow_run_report_chinese.md`

## 11. 当前结论

This workflow run executed the configured data collection workflow through the exported graph and artifact pipeline. The user-facing run status is: PARTIAL: accepted records produced, but some records were quarantined.
The run completed technically and produced quality-gated accepted records in the final dataset.

- Package metadata says LLM used: `True`
- Contains synthetic fixture data: `False`
- Generated at UTC: `2026-06-25T19:30:02.720317+00:00`

## 12. Workflow visualization artifacts

- Workflow visualization index: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_norovirus_us_2024_12_2025_02\workflow_visualization\index.html`
- Workflow timeline: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_norovirus_us_2024_12_2025_02\workflow_visualization\workflow_timeline.html`
- Evidence flow graph: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_norovirus_us_2024_12_2025_02\workflow_visualization\evidence_flow_graph.html`
- Claim comparison cards: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_norovirus_us_2024_12_2025_02\workflow_visualization\claim_comparison_cards.html`
- Dataset decision flow: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_norovirus_us_2024_12_2025_02\workflow_visualization\dataset_decision_flow.html`
- Human review workflow visualization: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_norovirus_us_2024_12_2025_02\workflow_visualization\human_review_workflow.html`
- Visualization summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_norovirus_us_2024_12_2025_02\workflow_visualization\workflow_visualization_summary.json`
