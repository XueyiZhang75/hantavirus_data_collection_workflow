from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CLI = [sys.executable, "-m", "hdc_workflow.cli"]


def _env(extra: dict[str, str] | None = None) -> dict[str, str]:
    env = os.environ.copy()
    src = str(PROJECT_ROOT / "src")
    env["PYTHONPATH"] = src + os.pathsep + env.get("PYTHONPATH", "")
    if extra:
        env.update(extra)
    return env


def _run(args: list[str], *, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        CLI + args,
        cwd=PROJECT_ROOT,
        env=env or _env(),
        text=True,
        capture_output=True,
        timeout=120,
    )


def _write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _make_session(
    root: Path,
    *,
    name: str,
    disease: str,
    location: str,
    start_date: str,
    end_date: str,
    search_mode: str,
    search_provider: str,
    live_search: bool,
    live_fetch: bool,
    discovery_method: str,
) -> Path:
    session = root / name
    session.mkdir(parents=True)
    records = [
        {
            "record_id": f"rec_{name}_001",
            "disease": disease,
            "disease_standard_name": disease,
            "subnational_location": location,
            "source_id": f"src_{name}",
            "source_url": f"https://example.org/{name}",
            "evidence_quote": f"{location} reported {disease} cases.",
            "supporting_chunk_id": f"chunk_{name}_001",
        }
    ]
    structured_task = {
        "disease": disease,
        "location": location,
        "start_date": start_date,
        "end_date": end_date,
    }
    workflow_summaries = {
        "task_intake_summary": structured_task,
        "disease_intelligence_summary": {
            "disease_standard_name": disease,
            "generation_method": "curated_profile",
        },
        "profile_schema_summary": {
            "schema_generation_method": "disease_intelligence_generated_profile_schema",
        },
        "executable_source_plan_summary": {
            "planned_query_count": 10,
            "generation_method": "deterministic_executable_source_plan",
        },
        "source_search_execution_summary": {
            "search_enabled": search_mode != "disabled",
            "live_search_enabled": live_search,
            "search_mode": search_mode,
            "search_provider": search_provider,
            "planned_query_count": 10,
            "candidate_from_search_count": 1 if search_mode != "disabled" else 0,
            "total_candidate_count": 3,
        },
        "source_credibility_summary": {
            "assessed_source_count": 3,
        },
        "content_fetch_summary": {
            "selected_search_derived_fetch_count": 1,
        },
        "evidence_chunk_summary": {
            "evidence_chunk_count": 1,
        },
        "validation_summary": {
            "validation_result_count": 1,
        },
        "anomaly_summary": {
            "anomaly_result_count": 0,
        },
        "human_review_application_summary": {
            "decisions_applied_count": 1,
        },
        "event_clustering_summary": {
            "event_cluster_count": 1,
        },
        "duplicate_detection_summary": {
            "duplicate_cluster_count": 0,
        },
    }
    summary = {
        "live_fetch_enabled": live_fetch,
        "live_search_enabled": live_search,
        "source_search_mode": search_mode,
        "source_search_provider": search_provider,
        "document_count": 1,
        "normalized_record_count": 1,
        "validation_result_count": 1,
        "anomaly_result_count": 0,
        "human_review_item_count": 1,
        "final_dataset_post_review_count": 1,
    }
    live_fetch_summary = {
        "live_fetch_enabled": live_fetch,
        "documents": [
            {
                "source_id": f"src_{name}",
                "url": f"https://example.org/{name}",
                "quality_status": "usable",
                "is_live_fetched": live_fetch,
            }
        ],
        "quality_status_counts": {"usable": 1},
    }
    source_registry = [
        {
            "source_id": f"src_{name}",
            "canonical_url": f"https://example.org/{name}",
            "discovery_method": discovery_method,
            "source_role_final": "collection",
        },
        {
            "source_id": f"src_{name}_validation",
            "canonical_url": f"https://validation.example.org/{name}",
            "discovery_method": "offline_seed_catalog",
            "source_role_final": "validation",
        },
    ]
    final_package = {
        "final_dataset": records,
        "final_dataset_post_review": records,
        "workflow_summaries": workflow_summaries,
        "source_registry": source_registry,
        "human_review_queue": [{"review_item_id": f"review_{name}_001"}],
    }

    _write_json(session / "workflow_run_summary.json", summary)
    _write_json(session / "diagnostics" / "workflow_summaries.json", workflow_summaries)
    _write_json(session / "diagnostics" / "live_fetch_summary.json", live_fetch_summary)
    _write_json(session / "diagnostics" / "normalized_records.json", records)
    _write_json(session / "diagnostics" / "raw_records.json", records)
    _write_json(session / "diagnostics" / "validated_records.json", records)
    _write_json(session / "diagnostics" / "event_clusters.json", [{"event_cluster_id": f"event_{name}_001"}])
    _write_json(session / "diagnostics" / "duplicate_clusters.json", [])
    _write_json(session / "diagnostics" / "validation_results.json", [{"validation_result_id": f"val_{name}_001"}])
    _write_json(session / "diagnostics" / "anomaly_results.json", [])
    _write_json(session / "diagnostics" / "human_review_application_summary.json", {"decisions_applied_count": 1})
    _write_json(session / "collection" / "final_package.json", final_package)
    (session / "workflow_console").mkdir()
    (session / "workflow_console" / "hdc_workflow_console.html").write_text("<html></html>", encoding="utf-8")
    return session


