"""Run the controlled live masked-validation pilot for MV Hondius.

This script is safe by default: it refuses live HTTP collection unless
--allow-live-fetch is passed. It does not read .env, does not call external
LLMs, and does not perform broad web search. WHO DON600 is used only through a
manual ground-truth CSV after collection output is exported.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_SRC = _PROJECT_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from hdc_workflow.config import load_source_role_policy  # noqa: E402
from hdc_workflow.evaluation_report_builder import (  # noqa: E402
    build_evaluation_report,
    read_csv_records,
    write_csv_records,
    write_evaluation_outputs,
)
from hdc_workflow.export import export_final_data_package, write_json  # noqa: E402
from hdc_workflow.graph import build_graph  # noqa: E402
from hdc_workflow.nodes.source_discovery import canonicalize_url  # noqa: E402


_CASE_STUDY_ID = "mv_hondius_multicountry_2026"
_CASE_SOURCE_IDS = [
    "src_reuters_mv_hondius_2026_05_27",
    "src_vdh_hantavirus_mv_hondius_context",
    "src_who_don600_mv_hondius_2026",
]
_WHO_SOURCE_ID = "src_who_don600_mv_hondius_2026"
_REUTERS_SOURCE_ID = "src_reuters_mv_hondius_2026_05_27"
_VDH_SOURCE_ID = "src_vdh_hantavirus_mv_hondius_context"
_RESOURCE_DIR = _SRC / "hdc_workflow" / "resources" / "live_case_studies"
_SEED_OVERLAY_PATH = _RESOURCE_DIR / "mv_hondius_seed_sources.json"
_ROLE_POLICY_OVERLAY_PATH = (
    _RESOURCE_DIR / "mv_hondius_source_role_policy_overlay.json"
)
_GROUND_TRUTH_PATH = _RESOURCE_DIR / "mv_hondius_ground_truth_records.csv"
_PROFESSOR_SUMMARY_PATH = (
    _PROJECT_ROOT
    / "outputs"
    / "professor_demo_package"
    / "stage3d_mv_hondius_guardrail_results_summary.json"
)
_ENV_KEYS = [
    "HDC_COLLECTION_MODE",
    "HDC_SEED_SOURCE_OVERLAY_PATH",
    "HDC_SOURCE_ROLE_POLICY_OVERLAY_PATH",
    "HDC_USE_FIXTURE_DOCUMENTS",
    "HDC_ENABLE_LIVE_FETCH",
    "HDC_ENABLE_LLM_EXTRACTION",
    "HDC_SOURCE_ID_ALLOWLIST",
    "HDC_FETCH_TIMEOUT_SECONDS",
]
_GROUND_TRUTH_FIELDNAMES = [
    "record_id",
    "linked_event_id",
    "disease",
    "virus_or_syndrome",
    "country",
    "geographic_scope",
    "subnational_location",
    "date_anchor",
    "date_anchor_field",
    "date_reported",
    "reporting_period",
    "statistical_count_type",
    "cases_unspecified",
    "cases_confirmed",
    "cases_probable",
    "deaths",
    "source_id",
    "source_url",
    "source_type",
    "evidence_quote",
    "supporting_chunk_id",
    "ground_truth_role",
    "curation_note",
]


def _initial_state() -> dict:
    return {
        "user_request": (
            "Controlled MV Hondius 2026 hantavirus masked validation pilot. "
            "Collect only allowlisted non-held-out sources and preserve "
            "provenance for comparison against manual WHO DON600 ground truth."
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
def _temporary_env(updates: dict[str, str]):
    original = {key: os.environ.get(key) for key in _ENV_KEYS}
    try:
        for key, value in updates.items():
            os.environ[key] = value
        yield
    finally:
        for key, value in original.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run controlled live masked-validation pilot for MV Hondius."
    )
    parser.add_argument(
        "--allow-live-fetch",
        action="store_true",
        help="Explicitly allow live HTTP fetch for the controlled allowlist.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(_PROJECT_ROOT / "outputs" / "live_masked_validation_mv_hondius"),
        help="Output directory for collection, validation, evaluation, and diagnostics.",
    )
    parser.add_argument(
        "--preserve-allowlist",
        action="store_true",
        help="Merge any existing HDC_SOURCE_ID_ALLOWLIST values with the pilot allowlist.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the planned environment and paths without running the graph.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=20.0,
        help="HTTP fetch timeout passed through HDC_FETCH_TIMEOUT_SECONDS.",
    )
    return parser


def _console_text(value) -> str:
    return str(value).encode("ascii", errors="backslashreplace").decode("ascii")


def _parse_allowlist(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [part.strip() for part in raw.split(",") if part.strip()]


def _collection_allowlist(preserve_allowlist: bool) -> list[str]:
    ids = list(_CASE_SOURCE_IDS)
    if preserve_allowlist:
        for source_id in _parse_allowlist(os.environ.get("HDC_SOURCE_ID_ALLOWLIST")):
            if source_id not in ids:
                ids.append(source_id)
    return ids


def _collection_env(args: argparse.Namespace) -> dict[str, str]:
    allowlist = _collection_allowlist(args.preserve_allowlist)
    return {
        "HDC_COLLECTION_MODE": "masked_validation",
        "HDC_SEED_SOURCE_OVERLAY_PATH": str(_SEED_OVERLAY_PATH),
        "HDC_SOURCE_ROLE_POLICY_OVERLAY_PATH": str(_ROLE_POLICY_OVERLAY_PATH),
        "HDC_USE_FIXTURE_DOCUMENTS": "false",
        "HDC_ENABLE_LIVE_FETCH": "true",
        "HDC_ENABLE_LLM_EXTRACTION": "false",
        "HDC_SOURCE_ID_ALLOWLIST": ",".join(allowlist),
        "HDC_FETCH_TIMEOUT_SECONDS": str(args.timeout_seconds),
    }


def _run_plan(args: argparse.Namespace) -> dict:
    env_updates = _collection_env(args)
    if not args.allow_live_fetch:
        env_updates["HDC_ENABLE_LIVE_FETCH"] = "false"
    return {
        "live_case_study_id": _CASE_STUDY_ID,
        "dry_run": bool(args.dry_run),
        "allow_live_fetch": bool(args.allow_live_fetch),
        "output_dir": str(Path(args.output_dir)),
        "seed_source_overlay_path": str(_SEED_OVERLAY_PATH),
        "source_role_policy_overlay_path": str(_ROLE_POLICY_OVERLAY_PATH),
        "manual_ground_truth_csv": str(_GROUND_TRUTH_PATH),
        "collection_allowlist": _collection_allowlist(args.preserve_allowlist),
        "environment_updates": env_updates,
        "llm_enabled": False,
        "broad_web_search_used": False,
        "validation_ground_truth_mode": "manual_curated_csv",
    }


def _read_seed_overlay() -> dict:
    with _SEED_OVERLAY_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def _source_id_from_seed_id(seed_source_id: str) -> str:
    if seed_source_id.startswith("seed_"):
        return "src_" + seed_source_id[len("seed_"):]
    return seed_source_id


def _fallback_registry_from_seed(source_id: str) -> dict | None:
    for seed in _read_seed_overlay().get("seed_sources") or []:
        seed_source_id = seed.get("seed_source_id") or ""
        if _source_id_from_seed_id(seed_source_id) != source_id:
            continue
        url = seed.get("url") or ""
        return {
            "source_id": source_id,
            "canonical_url": canonicalize_url(url),
            "title": seed.get("title"),
            "publisher": seed.get("publisher"),
            "source_type": seed.get("source_type"),
            "status": "validation_ground_truth_manual",
            "seed_source_id": seed_source_id,
            "priority": seed.get("priority"),
            "expected_fields": list(seed.get("expected_fields") or []),
            "matched_terms": list(seed.get("match_terms") or []),
            "source_purpose": seed.get("source_purpose"),
            "notes": seed.get("notes"),
            "source_role": "validation_reserved",
            "final_screening_decision": "reserved_for_validation",
            "ready_for_content_fetch": False,
            "routing_flags": ["validation_reserved", "blocked_from_collection"],
        }
    return None


def _write_validation_outputs(
    collection_registry: list[dict],
    validation_records: list[dict],
    output_dir: Path,
) -> list[dict]:
    validation_dir = output_dir / "validation"
    write_csv_records(
        validation_dir / "ground_truth_records.csv",
        validation_records,
        _GROUND_TRUTH_FIELDNAMES,
    )

    validation_source_ids = {
        record.get("source_id") for record in validation_records if record.get("source_id")
    }
    registry = [
        entry
        for entry in collection_registry
        if entry.get("source_id") in validation_source_ids
    ]
    existing_ids = {entry.get("source_id") for entry in registry}
    for source_id in sorted(validation_source_ids - existing_ids):
        fallback = _fallback_registry_from_seed(source_id)
        if fallback is not None:
            registry.append(fallback)
    write_json(registry, validation_dir / "validation_source_registry.json")
    return registry


def _source_ids(records: list[dict]) -> list[str]:
    return sorted({str(r.get("source_id")) for r in records if r.get("source_id")})


def _count_by_source(records: list[dict]) -> dict[str, int]:
    return dict(Counter(r.get("source_id") or "unknown" for r in records))


def _live_fetch_summary(result: dict) -> dict:
    documents = list(result.get("documents") or [])
    fetch_requests = list(result.get("content_fetch_requests") or [])
    fetch_summary = result.get("content_fetch_summary") or {}
    quality_summary = result.get("document_quality_summary") or {}
    document_rows = []
    for doc in documents:
        text = doc.get("clean_text") or ""
        document_rows.append(
            {
                "source_id": doc.get("source_id"),
                "url": doc.get("url"),
                "fetch_status": doc.get("fetch_status"),
                "fetch_error": doc.get("fetch_error"),
                "http_status_code": doc.get("http_status_code"),
                "content_type": doc.get("content_type"),
                "parse_status": doc.get("parse_status"),
                "quality_status": doc.get("quality_status"),
                "quality_issues": list(doc.get("quality_issues") or []),
                "clean_text_char_count": len(text),
                "is_live_fetched": bool(doc.get("is_live_fetched")),
            }
        )
    usable_fetched_source_ids = sorted(
        {
            doc.get("source_id")
            for doc in documents
            if doc.get("fetch_status") == "fetched"
            and doc.get("quality_status") in {"usable", "partial"}
            and (
                doc.get("http_status_code") is None
                or int(doc.get("http_status_code")) < 400
            )
        }
    )
    access_or_quality_limited_source_ids = sorted(
        {
            doc.get("source_id")
            for doc in documents
            if doc.get("fetch_status") == "fetch_failed"
            or doc.get("quality_status") in {"unusable", "parse_deferred"}
            or (
                doc.get("http_status_code") is not None
                and int(doc.get("http_status_code")) >= 400
            )
        }
    )
    reuters_docs = [
        doc for doc in documents if doc.get("source_id") == _REUTERS_SOURCE_ID
    ]
    reuters_access_or_quality_limited = any(
        doc.get("fetch_status") == "fetch_failed"
        or doc.get("quality_status") == "unusable"
        or (
            doc.get("http_status_code") is not None
            and int(doc.get("http_status_code")) >= 400
        )
        for doc in reuters_docs
    )
    content_fetch_summary = result.get("content_fetch_summary") or {}
    context_only_source_ids = content_fetch_summary.get("context_only_source_ids") or []
    context_only_sources_fetched = sorted(
        source_id
        for source_id in _source_ids(documents)
        if source_id in set(context_only_source_ids)
    )
    return {
        "live_fetch_enabled": True,
        "fixture_documents_enabled": False,
        "fetch_request_source_ids": _source_ids(fetch_requests),
        "document_source_ids": _source_ids(documents),
        "successfully_fetched_source_ids": sorted(
            {
                doc.get("source_id")
                for doc in documents
                if doc.get("fetch_status") in {"fetched", "fetched_pdf_parse_deferred"}
            }
        ),
        "usable_fetched_source_ids": usable_fetched_source_ids,
        "access_or_quality_limited_source_ids": access_or_quality_limited_source_ids,
        "reuters_access_or_quality_limited": reuters_access_or_quality_limited,
        "context_only_source_ids": context_only_source_ids,
        "context_only_sources_fetched": context_only_sources_fetched,
        "fetch_failed_source_ids": sorted(
            {
                doc.get("source_id")
                for doc in documents
                if doc.get("fetch_status") == "fetch_failed"
            }
        ),
        "fetch_status_counts": fetch_summary.get("fetch_status_counts") or {},
        "document_type_counts": fetch_summary.get("document_type_counts") or {},
        "quality_status_counts": quality_summary.get("quality_status_counts") or {},
        "skipped_validation_reserved_source_ids": (
            fetch_summary.get("skipped_validation_reserved_source_ids") or []
        ),
        "skipped_not_in_allowlist_count": fetch_summary.get(
            "skipped_not_in_allowlist_count", 0
        ),
        "source_id_allowlist": fetch_summary.get("source_id_allowlist") or [],
        "documents": document_rows,
    }


def _source_leakage_check(
    collection_records: list[dict],
    collection_registry: list[dict],
    role_policy: dict,
    fetch_summary: dict,
) -> dict:
    reserved_source_ids = set(role_policy.get("validation_reserved_source_ids") or [])
    collection_source_ids = set(_source_ids(collection_records))
    leaked_source_ids = sorted(collection_source_ids & reserved_source_ids)
    registry_by_id = {entry.get("source_id"): entry for entry in collection_registry}
    who_entry = registry_by_id.get(_WHO_SOURCE_ID) or {}
    who_blocked = (
        who_entry.get("source_role") == "validation_reserved"
        and who_entry.get("final_screening_decision") == "reserved_for_validation"
        and who_entry.get("ready_for_content_fetch") is False
    )
    skipped_validation_reserved = (
        fetch_summary.get("skipped_validation_reserved_source_ids") or []
    )
    return {
        "live_case_study_id": _CASE_STUDY_ID,
        "reserved_source_ids": sorted(reserved_source_ids),
        "collection_record_source_ids": sorted(collection_source_ids),
        "reserved_source_leakage_count": len(leaked_source_ids),
        "reserved_source_leakage_source_ids": leaked_source_ids,
        "who_source_id": _WHO_SOURCE_ID,
        "who_in_source_registry": bool(who_entry),
        "who_source_registry_status": who_entry.get("status"),
        "who_source_role": who_entry.get("source_role"),
        "who_final_screening_decision": who_entry.get("final_screening_decision"),
        "who_ready_for_content_fetch": who_entry.get("ready_for_content_fetch"),
        "who_blocked_from_collection": bool(who_blocked),
        "skipped_validation_reserved_source_ids": skipped_validation_reserved,
        "who_listed_as_skipped_validation_reserved": (
            _WHO_SOURCE_ID in skipped_validation_reserved
        ),
        "technical_masking_status": (
            "passed" if not leaked_source_ids and who_blocked else "failed_or_incomplete"
        ),
    }


def _collection_diagnostics(
    result: dict,
    collection_package: dict,
    role_policy: dict,
    allowlist: list[str],
) -> dict:
    context_only_source_ids = set(role_policy.get("context_only_source_ids") or [])
    collection_records = collection_package.get("final_dataset") or []
    context_only_records = [
        record
        for record in collection_records
        if record.get("source_id") in context_only_source_ids
    ]
    return {
        "live_case_study_id": _CASE_STUDY_ID,
        "collection_allowlist": list(allowlist),
        "role_policy_overlay_path": str(_ROLE_POLICY_OVERLAY_PATH),
        "seed_source_overlay_path": str(_SEED_OVERLAY_PATH),
        "collection_mode": "masked_validation",
        "live_fetch_enabled": True,
        "fixture_documents_enabled": False,
        "llm_enabled": False,
        "broad_web_search_used": False,
        "source_discovery_summary": result.get("source_discovery_summary"),
        "source_registry_summary": result.get("source_registry_summary"),
        "source_screening_summary": result.get("source_screening_summary"),
        "source_routing_summary": result.get("source_routing_summary"),
        "content_fetch_summary": result.get("content_fetch_summary"),
        "document_quality_summary": result.get("document_quality_summary"),
        "evidence_chunking_summary": result.get("evidence_chunking_summary"),
        "data_presence_summary": result.get("data_presence_summary"),
        "structured_extraction_summary": result.get("structured_extraction_summary"),
        "schema_validation_summary": result.get("schema_validation_summary"),
        "normalization_summary": result.get("normalization_summary"),
        "record_linking_summary": result.get("record_linking_summary"),
        "human_review_summary": result.get("human_review_summary"),
        "finalization_summary": result.get("finalization_summary"),
        "package_metadata": collection_package.get("package_metadata") or {},
        "validation_reserved_source_ids": sorted(
            role_policy.get("validation_reserved_source_ids") or []
        ),
        "context_only_source_ids": sorted(context_only_source_ids),
        "context_only_sources_fetched": list(
            (result.get("content_fetch_summary") or {}).get(
                "context_only_fetched_source_ids"
            )
            or []
        ),
        "context_only_guardrail_active": True,
        "context_only_record_count": len(context_only_records),
        "context_only_records_detected": bool(context_only_records),
        "context_only_record_leakage_status": (
            "passed" if not context_only_records else "failed_context_only_records_detected"
        ),
        "semantic_leakage_flags": role_policy.get("semantic_leakage_flags") or {},
        "record_counts_by_phase": {
            "raw_records": len(result.get("raw_records") or []),
            "validated_records": len(result.get("validated_records") or []),
            "normalized_records": len(result.get("normalized_records") or []),
            "final_dataset": len(collection_package.get("final_dataset") or []),
        },
        "final_dataset_source_counts": _count_by_source(
            collection_package.get("final_dataset") or []
        ),
    }


def _format_counts(counts: dict | None) -> str:
    if not counts:
        return "none"
    return ", ".join(f"{key}={value}" for key, value in sorted(counts.items()))


def _write_extraction_diagnostics(
    path: Path,
    diagnostics: dict,
    live_summary: dict,
    leakage_check: dict,
) -> None:
    records_by_source = diagnostics.get("final_dataset_source_counts") or {}
    data_presence_summary = diagnostics.get("data_presence_summary") or {}
    extraction_summary = diagnostics.get("structured_extraction_summary") or {}
    collection_count = diagnostics.get("record_counts_by_phase", {}).get(
        "final_dataset", 0
    )
    lines = [
        "# MV Hondius Live Extraction Diagnostics",
        "",
        "This diagnostic file summarizes a controlled live pilot. It is not a broad web-search benchmark and does not claim real-world epidemiological validation success.",
        "",
        "## Fetch",
        "",
        f"- Fetch request source IDs: {', '.join(live_summary.get('fetch_request_source_ids') or []) or 'none'}",
        f"- Document source IDs: {', '.join(live_summary.get('document_source_ids') or []) or 'none'}",
        f"- Usable fetched source IDs: {', '.join(live_summary.get('usable_fetched_source_ids') or []) or 'none'}",
        f"- Access/quality-limited source IDs: {', '.join(live_summary.get('access_or_quality_limited_source_ids') or []) or 'none'}",
        f"- Reuters access or quality limited: {live_summary.get('reuters_access_or_quality_limited')}",
        f"- Context-only source IDs: {', '.join(diagnostics.get('context_only_source_ids') or []) or 'none'}",
        f"- Context-only sources fetched: {', '.join(live_summary.get('context_only_sources_fetched') or []) or 'none'}",
        f"- Fetch status counts: {_format_counts(live_summary.get('fetch_status_counts'))}",
        f"- Quality status counts: {_format_counts(live_summary.get('quality_status_counts'))}",
        f"- Skipped validation-reserved source IDs: {', '.join(live_summary.get('skipped_validation_reserved_source_ids') or []) or 'none'}",
        "",
        "## Extraction",
        "",
        f"- Evidence chunk count: {(diagnostics.get('evidence_chunking_summary') or {}).get('total_chunk_count', 0)}",
        f"- Raw record count: {diagnostics.get('record_counts_by_phase', {}).get('raw_records', 0)}",
        f"- Validated record count: {diagnostics.get('record_counts_by_phase', {}).get('validated_records', 0)}",
        f"- Normalized record count: {diagnostics.get('record_counts_by_phase', {}).get('normalized_records', 0)}",
        f"- Final collection record count: {collection_count}",
        f"- Final dataset source counts: {_format_counts(records_by_source)}",
        f"- Reuters produced extractable records: {records_by_source.get(_REUTERS_SOURCE_ID, 0) > 0}",
        f"- VDH produced records: {records_by_source.get(_VDH_SOURCE_ID, 0) > 0}",
        f"- Context-only guardrail active: {diagnostics.get('context_only_guardrail_active')}",
        f"- Context-only record count: {diagnostics.get('context_only_record_count', 0)}",
        f"- Context-only target-data suppressed count: {data_presence_summary.get('context_only_target_data_suppressed_count', 0)}",
        f"- Structured extraction skipped context-only chunks: {extraction_summary.get('skipped_context_only_chunk_count', 0)}",
        "",
        "## Masking",
        "",
        f"- WHO blocked from collection: {leakage_check.get('who_blocked_from_collection')}",
        f"- Reserved source leakage count: {leakage_check.get('reserved_source_leakage_count', 0)}",
        f"- Technical masking status: {leakage_check.get('technical_masking_status')}",
        "",
        "## Interpretation",
        "",
    ]
    if collection_count == 0:
        lines.append(
            "- Collection produced zero final records. Treat this as a first live deterministic extraction limitation, not a masking failure."
        )
    else:
        lines.append(
            "- Collection produced final records; compare them conservatively against manual WHO ground truth and inspect provenance before interpretation."
        )
    lines.extend(
        [
            "- Reuters has high semantic leakage risk because it cites WHO.",
            "- VDH is configured as context-only in the case policy overlay and should not produce structured collection records after the Stage 3D guardrail.",
            "- No LLM extraction was used.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_semantic_leakage_assessment(path: Path, leakage_check: dict) -> None:
    lines = [
        "# MV Hondius Semantic Leakage Assessment",
        "",
        "## Summary",
        "",
        "Reuters is collection-allowed, but it explicitly cites WHO. Therefore this pilot demonstrates technical source masking, not independent epidemiological validation.",
        "",
        "## Technical Masking",
        "",
        f"- WHO source ID: {_WHO_SOURCE_ID}",
        f"- WHO blocked from collection: {leakage_check.get('who_blocked_from_collection')}",
        f"- Reserved source leakage count: {leakage_check.get('reserved_source_leakage_count', 0)}",
        "",
        "## Semantic Risk",
        "",
        "- Reuters semantic leakage risk: high; it may restate WHO information.",
        "- VDH semantic leakage risk: medium; it may point readers to WHO for latest counts.",
        "- Manual WHO ground truth is used only after collection export.",
        "",
        "## Reporting Constraint",
        "",
        "Do not report this run as real-world epidemiological validation success. Report it as a controlled source-masking pilot with disclosed semantic leakage risk.",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_live_professor_report(
    path: Path,
    rows: list[dict],
    summary: dict,
    leakage_check: dict,
) -> None:
    lines = [
        "# MV Hondius Live Masked Validation Pilot Report",
        "",
        "This is a controlled live source-masking pilot. It is not a broad web-search benchmark and does not claim real-world epidemiological validation success.",
        "",
        "## Run Summary",
        "",
        f"- Live case study ID: {summary.get('live_case_study_id')}",
        f"- Collection record count: {summary.get('collection_record_count', 0)}",
        f"- Validation ground truth record count: {summary.get('validation_record_count', 0)}",
        f"- Evaluation row count: {summary.get('evaluation_row_count', 0)}",
        f"- Overall match status counts: {_format_counts(summary.get('overall_match_status_counts'))}",
        f"- Masking compliance status counts: {_format_counts(summary.get('masking_compliance_status_counts'))}",
        f"- Human review flagged row count: {summary.get('human_review_flagged_row_count', 0)}",
        "",
        "## Source Masking",
        "",
        f"- WHO blocked from collection: {leakage_check.get('who_blocked_from_collection')}",
        f"- Reserved source leakage count: {leakage_check.get('reserved_source_leakage_count', 0)}",
        f"- Validation ground truth mode: {summary.get('validation_ground_truth_mode')}",
        "",
        "## Evaluation Rows",
        "",
    ]
    if not rows:
        lines.append("- None")
    for row in rows[:10]:
        lines.append(
            "- "
            f"{row.get('evaluation_row_id')}: "
            f"status={row.get('overall_match_status')}; "
            f"collection_cases={row.get('collection_case_count') or 'none'}; "
            f"validation_cases={row.get('validation_case_count') or 'none'}; "
            f"human_review={row.get('human_review_flag')}"
        )
    if len(rows) > 10:
        lines.append(f"- ... {len(rows) - 10} additional rows omitted")
    lines.extend(
        [
            "",
            "## Context-Only Guardrail",
            "",
            "VDH is configured as context-only. After Stage 3D, it may be fetched for context grounding but should not produce structured collection records.",
            "",
            "## Semantic Leakage Warning",
            "",
            "Reuters cites WHO, so any match or mismatch must be interpreted as source-masked comparison with semantic leakage risk, not independent validation.",
            "",
            "## Limitations",
            "",
            "- WHO ground truth is manually curated, not automatically scraped.",
            "- Live pages may change.",
            "- Deterministic extraction may under-extract from live HTML.",
            "- Count differences may reflect different reporting dates.",
            "- Broad web search and PDF/OCR are not implemented.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_professor_summary(
    result: dict,
    output_dir: Path,
    live_summary: dict,
    leakage_check: dict,
    evaluation_outputs: dict,
) -> None:
    summary = result["evaluation_summary"]
    final_dataset = result["collection_package"].get("final_dataset") or []
    professor_summary = {
        "stage": "Stage 3D",
        "live_case_study_id": _CASE_STUDY_ID,
        "context_only_guardrail_implemented": True,
        "vdh_context_only_source_id": _VDH_SOURCE_ID,
        "vdh_structured_record_count_after_guardrail": sum(
            1 for record in final_dataset if record.get("source_id") == _VDH_SOURCE_ID
        ),
        "reuters_access_or_quality_limited": live_summary.get(
            "reuters_access_or_quality_limited"
        ),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "output_dir": str(output_dir),
        "collection_record_count": summary.get("collection_record_count", 0),
        "validation_ground_truth_record_count": summary.get(
            "validation_record_count", 0
        ),
        "evaluation_row_count": summary.get("evaluation_row_count", 0),
        "overall_match_status_counts": summary.get("overall_match_status_counts") or {},
        "masking_compliance_status_counts": (
            summary.get("masking_compliance_status_counts") or {}
        ),
        "human_review_flagged_row_count": summary.get(
            "human_review_flagged_row_count", 0
        ),
        "technical_source_leakage_status": leakage_check.get(
            "technical_masking_status"
        ),
        "reserved_source_leakage_count": leakage_check.get(
            "reserved_source_leakage_count", 0
        ),
        "who_blocked_from_collection": leakage_check.get("who_blocked_from_collection"),
        "recommend_add_llm_now": False,
        "recommended_next_stage": (
            "Stage 3E - Review guarded MV Hondius output and decide whether "
            "to find another accessible MV Hondius collection source or switch "
            "to the New Mexico backup case."
        ),
        "semantic_leakage_risk": True,
        "semantic_leakage_notes": [
            "Reuters is collection-allowed but cites WHO.",
            "Use this as a technical source-masking pilot, not independent validation.",
        ],
        "live_fetch_summary": {
            "document_source_ids": live_summary.get("document_source_ids") or [],
            "successfully_fetched_source_ids": live_summary.get(
                "successfully_fetched_source_ids"
            )
            or [],
            "usable_fetched_source_ids": live_summary.get(
                "usable_fetched_source_ids"
            )
            or [],
            "access_or_quality_limited_source_ids": live_summary.get(
                "access_or_quality_limited_source_ids"
            )
            or [],
            "reuters_access_or_quality_limited": live_summary.get(
                "reuters_access_or_quality_limited"
            ),
            "context_only_source_ids": live_summary.get("context_only_source_ids")
            or [],
            "context_only_sources_fetched": live_summary.get(
                "context_only_sources_fetched"
            )
            or [],
            "fetch_failed_source_ids": live_summary.get("fetch_failed_source_ids") or [],
            "fetch_status_counts": live_summary.get("fetch_status_counts") or {},
            "quality_status_counts": live_summary.get("quality_status_counts") or {},
        },
        "artifact_paths": {
            "collection_final_package": str(
                output_dir / "collection" / "final_package.json"
            ),
            "validation_ground_truth": str(
                output_dir / "validation" / "ground_truth_records.csv"
            ),
            "evaluation_report_csv": evaluation_outputs.get("evaluation_report_csv"),
            "evaluation_summary_json": evaluation_outputs.get(
                "evaluation_summary_json"
            ),
            "professor_demo_report_md": evaluation_outputs.get(
                "professor_demo_report_md"
            ),
        },
    }
    write_json(professor_summary, _PROFESSOR_SUMMARY_PATH)


def run_pilot(args: argparse.Namespace) -> dict:
    output_dir = Path(args.output_dir)
    allowlist = _collection_allowlist(args.preserve_allowlist)
    env_updates = _collection_env(args)

    with _temporary_env(env_updates):
        role_policy = load_source_role_policy()
        graph = build_graph()
        collection_result = graph.invoke(_initial_state())

    collection_package = collection_result.get("final_data_package") or {}
    collection_dir = output_dir / "collection"
    collection_manifest = export_final_data_package(collection_package, collection_dir)

    validation_records = read_csv_records(_GROUND_TRUTH_PATH)
    validation_registry = _write_validation_outputs(
        collection_package.get("source_registry") or [],
        validation_records,
        output_dir,
    )

    reserved_source_ids = set(role_policy.get("validation_reserved_source_ids") or [])
    evaluation_rows, evaluation_summary = build_evaluation_report(
        collection_records=collection_package.get("final_dataset") or [],
        validation_records=validation_records,
        collection_source_registry=collection_package.get("source_registry") or [],
        reserved_source_ids=reserved_source_ids,
        conflicts=collection_package.get("conflicts") or [],
        human_review_items=collection_package.get("human_review_items") or [],
    )

    live_summary = _live_fetch_summary(collection_result)
    leakage_check = _source_leakage_check(
        collection_package.get("final_dataset") or [],
        collection_package.get("source_registry") or [],
        role_policy,
        live_summary,
    )
    diagnostics = _collection_diagnostics(
        collection_result, collection_package, role_policy, allowlist
    )

    evaluation_summary.update(
        {
            "live_case_study_id": _CASE_STUDY_ID,
            "collection_mode": "masked_validation",
            "validation_ground_truth_mode": "manual_curated_csv",
            "live_fetch_enabled": True,
            "fixture_documents_enabled": False,
            "llm_enabled": False,
            "broad_web_search_used": False,
            "semantic_leakage_risk": True,
            "semantic_leakage_notes": [
                "Reuters is collection-allowed but explicitly cites WHO.",
                "This run demonstrates technical source masking, not independent epidemiological validation.",
            ],
            "collection_allowlist": list(allowlist),
            "validation_reserved_source_ids": sorted(reserved_source_ids),
            "collection_export_manifest": collection_manifest,
            "validation_source_registry_count": len(validation_registry),
            "source_leakage_check": leakage_check,
            "context_only_guardrail_implemented": True,
            "context_only_source_ids": diagnostics.get("context_only_source_ids") or [],
            "context_only_record_count": diagnostics.get(
                "context_only_record_count", 0
            ),
            "context_only_record_leakage_status": diagnostics.get(
                "context_only_record_leakage_status"
            ),
            "pilot_limitations": [
                "Controlled explicit-allowlist pilot only.",
                "WHO ground truth is manually curated, not automatically scraped.",
                "Reuters has high semantic leakage risk because it cites WHO.",
                "Live pages may change after the run.",
                "Deterministic extraction may under-extract live HTML.",
                "Count differences may reflect different reporting dates.",
                "Broad web search is not implemented.",
                "PDF/OCR is not implemented.",
                "No external LLM is used.",
            ],
        }
    )

    evaluation_outputs = write_evaluation_outputs(
        evaluation_rows,
        evaluation_summary,
        output_dir / "evaluation",
    )
    _write_live_professor_report(
        Path(evaluation_outputs["professor_demo_report_md"]),
        evaluation_rows,
        evaluation_summary,
        leakage_check,
    )

    diagnostics_dir = output_dir / "diagnostics"
    write_json(diagnostics, diagnostics_dir / "collection_diagnostics.json")
    write_json(leakage_check, diagnostics_dir / "source_leakage_check.json")
    write_json(live_summary, diagnostics_dir / "live_fetch_summary.json")
    _write_extraction_diagnostics(
        diagnostics_dir / "extraction_diagnostics.md",
        diagnostics,
        live_summary,
        leakage_check,
    )
    _write_semantic_leakage_assessment(
        diagnostics_dir / "semantic_leakage_assessment.md",
        leakage_check,
    )

    result = {
        "output_dir": str(output_dir),
        "collection_result": collection_result,
        "collection_package": collection_package,
        "validation_records": validation_records,
        "validation_registry": validation_registry,
        "evaluation_rows": evaluation_rows,
        "evaluation_summary": evaluation_summary,
        "collection_manifest": collection_manifest,
        "evaluation_outputs": evaluation_outputs,
        "live_fetch_summary": live_summary,
        "source_leakage_check": leakage_check,
    }
    _write_professor_summary(
        result,
        output_dir,
        live_summary,
        leakage_check,
        evaluation_outputs,
    )
    return result


def _print_completed_summary(result: dict) -> None:
    summary = result["evaluation_summary"]
    live_summary = result["live_fetch_summary"]
    leakage = result["source_leakage_check"]
    evaluation_report = Path(result["evaluation_outputs"]["evaluation_report_csv"])
    print("=" * 72)
    print("MV Hondius live masked-validation pilot completed.")
    print(f"output_dir: {_console_text(result['output_dir'])}")
    print(f"collection_record_count: {summary.get('collection_record_count', 0)}")
    print(
        "validation_ground_truth_record_count:",
        summary.get("validation_record_count", 0),
    )
    print(f"evaluation_row_count: {summary.get('evaluation_row_count', 0)}")
    print(
        "reserved_source_leakage_count:",
        leakage.get("reserved_source_leakage_count", 0),
    )
    print(
        "context_only_record_count:",
        summary.get("context_only_record_count", 0),
    )
    print("semantic_leakage_risk: true")
    print(
        "fetched_source_ids:",
        ",".join(live_summary.get("document_source_ids") or []) or "none",
    )
    print(
        "skipped_validation_reserved_source_ids:",
        ",".join(live_summary.get("skipped_validation_reserved_source_ids") or [])
        or "none",
    )
    print(f"evaluation_report_csv_exists: {evaluation_report.exists()}")
    print("=" * 72)


def main() -> int:
    args = _build_parser().parse_args()
    if args.timeout_seconds <= 0:
        print("--timeout-seconds must be positive.", file=sys.stderr)
        return 2

    if args.dry_run:
        print(json.dumps(_run_plan(args), indent=2, sort_keys=True))
        if not args.allow_live_fetch:
            print(
                "Dry run only. Pass --allow-live-fetch to run controlled live collection."
            )
        return 0

    if not args.allow_live_fetch:
        print(
            "Live fetch is disabled by default. Pass --allow-live-fetch to run "
            "the controlled MV Hondius allowlist pilot, or use --dry-run to inspect "
            "the planned environment without network access.",
            file=sys.stderr,
        )
        return 2

    result = run_pilot(args)
    _print_completed_summary(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
