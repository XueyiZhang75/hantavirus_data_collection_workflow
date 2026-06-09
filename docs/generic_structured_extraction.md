# Generic Structured Extraction

## 1. Purpose

Stage 8 adds disease-generic public-health record extraction for the data collection workflow. The workflow can now represent COVID-19, dengue, hantavirus, and future diseases with a shared record shape instead of forcing every extracted record through hantavirus-specific semantics.

The internal package name remains `hdc_workflow`. `HantavirusRecord` remains available for backward compatibility, but the preferred cross-disease output representation is now `PublicHealthRecord`.

## 2. Inputs

Generic structured extraction reads the workflow state produced by earlier nodes:

- `collection_spec`: normalized disease, geography, time window, and target fields.
- `structured_task`: task-level disease, location, date range, target fields, and collection mode.
- `disease_intelligence`: disease aliases, abbreviations, pathogen terms, syndrome terms, and source hints.
- `collection_schema`: schema guidance derived from the disease/task profile.
- `documents`: fetched or fixture documents with source, parser, and quality metadata.
- `evidence_chunks`: chunked table or narrative evidence selected for extraction.
- `source_registry`: screened sources with source role and routing decisions.
- `source_credibility_summary`: deterministic credibility scores and reason fields.
- `source_search_execution_summary`: fixture or live search provenance.
- Optional LLM settings: provider/model flags and `HDC_ENABLE_LLM_EXTRACTION`, disabled by default unless explicitly enabled.

The extractor does not browse, search, or fetch. It only consumes evidence already present in workflow state.

## 3. Generic record schema

`PublicHealthRecord` extends the legacy `HantavirusRecord` field set and adds generic public-health fields. Missing information is represented as `null` rather than fabricated.

Disease identity fields include:

- `disease`
- `disease_standard_name`
- `disease_alias_used`
- `virus_or_syndrome`
- `pathogen_or_syndrome`
- `target_population`

Location fields include:

- `country`, `country_raw`
- `subnational_location`, `subnational_location_raw`
- `locality`, `locality_raw`
- `admin_level`
- `geographic_scope`, `geographic_scope_type`
- `location_confidence`, `location_notes`

Date and time fields include:

- `date_reported`, `date_reported_raw`
- `event_start_date`, `event_start_date_raw`
- `event_end_date`, `event_end_date_raw`
- `reporting_period`, `reporting_period_raw`
- `as_of_date`, `as_of_date_raw`
- `date_anchor`
- `date_confidence`, `date_notes`

Count fields include:

- `cases_confirmed`
- `cases_probable`
- `cases_suspected`
- `cases_unspecified`
- `deaths`
- `hospitalizations`
- `icu_admissions`
- `tests_positive`
- `tests_total`
- `positivity_rate`
- `incidence_rate`
- `cumulative_count`
- `new_count`
- `count_value_raw`
- `count_unit`
- `statistical_count_type`
- `count_semantics`
- `count_confidence`
- `count_notes`

Source and provenance fields include:

- `source_id`
- `source_url`
- `source_title`
- `source_type`
- `publisher`
- `source_role_final`
- `credibility_score`
- `credibility_level`
- `discovery_method`
- `search_provider`
- `query_id`
- `query_used`
- `document_id`
- `supporting_chunk_id`
- `evidence_quote`
- `evidence_context`
- `extraction_method`
- `extraction_model`
- `extraction_confidence`
- `extraction_warnings`

Review and compatibility fields include:

- `schema_status`
- `normalization_status`
- `record_linking_status`
- `record_conflict_status`
- `requires_human_review`
- `human_review_reason`
- `record_schema`
- `legacy_record_type`
- `notes`

## 4. Deterministic extraction

Deterministic extraction remains the default path. It supports table and narrative evidence chunks.

Table extraction recognizes simple delimited rows and common public-health columns such as date, location, cases, deaths, and hospitalizations. It creates records with source/evidence provenance copied from the chunk.

Narrative extraction recognizes simple patterns such as reported cases, confirmed cases, deaths, hospitalizations, years, and known locations. It uses task disease and disease-intelligence terms to avoid labeling non-hantavirus evidence as hantavirus.

Disease term matching uses active task context and disease intelligence:

- COVID-19: `COVID-19`, `COVID`, `SARS-CoV-2`
- Dengue: `dengue`, `DENV`, `dengue virus`
- Hantavirus: `hantavirus`, `HPS`, `Sin Nombre`

Count parsing preserves count semantics when the evidence suggests annual, historical total, cumulative, new, weekly, or unspecified counts. If semantics are unclear, the workflow keeps the count and records warnings or review flags rather than inventing certainty.

Review warnings are added for ambiguous disease, missing location/date on count-bearing records, unclear table columns, unclear count semantics, missing provenance, or extraction-level sanity concerns such as deaths greater than cases.

## 5. Optional LLM extraction

Optional LLM structured extraction is still gated by environment/config flags and is disabled by default in tests and fixture runs.

When enabled, the LLM prompt targets the generic record schema. The LLM receives evidence text and provenance only; it is not asked to browse, fetch, search, invent URLs, or create missing facts.

LLM output must validate against the generic schema. Invalid output is rejected or falls back to deterministic extraction when configured. Tests mock the LLM client and do not require API keys, internet access, or real model calls.

## 6. Backward compatibility

`HantavirusRecord` remains available and the New Mexico/Hantavirus path remains compatible. Stage 8 uses a unified approach: generic `PublicHealthRecord` records are produced for all diseases, with `legacy_record_type = "HantavirusRecord"` for hantavirus-compatible records.

Existing final dataset fields remain available. The final dataset field order is extended rather than replacing old fields.

## 7. What changes after Stage 8

After Stage 8:

- COVID-19 evidence can produce records with `disease = "COVID-19"`.
- Dengue evidence can produce records with `disease = "Dengue"`.
- Hantavirus evidence remains compatible with the legacy New Mexico workflow.
- `final_dataset` can include multiple disease types without forcing HantavirusRecord semantics.
- Search, fetch, source role, source credibility, document, and chunk provenance are preserved on generic records.
- Workflow summaries expose generic record counts, disease counts, extraction method counts, rejected record counts, and review-required record counts.

## 8. What is still not implemented

Stage 8 does not implement:

- validation refactor
- trusted-source validation
- cross-source validation refactor
- duplicate/event clustering overhaul
- anomaly detection
- human review decision application
- CLI redesign
- notebook redesign
- UI redesign
- broad crawling
- recursive crawling
- browser automation
- JavaScript rendering
- OCR
