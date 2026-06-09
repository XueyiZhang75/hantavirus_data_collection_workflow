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
    assert config["output"]["sessionized"] is True
    assert config["output"]["auto_build_console"] is True
    assert config["validation"]["allow_incompatible_validation_records"] is False

    env = workflow_run_env_from_config(config)
    assert env["HDC_COLLECTION_MODE"] == "masked_validation"
    assert env["HDC_USE_FIXTURE_DOCUMENTS"] == "false"
    assert env["HDC_ENABLE_LIVE_FETCH"] == "true"
    assert env["HDC_ENABLE_LLM_DISEASE_INTELLIGENCE"] == "false"
    assert env["HDC_ENABLE_LLM_SOURCE_PLANNING"] == "true"
    assert env["HDC_ENABLE_LLM_SOURCE_CRITIC"] == "true"
    assert env["HDC_ENABLE_LLM_EXTRACTION"] == "true"
    assert env["HDC_ALLOW_INCOMPATIBLE_VALIDATION_RECORDS"] == "false"
    assert env["HDC_LLM_PROVIDER"] == "anthropic"
    assert env["HDC_LLM_MODEL"] == "claude-sonnet-4-6"
    assert env["HDC_SOURCE_ID_ALLOWLIST"].split(",") == config["source_sets"][
        "workflow_source_ids"
    ]
    assert Path(env["HDC_SEED_SOURCE_OVERLAY_PATH"]).exists()
    assert Path(env["HDC_SOURCE_ROLE_POLICY_OVERLAY_PATH"]).exists()
    assert validation_records_path_from_config(config).exists()

    state = workflow_initial_state_from_config(config, include_empty_fields=False)
    assert state["user_request"] == config["user_request"]
    assert state["structured_task"] == config["structured_task"]
    assert state["structured_task"]["disease"] == "hantavirus"
    assert state["structured_task"]["location"] == "New Mexico"

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
    }
    env_override = workflow_run_env_from_config(validation_override)
    assert env_override["HDC_ALLOW_INCOMPATIBLE_VALIDATION_RECORDS"] == "true"


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
