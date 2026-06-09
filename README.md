# data collection workflow

**data collection workflow** is a LangGraph-based local package and CLI for
turning public-health source evidence into auditable structured records. It
accepts a structured task, plans sources, discovers or loads candidate sources,
scores credibility, fetches and parses bounded content, extracts generic
`PublicHealthRecord` records, normalizes records, clusters related events,
validates against reserved sources, detects anomalies, routes uncertain items to
human review, and exports a final package.

The current release is disease-generic at the workflow level. Hantavirus / New
Mexico remains the compatibility case study, while COVID-19 / New York and
dengue / Florida are included as multi-disease examples for fixture and live
acceptance checks. The workflow is an evidence organization tool, not medical
advice or official surveillance.

Key project documents:

- [Final product target](docs/final_product_target.md)
- [Current state audit](docs/current_state_audit.md)
- [Live baseline report](docs/live_baseline_report.md)
- [Structured task input](docs/structured_task_input.md)
- [Disease intelligence layer](docs/disease_intelligence_layer.md)
- [Generic profile/schema setup](docs/profile_schema_setup.md)
- [Executable source planning](docs/executable_source_planning.md)
- [Real source discovery](docs/real_source_discovery.md)
- [Stage 0 report](docs/stage_reports/STAGE_0_REPORT.md)
- [Stage 1 report](docs/stage_reports/STAGE_1_REPORT.md)
- [Stage 2 report](docs/stage_reports/STAGE_2_REPORT.md)
- [Stage 3 report](docs/stage_reports/STAGE_3_REPORT.md)
- [Stage 4 report](docs/stage_reports/STAGE_4_REPORT.md)
- [Stage 5 report](docs/stage_reports/STAGE_5_REPORT.md)

Controlled source-search execution is available: planned queries from the
executable source plan can run through fixture or live provider adapters when
explicitly enabled, producing search-derived source candidates with provenance.
The default test path remains offline and deterministic.

## Current User Quickstart

The user-facing project name is **data collection workflow**. The internal
Python package remains `hdc_workflow`.

Current case-study coverage remains Hantavirus / New Mexico, but the workflow
now also has disease-generic structured task input and deterministic fixture
examples for COVID-19 / New York and dengue / Florida. Fixed catalogs and
fixture search results are still used as offline seeds and fallbacks so tests
and development runs do not require internet access, search provider keys, or
LLM keys.

For the normal user path, run the interactive real workflow script:

```powershell
cd "C:\path\to\hantavirus_data_collection_workflow"
$env:PYTHONPATH = "src"
$env:TAVILY_API_KEY = [Environment]::GetEnvironmentVariable("TAVILY_API_KEY", "User")
$env:ANTHROPIC_API_KEY = [Environment]::GetEnvironmentVariable("ANTHROPIC_API_KEY", "User")
python scripts\run_interactive_workflow.py
```

The script asks for disease / virus, location, start date, end date, and an
optional session id. Record fields are fixed by the workflow schema, so normal
users do not need to decide extraction columns. After the input phase, it runs
the full real workflow with live search, live fetch, and LLM stages enabled by
default. It does not print API keys and does not fall back to fixture data.

Example direct run without prompts:

```powershell
python scripts\run_interactive_workflow.py --disease "hantavirus" --location "New Mexico" --start-date 2020 --end-date 2026 --session-id hantavirus_nm_real
```

For package/CLI commands, install the package in editable mode, then use:

```powershell
python -m pip install -e .
python -m hdc_workflow.cli --help
data-collection-workflow --help
```

For a one-off source-tree run without installation, set `PYTHONPATH=src` in the
current shell before calling `python -m hdc_workflow.cli`.

Deterministic offline fixture examples are for development, testing, and
acceptance checks. They are not the normal user path. Run them when you are
modifying the project or need a no-network smoke test. The bundled examples
include offline fixture COVID-19 and offline fixture dengue runs:

