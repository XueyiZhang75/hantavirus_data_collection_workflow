"""Shared runtime profile helpers for HDC workflow runs.

A workflow runtime profile controls the graph input, source overlays, live
fetch, LLM stages, source roles, validation evidence, and output paths.
"""

from __future__ import annotations

import os
import json
from copy import deepcopy
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"
LIVE_CASE_STUDY_ID = "new_mexico_hps_live_llm_workflow_run"
LIVE_CASE_DIR = Path(__file__).resolve().parent / "resources" / "live_case_studies"
SEED_SOURCE_OVERLAY_PATH = LIVE_CASE_DIR / "new_mexico_hps_seed_sources.json"
SOURCE_ROLE_POLICY_OVERLAY_PATH = (
    LIVE_CASE_DIR / "new_mexico_hps_source_role_policy_overlay.json"
)
GROUND_TRUTH_RECORDS_PATH = LIVE_CASE_DIR / "new_mexico_hps_ground_truth_records.csv"

COLLECTION_SOURCE_IDS = [
    "src_nmdoh_hps_2024_first_case",
    "src_nmdoh_hps_2025_first_case_death",
    "src_nmdoh_hps_2026_first_case_prior_year_summary",
]
CONTEXT_SOURCE_IDS = [
    "src_nmdoh_hps_overview_1975_2025",
    "src_cdc_hantavirus_reported_cases_through_2023",
]
VALIDATION_SOURCE_IDS = [
    "src_nmdoh_hps_cases_by_county_1975_2025_pdf",
]
CASE_SOURCE_IDS = [
    *COLLECTION_SOURCE_IDS,
    *CONTEXT_SOURCE_IDS,
    *VALIDATION_SOURCE_IDS,
]

DEFAULT_USER_REQUEST = (
    "Collect data on hantavirus from 2020 to 2026. For this workflow run, "
    "use the New Mexico HPS source set, keep collection sources and validation "
    "sources separated, extract cases, deaths, dates, locations, source URLs, "
    "source types, and evidence quotes, then route uncertain results to human "
    "review."
)
DEFAULT_PROVIDER = "anthropic"
DEFAULT_MODEL = "claude-sonnet-4-6"
DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "outputs"
DEFAULT_OUTPUT_DIR = DEFAULT_OUTPUT_ROOT
DEFAULT_CONSOLE_OUTPUT_ROOT = PROJECT_ROOT / "outputs" / "workflow_console"
DEFAULT_WORKFLOW_RUN_CONFIG_PATH = PROJECT_ROOT / "configs" / "hdc_workflow_run_config.jsonc"

ENV_KEYS = [
    "HDC_COLLECTION_MODE",
    "HDC_SEED_SOURCE_OVERLAY_PATH",
    "HDC_SOURCE_ROLE_POLICY_OVERLAY_PATH",
    "HDC_USE_FIXTURE_DOCUMENTS",
    "HDC_ENABLE_LIVE_FETCH",
    "HDC_ENABLE_LLM_SOURCE_PLANNING",
    "HDC_ENABLE_LLM_SOURCE_CRITIC",
    "HDC_ENABLE_LLM_EXTRACTION",
    "HDC_LLM_SOURCE_CRITIC_SOURCE_ID_ALLOWLIST",
    "HDC_LLM_SOURCE_CRITIC_MAX_SOURCES",
    "HDC_LLM_SOURCE_CRITIC_REVIEW_BLOCKS_FETCH",
    "HDC_LLM_PROVIDER",
    "HDC_LLM_MODEL",
    "HDC_LLM_MAX_CHUNKS",
    "HDC_LLM_MAX_TOKENS",
    "HDC_LLM_FALLBACK_TO_RULE_BASED",
    "HDC_SOURCE_ID_ALLOWLIST",
    "HDC_FETCH_TIMEOUT_SECONDS",
]


