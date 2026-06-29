# LLM-Led Iterative Source Discovery

## 1. Purpose

This optimization upgrades source discovery in the data collection workflow from one-shot first-N query execution into a bounded LLM-led search/observe/refine loop.

The goal is not to let the LLM browse or fetch pages. The LLM decides what query batch should be searched next, then the workflow executes those queries through the configured search provider and records every decision.

## 2. Why this was needed

The Virginia hantavirus live run showed limited source coverage. The previous source discovery path generated planned queries, executed only the first small batch, skipped the rest after max query limits were reached, and did not ask the LLM to observe returned results before deciding what to search next.

Users can input arbitrary disease, location, and time-window tasks. A fixed first-N search path is too brittle for that product shape. The LLM should decide search direction dynamically while the workflow enforces deterministic safety bounds.

## 3. Iterative loop

The loop is:

1. PLAN: the LLM proposes a bounded query batch for the current task.
2. SEARCH: the workflow executes the query batch through the configured search provider.
3. OBSERVE: the workflow summarizes search metadata, including result titles, snippets, URLs/domains, ranks, accepted candidates, duplicates, rejected results, and gaps.
4. REFINE: the LLM decides whether to continue and proposes follow-up queries, or stops with a reason.
5. STOP: the workflow stops when the LLM stops, limits are reached, or progress is blocked.

## 4. LLM responsibilities

The LLM is responsible for:

- deciding query text
- considering local language and disease terminology when relevant
- deciding what source types or evidence patterns are needed
- assessing whether returned search metadata is sufficient
- proposing follow-up queries from observed gaps
- stopping with a clear decision and reason

The LLM does not browse, fetch webpages, insert source candidates, or determine truth.

## 5. Workflow responsibilities

The workflow is responsible for:

- enforcing bounded iterations, query counts, and result counts
- executing the search provider
- validating and canonicalizing provider-returned URLs
- deduplicating source candidates
- exporting provenance and diagnostics
- preventing direct URL ingestion from LLM output
- preserving downstream source critic, disease relevance, content fetch, extraction, corroboration, and quality gates

## 6. Outputs

The iterative source discovery path exports:

- `iterative_source_discovery_summary`
- `search_iteration_plans`
- `search_iteration_observations`
- `search_refinement_decisions`
- `iterative_search_queries`

The configured runner writes these artifacts under each run session's `diagnostics/` directory.

## 7. Safety boundaries

This optimization keeps these boundaries:

- no crawling
- no recursive browsing
- no webpage fetch inside the LLM planning loop
- no direct LLM URL ingestion into source candidates
- no API keys in configs
- no API key printing
- no automatic truth determination

Only search provider results can become source candidates.

## 8. Limitations

Live search provider index coverage can still limit results. LLM planning may still miss useful sources. The downstream source critic, content fetch, extraction, disease relevance gates, claim corroboration, and quality gates remain necessary.

This optimization does not overhaul source identity or publisher extraction. It does not create the final_case_dataset / zero_case / exposure_monitoring split. It does not redesign interpretive human-readable reports, build a human review UI, or add workflow visualization.