```powershell
python -m hdc_workflow.cli collect --config configs/examples/covid19_new_york_2024_fixture_review_application_task.jsonc --session-id quickstart_covid19_fixture --disable-all-llm
python -m hdc_workflow.cli collect --config configs/examples/dengue_florida_2025_fixture_review_application_task.jsonc --session-id quickstart_dengue_fixture --disable-all-llm
```

Inspect and export a completed session:

```powershell
python -m hdc_workflow.cli inspect-run --session-dir outputs/sessions/quickstart_covid19_fixture
python -m hdc_workflow.cli review-summary --session-dir outputs/sessions/quickstart_covid19_fixture
python -m hdc_workflow.cli export --session-dir outputs/sessions/quickstart_covid19_fixture --output-dir outputs/exports/quickstart_covid19_fixture --format both
```

API keys are optional and should stay in your shell or user environment, not in
config files. Live source search uses Tavily search metadata. Configure
`TAVILY_API_KEY` in your shell or user environment before enabling live search.
LLM stages are also optional. Configure `ANTHROPIC_API_KEY` for Anthropic
models, or `OPENAI_API_KEY` for OpenAI models, and then explicitly enable the
LLM stages in config or with CLI flags. Never put real keys in config files.

Important artifacts include `collection/final_package.json`,
`collection/final_dataset.csv`, `collection/final_dataset_post_review.json`,
`diagnostics/validation_results.json`, `diagnostics/anomaly_results.json`,
`diagnostics/human_review_audit_trail.json`, and the HTML workflow console.

Generate a safe starting config:

```powershell
python -m hdc_workflow.cli init-config --disease dengue --location Florida --start-date 2025 --end-date 2025 --target-field cases_unspecified --target-field deaths --mode fixture-search --output configs/local_dengue_fixture.jsonc
python -m hdc_workflow.cli validate-config --config configs/local_dengue_fixture.jsonc
```

More detailed instructions are in [docs/user_guide.md](docs/user_guide.md), and
a notebook-style walkthrough is in
[examples/notebooks/data_collection_workflow_quickstart.md](examples/notebooks/data_collection_workflow_quickstart.md).

## Project Purpose

This project orchestrates a multi-stage public-health data collection workflow.
The architecture is centered on a LangGraph `StateGraph` so that each stage of
the pipeline is a named, inspectable node and the shared state can be traced
end-to-end.

## Current Implementation Status

