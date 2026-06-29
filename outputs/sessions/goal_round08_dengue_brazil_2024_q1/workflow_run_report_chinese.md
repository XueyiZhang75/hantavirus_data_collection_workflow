# data collection workflow Run Report

## 1. 输入任务

Collect Dengue cases, deaths, dates, locations, source URLs, source types, and evidence quotes for Brazil from 2024-01-01 to 2024-03-31.

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
- Search-derived source candidates: `44`
- Iterative source discovery: `True`
- Iterative search iterations: `2`
- Iterative stop decision: `stop_sufficient`
- Iterative stop reason: `max_iterations_reached_with_sufficient_coverage: Two iterations completed (8 queries executed). The candidate pool contains: (a) a confirmed Q1 2024 PAHO epidemiological update (29 March 2024, EW 12 data); (b) a Brazilian MoH/SVS bulletin referencing SE4/2024 with ~260k probable cases; (c) a peer-reviewed article with EW 11 2024 figures (1,978,372 suspected cases, 656 deaths); (d) state-level official bulletin portals for Distrito Federal, São Paulo, Minas Gerais, and Paraná; (e) InfoDengue structured database. The 50% duplicate rate in iteration 2 signals search saturation. Additional queries are unlikely to yield new authoritative Q1-specific sources beyond what has already been identified.`
- Source credibility assessed sources: `44`
- Source credibility role counts: `{'collection': 15, 'context': 6, 'validation': 23}`
- Source identity assessed sources: `44`
- Source identity type counts: `{'official_public_health_agency': 14, 'social_media': 4, 'structured_database': 2, 'unknown': 8, 'international_public_health_agency': 9, 'secondary_aggregator': 3, 'news_media': 4}`
- Source identity warning counts: `{'search_provider_not_publisher': 44, 'publisher_from_search_metadata_unverified': 44, 'actual_publisher_unknown': 33, 'direct_target_official_fast_path_skips_source_identity': 44}`
- Source discovery method: `live_search_only`
- Disease relevance target: `Dengue`
- Disease relevance source status counts: `{'target_disease_match': 40, 'ambiguous_disease': 2, 'insufficient_text': 2}`
- Disease relevance chunk status counts: `{'ambiguous_disease': 28, 'target_disease_match': 366, 'related_context_only': 5, 'insufficient_text': 2}`
- Disease relevance record status counts: `{'compatible': 80}`
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
- Surveillance summary record count: `5`
- Outbreak summary record count: `0`
- Context record count: `6`
- Unclassified observation count: `3`
- Observation dataset view counts: `{'final_case_dataset': 0, 'global_outbreak_event_dataset': 0, 'regional_surveillance_dataset': 0, 'country_year_aggregate_dataset': 0, 'official_alert_dataset': 0, 'probable_case_dataset': 0, 'suspected_case_dataset': 0, 'unspecified_case_dataset': 0, 'death_dataset': 0, 'hospitalization_dataset': 0, 'zero_case_statements': 0, 'exposure_monitoring_records': 0, 'surveillance_summary_records': 5, 'outbreak_summary_records': 0, 'context_records': 6, 'non_primary_observations': 8, 'unclassified_observation_records': 3}`
- Pre-quality-gate record count: `26`
- Quarantined record count: `11`
- Pending review record count: `15`
- Non-primary observation count: `5`
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
6. `source_discovery` - Discovered 44 source candidates using live_search_only.
7. `source_dedup_and_registry` - Built source registry with 44 entries (0 duplicates dropped).
8. `source_screening` - Screened 44 sources using deterministic policy.
9. `source_critic_and_uncertainty_routing` - Critic reviewed 44 sources; 37 ready for fetch, 0 deferred, 22 flagged for human review.
10. `content_fetch_and_parse` - Built 37 fetch requests, produced 37 documents (live_fetch_enabled=True, fixture_documents_enabled=False, fixtures_lo...
11. `document_quality_check` - Quality-checked 37 documents: 29 usable, 1 partial, 0 offline stub, 0 parse deferred, 7 unusable.
12. `evidence_chunking_and_data_presence_flagging` - Chunked 30/37 documents into 401 evidence chunks (370 flagged as containing target data).
13. `structured_extraction` - Built 27 raw records (extraction_mode=llm_structured_output, llm_enabled=True).
14. `schema_validation_and_repair` - Validated 27 raw records: 26 validated (7 need review), 1 rejected.
15. `record_normalization` - Normalized 26/26 records (7 need review).
16. `record_linking` - Linked 26/26 normalized records into 18 candidate events.
17. `cross_source_consistency_check` - Checked 6 multi-record events; found 3 new conflicts and 73 validation results (1 events need review).
18. `quality_gate_routing` - Human review disabled; preserving review flags as audit metadata and routing to final_data_package_builder.
19. `final_data_package_builder` - Assembled hardened FinalDataPackage from current state.

## 4. 数据源分工

| Role | Source ID | Publisher / title | Credibility | Final decision | Fetch ready |
|---|---|---|---|---|---|
| context_only | src_search_f28b6af274cc | / Dengue fever kills more than Covid-19 in Brazil in 2024 - YouTube | medium (0.6906) | include_for_content_fetch | False |
| context_only | src_search_08f8dd56800e | / Brasil registra mais de 1 milhão de casos de dengue em 2024; mortes chegam a 214 / G1 | needs_review (0.357) | needs_human_review | False |
| context_only | src_search_de67a8507994 | / Dados Dengue Brasil: Análise Completa das Estatísticas 2024-2025 | needs_review (0.357) | needs_human_review | False |
| context_only | src_search_aefdcfcb3ad8 | / Epidemia de Dengue: uma análise sobre as projeções para o ano ... | needs_review (0.3362) | needs_human_review | False |
| context_only | src_search_8f2793bd15b1 | / Brasil passa a marca de 715 mil casos de dengue em 2024 - YouTube | needs_review (0.357) | needs_human_review | False |
| context_only | src_search_f79ff78ee4b3 | / 050+n4+Contempor%C3%A2nea.pdf | low (0.1226) | needs_human_review | False |
| context_only | src_search_6d0ae6050d3b | / #Dengue state of emergency... - Infectious Disease News | medium (0.7319) | needs_human_review | False |
| context_only | src_search_5737ca939d71 | / Brazil braces for dengue epidemic after 2024 surge - YouTube | medium (0.7226) | needs_human_review | False |
| other | src_search_4520d2861241 | / [PDF] 2024 - Boletim Epidemiológico | high (0.5898) | include_for_content_fetch | True |
| other | src_search_8a863e6c52f9 | / Brasil registra queda de quase 70% nos casos de dengue nos 2 primeiros meses de 2025 — Ministério da Saúde | high (0.6474) | include_for_content_fetch | True |
| other | src_search_9f1bffa1139f | / Casos de dengue em 2024 passam de 6,4 milhões; mortes somam 5,9 mil / Agência Brasil | high (0.6658) | include_for_content_fetch | True |
| other | src_search_0cb54d17a3e3 | / Dengue aumentou 400% no Brasil em 2024 em comparação ao ano ... | high (0.6658) | include_for_content_fetch | True |
| other | src_search_55a815a5dfd8 | National Center for Biotechnology Information / Space-time dynamics of the dengue epidemic in Brazil, 2024 - PMC | high (0.8826) | include_for_content_fetch | True |
| other | src_search_042037d6ca22 | / Boletim Epidemiológico – Dengue, Chikungunya E Zika | high (0.6266) | include_for_content_fetch | True |
| other | src_search_5f398ee9785b | / Info Dengue | high (0.6266) | include_for_content_fetch | True |
| other | src_search_e6a611dc2382 | World Health Organization / Increase in dengue cases in the Americas Region - 7 October 2024 | high (0.8594) | include_for_content_fetch | True |
| other | src_search_c23afe16a48a | Pan American Health Organization / In record year of dengue cases, PAHO urges countries to strengthen response as seasonal transmission s... | high (0.8232) | include_for_content_fetch | True |
| other | src_search_1a6203f794f1 | Pan American Health Organization / [PDF] Epidemiological Alert Increase in dengue cases in the Americas ... | medium (0.7472) | include_for_content_fetch | True |
| other | src_search_9c7738debb9e | National Center for Biotechnology Information / The greatest Dengue epidemic in Brazil: Surveillance, Prevention ... | high (0.8642) | include_for_content_fetch | True |
| other | src_search_5bd1cae37e40 | World Health Organization / Dengue - Global situation - World Health Organization (WHO) | high (0.8024) | include_for_content_fetch | True |
| other | src_search_89d26cc955fb | / Brazil dengue cases top 6 million, nearly 4,000 deaths | high (0.841) | include_for_content_fetch | True |
| other | src_search_fe4e8f3af932 | / Brazil surpasses 1000 dengue deaths in 2025 - BEACON | high (0.841) | include_for_content_fetch | True |
| other | src_search_90b5fc59aef2 | Pan American Health Organization / Situation Report N.1: Dengue Epidemiological Situation in the Americas - 14 December 2023 - PAHO/WHO /... | high (0.8048) | include_for_content_fetch | True |
| other | src_search_c543063343d0 | / Brazil MOH: Dengue cases in 2024 - by Robert Herriman | medium (0.7777) | include_for_content_fetch | True |
| other | src_search_52123c6cbbdd | / Brazil 2024 Record-Breaking Dengue Outbreak / Dengue.com | high (0.8226) | include_for_content_fetch | True |
| other | src_search_beb2acd883bf | / Reported cases of dengue in Brazil from 2015 to 2024 | high (0.8226) | include_for_content_fetch | True |
| other | src_search_8deb58866e68 | World Health Organization / Dengue: global situation, surveillance and progress – 2024 update | high (0.836) | include_for_content_fetch | True |
| other | src_search_619f95867581 | European Centre for Disease Prevention and Control / Countries/territories reporting dengue cases since March 2023, and ... | high (0.836) | include_for_content_fetch | True |
| other | src_search_1e36efa321f9 | / Dengue cases in Brazil drop by more than 70% in 2025 - BEACON | high (0.8042) | include_for_content_fetch | True |
| other | src_search_87a1569617ed | / Brazil / World Mosquito Program | medium (0.5882) | include_for_content_fetch | True |
| other | src_search_f58afbf42419 | / [PDF] Boletim Epidemiológico - Secretaria de Saúde do Distrito Federal | high (0.5506) | include_for_content_fetch | True |
| other | src_search_422eae6f4cb9 | / Dengue Dados Estatísticos - Secretaria de Estado da Saúde | high (0.6266) | include_for_content_fetch | True |
| other | src_search_4e6c9d96071d | / Análise epidemiológica da Dengue no Brasil: uma série histórica 10 anos (2014 - 2024) / Journal of Medical and Biosciences Research | high (0.6658) | include_for_content_fetch | True |
| other | src_search_066d8ce49c2c | / Boletins da Dengue / Paraná contra a Dengue: Mude sua atitude | high (0.6266) | include_for_content_fetch | True |
| other | src_search_7ace0ccbb60e | / Dengue outbreaks in Brazil and Latin America - ScienceDirect.com | high (0.8202) | include_for_content_fetch | True |
| other | src_search_f4f555107be5 | Pan American Health Organization / Epidemiological Update - Increase in dengue cases in the Region of the Americas - 29 March 2024 - PAHO... | high (0.8232) | include_for_content_fetch | True |
| other | src_search_b6376a8d9edc | Pan American Health Organization / Documents - PAHO/WHO / Pan American Health Organization | medium (0.5888) | include_for_content_fetch | True |
| other | src_search_5fd7d33501e8 | / Ministério da Saúde divulga novos dados da dengue e demais arboviroses - APM | high (0.6266) | include_for_content_fetch | True |
| other | src_search_9baddae323c5 | / 52_BOLETIM_SEMANAL_DENGUE_SE_52 DF 2024.pdf | high (0.5898) | include_for_content_fetch | True |
| other | src_search_271588896c48 | / [PDF] Situação das Arboviroses no Brasil Mapa Incidência - Info Dengue | high (0.569) | include_for_content_fetch | True |
| other | src_search_fc7158cd447e | / Casos de dengue saltam 400% em 2024 - Portal Afya | high (0.6658) | include_for_content_fetch | True |
| other | src_search_9cacbefd56b5 | Outbreak News Today / Brazil dengue 2025: The first three weeks - Outbreak News Today | medium (0.7593) | include_for_content_fetch | True |
| other | src_search_2e96f00ec58d | Centers for Disease Control and Prevention / Brazil registered 82% of global dengue cases in 2024: WHO - Brazil Reports | high (0.8226) | include_for_content_fetch | True |
| other | src_search_1e7b9bff1f18 | European Centre for Disease Prevention and Control / Dengue worldwide overview - ECDC - European Union | high (0.7968) | include_for_content_fetch | True |

## 5. 真实网页抓取结果

- Documents fetched/parsed: `37`
- Search-derived sources selected for fetch: `37`
- Search-derived skipped by reason: `{}`
- Fetch status counts: `fetch_failed=1, fetched=36`
- External fetch enabled: `True`
- Fetch provider counts: `native_requests=2, tavily_extract=35`
- External fetch failure counts: `native_requests=1, tavily_extract=2`
- Selected fetch bucket counts: `target_official_authority=37`
- Parser status counts: `parsed_html=2, parsed_text=35`
- Parser used counts: `html_stdlib_parser=2, text_parser=35`
- Quality status counts: `partial=1, unusable=7, usable=29`
- Validation-reserved skipped from fetch: `[]`

| Source ID | Provider | Fetch status | HTTP | Parse | Parser | Quality | Text chars | Tables |
|---|---|---|---|---|---|---|---|---|
| src_search_55a815a5dfd8 | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 53984 | 0 |
| src_search_f28b6af274cc | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 4221 | 0 |
| src_search_9f1bffa1139f | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 11853 | 0 |
| src_search_0cb54d17a3e3 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 7332 | 0 |
| src_search_4e6c9d96071d | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 9681 | 0 |
| src_search_8a863e6c52f9 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 8723 | 0 |
| src_search_422eae6f4cb9 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 12903 | 0 |
| src_search_042037d6ca22 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 29439 | 0 |
| src_search_066d8ce49c2c | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 247295 | 0 |
| src_search_5f398ee9785b | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 2348 | 0 |
| src_search_4520d2861241 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 67722 | 0 |
| src_search_f58afbf42419 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 18998 | 0 |
| src_search_9c7738debb9e | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 109870 | 0 |
| src_search_e6a611dc2382 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 3993 | 0 |
| src_search_89d26cc955fb | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 3600 | 0 |
| src_search_fe4e8f3af932 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 9101 | 0 |
| src_search_c23afe16a48a | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 9698 | 0 |
| src_search_f4f555107be5 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 6510 | 0 |
| src_search_7ace0ccbb60e | native_requests | fetch_failed | 403 | parsed_html | html_stdlib_parser | unusable | 325 | 0 |
| src_search_90b5fc59aef2 | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 5946 | 0 |
| src_search_5bd1cae37e40 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 49456 | 0 |
| src_search_1a6203f794f1 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 34502 | 0 |
| src_search_b6376a8d9edc | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 8755 | 0 |
| src_search_fc7158cd447e | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 7645 | 0 |
| src_search_5fd7d33501e8 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 7596 | 0 |
| src_search_9baddae323c5 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 23962 | 0 |
| src_search_271588896c48 | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 14039 | 0 |
| src_search_8deb58866e68 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 11398 | 0 |
| src_search_619f95867581 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 1453 | 0 |
| src_search_52123c6cbbdd | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 20382 | 0 |
| src_search_beb2acd883bf | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 34313 | 0 |
| src_search_2e96f00ec58d | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 10266 | 0 |
| src_search_1e36efa321f9 | native_requests | fetched | 200 | parsed_html | html_stdlib_parser | partial | 129 | 0 |
| src_search_1e7b9bff1f18 | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 10898 | 0 |
| src_search_c543063343d0 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 2197 | 0 |
| src_search_9cacbefd56b5 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 5217 | 0 |
| src_search_87a1569617ed | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 28934 | 0 |

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
- Stop reason: `max_iterations_reached_with_sufficient_coverage: Two iterations completed (8 queries executed). The candidate pool contains: (a) a confirmed Q1 2024 PAHO epidemiological update (29 March 2024, EW 12 data); (b) a Brazilian MoH/SVS bulletin referencing SE4/2024 with ~260k probable cases; (c) a peer-reviewed article with EW 11 2024 figures (1,978,372 suspected cases, 656 deaths); (d) state-level official bulletin portals for Distrito Federal, São Paulo, Minas Gerais, and Paraná; (e) InfoDengue structured database. The 50% duplicate rate in iteration 2 signals search saturation. Additional queries are unlikely to yield new authoritative Q1-specific sources beyond what has already been identified.`
- Query source counts: `{'iterative_llm_initial_search_plan': 4, 'iterative_llm_refinement': 4}`
- Iteration query counts: `{'1': 4, '2': 4}`

### 6.2 LLM Source Critic

- Attempted source count: `0`
- Assessed source count: `0`
- Skipped source count: `44`
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
- Assessed source count: `44`
- Final role counts: `collection=15, context=6, validation=23`
- Risk flag counts: `ambiguous_disease=3, ambiguous_disease_signal_in_source_metadata=2, ambiguous_location=19, cannot_populate_required_case_count_fields_from_projections=1, complete_source_provenance=11, context_or_background_only=3, data_extraction_not_recommended_pending_official_source_confirmation=1, data_signal_in_source_metadata=44, data_signal_in_source_metadata_only=1, disease_relevance_unclear=2, geographic_granularity_insufficient_for_subnational_collection=1, geographic_granularity_insufficient_for_subnational_extraction=1, geographic_granularity_insufficient_for_subnational_fields=1, geographic_granularity_likely_national_aggregate_or_modeled=1, geographic_granularity_unclear=19, high_stakes_epidemiological_context_requires_elevated_scrutiny=1, independence_of_authorship_unverifiable=1, independence_score_low_derivative_of_official_data=1, independence_unclear=11, independence_unverifiable_possible_aggregated_repackaging=1, international_organization_authority=5, local_or_subnational_granularity=1, local_source_matches_task_location=16, location_match_from_planned_query=9, location_relevance_unclear=19, low_authority_domain_for_epidemiological_data=1, low_authority_relevant_source=4, low_machine_readability=6, machine_readable_or_structured=11, missing_publisher=33, missing_publisher_metadata_gap_not_genuine_ambiguity=1, missing_publisher_provenance_unverifiable=1, national_aggregate_only_likely=1, national_or_international_granularity=9, no_data_signal_detected_in_metadata=1, no_structured_data_extractable_from_video_format=1, null_publisher_unverifiable_authorship=1, official_public_health_authority=26, pdf_or_report_likely_medium_readability=6, pipeline_discovery_risk_disease_generic_not_confirmed=1, pipeline_schema_risk_hantavirus_model_not_yet_updated=1, platform_is_preprint_or_self_deposit_repository=1, possible_content_aggregator_or_repackager=1, possible_derivative_or_syndicated_source=2, primary_or_authoritative_source=31, primary_source_citation_within_video_unverified=1, projection_framing_not_observed_surveillance_data=1, screening_and_critic_disagree=8, screening_and_critic_disagree_requires_resolution=1, screening_and_critic_disagree_unresolved=1, secondary_news_or_media_source=7, secondary_or_tertiary_media_reporting_likely=1, source_disease_relevance:ambiguous_disease=2, source_disease_relevance:insufficient_text=2, source_disease_relevance:target_disease_match=40, source_metadata_matches_requested_disease=40, source_time_matches_requested_window=25, source_type_tag_mismatch_academic_not_news=1, standard_web_page=27, structured_data_source=8, task_location_granularity=15, time_window_match_from_planned_query=19, unverified_domain_authority=1, upstream_official_source_should_be_pursued_directly=1, use_as_pointer_to_official_ms_svsa_boletim_not_as_primary_source=1, youtube_video_platform_no_editorial_accountability=1`
- LLM assessed count: `4`
- LLM failure count: `0`
- Needs review count: `18`

### 6.3.5 Source Identity / Publisher Assessment

- Identity assessed source count: `44`
- LLM identity assessed source count: `0`
- Post-fetch identity assessed source count: `37`
- Unknown publisher count: `30`
- Source type counts: `international_public_health_agency=9, news_media=4, official_public_health_agency=14, secondary_aggregator=3, social_media=4, structured_database=2, unknown=8`
- Claim support role counts: `context_only=15, corroboration_support=7, insufficient_information=12, primary_case_claim_support=10`
- Fetch use counts: `fetch_for_context=15, fetch_for_extraction=17, fetch_only_after_review=12`
- Warning counts: `actual_publisher_unknown=33, direct_target_official_fast_path_skips_source_identity=44, publisher_from_search_metadata_unverified=44, search_provider_not_publisher=44`

### 6.4 LLM Structured Extraction

- Extraction mode: `llm_structured_output`
- Eligible chunk count: `395`
- LLM call count: `30`
- LLM success count: `30`
- LLM error count: `0`
- Raw record count: `27`

## 7. 最终抽取 records

- Normalized record count: `26`
- Run quality status: `no_primary_case_dataset_records`
- Final dataset mode: `task_aware_quality_gated_records`
- Quality-gated accepted final dataset count: `0`
- Final case dataset count: `0`
- Zero-case statement count: `0`
- Exposure-monitoring record count: `0`
- Surveillance summary record count: `5`
- Outbreak summary record count: `0`
- Context record count: `6`
- Unclassified observation count: `3`
- Observation dataset view counts: `{'final_case_dataset': 0, 'global_outbreak_event_dataset': 0, 'regional_surveillance_dataset': 0, 'country_year_aggregate_dataset': 0, 'official_alert_dataset': 0, 'probable_case_dataset': 0, 'suspected_case_dataset': 0, 'unspecified_case_dataset': 0, 'death_dataset': 0, 'hospitalization_dataset': 0, 'zero_case_statements': 0, 'exposure_monitoring_records': 0, 'surveillance_summary_records': 5, 'outbreak_summary_records': 0, 'context_records': 6, 'non_primary_observations': 8, 'unclassified_observation_records': 3}`
- Pre-quality-gate record count: `26`
- Quarantined record count: `11`
- Pending review record count: `15`
- Non-primary observation count: `5`
- Final dataset post-review count: `0`
- Primary-case dataset status: `no_primary_case_dataset_records`
- Recommended primary dataset message: `No primary case dataset records were accepted; inspect zero-case, exposure-monitoring, context, and other observation views.`
- Primary-case eligible accepted count: `0`
- Corroborated primary case event count: `0`
- Record inclusion status counts: `{'quarantined_outside_scope': 10, 'pending_human_review': 15, 'quarantined_schema_invalid': 1}`
- Run quality warnings: `['no_primary_case_dataset_records', 'no_corroborated_primary_case_events']`
- Accepted source counts: `none`

No quality-gated records are available to list.
Candidate records, if any, are recorded in the pre-quality, quarantined, and pending-review artifacts.

| Record ID | Date / period | Location | Cases | Deaths | Source | LLM used |
|---|---|---|---|---|---|---|

## 8. Validation 对比

### Claim-level corroboration

- Claim count: `31`
- Claim comparison count: `465`
- Corroborated event count: `7`
- Corroborated primary case event count: `0`
- Observation type counts: `ambiguous_public_health_observation=3, confirmed_case_record=1, death_record=11, probable_case_record=5, unspecified_case_record=11`
- Corroboration status counts: `conflicting_claims=1, insufficient_information=2, single_source_unverified=4`

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

- Human review item count: `115`
- Evaluation review flag count: `0`
- Anomaly review item count: `28`

| Review ID | Type | Related IDs | Reason |
|---|---|---|---|
| review_source_credibility_src_search_4520d2861241 | source_credibility | src_search_4520d2861241 | disease_relevant_but_location_unclear; missing_publisher |
| review_source_src_search_4520d2861241 | source_screening | src_search_4520d2861241 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_8a863e6c52f9 | source_credibility | src_search_8a863e6c52f9 | disease_relevant_but_location_unclear; missing_publisher |
| review_source_src_search_8a863e6c52f9 | source_screening | src_search_8a863e6c52f9 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_9f1bffa1139f | source_credibility | src_search_9f1bffa1139f | disease_relevant_but_location_unclear; missing_publisher |
| review_source_src_search_9f1bffa1139f | source_screening | src_search_9f1bffa1139f | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_0cb54d17a3e3 | source_credibility | src_search_0cb54d17a3e3 | disease_relevant_but_location_unclear; missing_publisher |
| review_source_src_search_0cb54d17a3e3 | source_screening | src_search_0cb54d17a3e3 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_src_search_f28b6af274cc | source_screening | src_search_f28b6af274cc | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_credibility_src_search_042037d6ca22 | source_credibility | src_search_042037d6ca22 | disease_relevant_but_location_unclear; missing_publisher |
| review_source_src_search_042037d6ca22 | source_screening | src_search_042037d6ca22 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_5f398ee9785b | source_credibility | src_search_5f398ee9785b | disease_relevant_but_location_unclear; missing_publisher |

## 9.5 Stage 11 anomaly detection and review application

- Anomaly result count: `34`
- Anomaly severity counts: `high=22, low=6, medium=6`
- Anomaly needs-human-review count: `28`
- Decisions provided: `0`
- Decisions applied: `0`
- Decisions rejected: `0`
- Audit entries: `0`
- Final dataset post-review count: `0`
- Records excluded by review: `0`

| Anomaly ID | Type | Severity | Target | Reason |
|---|---|---|---|---|
| anom_001 | abrupt_spike_simple_threshold | high | rec_src_search_619f95867581_001 | case count exceeds configured simple anomaly threshold |
| anom_002 | abrupt_spike_simple_threshold | high | rec_src_search_c543063343d0_001 | case count exceeds configured simple anomaly threshold |
| anom_003 | abrupt_spike_simple_threshold | high | rec_src_search_89d26cc955fb_001 | case count exceeds configured simple anomaly threshold |
| anom_004 | deaths_without_case_reference | low | rec_src_search_89d26cc955fb_002 | deaths present but no comparable case count is available |
| anom_005 | abrupt_spike_simple_threshold | high | rec_src_search_89d26cc955fb_003 | case count exceeds configured simple anomaly threshold |
| anom_006 | abrupt_spike_simple_threshold | medium | rec_src_search_89d26cc955fb_004 | case count exceeds configured simple anomaly threshold |
| anom_007 | abrupt_spike_simple_threshold | medium | rec_src_search_89d26cc955fb_005 | case count exceeds configured simple anomaly threshold |
| anom_008 | deaths_without_case_reference | low | rec_src_search_89d26cc955fb_006 | deaths present but no comparable case count is available |
| anom_009 | deaths_without_case_reference | low | rec_src_search_89d26cc955fb_007 | deaths present but no comparable case count is available |
| anom_010 | abrupt_spike_simple_threshold | high | rec_src_search_89d26cc955fb_009 | case count exceeds configured simple anomaly threshold |
| anom_011 | abrupt_spike_simple_threshold | high | rec_src_search_9cacbefd56b5_001 | case count exceeds configured simple anomaly threshold |
| anom_012 | deaths_without_case_reference | low | rec_src_search_9cacbefd56b5_002 | deaths present but no comparable case count is available |

| Applied decision | Type | Target | Audit IDs | Reason |
|---|---|---|---|---|

## 10. 输出文件

- Run output directory: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_dengue_brazil_2024_q1`
- Collection final dataset: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_dengue_brazil_2024_q1\collection\final_dataset.csv`
- Collection final case dataset: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_dengue_brazil_2024_q1\collection\final_case_dataset.csv`
- Collection zero-case statements: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_dengue_brazil_2024_q1\collection\zero_case_statements.csv`
- Collection exposure-monitoring records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_dengue_brazil_2024_q1\collection\exposure_monitoring_records.csv`
- Collection surveillance summaries: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_dengue_brazil_2024_q1\collection\surveillance_summary_records.csv`
- Collection outbreak summaries: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_dengue_brazil_2024_q1\collection\outbreak_summary_records.csv`
- Collection context records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_dengue_brazil_2024_q1\collection\context_records.csv`
- Collection unclassified observations: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_dengue_brazil_2024_q1\collection\unclassified_observation_records.csv`
- Collection observation dataset summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_dengue_brazil_2024_q1\collection\observation_type_dataset_summary.json`
- Collection pre-quality-gate records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_dengue_brazil_2024_q1\collection\final_dataset_pre_quality_gate.csv`
- Collection quarantined records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_dengue_brazil_2024_q1\collection\quarantined_records.csv`
- Collection pending review records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_dengue_brazil_2024_q1\collection\pending_review_records.csv`
- Collection non-primary observations: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_dengue_brazil_2024_q1\collection\non_primary_observations.csv`
- Collection record inclusion decisions: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_dengue_brazil_2024_q1\collection\record_inclusion_decisions.json`
- Collection final dataset post-review: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_dengue_brazil_2024_q1\collection\final_dataset_post_review.csv`
- Collection anomaly results: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_dengue_brazil_2024_q1\collection\anomaly_results.json`
- Collection human review audit trail: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_dengue_brazil_2024_q1\collection\human_review_audit_trail.json`
- Collection source registry: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_dengue_brazil_2024_q1\collection\source_registry.json`
- Validation mode: `diagnostic_only`
- Validation records source: `state`
- Validation records output: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_dengue_brazil_2024_q1\validation\ground_truth_records.csv`
- Inactive validation records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_dengue_brazil_2024_q1\validation\inactive_validation_records.csv`
- Validation compatibility summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_dengue_brazil_2024_q1\validation\validation_source_compatibility_summary.json`
- Evaluation report CSV: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_dengue_brazil_2024_q1\evaluation\evaluation_report.csv`
- Human-readable report: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_dengue_brazil_2024_q1\workflow_run_report_chinese.md`

## 11. 当前结论

This workflow run executed the configured data collection workflow through the exported graph and artifact pipeline. The user-facing run status is: COMPLETED WITH NO PRIMARY CASE DATASET RECORDS: workflow completed, but no primary case records were accepted into final_dataset.
The run completed technically, but it should not be read as a successful data collection result because no quality-gated accepted records were produced.

- Package metadata says LLM used: `True`
- Contains synthetic fixture data: `False`
- Generated at UTC: `2026-06-25T22:27:19.231734+00:00`

## 12. Workflow visualization artifacts

- Workflow visualization index: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_dengue_brazil_2024_q1\workflow_visualization\index.html`
- Workflow timeline: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_dengue_brazil_2024_q1\workflow_visualization\workflow_timeline.html`
- Evidence flow graph: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_dengue_brazil_2024_q1\workflow_visualization\evidence_flow_graph.html`
- Claim comparison cards: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_dengue_brazil_2024_q1\workflow_visualization\claim_comparison_cards.html`
- Dataset decision flow: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_dengue_brazil_2024_q1\workflow_visualization\dataset_decision_flow.html`
- Human review workflow visualization: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_dengue_brazil_2024_q1\workflow_visualization\human_review_workflow.html`
- Visualization summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round08_dengue_brazil_2024_q1\workflow_visualization\workflow_visualization_summary.json`
