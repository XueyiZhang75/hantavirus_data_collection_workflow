# Current State Audit

## 1. Repository overview

The repository currently contains:

- `README.md`: current implementation status, offline/live run notes, and historical step descriptions.
- `configs/`: a JSONC runtime profile, currently `configs/hdc_workflow_run_config.jsonc`.
- `scripts/`: current operational scripts for configured runs, Studio startup, Studio checks, initial-state printing, and workflow console generation.
- `src/hdc_workflow/`: the internal Python package containing the LangGraph graph, typed state/models, config loaders, LLM helpers, runtime profile helpers, node implementations, source-planning/source-critic agent helpers, resources, and export/evaluation helpers.
- `tests/`: offline deterministic tests for graph behavior, models, Studio setup, config loading, New Mexico HPS case behavior, guardrails, and evaluation reporting.
- `docs/`: workflow design/runbook material and the Stage 0 audit documents.
- `langgraph.json`: LangGraph Studio config mapping `hantavirus_data_collection_workflow` to `./src/hdc_workflow/studio_app.py:graph`.
- `archive/`: legacy demo/pilot assets moved out of the main operational scripts.

## 2. Current implemented capabilities

The current graph is built in `src/hdc_workflow/graph.py`. It is a serial LangGraph `StateGraph` with one conditional edge after `quality_gate_routing`. The graph nodes are:

1. `task_intake_and_scope_planning`
2. `hantavirus_profile_and_schema_setup`
3. `query_strategy_builder`
4. `source_discovery`
5. `source_dedup_and_registry`
6. `source_screening`
7. `source_critic_and_uncertainty_routing`
8. `content_fetch_and_parse`
9. `document_quality_check`
10. `evidence_chunking_and_data_presence_flagging`
11. `structured_extraction`
12. `schema_validation_and_repair`
13. `record_normalization`
14. `record_linking`
15. `cross_source_consistency_check`
16. `quality_gate_routing`
17. `human_review` when review is required
18. `final_data_package_builder`

Current implemented capabilities include:

- Graph / workflow skeleton: `src/hdc_workflow/graph.py` wires the inspectable LangGraph node sequence and route to `human_review` when the quality gate requests it.
- Task intake: `src/hdc_workflow/nodes/task_scope.py` builds a deterministic `CollectionSpec`, but currently with fixed hantavirus assumptions.
- Disease profile and schema setup: `hantavirus_profile_and_schema_setup` loads static hantavirus profile/schema/source strategy resources.
- Source discovery: `src/hdc_workflow/nodes/source_discovery.py` loads an offline seed source catalog and creates source candidates with discovery provenance.
- Source screening / source critic: `src/hdc_workflow/nodes/source_screening.py` performs deterministic screening, source-role routing, validation-reserved overrides, optional LLM source critic, and current source credibility fields.
- Content fetch / parse: `src/hdc_workflow/nodes/content_processing.py` builds fetch requests, defaults to offline stubs, supports fixture documents, and performs opt-in live HTML/text fetch when `HDC_ENABLE_LIVE_FETCH=true`; PDF parsing is deferred.
- Evidence chunking: `evidence_chunking_and_data_presence_flagging` chunks usable/partial documents and annotates target-data/context signals while suppressing context-only sources from extraction.
- Structured extraction: `src/hdc_workflow/nodes/extraction.py` supports deterministic rule-based extraction and optional LLM extraction controlled by `HDC_ENABLE_LLM_EXTRACTION`.
- Schema validation and repair: the extraction node validates `HantavirusRecord` records, applies deterministic repair, verifies provenance, and queues review items when required.
- Normalization: `src/hdc_workflow/nodes/normalization.py` normalizes country, subnational, date, virus/syndrome, case definition, source type, and numeric fields.
- Record linking: `src/hdc_workflow/nodes/linking_validation.py` groups normalized records into linked events using disease, virus/syndrome, geography, date anchor, and semantic count fields.
- Cross-source consistency: the same module compares records within linked events and creates conflict/review outputs when comparable records disagree.
- Human review packet: `src/hdc_workflow/nodes/human_review.py` builds review packets and records supplied human decisions, but does not modify final records or resolve conflicts.
- Final data package export: `src/hdc_workflow/nodes/finalization.py` builds the final package; `src/hdc_workflow/export.py` writes package JSON/CSV artifacts.
- Optional LLM structured extraction: `src/hdc_workflow/llm_clients.py` and `src/hdc_workflow/nodes/extraction.py` support Anthropic/OpenAI-style model calls behind environment flags.
- Controlled live-source pilot / configured run: `scripts/run_hdc_workflow_configured.py` loads the runtime profile, runs the graph, exports collection/validation/evaluation/diagnostics/report/HTML console artifacts.
- Semantic guardrails: `src/hdc_workflow/nodes/extraction.py`, `normalization.py`, and `linking_validation.py` include semantic fields and enum/date/geography canonicalization to reduce real-world LLM output drift.

