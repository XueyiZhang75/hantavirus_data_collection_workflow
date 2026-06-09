from __future__ import annotations

import csv
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_SRC = _PROJECT_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from hdc_workflow.evaluation_report_builder import (  # noqa: E402
    build_evaluation_report,
    read_csv_records,
    write_evaluation_outputs,
)
from hdc_workflow.nodes.linking_validation import (  # noqa: E402
    cross_source_consistency_check,
    record_linking,
)
from hdc_workflow.runtime_profile import GROUND_TRUTH_RECORDS_PATH  # noqa: E402


def _task(
    disease: str,
    location: str,
    start_date: str = "2024",
    end_date: str = "2026",
) -> dict:
    return {
        "structured_task": {
            "disease": disease,
            "location": location,
            "start_date": start_date,
            "end_date": end_date,
            "target_fields": ["cases_unspecified", "deaths", "source_url"],
        },
        "collection_spec": {
            "disease": disease,
            "geography": location,
            "start_date": start_date,
            "end_date": end_date,
            "time_window": f"{start_date}-{end_date}",
        },
        "disease_intelligence": {
            "disease_standard_name": disease,
            "aliases": [disease],
            "pathogen_terms": [disease],
            "syndrome_terms": ["HPS", "HFRS"] if "hanta" in disease.lower() else [],
        },
    }


def _record(record_id: str, **overrides) -> dict:
    record = {
        "record_id": record_id,
        "linked_event_id": f"event_{record_id}",
        "disease": "COVID-19",
        "disease_standard_name": "COVID-19",
        "virus_or_syndrome": "COVID-19",
        "country": "United States of America",
        "subnational_location": "New York",
        "date_reported": "2024-06-01",
        "date_anchor": "2024-06-01",
        "reporting_period": "2024",
        "statistical_count_type": "annual",
        "count_semantics": "annual",
        "cases_unspecified": 100,
        "deaths": 2,
        "source_id": f"src_{record_id}",
        "source_url": f"https://example.org/{record_id}",
        "source_type": "official_public_health_agency",
        "source_role_final": "collection",
        "evidence_quote": "Official source reports 100 COVID-19 cases in New York in 2024.",
        "supporting_chunk_id": f"chunk_{record_id}",
        "countable": True,
    }
    record.update(overrides)
    return record


def _linked_validation_state(
    collection_records: list[dict],
    validation_records: list[dict],
    *,
    task: dict | None = None,
) -> dict:
    linked = record_linking(
        {
            "normalized_records": collection_records,
            "human_review_queue": [],
            "collection_trace": [],
        }
    )
    task_context = task or _task("COVID-19", "New York", "2024", "2024")
    return {
        **task_context,
        "normalized_records": linked["normalized_records"],
        "linked_events": linked["linked_events"],
        "event_clusters": linked["event_clusters"],
        "duplicate_clusters": linked["duplicate_clusters"],
        "validation_records": validation_records,
        "source_registry": [],
        "conflicts": [],
        "human_review_queue": [],
        "collection_trace": linked["collection_trace"],
    }


def _write_validation_csv(path: Path, rows: list[dict]) -> None:
    fieldnames = sorted({key for row in rows for key in row})
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _resolve(records: list[dict], task_context: dict, **kwargs) -> dict:
    from hdc_workflow.validation_source_compatibility import (
        resolve_task_compatible_validation_records,
    )

    return resolve_task_compatible_validation_records(
        validation_records=records,
        state_or_task_context=task_context,
        **kwargs,
    )


def test_new_mexico_hps_validation_remains_compatible_for_new_mexico_task():
    records = read_csv_records(GROUND_TRUTH_RECORDS_PATH)
    result = _resolve(
        records,
        _task("hantavirus", "New Mexico", "2020", "2026"),
        validation_records_path=GROUND_TRUTH_RECORDS_PATH,
        validation_records_explicit=False,
    )

    summary = result["validation_source_compatibility_summary"]
    assert summary["compatibility_status"] in {"compatible", "partially_compatible"}
    assert summary["active_validation_record_count"] > 0
    assert result["active_validation_records"]
    assert all(
        "new mexico" in str(row.get("subnational_location", "")).lower()
        for row in result["active_validation_records"]
    )


