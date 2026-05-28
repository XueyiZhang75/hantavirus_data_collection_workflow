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
    Conflict,
    FinalDataPackage,
    FinalPackagePolicy,
    HantavirusRecord,
    HumanReviewItem,
    LinkedEvent,
    SourceRegistryEntry,
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
        "conflict_count": len(conflicts),
        "human_review_item_count": len(_safe_list(state, "human_review_queue")),
        "records_with_source_url_count": _count(normalized, "source_url"),
        "records_with_evidence_quote_count": _count(normalized, "evidence_quote"),
        "records_with_supporting_chunk_id_count": _count(normalized, "supporting_chunk_id"),
        "records_with_linked_event_id_count": _count(normalized, "linked_event_id"),
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
    return {
        "package_name": "hantavirus_data_collection_final_package",
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
        "web_search_used": False,
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
            "source_registry": len(package.source_registry),
            "linked_events": len(package.linked_events),
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
    return {
        "final_dataset_count": len(package.final_dataset),
        "source_registry_count": len(package.source_registry),
        "excluded_source_count": len(package.excluded_sources),
        "linked_event_count": len(package.linked_events),
        "conflict_count": len(package.conflicts),
        "human_review_item_count": len(package.human_review_items),
        "collection_trace_count": len(package.collection_trace),
        "workflow_summary_count": len(workflow_summaries),
        "contains_synthetic_fixture_data": contains_fixture,
        "final_package_keys": sorted(package_dict.keys()),
    }


# ---------------------------------------------------------------------------
# Node
# ---------------------------------------------------------------------------


def final_data_package_builder(state: DataCollectionState) -> dict:
    """Assemble the hardened, auditable FinalDataPackage."""

    policy = FinalPackagePolicy(**load_final_package_policy())

    normalized_records = _safe_list(state, "normalized_records")
    source_registry = _safe_list(state, "source_registry")
    linked_events = _safe_list(state, "linked_events")
    conflicts = _safe_list(state, "conflicts")
    human_review_queue = _safe_list(state, "human_review_queue")

    final_dataset = [HantavirusRecord(**r) for r in normalized_records]
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
    conflict_models = [Conflict(**c) for c in conflicts]
    human_review_items = [HumanReviewItem(**item) for item in human_review_queue]

    contains_fixture, fixture_notice = _detect_synthetic_fixture_data(state, policy)
    workflow_summaries = _collect_workflow_summaries(state, policy)
    data_dictionary = _build_data_dictionary(state, policy)
    provenance_manifest = _build_provenance_manifest(state)
    llm_used = _detect_llm_used(state)

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
        source_registry=included_registry,
        linked_events=linked_event_models,
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
        "collection_trace": trace,
    }