def workflow_run_env(
    *,
    collection_mode: str = "masked_validation",
    seed_source_overlay_path: str | Path | None = None,
    source_role_policy_overlay_path: str | Path | None = None,
    use_fixture_documents: bool = False,
    live_fetch: bool = True,
    llm_source_planning: bool = True,
    llm_source_critic: bool = True,
    llm_extraction: bool = True,
    provider: str | None = None,
    model: str | None = None,
    timeout_seconds: float = 30.0,
    llm_max_chunks: int = 8,
    llm_source_critic_max_sources: int | None = 6,
    llm_source_critic_review_blocks_fetch: bool = False,
    llm_max_tokens: int = 4096,
    fallback_to_rule_based: bool = False,
    source_id_allowlist: list[str] | None = None,
    llm_source_critic_source_id_allowlist: list[str] | None = None,
) -> dict[str, str]:
    """Return the environment for a configured HDC workflow run."""

    workflow_source_ids = source_id_allowlist or CASE_SOURCE_IDS
    critic_source_ids = llm_source_critic_source_id_allowlist or workflow_source_ids
    seed_overlay = seed_source_overlay_path or SEED_SOURCE_OVERLAY_PATH
    role_overlay = source_role_policy_overlay_path or SOURCE_ROLE_POLICY_OVERLAY_PATH
    env = {
        "HDC_COLLECTION_MODE": collection_mode,
        "HDC_SEED_SOURCE_OVERLAY_PATH": str(seed_overlay),
        "HDC_SOURCE_ROLE_POLICY_OVERLAY_PATH": str(role_overlay),
        "HDC_USE_FIXTURE_DOCUMENTS": "true" if use_fixture_documents else "false",
        "HDC_ENABLE_LIVE_FETCH": "true" if live_fetch else "false",
        "HDC_ENABLE_LLM_SOURCE_PLANNING": "true" if llm_source_planning else "false",
        "HDC_ENABLE_LLM_SOURCE_CRITIC": "true" if llm_source_critic else "false",
        "HDC_ENABLE_LLM_EXTRACTION": "true" if llm_extraction else "false",
        "HDC_SOURCE_ID_ALLOWLIST": ",".join(workflow_source_ids),
        "HDC_FETCH_TIMEOUT_SECONDS": str(timeout_seconds),
        "HDC_LLM_MAX_CHUNKS": str(llm_max_chunks),
        "HDC_LLM_MAX_TOKENS": str(llm_max_tokens),
        "HDC_LLM_SOURCE_CRITIC_SOURCE_ID_ALLOWLIST": ",".join(critic_source_ids),
        "HDC_LLM_SOURCE_CRITIC_REVIEW_BLOCKS_FETCH": (
            "true" if llm_source_critic_review_blocks_fetch else "false"
        ),
        "HDC_LLM_FALLBACK_TO_RULE_BASED": (
            "true" if fallback_to_rule_based else "false"
        ),
    }
    if llm_source_critic_max_sources is not None:
        env["HDC_LLM_SOURCE_CRITIC_MAX_SOURCES"] = str(
            llm_source_critic_max_sources
        )
    resolved_provider = provider or os.environ.get("HDC_LLM_PROVIDER") or DEFAULT_PROVIDER
    resolved_model = model or os.environ.get("HDC_LLM_MODEL") or DEFAULT_MODEL
    if resolved_provider:
        env["HDC_LLM_PROVIDER"] = resolved_provider
    if resolved_model:
        env["HDC_LLM_MODEL"] = resolved_model
    return env


