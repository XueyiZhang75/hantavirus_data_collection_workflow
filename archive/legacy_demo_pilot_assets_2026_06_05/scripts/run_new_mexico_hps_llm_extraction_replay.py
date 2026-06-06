"""Controlled LLM extraction replay for New Mexico HPS Stage 4E.

This script never performs live fetch and never performs broad web search. It
replays LLM extraction only on locally stored Stage 4C collection-side evidence
quotes/chunks. Validation-reserved and context-only sources are excluded from
LLM extraction input.
"""

from __future__ import annotations

import argparse
import csv
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

from hdc_workflow import llm_clients  # noqa: E402
from hdc_workflow.evaluation_report_builder import (  # noqa: E402
    build_evaluation_report,
    read_csv_records,
    write_csv_records,
    write_evaluation_outputs,
)
from hdc_workflow.export import write_json  # noqa: E402
from hdc_workflow.nodes.extraction import (  # noqa: E402
    schema_validation_and_repair,
    structured_extraction,
)
from hdc_workflow.nodes.finalization import final_data_package_builder  # noqa: E402
from hdc_workflow.nodes.linking_validation import (  # noqa: E402
    cross_source_consistency_check,
    record_linking,
)
from hdc_workflow.nodes.normalization import record_normalization  # noqa: E402


_CASE_STUDY_ID = "new_mexico_hps_2024_2026"
_DEFAULT_INPUT_DIR = _PROJECT_ROOT / "outputs" / "live_masked_validation_new_mexico_hps"
_DEFAULT_OUTPUT_DIR = (
    _PROJECT_ROOT / "outputs" / "live_masked_validation_new_mexico_hps_llm_replay"
)
_PROFESSOR_RESULTS_PATH = (
    _PROJECT_ROOT
    / "outputs"
    / "professor_demo_package"
    / "stage4e_new_mexico_hps_llm_extraction_results_summary.json"
)
_STAGE4F_RESULTS_PATH = (
    _PROJECT_ROOT
    / "outputs"
    / "professor_demo_package"
    / "stage4f_annual_alignment_results_summary.json"
)
_ROLE_POLICY_OVERLAY_PATH = (
    _SRC
    / "hdc_workflow"
    / "resources"
    / "live_case_studies"
    / "new_mexico_hps_source_role_policy_overlay.json"
)
_COLLECTION_SOURCE_IDS = [
    "src_nmdoh_hps_2024_first_case",
    "src_nmdoh_hps_2025_first_case_death",
    "src_nmdoh_hps_2026_first_case_prior_year_summary",
]
_CONTEXT_SOURCE_IDS = {
    "src_nmdoh_hps_overview_1975_2025",
    "src_cdc_hantavirus_reported_cases_through_2023",
}
_VALIDATION_SOURCE_ID = "src_nmdoh_hps_cases_by_county_1975_2025_pdf"
_KEY_SOURCE_ID = "src_nmdoh_hps_2026_first_case_prior_year_summary"
_KEY_CHUNK_ID = "chunk_src_nmdoh_hps_2026_first_case_prior_year_summary_001"
_TARGET_PHRASES = [
    "seven cases",
    "7 cases",
    "three of them fatal",
    "three fatal",
    "3 deaths",
    "2025",
    "fatal",
    "cases in 2025",
]
_ENV_KEYS = [
    "HDC_ENABLE_LLM_EXTRACTION",
    "HDC_ENABLE_LIVE_FETCH",
    "HDC_ENABLE_LLM_SOURCE_PLANNING",
    "HDC_ENABLE_LLM_SOURCE_CRITIC",
    "HDC_COLLECTION_MODE",
    "HDC_LLM_PROVIDER",
    "HDC_LLM_MODEL",
    "HDC_LLM_MAX_CHUNKS",
    "HDC_LLM_FALLBACK_TO_RULE_BASED",
    "HDC_SOURCE_ROLE_POLICY_OVERLAY_PATH",
]
_CASE_FIELDS = (
    "cases_confirmed",
    "cases_unspecified",
    "cases_probable",
    "cases_suspected",
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Replay controlled LLM extraction on already-fetched New Mexico HPS "
            "collection evidence."
        )
    )
    parser.add_argument(
        "--allow-llm-extraction",
        action="store_true",
        help="Explicitly allow LLM extraction on selected local collection chunks.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned replay inputs and safety settings without calling an LLM.",
    )
    parser.add_argument(
        "--reevaluate-existing",
        action="store_true",
        help=(
            "Rebuild evaluation/comparison outputs from existing replay records "
            "without live fetch or LLM extraction."
        ),
    )
    parser.add_argument(
        "--output-dir",
        default=str(_DEFAULT_OUTPUT_DIR),
        help="Output directory for replay inputs, extraction, evaluation, and diagnostics.",
    )
    parser.add_argument(
        "--input-dir",
        default=str(_DEFAULT_INPUT_DIR),
        help="Stage 4C live pilot output directory to read local artifacts from.",
    )
    parser.add_argument(
        "--provider",
        default=None,
        help="Optional LLM provider override, e.g. anthropic.",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Optional LLM model override, e.g. claude-sonnet-4-6.",
    )
    parser.add_argument(
        "--max-chunks",
        type=int,
        default=10,
        help="Maximum selected chunks and HDC_LLM_MAX_CHUNKS cap.",
    )
    parser.add_argument(
        "--target-source-id",
        action="append",
        default=None,
        help="Restrict replay to one collection source ID; repeatable.",
    )
    return parser


def _console_text(value) -> str:
    return str(value).encode("ascii", errors="backslashreplace").decode("ascii")


def _read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _read_json_optional(path: Path):
    if not path.exists():
        return None
    return _read_json(path)


