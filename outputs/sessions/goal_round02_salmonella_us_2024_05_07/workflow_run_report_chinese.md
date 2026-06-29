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
- Source search executed queries: `8`
- Search-derived source candidates: `50`
- Iterative source discovery: `True`
- Iterative search iterations: `2`
- Iterative stop decision: `stop_sufficient`
- Iterative stop reason: `Max iterations reached (iteration_index=2, max_iterations=2). Evidence coverage is substantively sufficient: three distinct in-scope Salmonella outbreak events (cucumbers June 2024, backyard poultry May 2024, eggs May–July 2024) are each covered by at least one authoritative CDC or FDA source candidate with quantitative epidemiological data. FSIS and state-level sources also surfaced. No critical unresolved gaps remain that would justify additional search within bounds.`
- Source credibility assessed sources: `50`
- Source credibility role counts: `{'collection': 14, 'context': 27, 'excluded': 4, 'search_endpoint': 1, 'collection_support': 4}`
- Source identity assessed sources: `50`
- Source identity type counts: `{'official_public_health_agency': 18, 'national_public_health_agency': 15, 'social_media': 7, 'academic_or_peer_reviewed_source': 3, 'state_or_local_public_health_agency': 2, 'news_media': 4, 'secondary_aggregator': 1}`
- Source identity warning counts: `{'search_provider_not_publisher': 50, 'publisher_from_search_metadata_unverified': 50, 'actual_publisher_unknown': 30, 'direct_target_official_fast_path_skips_source_identity': 50}`
- Source discovery method: `live_search_only`
- Disease relevance target: `Salmonella`
- Disease relevance source status counts: `{'target_disease_match': 33, 'ambiguous_disease': 11, 'insufficient_text': 6}`
- Disease relevance chunk status counts: `{'target_disease_match': 522, 'ambiguous_disease': 288, 'unrelated_disease': 8, 'related_context_only': 1, 'insufficient_text': 1}`
- Disease relevance record status counts: `{'compatible': 57}`
- Rejected incompatible record count: `0`
- Final route: `finalize`

## 2.5 Run quality status

