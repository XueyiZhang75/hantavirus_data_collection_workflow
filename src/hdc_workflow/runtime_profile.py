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
DEFAULT_SEARCH_FIXTURE_PATH = (
    Path(__file__).resolve().parent
    / "resources"
    / "search_fixtures"
    / "example_search_results.json"
)
DEFAULT_SEARCH_PROVIDER_CHANNEL_ALLOWLIST = [
    "web_search",
    "official_site_search",
    "news_search",
    "literature_api",
    "database_search",
]

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
DEFAULT_TARGET_FIELDS = [
    "disease",
    "virus_or_syndrome",
    "country",
    "subnational_location",
    "date_reported",
    "event_start_date",
    "event_end_date",
    "cases_confirmed",
    "cases_probable",
    "cases_suspected",
    "cases_unspecified",
    "deaths",
    "case_definition",
    "source_url",
    "source_type",
    "evidence_quote",
]
DEFAULT_SOURCE_PREFERENCES = [
    "official_public_health_agency",
    "international_organization_report",
    "peer_reviewed_literature",
    "structured_database",
    "news_and_situation_report",
]
DEFAULT_STRUCTURED_TASK = {
    "disease": "hantavirus",
    "location": "New Mexico",
    "start_date": "2020",
    "end_date": "2026",
    "target_fields": list(DEFAULT_TARGET_FIELDS),
    "source_preferences": list(DEFAULT_SOURCE_PREFERENCES),
    "collection_mode": "masked_validation",
    "user_request": DEFAULT_USER_REQUEST,
    "run_label": LIVE_CASE_STUDY_ID,
}
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
    "HDC_ENABLE_LLM_DISEASE_INTELLIGENCE",
    "HDC_DISEASE_INTELLIGENCE_FORCE_LLM",
    "HDC_DISEASE_INTELLIGENCE_FALLBACK_TO_CURATED",
    "HDC_ENABLE_LLM_SOURCE_PLANNING",
    "HDC_ENABLE_LLM_SOURCE_CRITIC",
    "HDC_ENABLE_LLM_SOURCE_CREDIBILITY",
    "HDC_ENABLE_LLM_EXTRACTION",
    "HDC_LLM_SOURCE_CRITIC_SOURCE_ID_ALLOWLIST",
    "HDC_LLM_SOURCE_CRITIC_MAX_SOURCES",
    "HDC_LLM_SOURCE_CRITIC_REVIEW_BLOCKS_FETCH",
    "HDC_LLM_SOURCE_CREDIBILITY_MAX_SOURCES",
    "HDC_LLM_SOURCE_CREDIBILITY_SOURCE_ID_ALLOWLIST",
    "HDC_LLM_PROVIDER",
    "HDC_LLM_MODEL",
    "HDC_LLM_MAX_CHUNKS",
    "HDC_LLM_MAX_TOKENS",
    "HDC_LLM_FALLBACK_TO_RULE_BASED",
    "HDC_SOURCE_ID_ALLOWLIST",
    "HDC_FETCH_TIMEOUT_SECONDS",
    "HDC_FETCH_SEARCH_DERIVED_SOURCES",
    "HDC_FETCH_MAX_SEARCH_DERIVED_SOURCES",
    "HDC_FETCH_MAX_TOTAL_SOURCES",
    "HDC_FETCH_MIN_CREDIBILITY_SCORE",
    "HDC_FETCH_ALLOWED_FINAL_ROLES",
    "HDC_FETCH_ALLOW_NEEDS_REVIEW",
    "HDC_FETCH_DOMAIN_ALLOWLIST",
    "HDC_FETCH_DOMAIN_BLOCKLIST",
    "HDC_FETCH_MAX_BYTES",
    "HDC_FETCH_USER_AGENT",
    "HDC_FETCH_PARSE_PDF_TEXT",
    "HDC_FETCH_PARSE_TABLES",
    "HDC_FETCH_STORE_RAW_TEXT",
    "HDC_CONTENT_FIXTURE_MAP_PATH",
    "HDC_ENABLE_LIVE_SEARCH",
    "HDC_SEARCH_MODE",
    "HDC_SEARCH_PROVIDER",
    "HDC_SEARCH_FIXTURE_PATH",
    "HDC_SEARCH_MAX_QUERIES",
    "HDC_SEARCH_MAX_RESULTS_PER_QUERY",
    "HDC_SEARCH_MAX_TOTAL_RESULTS",
    "HDC_SEARCH_TIMEOUT_SECONDS",
    "HDC_SEARCH_COMBINE_WITH_SEED_CATALOG",
    "HDC_SEARCH_CACHE_ENABLED",
    "HDC_SEARCH_PROVIDER_CHANNEL_ALLOWLIST",
    "HDC_HUMAN_REVIEW_DECISIONS_PATH",
    "HDC_HUMAN_REVIEW_APPLY_DECISIONS",
    "HDC_HUMAN_REVIEW_REQUIRE_REVIEWER_ID",
    "HDC_ANOMALY_MAX_CASES_THRESHOLD",
    "HDC_ANOMALY_MAX_DEATHS_THRESHOLD",
    "HDC_ANOMALY_SPIKE_MULTIPLIER",
    "HDC_ANOMALY_MIN_PRIOR_RECORDS",
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
    llm_source_credibility: bool = False,
    llm_extraction: bool = True,
    llm_disease_intelligence: bool = False,
    disease_intelligence_force_llm: bool = False,
    disease_intelligence_fallback_to_curated: bool = True,
    provider: str | None = None,
    model: str | None = None,
    timeout_seconds: float = 30.0,
    llm_max_chunks: int = 8,
    llm_source_critic_max_sources: int | None = 6,
    llm_source_critic_review_blocks_fetch: bool = False,
    llm_source_credibility_max_sources: int | None = None,
    llm_source_credibility_source_id_allowlist: list[str] | None = None,
    llm_max_tokens: int = 4096,
    fallback_to_rule_based: bool = False,
    source_id_allowlist: list[str] | None = None,
    source_id_allowlist_enabled: bool = True,
    llm_source_critic_source_id_allowlist: list[str] | None = None,
    live_search: bool = False,
    search_mode: str = "disabled",
    search_provider: str = "tavily",
    search_fixture_path: str | Path | None = None,
    search_max_queries: int = 3,
    search_max_results_per_query: int = 5,
    search_max_total_results: int = 15,
    search_timeout_seconds: float = 15.0,
    search_combine_with_seed_catalog: bool = True,
    search_cache_enabled: bool = True,
    search_provider_channel_allowlist: list[str] | None = None,
    fetch_search_derived_sources: bool = False,
    fetch_max_search_derived_sources: int = 2,
    fetch_max_total_sources: int = 10,
    fetch_min_credibility_score: float = 0.55,
    fetch_allowed_final_roles: list[str] | None = None,
    fetch_allow_needs_review: bool = False,
    fetch_domain_allowlist: list[str] | None = None,
    fetch_domain_blocklist: list[str] | None = None,
    fetch_max_bytes: int = 1_000_000,
    fetch_parse_pdf_text: bool = True,
    fetch_parse_tables: bool = True,
    fetch_store_raw_text: bool = False,
    fetch_user_agent: str = "data-collection-workflow/0.1",
    content_fixture_map_path: str | Path | None = None,
    human_review_decisions_path: str | Path | None = None,
    human_review_apply_decisions: bool = False,
    human_review_require_reviewer_id: bool = True,
    anomaly_max_cases_threshold: float = 1_000_000,
    anomaly_max_deaths_threshold: float = 100_000,
    anomaly_spike_multiplier: float = 10,
    anomaly_min_prior_records: int = 1,
) -> dict[str, str]:
    """Return the environment for a configured HDC workflow run."""

    workflow_source_ids = (
        source_id_allowlist or CASE_SOURCE_IDS
        if source_id_allowlist_enabled
        else []
    )
    critic_source_ids = llm_source_critic_source_id_allowlist or workflow_source_ids
    seed_overlay = seed_source_overlay_path or SEED_SOURCE_OVERLAY_PATH
    role_overlay = source_role_policy_overlay_path or SOURCE_ROLE_POLICY_OVERLAY_PATH
    env = {
        "HDC_COLLECTION_MODE": collection_mode,
        "HDC_SEED_SOURCE_OVERLAY_PATH": str(seed_overlay),
        "HDC_SOURCE_ROLE_POLICY_OVERLAY_PATH": str(role_overlay),
        "HDC_USE_FIXTURE_DOCUMENTS": "true" if use_fixture_documents else "false",
        "HDC_ENABLE_LIVE_FETCH": "true" if live_fetch else "false",
        "HDC_ENABLE_LLM_DISEASE_INTELLIGENCE": (
            "true" if llm_disease_intelligence else "false"
        ),
        "HDC_DISEASE_INTELLIGENCE_FORCE_LLM": (
            "true" if disease_intelligence_force_llm else "false"
        ),
        "HDC_DISEASE_INTELLIGENCE_FALLBACK_TO_CURATED": (
            "true" if disease_intelligence_fallback_to_curated else "false"
        ),
        "HDC_ENABLE_LLM_SOURCE_PLANNING": "true" if llm_source_planning else "false",
        "HDC_ENABLE_LLM_SOURCE_CRITIC": "true" if llm_source_critic else "false",
        "HDC_ENABLE_LLM_SOURCE_CREDIBILITY": (
            "true" if llm_source_credibility else "false"
        ),
        "HDC_ENABLE_LLM_EXTRACTION": "true" if llm_extraction else "false",
        "HDC_SOURCE_ID_ALLOWLIST": ",".join(workflow_source_ids),
        "HDC_FETCH_TIMEOUT_SECONDS": str(timeout_seconds),
        "HDC_FETCH_SEARCH_DERIVED_SOURCES": (
            "true" if fetch_search_derived_sources else "false"
        ),
        "HDC_FETCH_MAX_SEARCH_DERIVED_SOURCES": str(
            fetch_max_search_derived_sources
        ),
        "HDC_FETCH_MAX_TOTAL_SOURCES": str(fetch_max_total_sources),
        "HDC_FETCH_MIN_CREDIBILITY_SCORE": str(fetch_min_credibility_score),
        "HDC_FETCH_ALLOWED_FINAL_ROLES": ",".join(
            fetch_allowed_final_roles
            or ["collection", "validation", "collection_support", "context"]
        ),
        "HDC_FETCH_ALLOW_NEEDS_REVIEW": (
            "true" if fetch_allow_needs_review else "false"
        ),
        "HDC_FETCH_DOMAIN_ALLOWLIST": ",".join(fetch_domain_allowlist or []),
        "HDC_FETCH_DOMAIN_BLOCKLIST": ",".join(fetch_domain_blocklist or []),
        "HDC_FETCH_MAX_BYTES": str(fetch_max_bytes),
        "HDC_FETCH_PARSE_PDF_TEXT": "true" if fetch_parse_pdf_text else "false",
        "HDC_FETCH_PARSE_TABLES": "true" if fetch_parse_tables else "false",
        "HDC_FETCH_STORE_RAW_TEXT": "true" if fetch_store_raw_text else "false",
        "HDC_FETCH_USER_AGENT": fetch_user_agent,
        "HDC_CONTENT_FIXTURE_MAP_PATH": (
            str(content_fixture_map_path) if content_fixture_map_path else ""
        ),
        "HDC_LLM_MAX_CHUNKS": str(llm_max_chunks),
        "HDC_LLM_MAX_TOKENS": str(llm_max_tokens),
        "HDC_LLM_SOURCE_CRITIC_SOURCE_ID_ALLOWLIST": ",".join(critic_source_ids),
        "HDC_LLM_SOURCE_CRITIC_REVIEW_BLOCKS_FETCH": (
            "true" if llm_source_critic_review_blocks_fetch else "false"
        ),
        "HDC_LLM_FALLBACK_TO_RULE_BASED": (
            "true" if fallback_to_rule_based else "false"
        ),
        "HDC_ENABLE_LIVE_SEARCH": "true" if live_search else "false",
        "HDC_SEARCH_MODE": search_mode,
        "HDC_SEARCH_PROVIDER": search_provider,
        "HDC_SEARCH_FIXTURE_PATH": str(
            search_fixture_path or DEFAULT_SEARCH_FIXTURE_PATH
        ),
        "HDC_SEARCH_MAX_QUERIES": str(search_max_queries),
        "HDC_SEARCH_MAX_RESULTS_PER_QUERY": str(search_max_results_per_query),
        "HDC_SEARCH_MAX_TOTAL_RESULTS": str(search_max_total_results),
        "HDC_SEARCH_TIMEOUT_SECONDS": str(search_timeout_seconds),
        "HDC_SEARCH_COMBINE_WITH_SEED_CATALOG": (
            "true" if search_combine_with_seed_catalog else "false"
        ),
        "HDC_SEARCH_CACHE_ENABLED": "true" if search_cache_enabled else "false",
        "HDC_SEARCH_PROVIDER_CHANNEL_ALLOWLIST": ",".join(
            search_provider_channel_allowlist
            or DEFAULT_SEARCH_PROVIDER_CHANNEL_ALLOWLIST
        ),
        "HDC_HUMAN_REVIEW_DECISIONS_PATH": (
            str(human_review_decisions_path) if human_review_decisions_path else ""
        ),
        "HDC_HUMAN_REVIEW_APPLY_DECISIONS": (
            "true" if human_review_apply_decisions else "false"
        ),
        "HDC_HUMAN_REVIEW_REQUIRE_REVIEWER_ID": (
            "true" if human_review_require_reviewer_id else "false"
        ),
        "HDC_ANOMALY_MAX_CASES_THRESHOLD": str(anomaly_max_cases_threshold),
        "HDC_ANOMALY_MAX_DEATHS_THRESHOLD": str(anomaly_max_deaths_threshold),
        "HDC_ANOMALY_SPIKE_MULTIPLIER": str(anomaly_spike_multiplier),
        "HDC_ANOMALY_MIN_PRIOR_RECORDS": str(anomaly_min_prior_records),
    }
    if llm_source_critic_max_sources is not None:
        env["HDC_LLM_SOURCE_CRITIC_MAX_SOURCES"] = str(
            llm_source_critic_max_sources
        )
    if llm_source_credibility_max_sources is not None:
        env["HDC_LLM_SOURCE_CREDIBILITY_MAX_SOURCES"] = str(
            llm_source_credibility_max_sources
        )
    if llm_source_credibility_source_id_allowlist:
        env["HDC_LLM_SOURCE_CREDIBILITY_SOURCE_ID_ALLOWLIST"] = ",".join(
            llm_source_credibility_source_id_allowlist
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
        "structured_task": deepcopy(DEFAULT_STRUCTURED_TASK),
        "studio": {
            "port": None,
            "no_reload": True,
        },
        "live_web": {
            "enabled": True,
            "timeout_seconds": 30,
        },
        "source_search": {
            "enabled": False,
            "mode": "disabled",
            "provider": "tavily",
            "fixture_path": str(DEFAULT_SEARCH_FIXTURE_PATH.relative_to(PROJECT_ROOT)),
            "max_queries": 3,
            "max_results_per_query": 5,
            "max_total_results": 15,
            "timeout_seconds": 15,
            "combine_with_seed_catalog": True,
            "cache_enabled": True,
            "provider_channel_allowlist": list(
                DEFAULT_SEARCH_PROVIDER_CHANNEL_ALLOWLIST
            ),
        },
        "content_fetch": {
            "fetch_search_derived_sources": False,
            "max_search_derived_sources": 2,
            "max_total_sources": 10,
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
            "source_credibility": {
                "enabled": False,
                "max_sources": 6,
                "source_id_allowlist": [],
            },
        },
        "disease_intelligence": {
            "llm_enabled": False,
            "force_llm": False,
            "fallback_to_curated": True,
        },
        "anomaly_detection": {
            "enabled": True,
            "max_cases_threshold": 1000000,
            "max_deaths_threshold": 100000,
            "spike_multiplier": 10,
            "min_prior_records": 1,
        },
        "human_review": {
            "decisions_path": None,
            "apply_decisions": False,
            "require_reviewer_id": True,
        },
        "source_sets": {
            "source_id_allowlist_enabled": True,
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
    disease_intelligence = config.get("disease_intelligence") or {}
    source_search = config.get("source_search") or {}
    content_fetch = config.get("content_fetch") or {}
    human_review = config.get("human_review") or {}
    anomaly_detection = config.get("anomaly_detection") or {}
    source_critic = llm.get("source_critic") or {}
    source_credibility = llm.get("source_credibility") or {}
    source_sets = config.get("source_sets") or {}
    search_enabled = bool(source_search.get("enabled", False))
    search_mode = str(source_search.get("mode") or "disabled").strip().lower()
    if not search_enabled:
        search_mode = "disabled"
    live_search_enabled = (
        search_enabled
        and search_mode == "live"
        and bool(source_search.get("live_search_enabled", True))
    )
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
        llm_source_credibility=bool(source_credibility.get("enabled", False)),
        llm_extraction=bool(llm.get("structured_extraction_enabled", True)),
        llm_disease_intelligence=bool(
            disease_intelligence.get("llm_enabled", False)
        ),
        disease_intelligence_force_llm=bool(
            disease_intelligence.get("force_llm", False)
        ),
        disease_intelligence_fallback_to_curated=bool(
            disease_intelligence.get("fallback_to_curated", True)
        ),
        provider=llm.get("provider"),
        model=llm.get("model"),
        timeout_seconds=float(live_web.get("timeout_seconds", 30)),
        llm_max_chunks=int(llm.get("max_chunks", 8)),
        llm_source_critic_max_sources=source_critic.get("max_sources", 6),
        llm_source_critic_review_blocks_fetch=bool(
            source_critic.get("review_blocks_fetch", False)
        ),
        llm_source_credibility_max_sources=source_credibility.get("max_sources"),
        llm_source_credibility_source_id_allowlist=source_credibility.get(
            "source_id_allowlist"
        ),
        llm_max_tokens=int(llm.get("max_tokens", 4096)),
        fallback_to_rule_based=bool(llm.get("fallback_to_rule_based", False)),
        source_id_allowlist=source_sets.get("workflow_source_ids") or CASE_SOURCE_IDS,
        source_id_allowlist_enabled=bool(
            source_sets.get("source_id_allowlist_enabled", True)
        ),
        llm_source_critic_source_id_allowlist=source_sets.get(
            "llm_source_critic_source_ids"
        )
        or source_sets.get("workflow_source_ids")
        or CASE_SOURCE_IDS,
        live_search=live_search_enabled,
        search_mode=search_mode,
        search_provider=str(source_search.get("provider") or "tavily"),
        search_fixture_path=_resolve_project_path(
            source_search.get("fixture_path"),
            DEFAULT_SEARCH_FIXTURE_PATH,
        ),
        search_max_queries=int(source_search.get("max_queries", 3)),
        search_max_results_per_query=int(
            source_search.get("max_results_per_query", 5)
        ),
        search_max_total_results=int(source_search.get("max_total_results", 15)),
        search_timeout_seconds=float(source_search.get("timeout_seconds", 15)),
        search_combine_with_seed_catalog=bool(
            source_search.get("combine_with_seed_catalog", True)
        ),
        search_cache_enabled=bool(source_search.get("cache_enabled", True)),
        search_provider_channel_allowlist=source_search.get(
            "provider_channel_allowlist"
        )
        or DEFAULT_SEARCH_PROVIDER_CHANNEL_ALLOWLIST,
        fetch_search_derived_sources=bool(
            content_fetch.get("fetch_search_derived_sources", False)
        ),
        fetch_max_search_derived_sources=int(
            content_fetch.get("max_search_derived_sources", 2)
        ),
        fetch_max_total_sources=int(content_fetch.get("max_total_sources", 10)),
        fetch_min_credibility_score=float(
            content_fetch.get("min_credibility_score", 0.55)
        ),
        fetch_allowed_final_roles=content_fetch.get("allowed_final_roles")
        or ["collection", "validation", "collection_support", "context"],
        fetch_allow_needs_review=bool(content_fetch.get("allow_needs_review", False)),
        fetch_domain_allowlist=content_fetch.get("domain_allowlist") or [],
        fetch_domain_blocklist=content_fetch.get("domain_blocklist") or [],
        fetch_max_bytes=int(content_fetch.get("max_bytes", 1_000_000)),
        fetch_parse_pdf_text=bool(content_fetch.get("parse_pdf_text", True)),
        fetch_parse_tables=bool(content_fetch.get("parse_tables", True)),
        fetch_store_raw_text=bool(content_fetch.get("store_raw_text", False)),
        fetch_user_agent=str(
            content_fetch.get("user_agent") or "data-collection-workflow/0.1"
        ),
        content_fixture_map_path=_resolve_project_path(
            content_fetch.get("content_fixture_map_path"),
            PROJECT_ROOT,
        )
        if content_fetch.get("content_fixture_map_path")
        else None,
        human_review_decisions_path=_resolve_project_path(
            human_review.get("decisions_path")
            or config.get("human_review_decisions_path"),
            PROJECT_ROOT,
        )
        if (human_review.get("decisions_path") or config.get("human_review_decisions_path"))
        else None,
        human_review_apply_decisions=bool(
            human_review.get("apply_decisions", False)
        ),
        human_review_require_reviewer_id=bool(
            human_review.get("require_reviewer_id", True)
        ),
        anomaly_max_cases_threshold=float(
            anomaly_detection.get("max_cases_threshold", 1_000_000)
        ),
        anomaly_max_deaths_threshold=float(
            anomaly_detection.get("max_deaths_threshold", 100_000)
        ),
        anomaly_spike_multiplier=float(
            anomaly_detection.get("spike_multiplier", 10)
        ),
        anomaly_min_prior_records=int(
            anomaly_detection.get("min_prior_records", 1)
        ),
    )


def structured_task_from_config(config: dict) -> dict:
    """Return the structured task payload for graph initial state."""

    raw = deepcopy(config.get("structured_task") or {})
    if not isinstance(raw, dict):
        raise ValueError("workflow structured_task must be a JSON object.")

    raw.setdefault("user_request", config.get("user_request") or DEFAULT_USER_REQUEST)
    raw.setdefault("run_label", config.get("profile_name") or LIVE_CASE_STUDY_ID)

    workflow = config.get("workflow") or {}
    collection_mode = workflow.get("collection_mode")
    if collection_mode:
        raw.setdefault("collection_mode", collection_mode)

    return {
        key: value
        for key, value in raw.items()
        if value not in (None, "", [], {})
    }


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
        updated.setdefault("structured_task", {})["user_request"] = user_request
    return updated


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

    state = studio_initial_state(
        config.get("user_request") or DEFAULT_USER_REQUEST,
        structured_task=structured_task_from_config(config),
        include_empty_fields=include_empty_fields,
    )
    human_review = config.get("human_review") or {}
    decisions_path = human_review.get("decisions_path") or config.get(
        "human_review_decisions_path"
    )
    if decisions_path:
        state["human_review_decisions_path"] = str(
            _resolve_project_path(decisions_path, PROJECT_ROOT)
        )
    return state


def studio_initial_state(
    user_request: str | None = None,
    *,
    structured_task: dict | None = None,
    include_empty_fields: bool = True,
) -> dict:
    """Build the state payload a user can submit in LangGraph Studio."""

    state = {"user_request": user_request or DEFAULT_USER_REQUEST}
    if structured_task is not None:
        state["structured_task"] = deepcopy(structured_task)
    if not include_empty_fields:
        return state
    state.update(
        {
            "source_candidates": [],
            "source_search_results": [],
            "source_search_execution_summary": None,
            "source_discovery_summary": None,
            "source_registry": [],
            "source_registry_summary": None,
            "source_screening_summary": None,
            "source_critic_summary": None,
            "source_routing_summary": None,
            "source_credibility_assessments": [],
            "source_credibility_summary": None,
            "documents": [],
            "evidence_chunks": [],
            "raw_records": [],
            "validated_records": [],
            "normalized_records": [],
            "linked_events": [],
            "event_clusters": [],
            "duplicate_clusters": [],
            "validation_records": [],
            "validation_cases": [],
            "validation_comparisons": [],
            "validation_results": [],
            "validation_summary": None,
            "trusted_source_validation_summary": None,
            "cross_source_validation_summary": None,
            "anomaly_results": [],
            "anomaly_summary": None,
            "anomaly_review_items": [],
            "conflicts": [],
            "human_review_queue": [],
            "human_review_decisions": [],
            "human_review_decisions_path": None,
            "applied_human_review_decisions": [],
            "rejected_human_review_decisions": [],
            "human_review_audit_trail": [],
            "human_review_application_summary": None,
            "final_dataset_post_review": [],
            "records_excluded_by_human_review": [],
            "collection_trace": [],
            "collection_spec": None,
            "task_intake_summary": None,
            "disease_intelligence": None,
            "disease_intelligence_summary": None,
            "disease_profile": None,
            "collection_schema": None,
            "source_strategy": None,
            "screening_criteria": None,
            "profile_schema_summary": None,
            "search_queries": None,
            "search_query_inventory": [],
            "agentic_source_plan": None,
            "executable_source_plan_summary": None,
            "source_planning_agent_summary": None,
            "content_fetch_requests": [],
            "content_fetch_summary": None,
            "document_parse_summary": None,
            "fetch_manifest": [],
            "fixture_document_summary": None,
            "document_quality_summary": None,
            "structured_extraction_summary": None,
            "llm_extraction_summary": None,
            "schema_validation_summary": None,
            "record_normalization_summary": None,
            "record_linking_summary": None,
            "event_clustering_summary": None,
            "duplicate_detection_summary": None,
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