- **Step 1 — completed.** Project scaffolding, Pydantic schemas, typed `DataCollectionState`, placeholder nodes for every stage, and a compiled LangGraph skeleton runnable end-to-end.
- **Step 2 — completed.** Deterministic task scope inference (geography + time window), hantavirus disease profile loading, hantavirus collection schema (16 core fields + extraction rules), source strategy (5 source categories + screening criteria), and a structured search-query inventory.
- **Step 3 — completed.** Offline seed-source discovery using a curated hantavirus catalog (CDC, WHO, ECDC, PAHO, PubMed, Europe PMC, OpenAlex, plus placeholder structured-database and news seeds), URL canonicalization, deduplication, and a populated source registry with discovery provenance.
- **Step 4 — completed.** Deterministic source screening, source critic review, and source-level routing decisions. Every registered source is classified into a source role (`data_source` / `context_source` / `search_endpoint` / `placeholder_source` / `irrelevant_source`), screened, critic-reviewed, and assigned a final decision (`include_for_content_fetch` / `include_for_context_fetch` / `defer_to_search_expansion` / `needs_human_review` / `exclude`). Uncertain sources are queued for human review with deterministic review ids.
- **Step 5 — completed.** Content fetch request construction, offline metadata-stub document creation, optional live HTTP fetching (HTML/text via BeautifulSoup; PDF parse deferred), and document quality checks. Deferred / search-endpoint / placeholder / human-review sources are correctly skipped from fetching.
- **Step 6 — completed.** Evidence chunking and deterministic data presence flagging for usable/partial real documents, while safely skipping offline stubs, parse-deferred PDFs, and unusable documents. Each chunk is annotated with target-data signal types (case_count / death_count / outbreak / surveillance / date / location), context signal types (disease_definition / case_definition / clinical_or_background), and a deterministic confidence score.
- **Step 7 — completed.** Deterministic structured extraction from target evidence chunks (text + pipe-delimited tables) into `HantavirusRecord` objects, plus schema validation, deterministic repair, provenance checking, rejected-record tracking, and human-review flagging for incomplete records. Records carry full chunk-level provenance (`supporting_chunk_id`, `evidence_quote`, `source_url`, etc.) and a non-negative numeric check on all case/death fields.
- **Step 8 — completed.** Deterministic record normalization for country names (alias + canonical), subnational-to-country inference, non-country geography handling, date strings (ISO + month-name patterns), virus/syndrome aliases, case-definition labels (split-and-normalize, plus inference from populated case fields), source-type case normalization, and numeric string parsing. All original inputs are preserved on `*_raw` fields; review-trigger warnings route records to the human review queue.
- **Step 9 — completed.** Deterministic record linking from normalized records into linked events. Builds a stable per-record event key from (disease, virus_or_syndrome, country, subnational_location, date_anchor), groups records with the same key, writes `linked_event_id` back onto each record, and tracks per-event source diversity (`source_ids` / `source_urls` / `source_types` / `publishers`). Records missing disease + all geo/date signals fall into singleton "not_linkable" groups; records with review-trigger warnings (missing country with case data, missing date anchor, non-country geography, or carrying forward `requires_human_review` from earlier steps) are routed to the human review queue.
- **Step 10 — completed.** Deterministic cross-source consistency checking within linked events. Numeric fields (cases_*, deaths) are diffed using minor/major thresholds; text fields (country, subnational_location, virus_or_syndrome, case_definition) and date fields (date_reported, event_start_date, event_end_date, date_anchor) are compared with field-specific conflict types and severities. Each `Conflict` carries full provenance (record_ids, source_ids/urls/types, evidence quotes). Events and records are annotated with consistency status, and reviewable conflicts are routed to the human review queue. The quality gate now routes to `human_review` whenever the queue is non-empty.
- **Step 11 — completed.** Opt-in local synthetic fixture-document mode (`HDC_USE_FIXTURE_DOCUMENTS=true`) injects synthetic local documents for selected source IDs so the workflow produces non-empty `documents` / `evidence_chunks` / `raw_records` / `validated_records` / `normalized_records` / `linked_events` / `conflicts` / `human_review_queue` / final data package without internet and without LLMs. Default behavior is unchanged.
- **Step 12 — completed.** Human review packet construction inside the `human_review` node. Every queued item is coerced into a `HumanReviewItem`, given a deterministic priority by item type, packaged with relevant context (source registry entry / raw + validated record / validated + normalized record / linked event + related records / conflict + linked event + related records), and tagged with a synthetic-fixture warning when applicable. Optional decisions supplied via `state["human_review_decisions"]` are matched by `review_id` and recorded with status, reviewer, timestamp, notes, and audit metadata. The node does not modify records or resolve conflicts.
- **Step 13 — completed.** Final data package hardening and export utilities. `final_data_package_builder` now produces a self-contained, auditable package: `final_dataset` / `source_registry` / `linked_events` / `conflicts` / `human_review_items` / `excluded_sources` / `collection_trace` plus new `package_metadata`, `workflow_summaries` (aggregated across all earlier nodes), `data_dictionary` (from the loaded collection schema), `provenance_manifest`, `export_manifest`, `export_warnings`, `contains_synthetic_fixture_data` flag, and `synthetic_fixture_notice` when fixture data are present. A new `hdc_workflow.export` module writes the package to deterministic JSON + CSV artifacts.
- **Step 14 — completed.** Optional LLM-based structured extraction agent on the `structured_extraction` node. Default behavior is unchanged (deterministic rule-based). When `HDC_ENABLE_LLM_EXTRACTION=true`, the node calls a configured provider (Anthropic Claude via `langchain-anthropic`, or OpenAI via `langchain-openai`) per eligible evidence chunk and unpacks structured `LLMExtractionOutput` into `HantavirusRecord`s. Per-chunk fallback to the deterministic extractor is enabled by default and can be turned off. `llm_extraction_summary` is added to state and the final-package `workflow_summaries`. The `package_metadata.llm_used` flag reflects actual workflow output, and `workflow_node_count` now matches the final trace length.
- **Step 15 — completed.** Controlled live-source pilot mode. `HDC_SOURCE_ID_ALLOWLIST` restricts `content_fetch_and_parse` to a small comma-separated list of source IDs; `HDC_LLM_MAX_CHUNKS` caps the number of eligible evidence chunks sent to the LLM. A new `scripts/run_live_source_llm_pilot.py` runs a deterministic end-to-end pilot against real official source pages with optional Claude or OpenAI extraction and exports the final data package. Defaults remain unchanged.
- **Step 16 — completed.** Real-world semantic guardrails. `HantavirusRecord` gains `statistical_count_type` / `reporting_period` / `as_of_date` / `aggregation_level` / `geographic_scope` / `geographic_scope_type` / `population_scope` / `source_section` / `semantic_warnings`. A shared post-extraction guardrail (`_apply_extraction_semantic_guardrails`) standardizes `disease`, strips disease-level terms from `virus_or_syndrome`, infers `statistical_count_type` from chunk text, and handles regional / multi-country scopes (e.g. EU/EEA). Record linking now incorporates the new semantic fields into `event_key` so cumulative vs annual vs newly-reported counts no longer get linked together. Cross-source consistency check skips numeric comparison and records a skip warning when records inside the same event carry different `statistical_count_type` or `reporting_period`.
- **Step 16.1 — completed.** Hotfix exposed by the Step 16 live pilot. `record_linking_policy.json` extends `date_anchor_preference` to fall back to `as_of_date` and `reporting_period` when `date_reported` is missing, and a new `_normalize_date_anchor_value` helper canonicalizes natural-language temporal expressions such as `"December 2020"`, `"through December 2020"`, `"as of December 2020"`, and `"reported through December 2020"` into ISO-style anchors (`"2020-12"`). `_date_anchor` also keeps `as_of_date` / `reporting_period` as implicit fallbacks for older policy snapshots. Both `record_normalization` and `record_linking` now treat regional / multi-country / global `geographic_scope_type` as valid geography for case data — they emit a non-review `regional_or_aggregate_geographic_scope` warning instead of routing to the human review queue. Together these reduce false review routing for EU/EEA aggregates and for records whose only temporal field is `reporting_period`.
- **Step 16.1.1 — completed.** Enum-canonicalization hotfix. LLM output frequently emits hyphenated or free-text variants of the semantic enums (`"multi-country"` instead of `"multi_country"`, `"national"` instead of `"country"`, `"newly-reported"` instead of `"newly_reported"`). Step 16.1.1 adds shared canonicalization helpers (`_canonicalize_geographic_scope_type`, `_canonicalize_statistical_count_type`) in the extraction guardrails and mirrors them in `record_normalization` and `record_linking`, so the same canonical vocabulary reaches every downstream node regardless of the path a record took into state. The Step 16.1 regional-scope exception now fires on canonical `"multi_country"`, so EU/EEA records no longer get pushed to `missing_country_*` review by a hyphen mismatch. `llm_structured_extraction_policy.json` also tells the LLM to use the canonical enum values directly. Default behavior remains deterministic and offline-safe; no graph topology, node-name, or default-mode changes.