def test_stage13_acceptance_matrix_extracts_required_fields(tmp_path):
    from hdc_workflow.acceptance import build_acceptance_matrix, write_acceptance_matrix

    sessions_root = tmp_path / "sessions"
    cases = [
        {
            "case_name": "Hantavirus / New Mexico / 2020-2026",
            "command_used": "python -m hdc_workflow.cli collect --config configs\\hdc_workflow_run_config.jsonc --disable-all-llm",
            "config_used": "configs/hdc_workflow_run_config.jsonc",
            "session_dir": _make_session(
                sessions_root,
                name="hantavirus_nm",
                disease="Hantavirus disease",
                location="New Mexico",
                start_date="2020",
                end_date="2026",
                search_mode="disabled",
                search_provider="tavily",
                live_search=False,
                live_fetch=True,
                discovery_method="offline_seed_catalog",
            ),
            "acceptance_status": "PASSED",
            "notes": "controlled live fetch compatibility",
        },
        {
            "case_name": "COVID-19 / New York / 2024",
            "command_used": "python -m hdc_workflow.cli collect --config configs\\examples\\covid19_new_york_2024_fixture_review_application_task.jsonc",
            "config_used": "configs/examples/covid19_new_york_2024_fixture_review_application_task.jsonc",
            "session_dir": _make_session(
                sessions_root,
                name="covid19_ny",
                disease="COVID-19",
                location="New York",
                start_date="2024",
                end_date="2024",
                search_mode="fixture",
                search_provider="fixture",
                live_search=False,
                live_fetch=False,
                discovery_method="fixture_search_result",
            ),
            "acceptance_status": "PASSED",
        },
        {
            "case_name": "Dengue / Florida / 2025",
            "command_used": "python -m hdc_workflow.cli collect --config configs\\examples\\dengue_florida_2025_fixture_review_application_task.jsonc",
            "config_used": "configs/examples/dengue_florida_2025_fixture_review_application_task.jsonc",
            "session_dir": _make_session(
                sessions_root,
                name="dengue_fl",
                disease="Dengue",
                location="Florida",
                start_date="2025",
                end_date="2025",
                search_mode="fixture",
                search_provider="fixture",
                live_search=False,
                live_fetch=False,
                discovery_method="fixture_search_result",
            ),
            "acceptance_status": "PASSED",
        },
    ]

    rows = build_acceptance_matrix(cases)

    assert [row["case_name"] for row in rows] == [
        "Hantavirus / New Mexico / 2020-2026",
        "COVID-19 / New York / 2024",
        "Dengue / Florida / 2025",
    ]
    for row in rows:
        assert row["structured_task_disease"]
        assert row["structured_task_location"]
        assert row["disease_intelligence_standard_name"]
        assert row["profile_schema_generation_method"]
        assert row["planned_query_count"] == 10
        assert row["source_registry_count"] == 2
        assert row["source_credibility_assessed_count"] == 3
        assert row["document_count"] == 1
        assert row["usable_partial_document_count"] == 1
        assert row["evidence_chunk_count"] == 1
        assert row["raw_record_count"] == 1
        assert row["validated_record_count"] == 1
        assert row["normalized_record_count"] == 1
        assert row["event_cluster_count"] == 1
        assert row["validation_result_count"] == 1
        assert row["workflow_console_path"].endswith("hdc_workflow_console.html")
        assert "workflow_run_summary" in row["key_diagnostics_paths"]

    covid = next(row for row in rows if row["structured_task_disease"] == "COVID-19")
    assert covid["disease_values_in_records"] == {"COVID-19": 1}
    assert covid["search_derived_candidate_count"] == 1

    json_path = tmp_path / "matrix.json"
    csv_path = tmp_path / "matrix.csv"
    manifest = write_acceptance_matrix(rows, json_path=json_path, csv_path=csv_path)

    assert manifest["row_count"] == 3
    assert json.loads(json_path.read_text(encoding="utf-8"))[0]["case_name"].startswith("Hantavirus")
    assert "case_name" in csv_path.read_text(encoding="utf-8").splitlines()[0]