def _write_csv(path: Path, records: list[dict], fieldnames: list[str] | None = None) -> None:
    write_csv_records(path, records, fieldnames)


def _lower(text: str | None) -> str:
    return (text or "").lower()


def _contains_target_phrase(text: str | None) -> bool:
    lowered = _lower(text)
    return any(phrase.lower() in lowered for phrase in _TARGET_PHRASES)


def _api_key_present(provider: str | None) -> bool:
    provider_name = (provider or os.environ.get("HDC_LLM_PROVIDER") or "anthropic").lower()
    if provider_name == "anthropic":
        return bool(os.environ.get("ANTHROPIC_API_KEY"))
    if provider_name == "openai":
        return bool(os.environ.get("OPENAI_API_KEY"))
    return False


def _source_registry_by_id(input_dir: Path) -> dict[str, dict]:
    path = input_dir / "collection" / "source_registry.json"
    if not path.exists():
        return {}
    registry = _read_json(path)
    return {
        entry.get("source_id"): entry
        for entry in registry
        if isinstance(entry, dict) and entry.get("source_id")
    }


def _target_source_ids(raw: list[str] | None) -> list[str]:
    if raw:
        ids = []
        for source_id in raw:
            if source_id not in ids:
                ids.append(source_id)
        return ids
    return list(_COLLECTION_SOURCE_IDS)


def _chunk_sort_key(chunk: dict) -> tuple[int, str]:
    priority = 0 if chunk.get("chunk_id") == _KEY_CHUNK_ID else 1
    if chunk.get("source_id") != _KEY_SOURCE_ID:
        priority += 2
    return priority, str(chunk.get("chunk_id") or "")


def _chunk_from_record(record: dict, registry_entry: dict | None) -> dict:
    registry_entry = registry_entry or {}
    text = record.get("evidence_quote") or ""
    data_types = ["case_count", "date"]
    if "fatal" in _lower(text) or "death" in _lower(text):
        data_types.append("death_count")
    source_id = record.get("source_id") or ""
    return {
        "chunk_id": record.get("supporting_chunk_id") or f"replay_{source_id}",
        "source_id": source_id,
        "text": text,
        "section": "reconstructed_from_stage4c_final_dataset_evidence_quote",
        "contains_target_data": True,
        "data_types": data_types,
        "confidence": 0.75 if _contains_target_phrase(text) else 0.60,
        "document_type": "html",
        "fetch_purpose": "data_extraction",
        "source_url": record.get("source_url") or registry_entry.get("canonical_url"),
        "canonical_url": registry_entry.get("canonical_url") or record.get("source_url"),
        "title": registry_entry.get("title"),
        "publisher": registry_entry.get("publisher"),
        "source_type": record.get("source_type") or registry_entry.get("source_type"),
        "source_role": registry_entry.get("source_role") or "data_source",
        "quality_status": "usable",
        "chunk_index": None,
        "chunk_kind": "text",
        "context_types": [],
        "presence_reason": "Stage 4E replay input reconstructed from Stage 4C collection evidence_quote.",
        "replay_input_source": "stage4c_final_dataset_evidence_quote",
        "original_record_id": record.get("record_id"),
    }


def select_replay_chunks(
    input_dir: Path | str,
    target_source_ids: list[str] | None = None,
    max_chunks: int = 10,
) -> tuple[list[dict], dict]:
    """Select local collection-side replay chunks without network access."""

    input_path = Path(input_dir)
    target_ids = set(target_source_ids or _COLLECTION_SOURCE_IDS)
    registry = _source_registry_by_id(input_path)
    final_dataset_path = input_path / "collection" / "final_dataset.csv"
    final_package = _read_json_optional(input_path / "collection" / "final_package.json")
    final_package_has_documents = bool(
        isinstance(final_package, dict) and final_package.get("documents")
    )
    final_package_has_evidence_chunks = bool(
        isinstance(final_package, dict) and final_package.get("evidence_chunks")
    )

    candidates: list[dict] = []
    excluded_validation_ids: set[str] = set()
    excluded_context_ids: set[str] = set()
    excluded_not_target_ids: set[str] = set()
    seen_chunk_ids: set[str] = set()
    if final_dataset_path.exists():
        for row in read_csv_records(final_dataset_path):
            source_id = row.get("source_id") or ""
            entry = registry.get(source_id) or {}
            flags = set(entry.get("routing_flags") or [])
            is_validation = (
                source_id == _VALIDATION_SOURCE_ID
                or entry.get("source_role") == "validation_reserved"
                or "validation_reserved" in flags
            )
            is_context = (
                source_id in _CONTEXT_SOURCE_IDS
                or entry.get("source_role") in {"context_source", "context_only"}
                or "context_only" in flags
                or "blocked_from_structured_extraction" in flags
            )
            if is_validation:
                excluded_validation_ids.add(source_id)
                continue
            if is_context:
                excluded_context_ids.add(source_id)
                continue
            if source_id not in target_ids:
                excluded_not_target_ids.add(source_id)
                continue
            text = row.get("evidence_quote") or ""
            if not text.strip():
                continue
            chunk = _chunk_from_record(row, entry)
            chunk_id = chunk.get("chunk_id")
            if chunk_id in seen_chunk_ids:
                continue
            seen_chunk_ids.add(str(chunk_id))
            candidates.append(chunk)

    selected = sorted(candidates, key=_chunk_sort_key)[: max(0, int(max_chunks))]
    selected_source_ids = sorted({chunk.get("source_id") for chunk in selected if chunk.get("source_id")})
    selected_chunk_ids = [str(chunk.get("chunk_id")) for chunk in selected]
    target_phrase_present = any(_contains_target_phrase(chunk.get("text")) for chunk in selected)
    key_phrase_present = any(
        chunk.get("chunk_id") == _KEY_CHUNK_ID and _contains_target_phrase(chunk.get("text"))
        for chunk in selected
    )
    audit = {
        "input_dir": str(input_path),
        "selection_mode": "stage4c_final_dataset_evidence_quote_replay",
        "full_documents_available": final_package_has_documents,
        "full_evidence_chunks_available": final_package_has_evidence_chunks,
        "full_text_replay_limited": not final_package_has_evidence_chunks,
        "eligible_source_ids": sorted(target_ids),
        "excluded_validation_source_ids": sorted(excluded_validation_ids),
        "excluded_context_only_source_ids": sorted(excluded_context_ids),
        "excluded_not_target_source_ids": sorted(excluded_not_target_ids),
        "validation_reserved_sources_excluded": _VALIDATION_SOURCE_ID not in selected_source_ids,
        "context_only_sources_excluded": not (_CONTEXT_SOURCE_IDS & set(selected_source_ids)),
        "selected_chunk_count": len(selected),
        "selected_source_ids": selected_source_ids,
        "selected_chunk_ids": selected_chunk_ids,
        "target_phrase_present_in_selected_chunks": target_phrase_present,
        "key_chunk_selected": _KEY_CHUNK_ID in selected_chunk_ids,
        "key_chunk_target_phrase_present": key_phrase_present,
        "api_key_printed": False,
    }
    return selected, audit


