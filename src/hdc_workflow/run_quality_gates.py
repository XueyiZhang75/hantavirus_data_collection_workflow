"""Deterministic final dataset quality gates.

This module evaluates records that have already passed through extraction,
schema validation, normalization, linking, validation, anomaly detection, and
human review application. It does not search, fetch, call an LLM, or alter graph
topology.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from typing import Any

from .disease_relevance import (
    INCOMPATIBLE_DISEASE,
    UNRELATED_DISEASE,
    assess_record_disease_compatibility,
    build_disease_relevance_context,
)

QUALITY_GATE_METHOD = "deterministic_run_quality_gate_v1"

ACCEPTED_STATUSES = {
    "accepted",
    "accepted_with_warnings",
    "accepted_after_human_review",
    "corrected_after_human_review",
}

VALIDATION_LIMITED_STATUSES = {
    "no_task_compatible_validation_source",
    "incompatible_validation_source_disabled",
    "validation_limited_no_compatible_source",
    "no_compatible_validation_source",
}

_SOURCE_BLOCK_STATUSES = {"excluded", "blocked", "not_task_relevant"}
_SOURCE_EXCLUDED_ROLES = {"excluded", "search_endpoint"}
_SOURCE_UNRELATED_STATUSES = {UNRELATED_DISEASE, INCOMPATIBLE_DISEASE}
_DOCUMENT_BLOCK_STATUSES = {UNRELATED_DISEASE, INCOMPATIBLE_DISEASE}
_DOCUMENT_BLOCK_QUALITIES = {"not_task_relevant"}
_CHUNK_BLOCK_STATUSES = {UNRELATED_DISEASE, INCOMPATIBLE_DISEASE}
_SCHEMA_BLOCK_STATUSES = {"invalid", "rejected"}
_ANOMALY_BLOCK_SEVERITIES = {"high", "critical"}
_OUTSIDE_SCOPE_TOKENS = {
    "outside_scope",
    "outside_requested_scope",
    "outside_geography",
    "outside_time_window",
    "disease_mismatch",
}


def _as_list(value: Any) -> list:
    if isinstance(value, list):
        return value
    return []


def _as_dict(value: Any) -> dict:
    return value if isinstance(value, dict) else {}


def _lower(value: Any) -> str:
    return str(value or "").strip().lower()


def _record_id(record: dict) -> str:
    return str(record.get("record_id") or "")


def _source_id(record: dict) -> str:
    return str(record.get("source_id") or "")


def _supporting_chunk_id(record: dict) -> str:
    return str(record.get("supporting_chunk_id") or "")


def _source_url(record: dict) -> str | None:
    value = record.get("source_url")
    return str(value) if value else None


def _reason_text(*values: Any) -> str:
    return " ".join(str(value or "") for value in values).lower()


def _index_by_id(rows: list[dict], field: str) -> dict[str, dict]:
    return {
        str(row.get(field)): row
        for row in rows
        if isinstance(row, dict) and row.get(field)
    }


def _documents_by_source(rows: list[dict]) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        sid = row.get("source_id")
        if sid:
            out.setdefault(str(sid), []).append(row)
    return out


def _chunks_by_source(rows: list[dict]) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        sid = row.get("source_id")
        if sid:
            out.setdefault(str(sid), []).append(row)
    return out


def _validation_results_by_record(rows: list[dict]) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        ids = set()
        ids.update(str(v) for v in _as_list(row.get("left_record_ids")) if v)
        ids.update(str(v) for v in _as_list(row.get("right_record_ids")) if v)
        if row.get("record_id"):
            ids.add(str(row.get("record_id")))
        for rid in ids:
            out.setdefault(rid, []).append(row)
    return out


def _anomalies_by_record(rows: list[dict]) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        rid = row.get("record_id")
        if rid:
            out.setdefault(str(rid), []).append(row)
    return out


def _review_items_by_record(rows: list[dict]) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        ids = set(str(v) for v in _as_list(row.get("related_ids")) if v)
        if row.get("record_id"):
            ids.add(str(row.get("record_id")))
        for rid in ids:
            out.setdefault(rid, []).append(row)
    return out


def _human_review_rejected_record_ids(state: dict) -> set[str]:
    rejected: set[str] = set()
    for row in _as_list(state.get("records_excluded_by_human_review")):
        if isinstance(row, dict) and row.get("record_id"):
            rejected.add(str(row["record_id"]))
    for decision in _as_list(state.get("applied_human_review_decisions")):
        if not isinstance(decision, dict):
            continue
        if decision.get("decision_type") != "reject_record":
            continue
        rejected.update(str(v) for v in _as_list(decision.get("target_ids")) if v)
    for decision in _as_list(state.get("human_review_decisions")):
        if not isinstance(decision, dict):
            continue
        if decision.get("decision_type") != "reject_record":
            continue
        if decision.get("apply_decision") is False:
            continue
        rejected.update(str(v) for v in _as_list(decision.get("target_ids")) if v)
    return rejected


def _has_explicit_human_review_decisions(state: dict) -> bool:
    return bool(
        _as_list(state.get("applied_human_review_decisions"))
        or _as_list(state.get("rejected_human_review_decisions"))
        or _as_list(state.get("human_review_decisions"))
        or _as_list(state.get("records_excluded_by_human_review"))
    )


def _add_block(
    blocks: list[tuple[str, str, str]],
    status: str,
    flag: str,
    reason: str,
) -> None:
    blocks.append((status, flag, reason))


def _add_warning(warnings: list[str], warning: str) -> None:
    if warning and warning not in warnings:
        warnings.append(warning)


def _first_block(blocks: list[tuple[str, str, str]]) -> tuple[str, str, str] | None:
    if not blocks:
        return None
    priority = {
        "excluded_by_human_review": 0,
        "quarantined_disease_mismatch": 1,
        "quarantined_source_not_task_relevant": 2,
        "quarantined_document_not_task_relevant": 3,
        "quarantined_chunk_not_task_relevant": 4,
        "quarantined_schema_invalid": 5,
        "quarantined_normalization_rejected": 6,
        "quarantined_outside_scope": 7,
        "quarantined_validation_conflict": 8,
        "quarantined_critical_anomaly": 9,
    }
    return sorted(blocks, key=lambda item: priority.get(item[0], 100))[0]


def _task_metadata(state: dict) -> dict:
    structured_task = _as_dict(state.get("structured_task"))
    collection_spec = _as_dict(state.get("collection_spec"))
    return {
        "task_disease": structured_task.get("disease") or collection_spec.get("disease"),
        "task_location": structured_task.get("location")
        or collection_spec.get("geography")
        or collection_spec.get("location"),
        "task_start_date": structured_task.get("start_date")
        or collection_spec.get("start_date"),
        "task_end_date": structured_task.get("end_date") or collection_spec.get("end_date"),
    }


def _validation_limited(state: dict) -> tuple[bool, bool, list[str]]:
    summary = _as_dict(state.get("validation_source_compatibility_summary"))
    status = _lower(summary.get("compatibility_status") or summary.get("status"))
    warnings = [str(w) for w in _as_list(summary.get("warnings"))]
    limited = status in VALIDATION_LIMITED_STATUSES or any(
        _lower(w) in VALIDATION_LIMITED_STATUSES for w in warnings
    )
    if limited:
        if "no_task_compatible_validation_source" not in warnings:
            warnings.append("no_task_compatible_validation_source")
    return limited, limited, warnings


def _document_candidates(
    record: dict,
    docs_by_id: dict[str, dict],
    docs_by_source: dict[str, list[dict]],
) -> list[dict]:
    doc_id = record.get("document_id")
    if doc_id and str(doc_id) in docs_by_id:
        return [docs_by_id[str(doc_id)]]
    return list(docs_by_source.get(_source_id(record), []))


def _chunk_candidates(
    record: dict,
    chunks_by_id: dict[str, dict],
    chunks_by_source: dict[str, list[dict]],
) -> list[dict]:
    chunk_id = _supporting_chunk_id(record)
    if chunk_id and chunk_id in chunks_by_id:
        return [chunks_by_id[chunk_id]]
    return list(chunks_by_source.get(_source_id(record), []))


def _source_is_blocking(source: dict | None) -> tuple[str, str] | None:
    if not source:
        return None
    if source.get("blocked_from_fetch") or source.get("llm_source_critic_block_fetch"):
        return (
            "source_critic_blocked_from_fetch",
            source.get("blocked_from_fetch_reason")
            or source.get("llm_source_critic_reason")
            or "source critic blocked fetch",
        )
    role = _lower(source.get("source_role_final"))
    if role in _SOURCE_EXCLUDED_ROLES:
        return ("source_role_final_excluded", f"source_role_final={role}")
    status = _lower(source.get("status"))
    if status in _SOURCE_BLOCK_STATUSES:
        return ("source_status_excluded", f"source status={status}")
    for field in (
        "screening_decision",
        "critic_decision",
        "final_screening_decision",
        "llm_source_critic_decision",
        "llm_source_critic_fetch_recommendation",
    ):
        value = _lower(source.get(field))
        if value in {"exclude", "excluded", "not_task_relevant", "block_fetch"}:
            return (f"{field}_blocked", f"{field}={value}")
    if source.get("source_excluded_by_human_review"):
        return ("source_excluded_by_human_review", "source excluded by human review")
    if _lower(source.get("source_disease_relevance_status")) in _SOURCE_UNRELATED_STATUSES:
        return (
            "source_disease_relevance_status_unrelated",
            "source disease relevance is not task relevant",
        )
    return None


def _document_block(documents: list[dict]) -> tuple[str, str] | None:
    for doc in documents:
        status = _lower(doc.get("document_disease_relevance_status"))
        quality = _lower(doc.get("quality_status"))
        if status in _DOCUMENT_BLOCK_STATUSES:
            return (
                "document_disease_relevance_status_unrelated",
                "document is not task relevant",
            )
        if doc.get("not_extractable_for_task_disease") is True:
            return (
                "not_extractable_for_task_disease",
                "document is not extractable for the task disease",
            )
        if quality in _DOCUMENT_BLOCK_QUALITIES:
            return ("document_quality_not_task_relevant", "document is not task relevant")
    return None


def _chunk_block(chunks: list[dict]) -> tuple[str, str] | None:
    for chunk in chunks:
        status = _lower(chunk.get("disease_relevance_status"))
        if status in _CHUNK_BLOCK_STATUSES:
            return (
                "chunk_disease_relevance_status_unrelated",
                "evidence chunk is not task relevant",
            )
        if chunk.get("extraction_eligible_for_task_disease") is False:
            return (
                "chunk_not_extractable_for_task_disease",
                "evidence chunk is not extractable for the task disease",
            )
        if chunk.get("contains_target_data") is False:
            return ("chunk_contains_target_data_false", "evidence chunk is not task relevant")
    return None


def _validation_block(rows: list[dict]) -> tuple[str, str, str] | None:
    for row in rows:
        text = _reason_text(
            row.get("validation_status"),
            row.get("match_status"),
            row.get("comparability_status"),
            row.get("reason"),
            " ".join(str(w) for w in _as_list(row.get("warnings"))),
        )
        if any(token in text for token in _OUTSIDE_SCOPE_TOKENS):
            return (
                "quarantined_outside_scope",
                "validation_outside_scope",
                row.get("reason") or "validation marked record outside requested scope",
            )
        validation_type = _lower(row.get("validation_type"))
        trusted_conflict = validation_type in {
            "trusted_source_comparison",
            "held_out_source_comparison",
            "aggregate_comparison",
        }
        if trusted_conflict and (
            _lower(row.get("validation_status")) == "conflict"
            or _lower(row.get("match_status")) == "conflict"
        ):
            return (
                "quarantined_validation_conflict",
                "validation_conflict",
                row.get("reason") or "validation result is a conflict",
            )
    return None


def _anomaly_block(rows: list[dict]) -> tuple[str, str] | None:
    for row in rows:
        if _lower(row.get("anomaly_status")) in {"resolved", "dismissed"}:
            continue
        severity = _lower(row.get("severity"))
        anomaly_type = str(row.get("anomaly_type") or "high_or_critical_anomaly")
        if severity in _ANOMALY_BLOCK_SEVERITIES:
            return (
                anomaly_type,
                row.get("reason") or f"{severity} anomaly requires blocking review",
            )
    return None


def _pending_review_block(record: dict, review_items: list[dict]) -> tuple[str, str] | None:
    if record.get("requires_human_review"):
        return ("requires_human_review", record.get("human_review_reason") or "record requires human review")
    if record.get("countable") is False and record.get("duplicate_of_record_id"):
        return ("non_countable_duplicate", "record is marked as a non-countable duplicate")
    for item in review_items:
        if _lower(item.get("status") or "pending") == "pending":
            severity = _lower(item.get("severity"))
            if severity in {"high", "critical"}:
                return (
                    str(item.get("item_type") or "pending_human_review"),
                    item.get("reason") or "unresolved human review item targets record",
                )
    return None


def _review_acceptance_status(record: dict, default_status: str) -> str:
    if record.get("human_review_applied"):
        review_status = _lower(record.get("review_status"))
        if review_status == "corrected":
            return "corrected_after_human_review"
        if review_status in {"accepted", "accepted_as_is", "resolved"}:
            return "accepted_after_human_review"
    return default_status


def _evaluate_record(record: dict, state: dict, indexes: dict) -> tuple[dict, dict]:
    enriched = deepcopy(record)
    rid = _record_id(record)
    blocks: list[tuple[str, str, str]] = []
    warnings: list[str] = []

    context = indexes["disease_context"]
    disease_assessment = assess_record_disease_compatibility(record, context)
    if disease_assessment.get("reject_record") or record.get(
        "record_disease_compatibility_reject"
    ):
        _add_block(
            blocks,
            "quarantined_disease_mismatch",
            "disease_pathogen_incompatible_with_task",
            disease_assessment.get("reason")
            or record.get("record_disease_compatibility_reason")
            or "record disease/pathogen is incompatible with task disease",
        )
    elif _lower(record.get("record_disease_compatibility_status")) in {
        "incompatible_disease",
        "unrelated_disease",
        "disease_mismatch",
    }:
        _add_block(
            blocks,
            "quarantined_disease_mismatch",
            "disease_mismatch",
            record.get("record_disease_compatibility_reason")
            or "record disease compatibility status is blocking",
        )

    if rid in indexes["human_review_rejected_ids"] or record.get(
        "record_excluded_by_human_review"
    ):
        _add_block(
            blocks,
            "excluded_by_human_review",
            "explicit_human_review_reject",
            "explicit human review rejected this record",
        )

    schema_status = _lower(record.get("schema_status"))
    if schema_status in _SCHEMA_BLOCK_STATUSES:
        _add_block(
            blocks,
            "quarantined_schema_invalid",
            f"schema_status_{schema_status}",
            f"schema_status={schema_status}",
        )
    validation_errors = " ".join(str(v) for v in _as_list(record.get("validation_errors")))
    if "disease_mismatch" in validation_errors:
        _add_block(
            blocks,
            "quarantined_disease_mismatch",
            "disease_mismatch",
            "schema validation reported disease_mismatch",
        )

    normalization_status = _lower(record.get("normalization_status"))
    if any(token in normalization_status for token in ("rejected", "quarantined")):
        _add_block(
            blocks,
            "quarantined_normalization_rejected",
            "normalization_rejected",
            f"normalization_status={normalization_status}",
        )
    if "disease_mismatch" in normalization_status:
        _add_block(
            blocks,
            "quarantined_disease_mismatch",
            "disease_mismatch",
            f"normalization_status={normalization_status}",
        )
    if _lower(record.get("provenance_status")) == "failed":
        _add_block(
            blocks,
            "quarantined_schema_invalid",
            "provenance_failed",
            "provenance_status=failed",
        )

    source = indexes["sources_by_id"].get(_source_id(record))
    source_block = _source_is_blocking(source)
    if source_block:
        flag, reason = source_block
        _add_block(
            blocks,
            "quarantined_source_not_task_relevant",
            flag,
            reason,
        )

    document_block = _document_block(
        _document_candidates(
            record, indexes["documents_by_id"], indexes["documents_by_source"]
        )
    )
    if document_block:
        flag, reason = document_block
        _add_block(
            blocks,
            "quarantined_document_not_task_relevant",
            flag,
            reason,
        )

    chunk_block = _chunk_block(
        _chunk_candidates(record, indexes["chunks_by_id"], indexes["chunks_by_source"])
    )
    if chunk_block:
        flag, reason = chunk_block
        _add_block(
            blocks,
            "quarantined_chunk_not_task_relevant",
            flag,
            reason,
        )

    validation_block = _validation_block(indexes["validation_by_record"].get(rid, []))
    if validation_block:
        status, flag, reason = validation_block
        _add_block(blocks, status, flag, reason)

    anomaly_block = _anomaly_block(indexes["anomalies_by_record"].get(rid, []))
    if anomaly_block:
        flag, reason = anomaly_block
        _add_block(
            blocks,
            "quarantined_critical_anomaly",
            flag,
            reason,
        )

    pending_block = _pending_review_block(
        record, indexes["review_items_by_record"].get(rid, [])
    )

    validation_limited, _, validation_warnings = _validation_limited(state)
    if validation_limited:
        _add_warning(warnings, "no_task_compatible_validation_source")
    for warning in validation_warnings:
        _add_warning(warnings, warning)

    block = _first_block(blocks)
    if block:
        status, _, reason = block
        final_dataset_included = False
        quarantine_reason = reason
    elif pending_block:
        status = "pending_human_review"
        final_dataset_included = False
        quarantine_reason = pending_block[1]
        _add_warning(warnings, pending_block[0])
    else:
        status = _review_acceptance_status(
            record, "accepted_with_warnings" if warnings else "accepted"
        )
        final_dataset_included = True
        quarantine_reason = None

    blocking_flags = [flag for _, flag, _ in blocks]
    reasons = [reason for _, _, reason in blocks]
    if pending_block and not block:
        blocking_flags.append(pending_block[0])
        reasons.append(pending_block[1])
    if not reasons and final_dataset_included:
        reasons.append("record passed deterministic run quality gates")

    enriched.update(
        {
            "final_dataset_included": final_dataset_included,
            "record_final_inclusion_status": status,
            "quality_gate_reasons": reasons,
            "quality_gate_blocking_flags": blocking_flags,
            "quarantine_reason": quarantine_reason,
            "quality_gate_method": QUALITY_GATE_METHOD,
            "quality_gate_warnings": warnings,
            "record_disease_compatibility_status": disease_assessment.get("status")
            or record.get("record_disease_compatibility_status"),
            "record_disease_compatibility_reason": disease_assessment.get("reason")
            or record.get("record_disease_compatibility_reason"),
            "record_target_disease_terms_found": list(
                disease_assessment.get("target_disease_terms_found") or []
            ),
            "record_incompatible_disease_terms_found": list(
                disease_assessment.get("incompatible_disease_terms_found") or []
            ),
            "record_disease_compatibility_reject": bool(
                disease_assessment.get("reject_record")
                or record.get("record_disease_compatibility_reject")
            ),
        }
    )

    decision = {
        "record_id": rid,
        "source_id": _source_id(record) or None,
        "source_url": _source_url(record),
        "supporting_chunk_id": _supporting_chunk_id(record) or None,
        "evidence_quote": record.get("evidence_quote"),
        "final_dataset_included": final_dataset_included,
        "record_final_inclusion_status": status,
        "quality_gate_reasons": reasons,
        "quality_gate_blocking_flags": blocking_flags,
        "quarantine_reason": quarantine_reason,
        "quality_gate_method": QUALITY_GATE_METHOD,
        "quality_gate_warnings": warnings,
    }
    return enriched, decision


def _build_indexes(state: dict) -> dict:
    documents = [row for row in _as_list(state.get("documents")) if isinstance(row, dict)]
    chunks = [row for row in _as_list(state.get("evidence_chunks")) if isinstance(row, dict)]
    return {
        "disease_context": build_disease_relevance_context(state),
        "sources_by_id": _index_by_id(_as_list(state.get("source_registry")), "source_id"),
        "documents_by_id": _index_by_id(documents, "document_id"),
        "documents_by_source": _documents_by_source(documents),
        "chunks_by_id": _index_by_id(chunks, "chunk_id"),
        "chunks_by_source": _chunks_by_source(chunks),
        "validation_by_record": _validation_results_by_record(
            _as_list(state.get("validation_results"))
        ),
        "anomalies_by_record": _anomalies_by_record(
            _as_list(state.get("anomaly_results"))
        ),
        "review_items_by_record": _review_items_by_record(
            _as_list(state.get("human_review_queue"))
        ),
        "human_review_rejected_ids": _human_review_rejected_record_ids(state),
    }


def _split_evaluated(records: list[dict]) -> tuple[list[dict], list[dict], list[dict]]:
    accepted: list[dict] = []
    quarantined: list[dict] = []
    pending: list[dict] = []
    for record in records:
        status = record.get("record_final_inclusion_status")
        if record.get("final_dataset_included") and status in ACCEPTED_STATUSES:
            accepted.append(record)
        elif status == "pending_human_review":
            pending.append(record)
        else:
            quarantined.append(record)
    return accepted, quarantined, pending


def _evaluate_records(records: list[dict], state: dict, indexes: dict) -> tuple[list[dict], list[dict]]:
    evaluated: list[dict] = []
    decisions: list[dict] = []
    for record in records:
        if not isinstance(record, dict):
            continue
        enriched, decision = _evaluate_record(record, state, indexes)
        evaluated.append(enriched)
        decisions.append(decision)
    return evaluated, decisions


def _post_review_records(
    state: dict,
    accepted_records: list[dict],
    indexes: dict,
) -> tuple[list[dict], list[dict]]:
    if not _has_explicit_human_review_decisions(state):
        return deepcopy(accepted_records), []
    source_rows = [
        row
        for row in _as_list(state.get("final_dataset_post_review"))
        if isinstance(row, dict)
    ]
    if not source_rows:
        return [], []
    evaluated, decisions = _evaluate_records(source_rows, state, indexes)
    accepted, _, _ = _split_evaluated(evaluated)
    return accepted, decisions


def _no_task_relevant_signal(state: dict) -> bool:
    summary = _as_dict(state.get("disease_relevance_summary"))
    if summary.get("target_data_chunk_count") == 0:
        return True
    for key in (
        "chunk_status_counts",
        "document_status_counts",
        "source_status_counts",
    ):
        counts = _as_dict(summary.get(key))
        if counts and counts.get("target_disease_match", 0) == 0:
            return True
    data_presence = _as_dict(state.get("data_presence_summary"))
    if data_presence and data_presence.get("target_data_chunk_count", 0) == 0:
        return True
    return False


def _build_quality_summary(
    *,
    state: dict,
    pre_quality_records: list[dict],
    final_dataset: list[dict],
    quarantined_records: list[dict],
    pending_review_records: list[dict],
    final_dataset_post_review: list[dict],
    records_excluded_by_review: list[dict],
    decisions: list[dict],
) -> tuple[dict, dict]:
    blocking_counter = Counter()
    warning_counter = Counter()
    status_counter = Counter()
    for decision in decisions:
        status_counter[str(decision.get("record_final_inclusion_status") or "unknown")] += 1
        for flag in _as_list(decision.get("quality_gate_blocking_flags")):
            blocking_counter[str(flag)] += 1
        for warning in _as_list(decision.get("quality_gate_warnings")):
            warning_counter[str(warning)] += 1

    validation_limited, no_compatible_validation, validation_warnings = _validation_limited(state)
    accepted_count = len(final_dataset)
    quarantined_count = len(quarantined_records)
    pending_count = len(pending_review_records)
    normalized_count = len(pre_quality_records)
    human_review_required = pending_count > 0 or any(
        row.get("requires_human_review") for row in pre_quality_records
    )

    if normalized_count == 0:
        run_quality_status = (
            "no_task_relevant_records"
            if _no_task_relevant_signal(state)
            else "no_records_extracted"
        )
    elif accepted_count > 0 and quarantined_count > 0:
        run_quality_status = "partial_with_quarantined_records"
    elif accepted_count > 0 and human_review_required:
        run_quality_status = "passed_with_review"
    elif accepted_count > 0 and validation_limited:
        run_quality_status = "passed_with_review"
    elif accepted_count > 0:
        run_quality_status = "passed"
    elif pending_count > 0:
        run_quality_status = "human_review_required"
    elif quarantined_count > 0:
        run_quality_status = "failed_quality_gate"
    elif validation_limited:
        run_quality_status = "validation_limited_no_compatible_source"
    else:
        run_quality_status = "failed_quality_gate"

    if accepted_count > 0:
        acceptance_reason = "quality-gated accepted records are available"
        recommended = "Review final_dataset and warnings before use."
    elif normalized_count == 0:
        acceptance_reason = "no normalized records were extracted"
        recommended = "No reliable task-relevant records were accepted; inspect search, fetch, extraction, and quarantine diagnostics."
    elif quarantined_count:
        acceptance_reason = "all candidate records failed deterministic quality gates"
        recommended = "Use quarantined_records and record_inclusion_decisions to inspect why no records were accepted."
    else:
        acceptance_reason = "records remain pending human review"
        recommended = "Resolve pending human review items before using post-review data."

    warnings = list(validation_warnings)
    if validation_limited and "validation_limited_no_compatible_source" not in warnings:
        warnings.append("validation_limited_no_compatible_source")

    task = _task_metadata(state)
    disease_mismatch_count = status_counter.get("quarantined_disease_mismatch", 0)
    outside_scope_count = status_counter.get("quarantined_outside_scope", 0)
    validation_conflict_count = status_counter.get("quarantined_validation_conflict", 0)
    critical_anomaly_count = sum(
        1
        for row in quarantined_records
        if row.get("record_final_inclusion_status") == "quarantined_critical_anomaly"
        and any(
            _lower((anom or {}).get("severity")) == "critical"
            for anom in _as_list(state.get("anomaly_results"))
            if isinstance(anom, dict)
            and anom.get("record_id") == row.get("record_id")
        )
    )
    high_anomaly_count = sum(
        1
        for row in quarantined_records
        if row.get("record_final_inclusion_status") == "quarantined_critical_anomaly"
        and any(
            _lower((anom or {}).get("severity")) == "high"
            for anom in _as_list(state.get("anomaly_results"))
            if isinstance(anom, dict)
            and anom.get("record_id") == row.get("record_id")
        )
    )
    source_blocked_count = status_counter.get(
        "quarantined_source_not_task_relevant", 0
    )

    run_quality_summary = {
        "run_quality_status": run_quality_status,
        "final_dataset_mode": "quality_gated_accepted_records",
        **task,
        "normalized_record_count": normalized_count,
        "accepted_record_count": accepted_count,
        "quarantined_record_count": quarantined_count,
        "pending_review_record_count": pending_count,
        "final_dataset_count": len(final_dataset),
        "final_dataset_post_review_count": len(final_dataset_post_review),
        "rejected_record_count": len(records_excluded_by_review),
        "disease_mismatch_record_count": disease_mismatch_count,
        "outside_scope_record_count": outside_scope_count,
        "validation_conflict_record_count": validation_conflict_count,
        "critical_anomaly_record_count": critical_anomaly_count,
        "high_anomaly_record_count": high_anomaly_count,
        "source_blocked_record_count": source_blocked_count,
        "no_compatible_validation_source": no_compatible_validation,
        "validation_limited": validation_limited,
        "human_review_required": human_review_required,
        "blocking_reason_counts": dict(blocking_counter),
        "warning_counts": dict(warning_counter),
        "record_final_inclusion_status_counts": dict(status_counter),
        "acceptance_reason": acceptance_reason,
        "recommended_user_message": recommended,
        "warnings": warnings,
    }
    final_dataset_quality_summary = {
        "quality_gate_method": QUALITY_GATE_METHOD,
        "final_dataset_mode": "quality_gated_accepted_records",
        "normalized_record_count": normalized_count,
        "accepted_record_count": accepted_count,
        "quarantined_record_count": quarantined_count,
        "pending_review_record_count": pending_count,
        "post_review_record_count": len(final_dataset_post_review),
        "record_final_inclusion_status_counts": dict(status_counter),
        "blocking_reason_counts": dict(blocking_counter),
        "warning_counts": dict(warning_counter),
        "accepted_statuses": sorted(ACCEPTED_STATUSES),
    }
    return run_quality_summary, final_dataset_quality_summary


def apply_run_quality_gates(state: dict) -> dict:
    """Return quality-gated final dataset views and run quality summaries."""

    normalized_records = [
        row for row in _as_list(state.get("normalized_records")) if isinstance(row, dict)
    ]
    indexes = _build_indexes(state)
    pre_quality_records, decisions = _evaluate_records(normalized_records, state, indexes)
    final_dataset, quarantined_records, pending_review_records = _split_evaluated(
        pre_quality_records
    )
    final_dataset_post_review, post_review_decisions = _post_review_records(
        state, final_dataset, indexes
    )
    all_decisions = decisions + post_review_decisions
    records_excluded_by_review = [
        row
        for row in _as_list(state.get("records_excluded_by_human_review"))
        if isinstance(row, dict)
    ]
    run_quality_summary, final_dataset_quality_summary = _build_quality_summary(
        state=state,
        pre_quality_records=pre_quality_records,
        final_dataset=final_dataset,
        quarantined_records=quarantined_records,
        pending_review_records=pending_review_records,
        final_dataset_post_review=final_dataset_post_review,
        records_excluded_by_review=records_excluded_by_review,
        decisions=all_decisions,
    )
    return {
        "final_dataset_pre_quality_gate": pre_quality_records,
        "final_dataset": final_dataset,
        "final_dataset_post_review": final_dataset_post_review,
        "quarantined_records": quarantined_records,
        "pending_review_records": pending_review_records,
        "record_inclusion_decisions": all_decisions,
        "run_quality_summary": run_quality_summary,
        "final_dataset_quality_summary": final_dataset_quality_summary,
    }
