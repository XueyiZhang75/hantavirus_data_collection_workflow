"""Run the current LangGraph data collection workflow end-to-end and print key state."""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Make `src/` importable when the package isn't installed.
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_SRC = _PROJECT_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from hdc_workflow.graph import build_graph  # noqa: E402


def main() -> None:
    graph = build_graph()

    initial_state = {
        "user_request": (
            "Collect global human hantavirus case, outbreak, and surveillance data "
            "from 2020 to 2026, including cases, deaths, dates, locations, source URLs, "
            "source types, and evidence quotes."
        ),
        "source_candidates": [],
        "source_discovery_summary": None,
        "source_registry": [],
        "source_registry_summary": None,
        "documents": [],
        "evidence_chunks": [],
        "raw_records": [],
        "validated_records": [],
        "normalized_records": [],
        "linked_events": [],
        "conflicts": [],
        "human_review_queue": [],
        "collection_trace": [],
        "collection_spec": None,
        "disease_profile": None,
        "collection_schema": None,
        "source_strategy": None,
        "screening_criteria": None,
        "search_queries": None,
        "search_query_inventory": [],
        "final_data_package": None,
        "current_route": None,
    }

    result = graph.invoke(initial_state)

    sep = "=" * 72

    print(sep)
    print("collection_spec:")
    print(json.dumps(result.get("collection_spec"), indent=2))

    print(sep)
    disease_profile = result.get("disease_profile") or {}
    print(
        "disease_profile.disease_standard_name:",
        disease_profile.get("disease_standard_name"),
    )

    print(sep)
    schema = result.get("collection_schema") or {}
    print("collection_schema.schema_name:", schema.get("schema_name"))
    print("collection_schema.core_fields count:", len(schema.get("core_fields") or []))

    print(sep)
    strategy = result.get("source_strategy") or {}
    print("source_strategy.source_categories:")
    for cat in strategy.get("source_categories") or []:
        print(f"  - [priority={cat.get('priority')}] {cat.get('source_type')}")

    print(sep)
    search_queries = result.get("search_queries") or {}
    print("grouped search query counts:")
    for key, items in search_queries.items():
        print(f"  - {key}: {len(items)}")

    print(sep)
    inventory = result.get("search_query_inventory") or []
    print(f"search_query_inventory size: {len(inventory)}")
    print("first 3 search_query_inventory items:")
    for item in inventory[:3]:
        print(json.dumps(item, indent=2))

    print(sep)
    print("source_discovery_summary:")
    print(json.dumps(result.get("source_discovery_summary"), indent=2))

    print(sep)
    print("source_registry_summary:")
    print(json.dumps(result.get("source_registry_summary"), indent=2))

    print(sep)
    print("source_screening_summary:")
    print(json.dumps(result.get("source_screening_summary"), indent=2))

    print(sep)
    print("source_critic_summary:")
    print(json.dumps(result.get("source_critic_summary"), indent=2))

    print(sep)
    print("source_routing_summary:")
    print(json.dumps(result.get("source_routing_summary"), indent=2))

    print(sep)
    registry_after = result.get("source_registry") or []
    final_counts: dict = {}
    ready_count = 0
    review_count = 0
    for e in registry_after:
        key = e.get("final_screening_decision") or "unknown"
        final_counts[key] = final_counts.get(key, 0) + 1
        if e.get("ready_for_content_fetch"):
            ready_count += 1
        if e.get("requires_human_review"):
            review_count += 1
    print("counts by final_screening_decision:")
    for key, n in final_counts.items():
        print(f"  - {key}: {n}")
    print(f"ready_for_content_fetch_count: {ready_count}")
    print(f"requires_human_review_count: {review_count}")

    print(sep)
    print("first 10 source_registry entries after screening/critic/routing:")
    for entry in registry_after[:10]:
        print(
            f"  - {entry.get('source_id')} | "
            f"type={entry.get('source_type')} | "
            f"role={entry.get('source_role')} | "
            f"screen={entry.get('screening_decision')} | "
            f"critic={entry.get('critic_decision')} | "
            f"final={entry.get('final_screening_decision')} | "
            f"ready={entry.get('ready_for_content_fetch')} | "
            f"status={entry.get('status')}"
        )

    print(sep)
    print("content_fetch_summary:")
    print(json.dumps(result.get("content_fetch_summary"), indent=2))

    fixture_summary = result.get("fixture_document_summary")
    if fixture_summary:
        print(sep)
        print("fixture_document_summary:")
        print(json.dumps(fixture_summary, indent=2))

    print(sep)
    print("document_quality_summary:")
    print(json.dumps(result.get("document_quality_summary"), indent=2))

    print(sep)
    fetch_requests = result.get("content_fetch_requests") or []
    documents_after = result.get("documents") or []
    print(f"content_fetch_requests count: {len(fetch_requests)}")
    print(f"documents count: {len(documents_after)}")
    print("first 10 documents:")
    for doc in documents_after[:10]:
        ct_len = len(doc.get("clean_text") or "")
        print(
            f"  - {doc.get('source_id')} | "
            f"document_type={doc.get('document_type')} | "
            f"fetch_purpose={doc.get('fetch_purpose')} | "
            f"fetch_status={doc.get('fetch_status')} | "
            f"parse_status={doc.get('parse_status')} | "
            f"quality={doc.get('quality_status')} | "
            f"offline_stub={doc.get('is_offline_stub')} | "
            f"clean_text_len={ct_len}"
        )

    print(sep)
    print("evidence_chunking_summary:")
    print(json.dumps(result.get("evidence_chunking_summary"), indent=2))

    print(sep)
    print("data_presence_summary:")
    print(json.dumps(result.get("data_presence_summary"), indent=2))

    print(sep)
    evidence_chunks = result.get("evidence_chunks") or []
    print(f"evidence_chunks count: {len(evidence_chunks)}")
    print("first 10 evidence_chunks:")
    for chunk in evidence_chunks[:10]:
        text_len = len(chunk.get("text") or "")
        print(
            f"  - {chunk.get('chunk_id')} | "
            f"source_id={chunk.get('source_id')} | "
            f"chunk_kind={chunk.get('chunk_kind')} | "
            f"fetch_purpose={chunk.get('fetch_purpose')} | "
            f"contains_target_data={chunk.get('contains_target_data')} | "
            f"data_types={chunk.get('data_types')} | "
            f"context_types={chunk.get('context_types')} | "
            f"confidence={chunk.get('confidence')} | "
            f"text_len={text_len}"
        )

    print(sep)
    print("structured_extraction_summary:")
    print(json.dumps(result.get("structured_extraction_summary"), indent=2))

    llm_summary = result.get("llm_extraction_summary")
    if llm_summary:
        print(sep)
        print("llm_extraction_summary:")
        print(json.dumps(llm_summary, indent=2))
        struct = result.get("structured_extraction_summary") or {}
        print(
            f"extraction_mode={struct.get('extraction_mode')} | "
            f"llm_enabled={struct.get('llm_enabled')} | "
            f"llm_call_count={struct.get('llm_call_count')} | "
            f"llm_success_count={struct.get('llm_success_count')} | "
            f"llm_error_count={struct.get('llm_error_count')} | "
            f"llm_fallback_count={struct.get('llm_fallback_count')}"
        )

    print(sep)
    print("schema_validation_summary:")
    print(json.dumps(result.get("schema_validation_summary"), indent=2))

    print(sep)
    raw_records = result.get("raw_records") or []
    validated_records = result.get("validated_records") or []
    rejected_records = result.get("rejected_records") or []
    print(f"raw_records count: {len(raw_records)}")
    print(f"validated_records count: {len(validated_records)}")
    print(f"rejected_records count: {len(rejected_records)}")
    print("first 10 raw_records:")
    for rec in raw_records[:10]:
        print(
            f"  - {rec.get('record_id')} | "
            f"source_id={rec.get('source_id')} | "
            f"supporting_chunk_id={rec.get('supporting_chunk_id')} | "
            f"country={rec.get('country')} | "
            f"date_reported={rec.get('date_reported')} | "
            f"cases_confirmed={rec.get('cases_confirmed')} | "
            f"cases_probable={rec.get('cases_probable')} | "
            f"cases_suspected={rec.get('cases_suspected')} | "
            f"cases_unspecified={rec.get('cases_unspecified')} | "
            f"deaths={rec.get('deaths')} | "
            f"extraction_confidence={rec.get('extraction_confidence')}"
        )
    print("first 10 validated_records:")
    for rec in validated_records[:10]:
        print(
            f"  - {rec.get('record_id')} | "
            f"schema_status={rec.get('schema_status')} | "
            f"provenance_status={rec.get('provenance_status')} | "
            f"requires_human_review={rec.get('requires_human_review')} | "
            f"missing_fields={rec.get('missing_fields')} | "
            f"validation_errors={rec.get('validation_errors')}"
        )

    print(sep)
    print("record_normalization_summary:")
    print(json.dumps(result.get("record_normalization_summary"), indent=2))

    print(sep)
    normalized_records = result.get("normalized_records") or []
    print(f"normalized_records count: {len(normalized_records)}")
    print("first 10 normalized_records:")
    for rec in normalized_records[:10]:
        print(
            f"  - {rec.get('record_id')} | "
            f"country={rec.get('country')} | "
            f"country_raw={rec.get('country_raw')} | "
            f"subnational_location={rec.get('subnational_location')} | "
            f"date_reported={rec.get('date_reported')} | "
            f"date_reported_raw={rec.get('date_reported_raw')} | "
            f"virus_or_syndrome={rec.get('virus_or_syndrome')} | "
            f"virus_or_syndrome_raw={rec.get('virus_or_syndrome_raw')} | "
            f"case_definition={rec.get('case_definition')} | "
            f"case_definition_raw={rec.get('case_definition_raw')} | "
            f"source_type={rec.get('source_type')} | "
            f"normalization_status={rec.get('normalization_status')} | "
            f"requires_human_review={rec.get('requires_human_review')} | "
            f"normalization_warnings={rec.get('normalization_warnings')}"
        )

    print(sep)
    print("record_linking_summary:")
    print(json.dumps(result.get("record_linking_summary"), indent=2))

    print(sep)
    linked_events = result.get("linked_events") or []
    print(f"linked_events count: {len(linked_events)}")
    print("first 10 linked_events:")
    for ev in linked_events[:10]:
        print(
            f"  - {ev.get('linked_event_id')} | "
            f"record_count={ev.get('record_count')} | "
            f"linking_status={ev.get('linking_status')} | "
            f"requires_human_review={ev.get('requires_human_review')} | "
            f"disease={ev.get('disease')} | "
            f"virus_or_syndrome={ev.get('virus_or_syndrome')} | "
            f"country={ev.get('country')} | "
            f"subnational_location={ev.get('subnational_location')} | "
            f"date_anchor={ev.get('date_anchor')} | "
            f"record_ids={ev.get('record_ids')} | "
            f"source_ids={ev.get('source_ids')} | "
            f"linking_warnings={ev.get('linking_warnings')}"
        )

    print(sep)
    print("first 10 normalized_records with linking metadata:")
    for rec in normalized_records[:10]:
        print(
            f"  - {rec.get('record_id')} | "
            f"linked_event_id={rec.get('linked_event_id')} | "
            f"event_key={rec.get('event_key')} | "
            f"record_linking_status={rec.get('record_linking_status')} | "
            f"record_linking_warnings={rec.get('record_linking_warnings')}"
        )

    print(sep)
    print("cross_source_consistency_summary:")
    print(json.dumps(result.get("cross_source_consistency_summary"), indent=2))

    print(sep)
    conflicts = result.get("conflicts") or []
    print(f"conflicts count: {len(conflicts)}")
    print("first 10 conflicts:")
    for c in conflicts[:10]:
        print(
            f"  - {c.get('conflict_id')} | "
            f"linked_event_id={c.get('linked_event_id')} | "
            f"field={c.get('field')} | "
            f"conflict_type={c.get('conflict_type')} | "
            f"severity={c.get('severity')} | "
            f"requires_human_review={c.get('requires_human_review')} | "
            f"record_ids={c.get('record_ids')} | "
            f"source_ids={c.get('source_ids')} | "
            f"possible_reason={c.get('possible_reason')}"
        )

    print(sep)
    linked_events_after = result.get("linked_events") or []
    print("first 10 linked_events with consistency fields:")
    for ev in linked_events_after[:10]:
        print(
            f"  - {ev.get('linked_event_id')} | "
            f"record_count={ev.get('record_count')} | "
            f"linking_status={ev.get('linking_status')} | "
            f"consistency_status={ev.get('consistency_status')} | "
            f"conflict_ids={ev.get('conflict_ids')} | "
            f"requires_human_review={ev.get('requires_human_review')} | "
            f"consistency_warnings={ev.get('consistency_warnings')}"
        )

    print(sep)
    annotated_records = result.get("normalized_records") or []
    print("first 10 normalized_records with conflict metadata:")
    for rec in annotated_records[:10]:
        print(
            f"  - {rec.get('record_id')} | "
            f"linked_event_id={rec.get('linked_event_id')} | "
            f"record_conflict_status={rec.get('record_conflict_status')} | "
            f"conflict_ids={rec.get('conflict_ids')} | "
            f"record_consistency_warnings={rec.get('record_consistency_warnings')}"
        )

    print(sep)
    queue = result.get("human_review_queue") or []
    print(f"current_route: {result.get('current_route')}")
    print(f"human_review_queue count: {len(queue)}")

    human_review_summary = result.get("human_review_summary")
    if human_review_summary:
        print(sep)
        print("human_review_summary:")
        print(json.dumps(human_review_summary, indent=2))

    if queue:
        print(sep)
        print("first 10 human_review_queue items:")
        for item in queue[:10]:
            print(
                f"  - {item.get('review_id')} | "
                f"item_type={item.get('item_type')} | "
                f"priority={item.get('priority')} | "
                f"status={item.get('status')} | "
                f"human_decision={item.get('human_decision')} | "
                f"decision_applied={item.get('decision_applied')} | "
                f"related_ids={item.get('related_ids')} | "
                f"reason={item.get('reason')} | "
                f"has_review_packet={item.get('review_packet') is not None}"
            )

    finalization_summary = result.get("finalization_summary")
    if finalization_summary:
        print(sep)
        print("finalization_summary:")
        print(json.dumps(finalization_summary, indent=2))

    final_package = result.get("final_data_package") or {}
    pkg_meta = final_package.get("package_metadata")
    if pkg_meta:
        print(sep)
        print("final_data_package.package_metadata:")
        print(json.dumps(pkg_meta, indent=2))
    prov = final_package.get("provenance_manifest")
    if prov:
        print(sep)
        print("final_data_package.provenance_manifest:")
        print(json.dumps(prov, indent=2))
    print(sep)
    print(
        "contains_synthetic_fixture_data:",
        final_package.get("contains_synthetic_fixture_data"),
    )
    notice = final_package.get("synthetic_fixture_notice")
    if notice:
        print("synthetic_fixture_notice:", notice)

    print(sep)
    candidates = result.get("source_candidates") or []
    print(f"source_candidates count: {len(candidates)}")
    print("first 5 source_candidates:")
    for cand in candidates[:5]:
        print(
            f"  - source_id={cand.get('source_id')} | "
            f"source_type={cand.get('source_type')} | "
            f"publisher={cand.get('publisher')} | "
            f"query_id={cand.get('query_id')} | "
            f"title={cand.get('title')}"
        )

    print(sep)
    registry = result.get("source_registry") or []
    print(f"source_registry count: {len(registry)}")
    print("first 5 source_registry entries:")
    for entry in registry[:5]:
        print(
            f"  - source_id={entry.get('source_id')} | "
            f"source_type={entry.get('source_type')} | "
            f"status={entry.get('status')} | "
            f"priority={entry.get('priority')} | "
            f"canonical_url={entry.get('canonical_url')}"
        )

    print(sep)
    trace = result.get("collection_trace") or []
    print(f"number of trace events: {len(trace)}")

    print(sep)
    final_package = result.get("final_data_package") or {}
    print("final_data_package keys:")
    for key in final_package.keys():
        print(f"  - {key}")

    print(sep)
    print("ordered node names from collection_trace:")
    for i, event in enumerate(trace, start=1):
        print(f"  {i:>2}. {event.get('node_name')}")


if __name__ == "__main__":
    main()