@contextmanager
def _temporary_env(updates: dict[str, str | None]):
    original = {key: os.environ.get(key) for key in _ENV_KEYS}
    try:
        for key, value in updates.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        yield
    finally:
        for key, value in original.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def _env_updates(args: argparse.Namespace, allow_llm: bool) -> dict[str, str | None]:
    updates: dict[str, str | None] = {
        "HDC_ENABLE_LIVE_FETCH": "false",
        "HDC_ENABLE_LLM_EXTRACTION": "true" if allow_llm else "false",
        "HDC_ENABLE_LLM_SOURCE_PLANNING": "false",
        "HDC_ENABLE_LLM_SOURCE_CRITIC": "false",
        "HDC_COLLECTION_MODE": "masked_validation",
        "HDC_LLM_MAX_CHUNKS": str(args.max_chunks),
        "HDC_LLM_FALLBACK_TO_RULE_BASED": "false",
        "HDC_SOURCE_ROLE_POLICY_OVERLAY_PATH": str(_ROLE_POLICY_OVERLAY_PATH),
    }
    if getattr(args, "provider", None):
        updates["HDC_LLM_PROVIDER"] = args.provider
    if getattr(args, "model", None):
        updates["HDC_LLM_MODEL"] = args.model
    return updates


def _run_plan(args: argparse.Namespace) -> dict:
    target_ids = _target_source_ids(args.target_source_id)
    chunks, audit = select_replay_chunks(args.input_dir, target_ids, args.max_chunks)
    provider = args.provider or os.environ.get("HDC_LLM_PROVIDER") or "anthropic"
    model = args.model or os.environ.get("HDC_LLM_MODEL") or ""
    return {
        "stage": "Stage 4E",
        "dry_run": bool(args.dry_run),
        "allow_llm_extraction": bool(args.allow_llm_extraction),
        "input_dir": str(Path(args.input_dir)),
        "output_dir": str(Path(args.output_dir)),
        "provider": provider,
        "model": model,
        "api_key_present": _api_key_present(provider),
        "environment_updates": _env_updates(args, False),
        "eligible_source_ids": target_ids,
        "excluded_validation_reserved_source_id": _VALIDATION_SOURCE_ID,
        "excluded_context_only_source_ids": sorted(_CONTEXT_SOURCE_IDS),
        "selected_chunk_count": len(chunks),
        "selected_chunk_ids": audit.get("selected_chunk_ids") or [],
        "selected_source_ids": audit.get("selected_source_ids") or [],
        "target_phrase_present_in_selected_chunks": audit.get(
            "target_phrase_present_in_selected_chunks"
        ),
        "live_fetch_enabled": False,
        "broad_web_search_used": False,
        "validation_pdf_parsed": False,
    }


def _initial_replay_state(
    selected_chunks: list[dict],
    source_registry: list[dict],
) -> dict:
    return {
        "user_request": (
            "Stage 4E controlled LLM extraction replay on already-fetched New "
            "Mexico HPS collection evidence. No live fetch and no broad search."
        ),
        "source_candidates": [],
        "source_registry": source_registry,
        "documents": [],
        "evidence_chunks": selected_chunks,
        "raw_records": [],
        "validated_records": [],
        "normalized_records": [],
        "linked_events": [],
        "conflicts": [],
        "human_review_queue": [],
        "human_review_decisions": [],
        "collection_trace": [],
        "collection_spec": {
            "disease": "Hantavirus disease",
            "geography": "New Mexico, USA",
            "time_window": "2024-2026",
            "replay_mode": "llm_extraction_on_local_stage4c_evidence",
        },
        "disease_profile": None,
        "collection_schema": None,
        "source_strategy": None,
        "screening_criteria": None,
        "search_queries": None,
        "search_query_inventory": [],
        "content_fetch_requests": [],
        "content_fetch_summary": {
            "live_fetch_enabled": False,
            "replay_uses_local_stage4c_evidence": True,
        },
        "fixture_document_summary": None,
        "document_quality_summary": None,
        "final_data_package": None,
        "current_route": None,
    }


def _apply_node(state: dict, node_fn) -> None:
    updates = node_fn(state)
    state.update(updates)


