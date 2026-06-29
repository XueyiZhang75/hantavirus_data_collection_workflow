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
- Search-derived source candidates: `48`
- Iterative source discovery: `True`
- Iterative search iterations: `2`
- Iterative stop decision: `stop_limits_reached`
- Iterative stop reason: `max_iterations reached (2/2); max_queries consumed (8 executed across 2 iterations, within the 10-query ceiling). No further query batches may be issued.`
- Source credibility assessed sources: `48`
- Source credibility role counts: `{'collection': 14, 'validation': 21, 'context': 11, 'excluded': 2}`
- Source identity assessed sources: `48`
- Source identity type counts: `{'official_public_health_agency': 16, 'unknown': 12, 'international_public_health_agency': 7, 'structured_database': 1, 'news_media': 6, 'social_media': 2, 'secondary_aggregator': 3, 'background_fact_sheet': 1}`
- Source identity warning counts: `{'search_provider_not_publisher': 48, 'publisher_from_search_metadata_unverified': 48, 'actual_publisher_unknown': 40, 'direct_target_official_fast_path_skips_source_identity': 48}`
- Source discovery method: `live_search_only`
- Disease relevance target: `Dengue`
- Disease relevance source status counts: `{'target_disease_match': 42, 'ambiguous_disease': 2, 'insufficient_text': 4}`
- Disease relevance chunk status counts: `{'target_disease_match': 371, 'ambiguous_disease': 13, 'related_context_only': 2, 'insufficient_text': 2}`
- Disease relevance record status counts: `{'compatible': 54}`
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
- Exposure-monitoring record count: `1`
- Surveillance summary record count: `9`
- Outbreak summary record count: `1`
- Context record count: `15`
- Unclassified observation count: `3`
- Observation dataset view counts: `{'final_case_dataset': 0, 'global_outbreak_event_dataset': 0, 'regional_surveillance_dataset': 0, 'country_year_aggregate_dataset': 0, 'official_alert_dataset': 0, 'probable_case_dataset': 0, 'suspected_case_dataset': 0, 'unspecified_case_dataset': 0, 'death_dataset': 0, 'hospitalization_dataset': 0, 'zero_case_statements': 0, 'exposure_monitoring_records': 1, 'surveillance_summary_records': 9, 'outbreak_summary_records': 1, 'context_records': 15, 'non_primary_observations': 15, 'unclassified_observation_records': 3}`
- Pre-quality-gate record count: `18`
- Quarantined record count: `6`
- Pending review record count: `12`
- Non-primary observation count: `11`
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
6. `source_discovery` - Discovered 48 source candidates using live_search_only.
7. `source_dedup_and_registry` - Built source registry with 48 entries (0 duplicates dropped).
8. `source_screening` - Screened 48 sources using deterministic policy.
9. `source_critic_and_uncertainty_routing` - Critic reviewed 48 sources; 38 ready for fetch, 0 deferred, 25 flagged for human review.
10. `content_fetch_and_parse` - Built 38 fetch requests, produced 38 documents (live_fetch_enabled=True, fixture_documents_enabled=False, fixtures_lo...
11. `document_quality_check` - Quality-checked 38 documents: 30 usable, 2 partial, 0 offline stub, 0 parse deferred, 6 unusable.
12. `evidence_chunking_and_data_presence_flagging` - Chunked 32/38 documents into 388 evidence chunks (364 flagged as containing target data).
13. `structured_extraction` - Built 18 raw records (extraction_mode=llm_structured_output, llm_enabled=True).
14. `schema_validation_and_repair` - Validated 18 raw records: 18 validated (3 need review), 0 rejected.
15. `record_normalization` - Normalized 18/18 records (3 need review).
16. `record_linking` - Linked 18/18 normalized records into 15 candidate events.
17. `cross_source_consistency_check` - Checked 3 multi-record events; found 2 new conflicts and 53 validation results (0 events need review).
18. `quality_gate_routing` - Human review disabled; preserving review flags as audit metadata and routing to final_data_package_builder.
19. `final_data_package_builder` - Assembled hardened FinalDataPackage from current state.

## 4. 数据源分工

| Role | Source ID | Publisher / title | Credibility | Final decision | Fetch ready |
|---|---|---|---|---|---|
| context_only | src_search_1dbf2c45d0a6 | / Brazil in state of emergency due to dengue fever: 1 million cases so ... | needs_review (0.5735) | needs_human_review | False |
| context_only | src_search_da7ccbd13318 | / Brazil Has a Dengue Emergency, Portending a Health Crisis for the Americas - The New York Times | needs_review (0.541) | needs_human_review | False |
| context_only | src_search_2e8e30169e0b | / Dengue outbreak in Brazil prompting emergency health measures | needs_review (0.5434) | needs_human_review | False |
| context_only | src_search_3ab93461f77b | / 2024 dengue outbreak in Latin America and the Caribbean | needs_review (0.5024) | needs_human_review | False |
| context_only | src_search_f70e61906754 | / Dengue state of emergency declared in 21 cities in São Paulo state | low (0.4791) | needs_human_review | False |
| context_only | src_search_beb2acd883bf | / Reported cases of dengue in Brazil from 2015 to 2024 - MedCrave online | medium (0.5618) | needs_human_review | False |
| context_only | src_search_87a1569617ed | / Brazil/World Mosquito Program | low (0.3874) | needs_human_review | False |
| context_only | src_search_aa046585f404 | / Brazil records more than 5,600 deaths from dengue in 2024 - YouTube | high (0.7823) | include_for_content_fetch | False |
| context_only | src_search_52123c6cbbdd | / Brazil 2024 Record-Breaking Dengue Outbreak / Dengue.com | medium (0.5618) | needs_human_review | False |
| context_only | src_search_c543063343d0 | / Brazil MOH: Dengue cases in 2024 - Outbreak News Today | medium (0.5569) | needs_human_review | False |
| context_only | src_search_7e0b0805f573 | / Dengue outbreaks in Brazil and Latin America | low (0.5226) | needs_human_review | False |
| other | src_search_5fd7d33501e8 | / Ministério da Saúde divulga novos dados da dengue e demais arboviroses - APM | high (0.6266) | include_for_content_fetch | True |
| other | src_search_4520d2861241 | / [PDF] 2024 - Boletim Epidemiológico | high (0.5898) | include_for_content_fetch | True |
| other | src_search_2eb1c67db46f | / [PDF] Informe Epidemiológico DENGUE, CHIKUNGUNYA E ZIKA - GHC | high (0.5506) | include_for_content_fetch | True |
| other | src_search_17249087cee3 | / Boletim epidemiológico - Ecologia e Saúde | high (0.6266) | include_for_content_fetch | True |
| other | src_search_4e6c9d96071d | / Análise epidemiológica da Dengue no Brasil: uma série histórica 10 ... | high (0.6474) | include_for_content_fetch | True |
| other | src_search_042037d6ca22 | / Boletim Epidemiológico – Dengue, Chikungunya E Zika / Secretaria De Estado De Saúde De Minas Gerais | high (0.6266) | include_for_content_fetch | True |
| other | src_search_9baddae323c5 | / [PDF] Boletim Epidemiológico - Secretaria de Saúde do Distrito Federal | high (0.569) | include_for_content_fetch | True |
| other | src_search_9056ec86ef3d | / [PDF] Boletim Epidemiológico | high (0.569) | include_for_content_fetch | True |
| other | src_search_e6a611dc2382 | World Health Organization / Epidemiological Alert - Increase in dengue cases in the Americas Region - 7 October 2024 - Brazil / ReliefWeb | high (0.8594) | include_for_content_fetch | True |
| other | src_search_bda921ee5182 | Pan American Health Organization / [PDF] Epidemiological Update Increase in dengue cases in the Region of ... | medium (0.7472) | include_for_content_fetch | True |
| other | src_search_f4f555107be5 | Pan American Health Organization / Epidemiological Update - Increase in dengue cases in the Region of ... | high (0.8232) | include_for_content_fetch | True |
| other | src_search_9c7738debb9e | National Center for Biotechnology Information / The greatest Dengue epidemic in Brazil: Surveillance, Prevention, and Control | high (0.8642) | include_for_content_fetch | True |
| other | src_search_d67b1bd84e67 | / PAHO updates dengue situation in the Americas, recommends strengthened surveillance and health system preparedness | high (0.7816) | include_for_content_fetch | True |
| other | src_search_90b5fc59aef2 | Pan American Health Organization / Situation Report N.1: Dengue Epidemiological Situation in the Americas - 14 December 2023 - PAHO/WHO /... | high (0.8048) | include_for_content_fetch | True |
| other | src_search_fe4e8f3af932 | / Brazil surpasses 1000 dengue deaths in 2025 - BEACON | high (0.841) | include_for_content_fetch | True |
| other | src_search_60f9228c083d | Pan American Health Organization / Dengue Multi-Country Outbreak - PAHO/WHO / Pan American Health Organization | high (0.8048) | include_for_content_fetch | True |
| other | src_search_bca377d72697 | / Governo e estados divergem sobre mortos pela dengue - 06/03/2024 - Equilíbrio e Saúde - Folha | medium (0.6178) | include_for_content_fetch | True |
| other | src_search_5f0c9a8b5245 | / [PDF] Boletim Epidemiológico das Arboviroses | medium (0.597) | include_for_content_fetch | True |
| other | src_search_0cb54d17a3e3 | / Dengue aumentou 400% no Brasil em 2024 em comparação ao ano passado - Cofen | medium (0.6178) | include_for_content_fetch | True |
| other | src_search_f79ff78ee4b3 | / 050+n4+Contempor%C3%A2nea.pdf | high (0.3994) | include_for_content_fetch | True |
| other | src_search_4ac3da6a3dca | / [PDF] INFORMATIVO EPIDEMIOLÓGICO SEMESTRAL | high (0.4018) | include_for_content_fetch | True |
| other | src_search_ecf0b5d00c07 | / Portal de Dados Abertos do SUS | high (0.3834) | include_for_content_fetch | True |
| other | src_search_5f398ee9785b | / Info Dengue | medium (0.5786) | include_for_content_fetch | True |
| other | src_search_387675deae44 | / Indicadores de Dengue Brasil 2024: Informe SE 06 / PDF - Scribd | high (0.5898) | include_for_content_fetch | True |
| other | src_search_1e3a74a1fa2c | / [PDF] INDICADORES DE DENGUE (2024) Nº DE CASOS PROVÁVEIS DE ... | high (0.5898) | include_for_content_fetch | True |
| other | src_search_86d6f702e073 | / [PDF] SEMANAL - Poder360 | excluded (0.3738) | include_for_content_fetch | True |
| other | src_search_9f1bffa1139f | / Casos de dengue em 2024 passam de 6,4 milhões; mortes somam 5,9 mil / Agência Brasil | high (0.6658) | include_for_content_fetch | True |
| other | src_search_066d8ce49c2c | / Boletins da Dengue / Paraná contra a Dengue: Mude sua atitude | high (0.6266) | include_for_content_fetch | True |
| other | src_search_df7c57966665 | / Brazil Tries New Vaccine As 'Exponential' Rise In Dengue Cases Plagues The Americas - Health Policy Watch | high (0.841) | include_for_content_fetch | True |
| other | src_search_c19140f0ec24 | Pan American Health Organization / PAHO calls for collective action in response to record increase in dengue cases in the Americas - PAHO... | high (0.8232) | include_for_content_fetch | True |
| other | src_search_6dae7aeadbda | / Brasil - The greatest Dengue epidemic in Brazil: Surveillance, Prevention, and Control The greatest Dengue epidemic in Brazil: Surveill... | high (0.841) | include_for_content_fetch | True |
| other | src_search_1a6203f794f1 | Pan American Health Organization / [PDF] Epidemiological Alert Increase in dengue cases in the Americas ... | medium (0.7472) | include_for_content_fetch | True |
| other | src_search_4680c60f7257 | / Dengue, Brazil - BEACON | high (0.8202) | include_for_content_fetch | True |
| other | src_search_29507a107a69 | Pan American Health Organization / Epidemiological Alert - Increase in dengue cases in the Region of ... | high (0.8232) | include_for_content_fetch | True |
| other | src_search_1e36efa321f9 | / Dengue cases in Brazil drop by more than 70% in 2025 - BEACON | high (0.8639) | include_for_content_fetch | True |
| other | src_search_2c14c05742aa | / Painel de indicadores da Dengue - Rio de Janeiro | high (0.6266) | include_for_content_fetch | True |
| other | src_search_bc5de45a99e4 | / informe-semanal-no-02-coe | excluded (0.4658) | include_for_content_fetch | True |

## 5. 真实网页抓取结果

- Documents fetched/parsed: `38`
- Search-derived sources selected for fetch: `38`
- Search-derived skipped by reason: `{}`
- Fetch status counts: `fetched=38`
- External fetch enabled: `True`
- Fetch provider counts: `native_requests=2, tavily_extract=36`
- External fetch failure counts: `tavily_extract=2`
- Selected fetch bucket counts: `target_official_authority=38`
- Parser status counts: `parsed_html=2, parsed_text=36`
- Parser used counts: `html_stdlib_parser=2, text_parser=36`
- Quality status counts: `partial=2, unusable=6, usable=30`
- Validation-reserved skipped from fetch: `[]`

| Source ID | Provider | Fetch status | HTTP | Parse | Parser | Quality | Text chars | Tables |
|---|---|---|---|---|---|---|---|---|
| src_search_9f1bffa1139f | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 11853 | 0 |
| src_search_4e6c9d96071d | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 9681 | 0 |
| src_search_5fd7d33501e8 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 7596 | 0 |
| src_search_17249087cee3 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 49766 | 0 |
| src_search_042037d6ca22 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 29439 | 0 |
| src_search_066d8ce49c2c | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 247295 | 0 |
| src_search_387675deae44 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 4169 | 0 |
| src_search_4520d2861241 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 67722 | 0 |
| src_search_1e3a74a1fa2c | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 10962 | 0 |
| src_search_9baddae323c5 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 23962 | 0 |
| src_search_9056ec86ef3d | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 43725 | 0 |
| src_search_2eb1c67db46f | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 6107 | 0 |
| src_search_86d6f702e073 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 10224 | 0 |
| src_search_9c7738debb9e | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 109870 | 0 |
| src_search_e6a611dc2382 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 3993 | 0 |
| src_search_df7c57966665 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 7989 | 0 |
| src_search_6dae7aeadbda | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 45844 | 0 |
| src_search_fe4e8f3af932 | native_requests | fetched | 200 | parsed_html | html_stdlib_parser | partial | 129 | 0 |
| src_search_c19140f0ec24 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 10754 | 0 |
| src_search_f4f555107be5 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 6510 | 0 |
| src_search_29507a107a69 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 7437 | 0 |
| src_search_4680c60f7257 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 2124 | 0 |
| src_search_90b5fc59aef2 | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 5946 | 0 |
| src_search_60f9228c083d | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 23170 | 0 |
| src_search_d67b1bd84e67 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 10861 | 0 |
| src_search_bda921ee5182 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 30521 | 0 |
| src_search_1a6203f794f1 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 34502 | 0 |
| src_search_1e36efa321f9 | native_requests | fetched | 200 | parsed_html | html_stdlib_parser | partial | 129 | 0 |
| src_search_aa046585f404 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 2013 | 0 |
| src_search_2c14c05742aa | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 1290 | 0 |
| src_search_bca377d72697 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 15598 | 0 |
| src_search_0cb54d17a3e3 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 7332 | 0 |
| src_search_5f0c9a8b5245 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 22774 | 0 |
| src_search_5f398ee9785b | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 2348 | 0 |
| src_search_bc5de45a99e4 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 13301 | 0 |
| src_search_4ac3da6a3dca | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 11181 | 0 |
| src_search_f79ff78ee4b3 | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 41243 | 0 |
| src_search_ecf0b5d00c07 | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 33332 | 0 |

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
- Stop decision: `stop_limits_reached`
- Stop reason: `max_iterations reached (2/2); max_queries consumed (8 executed across 2 iterations, within the 10-query ceiling). No further query batches may be issued.`
- Query source counts: `{'iterative_llm_initial_search_plan': 4, 'iterative_llm_refinement': 4}`
- Iteration query counts: `{'1': 4, '2': 4}`

### 6.2 LLM Source Critic

- Attempted source count: `0`
- Assessed source count: `0`
- Skipped source count: `48`
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
- Assessed source count: `48`
- Final role counts: `collection=14, context=11, excluded=2, validation=21`
- Risk flag counts: `ambiguous_disease=6, ambiguous_disease_signal_in_source_metadata=2, ambiguous_location=22, channel_identity_unverified=1, cited_primary_sources_not_yet_identified=1, complete_source_provenance=8, context_or_background_only=2, crowd_edited_content_subject_to_revision=1, data_figures_unverified_without_tracing_to_primary_source=1, data_not_directly_extractable_from_news_narrative=1, data_signal_in_source_metadata=48, disease_relevance_unclear=4, do_not_use_as_primary_extraction_source_without_tracing_to_official_bulletin=1, extraction_record_schema_mismatch_warning_active=1, figures_likely_derived_from_official_sources_not_independently_verified=1, geographic_granularity_unclear=22, geographic_scope_broader_than_task_brazil_only=1, independence_unclear=15, independence_unclear_data_provenance_chain_unconfirmed=1, international_organization_authority=6, local_or_subnational_granularity=3, local_source_matches_task_location=16, location_match_from_planned_query=10, location_relevance_unclear=22, low_authority_relevant_source=9, low_epidemiological_authority_for_primary_extraction=1, low_machine_readability=9, machine_readable_or_structured=7, missing_publisher=40, missing_publisher_metadata=1, national_or_international_granularity=10, official_public_health_authority=25, pdf_or_report_likely_medium_readability=9, pipeline_schema_mismatch_risk_active=1, possible_derivative_or_syndicated_source=2, primary_or_authoritative_source=31, quantitative_extraction_not_supported_from_video_format=1, risk_penalty_applied_0.20=1, screening_and_critic_disagree=11, screening_and_critic_disagree_requires_adjudication=1, secondary_news_or_media_source=10, source_discovery_not_yet_disease_generic_warning_active=1, source_disease_relevance:ambiguous_disease=2, source_disease_relevance:insufficient_text=4, source_disease_relevance:target_disease_match=42, source_metadata_matches_requested_disease=42, source_time_matches_requested_window=25, standard_web_page=32, structured_data_source=7, task_location_granularity=13, time_window_match_from_planned_query=23, unknown_publisher_identity=1, upstream_cited_sources_should_be_collected_directly=1, use_as_pointer_to_primary_sources_only=1, video_platform_not_machine_readable=1, wikipedia_tertiary_source_not_suitable_for_primary_data_extraction=1`
- LLM assessed count: `4`
- LLM failure count: `0`
- Needs review count: `17`

### 6.3.5 Source Identity / Publisher Assessment

- Identity assessed source count: `48`
- LLM identity assessed source count: `0`
- Post-fetch identity assessed source count: `38`
- Unknown publisher count: `39`
- Source type counts: `background_fact_sheet=1, international_public_health_agency=7, news_media=6, official_public_health_agency=16, secondary_aggregator=3, social_media=2, structured_database=1, unknown=12`
- Claim support role counts: `context_only=16, corroboration_support=9, insufficient_information=14, primary_case_claim_support=9`
- Fetch use counts: `fetch_for_context=16, fetch_for_extraction=18, fetch_only_after_review=14`
- Warning counts: `actual_publisher_unknown=40, direct_target_official_fast_path_skips_source_identity=48, publisher_from_search_metadata_unverified=48, search_provider_not_publisher=48`

### 6.4 LLM Structured Extraction

- Extraction mode: `llm_structured_output`
- Eligible chunk count: `386`
- LLM call count: `30`
- LLM success count: `30`
- LLM error count: `0`
- Raw record count: `18`

## 7. 最终抽取 records

- Normalized record count: `18`
- Run quality status: `no_primary_case_dataset_records`
- Final dataset mode: `task_aware_quality_gated_records`
- Quality-gated accepted final dataset count: `0`
- Final case dataset count: `0`
- Zero-case statement count: `0`
- Exposure-monitoring record count: `1`
- Surveillance summary record count: `9`
- Outbreak summary record count: `1`
- Context record count: `15`
- Unclassified observation count: `3`
- Observation dataset view counts: `{'final_case_dataset': 0, 'global_outbreak_event_dataset': 0, 'regional_surveillance_dataset': 0, 'country_year_aggregate_dataset': 0, 'official_alert_dataset': 0, 'probable_case_dataset': 0, 'suspected_case_dataset': 0, 'unspecified_case_dataset': 0, 'death_dataset': 0, 'hospitalization_dataset': 0, 'zero_case_statements': 0, 'exposure_monitoring_records': 1, 'surveillance_summary_records': 9, 'outbreak_summary_records': 1, 'context_records': 15, 'non_primary_observations': 15, 'unclassified_observation_records': 3}`
- Pre-quality-gate record count: `18`
- Quarantined record count: `6`
- Pending review record count: `12`
- Non-primary observation count: `11`
- Final dataset post-review count: `0`
- Primary-case dataset status: `no_primary_case_dataset_records`
- Recommended primary dataset message: `No primary case dataset records were accepted; inspect zero-case, exposure-monitoring, context, and other observation views.`
- Primary-case eligible accepted count: `0`
- Corroborated primary case event count: `0`
- Record inclusion status counts: `{'pending_human_review': 12, 'quarantined_outside_scope': 4, 'quarantined_schema_invalid': 2}`
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
- Corroborated event count: `7`
- Corroborated primary case event count: `0`
- Observation type counts: `ambiguous_public_health_observation=3, confirmed_case_record=2, death_record=5, outbreak_summary=1, probable_case_record=4, suspected_case_record=4, unspecified_case_record=5`
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

- Human review item count: `81`
- Evaluation review flag count: `0`
- Anomaly review item count: `13`

| Review ID | Type | Related IDs | Reason |
|---|---|---|---|
| review_source_credibility_src_search_5fd7d33501e8 | source_credibility | src_search_5fd7d33501e8 | disease_relevant_but_location_unclear; missing_publisher |
| review_source_src_search_5fd7d33501e8 | source_screening | src_search_5fd7d33501e8 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_4520d2861241 | source_credibility | src_search_4520d2861241 | disease_relevant_but_location_unclear; missing_publisher |
| review_source_src_search_4520d2861241 | source_screening | src_search_4520d2861241 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_2eb1c67db46f | source_credibility | src_search_2eb1c67db46f | disease_relevant_but_location_unclear; missing_publisher |
| review_source_src_search_2eb1c67db46f | source_screening | src_search_2eb1c67db46f | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_17249087cee3 | source_credibility | src_search_17249087cee3 | disease_relevant_but_location_unclear; missing_publisher |
| review_source_src_search_17249087cee3 | source_screening | src_search_17249087cee3 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_4e6c9d96071d | source_credibility | src_search_4e6c9d96071d | disease_relevant_but_location_unclear; missing_publisher |
| review_source_src_search_4e6c9d96071d | source_screening | src_search_4e6c9d96071d | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_042037d6ca22 | source_credibility | src_search_042037d6ca22 | disease_relevant_but_location_unclear; missing_publisher |
| review_source_src_search_042037d6ca22 | source_screening | src_search_042037d6ca22 | Source classified as data_source; both screening and critic agree to include for content fetch. |

## 9.5 Stage 11 anomaly detection and review application

- Anomaly result count: `14`
- Anomaly severity counts: `high=13, low=1`
- Anomaly needs-human-review count: `13`
- Decisions provided: `0`
- Decisions applied: `0`
- Decisions rejected: `0`
- Audit entries: `0`
- Final dataset post-review count: `0`
- Records excluded by review: `0`

| Anomaly ID | Type | Severity | Target | Reason |
|---|---|---|---|---|
| anom_001 | abrupt_spike_simple_threshold | high | rec_src_search_5fd7d33501e8_001 | case count exceeds configured simple anomaly threshold |
| anom_002 | abrupt_spike_simple_threshold | high | rec_src_search_5fd7d33501e8_002 | case count exceeds configured simple anomaly threshold |
| anom_003 | abrupt_spike_simple_threshold | high | rec_src_search_df7c57966665_002 | case count exceeds configured simple anomaly threshold |
| anom_004 | abrupt_spike_simple_threshold | high | rec_src_search_6dae7aeadbda_001 | case count exceeds configured simple anomaly threshold |
| anom_005 | deaths_without_case_reference | low | rec_src_search_6dae7aeadbda_002 | deaths present but no comparable case count is available |
| anom_006 | abrupt_spike_simple_threshold | high | rec_src_search_6dae7aeadbda_003 | case count exceeds configured simple anomaly threshold |
| anom_007 | out_of_scope_count_bearing_record | high | event_005 | Stage 10 validation marked record outside requested scope: outside_geography |
| anom_008 | out_of_scope_count_bearing_record | high | event_009 | Stage 10 validation marked record outside requested scope: outside_time_window |
| anom_009 | out_of_scope_count_bearing_record | high | event_013 | Stage 10 validation marked record outside requested scope: outside_time_window |
| anom_010 | out_of_scope_count_bearing_record | high | event_001 | Stage 10 validation marked record outside requested scope: outside_geography;outside_time_window |
| anom_011 | out_of_scope_count_bearing_record | high | event_002 | Stage 10 validation marked record outside requested scope: outside_geography |
| anom_012 | out_of_scope_count_bearing_record | high | event_003 | Stage 10 validation marked record outside requested scope: outside_time_window |

| Applied decision | Type | Target | Audit IDs | Reason |
|---|---|---|---|---|

## 10. 输出文件

- Run output directory: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_dengue_brazil_2024_q1`
- Collection final dataset: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_dengue_brazil_2024_q1\collection\final_dataset.csv`
- Collection final case dataset: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_dengue_brazil_2024_q1\collection\final_case_dataset.csv`
- Collection zero-case statements: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_dengue_brazil_2024_q1\collection\zero_case_statements.csv`
- Collection exposure-monitoring records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_dengue_brazil_2024_q1\collection\exposure_monitoring_records.csv`
- Collection surveillance summaries: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_dengue_brazil_2024_q1\collection\surveillance_summary_records.csv`
- Collection outbreak summaries: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_dengue_brazil_2024_q1\collection\outbreak_summary_records.csv`
- Collection context records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_dengue_brazil_2024_q1\collection\context_records.csv`
- Collection unclassified observations: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_dengue_brazil_2024_q1\collection\unclassified_observation_records.csv`
- Collection observation dataset summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_dengue_brazil_2024_q1\collection\observation_type_dataset_summary.json`
- Collection pre-quality-gate records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_dengue_brazil_2024_q1\collection\final_dataset_pre_quality_gate.csv`
- Collection quarantined records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_dengue_brazil_2024_q1\collection\quarantined_records.csv`
- Collection pending review records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_dengue_brazil_2024_q1\collection\pending_review_records.csv`
- Collection non-primary observations: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_dengue_brazil_2024_q1\collection\non_primary_observations.csv`
- Collection record inclusion decisions: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_dengue_brazil_2024_q1\collection\record_inclusion_decisions.json`
- Collection final dataset post-review: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_dengue_brazil_2024_q1\collection\final_dataset_post_review.csv`
- Collection anomaly results: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_dengue_brazil_2024_q1\collection\anomaly_results.json`
- Collection human review audit trail: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_dengue_brazil_2024_q1\collection\human_review_audit_trail.json`
- Collection source registry: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_dengue_brazil_2024_q1\collection\source_registry.json`
- Validation mode: `diagnostic_only`
- Validation records source: `state`
- Validation records output: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_dengue_brazil_2024_q1\validation\ground_truth_records.csv`
- Inactive validation records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_dengue_brazil_2024_q1\validation\inactive_validation_records.csv`
- Validation compatibility summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_dengue_brazil_2024_q1\validation\validation_source_compatibility_summary.json`
- Evaluation report CSV: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_dengue_brazil_2024_q1\evaluation\evaluation_report.csv`
- Human-readable report: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_dengue_brazil_2024_q1\workflow_run_report_chinese.md`

## 11. 当前结论

This workflow run executed the configured data collection workflow through the exported graph and artifact pipeline. The user-facing run status is: COMPLETED WITH NO PRIMARY CASE DATASET RECORDS: workflow completed, but no primary case records were accepted into final_dataset.
The run completed technically, but it should not be read as a successful data collection result because no quality-gated accepted records were produced.

- Package metadata says LLM used: `True`
- Contains synthetic fixture data: `False`
- Generated at UTC: `2026-06-25T20:51:45.013481+00:00`

## 12. Workflow visualization artifacts

- Workflow visualization index: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_dengue_brazil_2024_q1\workflow_visualization\index.html`
- Workflow timeline: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_dengue_brazil_2024_q1\workflow_visualization\workflow_timeline.html`
- Evidence flow graph: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_dengue_brazil_2024_q1\workflow_visualization\evidence_flow_graph.html`
- Claim comparison cards: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_dengue_brazil_2024_q1\workflow_visualization\claim_comparison_cards.html`
- Dataset decision flow: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_dengue_brazil_2024_q1\workflow_visualization\dataset_decision_flow.html`
- Human review workflow visualization: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_dengue_brazil_2024_q1\workflow_visualization\human_review_workflow.html`
- Visualization summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round06_dengue_brazil_2024_q1\workflow_visualization\workflow_visualization_summary.json`