def default_workflow_run_config() -> dict:
    """Return built-in workflow runtime settings used when config keys are omitted."""

    return {
        "profile_name": "new_mexico_hps_live_llm_workflow_run",
        "description": (
            "Runtime profile for the HDC workflow. It controls graph input, "
            "source overlays, live fetch, LLM stages, source roles, and outputs."
        ),
        "workflow": {
            "graph_name": "hantavirus_data_collection_workflow",
            "collection_mode": "masked_validation",
            "seed_source_overlay_path": str(SEED_SOURCE_OVERLAY_PATH.relative_to(PROJECT_ROOT)),
            "source_role_policy_overlay_path": str(
                SOURCE_ROLE_POLICY_OVERLAY_PATH.relative_to(PROJECT_ROOT)
            ),
            "validation_ground_truth_records_path": str(
                GROUND_TRUTH_RECORDS_PATH.relative_to(PROJECT_ROOT)
            ),
            "use_fixture_documents": False,
        },
        "user_request": DEFAULT_USER_REQUEST,
        "studio": {
            "port": None,
            "no_reload": True,
        },
        "live_web": {
            "enabled": True,
            "timeout_seconds": 30,
        },
        "llm": {
            "provider": DEFAULT_PROVIDER,
            "model": DEFAULT_MODEL,
            "source_planning_enabled": True,
            "source_critic_enabled": True,
            "structured_extraction_enabled": True,
            "max_chunks": 8,
            "max_tokens": 4096,
            "fallback_to_rule_based": False,
            "source_critic": {
                "max_sources": 6,
                "review_blocks_fetch": False,
            },
        },
        "source_sets": {
            "collection_source_ids": list(COLLECTION_SOURCE_IDS),
            "context_source_ids": list(CONTEXT_SOURCE_IDS),
            "validation_reserved_source_ids": list(VALIDATION_SOURCE_IDS),
            "workflow_source_ids": list(CASE_SOURCE_IDS),
            "llm_source_critic_source_ids": list(CASE_SOURCE_IDS),
        },
        "output": {
            "run_output_root": str(DEFAULT_OUTPUT_ROOT.relative_to(PROJECT_ROOT)),
            "sessionized": True,
            "session_id": None,
            "auto_build_console": True,
            "console_output_root": str(
                DEFAULT_CONSOLE_OUTPUT_ROOT.relative_to(PROJECT_ROOT)
            ),
            "write_latest_alias": True,
        },
    }


def _deep_merge(base: dict, override: dict) -> dict:
    merged = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _strip_jsonc_comments(text: str) -> str:
    """Remove JSONC comments while preserving quoted string content."""

    result: list[str] = []
    in_string = False
    escaped = False
    index = 0
    while index < len(text):
        char = text[index]
        next_char = text[index + 1] if index + 1 < len(text) else ""

        if in_string:
            result.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            index += 1
            continue

        if char == '"':
            in_string = True
            result.append(char)
            index += 1
            continue

        if char == "/" and next_char == "/":
            index += 2
            while index < len(text) and text[index] not in "\r\n":
                index += 1
            continue

        if char == "/" and next_char == "*":
            index += 2
            while index + 1 < len(text) and not (
                text[index] == "*" and text[index + 1] == "/"
            ):
                index += 1
            index += 2
            continue

        result.append(char)
        index += 1
    return "".join(result)


def _load_json_or_jsonc(path: Path) -> dict:
    text = path.read_text(encoding="utf-8-sig")
    if path.suffix.lower() == ".jsonc":
        text = _strip_jsonc_comments(text)
    loaded = json.loads(text)
    if not isinstance(loaded, dict):
        raise ValueError(f"Workflow run config must be a JSON object: {path}")
    return loaded


def resolve_config_path(config_path: str | Path | None = None) -> Path:
    """Resolve a workflow runtime config path relative to the project root."""

    path = Path(config_path) if config_path else DEFAULT_WORKFLOW_RUN_CONFIG_PATH
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path


def load_config(config_path: str | Path | None = None) -> dict:
    """Load workflow runtime settings from JSON, with stable built-in defaults."""

    path = resolve_config_path(config_path)
    config = default_workflow_run_config()
    if path.exists():
        loaded = _load_json_or_jsonc(path)
        config = _deep_merge(config, loaded)
    elif config_path:
        raise FileNotFoundError(f"Workflow run config not found: {path}")
    return config


def _resolve_project_path(value: str | Path | None, default: Path) -> Path:
    path = Path(value) if value else default
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path


