"""Optional manual test: run the workflow with live HTTP fetching enabled.

Requires internet access. Sets HDC_ENABLE_LIVE_FETCH=true before importing the
graph so content_fetch_and_parse exercises the live path. Tests must NEVER
import or call this script.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

os.environ["HDC_ENABLE_LIVE_FETCH"] = "true"

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_SRC = _PROJECT_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from hdc_workflow.graph import build_graph  # noqa: E402


def _demo_initial_state() -> dict:
    return {
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
        "content_fetch_requests": [],
        "content_fetch_summary": None,
        "document_quality_summary": None,
        "final_data_package": None,
        "current_route": None,
    }


def main() -> None:
    graph = build_graph()
    result = graph.invoke(_demo_initial_state())

    sep = "=" * 72
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
    documents = result.get("documents") or []
    print(f"documents count: {len(documents)}")
    print("first 10 documents:")
    for doc in documents[:10]:
        ct_len = len(doc.get("clean_text") or "")
        print(
            f"  - {doc.get('source_id')} | "
            f"document_type={doc.get('document_type')} | "
            f"fetch_status={doc.get('fetch_status')} | "
            f"parse_status={doc.get('parse_status')} | "
            f"quality={doc.get('quality_status')} | "
            f"http={doc.get('http_status_code')} | "
            f"content_type={doc.get('content_type')} | "
            f"clean_text_len={ct_len} | "
            f"fetch_error={doc.get('fetch_error')}"
        )

    print(sep)
    print("evidence_chunking_summary:")
    print(json.dumps(result.get("evidence_chunking_summary"), indent=2))

    print(sep)
    print("data_presence_summary:")
    print(json.dumps(result.get("data_presence_summary"), indent=2))

    print(sep)
    chunks = result.get("evidence_chunks") or []
    print(f"evidence_chunks count: {len(chunks)}")
    print("first 10 evidence_chunks:")
    for chunk in chunks[:10]:
        text_len = len(chunk.get("text") or "")
        print(
            f"  - {chunk.get('chunk_id')} | "
            f"source_id={chunk.get('source_id')} | "
            f"contains_target_data={chunk.get('contains_target_data')} | "
            f"data_types={chunk.get('data_types')} | "
            f"context_types={chunk.get('context_types')} | "
            f"confidence={chunk.get('confidence')} | "
            f"text_len={text_len}"
        )

    print(sep)
    print("structured_extraction_summary:")
    print(json.dumps(result.get("structured_extraction_summary"), indent=2))

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
    print("first 10 validated_records:")
    for rec in validated_records[:10]:
        print(
            f"  - {rec.get('record_id')} | "
            f"country={rec.get('country')} | "
            f"date_reported={rec.get('date_reported')} | "
            f"cases_confirmed={rec.get('cases_confirmed')} | "
            f"cases_unspecified={rec.get('cases_unspecified')} | "
            f"deaths={rec.get('deaths')} | "
            f"schema_status={rec.get('schema_status')} | "
            f"source_url={rec.get('source_url')}"
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
            f"subnational_location={rec.get('subnational_location')} | "
            f"date_reported={rec.get('date_reported')} | "
            f"cases_confirmed={rec.get('cases_confirmed')} | "
            f"cases_unspecified={rec.get('cases_unspecified')} | "
            f"deaths={rec.get('deaths')} | "
            f"normalization_status={rec.get('normalization_status')} | "
            f"normalization_warnings={rec.get('normalization_warnings')} | "
            f"source_url={rec.get('source_url')}"
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
            f"country={ev.get('country')} | "
            f"subnational_location={ev.get('subnational_location')} | "
            f"date_anchor={ev.get('date_anchor')} | "
            f"source_ids={ev.get('source_ids')} | "
            f"record_ids={ev.get('record_ids')} | "
            f"linking_warnings={ev.get('linking_warnings')}"
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
            f"source_ids={c.get('source_ids')}"
        )

    print(sep)
    queue = result.get("human_review_queue") or []
    print(f"current_route: {result.get('current_route')}")
    print(f"human_review_queue count: {len(queue)}")


if __name__ == "__main__":
    main()
