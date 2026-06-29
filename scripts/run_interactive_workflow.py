"""Interactive real-run entrypoint for the data collection workflow."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import socket
import subprocess
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
from hdc_workflow.langflow_demo import (  # noqa: E402
    apply_quick_test_mode,
    generated_session_id,
    normalize_date_range,
    normalize_session_id as normalize_hdc_session_id,
)
from run_hdc_workflow_configured import run_workflow  # noqa: E402


def _configure_utf8_stdio(*, stdout=None, stderr=None) -> None:
    """Prefer UTF-8 console output so Windows paths with non-ASCII chars print safely."""

    for stream in (stdout or sys.stdout, stderr or sys.stderr):
        encoding = (getattr(stream, "encoding", None) or "").lower()
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure) and encoding not in {"utf-8", "utf8"}:
            reconfigure(encoding="utf-8", errors="replace")


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
    cleaned = normalize_hdc_session_id(raw)
    if cleaned == "workflow_run" and raw != "workflow_run":
        return default
    return cleaned or default


def _prompt(label: str, current: str | None = None) -> str:
    suffix = f" [{current}]" if current else ""
    value = input(f"{label}{suffix}: ").strip()
    return value or (current or "")


def _env_present(name: str) -> bool:
    return bool(os.environ.get(name))


def _provider_key_name(provider: str) -> str:
    return LLM_KEY_BY_PROVIDER.get(provider.strip().lower(), f"{provider.upper()}_API_KEY")


def _default_user_request(disease: str, location: str, start_date: str, end_date: str) -> str:
    return (
        f"Collect {disease} cases, deaths, dates, locations, source URLs, "
        f"source types, and evidence quotes for {location} from {start_date} to {end_date}."
    )


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
    user_request: str | None = None,
    quick_test_mode: bool = False,
    audit_mode: bool = False,
) -> dict:
    config = deepcopy(default_workflow_run_config())
    request_text = user_request or _default_user_request(disease, location, start_date, end_date)
    collection_mode = "standard" if audit_mode else "direct_collection"
    validation_mode = "live_cross_source" if audit_mode else "diagnostic_only"

    config["profile_name"] = f"{_slug(disease)}_{_slug(location)}_{start_date}_{end_date}_real_workflow"
    config["description"] = (
        "Interactive real data collection workflow run. Live search, live fetch, "
        "and LLM stages are enabled by default; API keys are read from environment variables."
    )
    config["workflow"] = {
        "collection_mode": collection_mode,
        "use_fixture_documents": False,
    }
    config["user_request"] = request_text
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
        "collection_mode": collection_mode,
        "user_request": request_text,
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
        "max_queries": 8,
        "max_results_per_query": 8,
        "max_total_results": 64,
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
        "iterative": {
            "enabled": True,
            "max_iterations": 3 if audit_mode else 2,
            "max_queries_per_iteration": 4,
            "max_total_queries": 20 if audit_mode else 10,
            "max_total_results": 120 if audit_mode else 50,
            "require_llm": True,
            "allow_deterministic_fallback": False,
            "stop_when_llm_says_sufficient": True,
            "require_observation_after_each_iteration": True,
        },
    }
    config["content_fetch"] = {
        "fetch_search_derived_sources": True,
        "max_search_derived_sources": 50 if audit_mode else 18,
        "max_total_sources": 50 if audit_mode else 18,
        "min_credibility_score": 0.55,
        "allowed_final_roles": [
            "collection",
            "validation",
            "collection_support",
            "context",
        ],
        "allow_needs_review": True,
        "domain_allowlist": [],
        "domain_blocklist": [],
        "max_bytes": 1_000_000,
        "parse_pdf_text": True,
        "parse_tables": True,
        "store_raw_text": False,
        "user_agent": "data-collection-workflow/0.1",
        "content_fixture_map_path": None,
        "external_fetch": {
            "enabled": True,
            "provider_order": ["tavily_extract", "native_requests"],
            "tavily_extract": {
                "format": "markdown",
                "extract_depth": "advanced",
                "timeout_seconds": 45,
                "chunks_per_source": 5,
            },
            "adaptive_budget": {
                "max_candidate_urls": 120 if audit_mode else 50,
                "max_fetch_urls": 50 if audit_mode else 18,
                "min_usable_documents": 12,
                "min_collection_sources": 6,
                "min_validation_sources": 3 if audit_mode else 0,
                "max_iterations": 3 if audit_mode else 2,
                "stop_when_llm_says_sufficient": True,
            },
        },
    }
    llm_enabled = not no_llm
    config["llm"] = {
        "provider": provider,
        "model": model,
        "source_planning_enabled": llm_enabled,
        "source_critic_enabled": llm_enabled,
        "structured_extraction_enabled": llm_enabled,
        "max_chunks": 30,
        "max_tokens": 4096,
        "fallback_to_rule_based": False,
        "source_critic": {
            "max_sources": 6 if audit_mode else 4,
            "review_blocks_fetch": False,
        },
        "source_credibility": {
            "enabled": llm_enabled,
            "max_sources": 6 if audit_mode else 4,
            "source_id_allowlist": [],
        },
        "source_identity": {
            "enabled": llm_enabled,
            "max_sources": 30 if audit_mode else 16,
            "post_fetch": True,
            "require_llm": llm_enabled,
            "allow_deterministic_fallback": not llm_enabled,
        },
        "must_fetch_min_chunks_per_source": 6,
        "official_extraction_max_chunks": 30,
    }
    config["disease_intelligence"] = {
        "llm_enabled": llm_enabled,
        "force_llm": llm_enabled,
        "fallback_to_curated": True,
    }
    config["human_review"] = {
        "enabled": False,
        "decisions_path": None,
        "apply_decisions": False,
        "require_reviewer_id": True,
    }
    config["validation"] = {
        "mode": validation_mode,
        "held_out_records_path": None,
        "allow_incompatible_validation_records": False,
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
    if quick_test_mode:
        apply_quick_test_mode(config)
        config.setdefault("structured_task", {})["quick_test_mode"] = True
    return config


def _collect_inputs(args: argparse.Namespace) -> dict:
    prompt_mode = not (args.disease and args.location and args.start_date and args.end_date)
    disease = args.disease or _prompt("Disease / virus")
    location = args.location or _prompt("Location")
    start_raw = args.start_date or _prompt("Start date (YYYY, YYYY-M-D, or YYYY-MM-DD)")
    end_raw = args.end_date or _prompt("End date (YYYY, YYYY-M-D, or YYYY-MM-DD)")
    start_date, end_date = normalize_date_range(start_raw, end_raw)
    target_fields = args.target_field or list(DEFAULT_TARGET_FIELDS)
    default_session_id = generated_session_id(disease, location, start_date, end_date)
    raw_session_id = args.session_id or (
        _prompt("Session id; press Enter to use the generated safe name", default_session_id)
        if (sys.stdin.isatty() or prompt_mode)
        else default_session_id
    )
    session_id = _normalize_session_id(raw_session_id, default_session_id)
    if raw_session_id != session_id:
        print(f"Using safe session id: {session_id}")
    default_request = _default_user_request(disease, location, start_date, end_date)
    if args.user_request is not None:
        user_request = args.user_request
    elif prompt_mode:
        user_request = _prompt("User request; press Enter to auto-generate", default_request)
    else:
        user_request = default_request
    return {
        "disease": disease,
        "location": location,
        "start_date": start_date,
        "end_date": end_date,
        "target_fields": target_fields,
        "session_id": session_id,
        "user_request": user_request,
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


def _session_dir_for_config(config: dict) -> Path:
    output = config.get("output") or {}
    root = Path(output.get("run_output_root") or "outputs")
    if not root.is_absolute():
        root = PROJECT_ROOT / root
    session_id = str(output.get("session_id") or "workflow_run")
    if bool(output.get("sessionized", True)):
        return root / "sessions" / session_id
    return root


def _find_available_port(preferred_port: int) -> int:
    for port in range(int(preferred_port), int(preferred_port) + 50):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.2)
            if sock.connect_ex(("127.0.0.1", port)) != 0:
                return port
    return int(preferred_port)


def _launch_live_dashboard(
    session_dir: Path,
    *,
    preferred_port: int = 8501,
) -> dict:
    """Start Streamlit dashboard for this session without blocking the workflow."""

    if importlib.util.find_spec("streamlit") is None:
        return {
            "started": False,
            "reason": "streamlit_not_installed",
            "install_command": "python -m pip install streamlit plotly nbformat nbconvert ipywidgets pypdf",
        }
    port = _find_available_port(preferred_port)
    log_dir = PROJECT_ROOT / "outputs"
    log_dir.mkdir(parents=True, exist_ok=True)
    stdout_path = log_dir / "streamlit_live_dashboard.log"
    stderr_path = log_dir / "streamlit_live_dashboard.err.log"
    command = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(PROJECT_ROOT / "scripts" / "live_workflow_dashboard.py"),
        "--server.port",
        str(port),
        "--server.headless",
        "true",
        "--browser.gatherUsageStats",
        "false",
        "--",
        "--session-dir",
        str(session_dir),
    ]
    stdout_handle = stdout_path.open("a", encoding="utf-8")
    stderr_handle = stderr_path.open("a", encoding="utf-8")
    try:
        process = subprocess.Popen(
            command,
            cwd=PROJECT_ROOT,
            stdout=stdout_handle,
            stderr=stderr_handle,
            stdin=subprocess.DEVNULL,
        )
    except OSError as exc:
        stdout_handle.close()
        stderr_handle.close()
        return {
            "started": False,
            "reason": f"{exc.__class__.__name__}: {exc}",
            "stdout_log": str(stdout_path),
            "stderr_log": str(stderr_path),
        }
    stdout_handle.close()
    stderr_handle.close()
    return {
        "started": True,
        "pid": process.pid,
        "port": port,
        "url": f"http://localhost:{port}",
        "stdout_log": str(stdout_path),
        "stderr_log": str(stderr_path),
    }


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
        live_status=bool(getattr(args, "live_status", True)),
        write_run_notebook=bool(getattr(args, "write_run_notebook", True)),
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
    parser.add_argument("--user-request")
    parser.add_argument("--target-field", action="append", default=[], help=argparse.SUPPRESS)
    parser.add_argument("--session-id")
    parser.add_argument("--output-dir")
    parser.add_argument("--provider", default=DEFAULT_PROVIDER)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--no-llm", action="store_true", help="Internal/debug option; real user runs enable LLM by default.")
    parser.add_argument("--quick-test-mode", action="store_true", help="Use the same reduced budget controls as the Langflow visual demo.")
    parser.add_argument(
        "--audit-mode",
        action="store_true",
        help="Use the legacy full audit collection mode instead of the default direct collection mode.",
    )
    parser.add_argument("--print-config-only", action="store_true", help="Preview sanitized generated config without running.")
    parser.add_argument("--live-status", dest="live_status", action="store_true", default=True)
    parser.add_argument("--no-live-status", dest="live_status", action="store_false")
    parser.add_argument("--write-run-notebook", dest="write_run_notebook", action="store_true", default=True)
    parser.add_argument("--no-run-notebook", dest="write_run_notebook", action="store_false")
    parser.add_argument("--dashboard", dest="dashboard", action="store_true", default=True)
    parser.add_argument("--no-dashboard", dest="dashboard", action="store_false")
    parser.add_argument("--dashboard-port", type=int, default=8501)
    return parser


def main(argv: list[str] | None = None) -> int:
    _configure_utf8_stdio()
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        collected = _collect_inputs(args)
    except ValueError as exc:
        print(f"Invalid interactive workflow input: {exc}", file=sys.stderr)
        return 2
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
        user_request=collected["user_request"],
        quick_test_mode=bool(args.quick_test_mode),
        audit_mode=bool(args.audit_mode),
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
    session_dir = _session_dir_for_config(config)
    print("data collection workflow interactive real run")
    print(f"generated_config: {generated_config}")
    print(f"session_id: {collected['session_id']}")
    print("live_search: true")
    print("live_fetch: true")
    print(f"llm_enabled: {str(not args.no_llm).lower()}")
    print(f"collection_mode: {config.get('workflow', {}).get('collection_mode')}")
    print(f"quick_test_mode: {str(bool(args.quick_test_mode)).lower()}")
    print(f"write_run_notebook: {str(args.write_run_notebook).lower()}")
    if args.dashboard:
        dashboard = _launch_live_dashboard(
            session_dir,
            preferred_port=args.dashboard_port,
        )
        if dashboard.get("started"):
            print(f"live_dashboard: {dashboard['url']}")
            print(f"dashboard_pid: {dashboard['pid']}")
        else:
            print(f"live_dashboard: not started ({dashboard.get('reason')})")
            if dashboard.get("install_command"):
                print(f"dashboard_install_command: {dashboard['install_command']}")
    else:
        print("live_dashboard: disabled")
    print("running workflow now...")
    return int(bool(run_workflow(_runner_args(generated_config, args)) is None))


if __name__ == "__main__":
    raise SystemExit(main())
