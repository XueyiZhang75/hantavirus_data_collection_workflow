"""Run the controlled live masked-validation pilot for New Mexico HPS.

This script is safe by default: it refuses live HTTP collection unless
--allow-live-fetch is passed. It does not read .env, does not call external
LLMs, and does not perform broad web search. The NMDOH county/year source is
used only through a manual ground-truth CSV after collection output is
exported.
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


_CASE_STUDY_ID = "new_mexico_hps_2024_2026"
_COLLECTION_SOURCE_IDS = [
    "src_nmdoh_hps_2024_first_case",
    "src_nmdoh_hps_2025_first_case_death",
    "src_nmdoh_hps_2026_first_case_prior_year_summary",
]
_CONTEXT_SOURCE_IDS = [
    "src_nmdoh_hps_overview_1975_2025",
    "src_cdc_hantavirus_reported_cases_through_2023",
]
_VALIDATION_SOURCE_ID = "src_nmdoh_hps_cases_by_county_1975_2025_pdf"
_CASE_SOURCE_IDS = [
    *_COLLECTION_SOURCE_IDS,
    *_CONTEXT_SOURCE_IDS,
    _VALIDATION_SOURCE_ID,
]
_RESOURCE_DIR = _SRC / "hdc_workflow" / "resources" / "live_case_studies"
_SEED_OVERLAY_PATH = _RESOURCE_DIR / "new_mexico_hps_seed_sources.json"
_ROLE_POLICY_OVERLAY_PATH = (
    _RESOURCE_DIR / "new_mexico_hps_source_role_policy_overlay.json"
)
_GROUND_TRUTH_PATH = _RESOURCE_DIR / "new_mexico_hps_ground_truth_records.csv"
_LLM_DEMO_DIR = _PROJECT_ROOT / "outputs" / "agentic_llm_source_demo" / "new_mexico_hps"
_PROFESSOR_RESULTS_PATH = (
    _PROJECT_ROOT
    / "outputs"
    / "professor_demo_package"
    / "stage4c_new_mexico_hps_live_results_summary.json"
)
_ENV_KEYS = [
    "HDC_COLLECTION_MODE",
    "HDC_SEED_SOURCE_OVERLAY_PATH",
    "HDC_SOURCE_ROLE_POLICY_OVERLAY_PATH",
    "HDC_USE_FIXTURE_DOCUMENTS",
    "HDC_ENABLE_LIVE_FETCH",
    "HDC_ENABLE_LLM_EXTRACTION",
    "HDC_ENABLE_LLM_SOURCE_PLANNING",
    "HDC_ENABLE_LLM_SOURCE_CRITIC",
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
            "Controlled New Mexico HPS 2024-2026 real-source masked "
            "validation pilot. Collect only allowlisted NMDOH HTML press "
            "releases, reserve the NMDOH county/year source for manual "
            "validation, and keep context-only sources out of structured "
            "record extraction."
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
        "human_review_decisions": [],
        "collection_trace": [],
        "collection_spec": None,
        "disease_profile": None,
        "collection_schema": None,
        "source_strategy": None,
        "screening_criteria": None,
        "search_queries": None,
        "search_query_inventory": [],
        "agentic_source_plan": None,
        "source_planning_agent_summary": None,
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
        description="Run controlled live masked-validation pilot for New Mexico HPS."
    )
    parser.add_argument(
        "--allow-live-fetch",
        action="store_true",
        help="Explicitly allow live HTTP fetch for the controlled allowlist.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the planned environment and paths without running the graph.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(
            _PROJECT_ROOT / "outputs" / "live_masked_validation_new_mexico_hps"
        ),
        help="Output directory for collection, validation, evaluation, and diagnostics.",
    )
    parser.add_argument(
        "--preserve-allowlist",
        action="store_true",
        help="Merge any existing HDC_SOURCE_ID_ALLOWLIST values with the pilot allowlist.",
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
        "HDC_ENABLE_LLM_SOURCE_PLANNING": "false",
        "HDC_ENABLE_LLM_SOURCE_CRITIC": "false",
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
        "stage4b4_llm_planning_reference_dir": str(_LLM_DEMO_DIR),
        "collection_allowlist": _collection_allowlist(args.preserve_allowlist),
        "environment_updates": env_updates,
        "llm_source_planning_enabled_for_live_run": False,
        "llm_source_critic_enabled_for_live_run": False,
        "llm_extraction_enabled": False,
        "broad_web_search_used": False,
        "validation_ground_truth_mode": "manual_curated_csv",
    }


def _read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _read_json_optional(path: Path):
    if not path.exists():
        return None
    return _read_json(path)


def _read_seed_overlay() -> dict:
    return _read_json(_SEED_OVERLAY_PATH)


def _read_role_overlay() -> dict:
    return _read_json(_ROLE_POLICY_OVERLAY_PATH)


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


def _safe_int(value) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


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
                _safe_int(doc.get("http_status_code")) is None
                or _safe_int(doc.get("http_status_code")) < 400
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
                _safe_int(doc.get("http_status_code")) is not None
                and _safe_int(doc.get("http_status_code")) >= 400
            )
        }
    )
    content_context_ids = fetch_summary.get("context_only_source_ids") or []
    context_only_sources_fetched = sorted(
        source_id
        for source_id in _source_ids(documents)
        if source_id in set(content_context_ids)
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
        "context_only_source_ids": content_context_ids,
        "context_only_sources_fetched": context_only_sources_fetched,
        "documents": document_rows,
    }


def _source_leakage_check(
    collection_records: list[dict],
    collection_registry: list[dict],
    fetch_summary: dict,
) -> dict:
    reserved_source_ids = set(_read_role_overlay().get("validation_reserved_source_ids") or [])
    collection_source_ids = set(_source_ids(collection_records))
    leaked_source_ids = sorted(collection_source_ids & reserved_source_ids)
    registry_by_id = {entry.get("source_id"): entry for entry in collection_registry}
    validation_entry = registry_by_id.get(_VALIDATION_SOURCE_ID) or {}
    validation_blocked = (
        validation_entry.get("source_role") == "validation_reserved"
        and validation_entry.get("final_screening_decision") == "reserved_for_validation"
        and validation_entry.get("ready_for_content_fetch") is False
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
        "validation_reserved_source_id": _VALIDATION_SOURCE_ID,
        "validation_reserved_source_present_in_registry": bool(validation_entry),
        "validation_reserved_source_registry_status": validation_entry.get("status"),
        "validation_reserved_source_role": validation_entry.get("source_role"),
        "validation_reserved_final_screening_decision": validation_entry.get(
            "final_screening_decision"
        ),
        "validation_reserved_ready_for_content_fetch": validation_entry.get(
            "ready_for_content_fetch"
        ),
        "validation_reserved_blocked_from_collection": bool(validation_blocked),
        "skipped_validation_reserved_source_ids": skipped_validation_reserved,
        "validation_reserved_listed_as_skipped_validation_reserved": (
            _VALIDATION_SOURCE_ID in skipped_validation_reserved
        ),
        "technical_masking_status": (
            "passed"
            if not leaked_source_ids and validation_blocked
            else "failed_or_incomplete"
        ),
    }


def _collection_diagnostics(
    result: dict,
    collection_package: dict,
    role_policy: dict,
    allowlist: list[str],
) -> dict:
    overlay = _read_role_overlay()
    context_only_source_ids = set(overlay.get("context_only_source_ids") or [])
    collection_records = collection_package.get("final_dataset") or []
    context_only_records = [
        record
        for record in collection_records
        if record.get("source_id") in context_only_source_ids
    ]
    registry = collection_package.get("source_registry") or []
    registry_source_ids = set(_source_ids(registry))
    return {
        "live_case_study_id": _CASE_STUDY_ID,
        "collection_allowlist": list(allowlist),
        "role_policy_overlay_path": str(_ROLE_POLICY_OVERLAY_PATH),
        "seed_source_overlay_path": str(_SEED_OVERLAY_PATH),
        "collection_mode": "masked_validation",
        "live_fetch_enabled": True,
        "fixture_documents_enabled": False,
        "llm_source_planning_enabled_for_live_run": False,
        "llm_source_critic_enabled_for_live_run": False,
        "llm_extraction_enabled": False,
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
            overlay.get("validation_reserved_source_ids") or []
        ),
        "context_only_source_ids": sorted(context_only_source_ids),
        "context_only_sources_fetched": list(
            (result.get("content_fetch_summary") or {}).get(
                "context_only_fetched_source_ids"
            )
            or []
        ),
        "case_source_ids_present_in_registry": sorted(
            source_id for source_id in _CASE_SOURCE_IDS if source_id in registry_source_ids
        ),
        "case_source_ids_missing_from_registry": sorted(
            source_id for source_id in _CASE_SOURCE_IDS if source_id not in registry_source_ids
        ),
        "context_only_guardrail_active": True,
        "context_only_record_count": len(context_only_records),
        "context_only_records_detected": bool(context_only_records),
        "context_only_record_leakage_status": (
            "passed" if not context_only_records else "failed_context_only_records_detected"
        ),
        "record_counts_by_phase": {
            "raw_records": len(result.get("raw_records") or []),
            "validated_records": len(result.get("validated_records") or []),
            "normalized_records": len(result.get("normalized_records") or []),
            "final_dataset": len(collection_records),
        },
        "final_dataset_source_counts": _count_by_source(collection_records),
    }


def _format_counts(counts: dict | None) -> str:
    if not counts:
        return "none"
    return ", ".join(f"{key}={value}" for key, value in sorted(counts.items()))


def _write_text(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


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
        "# New Mexico HPS Live Extraction Diagnostics",
        "",
        "This diagnostic file summarizes a controlled live pilot. It is not a broad web-search benchmark and does not claim full epidemiological validation success.",
        "",
        "## Fetch",
        "",
        f"- Fetch request source IDs: {', '.join(live_summary.get('fetch_request_source_ids') or []) or 'none'}",
        f"- Document source IDs: {', '.join(live_summary.get('document_source_ids') or []) or 'none'}",
        f"- Usable fetched source IDs: {', '.join(live_summary.get('usable_fetched_source_ids') or []) or 'none'}",
        f"- Access/quality-limited source IDs: {', '.join(live_summary.get('access_or_quality_limited_source_ids') or []) or 'none'}",
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
        f"- Context-only record count: {diagnostics.get('context_only_record_count', 0)}",
        f"- Context-only target-data suppressed count: {data_presence_summary.get('context_only_target_data_suppressed_count', 0)}",
        f"- Structured extraction skipped context-only chunks: {extraction_summary.get('skipped_context_only_chunk_count', 0)}",
        "",
        "## Masking",
        "",
        f"- Validation-reserved source blocked from collection: {leakage_check.get('validation_reserved_blocked_from_collection')}",
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
            "- Collection produced final records; compare them conservatively against manual NMDOH ground truth and inspect provenance before interpretation."
        )
    lines.extend(
        [
            "- The NMDOH county/year validation source is manually curated and not fetched for collection.",
            "- Context-only sources should not produce structured records.",
            "- No LLM extraction, broad web search, or live source planning was used in this run.",
            "",
        ]
    )
    _write_text(path, lines)


def _write_source_role_audit(path: Path, diagnostics: dict, leakage_check: dict) -> None:
    lines = [
        "# New Mexico HPS Source Role Audit",
        "",
        "## Configured Roles",
        "",
        f"- Collection-allowed source IDs: {', '.join(_COLLECTION_SOURCE_IDS)}",
        f"- Context-only source IDs: {', '.join(_CONTEXT_SOURCE_IDS)}",
        f"- Validation-reserved source IDs: {_VALIDATION_SOURCE_ID}",
        "",
        "## Registry Coverage",
        "",
        f"- Case source IDs present in registry: {', '.join(diagnostics.get('case_source_ids_present_in_registry') or []) or 'none'}",
        f"- Case source IDs missing from registry: {', '.join(diagnostics.get('case_source_ids_missing_from_registry') or []) or 'none'}",
        "",
        "## Masking Check",
        "",
        f"- Validation source present in registry: {leakage_check.get('validation_reserved_source_present_in_registry')}",
        f"- Validation source ready_for_content_fetch: {leakage_check.get('validation_reserved_ready_for_content_fetch')}",
        f"- Validation source appeared in collection final_dataset: {bool(leakage_check.get('reserved_source_leakage_source_ids'))}",
        f"- Reserved source leakage count: {leakage_check.get('reserved_source_leakage_count', 0)}",
        f"- Technical masking status: {leakage_check.get('technical_masking_status')}",
        "",
        "## Context-Only Check",
        "",
        f"- Context-only record count: {diagnostics.get('context_only_record_count', 0)}",
        f"- Context-only record leakage status: {diagnostics.get('context_only_record_leakage_status')}",
        "",
    ]
    _write_text(path, lines)


def _agent_queries(plan: dict | None) -> list[str]:
    if not isinstance(plan, dict):
        return []
    queries = []
    for item in plan.get("proposed_search_queries") or []:
        query = item.get("query")
        if query:
            queries.append(str(query))
    return queries


def _write_llm_planning_reference(path: Path) -> dict:
    plan = _read_json_optional(_LLM_DEMO_DIR / "agentic_source_plan.json")
    planning_summary = _read_json_optional(
        _LLM_DEMO_DIR / "source_planning_agent_summary.json"
    )
    demo_summary = _read_json_optional(_LLM_DEMO_DIR / "agentic_demo_summary.json")
    stage_summary = _read_json_optional(
        _PROJECT_ROOT
        / "outputs"
        / "professor_demo_package"
        / "stage4b4_structured_source_planning_results_summary.json"
    )
    query_lines = [f"{idx}. `{query}`" for idx, query in enumerate(_agent_queries(plan), 1)]
    if not query_lines:
        query_lines = ["- No agent queries found in local Stage 4B.4 artifacts."]

    reference = {
        "stage4b4_artifacts_present": bool(plan and planning_summary),
        "scenario": (demo_summary or {}).get("scenario"),
        "provider": (demo_summary or {}).get("provider"),
        "model": (demo_summary or {}).get("model"),
        "source_planning_status": (planning_summary or {}).get("status"),
        "structured_output_mode": (planning_summary or {}).get(
            "structured_output_mode"
        ),
        "agent_query_count": (planning_summary or {}).get("agent_query_count"),
        "rule_based_query_count": (demo_summary or {})
        .get("guardrail_checks", {})
        .get("rule_based_query_count"),
        "source_critic_succeeded": bool((demo_summary or {}).get("source_critic_summary")),
        "llm_extraction_enabled_in_stage4b4": (demo_summary or {}).get(
            "llm_extraction_enabled"
        ),
        "live_fetch_enabled_in_stage4b4": (demo_summary or {}).get(
            "live_fetch_enabled"
        ),
        "recommended_next_stage": (stage_summary or {}).get("recommended_next_stage"),
    }
    lines = [
        "# New Mexico HPS LLM Planning Reference",
        "",
        "Stage 4C uses local Stage 4B.4 planning artifacts as source-set design input. The Stage 4C live run does not call an LLM.",
        "",
        "## Stage 4B.4 Summary",
        "",
        f"- Scenario: `{reference.get('scenario')}`",
        f"- Provider: `{reference.get('provider')}`",
        f"- Model: `{reference.get('model')}`",
        f"- Source Planning status: `{reference.get('source_planning_status')}`",
        f"- Structured output mode: `{reference.get('structured_output_mode')}`",
        f"- Agent query count: `{reference.get('agent_query_count')}`",
        f"- Rule-based query count: `{reference.get('rule_based_query_count')}`",
        f"- Source Critic succeeded: `{reference.get('source_critic_succeeded')}`",
        f"- Stage 4B.4 live fetch enabled: `{reference.get('live_fetch_enabled_in_stage4b4')}`",
        f"- Stage 4B.4 LLM extraction enabled: `{reference.get('llm_extraction_enabled_in_stage4b4')}`",
        "",
        "## Agent-Proposed Queries",
        "",
        *query_lines,
        "",
        "## Stage 4C Use",
        "",
        "- The New Mexico pilot uses explicit NMDOH and CDC sources derived from the Stage 4B.4 source categories and human review.",
        "- The live run disables LLM source planning, LLM source critic, and LLM extraction.",
        "- Broad search and crawling remain out of scope.",
        "",
    ]
    _write_text(path, lines)
    return reference


def _write_live_professor_report(
    path: Path,
    rows: list[dict],
    summary: dict,
    leakage_check: dict,
) -> None:
    lines = [
        "# New Mexico HPS Live Masked Validation Pilot Report",
        "",
        "This is a controlled real-source source-masking pilot. It is not a broad web-search benchmark and does not claim complete epidemiological validation success.",
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
        f"- Validation source blocked from collection: {leakage_check.get('validation_reserved_blocked_from_collection')}",
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
            "The NMDOH overview and CDC national page are configured as context-only. They may support grounding, but should not produce structured collection records.",
            "",
            "## Limitations",
            "",
            "- NMDOH county/year ground truth is manually curated, not automatically scraped.",
            "- Live pages may change.",
            "- Deterministic extraction may under-extract from live HTML.",
            "- Count differences may reflect different reporting dates or annual versus event-level semantics.",
            "- Broad web search, PDF/OCR, and LLM extraction are not implemented in this run.",
            "",
        ]
    )
    _write_text(path, lines)


def _write_professor_summary(
    result: dict,
    output_dir: Path,
    live_summary: dict,
    leakage_check: dict,
    diagnostics: dict,
    llm_reference: dict,
    evaluation_outputs: dict,
) -> None:
    summary = result["evaluation_summary"]
    final_dataset = result["collection_package"].get("final_dataset") or []
    professor_summary = {
        "stage": "Stage 4C",
        "live_case_study_id": _CASE_STUDY_ID,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "output_dir": str(output_dir),
        "allowlist_source_ids": list(_CASE_SOURCE_IDS),
        "collection_allowed_source_ids": list(_COLLECTION_SOURCE_IDS),
        "context_only_source_ids": list(_CONTEXT_SOURCE_IDS),
        "validation_reserved_source_ids": [_VALIDATION_SOURCE_ID],
        "ground_truth_mode": "manual_curated_csv",
        "live_fetch_enabled": True,
        "llm_source_planning_enabled_for_live_run": False,
        "llm_source_critic_enabled_for_live_run": False,
        "llm_extraction_enabled": False,
        "broad_web_search_used": False,
        "collection_record_count": summary.get("collection_record_count", 0),
        "collection_source_counts": _count_by_source(final_dataset),
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
        "validation_reserved_source_blocked_from_collection": leakage_check.get(
            "validation_reserved_blocked_from_collection"
        ),
        "context_only_record_count": diagnostics.get("context_only_record_count", 0),
        "context_only_record_leakage_status": diagnostics.get(
            "context_only_record_leakage_status"
        ),
        "stage4b4_llm_planning_reference": llm_reference,
        "recommend_add_llm_extraction_now": False,
        "recommended_next_stage": (
            "Stage 4D - review New Mexico live deterministic extraction results, "
            "then decide whether to add controlled LLM extraction or PDF/OCR."
        ),
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
            "fetch_failed_source_ids": live_summary.get("fetch_failed_source_ids") or [],
            "fetch_status_counts": live_summary.get("fetch_status_counts") or {},
            "quality_status_counts": live_summary.get("quality_status_counts") or {},
        },
        "artifact_paths": {
            "collection_final_package": str(
                output_dir / "collection" / "final_package.json"
            ),
            "collection_final_dataset": str(
                output_dir / "collection" / "final_dataset.csv"
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
            "source_leakage_check": str(
                output_dir / "diagnostics" / "source_leakage_check.json"
            ),
            "live_fetch_summary": str(
                output_dir / "diagnostics" / "live_fetch_summary.json"
            ),
            "extraction_diagnostics": str(
                output_dir / "diagnostics" / "extraction_diagnostics.md"
            ),
        },
    }
    write_json(professor_summary, _PROFESSOR_RESULTS_PATH)


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

    reserved_source_ids = set(_read_role_overlay().get("validation_reserved_source_ids") or [])
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
            "llm_source_planning_enabled_for_live_run": False,
            "llm_source_critic_enabled_for_live_run": False,
            "llm_extraction_enabled": False,
            "broad_web_search_used": False,
            "collection_allowlist": list(allowlist),
            "collection_allowed_source_ids": list(_COLLECTION_SOURCE_IDS),
            "context_only_source_ids": list(_CONTEXT_SOURCE_IDS),
            "validation_reserved_source_ids": sorted(reserved_source_ids),
            "collection_export_manifest": collection_manifest,
            "validation_source_registry_count": len(validation_registry),
            "source_leakage_check": leakage_check,
            "context_only_guardrail_implemented": True,
            "context_only_record_count": diagnostics.get(
                "context_only_record_count", 0
            ),
            "context_only_record_leakage_status": diagnostics.get(
                "context_only_record_leakage_status"
            ),
            "case_source_ids_present_in_registry": diagnostics.get(
                "case_source_ids_present_in_registry"
            )
            or [],
            "case_source_ids_missing_from_registry": diagnostics.get(
                "case_source_ids_missing_from_registry"
            )
            or [],
            "pilot_limitations": [
                "Controlled explicit-allowlist pilot only.",
                "NMDOH county/year ground truth is manually curated, not automatically scraped.",
                "Live pages may change after the run.",
                "Deterministic extraction may under-extract live HTML.",
                "Count differences may reflect different reporting dates or annual versus event-level semantics.",
                "Broad web search is not implemented.",
                "PDF/OCR is not implemented.",
                "No external LLM is used in the live run.",
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
    _write_source_role_audit(
        diagnostics_dir / "source_role_audit.md",
        diagnostics,
        leakage_check,
    )
    llm_reference = _write_llm_planning_reference(
        diagnostics_dir / "llm_planning_reference.md"
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
        diagnostics,
        llm_reference,
        evaluation_outputs,
    )
    return result


def _print_completed_summary(result: dict) -> None:
    summary = result["evaluation_summary"]
    live_summary = result["live_fetch_summary"]
    leakage = result["source_leakage_check"]
    evaluation_report = Path(result["evaluation_outputs"]["evaluation_report_csv"])
    print("=" * 72)
    print("New Mexico HPS live masked-validation pilot completed.")
    print(f"output_dir: {_console_text(result['output_dir'])}")
    print(f"live_fetch_enabled: {summary.get('live_fetch_enabled')}")
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
        "fetched_source_ids:",
        ",".join(live_summary.get("document_source_ids") or []) or "none",
    )
    print(
        "access_or_quality_limited_source_ids:",
        ",".join(live_summary.get("access_or_quality_limited_source_ids") or [])
        or "none",
    )
    print(
        "human_review_flagged_row_count:",
        summary.get("human_review_flagged_row_count", 0),
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
            "the controlled New Mexico HPS allowlist pilot, or use --dry-run "
            "to inspect the planned environment without network access.",
            file=sys.stderr,
        )
        return 2

    result = run_pilot(args)
    _print_completed_summary(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
