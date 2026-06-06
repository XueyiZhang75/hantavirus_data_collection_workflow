# Agentic LLM Upgrade - Stage 4A

## 1. Purpose

Stage 4A upgrades selected existing workflow nodes with optional LLM/agent behavior while keeping the LangGraph topology unchanged.

The new behavior is advisory and feature-flagged. The rule-based workflow remains the default path.

## 2. Why this is needed

The existing workflow is stable and reproducible, but source planning and source criticism are mostly static and rule-based. That is useful for safety, yet it makes the system look less agentic when explaining how it adapts to a new public-health collection task.

Stage 4A adds an optional reasoning layer for:

- source strategy recommendations;
- proposed search queries;
- source role critique;
- credibility assessment;
- semantic leakage review;
- human review recommendations.

This does not add broad web search.

## 3. Hybrid architecture

The design separates advisory reasoning from deterministic enforcement.

LLM agents make proposals and explanations:

- `source_planning_agent` proposes source categories, search queries, validation/context separation, candidate hints, warnings, and human review needs.
- `source_critic_agent` proposes credibility, source role, screening decision, semantic leakage risk, context-only risk, validation-candidate risk, and human review need.

Deterministic guardrails enforce hard policy:

- `validation_reserved` sources are blocked from collection.
- `context_only` sources can be fetched for context but cannot produce structured records.
- schema validation, provenance checks, normalization, linking, evaluation, and final packaging stay deterministic by default.
- optional LLM extraction remains separate behind `HDC_ENABLE_LLM_EXTRACTION`.

LLM output is advisory. It cannot override source masking or context-only blocking.

## 4. Nodes upgraded in this stage

`query_strategy_builder` / source planning:

- calls the optional Source Planning Agent only when `HDC_ENABLE_LLM_SOURCE_PLANNING=true`;
- stores output in `agentic_source_plan`;
- stores node summary in `source_planning_agent_summary`;
- appends agent-proposed queries to `search_query_inventory` with `query_source=llm_source_planning_agent`;
- preserves all deterministic rule-based queries.

`source_critic_and_uncertainty_routing` / source critic:

- calls the optional Source Critic Agent only when `HDC_ENABLE_LLM_SOURCE_CRITIC=true`;
- stores advisory fields on each source registry entry;
- can route non-guarded sources to human review when the LLM recommends it;
- still applies validation-reserved and context-only deterministic overrides after LLM assessment.

## 5. Nodes not changed in this stage

Stage 4A does not change:

- graph topology;
- node names or ordering;
- content fetch behavior;
- evidence chunking behavior;
- extraction behavior, except for the pre-existing optional LLM extraction path;
- normalization;
- linking;
- evaluation;
- final package export.

`src/hdc_workflow/graph.py` was not modified.

## 6. Feature flags

New flags:

- `HDC_ENABLE_LLM_SOURCE_PLANNING`: default off; enables the Source Planning Agent.
- `HDC_ENABLE_LLM_SOURCE_CRITIC`: default off; enables the Source Critic Agent.

Existing LLM flags/settings:

- `HDC_ENABLE_LLM_EXTRACTION`: default off; controls optional structured extraction LLM path.
- `HDC_LLM_PROVIDER`: defaults to `anthropic`.
- `HDC_LLM_MODEL`: required only when a real LLM flag is enabled.

Provider API keys are read only by the lazy LLM helper when a real LLM call is explicitly enabled. Tests mock the central helper.

## 7. Safety and reproducibility

Safety properties:

- all LLM flags default off;
- tests do not call real LLM APIs;
- no API keys are printed;
- no `.env` file is read by the new agents;
- no live fetch is run by this stage;
- no broad web search is implemented;
- deterministic source masking remains authoritative;
- deterministic context-only extraction guardrail remains authoritative;
- malformed LLM output falls back to rule-based behavior.

## 8. Next stages

Recommended next stages:

- Stage 4B: controlled LLM source planning and source critic demo on a real hantavirus scenario.
- Stage 4C: LLM extraction pass after source selection is stable.
- Stage 4D: validation explanation agent for professor-facing interpretation.

Do not start real LLM demos without explicit approval, model selection, and API key configuration.