def _has_numeric(record: dict, fields: tuple[str, ...]) -> bool:
    for field in fields:
        value = record.get(field)
        if value in (None, ""):
            continue
        try:
            float(value)
            return True
        except (TypeError, ValueError):
            continue
    return False


def _case_count(record: dict) -> float | None:
    for field in _CASE_FIELDS:
        value = record.get(field)
        if value in (None, ""):
            continue
        try:
            return float(value)
        except (TypeError, ValueError):
            continue
    return None


def _death_count(record: dict) -> float | None:
    value = record.get("deaths")
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _is_2025_annual_record(record: dict) -> bool:
    case_value = _case_count(record)
    return (
        str(record.get("source_id") or "") == _KEY_SOURCE_ID
        and str(record.get("virus_or_syndrome") or "").upper() == "HPS"
        and str(record.get("subnational_location") or "").lower() == "new mexico"
        and str(record.get("reporting_period") or record.get("date_anchor") or "") == "2025"
        and str(record.get("statistical_count_type") or "").lower() == "annual"
        and case_value == 7.0
    )


def _records_with_case_counts(records: list[dict]) -> int:
    return sum(1 for record in records if _has_numeric(record, _CASE_FIELDS))


def _records_with_death_counts(records: list[dict]) -> int:
    return sum(1 for record in records if _has_numeric(record, ("deaths",)))


def _comparison_summary(
    deterministic_records: list[dict],
    llm_records: list[dict],
    deterministic_eval_summary: dict,
    llm_eval_summary: dict,
) -> dict:
    llm_annual_records = [record for record in llm_records if _is_2025_annual_record(record)]
    llm_cases_7 = any(_case_count(record) == 7.0 for record in llm_annual_records)
    llm_deaths_3 = any(_death_count(record) == 3.0 for record in llm_annual_records)
    det_missing = int(
        (deterministic_eval_summary.get("overall_match_status_counts") or {}).get(
            "missing_collection_record", 0
        )
    )
    llm_missing = int(
        (llm_eval_summary.get("overall_match_status_counts") or {}).get(
            "missing_collection_record", 0
        )
    )
    return {
        "deterministic_collection_record_count": len(deterministic_records),
        "deterministic_records_with_case_counts": _records_with_case_counts(
            deterministic_records
        ),
        "deterministic_records_with_death_counts": _records_with_death_counts(
            deterministic_records
        ),
        "llm_replay_record_count": len(llm_records),
        "llm_records_with_case_counts": _records_with_case_counts(llm_records),
        "llm_records_with_death_counts": _records_with_death_counts(llm_records),
        "llm_extracted_2025_annual_cases_7": bool(llm_cases_7),
        "llm_extracted_2025_annual_deaths_3": bool(llm_deaths_3),
        "evaluation_improved_from_missing_collection_record": (
            llm_missing < det_missing or bool(llm_cases_7)
        ),
        "deterministic_overall_match_status_counts": (
            deterministic_eval_summary.get("overall_match_status_counts") or {}
        ),
        "llm_overall_match_status_counts": (
            llm_eval_summary.get("overall_match_status_counts") or {}
        ),
        "llm_masking_compliance_status_counts": (
            llm_eval_summary.get("masking_compliance_status_counts") or {}
        ),
        "provenance_fields_complete_for_llm_records": all(
            record.get("source_url")
            and record.get("evidence_quote")
            and record.get("supporting_chunk_id")
            for record in llm_records
        ),
    }


def _load_existing_final_package(output_dir: Path) -> dict:
    for path in (
        output_dir / "llm_extraction" / "final_package.json",
        output_dir / "final_package.json",
    ):
        package = _read_json_optional(path)
        if isinstance(package, dict):
            return package
    return {}


def _load_existing_llm_records(output_dir: Path, final_package: dict) -> list[dict]:
    normalized_path = output_dir / "llm_extraction" / "normalized_records.csv"
    if normalized_path.exists():
        return read_csv_records(normalized_path)
    return list(final_package.get("final_dataset") or [])


def _annual_alignment_row(evaluation_rows: list[dict]) -> dict | None:
    for row in evaluation_rows:
        if (
            row.get("reporting_period") == "2025"
            and str(row.get("statistical_count_type") or "").lower() == "annual"
            and _KEY_SOURCE_ID in str(row.get("collection_source_ids") or "")
            and _VALIDATION_SOURCE_ID in str(row.get("validation_source_ids") or "")
        ):
            return row
    return None


def _write_stage4f_results_summary(
    evaluation_summary: dict,
    comparison: dict,
    annual_row: dict | None,
) -> dict:
    summary = {
        "stage": "Stage 4F",
        "annual_alignment_rule_implemented": True,
        "llm_extraction_rerun": False,
        "live_fetch_rerun": False,
        "annual_collection_record_aligned_with_validation": annual_row is not None,
        "llm_extracted_2025_annual_cases_7": comparison.get(
            "llm_extracted_2025_annual_cases_7"
        ),
        "llm_extracted_2025_annual_deaths_3": comparison.get(
            "llm_extracted_2025_annual_deaths_3"
        ),
        "evaluation_row_count_after_alignment": evaluation_summary.get(
            "evaluation_row_count"
        ),
        "overall_match_status_counts_after_alignment": (
            evaluation_summary.get("overall_match_status_counts") or {}
        ),
        "rows_with_both_collection_and_validation_evidence_count": (
            evaluation_summary.get(
                "rows_with_both_collection_and_validation_evidence_count"
            )
        ),
        "reserved_source_leakage_count": evaluation_summary.get(
            "reserved_source_leakage_count"
        ),
        "human_review_flagged_row_count": evaluation_summary.get(
            "human_review_flagged_row_count"
        ),
        "annual_row_field_level_match_status": (
            annual_row.get("field_level_match_status") if annual_row else None
        ),
        "annual_row_overall_match_status": (
            annual_row.get("overall_match_status") if annual_row else None
        ),
        "recommended_next_stage": (
            "Stage 4G - Prepare professor meeting package with full Stage 0-4F narrative"
        ),
    }
    write_json(summary, _STAGE4F_RESULTS_PATH)
    return summary


