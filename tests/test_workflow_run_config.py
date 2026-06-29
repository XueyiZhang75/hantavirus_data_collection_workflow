"""Tests for centralized HDC workflow runtime configuration."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_SRC = _PROJECT_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))


def test_default_workflow_run_config_drives_env_and_studio_input():
    from hdc_workflow.workflow_run_config import (
        DEFAULT_WORKFLOW_RUN_CONFIG_PATH,
        load_workflow_run_config,
        validation_records_path_from_config,
        workflow_initial_state_from_config,
        workflow_output_dir_from_config,
        workflow_run_config_with_overrides,
        workflow_run_env_from_config,
    )

    assert DEFAULT_WORKFLOW_RUN_CONFIG_PATH.exists()
    assert DEFAULT_WORKFLOW_RUN_CONFIG_PATH.suffix == ".jsonc"
    config = load_workflow_run_config()

    assert config["workflow"]["graph_name"] == "hantavirus_data_collection_workflow"
    assert config["workflow"]["collection_mode"] == "masked_validation"
    assert config["user_request"].startswith("Collect data on hantavirus")
    assert config["live_web"]["enabled"] is True
    assert config["llm"]["provider"] == "anthropic"
    assert config["llm"]["model"] == "claude-sonnet-4-6"
    assert config["llm"]["source_planning_enabled"] is True
    assert config["llm"]["source_critic_enabled"] is True
    assert config["llm"]["structured_extraction_enabled"] is True
    assert config["llm"]["source_identity"]["enabled"] is True
    assert config["llm"]["source_identity"]["require_llm"] is True
    assert config["llm"]["source_identity"]["allow_deterministic_fallback"] is False
    assert config["disease_intelligence"]["llm_enabled"] is True
    assert config["disease_intelligence"]["force_llm"] is True
    assert config["disease_intelligence"]["fallback_to_curated"] is True
    assert config["output"]["sessionized"] is True
    assert config["output"]["auto_build_console"] is True
    assert config["validation"]["allow_incompatible_validation_records"] is False

    env = workflow_run_env_from_config(config)
    assert env["HDC_COLLECTION_MODE"] == "masked_validation"
    assert env["HDC_USE_FIXTURE_DOCUMENTS"] == "false"
    assert env["HDC_ENABLE_LIVE_FETCH"] == "true"
    assert env["HDC_ENABLE_LLM_DISEASE_INTELLIGENCE"] == "true"
    assert env["HDC_DISEASE_INTELLIGENCE_FORCE_LLM"] == "true"
    assert env["HDC_DISEASE_INTELLIGENCE_FALLBACK_TO_CURATED"] == "true"
    assert env["HDC_ENABLE_LLM_SOURCE_PLANNING"] == "true"
    assert env["HDC_ENABLE_LLM_SOURCE_CRITIC"] == "true"
    assert env["HDC_ENABLE_LLM_SOURCE_IDENTITY"] == "true"
    assert env["HDC_LLM_SOURCE_IDENTITY_REQUIRE_LLM"] == "true"
    assert env["HDC_LLM_SOURCE_IDENTITY_ALLOW_DETERMINISTIC_FALLBACK"] == "false"
    assert env["HDC_ENABLE_LLM_EXTRACTION"] == "true"
    assert env["HDC_ALLOW_INCOMPATIBLE_VALIDATION_RECORDS"] == "false"
    assert env["HDC_HUMAN_REVIEW_ENABLED"] == "false"
    assert env["HDC_FETCH_ALLOW_NEEDS_REVIEW"] == "true"
    assert env["HDC_VALIDATION_MODE"] == "live_cross_source"
    assert env["HDC_EXTERNAL_FETCH_ENABLED"] == "true"
    assert env["HDC_LLM_PROVIDER"] == "anthropic"
    assert env["HDC_LLM_MODEL"] == "claude-sonnet-4-6"
    assert env["HDC_LLM_MUST_FETCH_MIN_CHUNKS_PER_SOURCE"] == "6"
    assert env["HDC_LLM_OFFICIAL_EXTRACTION_MAX_CHUNKS"] == "30"
    assert env["HDC_DIRECT_COLLECTION_ENABLE_AUDIT_VALIDATION"] == "false"
    assert env["HDC_SOURCE_ID_ALLOWLIST"].split(",") == config["source_sets"][
        "workflow_source_ids"
    ]
    assert Path(env["HDC_SEED_SOURCE_OVERLAY_PATH"]).exists()
    assert Path(env["HDC_SOURCE_ROLE_POLICY_OVERLAY_PATH"]).exists()
    assert validation_records_path_from_config(config) is None

    state = workflow_initial_state_from_config(config, include_empty_fields=False)
    assert state["user_request"] == config["user_request"]
    assert state["structured_task"] == config["structured_task"]
    assert state["structured_task"]["disease"] == "hantavirus"
    assert state["structured_task"]["location"] == "New Mexico"
    assert state["human_review_enabled"] is False

    override_request = "Collect dengue data for Florida in 2025."
    overridden = workflow_run_config_with_overrides(
        config,
        user_request=override_request,
    )
    assert overridden["user_request"] == override_request
    assert overridden["structured_task"]["user_request"] == override_request
    assert overridden["structured_task"]["disease"] == "hantavirus"

    output_dir = workflow_output_dir_from_config(config, session_id="test_session")
    assert output_dir == (
        _PROJECT_ROOT
        / "outputs"
        / "sessions"
        / "test_session"
    )

    validation_override = dict(config)
    validation_override["validation"] = {
        "allow_incompatible_validation_records": True,
        "mode": "held_out_file",
        "held_out_records_path": "src/hdc_workflow/resources/live_case_studies/new_mexico_hps_ground_truth_records.csv",
    }
    env_override = workflow_run_env_from_config(validation_override)
    assert env_override["HDC_ALLOW_INCOMPATIBLE_VALIDATION_RECORDS"] == "true"
    assert env_override["HDC_VALIDATION_MODE"] == "held_out_file"
    assert validation_records_path_from_config(validation_override).exists()


def test_direct_collection_config_maps_protected_extraction_budget_to_env():
    from hdc_workflow.workflow_run_config import workflow_run_env_from_config

    config = {
        "workflow": {
            "collection_mode": "direct_collection",
            "use_fixture_documents": False,
        },
        "llm": {
            "max_chunks": 20,
            "must_fetch_min_chunks_per_source": 4,
            "official_extraction_max_chunks": 12,
        },
        "validation": {
            "mode": "diagnostic_only",
            "direct_collection_enable_audit_validation": False,
        },
    }

    env = workflow_run_env_from_config(config)

    assert env["HDC_COLLECTION_MODE"] == "direct_collection"
    assert env["HDC_LLM_MAX_CHUNKS"] == "20"
    assert env["HDC_LLM_MUST_FETCH_MIN_CHUNKS_PER_SOURCE"] == "4"
    assert env["HDC_LLM_OFFICIAL_EXTRACTION_MAX_CHUNKS"] == "12"
    assert env["HDC_VALIDATION_MODE"] == "diagnostic_only"
    assert env["HDC_DIRECT_COLLECTION_ENABLE_AUDIT_VALIDATION"] == "false"


def test_low_level_workflow_env_defaults_disease_intelligence_to_resilient_fallback():
    from hdc_workflow.runtime_profile import workflow_run_env

    env = workflow_run_env()

    assert env["HDC_ENABLE_LLM_DISEASE_INTELLIGENCE"] == "true"
    assert env["HDC_DISEASE_INTELLIGENCE_FORCE_LLM"] == "true"
    assert env["HDC_DISEASE_INTELLIGENCE_FALLBACK_TO_CURATED"] == "true"


def test_jsonc_loader_preserves_urls_and_strips_comments(tmp_path):
    from hdc_workflow.workflow_run_config import load_workflow_run_config

    config_path = tmp_path / "profile.jsonc"
    config_path.write_text(
        """
        {
          // Comments outside strings are ignored.
          "profile_name": "jsonc_test",
          "workflow": {
            "seed_source_overlay_path": "src/hdc_workflow/resources/live_case_studies/new_mexico_hps_seed_sources.json"
          },
          "source_sets": {
            "workflow_source_ids": ["src_nmdoh_hps_2024_first_case"]
          },
          "example_url": "https://example.org/path//still-string"
        }
        """,
        encoding="utf-8",
    )

    config = load_workflow_run_config(config_path)
    assert config["profile_name"] == "jsonc_test"
    assert config["example_url"] == "https://example.org/path//still-string"
    assert config["source_sets"]["workflow_source_ids"] == [
        "src_nmdoh_hps_2024_first_case"
    ]


def test_custom_live_config_does_not_inherit_new_mexico_sources(tmp_path):
    from hdc_workflow.workflow_run_config import (
        load_workflow_run_config,
        workflow_run_env_from_config,
    )

    config_path = tmp_path / "new_york_live.jsonc"
    config_path.write_text(
        """
        {
          "profile_name": "new_york_live",
          "workflow": {
            "collection_mode": "standard",
            "use_fixture_documents": false
          },
          "structured_task": {
            "disease": "hantavirus",
            "location": "New York",
            "start_date": "2024",
            "end_date": "2026"
          },
          "source_search": {
            "enabled": true,
            "mode": "live",
            "combine_with_seed_catalog": false
          },
          "source_sets": {
            "source_id_allowlist_enabled": false
          },
          "validation": {
            "mode": "live_cross_source",
            "held_out_records_path": null
          }
        }
        """,
        encoding="utf-8",
    )

    config = load_workflow_run_config(config_path)
    env = workflow_run_env_from_config(config)

    assert env["HDC_SEED_SOURCE_OVERLAY_PATH"] == ""
    assert env["HDC_SOURCE_ROLE_POLICY_OVERLAY_PATH"] == ""
    assert env["HDC_SOURCE_ID_ALLOWLIST"] == ""
    assert "new_mexico" not in str(env).lower()


def test_live_cross_source_config_does_not_default_to_new_mexico_validation():
    from hdc_workflow.validation_source_compatibility import (
        resolve_task_compatible_validation_records,
    )
    from hdc_workflow.workflow_run_config import (
        validation_records_path_from_config,
        workflow_initial_state_from_config,
    )

    config = {
        "workflow": {"collection_mode": "standard", "use_fixture_documents": False},
        "structured_task": {
            "disease": "hantavirus",
            "location": "New York",
            "start_date": "2024",
            "end_date": "2026",
        },
        "validation": {"mode": "live_cross_source", "held_out_records_path": None},
    }

    assert validation_records_path_from_config(config) is None
    state = workflow_initial_state_from_config(config)
    resolved = resolve_task_compatible_validation_records(
        validation_records=[],
        state_or_task_context=state,
        validation_records_path=None,
        validation_records_path_requested=None,
        validation_records_explicit=False,
        validation_mode="live_cross_source",
    )

    summary = resolved["validation_source_compatibility_summary"]
    assert summary["validation_mode"] == "live_cross_source"
    assert summary["validation_records_path"] is None
    assert summary["validation_records_source"] == "none"
    assert summary["compatibility_status"] == "live_validation_pending"
    assert "New Mexico" not in str(summary)
