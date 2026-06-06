"""Export the fixture-mode final data package to local JSON + CSV files.

Sets HDC_USE_FIXTURE_DOCUMENTS=true and HDC_ENABLE_LIVE_FETCH=false BEFORE
importing the graph so the workflow runs deterministically on synthetic
local fixtures. Writes export artifacts under outputs/fixture_final_package/.

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

from hdc_workflow.export import export_final_data_package  # noqa: E402
from hdc_workflow.graph import build_graph  # noqa: E402


def _initial_state() -> dict:
    return {
        "user_request": (
            "Collect global human hantavirus case, outbreak, and surveillance data "
            "from 2020 to 2026, including cases, deaths, dates, locations, source URLs, "
            "source types, and evidence quotes."
        ),
        "source_candidates": [],
        "source_registry": [],
        "documents": [],
        "evidence_chunks": [],
        "raw_records": [],
        "validated_records": [],
        "normalized_records": [],
        "linked_events": [],
        "conflicts": [],
        "human_review_queue": [],
        "human_review_decisions": [],
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
    print("Fixture mode uses synthetic local documents; these are NOT real public")
    print("health data. Exporting deterministic offline output for inspection.")
    print(sep)

    graph = build_graph()
    result = graph.invoke(_initial_state())
    package = result.get("final_data_package") or {}

    output_dir = _PROJECT_ROOT / "outputs" / "fixture_final_package"
    manifest = export_final_data_package(package, output_dir)

    print("final_dataset count:", len(package.get("final_dataset") or []))
    print("linked_events count:", len(package.get("linked_events") or []))
    print("conflicts count:", len(package.get("conflicts") or []))
    print("human_review_items count:", len(package.get("human_review_items") or []))
    print("contains_synthetic_fixture_data:", package.get("contains_synthetic_fixture_data"))
    print("synthetic_fixture_notice:", package.get("synthetic_fixture_notice"))

    print(sep)
    print("export manifest:")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
