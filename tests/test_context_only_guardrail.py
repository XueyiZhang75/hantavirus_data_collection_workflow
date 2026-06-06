"""Offline-safe tests for the context-only extraction guardrail."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_SRC = _PROJECT_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from hdc_workflow.graph import build_graph  # noqa: E402
from hdc_workflow.nodes.content_processing import (  # noqa: E402
    evidence_chunking_and_data_presence_flagging,
)
from hdc_workflow.nodes.extraction import structured_extraction  # noqa: E402


_LIVE_CASE_DIR = _SRC / "hdc_workflow" / "resources" / "live_case_studies"
_SEED_OVERLAY = _LIVE_CASE_DIR / "mv_hondius_seed_sources.json"
_POLICY_OVERLAY = _LIVE_CASE_DIR / "mv_hondius_source_role_policy_overlay.json"
_REUTERS = "src_reuters_mv_hondius_2026_05_27"
_VDH = "src_vdh_hantavirus_mv_hondius_context"
_WHO = "src_who_don600_mv_hondius_2026"
_CASE_SOURCE_IDS = [_REUTERS, _VDH, _WHO]


def _initial_state() -> dict:
    return {
        "user_request": "Offline context-only guardrail test.",
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


def _set_mv_hondius_env(monkeypatch) -> None:
    monkeypatch.setenv("HDC_COLLECTION_MODE", "masked_validation")
    monkeypatch.setenv("HDC_SEED_SOURCE_OVERLAY_PATH", str(_SEED_OVERLAY))
    monkeypatch.setenv("HDC_SOURCE_ROLE_POLICY_OVERLAY_PATH", str(_POLICY_OVERLAY))
    monkeypatch.setenv("HDC_ENABLE_LIVE_FETCH", "false")
    monkeypatch.setenv("HDC_USE_FIXTURE_DOCUMENTS", "false")
    monkeypatch.setenv("HDC_ENABLE_LLM_EXTRACTION", "false")
    monkeypatch.setenv("HDC_SOURCE_ID_ALLOWLIST", ",".join(_CASE_SOURCE_IDS))


def test_mv_hondius_context_only_source_routes_to_context_fetch(monkeypatch):
    _set_mv_hondius_env(monkeypatch)

    result = build_graph().invoke(_initial_state())
    registry = {
        entry.get("source_id"): entry for entry in (result.get("source_registry") or [])
    }

    vdh = registry.get(_VDH)
    assert vdh is not None
    assert vdh.get("source_role") == "context_source"
    assert vdh.get("final_screening_decision") == "include_for_context_fetch"
    assert vdh.get("ready_for_content_fetch") is True
    assert vdh.get("status") == "ready_for_context_fetch"
    assert "context_only" in (vdh.get("routing_flags") or [])
    assert "blocked_from_structured_extraction" in (
        vdh.get("routing_flags") or []
    )

    who = registry.get(_WHO)
    assert who is not None
    assert who.get("source_role") == "validation_reserved"
    assert who.get("final_screening_decision") == "reserved_for_validation"

    reuters = registry.get(_REUTERS)
    assert reuters is not None
    assert reuters.get("source_role") != "validation_reserved"

    routing_summary = result.get("source_routing_summary") or {}
    assert _VDH in (routing_summary.get("context_only_source_ids") or [])


def test_evidence_chunking_suppresses_target_data_for_context_only_document(monkeypatch):
    _set_mv_hondius_env(monkeypatch)
    state = {
        "documents": [
            {
                "source_id": _VDH,
                "document_type": "html",
                "clean_text": (
                    "WHO was notified of a possible MV Hondius outbreak. "
                    "Multiple cases including fatal cases were reported."
                ),
                "tables": [],
                "metadata": {
                    "routing_flags": [
                        "context_only",
                        "blocked_from_structured_extraction",
                    ]
                },
                "parse_status": "parsed_html",
                "quality_status": "usable",
                "quality_issues": [],
                "url": "https://www.vdh.virginia.gov/hantavirus",
                "canonical_url": "https://www.vdh.virginia.gov/hantavirus",
                "title": "VDH Hantavirus",
                "publisher": "Virginia Department of Health",
                "source_type": "official_public_health_agency",
                "source_role": "context_source",
                "fetch_purpose": "context_grounding",
                "is_live_fetched": False,
                "is_offline_stub": False,
            }
        ],
        "collection_trace": [],
    }

    result = evidence_chunking_and_data_presence_flagging(state)
    chunks = result.get("evidence_chunks") or []
    presence_summary = result.get("data_presence_summary") or {}

    assert chunks
    assert not any(chunk.get("contains_target_data") for chunk in chunks)
    assert all(not (chunk.get("data_types") or []) for chunk in chunks)
    assert presence_summary.get("target_data_chunk_count") == 0
    assert presence_summary.get("context_only_target_data_suppressed_count", 0) >= 1
    assert _VDH in (presence_summary.get("context_only_source_ids") or [])


def test_structured_extraction_skips_context_only_chunk_even_if_marked_target_data(
    monkeypatch,
):
    _set_mv_hondius_env(monkeypatch)
    state = {
        "evidence_chunks": [
            {
                "chunk_id": "chunk_context_only_bad_001",
                "source_id": _VDH,
                "text": "The source says 8 cases and 3 deaths were reported.",
                "contains_target_data": True,
                "data_types": ["case_count", "death_count"],
                "confidence": 0.95,
                "document_type": "html",
                "fetch_purpose": "context_grounding",
                "source_url": "https://www.vdh.virginia.gov/hantavirus",
                "canonical_url": "https://www.vdh.virginia.gov/hantavirus",
                "title": "VDH Hantavirus",
                "publisher": "Virginia Department of Health",
                "source_type": "official_public_health_agency",
                "source_role": "context_source",
                "quality_status": "usable",
                "chunk_index": 1,
                "chunk_kind": "text",
                "context_types": ["clinical_or_background"],
                "presence_reason": "malicious test chunk",
            }
        ],
        "collection_trace": [],
    }

    result = structured_extraction(state)
    summary = result.get("structured_extraction_summary") or {}

    assert result.get("raw_records") == []
    assert summary.get("raw_record_count") == 0
    assert summary.get("skipped_context_only_chunk_count") == 1
    assert _VDH in (summary.get("skipped_context_only_source_ids") or [])
