"""Controlled live-source pilot (Step 15).

Replaces synthetic fixture documents with live HTTP fetches against a small
allowlist of official source IDs. Optionally calls Claude (Anthropic) or
OpenAI for structured extraction. Tests must NOT call this script.

Required external preconditions:
- Internet access.
- HDC_LLM_MODEL set to a real model in your provider account.
- ANTHROPIC_API_KEY (for provider=anthropic) or OPENAI_API_KEY (for openai).

NOTE: This pilot may contact external websites and a real LLM provider.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def _set_default(key: str, value: str) -> None:
    if not os.environ.get(key):
        os.environ[key] = value


_DEFAULT_ALLOWLIST = (
    "src_cdc_reported_cases,"
    "src_ecdc_surveillance_updates,"
    "src_ecdc_annual_report_2023,"
    "src_who_hantavirus_fact_sheet"
)

os.environ["HDC_USE_FIXTURE_DOCUMENTS"] = "false"
os.environ["HDC_ENABLE_LIVE_FETCH"] = "true"
_set_default("HDC_ENABLE_LLM_EXTRACTION", "true")
_set_default("HDC_LLM_PROVIDER", "anthropic")
_set_default("HDC_LLM_FALLBACK_TO_RULE_BASED", "true")
_set_default("HDC_SOURCE_ID_ALLOWLIST", _DEFAULT_ALLOWLIST)
_set_default("HDC_LLM_MAX_CHUNKS", "8")

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_SRC = _PROJECT_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))


def _validate_provider_credentials() -> tuple[str, str] | None:
    provider = (os.environ.get("HDC_LLM_PROVIDER") or "anthropic").strip().lower()
    model = (os.environ.get("HDC_LLM_MODEL") or "").strip()
    if provider == "anthropic":
        key = os.environ.get("ANTHROPIC_API_KEY") or ""
        if not key or not model:
            print(
                "Missing Anthropic configuration. Set ANTHROPIC_API_KEY and "
                "HDC_LLM_MODEL before running this pilot. Skipping."
            )
            return None
        return provider, model
    if provider == "openai":
        key = os.environ.get("OPENAI_API_KEY") or ""
        if not key or not model:
            print(
                "Missing OpenAI configuration. Set OPENAI_API_KEY and "
                "HDC_LLM_MODEL before running this pilot. Skipping."
            )
            return None
        return provider, model
    print(f"Unsupported HDC_LLM_PROVIDER='{provider}'. Skipping.")
    return None


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
    print("Live-source pilot: this run will CONTACT EXTERNAL WEBSITES")
    print("and call the configured LLM provider. Output is NOT a baseline")
    print("or evaluation benchmark — it is a controlled small-scale pilot.")
    print(sep)

    creds = _validate_provider_credentials()
    if creds is None:
        sys.exit(0)
    provider, model = creds

    from hdc_workflow.export import export_final_data_package  # noqa: E402
    from hdc_workflow.graph import build_graph  # noqa: E402

    print(f"provider: {provider}")
    print(f"model: {model}")
    print(f"source_id_allowlist: {os.environ.get('HDC_SOURCE_ID_ALLOWLIST')}")
    print(f"llm_max_chunks: {os.environ.get('HDC_LLM_MAX_CHUNKS')}")

    graph = build_graph()
    result = graph.invoke(_initial_state())

    for key in (
        "content_fetch_summary",
        "document_quality_summary",
        "evidence_chunking_summary",
        "data_presence_summary",
        "structured_extraction_summary",
        "llm_extraction_summary",
        "schema_validation_summary",
        "record_normalization_summary",
        "record_linking_summary",
        "cross_source_consistency_summary",
        "finalization_summary",
    ):
        print(sep)
        print(f"{key}:")
        print(json.dumps(result.get(key), indent=2))

    print(sep)
    print("counts:")
    for key in (
        "source_candidates",
        "source_registry",
        "content_fetch_requests",
        "documents",
        "evidence_chunks",
        "raw_records",
        "validated_records",
        "normalized_records",
        "linked_events",
        "conflicts",
        "human_review_queue",
    ):
        print(f"  - {key}: {len(result.get(key) or [])}")

    print(sep)
    print(f"current_route: {result.get('current_route')}")

    print(sep)
    print("first 10 documents:")
    for doc in (result.get("documents") or [])[:10]:
        ct_len = len(doc.get("clean_text") or "")
        print(
            f"  - {doc.get('source_id')} | "
            f"url={doc.get('url')} | "
            f"document_type={doc.get('document_type')} | "
            f"fetch_status={doc.get('fetch_status')} | "
            f"parse_status={doc.get('parse_status')} | "
            f"quality={doc.get('quality_status')} | "
            f"live={doc.get('is_live_fetched')} | "
            f"fixture={doc.get('is_fixture_document')} | "
            f"clean_text_len={ct_len} | "
            f"fetch_error={doc.get('fetch_error')}"
        )

    print(sep)
    print("first 10 evidence_chunks:")
    for chunk in (result.get("evidence_chunks") or [])[:10]:
        text_len = len(chunk.get("text") or "")
        print(
            f"  - {chunk.get('chunk_id')} | "
            f"source_id={chunk.get('source_id')} | "
            f"contains_target_data={chunk.get('contains_target_data')} | "
            f"data_types={chunk.get('data_types')} | "
            f"context_types={chunk.get('context_types')} | "
            f"confidence={chunk.get('confidence')} | "
            f"text_len={text_len}"
        )

    print(sep)
    print("first 10 raw_records:")
    for rec in (result.get("raw_records") or [])[:10]:
        print(
            f"  - {rec.get('record_id')} | "
            f"source_id={rec.get('source_id')} | "
            f"country={rec.get('country')} | "
            f"date_reported={rec.get('date_reported')} | "
            f"cases_confirmed={rec.get('cases_confirmed')} | "
            f"cases_probable={rec.get('cases_probable')} | "
            f"cases_suspected={rec.get('cases_suspected')} | "
            f"cases_unspecified={rec.get('cases_unspecified')} | "
            f"deaths={rec.get('deaths')} | "
            f"llm_used={rec.get('llm_used')} | "
            f"extraction_mode={rec.get('extraction_mode')}"
        )

    # Step 16.1 diagnostics: inspect temporal / statistical / geographic
    # fields that drive event-key construction and review routing.
    print(sep)
    print("first 10 raw_records (temporal/statistical/geographic fields):")
    for rec in (result.get("raw_records") or [])[:10]:
        print(
            f"  - {rec.get('record_id')} | "
            f"date_reported={rec.get('date_reported')} | "
            f"reporting_period={rec.get('reporting_period')} | "
            f"as_of_date={rec.get('as_of_date')} | "
            f"event_start_date={rec.get('event_start_date')} | "
            f"event_end_date={rec.get('event_end_date')} | "
            f"statistical_count_type={rec.get('statistical_count_type')} | "
            f"geographic_scope={rec.get('geographic_scope')} | "
            f"geographic_scope_type={rec.get('geographic_scope_type')}"
        )

    print(sep)
    print("first 10 normalized_records (anchor + scope fields):")
    for rec in (result.get("normalized_records") or [])[:10]:
        print(
            f"  - {rec.get('record_id')} | "
            f"country={rec.get('country')} | "
            f"date_reported={rec.get('date_reported')} | "
            f"reporting_period={rec.get('reporting_period')} | "
            f"as_of_date={rec.get('as_of_date')} | "
            f"date_anchor={rec.get('date_anchor')} | "
            f"date_anchor_field={rec.get('date_anchor_field')} | "
            f"statistical_count_type={rec.get('statistical_count_type')} | "
            f"geographic_scope={rec.get('geographic_scope')} | "
            f"geographic_scope_type={rec.get('geographic_scope_type')}"
        )

    package = result.get("final_data_package") or {}
    print(sep)
    print("final_data_package.package_metadata:")
    print(json.dumps(package.get("package_metadata"), indent=2))

    output_dir = Path(
        os.environ.get("HDC_LIVE_PILOT_OUTPUT_DIR")
        or _PROJECT_ROOT / "outputs" / "live_source_llm_pilot"
    )
    manifest = export_final_data_package(package, output_dir)

    print(sep)
    print("export manifest:")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
