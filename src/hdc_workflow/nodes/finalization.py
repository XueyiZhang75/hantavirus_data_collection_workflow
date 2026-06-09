"""Final data package builder (Step 13).

Assembles a hardened, auditable `FinalDataPackage` from the workflow state.
Adds package metadata, workflow-summary aggregation, data dictionary,
provenance manifest, export manifest, and synthetic-fixture detection.

Does NOT call LLMs, does NOT touch the network, does NOT resolve conflicts,
and does NOT apply human review decisions to modify records.
"""

from __future__ import annotations

from ..config import load_final_package_policy
from ..models import (
    AnomalyResult,
    AppliedHumanReviewDecision,
    Conflict,
    EventCluster,
    FinalDataPackage,
    FinalPackagePolicy,
    HumanReviewAuditEntry,
    HumanReviewItem,
    LinkedEvent,
    PublicHealthRecord,
    RejectedHumanReviewDecision,
    SourceRegistryEntry,
    ValidationCase,
    ValidationComparison,
    ValidationResult,
)
from ..state import DataCollectionState, append_trace


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------


def _fixed_generated_at(policy: FinalPackagePolicy) -> str:
    return policy.fixed_generated_at


def _safe_list(state: DataCollectionState, key: str) -> list:
    return list(state.get(key) or [])


def _collect_workflow_summaries(
    state: DataCollectionState,
    policy: FinalPackagePolicy,
) -> dict:
    return {field: state.get(field) for field in policy.workflow_summary_fields}


def _build_data_dictionary(
    state: DataCollectionState,
    policy: FinalPackagePolicy,
) -> list[dict]:
    schema = state.get("collection_schema") or {}
    core_fields = schema.get("core_fields") if isinstance(schema, dict) else None
    if core_fields:
        result: list[dict] = []
        for field in core_fields:
            result.append(
                {
                    "name": field.get("name"),
                    "type": field.get("type"),
                    "required": field.get("required", False),
                    "description": field.get("description") or "",
                }
            )
        return result
    return [
        {"name": name, "type": "unknown", "required": False, "description": ""}
        for name in policy.final_dataset_field_order
    ]


# ---------------------------------------------------------------------------
# Synthetic fixture detection
# ---------------------------------------------------------------------------


def _section_has_fixture(obj, markers: list[str]) -> bool:
    if obj is None:
        return False
    if isinstance(obj, dict):
        if obj.get("is_fixture_document") is True:
            return True
        if obj.get("fixture_id"):
            return True
        meta = obj.get("metadata")
        if isinstance(meta, dict):
            if meta.get("synthetic_fixture") is True:
                return True
            if meta.get("not_real_public_health_data") is True:
                return True
            if meta.get("fixture_id"):
                return True
        for value in obj.values():
            if _section_has_fixture(value, markers):
                return True
        return False
    if isinstance(obj, list):
        return any(_section_has_fixture(v, markers) for v in obj)
    if isinstance(obj, str):
        return any(marker in obj for marker in markers)
    return False


def _detect_synthetic_fixture_data(
    state: DataCollectionState,
    policy: FinalPackagePolicy,
) -> tuple[bool, str | None]:
    markers = list(policy.synthetic_fixture_markers or [])
    for key in (
        "documents",
        "evidence_chunks",
        "raw_records",
        "validated_records",
        "normalized_records",
        "conflicts",
        "human_review_queue",
    ):
        items = state.get(key) or []
        if _section_has_fixture(items, markers):
            return (
                True,
                (
                    "This final data package contains synthetic fixture data used "
                    "only for deterministic workflow testing; it is not real "
                    "public health data."
                ),
            )
    return False, None


# ---------------------------------------------------------------------------
# Provenance + metadata
# ---------------------------------------------------------------------------


