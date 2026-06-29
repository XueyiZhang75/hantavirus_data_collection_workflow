# data collection workflow Run Report

## 1. 输入任务

Collect Cholera cases, deaths, dates, locations, source URLs, source types, and evidence quotes for Haiti from 2024-01-01 to 2024-12-31.

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
- Search-derived source candidates: `42`
- Iterative source discovery: `True`
- Iterative search iterations: `2`
- Iterative stop decision: `partially_sufficient_with_unexecuted_queries`
- Iterative stop reason: `Max iterations (2) reached. The candidate pool is substantively sufficient for the collection workflow to proceed with PAHO, UNICEF, WHO, and ReliefWeb sources covering most of 2024. Three unresolved gaps (MSPP direct bulletins, post-March 2024 PAHO joint reports, individual UNICEF 2024 monthly SitRep content) are documented as unexecuted follow-up queries for human review or a future extended search run.`
- Source credibility assessed sources: `42`
- Source credibility role counts: `{'excluded': 7, 'collection_support': 13, 'validation': 15, 'context': 2, 'collection': 5}`
- Source identity assessed sources: `42`
- Source identity type counts: `{'official_public_health_agency': 8, 'international_public_health_agency': 15, 'unknown': 17, 'social_media': 1, 'structured_database': 1}`
- Source identity warning counts: `{'search_provider_not_publisher': 42, 'publisher_from_search_metadata_unverified': 42, 'actual_publisher_unknown': 26, 'direct_target_official_fast_path_skips_source_identity': 42}`
- Source discovery method: `live_search_only`
- Disease relevance target: `Cholera`
- Disease relevance source status counts: `{'insufficient_text': 11, 'ambiguous_disease': 10, 'target_disease_match': 21}`
- Disease relevance chunk status counts: `{'target_disease_match': 541, 'ambiguous_disease': 77, 'unrelated_disease': 4, 'insufficient_text': 3, 'related_context_only': 12}`
- Disease relevance record status counts: `{'compatible': 6}`
- Rejected incompatible record count: `0`
- Final route: `finalize`

## 2.5 Run quality status

- User-facing run status: `FAILED QUALITY GATE: records were produced but none passed final quality gates.`
- Technical execution status: `completed`
- Run quality status: `failed_quality_gate`
- Final dataset mode: `task_aware_quality_gated_records`
- Accepted final dataset count: `0`
- Final case dataset count: `0`
- Zero-case statement count: `1`
- Exposure-monitoring record count: `0`
- Surveillance summary record count: `0`
- Outbreak summary record count: `0`
- Context record count: `0`
- Unclassified observation count: `0`
- Observation dataset view counts: `{'final_case_dataset': 0, 'global_outbreak_event_dataset': 0, 'regional_surveillance_dataset': 0, 'country_year_aggregate_dataset': 0, 'official_alert_dataset': 0, 'probable_case_dataset': 0, 'suspected_case_dataset': 0, 'unspecified_case_dataset': 0, 'death_dataset': 0, 'hospitalization_dataset': 0, 'zero_case_statements': 1, 'exposure_monitoring_records': 0, 'surveillance_summary_records': 0, 'outbreak_summary_records': 0, 'context_records': 0, 'non_primary_observations': 1, 'unclassified_observation_records': 0}`
- Pre-quality-gate record count: `2`
- Quarantined record count: `2`
- Pending review record count: `0`
- Non-primary observation count: `0`
- Final dataset post-review count: `0`
- Primary-case dataset status: `no_corroborated_primary_case_events`
- Recommended primary dataset message: `No primary case dataset records were accepted; inspect zero-case, exposure-monitoring, context, and other observation views.`
- Primary-case eligible accepted count: `0`
- Corroborated primary case event count: `0`
- Recommended user message: `Use quarantined_records and record_inclusion_decisions to inspect why no records were accepted.`

workflow technically completed, but no quality-gated accepted records were produced.
本次 workflow 技术上完成，但没有产生通过质量门的 accepted records。

Workflow technically completed, but no primary case dataset records were accepted. Non-primary observations were preserved separately and should not be read as final epidemiological case data.

## 3. Workflow 运行过程

