# data collection workflow Run Report

## 1. 输入任务

Collect Influenza cases, deaths, dates, locations, source URLs, source types, and evidence quotes for United States from 2024-09-29 to 2024-10-05.

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
- Search-derived source candidates: `42`
- Iterative source discovery: `True`
- Iterative search iterations: `2`
- Iterative stop decision: `stop_sufficient`
- Iterative stop reason: `Max iterations (2) reached. Sufficient authoritative sources identified across CDC (national), MSDH (subnational/Mississippi), PAHO (international validation), ECDC (independent international corroboration), and news/specialist outlets. All planned queries from both iterations have been executed. No remaining query slots are available.`
- Source credibility assessed sources: `42`
- Source credibility role counts: `{'context': 26, 'validation': 13, 'excluded': 1, 'collection': 2}`
- Source identity assessed sources: `42`
- Source identity type counts: `{'national_public_health_agency': 17, 'unknown': 2, 'background_fact_sheet': 1, 'international_public_health_agency': 8, 'structured_database': 2, 'state_or_local_public_health_agency': 1, 'social_media': 2, 'secondary_aggregator': 1, 'academic_or_peer_reviewed_source': 1, 'news_media': 4, 'official_public_health_agency': 3}`
- Source identity warning counts: `{'search_provider_not_publisher': 42, 'publisher_from_search_metadata_unverified': 42, 'direct_target_official_fast_path_skips_source_identity': 42, 'actual_publisher_unknown': 13}`
- Source discovery method: `live_search_only`
- Disease relevance target: `Influenza`
- Disease relevance source status counts: `{'target_disease_match': 35, 'ambiguous_disease': 5, 'unrelated_disease': 1, 'insufficient_text': 1}`
- Disease relevance chunk status counts: `{'target_disease_match': 41, 'ambiguous_disease': 6, 'unrelated_disease': 1}`
- Disease relevance record status counts: `{'compatible': 42}`
- Rejected incompatible record count: `0`
- Final route: `finalize`

## 2.5 Run quality status