## Real-world Pilot Lessons

The first live-source pilot in Step 15 successfully fetched official CDC / ECDC / WHO webpages and ran Claude Sonnet 4.6 structured extraction end-to-end. The run was a **technical success** but exposed real-world semantic complexity that needed extra guardrails:

- The same CDC page can contain a cumulative case total, an annual increment, and a subset count — three numbers that look comparable but mean different things.
- Multi-country reports (e.g. ECDC "EU/EEA (28 countries)") are not single countries but regions; treating them as countries forces a normalization warning that can be avoided with explicit `geographic_scope_type`.
- LLM output sometimes writes disease-level terms into `virus_or_syndrome` (e.g. "hantavirus disease"), which splits otherwise-identical event keys.
- Death counts written in narrative form (e.g. "5 people died") are sometimes missed.

Step 16 adds the deterministic guardrails described above so the workflow handles these cases without changing graph topology or removing fallback safety. This is **not** evaluation, baseline comparison, or conflict resolution — just better real-world data semantics.

The follow-up live pilot after Step 16 surfaced two further symptoms that motivated Step 16.1:

- Sonnet 4.6 frequently placed the temporal cutoff (e.g. `"December 2020"`) inside `reporting_period` instead of `date_reported`, so `date_anchor` resolved to `UNKNOWN` and otherwise-identical records fragmented into separate `linked_events`.
- Regional aggregates such as ECDC's `EU/EEA` were correctly moved out of `country` into `geographic_scope`, but still triggered `missing_country_after_normalization` and routed every aggregate record into the human review queue.