def test_new_mexico_hps_validation_disabled_for_shanghai_task():
    records = read_csv_records(GROUND_TRUTH_RECORDS_PATH)
    result = _resolve(
        records,
        _task("hantavirus", "Shanghai", "2024", "2026"),
        validation_records_path=GROUND_TRUTH_RECORDS_PATH,
        validation_records_explicit=False,
    )

    summary = result["validation_source_compatibility_summary"]
    assert summary["compatibility_status"] in {
        "no_task_compatible_validation_source",
        "incompatible_validation_source_disabled",
    }
    assert summary["active_validation_record_count"] == 0
    assert summary["inactive_validation_record_count"] > 0
    assert not any(
        "new mexico" in str(row.get("subnational_location", "")).lower()
        for row in result["active_validation_records"]
    )
    assert any("geography" in warning.lower() for warning in summary["warnings"])


def test_new_mexico_hps_validation_disabled_for_covid19_new_york():
    records = read_csv_records(GROUND_TRUTH_RECORDS_PATH)
    result = _resolve(records, _task("COVID-19", "New York", "2024", "2024"))

    summary = result["validation_source_compatibility_summary"]
    assert summary["active_validation_record_count"] == 0
    assert summary["inactive_validation_record_count"] == len(records)
    assert any("disease" in warning.lower() for warning in summary["warnings"])


def test_new_mexico_hps_validation_disabled_for_dengue_florida():
    records = read_csv_records(GROUND_TRUTH_RECORDS_PATH)
    result = _resolve(records, _task("dengue", "Florida", "2025", "2025"))

    summary = result["validation_source_compatibility_summary"]
    assert summary["active_validation_record_count"] == 0
    assert summary["inactive_validation_record_count"] == len(records)
    assert any("disease" in warning.lower() for warning in summary["warnings"])


def test_explicit_compatible_validation_csv_loads(tmp_path):
    csv_path = tmp_path / "covid_new_york_validation.csv"
    row = _record("val_covid_ny", source_role_final="validation")
    _write_validation_csv(csv_path, [row])

    result = _resolve(
        read_csv_records(csv_path),
        _task("COVID-19", "New York", "2024", "2024"),
        validation_records_path=csv_path,
        validation_records_explicit=True,
    )

    summary = result["validation_source_compatibility_summary"]
    assert summary["compatibility_status"] == "compatible"
    assert summary["active_validation_record_count"] == 1
    assert result["active_validation_records"][0]["record_id"] == "val_covid_ny"


def test_explicit_incompatible_validation_csv_disabled_by_default(tmp_path):
    csv_path = tmp_path / "hps_new_mexico_validation.csv"
    row = _record(
        "val_hps_nm",
        disease="Hantavirus disease",
        disease_standard_name="Hantavirus disease",
        virus_or_syndrome="HPS",
        subnational_location="New Mexico",
        reporting_period="2025",
        date_reported="2026-03-12",
        source_role_final="validation",
    )
    _write_validation_csv(csv_path, [row])

    result = _resolve(
        read_csv_records(csv_path),
        _task("COVID-19", "New York", "2024", "2024"),
        validation_records_path=csv_path,
        validation_records_explicit=True,
    )

    summary = result["validation_source_compatibility_summary"]
    assert summary["compatibility_status"] == "incompatible_validation_source_disabled"
    assert summary["active_validation_record_count"] == 0
    assert summary["inactive_validation_record_count"] == 1


def test_override_can_load_incompatible_validation_with_warning(monkeypatch):
    records = read_csv_records(GROUND_TRUTH_RECORDS_PATH)
    monkeypatch.setenv("HDC_ALLOW_INCOMPATIBLE_VALIDATION_RECORDS", "true")

    result = _resolve(
        records,
        _task("COVID-19", "New York", "2024", "2024"),
        validation_records_explicit=True,
    )

    summary = result["validation_source_compatibility_summary"]
    assert summary["compatibility_status"] == "explicit_validation_source_loaded_with_warning"
    assert summary["active_validation_record_count"] == len(records)
    assert any("override" in warning.lower() for warning in summary["warnings"])


