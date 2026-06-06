"""Offline-safe tests for the Stage 4B controlled LLM source demo script."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_SCRIPT = _PROJECT_ROOT / "scripts" / "run_agentic_llm_source_demo.py"


def _run_script(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(_SCRIPT), *args],
        cwd=_PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )


def test_agentic_llm_source_demo_script_exists():
    assert _SCRIPT.exists(), f"missing {_SCRIPT}"


def test_agentic_llm_source_demo_requires_allow_llm_by_default():
    result = _run_script("--scenario", "mv_hondius")

    assert result.returncode != 0
    assert "Pass --allow-llm" in result.stderr
    assert "dry-run" in result.stderr


def test_agentic_llm_source_demo_dry_run_does_not_call_llm():
    result = _run_script("--dry-run", "--scenario", "mv_hondius")

    assert result.returncode == 0
    assert "dry run only" in result.stdout.lower()
    assert "No LLM will be called" in result.stdout
    assert "HDC_ENABLE_LLM_SOURCE_PLANNING" in result.stdout
    assert "HDC_ENABLE_LLM_SOURCE_CRITIC" in result.stdout
    assert "HDC_ENABLE_LLM_EXTRACTION" in result.stdout
    assert "HDC_ENABLE_LIVE_FETCH" in result.stdout
    assert "API_KEY" not in result.stdout


def test_agentic_llm_source_demo_script_safety_text():
    text = _SCRIPT.read_text(encoding="utf-8")

    assert "load_dotenv" not in text
    assert "HDC_ENABLE_LLM_SOURCE_PLANNING" in text
    assert "HDC_ENABLE_LLM_SOURCE_CRITIC" in text
    assert "HDC_ENABLE_LLM_EXTRACTION=false" in text
    assert "HDC_ENABLE_LIVE_FETCH=false" in text
    assert '"HDC_ENABLE_LLM_EXTRACTION": "false"' in text
    assert '"HDC_ENABLE_LIVE_FETCH": "false"' in text
    assert "run_mv_hondius_live_masked_pilot" not in text


def test_agentic_llm_source_demo_scenarios_exist():
    text = _SCRIPT.read_text(encoding="utf-8")

    assert '"mv_hondius"' in text
    assert '"new_mexico_hps"' in text
    assert '"global_hantavirus"' in text
    assert "mv_hondius_seed_sources.json" in text
    assert "mv_hondius_source_role_policy_overlay.json" in text
