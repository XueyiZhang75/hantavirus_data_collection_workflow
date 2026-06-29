# data collection workflow Run Report

## 1. 输入任务

Collect Mpox cases, deaths, dates, locations, source URLs, source types, and evidence quotes for Democratic Republic of the Congo from 2024-08-01 to 2024-08-31.

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
- Search-derived source candidates: `29`
- Iterative source discovery: `True`
- Iterative search iterations: `1`
- Iterative stop decision: `stop_no_promising_sources`
- Iterative stop reason: `LLM requested continuation but returned no next query batch.`
- Source credibility assessed sources: `29`
- Source credibility role counts: `{'collection_support': 5, 'collection': 12, 'context': 3, 'excluded': 3, 'validation': 6}`
- Source identity assessed sources: `29`
- Source identity type counts: `{'unknown': 13, 'international_public_health_agency': 6, 'national_public_health_agency': 1, 'social_media': 2, 'structured_database': 1, 'official_public_health_agency': 6}`
- Source identity warning counts: `{'search_provider_not_publisher': 29, 'publisher_from_search_metadata_unverified': 29, 'actual_publisher_unknown': 21, 'direct_target_official_fast_path_skips_source_identity': 29}`
- Source discovery method: `live_search_only`
- Disease relevance target: `Mpox`
- Disease relevance source status counts: `{'target_disease_match': 25, 'insufficient_text': 3, 'ambiguous_disease': 1}`
- Disease relevance chunk status counts: `{'target_disease_match': 502, 'ambiguous_disease': 243, 'related_context_only': 156, 'insufficient_text': 307, 'unrelated_disease': 5}`
- Disease relevance record status counts: `{'compatible': 105}`
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
- Exposure-monitoring record count: `2`
- Surveillance summary record count: `26`
- Outbreak summary record count: `6`
- Context record count: `11`
- Unclassified observation count: `5`
- Observation dataset view counts: `{'final_case_dataset': 0, 'global_outbreak_event_dataset': 0, 'regional_surveillance_dataset': 0, 'country_year_aggregate_dataset': 0, 'official_alert_dataset': 0, 'probable_case_dataset': 0, 'suspected_case_dataset': 0, 'unspecified_case_dataset': 0, 'death_dataset': 0, 'hospitalization_dataset': 0, 'zero_case_statements': 0, 'exposure_monitoring_records': 2, 'surveillance_summary_records': 26, 'outbreak_summary_records': 6, 'context_records': 11, 'non_primary_observations': 28, 'unclassified_observation_records': 5}`
- Pre-quality-gate record count: `35`
- Quarantined record count: `11`
- Pending review record count: `19`
- Non-primary observation count: `13`
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
2. `disease_intelligence_builder` - Built disease intelligence from LLM output (Mpox (Monkeypox)).
3. `profile_and_schema_setup` - Built active disease profile, collection schema, and source strategy (Mpox (Monkeypox), generation_method=disease_int...
4. `executable_source_planning` - Built executable source plan with 10 planned queries; no searches were executed.
5. `query_strategy_builder` - Built 10 direct_collection search queries from the LLM evidence strategy plan.
6. `source_discovery` - Discovered 29 source candidates using live_search_only.
7. `source_dedup_and_registry` - Built source registry with 29 entries (0 duplicates dropped).
8. `source_screening` - Screened 29 sources using deterministic policy.
9. `source_critic_and_uncertainty_routing` - Critic reviewed 29 sources; 26 ready for fetch, 0 deferred, 16 flagged for human review.
10. `content_fetch_and_parse` - Built 26 fetch requests, produced 26 documents (live_fetch_enabled=True, fixture_documents_enabled=False, fixtures_lo...
11. `document_quality_check` - Quality-checked 26 documents: 22 usable, 1 partial, 0 offline stub, 0 parse deferred, 3 unusable.
12. `evidence_chunking_and_data_presence_flagging` - Chunked 23/26 documents into 1213 evidence chunks (458 flagged as containing target data).
13. `structured_extraction` - Built 35 raw records (extraction_mode=llm_structured_output, llm_enabled=True).
14. `schema_validation_and_repair` - Validated 35 raw records: 35 validated (5 need review), 0 rejected.
15. `record_normalization` - Normalized 35/35 records (5 need review).
16. `record_linking` - Linked 35/35 normalized records into 26 candidate events.
17. `cross_source_consistency_check` - Checked 8 multi-record events; found 2 new conflicts and 98 validation results (0 events need review).
18. `quality_gate_routing` - Human review disabled; preserving review flags as audit metadata and routing to final_data_package_builder.
19. `final_data_package_builder` - Assembled hardened FinalDataPackage from current state.

## 4. 数据源分工

| Role | Source ID | Publisher / title | Credibility | Final decision | Fetch ready |
|---|---|---|---|---|---|
| context_only | src_search_56e2081249ad | / Arise News - WHO has reported at least 8,000 Mpox cases in... | needs_review (0.5546) | needs_human_review | False |
| context_only | src_search_07a961e1c71b | European Centre for Disease Prevention and Control / Epidemiological update – Week 36/2024: Mpox due to monkeypox virus clade I | medium (0.7092) | needs_human_review | False |
| context_only | src_search_ea380d328268 | / Mpox cases have declined significantly in the DR Congo, health ... | needs_review (0.5362) | needs_human_review | False |
| other | src_search_525c0a51cb88 | / [PDF] Democratic Republic of Congo Mpox Level 3 Emergency-2024 ... | high (0.5786) | include_for_content_fetch | True |
| other | src_search_9befc0a97780 | / Multi-country outbreak of mpox, External situation report #42 - 9 November 2024 - Democratic Republic of the Congo / ReliefWeb | high (0.8594) | include_for_content_fetch | True |
| other | src_search_1bd6a9f9e638 | World Health Organization / [PDF] Mpox: Multi-country External Situation Report no.57 | medium (0.7036) | include_for_content_fetch | True |
| other | src_search_b0d9edeca9ff | / Situation Report: Mpox Spreads in Africa / NETEC | high (0.6338) | include_for_content_fetch | True |
| other | src_search_c86ca682ec75 | World Health Organization / Mpox - Democratic Republic of the Congo | high (0.8618) | include_for_content_fetch | True |
| other | src_search_bda3df613334 | Centers for Disease Control and Prevention / Health Alert Network (HAN) - 00513 / Mpox Caused by Human-to-Human Transmission of Monkeypox... | high (0.8826) | include_for_content_fetch | True |
| other | src_search_5d3071bb1dac | / Mpox outbreak in DR Congo: What to know / Doctors Without Borders - USA | high (0.6362) | include_for_content_fetch | True |
| other | src_search_1255139db91f | National Center for Biotechnology Information / Profil des cas de mpox identifiés lors de la surveillance de la zone de santé Kokolo à Ki... | high (0.6778) | include_for_content_fetch | True |
| other | src_search_24b596bdbb18 | / Rapport de la situation épidémiologique de la variole simienne ... | excluded (0.4498) | include_for_content_fetch | True |
| other | src_search_88f3866c9627 | / [PDF] Rapport - Annuel - INRB | excluded (0.3738) | include_for_content_fetch | True |
| other | src_search_6d0aa2af1853 | / Epidémie de mpox en RDC : déclarée urgence de santé publique internationale / Médecins Sans Frontières (MSF) | high (0.6266) | include_for_content_fetch | True |
| other | src_search_612c687e0be4 | / RDC : 20 décès dus au Mpox enregistrés à la première semaine de ... | high (0.6474) | include_for_content_fetch | True |
| other | src_search_fe1a1f839d46 | / RDC: 537 décès de l'épidémie de Mpox enregistrés depuis début ... | high (0.6658) | include_for_content_fetch | True |
| other | src_search_5f5f052dfde8 | World Health Organization / Variole simienne – République démocratique du Congo | medium (0.5932) | include_for_content_fetch | True |
| other | src_search_fca80a60fed0 | / Mpox : la situation en République démocratique du Congo reste « préoccupante » (OMS) / ONU Info | high (0.6266) | include_for_content_fetch | True |
| other | src_search_0a1fd0f7808b | World Health Organization / Mpox – African Region | high (0.7884) | include_for_content_fetch | True |
| other | src_search_c182f7c3ebb1 | World Health Organization / [PDF] Mpox Alert, 27 August 2024 Africa - NICD | high (0.5786) | include_for_content_fetch | True |
| other | src_search_46e96c569bac | Centers for Disease Control and Prevention / Clade I Mpox Outbreak Originating in Central Africa - Restored CDC | high (0.6362) | include_for_content_fetch | True |
| other | src_search_80ad6c5bbfa5 | / DRC officially declares the end of the mpox epidemic - BEACON | high (0.6154) | include_for_content_fetch | True |
| other | src_search_350b26302501 | / Africa Region / Mpox Appeal - Operation Update #3 (MDRS1003) | high (0.6362) | include_for_content_fetch | True |
| other | src_search_e6822a6db0e7 | / Clinical presentation and epidemiological assessment of confirmed ... | excluded (0.4362) | include_for_content_fetch | True |
| other | src_search_da73a01ad891 | Centers for Disease Control and Prevention / Mpox Sequencing in Africa - Democratic Republic of the Congo | high (0.8202) | include_for_content_fetch | True |
| other | src_search_cd800c67453f | / WHO African Region Mpox Bulletin - 11 August 2024 - ReliefWeb | medium (0.6546) | include_for_content_fetch | True |
| other | src_search_94cc3f59e20e | World Health Organization / [PDF] Mpox: Multi-country External Situation Report n.38 | medium (0.722) | include_for_content_fetch | True |
| other | src_search_fa50642e386d | Centers for Disease Control and Prevention / [PDF] Mpox Virus: Clade I and Clade II | medium (0.5578) | include_for_content_fetch | True |
| other | src_search_255065bc24b2 | Centers for Disease Control and Prevention / [PDF] Democratic Republic of Congo: Monkeypox outbreak - ACAPS | medium (0.5786) | include_for_content_fetch | True |

## 5. 真实网页抓取结果

- Documents fetched/parsed: `26`
- Search-derived sources selected for fetch: `26`
- Search-derived skipped by reason: `{}`
- Fetch status counts: `fetch_failed=2, fetched=24`
- External fetch enabled: `True`
- Fetch provider counts: `native_requests=3, tavily_extract=23`
- External fetch failure counts: `native_requests=2, tavily_extract=3`
- Selected fetch bucket counts: `target_official_authority=26`
- Parser status counts: `fetch_failed=1, parsed_html=2, parsed_text=23`
- Parser used counts: `html_stdlib_parser=2, text_parser=23, unknown=1`
- Quality status counts: `partial=1, unusable=3, usable=22`
- Validation-reserved skipped from fetch: `[]`

| Source ID | Provider | Fetch status | HTTP | Parse | Parser | Quality | Text chars | Tables |
|---|---|---|---|---|---|---|---|---|
| src_search_bda3df613334 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 7398 | 0 |
| src_search_c86ca682ec75 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 460904 | 0 |
| src_search_9befc0a97780 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 5476 | 0 |
| src_search_1bd6a9f9e638 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 22575 | 0 |
| src_search_5d3071bb1dac | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 14513 | 0 |
| src_search_b0d9edeca9ff | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 7706 | 0 |
| src_search_525c0a51cb88 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 27261 | 0 |
| src_search_1255139db91f | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 66352 | 0 |
| src_search_fe1a1f839d46 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 24361 | 0 |
| src_search_612c687e0be4 | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 9063 | 0 |
| src_search_6d0aa2af1853 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 6284 | 0 |
| src_search_fca80a60fed0 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 9740 | 0 |
| src_search_5f5f052dfde8 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 866389 | 0 |
| src_search_24b596bdbb18 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 3178 | 0 |
| src_search_88f3866c9627 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 76508 | 0 |
| src_search_0a1fd0f7808b | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 51004 | 0 |
| src_search_46e96c569bac | native_requests | fetch_failed | none | fetch_failed | none | unusable | 0 | 0 |
| src_search_350b26302501 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 4914 | 0 |
| src_search_80ad6c5bbfa5 | native_requests | fetched | 200 | parsed_html | html_stdlib_parser | partial | 129 | 0 |
| src_search_c182f7c3ebb1 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 14894 | 0 |
| src_search_e6822a6db0e7 | native_requests | fetch_failed | 403 | parsed_html | html_stdlib_parser | unusable | 325 | 0 |
| src_search_da73a01ad891 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 3115 | 0 |
| src_search_94cc3f59e20e | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 34320 | 0 |
| src_search_cd800c67453f | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 6896 | 0 |
| src_search_255065bc24b2 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 15130 | 0 |
| src_search_fa50642e386d | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 41180 | 0 |

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
- Skipped source count: `29`
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
- Assessed source count: `29`
- Final role counts: `collection=12, collection_support=5, context=3, excluded=3, validation=6`
- Risk flag counts: `ambiguous_disease=4, ambiguous_disease_signal_in_source_metadata=1, ambiguous_location=20, authority_score_likely_inflated:brand_recognition_not_equivalent_to_epidemiological_authority=1, clade_specificity_check: report title specifies clade I; collection spec window (August 2024) also involves clade Ib (South Kivu) — verify whether clade Ib data is included or excluded in this document=1, complete_source_provenance=8, context_or_background_only=2, data_granularity_insufficient: headline-level national aggregate (≥8,000 cases, 384 deaths for full year 2024) does not meet subnational or monthly resolution required by collection spec=1, data_signal_in_source_metadata=29, disease_relevance_unclear=3, domain_platform_mismatch:facebook.com_is_social_media_not_authoritative_source=1, domain_source_type_mismatch: domain is facebook.com but source_type is tagged international_organization_report — metadata misclassification requires correction=1, double_counting_risk: ECDC figures may overlap with WHO, Africa CDC, INRB, and DRC MoH reports — cross-reference source chains before aggregating=1, double_counting_risk:if_numeric_claims_present_they_are_secondary_restatements_of_official_data=1, evidence_quote_extraction_unreliable:no_structured_document_format=1, extraction_schema_warning: task_input_warnings flag extraction_record_model_still_hantavirus_named — confirm Mpox-appropriate schema is active before ingesting any values from this source=1, geographic_granularity_gap: ECDC report likely presents DRC data at national or regional aggregate level; subnational province/health-zone breakdown required by collection spec may be absent=1, geographic_granularity_insufficient:score_0.30_subnational_health_zone_data_unlikely=1, geographic_granularity_unclear=20, international_organization_authority=17, local_relevance_low:score_0.25=1, local_source_matches_task_location=4, location_relevance_unclear=20, low_machine_readability=7, missing_publisher=21, missing_publisher: publisher field is null despite identifiable page owner (Arise TV News)=1, missing_publisher_metadata=1, national_or_international_context=5, national_or_international_granularity=5, no_provenance_chain:cannot_verify_original_data_source_from_social_media_post=1, no_snippet_available: absence of snippet prevents verification of exact claims or evidence quote extraction=1, no_snippet_available: snippet=null; content and subnational data availability cannot be pre-screened — human or agent review of full document required before extraction decision=1, no_snippet_available:content_unverifiable_without_access=1, no_structured_data:social_media_posts_lack_epidemiological_data_integrity=1, not_suitable_for_evidence_quote: Facebook post format cannot reliably yield verbatim evidence quotes meeting collection spec requirements=1, official_public_health_authority=12, pdf_or_report_likely_medium_readability=7, pheic_context_volatility: WHO declared Mpox PHEIC on 14 August 2024; Week 36 (early September) data may reflect rapidly evolving figures subject to revision — note extraction date and version=1, pheic_period_social_media_risk: social media posts during PHEIC declaration windows are elevated risk for selective quoting, outdated figures, or clade/count conflation=1, primary_or_authoritative_source=29, publisher_identity_unverified:cgtn_africa_is_state_affiliated_broadcast_media_not_public_health_org=1, query_domain_mismatch:query_targeted_who.int_africacdc.org_reliefweb.int_but_result_resolved_to_facebook.com=1, role_conflict_hint_vs_assignment: role_hint=collection but deterministic and LLM both recommend context — confirm intended use before extraction=1, screening_and_critic_disagree=3, screening_and_critic_disagree: deterministic assessment flags internal role/credibility disagreement — additional review warranted=1, screening_and_critic_disagree: deterministic risk flag present — LLM review warranted to resolve role ambiguity=1, screening_and_critic_disagree:internal_pipeline_inconsistency=1, secondary_provenance: Arise TV News is relaying WHO figures, not publishing original data — original WHO source must be retrieved directly=1, secondary_source_for_drc_data: ECDC is a European body; DRC figures in this report are derived from primary DRC/WHO sources, not independently collected — treat as secondary for DRC-specific records=1, social_media_post: Facebook post is not a primary or authoritative source regardless of content referenced=1, source_disease_relevance:ambiguous_disease=1, source_disease_relevance:insufficient_text=3, source_disease_relevance:target_disease_match=25, source_metadata_matches_requested_disease=25, source_time_matches_requested_window=18, source_type_mislabel:labeled_international_organization_report_but_is_social_media_post=1, standard_web_page=22, task_location_granularity=4, temporal_scope_mismatch: cited figures appear to be cumulative 2024 totals, not August 2024 period-specific data=1, time_window_match_from_planned_query=11`
- LLM assessed count: `3`
- LLM failure count: `0`
- Needs review count: `14`

### 6.3.5 Source Identity / Publisher Assessment

- Identity assessed source count: `29`
- LLM identity assessed source count: `0`
- Post-fetch identity assessed source count: `26`
- Unknown publisher count: `16`
- Source type counts: `international_public_health_agency=6, national_public_health_agency=1, official_public_health_agency=6, social_media=2, structured_database=1, unknown=13`
- Claim support role counts: `context_only=7, insufficient_information=15, primary_case_claim_support=7`
- Fetch use counts: `fetch_for_context=7, fetch_for_extraction=7, fetch_only_after_review=15`
- Warning counts: `actual_publisher_unknown=21, direct_target_official_fast_path_skips_source_identity=29, publisher_from_search_metadata_unverified=29, search_provider_not_publisher=29`

### 6.4 LLM Structured Extraction

- Extraction mode: `llm_structured_output`
- Eligible chunk count: `907`
- LLM call count: `30`
- LLM success count: `30`
- LLM error count: `0`
- Raw record count: `35`

## 7. 最终抽取 records

- Normalized record count: `35`
- Run quality status: `partial_with_quarantined_records`
- Final dataset mode: `task_aware_quality_gated_records`
- Quality-gated accepted final dataset count: `5`
- Final case dataset count: `0`
- Zero-case statement count: `0`
- Exposure-monitoring record count: `2`
- Surveillance summary record count: `26`
- Outbreak summary record count: `6`
- Context record count: `11`
- Unclassified observation count: `5`
- Observation dataset view counts: `{'final_case_dataset': 0, 'global_outbreak_event_dataset': 0, 'regional_surveillance_dataset': 0, 'country_year_aggregate_dataset': 0, 'official_alert_dataset': 0, 'probable_case_dataset': 0, 'suspected_case_dataset': 0, 'unspecified_case_dataset': 0, 'death_dataset': 0, 'hospitalization_dataset': 0, 'zero_case_statements': 0, 'exposure_monitoring_records': 2, 'surveillance_summary_records': 26, 'outbreak_summary_records': 6, 'context_records': 11, 'non_primary_observations': 28, 'unclassified_observation_records': 5}`
- Pre-quality-gate record count: `35`
- Quarantined record count: `11`
- Pending review record count: `19`
- Non-primary observation count: `13`
- Final dataset post-review count: `5`
- Primary-case dataset status: `no_primary_case_dataset_records`
- Recommended primary dataset message: `No primary case dataset records were accepted; inspect zero-case, exposure-monitoring, context, and other observation views.`
- Primary-case eligible accepted count: `0`
- Corroborated primary case event count: `0`
- Record inclusion status counts: `{'quarantined_exposure_monitoring': 2, 'pending_human_review': 19, 'quarantined_outside_scope': 5, 'accepted_with_warnings': 5, 'quarantined_schema_invalid': 2, 'quarantined_chunk_not_task_relevant': 2}`
- Run quality warnings: `['no_primary_case_dataset_records', 'no_corroborated_primary_case_events']`
- Accepted source counts: `src_search_c86ca682ec75=5`

| Record ID | Date / period | Location | Cases | Deaths | Source | LLM used |
|---|---|---|---|---|---|---|
| rec_src_search_c86ca682ec75_004 | 2024-08-01 to 2024-08-31 | South Kivu | none | none | src_search_c86ca682ec75 | True |
| rec_src_search_c86ca682ec75_005 | 2024-08-01 to 2024-08-31 | South Kivu | none | none | src_search_c86ca682ec75 | True |
| rec_src_search_c86ca682ec75_006 | 2024-08-01 to 2024-08-31 | South Kivu | none | none | src_search_c86ca682ec75 | True |
| rec_src_search_c86ca682ec75_007 | 2024 | Democratic Republic of the Congo | none | none | src_search_c86ca682ec75 | True |
| rec_src_search_c86ca682ec75_008 | 2024 | South Kivu | none | none | src_search_c86ca682ec75 | True |

## 8. Validation 对比

### Claim-level corroboration

- Claim count: `40`
- Claim comparison count: `780`
- Corroborated event count: `12`
- Corroborated primary case event count: `0`
- Observation type counts: `ambiguous_public_health_observation=5, confirmed_case_record=4, death_record=7, hospitalization_record=2, outbreak_summary=6, surveillance_summary=4, suspected_case_record=3, unspecified_case_record=9`
- Corroboration status counts: `conflicting_claims=1, insufficient_information=4, single_source_unverified=7`

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

- Human review item count: `90`
- Evaluation review flag count: `0`
- Anomaly review item count: `14`

| Review ID | Type | Related IDs | Reason |
|---|---|---|---|
| review_source_credibility_src_search_525c0a51cb88 | source_credibility | src_search_525c0a51cb88 | disease_relevant_but_location_unclear; missing_publisher |
| review_source_src_search_525c0a51cb88 | source_screening | src_search_525c0a51cb88 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_9befc0a97780 | source_credibility | src_search_9befc0a97780 | missing_publisher |
| review_source_src_search_9befc0a97780 | source_screening | src_search_9befc0a97780 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_b0d9edeca9ff | source_credibility | src_search_b0d9edeca9ff | disease_relevant_but_location_unclear; missing_publisher |
| review_source_src_search_b0d9edeca9ff | source_screening | src_search_b0d9edeca9ff | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_5d3071bb1dac | source_credibility | src_search_5d3071bb1dac | disease_relevant_but_location_unclear; missing_publisher |
| review_source_src_search_5d3071bb1dac | source_screening | src_search_5d3071bb1dac | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_56e2081249ad | source_credibility | src_search_56e2081249ad | This source is a Facebook post from Arise TV News — a broadcast media outlet — sharing what appears to be a summary of WHO-reported Mpox... |
| review_source_src_search_56e2081249ad | source_screening | src_search_56e2081249ad | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_credibility_src_search_1255139db91f | source_credibility | src_search_1255139db91f | disease_relevant_but_location_unclear |
| review_source_src_search_1255139db91f | source_screening | src_search_1255139db91f | Source classified as data_source; both screening and critic agree to include for content fetch. |

## 9.5 Stage 11 anomaly detection and review application

- Anomaly result count: `18`
- Anomaly severity counts: `high=8, low=4, medium=6`
- Anomaly needs-human-review count: `14`
- Decisions provided: `0`
- Decisions applied: `0`
- Decisions rejected: `0`
- Audit entries: `0`
- Final dataset post-review count: `5`
- Records excluded by review: `0`

| Anomaly ID | Type | Severity | Target | Reason |
|---|---|---|---|---|
| anom_001 | test_positivity_or_rate_invalid | medium | rec_src_search_94cc3f59e20e_002 | positivity_rate is outside expected proportion bounds |
| anom_002 | deaths_without_case_reference | low | rec_src_search_da73a01ad891_003 | deaths present but no comparable case count is available |
| anom_003 | test_positivity_or_rate_invalid | medium | rec_src_search_c86ca682ec75_007 | positivity_rate is outside expected proportion bounds |
| anom_004 | test_positivity_or_rate_invalid | medium | rec_src_search_c86ca682ec75_008 | positivity_rate is outside expected proportion bounds |
| anom_005 | deaths_without_case_reference | low | rec_src_search_525c0a51cb88_002 | deaths present but no comparable case count is available |
| anom_006 | test_positivity_or_rate_invalid | medium | rec_src_search_525c0a51cb88_005 | positivity_rate is outside expected proportion bounds |
| anom_007 | test_positivity_or_rate_invalid | medium | rec_src_search_255065bc24b2_002 | positivity_rate is outside expected proportion bounds |
| anom_008 | deaths_without_case_reference | low | rec_src_search_1bd6a9f9e638_002 | deaths present but no comparable case count is available |
| anom_009 | deaths_without_case_reference | low | rec_src_search_5d3071bb1dac_002 | deaths present but no comparable case count is available |
| anom_010 | out_of_scope_count_bearing_record | high | event_010 | Stage 10 validation marked record outside requested scope: outside_geography |
| anom_011 | out_of_scope_count_bearing_record | high | event_010 | Stage 10 validation marked record outside requested scope: outside_geography |
| anom_012 | out_of_scope_count_bearing_record | high | event_010 | Stage 10 validation marked record outside requested scope: outside_geography |

| Applied decision | Type | Target | Audit IDs | Reason |
|---|---|---|---|---|

## 10. 输出文件

- Run output directory: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_mpox_drc_2024_08`
- Collection final dataset: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_mpox_drc_2024_08\collection\final_dataset.csv`
- Collection final case dataset: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_mpox_drc_2024_08\collection\final_case_dataset.csv`
- Collection zero-case statements: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_mpox_drc_2024_08\collection\zero_case_statements.csv`
- Collection exposure-monitoring records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_mpox_drc_2024_08\collection\exposure_monitoring_records.csv`
- Collection surveillance summaries: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_mpox_drc_2024_08\collection\surveillance_summary_records.csv`
- Collection outbreak summaries: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_mpox_drc_2024_08\collection\outbreak_summary_records.csv`
- Collection context records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_mpox_drc_2024_08\collection\context_records.csv`
- Collection unclassified observations: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_mpox_drc_2024_08\collection\unclassified_observation_records.csv`
- Collection observation dataset summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_mpox_drc_2024_08\collection\observation_type_dataset_summary.json`
- Collection pre-quality-gate records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_mpox_drc_2024_08\collection\final_dataset_pre_quality_gate.csv`
- Collection quarantined records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_mpox_drc_2024_08\collection\quarantined_records.csv`
- Collection pending review records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_mpox_drc_2024_08\collection\pending_review_records.csv`
- Collection non-primary observations: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_mpox_drc_2024_08\collection\non_primary_observations.csv`
- Collection record inclusion decisions: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_mpox_drc_2024_08\collection\record_inclusion_decisions.json`
- Collection final dataset post-review: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_mpox_drc_2024_08\collection\final_dataset_post_review.csv`
- Collection anomaly results: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_mpox_drc_2024_08\collection\anomaly_results.json`
- Collection human review audit trail: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_mpox_drc_2024_08\collection\human_review_audit_trail.json`
- Collection source registry: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_mpox_drc_2024_08\collection\source_registry.json`
- Validation mode: `diagnostic_only`
- Validation records source: `state`
- Validation records output: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_mpox_drc_2024_08\validation\ground_truth_records.csv`
- Inactive validation records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_mpox_drc_2024_08\validation\inactive_validation_records.csv`
- Validation compatibility summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_mpox_drc_2024_08\validation\validation_source_compatibility_summary.json`
- Evaluation report CSV: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_mpox_drc_2024_08\evaluation\evaluation_report.csv`
- Human-readable report: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_mpox_drc_2024_08\workflow_run_report_chinese.md`

## 11. 当前结论

This workflow run executed the configured data collection workflow through the exported graph and artifact pipeline. The user-facing run status is: PARTIAL: accepted records produced, but some records were quarantined.
The run completed technically and produced quality-gated accepted records in the final dataset.

- Package metadata says LLM used: `True`
- Contains synthetic fixture data: `False`
- Generated at UTC: `2026-06-25T15:20:22.302703+00:00`

## 12. Workflow visualization artifacts

- Workflow visualization index: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_mpox_drc_2024_08\workflow_visualization\index.html`
- Workflow timeline: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_mpox_drc_2024_08\workflow_visualization\workflow_timeline.html`
- Evidence flow graph: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_mpox_drc_2024_08\workflow_visualization\evidence_flow_graph.html`
- Claim comparison cards: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_mpox_drc_2024_08\workflow_visualization\claim_comparison_cards.html`
- Dataset decision flow: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_mpox_drc_2024_08\workflow_visualization\dataset_decision_flow.html`
- Human review workflow visualization: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_mpox_drc_2024_08\workflow_visualization\human_review_workflow.html`
- Visualization summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round02_mpox_drc_2024_08\workflow_visualization\workflow_visualization_summary.json`