## 3. Current hantavirus-specific assumptions

| File | Function / component | Evidence | Why this blocks disease-generic behavior | Future-stage action |
|---|---|---|---|---|
| `src/hdc_workflow/nodes/task_scope.py` | `task_intake_and_scope_planning` | Sets `disease="Hantavirus disease"` and `data_focus="human hantavirus case, outbreak, and surveillance data"` | User disease input is not yet parsed into a generic disease spec. | Stage 1 structured task input and disease decoupling. |
| `src/hdc_workflow/nodes/task_scope.py` | `hantavirus_profile_and_schema_setup` | Function name and trace node are hantavirus-specific; loads `load_hantavirus_profile()` and `load_hantavirus_collection_schema()` | The graph profile/schema step cannot dynamically load disease-specific profiles. | Stage 3 generic profile/schema setup. |
| `src/hdc_workflow/config.py` | Config loaders | Functions include `load_hantavirus_profile`, `load_hantavirus_collection_schema`, `load_hantavirus_seed_sources`, `load_hantavirus_fixture_documents` | Resource loading is tied to hantavirus resource files. | Add disease-neutral profile/schema/catalog loaders while preserving old compatibility names. |
| `src/hdc_workflow/resources/hantavirus_profile.json` | Disease profile resource | Resource is explicitly a hantavirus profile | No equivalent dynamic disease intelligence layer exists for other diseases. | Stage 2 disease intelligence layer. |
| `src/hdc_workflow/resources/hantavirus_collection_schema.json` | Collection schema resource | Schema is for hantavirus human case/outbreak fields | Target fields are not derived from the user's disease/task. | Stage 3 generic profile/schema setup. |
| `src/hdc_workflow/resources/source_strategy.json` | Source strategy resource | Screening criteria mention hantavirus, HPS, HFRS, or named hantaviruses | Source categories and criteria do not change for COVID-19, dengue, or other diseases. | Stage 4 LLM executable source planning. |
| `src/hdc_workflow/resources/hantavirus_seed_sources.json` | Seed source catalog | Contains CDC/WHO/ECDC/PAHO/PubMed/Europe PMC/OpenAlex hantavirus seeds and `seed://...hantavirus...` placeholders | The source universe is a fixed hantavirus catalog. | Stage 5 real source discovery/search provider. |
| `src/hdc_workflow/resources/live_case_studies/new_mexico_hps_seed_sources.json` | Live case-study sources | Contains NMDOH HPS source IDs and New Mexico-specific URLs | The current live profile is a narrowed case study, not generic source discovery. | Keep as a case-study fixture/profile; add generic profile generation later. |
| `src/hdc_workflow/resources/live_case_studies/new_mexico_hps_source_role_policy_overlay.json` | Source role overlay | Defines New Mexico HPS collection/context/validation source roles | Source split is manually fixed for this profile. | Stage 6 generic source credibility and role assignment. |
| `src/hdc_workflow/models.py` | `HantavirusRecord` and `FinalDataPackage.final_dataset` | The primary record class is named `HantavirusRecord` | The data model name and assumptions are disease-specific even if many fields are reusable. | Stage 8 generic record schema and normalization. |
| `src/hdc_workflow/nodes/extraction.py` | `_standardize_disease` | Always forces disease to canonical `"Hantavirus disease"` | LLM/rule output for other diseases would be overwritten. | Stage 7/8 extraction and generic record schema generalization. |
| `src/hdc_workflow/nodes/extraction.py` | Hard-coded terms | Contains disease-level terms such as `hantavirus`, `hantavirus disease`, `orthohantavirus` | Extraction guardrails are disease-specific. | Move disease vocabulary to disease intelligence/profile layer. |
| `src/hdc_workflow/agents/source_planning_agent.py` | Advisory planner context | Imports `load_hantavirus_seed_sources()` and defaults disease to `"Hantavirus disease"` | LLM planning is anchored to the known hantavirus seed catalog. | Stage 4 LLM executable source planning. |
| `configs/hdc_workflow_run_config.jsonc` | Runtime profile | `user_request` is hantavirus/New Mexico and overlays point to `new_mexico_hps_*` resources | Configured product run is a New Mexico HPS profile, not a generic user task runner. | Stage 1/12 structured user input and CLI/notebook. |
| `tests/` | Test fixtures | Many tests assert `Hantavirus disease`, HPS, New Mexico, and hantavirus source IDs | Tests protect current behavior but do not cover non-hantavirus behavior. | Add multi-disease tests in later stages without breaking current fixtures. |

