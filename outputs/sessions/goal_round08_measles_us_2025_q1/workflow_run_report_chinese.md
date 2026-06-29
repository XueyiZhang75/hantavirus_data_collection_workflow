# data collection workflow Run Report

## 1. 输入任务

Collect Measles cases, deaths, dates, locations, source URLs, source types, and evidence quotes for United States from 2025-01-01 to 2025-03-31.

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
- Search-derived source candidates: `34`
- Iterative source discovery: `True`
- Iterative search iterations: `2`
- Iterative stop decision: `stop_sufficient`
- Iterative stop reason: `Maximum iteration limit reached (2/2). Evidence coverage is sufficient: national case counts, subnational (state/county) breakdowns, deaths, hospitalizations, and international cross-validation are all represented in the accepted candidate set. No critical unresolvable gaps remain within the Q1 2025 window.`
- Source credibility assessed sources: `34`
- Source credibility role counts: `{'collection': 8, 'context': 14, 'validation': 12}`
- Source identity assessed sources: `34`
- Source identity type counts: `{'official_public_health_agency': 7, 'national_public_health_agency': 6, 'unknown': 3, 'secondary_aggregator': 1, 'news_media': 6, 'state_or_local_public_health_agency': 1, 'academic_or_peer_reviewed_source': 3, 'structured_database': 1, 'background_fact_sheet': 1, 'international_public_health_agency': 5}`
- Source identity warning counts: `{'search_provider_not_publisher': 34, 'publisher_from_search_metadata_unverified': 34, 'actual_publisher_unknown': 18, 'direct_target_official_fast_path_skips_source_identity': 34}`
- Source discovery method: `live_search_only`
- Disease relevance target: `Measles`
- Disease relevance source status counts: `{'target_disease_match': 33, 'insufficient_text': 1}`
- Disease relevance chunk status counts: `{'target_disease_match': 814, 'ambiguous_disease': 57, 'related_context_only': 3}`
- Disease relevance record status counts: `{'compatible': 264}`
- Rejected incompatible record count: `0`
- Final route: `finalize`

## 2.5 Run quality status

