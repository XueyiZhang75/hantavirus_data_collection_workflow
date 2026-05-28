"""Deterministic offline end-to-end run using synthetic fixture documents.

Sets HDC_USE_FIXTURE_DOCUMENTS=true and HDC_ENABLE_LIVE_FETCH=false BEFORE
importing the graph so `content_fetch_and_parse` injects synthetic local
fixture documents for selected source IDs. The result is a non-empty
end-to-end run that exercises every downstream node without internet and
without LLM calls.

NOTE: Fixture mode uses synthetic local documents; these are NOT real public
health data.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

os.environ["HDC_USE_FIXTURE_DOCUMENTS"] = "true"
os.environ["HDC_ENABLE_LIVE_FETCH"] = "false"

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
        "fixture_document_summary": None,
        "document_quality_summary": None,
        "final_data_package": None,
        "current_route": None,
    }


def main() -> None:
    print("=" * 72)
    print("Fixture mode uses synthetic local documents; these are NOT real public")
    print("health data. This demo exists only to exercise the end-to-end workflow.")
    print("=" * 72)

    graph = build_graph()
    result = graph.invoke(_demo_initial_state())

    sep = "=" * 72
    section_summaries = [
        ("fixture_document_summary", result.get("fixture_document_summary")),
        ("content_fetch_summary", result.get("content_fetch_summary")),
        ("document_quality_summary", result.get("document_quality_summary")),
        ("evidence_chunking_summary", result.get("evidence_chunking_summary")),
        ("data_presence_summary", result.get("data_presence_summary")),
        ("structured_extraction_summary", result.get("structured_extraction_summary")),
        ("llm_extraction_summary", result.get("llm_extraction_summary")),
        ("schema_validation_summary", result.get("schema_validation_summary")),
        ("record_normalization_summary", result.get("record_normalization_summary")),
        ("record_linking_summary", result.get("record_linking_summary")),
        ("cross_source_consistency_summary", result.get("cross_source_consistency_summary")),
    ]
    for name, payload in section_summaries:
        print(sep)
        print(f"{name}:")
        print(json.dumps(payload, indent=2))

    print(sep)
    print("counts:")
    for key in (
        "documents",
        "evidence_chunks",
        "raw_records",
        "validated_records",
        "normalized_records",
        "linked_events",
        "conflicts",
        "human_review_queue",
    ):
        items = result.get(key) or []
        print(f"  - {key}: {len(items)}")

    trace = result.get("collection_trace") or []
    print(sep)
    print(f"current_route: {result.get('current_route')}")
    has_human_review = any(t.get("node_name") == "human_review" for t in trace)
    print(f"human_review appears in collection_trace: {has_human_review}")

    print(sep)
    print("first 10 validated_records:")
    for rec in (result.get("validated_records") or [])[:10]:
        print(
            f"  - {rec.get('record_id')} | "
            f"country={rec.get('country')} | "
            f"date_reported={rec.get('date_reported')} | "
            f"cases_unspecified={rec.get('cases_unspecified')} | "
            f"deaths={rec.get('deaths')} | "
            f"schema_status={rec.get('schema_status')}"
        )

    print(sep)
    print("first 10 normalized_records:")
    for rec in (result.get("normalized_records") or [])[:10]:
        print(
            f"  - {rec.get('record_id')} | "
            f"country={rec.get('country')} | "
            f"date_reported={rec.get('date_reported')} | "
            f"linked_event_id={rec.get('linked_event_id')} | "
            f"record_conflict_status={rec.get('record_conflict_status')} | "
            f"conflict_ids={rec.get('conflict_ids')}"
        )

    print(sep)
    print("first 10 linked_events:")
    for ev in (result.get("linked_events") or [])[:10]:
        print(
            f"  - {ev.get('linked_event_id')} | "
            f"record_count={ev.get('record_count')} | "
            f"linking_status={ev.get('linking_status')} | "
            f"consistency_status={ev.get('consistency_status')} | "
            f"requires_human_review={ev.get('requires_human_review')} | "
            f"conflict_ids={ev.get('conflict_ids')} | "
            f"record_ids={ev.get('record_ids')}"
        )

    print(sep)
    print("first 10 conflicts:")
    for c in (result.get("conflicts") or [])[:10]:
        print(
            f"  - {c.get('conflict_id')} | "
            f"field={c.get('field')} | "
            f"conflict_type={c.get('conflict_type')} | "
            f"severity={c.get('severity')} | "
            f"requires_human_review={c.get('requires_human_review')} | "
            f"record_ids={c.get('record_ids')}"
        )

    print(sep)
    print("human_review_summary:")
    print(json.dumps(result.get("human_review_summary"), indent=2))

    print(sep)
    queue = result.get("human_review_queue") or []
    print(f"human_review_queue count: {len(queue)}")
    print("first 10 human_review_queue items:")
    for item in queue[:10]:
        packet = item.get("review_packet") or {}
        packet_keys = list((packet.get("packet_sections") or {}).keys())
        print(
            f"  - {item.get('review_id')} | "
            f"item_type={item.get('item_type')} | "
            f"priority={item.get('priority')} | "
            f"status={item.get('status')} | "
            f"human_decision={item.get('human_decision')} | "
            f"decision_applied={item.get('decision_applied')} | "
            f"related_ids={item.get('related_ids')} | "
            f"packet_section_keys={packet_keys} | "
            f"fixture_warning={packet.get('synthetic_fixture_warning')}"
        )

    print(sep)
    package = result.get("final_data_package") or {}
    print("final_data_package key counts:")
    for key in ("final_dataset", "linked_events", "conflicts", "human_review_items"):
        print(f"  - {key}: {len(package.get(key) or [])}")

    print(sep)
    print("finalization_summary:")
    print(json.dumps(result.get("finalization_summary"), indent=2))

    print(sep)
    print("final_data_package.package_metadata:")
    print(json.dumps(package.get("package_metadata"), indent=2))

    print(sep)
    print("final_data_package.provenance_manifest:")
    print(json.dumps(package.get("provenance_manifest"), indent=2))

    print(sep)
    print("final_data_package.export_manifest:")
    print(json.dumps(package.get("export_manifest"), indent=2))

    print(sep)
    print(
        "contains_synthetic_fixture_data:",
        package.get("contains_synthetic_fixture_data"),
    )
    print("synthetic_fixture_notice:", package.get("synthetic_fixture_notice"))


if __name__ == "__main__":
    main()
