# data collection workflow Run Report

## 1. 输入任务

Collect Cholera cases, deaths, dates, locations, source URLs, source types, and evidence quotes for Haiti from 2024-10-01 to 2024-12-31.

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
- Search-derived source candidates: `40`
- Iterative source discovery: `True`
- Iterative search iterations: `2`
- Iterative stop decision: `stop_limits_reached`
- Iterative stop reason: `Hard limit reached: max_iterations=2 and max_total_queries=10 both exhausted. All 8 planned queries across iterations 1 and 2 have been executed. Continuing search is not permitted within the defined bounds.`
- Source credibility assessed sources: `40`
- Source credibility role counts: `{'collection': 10, 'excluded': 11, 'collection_support': 6, 'context': 6, 'validation': 7}`
- Source identity assessed sources: `40`
- Source identity type counts: `{'international_public_health_agency': 15, 'social_media': 4, 'unknown': 7, 'official_public_health_agency': 10, 'national_public_health_agency': 2, 'structured_database': 1, 'news_media': 1}`
- Source identity warning counts: `{'search_provider_not_publisher': 40, 'publisher_from_search_metadata_unverified': 40, 'direct_target_official_fast_path_skips_source_identity': 40, 'actual_publisher_unknown': 22}`
- Source discovery method: `live_search_only`
- Disease relevance target: `Cholera`
- Disease relevance source status counts: `{'target_disease_match': 25, 'insufficient_text': 11, 'ambiguous_disease': 4}`
- Disease relevance chunk status counts: `{'target_disease_match': 564, 'ambiguous_disease': 139, 'related_context_only': 9, 'unrelated_disease': 11, 'insufficient_text': 1}`
- Disease relevance record status counts: `{'compatible': 18}`
- Rejected incompatible record count: `0`
- Final route: `finalize`

## 2.5 Run quality status

