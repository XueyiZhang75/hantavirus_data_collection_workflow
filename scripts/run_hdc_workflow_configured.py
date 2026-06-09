"""Run an HDC workflow runtime profile and export readable artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_SRC = _PROJECT_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))
_SCRIPTS = _PROJECT_ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from hdc_workflow.evaluation_report_builder import (  # noqa: E402
    build_evaluation_report,
    build_evaluation_review_items,
    read_csv_records,
    write_csv_records,
    write_evaluation_outputs,
)
from hdc_workflow.export import export_final_data_package, write_json  # noqa: E402
from hdc_workflow.graph import build_graph  # noqa: E402
from hdc_workflow.search_providers import search_api_key_present  # noqa: E402
from hdc_workflow.validation_source_compatibility import (  # noqa: E402
    resolve_task_compatible_validation_records,
)
from hdc_workflow.workflow_run_config import (  # noqa: E402
    COLLECTION_SOURCE_IDS,
    CONTEXT_SOURCE_IDS,
    DEFAULT_WORKFLOW_RUN_CONFIG_PATH,
    VALIDATION_SOURCE_IDS,
    api_key_present,
    safe_env_for_display,
    load_workflow_run_config,
    resolve_workflow_run_config_path,
    temporary_workflow_env,
    validation_records_path_from_config,
    workflow_console_output_dir_from_config,
    workflow_initial_state_from_config,
    workflow_output_dir_from_config,
    workflow_run_config_with_overrides,
    workflow_run_env_from_config,
)

from build_workflow_run_console import (  # noqa: E402
    build_report as build_workflow_console,
    user_facing_run_status,
)

_TOP_LEVEL_REPORT_PATH = (
    _PROJECT_ROOT / "outputs" / "workflow_runs" / "latest_workflow_run_report_chinese.md"
)
_TOP_LEVEL_SUMMARY_PATH = (
    _PROJECT_ROOT / "outputs" / "workflow_runs" / "latest_workflow_run_summary.json"
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run a configured HDC workflow profile with live source fetch, LLM "
            "source planning, LLM source critic, and LLM structured extraction."
        )
    )
    parser.add_argument(
        "--config",
        default=str(DEFAULT_WORKFLOW_RUN_CONFIG_PATH),
        help="Path to the workflow runtime JSON config file.",
    )
    parser.add_argument(
        "--enable-live-fetch",
        action="store_true",
        help="Override config and enable live HTTP fetch for this run.",
    )
    parser.add_argument(
        "--disable-live-fetch",
        action="store_true",
        help="Override config and disable live HTTP fetch for this run.",
    )
    parser.add_argument(
        "--enable-all-llm",
        action="store_true",
        help="Override config and enable all three LLM stages for this run.",
    )
    parser.add_argument(
        "--disable-all-llm",
        action="store_true",
        help="Override config and disable all three LLM stages for this run.",
    )
    parser.add_argument("--provider", default=None)
    parser.add_argument("--model", default=None)
    parser.add_argument("--timeout-seconds", type=float, default=None)
    parser.add_argument("--llm-max-chunks", type=int, default=None)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument(
        "--session-id",
        default=None,
        help="Optional fixed run session id. Defaults to a UTC timestamp.",
    )
    parser.add_argument("--user-request", default=None)
    parser.add_argument(
        "--print-config-only",
        action="store_true",
        help="Print sanitized configuration without running live fetch or LLM calls.",
    )
    return parser


def _override_value(enable: bool, disable: bool) -> bool | None:
    if enable and disable:
        raise ValueError("Enable/allow and disable flags cannot both be set.")
    if enable:
        return True
    if disable:
        return False
    return None


def _config_with_cli_overrides(args: argparse.Namespace) -> tuple[Path, dict]:
    config_path = resolve_workflow_run_config_path(args.config)
    config = load_workflow_run_config(config_path)
    return config_path, workflow_run_config_with_overrides(
        config,
        live_fetch=_override_value(args.enable_live_fetch, args.disable_live_fetch),
        all_llm=_override_value(args.enable_all_llm, args.disable_all_llm),
        provider=args.provider,
        model=args.model,
        timeout_seconds=args.timeout_seconds,
        llm_max_chunks=args.llm_max_chunks,
        output_dir=args.output_dir,
        session_id=args.session_id,
        user_request=args.user_request,
    )


def _config_provider_model(config: dict) -> tuple[str, str]:
    llm = config.get("llm") or {}
    return str(llm.get("provider") or ""), str(llm.get("model") or "")


def _llm_enabled(env_updates: dict[str, str]) -> bool:
    return any(
        env_updates.get(key) == "true"
        for key in (
            "HDC_ENABLE_LLM_SOURCE_PLANNING",
            "HDC_ENABLE_LLM_SOURCE_CRITIC",
            "HDC_ENABLE_LLM_SOURCE_CREDIBILITY",
            "HDC_ENABLE_LLM_EXTRACTION",
        )
    )


def _console_text(value) -> str:
    return str(value).encode("ascii", errors="backslashreplace").decode("ascii")


def _format_counts(counts: dict | None) -> str:
    if not counts:
        return "none"
    return ", ".join(f"{key}={value}" for key, value in sorted(counts.items()))


def _preview(value, limit: int = 180) -> str:
    text = " ".join(str(value or "").split())
    if not text:
        return "none"
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def _cell(value) -> str:
    text = str(value if value is not None else "").replace("|", "/")
    return _preview(text, 140)


def _case_value(record: dict) -> str:
    for field in (
        "cases_confirmed",
        "cases_unspecified",
        "cases_probable",
        "cases_suspected",
    ):
        value = record.get(field)
        if value not in (None, "", []):
            return str(value)
    return ""


def _count_by(records: list[dict], field: str) -> dict:
    return dict(Counter(str(row.get(field) or "unknown") for row in records))


def _source_role(entry: dict) -> str:
    source_id = entry.get("source_id")
    flags = set(entry.get("routing_flags") or [])
    if (
        source_id in VALIDATION_SOURCE_IDS
        or entry.get("source_role") == "validation_reserved"
        or "validation_reserved" in flags
    ):
        return "validation_reserved"
    if (
        source_id in CONTEXT_SOURCE_IDS
        or entry.get("source_role") == "context_source"
        or "context_only" in flags
    ):
        return "context_only"
    if source_id in COLLECTION_SOURCE_IDS:
        return "collection"
    return "other"


def _source_split_summary(registry: list[dict]) -> dict:
    grouped: dict[str, list[dict]] = {
        "collection": [],
        "context_only": [],
        "validation_reserved": [],
        "other": [],
    }
    for entry in registry:
        grouped.setdefault(_source_role(entry), []).append(entry)
    return {
        role: [
            {
                "source_id": entry.get("source_id"),
                "title": entry.get("title"),
                "publisher": entry.get("publisher"),
                "canonical_url": entry.get("canonical_url"),
                "final_screening_decision": entry.get("final_screening_decision"),
                "ready_for_content_fetch": entry.get("ready_for_content_fetch"),
                "credibility_score": entry.get("credibility_score"),
                "credibility_level": entry.get("credibility_level"),
            }
            for entry in entries
        ]
        for role, entries in grouped.items()
    }


def _live_fetch_summary(result: dict) -> dict:
    documents = list(result.get("documents") or [])
    fetch_summary = result.get("content_fetch_summary") or {}
    quality_summary = result.get("document_quality_summary") or {}
    rows = []
    for doc in documents:
        rows.append(
            {
                "source_id": doc.get("source_id"),
                "url": doc.get("url"),
                "canonical_url": doc.get("canonical_url"),
                "title": doc.get("title"),
                "discovery_method": doc.get("discovery_method"),
                "source_role_final": doc.get("source_role_final"),
                "credibility_score": doc.get("credibility_score"),
                "credibility_level": doc.get("credibility_level"),
                "fetch_status": doc.get("fetch_status"),
                "http_status_code": doc.get("http_status_code"),
                "quality_status": doc.get("quality_status"),
                "parse_status": doc.get("parse_status"),
                "parser_used": doc.get("parser_used"),
                "content_type": doc.get("content_type"),
                "clean_text_char_count": len(doc.get("clean_text") or ""),
                "table_count": doc.get("table_count") or len(doc.get("tables") or []),
                "is_live_fetched": bool(doc.get("is_live_fetched")),
            }
        )
    return {
        "live_fetch_enabled": bool(fetch_summary.get("live_fetch_enabled")),
        "document_count": len(documents),
        "document_source_ids": sorted({row["source_id"] for row in rows if row["source_id"]}),
        "fetch_status_counts": fetch_summary.get("fetch_status_counts") or {},
        "parser_status_counts": fetch_summary.get("parser_status_counts") or {},
        "parser_used_counts": fetch_summary.get("parser_used_counts") or {},
        "selected_search_derived_fetch_count": fetch_summary.get(
            "selected_search_derived_fetch_count", 0
        ),
        "skipped_search_derived_fetch_disabled_count": fetch_summary.get(
            "skipped_search_derived_fetch_disabled_count", 0
        ),
        "skipped_search_derived_by_reason_counts": fetch_summary.get(
            "skipped_search_derived_by_reason_counts"
        )
        or {},
        "quality_status_counts": quality_summary.get("quality_status_counts") or {},
        "skipped_validation_reserved_source_ids": fetch_summary.get(
            "skipped_validation_reserved_source_ids"
        )
        or [],
        "skipped_not_in_allowlist_count": fetch_summary.get(
            "skipped_not_in_allowlist_count", 0
        ),
        "documents": rows,
    }


def _llm_stage_summary(result: dict, provider: str, model: str) -> dict:
    disease_intelligence = result.get("disease_intelligence_summary") or {}
    executable_plan = result.get("executable_source_plan_summary") or {}
    planning = result.get("source_planning_agent_summary") or {}
    critic = result.get("source_critic_summary") or {}
    credibility = result.get("source_credibility_summary") or {}
    extraction = result.get("structured_extraction_summary") or {}
    llm_extraction = result.get("llm_extraction_summary") or {}
    return {
        "provider": provider,
        "model": model,
        "api_key_present": api_key_present(provider),
        "disease_intelligence": {
            "generation_method": disease_intelligence.get("generation_method"),
            "disease_standard_name": disease_intelligence.get(
                "disease_standard_name"
            ),
            "query_term_count": disease_intelligence.get("query_term_count", 0),
            "warnings": disease_intelligence.get("warnings") or [],
            "llm_call_succeeded": (
                disease_intelligence.get("generation_method") == "llm_generated"
            ),
        },
        "source_planning": {
            "enabled": bool(planning.get("llm_source_planning_enabled")),
            "status": planning.get("status"),
            "generation_method": executable_plan.get("generation_method")
            or planning.get("generation_method"),
            "execution_status": executable_plan.get("execution_status")
            or planning.get("execution_status"),
            "planned_query_count": executable_plan.get("planned_query_count", 0),
            "planned_source_category_count": executable_plan.get(
                "planned_source_category_count", 0
            ),
            "provider_channel_counts": executable_plan.get(
                "provider_channel_counts"
            )
            or {},
            "agent_query_count": planning.get("agent_query_count", 0),
            "agent_query_added_count": planning.get("agent_query_added_count", 0),
            "candidate_hint_count": planning.get("agent_candidate_hint_count", 0),
            "warnings": executable_plan.get("warnings")
            or planning.get("warnings")
            or [],
            "failure_type": planning.get("failure_type"),
            "failure_message": planning.get("failure_message"),
        },
        "source_critic": {
            "enabled": bool(critic.get("llm_source_critic_enabled")),
            "attempted_source_count": critic.get(
                "attempted_source_count",
                critic.get("llm_source_critic_attempted_source_count", 0),
            ),
            "assessed_source_count": critic.get(
                "assessed_source_count", critic.get("llm_assessed_source_count", 0)
            ),
            "skipped_source_count": critic.get(
                "skipped_source_count", critic.get("llm_skipped_source_count", 0)
            ),
            "blocked_fetch_count": critic.get("blocked_fetch_count", 0),
            "needs_review_count": critic.get("needs_review_count", 0),
            "allowed_fetch_count": critic.get("allowed_fetch_count", 0),
            "context_only_count": critic.get("context_only_count", 0),
            "decision_counts": critic.get("decision_counts") or {},
            "fetch_recommendation_counts": (
                critic.get("fetch_recommendation_counts") or {}
            ),
            "risk_flag_counts": critic.get("risk_flag_counts") or {},
            "selection": critic.get("source_critic_selection_summary") or {},
            "allowlist_enabled": critic.get(
                "llm_source_critic_allowlist_enabled", False
            ),
            "max_sources": critic.get("llm_source_critic_max_sources"),
            "review_blocks_fetch": critic.get(
                "llm_source_critic_review_blocks_fetch"
            ),
            "failure_count": critic.get("llm_source_critic_failure_count", 0),
            "semantic_leakage_count": critic.get("llm_semantic_leakage_count", 0),
            "human_review_recommended_count": critic.get(
                "llm_human_review_recommended_count", 0
            ),
        },
        "source_credibility": {
            "enabled": bool(credibility.get("llm_enabled")),
            "assessed_source_count": credibility.get("assessed_source_count", 0),
            "role_counts": credibility.get("role_counts") or {},
            "risk_flag_counts": credibility.get("risk_flag_counts") or {},
            "llm_assessed_count": credibility.get("llm_assessed_count", 0),
            "llm_failure_count": credibility.get("llm_failure_count", 0),
            "needs_review_count": credibility.get("needs_review_count", 0),
        },
        "structured_extraction": {
            "enabled": bool(extraction.get("llm_enabled")),
            "mode": extraction.get("extraction_mode"),
            "eligible_chunk_count": extraction.get("llm_eligible_chunk_count", 0),
            "call_count": extraction.get("llm_call_count", 0),
            "success_count": extraction.get("llm_success_count", 0),
            "error_count": extraction.get("llm_error_count", 0),
            "fallback_count": extraction.get("llm_fallback_count", 0),
            "raw_record_count": extraction.get("raw_record_count", 0),
            "max_chunks": extraction.get("llm_max_chunks"),
            "error_messages": llm_extraction.get("llm_error_messages") or [],
        },
    }


def _write_validation_outputs(
    output_dir: Path,
    validation_records: list[dict],
    registry: list[dict],
    *,
    inactive_validation_records: list[dict] | None = None,
    validation_source_compatibility_summary: dict | None = None,
    raw_validation_records: list[dict] | None = None,
) -> dict:
    validation_dir = output_dir / "validation"
    all_validation_records = (
        list(validation_records)
        + list(inactive_validation_records or [])
        + list(raw_validation_records or [])
    )
    validation_fieldnames = sorted(
        {key for record in all_validation_records for key in record.keys()}
    )
    write_csv_records(
        validation_dir / "ground_truth_records.csv",
        validation_records,
        fieldnames=validation_fieldnames or None,
    )
    write_csv_records(
        validation_dir / "inactive_validation_records.csv",
        list(inactive_validation_records or []),
        fieldnames=validation_fieldnames or None,
    )
    write_json(
        list(inactive_validation_records or []),
        validation_dir / "inactive_validation_records.json",
    )
    write_json(
        validation_source_compatibility_summary or {},
        validation_dir / "validation_source_compatibility_summary.json",
    )
    validation_ids = {
        row.get("source_id") for row in validation_records if row.get("source_id")
    }
    validation_registry = [
        entry for entry in registry if entry.get("source_id") in validation_ids
    ]
    write_json(validation_registry, validation_dir / "validation_source_registry.json")
    return {
        "ground_truth_records_csv": str(validation_dir / "ground_truth_records.csv"),
        "validation_source_registry_json": str(
            validation_dir / "validation_source_registry.json"
        ),
        "validation_source_registry_count": len(validation_registry),
        "active_validation_record_count": len(validation_records),
        "inactive_validation_record_count": len(inactive_validation_records or []),
        "raw_validation_record_count": len(raw_validation_records or []),
        "validation_source_compatibility_status": (
            validation_source_compatibility_summary or {}
        ).get("compatibility_status"),
        "inactive_validation_records_csv": str(
            validation_dir / "inactive_validation_records.csv"
        ),
        "inactive_validation_records_json": str(
            validation_dir / "inactive_validation_records.json"
        ),
        "validation_source_compatibility_summary_json": str(
            validation_dir / "validation_source_compatibility_summary.json"
        ),
    }


def _append_stage11_report_section(
    lines: list[str],
    *,
    anomaly_results: list[dict],
    anomaly_summary: dict,
    human_review_application_summary: dict,
    applied_decisions: list[dict],
    rejected_decisions: list[dict],
    audit_trail: list[dict],
    final_dataset_post_review: list[dict],
    records_excluded_by_review: list[dict],
) -> None:
    lines.extend(
        [
            "",
            "## 9.5 Stage 11 anomaly detection and review application",
            "",
            f"- Anomaly result count: `{len(anomaly_results)}`",
            f"- Anomaly severity counts: `{_format_counts(anomaly_summary.get('severity_counts'))}`",
            f"- Anomaly needs-human-review count: `{anomaly_summary.get('needs_human_review_count', 0)}`",
            f"- Decisions provided: `{human_review_application_summary.get('decisions_provided_count', 0)}`",
            f"- Decisions applied: `{human_review_application_summary.get('decisions_applied_count', 0)}`",
            f"- Decisions rejected: `{human_review_application_summary.get('decisions_rejected_count', 0)}`",
            f"- Audit entries: `{len(audit_trail)}`",
            f"- Final dataset post-review count: `{len(final_dataset_post_review)}`",
            f"- Records excluded by review: `{len(records_excluded_by_review)}`",
            "",
            "| Anomaly ID | Type | Severity | Target | Reason |",
            "|---|---|---|---|---|",
        ]
    )
    for anomaly in anomaly_results[:12]:
        target = (
            anomaly.get("record_id")
            or anomaly.get("event_cluster_id")
            or anomaly.get("validation_result_id")
            or anomaly.get("source_id")
        )
        lines.append(
            "| "
            + " | ".join(
                [
                    _cell(anomaly.get("anomaly_id")),
                    _cell(anomaly.get("anomaly_type")),
                    _cell(anomaly.get("severity")),
                    _cell(target),
                    _cell(anomaly.get("reason")),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "| Applied decision | Type | Target | Audit IDs | Reason |",
            "|---|---|---|---|---|",
        ]
    )
    for decision in applied_decisions[:12]:
        lines.append(
            "| "
            + " | ".join(
                [
                    _cell(decision.get("decision_id")),
                    _cell(decision.get("decision_type")),
                    _cell(", ".join(decision.get("target_ids") or [])),
                    _cell(", ".join(decision.get("audit_ids") or [])),
                    _cell(decision.get("reason")),
                ]
            )
            + " |"
        )
    if rejected_decisions:
        lines.extend(
            [
                "",
                "| Rejected decision | Type | Target | Rejection reason |",
                "|---|---|---|---|",
            ]
        )
        for decision in rejected_decisions[:12]:
            lines.append(
                "| "
                + " | ".join(
                    [
                        _cell(decision.get("decision_id")),
                        _cell(decision.get("decision_type")),
                        _cell(", ".join(decision.get("target_ids") or [])),
                        _cell(decision.get("rejection_reason")),
                    ]
                )
                + " |"
            )


def _write_report(
    path: Path,
    *,
    user_request: str,
    provider: str,
    model: str,
    output_dir: Path,
    result: dict,
    collection_manifest: dict,
    validation_manifest: dict,
    evaluation_outputs: dict,
    evaluation_rows: list[dict],
    evaluation_summary: dict,
    source_split: dict,
    live_summary: dict,
    llm_summary: dict,
) -> str:
    trace = list(result.get("collection_trace") or [])
    registry = list(result.get("source_registry") or [])
    records = list(result.get("normalized_records") or [])
    review_items = list(result.get("human_review_queue") or [])
    final_package = result.get("final_data_package") or {}
    metadata = final_package.get("package_metadata") or {}
    anomaly_results = list(
        result.get("anomaly_results") or final_package.get("anomaly_results") or []
    )
    anomaly_summary = (
        result.get("anomaly_summary") or final_package.get("anomaly_summary") or {}
    )
    human_review_application_summary = (
        result.get("human_review_application_summary")
        or final_package.get("human_review_application_summary")
        or {}
    )
    applied_decisions = list(
        result.get("applied_human_review_decisions")
        or final_package.get("applied_human_review_decisions")
        or []
    )
    rejected_decisions = list(
        result.get("rejected_human_review_decisions")
        or final_package.get("rejected_human_review_decisions")
        or []
    )
    audit_trail = list(
        result.get("human_review_audit_trail")
        or final_package.get("human_review_audit_trail")
        or []
    )
    final_dataset_post_review = list(
        result.get("final_dataset_post_review")
        or final_package.get("final_dataset_post_review")
        or []
    )
    records_excluded_by_review = list(
        result.get("records_excluded_by_human_review")
        or final_package.get("records_excluded_by_human_review")
        or []
    )
    route = result.get("current_route")
    source_search = result.get("source_search_execution_summary") or {}
    source_discovery = result.get("source_discovery_summary") or {}
    source_credibility = result.get("source_credibility_summary") or {}
    disease_relevance = result.get("disease_relevance_summary") or {}
    run_quality = result.get("run_quality_summary") or final_package.get(
        "run_quality_summary"
    ) or {}
    final_dataset_quality = result.get(
        "final_dataset_quality_summary"
    ) or final_package.get("final_dataset_quality_summary") or {}
    final_dataset_pre_quality_gate = list(
        result.get("final_dataset_pre_quality_gate")
        or final_package.get("final_dataset_pre_quality_gate")
        or []
    )
    quarantined_records = list(
        result.get("quarantined_records")
        or final_package.get("quarantined_records")
        or []
    )
    pending_review_records = list(
        result.get("pending_review_records")
        or final_package.get("pending_review_records")
        or []
    )
    accepted_records = list(final_package.get("final_dataset") or [])
    accepted_record_count = len(accepted_records)
    pre_quality_record_count = len(final_dataset_pre_quality_gate)
    quarantined_record_count = len(quarantined_records)
    pending_review_record_count = len(pending_review_records)
    post_review_record_count = len(final_dataset_post_review)
    run_status_text = user_facing_run_status(run_quality)
    recommended_user_message = run_quality.get("recommended_user_message")
    validation_compatibility_status = validation_manifest.get(
        "validation_source_compatibility_status"
    )
    validation_limited = bool(
        run_quality.get("validation_limited")
        or run_quality.get("no_compatible_validation_source")
        or validation_compatibility_status
        in {
            "incompatible_validation_source_disabled",
            "no_task_compatible_validation_source",
            "missing_validation_source",
        }
    )

    node_lines = [
        f"{idx}. `{event.get('node_name')}` - {_preview(event.get('message'), 120)}"
        for idx, event in enumerate(trace, 1)
    ]
    if not node_lines:
        node_lines = ["- no trace events"]

    lines = [
        "# data collection workflow Run Report",
        "",
        "## 1. 输入任务",
        "",
        user_request,
        "",
        "## 2. 本次运行模式",
        "",
        f"- Live webpage fetch: `{live_summary.get('live_fetch_enabled', False)}`",
        f"- Fixture documents: `{bool((result.get('content_fetch_summary') or {}).get('fixture_documents_enabled'))}`",
        f"- Provider: `{provider}`",
        f"- Model: `{model}`",
        f"- API key present: `{api_key_present(provider)}`",
        f"- LLM source planning: `{llm_summary['source_planning']['enabled']}`",
        f"- LLM source critic: `{llm_summary['source_critic']['enabled']}`",
        f"- LLM structured extraction: `{llm_summary['structured_extraction']['enabled']}`",
        f"- Source search mode: `{source_search.get('search_mode') or 'disabled'}`",
        f"- Source search provider: `{source_search.get('search_provider') or 'n/a'}`",
        f"- Source search executed queries: `{source_search.get('executed_query_count', 0)}`",
        f"- Search-derived source candidates: `{source_search.get('candidate_from_search_count', 0)}`",
        f"- Source credibility assessed sources: `{source_credibility.get('assessed_source_count', 0)}`",
        f"- Source credibility role counts: `{source_credibility.get('role_counts') or {}}`",
        f"- Source discovery method: `{source_discovery.get('discovery_method')}`",
        f"- Disease relevance target: `{disease_relevance.get('target_disease') or 'n/a'}`",
        f"- Disease relevance source status counts: `{disease_relevance.get('source_status_counts') or {}}`",
        f"- Disease relevance chunk status counts: `{disease_relevance.get('chunk_status_counts') or {}}`",
        f"- Disease relevance record status counts: `{disease_relevance.get('record_compatibility_status_counts') or {}}`",
        f"- Rejected incompatible record count: `{disease_relevance.get('rejected_incompatible_record_count', 0)}`",
        f"- Final route: `{route}`",
        "",
        "## 2.5 Run quality status",
        "",
        f"- User-facing run status: `{run_status_text}`",
        "- Technical execution status: `completed`",
        f"- Run quality status: `{run_quality.get('run_quality_status') or 'n/a'}`",
        f"- Final dataset mode: `{run_quality.get('final_dataset_mode') or 'n/a'}`",
        f"- Accepted final dataset count: `{accepted_record_count}`",
        f"- Pre-quality-gate record count: `{pre_quality_record_count}`",
        f"- Quarantined record count: `{quarantined_record_count}`",
        f"- Pending review record count: `{pending_review_record_count}`",
        f"- Final dataset post-review count: `{post_review_record_count}`",
        f"- Recommended user message: `{recommended_user_message or 'n/a'}`",
        "",
        *(
            [
                (
                    "workflow technically completed, but no quality-gated accepted "
                    "records were produced."
                ),
                (
                    "本次 workflow 技术上完成，但没有产生通过质量门的 accepted "
                    "records。"
                ),
                "",
            ]
            if accepted_record_count == 0
            else [
                "Workflow technically completed and produced quality-gated accepted records.",
                "",
            ]
        ),
        *(
            [
                (
                    "Held-out validation was limited because no task-compatible "
                    "validation source was available."
                ),
                (
                    "未找到与本次任务兼容的 held-out validation source；这不是自动失败，"
                    "但 validation 有局限。"
                ),
                "",
            ]
            if validation_limited
            else []
        ),
        "## 3. Workflow 运行过程",
        "",
        (
            "Graph is executed as a mostly serial workflow. The only conditional "
            "branch is after `quality_gate_routing`: the run enters "
            "`human_review` when quality or validation checks require review, "
            "then still builds the final data package. In this run, the graph "
            "route is shown above; validation comparison review flags are "
            "reported separately in Section 8."
        ),
        "",
        *node_lines,
        "",
        "## 4. 数据源分工",
        "",
        "| Role | Source ID | Publisher / title | Credibility | Final decision | Fetch ready |",
        "|---|---|---|---|---|---|",
    ]
    for role in ("collection", "context_only", "validation_reserved", "other"):
        for entry in source_split.get(role) or []:
            title = f"{entry.get('publisher') or ''} / {entry.get('title') or ''}"
            lines.append(
                "| "
                + " | ".join(
                    [
                        _cell(role),
                        _cell(entry.get("source_id")),
                        _cell(title),
                        _cell(
                            f"{entry.get('credibility_level') or 'n/a'}"
                            f" ({entry.get('credibility_score') or 'n/a'})"
                        ),
                        _cell(entry.get("final_screening_decision")),
                        _cell(entry.get("ready_for_content_fetch")),
                    ]
                )
                + " |"
            )

    lines.extend(
        [
            "",
            "## 5. 真实网页抓取结果",
            "",
            f"- Documents fetched/parsed: `{live_summary.get('document_count', 0)}`",
            f"- Search-derived sources selected for fetch: `{live_summary.get('selected_search_derived_fetch_count', 0)}`",
            f"- Search-derived skipped by reason: `{live_summary.get('skipped_search_derived_by_reason_counts') or {}}`",
            f"- Fetch status counts: `{_format_counts(live_summary.get('fetch_status_counts'))}`",
            f"- Parser status counts: `{_format_counts(live_summary.get('parser_status_counts'))}`",
            f"- Parser used counts: `{_format_counts(live_summary.get('parser_used_counts'))}`",
            f"- Quality status counts: `{_format_counts(live_summary.get('quality_status_counts'))}`",
            f"- Validation-reserved skipped from fetch: `{live_summary.get('skipped_validation_reserved_source_ids')}`",
            "",
            "| Source ID | Fetch status | HTTP | Parse | Parser | Quality | Text chars | Tables |",
            "|---|---|---|---|---|---|---|---|",
        ]
    )
    for row in live_summary.get("documents") or []:
        lines.append(
            "| "
            + " | ".join(
                    [
                        _cell(row.get("source_id")),
                        _cell(row.get("fetch_status")),
                        _cell(row.get("http_status_code")),
                        _cell(row.get("parse_status")),
                        _cell(row.get("parser_used")),
                        _cell(row.get("quality_status")),
                        _cell(row.get("clean_text_char_count")),
                        _cell(row.get("table_count")),
                    ]
                )
            + " |"
        )

    lines.extend(
        [
            "",
            "## 6. 三个 LLM 环节调用结果",
            "",
            "### 6.1 LLM Source Planning",
            "",
            f"- Status: `{llm_summary['source_planning'].get('status')}`",
            f"- Plan generation method: `{llm_summary['source_planning'].get('generation_method')}`",
            f"- Plan execution status: `{llm_summary['source_planning'].get('execution_status')}`",
            f"- Planned query count: `{llm_summary['source_planning'].get('planned_query_count')}`",
            f"- Planned source category count: `{llm_summary['source_planning'].get('planned_source_category_count')}`",
            f"- Provider channel counts: `{_format_counts(llm_summary['source_planning'].get('provider_channel_counts'))}`",
            f"- Agent query count: `{llm_summary['source_planning'].get('agent_query_count')}`",
            f"- Agent query added count: `{llm_summary['source_planning'].get('agent_query_added_count')}`",
            f"- Candidate hint count: `{llm_summary['source_planning'].get('candidate_hint_count')}`",
            "",
            "### 6.2 LLM Source Critic",
            "",
            f"- Attempted source count: `{llm_summary['source_critic'].get('attempted_source_count')}`",
            f"- Assessed source count: `{llm_summary['source_critic'].get('assessed_source_count')}`",
            f"- Skipped source count: `{llm_summary['source_critic'].get('skipped_source_count')}`",
            f"- Blocked fetch count: `{llm_summary['source_critic'].get('blocked_fetch_count')}`",
            f"- Allowed fetch count: `{llm_summary['source_critic'].get('allowed_fetch_count')}`",
            f"- Context-only count: `{llm_summary['source_critic'].get('context_only_count')}`",
            f"- Needs review count: `{llm_summary['source_critic'].get('needs_review_count')}`",
            f"- Max sources: `{llm_summary['source_critic'].get('max_sources')}`",
            f"- Review blocks fetch: `{llm_summary['source_critic'].get('review_blocks_fetch')}`",
            f"- Failure count: `{llm_summary['source_critic'].get('failure_count')}`",
            f"- Semantic leakage count: `{llm_summary['source_critic'].get('semantic_leakage_count')}`",
            f"- Human review recommended count: `{llm_summary['source_critic'].get('human_review_recommended_count')}`",
            f"- Critic decision counts: `{_format_counts(llm_summary['source_critic'].get('decision_counts'))}`",
            f"- Fetch recommendation counts: `{_format_counts(llm_summary['source_critic'].get('fetch_recommendation_counts'))}`",
            f"- Risk flag counts: `{_format_counts(llm_summary['source_critic'].get('risk_flag_counts'))}`",
            f"- Selected source IDs: `{', '.join(llm_summary['source_critic'].get('selection', {}).get('selected_source_ids') or [])}`",
            "",
            "### 6.3 Optional LLM Source Credibility Advisory",
            "",
            f"- Enabled: `{llm_summary['source_credibility'].get('enabled')}`",
            f"- Assessed source count: `{llm_summary['source_credibility'].get('assessed_source_count')}`",
            f"- Final role counts: `{_format_counts(llm_summary['source_credibility'].get('role_counts'))}`",
            f"- Risk flag counts: `{_format_counts(llm_summary['source_credibility'].get('risk_flag_counts'))}`",
            f"- LLM assessed count: `{llm_summary['source_credibility'].get('llm_assessed_count')}`",
            f"- LLM failure count: `{llm_summary['source_credibility'].get('llm_failure_count')}`",
            f"- Needs review count: `{llm_summary['source_credibility'].get('needs_review_count')}`",
            "",
            "### 6.4 LLM Structured Extraction",
            "",
            f"- Extraction mode: `{llm_summary['structured_extraction'].get('mode')}`",
            f"- Eligible chunk count: `{llm_summary['structured_extraction'].get('eligible_chunk_count')}`",
            f"- LLM call count: `{llm_summary['structured_extraction'].get('call_count')}`",
            f"- LLM success count: `{llm_summary['structured_extraction'].get('success_count')}`",
            f"- LLM error count: `{llm_summary['structured_extraction'].get('error_count')}`",
            f"- Raw record count: `{llm_summary['structured_extraction'].get('raw_record_count')}`",
            "",
            "## 7. 最终抽取 records",
            "",
            f"- Normalized record count: `{len(records)}`",
            f"- Run quality status: `{run_quality.get('run_quality_status') or 'n/a'}`",
            f"- Final dataset mode: `{run_quality.get('final_dataset_mode') or 'n/a'}`",
            f"- Quality-gated accepted final dataset count: `{accepted_record_count}`",
            f"- Pre-quality-gate record count: `{pre_quality_record_count}`",
            f"- Quarantined record count: `{quarantined_record_count}`",
            f"- Pending review record count: `{pending_review_record_count}`",
            f"- Final dataset post-review count: `{post_review_record_count}`",
            f"- Record inclusion status counts: `{final_dataset_quality.get('record_final_inclusion_status_counts') or {}}`",
            f"- Run quality warnings: `{run_quality.get('warnings') or []}`",
            f"- Accepted source counts: `{_format_counts(_count_by(accepted_records, 'source_id'))}`",
            "",
            *(
                [
                    "No quality-gated records are available to list.",
                    "Candidate records, if any, are recorded in the pre-quality, quarantined, and pending-review artifacts.",
                    "",
                ]
                if accepted_record_count == 0
                else []
            ),
            "| Record ID | Date / period | Location | Cases | Deaths | Source | LLM used |",
            "|---|---|---|---|---|---|---|",
        ]
    )
    for record in accepted_records[:12]:
        date_value = record.get("reporting_period") or record.get("date_reported") or record.get("date_anchor")
        location = record.get("subnational_location") or record.get("geographic_scope") or record.get("country")
        lines.append(
            "| "
            + " | ".join(
                [
                    _cell(record.get("record_id")),
                    _cell(date_value),
                    _cell(location),
                    _cell(_case_value(record)),
                    _cell(record.get("deaths")),
                    _cell(record.get("source_id")),
                    _cell(record.get("llm_used")),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## 8. Validation 对比",
            "",
            (
                "- Validation source compatibility status: "
                f"`{validation_manifest.get('validation_source_compatibility_status')}`"
            ),
            (
                "- Active / inactive / raw validation records: "
                f"`{validation_manifest.get('active_validation_record_count', 0)}` / "
                f"`{validation_manifest.get('inactive_validation_record_count', 0)}` / "
                f"`{validation_manifest.get('raw_validation_record_count', 0)}`"
            ),
            f"- Validation record count: `{evaluation_summary.get('validation_record_count', 0)}`",
            f"- Evaluation row count: `{evaluation_summary.get('evaluation_row_count', 0)}`",
            f"- Evaluation rows flagged for human review: `{evaluation_summary.get('human_review_flagged_row_count', 0)}`",
            f"- Overall match status counts: `{_format_counts(evaluation_summary.get('overall_match_status_counts'))}`",
            f"- Masking compliance status counts: `{_format_counts(evaluation_summary.get('masking_compliance_status_counts'))}`",
            f"- Reserved source leakage count: `{evaluation_summary.get('reserved_source_leakage_count', 0)}`",
            "",
            "| Eval row | Status | Collection cases | Validation cases | Human review | Reason |",
            "|---|---|---|---|---|---|",
        ]
    )
    for row in evaluation_rows[:12]:
        lines.append(
            "| "
            + " | ".join(
                [
                    _cell(row.get("evaluation_row_id")),
                    _cell(row.get("overall_match_status")),
                    _cell(row.get("collection_case_count")),
                    _cell(row.get("validation_case_count")),
                    _cell(row.get("human_review_flag")),
                    _cell(row.get("review_reason")),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## 9. Human review queue",
            "",
            f"- Human review item count: `{len(review_items)}`",
            f"- Evaluation review flag count: `{evaluation_summary.get('human_review_flagged_row_count', 0)}`",
            f"- Anomaly review item count: `{len([item for item in review_items if item.get('item_type') == 'anomaly'])}`",
            "",
            "| Review ID | Type | Related IDs | Reason |",
            "|---|---|---|---|",
        ]
    )
    for item in review_items[:12]:
        lines.append(
            "| "
            + " | ".join(
                [
                    _cell(item.get("review_id")),
                    _cell(item.get("item_type")),
                    _cell(", ".join(item.get("related_ids") or [])),
                    _cell(item.get("reason")),
                ]
            )
            + " |"
        )

    _append_stage11_report_section(
        lines,
        anomaly_results=anomaly_results,
        anomaly_summary=anomaly_summary,
        human_review_application_summary=human_review_application_summary,
        applied_decisions=applied_decisions,
        rejected_decisions=rejected_decisions,
        audit_trail=audit_trail,
        final_dataset_post_review=final_dataset_post_review,
        records_excluded_by_review=records_excluded_by_review,
    )

    lines.extend(
        [
            "",
            "## 10. 输出文件",
            "",
            f"- Run output directory: `{output_dir}`",
            f"- Collection final dataset: `{collection_manifest['files'].get('final_dataset_csv')}`",
            f"- Collection pre-quality-gate records: `{collection_manifest['files'].get('final_dataset_pre_quality_gate_csv')}`",
            f"- Collection quarantined records: `{collection_manifest['files'].get('quarantined_records_csv')}`",
            f"- Collection pending review records: `{collection_manifest['files'].get('pending_review_records_csv')}`",
            f"- Collection record inclusion decisions: `{collection_manifest['files'].get('record_inclusion_decisions_json')}`",
            f"- Collection final dataset post-review: `{collection_manifest['files'].get('final_dataset_post_review_csv')}`",
            f"- Collection anomaly results: `{collection_manifest['files'].get('anomaly_results_json')}`",
            f"- Collection human review audit trail: `{collection_manifest['files'].get('human_review_audit_trail_json')}`",
            f"- Collection source registry: `{collection_manifest['files'].get('source_registry_json')}`",
            f"- Validation ground truth: `{validation_manifest.get('ground_truth_records_csv')}`",
            (
                "- Inactive validation records: "
                f"`{validation_manifest.get('inactive_validation_records_csv')}`"
            ),
            (
                "- Validation compatibility summary: "
                f"`{validation_manifest.get('validation_source_compatibility_summary_json')}`"
            ),
            f"- Evaluation report CSV: `{evaluation_outputs.get('evaluation_report_csv')}`",
            f"- Human-readable report: `{path}`",
            "",
            "## 11. 当前结论",
            "",
            (
                "This workflow run executed the configured data collection workflow "
                "through the exported graph and artifact pipeline. The user-facing "
                f"run status is: {run_status_text}"
            ),
            *(
                [
                    (
                        "The run completed technically, but it should not be read as "
                        "a successful data collection result because no quality-gated "
                        "accepted records were produced."
                    )
                ]
                if accepted_record_count == 0
                else [
                    (
                        "The run completed technically and produced quality-gated "
                        "accepted records in the final dataset."
                    )
                ]
            ),
            "",
            f"- Package metadata says LLM used: `{metadata.get('llm_used')}`",
            f"- Contains synthetic fixture data: `{metadata.get('contains_synthetic_fixture_data')}`",
            f"- Generated at UTC: `{datetime.now(timezone.utc).isoformat()}`",
            "",
        ]
    )
    report = "\n".join(lines)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report, encoding="utf-8")
    return report


def run_workflow(args: argparse.Namespace) -> dict:
    _, config = _config_with_cli_overrides(args)
    provider, model = _config_provider_model(config)
    output_dir = workflow_output_dir_from_config(config)
    env_updates = workflow_run_env_from_config(config)
    output_config = config.get("output") or {}
    workflow_config = config.get("workflow") or {}
    validation_records_requested_path = workflow_config.get(
        "validation_ground_truth_records_path"
    )
    validation_records_explicit = validation_records_requested_path not in {
        None,
        "",
    }
    validation_records_path = validation_records_path_from_config(config)
    validation_records = (
        read_csv_records(validation_records_path)
        if validation_records_path.exists()
        else []
    )
    validation_config = config.get("validation") or {}
    allow_incompatible_validation_records = validation_config.get(
        "allow_incompatible_validation_records"
    )
    initial_state = workflow_initial_state_from_config(config)
    resolved_validation = resolve_task_compatible_validation_records(
        validation_records=validation_records,
        state_or_task_context=initial_state,
        validation_records_path=validation_records_path,
        validation_records_path_requested=validation_records_requested_path,
        validation_records_explicit=validation_records_explicit,
        validation_records_defaulted=not validation_records_explicit,
        allow_incompatible_validation_records=allow_incompatible_validation_records,
    )

    with temporary_workflow_env(env_updates):
        initial_state["validation_records"] = validation_records
        initial_state["active_validation_records"] = resolved_validation[
            "active_validation_records"
        ]
        initial_state["inactive_validation_records"] = resolved_validation[
            "inactive_validation_records"
        ]
        initial_state["validation_source_compatibility_summary"] = (
            resolved_validation["validation_source_compatibility_summary"]
        )
        result = build_graph().invoke(initial_state)

    package = dict(result.get("final_data_package") or {})
    registry = list(result.get("source_registry") or package.get("source_registry") or [])
    active_validation_records = list(
        result.get("active_validation_records")
        if "active_validation_records" in result
        else resolved_validation["active_validation_records"]
    )
    inactive_validation_records = list(
        result.get("inactive_validation_records")
        if "inactive_validation_records" in result
        else resolved_validation["inactive_validation_records"]
    )
    validation_source_compatibility_summary = dict(
        result.get("validation_source_compatibility_summary")
        or resolved_validation["validation_source_compatibility_summary"]
    )
    validation_manifest = _write_validation_outputs(
        output_dir,
        active_validation_records,
        registry,
        inactive_validation_records=inactive_validation_records,
        validation_source_compatibility_summary=validation_source_compatibility_summary,
        raw_validation_records=validation_records,
    )
    evaluation_rows, evaluation_summary = build_evaluation_report(
        collection_records=package.get("final_dataset") or [],
        validation_records=active_validation_records,
        collection_source_registry=package.get("source_registry") or [],
        reserved_source_ids=set(VALIDATION_SOURCE_IDS),
        conflicts=package.get("conflicts") or [],
        human_review_items=package.get("human_review_items") or [],
        validation_source_compatibility_summary=validation_source_compatibility_summary,
    )
    evaluation_summary.update(
        {
            "live_fetch_enabled": env_updates.get("HDC_ENABLE_LIVE_FETCH") == "true",
            "fixture_documents_enabled": False,
            "llm_source_planning_enabled": env_updates.get(
                "HDC_ENABLE_LLM_SOURCE_PLANNING"
            )
            == "true",
            "llm_source_critic_enabled": env_updates.get(
                "HDC_ENABLE_LLM_SOURCE_CRITIC"
            )
            == "true",
            "llm_extraction_enabled": env_updates.get("HDC_ENABLE_LLM_EXTRACTION")
            == "true",
            "provider": provider,
            "model": model,
        }
    )
    existing_review_ids = {
        str(item.get("review_id"))
        for item in (package.get("human_review_items") or [])
        if item.get("review_id")
    }
    evaluation_review_items = build_evaluation_review_items(
        evaluation_rows,
        existing_review_ids=existing_review_ids,
    )
    if evaluation_review_items:
        package["human_review_items"] = (
            evaluation_review_items + list(package.get("human_review_items") or [])
        )
        result["human_review_queue"] = (
            evaluation_review_items + list(result.get("human_review_queue") or [])
        )
        result["final_data_package"] = package
        evaluation_summary["evaluation_review_item_count"] = len(evaluation_review_items)
    else:
        evaluation_summary["evaluation_review_item_count"] = 0
    evaluation_summary["human_review_item_count"] = len(
        package.get("human_review_items") or []
    )
    collection_manifest = export_final_data_package(package, output_dir / "collection")
    evaluation_outputs = write_evaluation_outputs(
        evaluation_rows,
        evaluation_summary,
        output_dir / "evaluation",
    )
    source_split = _source_split_summary(registry)
    live_summary = _live_fetch_summary(result)
    llm_summary = _llm_stage_summary(result, provider, model)

    diagnostics_dir = output_dir / "diagnostics"
    write_json(source_split, diagnostics_dir / "source_split_summary.json")
    write_json(live_summary, diagnostics_dir / "live_fetch_summary.json")
    write_json(
        result.get("content_fetch_summary") or {},
        diagnostics_dir / "content_fetch_summary.json",
    )
    write_json(
        result.get("document_quality_summary") or {},
        diagnostics_dir / "document_quality_summary.json",
    )
    write_json(
        result.get("document_parse_summary") or {},
        diagnostics_dir / "document_parse_summary.json",
    )
    write_json(
        result.get("fetch_manifest") or [],
        diagnostics_dir / "fetch_manifest.json",
    )
    write_json(llm_summary, diagnostics_dir / "llm_stage_summary.json")
    write_json(
        result.get("source_search_execution_summary") or {},
        diagnostics_dir / "source_search_execution_summary.json",
    )
    write_json(
        result.get("source_search_results") or [],
        diagnostics_dir / "search_results_manifest.json",
    )
    write_json(
        result.get("source_discovery_summary") or {},
        diagnostics_dir / "source_discovery_summary.json",
    )
    write_json(
        result.get("source_credibility_summary") or {},
        diagnostics_dir / "source_credibility_summary.json",
    )
    write_json(
        result.get("source_credibility_assessments") or [],
        diagnostics_dir / "source_credibility_assessments.json",
    )
    write_json(result.get("raw_records") or [], diagnostics_dir / "raw_records.json")
    write_json(
        result.get("validated_records") or [],
        diagnostics_dir / "validated_records.json",
    )
    write_json(
        result.get("rejected_records") or [],
        diagnostics_dir / "rejected_records.json",
    )
    write_json(
        result.get("normalized_records") or [],
        diagnostics_dir / "normalized_records.json",
    )
    write_json(
        result.get("event_clusters") or [],
        diagnostics_dir / "event_clusters.json",
    )
    write_json(
        result.get("duplicate_clusters") or [],
        diagnostics_dir / "duplicate_clusters.json",
    )
    write_json(
        result.get("validation_cases") or [],
        diagnostics_dir / "validation_cases.json",
    )
    write_json(
        result.get("validation_comparisons") or [],
        diagnostics_dir / "validation_comparisons.json",
    )
    write_json(
        result.get("validation_results") or [],
        diagnostics_dir / "validation_results.json",
    )
    write_json(
        active_validation_records,
        diagnostics_dir / "active_validation_records.json",
    )
    write_json(
        inactive_validation_records,
        diagnostics_dir / "inactive_validation_records.json",
    )
    write_json(
        validation_source_compatibility_summary,
        diagnostics_dir / "validation_source_compatibility_summary.json",
    )
    write_json(
        result.get("validation_summary") or {},
        diagnostics_dir / "validation_summary.json",
    )
    write_json(
        result.get("trusted_source_validation_summary") or {},
        diagnostics_dir / "trusted_source_validation_summary.json",
    )
    write_json(
        result.get("cross_source_validation_summary") or {},
        diagnostics_dir / "cross_source_validation_summary.json",
    )
    write_json(result.get("conflicts") or [], diagnostics_dir / "conflicts.json")
    write_json(
        result.get("anomaly_results") or [],
        diagnostics_dir / "anomaly_results.json",
    )
    write_json(
        result.get("anomaly_summary") or {},
        diagnostics_dir / "anomaly_summary.json",
    )
    write_json(
        result.get("human_review_decisions") or [],
        diagnostics_dir / "human_review_decisions.json",
    )
    write_json(
        result.get("applied_human_review_decisions") or [],
        diagnostics_dir / "applied_human_review_decisions.json",
    )
    write_json(
        result.get("rejected_human_review_decisions") or [],
        diagnostics_dir / "rejected_human_review_decisions.json",
    )
    write_json(
        result.get("human_review_audit_trail") or [],
        diagnostics_dir / "human_review_audit_trail.json",
    )
    write_json(
        result.get("human_review_application_summary") or {},
        diagnostics_dir / "human_review_application_summary.json",
    )
    write_json(
        result.get("run_quality_summary") or package.get("run_quality_summary") or {},
        diagnostics_dir / "run_quality_summary.json",
    )
    write_json(
        result.get("final_dataset_quality_summary")
        or package.get("final_dataset_quality_summary")
        or {},
        diagnostics_dir / "final_dataset_quality_summary.json",
    )
    write_json(
        result.get("record_inclusion_decisions")
        or package.get("record_inclusion_decisions")
        or [],
        diagnostics_dir / "record_inclusion_decisions.json",
    )
    write_json(
        result.get("final_dataset_pre_quality_gate")
        or package.get("final_dataset_pre_quality_gate")
        or [],
        diagnostics_dir / "final_dataset_pre_quality_gate.json",
    )
    write_json(
        result.get("quarantined_records") or package.get("quarantined_records") or [],
        diagnostics_dir / "quarantined_records.json",
    )
    write_json(
        result.get("pending_review_records")
        or package.get("pending_review_records")
        or [],
        diagnostics_dir / "pending_review_records.json",
    )
    write_json(
        result.get("final_dataset_post_review") or [],
        diagnostics_dir / "final_dataset_post_review.json",
    )
    write_json(
        result.get("records_excluded_by_human_review") or [],
        diagnostics_dir / "records_excluded_by_human_review.json",
    )
    write_json(
        result.get("structured_extraction_summary") or {},
        diagnostics_dir / "structured_extraction_summary.json",
    )
    write_json(
        result.get("schema_validation_summary") or {},
        diagnostics_dir / "schema_validation_summary.json",
    )
    write_json(
        result.get("record_normalization_summary") or {},
        diagnostics_dir / "record_normalization_summary.json",
    )
    write_json(
        result.get("event_clustering_summary") or {},
        diagnostics_dir / "event_clustering_summary.json",
    )
    write_json(
        result.get("duplicate_detection_summary") or {},
        diagnostics_dir / "duplicate_detection_summary.json",
    )
    write_json(
        result.get("disease_relevance_summary") or {},
        diagnostics_dir / "disease_relevance_summary.json",
    )
    write_json(
        result.get("localized_source_planning_summary") or {},
        diagnostics_dir / "localized_source_planning_summary.json",
    )
    write_json(
        result.get("source_critic_summary") or {},
        diagnostics_dir / "source_critic_summary.json",
    )
    write_json(
        result.get("source_critic_results") or [],
        diagnostics_dir / "source_critic_results.json",
    )
    write_json(result.get("collection_trace") or [], diagnostics_dir / "collection_trace.json")
    write_json(
        {
            "task_intake_summary": result.get("task_intake_summary"),
            "disease_intelligence_summary": result.get(
                "disease_intelligence_summary"
            ),
            "profile_schema_summary": result.get("profile_schema_summary"),
            "executable_source_plan_summary": result.get(
                "executable_source_plan_summary"
            ),
            "localized_source_planning_summary": result.get(
                "localized_source_planning_summary"
            ),
            "source_planning_agent_summary": result.get("source_planning_agent_summary"),
            "source_search_execution_summary": result.get(
                "source_search_execution_summary"
            ),
            "source_discovery_summary": result.get("source_discovery_summary"),
            "source_registry_summary": result.get("source_registry_summary"),
            "source_screening_summary": result.get("source_screening_summary"),
            "source_critic_summary": result.get("source_critic_summary"),
            "source_routing_summary": result.get("source_routing_summary"),
            "source_credibility_summary": result.get("source_credibility_summary"),
            "content_fetch_summary": result.get("content_fetch_summary"),
            "document_parse_summary": result.get("document_parse_summary"),
            "fixture_document_summary": result.get("fixture_document_summary"),
            "document_quality_summary": result.get("document_quality_summary"),
            "evidence_chunking_summary": result.get("evidence_chunking_summary"),
            "data_presence_summary": result.get("data_presence_summary"),
            "structured_extraction_summary": result.get("structured_extraction_summary"),
            "llm_extraction_summary": result.get("llm_extraction_summary"),
            "schema_validation_summary": result.get("schema_validation_summary"),
            "record_normalization_summary": result.get("record_normalization_summary"),
            "record_linking_summary": result.get("record_linking_summary"),
            "event_clustering_summary": result.get("event_clustering_summary"),
            "duplicate_detection_summary": result.get("duplicate_detection_summary"),
            "validation_summary": result.get("validation_summary"),
            "validation_source_compatibility_summary": (
                validation_source_compatibility_summary
            ),
            "trusted_source_validation_summary": result.get(
                "trusted_source_validation_summary"
            ),
            "cross_source_validation_summary": result.get(
                "cross_source_validation_summary"
            ),
            "cross_source_consistency_summary": result.get(
                "cross_source_consistency_summary"
            ),
            "anomaly_summary": result.get("anomaly_summary"),
            "human_review_summary": result.get("human_review_summary"),
            "human_review_application_summary": result.get(
                "human_review_application_summary"
            ),
            "run_quality_summary": result.get("run_quality_summary")
            or package.get("run_quality_summary"),
            "final_dataset_quality_summary": result.get(
                "final_dataset_quality_summary"
            )
            or package.get("final_dataset_quality_summary"),
            "disease_relevance_summary": result.get("disease_relevance_summary"),
            "finalization_summary": result.get("finalization_summary"),
        },
        diagnostics_dir / "workflow_summaries.json",
    )

    report_path = output_dir / "workflow_run_report_chinese.md"
    report = _write_report(
        report_path,
        user_request=config.get("user_request") or "",
        provider=provider,
        model=model,
        output_dir=output_dir,
        result=result,
        collection_manifest=collection_manifest,
        validation_manifest=validation_manifest,
        evaluation_outputs=evaluation_outputs,
        evaluation_rows=evaluation_rows,
        evaluation_summary=evaluation_summary,
        source_split=source_split,
        live_summary=live_summary,
        llm_summary=llm_summary,
    )
    _TOP_LEVEL_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    if bool(output_config.get("write_latest_alias", True)):
        _TOP_LEVEL_REPORT_PATH.write_text(report, encoding="utf-8")

    run_quality_summary = result.get("run_quality_summary") or package.get(
        "run_quality_summary"
    ) or {}
    final_dataset_quality_summary = result.get(
        "final_dataset_quality_summary"
    ) or package.get("final_dataset_quality_summary") or {}
    final_dataset = list(package.get("final_dataset") or [])
    final_dataset_pre_quality_gate = list(
        package.get("final_dataset_pre_quality_gate") or []
    )
    quarantined_records = list(package.get("quarantined_records") or [])
    pending_review_records = list(package.get("pending_review_records") or [])
    final_dataset_post_review = list(result.get("final_dataset_post_review") or [])

    summary = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "user_request": config.get("user_request"),
        "output_dir": str(output_dir),
        "provider": provider,
        "model": model,
        "api_key_present": api_key_present(provider),
        "config_path": str(resolve_workflow_run_config_path(args.config)),
        "live_fetch_enabled": env_updates.get("HDC_ENABLE_LIVE_FETCH") == "true",
        "live_search_enabled": env_updates.get("HDC_ENABLE_LIVE_SEARCH") == "true",
        "source_search_mode": env_updates.get("HDC_SEARCH_MODE"),
        "source_search_provider": env_updates.get("HDC_SEARCH_PROVIDER"),
        "source_search_api_key_present": search_api_key_present(
            env_updates.get("HDC_SEARCH_PROVIDER") or ""
        ),
        "fixture_documents_enabled": False,
        "all_three_llm_stages_enabled": all(
            env_updates.get(key) == "true"
            for key in (
                "HDC_ENABLE_LLM_SOURCE_PLANNING",
                "HDC_ENABLE_LLM_SOURCE_CRITIC",
                "HDC_ENABLE_LLM_EXTRACTION",
            )
        ),
        "trace_node_count": len(result.get("collection_trace") or []),
        "current_route": result.get("current_route"),
        "source_registry_count": len(registry),
        "document_count": live_summary.get("document_count", 0),
        "normalized_record_count": len(result.get("normalized_records") or []),
        "evaluation_row_count": evaluation_summary.get("evaluation_row_count", 0),
        "validation_source_compatibility_status": (
            validation_source_compatibility_summary.get("compatibility_status")
        ),
        "active_validation_record_count": len(active_validation_records),
        "inactive_validation_record_count": len(inactive_validation_records),
        "raw_validation_record_count": len(validation_records),
        "validation_result_count": (result.get("validation_summary") or {}).get(
            "validation_result_count", 0
        ),
        "anomaly_result_count": len(result.get("anomaly_results") or []),
        "anomaly_severity_counts": (
            result.get("anomaly_summary") or {}
        ).get("severity_counts")
        or {},
        "human_review_item_count": len(result.get("human_review_queue") or []),
        "human_review_decisions_provided_count": (
            result.get("human_review_application_summary") or {}
        ).get("decisions_provided_count", 0),
        "human_review_decisions_applied_count": (
            result.get("human_review_application_summary") or {}
        ).get("decisions_applied_count", 0),
        "human_review_decisions_rejected_count": (
            result.get("human_review_application_summary") or {}
        ).get("decisions_rejected_count", 0),
        "human_review_audit_entry_count": len(
            result.get("human_review_audit_trail") or []
        ),
        "run_quality_status": run_quality_summary.get("run_quality_status"),
        "run_quality_summary": run_quality_summary,
        "final_dataset_quality_summary": final_dataset_quality_summary,
        "user_facing_run_status": user_facing_run_status(run_quality_summary),
        "recommended_user_message": run_quality_summary.get(
            "recommended_user_message"
        ),
        "accepted_record_count": len(final_dataset),
        "final_dataset_count": len(final_dataset),
        "pre_quality_record_count": len(final_dataset_pre_quality_gate),
        "final_dataset_pre_quality_gate_count": len(final_dataset_pre_quality_gate),
        "quarantined_record_count": len(quarantined_records),
        "pending_review_record_count": len(pending_review_records),
        "post_review_record_count": len(final_dataset_post_review),
        "final_dataset_post_review_count": len(final_dataset_post_review),
        "llm_stage_summary": llm_summary,
        "source_search_execution_summary": result.get(
            "source_search_execution_summary"
        )
        or {},
        "localized_source_planning_summary": result.get(
            "localized_source_planning_summary"
        )
        or {},
        "source_critic_summary": result.get("source_critic_summary") or {},
        "source_credibility_summary": result.get("source_credibility_summary") or {},
        "disease_relevance_summary": result.get("disease_relevance_summary") or {},
        "validation_source_compatibility_summary": (
            validation_source_compatibility_summary
        ),
        "artifact_paths": {
            "run_report": str(report_path),
            "stable_run_report": str(_TOP_LEVEL_REPORT_PATH)
            if bool(output_config.get("write_latest_alias", True))
            else None,
            "collection_manifest": collection_manifest,
            "validation_manifest": validation_manifest,
            "evaluation_outputs": evaluation_outputs,
            "source_split_summary": str(diagnostics_dir / "source_split_summary.json"),
            "llm_stage_summary": str(diagnostics_dir / "llm_stage_summary.json"),
            "source_search_execution_summary": str(
                diagnostics_dir / "source_search_execution_summary.json"
            ),
            "search_results_manifest": str(
                diagnostics_dir / "search_results_manifest.json"
            ),
            "source_discovery_summary": str(
                diagnostics_dir / "source_discovery_summary.json"
            ),
            "localized_source_planning_summary": str(
                diagnostics_dir / "localized_source_planning_summary.json"
            ),
            "source_critic_summary": str(
                diagnostics_dir / "source_critic_summary.json"
            ),
            "source_critic_results": str(
                diagnostics_dir / "source_critic_results.json"
            ),
            "source_credibility_summary": str(
                diagnostics_dir / "source_credibility_summary.json"
            ),
            "source_credibility_assessments": str(
                diagnostics_dir / "source_credibility_assessments.json"
            ),
            "content_fetch_summary": str(diagnostics_dir / "content_fetch_summary.json"),
            "document_quality_summary": str(
                diagnostics_dir / "document_quality_summary.json"
            ),
            "document_parse_summary": str(
                diagnostics_dir / "document_parse_summary.json"
            ),
            "fetch_manifest": str(diagnostics_dir / "fetch_manifest.json"),
            "validation_cases": str(diagnostics_dir / "validation_cases.json"),
            "validation_comparisons": str(
                diagnostics_dir / "validation_comparisons.json"
            ),
            "validation_results": str(diagnostics_dir / "validation_results.json"),
            "active_validation_records": str(
                diagnostics_dir / "active_validation_records.json"
            ),
            "inactive_validation_records": str(
                diagnostics_dir / "inactive_validation_records.json"
            ),
            "validation_source_compatibility_summary": str(
                diagnostics_dir / "validation_source_compatibility_summary.json"
            ),
            "validation_summary": str(diagnostics_dir / "validation_summary.json"),
            "trusted_source_validation_summary": str(
                diagnostics_dir / "trusted_source_validation_summary.json"
            ),
            "cross_source_validation_summary": str(
                diagnostics_dir / "cross_source_validation_summary.json"
            ),
            "conflicts": str(diagnostics_dir / "conflicts.json"),
            "anomaly_results": str(diagnostics_dir / "anomaly_results.json"),
            "anomaly_summary": str(diagnostics_dir / "anomaly_summary.json"),
            "human_review_decisions": str(
                diagnostics_dir / "human_review_decisions.json"
            ),
            "applied_human_review_decisions": str(
                diagnostics_dir / "applied_human_review_decisions.json"
            ),
            "rejected_human_review_decisions": str(
                diagnostics_dir / "rejected_human_review_decisions.json"
            ),
            "human_review_audit_trail": str(
                diagnostics_dir / "human_review_audit_trail.json"
            ),
            "human_review_application_summary": str(
                diagnostics_dir / "human_review_application_summary.json"
            ),
            "run_quality_summary": str(diagnostics_dir / "run_quality_summary.json"),
            "final_dataset_quality_summary": str(
                diagnostics_dir / "final_dataset_quality_summary.json"
            ),
            "record_inclusion_decisions": str(
                diagnostics_dir / "record_inclusion_decisions.json"
            ),
            "final_dataset_pre_quality_gate": str(
                diagnostics_dir / "final_dataset_pre_quality_gate.json"
            ),
            "quarantined_records": str(diagnostics_dir / "quarantined_records.json"),
            "pending_review_records": str(
                diagnostics_dir / "pending_review_records.json"
            ),
            "final_dataset_post_review": str(
                diagnostics_dir / "final_dataset_post_review.json"
            ),
            "records_excluded_by_human_review": str(
                diagnostics_dir / "records_excluded_by_human_review.json"
            ),
            "disease_relevance_summary": str(
                diagnostics_dir / "disease_relevance_summary.json"
            ),
        },
    }
    write_json(summary, output_dir / "workflow_run_summary.json")
    if bool(output_config.get("auto_build_console", True)):
        console_dir = workflow_console_output_dir_from_config(
            config,
            run_output_dir=output_dir,
        )
        console_summary = build_workflow_console(console_dir, output_dir)
        summary["artifact_paths"]["workflow_console_html"] = console_summary.get(
            "html_path"
        )
        summary["artifact_paths"]["workflow_console_summary_json"] = (
            console_summary.get("summary_path")
        )
        if bool(output_config.get("write_latest_alias", True)):
            latest_console_summary = build_workflow_console(
                _PROJECT_ROOT / "outputs" / "workflow_console",
                output_dir,
            )
            summary["artifact_paths"]["latest_workflow_console_html"] = (
                latest_console_summary.get("html_path")
            )
            summary["artifact_paths"]["latest_workflow_console_summary_json"] = (
                latest_console_summary.get("summary_path")
            )
        write_json(summary, output_dir / "workflow_run_summary.json")
    if bool(output_config.get("write_latest_alias", True)):
        write_json(summary, _TOP_LEVEL_SUMMARY_PATH)
    return summary


def _print_config(args: argparse.Namespace) -> None:
    config_path, config = _config_with_cli_overrides(args)
    provider, model = _config_provider_model(config)
    env_updates = workflow_run_env_from_config(config)
    print(f"config_path: {_console_text(config_path)}")
    print(f"provider: {provider}")
    print(f"model: {model}")
    print(f"api_key_present: {api_key_present(provider)}")
    print("sanitized_environment:")
    print(json.dumps(safe_env_for_display(env_updates), indent=2, sort_keys=True))
    print("studio_minimal_input:")
    print(
        json.dumps(
            workflow_initial_state_from_config(config, include_empty_fields=False),
            indent=2,
        )
    )


def main() -> int:
    args = _build_parser().parse_args()
    if args.timeout_seconds is not None and args.timeout_seconds <= 0:
        print("--timeout-seconds must be positive.", file=sys.stderr)
        return 2
    if args.llm_max_chunks is not None and args.llm_max_chunks <= 0:
        print("--llm-max-chunks must be positive.", file=sys.stderr)
        return 2
    try:
        _, config = _config_with_cli_overrides(args)
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    env_updates = workflow_run_env_from_config(config)
    provider, model = _config_provider_model(config)
    if args.print_config_only:
        _print_config(args)
        return 0

    if _llm_enabled(env_updates) and not model:
        print("Config llm.model or --model is required.", file=sys.stderr)
        return 3
    if _llm_enabled(env_updates) and not api_key_present(provider):
        print(
            f"Missing API key for provider '{provider}'.",
            file=sys.stderr,
        )
        return 4

    summary = run_workflow(args)
    llm = summary.get("llm_stage_summary") or {}
    print("=" * 72)
    print("HDC workflow run completed.")
    print(f"output_dir: {_console_text(summary.get('output_dir'))}")
    artifact_paths = summary.get("artifact_paths") or {}
    print(f"run_report: {_console_text(artifact_paths.get('run_report'))}")
    if artifact_paths.get("stable_run_report"):
        print(f"stable_report: {_console_text(artifact_paths.get('stable_run_report'))}")
    if artifact_paths.get("workflow_console_html"):
        print(
            "workflow_console:",
            _console_text(artifact_paths.get("workflow_console_html")),
        )
    print(f"provider: {summary.get('provider')}")
    print(f"model: {summary.get('model')}")
    print(f"trace_node_count: {summary.get('trace_node_count')}")
    print(f"current_route: {summary.get('current_route')}")
    print(f"document_count: {summary.get('document_count')}")
    source_search = summary.get("source_search_execution_summary") or {}
    print(f"source_search_mode: {summary.get('source_search_mode')}")
    print(f"source_search_provider: {summary.get('source_search_provider')}")
    print(
        "source_search_executed_query_count:",
        source_search.get("executed_query_count"),
    )
    print(
        "search_derived_candidate_count:",
        source_search.get("candidate_from_search_count"),
    )
    print(f"normalized_record_count: {summary.get('normalized_record_count')}")
    print(f"run_quality_status: {summary.get('run_quality_status')}")
    print(f"final_dataset_count: {summary.get('final_dataset_count')}")
    print(f"quarantined_record_count: {summary.get('quarantined_record_count')}")
    print(f"pending_review_record_count: {summary.get('pending_review_record_count')}")
    print(f"evaluation_row_count: {summary.get('evaluation_row_count')}")
    print(f"human_review_item_count: {summary.get('human_review_item_count')}")
    print(
        "llm_source_planning_status:",
        (llm.get("source_planning") or {}).get("status"),
    )
    print(
        "llm_source_critic_assessed_source_count:",
        (llm.get("source_critic") or {}).get("assessed_source_count"),
    )
    print(
        "source_credibility_assessed_source_count:",
        (llm.get("source_credibility") or {}).get("assessed_source_count"),
    )
    print(
        "llm_structured_extraction_call_count:",
        (llm.get("structured_extraction") or {}).get("call_count"),
    )
    print("=" * 72)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
