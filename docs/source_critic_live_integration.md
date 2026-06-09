# Source Critic Live Integration

This document describes how the data collection workflow integrates the LLM source critic with live-search-derived source candidates.

## Purpose

The source critic is an advisory LLM stage that reviews source metadata before content fetch. It is designed to reduce unsafe or off-task fetches from live search results, especially when a search provider returns pages that match the query text but are not actually about the active disease, geography, or data task.

The source critic does not browse, fetch, search, or invent URLs. It only reviews source metadata already present in the workflow state.

## Candidate Selection

When `HDC_ENABLE_LLM_SOURCE_CRITIC=true`, the workflow selects source critic candidates before calling the model.

Default selection behavior:

- Empty `HDC_LLM_SOURCE_CRITIC_SOURCE_ID_ALLOWLIST` means no explicit critic allowlist.
- Live-search-derived sources are prioritized first.
- Fixture-search-derived sources are prioritized after live search sources.
- Seed catalog sources can still be reviewed if capacity remains.
- Search endpoints and placeholder sources are skipped unless explicitly allowlisted.
- `HDC_LLM_SOURCE_CRITIC_MAX_SOURCES` caps the number of LLM critic calls.

Explicit allowlist behavior:

- A non-empty `HDC_LLM_SOURCE_CRITIC_SOURCE_ID_ALLOWLIST` restricts critic calls to those source IDs.
- Sources outside that allowlist are marked skipped with reason `source_not_in_explicit_critic_allowlist`.

## Critic Output

Each assessed source receives source registry fields including:

- `llm_source_critic_attempted`
- `llm_source_critic_assessed`
- `llm_source_critic_status`
- `llm_source_critic_decision`
- `llm_source_critic_confidence`
- `llm_source_critic_reason`
- `llm_source_critic_risk_flags`
- `llm_source_critic_recommended_role`
- `llm_source_critic_fetch_recommendation`
- `llm_source_critic_review_required`
- `llm_source_critic_block_fetch`
- `blocked_from_fetch`
- `blocked_from_fetch_reason`

Skipped and failed calls are also recorded in the source registry so every source has an auditable critic status.

## Fetch Blocking

The critic can block content fetch when it identifies high-risk outcomes such as:

- disease mismatch
- source not about the active task
- outside task scope
- no extractable data for collection
- fetch should happen only after human review

When blocked, the source registry records:

- `ready_for_content_fetch=false`
- `blocked_from_fetch=true`
- `blocked_from_fetch_reason`

The workflow also creates a human review item with `item_type=source_critic_blocked_source`.

## Summary Artifacts

The workflow state now includes:

- `source_critic_summary`
- `source_critic_results`

Configured runner sessions export:

- `diagnostics/source_critic_summary.json`
- `diagnostics/source_critic_results.json`

The summary includes:

- attempted, assessed, skipped, and failed source counts
- blocked fetch count
- review-required count
- allowed fetch count
- context-only count
- decision counts
- fetch recommendation counts
- risk flag counts
- candidate selection summary
- skipped reason counts

## Configuration Notes

In `configs/hdc_workflow_run_config.jsonc`:

- `llm.source_critic.max_sources` controls critic call count.
- `llm.source_critic.review_blocks_fetch` controls whether review/block recommendations can prevent fetch.
- `source_sets.llm_source_critic_source_ids=[]` means no explicit critic allowlist.

This is workflow functionality, not a one-off demo branch.
