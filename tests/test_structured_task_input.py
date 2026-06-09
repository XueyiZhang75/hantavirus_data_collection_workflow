"""Stage 1 tests for structured task input."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_SRC = _PROJECT_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))


def test_structured_task_model_accepts_required_fields():
    from hdc_workflow.models import StructuredTaskInput

    task = StructuredTaskInput(
        disease="COVID-19",
        location="New York",
        start_date="2024",
        end_date="2024",
        target_fields=["cases_confirmed", "deaths", "date_reported"],
        source_preferences=["official_public_health_agency"],
        collection_mode="standard",
        user_request="Collect COVID-19 data for New York in 2024.",
        run_label="covid19_new_york_2024",
    )

    assert task.disease == "COVID-19"
    assert task.location == "New York"
    assert task.target_fields == ["cases_confirmed", "deaths", "date_reported"]


def test_task_intake_structured_fields_override_legacy_user_request():
    from hdc_workflow.nodes.task_scope import task_intake_and_scope_planning

    result = task_intake_and_scope_planning(
        {
            "user_request": "Collect hantavirus data from New Mexico.",
            "structured_task": {
                "disease": "COVID-19",
                "location": "New York",
                "start_date": "2024",
                "end_date": "2024",
                "target_fields": ["cases_confirmed", "deaths", "date_reported"],
                "source_preferences": ["official_public_health_agency"],
                "collection_mode": "standard",
                "user_request": "Collect COVID-19 data for New York in 2024.",
                "run_label": "covid19_new_york_2024",
            },
            "collection_trace": [],
        }
    )

    spec = result["collection_spec"]
    assert spec["disease"] == "COVID-19"
    assert spec["geography"] == "New York"
    assert spec["time_window"] == "2024"
    assert spec["required_fields"] == [
        "cases_confirmed",
        "deaths",
        "date_reported",
    ]
    assert spec["source_priority"] == ["official_public_health_agency"]
    assert spec["collection_mode"] == "standard"
    assert spec["run_label"] == "covid19_new_york_2024"


def test_task_intake_preserves_distinct_dengue_task():
    from hdc_workflow.nodes.task_scope import task_intake_and_scope_planning

    result = task_intake_and_scope_planning(
        {
            "structured_task": {
                "disease": "dengue",
                "location": "Florida",
                "start_date": "2025",
                "end_date": "2025",
                "target_fields": ["cases_unspecified", "deaths", "source_url"],
                "source_preferences": ["official_public_health_agency"],
                "collection_mode": "standard",
                "user_request": "Collect dengue data for Florida in 2025.",
                "run_label": "dengue_florida_2025",
            },
            "collection_trace": [],
        }
    )

    spec = result["collection_spec"]
    assert spec["disease"] == "dengue"
    assert spec["geography"] == "Florida"
    assert spec["time_window"] == "2025"
    assert spec["data_focus"] == "human dengue case, outbreak, and surveillance data"


def test_non_hantavirus_task_emits_remaining_future_stage_warnings():
    from hdc_workflow.nodes.task_scope import task_intake_and_scope_planning

    result = task_intake_and_scope_planning(
        {
            "structured_task": {
                "disease": "dengue",
                "location": "Florida",
                "start_date": "2025",
                "end_date": "2025",
                "target_fields": ["cases_unspecified", "deaths", "source_url"],
                "collection_mode": "standard",
                "user_request": "Collect dengue data for Florida in 2025.",
                "run_label": "dengue_florida_2025",
            },
            "collection_trace": [],
        }
    )

    expected = {
        "source_discovery_not_yet_disease_generic",
        "extraction_record_model_still_hantavirus_named",
    }
    stale = {
        "non_hantavirus_task_with_hantavirus_profile_resources",
        "profile_schema_not_yet_generalized",
    }
    spec_warnings = set(result["collection_spec"]["task_input_warnings"])
    summary_warnings = set(result["task_intake_summary"]["warnings"])
    trace_warnings = set(result["collection_trace"][-1]["metadata"]["warnings"])

    assert expected.issubset(spec_warnings)
    assert expected.issubset(summary_warnings)
    assert expected.issubset(trace_warnings)
    assert stale.isdisjoint(spec_warnings)
    assert stale.isdisjoint(summary_warnings)
    assert stale.isdisjoint(trace_warnings)


def test_final_package_policy_includes_task_intake_summary_for_audit():
    from hdc_workflow.config import load_final_package_policy

    policy = load_final_package_policy()

    assert "task_intake_summary" in policy["workflow_summary_fields"]


def test_task_intake_default_remains_hantavirus_compatible():
    from hdc_workflow.nodes.task_scope import task_intake_and_scope_planning

    result = task_intake_and_scope_planning(
        {
            "user_request": (
                "Collect global human hantavirus case, outbreak, and surveillance "
                "data from 2020 to 2026."
            ),
            "collection_trace": [],
        }
    )

    spec = result["collection_spec"]
    assert spec["disease"] == "Hantavirus disease"
    assert spec["geography"] == "global"
    assert spec["time_window"] == "2020-2026"


def test_workflow_initial_state_from_config_includes_structured_task():
    from hdc_workflow.workflow_run_config import (
        load_workflow_run_config,
        workflow_initial_state_from_config,
    )

    config = load_workflow_run_config()
    state = workflow_initial_state_from_config(config, include_empty_fields=False)

    assert state["user_request"] == config["user_request"]
    assert state["structured_task"] == config["structured_task"]
    assert state["structured_task"]["disease"] == "hantavirus"
    assert state["structured_task"]["location"] == "New Mexico"


def _run_full_graph_from_example_config(config_name: str) -> dict:
    from hdc_workflow.graph import build_graph
    from hdc_workflow.workflow_run_config import (
        load_workflow_run_config,
        temporary_workflow_env,
        workflow_initial_state_from_config,
        workflow_run_env_from_config,
    )

    config = load_workflow_run_config(_PROJECT_ROOT / "configs" / "examples" / config_name)
    env_updates = workflow_run_env_from_config(config)

    assert env_updates["HDC_USE_FIXTURE_DOCUMENTS"] == "true"
    assert env_updates["HDC_ENABLE_LIVE_FETCH"] == "false"
    assert env_updates["HDC_ENABLE_LLM_SOURCE_PLANNING"] == "false"
    assert env_updates["HDC_ENABLE_LLM_SOURCE_CRITIC"] == "false"
    assert env_updates["HDC_ENABLE_LLM_EXTRACTION"] == "false"

    with temporary_workflow_env(env_updates):
        return build_graph().invoke(workflow_initial_state_from_config(config))


def _assert_full_graph_non_hantavirus_task(
    result: dict,
    *,
    expected_disease: str,
    expected_location: str,
    expected_time_window: str,
) -> None:
    expected_warnings = {
        "source_discovery_not_yet_disease_generic",
        "extraction_record_model_still_hantavirus_named",
    }
    stale_warnings = {
        "profile_schema_not_yet_generalized",
        "non_hantavirus_task_with_hantavirus_profile_resources",
    }

    spec = result.get("collection_spec") or {}
    assert spec
    assert spec["disease"] == expected_disease
    assert spec["geography"] == expected_location
    assert spec["time_window"] == expected_time_window
    spec_warnings = set(spec.get("task_input_warnings") or [])
    assert expected_warnings.issubset(spec_warnings)
    assert stale_warnings.isdisjoint(spec_warnings)

    package = result.get("final_data_package") or {}
    assert package
    metadata = package.get("package_metadata") or {}
    assert metadata["disease"] == expected_disease
    assert metadata["geography"] == expected_location
    assert metadata["time_window"] == expected_time_window

    summaries = package.get("workflow_summaries") or {}
    intake_summary = summaries.get("task_intake_summary") or {}
    assert intake_summary["disease"] == expected_disease
    assert intake_summary["location"] == expected_location
    assert intake_summary["time_window"] == expected_time_window
    intake_warnings = set(intake_summary.get("warnings") or [])
    assert expected_warnings.issubset(intake_warnings)
    assert stale_warnings.isdisjoint(intake_warnings)
    profile_schema_summary = summaries.get("profile_schema_summary") or {}
    profile_warnings = set(profile_schema_summary.get("warnings") or [])
    assert expected_warnings.issubset(profile_warnings)
    assert stale_warnings.isdisjoint(profile_warnings)

    trace = package.get("collection_trace") or result.get("collection_trace") or []
    assert trace
    trace_warning_sets = [
        set((event.get("metadata") or {}).get("warnings") or [])
        for event in trace
    ]
    assert any(expected_warnings.issubset(warnings) for warnings in trace_warning_sets)
    assert all(stale_warnings.isdisjoint(warnings) for warnings in trace_warning_sets)


def test_full_graph_offline_covid19_new_york_preserves_task_metadata():
    result = _run_full_graph_from_example_config("covid19_new_york_2024_task.jsonc")

    _assert_full_graph_non_hantavirus_task(
        result,
        expected_disease="COVID-19",
        expected_location="New York",
        expected_time_window="2024",
    )


def test_full_graph_offline_dengue_florida_preserves_task_metadata():
    result = _run_full_graph_from_example_config("dengue_florida_2025_task.jsonc")

    _assert_full_graph_non_hantavirus_task(
        result,
        expected_disease="dengue",
        expected_location="Florida",
        expected_time_window="2025",
    )
