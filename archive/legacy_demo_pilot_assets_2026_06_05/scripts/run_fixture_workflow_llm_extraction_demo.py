"""Optional manual demo: fixture mode + LLM-based structured extraction.

Tests must NOT call this script. It requires a real Anthropic Claude or
OpenAI API key plus a real model name. If either is missing, the script
exits cleanly without invoking the graph.

Set BEFORE running:

    HDC_USE_FIXTURE_DOCUMENTS=true
    HDC_ENABLE_LIVE_FETCH=false
    HDC_ENABLE_LLM_EXTRACTION=true
    HDC_LLM_PROVIDER=anthropic       # or openai
    HDC_LLM_MODEL=<your-model-name>
    ANTHROPIC_API_KEY=<key>          # or OPENAI_API_KEY=<key>

NOTE: Fixture mode uses synthetic local documents; they are NOT real public
health data.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

os.environ.setdefault("HDC_USE_FIXTURE_DOCUMENTS", "true")
os.environ.setdefault("HDC_ENABLE_LIVE_FETCH", "false")
os.environ.setdefault("HDC_ENABLE_LLM_EXTRACTION", "true")
os.environ.setdefault("HDC_LLM_PROVIDER", "anthropic")

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_SRC = _PROJECT_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))


def _exit_if_missing(provider: str, model: str) -> None:
    if provider == "anthropic":
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key or not model:
            print(
                "Missing configuration for Anthropic provider: set both "
                "ANTHROPIC_API_KEY and HDC_LLM_MODEL. Skipping LLM demo."
            )
            sys.exit(0)
        return
    if provider == "openai":
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key or not model:
            print(
                "Missing configuration for OpenAI provider: set both "
                "OPENAI_API_KEY and HDC_LLM_MODEL. Skipping LLM demo."
            )
            sys.exit(0)
        return
    print(f"Unsupported HDC_LLM_PROVIDER='{provider}'. Skipping LLM demo.")
    sys.exit(0)


def _initial_state() -> dict:
    return {
        "user_request": (
            "Collect global human hantavirus case, outbreak, and surveillance data "
            "from 2020 to 2026, including cases, deaths, dates, locations, source URLs, "
            "source types, and evidence quotes."
        ),
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


def main() -> None:
    sep = "=" * 72
    print(sep)
    print("This demo uses synthetic fixture documents; they are NOT real public")
    print("health data. LLM extraction is enabled via real provider credentials.")
    print(sep)

    provider = (os.environ.get("HDC_LLM_PROVIDER") or "anthropic").lower()
    model = (os.environ.get("HDC_LLM_MODEL") or "").strip()
    _exit_if_missing(provider, model)

    from hdc_workflow.graph import build_graph  # noqa: E402  (post env setup)

    graph = build_graph()
    result = graph.invoke(_initial_state())

    print(f"provider: {provider}")
    print(f"model: {model}")

    print(sep)
    print("structured_extraction_summary:")
    print(json.dumps(result.get("structured_extraction_summary"), indent=2))

    print(sep)
    print("llm_extraction_summary:")
    print(json.dumps(result.get("llm_extraction_summary"), indent=2))

    print(sep)
    print(
        f"raw_records count: {len(result.get('raw_records') or [])}\n"
        f"validated_records count: {len(result.get('validated_records') or [])}\n"
        f"normalized_records count: {len(result.get('normalized_records') or [])}\n"
        f"linked_events count: {len(result.get('linked_events') or [])}\n"
        f"conflicts count: {len(result.get('conflicts') or [])}"
    )

    package = result.get("final_data_package") or {}
    print(sep)
    print("final_data_package.package_metadata:")
    print(json.dumps(package.get("package_metadata"), indent=2))


if __name__ == "__main__":
    main()
