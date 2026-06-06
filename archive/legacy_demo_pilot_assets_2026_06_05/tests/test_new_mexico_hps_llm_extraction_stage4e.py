"""Offline-safe tests for Stage 4E New Mexico HPS LLM extraction replay."""

from __future__ import annotations

import csv
import importlib.util
import json
import os
import subprocess
import sys
from argparse import Namespace
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_SRC = _PROJECT_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from hdc_workflow.models import LLMExtractedRecord, LLMExtractionOutput  # noqa: E402


_SCRIPT = _PROJECT_ROOT / "scripts" / "run_new_mexico_hps_llm_extraction_replay.py"
_VALIDATION_SOURCE_ID = "src_nmdoh_hps_cases_by_county_1975_2025_pdf"
_CONTEXT_SOURCE_IDS = {
    "src_nmdoh_hps_overview_1975_2025",
    "src_cdc_hantavirus_reported_cases_through_2023",
}
_KEY_SOURCE_ID = "src_nmdoh_hps_2026_first_case_prior_year_summary"
_KEY_CHUNK_ID = "chunk_src_nmdoh_hps_2026_first_case_prior_year_summary_001"


def _load_script_module():
    assert _SCRIPT.exists(), f"missing {_SCRIPT}"
    spec = importlib.util.spec_from_file_location("stage4e_replay", _SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["stage4e_replay"] = module
    spec.loader.exec_module(module)
    return module


def _write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _make_fake_input(root: Path) -> None:
    collection = root / "collection"
    validation = root / "validation"
    diagnostics = root / "diagnostics"
    collection.mkdir(parents=True)
    validation.mkdir(parents=True)
    diagnostics.mkdir(parents=True)

    _write_csv(
        collection / "final_dataset.csv",
        [
            {
                "record_id": "det_001",
                "source_id": _KEY_SOURCE_ID,
                "source_url": "https://www.nmhealth.org/news/safety/2026/3?view=2322",
                "source_type": "official_public_health_agency",
                "disease": "Hantavirus disease",
                "virus_or_syndrome": "HPS",
                "country": "United States of America",
                "geographic_scope": "United States of America",
                "subnational_location": "New Mexico",
                "date_reported": "2026",
                "date_anchor": "2026",
                "statistical_count_type": "annual",
                "evidence_quote": (
                    "New Mexico recorded seven cases in 2025, with three of "
                    "them fatal."
                ),
                "supporting_chunk_id": _KEY_CHUNK_ID,
            },
            {
                "record_id": "ctx_001",
                "source_id": "src_nmdoh_hps_overview_1975_2025",
                "source_url": "https://www.nmhealth.org/about/erd/ideb/zdp/hps/",
                "source_type": "official_public_health_agency",
                "evidence_quote": "Context-only overview mentions HPS.",
                "supporting_chunk_id": "chunk_context_001",
            },
            {
                "record_id": "val_001",
                "source_id": _VALIDATION_SOURCE_ID,
                "source_url": "https://www.nmhealth.org/data/view/infectious/890/",
                "source_type": "official_public_health_agency",
                "evidence_quote": "Validation source should never be replayed.",
                "supporting_chunk_id": "chunk_validation_001",
            },
        ],
    )
    (collection / "source_registry.json").write_text(
        json.dumps(
            [
                {
                    "source_id": _KEY_SOURCE_ID,
                    "canonical_url": "https://www.nmhealth.org/news/safety/2026/3?view=2322",
                    "title": "NMDOH 2026 HPS press release",
                    "publisher": "New Mexico Department of Health",
                    "source_type": "official_public_health_agency",
                    "status": "ready_for_content_fetch",
                    "source_role": "data_source",
                    "final_screening_decision": "include_for_content_fetch",
                    "ready_for_content_fetch": True,
                },
                {
                    "source_id": "src_nmdoh_hps_overview_1975_2025",
                    "canonical_url": "https://www.nmhealth.org/about/erd/ideb/zdp/hps",
                    "title": "NMDOH HPS overview",
                    "publisher": "New Mexico Department of Health",
                    "source_type": "official_public_health_agency",
                    "status": "ready_for_context_fetch",
                    "source_role": "context_source",
                    "routing_flags": ["context_only", "blocked_from_structured_extraction"],
                    "final_screening_decision": "include_for_context_fetch",
                    "ready_for_content_fetch": True,
                },
                {
                    "source_id": _VALIDATION_SOURCE_ID,
                    "canonical_url": "https://www.nmhealth.org/data/view/infectious/890",
                    "title": "NMDOH county HPS cases",
                    "publisher": "New Mexico Department of Health",
                    "source_type": "official_public_health_agency",
                    "status": "reserved_for_validation",
                    "source_role": "validation_reserved",
                    "routing_flags": ["validation_reserved", "blocked_from_collection"],
                    "final_screening_decision": "reserved_for_validation",
                    "ready_for_content_fetch": False,
                },
            ],
            indent=2,
        ),
        encoding="utf-8",
    )
    _write_csv(
        validation / "ground_truth_records.csv",
        [
            {
                "record_id": "gt_001",
                "linked_event_id": "event_new_mexico_hps_2025",
                "disease": "Hantavirus disease",
                "virus_or_syndrome": "HPS",
                "country": "United States of America",
                "geographic_scope": "subnational",
                "subnational_location": "New Mexico",
                "date_anchor": "2025",
                "date_anchor_field": "reporting_period",
                "reporting_period": "2025",
                "statistical_count_type": "annual",
                "cases_unspecified": "7",
                "deaths": "",
                "source_id": _VALIDATION_SOURCE_ID,
                "source_url": "https://www.nmhealth.org/data/view/infectious/890/",
                "source_type": "official_public_health_agency",
                "evidence_quote": "HPS Cases in New Mexico by County, 2025, Total = 7.",
                "supporting_chunk_id": "manual_gt",
                "ground_truth_role": "held_out_validation",
            }
        ],
    )


def test_stage4e_script_is_safe_by_default():
    assert _SCRIPT.exists(), f"missing {_SCRIPT}"
    text = _SCRIPT.read_text(encoding="utf-8")

    assert '"HDC_ENABLE_LIVE_FETCH": "false"' in text
    assert "HDC_ENABLE_LLM_EXTRACTION" in text
    assert "load_dotenv" not in text
    assert "run_live_source_llm_pilot.py" not in text

    result = subprocess.run(
        [sys.executable, str(_SCRIPT)],
        cwd=_PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert result.returncode != 0
    assert "Pass --allow-llm-extraction" in result.stderr


def test_stage4e_dry_run_is_offline_safe():
    result = subprocess.run(
        [sys.executable, str(_SCRIPT), "--dry-run"],
        cwd=_PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )

    assert result.returncode == 0
    assert '"HDC_ENABLE_LIVE_FETCH": "false"' in result.stdout
    assert '"HDC_ENABLE_LLM_EXTRACTION": "false"' in result.stdout
    assert "Dry run only" in result.stdout


def test_select_replay_chunks_excludes_reserved_and_context_sources(tmp_path):
    module = _load_script_module()
    input_dir = tmp_path / "input"
    _make_fake_input(input_dir)

    chunks, audit = module.select_replay_chunks(
        input_dir=input_dir,
        target_source_ids=[_KEY_SOURCE_ID],
        max_chunks=10,
    )

    assert chunks
    assert {chunk["source_id"] for chunk in chunks} == {_KEY_SOURCE_ID}
    assert _KEY_CHUNK_ID in {chunk["chunk_id"] for chunk in chunks}
    assert audit["validation_reserved_sources_excluded"] is True
    assert audit["context_only_sources_excluded"] is True
    assert _VALIDATION_SOURCE_ID not in audit["selected_source_ids"]
    assert not (_CONTEXT_SOURCE_IDS & set(audit["selected_source_ids"]))


def test_mock_llm_replay_extracts_2025_annual_record(tmp_path, monkeypatch):
    module = _load_script_module()
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    _make_fake_input(input_dir)

    def fake_extract_chunk_with_llm(chunk, policy):  # noqa: ARG001
        assert chunk["source_id"] == _KEY_SOURCE_ID
        return LLMExtractionOutput(
            records=[
                LLMExtractedRecord(
                    disease="Hantavirus disease",
                    virus_or_syndrome="HPS",
                    country="United States of America",
                    subnational_location="New Mexico",
                    cases_unspecified=7,
                    deaths=3,
                    reporting_period="2025",
                    statistical_count_type="annual",
                    geographic_scope="New Mexico",
                    geographic_scope_type="subnational",
                )
            ],
            chunk_is_relevant=True,
        )

    monkeypatch.setattr(
        module.llm_clients, "extract_chunk_with_llm", fake_extract_chunk_with_llm
    )

    args = Namespace(
        input_dir=str(input_dir),
        output_dir=str(output_dir),
        allow_llm_extraction=True,
        dry_run=False,
        provider="anthropic",
        model="test-model",
        max_chunks=10,
        target_source_id=[_KEY_SOURCE_ID],
    )
    result = module.run_replay(args)

    summary = result["llm_extraction_replay_summary"]
    comparison = result["comparison_summary"]

    assert summary["llm_call_attempted"] is True
    assert summary["llm_call_succeeded"] is True
    assert summary["extracted_annual_2025_case_record_found"] is True
    assert comparison["llm_extracted_2025_annual_cases_7"] is True
    assert comparison["llm_extracted_2025_annual_deaths_3"] is True
    assert comparison["evaluation_improved_from_missing_collection_record"] is True
    assert (output_dir / "inputs" / "selected_chunks.json").exists()
    assert (output_dir / "evaluation" / "evaluation_report.csv").exists()


def test_reevaluate_existing_rebuilds_outputs_without_llm_call(tmp_path, monkeypatch):
    module = _load_script_module()
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    _make_fake_input(input_dir)

    def fake_extract_chunk_with_llm(chunk, policy):  # noqa: ARG001
        return LLMExtractionOutput(
            records=[
                LLMExtractedRecord(
                    disease="Hantavirus disease",
                    virus_or_syndrome="HPS",
                    country="United States of America",
                    subnational_location="New Mexico",
                    date_reported="2026-03-12",
                    cases_unspecified=7,
                    deaths=3,
                    reporting_period="2025",
                    statistical_count_type="annual",
                    geographic_scope="New Mexico",
                    geographic_scope_type="subnational",
                )
            ],
            chunk_is_relevant=True,
        )

    monkeypatch.setattr(
        module.llm_clients, "extract_chunk_with_llm", fake_extract_chunk_with_llm
    )
    replay_args = Namespace(
        input_dir=str(input_dir),
        output_dir=str(output_dir),
        allow_llm_extraction=True,
        dry_run=False,
        provider="anthropic",
        model="test-model",
        max_chunks=10,
        target_source_id=[_KEY_SOURCE_ID],
    )
    module.run_replay(replay_args)

    def fail_if_llm_called(chunk, policy):  # noqa: ARG001
        raise AssertionError("reevaluate-existing must not call LLM")

    monkeypatch.setattr(
        module.llm_clients, "extract_chunk_with_llm", fail_if_llm_called
    )
    reevaluate_args = Namespace(
        input_dir=str(input_dir),
        output_dir=str(output_dir),
        provider="anthropic",
        model="test-model",
        max_chunks=10,
        target_source_id=None,
    )

    result = module.reevaluate_existing(reevaluate_args)

    assert result["reevaluation_summary"]["llm_extraction_rerun"] is False
    assert result["reevaluation_summary"]["live_fetch_rerun"] is False
    assert result["reevaluation_summary"][
        "annual_collection_record_aligned_with_validation"
    ] is True
    assert result["evaluation_summary"]["evaluation_row_count"] == 1
    assert result["evaluation_summary"][
        "rows_with_both_collection_and_validation_evidence_count"
    ] == 1
    assert (
        output_dir / "evaluation" / "evaluation_report.csv"
    ).exists()