Graph is executed as a mostly serial workflow. The only conditional branch is after `quality_gate_routing`: the run enters `human_review` when quality or validation checks require review, then still builds the final data package. In this run, the graph route is shown above; validation comparison review flags are reported separately in Section 8.

1. `task_intake_and_scope_planning` - Built CollectionSpec from structured task input.
2. `disease_intelligence_builder` - Built disease intelligence from LLM output (Cholera).
3. `profile_and_schema_setup` - Built active disease profile, collection schema, and source strategy (Cholera, generation_method=disease_intelligence...
4. `executable_source_planning` - Built executable source plan with 10 planned queries; no searches were executed.
5. `query_strategy_builder` - Built 10 direct_collection search queries from the LLM evidence strategy plan.
6. `source_discovery` - Discovered 42 source candidates using live_search_only.
7. `source_dedup_and_registry` - Built source registry with 42 entries (0 duplicates dropped).
8. `source_screening` - Screened 42 sources using deterministic policy.
9. `source_critic_and_uncertainty_routing` - Critic reviewed 42 sources; 41 ready for fetch, 0 deferred, 14 flagged for human review.
10. `content_fetch_and_parse` - Built 41 fetch requests, produced 41 documents (live_fetch_enabled=True, fixture_documents_enabled=False, fixtures_lo...
11. `document_quality_check` - Quality-checked 41 documents: 37 usable, 0 partial, 0 offline stub, 0 parse deferred, 4 unusable.
12. `evidence_chunking_and_data_presence_flagging` - Chunked 37/41 documents into 637 evidence chunks (528 flagged as containing target data).
13. `structured_extraction` - Built 2 raw records (extraction_mode=llm_structured_output, llm_enabled=True).
14. `schema_validation_and_repair` - Validated 2 raw records: 2 validated (0 need review), 0 rejected.
15. `record_normalization` - Normalized 2/2 records (0 need review).
16. `record_linking` - Linked 2/2 normalized records into 2 candidate events.
17. `cross_source_consistency_check` - Checked 0 multi-record events; found 0 new conflicts and 6 validation results (0 events need review).
18. `quality_gate_routing` - Human review disabled; preserving review flags as audit metadata and routing to final_data_package_builder.
19. `final_data_package_builder` - Assembled hardened FinalDataPackage from current state.

## 4. 数据源分工

| Role | Source ID | Publisher / title | Credibility | Final decision | Fetch ready |
|---|---|---|---|---|---|
| context_only | src_search_9551dc7b0b7e | / Situation Report In 2024, humanitarian partners & the Govt. of ... | needs_review (0.5) | needs_human_review | False |
| other | src_search_1f26d88854bb | / [PDF] Recrudescence mondiale du choléra - HAL | excluded (0.3554) | include_for_content_fetch | True |
| other | src_search_8f7e2ec5d5f0 | / L'origine de l'épidémie de choléra à Haïti en 2010 | excluded (0.6823) | include_for_content_fetch | True |
| other | src_search_3ddf5335d5cb | / Le choléra se propage dans les camps de déplacés d'Haïti, aggravant la crise humanitaire - The Haitian Times L'épidémie de choléra mena... | excluded (0.6479) | include_for_content_fetch | True |
| other | src_search_c853598f6ecb | Centers for Disease Control and Prevention / Surveillance du choléra en Haïti - GTFCC | high (0.6639) | include_for_content_fetch | True |
| other | src_search_664c22f9e3a2 | / Élimination du choléra en Haïti | excluded (0.6479) | include_for_content_fetch | True |
| other | src_search_ce1c475b85d0 | Pan American Health Organization / Épidémie de choléra en Haïti : les agents de santé communautaires ... | excluded (0.6599) | include_for_content_fetch | True |
| other | src_search_97b3a3ccdaaa | World Health Organization / Choléra – Haïti | medium (0.5748) | include_for_content_fetch | True |
| other | src_search_ccceaa1bbf80 | / [PDF] Choléra en Haïti et diffusion internationale | excluded (0.3554) | include_for_content_fetch | True |
| other | src_search_498deeccadeb | Pan American Health Organization / [PDF] Epidemiological update Cholera in the Region of the Americas | medium (0.7264) | include_for_content_fetch | True |
| other | src_search_a7051b05a7d5 | Pan American Health Organization / Cholera Documents - Pan American Health Organization | high (0.784) | include_for_content_fetch | True |
| other | src_search_4180ab8bf01c | Pan American Health Organization / Situation Reports Cholera Outbreak in Hispaniola. 2022 - Marzo 2024 | high (0.8943) | include_for_content_fetch | True |
| other | src_search_56a999cb40ed | Pan American Health Organization / Cholera Outbreak in Haiti: Situation Report 8 - 13 March 2024 - PAHO | high (0.8943) | include_for_content_fetch | True |
| other | src_search_720774886e64 | / Epidemiological update - Cholera in the Region of the Americas - Haiti | high (0.8503) | include_for_content_fetch | True |
| other | src_search_26644e72a6de | Pan American Health Organization / Cholera Outbreak in Haiti. Situation Report, n. 8 (13 March 2024) | high (0.8831) | include_for_content_fetch | True |
| other | src_search_3e55254055b3 | / Americas: update from the region - GTFCC | high (0.508) | include_for_content_fetch | True |
| other | src_search_52ecb7ba76dc | Pan American Health Organization / PAHO Responds to Haiti's Humanitarian Crisis Grade 3 | medium (0.6759) | include_for_content_fetch | True |
| other | src_search_cabaf4b4fb77 | / Haiti Emergency Situation Report No. 20 (As of 24 April 2024) | high (0.6711) | include_for_content_fetch | True |
| other | src_search_25902466ae28 | / UNICEF Haiti Humanitarian Situation Report No. 3: 1 to 30 April 2024 | high (0.6711) | include_for_content_fetch | True |
| other | src_search_dbb3d2d563a6 | / UNICEF Haiti Humanitarian Situation Report No. 11, End of Year 2024 | high (0.6711) | include_for_content_fetch | True |
| other | src_search_b3f2bb1a4939 | / UNICEF Haiti Humanitarian Situation Report No. 9: October 2024 | high (0.6711) | include_for_content_fetch | True |
| other | src_search_42c6ab0993b9 | / UNICEF Haiti Humanitarian Situation Report No. 7, 1 July-30 ... | high (0.6527) | include_for_content_fetch | True |
| other | src_search_52b7f0d4d92b | / UNICEF Haiti Humanitarian Situation Report No. 6: Mid-Year 2025 | high (0.6527) | include_for_content_fetch | True |
| other | src_search_32b79ff90e27 | World Health Organization / Data show marked increase in annual cholera deaths | high (0.836) | include_for_content_fetch | True |
| other | src_search_f4c1149a4012 | World Health Organization / Cholera burden in 2024 | medium (0.7232) | include_for_content_fetch | True |
| other | src_search_b2035616c3c6 | World Health Organization / Cholera - World Health Organization (WHO) | high (0.7968) | include_for_content_fetch | True |
| other | src_search_235751d2a1c0 | European Centre for Disease Prevention and Control / Cholera worldwide overview - ECDC - European Union | high (0.7968) | include_for_content_fetch | True |
| other | src_search_a2865ce57583 | / Cholera cases soar globally; Malawi, Haiti deadliest outbreaks ... | high (0.7826) | include_for_content_fetch | True |
| other | src_search_2c17a661f0e1 | / Cholera / GHDx | medium (0.724) | include_for_content_fetch | True |
| other | src_search_928dc973b35f | World Health Organization / Cholera reported deaths / Our World in Data | medium (0.7448) | include_for_content_fetch | True |
| other | src_search_9aefe8d01e47 | / Cholera outbreak in Haiti persists, particularly in sites ... - BEACON | high (0.8527) | include_for_content_fetch | True |
| other | src_search_efcb55db66a9 | Pan American Health Organization / Cholera outbreak in Haiti 2022 - Situation Report 1 - PAHO/WHO / Pan American Health Organization | high (0.8759) | include_for_content_fetch | True |
| other | src_search_ff6f6ca8effc | World Health Organization / Cholera- Haiti - World Health Organization (WHO) | high (0.8551) | include_for_content_fetch | True |
| other | src_search_6dc5eabed325 | / Water Insecurity, Sociopolitical Instability, and Resurgence of Cholera in Haiti, 2022: An Outbreak Investigation in: The American Jour... | high (0.8527) | include_for_content_fetch | True |
| other | src_search_464c57626567 | National Center for Biotechnology Information / Cholera in Haiti: A public health challenge in the Dominican Republic and Americas Region... | high (0.8551) | include_for_content_fetch | True |
| other | src_search_ddb620fb680b | / Haiti situation reports | high (0.6367) | include_for_content_fetch | True |
| other | src_search_76ddaf069a83 | / [PDF] Haiti - UNICEF | high (0.5791) | include_for_content_fetch | True |
| other | src_search_ae54b55bc3ab | World Health Organization / Global situation report for cholera, 2024 | high (0.8232) | include_for_content_fetch | True |
| other | src_search_fd011c887606 | / Amidst insecurity in Haiti, new cholera upsurge puts 1.2 million ... | high (0.8527) | include_for_content_fetch | True |
| other | src_search_c991ad095191 | Pan American Health Organization / Lutte contre le choléra en Haïti : communautés, autorités sanitaires et partenaires unissent leurs eff... | excluded (0.6599) | include_for_content_fetch | True |
| other | src_search_5394db32c32d | / [PDF] CHOLÉRA EN HAÏTI FICHE-INFO ECHO | medium (0.5719) | include_for_content_fetch | True |
| other | src_search_802ab0048156 | / Haiti: Cholera - Reports - ReliefWeb Response | high (0.8431) | include_for_content_fetch | True |

## 5. 真实网页抓取结果

- Documents fetched/parsed: `41`
- Search-derived sources selected for fetch: `41`
- Search-derived skipped by reason: `{}`
- Fetch status counts: `fetch_failed=2, fetched=39`
- External fetch enabled: `True`
- Fetch provider counts: `native_requests=3, tavily_extract=38`
- External fetch failure counts: `native_requests=2, tavily_extract=3`
- Selected fetch bucket counts: `target_official_authority=41`
- Parser status counts: `parsed_html=2, parsed_pdf=1, parsed_text=38`
- Parser used counts: `html_stdlib_parser=2, pdf_pymupdf_fallback_parser=1, text_parser=38`
- Quality status counts: `unusable=4, usable=37`
- Validation-reserved skipped from fetch: `[]`

| Source ID | Provider | Fetch status | HTTP | Parse | Parser | Quality | Text chars | Tables |
|---|---|---|---|---|---|---|---|---|
| src_search_8f7e2ec5d5f0 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 35524 | 0 |
| src_search_c853598f6ecb | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 5979 | 0 |
| src_search_ce1c475b85d0 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 8682 | 0 |
| src_search_3ddf5335d5cb | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 10086 | 0 |
| src_search_664c22f9e3a2 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 7879 | 0 |
| src_search_97b3a3ccdaaa | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 17826 | 0 |
| src_search_1f26d88854bb | native_requests | fetched | 200 | parsed_pdf | pdf_pymupdf_fallback_parser | usable | 32895 | 0 |
| src_search_ccceaa1bbf80 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 10818 | 0 |
| src_search_4180ab8bf01c | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 10865 | 0 |
| src_search_56a999cb40ed | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 5377 | 0 |
| src_search_26644e72a6de | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 24622 | 0 |
| src_search_efcb55db66a9 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 6325 | 0 |
| src_search_ff6f6ca8effc | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 22912 | 0 |
| src_search_464c57626567 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 13327 | 0 |
| src_search_9aefe8d01e47 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 8627 | 0 |
| src_search_6dc5eabed325 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 192274 | 0 |
| src_search_720774886e64 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 9429 | 0 |
| src_search_802ab0048156 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 5289 | 0 |
| src_search_a7051b05a7d5 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 13831 | 0 |
| src_search_498deeccadeb | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 20782 | 0 |
| src_search_52ecb7ba76dc | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 18129 | 0 |
| src_search_c991ad095191 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 11885 | 0 |
| src_search_5394db32c32d | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 7519 | 0 |
| src_search_3e55254055b3 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 5322 | 0 |
| src_search_fd011c887606 | native_requests | fetch_failed | 403 | parsed_html | html_stdlib_parser | unusable | 16 | 0 |
| src_search_32b79ff90e27 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 13526 | 0 |
| src_search_ae54b55bc3ab | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 11025 | 0 |
| src_search_b2035616c3c6 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 61503 | 0 |
| src_search_235751d2a1c0 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 29257 | 0 |
| src_search_a2865ce57583 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 10130 | 0 |
| src_search_928dc973b35f | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 11469 | 0 |
| src_search_2c17a661f0e1 | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 17189 | 0 |
| src_search_f4c1149a4012 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 3363 | 0 |
| src_search_cabaf4b4fb77 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 4598 | 0 |
| src_search_25902466ae28 | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 8777 | 0 |
| src_search_dbb3d2d563a6 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 8623 | 0 |
| src_search_b3f2bb1a4939 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 7066 | 0 |
| src_search_42c6ab0993b9 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 4684 | 0 |
| src_search_52b7f0d4d92b | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 7207 | 0 |
| src_search_ddb620fb680b | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 20104 | 0 |
| src_search_76ddaf069a83 | native_requests | fetch_failed | 403 | parsed_html | html_stdlib_parser | unusable | 16 | 0 |

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
- Total queries executed: `7`
- Stop decision: `partially_sufficient_with_unexecuted_queries`
- Stop reason: `Max iterations (2) reached. The candidate pool is substantively sufficient for the collection workflow to proceed with PAHO, UNICEF, WHO, and ReliefWeb sources covering most of 2024. Three unresolved gaps (MSPP direct bulletins, post-March 2024 PAHO joint reports, individual UNICEF 2024 monthly SitRep content) are documented as unexecuted follow-up queries for human review or a future extended search run.`
- Query source counts: `{'iterative_llm_initial_search_plan': 4, 'iterative_llm_refinement': 4}`
- Iteration query counts: `{'1': 4, '2': 4}`

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
- Final role counts: `collection=5, collection_support=13, context=2, excluded=7, validation=15`
- Risk flag counts: `ambiguous_disease=21, ambiguous_disease_signal=1, ambiguous_disease_signal_in_source_metadata=10, ambiguous_location=2, complete_source_provenance=16, context_or_background_only=2, data_signal_in_source_metadata=42, disease_relevance_unclear=11, disease_relevance_very_low:score_0.20_no_cholera_terms_found=1, do_not_use_as_primary_data_source=1, ephemeral_and_unstructured_content=1, false_positive_discovery:haiti_query_returned_ethiopia_account=1, geographic_granularity_unclear=2, geographic_mismatch:account_is_OCHA_Ethiopia_not_OCHA_Haiti=1, independence_unclear=4, international_organization_authority=15, local_or_subnational_granularity=27, local_source_matches_task_location=28, location_match_from_planned_query=11, location_relevance_unclear=2, low_machine_readability=6, machine_readable_or_structured=7, missing_publisher=26, national_or_international_context=1, national_or_international_granularity=12, official_public_health_authority=23, pdf_or_report_likely_medium_readability=6, platform_risk:social_media_post_not_a_formal_report=1, primary_or_authoritative_source=38, screening_and_critic_disagree=1, secondary_news_or_media_source=2, source_disease_relevance:ambiguous_disease=10, source_disease_relevance:insufficient_text=11, source_disease_relevance:target_disease_match=21, source_metadata_matches_requested_disease=21, source_time_matches_requested_window=17, source_type_label_inflation:labeled_international_organization_report_but_is_x.com_post=1, standard_web_page=29, structured_data_source=4, task_location_granularity=1, time_window_match_from_planned_query=25, underlying_report_not_directly_accessible_from_this_url=1`
- LLM assessed count: `1`
- LLM failure count: `0`
- Needs review count: `10`

### 6.3.5 Source Identity / Publisher Assessment

- Identity assessed source count: `42`
- LLM identity assessed source count: `0`
- Post-fetch identity assessed source count: `41`
- Unknown publisher count: `23`
- Source type counts: `international_public_health_agency=15, official_public_health_agency=8, social_media=1, structured_database=1, unknown=17`
- Claim support role counts: `context_only=10, insufficient_information=18, primary_case_claim_support=14`
- Fetch use counts: `fetch_for_context=10, fetch_for_extraction=14, fetch_only_after_review=18`
- Warning counts: `actual_publisher_unknown=26, direct_target_official_fast_path_skips_source_identity=42, publisher_from_search_metadata_unverified=42, search_provider_not_publisher=42`

### 6.4 LLM Structured Extraction

- Extraction mode: `llm_structured_output`
- Eligible chunk count: `637`
- LLM call count: `30`
- LLM success count: `30`
- LLM error count: `0`
- Raw record count: `2`

## 7. 最终抽取 records

- Normalized record count: `2`
- Run quality status: `failed_quality_gate`
- Final dataset mode: `task_aware_quality_gated_records`
- Quality-gated accepted final dataset count: `0`
- Final case dataset count: `0`
- Zero-case statement count: `1`
- Exposure-monitoring record count: `0`
- Surveillance summary record count: `0`
- Outbreak summary record count: `0`
- Context record count: `0`
- Unclassified observation count: `0`
- Observation dataset view counts: `{'final_case_dataset': 0, 'global_outbreak_event_dataset': 0, 'regional_surveillance_dataset': 0, 'country_year_aggregate_dataset': 0, 'official_alert_dataset': 0, 'probable_case_dataset': 0, 'suspected_case_dataset': 0, 'unspecified_case_dataset': 0, 'death_dataset': 0, 'hospitalization_dataset': 0, 'zero_case_statements': 1, 'exposure_monitoring_records': 0, 'surveillance_summary_records': 0, 'outbreak_summary_records': 0, 'context_records': 0, 'non_primary_observations': 1, 'unclassified_observation_records': 0}`
- Pre-quality-gate record count: `2`
- Quarantined record count: `2`
- Pending review record count: `0`
- Non-primary observation count: `0`
- Final dataset post-review count: `0`
- Primary-case dataset status: `no_corroborated_primary_case_events`
- Recommended primary dataset message: `No primary case dataset records were accepted; inspect zero-case, exposure-monitoring, context, and other observation views.`
- Primary-case eligible accepted count: `0`
- Corroborated primary case event count: `0`
- Record inclusion status counts: `{'quarantined_schema_invalid': 2}`
- Run quality warnings: `['no_corroborated_primary_case_events']`
- Accepted source counts: `none`

No quality-gated records are available to list.
Candidate records, if any, are recorded in the pre-quality, quarantined, and pending-review artifacts.

| Record ID | Date / period | Location | Cases | Deaths | Source | LLM used |
|---|---|---|---|---|---|---|

## 8. Validation 对比

### Claim-level corroboration

- Claim count: `5`
- Claim comparison count: `10`
- Corroborated event count: `1`
- Corroborated primary case event count: `0`
- Observation type counts: `confirmed_case_record=2, death_record=1, suspected_case_record=2`
- Corroboration status counts: `single_source_unverified=1`

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

- Human review item count: `29`
- Evaluation review flag count: `0`
- Anomaly review item count: `0`

| Review ID | Type | Related IDs | Reason |
|---|---|---|---|
| review_source_credibility_src_search_c853598f6ecb | source_credibility | src_search_c853598f6ecb | missing_publisher |
| review_source_src_search_c853598f6ecb | source_screening | src_search_c853598f6ecb | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_cabaf4b4fb77 | source_credibility | src_search_cabaf4b4fb77 | missing_publisher |
| review_source_src_search_cabaf4b4fb77 | source_screening | src_search_cabaf4b4fb77 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_25902466ae28 | source_credibility | src_search_25902466ae28 | missing_publisher |
| review_source_src_search_25902466ae28 | source_screening | src_search_25902466ae28 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_dbb3d2d563a6 | source_credibility | src_search_dbb3d2d563a6 | missing_publisher |
| review_source_src_search_dbb3d2d563a6 | source_screening | src_search_dbb3d2d563a6 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_b3f2bb1a4939 | source_credibility | src_search_b3f2bb1a4939 | missing_publisher |
| review_source_src_search_b3f2bb1a4939 | source_screening | src_search_b3f2bb1a4939 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_42c6ab0993b9 | source_credibility | src_search_42c6ab0993b9 | missing_publisher |
| review_source_src_search_42c6ab0993b9 | source_screening | src_search_42c6ab0993b9 | Source classified as data_source; both screening and critic agree to include for content fetch. |

## 9.5 Stage 11 anomaly detection and review application

- Anomaly result count: `0`
- Anomaly severity counts: `none`
- Anomaly needs-human-review count: `0`
- Decisions provided: `0`
- Decisions applied: `0`
- Decisions rejected: `0`
- Audit entries: `0`
- Final dataset post-review count: `0`
- Records excluded by review: `0`

| Anomaly ID | Type | Severity | Target | Reason |
|---|---|---|---|---|

| Applied decision | Type | Target | Audit IDs | Reason |
|---|---|---|---|---|

## 10. 输出文件

- Run output directory: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_cholera_haiti_2024_full_year`
- Collection final dataset: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_cholera_haiti_2024_full_year\collection\final_dataset.csv`
- Collection final case dataset: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_cholera_haiti_2024_full_year\collection\final_case_dataset.csv`
- Collection zero-case statements: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_cholera_haiti_2024_full_year\collection\zero_case_statements.csv`
- Collection exposure-monitoring records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_cholera_haiti_2024_full_year\collection\exposure_monitoring_records.csv`
- Collection surveillance summaries: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_cholera_haiti_2024_full_year\collection\surveillance_summary_records.csv`
- Collection outbreak summaries: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_cholera_haiti_2024_full_year\collection\outbreak_summary_records.csv`
- Collection context records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_cholera_haiti_2024_full_year\collection\context_records.csv`
- Collection unclassified observations: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_cholera_haiti_2024_full_year\collection\unclassified_observation_records.csv`
- Collection observation dataset summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_cholera_haiti_2024_full_year\collection\observation_type_dataset_summary.json`
- Collection pre-quality-gate records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_cholera_haiti_2024_full_year\collection\final_dataset_pre_quality_gate.csv`
- Collection quarantined records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_cholera_haiti_2024_full_year\collection\quarantined_records.csv`
- Collection pending review records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_cholera_haiti_2024_full_year\collection\pending_review_records.csv`
- Collection non-primary observations: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_cholera_haiti_2024_full_year\collection\non_primary_observations.csv`
- Collection record inclusion decisions: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_cholera_haiti_2024_full_year\collection\record_inclusion_decisions.json`
- Collection final dataset post-review: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_cholera_haiti_2024_full_year\collection\final_dataset_post_review.csv`
- Collection anomaly results: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_cholera_haiti_2024_full_year\collection\anomaly_results.json`
- Collection human review audit trail: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_cholera_haiti_2024_full_year\collection\human_review_audit_trail.json`
- Collection source registry: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_cholera_haiti_2024_full_year\collection\source_registry.json`
- Validation mode: `diagnostic_only`
- Validation records source: `state`
- Validation records output: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_cholera_haiti_2024_full_year\validation\ground_truth_records.csv`
- Inactive validation records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_cholera_haiti_2024_full_year\validation\inactive_validation_records.csv`
- Validation compatibility summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_cholera_haiti_2024_full_year\validation\validation_source_compatibility_summary.json`
- Evaluation report CSV: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_cholera_haiti_2024_full_year\evaluation\evaluation_report.csv`
- Human-readable report: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_cholera_haiti_2024_full_year\workflow_run_report_chinese.md`

## 11. 当前结论

This workflow run executed the configured data collection workflow through the exported graph and artifact pipeline. The user-facing run status is: FAILED QUALITY GATE: records were produced but none passed final quality gates.
The run completed technically, but it should not be read as a successful data collection result because no quality-gated accepted records were produced.

- Package metadata says LLM used: `True`
- Contains synthetic fixture data: `False`
- Generated at UTC: `2026-06-25T19:57:26.039727+00:00`

## 12. Workflow visualization artifacts

- Workflow visualization index: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_cholera_haiti_2024_full_year\workflow_visualization\index.html`
- Workflow timeline: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_cholera_haiti_2024_full_year\workflow_visualization\workflow_timeline.html`
- Evidence flow graph: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_cholera_haiti_2024_full_year\workflow_visualization\evidence_flow_graph.html`
- Claim comparison cards: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_cholera_haiti_2024_full_year\workflow_visualization\claim_comparison_cards.html`
- Dataset decision flow: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_cholera_haiti_2024_full_year\workflow_visualization\dataset_decision_flow.html`
- Human review workflow visualization: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_cholera_haiti_2024_full_year\workflow_visualization\human_review_workflow.html`
- Visualization summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round05_cholera_haiti_2024_full_year\workflow_visualization\workflow_visualization_summary.json`