def test_collect_print_config_only_preserves_config_user_request_without_structured_overrides():
    result = _run(
        [
            "collect",
            "--config",
            "configs/examples/covid19_new_york_2024_fixture_review_application_task.jsonc",
            "--print-config-only",
        ]
    )

    assert result.returncode == 0, result.stderr
    assert "Collect COVID-19 data for New York in 2024, detect anomalies" in result.stdout
    assert "Collect COVID-19 data for New York from 2024 to 2024" not in result.stdout


def test_collect_print_config_only_applies_explicit_structured_task_overrides():
    result = _run(
        [
            "collect",
            "--config",
            "configs/examples/covid19_new_york_2024_fixture_review_application_task.jsonc",
            "--disease",
            "dengue",
            "--location",
            "Florida",
            "--start-date",
            "2025",
            "--end-date",
            "2025",
            "--target-field",
            "deaths",
            "--print-config-only",
        ]
    )

    assert result.returncode == 0, result.stderr
    assert "Collect dengue data for Florida from 2025 to 2025" in result.stdout
    assert '"disease": "dengue"' in result.stdout
    assert '"location": "Florida"' in result.stdout


def test_stage13_release_docs_are_not_hantavirus_only():
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    guide = (PROJECT_ROOT / "docs" / "user_guide.md").read_text(encoding="utf-8")
    notebook = (PROJECT_ROOT / "examples" / "notebooks" / "data_collection_workflow_quickstart.md").read_text(
        encoding="utf-8"
    )

    assert readme.startswith("# data collection workflow")
    first_section = readme.split("##", 1)[0]
    assert "hantavirus-only" not in first_section.lower()
    assert "COVID-19" in first_section
    assert "dengue" in first_section.lower()
    assert "API keys" in readme
    assert "final_dataset_post_review" in readme
    assert "workflow console" in readme.lower()

    for section in (
        "Installation",
        "CLI commands",
        "Running offline fixture examples",
        "Running live search examples",
        "Environment variables",
        "Human review decision files",
        "Inspecting, reviewing, and exporting runs",
        "Output artifacts",
        "Workflow console",
        "Safety and limitations",
        "Troubleshooting",
    ):
        assert section in guide

    assert "data collection workflow" in notebook
    assert "not medical advice" in notebook