- User-facing run status: `STATUS: human_review_required`
- Technical execution status: `completed`
- Run quality status: `human_review_required`
- Final dataset mode: `task_aware_quality_gated_records`
- Accepted final dataset count: `0`
- Final case dataset count: `0`
- Zero-case statement count: `1`
- Exposure-monitoring record count: `0`
- Surveillance summary record count: `0`
- Outbreak summary record count: `0`
- Context record count: `2`
- Unclassified observation count: `0`
- Observation dataset view counts: `{'final_case_dataset': 0, 'global_outbreak_event_dataset': 0, 'regional_surveillance_dataset': 0, 'country_year_aggregate_dataset': 0, 'official_alert_dataset': 0, 'probable_case_dataset': 0, 'suspected_case_dataset': 0, 'unspecified_case_dataset': 0, 'death_dataset': 0, 'hospitalization_dataset': 0, 'zero_case_statements': 1, 'exposure_monitoring_records': 0, 'surveillance_summary_records': 0, 'outbreak_summary_records': 0, 'context_records': 2, 'non_primary_observations': 3, 'unclassified_observation_records': 0}`
- Pre-quality-gate record count: `6`
- Quarantined record count: `4`
- Pending review record count: `2`
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
6. `source_discovery` - Discovered 40 source candidates using live_search_only.
7. `source_dedup_and_registry` - Built source registry with 40 entries (0 duplicates dropped).
8. `source_screening` - Screened 40 sources using deterministic policy.
9. `source_critic_and_uncertainty_routing` - Critic reviewed 40 sources; 37 ready for fetch, 0 deferred, 12 flagged for human review.
10. `content_fetch_and_parse` - Built 37 fetch requests, produced 37 documents (live_fetch_enabled=True, fixture_documents_enabled=False, fixtures_lo...
11. `document_quality_check` - Quality-checked 37 documents: 33 usable, 1 partial, 0 offline stub, 0 parse deferred, 3 unusable.
12. `evidence_chunking_and_data_presence_flagging` - Chunked 34/37 documents into 724 evidence chunks (689 flagged as containing target data).
13. `structured_extraction` - Built 6 raw records (extraction_mode=llm_structured_output, llm_enabled=True).
14. `schema_validation_and_repair` - Validated 6 raw records: 6 validated (0 need review), 0 rejected.
15. `record_normalization` - Normalized 6/6 records (0 need review).
16. `record_linking` - Linked 6/6 normalized records into 3 candidate events.
17. `cross_source_consistency_check` - Checked 1 multi-record events; found 0 new conflicts and 15 validation results (0 events need review).
18. `quality_gate_routing` - Human review disabled; preserving review flags as audit metadata and routing to final_data_package_builder.
19. `final_data_package_builder` - Assembled hardened FinalDataPackage from current state.

## 4. 数据源分工

| Role | Source ID | Publisher / title | Credibility | Final decision | Fetch ready |
|---|---|---|---|---|---|
| context_only | src_search_505b2ac21551 | / An Update of Cholera Cases as of 30th December 2024 ... - Facebook | medium (0.7) | needs_human_review | False |
| context_only | src_search_f93d701ca110 | / Les décès dus au choléra ont augmenté de 50 % en 2024 - YouTube | medium (0.5658) | include_for_content_fetch | False |
| context_only | src_search_bd6f7e5cf18e | / 2 February 2024 cholera update - Facebook | medium (0.7) | needs_human_review | False |
| context_only | src_search_e07e6217756f | / Découverte des premiers casde choléra en Haïti - Facebook | high (0.3314) | include_for_content_fetch | False |
| context_only | src_search_103c81f1c004 | / [PDF] CHOLERA SURVEILLANCE IN HAITI OCTOBER 2022- MAY 2024 | needs_review (0.4858) | needs_human_review | False |
| context_only | src_search_d48598a09a0c | Centers for Disease Control and Prevention / Cholera Outbreak — Haiti, September 2022–January 2023 / MMWR | medium (0.7242) | include_for_content_fetch | True |
| other | src_search_803858403368 | World Health Organization / [PDF] Multi-country outbreak of cholera - World Health Organization (WHO) | medium (0.7288) | include_for_content_fetch | True |
| other | src_search_ae84970cb766 | Pan American Health Organization / [PDF] Haiti - Pan American Health Organization | excluded (0.5906) | include_for_content_fetch | True |
| other | src_search_26644e72a6de | Pan American Health Organization / Cholera Outbreak in Haiti. Situation Report, n. 8 (13 March 2024) | high (0.8714) | include_for_content_fetch | True |
| other | src_search_498deeccadeb | Pan American Health Organization / [PDF] Epidemiological update Cholera in the Region of the Americas | medium (0.7264) | include_for_content_fetch | True |
| other | src_search_32b79ff90e27 | World Health Organization / Data show marked increase in annual cholera deaths | high (0.8232) | include_for_content_fetch | True |
| other | src_search_9aefe8d01e47 | / BEACON | excluded (0.5656) | include_for_content_fetch | True |
| other | src_search_694fdd383b8c | Pan American Health Organization / [PDF] SITREP HUMANITAIRE - HAITI - PAHO | medium (0.7791) | include_for_content_fetch | True |
| other | src_search_eab87c3f08bd | / Situation épidémiologique des cas suspects de choléra et de fièvres dans le Département du Centre - Haiti / ReliefWeb | excluded (0.6479) | include_for_content_fetch | True |
| other | src_search_3ddf5335d5cb | / Le choléra se propage dans les camps de déplacés d'Haïti ... | excluded (0.6479) | include_for_content_fetch | True |
| other | src_search_d7b21c68da3e | / Lutter contre le choléra - Les Nations Unies en Haïti | excluded (0.6479) | include_for_content_fetch | True |
| other | src_search_c853598f6ecb | Centers for Disease Control and Prevention / Surveillance du choléra en Haïti – GTFCC | high (0.6639) | include_for_content_fetch | True |
| other | src_search_664c22f9e3a2 | / Élimination du choléra en Haïti / The Global Alliance Against Cholera (G.A.A.C) | high (0.8431) | include_for_content_fetch | True |
| other | src_search_97b3a3ccdaaa | World Health Organization / Choléra – Haïti | medium (0.5748) | include_for_content_fetch | True |
| other | src_search_8fb70e3827e3 | World Health Organization / [PDF] Multi-country outbreak of cholera - World Health Organization (WHO) | medium (0.7288) | include_for_content_fetch | True |
| other | src_search_5b9b31558c67 | / Haiti Country Report - Cholera Taxonomy | high (0.8319) | include_for_content_fetch | True |
| other | src_search_8929f93c6a7e | / Multi-Country Outbreak of Cholera, External Situation Report #21 ... | high (0.8) | include_for_content_fetch | True |
| other | src_search_a0ed0f2ccd87 | / Cholera, Haiti - BEACON | high (0.8319) | include_for_content_fetch | True |
| other | src_search_b2035616c3c6 | World Health Organization / Cholera - World Health Organization (WHO) | high (0.784) | include_for_content_fetch | True |
| other | src_search_bbe750c5b8de | Centers for Disease Control and Prevention / Enhanced Risk for Epidemic Cholera Transmission, Haiti - Volume 31, Number 12—December 2025... | high (0.877) | include_for_content_fetch | True |
| other | src_search_ae54b55bc3ab | World Health Organization / Global situation report for cholera, 2024 | high (0.836) | include_for_content_fetch | True |
| other | src_search_235751d2a1c0 | European Centre for Disease Prevention and Control / Cholera worldwide overview - ECDC - European Union | high (0.7968) | include_for_content_fetch | True |
| other | src_search_a2865ce57583 | / Cholera cases soar globally; Malawi, Haiti deadliest outbreaks ... | high (0.7826) | include_for_content_fetch | True |
| other | src_search_17fe4af3bf55 | / Cholera trends – GTFCC | medium (0.724) | include_for_content_fetch | True |
| other | src_search_2a6bca803335 | National Center for Biotechnology Information / Enhanced Risk for Epidemic Cholera Transmission, Haiti - PMC - NIH | high (0.8562) | include_for_content_fetch | True |
| other | src_search_2c17a661f0e1 | / Cholera / GHDx | medium (0.724) | include_for_content_fetch | True |
| other | src_search_8937e214a08b | Pan American Health Organization / [PDF] 4 Octobre 2024 - PAHO | excluded (0.6066) | include_for_content_fetch | True |
| other | src_search_52ecb7ba76dc | Pan American Health Organization / PAHO Responds to Haiti's Humanitarian Crisis Grade 3 | excluded (0.6642) | include_for_content_fetch | True |
| other | src_search_ff6f6ca8effc | World Health Organization / Cholera- Haiti - World Health Organization (WHO) | high (0.8434) | include_for_content_fetch | True |
| other | src_search_d0b5c5f27ce6 | Pan American Health Organization / [PDF] SITREP HUMANITAIRE - HAITI - PAHO | medium (0.7791) | include_for_content_fetch | True |
| other | src_search_1f26d88854bb | / [PDF] Recrudescence mondiale du choléra - HAL | excluded (0.3554) | include_for_content_fetch | True |
| other | src_search_9c2256752686 | / Recrudescence mondiale du choléra - ipubli.inserm.fr | excluded (0.4314) | include_for_content_fetch | True |
| other | src_search_4f1e08e3f365 | / Haïti : La résurgence du choléra menace les communautés ... | high (0.6479) | include_for_content_fetch | True |
| other | src_search_ccceaa1bbf80 | / [PDF] Choléra en Haïti et diffusion internationale | excluded (0.3554) | include_for_content_fetch | True |
| other | src_search_e96fb03de8d4 | / Haïti : Situation épidémiologique du choléra 11 octobre 2022 ... | excluded (0.6639) | include_for_content_fetch | True |

## 5. 真实网页抓取结果

- Documents fetched/parsed: `37`
- Search-derived sources selected for fetch: `37`
- Search-derived skipped by reason: `{}`
- Fetch status counts: `fetched=37`
- External fetch enabled: `True`
- Fetch provider counts: `native_requests=2, tavily_extract=35`
- External fetch failure counts: `tavily_extract=2`
- Selected fetch bucket counts: `target_official_authority=37`
- Parser status counts: `parsed_html=1, parsed_pdf=1, parsed_text=35`
- Parser used counts: `html_stdlib_parser=1, pdf_pymupdf_fallback_parser=1, text_parser=35`
- Quality status counts: `partial=1, unusable=3, usable=33`
- Validation-reserved skipped from fetch: `[]`

| Source ID | Provider | Fetch status | HTTP | Parse | Parser | Quality | Text chars | Tables |
|---|---|---|---|---|---|---|---|---|
| src_search_26644e72a6de | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 24622 | 0 |
| src_search_ff6f6ca8effc | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 22912 | 0 |
| src_search_32b79ff90e27 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 13526 | 0 |
| src_search_803858403368 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 28881 | 0 |
| src_search_498deeccadeb | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 20782 | 0 |
| src_search_52ecb7ba76dc | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 18129 | 0 |
| src_search_8937e214a08b | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 103846 | 0 |
| src_search_ae84970cb766 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 88355 | 0 |
| src_search_9aefe8d01e47 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 8627 | 0 |
| src_search_664c22f9e3a2 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 7879 | 0 |
| src_search_694fdd383b8c | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 8735 | 0 |
| src_search_d0b5c5f27ce6 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 9870 | 0 |
| src_search_c853598f6ecb | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 5979 | 0 |
| src_search_e96fb03de8d4 | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 1779 | 0 |
| src_search_eab87c3f08bd | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 4393 | 0 |
| src_search_3ddf5335d5cb | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 10086 | 0 |
| src_search_4f1e08e3f365 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 19435 | 0 |
| src_search_d7b21c68da3e | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 18033 | 0 |
| src_search_97b3a3ccdaaa | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 17826 | 0 |
| src_search_f93d701ca110 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 17540 | 0 |
| src_search_9c2256752686 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 32001 | 0 |
| src_search_1f26d88854bb | native_requests | fetched | 200 | parsed_pdf | pdf_pymupdf_fallback_parser | usable | 32895 | 0 |
| src_search_ccceaa1bbf80 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 10818 | 0 |
| src_search_e07e6217756f | native_requests | fetched | 200 | parsed_html | html_stdlib_parser | partial | 253 | 0 |
| src_search_5b9b31558c67 | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 46794 | 0 |
| src_search_a0ed0f2ccd87 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 2124 | 0 |
| src_search_8929f93c6a7e | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 3173 | 0 |
| src_search_b2035616c3c6 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 61503 | 0 |
| src_search_8fb70e3827e3 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 28881 | 0 |
| src_search_bbe750c5b8de | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 14584 | 0 |
| src_search_2a6bca803335 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 16807 | 0 |
| src_search_ae54b55bc3ab | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 11025 | 0 |
| src_search_235751d2a1c0 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 29257 | 0 |
| src_search_a2865ce57583 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 10130 | 0 |
| src_search_d48598a09a0c | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 17553 | 0 |
| src_search_17fe4af3bf55 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 3341 | 0 |
| src_search_2c17a661f0e1 | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 17189 | 0 |

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
- Stop decision: `stop_limits_reached`
- Stop reason: `Hard limit reached: max_iterations=2 and max_total_queries=10 both exhausted. All 8 planned queries across iterations 1 and 2 have been executed. Continuing search is not permitted within the defined bounds.`
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
- Final role counts: `collection=10, collection_support=6, context=6, excluded=11, validation=7`
- Risk flag counts: `ADVISORY: deterministic human_review_recommended=false is likely incorrect given compound critical mismatches; override recommended=1, CRITICAL: domain_is_social_media — canonical URL resolves to facebook.com; social media posts are not reliable, versioned, or archivally stable publication venues for epidemiological data=1, CRITICAL: geographic_mismatch — source is Zambia MoH (mohzambia), task geography is Haiti; no data from this source is attributable to Haiti=1, CRITICAL: time_window_mismatch — source dated 2 February 2024, collection window is 2024-10-01 to 2024-12-31; source is ~8 months outside target window=1, HIGH: authority_score_misleading — authority_score of 0.88 reflects poster identity (MoH Zambia) but is irrelevant and potentially inflating overall credibility score for a Haiti-focused task=1, HIGH: query_result_anomaly — live search query targeted Haiti + reliefweb.int/unocha.org but returned a Facebook/Zambia result; suggests search result contamination or query failure requiring pipeline review=1, HIGH: source_type_misclassification — deterministic scorer labeled this 'international_organization_report'; MoH Zambia is a national authority, not an international organization, and a Facebook post is not a formal report=1, MEDIUM: missing_publisher — publisher field is null, reducing provenance traceability=1, MEDIUM: screening_and_critic_disagree — internal pipeline flag already present; advisory assessment amplifies this disagreement=1, ambiguous_disease=15, ambiguous_disease_signal_in_source_metadata=4, ambiguous_location=5, authority_score_likely_inflated:social_media_platform_context=1, complete_source_provenance=18, context_or_background_only=3, data_signal_in_source_metadata=40, disease_relevance_unclear=11, geographic_granularity_unclear=5, geographic_mismatch:malawi_moh_not_haiti=1, gtfcc_is_who_affiliated_authority_not_media_source=1, independence_unclear=4, independence_unclear_presenter_affiliation_not_confirmed_in_metadata=1, informal_data_channel:facebook_post_lacks_structured_surveillance_fields=1, international_organization_authority=7, local_or_subnational_granularity=11, local_source_matches_task_location=21, location_match_from_planned_query=13, location_relevance_unclear=5, low_authority_relevant_source=1, low_machine_readability=10, low_machine_readability_extraction_effort_required=1, machine_readable_or_structured=7, missing_publisher=22, missing_publisher:formal_attribution_unavailable=1, missing_publisher_field_despite_clear_institutional_host=1, named_presenter_not_institutional_author_provenance_partially_indirect=1, national_or_international_context=1, national_or_international_granularity=14, no_snippet_available:content_unverifiable_from_metadata=1, no_snippet_available_content_inference_from_title_only=1, official_public_health_authority=29, pdf_or_report_likely_medium_readability=10, pdf_slide_deck_format_limits_structured_data_extraction=1, platform_risk:social_media_not_formal_surveillance_report=1, primary_or_authoritative_source=36, publisher_identity_mismatch:malawimoh_irrelevant_to_haiti_collection_task=1, query_domain_mismatch:result_not_from_who.int_or_paho.org_as_queried=1, screening_and_critic_disagree=6, screening_and_critic_disagree:unresolved=1, screening_and_critic_disagree_warrants_llm_review=1, secondary_news_or_media_source=3, source_disease_relevance:ambiguous_disease=4, source_disease_relevance:insufficient_text=11, source_disease_relevance:target_disease_match=25, source_metadata_matches_requested_disease=25, source_time_matches_requested_window=12, source_type_likely_miscategorized_as_news_should_be_international_organization_report=1, source_type_metadata_mismatch:facebook_post_tagged_as_international_organization_report=1, standard_web_page=23, structured_data_source=3, task_location_granularity=10, time_window_match_from_planned_query=28, time_window_mismatch_document_ends_may_2024_target_window_is_q4_2024=1`
- LLM assessed count: `3`
- LLM failure count: `0`
- Needs review count: `3`

### 6.3.5 Source Identity / Publisher Assessment

- Identity assessed source count: `40`
- LLM identity assessed source count: `0`
- Post-fetch identity assessed source count: `37`
- Unknown publisher count: `21`
- Source type counts: `international_public_health_agency=15, national_public_health_agency=2, news_media=1, official_public_health_agency=10, social_media=4, structured_database=1, unknown=7`
- Claim support role counts: `context_only=14, corroboration_support=1, insufficient_information=11, primary_case_claim_support=14`
- Fetch use counts: `fetch_for_context=14, fetch_for_extraction=15, fetch_only_after_review=11`
- Warning counts: `actual_publisher_unknown=22, direct_target_official_fast_path_skips_source_identity=40, publisher_from_search_metadata_unverified=40, search_provider_not_publisher=40`

### 6.4 LLM Structured Extraction

- Extraction mode: `llm_structured_output`
- Eligible chunk count: `690`
- LLM call count: `30`
- LLM success count: `30`
- LLM error count: `0`
- Raw record count: `6`

## 7. 最终抽取 records

- Normalized record count: `6`
- Run quality status: `human_review_required`
- Final dataset mode: `task_aware_quality_gated_records`
- Quality-gated accepted final dataset count: `0`
- Final case dataset count: `0`
- Zero-case statement count: `1`
- Exposure-monitoring record count: `0`
- Surveillance summary record count: `0`
- Outbreak summary record count: `0`
- Context record count: `2`
- Unclassified observation count: `0`
- Observation dataset view counts: `{'final_case_dataset': 0, 'global_outbreak_event_dataset': 0, 'regional_surveillance_dataset': 0, 'country_year_aggregate_dataset': 0, 'official_alert_dataset': 0, 'probable_case_dataset': 0, 'suspected_case_dataset': 0, 'unspecified_case_dataset': 0, 'death_dataset': 0, 'hospitalization_dataset': 0, 'zero_case_statements': 1, 'exposure_monitoring_records': 0, 'surveillance_summary_records': 0, 'outbreak_summary_records': 0, 'context_records': 2, 'non_primary_observations': 3, 'unclassified_observation_records': 0}`
- Pre-quality-gate record count: `6`
- Quarantined record count: `4`
- Pending review record count: `2`
- Non-primary observation count: `0`
- Final dataset post-review count: `0`
- Primary-case dataset status: `no_corroborated_primary_case_events`
- Recommended primary dataset message: `No primary case dataset records were accepted; inspect zero-case, exposure-monitoring, context, and other observation views.`
- Primary-case eligible accepted count: `0`
- Corroborated primary case event count: `0`
- Record inclusion status counts: `{'quarantined_outside_scope': 4, 'pending_human_review': 2}`
- Run quality warnings: `['no_corroborated_primary_case_events']`
- Accepted source counts: `none`

No quality-gated records are available to list.
Candidate records, if any, are recorded in the pre-quality, quarantined, and pending-review artifacts.

| Record ID | Date / period | Location | Cases | Deaths | Source | LLM used |
|---|---|---|---|---|---|---|

## 8. Validation 对比

### Claim-level corroboration

- Claim count: `9`
- Claim comparison count: `36`
- Corroborated event count: `1`
- Corroborated primary case event count: `0`
- Observation type counts: `confirmed_case_record=2, death_record=3, suspected_case_record=2, unspecified_case_record=2`
- Corroboration status counts: `conflicting_claims=1`

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

- Human review item count: `24`
- Evaluation review flag count: `0`
- Anomaly review item count: `1`

| Review ID | Type | Related IDs | Reason |
|---|---|---|---|
| review_source_credibility_src_search_505b2ac21551 | source_credibility | src_search_505b2ac21551 | This source presents several compounding credibility concerns that the deterministic assessment partially captures but underweights. The... |
| review_source_src_search_505b2ac21551 | source_screening | src_search_505b2ac21551 | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_src_search_f93d701ca110 | source_screening | src_search_f93d701ca110 | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_credibility_src_search_c853598f6ecb | source_credibility | src_search_c853598f6ecb | missing_publisher |
| review_source_src_search_c853598f6ecb | source_screening | src_search_c853598f6ecb | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_664c22f9e3a2 | source_credibility | src_search_664c22f9e3a2 | missing_publisher |
| review_source_src_search_664c22f9e3a2 | source_screening | src_search_664c22f9e3a2 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_5b9b31558c67 | source_credibility | src_search_5b9b31558c67 | missing_publisher |
| review_source_src_search_5b9b31558c67 | source_screening | src_search_5b9b31558c67 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_8929f93c6a7e | source_credibility | src_search_8929f93c6a7e | missing_publisher |
| review_source_src_search_8929f93c6a7e | source_screening | src_search_8929f93c6a7e | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_a0ed0f2ccd87 | source_credibility | src_search_a0ed0f2ccd87 | missing_publisher |

## 9.5 Stage 11 anomaly detection and review application

- Anomaly result count: `3`
- Anomaly severity counts: `low=2, medium=1`
- Anomaly needs-human-review count: `1`
- Decisions provided: `0`
- Decisions applied: `0`
- Decisions rejected: `0`
- Audit entries: `0`
- Final dataset post-review count: `0`
- Records excluded by review: `0`

| Anomaly ID | Type | Severity | Target | Reason |
|---|---|---|---|---|
| anom_001 | deaths_without_case_reference | low | rec_src_search_803858403368_002 | deaths present but no comparable case count is available |
| anom_002 | deaths_without_case_reference | low | rec_src_search_8fb70e3827e3_002 | deaths present but no comparable case count is available |
| anom_003 | aggregate_member_mismatch | medium | event_001 | event cluster canonical count differs from sum of comparable countable members |

| Applied decision | Type | Target | Audit IDs | Reason |
|---|---|---|---|---|

## 10. 输出文件

- Run output directory: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_cholera_haiti_2024_q4`
- Collection final dataset: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_cholera_haiti_2024_q4\collection\final_dataset.csv`
- Collection final case dataset: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_cholera_haiti_2024_q4\collection\final_case_dataset.csv`
- Collection zero-case statements: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_cholera_haiti_2024_q4\collection\zero_case_statements.csv`
- Collection exposure-monitoring records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_cholera_haiti_2024_q4\collection\exposure_monitoring_records.csv`
- Collection surveillance summaries: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_cholera_haiti_2024_q4\collection\surveillance_summary_records.csv`
- Collection outbreak summaries: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_cholera_haiti_2024_q4\collection\outbreak_summary_records.csv`
- Collection context records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_cholera_haiti_2024_q4\collection\context_records.csv`
- Collection unclassified observations: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_cholera_haiti_2024_q4\collection\unclassified_observation_records.csv`
- Collection observation dataset summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_cholera_haiti_2024_q4\collection\observation_type_dataset_summary.json`
- Collection pre-quality-gate records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_cholera_haiti_2024_q4\collection\final_dataset_pre_quality_gate.csv`
- Collection quarantined records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_cholera_haiti_2024_q4\collection\quarantined_records.csv`
- Collection pending review records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_cholera_haiti_2024_q4\collection\pending_review_records.csv`
- Collection non-primary observations: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_cholera_haiti_2024_q4\collection\non_primary_observations.csv`
- Collection record inclusion decisions: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_cholera_haiti_2024_q4\collection\record_inclusion_decisions.json`
- Collection final dataset post-review: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_cholera_haiti_2024_q4\collection\final_dataset_post_review.csv`
- Collection anomaly results: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_cholera_haiti_2024_q4\collection\anomaly_results.json`
- Collection human review audit trail: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_cholera_haiti_2024_q4\collection\human_review_audit_trail.json`
- Collection source registry: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_cholera_haiti_2024_q4\collection\source_registry.json`
- Validation mode: `diagnostic_only`
- Validation records source: `state`
- Validation records output: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_cholera_haiti_2024_q4\validation\ground_truth_records.csv`
- Inactive validation records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_cholera_haiti_2024_q4\validation\inactive_validation_records.csv`
- Validation compatibility summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_cholera_haiti_2024_q4\validation\validation_source_compatibility_summary.json`
- Evaluation report CSV: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_cholera_haiti_2024_q4\evaluation\evaluation_report.csv`
- Human-readable report: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_cholera_haiti_2024_q4\workflow_run_report_chinese.md`

## 11. 当前结论

This workflow run executed the configured data collection workflow through the exported graph and artifact pipeline. The user-facing run status is: STATUS: human_review_required
The run completed technically, but it should not be read as a successful data collection result because no quality-gated accepted records were produced.

- Package metadata says LLM used: `True`
- Contains synthetic fixture data: `False`
- Generated at UTC: `2026-06-25T19:17:26.594988+00:00`

## 12. Workflow visualization artifacts

- Workflow visualization index: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_cholera_haiti_2024_q4\workflow_visualization\index.html`
- Workflow timeline: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_cholera_haiti_2024_q4\workflow_visualization\workflow_timeline.html`
- Evidence flow graph: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_cholera_haiti_2024_q4\workflow_visualization\evidence_flow_graph.html`
- Claim comparison cards: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_cholera_haiti_2024_q4\workflow_visualization\claim_comparison_cards.html`
- Dataset decision flow: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_cholera_haiti_2024_q4\workflow_visualization\dataset_decision_flow.html`
- Human review workflow visualization: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_cholera_haiti_2024_q4\workflow_visualization\human_review_workflow.html`
- Visualization summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round04_cholera_haiti_2024_q4\workflow_visualization\workflow_visualization_summary.json`
