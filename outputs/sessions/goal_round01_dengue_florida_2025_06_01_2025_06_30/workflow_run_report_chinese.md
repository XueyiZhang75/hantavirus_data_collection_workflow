# data collection workflow Run Report

## 1. 输入任务

Collect dengue cases, deaths, dates, locations, source URLs, source types, and evidence quotes for Florida from 2025-06-01 to 2025-06-30.

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
- Search-derived source candidates: `40`
- Iterative source discovery: `True`
- Iterative search iterations: `2`
- Iterative stop decision: `stop_sufficient`
- Iterative stop reason: `Maximum iteration limit reached (iteration 2 of 2). All four epidemiological weeks within June 2025 (weeks 22–26) are now covered by confirmed FDOH PDF candidates. The primary remaining gap (deaths/hospitalizations) was not resolved by iteration 2 searches, and no snippet from any source confirms dengue deaths or hospitalizations in Florida during June 2025 — this is likely a true data absence rather than a retrieval gap, consistent with Florida's predominantly travel-associated dengue profile. Further searching is not possible within bounds and is unlikely to yield deaths/hospitalization data that does not exist in the public record for this period.`
- Source credibility assessed sources: `40`
- Source credibility role counts: `{'collection': 3, 'excluded': 15, 'context': 16, 'validation': 6}`
- Source identity assessed sources: `40`
- Source identity type counts: `{'official_public_health_agency': 5, 'state_or_local_public_health_agency': 14, 'international_public_health_agency': 6, 'national_public_health_agency': 5, 'structured_database': 2, 'secondary_aggregator': 1, 'news_media': 5, 'background_fact_sheet': 1, 'social_media': 1}`
- Source identity warning counts: `{'search_provider_not_publisher': 40, 'publisher_from_search_metadata_unverified': 40, 'actual_publisher_unknown': 13, 'direct_target_official_fast_path_skips_source_identity': 40}`
- Source discovery method: `live_search_only`
- Disease relevance target: `Dengue`
- Disease relevance source status counts: `{'target_disease_match': 23, 'ambiguous_disease': 14, 'insufficient_text': 3}`
- Disease relevance chunk status counts: `{'target_disease_match': 342, 'ambiguous_disease': 56, 'insufficient_text': 1}`
- Disease relevance record status counts: `{'compatible': 129}`
- Rejected incompatible record count: `0`
- Final route: `finalize`

## 2.5 Run quality status

