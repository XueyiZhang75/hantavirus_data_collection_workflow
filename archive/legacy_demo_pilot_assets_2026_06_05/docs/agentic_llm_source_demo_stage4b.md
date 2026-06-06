# Agentic LLM Source Demo - Stage 4B

## 1. Purpose

Stage 4B runs a controlled real-LLM demo for source planning and source critic only.

The goal is to prove that the optional Stage 4A agent hooks can call a configured model, capture advisory outputs in workflow state and source registry entries, and preserve deterministic guardrails.

## 2. What Is Enabled

When `--allow-llm` is passed, the demo enables:

- `HDC_ENABLE_LLM_SOURCE_PLANNING=true`
- `HDC_ENABLE_LLM_SOURCE_CRITIC=true`

This allows:

- the Source Planning Agent inside `query_strategy_builder`;
- the Source Critic Agent inside `source_critic_and_uncertainty_routing`.

## 3. What Remains Disabled

Stage 4B keeps these disabled:

- live fetch;
- LLM extraction;
- broad web search;
- automated crawling.

The script enforces:

- `HDC_ENABLE_LIVE_FETCH=false`
- `HDC_ENABLE_LLM_EXTRACTION=false`
- `HDC_USE_FIXTURE_DOCUMENTS=false`

## 4. How To Run

Dry run, no LLM call:

```powershell
python scripts/run_agentic_llm_source_demo.py --dry-run --scenario mv_hondius
```

MV Hondius with real LLM:

```powershell
python scripts/run_agentic_llm_source_demo.py --allow-llm --scenario mv_hondius --provider anthropic --model <model-name>
```

New Mexico HPS with real LLM:

```powershell
python scripts/run_agentic_llm_source_demo.py --allow-llm --scenario new_mexico_hps --provider anthropic --model <model-name>
```

Global hantavirus with real LLM:

```powershell
python scripts/run_agentic_llm_source_demo.py --allow-llm --scenario global_hantavirus --provider anthropic --model <model-name>
```

Without `--allow-llm`, the script refuses to call the model and exits safely.

## 5. Required Environment

Required model settings:

- `HDC_LLM_PROVIDER`
- `HDC_LLM_MODEL`

Provider API key must already be configured in the shell environment:

- `ANTHROPIC_API_KEY` for `HDC_LLM_PROVIDER=anthropic`
- `OPENAI_API_KEY` for `HDC_LLM_PROVIDER=openai`

Do not print API keys. The script reports provider and model only.

## 6. How To Inspect Outputs

Outputs are written to:

`outputs/agentic_llm_source_demo/<scenario>/`

Artifacts:

- `agentic_source_plan.json`
- `source_planning_agent_summary.json`
- `search_query_inventory.json`
- `source_registry_llm_critic.json`
- `source_routing_summary.json`
- `collection_trace.json`
- `agentic_demo_summary.json`
- `agentic_demo_report.md`

For a successful real run, a compact professor-package JSON summary is also written to:

`outputs/professor_demo_package/stage4b_agentic_llm_source_demo_results.json`

## 7. Guardrail Interpretation

LLM recommendations are advisory.

Deterministic policy still controls:

- `validation_reserved` source masking;
- context-only source routing;
- source readiness for fetch;
- extraction blocking for context-only sources;
- downstream schema/provenance behavior.

For the MV Hondius scenario, the script explicitly checks that:

- WHO DON600 remains `validation_reserved`;
- WHO is not ready for content fetch;
- VDH remains context-only when the overlay is active;
- Reuters is not treated as validation-reserved;
- Reuters semantic leakage risk is reported if the LLM flags it.

If the LLM does not flag Reuters semantic leakage, that is recorded as a model limitation and a human-review reason.

## 8. Limitations

Stage 4B does not collect real webpage data.

Limitations:

- no web search yet;
- no live fetch;
- no automated crawling;
- no extraction improvement is demonstrated;
- output quality depends on the selected model;
- agent outputs require human review;
- real data collection still needs separate approval.
