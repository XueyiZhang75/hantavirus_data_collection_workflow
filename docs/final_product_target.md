# Final Product Target: data collection workflow

## 1. One-sentence target

The data collection workflow is a practical public-health disease data collection package / skill-like workflow that accepts user-specified disease, location, time range, and target fields, then uses LLM-driven planning and live source discovery to collect, extract, validate, deduplicate, review, and export disease data.

## 2. What this is NOT

- Not a hantavirus-only workflow.
- Not only a New Mexico HPS case study.
- Not merely a fixed source catalog filter.
- Not a pure rule-based crawler.
- Not just a paper demo.
- Not an uncontrolled blind web scraper.
- Not a claim of new CS algorithmic novelty.
- Not fully automatic truth determination without human review.

## 3. Required final user experience

The final data collection workflow should start from a structured user task, not from a hard-coded disease profile or case-study source set.

Example user input:

- disease = hantavirus
- location = New Mexico
- time range = 2020-2026

The workflow should generate hantavirus-specific aliases, syndrome terms, source needs, official agency targets, validation candidates, and executable search terms for New Mexico and the requested years.

Example user input:

- disease = COVID-19
- location = New York
- time range = 2024

The workflow should generate COVID-19-specific terminology, reporting sources, dashboard or health department targets, likely structured data sources, validation candidates, and extraction priorities appropriate for COVID-19 rather than reusing hantavirus/HPS assumptions.

Example user input:

- disease = dengue
- location = Florida or Brazil
- time range = 2025

The workflow should generate dengue-specific aliases, vector-borne disease source categories, region-specific agency and surveillance sources, validation source candidates, and extraction priorities appropriate for dengue.

Search needs, aliases, source categories, validation sources, and extraction priorities must change dynamically based on the disease, location, time window, and requested fields.

## 4. Required final architecture

The final architecture should include these components:

- structured user task intake
- disease intelligence layer
- LLM-driven source planning
- LLM-generated executable search queries
- real source discovery
- source registry
- source credibility and role assignment
- live fetch and parse
- evidence chunking
- structured extraction
- record normalization
- duplicate detection and event clustering
- trusted-source validation
- cross-source validation
- anomaly detection
- human review
- user-friendly final outputs
- process transparency report

## 5. Role of LLMs

LLMs should not only summarize final text. They should help with:

- disease-specific terminology expansion
- source discovery planning
- executable query generation
- source role and credibility reasoning
- extraction from heterogeneous evidence
- validation reasoning
- duplicate/same-event reasoning
- human review explanations

LLM outputs must remain auditable. The workflow should record prompts or prompt versions, model/provider metadata, source IDs, source URLs, evidence chunk IDs, evidence quotes, confidence or reason fields, and fallback behavior where applicable.

## 6. Role of fixed catalogs

Fixed catalogs may remain as seed sources, trusted hints, fallbacks, fixtures, and guardrails.

Fixed catalogs must not be the final primary source discovery mechanism.

The final workflow must be able to discover new sources from LLM-generated search plans and executable search queries. The catalog should help constrain and audit discovery, but it should not be the only place where candidate sources can originate.

## 7. Final output artifacts

Expected final outputs include:

- final_dataset.csv
- final_dataset.json
- source_registry.csv/json
- search_plan.json
- search_queries.json
- search_results.json
- fetched_documents_manifest.json
- evidence_chunks.json
- extracted_records.csv/json
- normalized_records.csv/json
- duplicate_clusters.csv/json
- validation_results.csv/json
- anomaly_warnings.csv/json
- human_review_queue.csv/json
- process_trace.html or process_trace.md
- run_metadata.json

Each output should preserve provenance when applicable: source_id, source_url, source type, evidence_quote or evidence_chunk_id, run/config metadata, model metadata, and reason fields.

## 8. Final success criteria

- Works for hantavirus and at least one non-hantavirus disease.
- Search strategy changes based on disease input.
- Real source discovery is available.
- Fixed catalog is not the only source mechanism.
- Real sources can be fetched and parsed.
- Records include disease, date/time, location, counts, source URL, source type, evidence quote, and provenance.
- Duplicates and conflicts can be flagged.
- Validation explains what is compared with what.
- Human review is part of trust, not a failure.
- Outputs are understandable to public-health users.