## 4. Current fixed-catalog / non-searching assumptions

| File | Function / component | Evidence | Current behavior | Why this blocks final source discovery target | Future-stage action |
|---|---|---|---|---|---|
| `src/hdc_workflow/nodes/source_discovery.py` | Module docstring and `_DISCOVERY_METHOD` | Docstring says offline seed catalog, no network; `_DISCOVERY_METHOD = "offline_seed_catalog"` | Loads fixed seed sources and creates candidates without external search. | Final target requires real source discovery beyond fixed catalogs. | Stage 5 real source discovery/search provider. |
| `src/hdc_workflow/nodes/source_discovery.py` | `source_discovery` | Calls `load_hantavirus_seed_sources()` | Candidate sources come from the static catalog and overlay. | New sources cannot be discovered unless they are pre-added to catalog/overlay. | Add executable search result ingestion. |
| `src/hdc_workflow/agents/source_planning_agent.py` | `_build_user_payload` | Sets `"network_policy": "Do not perform broad web search or fetch URLs."` | LLM planning can propose queries/hints but cannot execute search. | Planning does not produce real search results or new fetched sources. | Stage 4 creates executable query plan; Stage 5 executes it. |
| `src/hdc_workflow/resources/source_planning_agent_prompt.json` | Prompt rules | Rule says `Do not perform broad web search.` | LLM source planning is advisory and constrained. | The final workflow needs controlled real discovery, not advisory-only hints. | Replace with search-provider-aware planning later. |
| `configs/hdc_workflow_run_config.jsonc` | `source_sets.workflow_source_ids` | Fixed allowlist contains six New Mexico/CDC source IDs | Configured live run only processes allowlisted source IDs. | Runtime cannot expand sources from search results. | Stage 5/6 search result selection and role assignment. |
| `src/hdc_workflow/nodes/content_processing.py` | `_parse_source_id_allowlist` and skip logic | Reads `HDC_SOURCE_ID_ALLOWLIST`; skips sources not in allowlist | Live fetch is controlled by source ID allowlist. | Good safety guardrail, but not a discovery mechanism. | Keep allowlist as guardrail; add source discovery before allowlist/fetch. |
| `src/hdc_workflow/resources/live_case_studies/new_mexico_hps_*` | Case-study overlays | Fixed NMDOH/CDC HPS source sets | Profile-specific sources are curated by hand. | Cannot generalize to COVID-19/dengue without hand-built overlays. | Use as fixtures/acceptance cases; add dynamic source generation. |
| `src/hdc_workflow/resources/source_role_policy.json` | Source role policy | Contains fixed validation-reserved/context source IDs | Source role policy is source-ID driven. | Role assignment needs source metadata and credibility reasoning for new sources. | Stage 6 source credibility and role assignment. |

## 5. Current live-web and LLM capabilities

Current live-web controls:

- `HDC_ENABLE_LIVE_FETCH`: enables real HTTP fetch in `content_fetch_and_parse`.
- `HDC_USE_FIXTURE_DOCUMENTS`: injects local fixture documents for deterministic offline runs.
- `HDC_SOURCE_ID_ALLOWLIST`: restricts which registered source IDs may be fetched.
- `HDC_FETCH_TIMEOUT_SECONDS`: controls HTTP timeout.
- HTML/text parsing exists; PDF parsing is currently deferred.

Current LLM controls:

- `HDC_ENABLE_LLM_SOURCE_PLANNING`: enables advisory source planning in `query_strategy_builder`.
- `HDC_ENABLE_LLM_SOURCE_CRITIC`: enables source critic assessment in `source_critic_and_uncertainty_routing`.
- `HDC_ENABLE_LLM_EXTRACTION`: enables LLM structured extraction in `structured_extraction`.
- `HDC_LLM_PROVIDER`, `HDC_LLM_MODEL`, `HDC_LLM_MAX_TOKENS`, `HDC_LLM_MAX_CHUNKS`: configure provider/model/output and chunk caps.
- `HDC_LLM_FALLBACK_TO_RULE_BASED`: controls fallback behavior.
- `HDC_LLM_SOURCE_CRITIC_SOURCE_ID_ALLOWLIST`, `HDC_LLM_SOURCE_CRITIC_MAX_SOURCES`, `HDC_LLM_SOURCE_CRITIC_REVIEW_BLOCKS_FETCH`: limit and control source critic behavior.

