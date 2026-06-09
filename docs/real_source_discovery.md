# Real Source Discovery

## 1. Purpose

Stage 5 lets the **data collection workflow** execute planned queries from
`agentic_source_plan` through a controlled search provider layer. Search
results become source candidates beyond the fixed seed catalog, while the
fixed catalog remains available as a seed, fallback, fixture, and guardrail.

The search provider returns result metadata only. It does not fetch discovered
webpages, crawl recursively, parse PDFs, or ingest arbitrary URLs as document
content.

## 2. Inputs

Real source discovery consumes the upstream workflow state:

- structured task: disease, location, time window, target fields, and user request
- disease intelligence: aliases, abbreviations, reporting terms, and source hints
- profile/schema/source strategy: expected source categories and extractable fields
- executable source plan: `agentic_source_plan`
- planned queries: `agentic_source_plan.planned_queries`
- source search config: `source_search` in the runtime config or equivalent env vars

## 3. Outputs

Stage 5 adds or enriches these outputs:

- `source_search_execution_summary`: query selection, provider status, limits,
  result counts, rejection reasons, warnings, and search-derived source IDs
- `source_search_results`: normalized search result manifest with accepted or
  rejected status for each result
- search-derived `source_candidates`: candidates with query/provider/URL
  provenance and `discovery_method` set to `fixture_search_result` or
  `live_search_result`
- enriched `source_discovery_summary`: discovery method, search mode, provider,
  seed count, search candidate count, raw result count, and rejected result count
- `source_registry` entries after `source_dedup_and_registry`, preserving search
  provenance fields such as `query_id`, `query_used`, `search_provider`,
  `search_rank`, `provider_channel`, `planned_query_id`, `canonical_url`, and
  `domain`

## 4. Modes

`disabled` / offline seed catalog:

- Default safe mode.
- No provider call, no internet, no API key.
- Source candidates come from the existing seed catalog.
- Discovery method remains `offline_seed_catalog`.

`fixture` search:

- Executes planned queries against local JSON fixture results.
- Used by tests and offline smoke runs.
- Produces `fixture_search_result` candidates.
- Can combine fixture search candidates with seed catalog candidates.

`live` search:

- Explicitly enabled only.
- Executes bounded planned queries through a real provider adapter.
- Current live adapter: Tavily.
- Produces `live_search_result` candidates only when provider credentials and
  network access allow successful search responses.
- Does not fetch page bodies. Downstream `content_fetch_and_parse` may fetch
  screened sources later only if live fetch is separately enabled.

Seed catalog plus search combined mode:

- Controlled by `source_search.combine_with_seed_catalog`.
- `true` keeps seed candidates plus search-derived candidates.
- `false` returns only search-derived candidates when search is enabled.

## 5. Provider Configuration

Runtime config block:

```json
"source_search": {
  "enabled": false,
  "mode": "disabled",
  "provider": "tavily",
  "fixture_path": "src/hdc_workflow/resources/search_fixtures/example_search_results.json",
  "max_queries": 3,
  "max_results_per_query": 5,
  "max_total_results": 15,
  "timeout_seconds": 15,
  "combine_with_seed_catalog": true,
  "cache_enabled": true,
  "provider_channel_allowlist": [
    "web_search",
    "official_site_search",
    "news_search",
    "literature_api",
    "database_search"
  ]
}
```

Environment variables:

- `HDC_ENABLE_LIVE_SEARCH`
- `HDC_SEARCH_MODE`
- `HDC_SEARCH_PROVIDER`
- `HDC_SEARCH_FIXTURE_PATH`
- `HDC_SEARCH_MAX_QUERIES`
- `HDC_SEARCH_MAX_RESULTS_PER_QUERY`
- `HDC_SEARCH_MAX_TOTAL_RESULTS`
- `HDC_SEARCH_TIMEOUT_SECONDS`
- `HDC_SEARCH_COMBINE_WITH_SEED_CATALOG`
- `HDC_SEARCH_CACHE_ENABLED`
- `HDC_SEARCH_PROVIDER_CHANNEL_ALLOWLIST`

Supported provider key variables:

- `TAVILY_API_KEY`
- `BRAVE_SEARCH_API_KEY`
- `SERPAPI_API_KEY`
- `BING_SEARCH_V7_SUBSCRIPTION_KEY`

The Stage 5 live adapter currently implements Tavily. Other key variables are
documented for future provider adapters. API keys must stay in environment
variables and must not be stored in config files.

## 6. Safety Boundaries

- Live search is disabled by default.
- Tests use fixtures or mocks and do not require internet, API keys, live web,
  or real LLM calls.
- Query execution is bounded by `max_queries`, `max_results_per_query`, and
  `max_total_results`.
- Provider channels are limited by `provider_channel_allowlist`.
- `manual_user_url` is intentionally excluded from the default allowlist.
- Search execution rejects empty queries, non-planned queries, raw URL-only
  queries, unsupported provider channels, and queries beyond limits.
- Search result URLs accept only `http` and `https`.
- `javascript:`, `file:`, `data:`, `mailto:`, `ftp:`, `seed:`, missing URLs,
  invalid URLs, duplicate URLs, and empty title/snippet results are rejected
  with auditable rejection reasons.
- API keys are never printed by provider code or config display.

## 7. What Changes After Stage 5

Before Stage 5, `agentic_source_plan.planned_queries` were auditable but always
`planned_not_executed`, and source candidates came only from the fixed catalog.

After Stage 5:

- planned queries can execute when source search is explicitly enabled
- fixture search can prove search ingestion offline
- live search can discover source candidates when provider credentials are
  available
- fixed catalogs are no longer the only source mechanism
- COVID-19 and dengue fixture runs discover disease-specific candidate sources
  based on their planned queries

## 8. What Is Still Not Implemented

- Source credibility scoring overhaul is not implemented yet.
- LLM source credibility overhaul is not implemented yet.
- Fetch/parse generalization is not implemented yet.
- PDF parsing/OCR is not implemented yet.
- Disease-generic extraction record model is not implemented yet.
- Validation refactor is not implemented yet.
- Duplicate/event clustering is not implemented yet.
- Anomaly detection is not implemented yet.
- Human review decision application is not implemented yet.
- CLI/notebook/UI redesign is not implemented yet.
