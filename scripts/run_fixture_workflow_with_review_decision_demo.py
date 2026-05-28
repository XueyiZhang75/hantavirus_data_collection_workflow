"""Fixture-mode demo that pre-supplies a synthetic human review decision.

Demonstrates how a UI or manual annotation tool could feed decisions into
`state["human_review_decisions"]` without changing the graph topology. The
`human_review` node will match decisions by review_id and update the queue's
status fields plus decision audit metadata.

NOTE: This demo records a synthetic human review decision; it does NOT
resolve conflicts or modify records/conflicts/sources.
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


def _initial_state_with_decision() -> dict:
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
        "human_review_decisions": [
            {
                "review_id": "review_conflict_conf_001",
                "decision": "needs_more_evidence",
                "reviewer_id": "demo_reviewer",
                "notes": (
                    "Synthetic fixture conflict should remain unresolved; "
                    "request more evidence for demonstration."
                ),
                "modified_values": {},
            }
        ],
        "human_review_summary": None,
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
    sep = "=" * 72
    print(sep)
    print("This demo records a synthetic human review decision; it does NOT")
    print("resolve conflicts or modify records/conflicts/sources.")
    print(sep)

    graph = build_graph()
    result = graph.invoke(_initial_state_with_decision())

    print(sep)
    print("human_review_summary:")
    print(json.dumps(result.get("human_review_summary"), indent=2))

    print(sep)
    queue = result.get("human_review_queue") or []
    print(f"human_review_queue count: {len(queue)}")
    print("human_review_queue items:")
    for item in queue:
        print(
            f"  - {item.get('review_id')} | "
            f"item_type={item.get('item_type')} | "
            f"priority={item.get('priority')} | "
            f"status={item.get('status')} | "
            f"human_decision={item.get('human_decision')} | "
            f"decision_applied={item.get('decision_applied')} | "
            f"reviewer_id={item.get('reviewer_id')} | "
            f"notes={item.get('notes')}"
        )

    package = result.get("final_data_package") or {}
    print(sep)
    print("final_data_package.human_review_items:")
    for item in package.get("human_review_items") or []:
        print(
            f"  - {item.get('review_id')} | "
            f"status={item.get('status')} | "
            f"human_decision={item.get('human_decision')} | "
            f"decision_applied={item.get('decision_applied')}"
        )

    print(sep)
    print(f"current_route: {result.get('current_route')}")

    print(sep)
    print("finalization_summary:")
    print(json.dumps(result.get("finalization_summary"), indent=2))

    print(sep)
    print("final_data_package.package_metadata:")
    print(json.dumps(package.get("package_metadata"), indent=2))


if __name__ == "__main__":
    main()