def workflow_run_env_from_config(config: dict) -> dict[str, str]:
    """Build workflow environment variables from a runtime profile."""

    workflow = config.get("workflow") or {}
    live_web = config.get("live_web") or {}
    llm = config.get("llm") or {}
    source_critic = llm.get("source_critic") or {}
    source_sets = config.get("source_sets") or {}
    return workflow_run_env(
        collection_mode=workflow.get("collection_mode", "masked_validation"),
        seed_source_overlay_path=_resolve_project_path(
            workflow.get("seed_source_overlay_path"), SEED_SOURCE_OVERLAY_PATH
        ),
        source_role_policy_overlay_path=_resolve_project_path(
            workflow.get("source_role_policy_overlay_path"),
            SOURCE_ROLE_POLICY_OVERLAY_PATH,
        ),
        use_fixture_documents=bool(workflow.get("use_fixture_documents", False)),
        live_fetch=bool(live_web.get("enabled", True)),
        llm_source_planning=bool(llm.get("source_planning_enabled", True)),
        llm_source_critic=bool(llm.get("source_critic_enabled", True)),
        llm_extraction=bool(llm.get("structured_extraction_enabled", True)),
        provider=llm.get("provider"),
        model=llm.get("model"),
        timeout_seconds=float(live_web.get("timeout_seconds", 30)),
        llm_max_chunks=int(llm.get("max_chunks", 8)),
        llm_source_critic_max_sources=source_critic.get("max_sources", 6),
        llm_source_critic_review_blocks_fetch=bool(
            source_critic.get("review_blocks_fetch", False)
        ),
        llm_max_tokens=int(llm.get("max_tokens", 4096)),
        fallback_to_rule_based=bool(llm.get("fallback_to_rule_based", False)),
        source_id_allowlist=source_sets.get("workflow_source_ids") or CASE_SOURCE_IDS,
        llm_source_critic_source_id_allowlist=source_sets.get(
            "llm_source_critic_source_ids"
        )
        or source_sets.get("workflow_source_ids")
        or CASE_SOURCE_IDS,
    )


def workflow_run_config_with_overrides(
    config: dict,
    *,
    live_fetch: bool | None = None,
    all_llm: bool | None = None,
    provider: str | None = None,
    model: str | None = None,
    timeout_seconds: float | None = None,
    llm_max_chunks: int | None = None,
    port: int | None = None,
    output_dir: str | Path | None = None,
    session_id: str | None = None,
    user_request: str | None = None,
) -> dict:
    """Return a config copy with one-run command-line overrides applied."""

    updated = deepcopy(config)
    updated.setdefault("live_web", {})
    updated.setdefault("llm", {})
    updated.setdefault("studio", {})
    updated.setdefault("output", {})

    if live_fetch is not None:
        updated["live_web"]["enabled"] = bool(live_fetch)
    if all_llm is not None:
        updated["llm"]["source_planning_enabled"] = bool(all_llm)
        updated["llm"]["source_critic_enabled"] = bool(all_llm)
        updated["llm"]["structured_extraction_enabled"] = bool(all_llm)
    if provider:
        updated["llm"]["provider"] = provider
    if model:
        updated["llm"]["model"] = model
    if timeout_seconds is not None:
        updated["live_web"]["timeout_seconds"] = timeout_seconds
    if llm_max_chunks is not None:
        updated["llm"]["max_chunks"] = llm_max_chunks
    if port is not None:
        updated["studio"]["port"] = port
    if output_dir is not None:
        updated["output"]["run_output_root"] = str(output_dir)
    if session_id:
        updated["output"]["session_id"] = session_id
    if user_request:
        updated["user_request"] = user_request
    return updated


def workflow_initial_state_from_config(
    config: dict,
    *,
    include_empty_fields: bool = True,
) -> dict:
    """Build the Studio input payload from the centralized config."""

    return studio_initial_state(
        config.get("user_request") or DEFAULT_USER_REQUEST,
        include_empty_fields=include_empty_fields,
    )


def workflow_session_id(now: datetime | None = None) -> str:
    """Return a timestamped workflow session id."""

    timestamp = now or datetime.now(timezone.utc)
    return timestamp.strftime("%Y%m%d_%H%M%S_utc")


def workflow_output_root_from_config(config: dict) -> Path:
    """Resolve the workflow run output root from the centralized config."""

    output = config.get("output") or {}
    root_value = (
        output.get("run_output_root")
        or output.get("run_output_dir")
        or DEFAULT_OUTPUT_ROOT
    )
    root = Path(root_value)
    if not root.is_absolute():
        root = PROJECT_ROOT / root
    return root


