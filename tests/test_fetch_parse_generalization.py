"""Stage 7 tests for controlled fetch/parse generalization."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_SRC = _PROJECT_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))


STAGE7_ENV_KEYS = [
    "HDC_COLLECTION_MODE",
    "HDC_SOURCE_ID_ALLOWLIST",
    "HDC_ENABLE_LIVE_FETCH",
    "HDC_USE_FIXTURE_DOCUMENTS",
    "HDC_FETCH_SEARCH_DERIVED_SOURCES",
    "HDC_FETCH_MAX_SEARCH_DERIVED_SOURCES",
    "HDC_FETCH_MAX_TOTAL_SOURCES",
    "HDC_FETCH_MIN_CREDIBILITY_SCORE",
    "HDC_FETCH_ALLOWED_FINAL_ROLES",
    "HDC_FETCH_ALLOW_NEEDS_REVIEW",
    "HDC_FETCH_DOMAIN_ALLOWLIST",
    "HDC_FETCH_DOMAIN_BLOCKLIST",
    "HDC_FETCH_MAX_BYTES",
    "HDC_FETCH_USER_AGENT",
    "HDC_FETCH_PARSE_PDF_TEXT",
    "HDC_FETCH_PARSE_TABLES",
    "HDC_FETCH_STORE_RAW_TEXT",
    "HDC_CONTENT_FIXTURE_MAP_PATH",
    "HDC_SEARCH_MODE",
    "HDC_SEARCH_PROVIDER",
    "HDC_SEARCH_FIXTURE_PATH",
    "HDC_ENABLE_LIVE_SEARCH",
    "HDC_SEARCH_MAX_QUERIES",
    "HDC_SEARCH_MAX_RESULTS_PER_QUERY",
    "HDC_SEARCH_MAX_TOTAL_RESULTS",
    "HDC_SEARCH_COMBINE_WITH_SEED_CATALOG",
    "HDC_ENABLE_LLM_SOURCE_PLANNING",
    "HDC_ENABLE_LLM_SOURCE_CRITIC",
    "HDC_ENABLE_LLM_SOURCE_CREDIBILITY",
    "HDC_ENABLE_LLM_EXTRACTION",
]


def _clear_stage7_env(monkeypatch) -> None:
    for key in STAGE7_ENV_KEYS:
        monkeypatch.delenv(key, raising=False)


def _search_entry(
    source_id: str = "src_search_test",
    *,
    url: str = "https://health.ny.gov/example/covid-19-surveillance-2024",
    final_role: str = "collection",
    credibility_score: float = 0.88,
    credibility_level: str = "high",
    final_decision: str = "include_for_content_fetch",
    discovery_method: str = "fixture_search_result",
    source_type: str = "official_public_health_agency",
    ready: bool = True,
    requires_review: bool = False,
    human_review_recommended: bool = False,
    publisher: str = "New York State Department of Health",
) -> dict:
    return {
        "source_id": source_id,
        "canonical_url": url,
        "title": "Official surveillance update",
        "publisher": publisher,
        "source_type": source_type,
        "status": "ready_for_content_fetch" if ready else "needs_human_review",
        "final_screening_decision": final_decision,
        "ready_for_content_fetch": ready,
        "requires_human_review": requires_review,
        "discovery_method": discovery_method,
        "query_id": "q_official_001",
        "query_used": "COVID-19 New York 2024 official cases deaths",
        "search_provider": "fixture",
        "search_rank": 1,
        "provider_channel": "web_search",
        "role_hint": "collection",
        "planned_query_id": "q_official_001",
        "domain": "health.ny.gov",
        "source_role": "data_source",
        "source_role_final": final_role,
        "credibility_score": credibility_score,
        "credibility_level": credibility_level,
        "risk_flags": ["official_public_health_authority"],
        "human_review_recommended": human_review_recommended,
    }


def _state_with_sources(entries: list[dict]) -> dict:
    return {
        "source_registry": entries,
        "collection_trace": [],
        "documents": [],
        "content_fetch_requests": [],
    }


def _fixture_path(name: str) -> Path:
    return _PROJECT_ROOT / "src" / "hdc_workflow" / "resources" / "content_fixtures" / name


def test_default_behavior_does_not_fetch_search_derived_sources(monkeypatch):
    from hdc_workflow.nodes.content_processing import content_fetch_and_parse

    _clear_stage7_env(monkeypatch)
    result = content_fetch_and_parse(_state_with_sources([_search_entry()]))

    assert result.get("content_fetch_requests") == []
    assert result.get("documents") == []
    summary = result.get("content_fetch_summary") or {}
    assert summary["search_derived_fetch_enabled"] is False
    assert summary["search_derived_input_count"] == 1
    assert summary["selected_search_derived_fetch_count"] == 0
    assert summary["skipped_search_derived_fetch_disabled_count"] == 1


def test_eligible_search_derived_source_becomes_fetch_request(monkeypatch):
    from hdc_workflow.nodes.content_processing import content_fetch_and_parse

    _clear_stage7_env(monkeypatch)
    monkeypatch.setenv("HDC_FETCH_SEARCH_DERIVED_SOURCES", "true")
    result = content_fetch_and_parse(_state_with_sources([_search_entry()]))

    requests = result.get("content_fetch_requests") or []
    assert len(requests) == 1
    request = requests[0]
    assert request["source_id"] == "src_search_test"
    assert request["canonical_url"] == "https://health.ny.gov/example/covid-19-surveillance-2024"
    assert request["discovery_method"] == "fixture_search_result"
    assert request["source_role_final"] == "collection"
    assert request["credibility_score"] == 0.88
    assert request["query_id"] == "q_official_001"
    assert request["query_used"]


def test_low_credibility_excluded_endpoint_and_review_sources_are_not_fetched(monkeypatch):
    from hdc_workflow.nodes.content_processing import content_fetch_and_parse

    _clear_stage7_env(monkeypatch)
    monkeypatch.setenv("HDC_FETCH_SEARCH_DERIVED_SOURCES", "true")
    entries = [
        _search_entry("src_excluded", final_role="excluded"),
        _search_entry("src_endpoint", final_role="search_endpoint", publisher="PubMed"),
        _search_entry("src_review", final_role="needs_human_review", credibility_level="needs_review"),
        _search_entry("src_low_score", credibility_score=0.30, credibility_level="low"),
    ]

    result = content_fetch_and_parse(_state_with_sources(entries))

    assert result.get("content_fetch_requests") == []
    summary = result.get("content_fetch_summary") or {}
    reasons = summary.get("skipped_search_derived_by_reason_counts") or {}
    assert reasons["final_role_excluded"] == 1
    assert reasons["final_role_search_endpoint"] == 1
    assert reasons["needs_review_not_allowed"] == 1
    assert reasons["credibility_score_below_threshold"] == 1


def test_max_search_derived_fetch_limit_is_enforced(monkeypatch):
    from hdc_workflow.nodes.content_processing import content_fetch_and_parse

    _clear_stage7_env(monkeypatch)
    monkeypatch.setenv("HDC_FETCH_SEARCH_DERIVED_SOURCES", "true")
    monkeypatch.setenv("HDC_FETCH_MAX_SEARCH_DERIVED_SOURCES", "1")
    entries = [
        _search_entry("src_one", url="https://health.ny.gov/example/one"),
        _search_entry("src_two", url="https://health.ny.gov/example/two"),
    ]

    result = content_fetch_and_parse(_state_with_sources(entries))

    requests = result.get("content_fetch_requests") or []
    assert len(requests) == 1
    summary = result.get("content_fetch_summary") or {}
    assert summary["selected_search_derived_fetch_count"] == 1
    assert summary["skipped_search_derived_fetch_limit_count"] == 1
    assert summary["skipped_search_derived_by_reason_counts"]["max_search_derived_sources_reached"] == 1


def test_html_parser_extracts_title_text_table_and_date():
    from hdc_workflow.nodes.content_processing import _parse_document_content

    fixture = _fixture_path("covid19_ny_official_page.html")
    result = _parse_document_content(
        fixture.read_bytes(),
        url="https://health.ny.gov/example/covid-19-surveillance-2024",
        content_type="text/html; charset=utf-8",
        parse_pdf_text=True,
        parse_tables=True,
    )

    assert result["parser_used"] == "html_stdlib_parser"
    assert result["parse_status"] == "parsed_html"
    assert "New York COVID-19 Surveillance Update 2024" in result["title"]
    assert "COVID-19" in result["clean_text"] or "SARS-CoV-2" in result["clean_text"]
    assert "New York" in result["clean_text"]
    assert result["published_date"] == "2024-06-01"
    assert result["table_count"] > 0


def test_dengue_html_fixture_parses_correctly():
    from hdc_workflow.nodes.content_processing import _parse_document_content

    fixture = _fixture_path("dengue_florida_official_page.html")
    result = _parse_document_content(
        fixture.read_bytes(),
        url="https://www.floridahealth.gov/example/dengue-surveillance-2025",
        content_type="text/html; charset=utf-8",
        parse_pdf_text=True,
        parse_tables=True,
    )

    assert result["parser_used"] == "html_stdlib_parser"
    assert result["parse_status"] == "parsed_html"
    assert "Florida Dengue Surveillance Update 2025" in result["title"]
    assert "dengue" in result["clean_text"].lower() or "denv" in result["clean_text"].lower()
    assert "Florida" in result["clean_text"]
    assert result["table_count"] > 0


def test_pdf_parser_gracefully_parses_or_defers():
    from hdc_workflow.nodes.content_processing import _parse_document_content

    result = _parse_document_content(
        b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\n%%EOF",
        url="https://example.org/report.pdf",
        content_type="application/pdf",
        parse_pdf_text=True,
        parse_tables=True,
    )

    assert result["parser_used"] in {"pdf_pypdf_parser", "pdf_parse_deferred", "pdf_parse_failed"}
    assert result["parse_status"] in {"parsed_pdf", "parse_deferred", "parse_failed"}
    if result["parse_status"] != "parsed_pdf":
        assert result["parse_error"]


def test_evidence_chunks_preserve_search_and_credibility_provenance(monkeypatch):
    from hdc_workflow.nodes.content_processing import (
        document_quality_check,
        evidence_chunking_and_data_presence_flagging,
    )

    _clear_stage7_env(monkeypatch)
    doc = {
        "source_id": "src_search_test",
        "document_type": "html",
        "clean_text": (
            "New York reported COVID-19 cases and deaths in 2024. "
            "The surveillance table includes cases, deaths, dates, and location."
        ),
        "tables": [],
        "metadata": {},
        "parse_status": "parsed_html",
        "url": "https://health.ny.gov/example/covid-19-surveillance-2024",
        "canonical_url": "https://health.ny.gov/example/covid-19-surveillance-2024",
        "title": "Official surveillance update",
        "publisher": "New York State Department of Health",
        "source_type": "official_public_health_agency",
        "source_role": "data_source",
        "source_role_final": "collection",
        "credibility_score": 0.88,
        "credibility_level": "high",
        "discovery_method": "fixture_search_result",
        "query_id": "q_official_001",
        "query_used": "COVID-19 New York 2024 official cases deaths",
        "search_provider": "fixture",
        "provider_channel": "web_search",
        "role_hint": "collection",
        "fetch_purpose": "data_extraction",
        "fetch_status": "fixture_content_loaded",
        "is_offline_stub": False,
    }

    state = {"documents": [doc], "collection_trace": []}
    state.update(document_quality_check(state))
    result = evidence_chunking_and_data_presence_flagging(state)

    chunks = result.get("evidence_chunks") or []
    assert chunks
    chunk = chunks[0]
    assert chunk["source_id"] == "src_search_test"
    assert chunk["source_role_final"] == "collection"
    assert chunk["credibility_score"] == 0.88
    assert chunk["discovery_method"] == "fixture_search_result"
    assert chunk["query_id"] == "q_official_001"
    assert chunk["query_used"]


def _run_full_graph_from_config(config_name: str) -> dict:
    from hdc_workflow.graph import build_graph
    from hdc_workflow.workflow_run_config import (
        load_workflow_run_config,
        temporary_workflow_env,
        workflow_initial_state_from_config,
        workflow_run_env_from_config,
    )

    config_path = _PROJECT_ROOT / "configs" / "examples" / config_name
    assert config_path.exists(), f"missing required config example: {config_path}"
    config = load_workflow_run_config(config_path)
    env_updates = workflow_run_env_from_config(config)
    assert env_updates["HDC_ENABLE_LIVE_FETCH"] == "false"
    assert env_updates["HDC_FETCH_SEARCH_DERIVED_SOURCES"] == "true"
    assert env_updates["HDC_ENABLE_LLM_SOURCE_PLANNING"] == "false"
    assert env_updates["HDC_ENABLE_LLM_SOURCE_CRITIC"] == "false"
    assert env_updates["HDC_ENABLE_LLM_EXTRACTION"] == "false"
    with temporary_workflow_env(env_updates):
        return build_graph().invoke(workflow_initial_state_from_config(config))


def test_full_graph_covid19_fixture_search_and_fixture_content_smoke():
    result = _run_full_graph_from_config(
        "covid19_new_york_2024_fixture_search_fetch_task.jsonc"
    )
    package = result.get("final_data_package") or {}
    summaries = package.get("workflow_summaries") or {}
    fetch_summary = result.get("content_fetch_summary") or {}
    parse_summary = result.get("document_parse_summary") or {}
    documents = result.get("documents") or []

    assert package
    assert fetch_summary["selected_search_derived_fetch_count"] >= 1
    assert any(doc.get("discovery_method") == "fixture_search_result" for doc in documents)
    assert any("COVID-19" in (doc.get("clean_text") or "") for doc in documents)
    assert parse_summary["parser_status_counts"].get("parsed_html", 0) >= 1
    assert parse_summary["total_table_count"] >= 1
    assert result.get("evidence_chunks")
    assert summaries.get("document_parse_summary")
    assert summaries.get("content_fetch_summary")


def test_full_graph_dengue_fixture_search_and_fixture_content_smoke():
    result = _run_full_graph_from_config(
        "dengue_florida_2025_fixture_search_fetch_task.jsonc"
    )
    package = result.get("final_data_package") or {}
    summaries = package.get("workflow_summaries") or {}
    fetch_summary = result.get("content_fetch_summary") or {}
    parse_summary = result.get("document_parse_summary") or {}
    documents = result.get("documents") or []

    assert package
    assert fetch_summary["selected_search_derived_fetch_count"] >= 1
    assert any(doc.get("discovery_method") == "fixture_search_result" for doc in documents)
    assert any("dengue" in (doc.get("clean_text") or "").lower() for doc in documents)
    assert parse_summary["parser_status_counts"].get("parsed_html", 0) >= 1
    assert parse_summary["total_table_count"] >= 1
    assert result.get("evidence_chunks")
    assert summaries.get("document_parse_summary")


def test_hantavirus_new_mexico_compatibility_keeps_seed_fetch_behavior(monkeypatch):
    from hdc_workflow.graph import build_graph

    _clear_stage7_env(monkeypatch)
    monkeypatch.setenv("HDC_ENABLE_LIVE_FETCH", "false")
    result = build_graph().invoke(
        {
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
            "collection_trace": [],
        }
    )

    summary = result.get("content_fetch_summary") or {}
    assert summary["search_derived_fetch_enabled"] is False
    assert summary["search_derived_input_count"] == 0
    assert summary["fetch_request_count"] == 10
    assert result.get("document_parse_summary")


def test_console_stage_payload_exposes_fetch_manifest_and_parse_summary():
    from scripts.build_workflow_run_console import _stage_payload

    stages = _stage_payload(
        {
            "collection_trace": [
                {"node_name": "content_fetch_and_parse", "message": "fetched"}
            ],
            "content_fetch_summary": {"selected_search_derived_fetch_count": 1},
            "document_parse_summary": {"parser_status_counts": {"parsed_html": 1}},
            "fetch_manifest": [
                {
                    "source_id": "src_search_example",
                    "selected_for_fetch": True,
                    "skip_reason": None,
                }
            ],
            "documents": [{"source_id": "src_search_example"}],
        }
    )

    content_stage = next(
        stage for stage in stages if stage["node"] == "content_fetch_and_parse"
    )

    assert "document_parse_summary" in content_stage["state_writes"]
    assert "fetch_manifest" in content_stage["state_writes"]
    assert content_stage["show"]["document_parse_summary"]["parser_status_counts"][
        "parsed_html"
    ] == 1
    assert content_stage["show"]["fetch_manifest"][0]["source_id"] == "src_search_example"