- User-facing run status: `COMPLETED WITH NO PRIMARY CASE DATASET RECORDS: workflow completed, but no primary case records were accepted into final_dataset.`
- Technical execution status: `completed`
- Run quality status: `no_primary_case_dataset_records`
- Final dataset mode: `task_aware_quality_gated_records`
- Accepted final dataset count: `0`
- Final case dataset count: `0`
- Zero-case statement count: `16`
- Exposure-monitoring record count: `16`
- Surveillance summary record count: `16`
- Outbreak summary record count: `0`
- Context record count: `16`
- Unclassified observation count: `0`
- Observation dataset view counts: `{'final_case_dataset': 0, 'global_outbreak_event_dataset': 0, 'regional_surveillance_dataset': 0, 'country_year_aggregate_dataset': 0, 'official_alert_dataset': 0, 'probable_case_dataset': 0, 'suspected_case_dataset': 0, 'unspecified_case_dataset': 0, 'death_dataset': 0, 'hospitalization_dataset': 0, 'zero_case_statements': 16, 'exposure_monitoring_records': 16, 'surveillance_summary_records': 16, 'outbreak_summary_records': 0, 'context_records': 16, 'non_primary_observations': 32, 'unclassified_observation_records': 0}`
- Pre-quality-gate record count: `43`
- Quarantined record count: `0`
- Pending review record count: `43`
- Non-primary observation count: `32`
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
2. `disease_intelligence_builder` - Built disease intelligence from LLM output (Dengue).
3. `profile_and_schema_setup` - Built active disease profile, collection schema, and source strategy (Dengue, generation_method=disease_intelligence_...
4. `executable_source_planning` - Built executable source plan with 10 planned queries; no searches were executed.
5. `query_strategy_builder` - Built 10 direct_collection search queries from the LLM evidence strategy plan.
6. `source_discovery` - Discovered 40 source candidates using live_search_only.
7. `source_dedup_and_registry` - Built source registry with 40 entries (0 duplicates dropped).
8. `source_screening` - Screened 40 sources using deterministic policy.
9. `source_critic_and_uncertainty_routing` - Critic reviewed 40 sources; 31 ready for fetch, 0 deferred, 12 flagged for human review.
10. `content_fetch_and_parse` - Built 31 fetch requests, produced 31 documents (live_fetch_enabled=True, fixture_documents_enabled=False, fixtures_lo...
11. `document_quality_check` - Quality-checked 31 documents: 29 usable, 0 partial, 0 offline stub, 0 parse deferred, 2 unusable.
12. `evidence_chunking_and_data_presence_flagging` - Chunked 29/31 documents into 399 evidence chunks (388 flagged as containing target data).
13. `structured_extraction` - Built 43 raw records (extraction_mode=llm_structured_output, llm_enabled=True).
14. `schema_validation_and_repair` - Validated 43 raw records: 43 validated (16 need review), 0 rejected.
15. `record_normalization` - Normalized 43/43 records (16 need review).
16. `record_linking` - Linked 43/43 normalized records into 21 candidate events.
17. `cross_source_consistency_check` - Checked 8 multi-record events; found 10 new conflicts and 116 validation results (6 events need review).
18. `quality_gate_routing` - Human review disabled; preserving review flags as audit metadata and routing to final_data_package_builder.
19. `final_data_package_builder` - Assembled hardened FinalDataPackage from current state.

## 4. 数据源分工

| Role | Source ID | Publisher / title | Credibility | Final decision | Fetch ready |
|---|---|---|---|---|---|
| context_only | src_search_538a1d433fd1 | Pan American Health Organization / Dengue Epidemiological Situation in the Region of the Americas - Epidemiological Week 20, 2026 - PAHO/... | medium (0.7048) | needs_human_review | False |
| context_only | src_search_304300adfbfc | / Florida reports 1st dengue local transmission case of 2025 | needs_review (0.5686) | needs_human_review | False |
| context_only | src_search_ba28ea669df7 | / Report finds 359% rise in U.S. cases of dengue / AHA News | needs_review (0.484) | needs_human_review | False |
| context_only | src_search_19e4b6b2e376 | / News Release – DOH Reports 14th Travel-Related Dengue Virus Case of 2025 / Governor Josh Green, M.D. | medium (0.6712) | needs_human_review | False |
| context_only | src_search_051cb6779b0a | / Imported Dengue Case Numbers and Local Climatic Patterns Are ... | low (0.484) | needs_human_review | False |
| context_only | src_search_fbcc657a07a3 | / Dengue fever Florida. Symptoms watch for. - Sarasota Herald-Tribune | low (0.5343) | needs_human_review | False |
| context_only | src_search_6cc03a0a2cfe | / Brevard topped the 2025 locally acquired dengue fever cases, with ... | high (0.7823) | include_for_content_fetch | False |
| context_only | src_search_302edcfa2635 | / What is dengue? Mosquito-borne illness reported in Florida counties | medium (0.5735) | needs_human_review | False |
| context_only | src_search_74e6da22c7aa | National Center for Biotechnology Information / Fatal Dengue Acquired in Florida - PMC - NIH | medium (0.7151) | needs_human_review | False |
| context_only | src_search_be4bdb98b361 | / Florida Dengue travel cases exceed this year's expectations, data ... | medium (0.5551) | needs_human_review | False |
| other | src_search_53763309bf94 | / Dengue in Florida: What to know - Emerging Pathogens Institute | high (0.8615) | include_for_content_fetch | True |
| other | src_search_19aff7ba1bc3 | floridahealth.gov / [PDF] Florida Arbovirus Surveillance | excluded (0.6183) | include_for_content_fetch | True |
| other | src_search_84acc76573c8 | floridahealth.gov / [PDF] Florida Arbovirus Surveillance | excluded (0.6183) | include_for_content_fetch | True |
| other | src_search_b1f2ac4b0ced | floridahealth.gov / [PDF] Florida Arbovirus Surveillance | excluded (0.5999) | include_for_content_fetch | True |
| other | src_search_1298a67f3fad | floridahealth.gov / [PDF] Florida Arbovirus Surveillance | excluded (0.6183) | include_for_content_fetch | True |
| other | src_search_b833a635676e | World Health Organization / [PDF] Dengue Situation Update 725 - 10 July 2025 | medium (0.7472) | include_for_content_fetch | True |
| other | src_search_cab7ecda0f44 | / Florida Arbovirus Reports - Pasco County Mosquito Control District | medium (0.6479) | include_for_content_fetch | True |
| other | src_search_f8170b43e1cb | floridahealth.gov / Arbovirus Surveillance - Florida Department of Health | excluded (0.6759) | include_for_content_fetch | True |
| other | src_search_6aa02e4e4389 | floridahealth.gov / [PDF] Florida Arbovirus Surveillance | excluded (0.6066) | include_for_content_fetch | True |
| other | src_search_526c2e2794af | Centers for Disease Control and Prevention / Using Routine Surveillance Data to Assess Dengue Virus Transmission Risk in Travelers Return... | high (0.8048) | include_for_content_fetch | True |
| other | src_search_10be9e5758bd | Centers for Disease Control and Prevention / Data and Statistics on Dengue in the United States - CDC | high (0.784) | include_for_content_fetch | True |
| other | src_search_fbce10f4ecc0 | Centers for Disease Control and Prevention / Ongoing Risk of Dengue Virus Infections and Updated Testing Recommendations in the United St... | high (0.784) | include_for_content_fetch | True |
| other | src_search_61d84b08b5f6 | Centers for Disease Control and Prevention / Historic Data (2010-2025) / Dengue / CDC | high (0.8232) | include_for_content_fetch | True |
| other | src_search_1b7b98980b61 | Centers for Disease Control and Prevention / Current Year Data (2026) / Dengue / CDC | high (0.8048) | include_for_content_fetch | True |
| other | src_search_1e7b9bff1f18 | European Centre for Disease Prevention and Control / Dengue worldwide overview - ECDC - European Union | high (0.784) | include_for_content_fetch | True |
| other | src_search_ca32feb87a96 | Pan American Health Organization / PAHO updates dengue situation in the Americas, recommends strengthened surveillance and health system... | high (0.8048) | include_for_content_fetch | True |
| other | src_search_ff7b38a2792d | Pan American Health Organization / Situation reports - PAHO/WHO / Pan American Health Organization | medium (0.5888) | include_for_content_fetch | True |
| other | src_search_60f9228c083d | Pan American Health Organization / Dengue Multi-Country Outbreak - PAHO/WHO | high (0.8048) | include_for_content_fetch | True |
| other | src_search_41068fc0d551 | globalhealthreports.health.ny.gov / Contents Dengue Region of the Americas – PAHO Issues ... | medium (0.7264) | include_for_content_fetch | True |
| other | src_search_5aec5f976eeb | National Center for Biotechnology Information / Dengue 2025 global surge: urgent call to bolster hospital ... - PMC | high (0.8232) | include_for_content_fetch | True |
| other | src_search_ce6ce02a80f2 | floridahealth.gov / [PDF] Florida Arbovirus Surveillance | excluded (0.6183) | include_for_content_fetch | True |
| other | src_search_e1219da5b350 | floridahealth.gov / [PDF] Florida Arbovirus Surveillance | excluded (0.6183) | include_for_content_fetch | True |
| other | src_search_752899844c7d | floridahealth.gov / [PDF] Florida Arbovirus Surveillance | excluded (0.6183) | include_for_content_fetch | True |
| other | src_search_0b6168dbc1ac | floridahealth.gov / [PDF] Florida Arbovirus Surveillance | excluded (0.6183) | include_for_content_fetch | True |
| other | src_search_24c5b0ef4721 | floridahealth.gov / [PDF] Florida Arbovirus Surveillance | excluded (0.6183) | include_for_content_fetch | True |
| other | src_search_1924f0a4657b | floridahealth.gov / [PDF] Florida Arbovirus Surveillance | excluded (0.6183) | include_for_content_fetch | True |
| other | src_search_27e7d88d8c1f | / [PDF] Utah Arboviral Surveillance Weekly Report__MMWR30_2025 | excluded (0.5352) | include_for_content_fetch | True |
| other | src_search_7c5388af6a44 | / Publications - SECVBD | excluded (0.6479) | include_for_content_fetch | True |
| other | src_search_31cd9572c4dd | globalhealthreports.health.ny.gov / [PDF] Second Locally Acquired Case of 2025 Reported in Florida | excluded (0.6183) | include_for_content_fetch | True |
| other | src_search_d0df6d007394 | Centers for Disease Control and Prevention / CDC issues dengue fever warning for spring, summer travelers | medium (0.772) | include_for_content_fetch | True |

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
- Quality status counts: `unusable=2, usable=29`
- Validation-reserved skipped from fetch: `[]`

| Source ID | Provider | Fetch status | HTTP | Parse | Parser | Quality | Text chars | Tables |
|---|---|---|---|---|---|---|---|---|
| src_search_53763309bf94 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 12605 | 0 |
| src_search_b833a635676e | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 22722 | 0 |
| src_search_f8170b43e1cb | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 61678 | 0 |
| src_search_cab7ecda0f44 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 6450 | 0 |
| src_search_19aff7ba1bc3 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 10329 | 0 |
| src_search_ce6ce02a80f2 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 11064 | 0 |
| src_search_84acc76573c8 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 10750 | 0 |
| src_search_1298a67f3fad | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 15965 | 0 |
| src_search_e1219da5b350 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 11173 | 0 |
| src_search_752899844c7d | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 12018 | 0 |
| src_search_0b6168dbc1ac | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 14878 | 0 |
| src_search_24c5b0ef4721 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 20621 | 0 |
| src_search_b1f2ac4b0ced | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 17814 | 0 |
| src_search_61d84b08b5f6 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 2412 | 0 |
| src_search_526c2e2794af | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 47547 | 0 |
| src_search_1b7b98980b61 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 2428 | 0 |
| src_search_10be9e5758bd | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 1764 | 0 |
| src_search_fbce10f4ecc0 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 7358 | 0 |
| src_search_1e7b9bff1f18 | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 10898 | 0 |
| src_search_7c5388af6a44 | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 42614 | 0 |
| src_search_1924f0a4657b | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 20134 | 0 |
| src_search_6aa02e4e4389 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 10272 | 0 |
| src_search_27e7d88d8c1f | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 10950 | 0 |
| src_search_5aec5f976eeb | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 16408 | 0 |
| src_search_ca32feb87a96 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 9518 | 0 |
| src_search_60f9228c083d | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 23170 | 0 |
| src_search_6cc03a0a2cfe | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 12938 | 0 |
| src_search_d0df6d007394 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 10280 | 0 |
| src_search_41068fc0d551 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 21359 | 0 |
| src_search_31cd9572c4dd | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 40508 | 0 |
| src_search_ff7b38a2792d | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 11069 | 0 |

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
- Stop reason: `Maximum iteration limit reached (iteration 2 of 2). All four epidemiological weeks within June 2025 (weeks 22–26) are now covered by confirmed FDOH PDF candidates. The primary remaining gap (deaths/hospitalizations) was not resolved by iteration 2 searches, and no snippet from any source confirms dengue deaths or hospitalizations in Florida during June 2025 — this is likely a true data absence rather than a retrieval gap, consistent with Florida's predominantly travel-associated dengue profile. Further searching is not possible within bounds and is unlikely to yield deaths/hospitalization data that does not exist in the public record for this period.`
- Query source counts: `{'iterative_llm_initial_search_plan': 4, 'iterative_llm_refinement': 4}`
- Iteration query counts: `{'1': 4, '2': 4}`

### 6.2 LLM Source Critic

- Attempted source count: `0`
- Assessed source count: `0`
- Skipped source count: `40`
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
- Assessed source count: `40`
- Final role counts: `collection=3, context=16, excluded=15, validation=6`
- Risk flag counts: `CRITICAL_TEMPORAL_MISMATCH: URL references Epidemiological Week 20 of 2026; collection window is June 2025 — one-year discrepancy requires human verification before any data extraction=1, FLORIDA_ATTRIBUTION_UNCONFIRMED: No snippet available to verify whether Florida is explicitly named; disease intelligence summary warns against assuming Florida attribution from U.S. national counts=1, GEOGRAPHIC_GRANULARITY_INSUFFICIENT_FOR_PRIMARY_USE: PAHO Americas-level reports aggregate at national/regional scale; Florida subnational data is unlikely to be explicitly disaggregated=1, NULL_SNIPPET: Absence of snippet prevents any pre-extraction textual verification of content relevance to target geography and time window=1, QUERY_URL_YEAR_MISMATCH: Search query targeted June 2025 but returned a document URL dated 2026 — possible stale search index, URL construction error, or misattributed result=1, SCREENING_AND_CRITIC_DISAGREE: Deterministic pipeline flagged internal assessment divergence — LLM review confirms this source warrants elevated scrutiny=1, VALIDATION_ROLE_TEMPORALLY_COMPROMISED: Even as a validation source, the 2026 document date renders it non-applicable to the June 2025 collection window unless the date discrepancy is resolved=1, ambiguous_disease=17, ambiguous_disease_signal_in_source_metadata=14, complete_source_provenance=27, context_or_background_only=10, contradictory_risk_flags:screening_and_critic_disagree=1, data_not_directly_usable_for_florida_subnational_fields=1, data_signal_in_source_metadata=40, disease_relevance_unclear=3, do_not_extract_without_primary_source_verification=1, geographic_mismatch:source_covers_hawaii_not_florida=1, independence_score_low_likely_derivative_of_official_report=1, independence_unclear=5, independence_unclear_likely_relay_of_cdc_or_fdoh_report=1, local_or_subnational_granularity=21, local_source_matches_task_location=22, location_match_from_planned_query=18, low_authority_relevant_source=6, low_machine_readability=15, missing_publisher=13, missing_publisher_metadata=1, national_granularity_not_florida_specific=1, national_or_international_granularity=18, news_release_format:low_data_extractability_for_required_fields=1, official_public_health_authority=34, pdf_or_report_likely_medium_readability=15, possible_derivative_or_syndicated_source=1, primary_or_authoritative_source=34, publisher_identity_unresolved_null_field=1, query_surfaced_off_target_geography:florida_query_returned_hawaii_result=1, role_confirmed_as_context_not_collection_support=1, screening_and_critic_disagree=10, screening_and_critic_disagree_internal_pipeline_conflict=1, secondary_news_aggregator_not_primary_surveillance_authority=1, secondary_news_or_media_source=8, source_disease_relevance:ambiguous_disease=14, source_disease_relevance:insufficient_text=3, source_disease_relevance:target_disease_match=23, source_metadata_matches_requested_disease=23, source_time_matches_requested_window=21, standard_web_page=25, substack_self_publishing_platform_no_editorial_gatekeeping=1, task_location_granularity=1, time_window_match_from_planned_query=19, travel_related_case_only:not_locally_acquired=1, underlying_primary_source_unknown_requires_tracing=1, url_date_anomaly_future_date_2026_in_2025_collection_window=1, wrong_jurisdiction_for_collection_task=1`
- LLM assessed count: `4`
- LLM failure count: `0`
- Needs review count: `2`

### 6.3.5 Source Identity / Publisher Assessment

- Identity assessed source count: `40`
- LLM identity assessed source count: `0`
- Post-fetch identity assessed source count: `31`
- Unknown publisher count: `12`
- Source type counts: `background_fact_sheet=1, international_public_health_agency=6, national_public_health_agency=5, news_media=5, official_public_health_agency=5, secondary_aggregator=1, social_media=1, state_or_local_public_health_agency=14, structured_database=2`
- Claim support role counts: `context_only=6, corroboration_support=6, insufficient_information=1, primary_case_claim_support=27`
- Fetch use counts: `fetch_for_context=6, fetch_for_extraction=33, fetch_only_after_review=1`
- Warning counts: `actual_publisher_unknown=13, direct_target_official_fast_path_skips_source_identity=40, publisher_from_search_metadata_unverified=40, search_provider_not_publisher=40`

### 6.4 LLM Structured Extraction

- Extraction mode: `llm_structured_output`
- Eligible chunk count: `355`
- LLM call count: `30`
- LLM success count: `30`
- LLM error count: `0`
- Raw record count: `43`

## 7. 最终抽取 records

- Normalized record count: `43`
- Run quality status: `no_primary_case_dataset_records`
- Final dataset mode: `task_aware_quality_gated_records`
- Quality-gated accepted final dataset count: `0`
- Final case dataset count: `0`
- Zero-case statement count: `16`
- Exposure-monitoring record count: `16`
- Surveillance summary record count: `16`
- Outbreak summary record count: `0`
- Context record count: `16`
- Unclassified observation count: `0`
- Observation dataset view counts: `{'final_case_dataset': 0, 'global_outbreak_event_dataset': 0, 'regional_surveillance_dataset': 0, 'country_year_aggregate_dataset': 0, 'official_alert_dataset': 0, 'probable_case_dataset': 0, 'suspected_case_dataset': 0, 'unspecified_case_dataset': 0, 'death_dataset': 0, 'hospitalization_dataset': 0, 'zero_case_statements': 16, 'exposure_monitoring_records': 16, 'surveillance_summary_records': 16, 'outbreak_summary_records': 0, 'context_records': 16, 'non_primary_observations': 32, 'unclassified_observation_records': 0}`
- Pre-quality-gate record count: `43`
- Quarantined record count: `0`
- Pending review record count: `43`
- Non-primary observation count: `32`
- Final dataset post-review count: `0`
- Primary-case dataset status: `no_primary_case_dataset_records`
- Recommended primary dataset message: `No primary case dataset records were accepted; inspect zero-case, exposure-monitoring, context, and other observation views.`
- Primary-case eligible accepted count: `0`
- Corroborated primary case event count: `0`
- Record inclusion status counts: `{'pending_human_review': 43}`
- Run quality warnings: `['no_primary_case_dataset_records', 'no_corroborated_primary_case_events']`
- Accepted source counts: `none`

No quality-gated records are available to list.
Candidate records, if any, are recorded in the pre-quality, quarantined, and pending-review artifacts.

| Record ID | Date / period | Location | Cases | Deaths | Source | LLM used |
|---|---|---|---|---|---|---|

## 8. Validation 对比

### Claim-level corroboration

- Claim count: `43`
- Claim comparison count: `903`
- Corroborated event count: `7`
- Corroborated primary case event count: `0`
- Observation type counts: `surveillance_summary=16, unspecified_case_record=11, zero_case_statement=16`
- Corroboration status counts: `conflicting_claims=1, insufficient_information=1, single_source_unverified=5`

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

- Human review item count: `103`
- Evaluation review flag count: `0`
- Anomaly review item count: `18`

| Review ID | Type | Related IDs | Reason |
|---|---|---|---|
| review_source_credibility_src_search_53763309bf94 | source_credibility | src_search_53763309bf94 | missing_publisher |
| review_source_src_search_53763309bf94 | source_screening | src_search_53763309bf94 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_538a1d433fd1 | source_credibility | src_search_538a1d433fd1 | This source is a PAHO/WHO international organization report on dengue epidemiology in the Americas, which carries very high institutional... |
| review_source_src_search_538a1d433fd1 | source_screening | src_search_538a1d433fd1 | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_credibility_src_search_304300adfbfc | source_credibility | src_search_304300adfbfc | This source is a Substack-hosted article from "Outbreak News Today," a secondary news/media outlet rather than an official public health... |
| review_source_src_search_304300adfbfc | source_screening | src_search_304300adfbfc | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_credibility_src_search_ba28ea669df7 | source_credibility | src_search_ba28ea669df7 | This source is an AHA (American Hospital Association) news headline page (aha.org), which is a secondary news/media aggregator rather tha... |
| review_source_src_search_ba28ea669df7 | source_screening | src_search_ba28ea669df7 | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_src_search_19e4b6b2e376 | source_screening | src_search_19e4b6b2e376 | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_src_search_051cb6779b0a | source_screening | src_search_051cb6779b0a | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_src_search_fbcc657a07a3 | source_screening | src_search_fbcc657a07a3 | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_src_search_6cc03a0a2cfe | source_screening | src_search_6cc03a0a2cfe | Screening and critic disagree on this source; routing to human review for resolution. |

## 9.5 Stage 11 anomaly detection and review application

- Anomaly result count: `18`
- Anomaly severity counts: `high=14, medium=4`
- Anomaly needs-human-review count: `18`
- Decisions provided: `0`
- Decisions applied: `0`
- Decisions rejected: `0`
- Audit entries: `0`
- Final dataset post-review count: `0`
- Records excluded by review: `0`

| Anomaly ID | Type | Severity | Target | Reason |
|---|---|---|---|---|
| anom_001 | out_of_scope_count_bearing_record | high | event_015 | Stage 10 validation marked record outside requested scope: outside_time_window |
| anom_002 | out_of_scope_count_bearing_record | high | event_002 | Stage 10 validation marked record outside requested scope: outside_time_window |
| anom_003 | out_of_scope_count_bearing_record | high | event_001 | Stage 10 validation marked record outside requested scope: outside_time_window |
| anom_004 | out_of_scope_count_bearing_record | high | event_002 | Stage 10 validation marked record outside requested scope: outside_time_window |
| anom_005 | validation_conflict_anomaly | high | event_002 | Validation result is a conflict: Sources report substantially different numeric values for the same linked event. |
| anom_006 | validation_conflict_anomaly | high | event_003 | Validation result is a conflict: Sources report substantially different numeric values for the same linked event. |
| anom_007 | validation_conflict_anomaly | high | event_003 | Validation result is a conflict: Sources may use different case definitions or reporting categories. |
| anom_008 | validation_conflict_anomaly | high | event_005 | Validation result is a conflict: Sources report substantially different numeric values for the same linked event. |
| anom_009 | validation_conflict_anomaly | high | event_005 | Validation result is a conflict: Sources may use different case definitions or reporting categories. |
| anom_010 | validation_conflict_anomaly | high | event_006 | Validation result is a conflict: Sources report substantially different numeric values for the same linked event. |
| anom_011 | validation_conflict_anomaly | high | event_007 | Validation result is a conflict: Sources report substantially different numeric values for the same linked event. |
| anom_012 | validation_conflict_anomaly | high | event_016 | Validation result is a conflict: Sources may use different case definitions or reporting categories. |

| Applied decision | Type | Target | Audit IDs | Reason |
|---|---|---|---|---|

## 10. 输出文件

- Run output directory: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_dengue_florida_2025_06_01_2025_06_30`
- Collection final dataset: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_dengue_florida_2025_06_01_2025_06_30\collection\final_dataset.csv`
- Collection final case dataset: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_dengue_florida_2025_06_01_2025_06_30\collection\final_case_dataset.csv`
- Collection zero-case statements: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_dengue_florida_2025_06_01_2025_06_30\collection\zero_case_statements.csv`
- Collection exposure-monitoring records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_dengue_florida_2025_06_01_2025_06_30\collection\exposure_monitoring_records.csv`
- Collection surveillance summaries: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_dengue_florida_2025_06_01_2025_06_30\collection\surveillance_summary_records.csv`
- Collection outbreak summaries: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_dengue_florida_2025_06_01_2025_06_30\collection\outbreak_summary_records.csv`
- Collection context records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_dengue_florida_2025_06_01_2025_06_30\collection\context_records.csv`
- Collection unclassified observations: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_dengue_florida_2025_06_01_2025_06_30\collection\unclassified_observation_records.csv`
- Collection observation dataset summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_dengue_florida_2025_06_01_2025_06_30\collection\observation_type_dataset_summary.json`
- Collection pre-quality-gate records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_dengue_florida_2025_06_01_2025_06_30\collection\final_dataset_pre_quality_gate.csv`
- Collection quarantined records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_dengue_florida_2025_06_01_2025_06_30\collection\quarantined_records.csv`
- Collection pending review records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_dengue_florida_2025_06_01_2025_06_30\collection\pending_review_records.csv`
- Collection non-primary observations: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_dengue_florida_2025_06_01_2025_06_30\collection\non_primary_observations.csv`
- Collection record inclusion decisions: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_dengue_florida_2025_06_01_2025_06_30\collection\record_inclusion_decisions.json`
- Collection final dataset post-review: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_dengue_florida_2025_06_01_2025_06_30\collection\final_dataset_post_review.csv`
- Collection anomaly results: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_dengue_florida_2025_06_01_2025_06_30\collection\anomaly_results.json`
- Collection human review audit trail: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_dengue_florida_2025_06_01_2025_06_30\collection\human_review_audit_trail.json`
- Collection source registry: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_dengue_florida_2025_06_01_2025_06_30\collection\source_registry.json`
- Validation mode: `diagnostic_only`
- Validation records source: `state`
- Validation records output: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_dengue_florida_2025_06_01_2025_06_30\validation\ground_truth_records.csv`
- Inactive validation records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_dengue_florida_2025_06_01_2025_06_30\validation\inactive_validation_records.csv`
- Validation compatibility summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_dengue_florida_2025_06_01_2025_06_30\validation\validation_source_compatibility_summary.json`
- Evaluation report CSV: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_dengue_florida_2025_06_01_2025_06_30\evaluation\evaluation_report.csv`
- Human-readable report: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_dengue_florida_2025_06_01_2025_06_30\workflow_run_report_chinese.md`

## 11. 当前结论

This workflow run executed the configured data collection workflow through the exported graph and artifact pipeline. The user-facing run status is: COMPLETED WITH NO PRIMARY CASE DATASET RECORDS: workflow completed, but no primary case records were accepted into final_dataset.
The run completed technically, but it should not be read as a successful data collection result because no quality-gated accepted records were produced.

- Package metadata says LLM used: `True`
- Contains synthetic fixture data: `False`
- Generated at UTC: `2026-06-25T14:25:09.130551+00:00`

## 12. Workflow visualization artifacts

- Workflow visualization index: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_dengue_florida_2025_06_01_2025_06_30\workflow_visualization\index.html`
- Workflow timeline: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_dengue_florida_2025_06_01_2025_06_30\workflow_visualization\workflow_timeline.html`
- Evidence flow graph: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_dengue_florida_2025_06_01_2025_06_30\workflow_visualization\evidence_flow_graph.html`
- Claim comparison cards: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_dengue_florida_2025_06_01_2025_06_30\workflow_visualization\claim_comparison_cards.html`
- Dataset decision flow: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_dengue_florida_2025_06_01_2025_06_30\workflow_visualization\dataset_decision_flow.html`
- Human review workflow visualization: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_dengue_florida_2025_06_01_2025_06_30\workflow_visualization\human_review_workflow.html`
- Visualization summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round01_dengue_florida_2025_06_01_2025_06_30\workflow_visualization\workflow_visualization_summary.json`