def workflow_output_dir_from_config(
    config: dict,
    *,
    session_id: str | None = None,
) -> Path:
    """Resolve the run output directory from the centralized config."""

    output = config.get("output") or {}
    if bool(output.get("sessionized", True)):
        resolved_session_id = (
            session_id
            or output.get("session_id")
            or workflow_session_id()
        )
        return workflow_output_root_from_config(config) / "sessions" / str(
            resolved_session_id
        )

    output_dir = Path(
        output.get("run_output_dir")
        or output.get("run_output_root")
        or DEFAULT_OUTPUT_DIR
    )
    if not output_dir.is_absolute():
        output_dir = PROJECT_ROOT / output_dir
    return output_dir


def workflow_console_output_dir_from_config(
    config: dict,
    *,
    run_output_dir: Path | None = None,
    session_id: str | None = None,
) -> Path:
    """Resolve where the HTML workflow console should be written."""

    output = config.get("output") or {}
    if bool(output.get("sessionized", True)) and run_output_dir is not None:
        return run_output_dir / "workflow_console"

    console_root = Path(output.get("console_output_root") or DEFAULT_CONSOLE_OUTPUT_ROOT)
    if not console_root.is_absolute():
        console_root = PROJECT_ROOT / console_root
    if session_id:
        return console_root / "sessions" / session_id
    return console_root


def validation_records_path_from_config(config: dict) -> Path:
    """Resolve the validation ground-truth CSV path from a runtime profile."""

    workflow = config.get("workflow") or {}
    return _resolve_project_path(
        workflow.get("validation_ground_truth_records_path"),
        GROUND_TRUTH_RECORDS_PATH,
    )


def resolve_workflow_run_config_path(config_path: str | Path | None = None) -> Path:
    """Resolve the primary workflow runtime config path."""

    path = Path(config_path) if config_path else DEFAULT_WORKFLOW_RUN_CONFIG_PATH
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path


def load_workflow_run_config(config_path: str | Path | None = None) -> dict:
    """Load the primary workflow runtime profile."""

    return load_config(resolve_workflow_run_config_path(config_path))


def workflow_initial_state_from_config(
    config: dict,
    *,
    include_empty_fields: bool = True,
) -> dict:
    """Build the LangGraph Studio input payload from a runtime profile."""

    return studio_initial_state(
        config.get("user_request") or DEFAULT_USER_REQUEST,
        include_empty_fields=include_empty_fields,
    )


def studio_initial_state(
    user_request: str | None = None,
    *,
    include_empty_fields: bool = True,
) -> dict:
    """Build the state payload a user can submit in LangGraph Studio."""

    state = {"user_request": user_request or DEFAULT_USER_REQUEST}
    if not include_empty_fields:
        return state
    state.update(
        {
            "source_candidates": [],
            "source_discovery_summary": None,
            "source_registry": [],
            "source_registry_summary": None,
            "source_screening_summary": None,
            "source_critic_summary": None,
            "source_routing_summary": None,
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
            "structured_extraction_summary": None,
            "llm_extraction_summary": None,
            "schema_validation_summary": None,
            "record_normalization_summary": None,
            "record_linking_summary": None,
            "cross_source_consistency_summary": None,
            "human_review_summary": None,
            "final_data_package": None,
            "finalization_summary": None,
            "current_route": None,
        }
    )
    return state


@contextmanager
def temporary_workflow_env(updates: dict[str, str]):
    """Temporarily apply workflow runtime environment values."""

    original = {key: os.environ.get(key) for key in ENV_KEYS}
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


def api_key_present(provider: str) -> bool:
    """Return whether the configured provider has a key in the environment."""

    provider_name = (provider or "").strip().lower()
    if provider_name == "anthropic":
        return bool(os.environ.get("ANTHROPIC_API_KEY"))
    if provider_name == "openai":
        return bool(os.environ.get("OPENAI_API_KEY"))
    return False


def safe_env_for_display(env: dict[str, str]) -> dict[str, str]:
    """Hide secrets before printing an environment preview."""

    return {
        key: value
        for key, value in env.items()
        if "API_KEY" not in key and "TOKEN" not in key and "SECRET" not in key
    }
