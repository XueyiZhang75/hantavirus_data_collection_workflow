"""Offline-safe tests for the Stage 3B MV Hondius live pilot scaffolding."""

from __future__ import annotations

import csv
import os
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
_SEED_OVERLAY = _LIVE_CASE_DIR / "mv_hondius_seed_sources.json"
_POLICY_OVERLAY = _LIVE_CASE_DIR / "mv_hondius_source_role_policy_overlay.json"
_GROUND_TRUTH = _LIVE_CASE_DIR / "mv_hondius_ground_truth_records.csv"
_CASE_SOURCE_IDS = {
    "src_reuters_mv_hondius_2026_05_27",
    "src_vdh_hantavirus_mv_hondius_context",
    "src_who_don600_mv_hondius_2026",
}
_BASE_RESERVED_SOURCE_IDS = {
    "src_cdc_reported_cases",
    "src_ecdc_surveillance_updates",
    "src_ecdc_annual_report_2023",
    "src_who_hantavirus_fact_sheet",
}


def _source_id_from_seed_id(seed_source_id: str) -> str:
    if seed_source_id.startswith("seed_"):
        return "src_" + seed_source_id[len("seed_"):]
    return seed_source_id


def _initial_state() -> dict:
    return {
        "user_request": "Offline routing test for MV Hondius Stage 3B.",
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


def test_seed_overlay_unset_keeps_base_catalog(monkeypatch):
    monkeypatch.delenv("HDC_SEED_SOURCE_OVERLAY_PATH", raising=False)

    catalog = load_hantavirus_seed_sources()

    assert len(catalog.get("seed_sources") or []) == 15
    seed_ids = {s.get("seed_source_id") for s in catalog.get("seed_sources") or []}
    assert "seed_cdc_about_hantavirus" in seed_ids
    assert not (_CASE_SOURCE_IDS & {_source_id_from_seed_id(sid) for sid in seed_ids})


def test_seed_overlay_adds_mv_hondius_sources(monkeypatch):
    monkeypatch.setenv("HDC_SEED_SOURCE_OVERLAY_PATH", str(_SEED_OVERLAY))

    catalog = load_hantavirus_seed_sources()

    seed_ids = {s.get("seed_source_id") for s in catalog.get("seed_sources") or []}
    source_ids = {_source_id_from_seed_id(sid) for sid in seed_ids}
    assert _CASE_SOURCE_IDS <= source_ids
    assert "seed_cdc_about_hantavirus" in seed_ids
    assert len(catalog.get("seed_sources") or []) == 18
    assert (catalog.get("overlay_metadata") or {}).get("enabled") is True


def test_source_role_policy_overlay_preserves_base_and_adds_who(monkeypatch):
    monkeypatch.delenv("HDC_SOURCE_ROLE_POLICY_OVERLAY_PATH", raising=False)
    base_policy = load_source_role_policy()
    base_reserved = set(base_policy.get("validation_reserved_source_ids") or [])
    assert _BASE_RESERVED_SOURCE_IDS <= base_reserved
    assert "src_who_don600_mv_hondius_2026" not in base_reserved

    monkeypatch.setenv("HDC_SOURCE_ROLE_POLICY_OVERLAY_PATH", str(_POLICY_OVERLAY))
    policy = load_source_role_policy()
    reserved = set(policy.get("validation_reserved_source_ids") or [])

    assert _BASE_RESERVED_SOURCE_IDS <= reserved
    assert "src_who_don600_mv_hondius_2026" in reserved
    assert policy.get("domain_masking_enabled") is False
    assert "src_reuters_mv_hondius_2026_05_27" in (
        policy.get("collection_allowed_source_ids") or []
    )
    assert "src_vdh_hantavirus_mv_hondius_context" in (
        policy.get("context_only_source_ids") or []
    )


def test_masked_routing_blocks_who_with_overlays(monkeypatch):
    monkeypatch.setenv("HDC_COLLECTION_MODE", "masked_validation")
    monkeypatch.setenv("HDC_SEED_SOURCE_OVERLAY_PATH", str(_SEED_OVERLAY))
    monkeypatch.setenv("HDC_SOURCE_ROLE_POLICY_OVERLAY_PATH", str(_POLICY_OVERLAY))
    monkeypatch.setenv("HDC_USE_FIXTURE_DOCUMENTS", "false")
    monkeypatch.setenv("HDC_ENABLE_LIVE_FETCH", "false")
    monkeypatch.setenv("HDC_ENABLE_LLM_EXTRACTION", "false")
    monkeypatch.setenv(
        "HDC_SOURCE_ID_ALLOWLIST",
        ",".join(sorted(_CASE_SOURCE_IDS)),
    )

    result = build_graph().invoke(_initial_state())
    registry = {
        entry.get("source_id"): entry for entry in (result.get("source_registry") or [])
    }

    who = registry.get("src_who_don600_mv_hondius_2026")
    assert who is not None
    assert who.get("source_role") == "validation_reserved"
    assert who.get("final_screening_decision") == "reserved_for_validation"
    assert who.get("ready_for_content_fetch") is False
    assert "validation_reserved" in (who.get("routing_flags") or [])

    reuters = registry.get("src_reuters_mv_hondius_2026_05_27")
    assert reuters is not None
    assert reuters.get("source_role") != "validation_reserved"
    assert reuters.get("final_screening_decision") != "reserved_for_validation"


def test_mv_hondius_script_is_safe_by_default():
    script = _PROJECT_ROOT / "scripts" / "run_mv_hondius_live_masked_pilot.py"
    assert script.exists(), f"missing {script}"

    text = script.read_text(encoding="utf-8")
    assert '"HDC_ENABLE_LLM_EXTRACTION": "false"' in text
    assert "load_dotenv" not in text
    assert "requests.get" not in text

    env = os.environ.copy()
    env["HDC_ENABLE_LIVE_FETCH"] = "false"
    env["HDC_ENABLE_LLM_EXTRACTION"] = "false"
    env.pop("ANTHROPIC_API_KEY", None)
    env.pop("OPENAI_API_KEY", None)
    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=_PROJECT_ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )

    assert result.returncode != 0
    assert "Pass --allow-live-fetch" in result.stderr


def test_mv_hondius_script_dry_run_is_offline_safe():
    script = _PROJECT_ROOT / "scripts" / "run_mv_hondius_live_masked_pilot.py"
    result = subprocess.run(
        [sys.executable, str(script), "--dry-run"],
        cwd=_PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )

    assert result.returncode == 0
    assert '"HDC_ENABLE_LIVE_FETCH": "false"' in result.stdout
    assert "Dry run only" in result.stdout
    assert "mv_hondius_ground_truth_records.csv" in result.stdout


def test_mv_hondius_ground_truth_csv_is_manual_who_record():
    assert _GROUND_TRUTH.exists(), f"missing {_GROUND_TRUTH}"
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
    assert len(rows) == 1
    row = rows[0]
    assert row["source_id"] == "src_who_don600_mv_hondius_2026"
    assert row["cases_unspecified"] == "8"
    assert row["deaths"] == "3"
    assert len(row["evidence_quote"].split()) <= 25