Step 16.1 adds a date-anchor fallback so `reporting_period` and `as_of_date` can serve as the anchor when `date_reported` is missing, normalizes common natural-language temporal expressions to ISO form, and treats regional / multi-country / global `geographic_scope_type` as valid geography so the workflow no longer routes EU/EEA-style aggregates to human review.

The post-Step-16.1 live pilot exposed a remaining string-shape issue: the LLM was emitting `geographic_scope_type="multi-country"` (hyphenated) and `geographic_scope_type="national"` while the Step 16.1 regional-scope exception looked for the canonical `"multi_country"` / `"country"`. Step 16.1.1 canonicalizes these LLM enum-like outputs (e.g. `multi-country` → `multi_country`, `national` → `country`, `newly-reported` → `newly_reported`) at the extraction guardrail, normalization, and linking layers so that semantically correct but string-inconsistent LLM outputs no longer inflate the human review queue downstream.

Still **not** implemented in any current step:

- LLM source screening
- LLM validation
- Applying human decisions to modify records / conflicts
- Conflict resolution
- Credibility scoring
- Broad real web search
- Article-level expansion from literature search endpoints
- PDF parsing / OCR
- Human review UI
- Baseline comparison or evaluation metrics

These remain placeholders and will be filled in by later steps without changing node names.

### Live HTTP fetching (opt-in)

By default the workflow runs `HDC_ENABLE_LIVE_FETCH=false`, so `content_fetch_and_parse` creates deterministic offline **metadata-stub documents** and does NOT contact any external website. Tests must not depend on internet access.

To manually exercise the live HTTP path on a machine with internet, run:

```bash
HDC_ENABLE_LIVE_FETCH=true python scripts/run_live_fetch_demo.py
```

This will fetch HTTP/HTTPS sources, parse HTML with BeautifulSoup, and defer PDF parsing. Search endpoints (PubMed / Europe PMC / OpenAlex) and `seed://` placeholders are never fetched.

### Evidence chunking in default offline mode

In the default offline run, `evidence_chunks` will be **empty** because all documents are deterministic metadata stubs, not real source content. Evidence chunks are produced only for **real** fetched documents whose `quality_status` is `usable` or `partial`. Switch on live fetch (above) to see populated chunks.

### Structured extraction in default offline mode

In the default offline run, `raw_records` and `validated_records` are also **empty** because no evidence chunks are produced. Step 7 extraction logic is exercised directly via the test suite using synthetic evidence chunks. Later steps can swap the deterministic extractor for an LLM structured-output agent without changing node names.

### Record normalization in default offline mode

In the default offline run, `normalized_records` is also **empty** because `validated_records` is empty. Step 8 normalization logic is exercised directly via the test suite using synthetic validated records. The downstream `record_linking` node will consume `normalized_records` once real records start flowing through the pipeline.

