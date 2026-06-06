"""Run a controlled LLM source planning/source critic demo.

This script does not read .env, does not run live fetch, does not run broad web
search, and does not enable LLM extraction.

Safety overrides used during allowed LLM runs:
- HDC_ENABLE_LLM_SOURCE_PLANNING=true
- HDC_ENABLE_LLM_SOURCE_CRITIC=true
- HDC_ENABLE_LLM_EXTRACTION=false
- HDC_ENABLE_LIVE_FETCH=false
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from contextlib import contextmanager
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_SRC = _PROJECT_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from hdc_workflow.export import write_json  # noqa: E402
from hdc_workflow.graph import build_graph  # noqa: E402

_DEFAULT_OUTPUT_DIR = _PROJECT_ROOT / "outputs" / "agentic_llm_source_demo"
_PROFESSOR_RESULTS_PATH = (
    _PROJECT_ROOT
    / "outputs"
    / "professor_demo_package"
    / "stage4b_agentic_llm_source_demo_results.json"
)
_LIVE_CASE_DIR = _SRC / "hdc_workflow" / "resources" / "live_case_studies"
_MV_HONDIUS_SEED_OVERLAY = _LIVE_CASE_DIR / "mv_hondius_seed_sources.json"
_MV_HONDIUS_ROLE_OVERLAY = (
    _LIVE_CASE_DIR / "mv_hondius_source_role_policy_overlay.json"
)
_MV_HONDIUS_ALLOWLIST = ",".join(
    [
        "src_reuters_mv_hondius_2026_05_27",
        "src_vdh_hantavirus_mv_hondius_context",
        "src_who_don600_mv_hondius_2026",
    ]
)

_ENV_KEYS = [
    "HDC_ENABLE_LLM_SOURCE_PLANNING",
    "HDC_ENABLE_LLM_SOURCE_CRITIC",
    "HDC_ENABLE_LLM_EXTRACTION",
    "HDC_ENABLE_LIVE_FETCH",
    "HDC_USE_FIXTURE_DOCUMENTS",
    "HDC_COLLECTION_MODE",
    "HDC_SEED_SOURCE_OVERLAY_PATH",
    "HDC_SOURCE_ROLE_POLICY_OVERLAY_PATH",
    "HDC_SOURCE_ID_ALLOWLIST",
    "HDC_LLM_PROVIDER",
    "HDC_LLM_MODEL",
]


SCENARIOS = {
    "mv_hondius": {
        "scenario": "mv_hondius",
        "user_request": (
            "Plan and critique sources for a controlled hantavirus "
            "masked-validation pilot about the 2026 MV Hondius multi-country "
            "outbreak. Separate collection sources, context sources, and "
            "held-out validation sources. Pay attention to WHO-derived "
            "semantic leakage."
        ),
        "purpose": (
            "Show LLM source planning/critic behavior for the MV Hondius case "
            "while deterministic masking and context-only guardrails remain active."
        ),
        "env": {
            "HDC_COLLECTION_MODE": "masked_validation",
            "HDC_SEED_SOURCE_OVERLAY_PATH": str(_MV_HONDIUS_SEED_OVERLAY),
            "HDC_SOURCE_ROLE_POLICY_OVERLAY_PATH": str(_MV_HONDIUS_ROLE_OVERLAY),
            "HDC_SOURCE_ID_ALLOWLIST": _MV_HONDIUS_ALLOWLIST,
        },
    },
    "new_mexico_hps": {
        "scenario": "new_mexico_hps",
        "user_request": (
            "Plan sources for a hantavirus pulmonary syndrome data collection "
            "and validation pilot for New Mexico from 2024 to 2026. Identify "
            "possible collection, validation, and context source categories and "
            "queries. Do not fetch webpages."
        ),
        "purpose": (
            "Show LLM source planning for a New Mexico HPS pilot without adding "
            "new seed sources or fetching webpages."
        ),
        "env": {},
    },
    "global_hantavirus": {
        "scenario": "global_hantavirus",
        "user_request": (
            "Plan sources for global human hantavirus case, outbreak, and "
            "surveillance data collection from 2020 to 2026, including cases, "
            "deaths, dates, locations, source URLs, source types, and evidence "
            "quotes."
        ),
        "purpose": "Show general LLM source planning on the original global task.",
        "env": {},
    },
}


def _initial_state(user_request: str) -> dict:
    return {
        "user_request": user_request,
        "source_candidates": [],
        "source_discovery_summary": None,
        "source_registry": [],
        "source_registry_summary": None,
        "documents": [],
        "evidence_chunks": [],
        "raw_records": [],
        "validated_records": [],
        "normalized_records": [],
        "linked_events": [],
        "conflicts": [],
        "human_review_queue": [],
        "human_review_decisions": [],
        "collection_trace": [],
        "collection_spec": None,
        "disease_profile": None,
        "collection_schema": None,
        "source_strategy": None,
        "screening_criteria": None,
        "search_queries": None,
        "search_query_inventory": [],
        "agentic_source_plan": None,
        "source_planning_agent_summary": None,
        "content_fetch_requests": [],
        "content_fetch_summary": None,
        "fixture_document_summary": None,
        "document_quality_summary": None,
        "final_data_package": None,
        "current_route": None,
    }


@contextmanager
def _temporary_env(updates: dict[str, str]):
    original = {key: os.environ.get(key) for key in _ENV_KEYS}
    try:
        for key, value in updates.items():
            os.environ[key] = str(value)
        yield
    finally:
        for key, value in original.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def _scenario_env(args: argparse.Namespace) -> dict[str, str]:
    scenario = SCENARIOS[args.scenario]
    env = {
        "HDC_ENABLE_LLM_SOURCE_PLANNING": "true",
        "HDC_ENABLE_LLM_SOURCE_CRITIC": "true",
        "HDC_ENABLE_LLM_EXTRACTION": "false",
        "HDC_ENABLE_LIVE_FETCH": "false",
        "HDC_USE_FIXTURE_DOCUMENTS": "false",
        "HDC_COLLECTION_MODE": "masked_validation"
        if args.masked_validation
        else "standard",
    }
    env.update(scenario["env"])
    if args.provider:
        env["HDC_LLM_PROVIDER"] = args.provider
    if args.model:
        env["HDC_LLM_MODEL"] = args.model
    return env


def _safe_env_for_display(env: dict[str, str]) -> dict[str, str]:
    return {
        key: value
        for key, value in env.items()
        if "API_KEY" not in key and "TOKEN" not in key and "SECRET" not in key
    }


def _ascii_display(value) -> str:
    return str(value).encode("ascii", "backslashreplace").decode("ascii")


def _resolve_provider_model(env: dict[str, str]) -> tuple[str, str | None]:
    provider = env.get("HDC_LLM_PROVIDER") or os.environ.get("HDC_LLM_PROVIDER")
    model = env.get("HDC_LLM_MODEL") or os.environ.get("HDC_LLM_MODEL")
    return (provider or "anthropic", model or None)


def _api_key_present(provider: str) -> bool:
    if provider == "anthropic":
        return bool(os.environ.get("ANTHROPIC_API_KEY"))
    if provider == "openai":
        return bool(os.environ.get("OPENAI_API_KEY"))
    return False


def _registry_by_id(registry: list[dict]) -> dict[str, dict]:
    return {entry.get("source_id"): entry for entry in registry}


def _guardrail_checks(result: dict, scenario_name: str) -> dict:
    registry = list(result.get("source_registry") or [])
    by_id = _registry_by_id(registry)
    reserved = [
        entry
        for entry in registry
        if entry.get("source_role") == "validation_reserved"
        or "validation_reserved" in (entry.get("routing_flags") or [])
    ]
    reserved_ready = [
        entry.get("source_id")
        for entry in reserved
        if entry.get("ready_for_content_fetch") is True
    ]
    context_only = [
        entry
        for entry in registry
        if "context_only" in (entry.get("routing_flags") or [])
        or "blocked_from_structured_extraction" in (entry.get("routing_flags") or [])
    ]
    context_only_blocked = [
        entry.get("source_id")
        for entry in context_only
        if "blocked_from_structured_extraction" in (entry.get("routing_flags") or [])
    ]
    leakage_sources = [
        entry.get("source_id")
        for entry in registry
        if entry.get("llm_semantic_leakage_risk") is True
    ]
    human_review_sources = [
        entry.get("source_id")
        for entry in registry
        if entry.get("llm_needs_human_review") is True
    ]
    inventory = list(result.get("search_query_inventory") or [])
    agent_queries = [
        item
        for item in inventory
        if item.get("query_source") == "llm_source_planning_agent"
        or item.get("discovery_method") == "llm_source_planning_agent"
    ]
    checks = {
        "live_fetch_enabled": False,
        "llm_extraction_enabled": False,
        "llm_source_planning_enabled": bool(
            (result.get("source_planning_agent_summary") or {}).get(
                "llm_source_planning_enabled"
            )
        ),
        "llm_source_critic_enabled": bool(
            (result.get("source_routing_summary") or {}).get(
                "llm_source_critic_enabled"
            )
        ),
        "validation_reserved_source_ids_in_registry": [
            entry.get("source_id") for entry in reserved
        ],
        "validation_reserved_sources_ready_for_fetch": reserved_ready,
        "context_only_sources_with_blocked_from_structured_extraction": (
            context_only_blocked
        ),
        "llm_semantic_leakage_risk_source_ids": leakage_sources,
        "llm_semantic_leakage_risk_count": len(leakage_sources),
        "llm_human_review_recommended_source_ids": human_review_sources,
        "llm_human_review_recommended_count": len(human_review_sources),
        "agent_query_count": len(agent_queries),
        "rule_based_query_count": len(inventory) - len(agent_queries),
    }
    if scenario_name == "mv_hondius":
        who = by_id.get("src_who_don600_mv_hondius_2026") or {}
        vdh = by_id.get("src_vdh_hantavirus_mv_hondius_context") or {}
        reuters = by_id.get("src_reuters_mv_hondius_2026_05_27") or {}
        checks["mv_hondius"] = {
            "who_source_role": who.get("source_role"),
            "who_final_screening_decision": who.get("final_screening_decision"),
            "who_ready_for_content_fetch": who.get("ready_for_content_fetch"),
            "who_guardrail_passed": (
                who.get("source_role") == "validation_reserved"
                and who.get("ready_for_content_fetch") is False
            ),
            "vdh_source_role": vdh.get("source_role"),
            "vdh_final_screening_decision": vdh.get("final_screening_decision"),
            "vdh_context_only_guardrail_passed": (
                vdh.get("source_role") == "context_source"
                and "blocked_from_structured_extraction"
                in (vdh.get("routing_flags") or [])
            ),
            "reuters_source_role": reuters.get("source_role"),
            "reuters_is_validation_reserved": (
                reuters.get("source_role") == "validation_reserved"
            ),
            "reuters_semantic_leakage_flagged_by_llm": bool(
                reuters.get("llm_semantic_leakage_risk")
            ),
            "reuters_semantic_leakage_interpretation": (
                "LLM flagged Reuters semantic leakage risk."
                if reuters.get("llm_semantic_leakage_risk")
                else "LLM did not flag Reuters semantic leakage risk; treat as a model limitation and retain human review."
            ),
        }
    return checks


def _top_agent_queries(inventory: list[dict], limit: int = 10) -> list[dict]:
    agent_queries = [
        item
        for item in inventory
        if item.get("query_source") == "llm_source_planning_agent"
        or item.get("discovery_method") == "llm_source_planning_agent"
    ]
    return agent_queries[:limit]


def _source_planning_summary_with_diagnostics(result: dict) -> dict:
    plan_summary = dict(result.get("source_planning_agent_summary") or {})
    plan = result.get("agentic_source_plan") or {}
    if isinstance(plan, dict) and plan:
        for key in (
            "structured_output_attempted",
            "structured_output_mode",
            "retry_attempted",
            "retry_succeeded",
            "failure_type",
            "failure_message",
        ):
            if key in plan:
                plan_summary[key] = plan.get(key)
    else:
        failure_message = str(plan_summary.get("failure_message") or "")
        retry_failed = "Retry failed:" in failure_message
        plan_summary.setdefault("structured_output_attempted", True)
        plan_summary.setdefault("structured_output_mode", "unknown")
        plan_summary.setdefault("retry_attempted", retry_failed)
        plan_summary.setdefault("retry_succeeded", False)
    return plan_summary


def _report_markdown(
    scenario_name: str,
    scenario: dict,
    provider: str,
    model: str | None,
    result: dict,
    checks: dict,
) -> str:
    plan_summary = result.get("source_planning_agent_summary") or {}
    critic_summary = result.get("source_critic_summary") or {}
    routing_summary = result.get("source_routing_summary") or {}
    top_queries = _top_agent_queries(result.get("search_query_inventory") or [])
    leakage = checks.get("llm_semantic_leakage_risk_source_ids") or []
    human_review = checks.get("llm_human_review_recommended_source_ids") or []

    lines = [
        f"# Agentic LLM Source Demo - {scenario_name}",
        "",
        "## Scenario",
        "",
        f"- Scenario: `{scenario_name}`",
        f"- Purpose: {scenario.get('purpose')}",
        f"- Provider: `{provider}`",
        f"- Model: `{model or 'not configured'}`",
        "- Live fetch disabled: `true`",
        "- LLM extraction disabled: `true`",
        "",
        "## Source Planning Summary",
        "",
        f"- Status: `{plan_summary.get('status')}`",
        f"- Agent query count: `{plan_summary.get('agent_query_count', 0)}`",
        f"- Agent query added count: `{plan_summary.get('agent_query_added_count', 0)}`",
        f"- Candidate hint count: `{plan_summary.get('agent_candidate_hint_count', 0)}`",
        f"- Structured output mode: `{plan_summary.get('structured_output_mode', 'unknown')}`",
        f"- Retry attempted: `{plan_summary.get('retry_attempted', False)}`",
        f"- Retry succeeded: `{plan_summary.get('retry_succeeded', False)}`",
        "",
        "## Top Agent-Proposed Queries",
        "",
    ]
    if top_queries:
        for item in top_queries:
            lines.append(f"- `{item.get('query')}`")
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Source Critic Summary",
            "",
            f"- LLM source critic enabled: `{critic_summary.get('llm_source_critic_enabled')}`",
            f"- Assessed source count: `{critic_summary.get('llm_assessed_source_count', 0)}`",
            f"- Semantic leakage count: `{critic_summary.get('llm_semantic_leakage_count', 0)}`",
            f"- Human review recommended count: `{critic_summary.get('llm_human_review_recommended_count', 0)}`",
            "",
            "## Sources Flagged For Semantic Leakage",
            "",
        ]
    )
    if leakage:
        for source_id in leakage:
            lines.append(f"- `{source_id}`")
    else:
        lines.append("- none")

    lines.extend(["", "## Sources Flagged For Human Review", ""])
    if human_review:
        for source_id in human_review:
            lines.append(f"- `{source_id}`")
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Guardrail Proof",
            "",
            f"- Validation-reserved ready for fetch: `{checks.get('validation_reserved_sources_ready_for_fetch')}`",
            f"- Context-only blocked source IDs: `{checks.get('context_only_sources_with_blocked_from_structured_extraction')}`",
            f"- Final decision counts: `{(routing_summary.get('final_decision_counts') or {})}`",
            "",
            "## Limitations",
            "",
            "- This demo does not fetch live webpages.",
            "- This demo does not run broad web search.",
            "- This demo does not run LLM extraction.",
            "- Agent outputs are advisory and require human review.",
        ]
    )
    return "\n".join(lines) + "\n"


def _write_outputs(
    output_dir: Path,
    scenario_name: str,
    scenario: dict,
    provider: str,
    model: str | None,
    result: dict,
    checks: dict,
) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    registry = list(result.get("source_registry") or [])
    plan_summary = _source_planning_summary_with_diagnostics(result)
    report_result = dict(result)
    report_result["source_planning_agent_summary"] = plan_summary
    summary = {
        "scenario": scenario_name,
        "provider": provider,
        "model": model,
        "live_fetch_enabled": False,
        "llm_extraction_enabled": False,
        "source_planning_agent_summary": plan_summary,
        "source_critic_summary": result.get("source_critic_summary") or {},
        "source_routing_summary": result.get("source_routing_summary") or {},
        "guardrail_checks": checks,
        "output_dir": str(output_dir),
    }

    paths = {
        "agentic_source_plan": write_json(
            result.get("agentic_source_plan") or {},
            output_dir / "agentic_source_plan.json",
        ),
        "source_planning_agent_summary": write_json(
            plan_summary,
            output_dir / "source_planning_agent_summary.json",
        ),
        "search_query_inventory": write_json(
            result.get("search_query_inventory") or [],
            output_dir / "search_query_inventory.json",
        ),
        "source_registry_llm_critic": write_json(
            registry,
            output_dir / "source_registry_llm_critic.json",
        ),
        "source_routing_summary": write_json(
            result.get("source_routing_summary") or {},
            output_dir / "source_routing_summary.json",
        ),
        "collection_trace": write_json(
            result.get("collection_trace") or [],
            output_dir / "collection_trace.json",
        ),
        "agentic_demo_summary": write_json(
            summary,
            output_dir / "agentic_demo_summary.json",
        ),
    }
    report = _report_markdown(
        scenario_name, scenario, provider, model, report_result, checks
    )
    report_path = output_dir / "agentic_demo_report.md"
    report_path.write_text(report, encoding="utf-8")
    paths["agentic_demo_report"] = report_path
    summary["artifact_paths"] = {key: str(path) for key, path in paths.items()}
    write_json(summary, output_dir / "agentic_demo_summary.json")
    return summary


def _print_dry_run(args: argparse.Namespace, env: dict[str, str]) -> None:
    provider, model = _resolve_provider_model(env)
    print("=" * 72)
    print("Agentic LLM source demo dry run only. No LLM will be called.")
    print(f"scenario: {args.scenario}")
    print(f"provider: {provider}")
    print(f"model: {model or 'not configured'}")
    print(f"output_dir: {_ascii_display(Path(args.output_dir) / args.scenario)}")
    print("planned_env:")
    print(json.dumps(_safe_env_for_display(env), indent=2, sort_keys=True))
    print("=" * 72)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Controlled real-LLM source planning/source critic demo."
    )
    parser.add_argument("--allow-llm", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--scenario",
        choices=sorted(SCENARIOS.keys()),
        default="mv_hondius",
    )
    parser.add_argument("--output-dir", default=str(_DEFAULT_OUTPUT_DIR))
    parser.add_argument("--masked-validation", action="store_true")
    parser.add_argument("--provider")
    parser.add_argument("--model")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    scenario = SCENARIOS[args.scenario]
    env = _scenario_env(args)
    provider, model = _resolve_provider_model(env)

    if args.dry_run:
        _print_dry_run(args, env)
        return 0

    if not args.allow_llm:
        print(
            "Refusing to call LLM. Pass --allow-llm to run the controlled "
            "source planning/source critic demo, or use --dry-run to inspect "
            "the configuration.",
            file=sys.stderr,
        )
        return 2

    if not model:
        print(
            "Refusing to call LLM because HDC_LLM_MODEL is not configured. "
            "Pass --model or set HDC_LLM_MODEL in the shell environment.",
            file=sys.stderr,
        )
        return 3

    if not _api_key_present(provider):
        print(
            f"Refusing to call LLM because the API key for provider '{provider}' "
            "is not configured in the shell environment.",
            file=sys.stderr,
        )
        return 4

    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = _PROJECT_ROOT / output_dir
    scenario_output_dir = output_dir / args.scenario

    with _temporary_env(env):
        result = build_graph().invoke(_initial_state(scenario["user_request"]))

    checks = _guardrail_checks(result, args.scenario)
    summary = _write_outputs(
        scenario_output_dir,
        args.scenario,
        scenario,
        provider,
        model,
        result,
        checks,
    )
    write_json(summary, _PROFESSOR_RESULTS_PATH)

    print("=" * 72)
    print("Agentic LLM source demo completed.")
    print(f"scenario: {args.scenario}")
    print(f"provider: {provider}")
    print(f"model: {model}")
    print(f"output_dir: {_ascii_display(scenario_output_dir)}")
    print(f"agent_query_count: {checks.get('agent_query_count')}")
    print(
        "llm_semantic_leakage_risk_count:",
        checks.get("llm_semantic_leakage_risk_count"),
    )
    print(
        "llm_human_review_recommended_count:",
        checks.get("llm_human_review_recommended_count"),
    )
    print("live_fetch_enabled: False")
    print("llm_extraction_enabled: False")
    print("artifact_count:", len(summary.get("artifact_paths") or {}))
    print("=" * 72)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
