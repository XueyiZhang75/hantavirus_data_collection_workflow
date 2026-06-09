"""Acceptance artifact helpers for release-readiness checks."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


SEARCH_DERIVED_METHODS = {"fixture_search_result", "live_search_result"}

ACCEPTANCE_MATRIX_FIELDS = [
    "case_name",
    "command_used",
    "config_used",
    "output_session_directory",
    "live_search_enabled",
    "live_fetch_enabled",
    "llm_stages_enabled_disabled",
    "source_search_mode",
    "source_search_provider",
    "structured_task_disease",
    "structured_task_location",
    "structured_task_start_date",
    "structured_task_end_date",
    "disease_intelligence_standard_name",
    "profile_schema_generation_method",
    "planned_query_count",
    "source_candidate_count",
    "search_derived_candidate_count",
    "source_registry_count",
    "source_credibility_assessed_count",
    "selected_fetch_count",
    "document_count",
    "usable_partial_document_count",
    "evidence_chunk_count",
    "raw_record_count",
    "validated_record_count",
    "normalized_record_count",
    "disease_values_in_records",
    "event_cluster_count",
    "duplicate_cluster_count",
    "validation_result_count",
    "anomaly_result_count",
    "human_review_item_count",
    "applied_decision_count",
    "final_dataset_count",
    "final_dataset_post_review_count",
    "workflow_console_path",
    "key_diagnostics_paths",
    "acceptance_status",
    "notes",
]


def _load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _count(value: Any) -> int:
    if isinstance(value, list):
        return len(value)
    if isinstance(value, dict):
        return len(value)
    if isinstance(value, int):
        return value
    return 0


def _first_int(*values: Any) -> int:
    for value in values:
        if isinstance(value, bool):
            continue
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return int(value)
    return 0


def _bool_or_none(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    return None


def _path_if_exists(path: Path) -> str | None:
    return str(path) if path.exists() else None


def _workflow_console_path(session_dir: Path) -> str | None:
    path = session_dir / "workflow_console" / "hdc_workflow_console.html"
    return _path_if_exists(path)


def _quality_count(live_fetch_summary: dict[str, Any]) -> int:
    documents = _as_list(live_fetch_summary.get("documents"))
    if documents:
        return sum(1 for doc in documents if doc.get("quality_status") in {"usable", "partial"})
    counts = _as_dict(live_fetch_summary.get("quality_status_counts"))
    return _first_int(counts.get("usable"), 0) + _first_int(counts.get("partial"), 0)


def _disease_values(records: list[dict[str, Any]]) -> dict[str, int]:
    values = Counter()
    for record in records:
        disease = record.get("disease") or record.get("disease_standard_name") or "UNKNOWN"
        values[str(disease)] += 1
    return dict(sorted(values.items()))


def _llm_stage_flags(summary: dict[str, Any]) -> dict[str, bool]:
    llm = _as_dict(summary.get("llm_stage_summary"))
    if not llm:
        return {}
    result: dict[str, bool] = {}
    for name in ("source_planning", "source_critic", "source_credibility", "structured_extraction"):
        stage = _as_dict(llm.get(name))
        if "enabled" in stage:
            result[name] = bool(stage.get("enabled"))
    return result


def build_acceptance_matrix_row(case: dict[str, Any]) -> dict[str, Any]:
    """Build one Stage 13 acceptance row from a completed session directory."""

    session_dir = Path(case["session_dir"])
    summary = _as_dict(_load_json(session_dir / "workflow_run_summary.json", {}))
    final_package = _as_dict(_load_json(session_dir / "collection" / "final_package.json", {}))
    workflow_summaries = _as_dict(
        _load_json(session_dir / "diagnostics" / "workflow_summaries.json", {})
    ) or _as_dict(final_package.get("workflow_summaries"))
    live_fetch_summary = _as_dict(
        _load_json(session_dir / "diagnostics" / "live_fetch_summary.json", {})
    )
    normalized_records = [
        row
        for row in _as_list(
            _load_json(
                session_dir / "diagnostics" / "normalized_records.json",
                final_package.get("final_dataset") or [],
            )
        )
        if isinstance(row, dict)
    ]
    raw_records = _as_list(_load_json(session_dir / "diagnostics" / "raw_records.json", []))
    validated_records = _as_list(
        _load_json(session_dir / "diagnostics" / "validated_records.json", [])
    )
    event_clusters = _as_list(_load_json(session_dir / "diagnostics" / "event_clusters.json", []))
    duplicate_clusters = _as_list(
        _load_json(session_dir / "diagnostics" / "duplicate_clusters.json", [])
    )
    validation_results = _as_list(
        _load_json(session_dir / "diagnostics" / "validation_results.json", [])
    )
    anomaly_results = _as_list(_load_json(session_dir / "diagnostics" / "anomaly_results.json", []))
    source_registry = _as_list(final_package.get("source_registry"))
    final_dataset = _as_list(final_package.get("final_dataset"))
    final_dataset_post_review = _as_list(final_package.get("final_dataset_post_review"))

    task = _as_dict(workflow_summaries.get("task_intake_summary"))
    disease_intelligence = _as_dict(workflow_summaries.get("disease_intelligence_summary"))
    profile_schema = _as_dict(workflow_summaries.get("profile_schema_summary"))
    executable_plan = _as_dict(workflow_summaries.get("executable_source_plan_summary"))
    source_search = _as_dict(workflow_summaries.get("source_search_execution_summary")) or _as_dict(
        summary.get("source_search_execution_summary")
    )
    source_credibility = _as_dict(workflow_summaries.get("source_credibility_summary"))
    content_fetch = _as_dict(workflow_summaries.get("content_fetch_summary"))
    evidence_summary = _as_dict(workflow_summaries.get("evidence_chunking_summary")) or _as_dict(
        workflow_summaries.get("evidence_chunk_summary")
    )
    validation_summary = _as_dict(workflow_summaries.get("validation_summary"))
    anomaly_summary = _as_dict(workflow_summaries.get("anomaly_summary"))
    human_review_application = _as_dict(
        workflow_summaries.get("human_review_application_summary")
    ) or _as_dict(
        _load_json(session_dir / "diagnostics" / "human_review_application_summary.json", {})
    )
    event_summary = _as_dict(workflow_summaries.get("event_clustering_summary"))
    duplicate_summary = _as_dict(workflow_summaries.get("duplicate_detection_summary"))

    search_derived_registry_count = sum(
        1
        for source in source_registry
        if isinstance(source, dict) and source.get("discovery_method") in SEARCH_DERIVED_METHODS
    )
    key_diagnostics_paths = {
        "workflow_run_summary": _path_if_exists(session_dir / "workflow_run_summary.json"),
        "workflow_summaries": _path_if_exists(session_dir / "diagnostics" / "workflow_summaries.json"),
        "live_fetch_summary": _path_if_exists(session_dir / "diagnostics" / "live_fetch_summary.json"),
        "source_search_execution_summary": _path_if_exists(
            session_dir / "diagnostics" / "source_search_execution_summary.json"
        ),
        "source_credibility_summary": _path_if_exists(
            session_dir / "diagnostics" / "source_credibility_summary.json"
        ),
        "validation_results": _path_if_exists(session_dir / "diagnostics" / "validation_results.json"),
        "anomaly_results": _path_if_exists(session_dir / "diagnostics" / "anomaly_results.json"),
        "human_review_application_summary": _path_if_exists(
            session_dir / "diagnostics" / "human_review_application_summary.json"
        ),
    }

    return {
        "case_name": case.get("case_name"),
        "command_used": case.get("command_used"),
        "config_used": case.get("config_used"),
        "output_session_directory": str(session_dir),
        "live_search_enabled": _bool_or_none(summary.get("live_search_enabled"))
        if "live_search_enabled" in summary
        else _bool_or_none(source_search.get("live_search_enabled")),
        "live_fetch_enabled": _bool_or_none(summary.get("live_fetch_enabled"))
        if "live_fetch_enabled" in summary
        else _bool_or_none(live_fetch_summary.get("live_fetch_enabled")),
        "llm_stages_enabled_disabled": _llm_stage_flags(summary),
        "source_search_mode": summary.get("source_search_mode") or source_search.get("search_mode"),
        "source_search_provider": summary.get("source_search_provider")
        or source_search.get("search_provider"),
        "structured_task_disease": task.get("disease"),
        "structured_task_location": task.get("location"),
        "structured_task_start_date": task.get("start_date"),
        "structured_task_end_date": task.get("end_date"),
        "disease_intelligence_standard_name": disease_intelligence.get("disease_standard_name"),
        "profile_schema_generation_method": profile_schema.get("schema_generation_method")
        or profile_schema.get("profile_generation_method"),
        "planned_query_count": _first_int(
            executable_plan.get("planned_query_count"),
            source_search.get("planned_query_count"),
        ),
        "source_candidate_count": _first_int(
            source_search.get("total_candidate_count"),
            source_search.get("source_candidate_count"),
            len(source_registry),
        ),
        "search_derived_candidate_count": _first_int(
            source_search.get("candidate_from_search_count"),
            search_derived_registry_count,
        ),
        "source_registry_count": len(source_registry),
        "source_credibility_assessed_count": _first_int(
            source_credibility.get("assessed_source_count"),
            source_credibility.get("input_source_count"),
        ),
        "selected_fetch_count": _first_int(
            content_fetch.get("fetch_request_count"),
            content_fetch.get("selected_fetch_request_count"),
            content_fetch.get("selected_search_derived_fetch_count"),
            summary.get("document_count"),
        ),
        "document_count": _first_int(summary.get("document_count"), _count(live_fetch_summary.get("documents"))),
        "usable_partial_document_count": _quality_count(live_fetch_summary),
        "evidence_chunk_count": _first_int(
            evidence_summary.get("total_chunk_count"),
            evidence_summary.get("evidence_chunk_count"),
            evidence_summary.get("target_chunk_count"),
            summary.get("evidence_chunk_count"),
            _count(_load_json(session_dir / "diagnostics" / "evidence_chunks.json", [])),
        ),
        "raw_record_count": _first_int(summary.get("raw_record_count"), len(raw_records)),
        "validated_record_count": _first_int(summary.get("validated_record_count"), len(validated_records)),
        "normalized_record_count": _first_int(summary.get("normalized_record_count"), len(normalized_records)),
        "disease_values_in_records": _disease_values(normalized_records or final_dataset),
        "event_cluster_count": _first_int(event_summary.get("event_cluster_count"), len(event_clusters)),
        "duplicate_cluster_count": _first_int(
            duplicate_summary.get("duplicate_cluster_count"), len(duplicate_clusters)
        ),
        "validation_result_count": _first_int(
            summary.get("validation_result_count"),
            validation_summary.get("validation_result_count"),
            len(validation_results),
        ),
        "anomaly_result_count": _first_int(
            summary.get("anomaly_result_count"),
            anomaly_summary.get("anomaly_result_count"),
            len(anomaly_results),
        ),
        "human_review_item_count": _first_int(
            summary.get("human_review_item_count"),
            len(_as_list(final_package.get("human_review_queue"))),
        ),
        "applied_decision_count": _first_int(
            summary.get("human_review_decisions_applied_count"),
            human_review_application.get("decisions_applied_count"),
        ),
        "final_dataset_count": len(final_dataset),
        "final_dataset_post_review_count": _first_int(
            summary.get("final_dataset_post_review_count"),
            len(final_dataset_post_review),
        ),
        "workflow_console_path": _workflow_console_path(session_dir),
        "key_diagnostics_paths": key_diagnostics_paths,
        "acceptance_status": case.get("acceptance_status") or "PENDING",
        "notes": case.get("notes") or "",
    }


def build_acceptance_matrix(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [build_acceptance_matrix_row(case) for case in cases]


def _csv_value(value: Any) -> str:
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    if value is None:
        return ""
    return str(value)


def write_acceptance_matrix(
    rows: list[dict[str, Any]], *, json_path: Path, csv_path: Path
) -> dict[str, Any]:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")

    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=ACCEPTANCE_MATRIX_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: _csv_value(row.get(field)) for field in ACCEPTANCE_MATRIX_FIELDS})

    return {
        "row_count": len(rows),
        "json_path": str(json_path),
        "csv_path": str(csv_path),
    }
