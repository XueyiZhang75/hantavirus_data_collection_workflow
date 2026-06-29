# data collection workflow Run Report

## 1. 输入任务

Collect data on hantavirus from 2020 to 2026. For this workflow run, use the New Mexico HPS source set, keep collection sources and validation sources separated, extract cases, deaths, dates, locations, source URLs, source types, and evidence quotes.

## 2. 本次运行模式

- Live webpage fetch: `False`
- Fixture documents: `False`
- Provider: `anthropic`
- Model: `claude-sonnet-4-6`
- API key present: `True`
- LLM source planning: `False`
- LLM source critic: `False`
- LLM source identity assessed sources: `0`
- LLM structured extraction: `False`
- Source search mode: `live`
- Source search provider: `tavily`
- Source search executed queries: `0`
- Search-derived source candidates: `0`
- Iterative source discovery: `True`
- Iterative search iterations: `0`
- Iterative stop decision: `stop_llm_unavailable`
- Iterative stop reason: `iterative_llm_initial_plan_failed:ValueError`
- Source credibility assessed sources: `20`
- Source credibility role counts: `{'collection': 3, 'context': 8, 'validation': 4, 'search_endpoint': 5}`
- Source identity assessed sources: `20`
- Source identity type counts: `{'state_or_local_public_health_agency': 5, 'national_public_health_agency': 4, 'international_public_health_agency': 6, 'search_endpoint': 3, 'unknown': 1, 'news_media': 1}`
- Source identity warning counts: `{'actual_publisher_unknown': 4}`
- Source discovery method: `live_search_plus_seed_catalog`
- Disease relevance target: `Hantavirus disease`
- Disease relevance source status counts: `{'target_disease_match': 20}`
- Disease relevance chunk status counts: `{}`
- Disease relevance record status counts: `{}`
- Rejected incompatible record count: `0`
- Final route: `finalize`

## 2.5 Run quality status

- User-facing run status: `COMPLETED WITH NO TASK-RELEVANT RECORDS: no accepted records passed the disease/task relevance gates. Held-out validation was limited because no task-compatible validation source was available.`
- Technical execution status: `completed`
- Run quality status: `no_task_relevant_records`
- Final dataset mode: `task_aware_quality_gated_records`
- Accepted final dataset count: `0`
- Final case dataset count: `0`
- Zero-case statement count: `0`
- Exposure-monitoring record count: `0`
- Surveillance summary record count: `0`
- Outbreak summary record count: `0`
- Context record count: `0`
- Unclassified observation count: `0`
- Observation dataset view counts: `{'final_case_dataset': 0, 'global_outbreak_event_dataset': 0, 'regional_surveillance_dataset': 0, 'country_year_aggregate_dataset': 0, 'official_alert_dataset': 0, 'probable_case_dataset': 0, 'suspected_case_dataset': 0, 'unspecified_case_dataset': 0, 'death_dataset': 0, 'hospitalization_dataset': 0, 'zero_case_statements': 0, 'exposure_monitoring_records': 0, 'surveillance_summary_records': 0, 'outbreak_summary_records': 0, 'context_records': 0, 'non_primary_observations': 0, 'unclassified_observation_records': 0}`
- Pre-quality-gate record count: `0`
- Quarantined record count: `0`
- Pending review record count: `0`
- Non-primary observation count: `0`
- Final dataset post-review count: `0`
- Primary-case dataset status: `unknown_no_claim_outputs`
- Recommended primary dataset message: `No primary case dataset records were accepted; inspect zero-case, exposure-monitoring, context, and other observation views.`
- Primary-case eligible accepted count: `0`
- Corroborated primary case event count: `0`
- Recommended user message: `No reliable task-relevant records were accepted; inspect search, fetch, extraction, and quarantine diagnostics.`

workflow technically completed, but no quality-gated accepted records were produced.
本次 workflow 技术上完成，但没有产生通过质量门的 accepted records。

Workflow technically completed, but no primary case dataset records were accepted. Non-primary observations were preserved separately and should not be read as final epidemiological case data.

Live cross-source validation was limited because this run did not find a task-compatible validation source.
This does not prove absence of cases; it means the live search/fetch set did not include enough independent validation evidence.

## 3. Workflow 运行过程

