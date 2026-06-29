# Source Identity, Publisher, and Credibility

## 1. Purpose

This document describes the source identity layer in the data collection workflow. Its job is to distinguish the search provider that found a URL from the real publisher or owner of the target page, then pass that identity into credibility, routing, claim corroboration, and exports.

## 2. Why this was needed

Live search providers can return a metadata field named `source`. In Tavily results, that value may be `Tavily` or another search-metadata label. That label is not necessarily the publisher of the webpage. Treating it as publisher causes misleading source registry rows, inflated trust, and weak claim independence checks.

The workflow now preserves search metadata separately:

- `search_provider`: the tool used for search, such as `tavily`.
- `search_result_source_raw`: the raw source label returned by the provider.
- `actual_publisher`: the organization assessed as publishing the page.
- `source_owner`: the organization responsible for the source when inferable.

## 3. Source Identity Fields

The main source identity fields are stored on registry entries and assessment files:

- `actual_publisher`, `actual_publisher_normalized`, `actual_publisher_confidence`
- `publisher_evidence_fields`, `publisher_evidence_quotes`, `publisher_source`
- `source_owner`, `source_owner_confidence`
- `source_type_llm`, `source_type_final`, `source_type_confidence`, `source_type_evidence`
- `claim_support_role`
- `recommended_source_role`, `recommended_fetch_use`, `recommended_extraction_use`
- `credibility_level_llm`, `credibility_rationale`, `trust_basis`
- `source_independence_group`, `independence_confidence`
- `likely_syndicated_or_aggregated`, `upstream_source_mentions`
- `source_identity_status`, `source_identity_warnings`, `source_identity_errors`

Allowed source type and usage values are intentionally coarse. The goal is not automatic truth determination; it is safer publisher identity and source-role routing.

## 4. LLM Source Identity Assessment

The optional LLM source identity agent is controlled by:

- `HDC_ENABLE_LLM_SOURCE_IDENTITY`
- `HDC_LLM_SOURCE_IDENTITY_MAX_SOURCES`
- `HDC_LLM_SOURCE_IDENTITY_POST_FETCH`
- `HDC_LLM_SOURCE_IDENTITY_REQUIRE_LLM`
- `HDC_LLM_SOURCE_IDENTITY_ALLOW_DETERMINISTIC_FALLBACK`

The prompt forbids browsing, fetching, searching, or inventing publisher facts. The model can only inspect source metadata and already fetched page snippets supplied by the workflow.

If `require_llm=true` and the model is unavailable while deterministic fallback is disabled, the assessment records `source_identity_status=blocked_llm_required`. It does not pretend that the LLM assessment succeeded.

## 5. Pre-Fetch and Post-Fetch Identity

Pre-fetch assessment uses:

- URL and domain
- title and snippet
- raw search metadata
- query and discovery provenance

Post-fetch enrichment uses only already fetched document fields:

- final/canonical URL
- HTTP and parse status
- page title
- metadata/site hints when available
- clean text excerpt

Post-fetch enrichment can correct the publisher when the fetched page gives stronger evidence. If search metadata and page metadata conflict, the workflow records warning flags instead of silently overwriting provenance.

## 6. Interaction With Credibility and Claims

Source identity is applied before source credibility scoring and final routing. It can conservatively block search endpoints from fetch/extraction and route social media sources to review.

Claim corroboration now prefers:

1. `source_independence_group`
2. `actual_publisher_normalized`
3. `actual_publisher`
4. URL/source fallback

This prevents two syndicated or aggregated sources that point to the same upstream publisher from being counted as independent corroboration.

## 7. Outputs

The workflow writes source identity outputs in both diagnostics and the final collection package:

- `diagnostics/source_identity_assessments.json`
- `diagnostics/source_identity_summary.json`
- `collection/source_identity_assessments.json`
- `collection/source_identity_assessments.csv`
- `collection/source_identity_summary.json`

The workflow run summary and HTML console also include source identity summary counts.

## 8. Safety Boundaries

This layer does not:

- determine whether a public-health claim is true
- bypass paywalls, OCR scanned PDFs, or browser-only pages
- run additional search
- fetch pages outside the content fetch node
- store or print API keys
- replace validation or human review

It only improves publisher/source identity and routes that information through the existing workflow.

## 9. Limitations

Publisher identity can remain unknown when metadata is weak and the page does not expose clear publisher text. LLM judgments are advisory and must be interpreted with recorded warnings, evidence fields, and confidence levels. This optimization does not redesign validation logic, observation-type dataset splitting, or the final readable report format.
