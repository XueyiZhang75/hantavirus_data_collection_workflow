"""Deterministic export utilities for the final data package.

No LangGraph, no LLM, no network. Writes JSON and CSV artifacts under a
user-supplied output directory.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from .config import load_final_package_policy
from .models import FinalPackagePolicy


def ensure_output_dir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def write_json(data, path: str | Path) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return p


def write_csv_rows(
    rows: list[dict],
    path: str | Path,
    field_order: list[str] | None = None,
) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    ordered = list(field_order or [])

    if not rows:
        with p.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=ordered)
            writer.writeheader()
        return p

    extras: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        for key in row.keys():
            if key not in ordered:
                extras.add(key)
    fieldnames = ordered + sorted(extras)

    with p.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            if not isinstance(row, dict):
                continue
            cleaned: dict = {}
            for key in fieldnames:
                value = row.get(key)
                if value is None:
                    cleaned[key] = ""
                elif isinstance(value, (list, dict)):
                    cleaned[key] = json.dumps(value, ensure_ascii=False)
                else:
                    cleaned[key] = value
            writer.writerow(cleaned)
    return p


def export_final_data_package(
    package: dict,
    output_dir: str | Path,
) -> dict:
    """Write the final data package to JSON + CSV files. Returns a manifest."""

    policy = FinalPackagePolicy(**load_final_package_policy())
    out_dir = ensure_output_dir(output_dir)

    files: dict[str, str] = {}

    files["final_package_json"] = str(
        write_json(package, out_dir / "final_package.json")
    )
    files["final_dataset_json"] = str(
        write_json(package.get("final_dataset") or [], out_dir / "final_dataset.json")
    )
    files["final_dataset_csv"] = str(
        write_csv_rows(
            package.get("final_dataset") or [],
            out_dir / "final_dataset.csv",
            field_order=policy.final_dataset_field_order,
        )
    )
    files["final_dataset_pre_quality_gate_json"] = str(
        write_json(
            package.get("final_dataset_pre_quality_gate") or [],
            out_dir / "final_dataset_pre_quality_gate.json",
        )
    )
    files["final_dataset_pre_quality_gate_csv"] = str(
        write_csv_rows(
            package.get("final_dataset_pre_quality_gate") or [],
            out_dir / "final_dataset_pre_quality_gate.csv",
            field_order=policy.final_dataset_field_order,
        )
    )
    files["final_dataset_post_review_json"] = str(
        write_json(
            package.get("final_dataset_post_review") or [],
            out_dir / "final_dataset_post_review.json",
        )
    )
    files["final_dataset_post_review_csv"] = str(
        write_csv_rows(
            package.get("final_dataset_post_review") or [],
            out_dir / "final_dataset_post_review.csv",
            field_order=policy.final_dataset_field_order,
        )
    )
    files["quarantined_records_json"] = str(
        write_json(
            package.get("quarantined_records") or [],
            out_dir / "quarantined_records.json",
        )
    )
    files["quarantined_records_csv"] = str(
        write_csv_rows(
            package.get("quarantined_records") or [],
            out_dir / "quarantined_records.csv",
            field_order=policy.final_dataset_field_order,
        )
    )
    files["pending_review_records_json"] = str(
        write_json(
            package.get("pending_review_records") or [],
            out_dir / "pending_review_records.json",
        )
    )
    files["pending_review_records_csv"] = str(
        write_csv_rows(
            package.get("pending_review_records") or [],
            out_dir / "pending_review_records.csv",
            field_order=policy.final_dataset_field_order,
        )
    )
    files["record_inclusion_decisions_json"] = str(
        write_json(
            package.get("record_inclusion_decisions") or [],
            out_dir / "record_inclusion_decisions.json",
        )
    )
    files["records_excluded_by_human_review_json"] = str(
        write_json(
            package.get("records_excluded_by_human_review") or [],
            out_dir / "records_excluded_by_human_review.json",
        )
    )
    files["source_registry_json"] = str(
        write_json(package.get("source_registry") or [], out_dir / "source_registry.json")
    )
    files["linked_events_json"] = str(
        write_json(package.get("linked_events") or [], out_dir / "linked_events.json")
    )
    files["event_clusters_json"] = str(
        write_json(package.get("event_clusters") or [], out_dir / "event_clusters.json")
    )
    files["duplicate_clusters_json"] = str(
        write_json(
            package.get("duplicate_clusters") or [],
            out_dir / "duplicate_clusters.json",
        )
    )
    files["validation_cases_json"] = str(
        write_json(
            package.get("validation_cases") or [],
            out_dir / "validation_cases.json",
        )
    )
    files["validation_comparisons_json"] = str(
        write_json(
            package.get("validation_comparisons") or [],
            out_dir / "validation_comparisons.json",
        )
    )
    files["validation_results_json"] = str(
        write_json(
            package.get("validation_results") or [],
            out_dir / "validation_results.json",
        )
    )
    files["validation_results_csv"] = str(
        write_csv_rows(
            package.get("validation_results") or [],
            out_dir / "validation_results.csv",
        )
    )
    files["anomaly_results_json"] = str(
        write_json(
            package.get("anomaly_results") or [],
            out_dir / "anomaly_results.json",
        )
    )
    files["anomaly_results_csv"] = str(
        write_csv_rows(
            package.get("anomaly_results") or [],
            out_dir / "anomaly_results.csv",
        )
    )
    files["applied_human_review_decisions_json"] = str(
        write_json(
            package.get("applied_human_review_decisions") or [],
            out_dir / "applied_human_review_decisions.json",
        )
    )
    files["rejected_human_review_decisions_json"] = str(
        write_json(
            package.get("rejected_human_review_decisions") or [],
            out_dir / "rejected_human_review_decisions.json",
        )
    )
    files["human_review_audit_trail_json"] = str(
        write_json(
            package.get("human_review_audit_trail") or [],
            out_dir / "human_review_audit_trail.json",
        )
    )
    files["human_review_application_summary_json"] = str(
        write_json(
            package.get("human_review_application_summary") or {},
            out_dir / "human_review_application_summary.json",
        )
    )
    files["conflicts_json"] = str(
        write_json(package.get("conflicts") or [], out_dir / "conflicts.json")
    )
    files["human_review_items_json"] = str(
        write_json(
            package.get("human_review_items") or [],
            out_dir / "human_review_items.json",
        )
    )
    files["collection_trace_json"] = str(
        write_json(package.get("collection_trace") or [], out_dir / "collection_trace.json")
    )
    files["workflow_summaries_json"] = str(
        write_json(
            package.get("workflow_summaries") or {},
            out_dir / "workflow_summaries.json",
        )
    )
    files["package_metadata_json"] = str(
        write_json(
            package.get("package_metadata") or {},
            out_dir / "package_metadata.json",
        )
    )
    files["provenance_manifest_json"] = str(
        write_json(
            package.get("provenance_manifest") or {},
            out_dir / "provenance_manifest.json",
        )
    )

    manifest = {
        "output_dir": str(out_dir),
        "files": files,
        "section_counts": {
            "final_dataset": len(package.get("final_dataset") or []),
            "final_dataset_pre_quality_gate": len(
                package.get("final_dataset_pre_quality_gate") or []
            ),
            "final_dataset_post_review": len(
                package.get("final_dataset_post_review") or []
            ),
            "quarantined_records": len(package.get("quarantined_records") or []),
            "pending_review_records": len(package.get("pending_review_records") or []),
            "record_inclusion_decisions": len(
                package.get("record_inclusion_decisions") or []
            ),
            "run_quality_summary": 1 if package.get("run_quality_summary") else 0,
            "final_dataset_quality_summary": (
                1 if package.get("final_dataset_quality_summary") else 0
            ),
            "records_excluded_by_human_review": len(
                package.get("records_excluded_by_human_review") or []
            ),
            "source_registry": len(package.get("source_registry") or []),
            "linked_events": len(package.get("linked_events") or []),
            "event_clusters": len(package.get("event_clusters") or []),
            "duplicate_clusters": len(package.get("duplicate_clusters") or []),
            "validation_cases": len(package.get("validation_cases") or []),
            "validation_comparisons": len(package.get("validation_comparisons") or []),
            "validation_results": len(package.get("validation_results") or []),
            "anomaly_results": len(package.get("anomaly_results") or []),
            "applied_human_review_decisions": len(
                package.get("applied_human_review_decisions") or []
            ),
            "rejected_human_review_decisions": len(
                package.get("rejected_human_review_decisions") or []
            ),
            "human_review_audit_trail": len(
                package.get("human_review_audit_trail") or []
            ),
            "conflicts": len(package.get("conflicts") or []),
            "human_review_items": len(package.get("human_review_items") or []),
            "excluded_sources": len(package.get("excluded_sources") or []),
            "collection_trace": len(package.get("collection_trace") or []),
            "data_dictionary": len(package.get("data_dictionary") or []),
        },
    }
    return manifest
