# data collection workflow Run Report

## 1. 输入任务

Collect West Nile virus cases, deaths, dates, locations, source URLs, source types, and evidence quotes for California from 2024-08-01 to 2024-08-31.

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
- Search-derived source candidates: `46`
- Iterative source discovery: `True`
- Iterative search iterations: `2`
- Iterative stop decision: `stop_sufficient`
- Iterative stop reason: `Maximum iterations (2) reached. The search has surfaced a strong, multi-layered set of authoritative source candidates: (1) The CDPH VBDS Annual Report 2024 (westnile.ca.gov/pdfs/VBDSAnnualReport24.pdf) — the highest-authority source, providing county-level WNV case incidence for 2024 across all California counties, enabling population of subnational_location, locality, cases_confirmed, and date_reported fields; (2) CDPH News Release NR24-27 (cdph.ca.gov/Programs/OPA/Pages/NR24-27.aspx) — reporting 63 human WNV cases and 6 deaths for 2024, with evidence quote potential; (3) CDPH 2024 Year-End Monthly Summary PDF (cdph.ca.gov) — providing WNV case type breakdowns (neuroinvasive: 103, non-neuroinvasive: 30, asymptomatic: 20, total: 153) with monthly columns; (4) Greater Los Angeles County Vector Control District 2024 activity page (glamosquito.org) — providing locality-level August 2024 mosquito pool data with specific dates (8/7/2024, 8/22/2024, 8/29/2024) and neighborhood-level granularity; (5) contracosta.news article (2024-10-01) republishing CDPH figures (63 cases, 6 deaths) with evidence quote; (6) CDC Historic Data page (cdc.gov/west-nile-virus/data-maps/historic-data.html) — ArboNET state-level data for cross-validation; (7) kernpublichealth.com, ruhealth.org, nevadacountyca.gov — county-level public health sources for Kern, Riverside, and Nevada counties. Key remaining gap: August-specific monthly case counts are not confirmed from snippets alone (the CDPH year-end PDF has monthly columns but the August column values are not visible in the snippet; the VBDS Annual Report provides 2024 annual totals by county but not month-specific breakdowns). However, these sources are the correct candidates for extraction — the gap is a data extraction challenge, not a source discovery gap. Additional searching is unlikely to surface sources with better August-specific granularity than the CDPH VBDS Annual Report and the westnile.ca.gov portal, which are the definitive California WNV surveillance sources.`
- Source credibility assessed sources: `46`
- Source credibility role counts: `{'excluded': 16, 'collection_support': 5, 'validation': 11, 'context': 11, 'collection': 3}`
- Source identity assessed sources: `46`
- Source identity type counts: `{'official_public_health_agency': 24, 'national_public_health_agency': 11, 'social_media': 3, 'news_media': 7, 'academic_or_peer_reviewed_source': 1}`
- Source identity warning counts: `{'search_provider_not_publisher': 46, 'publisher_from_search_metadata_unverified': 46, 'actual_publisher_unknown': 34, 'direct_target_official_fast_path_skips_source_identity': 46}`
- Source discovery method: `live_search_only`
- Disease relevance target: `West Nile virus`
- Disease relevance source status counts: `{'insufficient_text': 19, 'ambiguous_disease': 22, 'unrelated_disease': 1, 'target_disease_match': 4}`
- Disease relevance chunk status counts: `{'target_disease_match': 665, 'ambiguous_disease': 413, 'unrelated_disease': 51, 'insufficient_text': 55, 'related_context_only': 3}`
- Disease relevance record status counts: `{'ambiguous_disease': 19, 'compatible': 20}`
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
- Surveillance summary record count: `1`
- Outbreak summary record count: `0`
- Context record count: `1`
- Unclassified observation count: `1`
- Observation dataset view counts: `{'final_case_dataset': 0, 'global_outbreak_event_dataset': 0, 'regional_surveillance_dataset': 0, 'country_year_aggregate_dataset': 0, 'official_alert_dataset': 0, 'probable_case_dataset': 0, 'suspected_case_dataset': 0, 'unspecified_case_dataset': 0, 'death_dataset': 0, 'hospitalization_dataset': 0, 'zero_case_statements': 0, 'exposure_monitoring_records': 0, 'surveillance_summary_records': 1, 'outbreak_summary_records': 0, 'context_records': 1, 'non_primary_observations': 2, 'unclassified_observation_records': 1}`
- Pre-quality-gate record count: `13`
- Quarantined record count: `8`
- Pending review record count: `5`
- Non-primary observation count: `1`
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
2. `disease_intelligence_builder` - Built disease intelligence from LLM output (West Nile Virus Disease).
3. `profile_and_schema_setup` - Built active disease profile, collection schema, and source strategy (West Nile Virus Disease, generation_method=dise...
4. `executable_source_planning` - Built executable source plan with 10 planned queries; no searches were executed.
5. `query_strategy_builder` - Built 10 direct_collection search queries from the LLM evidence strategy plan.
6. `source_discovery` - Discovered 46 source candidates using live_search_only.
7. `source_dedup_and_registry` - Built source registry with 46 entries (0 duplicates dropped).
8. `source_screening` - Screened 46 sources using deterministic policy.
9. `source_critic_and_uncertainty_routing` - Critic reviewed 46 sources; 36 ready for fetch, 0 deferred, 18 flagged for human review.
10. `content_fetch_and_parse` - Built 37 fetch requests, produced 37 documents (live_fetch_enabled=True, fixture_documents_enabled=False, fixtures_lo...
11. `document_quality_check` - Quality-checked 37 documents: 30 usable, 0 partial, 0 offline stub, 0 parse deferred, 7 unusable.
12. `evidence_chunking_and_data_presence_flagging` - Chunked 30/37 documents into 1187 evidence chunks (1020 flagged as containing target data).
13. `structured_extraction` - Built 13 raw records (extraction_mode=llm_structured_output, llm_enabled=True).
14. `schema_validation_and_repair` - Validated 13 raw records: 13 validated (5 need review), 0 rejected.
15. `record_normalization` - Normalized 13/13 records (5 need review).
16. `record_linking` - Linked 13/13 normalized records into 11 candidate events.
17. `cross_source_consistency_check` - Checked 2 multi-record events; found 0 new conflicts and 37 validation results (0 events need review).
18. `quality_gate_routing` - Human review disabled; preserving review flags as audit metadata and routing to final_data_package_builder.
19. `final_data_package_builder` - Assembled hardened FinalDataPackage from current state.

## 4. 数据源分工

| Role | Source ID | Publisher / title | Credibility | Final decision | Fetch ready |
|---|---|---|---|---|---|
| context_only | src_search_75f2c3795fd4 | / West Nile death reported in California The death, in a county where high numbers of West Nile virus-positive mosquitoes and dead birds... | medium (0.5639) | include_for_content_fetch | False |
| context_only | src_search_57a4e03b15a3 | / First Illinois West Nile Virus Death of 2024 is Reported by IDPH in Lake County | needs_review (0.4712) | needs_human_review | False |
| context_only | src_search_66bbd37d9fcc | / First human neuroinvasive case of West Nile virus (WNV) in Texas ... | needs_review (0.484) | needs_human_review | False |
| context_only | src_search_abcdf3745880 | / First Human Cases of West Nile Virus Reported in Los Angeles County for 2025 – COUNTY OF LOS ANGELES | needs_review (0.4528) | needs_human_review | False |
| context_only | src_search_08a8384dc2e1 | / Health... - Sacramento-Yolo Mosquito & Vector Control District | needs_review (0.328) | needs_human_review | False |
| context_only | src_search_fbdec1bc87c7 | / Fresno County is among nine counties... - ABC30 Action News | low (0.3991) | needs_human_review | False |
| context_only | src_search_87c273c59b72 | / First human death caused by West Nile Virus in Fresno County | low (0.344) | needs_human_review | False |
| context_only | src_search_c0d70a141aca | / West Nile virus, spread by mosquitoes, claims a third life in the San Joaquin Valley - The Intersection | low (0.328) | needs_human_review | False |
| context_only | src_search_a666cd39412c | / What to know about West Nile Virus as cases increase in Northern California | low (0.4151) | needs_human_review | False |
| context_only | src_search_860d6a928e1e | / Mosquito-Borne Illnesses / Kern County, CA | low (0.328) | needs_human_review | False |
| other | src_search_bc22a2200088 | / California Tracking Increase in Diseases Spread by Mosquitoes | excluded (0.6479) | include_for_content_fetch | True |
| other | src_search_e4be88982e7e | / [PDF] 2024 Year-end Monthly Summary Report of Selected ... - CDPH | excluded (0.5352) | include_for_content_fetch | True |
| other | src_search_ba887a60c89b | / California Sets Record for West Nile Virus Activity - CDPH | excluded (0.6479) | include_for_content_fetch | True |
| other | src_search_6f9cdd03f6b0 | / Dengue - CDPH - CA.gov | excluded (0.5608) | exclude | False |
| other | src_search_880439788e37 | / California State of Public Health Full Report 2024 | excluded (0.6063) | include_for_content_fetch | True |
| other | src_search_0b5d8dbbd871 | / News Releases 2024 - CDPH - CA.gov | high (0.6112) | include_for_content_fetch | True |
| other | src_search_0297991a455b | / West Nile Virus - CDPH - CA.gov | excluded (0.5768) | include_for_content_fetch | True |
| other | src_search_40e1767f9183 | / News Releases 2017 - CDPH - CA.gov | high (0.5928) | include_for_content_fetch | True |
| other | src_search_d879ecf59b5b | Centers for Disease Control and Prevention / Historic Data (1999-2025) / West Nile Virus / CDC | medium (0.6176) | include_for_content_fetch | True |
| other | src_search_0a4aa71e9362 | Centers for Disease Control and Prevention / [PDF] West Nile Virus Surveillance and Control Guidelines / CDC | medium (0.636) | include_for_content_fetch | True |
| other | src_search_d2d74c964ac6 | Centers for Disease Control and Prevention / Data and Maps for West Nile / West Nile Virus / CDC | medium (0.6016) | include_for_content_fetch | True |
| other | src_search_33137ddb1958 | Centers for Disease Control and Prevention / Current Year Data (2026) / West Nile Virus / CDC | medium (0.6176) | include_for_content_fetch | True |
| other | src_search_3b0cf6d737fc | Centers for Disease Control and Prevention / CDC Science Clips - Public Health Genomics and Precision Health ... | medium (0.6016) | include_for_content_fetch | True |
| other | src_search_8ff31ebb8264 | Centers for Disease Control and Prevention / CDC Science Clips - Public Health Genomics and Precision Health ... | medium (0.6016) | include_for_content_fetch | True |
| other | src_search_d25517dc4216 | Centers for Disease Control and Prevention / MMWR, Volume 73, Issue 21 — May 30, 2024 | medium (0.636) | include_for_content_fetch | True |
| other | src_search_65b7f3632065 | Centers for Disease Control and Prevention / West Nile Virus - CDC | medium (0.6016) | include_for_content_fetch | True |
| other | src_search_3bebe5502dfd | / L.A. County reports first West Nile virus death this year - Los Angeles Times | excluded (0.6823) | include_for_content_fetch | True |
| other | src_search_5c954f0581ec | / LISTING OF DEPARTMENT OF PUBLIC HEALTH PRESS RELEASES | high (0.5768) | include_for_content_fetch | True |
| other | src_search_5d796f40b9b1 | / West Nile Virus Activity 2024 - Greater Los Angeles County Vector Control District | medium (0.6112) | include_for_content_fetch | True |
| other | src_search_0d4e7ec87258 | / Health officials report 3 West Nile virus deaths; warn of mosquito-spread illnesses - ABC News | high (0.7928) | include_for_content_fetch | True |
| other | src_search_fc3322f3069f | / Westnile.ca.gov / California West Nile Virus Website | excluded (0.6479) | include_for_content_fetch | True |
| other | src_search_2e488c45a73e | / West Nile Virus Activity in California | excluded (0.6479) | include_for_content_fetch | True |
| other | src_search_4f8e542dc010 | / West Nile virus (WNV) Activity - Alameda County Mosquito Abatement District | medium (0.772) | include_for_content_fetch | True |
| other | src_search_ade4b3df439a | / [PDF] CDPH Vector-Borne Disease Section Annual Report 2024 | excluded (0.5352) | include_for_content_fetch | True |
| other | src_search_7f4a3e46c1d4 | Centers for Disease Control and Prevention / [PDF] West Nile virus and other nationally notifiable arboviruses | excluded (0.5008) | include_for_content_fetch | True |
| other | src_search_14d0fc5d0793 | / Westnile.ca.gov / California West Nile Virus Website | excluded (0.6479) | include_for_content_fetch | True |
| other | src_search_be9523f722c4 | / St. Louis Encephalitis Virus - California West Nile Virus - CA.gov | high (0.8431) | include_for_content_fetch | True |
| other | src_search_4c3e4b64e0ff | / [PDF] VBDS Annual Report, 2023 - California West Nile Virus | excluded (0.5879) | include_for_content_fetch | True |
| other | src_search_605afafe9104 | / [PDF] California Mosquito-Borne Virus Surveillance and Response Plan | excluded (0.5879) | include_for_content_fetch | True |
| other | src_search_071605a69e2e | / California Tracking Increase in Diseases Spread by Mosquitoes | high (0.6663) | include_for_content_fetch | True |
| other | src_search_e48597594966 | / [PDF] 8/21/2023 Increasing West Nile Virus Activity | excluded (0.5352) | include_for_content_fetch | True |
| other | src_search_c95b5eedc56a | CIDRAP / West Nile death reported in California / CIDRAP | excluded (0.6759) | include_for_content_fetch | True |
| other | src_search_cb36ac8997e4 | / Riverside County Reports First Human Case of West Nile this Year / Riverside University Health System | high (0.5928) | include_for_content_fetch | True |
| other | src_search_e5ba83f1bd09 | Centers for Disease Control and Prevention / [PDF] Current Year Data (2024) / West Nile Virus - CDC Stacks | medium (0.636) | include_for_content_fetch | True |
| other | src_search_6e4f8ca1b1cc | Centers for Disease Control and Prevention / West Nile Virus and Other Nationally Notifiable Arboviral Diseases | medium (0.6016) | include_for_content_fetch | True |
| other | src_search_5ecab69111e7 | Centers for Disease Control and Prevention / West Nile Virus and Other Nationally Notifiable Arboviral Diseases | medium (0.6016) | include_for_content_fetch | True |

## 5. 真实网页抓取结果

- Documents fetched/parsed: `37`
- Search-derived sources selected for fetch: `37`
- Search-derived skipped by reason: `{}`
- Fetch status counts: `fetch_failed=2, fetched=35`
- External fetch enabled: `True`
- Fetch provider counts: `native_requests=2, tavily_extract=35`
- External fetch failure counts: `native_requests=2, tavily_extract=2`
- Selected fetch bucket counts: `target_official_authority=37`
- Parser status counts: `fetch_failed=2, parsed_text=35`
- Parser used counts: `text_parser=35, unknown=2`
- Quality status counts: `unusable=7, usable=30`
- Validation-reserved skipped from fetch: `[]`

| Source ID | Provider | Fetch status | HTTP | Parse | Parser | Quality | Text chars | Tables |
|---|---|---|---|---|---|---|---|---|
| src_search_be9523f722c4 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 16022 | 0 |
| src_search_bc22a2200088 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 130194 | 0 |
| src_search_ba887a60c89b | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 128205 | 0 |
| src_search_14d0fc5d0793 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 10048 | 0 |
| src_search_0b5d8dbbd871 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 145355 | 0 |
| src_search_880439788e37 | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 243236 | 0 |
| src_search_40e1767f9183 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 154994 | 0 |
| src_search_4c3e4b64e0ff | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 104221 | 0 |
| src_search_605afafe9104 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 119553 | 0 |
| src_search_0297991a455b | native_requests | fetch_failed | none | fetch_failed | none | unusable | 0 | 0 |
| src_search_6f9cdd03f6b0 | native_requests | fetch_failed | none | fetch_failed | none | unusable | 0 | 0 |
| src_search_ade4b3df439a | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 94027 | 0 |
| src_search_e4be88982e7e | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 33323 | 0 |
| src_search_7f4a3e46c1d4 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 5584 | 0 |
| src_search_c95b5eedc56a | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 11876 | 0 |
| src_search_071605a69e2e | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 25749 | 0 |
| src_search_0a4aa71e9362 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 140637 | 0 |
| src_search_d25517dc4216 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 142594 | 0 |
| src_search_d879ecf59b5b | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 2251 | 0 |
| src_search_33137ddb1958 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 1581 | 0 |
| src_search_d2d74c964ac6 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 2067 | 0 |
| src_search_3b0cf6d737fc | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 72228 | 0 |
| src_search_8ff31ebb8264 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 84005 | 0 |
| src_search_65b7f3632065 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 1817 | 0 |
| src_search_cb36ac8997e4 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 23715 | 0 |
| src_search_e48597594966 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 5499 | 0 |
| src_search_0d4e7ec87258 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 7034 | 0 |
| src_search_4f8e542dc010 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 4638 | 0 |
| src_search_3bebe5502dfd | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 21172 | 0 |
| src_search_fc3322f3069f | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 10078 | 0 |
| src_search_2e488c45a73e | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 18714 | 0 |
| src_search_e5ba83f1bd09 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 10221 | 0 |
| src_search_5d796f40b9b1 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 6296 | 0 |
| src_search_6e4f8ca1b1cc | tavily_extract | fetched | 200 | parsed_text | text_parser | unusable | 34115 | 0 |
| src_search_5ecab69111e7 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 24409 | 0 |
| src_search_5c954f0581ec | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 6003 | 0 |
| src_search_75f2c3795fd4 | tavily_extract | fetched | 200 | parsed_text | text_parser | usable | 23597 | 0 |

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
- Stop reason: `Maximum iterations (2) reached. The search has surfaced a strong, multi-layered set of authoritative source candidates: (1) The CDPH VBDS Annual Report 2024 (westnile.ca.gov/pdfs/VBDSAnnualReport24.pdf) — the highest-authority source, providing county-level WNV case incidence for 2024 across all California counties, enabling population of subnational_location, locality, cases_confirmed, and date_reported fields; (2) CDPH News Release NR24-27 (cdph.ca.gov/Programs/OPA/Pages/NR24-27.aspx) — reporting 63 human WNV cases and 6 deaths for 2024, with evidence quote potential; (3) CDPH 2024 Year-End Monthly Summary PDF (cdph.ca.gov) — providing WNV case type breakdowns (neuroinvasive: 103, non-neuroinvasive: 30, asymptomatic: 20, total: 153) with monthly columns; (4) Greater Los Angeles County Vector Control District 2024 activity page (glamosquito.org) — providing locality-level August 2024 mosquito pool data with specific dates (8/7/2024, 8/22/2024, 8/29/2024) and neighborhood-level granularity; (5) contracosta.news article (2024-10-01) republishing CDPH figures (63 cases, 6 deaths) with evidence quote; (6) CDC Historic Data page (cdc.gov/west-nile-virus/data-maps/historic-data.html) — ArboNET state-level data for cross-validation; (7) kernpublichealth.com, ruhealth.org, nevadacountyca.gov — county-level public health sources for Kern, Riverside, and Nevada counties. Key remaining gap: August-specific monthly case counts are not confirmed from snippets alone (the CDPH year-end PDF has monthly columns but the August column values are not visible in the snippet; the VBDS Annual Report provides 2024 annual totals by county but not month-specific breakdowns). However, these sources are the correct candidates for extraction — the gap is a data extraction challenge, not a source discovery gap. Additional searching is unlikely to surface sources with better August-specific granularity than the CDPH VBDS Annual Report and the westnile.ca.gov portal, which are the definitive California WNV surveillance sources.`
- Query source counts: `{'iterative_llm_initial_search_plan': 4, 'iterative_llm_refinement': 4}`
- Iteration query counts: `{'1': 4, '2': 4}`

### 6.2 LLM Source Critic

- Attempted source count: `0`
- Assessed source count: `0`
- Skipped source count: `46`
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
- Assessed source count: `46`
- Final role counts: `collection=3, collection_support=5, context=11, excluded=16, validation=11`
- Risk flag counts: `AMBIGUOUS_DISEASE_IN_METADATA: disease_relevance_score=0.20; no target WNV disease terms confirmed in indexed metadata despite title implying WNV content — verify full document text=1, COLLECTION_SPEC_INHERITANCE_WARNING: task input warnings note extraction_record_model_still_hantavirus_named — confirm schema is WNV-appropriate before any ingestion from this or any source=1, CONTEXT_ROLE_ONLY: if retained, source should be used exclusively as contextual background, not as a direct collection record; no required_fields should be populated from this source as primary evidence=1, CRITICAL_YEAR_MISMATCH: URL and title explicitly reference 2025; collection window is 2024-08-01 to 2024-08-31 — source cannot be primary collection target=1, DISEASE_SCORING_PIPELINE_DISAGREEMENT: Title explicitly names West Nile Virus but deterministic disease_relevance_score=0.20 with no target disease terms found — scoring pipeline likely failed to parse title or lacked snippet content; manual verification of disease relevance warranted=1, GEOGRAPHIC_GRANULARITY_CONCERN: source is county-level (LA County) but flagged 'national_or_international_granularity' — flag may be misapplied; verify granularity scoring logic=1, GEOGRAPHIC_MISMATCH: Source reports Illinois (Lake County) data; collection task targets California — no extractable California data=1, MISSING_PUBLISHER: Publisher field is null; minor provenance gap mitigated by authoritative .gov domain=1, MISSING_PUBLISHER: publisher field is null; reduces provenance traceability despite known domain authority=1, NO_EXTRACTABLE_COLLECTION_DATA: Source cannot populate any required_fields (cases_confirmed, cases_probable, deaths, hospitalizations, subnational_location=California, etc.) for the target task=1, QUERY_BLEED: Source was surfaced by a California-targeted query but contains no California content; indicates search result false positive=1, ROLE_CONFLICT_IN_FLAGS: flags simultaneously assert 'primary_or_authoritative_source' and 'secondary_news_or_media_source' — contradictory classification requires resolution=1, ROLE_DOWNGRADE: Deterministic pipeline correctly downgraded from collection_support to context, but LLM advisory confirms this source cannot contribute to required_fields for California=1, SCREENING_AND_CRITIC_DISAGREE: role_hint=collection_support vs. final role=context; internal pipeline disagreement on source utility=1, SCREENING_CRITIC_DISAGREEMENT: deterministic flags contain 'screening_and_critic_disagree' — internal scoring conflict requires LLM or human adjudication before role finalization=1, SOURCE_TYPE_LOWEST_PRIORITY: news_and_situation_report is the lowest tier in collection spec source_priority hierarchy; should not substitute for CDPH VBDS weekly reports or ArboNET=1, SOURCE_TYPE_LOW_PRIORITY: Classified as news_and_situation_report — lowest tier in collection spec source_priority hierarchy=1, TEMPORAL_DISQUALIFICATION_FOR_DIRECT_COLLECTION: 2025-dated document cannot contain in-window 2024 August data as primary subject; any 2024 figures would be retrospective/incidental only=1, agency_credible_but_channel_informal=1, aggregator_or_republisher_suspected=1, ambiguous_disease=42, ambiguous_disease_signal_in_source_metadata=22, complete_source_provenance=12, context_or_background_only=13, data_signal_in_source_metadata=46, data_signal_unverifiable_from_metadata=1, disease_relevance_unclear=19, facebook_post_not_citable_as_primary_source=1, geographic_mismatch_title_references_texas_not_california=1, independence_unclear=7, local_or_subnational_granularity=15, local_source_matches_task_location=15, location_match_from_planned_query=31, low_authority_relevant_source=1, low_machine_readability=7, machine_readable_or_structured=11, missing_publisher=34, national_or_international_granularity=31, no_snippet_available_for_content_verification=1, null_snippet_prevents_evidence_extraction=1, official_public_health_authority=39, pdf_or_report_likely_medium_readability=7, potential_death_signal_in_title_unconfirmed=1, primary_or_authoritative_source=39, primary_source_pointer_only=1, screening_and_critic_disagree=10, screening_and_critic_disagree_requires_review=1, secondary_news_or_media_source=9, social_media_delivery_channel=1, source_disease_relevance:ambiguous_disease=22, source_disease_relevance:insufficient_text=19, source_disease_relevance:target_disease_match=4, source_disease_relevance:unrelated_disease=1, source_metadata_matches_requested_disease=4, source_time_matches_requested_window=12, standard_web_page=28, time_window_match_from_planned_query=34, title_content_misaligned_with_collection_geography=1, unrelated_disease_signal_in_source_metadata=1, verbatim_quote_extraction_not_feasible=1`
- LLM assessed count: `4`
- LLM failure count: `0`
- Needs review count: `9`

### 6.3.5 Source Identity / Publisher Assessment

- Identity assessed source count: `46`
- LLM identity assessed source count: `0`
- Post-fetch identity assessed source count: `37`
- Unknown publisher count: `33`
- Source type counts: `academic_or_peer_reviewed_source=1, national_public_health_agency=11, news_media=7, official_public_health_agency=24, social_media=3`
- Claim support role counts: `corroboration_support=7, insufficient_information=4, primary_case_claim_support=35`
- Fetch use counts: `fetch_for_extraction=42, fetch_only_after_review=4`
- Warning counts: `actual_publisher_unknown=34, direct_target_official_fast_path_skips_source_identity=46, publisher_from_search_metadata_unverified=46, search_provider_not_publisher=46`

### 6.4 LLM Structured Extraction

- Extraction mode: `llm_structured_output`
- Eligible chunk count: `1172`
- LLM call count: `30`
- LLM success count: `30`
- LLM error count: `0`
- Raw record count: `13`

## 7. 最终抽取 records

- Normalized record count: `13`
- Run quality status: `no_primary_case_dataset_records`
- Final dataset mode: `task_aware_quality_gated_records`
- Quality-gated accepted final dataset count: `0`
- Final case dataset count: `0`
- Zero-case statement count: `0`
- Exposure-monitoring record count: `0`
- Surveillance summary record count: `1`
- Outbreak summary record count: `0`
- Context record count: `1`
- Unclassified observation count: `1`
- Observation dataset view counts: `{'final_case_dataset': 0, 'global_outbreak_event_dataset': 0, 'regional_surveillance_dataset': 0, 'country_year_aggregate_dataset': 0, 'official_alert_dataset': 0, 'probable_case_dataset': 0, 'suspected_case_dataset': 0, 'unspecified_case_dataset': 0, 'death_dataset': 0, 'hospitalization_dataset': 0, 'zero_case_statements': 0, 'exposure_monitoring_records': 0, 'surveillance_summary_records': 1, 'outbreak_summary_records': 0, 'context_records': 1, 'non_primary_observations': 2, 'unclassified_observation_records': 1}`
- Pre-quality-gate record count: `13`
- Quarantined record count: `8`
- Pending review record count: `5`
- Non-primary observation count: `1`
- Final dataset post-review count: `0`
- Primary-case dataset status: `no_primary_case_dataset_records`
- Recommended primary dataset message: `No primary case dataset records were accepted; inspect zero-case, exposure-monitoring, context, and other observation views.`
- Primary-case eligible accepted count: `0`
- Corroborated primary case event count: `0`
- Record inclusion status counts: `{'quarantined_outside_scope': 8, 'pending_human_review': 5}`
- Run quality warnings: `['no_primary_case_dataset_records', 'no_corroborated_primary_case_events']`
- Accepted source counts: `none`

No quality-gated records are available to list.
Candidate records, if any, are recorded in the pre-quality, quarantined, and pending-review artifacts.

| Record ID | Date / period | Location | Cases | Deaths | Source | LLM used |
|---|---|---|---|---|---|---|

## 8. Validation 对比

### Claim-level corroboration

- Claim count: `13`
- Claim comparison count: `78`
- Corroborated event count: `9`
- Corroborated primary case event count: `0`
- Observation type counts: `ambiguous_public_health_observation=1, death_record=7, unspecified_case_record=5`
- Corroboration status counts: `conflicting_claims=1, insufficient_information=1, single_source_unverified=7`

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

- Human review item count: `74`
- Evaluation review flag count: `0`
- Anomaly review item count: `8`

| Review ID | Type | Related IDs | Reason |
|---|---|---|---|
| review_source_credibility_src_search_0b5d8dbbd871 | source_credibility | src_search_0b5d8dbbd871 | missing_publisher |
| review_source_src_search_0b5d8dbbd871 | source_screening | src_search_0b5d8dbbd871 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_40e1767f9183 | source_credibility | src_search_40e1767f9183 | missing_publisher |
| review_source_src_search_40e1767f9183 | source_screening | src_search_40e1767f9183 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_5c954f0581ec | source_credibility | src_search_5c954f0581ec | missing_publisher |
| review_source_src_search_5c954f0581ec | source_screening | src_search_5c954f0581ec | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_src_search_75f2c3795fd4 | source_screening | src_search_75f2c3795fd4 | Screening and critic disagree on this source; routing to human review for resolution. |
| review_source_credibility_src_search_0d4e7ec87258 | source_credibility | src_search_0d4e7ec87258 | missing_publisher |
| review_source_src_search_0d4e7ec87258 | source_screening | src_search_0d4e7ec87258 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_4f8e542dc010 | source_credibility | src_search_4f8e542dc010 | missing_publisher |
| review_source_src_search_4f8e542dc010 | source_screening | src_search_4f8e542dc010 | Source classified as data_source; both screening and critic agree to include for content fetch. |
| review_source_credibility_src_search_57a4e03b15a3 | source_credibility | src_search_57a4e03b15a3 | This source is an official Illinois Department of Public Health (IDPH) press release reporting the first West Nile virus death of 2024 in... |

## 9.5 Stage 11 anomaly detection and review application

- Anomaly result count: `15`
- Anomaly severity counts: `high=8, low=7`
- Anomaly needs-human-review count: `8`
- Decisions provided: `0`
- Decisions applied: `0`
- Decisions rejected: `0`
- Audit entries: `0`
- Final dataset post-review count: `0`
- Records excluded by review: `0`

| Anomaly ID | Type | Severity | Target | Reason |
|---|---|---|---|---|
| anom_001 | deaths_without_case_reference | low | rec_src_search_5c954f0581ec_001 | deaths present but no comparable case count is available |
| anom_002 | deaths_without_case_reference | low | rec_src_search_0d4e7ec87258_002 | deaths present but no comparable case count is available |
| anom_003 | deaths_without_case_reference | low | rec_src_search_0d4e7ec87258_003 | deaths present but no comparable case count is available |
| anom_004 | deaths_without_case_reference | low | rec_src_search_ba887a60c89b_004 | deaths present but no comparable case count is available |
| anom_005 | deaths_without_case_reference | low | rec_src_search_14d0fc5d0793_002 | deaths present but no comparable case count is available |
| anom_006 | deaths_without_case_reference | low | rec_src_search_14d0fc5d0793_003 | deaths present but no comparable case count is available |
| anom_007 | deaths_without_case_reference | low | rec_src_search_071605a69e2e_001 | deaths present but no comparable case count is available |
| anom_008 | out_of_scope_count_bearing_record | high | event_001 | Stage 10 validation marked record outside requested scope: outside_geography |
| anom_009 | out_of_scope_count_bearing_record | high | event_007 | Stage 10 validation marked record outside requested scope: outside_geography |
| anom_010 | out_of_scope_count_bearing_record | high | event_006 | Stage 10 validation marked record outside requested scope: outside_geography;outside_time_window |
| anom_011 | out_of_scope_count_bearing_record | high | event_011 | Stage 10 validation marked record outside requested scope: insufficient_scope_information;outside_geography |
| anom_012 | out_of_scope_count_bearing_record | high | event_002 | Stage 10 validation marked record outside requested scope: outside_time_window |

| Applied decision | Type | Target | Audit IDs | Reason |
|---|---|---|---|---|

## 10. 输出文件

- Run output directory: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_west_nile_california_2024_08`
- Collection final dataset: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_west_nile_california_2024_08\collection\final_dataset.csv`
- Collection final case dataset: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_west_nile_california_2024_08\collection\final_case_dataset.csv`
- Collection zero-case statements: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_west_nile_california_2024_08\collection\zero_case_statements.csv`
- Collection exposure-monitoring records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_west_nile_california_2024_08\collection\exposure_monitoring_records.csv`
- Collection surveillance summaries: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_west_nile_california_2024_08\collection\surveillance_summary_records.csv`
- Collection outbreak summaries: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_west_nile_california_2024_08\collection\outbreak_summary_records.csv`
- Collection context records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_west_nile_california_2024_08\collection\context_records.csv`
- Collection unclassified observations: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_west_nile_california_2024_08\collection\unclassified_observation_records.csv`
- Collection observation dataset summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_west_nile_california_2024_08\collection\observation_type_dataset_summary.json`
- Collection pre-quality-gate records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_west_nile_california_2024_08\collection\final_dataset_pre_quality_gate.csv`
- Collection quarantined records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_west_nile_california_2024_08\collection\quarantined_records.csv`
- Collection pending review records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_west_nile_california_2024_08\collection\pending_review_records.csv`
- Collection non-primary observations: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_west_nile_california_2024_08\collection\non_primary_observations.csv`
- Collection record inclusion decisions: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_west_nile_california_2024_08\collection\record_inclusion_decisions.json`
- Collection final dataset post-review: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_west_nile_california_2024_08\collection\final_dataset_post_review.csv`
- Collection anomaly results: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_west_nile_california_2024_08\collection\anomaly_results.json`
- Collection human review audit trail: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_west_nile_california_2024_08\collection\human_review_audit_trail.json`
- Collection source registry: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_west_nile_california_2024_08\collection\source_registry.json`
- Validation mode: `diagnostic_only`
- Validation records source: `state`
- Validation records output: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_west_nile_california_2024_08\validation\ground_truth_records.csv`
- Inactive validation records: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_west_nile_california_2024_08\validation\inactive_validation_records.csv`
- Validation compatibility summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_west_nile_california_2024_08\validation\validation_source_compatibility_summary.json`
- Evaluation report CSV: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_west_nile_california_2024_08\evaluation\evaluation_report.csv`
- Human-readable report: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_west_nile_california_2024_08\workflow_run_report_chinese.md`

## 11. 当前结论

This workflow run executed the configured data collection workflow through the exported graph and artifact pipeline. The user-facing run status is: COMPLETED WITH NO PRIMARY CASE DATASET RECORDS: workflow completed, but no primary case records were accepted into final_dataset.
The run completed technically, but it should not be read as a successful data collection result because no quality-gated accepted records were produced.

- Package metadata says LLM used: `True`
- Contains synthetic fixture data: `False`
- Generated at UTC: `2026-06-25T21:38:31.152960+00:00`

## 12. Workflow visualization artifacts

- Workflow visualization index: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_west_nile_california_2024_08\workflow_visualization\index.html`
- Workflow timeline: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_west_nile_california_2024_08\workflow_visualization\workflow_timeline.html`
- Evidence flow graph: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_west_nile_california_2024_08\workflow_visualization\evidence_flow_graph.html`
- Claim comparison cards: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_west_nile_california_2024_08\workflow_visualization\claim_comparison_cards.html`
- Dataset decision flow: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_west_nile_california_2024_08\workflow_visualization\dataset_decision_flow.html`
- Human review workflow visualization: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_west_nile_california_2024_08\workflow_visualization\human_review_workflow.html`
- Visualization summary: `C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow\outputs\sessions\goal_round07_west_nile_california_2024_08\workflow_visualization\workflow_visualization_summary.json`
