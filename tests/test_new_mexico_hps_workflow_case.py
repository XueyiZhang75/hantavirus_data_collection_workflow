"""Offline-safe tests for the New Mexico HPS workflow case study."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_SRC = _PROJECT_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from hdc_workflow.config import (  # noqa: E402
    load_hantavirus_seed_sources,
    load_source_role_policy,
)
from hdc_workflow.graph import build_graph  # noqa: E402


_LIVE_CASE_DIR = _SRC / "hdc_workflow" / "resources" / "live_case_studies"
_SEED_OVERLAY = _LIVE_CASE_DIR / "new_mexico_hps_seed_sources.json"
_POLICY_OVERLAY = _LIVE_CASE_DIR / "new_mexico_hps_source_role_policy_overlay.json"
_GROUND_TRUTH = _LIVE_CASE_DIR / "new_mexico_hps_ground_truth_records.csv"
_SCRIPT = _PROJECT_ROOT / "scripts" / "run_hdc_workflow_configured.py"
_COLLECTION_IDS = {
    "src_nmdoh_hps_2024_first_case",
    "src_nmdoh_hps_2025_first_case_death",
    "src_nmdoh_hps_2026_first_case_prior_year_summary",
}
_CONTEXT_IDS = {
    "src_nmdoh_hps_overview_1975_2025",
    "src_cdc_hantavirus_reported_cases_through_2023",
}
_VALIDATION_IDS = {"src_nmdoh_hps_cases_by_county_1975_2025_pdf"}
_CASE_SOURCE_IDS = _COLLECTION_IDS | _CONTEXT_IDS | _VALIDATION_IDS


def _source_id_from_seed_id(seed_source_id: str) -> str:
    if seed_source_id.startswith("seed_"):
        return "src_" + seed_source_id[len("seed_"):]
    return seed_source_id


def _initial_state() -> dict:
    return {
        "user_request": "Offline routing test for the New Mexico HPS workflow profile.",
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


def test_new_mexico_seed_overlay_adds_six_sources(monkeypatch):
    monkeypatch.delenv("HDC_SEED_SOURCE_OVERLAY_PATH", raising=False)
    base_catalog = load_hantavirus_seed_sources()
    base_ids = {
        _source_id_from_seed_id(s.get("seed_source_id") or "")
        for s in base_catalog.get("seed_sources") or []
    }
    assert not (_CASE_SOURCE_IDS & base_ids)

    monkeypatch.setenv("HDC_SEED_SOURCE_OVERLAY_PATH", str(_SEED_OVERLAY))
    catalog = load_hantavirus_seed_sources()
    source_ids = {
        _source_id_from_seed_id(s.get("seed_source_id") or "")
        for s in catalog.get("seed_sources") or []
    }

    assert _CASE_SOURCE_IDS <= source_ids
    assert len(catalog.get("seed_sources") or []) == len(
        base_catalog.get("seed_sources") or []
    ) + 6


def test_new_mexico_source_role_overlay(monkeypatch):
    monkeypatch.setenv("HDC_SOURCE_ROLE_POLICY_OVERLAY_PATH", str(_POLICY_OVERLAY))
    policy = load_source_role_policy()

    assert _COLLECTION_IDS <= set(policy.get("collection_allowed_source_ids") or [])
    assert _VALIDATION_IDS <= set(policy.get("validation_reserved_source_ids") or [])
    assert _CONTEXT_IDS <= set(policy.get("context_only_source_ids") or [])
    assert policy.get("validation_reserved_domains") == []
    assert policy.get("domain_masking_enabled") is False


def test_new_mexico_masked_routing_blocks_validation_pdf(monkeypatch):
    monkeypatch.setenv("HDC_COLLECTION_MODE", "masked_validation")
    monkeypatch.setenv("HDC_SEED_SOURCE_OVERLAY_PATH", str(_SEED_OVERLAY))
    monkeypatch.setenv("HDC_SOURCE_ROLE_POLICY_OVERLAY_PATH", str(_POLICY_OVERLAY))
    monkeypatch.setenv("HDC_ENABLE_LIVE_FETCH", "false")
    monkeypatch.setenv("HDC_USE_FIXTURE_DOCUMENTS", "false")
    monkeypatch.setenv("HDC_ENABLE_LLM_EXTRACTION", "false")
    monkeypatch.setenv("HDC_SOURCE_ID_ALLOWLIST", ",".join(sorted(_CASE_SOURCE_IDS)))

    result = build_graph().invoke(_initial_state())
    registry = {
        entry.get("source_id"): entry
        for entry in (result.get("source_registry") or [])
    }

    validation = registry["src_nmdoh_hps_cases_by_county_1975_2025_pdf"]
    assert validation["source_role"] == "validation_reserved"
    assert validation["final_screening_decision"] == "reserved_for_validation"
    assert validation["ready_for_content_fetch"] is False
    assert validation["credibility_rubric_version"] == "source_credibility_v2"
    assert validation["source_role_final"] == "validation"
    assert validation["credibility_level"] in {"high", "medium"}
    assert 0.0 <= validation["credibility_score"] <= 1.0
    assert {
        "authority",
        "granularity",
        "provenance",
        "timeliness",
        "independence",
        "risk",
    } <= set(validation["credibility_score_components"])

    for source_id in _COLLECTION_IDS:
        entry = registry[source_id]
        assert entry["source_role"] != "validation_reserved"
        assert entry["final_screening_decision"] != "reserved_for_validation"
        assert entry["credibility_level"] in {"high", "medium"}
        assert entry["credibility_score"] >= 0.60

    for source_id in _CONTEXT_IDS:
        entry = registry[source_id]
        assert entry["source_role"] == "context_source"
        assert "blocked_from_structured_extraction" in (
            entry.get("routing_flags") or []
        )
        assert entry["credibility_reason"]


def test_new_mexico_ground_truth_csv_shape():
    with _GROUND_TRUTH.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = set(reader.fieldnames or [])

    required = {
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
    }
    assert required <= fieldnames
    assert rows
    row = rows[0]
    assert row["source_id"] == "src_nmdoh_hps_cases_by_county_1975_2025_pdf"
    assert row["cases_unspecified"] == "7"
    assert row["reporting_period"] == "2025"
    assert len(row["evidence_quote"].split()) <= 25


def test_configured_workflow_run_script_uses_config_directly():
    assert _SCRIPT.exists(), f"missing {_SCRIPT}"
    text = _SCRIPT.read_text(encoding="utf-8")

    assert "--disable-live-fetch" in text
    assert "--disable-all-llm" in text
    assert "Pass --allow-live-fetch" not in text
    assert "Pass --allow-llm" not in text
    assert "load_dotenv" not in text


def test_configured_workflow_run_script_print_config_is_offline_safe():
    result = subprocess.run(
        [
            sys.executable,
            str(_SCRIPT),
            "--print-config-only",
            "--disable-live-fetch",
            "--disable-all-llm",
        ],
        cwd=_PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )

    assert result.returncode == 0
    assert '"HDC_ENABLE_LIVE_FETCH": "false"' in result.stdout
    assert '"HDC_ENABLE_LLM_EXTRACTION": "false"' in result.stdout
    assert "new_mexico_hps_seed_sources.json" in result.stdout
    assert "new_mexico_hps_source_role_policy_overlay.json" in result.stdout
    assert "studio_minimal_input:" in result.stdout