Current output paths:

- Configured runs write sessionized outputs under `outputs/sessions/<session_id>/`.
- Latest aliases are written under `outputs/workflow_runs/` and `outputs/workflow_console/` when enabled.
- Collection artifacts are exported under each session's `collection/`.
- Validation artifacts are exported under `validation/`.
- Evaluation artifacts are exported under `evaluation/`.
- Diagnostics are exported under `diagnostics/`.
- HTML process console is exported under `workflow_console/`.

## 6. Current validation status

Current validation exists at two levels:

- In-graph cross-source consistency: `cross_source_consistency_check` compares records within linked events. It can flag numeric/text/date conflicts and route reviewable conflicts to the human review queue.
- Configured masked-validation evaluation: `scripts/run_hdc_workflow_configured.py` reads `validation_ground_truth_records_path`, writes validation source registry artifacts, calls `build_evaluation_report`, and appends evaluation review items to output review artifacts.

Current limitations:

- Trusted-source comparison exists only in the configured run/evaluation helper path, not as a general graph-native validation node.
- Validation is tied to hand-curated ground truth CSVs such as `new_mexico_hps_ground_truth_records.csv`.
- LLM validation reasoning is not implemented.
- Validation partly explains match status in evaluation outputs, but the general graph does not yet provide a disease-generic "what is compared with what" validation model.
- Duplicate detection is currently record linking by event key; it is not yet a full duplicate clustering/event resolution system.
- Anomaly detection is not implemented.
- Human review decisions are recorded in review packets, but final records/conflicts are not modified by those decisions.

## 7. Current user experience and visualization status

Current user-facing run methods:

- `python scripts/run_hdc_workflow_configured.py`: runs the current config-driven workflow profile and exports Markdown, JSON, CSV, diagnostics, and HTML console artifacts.
- `python scripts/run_hdc_workflow_configured.py --print-config`: prints sanitized resolved config and minimal Studio input.
- `python scripts/start_hdc_workflow_studio.py`: starts LangGraph Studio using the same runtime profile environment.
- `python scripts/build_workflow_run_console.py`: builds the workflow HTML console from an existing run session.

Current visualization:

- `scripts/build_workflow_run_console.py` generates a custom HTML console from exported run artifacts.
- `langgraph.json` supports LangGraph Studio for graph/state inspection.
- Studio is useful for observing nodes/state, but the current workflow is still mostly configured and launched from scripts.

Current pain points for public-health users:

- The default runtime profile is still New Mexico HPS/hantavirus-specific.
- The user task is a config string, not a general structured intake interface.
- Broad source search is not available.
- Validation outputs are improved but still partly CSV/JSON-oriented.
- The HTML console is generated after a run; it is not a live updating product UI.
- Human review packet construction exists, but no UI applies review decisions back into final data.

## 8. Do not rebuild from scratch

The following components should be reused and extended rather than rebuilt:

- LangGraph state model and graph skeleton.
- Existing Pydantic models, with backward-compatible generic extensions later.
- Existing fetch/parse logic.
- Evidence chunking and data-presence flagging.
- Rule-based extraction fallback and LLM extraction wrapper.
- Schema validation and repair pattern.
- Normalization utilities.
- Record linking and consistency checking foundations.
- Human review packet builder.
- Final package builder and export utilities.
- Config/runtime profile helper pattern.
- Existing tests and fixtures, especially offline deterministic tests.
- Existing live case-study resources as controlled regression/acceptance cases.

## 9. Future-stage backlog

High-level future stages:

- Stage 1 structured task input and disease decoupling
- Stage 2 disease intelligence layer
- Stage 3 generic profile/schema setup
- Stage 4 LLM executable source planning
- Stage 5 real source discovery/search provider
- Stage 6 source credibility and role assignment
- Stage 7 fetch/parse/extraction generalization
- Stage 8 generic record schema and normalization
- Stage 9 duplicate detection/event clustering
- Stage 10 validation refactor
- Stage 11 human review decision application
- Stage 12 CLI/notebook/process visualization
- Stage 13 multi-disease live acceptance