### Record linking in default offline mode

In the default offline run, `linked_events` is also **empty** because `normalized_records` is empty. Step 9 linking logic is exercised directly via the test suite using synthetic normalized records. The next step (`cross_source_consistency_check`) will use `linked_events` plus `normalized_records` to detect value-level disagreements across linked sources.

### Cross-source consistency checking in default offline mode

In the default offline run, `conflicts` is also **empty** because `linked_events` is empty. Step 10 conflict detection is exercised directly via the test suite using synthetic linked events and normalized records. The next step can focus on final data package completeness and the workflow audit trail, or on introducing local fixture documents for an end-to-end non-empty run.

## Local Fixture Document Mode

By default the workflow uses offline metadata stubs and produces no records. Step 11 adds an **opt-in synthetic fixture mode**:

- Set `HDC_USE_FIXTURE_DOCUMENTS=true` to inject synthetic local fixture documents for selected source IDs (CDC reported cases, ECDC surveillance updates, ECDC annual report, WHO context).
- **Fixture documents are NOT real public health data.** They are deliberately synthetic and intended only to exercise the full workflow end-to-end without internet and without LLMs.
- In fixture mode the workflow should produce evidence chunks, extracted records, normalized records, linked events, cross-source conflicts, and human-review items.
- The three data-source fixtures (CDC + ECDC ×2) intentionally report 12, 13, and 30 cases for the same synthetic linked event so the cross-source consistency checker detects a **high-severity major-numeric-difference conflict** and routes the workflow to `human_review`.

Run the deterministic fixture-mode demo:

```bash
python scripts/run_fixture_workflow_demo.py
```

Expected behavior:

- `current_route` becomes `human_review` (the high-severity conflict triggers review).
- `final_data_package` contains non-empty `final_dataset`, `linked_events`, `conflicts`, and `human_review_items`.
- The workflow never contacts the network.

Default behavior is preserved: with `HDC_USE_FIXTURE_DOCUMENTS=false` (or unset), the workflow still produces empty downstream stages and routes to `finalize`.

## Human Review Packet Mode

The `human_review` node structures every queued review item into a richer **review packet** before downstream consumption. For each item it:

- Coerces the item into a validated `HumanReviewItem` shape.
- Assigns a deterministic priority by `item_type` (cross-source conflicts are highest).
- Attaches a `review_packet` containing the relevant context (source registry entry / raw + validated record / validated + normalized record / linked event + related records / conflict + linked event + related records).
- Sets a `synthetic_fixture_warning` if any packet content comes from synthetic fixture data.
- Optionally records a decision supplied in `state["human_review_decisions"]`, matched by `review_id`. Decision intake writes the new `status`, `human_decision`, `reviewer_id`, `decided_at`, `modified_values`, and `decision_applied` audit fields — but **does not modify the underlying records, conflicts, or sources**.

The same `human_review_decisions` field can later be fed by a UI without changing the graph topology.

Try it:

```bash
python scripts/run_fixture_workflow_demo.py
python scripts/run_fixture_workflow_with_review_decision_demo.py
```

Expected behavior:

- The first fixture demo creates a single pending `cross_source_conflict` review item (high-severity cases-count conflict) with a fully populated `review_packet`.
- The second fixture demo records a `needs_more_evidence` decision for that item; status flips to `requires_follow_up`, `decision_applied=True`, and the reviewer + notes are preserved.
- Both demos use **synthetic fixture data** — not real public health data.

## Final Data Package and Export

Step 13 turns the workflow's final output into a self-contained, auditable package. In addition to the existing record/source/event/conflict/review/excluded/trace sections, every run now produces:

