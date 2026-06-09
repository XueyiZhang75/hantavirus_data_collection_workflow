from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = [sys.executable, "scripts/run_interactive_workflow.py"]


def _env(extra: dict[str, str] | None = None) -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT / "src") + os.pathsep + env.get("PYTHONPATH", "")
    if extra:
        env.update(extra)
    return env


def _run(args: list[str], *, input_text: str = "", env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        SCRIPT + args,
        cwd=PROJECT_ROOT,
        env=env or _env(),
        input=input_text,
        text=True,
        encoding="utf-8",
        capture_output=True,
        timeout=120,
    )


def _extract_preview_json(stdout: str) -> dict:
    marker = "sanitized_config_json:"
    assert marker in stdout
    text = stdout.split(marker, 1)[1].strip()
    return json.loads(text)


def test_interactive_help_hides_target_field_option_from_normal_users():
    result = _run(["--help"])

    assert result.returncode == 0, result.stdout + result.stderr
    assert "--target-field" not in result.stdout
    assert "target fields" not in result.stdout.lower()


def test_interactive_script_generates_real_workflow_config_from_prompts_without_leaking_keys():
    env = _env(
        {
            "TAVILY_API_KEY": "tvly-test-key",
            "ANTHROPIC_API_KEY": "sk-ant-test-key",
        }
    )
    result = _run(
        ["--print-config-only"],
        input_text="\n".join(
            [
                "Orthoebolavirus zairense",
                "Democratic Republic of the Congo",
                "2022",
                "2026",
                "orthoebolavirus_drc_preview",
            ]
        )
        + "\n",
        env=env,
    )

    combined = result.stdout + result.stderr
    assert result.returncode == 0, combined
    assert "tvly-test-key" not in combined
    assert "sk-ant-test-key" not in combined

    preview = _extract_preview_json(result.stdout)
    assert preview["project_name"] == "data collection workflow"
    assert preview["api_keys"]["tavily_api_key_present"] is True
    assert preview["api_keys"]["llm_api_key_present"] is True

    config = preview["config"]
    assert config["structured_task"]["disease"] == "Orthoebolavirus zairense"
    assert config["structured_task"]["location"] == "Democratic Republic of the Congo"
    assert config["structured_task"]["start_date"] == "2022"
    assert config["structured_task"]["end_date"] == "2026"
    assert config["structured_task"]["target_fields"] == [
        "disease",
        "country",
        "subnational_location",
        "locality",
        "date_reported",
        "cases_confirmed",
        "cases_probable",
        "cases_suspected",
        "cases_unspecified",
        "deaths",
        "hospitalizations",
        "source_url",
        "source_type",
        "evidence_quote",
    ]
    assert config["workflow"]["use_fixture_documents"] is False
    assert config["source_search"]["enabled"] is True
    assert config["source_search"]["mode"] == "live"
    assert config["source_search"]["provider"] == "tavily"
    assert config["source_search"]["combine_with_seed_catalog"] is False
    assert config["live_web"]["enabled"] is True
    assert config["content_fetch"]["fetch_search_derived_sources"] is True
    assert config["llm"]["source_planning_enabled"] is True
    assert config["llm"]["source_critic_enabled"] is True
    assert config["llm"]["structured_extraction_enabled"] is True
    assert config["llm"]["source_credibility"]["enabled"] is True
    assert config["disease_intelligence"]["llm_enabled"] is True
    assert config["output"]["session_id"] == "orthoebolavirus_drc_preview"


def test_interactive_script_accepts_noninteractive_arguments_for_preview():
    result = _run(
        [
            "--disease",
            "COVID-19",
            "--location",
            "New York",
            "--start-date",
            "2024",
            "--end-date",
            "2024",
            "--target-field",
            "cases_confirmed",
            "--target-field",
            "deaths",
            "--session-id",
            "covid19_ny_preview",
            "--print-config-only",
        ],
        env=_env({"TAVILY_API_KEY": "tvly-test-key", "ANTHROPIC_API_KEY": "sk-ant-test-key"}),
    )

    assert result.returncode == 0, result.stdout + result.stderr
    config = _extract_preview_json(result.stdout)["config"]
    assert config["structured_task"]["disease"] == "COVID-19"
    assert config["structured_task"]["target_fields"] == ["cases_confirmed", "deaths"]
    assert config["source_search"]["mode"] == "live"
    assert config["llm"]["provider"] == "anthropic"


def test_interactive_script_normalizes_range_and_question_mark_session_id_without_field_prompt():
    result = _run(
        ["--print-config-only"],
        input_text="\n".join(
            [
                "hantavirus",
                "America",
                "2024-2026",
                "2026",
                "？",
            ]
        )
        + "\n",
        env=_env({"TAVILY_API_KEY": "tvly-test-key", "ANTHROPIC_API_KEY": "sk-ant-test-key"}),
    )

    combined = result.stdout + result.stderr
    assert result.returncode == 0, combined
    assert "Interpreted Start year/date '2024-2026' as date range 2024 to 2026." in combined
    assert "Using safe session id:" in combined
    assert "Target fields" not in combined

    config = _extract_preview_json(result.stdout)["config"]
    assert config["structured_task"]["start_date"] == "2024"
    assert config["structured_task"]["end_date"] == "2026"
    assert config["structured_task"]["target_fields"] == [
        "disease",
        "country",
        "subnational_location",
        "locality",
        "date_reported",
        "cases_confirmed",
        "cases_probable",
        "cases_suspected",
        "cases_unspecified",
        "deaths",
        "hospitalizations",
        "source_url",
        "source_type",
        "evidence_quote",
    ]
    assert config["output"]["session_id"].startswith("hantavirus_america_2024_2026_")
    assert "？" not in config["output"]["session_id"]


def test_interactive_script_blocks_real_run_when_required_keys_are_missing():
    env = _env({"TAVILY_API_KEY": "", "ANTHROPIC_API_KEY": ""})
    result = _run(
        [
            "--disease",
            "hantavirus",
            "--location",
            "New Mexico",
            "--start-date",
            "2020",
            "--end-date",
            "2026",
            "--session-id",
            "missing_key_run",
        ],
        env=env,
    )

    combined = result.stdout + result.stderr
    assert result.returncode != 0
    assert "Missing required API key" in combined
    assert "TAVILY_API_KEY" in combined
    assert "ANTHROPIC_API_KEY" in combined
