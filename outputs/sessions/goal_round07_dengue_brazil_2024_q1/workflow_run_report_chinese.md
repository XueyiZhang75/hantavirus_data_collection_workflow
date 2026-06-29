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
- Source search executed queries: `4`
- Search-derived source candidates: `28`
- Iterative source discovery: `True`
- Iterative search iterations: `1`
- Iterative stop decision: `stop_no_promising_sources`
- Iterative stop reason: `LLM requested continuation but returned no next query batch.`
- Source credibility assessed sources: `28`
- Source credibility role counts: `{'collection': 6, 'context': 9, 'validation': 13}`
- Source identity assessed sources: `28`
- Source identity type counts: `{'official_public_health_agency': 6, 'structured_database': 2, 'social_media': 4, 'international_public_health_agency': 4, 'unknown': 6, 'news_media': 4, 'secondary_aggregator': 1, 'background_fact_sheet': 1}`
- Source identity warning counts: `{'search_provider_not_publisher': 28, 'publisher_from_search_metadata_unverified': 28, 'actual_publisher_unknown': 22, 'direct_target_official_fast_path_skips_source_identity': 28}`
- Source discovery method: `live_search_only`
- Disease relevance target: `Dengue`
- Disease relevance source status counts: `{'target_disease_match': 25, 'insufficient_text': 1, 'ambiguous_disease': 2}`
- Disease relevance chunk status counts: `{'target_disease_match': 252, 'related_context_only': 3, 'ambiguous_disease': 14, 'insufficient_text': 1, 'unrelated_disease': 1}`
- Disease relevance record status counts: `{'compatible': 81}`
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
- Surveillance summary record count: `8`
- Outbreak summary record count: `1`
- Context record count: `15`
- Unclassified observation count: `2`
- Observation dataset view counts: `{'final_case_dataset': 0, 'global_outbreak_event_dataset': 0, 'regional_surveillance_dataset': 0, 'country_year_aggregate_dataset': 0, 'official_alert_dataset': 0, 'probable_case_dataset': 0, 'suspected_case_dataset': 0, 'unspecified_case_dataset': 0, 'death_dataset': 0, 'hospitalization_dataset': 0, 'zero_case_statements': 0, 'exposure_monitoring_records': 0, 'surveillance_summary_records': 8, 'outbreak_summary_records': 1, 'context_records': 15, 'non_primary_observations': 17, 'unclassified_observation_records': 2}`
- Pre-quality-gate record count: `27`
- Quarantined record count: `11`
- Pending review record count: `16`
- Non-primary observation count: `9`
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
6. `source_discovery` - Discovered 28 source candidates using live_search_only.
7. `source_dedup_and_registry` - Built source registry with 28 entries (0 duplicates dropped).
8. `source_screening` - Screened 28 sources using deterministic policy.
9. `source_critic_and_uncertainty_routing` - Critic reviewed 28 sources; 20 ready for fetch, 0 deferred, 15 flagged for human review.
10. `content_fetch_and_parse` - Built 20 fetch requests, produced 20 documents (live_fetch_enabled=True, fixture_documents_enabled=False, fixtures_lo...
11. `document_quality_check` - Quality-checked 20 documents: 15 usable, 1 partial, 0 offline stub, 0 parse deferred, 4 unusable.
12. `evidence_chunking_and_data_presence_flagging` - Chunked 16/20 documents into 271 evidence chunks (256 flagged as containing target data).
13. `structured_extraction` - Built 27 raw records (extraction_mode=llm_structured_output, llm_enabled=True).
14. `schema_validation_and_repair` - Validated 27 raw records: 27 validated (5 need review), 0 rejected.
15. `record_normalization` - Normalized 27/27 records (5 need review).
16. `record_linking` - Linked 27/27 normalized records into 14 candidate events.
17. `cross_source_consistency_check` - Checked 7 multi-record events; found 7 new conflicts and 75 validation results (2 events need review).
18. `quality_gate_routing` - Human review disabled; preserving review flags as audit metadata and routing to final_data_package_builder.
19. `final_data_package_builder` - Assembled hardened FinalDataPackage from current state.

## 4. 数据源分工

| Role | Source ID | Publisher / title | Credibility | Final decision | Fetch ready |
|---|---|---|---|---|---|
| context_only | src_search_3cd97c76f675 | / #AoVivo / Atualização do cenário epidemiológico da dengue no país | high (0.5266) | include_for_content_fetch | False |
| context_only | src_search_2e8e30169e0b | / Dengue outbreak in Brazil prompting emergency health measures | medium (0.741) | needs_human_review | False |
| context_only | src_search_bca377d72697 | / Governo e estados divergem sobre mortos pela dengue - 06/03/2024 | low (0.357) | needs_human_review | False |
| context_only | src_search_aa712b85098b | / Brasil tem quase mil mortes por dengue em investigação | low (0.3362) | needs_human_review | False |
| context_only | src_search_8a863e6c52f9 | / Brasil registra queda de quase 70% nos casos de dengue nos 2 ... | low (0.3386) | needs_human_review | False |
| context_only | src_search_08f8dd56800e | / Brasil registra mais de 1 milhão de casos de dengue em 2024 - G1 | low (0.357) | needs_human_review | False |
| context_only | src_search_a55218ea3f18 | / São Paulo tem mais de 2 milhões de casos de dengue em 2024 | low (0.357) | needs_human_review | False |
| context_only | src_search_f28b6af274cc | / Dengue mata mais que Covid-19 em 2024 no Brasil | low (0.337) | needs_human_review | False |
| context_only | src_search_55a815a5dfd8 | National Center for Biotechnology Information / Space-time dynamics of the dengue epidemic in Brazil, 2024 - PMC | medium (0.7543) | needs_human_review | False |
| other | src_search_4520d2861241 | / [PDF] 2024 - Boletim Epidemiológico | high (0.5898) | include_for_content_fetch | True |
| other | src_search_2eb1c67db46f | / [PDF] Informe Epidemiológico DENGUE, CHIKUNGUNYA E ZIKA - GHC | high (0.5506) | include_for_content_fetch | True |
| other | src_search_0cb54d17a3e3 | / Dengue aumentou 400% no Brasil em 2024 em comparação ao ano passado - Cofen | high (0.6658) | include_for_content_fetch | True |
| other | src_search_9c7738debb9e | National Center for Biotechnology Information / The greatest Dengue epidemic in Brazil: Surveillance, Prevention, and Control | high (0.8642) | include_for_content_fetch | True |
| other | src_search_042037d6ca22 | / Boletim Epidemiológico – Dengue, Chikungunya E Zika / Secretaria De Estado De Saúde De Minas Gerais | high (0.6266) | include_for_content_fetch | True |
| other | src_search_ba94b872eb23 | / Dengue, Chikungunya, Zika e Febre Amarela | high (0.6266) | include_for_content_fetch | True |
| other | src_search_5f398ee9785b | / Info Dengue | high (0.6266) | include_for_content_fetch | True |
| other | src_search_c19140f0ec24 | Pan American Health Organization / PAHO calls for collective action in response to record increase in ... | medium (0.6072) | include_for_content_fetch | True |
| other | src_search_e6a611dc2382 | World Health Organization / Epidemiological Alert - Increase in dengue cases in the Americas Region - 7 October 2024 - Brazil / ReliefWeb | high (0.8594) | include_for_content_fetch | True |
| other | src_search_beb2acd883bf | / Reported cases of dengue in Brazil from 2015 to 2024 - MedCrave online | high (0.8594) | include_for_content_fetch | True |
| other | src_search_1a6203f794f1 | Pan American Health Organization / [PDF] Epidemiological Alert Increase in dengue cases in the Americas ... | medium (0.7472) | include_for_content_fetch | True |
| other | src_search_5bd1cae37e40 | World Health Organization / Dengue - Global situation | high (0.8024) | include_for_content_fetch | True |
| other | src_search_60f9228c083d | Pan American Health Organization / Dengue Multi-Country Outbreak - PAHO/WHO | high (0.8048) | include_for_content_fetch | True |
| other | src_search_d40be1c01bdd | / Situation Report No 14 - Epidemiological Week 13, 2024 - Brazil | medium (0.6343) | include_for_content_fetch | True |
| other | src_search_cbd687ebb5a6 | / (PDF) Dengue in Brazil: An Ecological Study of Burden ... | high (0.8135) | include_for_content_fetch | True |
| other | src_search_69771f1b5bcc | / [PDF] Dengue in Brazil: An Ecological Study of Burden, Hospitalizations ... | high (0.8159) | include_for_content_fetch | True |
| other | src_search_2ac70c766155 | / Brazil reports 217K probable dengue cases during the first weeks of ... | medium (0.771) | include_for_content_fetch | True |
| other | src_search_0d8e5c276e4c | / Brasil - The greatest Dengue epidemic in Brazil: Surveillance, Prevention, and Control The greatest Dengue epidemic in Brazil: Surveill... | high (0.8159) | include_for_content_fetch | True |
| other | src_search_1e36efa321f9 | / Dengue cases in Brazil drop by more than 70% in 2025 - BEACON | high (0.8159) | include_for_content_fetch | True |

## 5. 真实网页抓取结果

- Documents fetched/parsed: `20`
- Search-derived sources selected for fetch: `20`
- Search-derived skipped by reason: `{}`
- Fetch status counts: `fetch_failed=1, fetched=19`
- External fetch enabled: `True`
- Fetch provider counts: `native_requests=2, tavily_extract=18`
- External fetch failure counts: `native_requests=1, tavily_extract=2`
- Selected fetch bucket counts: `target_official_authority=20`
- Parser status counts: `parsed_html=2, parsed_text=18`
- Parser used counts: `html_stdlib_parser=2, text_parser=18`
- Quality status counts: `partial=1, unusable=4, usable=15`
- Validation-reserved skipped from fetch: `[]`

| Source ID | Provider | Fetch status | HTTP | Parse | Parser | Quality | Text chars | Tables |
|---|---|---|---|---|---|---|---|---|
| src_search_9c7738debb9e | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 109870 | 0 |
| src_search_0cb54d17a3e3 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 7332 | 0 |
| src_search_042037d6ca22 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 29439 | 0 |
| src_search_ba94b872eb23 | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 138705 | 0 |
| src_search_5f398ee9785b | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 2348 | 0 |
| src_search_4520d2861241 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 67722 | 0 |
| src_search_2eb1c67db46f | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 6107 | 0 |
| src_search_3cd97c76f675 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 17108 | 0 |
| src_search_e6a611dc2382 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 3993 | 0 |
| src_search_beb2acd883bf | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 34313 | 0 |
| src_search_60f9228c083d | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 23170 | 0 |
| src_search_5bd1cae37e40 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 49456 | 0 |
| src_search_1a6203f794f1 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 34502 | 0 |
| src_search_c19140f0ec24 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 10754 | 0 |
| src_search_69771f1b5bcc | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 44435 | 0 |
| src_search_0d8e5c276e4c | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 45844 | 0 |
| src_search_1e36efa321f9 | native_requests | fetched | 200 | parsed_html | html_stdlib_parser | partial | 129 | 0 |
| src_search_cbd687ebb5a6 | native_requests | fetch_failed | 403 | parsed_html | html_stdlib_parser | unusable | 278 | 0 |
| src_search_2ac70c766155 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 2761 | 0 |
| src_search_d40be1c01bdd | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 2283 | 0 |

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
- Search iteration count: `1`
- LLM refinement call count: `1`
- Total queries planned: `4`
- Total queries executed: `4`
- Stop decision: `stop_no_promising_sources`
- Stop reason: `LLM requested continuation but returned no next query batch.`
- Query source counts: `{'iterative_llm_initial_search_plan': 4}`
- Iteration query counts: `{'1': 4}`

### 6.2 LLM Source Critic

- Attempted source count: `0`
- Assessed source count: `0`
- Skipped source count: `28`
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
- Assessed source count: `28`
- Final role counts: `collection=6, context=9, validation=13`
- Risk flag counts: `ambiguous_disease=2, ambiguous_disease_signal_in_source_metadata=2, ambiguous_location=13, complete_source_provenance=6, context_or_background_only=2, data_signal_in_source_metadata=28, disease_relevance_unclear=1, geographic_granularity_unclear=13, independence_unclear=11, international_organization_authority=3, local_or_subnational_granularity=7, local_source_matches_task_location=11, location_match_from_planned_query=4, location_relevance_unclear=13, low_authority_relevant_source=5, low_machine_readability=3, machine_readable_or_structured=6, missing_publisher=22, national_or_international_granularity=4, official_public_health_authority=13, pdf_or_report_likely_medium_readability=3, possible_derivative_or_syndicated_source=1, primary_or_authoritative_source=16, screening_and_critic_disagree=9, secondary_news_or_media_source=8, source_disease_relevance:ambiguous_disease=2, source_disease_relevance:insufficient_text=1, source_disease_relevance:target_disease_match=25, source_metadata_matches_requested_disease=25, source_time_matches_requested_window=15, standard_web_page=19, structured_data_source=6, task_location_granularity=4, time_window_match_from_planned_query=13`
- LLM assessed count: `0`
- LLM failure count: `0`
- Needs review count: `6`

### 6.3.5 Source Identity / Publisher Assessment

- Identity assessed source count: `28`
- LLM identity assessed source count: `0`
- Post-fetch identity assessed source count: `20`
- Unknown publisher count: `21`
- Source type counts: `background_fact_sheet=1, international_public_health_agency=4, news_media=4, official_public_health_agency=6, secondary_aggregator=1, social_media=4, structured_database=2, unknown=6`
- Claim support role counts: `context_only=8, corroboration_support=5, insufficient_information=10, primary_case_claim_support=5`
- Fetch use counts: `fetch_for_context=8, fetch_for_extraction=10, fetch_only_after_review=10`
- Warning counts: `actual_publisher_unknown=22, direct_target_official_fast_path_skips_source_identity=28, publisher_from_search_metadata_unverified=28, search_provider_not_publisher=28`

### 6.4 LLM Structured Extraction

- Extraction mode: `llm_structured_output`
- Eligible chunk count: `258`
- LLM call count: `30`
- LLM success count: `30`
- LLM error count: `0`
- Raw record count: `27`

## 7. 最终抽取 records

- Normalized record count: `27`
- Run quality status: `no_primary_case_dataset_records`
- Final dataset mode: `task_aware_quality_gated_records`
- Quality-gated accepted final dataset count: `0`
- Final case dataset count: `0`
- Zero-case statement count: `0`
- Exposure-monitoring record count: `0`
- Surveillance summary record count: `8`
- Outbreak summary record count: `1`
- Context record count: `15`
- Unclassified observation count: `2`
- Observation dataset view counts: `{'final_case_dataset': 0, 'global_outbreak_event_dataset': 0, 'regional_surveillance_dataset': 0, 'country_year_aggregate_dataset': 0, 'official_alert_dataset': 0, 'probable_case_dataset': 0, 'suspected_case_dataset': 0, 'unspecified_case_dataset': 0, 'death_dataset': 0, 'hospitalization_dataset': 0, 'zero_case_statements': 0, 'exposure_monitoring_records': 0, 'surveillance_summary_records': 8, 'outbreak_summary_records': 1, 'context_records': 15, 'non_primary_observations': 17, 'unclassified_observation_records': 2}`
- Pre-quality-gate record count: `27`
- Quarantined record count: `11`
- Pending review record count: `16`
- Non-primary observation count: `9`
- Final dataset post-review count: `0`
- Primary-case dataset status: `no_primary_case_dataset_records`
- Recommended primary dataset message: `No primary case dataset records were accepted; inspect zero-case, exposure-monitoring, context, and other observation views.`
- Primary-case eligible accepted count: `0`
- Corroborated primary case event count: `0`
- Record inclusion status counts: `{'pending_human_review': 16, 'quarantined_outside_scope': 9, 'quarantined_schema_invalid': 2}`
- Run quality warnings: `['no_primary_case_dataset_records', 'no_corroborated_primary_case_events']`
- Accepted source counts: `none`

No quality-gated records are available to list.
Candidate records, if any, are recorded in the pre-quality, quarantined, and pending-review artifacts.

| Record ID | Date / period | Location | Cases | Deaths | Source | LLM used |
|---|---|---|---|---|---|---|

## 8. Validation 对比

### Claim-level corroboration

- Claim count: `33`
- Claim comparison count: `528`
- Corroborated event count: `7`
- Corroborated primary case event count: `0`
- Observation type counts: `ambiguous_public_health_observation=2, confirmed_case_record=2, death_record=13, hospitalization_record=1, outbreak_summary=1, probable_case_record=7, suspected_case_record=3, unspecified_case_record=4`
- Corroboration status counts: `conflicting_claims=1, single_source_unverified=6`

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

- Human review item count: `82`
- Evaluation review flag count: `0`
- Anomaly review item count: `23`

| Review ID | Type | Related IDs | Reason |
|---|---|---|---|
| review_source_credibility_src_search_4520d2861241 | source_credibility | src_search_4520d2861241 | disease_relevant_but_location_unclear; missing_publisher |
| review_source_src_search_4520d2861241 | source_screening | src_search_4520d2861241 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_2eb1c67db46f | source_credibility | src_search_2eb1c67db46f | disease_relevant_but_location_unclear; missing_publisher |
| review_source_src_search_2eb1c67db46f | source_screening | src_search_2eb1c67db46f | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_0cb54d17a3e3 | source_credibility | src_search_0cb54d17a3e3 | disease_relevant_but_location_unclear; missing_publisher |
| review_source_src_search_0cb54d17a3e3 | source_screening | src_search_0cb54d17a3e3 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_src_search_3cd97c76f675 | source_screening | src_search_3cd97c76f675 | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_credibility_src_search_042037d6ca22 | source_credibility | src_search_042037d6ca22 | disease_relevant_but_location_unclear; missing_publisher |
| review_source_src_search_042037d6ca22 | source_screening | src_search_042037d6ca22 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_ba94b872eb23 | source_credibility | src_search_ba94b872eb23 | disease_relevant_but_location_unclear; missing_publisher |
| review_source_src_search_ba94b872eb23 | source_screening | src_search_ba94b872eb23 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_5f398ee9785b | source_credibility | src_search_5f398ee9785b | disease_relevant_but_location_unclear; missing_publisher |

## 9.5 Stage 11 anomaly detection and review application

- Anomaly result count: `30`
- Anomaly severity counts: `high=21, low=7, medium=2`
- Anomaly needs-human-review count: `23`
- Decisions provided: `0`
- Decisions applied: `0`
- Decisions rejected: `0`
- Audit entries: `0`
- Final dataset post-review count: `0`
- Records excluded by review: `0`

| Anomaly ID | Type | Severity | Target | Reason |
|---|---|---|---|---|
| anom_001 | abrupt_spike_simple_threshold | high | rec_src_search_c19140f0ec24_001 | case count exceeds configured simple anomaly threshold |
| anom_002 | deaths_without_case_reference | low | rec_src_search_c19140f0ec24_002 | deaths present but no comparable case count is available |
| anom_003 | abrupt_spike_simple_threshold | high | rec_src_search_0cb54d17a3e3_001 | case count exceeds configured simple anomaly threshold |
| anom_004 | abrupt_spike_simple_threshold | medium | rec_src_search_0cb54d17a3e3_001 | case count is a simple-threshold spike over prior comparable records |
| anom_005 | deaths_without_case_reference | low | rec_src_search_0cb54d17a3e3_002 | deaths present but no comparable case count is available |
| anom_006 | deaths_without_case_reference | low | rec_src_search_0cb54d17a3e3_003 | deaths present but no comparable case count is available |
| anom_007 | abrupt_spike_simple_threshold | high | rec_src_search_0cb54d17a3e3_005 | case count exceeds configured simple anomaly threshold |
| anom_008 | abrupt_spike_simple_threshold | high | rec_src_search_0d8e5c276e4c_001 | case count exceeds configured simple anomaly threshold |
| anom_009 | deaths_without_case_reference | low | rec_src_search_0d8e5c276e4c_002 | deaths present but no comparable case count is available |
| anom_010 | abrupt_spike_simple_threshold | high | rec_src_search_0d8e5c276e4c_003 | case count exceeds configured simple anomaly threshold |
| anom_011 | deaths_without_case_reference | low | rec_src_search_2ac70c766155_005 | deaths present but no comparable case count is available |
| anom_012 | deaths_without_case_reference | low | rec_src_search_2ac70c766155_006 | deaths present but no comparable case count is available |

| Applied decision | Type | Target | Audit IDs | Reason |
|---|---|---|---|---|

## 10. 输出文件

- Run output directory: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_dengue_brazil_2024_q1`
- Collection final dataset: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_dengue_brazil_2024_q1\collection\final_dataset.csv`
- Collection final case dataset: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_dengue_brazil_2024_q1\collection\final_case_dataset.csv`
- Collection zero-case statements: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_dengue_brazil_2024_q1\collection\zero_case_statements.csv`
- Collection exposure-monitoring records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_dengue_brazil_2024_q1\collection\exposure_monitoring_records.csv`
- Collection surveillance summaries: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_dengue_brazil_2024_q1\collection\surveillance_summary_records.csv`
- Collection outbreak summaries: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_dengue_brazil_2024_q1\collection\outbreak_summary_records.csv`
- Collection context records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_dengue_brazil_2024_q1\collection\context_records.csv`
- Collection unclassified observations: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_dengue_brazil_2024_q1\collection\unclassified_observation_records.csv`
- Collection observation dataset summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_dengue_brazil_2024_q1\collection\observation_type_dataset_summary.json`
- Collection pre-quality-gate records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_dengue_brazil_2024_q1\collection\final_dataset_pre_quality_gate.csv`
- Collection quarantined records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_dengue_brazil_2024_q1\collection\quarantined_records.csv`
- Collection pending review records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_dengue_brazil_2024_q1\collection\pending_review_records.csv`
- Collection non-primary observations: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_dengue_brazil_2024_q1\collection\non_primary_observations.csv`
- Collection record inclusion decisions: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_dengue_brazil_2024_q1\collection\record_inclusion_decisions.json`
- Collection final dataset post-review: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_dengue_brazil_2024_q1\collection\final_dataset_post_review.csv`
- Collection anomaly results: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_dengue_brazil_2024_q1\collection\anomaly_results.json`
- Collection human review audit trail: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_dengue_brazil_2024_q1\collection\human_review_audit_trail.json`
- Collection source registry: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_dengue_brazil_2024_q1\collection\source_registry.json`
- Validation mode: `diagnostic_only`
- Validation records source: `state`
- Validation records output: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_dengue_brazil_2024_q1\validation\ground_truth_records.csv`
- Inactive validation records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_dengue_brazil_2024_q1\validation\inactive_validation_records.csv`
- Validation compatibility summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_dengue_brazil_2024_q1\validation\validation_source_compatibility_summary.json`
- Evaluation report CSV: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_dengue_brazil_2024_q1\evaluation\evaluation_report.csv`
- Human-readable report: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_dengue_brazil_2024_q1\workflow_run_report_chinese.md`

## 11. 当前结论

This workflow run executed the configured data collection workflow through the exported graph and artifact pipeline. The user-facing run status is: COMPLETED WITH NO PRIMARY CASE DATASET RECORDS: workflow completed, but no primary case records were accepted into final_dataset.
The run completed technically, but it should not be read as a successful data collection result because no quality-gated accepted records were produced.

- Package metadata says LLM used: `True`
- Contains synthetic fixture data: `False`
- Generated at UTC: `2026-06-25T21:48:08.924044+00:00`

## 12. Workflow visualization artifacts

- Workflow visualization index: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_dengue_brazil_2024_q1\workflow_visualization\index.html`
- Workflow timeline: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_dengue_brazil_2024_q1\workflow_visualization\workflow_timeline.html`
- Evidence flow graph: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_dengue_brazil_2024_q1\workflow_visualization\evidence_flow_graph.html`
- Claim comparison cards: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_dengue_brazil_2024_q1\workflow_visualization\claim_comparison_cards.html`
- Dataset decision flow: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_dengue_brazil_2024_q1\workflow_visualization\dataset_decision_flow.html`
- Human review workflow visualization: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_dengue_brazil_2024_q1\workflow_visualization\human_review_workflow.html`
- Visualization summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_dengue_brazil_2024_q1\workflow_visualization\workflow_visualization_summary.json`