def _build_provenance_manifest(state: DataCollectionState) -> dict:
    normalized = _safe_list(state, "normalized_records")
    conflicts = _safe_list(state, "conflicts")

    def _count(records, field):
        return sum(
            1
            for r in records
            if isinstance(r, dict)
            and r.get(field) not in (None, "", [], {})
        )

    return {
        "source_count": len(_safe_list(state, "source_registry")),
        "document_count": len(_safe_list(state, "documents")),
        "evidence_chunk_count": len(_safe_list(state, "evidence_chunks")),
        "raw_record_count": len(_safe_list(state, "raw_records")),
        "validated_record_count": len(_safe_list(state, "validated_records")),
        "normalized_record_count": len(normalized),
        "linked_event_count": len(_safe_list(state, "linked_events")),
        "event_cluster_count": len(_safe_list(state, "event_clusters")),
        "duplicate_cluster_count": len(_safe_list(state, "duplicate_clusters")),
        "validation_case_count": len(_safe_list(state, "validation_cases")),
        "validation_comparison_count": len(_safe_list(state, "validation_comparisons")),
        "validation_result_count": len(_safe_list(state, "validation_results")),
        "anomaly_result_count": len(_safe_list(state, "anomaly_results")),
        "applied_human_review_decision_count": len(
            _safe_list(state, "applied_human_review_decisions")
        ),
        "rejected_human_review_decision_count": len(
            _safe_list(state, "rejected_human_review_decisions")
        ),
        "human_review_audit_entry_count": len(
            _safe_list(state, "human_review_audit_trail")
        ),
        "final_dataset_post_review_count": len(
            _safe_list(state, "final_dataset_post_review")
        ),
        "conflict_count": len(conflicts),
        "human_review_item_count": len(_safe_list(state, "human_review_queue")),
        "records_with_source_url_count": _count(normalized, "source_url"),
        "records_with_evidence_quote_count": _count(normalized, "evidence_quote"),
        "records_with_supporting_chunk_id_count": _count(normalized, "supporting_chunk_id"),
        "records_with_linked_event_id_count": _count(normalized, "linked_event_id"),
        "records_with_event_cluster_id_count": _count(normalized, "event_cluster_id"),
        "countable_record_count": sum(
            1 for r in normalized if isinstance(r, dict) and r.get("countable") is True
        ),
        "non_countable_duplicate_count": sum(
            1
            for r in normalized
            if isinstance(r, dict)
            and r.get("event_member_status") == "non_countable_duplicate"
        ),
        "generic_record_count": sum(
            1
            for r in normalized
            if isinstance(r, dict)
            and r.get("record_schema") == "generic_public_health_record"
        ),
        "legacy_hantavirus_record_count": sum(
            1
            for r in normalized
            if isinstance(r, dict) and r.get("disease") == "Hantavirus disease"
        ),
        "conflicts_with_record_ids_count": sum(
            1
            for c in conflicts
            if isinstance(c, dict) and (c.get("record_ids") or [])
        ),
        "conflicts_requiring_human_review_count": sum(
            1
            for c in conflicts
            if isinstance(c, dict) and c.get("requires_human_review")
        ),
    }


def _detect_llm_used(state: DataCollectionState) -> bool:
    for key in ("normalized_records", "validated_records", "raw_records"):
        for record in state.get(key) or []:
            if isinstance(record, dict) and record.get("llm_used"):
                return True
    summary = state.get("llm_extraction_summary") or {}
    if isinstance(summary, dict):
        if summary.get("llm_enabled") and (summary.get("llm_success_count") or 0) > 0:
            return True
    return False


def _build_package_metadata(
    state: DataCollectionState,
    policy: FinalPackagePolicy,
    contains_fixture: bool,
    fixture_notice: str | None,
    trace: list[dict],
    llm_used: bool,
) -> dict:
    spec = state.get("collection_spec") or {}
    llm_summary = state.get("llm_extraction_summary") or {}
    search_summary = state.get("source_search_execution_summary") or {}
    return {
        "package_name": "data_collection_workflow_final_package",
        "package_version": policy.package_version,
        "package_builder": policy.package_builder,
        "generated_at": _fixed_generated_at(policy),
        "disease": spec.get("disease") if isinstance(spec, dict) else None,
        "geography": spec.get("geography") if isinstance(spec, dict) else None,
        "time_window": spec.get("time_window") if isinstance(spec, dict) else None,
        "workflow_node_count": len(trace),
        "contains_synthetic_fixture_data": contains_fixture,
        "synthetic_fixture_notice": fixture_notice,
        "llm_used": llm_used,
        "llm_provider": llm_summary.get("llm_provider") if isinstance(llm_summary, dict) else None,
        "llm_model": llm_summary.get("llm_model") if isinstance(llm_summary, dict) else None,
        "web_search_used": bool(
            isinstance(search_summary, dict)
            and (search_summary.get("executed_query_count") or 0) > 0
        ),
        "baseline_comparison_included": False,
        "evaluation_metrics_included": False,
    }


