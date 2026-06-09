"""LangGraph shared state definition and helpers."""

from __future__ import annotations

from typing import TypedDict

from .models import TraceEvent


class DataCollectionState(TypedDict, total=False):
    user_request: str
    structured_task: dict | None
    collection_spec: dict | None
    task_intake_summary: dict | None
    disease_intelligence: dict | None
    disease_intelligence_summary: dict | None
    disease_profile: dict | None
    collection_schema: dict | None
    source_strategy: dict | None
    screening_criteria: dict | None
    profile_schema_summary: dict | None
    search_queries: dict | None
    search_query_inventory: list[dict]
    agentic_source_plan: dict | None
    executable_source_plan_summary: dict | None
    source_planning_agent_summary: dict | None
    source_candidates: list[dict]
    source_search_results: list[dict]
    source_search_execution_summary: dict | None
    source_discovery_summary: dict | None
    source_registry: list[dict]
    source_registry_summary: dict | None
    source_screening_summary: dict | None
    source_critic_summary: dict | None
    source_routing_summary: dict | None
    source_credibility_assessments: list[dict]
    source_credibility_summary: dict | None
    content_fetch_requests: list[dict]
    content_fetch_summary: dict | None
    document_parse_summary: dict | None
    fetch_manifest: list[dict]
    fixture_document_summary: dict | None
    documents: list[dict]
    document_quality_summary: dict | None
    evidence_chunks: list[dict]
    evidence_chunking_summary: dict | None
    data_presence_summary: dict | None
    raw_records: list[dict]
    structured_extraction_summary: dict | None
    llm_extraction_summary: dict | None
    validated_records: list[dict]
    rejected_records: list[dict]
    schema_validation_summary: dict | None
    normalized_records: list[dict]
    record_normalization_summary: dict | None
    linked_events: list[dict]
    record_linking_summary: dict | None
    event_clusters: list[dict]
    duplicate_clusters: list[dict]
    event_clustering_summary: dict | None
    duplicate_detection_summary: dict | None
    validation_records: list[dict]
    validation_cases: list[dict]
    validation_comparisons: list[dict]
    validation_results: list[dict]
    validation_summary: dict | None
    trusted_source_validation_summary: dict | None
    cross_source_validation_summary: dict | None
    anomaly_results: list[dict]
    anomaly_summary: dict | None
    anomaly_review_items: list[dict]
    conflicts: list[dict]
    cross_source_consistency_summary: dict | None
    human_review_queue: list[dict]
    human_review_decisions: list[dict]
    human_review_decisions_path: str | None
    applied_human_review_decisions: list[dict]
    rejected_human_review_decisions: list[dict]
    human_review_audit_trail: list[dict]
    human_review_application_summary: dict | None
    final_dataset_post_review: list[dict]
    records_excluded_by_human_review: list[dict]
    human_review_summary: dict | None
    final_data_package: dict | None
    finalization_summary: dict | None
    collection_trace: list[dict]
    current_route: str | None


def append_trace(
    state: DataCollectionState,
    node_name: str,
    message: str,
    metadata: dict | None = None,
) -> list[dict]:
    """Return an updated collection_trace list with a new TraceEvent appended.

    The original state is not mutated; callers should assign the returned list
    back into the state update returned from their node function.
    """

    existing = list(state.get("collection_trace") or [])
    event = TraceEvent(
        node_name=node_name,
        message=message,
        metadata=metadata or {},
    )
    existing.append(event.model_dump())
    return existing
