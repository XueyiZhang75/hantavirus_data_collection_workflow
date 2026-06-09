"""Interactive real-run entrypoint for the data collection workflow."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(PROJECT_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from hdc_workflow.runtime_profile import (  # noqa: E402
    DEFAULT_MODEL,
    DEFAULT_PROVIDER,
    default_workflow_run_config,
)
from run_hdc_workflow_configured import run_workflow  # noqa: E402


DEFAULT_TARGET_FIELDS = [
    "disease",
    "country",
    "subnational_location",
    "locality",
    "date_reported",
    "cases_confirmed",
    "cases_probable",
    "cases_suspected",
    "cases_unspecified",
    "deaths",
    "hospitalizations",
    "source_url",
    "source_type",
    "evidence_quote",
]

LLM_KEY_BY_PROVIDER = {
    "anthropic": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
}


def _slug(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", value.strip().lower()).strip("_")
    return cleaned or "workflow_run"


def _session_id(disease: str, location: str, start_date: str, end_date: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_utc")
    return f"{_slug(disease)}_{_slug(location)}_{_slug(start_date)}_{_slug(end_date)}_{stamp}"


def _normalize_session_id(value: str, default: str) -> str:
    raw = value.strip()
    if not raw or raw in {"?", "？"}:
        return default
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", raw).strip("._-")
    return cleaned or default


def _normalize_dates(start_date: str, end_date: str) -> tuple[str, str, str | None]:
    start = start_date.strip()
    end = end_date.strip()
    match = re.fullmatch(r"(\d{4})\s*[-–—]\s*(\d{4})", start)
    if match:
        inferred_start, inferred_end = match.groups()
        if not end or end == inferred_end:
            return (
                inferred_start,
                inferred_end,
                f"Interpreted Start year/date '{start}' as date range {inferred_start} to {inferred_end}.",
            )
    return start, end, None


def _prompt(label: str, current: str | None = None) -> str:
    suffix = f" [{current}]" if current else ""
    value = input(f"{label}{suffix}: ").strip()
    return value or (current or "")


def _env_present(name: str) -> bool:
    return bool(os.environ.get(name))


def _provider_key_name(provider: str) -> str:
    return LLM_KEY_BY_PROVIDER.get(provider.strip().lower(), f"{provider.upper()}_API_KEY")


def _require_keys(*, provider: str, llm_enabled: bool) -> list[str]:
    missing: list[str] = []
    if not _env_present("TAVILY_API_KEY"):
        missing.append("TAVILY_API_KEY")
    if llm_enabled:
        llm_key = _provider_key_name(provider)
        if not _env_present(llm_key):
            missing.append(llm_key)
    return missing


def _real_run_config(
    *,
    disease: str,
    location: str,
    start_date: str,
    end_date: str,
    target_fields: list[str],
    session_id: str,
    provider: str,
    model: str,
    output_dir: str | None,
    no_llm: bool,
) -> dict:
    config = deepcopy(default_workflow_run_config())
    user_request = (
        f"Collect {disease} cases, deaths, dates, locations, source URLs, "
        f"source types, and evidence quotes for {location} from {start_date} to {end_date}."
    )

    config["profile_name"] = f"{_slug(disease)}_{_slug(location)}_{start_date}_{end_date}_real_workflow"
    config["description"] = (
        "Interactive real data collection workflow run. Live search, live fetch, "
        "and LLM stages are enabled by default; API keys are read from environment variables."
    )
    config["workflow"] = {
        "collection_mode": "standard",
        "use_fixture_documents": False,
    }
    config["user_request"] = user_request
    config["structured_task"] = {
        "disease": disease,
        "location": location,
        "start_date": start_date,
        "end_date": end_date,
        "target_fields": target_fields,
        "source_preferences": [
            "official_public_health_agency",
            "international_organization_report",
            "structured_database",
            "peer_reviewed_literature",
            "news_and_situation_report",
        ],
        "collection_mode": "standard",
        "user_request": user_request,
        "run_label": session_id,
    }
    config["live_web"] = {
        "enabled": True,
        "timeout_seconds": 30,
    }
    config["source_search"] = {
        "enabled": True,
        "mode": "live",
        "provider": "tavily",
        "fixture_path": "src/hdc_workflow/resources/search_fixtures/example_search_results.json",
        "max_queries": 3,
        "max_results_per_query": 5,
        "max_total_results": 15,
        "timeout_seconds": 20,
        "combine_with_seed_catalog": False,
        "cache_enabled": True,
        "provider_channel_allowlist": [
            "web_search",
            "official_site_search",
            "news_search",
            "literature_api",
            "database_search",
        ],
    }
    config["content_fetch"] = {
        "fetch_search_derived_sources": True,
        "max_search_derived_sources": 5,
        "max_total_sources": 8,
        "min_credibility_score": 0.55,
        "allowed_final_roles": [
            "collection",
            "validation",
            "collection_support",
            "context",
        ],
        "allow_needs_review": False,
        "domain_allowlist": [],
        "domain_blocklist": [],
        "max_bytes": 1_000_000,
        "parse_pdf_text": True,
        "parse_tables": True,
        "store_raw_text": False,
        "user_agent": "data-collection-workflow/0.1",
        "content_fixture_map_path": None,
    }
    llm_enabled = not no_llm
    config["llm"] = {
        "provider": provider,
        "model": model,
        "source_planning_enabled": llm_enabled,
        "source_critic_enabled": llm_enabled,
        "structured_extraction_enabled": llm_enabled,
        "max_chunks": 8,
        "max_tokens": 4096,
        "fallback_to_rule_based": False,
        "source_critic": {
            "max_sources": 6,
            "review_blocks_fetch": False,
        },
        "source_credibility": {
            "enabled": llm_enabled,
            "max_sources": 6,
            "source_id_allowlist": [],
        },
    }
    config["disease_intelligence"] = {
        "llm_enabled": llm_enabled,
        "force_llm": False,
        "fallback_to_curated": True,
    }
    config["human_review"] = {
        "decisions_path": None,
        "apply_decisions": False,
        "require_reviewer_id": True,
    }
    config["source_sets"] = {
        "source_id_allowlist_enabled": False,
        "collection_source_ids": [],
        "context_source_ids": [],
        "validation_reserved_source_ids": [],
        "workflow_source_ids": [],
        "llm_source_critic_source_ids": [],
    }
    config["output"] = {
        "run_output_root": output_dir or "outputs",
        "sessionized": True,
        "session_id": session_id,
        "auto_build_console": True,
        "console_output_root": "outputs/workflow_console",
        "write_latest_alias": True,
    }
    return config


def _collect_inputs(args: argparse.Namespace) -> dict:
    prompt_mode = not (args.disease and args.location and args.start_date and args.end_date)
    disease = args.disease or _prompt("Disease / virus")
    location = args.location or _prompt("Location")
    start_date = args.start_date or _prompt("Start year/date (example: 2024; use one value, not a range)")
    end_date = args.end_date or _prompt("End year/date (example: 2026)")
    start_date, end_date, date_note = _normalize_dates(start_date, end_date)
    if date_note:
        print(date_note)
    target_fields = args.target_field or list(DEFAULT_TARGET_FIELDS)
    default_session_id = _session_id(disease, location, start_date, end_date)
    raw_session_id = args.session_id or (
        _prompt("Session id; press Enter to use the generated safe name", default_session_id)
        if (sys.stdin.isatty() or prompt_mode)
        else default_session_id
    )
    session_id = _normalize_session_id(raw_session_id, default_session_id)
    if raw_session_id != session_id:
        print(f"Using safe session id: {session_id}")
    return {
        "disease": disease,
        "location": location,
        "start_date": start_date,
        "end_date": end_date,
        "target_fields": target_fields,
        "session_id": session_id,
    }


def _sanitized_preview(config: dict, provider: str, no_llm: bool) -> dict:
    return {
        "project_name": "data collection workflow",
        "mode": "interactive_real_run",
        "api_keys": {
            "tavily_api_key_present": _env_present("TAVILY_API_KEY"),
            "llm_provider": provider,
            "llm_api_key_name": None if no_llm else _provider_key_name(provider),
            "llm_api_key_present": True if no_llm else _env_present(_provider_key_name(provider)),
        },
        "config": config,
    }


def _write_generated_config(config: dict, session_id: str) -> Path:
    output = PROJECT_ROOT / "outputs" / "generated_configs" / f"{session_id}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")
    return output


def _runner_args(config_path: Path, args: argparse.Namespace) -> argparse.Namespace:
    return argparse.Namespace(
        config=str(config_path),
        enable_live_fetch=False,
        disable_live_fetch=False,
        enable_all_llm=False,
        disable_all_llm=False,
        provider=None,
        model=None,
        timeout_seconds=None,
        llm_max_chunks=None,
        output_dir=args.output_dir,
        session_id=None,
        user_request=None,
        print_config_only=False,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Interactively run the data collection workflow in real mode. "
            "Live search, live fetch, and LLM stages are enabled by default."
        )
    )
    parser.add_argument("--disease")
    parser.add_argument("--location")
    parser.add_argument("--start-date")
    parser.add_argument("--end-date")
    parser.add_argument("--target-field", action="append", default=[], help=argparse.SUPPRESS)
    parser.add_argument("--session-id")
    parser.add_argument("--output-dir")
    parser.add_argument("--provider", default=DEFAULT_PROVIDER)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--no-llm", action="store_true", help="Internal/debug option; real user runs enable LLM by default.")
    parser.add_argument("--print-config-only", action="store_true", help="Preview sanitized generated config without running.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    collected = _collect_inputs(args)
    config = _real_run_config(
        disease=collected["disease"],
        location=collected["location"],
        start_date=collected["start_date"],
        end_date=collected["end_date"],
        target_fields=collected["target_fields"],
        session_id=collected["session_id"],
        provider=args.provider,
        model=args.model,
        output_dir=args.output_dir,
        no_llm=args.no_llm,
    )

    if args.print_config_only:
        print("data collection workflow interactive real-run preview")
        print("sanitized_config_json:")
        print(json.dumps(_sanitized_preview(config, args.provider, args.no_llm), indent=2, ensure_ascii=False))
        return 0

    missing = _require_keys(provider=args.provider, llm_enabled=not args.no_llm)
    if missing:
        for name in missing:
            print(f"Missing required API key: {name}", file=sys.stderr)
        print(
            "Set the missing key in the environment before running a real workflow. "
            "The workflow will not fall back to fixture data for this interactive entrypoint.",
            file=sys.stderr,
        )
        return 2

    generated_config = _write_generated_config(config, collected["session_id"])
    print("data collection workflow interactive real run")
    print(f"generated_config: {generated_config}")
    print(f"session_id: {collected['session_id']}")
    print("live_search: true")
    print("live_fetch: true")
    print(f"llm_enabled: {str(not args.no_llm).lower()}")
    print("running workflow now...")
    return int(bool(run_workflow(_runner_args(generated_config, args)) is None))


if __name__ == "__main__":
    raise SystemExit(main())