def test_evaluation_report_does_not_compare_shanghai_to_new_mexico(tmp_path):
    records = read_csv_records(GROUND_TRUTH_RECORDS_PATH)
    resolved = _resolve(records, _task("hantavirus", "Shanghai", "2024", "2026"))
    collection = [
        _record(
            "rec_shanghai",
            disease="Hantavirus disease",
            disease_standard_name="Hantavirus disease",
            virus_or_syndrome="HFRS",
            country="China",
            subnational_location="Shanghai",
            reporting_period="2025",
        )
    ]

    rows, summary = build_evaluation_report(
        collection_records=collection,
        validation_records=resolved["active_validation_records"],
        validation_source_compatibility_summary=resolved[
            "validation_source_compatibility_summary"
        ],
    )
    outputs = write_evaluation_outputs(rows, summary, tmp_path)
    report_text = Path(outputs["evaluation_report_csv"]).read_text(encoding="utf-8")

    assert rows == []
    assert summary["validation_source_compatibility_status"] in {
        "no_task_compatible_validation_source",
        "incompatible_validation_source_disabled",
    }
    assert "New Mexico" not in report_text
    assert "gt_nmdoh_hps_2025_cases_001" not in report_text
    assert "missing_collection_record" not in report_text
    assert "missing_validation_record" not in report_text


def test_graph_validation_uses_active_validation_records_only():
    compatible = _record("val_covid_ny", source_role_final="validation")
    incompatible = _record(
        "val_hps_nm",
        disease="Hantavirus disease",
        disease_standard_name="Hantavirus disease",
        virus_or_syndrome="HPS",
        subnational_location="New Mexico",
        reporting_period="2025",
        source_role_final="validation",
    )
    state = _linked_validation_state(
        [_record("rec_covid_ny")],
        [compatible, incompatible],
    )

    result = cross_source_consistency_check(state)

    summary = result["validation_source_compatibility_summary"]
    assert summary["active_validation_record_count"] == 1
    assert summary["inactive_validation_record_count"] == 1
    right_ids = {
        rid
        for row in result["validation_results"]
        for rid in (row.get("right_record_ids") or [])
    }
    assert "val_covid_ny" in right_ids
    assert "val_hps_nm" not in right_ids


def test_no_compatible_validation_source_does_not_fail_graph():
    from hdc_workflow.graph import build_graph

    initial_state = {
        "user_request": "Collect COVID-19 data for New York in 2024.",
        "structured_task": {
            "disease": "COVID-19",
            "location": "New York",
            "start_date": "2024",
            "end_date": "2024",
        },
        "validation_records": read_csv_records(GROUND_TRUTH_RECORDS_PATH),
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
        "collection_trace": [],
    }

    result = build_graph().invoke(initial_state)

    assert result.get("final_data_package") is not None
    summary = result.get("validation_source_compatibility_summary") or {}
    assert summary["active_validation_record_count"] == 0
    assert result.get("validation_summary") is not None
    assert result["trusted_source_validation_summary"]["status"] in {
        "no_task_compatible_validation_source",
        "incompatible_validation_source_disabled",
    }


def test_validation_output_writer_exports_active_inactive_and_summary(tmp_path):
    from scripts.run_hdc_workflow_configured import _write_validation_outputs

    active = [_record("val_covid_ny", source_role_final="validation")]
    inactive = [
        _record(
            "val_hps_nm",
            disease="Hantavirus disease",
            disease_standard_name="Hantavirus disease",
            virus_or_syndrome="HPS",
            subnational_location="New Mexico",
            reporting_period="2025",
            source_role_final="validation",
        )
    ]
    summary = {
        "compatibility_status": "partially_compatible",
        "active_validation_record_count": 1,
        "inactive_validation_record_count": 1,
    }

    manifest = _write_validation_outputs(
        tmp_path,
        active,
        registry=[],
        inactive_validation_records=inactive,
        validation_source_compatibility_summary=summary,
        raw_validation_records=active + inactive,
    )

    active_text = Path(manifest["ground_truth_records_csv"]).read_text(
        encoding="utf-8"
    )
    inactive_text = Path(manifest["inactive_validation_records_csv"]).read_text(
        encoding="utf-8"
    )
    summary_text = Path(
        manifest["validation_source_compatibility_summary_json"]
    ).read_text(encoding="utf-8")

    assert "val_covid_ny" in active_text
    assert "val_hps_nm" not in active_text
    assert "val_hps_nm" in inactive_text
    assert "partially_compatible" in summary_text
    assert manifest["active_validation_record_count"] == 1
    assert manifest["inactive_validation_record_count"] == 1
