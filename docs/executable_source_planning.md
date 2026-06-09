# Executable Source Planning

## Purpose

`executable_source_planning` converts the source-planning step in the **data collection workflow** from advisory notes into an auditable source discovery plan.

The plan is executable in the sense that it contains source objectives, source category roles, provider channels, query types, and planned search query specifications. Stage 4 does not execute those queries, call search providers, fetch pages, or add LLM-proposed URLs to `source_candidates` or `source_registry`.

## Graph Position

Current graph order:

1. `task_intake_and_scope_planning`
2. `disease_intelligence_builder`
3. `profile_and_schema_setup`
4. `executable_source_planning`
5. `query_strategy_builder`
6. `source_discovery`

`query_strategy_builder` no longer calls the LLM source planner. It consumes the already-created `agentic_source_plan.planned_queries` and adds them to `search_query_inventory` with `query_source="executable_source_plan"` and `execution_status="planned_not_executed"`.

## Main State Outputs

- `agentic_source_plan`: full structured executable plan.
- `executable_source_plan_summary`: compact summary exported through final package `workflow_summaries`.
- `source_planning_agent_summary`: backward-compatible LLM/source-planning summary enriched with plan generation and fallback status.

## Plan Contents

The plan uses Pydantic models in `src/hdc_workflow/models.py`:

- `ExecutableSourcePlan`
- `SourceDiscoveryObjective`
- `PlannedSourceCategory`
- `PlannedSearchQuery`
- `SourcePlanningRisk`

Every planned query includes:

- `query_id`
- `query`
- `query_type`
- `provider_channel`
- `source_type`
- `role_hint`
- `priority`
- `expected_fields`
- `disease_terms_used`
- `location_terms_used`
- `time_terms_used`
- `rationale`
- `execution_status="planned_not_executed"`

Allowed source roles are:

- `collection`
- `validation`
- `context`
- `collection_support`
- `human_review`

Allowed source types are:

- `official_public_health_agency`
- `international_organization_report`
- `peer_reviewed_literature`
- `structured_database`
- `news_and_situation_report`

## Deterministic and LLM Paths

Default offline behavior is deterministic and does not require internet access, API keys, or real LLM calls.

When `HDC_ENABLE_LLM_SOURCE_PLANNING=true`, the node calls `llm_clients.run_pydantic_structured_llm` once with the `ExecutableSourcePlan` schema. Valid LLM output uses `generation_method="llm_executable_source_plan"`.

If the LLM call fails, the node returns a deterministic fallback plan with:

- `generation_method="llm_failed_deterministic_fallback"`
- `llm_enabled=true`
- warning `llm_source_planning_failed_deterministic_fallback_used`

LLM-proposed URLs inside planned query text are sanitized into search text. They are not added to `source_candidates`, `source_registry`, or fetch requests.

## Stage 4 Boundary

Implemented:

- Executable source discovery plan schema.
- Disease-aware deterministic planned queries.
- Optional one-call LLM executable source planning.
- Fallback to deterministic plan.
- URL sanitization for LLM planned query text.
- Plan summary export.
- Query strategy consumption of planned queries.

Not implemented:

- Real web search.
- Search provider integration.
- Search-result ingestion.
- Conversion of planned queries into source candidates.
- LLM-proposed source URL ingestion.
- Fetch/parse generalization.
- Validation refactor.
- Record model replacement.