Graph is executed as a mostly serial workflow. The only conditional branch is after `quality_gate_routing`: the run enters `human_review` when quality or validation checks require review, then still builds the final data package. In this run, the graph route is shown above; validation comparison review flags are reported separately in Section 8.

1. `task_intake_and_scope_planning` - Built CollectionSpec from structured task input.
2. `disease_intelligence_builder` - Built disease intelligence (Hantavirus disease, generation_method=curated_profile).
3. `profile_and_schema_setup` - Built active disease profile, collection schema, and source strategy (Hantavirus disease, generation_method=legacy_ha...
4. `executable_source_planning` - Built executable source plan with 10 planned queries; no searches were executed.
5. `query_strategy_builder` - Built 91 search queries across 5 source categories (executable_source_plan_present=True).
6. `source_discovery` - Discovered 21 source candidates using live_search_plus_seed_catalog.
7. `source_dedup_and_registry` - Built source registry with 20 entries (1 duplicates dropped).
8. `source_screening` - Screened 20 sources using deterministic policy.
9. `source_critic_and_uncertainty_routing` - Critic reviewed 20 sources; 11 ready for fetch, 5 deferred, 0 flagged for human review.
10. `content_fetch_and_parse` - Built 5 fetch requests, produced 5 documents (live_fetch_enabled=False, fixture_documents_enabled=False, fixtures_loa...
11. `document_quality_check` - Quality-checked 5 documents: 0 usable, 0 partial, 5 offline stub, 0 parse deferred, 0 unusable.
12. `evidence_chunking_and_data_presence_flagging` - Chunked 0/5 documents into 0 evidence chunks (0 flagged as containing target data).
13. `structured_extraction` - Built 0 raw records (extraction_mode=deterministic_rule_based, llm_enabled=False).
14. `schema_validation_and_repair` - Validated 0 raw records: 0 validated (0 need review), 0 rejected.
15. `record_normalization` - Normalized 0/0 records (0 need review).
16. `record_linking` - Linked 0/0 normalized records into 0 candidate events.
17. `cross_source_consistency_check` - Checked 0 multi-record events; found 0 new conflicts and 0 validation results (0 events need review).
18. `quality_gate_routing` - Human review disabled; preserving review flags as audit metadata and routing to final_data_package_builder.
19. `final_data_package_builder` - Assembled hardened FinalDataPackage from current state.

## 4. 数据源分工

| Role | Source ID | Publisher / title | Credibility | Final decision | Fetch ready |
|---|---|---|---|---|---|
| collection | src_nmdoh_hps_2024_first_case | New Mexico Department of Health / NMDOH: New Mexico reports first hantavirus pulmonary syndrome case of 2024 | high (0.8978) | include_for_content_fetch | True |
| collection | src_nmdoh_hps_2025_first_case_death | New Mexico Department of Health / NMDOH: Hantavirus death confirmed in Santa Fe County woman | high (0.9095) | include_for_content_fetch | True |
| collection | src_nmdoh_hps_2026_first_case_prior_year_summary | New Mexico Department of Health / NMDOH: Hantavirus confirmed in Santa Fe County resident | high (0.9279) | include_for_content_fetch | True |
| context_only | src_nmdoh_hps_overview_1975_2025 | New Mexico Department of Health / NMDOH: Hantavirus Pulmonary Syndrome | high (0.877) | include_for_context_fetch | True |
| context_only | src_cdc_hantavirus_reported_cases_through_2023 | CDC / CDC: Reported Cases of Hantavirus Disease | high (0.9083) | include_for_context_fetch | True |
| context_only | src_cdc_about_hantavirus | CDC / About Hantavirus | high (0.8048) | include_for_context_fetch | True |
| context_only | src_cdc_clinical_overview | CDC / Clinical Overview of Hantavirus | medium (0.6646) | include_for_context_fetch | True |
| context_only | src_ecdc_hantavirus_infection | ECDC / Hantavirus infection | medium (0.6578) | include_for_context_fetch | True |
| validation_reserved | src_nmdoh_hps_cases_by_county_1975_2025_pdf | New Mexico Department of Health / NMDOH: HPS Cases in New Mexico by County, 1975-2025 | high (0.8139) | reserved_for_validation | False |
| validation_reserved | src_who_hantavirus_fact_sheet | WHO / Hantavirus | medium (0.6438) | reserved_for_validation | False |
| validation_reserved | src_ecdc_surveillance_updates | ECDC / Surveillance and updates for hantavirus | high (0.8188) | reserved_for_validation | False |
| validation_reserved | src_ecdc_annual_report_2023 | ECDC / Hantavirus infection - Annual Epidemiological Report for 2023 | high (0.8188) | reserved_for_validation | False |
| other | src_cdc_case_definition_reporting | CDC / Hantavirus Case Definition and Reporting | medium (0.6646) | include_for_content_fetch | True |
| other | src_ecdc_factsheet_orthohantavirus | ECDC / Factsheet on orthohantavirus infections | medium (0.6646) | include_for_content_fetch | True |
| other | src_paho_hantavirus_americas_guidelines | PAHO / Hantavirus in the Americas: guidelines for prevention, diagnosis, treatment, and control | medium (0.6534) | include_for_content_fetch | True |
| other | src_pubmed_hantavirus_search | PubMed / PubMed search for hantavirus outbreak cases deaths | medium (0.6576) | defer_to_search_expansion | False |
| other | src_europe_pmc_hantavirus_search | Europe PMC / Europe PMC search for hantavirus outbreak cases deaths | medium (0.617) | defer_to_search_expansion | False |
| other | src_openalex_hantavirus_search | OpenAlex / OpenAlex search for hantavirus outbreak cases deaths | medium (0.617) | defer_to_search_expansion | False |
| other | src_structured_database_surveillance_query | Internal seed catalog / Hantavirus surveillance dataset query | medium (0.6236) | defer_to_search_expansion | False |
| other | src_news_situation_report_query | Internal seed catalog / Hantavirus outbreak news and situation report query | low (0.3692) | defer_to_search_expansion | False |

## 5. 真实网页抓取结果

- Documents fetched/parsed: `5`
- Search-derived sources selected for fetch: `0`
- Search-derived skipped by reason: `{}`
- Fetch status counts: `offline_stub=5`
- External fetch enabled: `True`
- Fetch provider counts: `offline_stub=5`
- External fetch failure counts: `none`
- Selected fetch bucket counts: `national_context=1, official_authority=2, target_official_authority=2`
- Parser status counts: `offline_stub=5`
- Parser used counts: `offline_metadata_stub=5`
- Quality status counts: `offline_stub_pending_live_fetch=5`
- Validation-reserved skipped from fetch: `['src_nmdoh_hps_cases_by_county_1975_2025_pdf', 'src_who_hantavirus_fact_sheet', 'src_ecdc_surveillance_updates', 'src_ecdc_annual_report_2023']`

| Source ID | Provider | Fetch status | HTTP | Parse | Parser | Quality | Text chars | Tables |
|---|---|---|---|---|---|---|---|---|
| src_nmdoh_hps_2024_first_case | offline_stub | offline_stub | none | offline_stub | offline_metadata_stub | offline_stub_pending_live_fetch | 572 | 0 |
| src_nmdoh_hps_2025_first_case_death | offline_stub | offline_stub | none | offline_stub | offline_metadata_stub | offline_stub_pending_live_fetch | 561 | 0 |
| src_nmdoh_hps_2026_first_case_prior_year_summary | offline_stub | offline_stub | none | offline_stub | offline_metadata_stub | offline_stub_pending_live_fetch | 596 | 0 |
| src_nmdoh_hps_overview_1975_2025 | offline_stub | offline_stub | none | offline_stub | offline_metadata_stub | offline_stub_pending_live_fetch | 730 | 0 |
| src_cdc_hantavirus_reported_cases_through_2023 | offline_stub | offline_stub | none | offline_stub | offline_metadata_stub | offline_stub_pending_live_fetch | 753 | 0 |

## 6. 三个 LLM 环节调用结果

### 6.1 LLM Source Planning

- Status: `deterministic_plan_created`
- Plan generation method: `deterministic_executable_source_plan`
- Plan execution status: `planned_not_executed`
- Planned query count: `10`
- Planned source category count: `5`
- Provider channel counts: `database_search=2, literature_api=2, news_search=2, official_site_search=4`
- Agent query count: `10`
- Agent query added count: `10`
- Candidate hint count: `0`

### 6.1.5 LLM Iterative Source Discovery

- Enabled: `True`
- LLM iterative planning enabled: `False`
- Search iteration count: `0`
- LLM refinement call count: `0`
- Total queries planned: `0`
- Total queries executed: `0`
- Stop decision: `stop_llm_unavailable`
- Stop reason: `iterative_llm_initial_plan_failed:ValueError`
- Query source counts: `{}`
- Iteration query counts: `{}`

### 6.2 LLM Source Critic

- Attempted source count: `0`
- Assessed source count: `0`
- Skipped source count: `0`
- Blocked fetch count: `0`
- Allowed fetch count: `0`
- Context-only count: `0`
- Needs review count: `0`
- Max sources: `6`
- Review blocks fetch: `False`
- Failure count: `0`
- Semantic leakage count: `0`
- Human review recommended count: `0`
- Critic decision counts: `none`
- Fetch recommendation counts: `none`
- Risk flag counts: `none`
- Selected source IDs: ``

### 6.3 Optional LLM Source Credibility Advisory

- Enabled: `False`
- Assessed source count: `20`
- Final role counts: `collection=3, context=8, search_endpoint=5, validation=4`
- Risk flag counts: `academic_or_literature_source=2, blocked_from_collection=4, case_death_date_location_expected=4, complete_source_provenance=20, context_or_background_only=5, context_or_prevention_only=5, data_granularity_unclear=1, data_signal_in_source_metadata=1, independent_literature_source=2, international_organization_authority=1, local_or_subnational_granularity=4, local_source_matches_task_location=6, location_match_from_planned_query=14, low_authority_relevant_source=1, low_machine_readability=2, machine_readable_or_structured=1, named_publisher=2, national_or_international_granularity=14, not_directly_extractable_search_endpoint=5, official_public_health_authority=15, partial_case_or_death_data_expected=4, pdf_or_report_likely_medium_readability=1, placeholder_uri_not_fetchable=1, primary_or_authoritative_source=16, secondary_news_or_media_source=1, source_disease_relevance:target_disease_match=20, source_likely_not_extractable=11, source_metadata_matches_requested_disease=20, source_time_matches_requested_window=2, standard_web_page=17, structured_data_source=1, task_location_granularity=2, time_window_match_from_planned_query=18, validation_reserved=4`
- LLM assessed count: `0`
- LLM failure count: `0`
- Needs review count: `0`

### 6.3.5 Source Identity / Publisher Assessment

- Identity assessed source count: `20`
- LLM identity assessed source count: `0`
- Post-fetch identity assessed source count: `5`
- Unknown publisher count: `4`
- Source type counts: `international_public_health_agency=6, national_public_health_agency=4, news_media=1, search_endpoint=3, state_or_local_public_health_agency=5, unknown=1`
- Claim support role counts: `context_only=5, corroboration_support=1, insufficient_information=1, primary_case_claim_support=10, search_discovery_only=3`
- Fetch use counts: `do_not_fetch=3, fetch_for_context=5, fetch_for_extraction=11, fetch_only_after_review=1`
- Warning counts: `actual_publisher_unknown=4`

### 6.4 LLM Structured Extraction

- Extraction mode: `deterministic_rule_based`
- Eligible chunk count: `0`
- LLM call count: `0`
- LLM success count: `0`
- LLM error count: `0`
- Raw record count: `0`

## 7. 最终抽取 records

- Normalized record count: `0`
- Run quality status: `no_task_relevant_records`
- Final dataset mode: `task_aware_quality_gated_records`
- Quality-gated accepted final dataset count: `0`
- Final case dataset count: `0`
- Zero-case statement count: `0`
- Exposure-monitoring record count: `0`
- Surveillance summary record count: `0`
- Outbreak summary record count: `0`
- Context record count: `0`
- Unclassified observation count: `0`
- Observation dataset view counts: `{'final_case_dataset': 0, 'global_outbreak_event_dataset': 0, 'regional_surveillance_dataset': 0, 'country_year_aggregate_dataset': 0, 'official_alert_dataset': 0, 'probable_case_dataset': 0, 'suspected_case_dataset': 0, 'unspecified_case_dataset': 0, 'death_dataset': 0, 'hospitalization_dataset': 0, 'zero_case_statements': 0, 'exposure_monitoring_records': 0, 'surveillance_summary_records': 0, 'outbreak_summary_records': 0, 'context_records': 0, 'non_primary_observations': 0, 'unclassified_observation_records': 0}`
- Pre-quality-gate record count: `0`
- Quarantined record count: `0`
- Pending review record count: `0`
- Non-primary observation count: `0`
- Final dataset post-review count: `0`
- Primary-case dataset status: `unknown_no_claim_outputs`
- Recommended primary dataset message: `No primary case dataset records were accepted; inspect zero-case, exposure-monitoring, context, and other observation views.`
- Primary-case eligible accepted count: `0`
- Corroborated primary case event count: `0`
- Record inclusion status counts: `{}`
- Run quality warnings: `['no_task_compatible_validation_source', 'validation_limited_no_compatible_source']`
- Accepted source counts: `none`

No quality-gated records are available to list.
Candidate records, if any, are recorded in the pre-quality, quarantined, and pending-review artifacts.

| Record ID | Date / period | Location | Cases | Deaths | Source | LLM used |
|---|---|---|---|---|---|---|

## 8. Validation 对比

### Claim-level corroboration

- Claim count: `0`
- Claim comparison count: `0`
- Corroborated event count: `0`
- Corroborated primary case event count: `0`
- Observation type counts: `none`
- Corroboration status counts: `none`

- Validation source compatibility status: `live_validation_pending`
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

- Human review item count: `0`
- Evaluation review flag count: `0`
- Anomaly review item count: `0`

| Review ID | Type | Related IDs | Reason |
|---|---|---|---|

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

- Run output directory: `C:\Users\zhang\AppData\Local\Temp\pytest-of-zhang\pytest-132\test_configured_workflow_scrip0\sessions\test_session`
- Collection final dataset: `C:\Users\zhang\AppData\Local\Temp\pytest-of-zhang\pytest-132\test_configured_workflow_scrip0\sessions\test_session\collection\final_dataset.csv`
- Collection final case dataset: `C:\Users\zhang\AppData\Local\Temp\pytest-of-zhang\pytest-132\test_configured_workflow_scrip0\sessions\test_session\collection\final_case_dataset.csv`
- Collection zero-case statements: `C:\Users\zhang\AppData\Local\Temp\pytest-of-zhang\pytest-132\test_configured_workflow_scrip0\sessions\test_session\collection\zero_case_statements.csv`
- Collection exposure-monitoring records: `C:\Users\zhang\AppData\Local\Temp\pytest-of-zhang\pytest-132\test_configured_workflow_scrip0\sessions\test_session\collection\exposure_monitoring_records.csv`
- Collection surveillance summaries: `C:\Users\zhang\AppData\Local\Temp\pytest-of-zhang\pytest-132\test_configured_workflow_scrip0\sessions\test_session\collection\surveillance_summary_records.csv`
- Collection outbreak summaries: `C:\Users\zhang\AppData\Local\Temp\pytest-of-zhang\pytest-132\test_configured_workflow_scrip0\sessions\test_session\collection\outbreak_summary_records.csv`
- Collection context records: `C:\Users\zhang\AppData\Local\Temp\pytest-of-zhang\pytest-132\test_configured_workflow_scrip0\sessions\test_session\collection\context_records.csv`
- Collection unclassified observations: `C:\Users\zhang\AppData\Local\Temp\pytest-of-zhang\pytest-132\test_configured_workflow_scrip0\sessions\test_session\collection\unclassified_observation_records.csv`
- Collection observation dataset summary: `C:\Users\zhang\AppData\Local\Temp\pytest-of-zhang\pytest-132\test_configured_workflow_scrip0\sessions\test_session\collection\observation_type_dataset_summary.json`
- Collection pre-quality-gate records: `C:\Users\zhang\AppData\Local\Temp\pytest-of-zhang\pytest-132\test_configured_workflow_scrip0\sessions\test_session\collection\final_dataset_pre_quality_gate.csv`
- Collection quarantined records: `C:\Users\zhang\AppData\Local\Temp\pytest-of-zhang\pytest-132\test_configured_workflow_scrip0\sessions\test_session\collection\quarantined_records.csv`
- Collection pending review records: `C:\Users\zhang\AppData\Local\Temp\pytest-of-zhang\pytest-132\test_configured_workflow_scrip0\sessions\test_session\collection\pending_review_records.csv`
- Collection non-primary observations: `C:\Users\zhang\AppData\Local\Temp\pytest-of-zhang\pytest-132\test_configured_workflow_scrip0\sessions\test_session\collection\non_primary_observations.csv`
- Collection record inclusion decisions: `C:\Users\zhang\AppData\Local\Temp\pytest-of-zhang\pytest-132\test_configured_workflow_scrip0\sessions\test_session\collection\record_inclusion_decisions.json`
- Collection final dataset post-review: `C:\Users\zhang\AppData\Local\Temp\pytest-of-zhang\pytest-132\test_configured_workflow_scrip0\sessions\test_session\collection\final_dataset_post_review.csv`
- Collection anomaly results: `C:\Users\zhang\AppData\Local\Temp\pytest-of-zhang\pytest-132\test_configured_workflow_scrip0\sessions\test_session\collection\anomaly_results.json`
- Collection human review audit trail: `C:\Users\zhang\AppData\Local\Temp\pytest-of-zhang\pytest-132\test_configured_workflow_scrip0\sessions\test_session\collection\human_review_audit_trail.json`
- Collection source registry: `C:\Users\zhang\AppData\Local\Temp\pytest-of-zhang\pytest-132\test_configured_workflow_scrip0\sessions\test_session\collection\source_registry.json`
- Validation mode: `live_cross_source`
- Validation records source: `none`
- Validation records output: `C:\Users\zhang\AppData\Local\Temp\pytest-of-zhang\pytest-132\test_configured_workflow_scrip0\sessions\test_session\validation\ground_truth_records.csv`
- Inactive validation records: `C:\Users\zhang\AppData\Local\Temp\pytest-of-zhang\pytest-132\test_configured_workflow_scrip0\sessions\test_session\validation\inactive_validation_records.csv`
- Validation compatibility summary: `C:\Users\zhang\AppData\Local\Temp\pytest-of-zhang\pytest-132\test_configured_workflow_scrip0\sessions\test_session\validation\validation_source_compatibility_summary.json`
- Evaluation report CSV: `C:\Users\zhang\AppData\Local\Temp\pytest-of-zhang\pytest-132\test_configured_workflow_scrip0\sessions\test_session\evaluation\evaluation_report.csv`
- Human-readable report: `C:\Users\zhang\AppData\Local\Temp\pytest-of-zhang\pytest-132\test_configured_workflow_scrip0\sessions\test_session\workflow_run_report_chinese.md`

## 11. 当前结论

This workflow run executed the configured data collection workflow through the exported graph and artifact pipeline. The user-facing run status is: COMPLETED WITH NO TASK-RELEVANT RECORDS: no accepted records passed the disease/task relevance gates. Held-out validation was limited because no task-compatible validation source was available.
The run completed technically, but it should not be read as a successful data collection result because no quality-gated accepted records were produced.

- Package metadata says LLM used: `False`
- Contains synthetic fixture data: `False`
- Generated at UTC: `2026-06-29T14:35:41.386554+00:00`

## 12. Workflow visualization artifacts

- Workflow visualization index: `C:\Users\zhang\AppData\Local\Temp\pytest-of-zhang\pytest-132\test_configured_workflow_scrip0\sessions\test_session\workflow_visualization\index.html`
- Workflow timeline: `C:\Users\zhang\AppData\Local\Temp\pytest-of-zhang\pytest-132\test_configured_workflow_scrip0\sessions\test_session\workflow_visualization\workflow_timeline.html`
- Evidence flow graph: `C:\Users\zhang\AppData\Local\Temp\pytest-of-zhang\pytest-132\test_configured_workflow_scrip0\sessions\test_session\workflow_visualization\evidence_flow_graph.html`
- Claim comparison cards: `C:\Users\zhang\AppData\Local\Temp\pytest-of-zhang\pytest-132\test_configured_workflow_scrip0\sessions\test_session\workflow_visualization\claim_comparison_cards.html`
- Dataset decision flow: `C:\Users\zhang\AppData\Local\Temp\pytest-of-zhang\pytest-132\test_configured_workflow_scrip0\sessions\test_session\workflow_visualization\dataset_decision_flow.html`
- Human review workflow visualization: `C:\Users\zhang\AppData\Local\Temp\pytest-of-zhang\pytest-132\test_configured_workflow_scrip0\sessions\test_session\workflow_visualization\human_review_workflow.html`
- Visualization summary: `C:\Users\zhang\AppData\Local\Temp\pytest-of-zhang\pytest-132\test_configured_workflow_scrip0\sessions\test_session\workflow_visualization\workflow_visualization_summary.json`