- `package_metadata` — package name, version, deterministic generated_at, disease/geography/time window from `collection_spec`, workflow node count, and flags asserting that no LLM, no real web search, no baseline comparison, and no evaluation metrics were used.
- `workflow_summaries` — every summary dict from every earlier node (source discovery / screening / critic / routing / content fetch / fixture / document quality / evidence chunking / data presence / structured extraction / schema validation / record normalization / record linking / cross-source consistency / human review).
- `data_dictionary` — the active collection schema's field definitions, or a minimal one derived from the policy field order.
- `provenance_manifest` — counts of records that actually carry source URL, evidence quote, supporting chunk id, and linked event id, plus per-section totals.
- `export_manifest` — list of exportable sections and per-section counts.
- `contains_synthetic_fixture_data` + `synthetic_fixture_notice` — clearly flagged when any fixture-origin content is detected anywhere in the workflow state.

The `hdc_workflow.export` module writes the package to deterministic JSON + CSV artifacts under an output directory:

```bash
python scripts/export_fixture_final_package.py
```

Expected outputs (under `outputs/fixture_final_package/`):

- `final_package.json`
- `final_dataset.csv`
- `source_registry.json`
- `linked_events.json`
- `conflicts.json`
- `human_review_items.json`
- `collection_trace.json`
- `workflow_summaries.json`
- `package_metadata.json`
- `provenance_manifest.json`

Fixture-mode export is deterministic and fully offline; it emits a `contains_synthetic_fixture_data=true` flag and a clear notice that the contents are not real public health data.

## Optional LLM Structured Extraction

Default `structured_extraction` is deterministic and offline. Step 14 adds an opt-in LLM extraction agent that runs only when `HDC_ENABLE_LLM_EXTRACTION=true`:

- Both **Anthropic Claude** (`langchain-anthropic`) and **OpenAI** (`langchain-openai`) are supported.
- The agent reads each eligible evidence chunk and returns structured records.
- Per-chunk **fallback to the deterministic extractor** is enabled by default; disable by setting `HDC_LLM_FALLBACK_TO_RULE_BASED=false`.
- Tests do **not** require an API key — they monkeypatch the LLM client.
- Fixture documents are synthetic; even with LLM extraction enabled, they remain not real public health data.

Try it with Claude (replace placeholders; never commit real keys):

```bash
export HDC_USE_FIXTURE_DOCUMENTS=true
export HDC_ENABLE_LIVE_FETCH=false
export HDC_ENABLE_LLM_EXTRACTION=true
export HDC_LLM_PROVIDER=anthropic
export HDC_LLM_MODEL=<your-claude-model-name>
export ANTHROPIC_API_KEY=<your-anthropic-api-key>
python scripts/run_fixture_workflow_llm_extraction_demo.py
```

Or with OpenAI:

```bash
export HDC_USE_FIXTURE_DOCUMENTS=true
export HDC_ENABLE_LIVE_FETCH=false
export HDC_ENABLE_LLM_EXTRACTION=true
export HDC_LLM_PROVIDER=openai
export HDC_LLM_MODEL=<your-openai-model-name>
export OPENAI_API_KEY=<your-openai-api-key>
python scripts/run_fixture_workflow_llm_extraction_demo.py
```

Notes:

- Do not commit API keys.
- If no API key or model is provided, the demo exits before invoking the graph.
- The default workflow remains offline and deterministic.
- LLM extraction is a single optional node behavior. The rest of the pipeline (schema validation, normalization, linking, consistency checking, human review, final packaging) continues to run as before.

## Controlled Live Source Pilot

Step 11 fixture mode proves the workflow end-to-end on synthetic local documents. Step 15 adds an opt-in **live-source pilot** that replaces fixture documents with real HTTP-fetched source content from a small allowlist of official source IDs. It is **not** broad web search — the registry is unchanged, and the allowlist only limits which already-registered sources actually get fetched.

What the pilot does:

- Disables fixture documents (`HDC_USE_FIXTURE_DOCUMENTS=false`).
- Enables live HTTP fetching (`HDC_ENABLE_LIVE_FETCH=true`).
- Enables LLM extraction by default (overridable via env).
- Restricts sources via `HDC_SOURCE_ID_ALLOWLIST` (comma-separated `source_id`s).
- Caps LLM calls via `HDC_LLM_MAX_CHUNKS` to keep API cost predictable.
- Exports the resulting final data package to `outputs/live_source_llm_pilot/` (or `HDC_LIVE_PILOT_OUTPUT_DIR`).