def _build_export_manifest(
    package: FinalDataPackage,
    policy: FinalPackagePolicy,
) -> dict:
    return {
        "exportable_sections": list(policy.exportable_sections),
        "section_counts": {
            "final_dataset": len(package.final_dataset),
            "final_dataset_post_review": len(package.final_dataset_post_review),
            "records_excluded_by_human_review": len(
                package.records_excluded_by_human_review
            ),
            "source_registry": len(package.source_registry),
            "linked_events": len(package.linked_events),
            "event_clusters": len(package.event_clusters),
            "duplicate_clusters": len(package.duplicate_clusters),
            "validation_cases": len(package.validation_cases),
            "validation_comparisons": len(package.validation_comparisons),
            "validation_results": len(package.validation_results),
            "anomaly_results": len(package.anomaly_results),
            "applied_human_review_decisions": len(
                package.applied_human_review_decisions
            ),
            "rejected_human_review_decisions": len(
                package.rejected_human_review_decisions
            ),
            "human_review_audit_trail": len(package.human_review_audit_trail),
            "conflicts": len(package.conflicts),
            "human_review_items": len(package.human_review_items),
            "excluded_sources": len(package.excluded_sources),
            "collection_trace": len(package.collection_trace),
            "data_dictionary": len(package.data_dictionary),
        },
    }


def _build_finalization_summary(
    package: FinalDataPackage,
    workflow_summaries: dict,
    contains_fixture: bool,
) -> dict:
    package_dict = package.model_dump()
    disease_counts: dict[str, int] = {}
    source_type_counts: dict[str, int] = {}
    extraction_method_counts: dict[str, int] = {}
    for record in package_dict.get("final_dataset") or []:
        disease = str(record.get("disease") or "unknown")
        source_type = str(record.get("source_type") or "unknown")
        method = str(record.get("extraction_method") or "unknown")
        disease_counts[disease] = disease_counts.get(disease, 0) + 1
        source_type_counts[source_type] = source_type_counts.get(source_type, 0) + 1
        extraction_method_counts[method] = extraction_method_counts.get(method, 0) + 1
    return {
        "final_dataset_count": len(package.final_dataset),
        "final_dataset_post_review_count": len(package.final_dataset_post_review),
        "records_excluded_by_human_review_count": len(
            package.records_excluded_by_human_review
        ),
        "generic_record_count": sum(
            1
            for record in package_dict.get("final_dataset") or []
            if record.get("record_schema") == "generic_public_health_record"
        ),
        "legacy_hantavirus_record_count": sum(
            1
            for record in package_dict.get("final_dataset") or []
            if record.get("disease") == "Hantavirus disease"
        ),
        "disease_counts": disease_counts,
        "source_type_counts": source_type_counts,
        "extraction_method_counts": extraction_method_counts,
        "source_registry_count": len(package.source_registry),
        "excluded_source_count": len(package.excluded_sources),
        "linked_event_count": len(package.linked_events),
        "event_cluster_count": len(package.event_clusters),
        "duplicate_cluster_count": len(package.duplicate_clusters),
        "validation_case_count": len(package.validation_cases),
        "validation_comparison_count": len(package.validation_comparisons),
        "validation_result_count": len(package.validation_results),
        "anomaly_result_count": len(package.anomaly_results),
        "applied_human_review_decision_count": len(
            package.applied_human_review_decisions
        ),
        "rejected_human_review_decision_count": len(
            package.rejected_human_review_decisions
        ),
        "human_review_audit_entry_count": len(package.human_review_audit_trail),
        "countable_record_count": sum(
            1
            for record in package_dict.get("final_dataset") or []
            if record.get("countable") is True
        ),
        "non_countable_duplicate_count": sum(
            1
            for record in package_dict.get("final_dataset") or []
            if record.get("event_member_status") == "non_countable_duplicate"
        ),
        "conflict_count": len(package.conflicts),
        "human_review_item_count": len(package.human_review_items),
        "collection_trace_count": len(package.collection_trace),
        "workflow_summary_count": len(workflow_summaries),
        "contains_synthetic_fixture_data": contains_fixture,
        "final_package_keys": sorted(package_dict.keys()),
}