- User-facing run status: `PARTIAL: accepted records produced, but some records were quarantined.`
- Technical execution status: `completed`
- Run quality status: `partial_with_quarantined_records`
- Final dataset mode: `task_aware_quality_gated_records`
- Accepted final dataset count: `5`
- Final case dataset count: `0`
- Zero-case statement count: `0`
- Exposure-monitoring record count: `0`
- Surveillance summary record count: `14`
- Outbreak summary record count: `0`
- Context record count: `0`
- Unclassified observation count: `3`
- Observation dataset view counts: `{'final_case_dataset': 0, 'global_outbreak_event_dataset': 0, 'regional_surveillance_dataset': 0, 'country_year_aggregate_dataset': 0, 'official_alert_dataset': 0, 'probable_case_dataset': 0, 'suspected_case_dataset': 0, 'unspecified_case_dataset': 0, 'death_dataset': 1, 'hospitalization_dataset': 0, 'zero_case_statements': 0, 'exposure_monitoring_records': 0, 'surveillance_summary_records': 14, 'outbreak_summary_records': 0, 'context_records': 0, 'non_primary_observations': 14, 'unclassified_observation_records': 3}`
- Pre-quality-gate record count: `14`
- Quarantined record count: `7`
- Pending review record count: `2`
- Non-primary observation count: `8`
- Final dataset post-review count: `5`
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
2. `disease_intelligence_builder` - Built disease intelligence from LLM output (Influenza).
3. `profile_and_schema_setup` - Built active disease profile, collection schema, and source strategy (Influenza, generation_method=disease_intelligen...
4. `executable_source_planning` - Built executable source plan with 10 planned queries; no searches were executed.
5. `query_strategy_builder` - Built 10 direct_collection search queries from the LLM evidence strategy plan.
6. `source_discovery` - Discovered 43 source candidates using live_search_only.
7. `source_dedup_and_registry` - Built source registry with 42 entries (1 duplicates dropped).
8. `source_screening` - Screened 42 sources using deterministic policy.
9. `source_critic_and_uncertainty_routing` - Critic reviewed 42 sources; 23 ready for fetch, 0 deferred, 19 flagged for human review.
10. `content_fetch_and_parse` - Built 3 fetch requests, produced 3 documents (live_fetch_enabled=True, fixture_documents_enabled=False, fixtures_load...
11. `document_quality_check` - Quality-checked 3 documents: 3 usable, 0 partial, 0 offline stub, 0 parse deferred, 0 unusable.
12. `evidence_chunking_and_data_presence_flagging` - Chunked 3/3 documents into 48 evidence chunks (48 flagged as containing target data).
13. `structured_extraction` - Built 14 raw records (extraction_mode=llm_structured_output, llm_enabled=True).
14. `schema_validation_and_repair` - Validated 14 raw records: 14 validated (0 need review), 0 rejected.
15. `record_normalization` - Normalized 14/14 records (0 need review).
16. `record_linking` - Linked 14/14 normalized records into 8 candidate events.
17. `cross_source_consistency_check` - Checked 4 multi-record events; found 0 new conflicts and 36 validation results (0 events need review).
18. `quality_gate_routing` - Human review disabled; preserving review flags as audit metadata and routing to final_data_package_builder.
19. `final_data_package_builder` - Assembled hardened FinalDataPackage from current state.

## 4. 数据源分工

| Role | Source ID | Publisher / title | Credibility | Final decision | Fetch ready |
|---|---|---|---|---|---|
| context_only | src_search_0a7b36e413fd | Centers for Disease Control and Prevention / Weekly US Influenza Surveillance Report: Key Updates for Week 40, ending October 4, 2025 / F... | medium (0.7642) | needs_human_review | False |
| context_only | src_search_7edb5942f160 | Centers for Disease Control and Prevention / Weekly US Influenza Surveillance Report: Key Updates for Week 51, ending December 20, 2025 /... | medium (0.7642) | needs_human_review | False |
| context_only | src_search_d4520b372d72 | Centers for Disease Control and Prevention / Weekly US Influenza Surveillance Report: Key Updates for Week 49, ending December 6, 2025 | medium (0.7642) | needs_human_review | False |
| context_only | src_search_0fff1ff8aec5 | Centers for Disease Control and Prevention / Weekly US Influenza Surveillance Report: Key Updates for Week 53, ending January 3, 2026 / F... | medium (0.7642) | needs_human_review | False |
| context_only | src_search_7c93d846b7e6 | Centers for Disease Control and Prevention / Weekly US Influenza Surveillance Report: Key Updates for Week 46, ending November 15, 2025 /... | medium (0.7642) | needs_human_review | False |
| context_only | src_search_421d9a4e7d1c | Centers for Disease Control and Prevention / Weekly US Influenza Surveillance Report: Key Updates for Week 34, ending August 23, 2025 / F... | medium (0.7642) | needs_human_review | False |
| context_only | src_search_7a2a0b4aafab | Centers for Disease Control and Prevention / Weekly US Influenza Surveillance Report: Key Updates for Week 31, ending August 2, 2025 / Fl... | medium (0.7642) | needs_human_review | False |
| context_only | src_search_2803152d7acd | Centers for Disease Control and Prevention / Weekly US Influenza Surveillance Report: Key Updates for Week 52, ending December 28, 2024 /... | high (0.7826) | needs_human_review | False |
| context_only | src_search_2f0a4cb6cf21 | World Health Organization / [PDF] Influenza weekly bulletin Week 40-2025 | medium (0.6176) | needs_human_review | False |
| context_only | src_search_275b134ca50b | Pan American Health Organization / Regional Update, Influenza and Other Respiratory Viruses. Epidemiological Week 40 (10 October 2025) -... | medium (0.7642) | needs_human_review | False |
| context_only | src_search_3c62a0b5d9d6 | / PAHO calls for strengthened vaccination and surveillance in Americas | low (0.4816) | needs_human_review | False |
| context_only | src_search_0ecd29cced03 | / 2024–2025 United States flu season - Wikipedia | medium (0.5735) | needs_human_review | False |
| context_only | src_search_3ca7d0dccaf3 | CIDRAP / US data highlight severity of 2024-25 flu season / CIDRAP | medium (0.5995) | needs_human_review | False |
| context_only | src_search_56ae1d93a391 | Centers for Disease Control and Prevention / 2024–2025 Influenza Season Summary: Severity, Disease Burden, and Burden Prevented / Flu Bur... | medium (0.7543) | needs_human_review | False |
| context_only | src_search_ab285e09d5d1 | / US flu map update for 2024-25 season - Facebook | medium (0.5735) | needs_human_review | False |
| context_only | src_search_5d420ffb46a3 | / Microsoft Word - 2023-2024 Season Summary Final | low (0.2864) | needs_human_review | False |
| context_only | src_search_56888319c899 | / 2024 to 2025 US Influenza Season Sets Record Hospitalization Rate | medium (0.5735) | needs_human_review | False |
| context_only | src_search_788fc63b0a32 | / Number of flu cases per year U.S./ Statista | medium (0.5551) | needs_human_review | False |
| context_only | src_search_5b96994980c5 | / Last Flu Season Saw Highest U.S. Hospitalization Rates in Over a Decade | high (0.7928) | include_for_context_fetch | True |
| context_only | src_search_dccb1d80faf5 | / Influenza Affects the US Seasonally - Infection Control Today | medium (0.6912) | include_for_context_fetch | True |
| context_only | src_search_7813d28aa66e | / Week%2010%202024-2025.pdf | low (0.5352) | include_for_context_fetch | True |
| other | src_search_ff1cee7a6f74 | Centers for Disease Control and Prevention / Weekly US Influenza Surveillance Report: Key Updates for Week 40, ending October 5, 2024 / F... | high (0.8826) | include_for_content_fetch | True |
| other | src_search_08ff4e621e6d | Centers for Disease Control and Prevention / Past Weekly Report / FluView / CDC | high (0.8434) | include_for_content_fetch | True |
| other | src_search_39cef9614d66 | Centers for Disease Control and Prevention / FluView / CDC | high (0.8434) | include_for_content_fetch | True |
| other | src_search_e0370422d92f | Centers for Disease Control and Prevention / Influenza Activity in the United States during the 2024–25 Season and Composition of the 202... | high (0.8943) | include_for_content_fetch | True |
| other | src_search_2a8f5ab401f0 | Centers for Disease Control and Prevention / Interim Estimates of 2024–2025 Seasonal Influenza Vaccine Effectiveness — Four Vaccine Effec... | high (0.8943) | include_for_content_fetch | True |
| other | src_search_4113f9b4d265 | Centers for Disease Control and Prevention / 2025-2026 United States Flu Season: Preliminary In-Season Severity Assessment / Flu Burden /... | high (0.8759) | include_for_content_fetch | True |
| other | src_search_4fcd8a7806fd | Centers for Disease Control and Prevention / Influenza Activity in the United States during the 2023–2024 Season and Composition of the 2... | high (0.8943) | include_for_content_fetch | True |
| other | src_search_c95c26c7b200 | / [PDF] 2024-2025 Influenza Surveillance Report Week 40 | medium (0.7352) | include_for_content_fetch | True |
| other | src_search_89fe45c6c3cc | / JMIR Public Health and Surveillance - Responding to the Return of Influenza in the United States by Applying Centers for Disease Contro... | high (0.8823) | include_for_content_fetch | True |
| other | src_search_e47f7e6085a6 | European Centre for Disease Prevention and Control / Communicable disease threats report, 28 September - 4 October 2024, week 40 | medium (0.6826) | include_for_content_fetch | True |
| other | src_search_6d302758cdcd | / Influenza - Our World in Data | medium (0.7608) | include_for_content_fetch | True |
| other | src_search_ebff1481f418 | World Health Organization / Global Influenza Programme | high (0.8434) | include_for_content_fetch | True |
| other | src_search_739c5a440dbf | National Center for Biotechnology Information / National Influenza Annual Report 2023–2024: A focus on influenza B and public health impl... | high (0.8826) | include_for_content_fetch | True |
| other | src_search_1b15a2673061 | Pan American Health Organization / Regional Update, Influenza and Other Respiratory Viruses. Epidemiological Week 40 (11 October 2024) -... | high (0.8826) | include_for_content_fetch | True |
| other | src_search_41068fc0d551 | globalhealthreports.health.ny.gov / [PDF] Contents Dengue Region of the Americas – PAHO Issues ... | excluded (0.4968) | exclude | False |
| other | src_search_a528d9bf475d | Pan American Health Organization / Regional Update, Influenza and Other Respiratory Viruses ... | high (0.8322) | include_for_content_fetch | True |
| other | src_search_79e3303d15e2 | Pan American Health Organization / Influenza, SARS-CoV-2, RSV and other Respiratory Viruses Regional Situation - PAHO/WHO / Pan American... | high (0.7842) | include_for_content_fetch | True |
| other | src_search_040dd0cc2a13 | Pan American Health Organization / Technical reports - PAHO/WHO / Pan American Health Organization | medium (0.5888) | include_for_content_fetch | True |
| other | src_search_2466312a2ac3 | National Center for Biotechnology Information / Influenza-Associated Hospitalizations During a High Severity Season — Influenza Hospitali... | high (0.8943) | include_for_content_fetch | True |
| other | src_search_50b73d583e75 | / US CDC says 2025-26 flu season 'moderately severe' as cases hit ... | high (0.8522) | include_for_content_fetch | True |
| other | src_search_5e5db7631a59 | Centers for Disease Control and Prevention / Influenza Hospitalization Surveillance Network (FluSurv-NET) / FluView / CDC | medium (0.724) | include_for_content_fetch | True |

## 5. 真实网页抓取结果

- Documents fetched/parsed: `3`
- Search-derived sources selected for fetch: `3`
- Search-derived skipped by reason: `{}`
- Fetch status counts: `fetched=3`
- External fetch enabled: `True`
- Fetch provider counts: `tavily_extract=3`
- External fetch failure counts: `none`
- Selected fetch bucket counts: `target_official_authority=1, validation=2`
- Parser status counts: `parsed_text=3`
- Parser used counts: `text_parser=3`
- Quality status counts: `usable=3`
- Validation-reserved skipped from fetch: `[]`

| Source ID | Provider | Fetch status | HTTP | Parse | Parser | Quality | Text chars | Tables |
|---|---|---|---|---|---|---|---|---|
| src_search_ff1cee7a6f74 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 31357 | 0 |
| src_search_e47f7e6085a6 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 2765 | 0 |
| src_search_1b15a2673061 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 6339 | 0 |

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
- Total queries executed: `6`
- Stop decision: `stop_sufficient`
- Stop reason: `Max iterations (2) reached. Sufficient authoritative sources identified across CDC (national), MSDH (subnational/Mississippi), PAHO (international validation), ECDC (independent international corroboration), and news/specialist outlets. All planned queries from both iterations have been executed. No remaining query slots are available.`
- Query source counts: `{'iterative_llm_initial_search_plan': 2, 'iterative_llm_refinement': 4}`
- Iteration query counts: `{'1': 2, '2': 4}`

### 6.2 LLM Source Critic

- Attempted source count: `0`
- Assessed source count: `0`
- Skipped source count: `42`
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
- Assessed source count: `42`
- Final role counts: `collection=2, context=26, excluded=1, validation=13`
- Risk flag counts: `ambiguous_disease=6, ambiguous_disease_signal_in_source_metadata=5, complete_source_provenance=29, context_or_background_only=20, context_or_prevention_only=2, data_signal_in_source_metadata=40, disease_relevance_unclear=1, independence_unclear=5, international_organization_authority=4, local_or_subnational_granularity=12, local_source_matches_task_location=33, location_match_from_planned_query=9, low_authority_relevant_source=5, low_machine_readability=5, missing_publisher=13, named_publisher=1, national_or_international_granularity=9, official_public_health_authority=32, pdf_or_report_likely_medium_readability=5, primary_or_authoritative_source=36, screening_and_critic_disagree=18, secondary_news_or_media_source=7, source_disease_relevance:ambiguous_disease=5, source_disease_relevance:insufficient_text=1, source_disease_relevance:target_disease_match=35, source_disease_relevance:unrelated_disease=1, source_likely_not_extractable=2, source_metadata_matches_requested_disease=35, source_time_matches_requested_window=18, standard_web_page=37, task_location_granularity=21, time_window_match_from_planned_query=24, unrelated_disease_signal_in_source_metadata=1`
- LLM assessed count: `0`
- LLM failure count: `0`
- Needs review count: `0`

### 6.3.5 Source Identity / Publisher Assessment

- Identity assessed source count: `42`
- LLM identity assessed source count: `0`
- Post-fetch identity assessed source count: `3`
- Unknown publisher count: `13`
- Source type counts: `academic_or_peer_reviewed_source=1, background_fact_sheet=1, international_public_health_agency=8, national_public_health_agency=17, news_media=4, official_public_health_agency=3, secondary_aggregator=1, social_media=2, state_or_local_public_health_agency=1, structured_database=2, unknown=2`
- Claim support role counts: `context_only=7, corroboration_support=5, insufficient_information=5, primary_case_claim_support=25`
- Fetch use counts: `fetch_for_context=7, fetch_for_extraction=30, fetch_only_after_review=5`
- Warning counts: `actual_publisher_unknown=13, direct_target_official_fast_path_skips_source_identity=42, publisher_from_search_metadata_unverified=42, search_provider_not_publisher=42`

### 6.4 LLM Structured Extraction

- Extraction mode: `llm_structured_output`
- Eligible chunk count: `20`
- LLM call count: `4`
- LLM success count: `4`
- LLM error count: `0`
- Raw record count: `14`

## 7. 最终抽取 records

- Normalized record count: `14`
- Run quality status: `partial_with_quarantined_records`
- Final dataset mode: `task_aware_quality_gated_records`
- Quality-gated accepted final dataset count: `5`
- Final case dataset count: `0`
- Zero-case statement count: `0`
- Exposure-monitoring record count: `0`
- Surveillance summary record count: `14`
- Outbreak summary record count: `0`
- Context record count: `0`
- Unclassified observation count: `3`
- Observation dataset view counts: `{'final_case_dataset': 0, 'global_outbreak_event_dataset': 0, 'regional_surveillance_dataset': 0, 'country_year_aggregate_dataset': 0, 'official_alert_dataset': 0, 'probable_case_dataset': 0, 'suspected_case_dataset': 0, 'unspecified_case_dataset': 0, 'death_dataset': 1, 'hospitalization_dataset': 0, 'zero_case_statements': 0, 'exposure_monitoring_records': 0, 'surveillance_summary_records': 14, 'outbreak_summary_records': 0, 'context_records': 0, 'non_primary_observations': 14, 'unclassified_observation_records': 3}`
- Pre-quality-gate record count: `14`
- Quarantined record count: `7`
- Pending review record count: `2`
- Non-primary observation count: `8`
- Final dataset post-review count: `5`
- Primary-case dataset status: `no_primary_case_dataset_records`
- Recommended primary dataset message: `No primary case dataset records were accepted; inspect zero-case, exposure-monitoring, context, and other observation views.`
- Primary-case eligible accepted count: `0`
- Corroborated primary case event count: `0`
- Record inclusion status counts: `{'accepted_with_warnings': 5, 'quarantined_outside_scope': 6, 'quarantined_disease_mismatch': 1, 'pending_human_review': 2}`
- Run quality warnings: `['no_primary_case_dataset_records', 'no_corroborated_primary_case_events']`
- Accepted source counts: `src_search_ff1cee7a6f74=5`

| Record ID | Date / period | Location | Cases | Deaths | Source | LLM used |
|---|---|---|---|---|---|---|
| rec_src_search_ff1cee7a6f74_001 | MMWR week 40, 2024 | United States | none | none | src_search_ff1cee7a6f74 | False |
| rec_src_search_ff1cee7a6f74_003 | MMWR week 40, 2024 | United States | none | none | src_search_ff1cee7a6f74 | False |
| rec_src_search_ff1cee7a6f74_004 | MMWR week 40, 2024 | United States | none | none | src_search_ff1cee7a6f74 | False |
| rec_src_search_ff1cee7a6f74_007 | Week 40, ending October 5, 2024 | United States | none | 0.0 | src_search_ff1cee7a6f74 | True |
| rec_src_search_ff1cee7a6f74_009 | Week 40, ending October 5, 2024 | United States | none | none | src_search_ff1cee7a6f74 | True |

## 8. Validation 对比

### Claim-level corroboration

- Claim count: `14`
- Claim comparison count: `91`
- Corroborated event count: `2`
- Corroborated primary case event count: `0`
- Observation type counts: `ambiguous_public_health_observation=3, death_record=2, surveillance_summary=8, unspecified_case_record=1`
- Corroboration status counts: `insufficient_information=1, single_source_unverified=1`

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

- Human review item count: `28`
- Evaluation review flag count: `0`
- Anomaly review item count: `0`

| Review ID | Type | Related IDs | Reason |
|---|---|---|---|
| review_source_src_search_0a7b36e413fd | source_screening | src_search_0a7b36e413fd | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_src_search_7edb5942f160 | source_screening | src_search_7edb5942f160 | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_src_search_d4520b372d72 | source_screening | src_search_d4520b372d72 | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_src_search_0fff1ff8aec5 | source_screening | src_search_0fff1ff8aec5 | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_src_search_7c93d846b7e6 | source_screening | src_search_7c93d846b7e6 | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_src_search_421d9a4e7d1c | source_screening | src_search_421d9a4e7d1c | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_src_search_7a2a0b4aafab | source_screening | src_search_7a2a0b4aafab | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_src_search_2803152d7acd | source_screening | src_search_2803152d7acd | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_src_search_2f0a4cb6cf21 | source_screening | src_search_2f0a4cb6cf21 | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_src_search_275b134ca50b | source_screening | src_search_275b134ca50b | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_src_search_3c62a0b5d9d6 | source_screening | src_search_3c62a0b5d9d6 | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_src_search_0ecd29cced03 | source_screening | src_search_0ecd29cced03 | Screening and critic disagree on this source; routing to human review for resolution. |

## 9.5 Stage 11 anomaly detection and review application

- Anomaly result count: `2`
- Anomaly severity counts: `low=2`
- Anomaly needs-human-review count: `0`
- Decisions provided: `0`
- Decisions applied: `0`
- Decisions rejected: `0`
- Audit entries: `0`
- Final dataset post-review count: `5`
- Records excluded by review: `0`

| Anomaly ID | Type | Severity | Target | Reason |
|---|---|---|---|---|
| anom_001 | deaths_without_case_reference | low | rec_src_search_ff1cee7a6f74_007 | deaths present but no comparable case count is available |
| anom_002 | deaths_without_case_reference | low | rec_src_search_ff1cee7a6f74_010 | deaths present but no comparable case count is available |

| Applied decision | Type | Target | Audit IDs | Reason |
|---|---|---|---|---|

## 10. 输出文件

- Run output directory: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_flu_united_states_2024_09_29_2024_10_05`
- Collection final dataset: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_flu_united_states_2024_09_29_2024_10_05\collection\final_dataset.csv`
- Collection final case dataset: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_flu_united_states_2024_09_29_2024_10_05\collection\final_case_dataset.csv`
- Collection zero-case statements: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_flu_united_states_2024_09_29_2024_10_05\collection\zero_case_statements.csv`
- Collection exposure-monitoring records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_flu_united_states_2024_09_29_2024_10_05\collection\exposure_monitoring_records.csv`
- Collection surveillance summaries: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_flu_united_states_2024_09_29_2024_10_05\collection\surveillance_summary_records.csv`
- Collection outbreak summaries: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_flu_united_states_2024_09_29_2024_10_05\collection\outbreak_summary_records.csv`
- Collection context records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_flu_united_states_2024_09_29_2024_10_05\collection\context_records.csv`
- Collection unclassified observations: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_flu_united_states_2024_09_29_2024_10_05\collection\unclassified_observation_records.csv`
- Collection observation dataset summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_flu_united_states_2024_09_29_2024_10_05\collection\observation_type_dataset_summary.json`
- Collection pre-quality-gate records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_flu_united_states_2024_09_29_2024_10_05\collection\final_dataset_pre_quality_gate.csv`
- Collection quarantined records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_flu_united_states_2024_09_29_2024_10_05\collection\quarantined_records.csv`
- Collection pending review records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_flu_united_states_2024_09_29_2024_10_05\collection\pending_review_records.csv`
- Collection non-primary observations: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_flu_united_states_2024_09_29_2024_10_05\collection\non_primary_observations.csv`
- Collection record inclusion decisions: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_flu_united_states_2024_09_29_2024_10_05\collection\record_inclusion_decisions.json`
- Collection final dataset post-review: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_flu_united_states_2024_09_29_2024_10_05\collection\final_dataset_post_review.csv`
- Collection anomaly results: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_flu_united_states_2024_09_29_2024_10_05\collection\anomaly_results.json`
- Collection human review audit trail: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_flu_united_states_2024_09_29_2024_10_05\collection\human_review_audit_trail.json`
- Collection source registry: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_flu_united_states_2024_09_29_2024_10_05\collection\source_registry.json`
- Validation mode: `diagnostic_only`
- Validation records source: `state`
- Validation records output: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_flu_united_states_2024_09_29_2024_10_05\validation\ground_truth_records.csv`
- Inactive validation records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_flu_united_states_2024_09_29_2024_10_05\validation\inactive_validation_records.csv`
- Validation compatibility summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_flu_united_states_2024_09_29_2024_10_05\validation\validation_source_compatibility_summary.json`
- Evaluation report CSV: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_flu_united_states_2024_09_29_2024_10_05\evaluation\evaluation_report.csv`
- Human-readable report: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_flu_united_states_2024_09_29_2024_10_05\workflow_run_report_chinese.md`

## 11. 当前结论

This workflow run executed the configured data collection workflow through the exported graph and artifact pipeline. The user-facing run status is: PARTIAL: accepted records produced, but some records were quarantined.
The run completed technically and produced quality-gated accepted records in the final dataset.

- Package metadata says LLM used: `True`
- Contains synthetic fixture data: `False`
- Generated at UTC: `2026-06-25T22:15:32.083846+00:00`

## 12. Workflow visualization artifacts

- Workflow visualization index: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_flu_united_states_2024_09_29_2024_10_05\workflow_visualization\index.html`
- Workflow timeline: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_flu_united_states_2024_09_29_2024_10_05\workflow_visualization\workflow_timeline.html`
- Evidence flow graph: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_flu_united_states_2024_09_29_2024_10_05\workflow_visualization\evidence_flow_graph.html`
- Claim comparison cards: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_flu_united_states_2024_09_29_2024_10_05\workflow_visualization\claim_comparison_cards.html`
- Dataset decision flow: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_flu_united_states_2024_09_29_2024_10_05\workflow_visualization\dataset_decision_flow.html`
- Human review workflow visualization: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_flu_united_states_2024_09_29_2024_10_05\workflow_visualization\human_review_workflow.html`
- Visualization summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_flu_united_states_2024_09_29_2024_10_05\workflow_visualization\workflow_visualization_summary.json`