def _write_selected_chunk_audit(path: Path, audit: dict, chunks: list[dict]) -> None:
    lines = [
        "# Stage 4E Selected Chunk Audit",
        "",
        f"- Input dir: `{audit.get('input_dir')}`",
        f"- Selection mode: `{audit.get('selection_mode')}`",
        f"- Full evidence chunks available: `{audit.get('full_evidence_chunks_available')}`",
        f"- Full text replay limited: `{audit.get('full_text_replay_limited')}`",
        f"- Selected chunk count: `{audit.get('selected_chunk_count')}`",
        f"- Selected source IDs: `{', '.join(audit.get('selected_source_ids') or []) or 'none'}`",
        f"- Validation-reserved sources excluded: `{audit.get('validation_reserved_sources_excluded')}`",
        f"- Context-only sources excluded: `{audit.get('context_only_sources_excluded')}`",
        f"- Target phrase present: `{audit.get('target_phrase_present_in_selected_chunks')}`",
        "",
        "## Chunks",
        "",
    ]
    for chunk in chunks:
        preview = " ".join((chunk.get("text") or "").split())[:240]
        lines.append(
            f"- `{chunk.get('chunk_id')}` / `{chunk.get('source_id')}`: {preview}"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_llm_diagnostics(path: Path, summary: dict, extraction_summary: dict) -> None:
    lines = [
        "# Stage 4E LLM Extraction Diagnostics",
        "",
        f"- Live fetch enabled: `{summary.get('live_fetch_enabled')}`",
        f"- Broad web search used: `{summary.get('broad_web_search_used')}`",
        f"- LLM extraction enabled: `{summary.get('llm_extraction_enabled')}`",
        f"- LLM call attempted: `{summary.get('llm_call_attempted')}`",
        f"- LLM call succeeded: `{summary.get('llm_call_succeeded')}`",
        f"- Extracted record count: `{summary.get('extracted_record_count')}`",
        f"- Extracted annual 2025 case record found: `{summary.get('extracted_annual_2025_case_record_found')}`",
        f"- Extraction errors: `{'; '.join(summary.get('extraction_errors') or []) or 'none'}`",
        "",
        "## Structured Extraction Summary",
        "",
        "```json",
        json.dumps(extraction_summary, ensure_ascii=False, indent=2),
        "```",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_comparison_report(path: Path, comparison: dict) -> None:
    lines = [
        "# Deterministic vs LLM Extraction Summary",
        "",
        f"- Deterministic collection records: `{comparison.get('deterministic_collection_record_count')}`",
        f"- Deterministic records with case counts: `{comparison.get('deterministic_records_with_case_counts')}`",
        f"- Deterministic records with death counts: `{comparison.get('deterministic_records_with_death_counts')}`",
        f"- LLM replay records: `{comparison.get('llm_replay_record_count')}`",
        f"- LLM records with case counts: `{comparison.get('llm_records_with_case_counts')}`",
        f"- LLM records with death counts: `{comparison.get('llm_records_with_death_counts')}`",
        f"- LLM extracted 2025 annual cases=7: `{comparison.get('llm_extracted_2025_annual_cases_7')}`",
        f"- LLM extracted 2025 annual deaths=3: `{comparison.get('llm_extracted_2025_annual_deaths_3')}`",
        f"- Evaluation improved from missing collection record: `{comparison.get('evaluation_improved_from_missing_collection_record')}`",
        f"- Provenance complete for LLM records: `{comparison.get('provenance_fields_complete_for_llm_records')}`",
        f"- Annual collection record aligned with validation: `{comparison.get('annual_collection_record_aligned_with_validation')}`",
        f"- Annual row field-level match status: `{comparison.get('annual_row_field_level_match_status') or 'not_applicable'}`",
        f"- Annual row overall match status: `{comparison.get('annual_row_overall_match_status') or 'not_applicable'}`",
        "",
        "## Interpretation",
        "",
        "This replay compares extraction behavior only. It does not rerun live fetch and does not change the held-out validation source.",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_professor_summary(
    output_dir: Path,
    replay_summary: dict,
    comparison: dict,
    evaluation_summary: dict,
    selected_audit: dict,
) -> None:
    summary = {
        "stage": "Stage 4E",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "output_dir": str(output_dir),
        "provider": replay_summary.get("provider"),
        "model": replay_summary.get("model"),
        "api_key_present": replay_summary.get("api_key_present"),
        "allow_llm_extraction_used": replay_summary.get("allow_llm_extraction_used"),
        "llm_call_attempted": replay_summary.get("llm_call_attempted"),
        "llm_call_succeeded": replay_summary.get("llm_call_succeeded"),
        "live_fetch_enabled": False,
        "broad_web_search_used": False,
        "validation_reserved_sources_excluded": selected_audit.get(
            "validation_reserved_sources_excluded"
        ),
        "context_only_sources_excluded": selected_audit.get(
            "context_only_sources_excluded"
        ),
        "selected_source_ids": selected_audit.get("selected_source_ids") or [],
        "selected_chunk_ids": selected_audit.get("selected_chunk_ids") or [],
        "target_phrase_present_in_selected_chunks": selected_audit.get(
            "target_phrase_present_in_selected_chunks"
        ),
        "raw_record_count": replay_summary.get("raw_record_count"),
        "validated_record_count": replay_summary.get("validated_record_count"),
        "normalized_record_count": replay_summary.get("normalized_record_count"),
        "extracted_annual_2025_case_record_found": replay_summary.get(
            "extracted_annual_2025_case_record_found"
        ),
        "llm_extracted_2025_annual_cases_7": comparison.get(
            "llm_extracted_2025_annual_cases_7"
        ),
        "llm_extracted_2025_annual_deaths_3": comparison.get(
            "llm_extracted_2025_annual_deaths_3"
        ),
        "evaluation_row_count": evaluation_summary.get("evaluation_row_count"),
        "overall_match_status_counts": evaluation_summary.get(
            "overall_match_status_counts"
        )
        or {},
        "masking_compliance_status_counts": evaluation_summary.get(
            "masking_compliance_status_counts"
        )
        or {},
        "evaluation_improved_from_stage4c": comparison.get(
            "evaluation_improved_from_missing_collection_record"
        ),
        "recommended_next_stage": _recommended_next_stage(replay_summary, comparison),
        "api_key_printed": False,
    }
    write_json(summary, _PROFESSOR_RESULTS_PATH)


def _recommended_next_stage(replay_summary: dict, comparison: dict) -> str:
    if not replay_summary.get("llm_call_succeeded"):
        return "Stage 4F - Improve LLM extraction prompt/schema if extraction failed"
    if comparison.get("llm_extracted_2025_annual_cases_7"):
        return "Stage 4F - Review LLM extraction output and prepare professor meeting package"
    return "Stage 4F - Improve LLM extraction prompt/schema if extraction failed"


def _deterministic_evaluation_summary(
    input_dir: Path,
    deterministic_records: list[dict],
    validation_records: list[dict],
) -> dict:
    existing = _read_json_optional(input_dir / "evaluation" / "evaluation_summary.json")
    if isinstance(existing, dict):
        return existing
    rows, summary = build_evaluation_report(
        collection_records=deterministic_records,
        validation_records=validation_records,
        reserved_source_ids={_VALIDATION_SOURCE_ID},
    )
    summary["evaluation_rows"] = rows
    return summary


def run_replay(args: argparse.Namespace) -> dict:
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    target_ids = _target_source_ids(args.target_source_id)
    selected_chunks, selected_audit = select_replay_chunks(
        input_dir, target_ids, args.max_chunks
    )
    source_registry_path = input_dir / "collection" / "source_registry.json"
    source_registry = _read_json(source_registry_path) if source_registry_path.exists() else []
    validation_records = read_csv_records(input_dir / "validation" / "ground_truth_records.csv")
    deterministic_records = read_csv_records(input_dir / "collection" / "final_dataset.csv")
    deterministic_eval_summary = _deterministic_evaluation_summary(
        input_dir, deterministic_records, validation_records
    )

    inputs_dir = output_dir / "inputs"
    extraction_dir = output_dir / "llm_extraction"
    diagnostics_dir = output_dir / "diagnostics"
    comparison_dir = output_dir / "comparison"
    write_json(selected_chunks, inputs_dir / "selected_chunks.json")
    _write_csv(
        inputs_dir / "selected_chunks.csv",
        selected_chunks,
        [
            "chunk_id",
            "source_id",
            "source_url",
            "source_type",
            "contains_target_data",
            "fetch_purpose",
            "chunk_kind",
            "text",
        ],
    )

    env_updates = _env_updates(args, True)
    state = _initial_replay_state(selected_chunks, source_registry)
    with _temporary_env(env_updates):
        _apply_node(state, structured_extraction)
        _apply_node(state, schema_validation_and_repair)
        _apply_node(state, record_normalization)
        _apply_node(state, record_linking)
        _apply_node(state, cross_source_consistency_check)
        _apply_node(state, final_data_package_builder)

    raw_records = list(state.get("raw_records") or [])
    validated_records = list(state.get("validated_records") or [])
    normalized_records = list(state.get("normalized_records") or [])
    final_package = state.get("final_data_package") or {}
    extraction_summary = state.get("structured_extraction_summary") or {}
    llm_summary = state.get("llm_extraction_summary") or {}

    write_json(raw_records, extraction_dir / "raw_records.json")
    _write_csv(extraction_dir / "validated_records.csv", validated_records)
    _write_csv(extraction_dir / "normalized_records.csv", normalized_records)
    write_json(final_package, extraction_dir / "final_package.json")

    evaluation_rows, evaluation_summary = build_evaluation_report(
        collection_records=normalized_records,
        validation_records=validation_records,
        collection_source_registry=source_registry,
        reserved_source_ids={_VALIDATION_SOURCE_ID},
        conflicts=final_package.get("conflicts") or [],
        human_review_items=final_package.get("human_review_items") or [],
    )
    evaluation_summary.update(
        {
            "stage": "Stage 4E",
            "live_case_study_id": _CASE_STUDY_ID,
            "replay_mode": "llm_extraction_on_local_stage4c_collection_evidence",
            "live_fetch_enabled": False,
            "broad_web_search_used": False,
            "validation_pdf_parsed": False,
            "llm_extraction_enabled": True,
            "selected_chunk_audit": selected_audit,
        }
    )
    evaluation_outputs = write_evaluation_outputs(
        evaluation_rows, evaluation_summary, output_dir / "evaluation"
    )

    comparison = _comparison_summary(
        deterministic_records,
        normalized_records,
        deterministic_eval_summary,
        evaluation_summary,
    )
    write_json(comparison, comparison_dir / "deterministic_vs_llm_summary.json")
    _write_comparison_report(
        comparison_dir / "deterministic_vs_llm_report.md",
        comparison,
    )

    llm_call_attempted = int(llm_summary.get("llm_call_count") or 0) > 0
    llm_call_succeeded = int(llm_summary.get("llm_success_count") or 0) > 0
    annual_found = any(_is_2025_annual_record(record) for record in normalized_records)
    replay_summary = {
        "stage": "Stage 4E",
        "live_case_study_id": _CASE_STUDY_ID,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "provider": args.provider or os.environ.get("HDC_LLM_PROVIDER") or "anthropic",
        "model": args.model or os.environ.get("HDC_LLM_MODEL") or "",
        "api_key_present": _api_key_present(args.provider),
        "allow_llm_extraction_used": bool(args.allow_llm_extraction),
        "live_fetch_enabled": False,
        "broad_web_search_used": False,
        "llm_extraction_enabled": True,
        "validation_reserved_sources_excluded": selected_audit.get(
            "validation_reserved_sources_excluded"
        ),
        "context_only_sources_excluded": selected_audit.get(
            "context_only_sources_excluded"
        ),
        "selected_chunk_count": selected_audit.get("selected_chunk_count"),
        "selected_source_ids": selected_audit.get("selected_source_ids") or [],
        "selected_chunk_ids": selected_audit.get("selected_chunk_ids") or [],
        "target_phrase_present_in_selected_chunks": selected_audit.get(
            "target_phrase_present_in_selected_chunks"
        ),
        "llm_call_attempted": llm_call_attempted,
        "llm_call_succeeded": llm_call_succeeded,
        "extracted_record_count": len(raw_records),
        "raw_record_count": len(raw_records),
        "validated_record_count": len(validated_records),
        "normalized_record_count": len(normalized_records),
        "extracted_annual_2025_case_record_found": annual_found,
        "extraction_errors": llm_summary.get("llm_error_messages") or [],
        "api_key_printed": False,
        "llm_summary": llm_summary,
        "structured_extraction_summary": extraction_summary,
    }
    source_safety = {
        "validation_reserved_sources_excluded": selected_audit.get(
            "validation_reserved_sources_excluded"
        ),
        "context_only_sources_excluded": selected_audit.get(
            "context_only_sources_excluded"
        ),
        "selected_source_ids": selected_audit.get("selected_source_ids") or [],
        "selected_chunk_ids": selected_audit.get("selected_chunk_ids") or [],
        "validation_reserved_source_id": _VALIDATION_SOURCE_ID,
        "context_only_source_ids": sorted(_CONTEXT_SOURCE_IDS),
        "live_fetch_enabled": False,
        "broad_web_search_used": False,
        "api_key_printed": False,
    }
    write_json(
        replay_summary,
        diagnostics_dir / "llm_extraction_replay_summary.json",
    )
    write_json(source_safety, diagnostics_dir / "source_role_safety_check.json")
    _write_selected_chunk_audit(
        diagnostics_dir / "selected_chunk_audit.md",
        selected_audit,
        selected_chunks,
    )
    _write_llm_diagnostics(
        diagnostics_dir / "llm_extraction_diagnostics.md",
        replay_summary,
        extraction_summary,
    )
    _write_professor_summary(
        output_dir, replay_summary, comparison, evaluation_summary, selected_audit
    )
    return {
        "output_dir": str(output_dir),
        "selected_chunks": selected_chunks,
        "selected_audit": selected_audit,
        "raw_records": raw_records,
        "validated_records": validated_records,
        "normalized_records": normalized_records,
        "evaluation_rows": evaluation_rows,
        "evaluation_summary": evaluation_summary,
        "evaluation_outputs": evaluation_outputs,
        "comparison_summary": comparison,
        "llm_extraction_replay_summary": replay_summary,
        "source_role_safety_check": source_safety,
    }


def reevaluate_existing(args: argparse.Namespace) -> dict:
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    source_registry_path = input_dir / "collection" / "source_registry.json"
    source_registry = _read_json(source_registry_path) if source_registry_path.exists() else []
    validation_records = read_csv_records(input_dir / "validation" / "ground_truth_records.csv")
    deterministic_records = read_csv_records(input_dir / "collection" / "final_dataset.csv")
    deterministic_eval_summary = _deterministic_evaluation_summary(
        input_dir, deterministic_records, validation_records
    )

    final_package = _load_existing_final_package(output_dir)
    llm_records = _load_existing_llm_records(output_dir, final_package)
    evaluation_rows, evaluation_summary = build_evaluation_report(
        collection_records=llm_records,
        validation_records=validation_records,
        collection_source_registry=source_registry,
        reserved_source_ids={_VALIDATION_SOURCE_ID},
        conflicts=final_package.get("conflicts") or [],
        human_review_items=final_package.get("human_review_items") or [],
    )
    previous_summary = _read_json_optional(
        output_dir / "evaluation" / "evaluation_summary.json"
    )
    evaluation_summary.update(
        {
            "stage": "Stage 4F",
            "live_case_study_id": _CASE_STUDY_ID,
            "replay_mode": "reevaluate_existing_llm_extraction_outputs",
            "annual_alignment_rule": (
                "annual records use reporting_period as evaluation comparison "
                "anchor when reporting_period is present"
            ),
            "live_fetch_enabled": False,
            "broad_web_search_used": False,
            "validation_pdf_parsed": False,
            "llm_extraction_enabled": False,
            "llm_extraction_rerun": False,
            "previous_evaluation_summary": previous_summary or {},
        }
    )
    evaluation_outputs = write_evaluation_outputs(
        evaluation_rows, evaluation_summary, output_dir / "evaluation"
    )

    comparison = _comparison_summary(
        deterministic_records,
        llm_records,
        deterministic_eval_summary,
        evaluation_summary,
    )
    annual_row = _annual_alignment_row(evaluation_rows)
    comparison.update(
        {
            "annual_collection_record_aligned_with_validation": annual_row is not None,
            "annual_row_field_level_match_status": (
                annual_row.get("field_level_match_status") if annual_row else None
            ),
            "annual_row_overall_match_status": (
                annual_row.get("overall_match_status") if annual_row else None
            ),
        }
    )
    comparison_dir = output_dir / "comparison"
    write_json(comparison, comparison_dir / "deterministic_vs_llm_summary.json")
    _write_comparison_report(
        comparison_dir / "deterministic_vs_llm_report.md",
        comparison,
    )
    stage4f_summary = _write_stage4f_results_summary(
        evaluation_summary,
        comparison,
        annual_row,
    )
    reevaluation_summary = {
        "stage": "Stage 4F",
        "output_dir": str(output_dir),
        "llm_extraction_rerun": False,
        "live_fetch_rerun": False,
        "broad_web_search_used": False,
        "validation_pdf_parsed": False,
        "annual_collection_record_aligned_with_validation": annual_row is not None,
        "evaluation_row_count": evaluation_summary.get("evaluation_row_count"),
        "overall_match_status_counts": (
            evaluation_summary.get("overall_match_status_counts") or {}
        ),
        "rows_with_both_collection_and_validation_evidence_count": (
            evaluation_summary.get(
                "rows_with_both_collection_and_validation_evidence_count"
            )
        ),
        "reserved_source_leakage_count": evaluation_summary.get(
            "reserved_source_leakage_count"
        ),
        "human_review_flagged_row_count": evaluation_summary.get(
            "human_review_flagged_row_count"
        ),
    }
    return {
        "output_dir": str(output_dir),
        "llm_records": llm_records,
        "evaluation_rows": evaluation_rows,
        "evaluation_summary": evaluation_summary,
        "evaluation_outputs": evaluation_outputs,
        "comparison_summary": comparison,
        "reevaluation_summary": reevaluation_summary,
        "stage4f_results_summary": stage4f_summary,
    }


def _print_completed_summary(result: dict) -> None:
    replay = result["llm_extraction_replay_summary"]
    comparison = result["comparison_summary"]
    evaluation = result["evaluation_summary"]
    print("=" * 72)
    print("New Mexico HPS LLM extraction replay completed.")
    print(f"output_dir: {_console_text(result['output_dir'])}")
    print(f"live_fetch_enabled: {replay.get('live_fetch_enabled')}")
    print(f"broad_web_search_used: {replay.get('broad_web_search_used')}")
    print(f"llm_call_attempted: {replay.get('llm_call_attempted')}")
    print(f"llm_call_succeeded: {replay.get('llm_call_succeeded')}")
    print(f"selected_chunk_count: {replay.get('selected_chunk_count')}")
    print(f"raw_record_count: {replay.get('raw_record_count')}")
    print(f"validated_record_count: {replay.get('validated_record_count')}")
    print(f"normalized_record_count: {replay.get('normalized_record_count')}")
    print(
        "extracted_annual_2025_case_record_found:",
        replay.get("extracted_annual_2025_case_record_found"),
    )
    print(
        "llm_extracted_2025_annual_cases_7:",
        comparison.get("llm_extracted_2025_annual_cases_7"),
    )
    print(
        "llm_extracted_2025_annual_deaths_3:",
        comparison.get("llm_extracted_2025_annual_deaths_3"),
    )
    print(
        "overall_match_status_counts:",
        json.dumps(evaluation.get("overall_match_status_counts") or {}),
    )
    print("=" * 72)


def _print_reevaluation_summary(result: dict) -> None:
    summary = result["reevaluation_summary"]
    evaluation = result["evaluation_summary"]
    print("=" * 72)
    print("New Mexico HPS existing LLM replay re-evaluation completed.")
    print(f"output_dir: {_console_text(result['output_dir'])}")
    print(f"live_fetch_rerun: {summary.get('live_fetch_rerun')}")
    print(f"llm_extraction_rerun: {summary.get('llm_extraction_rerun')}")
    print(f"broad_web_search_used: {summary.get('broad_web_search_used')}")
    print(
        "annual_collection_record_aligned_with_validation:",
        summary.get("annual_collection_record_aligned_with_validation"),
    )
    print(
        "evaluation_row_count:",
        evaluation.get("evaluation_row_count"),
    )
    print(
        "overall_match_status_counts:",
        json.dumps(evaluation.get("overall_match_status_counts") or {}),
    )
    print(
        "rows_with_both_collection_and_validation_evidence_count:",
        evaluation.get("rows_with_both_collection_and_validation_evidence_count"),
    )
    print(
        "reserved_source_leakage_count:",
        evaluation.get("reserved_source_leakage_count"),
    )
    print("=" * 72)


def main() -> int:
    args = _build_parser().parse_args()
    if args.max_chunks <= 0:
        print("--max-chunks must be positive.", file=sys.stderr)
        return 2

    if args.dry_run:
        print(json.dumps(_run_plan(args), indent=2, sort_keys=True))
        if not args.allow_llm_extraction:
            print(
                "Dry run only. Pass --allow-llm-extraction to run controlled LLM extraction replay."
            )
        return 0

    if args.reevaluate_existing:
        result = reevaluate_existing(args)
        _print_reevaluation_summary(result)
        return 0

    if not args.allow_llm_extraction:
        print(
            "LLM extraction is disabled by default. Pass --allow-llm-extraction "
            "to run the controlled replay on already-fetched New Mexico collection "
            "evidence, or use --dry-run to inspect planned inputs.",
            file=sys.stderr,
        )
        return 2

    result = run_replay(args)
    _print_completed_summary(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
