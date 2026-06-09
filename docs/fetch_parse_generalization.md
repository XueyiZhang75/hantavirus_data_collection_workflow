# Controlled Fetch and Parse Generalization

## 1. Purpose

Stage 7 lets the `data collection workflow` fetch and parse credible
search-derived sources under bounded, auditable controls. It extends the
existing `content_fetch_and_parse` node so search results discovered in Stage 5
and scored in Stage 6 can become real document and evidence inputs.

This stage does not replace the disease-specific structured record schema. For
non-hantavirus runs, parsed documents and evidence chunks may be available while
normalized records remain empty or limited until the later generic extraction
stage.

## 2. Inputs

The fetch/parse node consumes:

- `source_registry`: the current registry of seed and search-derived sources.
- `source_credibility_summary`: aggregate credibility and role statistics.
- `source_credibility_assessments`: per-source scores and final role decisions.
- `source_role_final`: final role used for fetch eligibility.
- `credibility_score` and `credibility_level`: thresholds for controlled fetch.
- `discovery_method`: distinguishes seed catalog, fixture search, and live
  search candidates.
- search provenance: `search_provider`, `query_id`, `query_used`,
  `planned_query_id`, `provider_channel`, and `role_hint`.
- `content_fetch` config: search-derived fetch flag, max source limits, score
  threshold, role allowlist, domain allowlist/blocklist, byte cap, parser flags,
  and fixture content map.

## 3. Outputs

The node and downstream evidence preparation now expose:

- `content_fetch_requests`: bounded fetch requests with source, search, and
  credibility provenance.
- `documents`: fetched or fixture-loaded documents with fetch status, parser
  status, parser used, content type, title, published date, text length, table
  count, quality fields, and provenance.
- `content_fetch_summary`: selected counts, skipped reason counts, parser
  counts, fetch status counts, role/domain controls, and source limits.
- `document_parse_summary`: parser status counts, parser used counts, content
  type counts, parsed/deferred/failed counts, text counts, table counts, and
  per-document parse metadata.
- `document_quality_summary`: quality status counts and document quality
  diagnostics.
- `fetch_manifest`: per-source selected/skipped manifest with reason fields.
- `evidence_chunks`: chunks prepared from parsed documents, preserving
  compatible source/search/credibility provenance fields.

## 4. Fetch Eligibility

Search-derived sources are eligible only when all configured gates pass:

- search-derived fetch is explicitly enabled.
- URL scheme is `http` or `https`.
- `source_role_final` is one of `collection`, `validation`,
  `collection_support`, or `context`.
- `source_role_final` is not `excluded`, `search_endpoint`, or
  `needs_human_review`.
- `credibility_score` is at or above `HDC_FETCH_MIN_CREDIBILITY_SCORE`.
- `credibility_level` is `high` or `medium`, unless needs-review fetch is
  explicitly allowed.
- `ready_for_content_fetch` is true.
- `final_screening_decision` is fetchable.
- `source_type` is present.
- domain is not blocklisted.
- domain is allowlisted when a domain allowlist is configured.
- max search-derived and max total fetch limits are not exceeded.

Skipped candidates are recorded with reasons such as
`search_derived_fetch_disabled`, `final_role_excluded`,
`final_role_search_endpoint`, `needs_review_not_allowed`,
`credibility_score_below_threshold`, `domain_not_allowlisted`,
`max_search_derived_sources_reached`, and `max_total_sources_reached`.

## 5. Parser Behavior

HTML parser:

- uses a deterministic standard-library parser.
- extracts title, headings, visible body text, meta description, common
  publication date meta tags, and simple tables.
- records `parser_used=html_stdlib_parser` and `parse_status=parsed_html`.

Text parser:

- supports `text/plain` and simple text-like responses.
- stores clean text and parser metadata without network-dependent behavior.

Table extraction:

- extracts simple HTML table rows as structured row/cell text.
- records `table_count` in documents and summaries.

PDF behavior:

- lazily attempts lightweight PDF parsing when enabled and dependencies are
  available.
- if parsing is unavailable, disabled, or fails, it records `parse_deferred` or
  `parse_failed` with a reason.
- no OCR is attempted.
- no browser automation or JavaScript rendering is attempted.

## 6. Safety Boundaries

Safety defaults and boundaries:

- live fetch is explicit opt-in.
- live search is explicit opt-in.
- search-derived fetch is explicit opt-in.
- max source limits and max byte limits are enforced.
- unsupported URL schemes are blocked.
- domain allowlists and blocklists are honored.
- no recursive crawl is implemented.
- no uncontrolled crawling is implemented.
- no paywall bypass is implemented.
- no browser or JavaScript rendering is implemented.
- no API keys or secrets are stored or printed.

## 7. What Changes After Stage 7

After Stage 7, credible discovered sources can move from search metadata into
fetched and parsed documents. Search-derived provenance is preserved from query
planning/search through documents and evidence chunks. COVID-19/New York and
dengue/Florida fixture runs can now produce parsed evidence inputs, even though
the disease-generic structured extraction model remains future work.

## 8. What Is Still Not Implemented

Stage 7 does not implement:

- disease-generic extraction record model.
- disease-generic structured extraction schema replacement.
- validation refactor.
- trusted-source validation overhaul.
- cross-source validation overhaul.
- duplicate/event clustering.
- anomaly detection.
- human review decision application.
- final product CLI.
- notebook or UI redesign.
- OCR.
- browser automation.
- JavaScript rendering.
