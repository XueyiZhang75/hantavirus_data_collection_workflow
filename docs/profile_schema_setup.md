# Generic Profile and Schema Setup

## 1. Purpose

Stage 3 makes profile/schema setup disease-aware for the **data collection workflow**. After structured task intake and disease intelligence, the workflow now builds the active `disease_profile`, `collection_schema`, and `source_strategy` from the requested disease rather than always using the static hantavirus profile/schema.

The active graph node is:

```text
profile_and_schema_setup
```

The old callable name remains as a backward-compatible alias:

```text
hantavirus_profile_and_schema_setup
```

## 2. Inputs

The node reads:

- `structured_task`
- `collection_spec`
- `disease_intelligence`
- task `target_fields`
- task `source_preferences`

For curated disease-intelligence profiles, the node uses disease-specific terms, pathogen terms, syndrome terms, extraction priorities, source categories, likely reporting agencies, and validation source categories. For unknown diseases, the existing generic deterministic disease-intelligence fallback is used.

## 3. Outputs

The node writes:

- `disease_profile`
- `collection_schema`
- `source_strategy`
- `screening_criteria`
- `profile_schema_summary`

`profile_schema_summary` is exported through final package `workflow_summaries`. It includes:

- disease
- profile generation method
- schema generation method
- source strategy generation method
- active disease profile name
- active collection schema name/version
- core field count
- target field count
- source category count
- warnings

## 4. Hantavirus Compatibility Path

Hantavirus tasks remain backward-compatible with the current curated resources. For hantavirus/HPS tasks, the node still loads:

- `src/hdc_workflow/resources/hantavirus_profile.json`
- `src/hdc_workflow/resources/hantavirus_collection_schema.json`
- `src/hdc_workflow/resources/source_strategy.json`

The summary generation method for this path is:

```text
legacy_hantavirus_profile_schema
```

This preserves the New Mexico HPS case-study behavior and existing hantavirus tests.

## 5. Non-Hantavirus Generated Path

For non-hantavirus tasks such as COVID-19 and dengue, the workflow now generates active profile/schema resources from `disease_intelligence` and `collection_spec`.

Examples:

- COVID-19 active profile includes COVID-19/SARS-CoV-2 terms rather than HPS/Sin Nombre terms.
- Dengue active profile includes dengue/DENV/dengue fever/severe dengue terms rather than HPS terms.
- Generated collection schemas use disease-neutral public-health fields such as cases, deaths, dates, source URL, source type, evidence quote, supporting chunk ID, statistical count type, reporting period, as-of date, and geographic scope fields.
- Generated source strategies use disease-aware but disease-neutral screening criteria: include human case/death/hospitalization/surveillance data for the requested disease, exclude background-only or unrelated material, and mark unclear disease/geography/time/count semantics as uncertain.

The summary generation method for curated disease-intelligence tasks is:

```text
disease_intelligence_generated_profile_schema
```

For unknown diseases with only the generic deterministic disease-intelligence fallback, the summary generation method is:

```text
generic_fallback_profile_schema
```

## 6. What Changes After Stage 3

- Non-hantavirus tasks no longer use the hantavirus profile/schema as active resources.
- Query strategy receives disease-aware active profile/source strategy resources.
- `profile_schema_summary` is exported in final package `workflow_summaries`.
- Stale non-hantavirus warnings are removed:
  - `profile_schema_not_yet_generalized`
  - `non_hantavirus_task_with_hantavirus_profile_resources`
- Remaining future-stage warnings are preserved:
  - `source_discovery_not_yet_disease_generic`
  - `extraction_record_model_still_hantavirus_named`
  - `extraction_record_schema_not_yet_disease_generic`

## 7. What Is Still Not Implemented

Stage 3 does not implement:

- real source discovery/search provider
- executable LLM source planning
- source URL generation or source URL ingestion from LLM output
- disease-generic extraction record model
- replacement or mass rename of `HantavirusRecord`
- validation refactor
- duplicate clustering changes
- anomaly detection
- human review decision application
- CLI redesign
- notebook redesign
- UI redesign

Those remain future-stage work.