def _default_post_review_records(records: list[dict]) -> list[dict]:
    out: list[dict] = []
    for record in records:
        row = dict(record)
        row.setdefault("review_status", "unreviewed")
        row.setdefault("review_decision_ids", [])
        row.setdefault("record_excluded_by_human_review", False)
        row.setdefault("final_dataset_included", True)
        row.setdefault("human_review_applied", False)
        row.setdefault("human_review_audit_ids", [])
        row.setdefault("anomaly_status", None)
        row.setdefault("anomaly_ids", [])
        out.append(row)
    return out


def _default_human_review_application_summary(records: list[dict]) -> dict:
    return {
        "records_before_review": len(records),
        "records_after_review": len(records),
        "records_excluded_by_review": 0,
        "records_corrected_by_review": 0,
        "clusters_modified_by_review": 0,
        "validation_results_modified_by_review": 0,
        "sources_modified_by_review": 0,
        "anomalies_resolved_by_review": 0,
        "decisions_provided_count": 0,
        "decisions_applied_count": 0,
        "decisions_rejected_count": 0,
        "audit_entry_count": 0,
    }


# ---------------------------------------------------------------------------
# Node
# ---------------------------------------------------------------------------


def final_data_package_builder(state: DataCollectionState) -> dict:
    """Assemble the hardened, auditable FinalDataPackage."""

    policy = FinalPackagePolicy(**load_final_package_policy())

    normalized_records = _safe_list(state, "normalized_records")
    post_review_records = _safe_list(state, "final_dataset_post_review")
    if not post_review_records:
        post_review_records = _default_post_review_records(normalized_records)
    records_excluded_by_review = _safe_list(state, "records_excluded_by_human_review")
    source_registry = _safe_list(state, "source_registry")
    linked_events = _safe_list(state, "linked_events")
    event_clusters = _safe_list(state, "event_clusters")
    duplicate_clusters = _safe_list(state, "duplicate_clusters")
    validation_cases = _safe_list(state, "validation_cases")
    validation_comparisons = _safe_list(state, "validation_comparisons")
    validation_results = _safe_list(state, "validation_results")
    anomaly_results = _safe_list(state, "anomaly_results")
    applied_decisions = _safe_list(state, "applied_human_review_decisions")
    rejected_decisions = _safe_list(state, "rejected_human_review_decisions")
    audit_trail = _safe_list(state, "human_review_audit_trail")
    conflicts = _safe_list(state, "conflicts")
    human_review_queue = _safe_list(state, "human_review_queue")

    final_dataset = [PublicHealthRecord(**r) for r in normalized_records]
    final_dataset_post_review = [
        PublicHealthRecord(**r) for r in post_review_records
    ]
    records_excluded_models = [
        PublicHealthRecord(**r) for r in records_excluded_by_review
    ]
    registry_models = [SourceRegistryEntry(**e) for e in source_registry]
    excluded_sources = [
        e
        for e in registry_models
        if e.screening_decision == "exclude"
        or e.critic_decision == "exclude"
        or e.final_screening_decision == "exclude"
        or e.status == "excluded"
    ]
    included_registry = [e for e in registry_models if e not in excluded_sources]

    linked_event_models = [LinkedEvent(**le) for le in linked_events]
    event_cluster_models = [EventCluster(**cluster) for cluster in event_clusters]
    duplicate_cluster_models = [
        EventCluster(**cluster) for cluster in duplicate_clusters
    ]
    validation_case_models = [ValidationCase(**item) for item in validation_cases]
    validation_comparison_models = [
        ValidationComparison(**item) for item in validation_comparisons
    ]
    validation_result_models = [
        ValidationResult(**item) for item in validation_results
    ]
    anomaly_result_models = [AnomalyResult(**item) for item in anomaly_results]
    applied_decision_models = [
        AppliedHumanReviewDecision(**item) for item in applied_decisions
    ]
    rejected_decision_models = [
        RejectedHumanReviewDecision(**item) for item in rejected_decisions
    ]
    audit_models = [HumanReviewAuditEntry(**item) for item in audit_trail]
    conflict_models = [Conflict(**c) for c in conflicts]
    human_review_items = [HumanReviewItem(**item) for item in human_review_queue]

    contains_fixture, fixture_notice = _detect_synthetic_fixture_data(state, policy)
    workflow_summaries = _collect_workflow_summaries(state, policy)
    data_dictionary = _build_data_dictionary(state, policy)
    provenance_manifest = _build_provenance_manifest(state)
    llm_used = _detect_llm_used(state)
    human_review_application_summary = state.get(
        "human_review_application_summary"
    ) or _default_human_review_application_summary(normalized_records)

    # Append trace before building the package so package.collection_trace
    # includes this very event and stays length-aligned with state trace.
    trace = append_trace(
        state,
        node_name="final_data_package_builder",
        message="Assembled hardened FinalDataPackage from current state.",
        metadata={
            "final_dataset_size": len(final_dataset),
            "source_registry_size": len(included_registry),
            "excluded_source_count": len(excluded_sources),
            "linked_event_count": len(linked_event_models),
            "event_cluster_count": len(event_cluster_models),
            "duplicate_cluster_count": len(duplicate_cluster_models),
            "validation_result_count": len(validation_result_models),
            "anomaly_result_count": len(anomaly_result_models),
            "applied_human_review_decision_count": len(applied_decision_models),
            "rejected_human_review_decision_count": len(rejected_decision_models),
            "human_review_audit_entry_count": len(audit_models),
            "conflict_count": len(conflict_models),
            "human_review_item_count": len(human_review_items),
            "contains_synthetic_fixture_data": contains_fixture,
            "llm_used": llm_used,
            "package_version": policy.package_version,
        },
    )
    package_metadata = _build_package_metadata(
        state, policy, contains_fixture, fixture_notice, trace, llm_used
    )

    package = FinalDataPackage(
        final_dataset=final_dataset,
        final_dataset_post_review=final_dataset_post_review,
        records_excluded_by_human_review=records_excluded_models,
        source_registry=included_registry,
        linked_events=linked_event_models,
        event_clusters=event_cluster_models,
        duplicate_clusters=duplicate_cluster_models,
        validation_cases=validation_case_models,
        validation_comparisons=validation_comparison_models,
        validation_results=validation_result_models,
        validation_summary=state.get("validation_summary") or {},
        trusted_source_validation_summary=state.get(
            "trusted_source_validation_summary"
        )
        or {},
        cross_source_validation_summary=state.get(
            "cross_source_validation_summary"
        )
        or {},
        anomaly_results=anomaly_result_models,
        anomaly_summary=state.get("anomaly_summary") or {},
        applied_human_review_decisions=applied_decision_models,
        rejected_human_review_decisions=rejected_decision_models,
        human_review_audit_trail=audit_models,
        human_review_application_summary=state.get(
            "human_review_application_summary"
        )
        or human_review_application_summary,
        conflicts=conflict_models,
        human_review_items=human_review_items,
        excluded_sources=excluded_sources,
        collection_trace=trace,
        package_metadata=package_metadata,
        workflow_summaries=workflow_summaries,
        data_dictionary=data_dictionary,
        provenance_manifest=provenance_manifest,
        export_manifest={},
        export_warnings=(
            ["contains_synthetic_fixture_data"] if contains_fixture else []
        ),
        contains_synthetic_fixture_data=contains_fixture,
        synthetic_fixture_notice=fixture_notice,
    )
    # Export manifest needs the final package; fill it now.
    package.export_manifest = _build_export_manifest(package, policy)

    finalization_summary = _build_finalization_summary(
        package, workflow_summaries, contains_fixture
    )

    return {
        "final_data_package": package.model_dump(),
        "finalization_summary": finalization_summary,
        "final_dataset_post_review": [
            record.model_dump() for record in final_dataset_post_review
        ],
        "records_excluded_by_human_review": [
            record.model_dump() for record in records_excluded_models
        ],
        "human_review_application_summary": human_review_application_summary,
        "collection_trace": trace,
    }