- User-facing run status: `COMPLETED WITH NO PRIMARY CASE DATASET RECORDS: workflow completed, but no primary case records were accepted into final_dataset.`
- Technical execution status: `completed`
- Run quality status: `no_primary_case_dataset_records`
- Final dataset mode: `task_aware_quality_gated_records`
- Accepted final dataset count: `0`
- Final case dataset count: `0`
- Zero-case statement count: `0`
- Exposure-monitoring record count: `0`
- Surveillance summary record count: `2`
- Outbreak summary record count: `6`
- Context record count: `6`
- Unclassified observation count: `6`
- Observation dataset view counts: `{'final_case_dataset': 0, 'global_outbreak_event_dataset': 0, 'regional_surveillance_dataset': 0, 'country_year_aggregate_dataset': 0, 'official_alert_dataset': 0, 'probable_case_dataset': 0, 'suspected_case_dataset': 0, 'unspecified_case_dataset': 0, 'death_dataset': 0, 'hospitalization_dataset': 0, 'zero_case_statements': 0, 'exposure_monitoring_records': 0, 'surveillance_summary_records': 2, 'outbreak_summary_records': 6, 'context_records': 6, 'non_primary_observations': 19, 'unclassified_observation_records': 6}`
- Pre-quality-gate record count: `88`
- Quarantined record count: `15`
- Pending review record count: `73`
- Non-primary observation count: `13`
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
2. `disease_intelligence_builder` - Built disease intelligence from LLM output (Measles).
3. `profile_and_schema_setup` - Built active disease profile, collection schema, and source strategy (Measles, generation_method=disease_intelligence...
4. `executable_source_planning` - Built executable source plan with 10 planned queries; no searches were executed.
5. `query_strategy_builder` - Built 10 direct_collection search queries from the LLM evidence strategy plan.
6. `source_discovery` - Discovered 34 source candidates using live_search_only.
7. `source_dedup_and_registry` - Built source registry with 34 entries (0 duplicates dropped).
8. `source_screening` - Screened 34 sources using deterministic policy.
9. `source_critic_and_uncertainty_routing` - Critic reviewed 34 sources; 28 ready for fetch, 0 deferred, 14 flagged for human review.
10. `content_fetch_and_parse` - Built 28 fetch requests, produced 28 documents (live_fetch_enabled=True, fixture_documents_enabled=False, fixtures_lo...
11. `document_quality_check` - Quality-checked 28 documents: 27 usable, 0 partial, 0 offline stub, 0 parse deferred, 1 unusable.
12. `evidence_chunking_and_data_presence_flagging` - Chunked 27/28 documents into 874 evidence chunks (800 flagged as containing target data).
13. `structured_extraction` - Built 88 raw records (extraction_mode=llm_structured_output, llm_enabled=True).
14. `schema_validation_and_repair` - Validated 88 raw records: 88 validated (0 need review), 0 rejected.
15. `record_normalization` - Normalized 88/88 records (0 need review).
16. `record_linking` - Linked 88/88 normalized records into 54 candidate events.
17. `cross_source_consistency_check` - Checked 23 multi-record events; found 7 new conflicts and 236 validation results (6 events need review).
18. `quality_gate_routing` - Human review disabled; preserving review flags as audit metadata and routing to final_data_package_builder.
19. `final_data_package_builder` - Assembled hardened FinalDataPackage from current state.

## 4. 数据源分工

| Role | Source ID | Publisher / title | Credibility | Final decision | Fetch ready |
|---|---|---|---|---|---|
| context_only | src_search_aabc350f7aa0 | / [PDF] MEASLES – THE AMERICAS 2025 - 2026 - Yale Health | needs_review (0.4264) | needs_human_review | False |
| context_only | src_search_0dac63a18578 | / Measles is spreading in multiple U.S. states. Experts warn cases are going unreported. - Healthbeat | needs_review (0.484) | needs_human_review | False |
| context_only | src_search_296bf3da1bef | / 2025 measles cases highest since 1991 - AAP Publications | needs_review (0.5024) | needs_human_review | False |
| context_only | src_search_eec8c3f3b772 | National Center for Biotechnology Information / Measles resurgence in the United States: epidemiological and ... | medium (0.7151) | needs_human_review | False |
| context_only | src_search_1639787c4334 | / Communicating About the Ongoing Measles Outbreak - Public Health Communications Collaborative | medium (0.6712) | needs_human_review | False |
| context_only | src_search_3d2f6cacf3f7 | CIDRAP / As US measles cases top 1,300, report details last year’s outbreak in New Mexico / CIDRAP | medium (0.5811) | include_for_content_fetch | True |
| context_only | src_search_c4a96c8b3aa2 | / [PDF] MEASLES OUTBREAK - SOUTHWEST U.S. - 2025 - Campus Health | low (0.4975) | needs_human_review | False |
| other | src_search_3c843cdae62c | Centers for Disease Control and Prevention / CDC reports over 2,000 US measles cases after recent outbreaks | high (0.8522) | include_for_content_fetch | True |
| other | src_search_0132cfa4f779 | / 2025-2026 Measles Outbreaks: Where Are We Now? Resources ... | high (0.8112) | include_for_content_fetch | True |
| other | src_search_cd5fb2750261 | Centers for Disease Control and Prevention / Measles Cases This Year Are Outpacing 2025 - Forbes | high (0.8112) | include_for_content_fetch | True |
| other | src_search_78fdd46eb63c | / 2025-2026 US Measles Map | high (0.8834) | include_for_content_fetch | True |
| other | src_search_283a8bed6a9d | Centers for Disease Control and Prevention / Measles Cases and Outbreaks | high (0.8642) | include_for_content_fetch | True |
| other | src_search_3109afb35d90 | Centers for Disease Control and Prevention / Measles Update — United States, January 1–April 17, 2025 / MMWR | high (0.8943) | include_for_content_fetch | True |
| other | src_search_f259b36c3067 | Centers for Disease Control and Prevention / Measles cases in the United States | high (0.8639) | include_for_content_fetch | True |
| other | src_search_eaa906b768dd | Centers for Disease Control and Prevention / MMWR Home Page / MMWR | medium (0.6482) | include_for_content_fetch | True |
| other | src_search_74152a4ae4ab | / Public Health: U.S. Measles Outbreak 2025 - MSK Library Guides | high (0.8951) | include_for_content_fetch | True |
| other | src_search_14e93bfe3eec | / 2025 Southwest United States measles outbreak - Wikipedia | high (0.8343) | include_for_content_fetch | True |
| other | src_search_1be284797a9b | Centers for Disease Control and Prevention / Map: Track measles outbreaks, cases and vaccination rates by state across the U.S. | medium (0.7759) | include_for_content_fetch | True |
| other | src_search_16671615d27a | health.ny.gov / Measles Update | high (0.8679) | include_for_content_fetch | True |
| other | src_search_4847d41afdb8 | CIDRAP / US measles outbreak approaches 1,500 cases / CIDRAP | high (0.8419) | include_for_content_fetch | True |
| other | src_search_62409e4d2cf9 | / US Measles Cases Near 2,000 in 2025 as Multi-State Outbreaks Expand | high (0.8343) | include_for_content_fetch | True |
| other | src_search_7cb311dd75e6 | / U.S. Measles Tracker / International Vaccine Access Center | high (0.7951) | include_for_content_fetch | True |
| other | src_search_fede8be6ac1e | Centers for Disease Control and Prevention / Notes from the Field: Initial Public Health Response to a Measles Outbreak in a Close-Knit W... | high (0.8943) | include_for_content_fetch | True |
| other | src_search_4e73f2d0f38f | Centers for Disease Control and Prevention / Characteristics of Patients Hospitalized with Measles During ... - CDC | high (0.8551) | include_for_content_fetch | True |
| other | src_search_4269b2fb672d | / Measles in Texas 2026: Symptoms, Risks & When to Visit the ER | medium (0.6474) | include_for_content_fetch | True |
| other | src_search_831265159816 | / Texas Measles Outbreak: 2025 / RT | high (0.8823) | include_for_content_fetch | True |
| other | src_search_10eb05b1063d | / Risk and Spatial Spread of a Measles Outbreak in Texas / medRxiv | high (0.6658) | include_for_content_fetch | True |
| other | src_search_babdba80f49a | Centers for Disease Control and Prevention / [PDF] Characteristics of Patients Hospitalized with Measles During ... - CDC | medium (0.7791) | include_for_content_fetch | True |
| other | src_search_4ea030a47321 | CIDRAP / CDC: Only 1 in 10 hospital patients early in the West Texas measles outbreak had underlying conditions / CIDRAP | high (0.8759) | include_for_content_fetch | True |
| other | src_search_8242cbb785a1 | Pan American Health Organization / Situation Report #2: Measles in the Americas Region - PAHO/WHO | high (0.8048) | include_for_content_fetch | True |
| other | src_search_200d5531b1f1 | Pan American Health Organization / Situation Report #4: Measles in the Americas Region. 4 June 2026 - PAHO/WHO / Pan American Health Orga... | high (0.8048) | include_for_content_fetch | True |
| other | src_search_5ca479a49f5f | Pan American Health Organization / PAHO issues epidemiological alert amid continued measles transmission in the Americas and urges streng... | high (0.8048) | include_for_content_fetch | True |
| other | src_search_6e578fc529e9 | Pan American Health Organization / Situation Report #1: Measles in the Americas Region - PAHO/WHO | high (0.8048) | include_for_content_fetch | True |
| other | src_search_4250b5c89dbb | World Health Organization / Measles - United States of America | high (0.8735) | include_for_content_fetch | True |

## 5. 真实网页抓取结果

- Documents fetched/parsed: `28`
- Search-derived sources selected for fetch: `28`
- Search-derived skipped by reason: `{}`
- Fetch status counts: `fetched=28`
- External fetch enabled: `True`
- Fetch provider counts: `tavily_extract=28`
- External fetch failure counts: `none`
- Selected fetch bucket counts: `target_official_authority=28`
- Parser status counts: `parsed_text=28`
- Parser used counts: `text_parser=28`
- Quality status counts: `unusable=1, usable=27`
- Validation-reserved skipped from fetch: `[]`

| Source ID | Provider | Fetch status | HTTP | Parse | Parser | Quality | Text chars | Tables |
|---|---|---|---|---|---|---|---|---|
| src_search_fede8be6ac1e | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 19689 | 0 |
| src_search_3109afb35d90 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 28035 | 0 |
| src_search_78fdd46eb63c | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 18074 | 0 |
| src_search_831265159816 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 32393 | 0 |
| src_search_4ea030a47321 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 12776 | 0 |
| src_search_283a8bed6a9d | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 57418 | 0 |
| src_search_f259b36c3067 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 25507 | 0 |
| src_search_4e73f2d0f38f | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 26745 | 0 |
| src_search_3c843cdae62c | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 12727 | 0 |
| src_search_0132cfa4f779 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 41938 | 0 |
| src_search_cd5fb2750261 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 7862 | 0 |
| src_search_babdba80f49a | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 27082 | 0 |
| src_search_10eb05b1063d | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 101519 | 0 |
| src_search_eaa906b768dd | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 3239 | 0 |
| src_search_4269b2fb672d | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 10173 | 0 |
| src_search_74152a4ae4ab | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 23059 | 0 |
| src_search_4250b5c89dbb | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 26003 | 0 |
| src_search_16671615d27a | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 18101 | 0 |
| src_search_4847d41afdb8 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 12565 | 0 |
| src_search_14e93bfe3eec | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 24119 | 0 |
| src_search_62409e4d2cf9 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 210128 | 0 |
| src_search_8242cbb785a1 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 6145 | 0 |
| src_search_200d5531b1f1 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 6869 | 0 |
| src_search_5ca479a49f5f | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 11388 | 0 |
| src_search_6e578fc529e9 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 6288 | 0 |
| src_search_7cb311dd75e6 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 13445 | 0 |
| src_search_1be284797a9b | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 4231 | 0 |
| src_search_3d2f6cacf3f7 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 15330 | 0 |

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
- Stop reason: `Maximum iteration limit reached (2/2). Evidence coverage is sufficient: national case counts, subnational (state/county) breakdowns, deaths, hospitalizations, and international cross-validation are all represented in the accepted candidate set. No critical unresolvable gaps remain within the Q1 2025 window.`
- Query source counts: `{'iterative_llm_initial_search_plan': 4, 'iterative_llm_refinement': 4}`
- Iteration query counts: `{'1': 4, '2': 4}`

### 6.2 LLM Source Critic

- Attempted source count: `0`
- Assessed source count: `0`
- Skipped source count: `34`
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
- Assessed source count: `34`
- Final role counts: `collection=8, context=14, validation=12`
- Risk flag counts: `ambiguous_disease=1, ambiguous_location=2, complete_source_provenance=16, context_or_background_only=7, cross_reference_required_before_any_data_extraction=1, cumulative_vs_incident_count_confusion_risk_elevated=1, cumulative_vs_incident_count_risk — per disease intelligence warnings, cumulative vs. incident count confusion is a major extraction risk for 2025 measles data; any figures extracted from this article must be annotated with count type and cross-checked against CDC weekly updates=1, data_granularity_moderate: score=0.68; PMC articles may present aggregated or analyzed data rather than raw surveillance counts required by collection spec=1, data_signal_in_source_metadata=34, data_signal_in_source_metadata — title contains a comparative case count claim ('highest since 1991') which is a data signal, but the underlying count and date range must be confirmed against primary CDC source before extraction=1, disease_intelligence_warning: extraction_record_model_still_hantavirus_named — verify schema has been updated to measles-appropriate fields before any ingestion from this source=1, disease_intelligence_warning: source_discovery_not_yet_disease_generic — validate source list manually for measles applicability=1, disease_relevance_unclear=1, geographic_granularity_unclear=2, geographic_scope_americas_not_us_specific=1, independence_unclear=8, independence_unclear — AAP News may be summarizing CDC or state health department data without independent data collection; provenance of any cited figures must be verified=1, independence_unclear_likely_synthesizes_cdc_paho_data=1, local_or_subnational_granularity=18, local_source_matches_task_location=22, location_match_from_planned_query=10, location_relevance_unclear=2, low_authority_relevant_source=5, low_authority_relevant_source — despite strong institutional domain, the news-article format limits primary data authority; do not treat as equivalent to an official CDC MMWR report or state health department advisory=1, low_authority_score_0.48_for_primary_collection_use=1, low_machine_readability=3, lowest_priority_source_tier=1, machine_readable_or_structured=8, missing_publisher=18, missing_publisher — publisher field is null; AAP should be confirmed as publisher to close this metadata gap before archiving=1, missing_publisher_provenance_gap=1, named_publisher=2, national_or_international_granularity=10, national_or_international_granularity — title references national-level case counts ('highest since 1991'); subnational or state-level breakdowns, if present, must be explicitly verified in article body before populating subnational_location fields=1, no_snippet_available: extractable data fields (cases_confirmed, deaths, hospitalizations, subnational_location, date_reported) cannot be confirmed from metadata alone=1, no_snippet_available_content_unverifiable=1, null_snippet_no_preview_of_data_content=1, official_public_health_authority=24, pdf_format_low_machine_readability=1, pdf_or_report_likely_medium_readability=3, primary_or_authoritative_source=24, publication_year_2026_vs_target_window_2025_q1=1, retrospective_or_post_hoc_reporting_risk=1, retrospective_summary_not_contemporaneous_surveillance=1, role_as_context_only: source assigned context role; should not substitute for CDC or state health department primary sources for required_fields extraction=1, rubella_disambiguation_not_applicable_but_monitor — no rubella signal detected in this source, but downstream extraction logic should confirm no 'German measles' or '3-day measles' conflation occurs if article discusses historical comparisons=1, screening_and_critic_disagree=7, screening_and_critic_disagree — deterministic passes produced conflicting signals; the AAP institutional domain may be inflating screening scores relative to the article's actual data authority; human adjudication recommended=1, screening_and_critic_disagree: internal pipeline disagreement on source role or credibility classification; classification may be unstable=1, screening_and_critic_disagree_internal_scoring_tension=1, screening_and_critic_disagree_unresolved=1, secondary_academic_synthesis_not_primary_surveillance_agency=1, secondary_news_or_media_source=8, secondary_news_or_media_source flag present despite authoritative PMC domain — likely a pipeline classification artifact requiring correction=1, secondary_news_or_media_source — AAP News is a journalistic product, not a peer-reviewed article or official surveillance report; case counts extracted from this source must be traced to the cited primary source before ingestion=1, source_disease_relevance:insufficient_text=1, source_disease_relevance:target_disease_match=33, source_metadata_matches_requested_disease=33, source_time_matches_requested_window=15, source_type_mismatch: tagged as news_and_situation_report but domain is pmc.ncbi.nlm.nih.gov — likely peer_reviewed_literature; reclassification recommended=1, speculative_underreporting_framing_in_title=1, standard_web_page=23, structured_data_source=5, subnational_granularity_likely_insufficient=1, task_location_granularity=4, temporal_mismatch_publication_date_2026_vs_collection_window_2025_q1=1, time_window_match_from_planned_query=19, timeliness_uncertainty: publication lag relative to Q1 2025 outbreak period unknown without retrieval; very high PMC ID suggests recent but potentially unfinalized data=1, url_date_outside_target_time_window=1`
- LLM assessed count: `4`
- LLM failure count: `0`
- Needs review count: `4`

### 6.3.5 Source Identity / Publisher Assessment

- Identity assessed source count: `34`
- LLM identity assessed source count: `0`
- Post-fetch identity assessed source count: `28`
- Unknown publisher count: `14`
- Source type counts: `academic_or_peer_reviewed_source=3, background_fact_sheet=1, international_public_health_agency=5, national_public_health_agency=6, news_media=6, official_public_health_agency=7, secondary_aggregator=1, state_or_local_public_health_agency=1, structured_database=1, unknown=3`
- Claim support role counts: `context_only=1, corroboration_support=7, insufficient_information=6, primary_case_claim_support=20`
- Fetch use counts: `fetch_for_context=1, fetch_for_extraction=27, fetch_only_after_review=6`
- Warning counts: `actual_publisher_unknown=18, direct_target_official_fast_path_skips_source_identity=34, publisher_from_search_metadata_unverified=34, search_provider_not_publisher=34`

### 6.4 LLM Structured Extraction

- Extraction mode: `llm_structured_output`
- Eligible chunk count: `816`
- LLM call count: `30`
- LLM success count: `30`
- LLM error count: `0`
- Raw record count: `88`

## 7. 最终抽取 records

- Normalized record count: `88`
- Run quality status: `no_primary_case_dataset_records`
- Final dataset mode: `task_aware_quality_gated_records`
- Quality-gated accepted final dataset count: `0`
- Final case dataset count: `0`
- Zero-case statement count: `0`
- Exposure-monitoring record count: `0`
- Surveillance summary record count: `2`
- Outbreak summary record count: `6`
- Context record count: `6`
- Unclassified observation count: `6`
- Observation dataset view counts: `{'final_case_dataset': 0, 'global_outbreak_event_dataset': 0, 'regional_surveillance_dataset': 0, 'country_year_aggregate_dataset': 0, 'official_alert_dataset': 0, 'probable_case_dataset': 0, 'suspected_case_dataset': 0, 'unspecified_case_dataset': 0, 'death_dataset': 0, 'hospitalization_dataset': 0, 'zero_case_statements': 0, 'exposure_monitoring_records': 0, 'surveillance_summary_records': 2, 'outbreak_summary_records': 6, 'context_records': 6, 'non_primary_observations': 19, 'unclassified_observation_records': 6}`
- Pre-quality-gate record count: `88`
- Quarantined record count: `15`
- Pending review record count: `73`
- Non-primary observation count: `13`
- Final dataset post-review count: `0`
- Primary-case dataset status: `no_primary_case_dataset_records`
- Recommended primary dataset message: `No primary case dataset records were accepted; inspect zero-case, exposure-monitoring, context, and other observation views.`
- Primary-case eligible accepted count: `0`
- Corroborated primary case event count: `0`
- Record inclusion status counts: `{'quarantined_schema_invalid': 1, 'pending_human_review': 73, 'quarantined_outside_scope': 13, 'quarantined_non_primary_observation': 1}`
- Run quality warnings: `['no_primary_case_dataset_records', 'no_corroborated_primary_case_events']`
- Accepted source counts: `none`

No quality-gated records are available to list.
Candidate records, if any, are recorded in the pre-quality, quarantined, and pending-review artifacts.

| Record ID | Date / period | Location | Cases | Deaths | Source | LLM used |
|---|---|---|---|---|---|---|

## 8. Validation 对比

### Claim-level corroboration

- Claim count: `97`
- Claim comparison count: `4656`
- Corroborated event count: `14`
- Corroborated primary case event count: `0`
- Observation type counts: `ambiguous_public_health_observation=6, confirmed_case_record=16, death_record=15, hospitalization_record=19, outbreak_summary=6, unspecified_case_record=35`
- Corroboration status counts: `conflicting_claims=2, insufficient_information=2, single_source_unverified=10`

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

- Human review item count: `119`
- Evaluation review flag count: `0`
- Anomaly review item count: `20`

| Review ID | Type | Related IDs | Reason |
|---|---|---|---|
| review_source_credibility_src_search_3c843cdae62c | source_credibility | src_search_3c843cdae62c | missing_publisher |
| review_source_src_search_3c843cdae62c | source_screening | src_search_3c843cdae62c | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_0132cfa4f779 | source_credibility | src_search_0132cfa4f779 | missing_publisher |
| review_source_src_search_0132cfa4f779 | source_screening | src_search_0132cfa4f779 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_cd5fb2750261 | source_credibility | src_search_cd5fb2750261 | missing_publisher |
| review_source_src_search_cd5fb2750261 | source_screening | src_search_cd5fb2750261 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_78fdd46eb63c | source_credibility | src_search_78fdd46eb63c | missing_publisher |
| review_source_src_search_78fdd46eb63c | source_screening | src_search_78fdd46eb63c | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_f259b36c3067 | source_credibility | src_search_f259b36c3067 | missing_publisher |
| review_source_src_search_f259b36c3067 | source_screening | src_search_f259b36c3067 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_aabc350f7aa0 | source_credibility | src_search_aabc350f7aa0 | This source is a PDF situation report published on the Yale Health / Yale School of Public Health (YSPH) domain, titled "MEASLES – THE AM... |
| review_source_src_search_aabc350f7aa0 | source_screening | src_search_aabc350f7aa0 | Screening and critic disagree on this source; routing to human review for resolution. |

## 9.5 Stage 11 anomaly detection and review application

- Anomaly result count: `31`
- Anomaly severity counts: `high=10, low=11, medium=10`
- Anomaly needs-human-review count: `20`
- Decisions provided: `0`
- Decisions applied: `0`
- Decisions rejected: `0`
- Audit entries: `0`
- Final dataset post-review count: `0`
- Records excluded by review: `0`

| Anomaly ID | Type | Severity | Target | Reason |
|---|---|---|---|---|
| anom_001 | deaths_without_case_reference | low | rec_src_search_8242cbb785a1_002 | deaths present but no comparable case count is available |
| anom_002 | deaths_without_case_reference | low | rec_src_search_6e578fc529e9_002 | deaths present but no comparable case count is available |
| anom_003 | deaths_without_case_reference | low | rec_src_search_fede8be6ac1e_003 | deaths present but no comparable case count is available |
| anom_004 | deaths_without_case_reference | low | rec_src_search_78fdd46eb63c_001 | deaths present but no comparable case count is available |
| anom_005 | deaths_without_case_reference | low | rec_src_search_78fdd46eb63c_002 | deaths present but no comparable case count is available |
| anom_006 | deaths_without_case_reference | low | rec_src_search_78fdd46eb63c_003 | deaths present but no comparable case count is available |
| anom_007 | deaths_without_case_reference | low | rec_src_search_78fdd46eb63c_004 | deaths present but no comparable case count is available |
| anom_008 | deaths_without_case_reference | low | rec_src_search_831265159816_002 | deaths present but no comparable case count is available |
| anom_009 | deaths_without_case_reference | low | rec_src_search_831265159816_014 | deaths present but no comparable case count is available |
| anom_010 | deaths_without_case_reference | low | rec_src_search_831265159816_022 | deaths present but no comparable case count is available |
| anom_011 | deaths_without_case_reference | low | rec_src_search_831265159816_040 | deaths present but no comparable case count is available |
| anom_012 | out_of_scope_count_bearing_record | high | event_007 | Stage 10 validation marked record outside requested scope: outside_time_window |

| Applied decision | Type | Target | Audit IDs | Reason |
|---|---|---|---|---|

## 10. 输出文件

- Run output directory: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_measles_us_2025_q1`
- Collection final dataset: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_measles_us_2025_q1\collection\final_dataset.csv`
- Collection final case dataset: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_measles_us_2025_q1\collection\final_case_dataset.csv`
- Collection zero-case statements: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_measles_us_2025_q1\collection\zero_case_statements.csv`
- Collection exposure-monitoring records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_measles_us_2025_q1\collection\exposure_monitoring_records.csv`
- Collection surveillance summaries: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_measles_us_2025_q1\collection\surveillance_summary_records.csv`
- Collection outbreak summaries: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_measles_us_2025_q1\collection\outbreak_summary_records.csv`
- Collection context records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_measles_us_2025_q1\collection\context_records.csv`
- Collection unclassified observations: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_measles_us_2025_q1\collection\unclassified_observation_records.csv`
- Collection observation dataset summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_measles_us_2025_q1\collection\observation_type_dataset_summary.json`
- Collection pre-quality-gate records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_measles_us_2025_q1\collection\final_dataset_pre_quality_gate.csv`
- Collection quarantined records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_measles_us_2025_q1\collection\quarantined_records.csv`
- Collection pending review records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_measles_us_2025_q1\collection\pending_review_records.csv`
- Collection non-primary observations: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_measles_us_2025_q1\collection\non_primary_observations.csv`
- Collection record inclusion decisions: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_measles_us_2025_q1\collection\record_inclusion_decisions.json`
- Collection final dataset post-review: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_measles_us_2025_q1\collection\final_dataset_post_review.csv`
- Collection anomaly results: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_measles_us_2025_q1\collection\anomaly_results.json`
- Collection human review audit trail: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_measles_us_2025_q1\collection\human_review_audit_trail.json`
- Collection source registry: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_measles_us_2025_q1\collection\source_registry.json`
- Validation mode: `diagnostic_only`
- Validation records source: `state`
- Validation records output: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_measles_us_2025_q1\validation\ground_truth_records.csv`
- Inactive validation records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_measles_us_2025_q1\validation\inactive_validation_records.csv`
- Validation compatibility summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_measles_us_2025_q1\validation\validation_source_compatibility_summary.json`
- Evaluation report CSV: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_measles_us_2025_q1\evaluation\evaluation_report.csv`
- Human-readable report: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_measles_us_2025_q1\workflow_run_report_chinese.md`

## 11. 当前结论

This workflow run executed the configured data collection workflow through the exported graph and artifact pipeline. The user-facing run status is: COMPLETED WITH NO PRIMARY CASE DATASET RECORDS: workflow completed, but no primary case records were accepted into final_dataset.
The run completed technically, but it should not be read as a successful data collection result because no quality-gated accepted records were produced.

- Package metadata says LLM used: `True`
- Contains synthetic fixture data: `False`
- Generated at UTC: `2026-06-25T22:09:38.025815+00:00`

## 12. Workflow visualization artifacts

- Workflow visualization index: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_measles_us_2025_q1\workflow_visualization\index.html`
- Workflow timeline: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_measles_us_2025_q1\workflow_visualization\workflow_timeline.html`
- Evidence flow graph: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_measles_us_2025_q1\workflow_visualization\evidence_flow_graph.html`
- Claim comparison cards: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_measles_us_2025_q1\workflow_visualization\claim_comparison_cards.html`
- Dataset decision flow: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_measles_us_2025_q1\workflow_visualization\dataset_decision_flow.html`
- Human review workflow visualization: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_measles_us_2025_q1\workflow_visualization\human_review_workflow.html`
- Visualization summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_measles_us_2025_q1\workflow_visualization\workflow_visualization_summary.json`