Run (replace placeholders; never commit real keys):

```bash
export HDC_LLM_PROVIDER=anthropic
export HDC_LLM_MODEL=<your-claude-model-name>
export ANTHROPIC_API_KEY=<your-anthropic-api-key>
export HDC_SOURCE_ID_ALLOWLIST=src_cdc_reported_cases,src_ecdc_surveillance_updates,src_ecdc_annual_report_2023,src_who_hantavirus_fact_sheet
export HDC_LLM_MAX_CHUNKS=8
python scripts/run_live_source_llm_pilot.py
```

Notes:

- Do not commit API keys.
- The pilot contacts external websites and a real LLM provider.
- If the fetched pages contain little extractable case data, `raw_records` may be small or empty — that is a real finding about live source content, not a code failure.
- If pages block requests, return JS-rendered content, or are large PDFs, `quality_status` may end up `partial`, `unusable`, or `parse_deferred`.
- The next phase after this pilot could focus on better real-source connectors, PDF/OCR parsing, or article-level expansion from literature search endpoints — none of which are part of Step 15.

## Workflow Nodes

In execution order:

1. `task_intake_and_scope_planning`
2. `disease_intelligence_builder`
3. `profile_and_schema_setup`
4. `executable_source_planning`
5. `query_strategy_builder`
6. `source_discovery`
7. `source_dedup_and_registry`
8. `source_screening`
9. `source_critic_and_uncertainty_routing`
10. `content_fetch_and_parse`
11. `document_quality_check`
12. `evidence_chunking_and_data_presence_flagging`
13. `structured_extraction`
14. `schema_validation_and_repair`
15. `record_normalization`
16. `record_linking`
17. `cross_source_consistency_check`
18. `quality_gate_routing`
19. `human_review` (conditional)
20. `final_data_package_builder`

`quality_gate_routing` conditionally routes either to `human_review` and then on to `final_data_package_builder`, or directly to `final_data_package_builder`.

## Installation

Requires Python 3.11+.

```bash
cd hantavirus_data_collection_workflow
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Copy `.env.example` to `.env` and fill in any values you intend to use in later steps:

```bash
cp .env.example .env
```

## Running the Demo

```bash
python scripts/run_workflow_demo.py
```

The demo invokes the full LangGraph skeleton with an empty input state, prints the resolved collection spec, disease profile name, generated search queries, the trace length, the final data package keys, and the ordered list of node names executed.

## Running Tests

```bash
pytest -q
```

The smoke tests verify that the graph compiles, that an end-to-end invocation produces a final data package, that the trace contains at least 15 events, and that the schemas validate inputs as expected.

## LangGraph Studio / Workflow Visualization

Step 3.5 adds local LangGraph Studio support so the workflow can be inspected visually — every node, every conditional edge, and every state update — in a browser UI.

How it is wired up:

- `langgraph.json` at the project root declares the package dependencies and the graph entry point.
- The entry point is [src/hdc_workflow/studio_app.py](src/hdc_workflow/studio_app.py), which exposes a compiled `graph` object built by `build_graph()`.
- The current workflow is **still fully offline and deterministic** — no LLM call, no web search, and no scraping is performed when Studio runs the graph.

Install with the optional dev tooling:

```bash
pip install -e ".[dev]"
```

Run a quick sanity check that the Studio entry point compiles and invokes correctly:

```bash
python scripts/check_studio_app.py
```

If you want a JSON blob to paste into the Studio "input state" panel:

```bash
python scripts/print_studio_initial_state.py
```

Launch the LangGraph local development server:

```bash
langgraph dev
```

The CLI uses `langgraph.json` by default and opens a browser tab pointed at the local server. If a browser (notably Safari) refuses to connect to `localhost`, try the tunnel mode:

```bash
langgraph dev --tunnel
```
