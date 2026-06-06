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

from hdc_workflow.evaluation_report_builder import (  # noqa: E402
    build_evaluation_report,
    read_csv_records,
    write_csv_records,
    write_evaluation_outputs,
)
from hdc_workflow.export import export_final_data_package, write_json  # noqa: E402
from hdc_workflow.graph import build_graph  # noqa: E402
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
    workflow_initial_state_from_config,
    workflow_output_dir_from_config,
    workflow_run_config_with_overrides,
    workflow_run_env_from_config,
)

_TOP_LEVEL_REPORT_PATH = (
    _PROJECT_ROOT / "outputs" / "demo_package" / "stage4h_live_product_run_report_chinese.md"
)
_TOP_LEVEL_SUMMARY_PATH = (
    _PROJECT_ROOT / "outputs" / "demo_package" / "stage4h_live_product_run_summary.json"
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
        "--allow-live-fetch",
        action="store_true",
        help=(
            "Confirm that this run may use live HTTP fetch. This also keeps "
            "backward compatibility by enabling live fetch for this run."
        ),
    )
    parser.add_argument(
        "--disable-live-fetch",
        action="store_true",
        help="Override config and disable live HTTP fetch for this run.",
    )
    parser.add_argument(
        "--allow-llm",
        action="store_true",
        help=(
            "Confirm that this run may call the configured LLM. This also keeps "
            "backward compatibility by enabling all three LLM stages for this run."
        ),
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
        live_fetch=_override_value(args.allow_live_fetch, args.disable_live_fetch),
        all_llm=_override_value(args.allow_llm, args.disable_all_llm),
        provider=args.provider,
        model=args.model,
        timeout_seconds=args.timeout_seconds,
        llm_max_chunks=args.llm_max_chunks,
        output_dir=args.output_dir,
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
                "fetch_status": doc.get("fetch_status"),
                "http_status_code": doc.get("http_status_code"),
                "quality_status": doc.get("quality_status"),
                "parse_status": doc.get("parse_status"),
                "clean_text_char_count": len(doc.get("clean_text") or ""),
                "is_live_fetched": bool(doc.get("is_live_fetched")),
            }
        )
    return {
        "live_fetch_enabled": True,
        "document_count": len(documents),
        "document_source_ids": sorted({row["source_id"] for row in rows if row["source_id"]}),
        "fetch_status_counts": fetch_summary.get("fetch_status_counts") or {},
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
    planning = result.get("source_planning_agent_summary") or {}
    critic = result.get("source_critic_summary") or {}
    extraction = result.get("structured_extraction_summary") or {}
    llm_extraction = result.get("llm_extraction_summary") or {}
    return {
        "provider": provider,
        "model": model,
        "api_key_present": api_key_present(provider),
        "source_planning": {
            "enabled": bool(planning.get("llm_source_planning_enabled")),
            "status": planning.get("status"),
            "agent_query_count": planning.get("agent_query_count", 0),
            "agent_query_added_count": planning.get("agent_query_added_count", 0),
            "candidate_hint_count": planning.get("agent_candidate_hint_count", 0),
            "warnings": planning.get("warnings") or [],
            "failure_type": planning.get("failure_type"),
            "failure_message": planning.get("failure_message"),
        },
        "source_critic": {
            "enabled": bool(critic.get("llm_source_critic_enabled")),
            "attempted_source_count": critic.get(
                "llm_source_critic_attempted_source_count", 0
            ),
            "assessed_source_count": critic.get("llm_assessed_source_count", 0),
            "skipped_source_count": critic.get("llm_skipped_source_count", 0),
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
) -> dict:
    validation_dir = output_dir / "validation"
    write_csv_records(validation_dir / "ground_truth_records.csv", validation_records)
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
    }


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
    route = result.get("current_route")

    node_lines = [
        f"{idx}. `{event.get('node_name')}` - {_preview(event.get('message'), 120)}"
        for idx, event in enumerate(trace, 1)
    ]
    if not node_lines:
        node_lines = ["- no trace events"]

    lines = [
        "# Live Product Run Report - New Mexico HPS",
        "",
        "## 1. 输入任务",
        "",
        user_request,
        "",
        "## 2. 本次运行模式",
        "",
        f"- Live webpage fetch: `true`",
        f"- Fixture documents: `false`",
        f"- Provider: `{provider}`",
        f"- Model: `{model}`",
        f"- API key present: `{api_key_present(provider)}`",
        f"- LLM source planning: `{llm_summary['source_planning']['enabled']}`",
        f"- LLM source critic: `{llm_summary['source_critic']['enabled']}`",
        f"- LLM structured extraction: `{llm_summary['structured_extraction']['enabled']}`",
        f"- Final route: `{route}`",
        "",
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
        "| Role | Source ID | Publisher / title | Final decision | Fetch ready |",
        "|---|---|---|---|---|",
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
            f"- Fetch status counts: `{_format_counts(live_summary.get('fetch_status_counts'))}`",
            f"- Quality status counts: `{_format_counts(live_summary.get('quality_status_counts'))}`",
            f"- Validation-reserved skipped from fetch: `{live_summary.get('skipped_validation_reserved_source_ids')}`",
            "",
            "| Source ID | Fetch status | HTTP | Quality | Text chars |",
            "|---|---|---|---|---|",
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
                    _cell(row.get("quality_status")),
                    _cell(row.get("clean_text_char_count")),
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
            f"- Agent query count: `{llm_summary['source_planning'].get('agent_query_count')}`",
            f"- Agent query added count: `{llm_summary['source_planning'].get('agent_query_added_count')}`",
            f"- Candidate hint count: `{llm_summary['source_planning'].get('candidate_hint_count')}`",
            "",
            "### 6.2 LLM Source Critic",
            "",
            f"- Attempted source count: `{llm_summary['source_critic'].get('attempted_source_count')}`",
            f"- Assessed source count: `{llm_summary['source_critic'].get('assessed_source_count')}`",
            f"- Skipped source count: `{llm_summary['source_critic'].get('skipped_source_count')}`",
            f"- Max sources: `{llm_summary['source_critic'].get('max_sources')}`",
            f"- Review blocks fetch: `{llm_summary['source_critic'].get('review_blocks_fetch')}`",
            f"- Failure count: `{llm_summary['source_critic'].get('failure_count')}`",
            f"- Semantic leakage count: `{llm_summary['source_critic'].get('semantic_leakage_count')}`",
            f"- Human review recommended count: `{llm_summary['source_critic'].get('human_review_recommended_count')}`",
            "",
            "### 6.3 LLM Structured Extraction",
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
            f"- Source counts: `{_format_counts(_count_by(records, 'source_id'))}`",
            "",
            "| Record ID | Date / period | Location | Cases | Deaths | Source | LLM used |",
            "|---|---|---|---|---|---|---|",
        ]
    )
    for record in records[:12]:
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

    lines.extend(
        [
            "",
            "## 10. 输出文件",
            "",
            f"- Run output directory: `{output_dir}`",
            f"- Collection final dataset: `{collection_manifest['files'].get('final_dataset_csv')}`",
            f"- Collection source registry: `{collection_manifest['files'].get('source_registry_json')}`",
            f"- Validation ground truth: `{validation_manifest.get('ground_truth_records_csv')}`",
            f"- Evaluation report CSV: `{evaluation_outputs.get('evaluation_report_csv')}`",
            f"- Human-readable report: `{path}`",
            "",
            "## 11. 当前结论",
            "",
            (
                "This run demonstrates the product workflow end to end: a user "
                "request enters the LangGraph state, the graph fetches controlled "
                "real web sources, calls all three LLM stages, separates collection "
                "and validation sources, extracts structured records, compares "
                "against held-out validation evidence, and flags unresolved "
                "validation rows for human review."
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


def run_product(args: argparse.Namespace) -> dict:
    _, config = _config_with_cli_overrides(args)
    provider, model = _config_provider_model(config)
    output_dir = workflow_output_dir_from_config(config)
    env_updates = workflow_run_env_from_config(config)

    with temporary_workflow_env(env_updates):
        result = build_graph().invoke(workflow_initial_state_from_config(config))

    package = result.get("final_data_package") or {}
    collection_manifest = export_final_data_package(package, output_dir / "collection")
    validation_records = read_csv_records(validation_records_path_from_config(config))
    registry = list(result.get("source_registry") or package.get("source_registry") or [])
    validation_manifest = _write_validation_outputs(
        output_dir, validation_records, registry
    )
    evaluation_rows, evaluation_summary = build_evaluation_report(
        collection_records=package.get("final_dataset") or [],
        validation_records=validation_records,
        collection_source_registry=package.get("source_registry") or [],
        reserved_source_ids=set(VALIDATION_SOURCE_IDS),
        conflicts=package.get("conflicts") or [],
        human_review_items=package.get("human_review_items") or [],
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
    write_json(llm_summary, diagnostics_dir / "llm_stage_summary.json")
    write_json(result.get("collection_trace") or [], diagnostics_dir / "collection_trace.json")
    write_json(
        {
            "source_planning_agent_summary": result.get("source_planning_agent_summary"),
            "source_critic_summary": result.get("source_critic_summary"),
            "structured_extraction_summary": result.get("structured_extraction_summary"),
            "llm_extraction_summary": result.get("llm_extraction_summary"),
            "schema_validation_summary": result.get("schema_validation_summary"),
            "record_normalization_summary": result.get("record_normalization_summary"),
            "record_linking_summary": result.get("record_linking_summary"),
            "cross_source_consistency_summary": result.get(
                "cross_source_consistency_summary"
            ),
            "human_review_summary": result.get("human_review_summary"),
            "finalization_summary": result.get("finalization_summary"),
        },
        diagnostics_dir / "workflow_summaries.json",
    )

    report_path = output_dir / "stage4h_live_product_run_report_chinese.md"
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
    _TOP_LEVEL_REPORT_PATH.write_text(report, encoding="utf-8")

    summary = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "user_request": config.get("user_request"),
        "output_dir": str(output_dir),
        "provider": provider,
        "model": model,
        "api_key_present": api_key_present(provider),
        "config_path": str(resolve_workflow_run_config_path(args.config)),
        "live_fetch_enabled": env_updates.get("HDC_ENABLE_LIVE_FETCH") == "true",
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
        "human_review_item_count": len(result.get("human_review_queue") or []),
        "llm_stage_summary": llm_summary,
        "artifact_paths": {
            "run_report": str(report_path),
            "stable_run_report": str(_TOP_LEVEL_REPORT_PATH),
            "collection_manifest": collection_manifest,
            "validation_manifest": validation_manifest,
            "evaluation_outputs": evaluation_outputs,
            "source_split_summary": str(diagnostics_dir / "source_split_summary.json"),
            "llm_stage_summary": str(diagnostics_dir / "llm_stage_summary.json"),
        },
    }
    write_json(summary, output_dir / "stage4h_live_product_run_summary.json")
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

    if env_updates.get("HDC_ENABLE_LIVE_FETCH") == "true" and not args.allow_live_fetch:
        print(
            "Config enables live fetch. Pass --allow-live-fetch to run the "
            "controlled live product workflow.",
            file=sys.stderr,
        )
        return 2
    if _llm_enabled(env_updates) and not args.allow_llm:
        print(
            "Config enables one or more LLM stages. Pass --allow-llm to call "
            "the configured model.",
            file=sys.stderr,
        )
        return 2
    if _llm_enabled(env_updates) and not model:
        print("Config llm.model or --model is required.", file=sys.stderr)
        return 3
    if _llm_enabled(env_updates) and not api_key_present(provider):
        print(
            f"Missing API key for provider '{provider}'.",
            file=sys.stderr,
        )
        return 4

    summary = run_product(args)
    llm = summary.get("llm_stage_summary") or {}
    print("=" * 72)
    print("Stage 4H live product LLM run completed.")
    print(f"output_dir: {_console_text(summary.get('output_dir'))}")
    print(f"stable_report: {_console_text(_TOP_LEVEL_REPORT_PATH)}")
    print(f"provider: {summary.get('provider')}")
    print(f"model: {summary.get('model')}")
    print(f"trace_node_count: {summary.get('trace_node_count')}")
    print(f"current_route: {summary.get('current_route')}")
    print(f"document_count: {summary.get('document_count')}")
    print(f"normalized_record_count: {summary.get('normalized_record_count')}")
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
        "llm_structured_extraction_call_count:",
        (llm.get("structured_extraction") or {}).get("call_count"),
    )
    print("=" * 72)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
