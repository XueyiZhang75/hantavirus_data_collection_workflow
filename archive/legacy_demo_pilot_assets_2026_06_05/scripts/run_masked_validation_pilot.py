"""Run a deterministic offline masked-validation pilot.

The script runs two fixture workflows:
1. masked collection, where reserved sources are blocked from collection;
2. standard validation, where fixture records from reserved sources are treated
   as held-out ground truth for pilot comparison.

It does not read .env, does not call live fetch, and does not call any LLM.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from contextlib import contextmanager
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_SRC = _PROJECT_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from hdc_workflow.config import load_source_role_policy  # noqa: E402
from hdc_workflow.evaluation_report_builder import (  # noqa: E402
    build_evaluation_report,
    write_csv_records,
    write_evaluation_outputs,
)
from hdc_workflow.export import export_final_data_package, write_json  # noqa: E402
from hdc_workflow.graph import build_graph  # noqa: E402


_ENV_KEYS = [
    "HDC_COLLECTION_MODE",
    "HDC_USE_FIXTURE_DOCUMENTS",
    "HDC_ENABLE_LIVE_FETCH",
    "HDC_ENABLE_LLM_EXTRACTION",
    "HDC_SOURCE_ID_ALLOWLIST",
]


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


@contextmanager
def _temporary_env(updates: dict[str, str], unset: list[str] | None = None):
    original = {key: os.environ.get(key) for key in _ENV_KEYS}
    try:
        for key, value in updates.items():
            os.environ[key] = value
        for key in unset or []:
            os.environ.pop(key, None)
        yield
    finally:
        for key, value in original.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def _run_workflow(collection_mode: str, preserve_allowlist: bool) -> dict:
    unset = [] if preserve_allowlist else ["HDC_SOURCE_ID_ALLOWLIST"]
    with _temporary_env(
        {
            "HDC_COLLECTION_MODE": collection_mode,
            "HDC_USE_FIXTURE_DOCUMENTS": "true",
            "HDC_ENABLE_LIVE_FETCH": "false",
            "HDC_ENABLE_LLM_EXTRACTION": "false",
        },
        unset=unset,
    ):
        graph = build_graph()
        return graph.invoke(_initial_state())


def _resolve_output_dir(args) -> Path:
    if args.output_dir:
        return Path(args.output_dir)
    env_value = os.environ.get("HDC_MASKED_VALIDATION_OUTPUT_DIR")
    if env_value:
        return Path(env_value)
    return _PROJECT_ROOT / "outputs" / "masked_validation_pilot"


def _filter_records_by_source(records: list[dict], source_ids: set[str]) -> list[dict]:
    return [record for record in records if record.get("source_id") in source_ids]


def _filter_registry_by_source(registry: list[dict], source_ids: set[str]) -> list[dict]:
    return [entry for entry in registry if entry.get("source_id") in source_ids]


def run_pilot(output_dir: Path, preserve_allowlist: bool = False) -> dict:
    role_policy = load_source_role_policy()
    reserved_source_ids = set(role_policy.get("validation_reserved_source_ids") or [])

    collection_result = _run_workflow("masked_validation", preserve_allowlist)
    collection_package = collection_result.get("final_data_package") or {}
    collection_dir = output_dir / "collection"
    collection_manifest = export_final_data_package(collection_package, collection_dir)

    validation_result = _run_workflow("standard", preserve_allowlist)
    validation_package = validation_result.get("final_data_package") or {}
    validation_records = _filter_records_by_source(
        validation_package.get("final_dataset") or [],
        reserved_source_ids,
    )
    validation_registry = _filter_registry_by_source(
        validation_package.get("source_registry") or [],
        reserved_source_ids,
    )

    validation_dir = output_dir / "validation"
    write_csv_records(validation_dir / "ground_truth_records.csv", validation_records)
    write_json(validation_registry, validation_dir / "validation_source_registry.json")

    evaluation_rows, evaluation_summary = build_evaluation_report(
        collection_records=collection_package.get("final_dataset") or [],
        validation_records=validation_records,
        collection_source_registry=collection_package.get("source_registry") or [],
        reserved_source_ids=reserved_source_ids,
        conflicts=collection_package.get("conflicts") or [],
        human_review_items=collection_package.get("human_review_items") or [],
    )
    evaluation_summary.update(
        {
            "collection_mode": "masked_validation",
            "validation_mode": "standard",
            "live_fetch_enabled": False,
            "llm_enabled": False,
            "collection_export_manifest": collection_manifest,
            "validation_source_registry_count": len(validation_registry),
        }
    )
    evaluation_outputs = write_evaluation_outputs(
        evaluation_rows,
        evaluation_summary,
        output_dir / "evaluation",
    )

    return {
        "output_dir": str(output_dir),
        "collection_package": collection_package,
        "validation_records": validation_records,
        "validation_registry": validation_registry,
        "evaluation_rows": evaluation_rows,
        "evaluation_summary": evaluation_summary,
        "collection_manifest": collection_manifest,
        "evaluation_outputs": evaluation_outputs,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run deterministic offline masked-validation pilot."
    )
    parser.add_argument(
        "--output-dir",
        help="Output directory. Defaults to HDC_MASKED_VALIDATION_OUTPUT_DIR or outputs/masked_validation_pilot.",
    )
    parser.add_argument(
        "--preserve-allowlist",
        action="store_true",
        help="Do not unset HDC_SOURCE_ID_ALLOWLIST during pilot phases.",
    )
    return parser


def _console_text(value) -> str:
    return str(value).encode("ascii", errors="backslashreplace").decode("ascii")


def main() -> None:
    args = _build_parser().parse_args()
    output_dir = _resolve_output_dir(args)
    result = run_pilot(output_dir, preserve_allowlist=args.preserve_allowlist)

    summary = result["evaluation_summary"]
    print("=" * 72)
    print("Masked validation pilot completed.")
    print(f"output_dir: {_console_text(result['output_dir'])}")
    print(f"collection_record_count: {summary.get('collection_record_count', 0)}")
    print(f"validation_ground_truth_record_count: {summary.get('validation_record_count', 0)}")
    print(f"evaluation_row_count: {summary.get('evaluation_row_count', 0)}")
    print(
        "masking_compliance_status_counts:",
        json.dumps(summary.get("masking_compliance_status_counts") or {}, sort_keys=True),
    )
    print(
        "human_review_flagged_row_count:",
        summary.get("human_review_flagged_row_count", 0),
    )
    print("=" * 72)


if __name__ == "__main__":
    main()
