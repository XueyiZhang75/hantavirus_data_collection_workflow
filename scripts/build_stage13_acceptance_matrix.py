from __future__ import annotations

import argparse
from pathlib import Path

from hdc_workflow.acceptance import build_acceptance_matrix, write_acceptance_matrix


DEFAULT_CASES = [
    {
        "case_name": "Hantavirus / New Mexico / 2020-2026",
        "command_used": (
            "python -m hdc_workflow.cli collect --config "
            "configs\\hdc_workflow_run_config.jsonc --disable-all-llm "
            "--session-id stage13_hantavirus_cli_acceptance_no_llm_escalated"
        ),
        "config_used": "configs/hdc_workflow_run_config.jsonc",
        "session_dir": "outputs/sessions/stage13_hantavirus_cli_acceptance_no_llm_escalated",
        "acceptance_status": "PASSED",
        "notes": (
            "CLI compatibility rerun with network access; no live search and all LLM stages disabled. "
            "Non-escalated CLI run produced fetch_failed documents because of sandbox network restrictions."
        ),
    },
    {
        "case_name": "COVID-19 / New York / 2024",
        "command_used": (
            "python -m hdc_workflow.cli collect --config "
            "configs\\examples\\covid19_new_york_2024_live_review_smoke.jsonc "
            "--session-id stage13_covid19_live_acceptance_escalated"
        ),
        "config_used": "configs/examples/covid19_new_york_2024_live_review_smoke.jsonc",
        "session_dir": "outputs/sessions/stage13_covid19_live_acceptance_escalated",
        "acceptance_status": "PASSED",
        "notes": "Real Tavily live-search and controlled live-fetch acceptance run.",
    },
    {
        "case_name": "Dengue / Florida / 2025",
        "command_used": (
            "python -m hdc_workflow.cli collect --config "
            "configs\\examples\\dengue_florida_2025_live_review_smoke.jsonc "
            "--session-id stage13_dengue_live_acceptance_escalated"
        ),
        "config_used": "configs/examples/dengue_florida_2025_live_review_smoke.jsonc",
        "session_dir": "outputs/sessions/stage13_dengue_live_acceptance_escalated",
        "acceptance_status": "PASSED",
        "notes": "Real Tavily live-search and controlled live-fetch acceptance run.",
    },
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the Stage 13 acceptance matrix.")
    parser.add_argument(
        "--json-output",
        default="outputs/stage13_multidisease_acceptance_matrix.json",
        help="JSON output path.",
    )
    parser.add_argument(
        "--csv-output",
        default="outputs/stage13_multidisease_acceptance_matrix.csv",
        help="CSV output path.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows = build_acceptance_matrix(DEFAULT_CASES)
    manifest = write_acceptance_matrix(
        rows,
        json_path=Path(args.json_output),
        csv_path=Path(args.csv_output),
    )
    print(f"row_count: {manifest['row_count']}")
    print(f"json_path: {manifest['json_path']}")
    print(f"csv_path: {manifest['csv_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