- User-facing run status: `PARTIAL: accepted records produced, but some records were quarantined.`
- Technical execution status: `completed`
- Run quality status: `partial_with_quarantined_records`
- Final dataset mode: `task_aware_quality_gated_records`
- Accepted final dataset count: `5`
- Final case dataset count: `3`
- Zero-case statement count: `0`
- Exposure-monitoring record count: `0`
- Surveillance summary record count: `0`
- Outbreak summary record count: `0`
- Context record count: `1`
- Unclassified observation count: `0`
- Observation dataset view counts: `{'final_case_dataset': 3, 'global_outbreak_event_dataset': 0, 'regional_surveillance_dataset': 0, 'country_year_aggregate_dataset': 0, 'official_alert_dataset': 0, 'probable_case_dataset': 0, 'suspected_case_dataset': 0, 'unspecified_case_dataset': 3, 'death_dataset': 3, 'hospitalization_dataset': 2, 'zero_case_statements': 0, 'exposure_monitoring_records': 0, 'surveillance_summary_records': 0, 'outbreak_summary_records': 0, 'context_records': 1, 'non_primary_observations': 3, 'unclassified_observation_records': 0}`
- Pre-quality-gate record count: `19`
- Quarantined record count: `4`
- Pending review record count: `10`
- Non-primary observation count: `0`
- Final dataset post-review count: `5`
- Primary-case dataset status: `primary_case_records_present`
- Recommended primary dataset message: `Primary case dataset records are available in final_case_dataset.`
- Primary-case eligible accepted count: `3`
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
6. `source_discovery` - Discovered 50 source candidates using live_search_only.
7. `source_dedup_and_registry` - Built source registry with 50 entries (0 duplicates dropped).
8. `source_screening` - Screened 50 sources using deterministic policy.
9. `source_critic_and_uncertainty_routing` - Critic reviewed 50 sources; 45 ready for fetch, 0 deferred, 27 flagged for human review.
10. `content_fetch_and_parse` - Built 45 fetch requests, produced 45 documents (live_fetch_enabled=True, fixture_documents_enabled=False, fixtures_lo...
11. `document_quality_check` - Quality-checked 45 documents: 39 usable, 1 partial, 0 offline stub, 0 parse deferred, 5 unusable.
12. `evidence_chunking_and_data_presence_flagging` - Chunked 40/45 documents into 820 evidence chunks (764 flagged as containing target data).
13. `structured_extraction` - Built 19 raw records (extraction_mode=llm_structured_output, llm_enabled=True).
14. `schema_validation_and_repair` - Validated 19 raw records: 19 validated (0 need review), 0 rejected.
15. `record_normalization` - Normalized 19/19 records (0 need review).
16. `record_linking` - Linked 19/19 normalized records into 15 candidate events.
17. `cross_source_consistency_check` - Checked 3 multi-record events; found 1 new conflicts and 54 validation results (0 events need review).
18. `quality_gate_routing` - Human review disabled; preserving review flags as audit metadata and routing to final_data_package_builder.
19. `final_data_package_builder` - Assembled hardened FinalDataPackage from current state.

## 4. 数据源分工

| Role | Source ID | Publisher / title | Credibility | Final decision | Fetch ready |
|---|---|---|---|---|---|
| context_only | src_search_712e948506d7 | Centers for Disease Control and Prevention / At least 16 illnesses have been reported, with six hospitalizations ... | medium (0.5639) | include_for_content_fetch | False |
| context_only | src_search_b51a5ab7bcd8 | Centers for Disease Control and Prevention / Salmonella Outbreak Update | medium (0.7639) | include_for_content_fetch | False |
| context_only | src_search_34a66c01ab1b | / As of Friday, at least a dozen products related to the recall have ... | high (0.4768) | include_for_content_fetch | False |
| context_only | src_search_d75a6eda1263 | / WBFF FOX 45 - A major food brand issued a voluntary recall... | high (0.4928) | include_for_content_fetch | False |
| context_only | src_search_1aa919b25056 | / There are 173 new cases and 50 new hospitalizations ... - Facebook | medium (0.5639) | include_for_content_fetch | False |
| context_only | src_search_15fc5f8d47e2 | / Food for Thought 2025 | needs_review (0.344) | needs_human_review | False |
| context_only | src_search_397f647da895 | / Cucumbers linked to salmonella outbreak in 31 states - abc7NY | needs_review (0.5551) | needs_human_review | False |
| context_only | src_search_fe233d5728e3 | Centers for Disease Control and Prevention / Investigation Update: Salmonella Outbreak, August 2025 / Salmonella Infection / CDC | medium (0.7359) | include_for_content_fetch | True |
| context_only | src_search_76394e8294e0 | / List of foodborne illness outbreaks in the United States - Wikipedia | needs_review (0.3991) | needs_human_review | False |
| context_only | src_search_db7489def0f9 | / Recalls & Public Health Alerts / Food Safety and Inspection Service | needs_review (0.5079) | needs_human_review | False |
| context_only | src_search_e48f82c4451a | / The 10 Riskiest Foods to Eat Right Now, According to Food Safety ... | low (0.344) | needs_human_review | False |
| context_only | src_search_b1fd759a3dac | / Eggs linked to salmonella outbreak sold by Milo's Poultry Farms in ... | medium (0.6928) | include_for_content_fetch | False |
| context_only | src_search_efda92ce4d43 | / USDA withdraws proposed rule on salmonella-contaminated poultry | medium (0.7314) | include_for_content_fetch | False |
| other | src_search_33733b13ba13 | / Outbreak Investigation of Salmonella: Cucumbers (June 2024) - FDA | high (0.8823) | include_for_content_fetch | True |
| other | src_search_85d5f7f41e48 | Centers for Disease Control and Prevention / Investigation Update: Salmonella Outbreaks, May 2025 / Salmonella Infection / CDC | high (0.8759) | include_for_content_fetch | True |
| other | src_search_a5bc6c5400a7 | Centers for Disease Control and Prevention / Investigation Update: Salmonella Outbreak, Eggs - September 2024 / Salmonella Infection / CDC | high (0.8943) | include_for_content_fetch | True |
| other | src_search_e0c58bcf769a | Centers for Disease Control and Prevention / Salmonella Outbreak Linked to Cucumbers - June 2024 - CDC | high (0.8943) | include_for_content_fetch | True |
| other | src_search_057e55c5d693 | Centers for Disease Control and Prevention / Investigation Update: Salmonella Outbreak, July 2025 / Salmonella Infection / CDC | high (0.8759) | include_for_content_fetch | True |
| other | src_search_8207a084046e | CIDRAP / Report: Illnesses from contaminated food increased in 2024, severe cases doubled / CIDRAP | excluded (0.6943) | include_for_content_fetch | True |
| other | src_search_793a8dd9911b | / Outbreak Investigation of Salmonella: Cucumbers (November 2024) | high (0.8112) | include_for_content_fetch | True |
| other | src_search_a37f3105d277 | / FDA Recalls: July 2024 Mid-Month Check In / Contagion Live | excluded (0.6112) | include_for_content_fetch | True |
| other | src_search_843a36718811 | / FSIS Issues Public Health Alert for Various Meat and Poultry Products Containing FDA-Regulated Dairy Products That Have Been Recalled D... | high (0.8431) | include_for_content_fetch | True |
| other | src_search_1f2ad0f9f937 | / Food Recalls US – Complete List for Parents - KidsAdvisory | excluded (0.6479) | include_for_content_fetch | True |
| other | src_search_139b1ba6fd05 | / Recalls and Outbreaks / FoodSafety.gov | excluded (0.5768) | include_for_content_fetch | True |
| other | src_search_1a43f41dad6f | Centers for Disease Control and Prevention / Investigation Update: Salmonella Outbreaks, April 2026 / Salmonella Infection / CDC | high (0.8759) | include_for_content_fetch | True |
| other | src_search_bebdb72f384b | doh.wa.gov / 2026 Extensively Drug-Resistant Salmonella Multistate Outbreak linked to Moringa Powder Capsules / Washington State Departme... | high (0.8048) | include_for_content_fetch | True |
| other | src_search_58cd0c44b219 | Centers for Disease Control and Prevention / Investigation Update: Salmonella Outbreak, January 2026 / Salmonella Infection / CDC | high (0.8759) | include_for_content_fetch | True |
| other | src_search_814630932f43 | Centers for Disease Control and Prevention / Public Health Alert Issued Amid January 2026 Salmonella Outbreak | high (0.7928) | include_for_content_fetch | True |
| other | src_search_25738f18fb27 | / Salmonella outbreak detected in 29 U.S. states as health officials ... | high (0.8639) | include_for_content_fetch | True |
| other | src_search_8d0aef1a7c3b | / Salmonellosis, USA - BEACON | high (0.8431) | include_for_content_fetch | True |
| other | src_search_341f243cf7df | Centers for Disease Control and Prevention / Investigation Update: Salmonella Outbreak, Backyard Poultry - CDC | high (0.8642) | include_for_content_fetch | True |
| other | src_search_b85f60e7676f | Centers for Disease Control and Prevention / Salmonella Outbreak Linked to Backyard Poultry -May 2024 - CDC | high (0.8826) | include_for_content_fetch | True |
| other | src_search_48540a4df4f2 | / Chicken Linked to Salmonella Outbreak in 29 States - Allrecipes | high (0.8112) | include_for_content_fetch | True |
| other | src_search_95a418d2f831 | CIDRAP / Salmonella outbreak linked to backyard poultry grows to ... - CIDRAP | high (0.8048) | include_for_content_fetch | True |
| other | src_search_af2190be6282 | Centers for Disease Control and Prevention / CDC warns of Salmonella outbreaks linked to backyard poultry flocks / CDC Online Newsroom / CDC | high (0.8618) | include_for_content_fetch | True |
| other | src_search_6ec6e3fd8adc | Centers for Disease Control and Prevention / Ongoing Salmonella outbreaks linked to backyard poultry sickens ... | high (0.8434) | include_for_content_fetch | True |
| other | src_search_bbfd11297ad8 | Centers for Disease Control and Prevention / Investigation Update: Salmonella Outbreak, Cucumbers - June 2024 | high (0.8826) | include_for_content_fetch | True |
| other | src_search_8fb76173fa13 | CIDRAP / CDC ends its probe of cucumber Salmonella outbreak after 551 cases / CIDRAP | high (0.8642) | include_for_content_fetch | True |
| other | src_search_fe091021a27e | doh.wa.gov / 2024 Salmonella Multi-state Outbreak Linked to Cucumbers / Washington State Department of Health | high (0.8232) | include_for_content_fetch | True |
| other | src_search_f06158a1a260 | / Cucumber outbreak from salmonella over - PIRG | high (0.7928) | include_for_content_fetch | True |
| other | src_search_3c32f8c03a31 | / Outbreak Investigation of Salmonella: Cucumbers (May 2025) - FDA | high (0.7928) | include_for_content_fetch | True |
| other | src_search_d95e02cc3006 | / Outbreak Investigation of Salmonella: Eggs (Sept 2024) - FDA | high (0.8112) | include_for_content_fetch | True |
| other | src_search_f3dfdc0c6d99 | Centers for Disease Control and Prevention / Investigation Update: Salmonella Outbreak, Eggs, June 2025 / Salmonella Infection / CDC | high (0.8642) | include_for_content_fetch | True |
| other | src_search_00ed2e227127 | / Salmonella Enteritidis outbreak linked to eggs sickens 79 ... - BEACON | medium (0.6456) | include_for_content_fetch | True |
| other | src_search_69331015856f | Centers for Disease Control and Prevention / CDC announces Salmonella outbreak in 13 states linked to backyard poultry. Take steps to pro... | high (0.8759) | include_for_content_fetch | True |
| other | src_search_c6847df134ad | / USDA-FSIS Recall Cases, Retail List - Update | high (0.6522) | include_for_content_fetch | True |
| other | src_search_e7a1cca073de | / Outbreak Investigations: Response / Food Safety and Inspection Service | high (0.6522) | include_for_content_fetch | True |
| other | src_search_01e4ab75e33f | / FSIS Issues Public Health Alert For Ready-To-Eat Poultry Products Containing FDA-Regulated Dairy Products That Have Been Recalled Due T... | high (0.6362) | include_for_content_fetch | True |
| other | src_search_4526a2ab0e84 | Centers for Disease Control and Prevention / Investigation Update: Listeria Outbreak, Meat and Poultry Products, 2024 / Listeria Infectio... | medium (0.6826) | include_for_content_fetch | True |
| other | src_search_b3970fa613bc | / Constituent Update - April 25, 2025 / Food Safety and Inspection Service | high (0.6522) | include_for_content_fetch | True |

## 5. 真实网页抓取结果

- Documents fetched/parsed: `45`
- Search-derived sources selected for fetch: `45`
- Search-derived skipped by reason: `{}`
- Fetch status counts: `fetch_failed=2, fetched=43`
- External fetch enabled: `True`
- Fetch provider counts: `native_requests=3, tavily_extract=42`
- External fetch failure counts: `native_requests=2, tavily_extract=3`
- Selected fetch bucket counts: `target_official_authority=45`
- Parser status counts: `parsed_html=3, parsed_text=42`
- Parser used counts: `html_stdlib_parser=3, text_parser=42`
- Quality status counts: `partial=1, unusable=5, usable=39`
- Validation-reserved skipped from fetch: `[]`

| Source ID | Provider | Fetch status | HTTP | Parse | Parser | Quality | Text chars | Tables |
|---|---|---|---|---|---|---|---|---|
| src_search_a5bc6c5400a7 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 10534 | 0 |
| src_search_e0c58bcf769a | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 2494 | 0 |
| src_search_b85f60e7676f | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 2035 | 0 |
| src_search_33733b13ba13 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 14729 | 0 |
| src_search_85d5f7f41e48 | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 23998 | 0 |
| src_search_057e55c5d693 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 9859 | 0 |
| src_search_341f243cf7df | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 20820 | 0 |
| src_search_af2190be6282 | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 2030 | 0 |
| src_search_6ec6e3fd8adc | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 2381 | 0 |
| src_search_48540a4df4f2 | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 27767 | 0 |
| src_search_95a418d2f831 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 16841 | 0 |
| src_search_b51a5ab7bcd8 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 1013 | 0 |
| src_search_8207a084046e | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 15762 | 0 |
| src_search_712e948506d7 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 11548 | 0 |
| src_search_bbfd11297ad8 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 29471 | 0 |
| src_search_8fb76173fa13 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 19359 | 0 |
| src_search_843a36718811 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 4858 | 0 |
| src_search_fe091021a27e | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 4739 | 0 |
| src_search_793a8dd9911b | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 24695 | 0 |
| src_search_f06158a1a260 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 10672 | 0 |
| src_search_3c32f8c03a31 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 12251 | 0 |
| src_search_1f2ad0f9f937 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 499103 | 0 |
| src_search_a37f3105d277 | native_requests | fetch_failed | 403 | parsed_html | html_stdlib_parser | unusable | 16 | 0 |
| src_search_139b1ba6fd05 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 13899 | 0 |
| src_search_d75a6eda1263 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 5160 | 0 |
| src_search_34a66c01ab1b | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 29072 | 0 |
| src_search_1a43f41dad6f | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 16213 | 0 |
| src_search_58cd0c44b219 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 17051 | 0 |
| src_search_69331015856f | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 2352 | 0 |
| src_search_f3dfdc0c6d99 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 11330 | 0 |
| src_search_25738f18fb27 | native_requests | fetch_failed | 403 | parsed_html | html_stdlib_parser | unusable | 46 | 0 |
| src_search_8d0aef1a7c3b | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 2124 | 0 |
| src_search_d95e02cc3006 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 6778 | 0 |
| src_search_bebdb72f384b | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 5927 | 0 |
| src_search_814630932f43 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 7386 | 0 |
| src_search_b1fd759a3dac | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 18116 | 0 |
| src_search_00ed2e227127 | native_requests | fetched | 200 | parsed_html | html_stdlib_parser | partial | 129 | 0 |
| src_search_1aa919b25056 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 19967 | 0 |
| src_search_fe233d5728e3 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 11215 | 0 |
| src_search_efda92ce4d43 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 3032 | 0 |
| src_search_4526a2ab0e84 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 13531 | 0 |
| src_search_c6847df134ad | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 2982 | 0 |
| src_search_e7a1cca073de | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 39988 | 0 |
| src_search_b3970fa613bc | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 9339 | 0 |
| src_search_01e4ab75e33f | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 6765 | 0 |

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
- Stop reason: `Max iterations reached (iteration_index=2, max_iterations=2). Evidence coverage is substantively sufficient: three distinct in-scope Salmonella outbreak events (cucumbers June 2024, backyard poultry May 2024, eggs May–July 2024) are each covered by at least one authoritative CDC or FDA source candidate with quantitative epidemiological data. FSIS and state-level sources also surfaced. No critical unresolved gaps remain that would justify additional search within bounds.`
- Query source counts: `{'iterative_llm_initial_search_plan': 4, 'iterative_llm_refinement': 4}`
- Iteration query counts: `{'1': 4, '2': 4}`

### 6.2 LLM Source Critic

- Attempted source count: `0`
- Assessed source count: `0`
- Skipped source count: `50`
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
- Assessed source count: `50`
- Final role counts: `collection=14, collection_support=4, context=27, excluded=4, search_endpoint=1`
- Risk flag counts: `advocacy_organization_publisher=1, ambiguous_disease=17, ambiguous_disease_scope=1, ambiguous_disease_signal=1, ambiguous_disease_signal_in_source_metadata=11, case_counts_are_derivative_transcriptions=1, case_counts_if_present_require_primary_source_cross_validation=1, complete_source_provenance=20, context_or_background_only=15, contradictory_risk_flags: simultaneous presence of official_public_health_authority and secondary_news_or_media_source flags indicates internal classifier conflict=1, contradictory_risk_flags: simultaneous presence of primary_or_authoritative_source and screening_and_critic_disagree flags indicates unresolved scoring tension=1, credibility_score_suppressed_by_metadata_gap: overall score of 0.51 (low) is inconsistent with authority=0.95, provenance=0.85, independence=0.90; low disease relevance from insufficient_text is driving score down artificially=1, cross_validation_required_before_extraction=1, data_may_lag_official_agency_updates=1, data_signal_in_source_metadata=49, disease_relevance_score_unreliable: score of 0.10 reflects absence of Salmonella terms in snippet/metadata, not absence of relevant content; index/landing pages routinely suppress case-level text at metadata layer=1, disease_relevance_unclear=6, disease_relevance_unconfirmed_no_snippet=1, http_not_https: canonical URL uses HTTP; verify whether HTTPS redirect is active and update canonical URL accordingly=1, human_review_suppressed_inconsistently: screening_and_critic_disagree flag is present but human_review_recommended=false; these are in conflict=1, independence_below_threshold=1, independence_low_paraphrases_primary_sources=1, independence_unclear=4, landing_page_not_record_level: this is an index/listing page; individual recall announcement sub-pages are the appropriate extraction targets for required fields (cases_confirmed, hospitalizations, date_reported, evidence_quote)=1, likely_secondary_synthesis_report=1, local_or_subnational_granularity=20, local_source_matches_task_location=33, location_match_from_planned_query=17, low_authority_relevant_source=1, missing_publisher=30, missing_publisher_field: publisher is null; should be populated as 'USDA Food Safety and Inspection Service' for provenance completeness=1, missing_publisher_metadata=1, national_or_international_granularity=17, news_case_counts_likely_preliminary=1, not_directly_extractable_search_endpoint=1, not_suitable_as_primary_collection_source=1, official_public_health_authority=46, potential_pointer_to_primary_cdc_fda_sources_only=1, primary_or_authoritative_source=46, recall_linked_report_no_confirmed_case_count_guarantee=1, recall_page_case_count_caveat: per disease intelligence summary, FSIS recall pages may not include confirmed human case counts — do not infer case counts from recall scope or product volume=1, required_field_granularity_unlikely_met=1, screening_and_critic_disagree=13, screening_and_critic_disagree_warrants_review=1, secondary_aggregator_not_primary_source=1, secondary_news_or_media_source=6, source_disease_relevance:ambiguous_disease=11, source_disease_relevance:insufficient_text=6, source_disease_relevance:target_disease_match=33, source_likely_not_extractable=1, source_metadata_matches_requested_disease=33, source_time_matches_requested_window=13, source_type_mismatch: classified as news_and_situation_report but domain is a federal regulatory authority (USDA FSIS); should be reclassified as official_public_health_agency or regulatory_agency=1, standard_web_page=50, task_input_warning_active: extraction_record_model_still_hantavirus_named — confirm schema remapping to Salmonella/generic fields before any extraction from this source=1, task_input_warning_active: source_discovery_not_yet_disease_generic — FSIS was surfaced via live search but may not be systematically included in source discovery; manual seeding of FSIS recall sub-pages recommended=1, task_location_granularity=13, time_window_coverage_unverified=1, time_window_match_from_planned_query=37, title_year_mismatch_with_collection_window=1, wikipedia_crowd_edited_tertiary_source=1, zero_target_disease_terms_in_metadata=1`
- LLM assessed count: `4`
- LLM failure count: `0`
- Needs review count: `8`

### 6.3.5 Source Identity / Publisher Assessment

- Identity assessed source count: `50`
- LLM identity assessed source count: `0`
- Post-fetch identity assessed source count: `45`
- Unknown publisher count: `27`
- Source type counts: `academic_or_peer_reviewed_source=3, national_public_health_agency=15, news_media=4, official_public_health_agency=18, secondary_aggregator=1, social_media=7, state_or_local_public_health_agency=2`
- Claim support role counts: `corroboration_support=5, insufficient_information=10, primary_case_claim_support=35`
- Fetch use counts: `fetch_for_extraction=40, fetch_only_after_review=10`
- Warning counts: `actual_publisher_unknown=30, direct_target_official_fast_path_skips_source_identity=50, publisher_from_search_metadata_unverified=50, search_provider_not_publisher=50`

### 6.4 LLM Structured Extraction

- Extraction mode: `llm_structured_output`
- Eligible chunk count: `720`
- LLM call count: `30`
- LLM success count: `30`
- LLM error count: `0`
- Raw record count: `19`

## 7. 最终抽取 records

- Normalized record count: `19`
- Run quality status: `partial_with_quarantined_records`
- Final dataset mode: `task_aware_quality_gated_records`
- Quality-gated accepted final dataset count: `5`
- Final case dataset count: `3`
- Zero-case statement count: `0`
- Exposure-monitoring record count: `0`
- Surveillance summary record count: `0`
- Outbreak summary record count: `0`
- Context record count: `1`
- Unclassified observation count: `0`
- Observation dataset view counts: `{'final_case_dataset': 3, 'global_outbreak_event_dataset': 0, 'regional_surveillance_dataset': 0, 'country_year_aggregate_dataset': 0, 'official_alert_dataset': 0, 'probable_case_dataset': 0, 'suspected_case_dataset': 0, 'unspecified_case_dataset': 3, 'death_dataset': 3, 'hospitalization_dataset': 2, 'zero_case_statements': 0, 'exposure_monitoring_records': 0, 'surveillance_summary_records': 0, 'outbreak_summary_records': 0, 'context_records': 1, 'non_primary_observations': 3, 'unclassified_observation_records': 0}`
- Pre-quality-gate record count: `19`
- Quarantined record count: `4`
- Pending review record count: `10`
- Non-primary observation count: `0`
- Final dataset post-review count: `5`
- Primary-case dataset status: `primary_case_records_present`
- Recommended primary dataset message: `Primary case dataset records are available in final_case_dataset.`
- Primary-case eligible accepted count: `3`
- Corroborated primary case event count: `0`
- Record inclusion status counts: `{'accepted_with_warnings': 5, 'quarantined_outside_scope': 4, 'pending_human_review': 10}`
- Run quality warnings: `['no_corroborated_primary_case_events']`
- Accepted source counts: `src_search_33733b13ba13=3, src_search_6ec6e3fd8adc=1, src_search_793a8dd9911b=1`

| Record ID | Date / period | Location | Cases | Deaths | Source | LLM used |
|---|---|---|---|---|---|---|
| rec_src_search_6ec6e3fd8adc_001 | 2024-05-01 to 2024-07-31 | United States | 150.0 | none | src_search_6ec6e3fd8adc | True |
| rec_src_search_33733b13ba13_001 | as of July 1, 2024 | United States | 551.0 | 0.0 | src_search_33733b13ba13 | True |
| rec_src_search_33733b13ba13_002 | as of July 1, 2024 | United States | none | none | src_search_33733b13ba13 | True |
| rec_src_search_33733b13ba13_003 | as of July 1, 2024 | United States | none | 0.0 | src_search_33733b13ba13 | True |
| rec_src_search_793a8dd9911b_003 | November 2024 outbreak investigation | United States | none | 0.0 | src_search_793a8dd9911b | True |

## 8. Validation 对比

### Claim-level corroboration

- Claim count: `25`
- Claim comparison count: `300`
- Corroborated event count: `8`
- Corroborated primary case event count: `0`
- Observation type counts: `confirmed_case_record=6, death_record=5, hospitalization_record=7, unspecified_case_record=7`
- Corroboration status counts: `conflicting_claims=1, single_source_unverified=7`

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
- Anomaly review item count: `5`

| Review ID | Type | Related IDs | Reason |
|---|---|---|---|
| review_source_credibility_src_search_33733b13ba13 | source_credibility | src_search_33733b13ba13 | missing_publisher |
| review_source_src_search_33733b13ba13 | source_screening | src_search_33733b13ba13 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_src_search_712e948506d7 | source_screening | src_search_712e948506d7 | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_src_search_b51a5ab7bcd8 | source_screening | src_search_b51a5ab7bcd8 | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_credibility_src_search_793a8dd9911b | source_credibility | src_search_793a8dd9911b | missing_publisher |
| review_source_src_search_793a8dd9911b | source_screening | src_search_793a8dd9911b | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_843a36718811 | source_credibility | src_search_843a36718811 | missing_publisher |
| review_source_src_search_843a36718811 | source_screening | src_search_843a36718811 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_src_search_34a66c01ab1b | source_screening | src_search_34a66c01ab1b | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_src_search_d75a6eda1263 | source_screening | src_search_d75a6eda1263 | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_credibility_src_search_814630932f43 | source_credibility | src_search_814630932f43 | missing_publisher |
| review_source_src_search_814630932f43 | source_screening | src_search_814630932f43 | Source classified as data_source; both screening and critic agree to include for content fetch. |

## 9.5 Stage 11 anomaly detection and review application

- Anomaly result count: `7`
- Anomaly severity counts: `high=3, low=2, medium=2`
- Anomaly needs-human-review count: `5`
- Decisions provided: `0`
- Decisions applied: `0`
- Decisions rejected: `0`
- Audit entries: `0`
- Final dataset post-review count: `5`
- Records excluded by review: `0`

| Anomaly ID | Type | Severity | Target | Reason |
|---|---|---|---|---|
| anom_001 | deaths_without_case_reference | low | rec_src_search_33733b13ba13_003 | deaths present but no comparable case count is available |
| anom_002 | deaths_without_case_reference | low | rec_src_search_793a8dd9911b_003 | deaths present but no comparable case count is available |
| anom_003 | out_of_scope_count_bearing_record | high | event_004 | Stage 10 validation marked record outside requested scope: outside_time_window |
| anom_004 | out_of_scope_count_bearing_record | high | event_004 | Stage 10 validation marked record outside requested scope: outside_time_window |
| anom_005 | validation_conflict_anomaly | high | event_004 | Validation result is a conflict: Sources may use different case definitions or reporting categories. |
| anom_006 | aggregate_member_mismatch | medium | event_001 | event cluster canonical count differs from sum of comparable countable members |
| anom_007 | aggregate_member_mismatch | medium | event_005 | event cluster canonical count differs from sum of comparable countable members |

| Applied decision | Type | Target | Audit IDs | Reason |
|---|---|---|---|---|

## 10. 输出文件

- Run output directory: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_salmonella_us_2024_05_07`
- Collection final dataset: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_salmonella_us_2024_05_07\collection\final_dataset.csv`
- Collection final case dataset: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_salmonella_us_2024_05_07\collection\final_case_dataset.csv`
- Collection zero-case statements: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_salmonella_us_2024_05_07\collection\zero_case_statements.csv`
- Collection exposure-monitoring records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_salmonella_us_2024_05_07\collection\exposure_monitoring_records.csv`
- Collection surveillance summaries: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_salmonella_us_2024_05_07\collection\surveillance_summary_records.csv`
- Collection outbreak summaries: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_salmonella_us_2024_05_07\collection\outbreak_summary_records.csv`
- Collection context records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_salmonella_us_2024_05_07\collection\context_records.csv`
- Collection unclassified observations: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_salmonella_us_2024_05_07\collection\unclassified_observation_records.csv`
- Collection observation dataset summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_salmonella_us_2024_05_07\collection\observation_type_dataset_summary.json`
- Collection pre-quality-gate records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_salmonella_us_2024_05_07\collection\final_dataset_pre_quality_gate.csv`
- Collection quarantined records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_salmonella_us_2024_05_07\collection\quarantined_records.csv`
- Collection pending review records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_salmonella_us_2024_05_07\collection\pending_review_records.csv`
- Collection non-primary observations: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_salmonella_us_2024_05_07\collection\non_primary_observations.csv`
- Collection record inclusion decisions: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_salmonella_us_2024_05_07\collection\record_inclusion_decisions.json`
- Collection final dataset post-review: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_salmonella_us_2024_05_07\collection\final_dataset_post_review.csv`
- Collection anomaly results: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_salmonella_us_2024_05_07\collection\anomaly_results.json`
- Collection human review audit trail: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_salmonella_us_2024_05_07\collection\human_review_audit_trail.json`
- Collection source registry: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_salmonella_us_2024_05_07\collection\source_registry.json`
- Validation mode: `diagnostic_only`
- Validation records source: `state`
- Validation records output: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_salmonella_us_2024_05_07\validation\ground_truth_records.csv`
- Inactive validation records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_salmonella_us_2024_05_07\validation\inactive_validation_records.csv`
- Validation compatibility summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_salmonella_us_2024_05_07\validation\validation_source_compatibility_summary.json`
- Evaluation report CSV: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_salmonella_us_2024_05_07\evaluation\evaluation_report.csv`
- Human-readable report: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_salmonella_us_2024_05_07\workflow_run_report_chinese.md`

## 11. 当前结论

This workflow run executed the configured data collection workflow through the exported graph and artifact pipeline. The user-facing run status is: PARTIAL: accepted records produced, but some records were quarantined.
The run completed technically and produced quality-gated accepted records in the final dataset.

- Package metadata says LLM used: `True`
- Contains synthetic fixture data: `False`
- Generated at UTC: `2026-06-25T15:32:14.808126+00:00`

## 12. Workflow visualization artifacts

- Workflow visualization index: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_salmonella_us_2024_05_07\workflow_visualization\index.html`
- Workflow timeline: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_salmonella_us_2024_05_07\workflow_visualization\workflow_timeline.html`
- Evidence flow graph: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_salmonella_us_2024_05_07\workflow_visualization\evidence_flow_graph.html`
- Claim comparison cards: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_salmonella_us_2024_05_07\workflow_visualization\claim_comparison_cards.html`
- Dataset decision flow: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_salmonella_us_2024_05_07\workflow_visualization\dataset_decision_flow.html`
- Human review workflow visualization: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_salmonella_us_2024_05_07\workflow_visualization\human_review_workflow.html`
- Visualization summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_salmonella_us_2024_05_07\workflow_visualization\workflow_visualization_summary.json`
