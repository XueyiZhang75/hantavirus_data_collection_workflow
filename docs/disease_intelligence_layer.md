# Disease Intelligence Layer

## 1. Purpose

Stage 2 adds a disease intelligence layer to the **data collection workflow**. The layer converts a structured task disease, location, time window, and target fields into auditable disease-specific intelligence for downstream source planning and query construction.

This layer is intentionally narrow. It provides terminology, source-need categories, suggested query terms, validation source categories, extraction priorities, and risk notes. It does not perform web search, does not create source URLs, and does not replace the existing extraction schema.

The new graph node is:

```text
disease_intelligence_builder
```

It runs after:

```text
task_intake_and_scope_planning
```

and before:

```text
profile_and_schema_setup
```

All existing node names remain available. The internal package name remains `hdc_workflow`.

## 2. Inputs

The node reads the existing task state:

- `structured_task.disease`
- `structured_task.location`
- `structured_task.start_date`
- `structured_task.end_date`
- `structured_task.target_fields`
- `collection_spec`

If the disease is one of the curated profiles, the workflow loads a deterministic local profile. If the disease is not curated, it emits a generic deterministic fallback profile with clear warnings.

The current curated profile directory is:

```text
src/hdc_workflow/resources/disease_intelligence/
```

Current curated profiles:

- `hantavirus.json`
- `covid19.json`
- `dengue.json`

## 3. Outputs

The node writes two state fields:

```text
disease_intelligence
disease_intelligence_summary
```

`disease_intelligence` contains the full structured profile:

- disease input and standard name
- aliases and abbreviations
- pathogen, syndrome, clinical, transmission, surveillance, outbreak, case-count, death, and hospitalization terms
- likely reporting agencies
- preferred collection source categories
- validation source categories
- suggested geographic and time granularity
- extraction priority fields
- count semantics notes
- disambiguation risks and exclusion terms
- suggested query terms and templates
- confidence, generation method, and warnings

`disease_intelligence_summary` is a compact auditable summary exported through the final package workflow summaries:

- `disease_input`
- `disease_standard_name`
- `generation_method`
- term/source/query counts
- warnings

The query strategy builder now uses `disease_intelligence.suggested_query_terms`, `syndrome_terms`, and `pathogen_terms` when available. This changes query text by disease, but it still only builds an internal query inventory. It does not execute search.

## 4. Curated Profiles

Curated profiles are the default path. They keep tests deterministic and offline.

For example:

- Hantavirus tasks include terms such as HPS, hantavirus pulmonary syndrome, Sin Nombre virus, rodent exposure, cases, deaths, and official health agency reporting.
- COVID-19 tasks include COVID-19, SARS-CoV-2, hospitalization, deaths, respiratory surveillance, dashboard, CDC, state health department, and related reporting risks.
- Dengue tasks include dengue, DENV, dengue virus, arbovirus surveillance, mosquito-borne disease, imported case, locally acquired case, and vector-borne source needs.

These profiles are advisory. They help source planning and query construction. They do not certify a source, validate a record, or decide whether an extracted count is correct.

## 5. Optional LLM Generation

The LLM disease intelligence path is disabled by default.

Enable it with:

```text
HDC_ENABLE_LLM_DISEASE_INTELLIGENCE=true
```

Optional controls:

```text
HDC_DISEASE_INTELLIGENCE_FORCE_LLM=true
HDC_DISEASE_INTELLIGENCE_FALLBACK_TO_CURATED=true
```

Provider/model settings continue to use the existing LLM environment keys:

```text
HDC_LLM_PROVIDER
HDC_LLM_MODEL
HDC_LLM_MAX_TOKENS
ANTHROPIC_API_KEY or OPENAI_API_KEY
```

When enabled, the prompt asks the model to generate disease intelligence for source planning only. It explicitly tells the model:

- do not perform web search
- do not provide URLs
- do not claim source discovery
- return structured terminology, source needs, validation categories, extraction priorities, and warnings

If the LLM call fails, the node falls back to the curated or generic deterministic profile when fallback is enabled. The fallback records warnings such as:

```text
llm_disease_intelligence_failed_curated_fallback
llm_failure_type:<ExceptionType>
```

## 6. What Changes After Stage 2

After Stage 2:

- The workflow can preserve non-hantavirus tasks from Stage 1 and attach disease-specific source-planning intelligence.
- Full graph outputs now include `disease_intelligence_summary`.
- Query inventories differ for hantavirus, COVID-19, and dengue tasks.
- The default offline run remains deterministic and does not require internet, API keys, live web, or real LLM calls.
- A live LLM smoke test can be run for disease intelligence only, without fetching webpages or sending webpage evidence.

## 7. What Is Still Not Implemented

Stage 2 does not implement:

- broad real web search
- search provider integration
- executable source discovery from generated query terms
- generic disease profile/schema setup
- disease-generic extraction schema replacement
- validation refactor
- duplicate clustering changes
- anomaly detection
- human review decision application
- CLI, notebook, or UI redesign
- graph topology changes beyond the approved `disease_intelligence_builder` node
- source URL invention or LLM-generated source registry entries

Those items remain future-stage work.
