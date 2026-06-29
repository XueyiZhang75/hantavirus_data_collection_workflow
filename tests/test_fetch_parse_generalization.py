"""Stage 7 tests for controlled fetch/parse generalization."""

from __future__ import annotations

import json
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_SRC = _PROJECT_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))


STAGE7_ENV_KEYS = [
    "HDC_COLLECTION_MODE",
    "HDC_SEED_SOURCE_OVERLAY_PATH",
    "HDC_SOURCE_ROLE_POLICY_OVERLAY_PATH",
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
    "HDC_EXTERNAL_FETCH_ENABLED",
    "HDC_EXTERNAL_FETCH_PROVIDER_ORDER",
    "HDC_TAVILY_EXTRACT_FORMAT",
    "HDC_TAVILY_EXTRACT_DEPTH",
    "HDC_TAVILY_EXTRACT_TIMEOUT_SECONDS",
    "HDC_TAVILY_EXTRACT_CHUNKS_PER_SOURCE",
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
    "HDC_ENABLE_LLM_SOURCE_IDENTITY",
    "HDC_LLM_SOURCE_IDENTITY_REQUIRE_LLM",
    "HDC_LLM_SOURCE_IDENTITY_ALLOW_DETERMINISTIC_FALLBACK",
    "HDC_ENABLE_LLM_DISEASE_INTELLIGENCE",
    "HDC_DISEASE_INTELLIGENCE_FORCE_LLM",
    "HDC_DISEASE_INTELLIGENCE_FALLBACK_TO_CURATED",
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


def test_excluded_or_review_source_never_becomes_task_usable_document():
    from hdc_workflow.nodes.content_processing import _document_task_usability

    document = {
        "source_id": "src_excluded_tb_context",
        "fetch_status": "fetched",
        "http_status_code": 200,
        "parse_status": "parsed_text",
        "quality_status": "usable",
        "title": "Tuberculosis surveillance training and resources",
        "clean_text": (
            "Tuberculosis surveillance data for United Kingdom 2025 reported "
            "case counts and incidence rates in a public health resource. "
            "The document includes tables and epidemiology data signals. "
            * 5
        ),
    }
    state = {
        "structured_task": {
            "disease": "Tuberculosis",
            "location": "United Kingdom",
            "start_date": "2025-01-01",
            "end_date": "2025-12-31",
            "collection_mode": "direct_collection",
        },
        "collection_spec": {
            "disease": "Tuberculosis",
            "geography": "United Kingdom",
            "start_date": "2025-01-01",
            "end_date": "2025-12-31",
            "collection_mode": "direct_collection",
        },
    }
    excluded_source = {
        "source_id": "src_excluded_tb_context",
        "canonical_url": "https://example.org/tb-training-resource",
        "title": "Tuberculosis surveillance training and resources",
        "publisher": "Example Training Provider",
        "source_type_final": "official_public_health_agency",
        "source_role_final": "excluded",
        "target_fit_status": "task_record_collection_candidate",
        "triage_role": "task_record_collection_candidate",
        "target_verification_status": "candidate_task_record_source",
        "discovery_method": "fixture_search_result",
    }
    review_source = {
        **excluded_source,
        "source_id": "src_review_tb_context",
        "source_role_final": "needs_human_review",
        "requires_human_review": True,
        "human_review_reason": "source_trust_requires_human_review",
    }

    excluded_usable, excluded_reasons = _document_task_usability(
        document,
        excluded_source,
        state,
    )
    review_usable, review_reasons = _document_task_usability(
        {**document, "source_id": "src_review_tb_context"},
        review_source,
        state,
    )

    assert excluded_usable is False
    assert "source_role_not_task_collection" in excluded_reasons
    assert review_usable is False
    assert "source_trust_requires_review" in review_reasons


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


def test_document_quality_marks_http_200_error_page_unusable(monkeypatch):
    from hdc_workflow.nodes.content_processing import document_quality_check

    _clear_stage7_env(monkeypatch)
    state = {
        "structured_task": {
            "disease": "FLU",
            "location": "VIRGINIA",
            "start_date": "2024-10-06",
            "end_date": "2024-10-12",
            "collection_mode": "direct_collection",
        },
        "collection_trace": [],
        "documents": [
            {
                "source_id": "src_vdh_week41_generated",
                "fetch_status": "fetched",
                "http_status_code": 200,
                "parse_status": "parsed_text",
                "title": "Page not found - Virginia Department of Health",
                "clean_text": (
                    "# Page not found - Virginia Department of Health\n"
                    "A Commonwealth of Virginia Website. The page you requested "
                    "was not found. Locations Data Clinicians Newsroom Privacy "
                    "Policy Non-Discrimination Policy Language Access Plan. "
                    * 6
                ),
            }
        ],
    }

    result = document_quality_check(state)

    doc = result["documents"][0]
    summary = result["document_quality_summary"]
    assert doc["quality_status"] == "unusable"
    assert "error_page_detected" in doc["quality_issues"]
    assert summary["unusable_count"] == 1
    assert summary["error_page_document_count"] == 1
    assert summary["usable_count"] == 0


def test_direct_fast_path_fetches_search_verified_target_fallback(monkeypatch):
    from hdc_workflow.nodes.content_processing import content_fetch_and_parse

    _clear_stage7_env(monkeypatch)
    monkeypatch.setenv("HDC_COLLECTION_MODE", "direct_collection")
    monkeypatch.setenv("HDC_FETCH_SEARCH_DERIVED_SOURCES", "true")
    monkeypatch.setenv("HDC_FETCH_MAX_SEARCH_DERIVED_SOURCES", "1")
    entries = [
        _search_entry(
            "src_vdh_generated_week41",
            url=(
                "https://www.vdh.virginia.gov/content/uploads/sites/13/"
                "2024/10/Weekly-RDS-Report_Week-41.pdf"
            ),
            discovery_method="official_coverage_requirement",
            publisher="Virginia Department of Health",
        )
        | {
            "must_fetch": True,
            "must_fetch_reason": "official_coverage_requirement",
            "coverage_requirement_ids": ["virginia_influenza_official_week_41_2024"],
            "target_fit_status": "predicted_target_candidate",
            "triage_role": "predicted_target_candidate",
        },
        _search_entry(
            "src_vdh_search_verified_week41",
            url=(
                "https://www.vdh.virginia.gov/epidemiology/influenza/"
                "virginia-weekly-respiratory-disease-surveillance-week-41-2024"
            ),
            publisher="Virginia Department of Health",
        )
        | {
            "target_fit_status": "verified_target_collection",
            "target_verification_status": "verified",
            "triage_role": "verified_target_collection",
            "coverage_requirement_ids": ["virginia_influenza_official_week_41_2024"],
        },
        _search_entry(
            "src_forum_context",
            url="https://flutrackers.com/forum/virginia-week-41-2024",
            publisher="FluTrackers",
            source_type="news_and_situation_report",
            credibility_score=0.99,
            credibility_level="high",
        ),
    ]
    state = _state_with_sources(entries)
    state["structured_task"] = {
        "disease": "FLU",
        "location": "VIRGINIA",
        "start_date": "2024-10-06",
        "end_date": "2024-10-12",
        "collection_mode": "direct_collection",
    }
    state["collection_spec"] = {
        "disease": "FLU",
        "geography": "VIRGINIA",
        "start_date": "2024-10-06",
        "end_date": "2024-10-12",
        "collection_mode": "direct_collection",
    }

    result = content_fetch_and_parse(state)

    selected_ids = [request["source_id"] for request in result.get("content_fetch_requests") or []]
    assert selected_ids == [
        "src_vdh_generated_week41",
        "src_vdh_search_verified_week41",
    ]
    summary = result["content_fetch_summary"]
    assert summary["selected_search_derived_fetch_count"] == 1
    assert summary["search_verified_target_fetch_count"] == 1
    assert summary["fallback_fetch_attempted"] is True
    assert summary["fallback_fetch_selected_source_ids"] == [
        "src_vdh_search_verified_week41"
    ]
    manifest = {row["source_id"]: row for row in summary["selection_manifest"]}
    assert manifest["src_vdh_search_verified_week41"]["skip_reason"] is None
    assert manifest["src_forum_context"]["skip_reason"] == "direct_target_official_fast_path"


def test_direct_fast_path_defers_task_candidate_when_verified_target_is_usable(
    monkeypatch,
    tmp_path,
):
    from hdc_workflow.nodes.content_processing import content_fetch_and_parse

    _clear_stage7_env(monkeypatch)
    monkeypatch.setenv("HDC_COLLECTION_MODE", "direct_collection")
    monkeypatch.setenv("HDC_FETCH_SEARCH_DERIVED_SOURCES", "true")
    monkeypatch.setenv("HDC_FETCH_MAX_TOTAL_SOURCES", "4")
    target_url = "https://www.cdc.gov/fluview/surveillance/2024-week-40.html"
    fallback_url = "https://nnph.org/influenza-week-40-2024"
    target_fixture = tmp_path / "cdc_week40.html"
    target_fixture.write_text(
        "<html><title>CDC FluView Week 40</title><body>"
        "Weekly US influenza surveillance report for Week 40 ending "
        "October 5, 2024. Clinical laboratories tested specimens and "
        "reported positive influenza results for the United States."
        "</body></html>",
        encoding="utf-8",
    )
    fallback_fixture = tmp_path / "fallback.html"
    fallback_fixture.write_text(
        "<html><title>Local influenza dashboard</title><body>"
        "Local influenza dashboard for Week 40 ending October 5, 2024."
        "</body></html>",
        encoding="utf-8",
    )
    fixture_map = tmp_path / "fixture_map.json"
    fixture_map.write_text(
        json.dumps(
            {
                "fixtures": [
                    {
                        "canonical_url": target_url,
                        "fixture_path": str(target_fixture),
                        "content_type": "text/html; charset=utf-8",
                    },
                    {
                        "canonical_url": fallback_url,
                        "fixture_path": str(fallback_fixture),
                        "content_type": "text/html; charset=utf-8",
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("HDC_CONTENT_FIXTURE_MAP_PATH", str(fixture_map))
    req_id = "united_states_influenza_official_week_40_2024"
    entries = [
        _search_entry(
            "src_cdc_week40",
            url=target_url,
            publisher="CDC",
        )
        | {
            "must_fetch": True,
            "must_fetch_reason": "search_verified_target_collection",
            "coverage_requirement_ids": [req_id],
            "target_fit_status": "verified_target_collection",
            "target_verification_status": "verified",
            "triage_role": "verified_target_collection",
            "source_role_final": "collection",
        },
        _search_entry(
            "src_local_candidate_week40",
            url=fallback_url,
            discovery_method="live_search_result",
            publisher="Northern Nevada Public Health",
        )
        | {
            "target_fit_status": "task_record_collection_candidate",
            "target_verification_status": "candidate_task_record_source",
            "triage_role": "task_record_collection_candidate",
            "source_role_final": "collection",
        },
    ]
    state = _state_with_sources(entries)
    state["structured_task"] = {
        "disease": "FLU",
        "location": "United States",
        "start_date": "2024-09-29",
        "end_date": "2024-10-05",
        "collection_mode": "direct_collection",
    }
    state["collection_spec"] = {
        "disease": "FLU",
        "geography": "United States",
        "start_date": "2024-09-29",
        "end_date": "2024-10-05",
        "collection_mode": "direct_collection",
    }

    result = content_fetch_and_parse(state)

    request_ids = [request["source_id"] for request in result["content_fetch_requests"]]
    assert request_ids == ["src_cdc_week40"]
    summary = result["content_fetch_summary"]
    assert summary["fallback_fetch_attempted"] is False
    assert summary["fallback_fetch_selected_source_ids"] == []
    manifest = {row["source_id"]: row for row in summary["selection_manifest"]}
    assert (
        manifest["src_local_candidate_week40"]["skip_reason"]
        == "direct_target_official_fast_path_deferred_task_candidate"
    )


def test_generated_target_candidate_is_not_counted_as_search_verified(monkeypatch):
    from hdc_workflow.nodes.content_processing import content_fetch_and_parse

    _clear_stage7_env(monkeypatch)
    monkeypatch.setenv("HDC_COLLECTION_MODE", "direct_collection")
    entry = _search_entry(
        "src_vdh_generated_week42",
        url=(
            "https://www.vdh.virginia.gov/content/uploads/sites/13/"
            "2024/10/Weekly-RDS-Report_Week-42.pdf"
        ),
        discovery_method="official_coverage_requirement",
        publisher="Virginia Department of Health",
    ) | {
        "must_fetch": True,
        "must_fetch_reason": "official_coverage_requirement",
        "coverage_requirement_ids": ["virginia_influenza_official_week_42_2024"],
        "target_fit_status": "verified_target",
        "target_verification_status": "predicted_unverified",
        "triage_role": "predicted_target_candidate",
    }
    state = _state_with_sources([entry])
    state["structured_task"] = {
        "disease": "FLU",
        "location": "VIRGINIA",
        "start_date": "2024-10-13",
        "end_date": "2024-10-19",
        "collection_mode": "direct_collection",
    }
    state["collection_spec"] = {
        "disease": "FLU",
        "geography": "VIRGINIA",
        "start_date": "2024-10-13",
        "end_date": "2024-10-19",
        "collection_mode": "direct_collection",
    }

    result = content_fetch_and_parse(state)

    summary = result["content_fetch_summary"]
    assert summary["generated_target_fetch_count"] == 1
    assert summary["search_verified_target_fetch_count"] == 0
    assert summary["fallback_fetch_attempted"] is False


def test_fetch_manifest_includes_url_quality_fit_and_task_usability(monkeypatch, tmp_path):
    from hdc_workflow.nodes.content_processing import content_fetch_and_parse

    _clear_stage7_env(monkeypatch)
    monkeypatch.setenv("HDC_USE_FIXTURE_DOCUMENTS", "true")
    monkeypatch.setenv("HDC_FETCH_SEARCH_DERIVED_SOURCES", "true")
    monkeypatch.setenv("HDC_COLLECTION_MODE", "direct_collection")
    url = "https://www.cdc.gov/fluview/surveillance/2024-week-40.html"
    fixture = tmp_path / "cdc_week40.html"
    fixture.write_text(
        "<html><title>CDC Week 40 FluView</title><body>"
        "United States influenza surveillance data for Week 40 ending October 5, 2024."
        "</body></html>",
        encoding="utf-8",
    )
    fixture_map = tmp_path / "fixture_map.json"
    fixture_map.write_text(
        json.dumps(
            {
                "fixtures": [
                    {
                        "canonical_url": url,
                        "fixture_path": str(fixture),
                        "content_type": "text/html; charset=utf-8",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("HDC_CONTENT_FIXTURE_MAP_PATH", str(fixture_map))
    req_id = "united_states_influenza_official_week_40_2024"
    state = _state_with_sources(
        [
            _search_entry("src_cdc_week40", url=url, publisher="CDC")
            | {
                "must_fetch": True,
                "coverage_requirement_ids": [req_id],
                "target_fit_status": "verified_target_collection",
                "triage_role": "verified_target_collection",
                "disease_fit": "match",
                "geography_fit": "match",
                "date_fit": "match",
                "source_role_final": "collection",
            }
        ]
    )
    state["structured_task"] = {
        "disease": "FLU",
        "location": "United States",
        "start_date": "2024-09-29",
        "end_date": "2024-10-05",
        "collection_mode": "direct_collection",
    }
    state["collection_spec"] = {
        "disease": "FLU",
        "geography": "United States",
        "start_date": "2024-09-29",
        "end_date": "2024-10-05",
        "collection_mode": "direct_collection",
    }

    result = content_fetch_and_parse(state)

    row = next(item for item in result["fetch_manifest"] if item["source_id"] == "src_cdc_week40")
    assert row["url"] == url
    assert row["canonical_url"] == url
    assert row["http_status"] == 200
    assert row["fetch_status"] in {"fetched", "fixture_content_loaded"}
    assert row["parse_status"].startswith("parsed")
    assert row["quality_status"] in {"usable", "partial"}
    assert row["source_role_final"] == "collection"
    assert row["target_fit_status"] == "verified_target_collection"
    assert row["usable_for_task_collection"] is True
    assert row["coverage_requirement_ids"] == [req_id]


def test_short_window_task_candidate_annual_document_is_best_available_not_task_usable(
    monkeypatch,
    tmp_path,
):
    from hdc_workflow.nodes.content_processing import content_fetch_and_parse

    _clear_stage7_env(monkeypatch)
    monkeypatch.setenv("HDC_USE_FIXTURE_DOCUMENTS", "true")
    monkeypatch.setenv("HDC_FETCH_SEARCH_DERIVED_SOURCES", "true")
    monkeypatch.setenv("HDC_COLLECTION_MODE", "direct_collection")
    url = "https://example.org/india-tb-report-2024"
    fixture = tmp_path / "india_tb_report_2024.html"
    fixture.write_text(
        "<html><title>India TB Report 2024</title><body>"
        "India annual tuberculosis report for 2024. The report summarizes "
        "national TB notifications and incidence for the full year 2024."
        "</body></html>",
        encoding="utf-8",
    )
    fixture_map = tmp_path / "fixture_map.json"
    fixture_map.write_text(
        json.dumps(
            {
                "fixtures": [
                    {
                        "canonical_url": url,
                        "fixture_path": str(fixture),
                        "content_type": "text/html; charset=utf-8",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("HDC_CONTENT_FIXTURE_MAP_PATH", str(fixture_map))
    state = _state_with_sources(
        [
            _search_entry(
                "src_india_tb_annual",
                url=url,
                publisher="National Tuberculosis Elimination Programme",
            )
            | {
                "target_fit_status": "task_record_collection_candidate",
                "triage_role": "task_record_collection_candidate",
                "disease_fit": "match",
                "geography_fit": "match",
                "date_fit": "candidate",
                "source_role_final": "collection",
            }
        ]
    )
    state["structured_task"] = {
        "disease": "Tuberculosis",
        "location": "India",
        "start_date": "2024-09-29",
        "end_date": "2024-10-05",
        "collection_mode": "direct_collection",
    }
    state["collection_spec"] = {
        "disease": "Tuberculosis",
        "geography": "India",
        "start_date": "2024-09-29",
        "end_date": "2024-10-05",
        "collection_mode": "direct_collection",
    }

    result = content_fetch_and_parse(state)

    row = next(item for item in result["fetch_manifest"] if item["source_id"] == "src_india_tb_annual")
    assert row["fetch_status"] in {"fetched", "fixture_content_loaded"}
    assert row["quality_status"] in {"usable", "partial"}
    assert row["usable_for_task_collection"] is False
    assert row["usable_for_best_available_context"] is True
    assert "period_not_exact_for_task" in row["task_usability_reasons"]


def test_annual_task_candidate_weekly_document_is_best_available_not_task_usable(
    monkeypatch,
    tmp_path,
):
    from hdc_workflow.nodes.content_processing import content_fetch_and_parse

    _clear_stage7_env(monkeypatch)
    monkeypatch.setenv("HDC_USE_FIXTURE_DOCUMENTS", "true")
    monkeypatch.setenv("HDC_FETCH_SEARCH_DERIVED_SOURCES", "true")
    monkeypatch.setenv("HDC_COLLECTION_MODE", "direct_collection")
    url = "https://www.cdc.gov/fluview/surveillance/2024-week-51.html"
    fixture = tmp_path / "cdc_week51.html"
    fixture.write_text(
        "<html><title>Weekly US Influenza Surveillance Report: Week 51</title><body>"
        "CDC FluView Week 51 ending December 21, 2024. Florida clinical "
        "laboratories reported current week influenza specimens in Week 51."
        "</body></html>",
        encoding="utf-8",
    )
    fixture_map = tmp_path / "fixture_map.json"
    fixture_map.write_text(
        json.dumps(
            {
                "fixtures": [
                    {
                        "canonical_url": url,
                        "fixture_path": str(fixture),
                        "content_type": "text/html; charset=utf-8",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("HDC_CONTENT_FIXTURE_MAP_PATH", str(fixture_map))
    state = _state_with_sources(
        [
            _search_entry(
                "src_cdc_week51",
                url=url,
                publisher="Centers for Disease Control and Prevention",
            )
            | {
                "target_fit_status": "verified_target_collection",
                "triage_role": "verified_target_collection",
                "disease_fit": "match",
                "geography_fit": "candidate",
                "date_fit": "candidate",
                "source_role_final": "collection",
                "coverage_requirement_ids": ["florida_flu_annual_2024"],
            }
        ]
    )
    state["structured_task"] = {
        "disease": "FLU",
        "location": "Florida",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "collection_mode": "direct_collection",
    }
    state["collection_spec"] = {
        "disease": "FLU",
        "geography": "Florida",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "collection_mode": "direct_collection",
    }
    state["task_evidence_contract"] = {
        "time_granularity": "annual",
        "requirements": [
            {
                "requirement_id": "florida_flu_annual_2024",
                "period_start": "2024-01-01",
                "period_end": "2024-12-31",
                "period_basis": "annual",
                "geography": "Florida",
                "disease": "flu",
            }
        ],
    }

    result = content_fetch_and_parse(state)

    row = next(item for item in result["fetch_manifest"] if item["source_id"] == "src_cdc_week51")
    assert row["fetch_status"] in {"fetched", "fixture_content_loaded"}
    assert row["quality_status"] in {"usable", "partial"}
    assert row["usable_for_task_collection"] is False
    assert row["usable_for_best_available_context"] is True
    assert "period_not_exact_for_task" in row["task_usability_reasons"]


def test_annual_task_candidate_training_page_is_best_available_not_task_usable(
    monkeypatch,
    tmp_path,
):
    from hdc_workflow.nodes.content_processing import content_fetch_and_parse

    _clear_stage7_env(monkeypatch)
    monkeypatch.setenv("HDC_USE_FIXTURE_DOCUMENTS", "true")
    monkeypatch.setenv("HDC_FETCH_SEARCH_DERIVED_SOURCES", "true")
    monkeypatch.setenv("HDC_COLLECTION_MODE", "direct_collection")
    url = "https://www.example.gov/tuberculosis/training"
    fixture = tmp_path / "tb_training.html"
    fixture.write_text(
        "<html><title>Tuberculosis Training</title><body>"
        "Virginia tuberculosis training resources for 2025. This page "
        "contains course materials, contact information, and education links, "
        "but does not report cases, incidence, deaths, or surveillance metrics."
        "</body></html>",
        encoding="utf-8",
    )
    fixture_map = tmp_path / "fixture_map.json"
    fixture_map.write_text(
        json.dumps(
            {
                "fixtures": [
                    {
                        "canonical_url": url,
                        "fixture_path": str(fixture),
                        "content_type": "text/html; charset=utf-8",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("HDC_CONTENT_FIXTURE_MAP_PATH", str(fixture_map))
    state = _state_with_sources(
        [
            _search_entry(
                "src_tb_training",
                url=url,
                publisher="Virginia Department of Health",
            )
            | {
                "target_fit_status": "task_record_collection_candidate",
                "triage_role": "task_record_collection_candidate",
                "disease_fit": "match",
                "geography_fit": "match",
                "date_fit": "candidate",
                "source_role_final": "collection",
                "coverage_requirement_ids": ["virginia_tuberculosis_annual_2025"],
            }
        ]
    )
    state["structured_task"] = {
        "disease": "Tuberculosis",
        "location": "Virginia",
        "start_date": "2025-01-01",
        "end_date": "2025-12-31",
        "collection_mode": "direct_collection",
    }
    state["collection_spec"] = {
        "disease": "Tuberculosis",
        "geography": "Virginia",
        "start_date": "2025-01-01",
        "end_date": "2025-12-31",
        "collection_mode": "direct_collection",
    }
    state["task_evidence_contract"] = {
        "time_granularity": "annual",
        "requirements": [
            {
                "requirement_id": "virginia_tuberculosis_annual_2025",
                "period_start": "2025-01-01",
                "period_end": "2025-12-31",
                "period_basis": "annual",
                "geography": "Virginia",
                "disease": "tuberculosis",
            }
        ],
    }

    result = content_fetch_and_parse(state)

    row = next(item for item in result["fetch_manifest"] if item["source_id"] == "src_tb_training")
    assert row["fetch_status"] in {"fetched", "fixture_content_loaded"}
    assert row["quality_status"] in {"usable", "partial"}
    assert row["usable_for_task_collection"] is False
    assert row["usable_for_best_available_context"] is True
    assert "document_lacks_task_data_signal" in row["task_usability_reasons"]


def test_social_video_page_is_review_context_not_task_usable(
    monkeypatch,
    tmp_path,
):
    from hdc_workflow.nodes.content_processing import content_fetch_and_parse

    _clear_stage7_env(monkeypatch)
    monkeypatch.setenv("HDC_USE_FIXTURE_DOCUMENTS", "true")
    monkeypatch.setenv("HDC_FETCH_SEARCH_DERIVED_SOURCES", "true")
    monkeypatch.setenv("HDC_FETCH_ALLOW_NEEDS_REVIEW", "true")
    monkeypatch.setenv("HDC_COLLECTION_MODE", "direct_collection")
    url = "https://www.youtube.com/watch?v=YE-dJl4lhKw"
    fixture = tmp_path / "flu_video.html"
    fixture.write_text(
        "<html><title>Seasonal influenza situation in India 2024</title><body>"
        "Video transcript: discussion of seasonal influenza in India in 2024. "
        "The speaker refers to government surveillance and case counts, but "
        "this page is a video platform page and not a primary surveillance "
        "report, dataset, dashboard, or official annual source."
        "</body></html>",
        encoding="utf-8",
    )
    fixture_map = tmp_path / "fixture_map.json"
    fixture_map.write_text(
        json.dumps(
            {
                "fixtures": [
                    {
                        "canonical_url": url,
                        "fixture_path": str(fixture),
                        "content_type": "text/html; charset=utf-8",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("HDC_CONTENT_FIXTURE_MAP_PATH", str(fixture_map))
    state = _state_with_sources(
        [
            _search_entry(
                "src_youtube_flu",
                url=url,
                publisher="YouTube",
                source_type="social_media",
                final_role="needs_human_review",
                ready=False,
                requires_review=True,
            )
            | {
                "target_fit_status": "needs_human_review",
                "triage_role": "needs_human_review",
                "disease_fit": "candidate",
                "geography_fit": "candidate",
                "date_fit": "candidate",
                "coverage_requirement_ids": ["india_flu_annual_2024"],
                "screening_flags": ["source_trust_requires_human_review"],
            }
        ]
    )
    state["structured_task"] = {
        "disease": "FLU",
        "location": "India",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "collection_mode": "direct_collection",
    }
    state["collection_spec"] = {
        "disease": "FLU",
        "geography": "India",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "collection_mode": "direct_collection",
    }
    state["task_evidence_contract"] = {
        "time_granularity": "annual",
        "requirements": [
            {
                "requirement_id": "india_flu_annual_2024",
                "period_start": "2024-01-01",
                "period_end": "2024-12-31",
                "period_basis": "annual",
                "geography": "India",
                "disease": "flu",
            }
        ],
    }

    result = content_fetch_and_parse(state)

    row = next(item for item in result["fetch_manifest"] if item["source_id"] == "src_youtube_flu")
    assert row["fetch_status"] in {"fetched", "fixture_content_loaded"}
    assert row["usable_for_task_collection"] is False
    assert row["usable_for_best_available_context"] is True
    assert "source_trust_requires_review" in row["task_usability_reasons"]


def test_regional_source_with_task_signals_is_not_exact_task_document(
    monkeypatch,
    tmp_path,
):
    from hdc_workflow.nodes.content_processing import content_fetch_and_parse

    _clear_stage7_env(monkeypatch)
    monkeypatch.setenv("HDC_USE_FIXTURE_DOCUMENTS", "true")
    monkeypatch.setenv("HDC_FETCH_SEARCH_DERIVED_SOURCES", "true")
    monkeypatch.setenv("HDC_COLLECTION_MODE", "direct_collection")
    url = "https://www.ecdc.europa.eu/en/tuberculosis/surveillance-report-2024"
    fixture = tmp_path / "ecdc_tb_europe.html"
    fixture.write_text(
        "<html><title>ECDC tuberculosis surveillance report 2024</title><body>"
        "ECDC reports tuberculosis notifications for Germany and the EU/EEA "
        "during September 29, 2024 through October 5, 2024. The table covers "
        "regional European surveillance, including cases and incidence."
        "</body></html>",
        encoding="utf-8",
    )
    fixture_map = tmp_path / "fixture_map.json"
    fixture_map.write_text(
        json.dumps(
            {
                "fixtures": [
                    {
                        "canonical_url": url,
                        "fixture_path": str(fixture),
                        "content_type": "text/html; charset=utf-8",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("HDC_CONTENT_FIXTURE_MAP_PATH", str(fixture_map))
    req_id = "germany_tuberculosis_task_window_2024_09_29_2024_10_05"
    state = _state_with_sources(
        [
            _search_entry(
                "src_ecdc_tb_europe",
                url=url,
                publisher="European Centre for Disease Prevention and Control",
                source_type="supranational_public_health_agency",
            )
            | {
                "target_fit_status": "task_record_collection_candidate",
                "triage_role": "task_record_collection_candidate",
                "disease_fit": "match",
                "geography_fit": "broader_than_task",
                "date_fit": "match",
                "source_role_final": "collection",
                "coverage_requirement_ids": [req_id],
            }
        ]
    )
    state["structured_task"] = {
        "disease": "Tuberculosis",
        "location": "Germany",
        "start_date": "2024-09-29",
        "end_date": "2024-10-05",
        "collection_mode": "direct_collection",
    }
    state["collection_spec"] = {
        "disease": "Tuberculosis",
        "geography": "Germany",
        "start_date": "2024-09-29",
        "end_date": "2024-10-05",
        "collection_mode": "direct_collection",
    }

    result = content_fetch_and_parse(state)

    row = next(item for item in result["fetch_manifest"] if item["source_id"] == "src_ecdc_tb_europe")
    assert row["fetch_status"] in {"fetched", "fixture_content_loaded"}
    assert row["quality_status"] in {"usable", "partial"}
    assert row["usable_for_task_collection"] is False
    assert row["usable_for_best_available_context"] is True
    assert "geography_not_exact_for_task" in row["task_usability_reasons"]


def test_literature_source_with_exact_task_signals_requires_review_not_task_usable(
    monkeypatch,
    tmp_path,
):
    from hdc_workflow.nodes.content_processing import content_fetch_and_parse

    _clear_stage7_env(monkeypatch)
    monkeypatch.setenv("HDC_USE_FIXTURE_DOCUMENTS", "true")
    monkeypatch.setenv("HDC_FETCH_SEARCH_DERIVED_SOURCES", "true")
    monkeypatch.setenv("HDC_COLLECTION_MODE", "direct_collection")
    url = "https://pubmed.ncbi.nlm.nih.gov/12345678/"
    fixture = tmp_path / "pubmed_measles_london.html"
    fixture.write_text(
        "<html><title>Measles in London, September 2024</title><body>"
        "A journal abstract reports measles cases in London from September 29, "
        "2024 through October 5, 2024 with surveillance statistics and rates."
        "</body></html>",
        encoding="utf-8",
    )
    fixture_map = tmp_path / "fixture_map.json"
    fixture_map.write_text(
        json.dumps(
            {
                "fixtures": [
                    {
                        "canonical_url": url,
                        "fixture_path": str(fixture),
                        "content_type": "text/html; charset=utf-8",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("HDC_CONTENT_FIXTURE_MAP_PATH", str(fixture_map))
    req_id = "london_measles_task_window_2024_09_29_2024_10_05"
    state = _state_with_sources(
        [
            _search_entry(
                "src_pubmed_london_measles",
                url=url,
                publisher="PubMed",
                source_type="journal_article",
            )
            | {
                "target_fit_status": "task_record_collection_candidate",
                "triage_role": "task_record_collection_candidate",
                "disease_fit": "match",
                "geography_fit": "match",
                "date_fit": "match",
                "source_role_final": "collection",
                "coverage_requirement_ids": [req_id],
            }
        ]
    )
    state["structured_task"] = {
        "disease": "Measles",
        "location": "London",
        "start_date": "2024-09-29",
        "end_date": "2024-10-05",
        "collection_mode": "direct_collection",
    }
    state["collection_spec"] = {
        "disease": "Measles",
        "geography": "London",
        "start_date": "2024-09-29",
        "end_date": "2024-10-05",
        "collection_mode": "direct_collection",
    }

    result = content_fetch_and_parse(state)

    row = next(item for item in result["fetch_manifest"] if item["source_id"] == "src_pubmed_london_measles")
    assert row["fetch_status"] in {"fetched", "fixture_content_loaded"}
    assert row["usable_for_task_collection"] is False
    assert row["usable_for_best_available_context"] is True
    assert "source_trust_requires_review" in row["task_usability_reasons"]


def test_weekly_task_candidate_season_report_mentioning_week_is_best_available_not_task_usable(
    monkeypatch,
    tmp_path,
):
    from hdc_workflow.nodes.content_processing import content_fetch_and_parse

    _clear_stage7_env(monkeypatch)
    monkeypatch.setenv("HDC_USE_FIXTURE_DOCUMENTS", "true")
    monkeypatch.setenv("HDC_FETCH_SEARCH_DERIVED_SOURCES", "true")
    monkeypatch.setenv("HDC_COLLECTION_MODE", "direct_collection")
    url = "https://www.vdh.virginia.gov/content/uploads/sites/3/2025/01/2024-end-season-rds.pdf"
    fixture = tmp_path / "vdh_end_season.html"
    fixture.write_text(
        "<html><title>Virginia Respiratory Disease End of Season Report</title><body>"
        "Virginia respiratory disease end-of-season report for 2023-2024. "
        "The season report mentions MMWR Week 40, 2024 in a trend chart, "
        "but summarizes season-to-date activity rather than the exact "
        "September 29 - October 5, 2024 surveillance week."
        "</body></html>",
        encoding="utf-8",
    )
    fixture_map = tmp_path / "fixture_map.json"
    fixture_map.write_text(
        json.dumps(
            {
                "fixtures": [
                    {
                        "canonical_url": url,
                        "fixture_path": str(fixture),
                        "content_type": "text/html; charset=utf-8",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("HDC_CONTENT_FIXTURE_MAP_PATH", str(fixture_map))
    state = _state_with_sources(
        [
            _search_entry(
                "src_vdh_end_season",
                url=url,
                publisher="Virginia Department of Health",
            )
            | {
                "target_fit_status": "task_record_collection_candidate",
                "triage_role": "task_record_collection_candidate",
                "disease_fit": "match",
                "geography_fit": "match",
                "date_fit": "candidate",
                "source_role_final": "collection",
            }
        ]
    )
    state["structured_task"] = {
        "disease": "FLU",
        "location": "Virginia",
        "start_date": "2024-09-29",
        "end_date": "2024-10-05",
        "collection_mode": "direct_collection",
    }
    state["collection_spec"] = {
        "disease": "FLU",
        "geography": "Virginia",
        "start_date": "2024-09-29",
        "end_date": "2024-10-05",
        "collection_mode": "direct_collection",
    }

    result = content_fetch_and_parse(state)

    row = next(item for item in result["fetch_manifest"] if item["source_id"] == "src_vdh_end_season")
    assert row["quality_status"] in {"usable", "partial"}
    assert row["usable_for_task_collection"] is False
    assert row["usable_for_best_available_context"] is True
    assert "period_not_exact_for_task" in row["task_usability_reasons"]


def test_must_fetch_official_report_fetches_alias_after_error_page(
    monkeypatch,
    tmp_path,
):
    from hdc_workflow.nodes.content_processing import content_fetch_and_parse

    _clear_stage7_env(monkeypatch)
    monkeypatch.setenv("HDC_COLLECTION_MODE", "direct_collection")
    bad_url = (
        "https://www.vdh.virginia.gov/content/uploads/sites/13/"
        "2024/10/Weekly-RDS-Report_Week-43.pdf"
    )
    good_url = (
        "https://www.vdh.virginia.gov/content/uploads/sites/3/"
        "2024/10/2024-25_Weekly-RDS-Report_Week-43.pdf"
    )
    bad_fixture = tmp_path / "bad_week43.html"
    bad_fixture.write_text(
        "<html><title>Page not found - Virginia Department of Health</title>"
        "<body>Page not found. The page you requested was not found.</body></html>",
        encoding="utf-8",
    )
    good_fixture = tmp_path / "good_week43.html"
    good_fixture.write_text(
        "<html><title>VDH Weekly Respiratory Disease Surveillance Report Week 43</title>"
        "<body>Virginia Department of Health Respiratory Disease Surveillance. "
        "During the week of October 20 - October 26, 2024 (MMWR Week 43), "
        "VDH received 31 positive influenza lab results in Virginia. "
        "Influenza-like illness visits in Virginia were reported for the same week. "
        "</body></html>",
        encoding="utf-8",
    )
    fixture_map = tmp_path / "content_fixtures.json"
    fixture_map.write_text(
        json.dumps(
            {
                "fixtures": [
                    {
                        "canonical_url": bad_url,
                        "fixture_path": str(bad_fixture),
                        "content_type": "text/html; charset=utf-8",
                    },
                    {
                        "canonical_url": good_url,
                        "fixture_path": str(good_fixture),
                        "content_type": "text/html; charset=utf-8",
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("HDC_CONTENT_FIXTURE_MAP_PATH", str(fixture_map))
    entry = _search_entry(
        "src_vdh_generated_week43",
        url=bad_url,
        discovery_method="official_coverage_requirement",
        publisher="Virginia Department of Health",
    ) | {
        "must_fetch": True,
        "must_fetch_reason": "official_coverage_requirement",
        "coverage_requirement_ids": ["virginia_influenza_official_week_43_2024"],
        "target_fit_status": "predicted_target_candidate",
        "target_verification_status": "predicted_unverified",
        "triage_role": "predicted_target_candidate",
        "official_report_key": "virginia_rds_weekly_report:2024:week_43",
        "official_report_alias_urls": [bad_url, good_url],
        "official_report_alias_source_ids": [
            "src_vdh_generated_week43",
            "src_vdh_generated_week43_alias",
        ],
    }
    state = _state_with_sources([entry])
    state["structured_task"] = {
        "disease": "FLU",
        "location": "VIRGINIA",
        "start_date": "2024-10-20",
        "end_date": "2024-10-26",
        "collection_mode": "direct_collection",
    }
    state["collection_spec"] = {
        "disease": "FLU",
        "geography": "VIRGINIA",
        "start_date": "2024-10-20",
        "end_date": "2024-10-26",
        "collection_mode": "direct_collection",
    }

    result = content_fetch_and_parse(state)

    request_urls = [request["url"] for request in result["content_fetch_requests"]]
    assert request_urls == [bad_url, good_url]
    documents = result["documents"]
    assert len(documents) == 2
    assert documents[0]["canonical_url"] == bad_url
    assert documents[1]["canonical_url"] == good_url
    assert "31 positive influenza lab results" in documents[1]["clean_text"]
    summary = result["content_fetch_summary"]
    assert summary["error_page_document_count"] == 1
    assert summary["usable_target_document_count"] == 1
    assert summary["alias_fetch_attempted_count"] == 1
    assert summary["alias_fetch_success_count"] == 1
    assert summary["error_alias_urls"] == [bad_url]
    assert summary["usable_target_alias_urls"] == [good_url]


def test_direct_collection_fetches_task_fallback_when_target_aliases_unusable(
    monkeypatch,
    tmp_path,
):
    from hdc_workflow.nodes.content_processing import content_fetch_and_parse

    _clear_stage7_env(monkeypatch)
    monkeypatch.setenv("HDC_COLLECTION_MODE", "direct_collection")
    monkeypatch.setenv("HDC_FETCH_SEARCH_DERIVED_SOURCES", "true")
    monkeypatch.setenv("HDC_FETCH_MAX_SEARCH_DERIVED_SOURCES", "1")
    req_id = "virginia_influenza_official_week_40_2024"
    generated_bad = (
        "https://www.vdh.virginia.gov/content/uploads/sites/13/"
        "2024/10/Weekly-RDS-Report_Week-40.pdf"
    )
    search_bad = (
        "https://www.vdh.virginia.gov/content/uploads/sites/3/"
        "2024/10/2024-25_Weekly-RDS-Report_Week-40.pdf"
    )
    fallback_good = "https://data.virginia.gov/health/influenza-week-40-2024"
    bad_fixture = tmp_path / "vdh_not_found.html"
    bad_fixture.write_text(
        "<html><title>Page not found - Virginia Department of Health</title>"
        "<body>Page not found. The page you requested was not found.</body></html>",
        encoding="utf-8",
    )
    fallback_fixture = tmp_path / "virginia_fallback.html"
    fallback_fixture.write_text(
        "<html><title>Virginia influenza surveillance week 40 2024</title>"
        "<body>Virginia influenza surveillance, MMWR Week 40, "
        "September 29 - October 5, 2024. Positive influenza specimens: 42. "
        "Influenza-like illness emergency department visits: 2.1%.</body></html>",
        encoding="utf-8",
    )
    fixture_map = tmp_path / "content_fixtures.json"
    fixture_map.write_text(
        json.dumps(
            {
                "fixtures": [
                    {
                        "canonical_url": generated_bad,
                        "fixture_path": str(bad_fixture),
                        "content_type": "text/html; charset=utf-8",
                    },
                    {
                        "canonical_url": search_bad,
                        "fixture_path": str(bad_fixture),
                        "content_type": "text/html; charset=utf-8",
                    },
                    {
                        "canonical_url": fallback_good,
                        "fixture_path": str(fallback_fixture),
                        "content_type": "text/html; charset=utf-8",
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("HDC_CONTENT_FIXTURE_MAP_PATH", str(fixture_map))
    entries = [
        _search_entry(
            "src_vdh_generated_week40",
            url=generated_bad,
            discovery_method="official_coverage_requirement",
            publisher="Virginia Department of Health",
        )
        | {
            "must_fetch": True,
            "must_fetch_reason": "official_coverage_requirement",
            "coverage_requirement_ids": [req_id],
            "target_fit_status": "predicted_target_candidate",
            "target_verification_status": "predicted_unverified",
            "triage_role": "predicted_target_candidate",
            "official_report_key": "virginia_rds_weekly_report:2024:week_40",
        },
        _search_entry(
            "src_vdh_search_verified_week40",
            url=search_bad,
            discovery_method="live_search_result",
            publisher="Virginia Department of Health",
        )
        | {
            "coverage_requirement_ids": [req_id],
            "target_fit_status": "verified_target_collection",
            "target_verification_status": "verified",
            "triage_role": "verified_target_collection",
            "official_report_key": "virginia_rds_weekly_report:2024:week_40",
        },
        _search_entry(
            "src_virginia_task_fallback_week40",
            url=fallback_good,
            discovery_method="live_search_result",
            publisher="Virginia Open Data",
            source_type="structured_database",
            credibility_score=0.82,
            credibility_level="high",
        )
        | {
            "target_fit_status": "task_record_collection_candidate",
            "target_verification_status": "candidate_task_record_source",
            "triage_role": "task_record_collection_candidate",
            "source_role_final": "collection",
            "coverage_requirement_ids": [req_id],
        },
    ]
    state = _state_with_sources(entries)
    state["structured_task"] = {
        "disease": "FLU",
        "location": "VIRGINIA",
        "start_date": "2024-09-29",
        "end_date": "2024-10-05",
        "collection_mode": "direct_collection",
    }
    state["collection_spec"] = {
        "disease": "FLU",
        "geography": "VIRGINIA",
        "start_date": "2024-09-29",
        "end_date": "2024-10-05",
        "collection_mode": "direct_collection",
    }

    result = content_fetch_and_parse(state)

    request_ids = [request["source_id"] for request in result["content_fetch_requests"]]
    assert request_ids == [
        "src_vdh_generated_week40",
        "src_vdh_search_verified_week40",
        "src_virginia_task_fallback_week40",
    ]
    summary = result["content_fetch_summary"]
    assert summary["target_unusable_needs_fallback"] is True
    assert summary["fallback_fetch_attempted"] is True
    assert summary["fallback_fetch_selected_source_ids"] == [
        "src_virginia_task_fallback_week40"
    ]
    assert summary["usable_task_collection_document_count"] >= 1
    assert fallback_good in summary["usable_task_collection_urls"]


def test_direct_collection_second_pass_fetches_fallback_after_target_error_page(
    monkeypatch,
    tmp_path,
):
    from hdc_workflow.nodes.content_processing import content_fetch_and_parse

    _clear_stage7_env(monkeypatch)
    monkeypatch.setenv("HDC_COLLECTION_MODE", "direct_collection")
    monkeypatch.setenv("HDC_FETCH_SEARCH_DERIVED_SOURCES", "true")
    monkeypatch.setenv("HDC_FETCH_MAX_TOTAL_SOURCES", "1")
    req_id = "virginia_influenza_official_week_40_2024"
    generated_bad = (
        "https://www.vdh.virginia.gov/content/uploads/sites/13/"
        "2024/10/Weekly-RDS-Report_Week-40.pdf"
    )
    fallback_good = "https://data.virginia.gov/health/influenza-week-40-2024"
    bad_fixture = tmp_path / "vdh_not_found.html"
    bad_fixture.write_text(
        "<html><title>Page not found - Virginia Department of Health</title>"
        "<body>Page not found. The page you requested was not found.</body></html>",
        encoding="utf-8",
    )
    fallback_fixture = tmp_path / "virginia_fallback.html"
    fallback_fixture.write_text(
        "<html><title>Virginia influenza surveillance week 40 2024</title>"
        "<body>Virginia influenza surveillance, MMWR Week 40, "
        "September 29 - October 5, 2024. Positive influenza specimens: 42. "
        "Influenza-like illness emergency department visits: 2.1%.</body></html>",
        encoding="utf-8",
    )
    fixture_map = tmp_path / "content_fixtures.json"
    fixture_map.write_text(
        json.dumps(
            {
                "fixtures": [
                    {
                        "canonical_url": generated_bad,
                        "fixture_path": str(bad_fixture),
                        "content_type": "text/html; charset=utf-8",
                    },
                    {
                        "canonical_url": fallback_good,
                        "fixture_path": str(fallback_fixture),
                        "content_type": "text/html; charset=utf-8",
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("HDC_CONTENT_FIXTURE_MAP_PATH", str(fixture_map))
    entries = [
        _search_entry(
            "src_vdh_generated_week40",
            url=generated_bad,
            discovery_method="official_coverage_requirement",
            publisher="Virginia Department of Health",
        )
        | {
            "must_fetch": True,
            "must_fetch_reason": "official_coverage_requirement",
            "coverage_requirement_ids": [req_id],
            "target_fit_status": "predicted_target_candidate",
            "target_verification_status": "predicted_unverified",
            "triage_role": "predicted_target_candidate",
            "official_report_key": "virginia_rds_weekly_report:2024:week_40",
        },
        _search_entry(
            "src_virginia_task_fallback_week40",
            url=fallback_good,
            discovery_method="live_search_result",
            publisher="Virginia Open Data",
            source_type="structured_database",
            credibility_score=0.82,
            credibility_level="high",
        )
        | {
            "target_fit_status": "task_record_collection_candidate",
            "target_verification_status": "candidate_task_record_source",
            "triage_role": "task_record_collection_candidate",
            "source_role_final": "collection",
            "coverage_requirement_ids": [req_id],
        },
    ]
    state = _state_with_sources(entries)
    state["structured_task"] = {
        "disease": "FLU",
        "location": "VIRGINIA",
        "start_date": "2024-09-29",
        "end_date": "2024-10-05",
        "collection_mode": "direct_collection",
    }
    state["collection_spec"] = {
        "disease": "FLU",
        "geography": "VIRGINIA",
        "start_date": "2024-09-29",
        "end_date": "2024-10-05",
        "collection_mode": "direct_collection",
    }

    result = content_fetch_and_parse(state)

    request_ids = [request["source_id"] for request in result["content_fetch_requests"]]
    assert request_ids == [
        "src_vdh_generated_week40",
        "src_virginia_task_fallback_week40",
    ]
    summary = result["content_fetch_summary"]
    assert summary["target_unusable_needs_fallback"] is True
    assert summary["fallback_fetch_attempted"] is True
    assert summary["fallback_fetch_selected_source_ids"] == [
        "src_virginia_task_fallback_week40"
    ]
    assert summary["usable_task_collection_document_count"] >= 1
    assert fallback_good in summary["usable_task_collection_urls"]


def test_direct_collection_fetches_fallback_for_unusable_requirement_despite_other_usable_target(
    monkeypatch,
    tmp_path,
):
    from hdc_workflow.nodes.content_processing import content_fetch_and_parse

    _clear_stage7_env(monkeypatch)
    monkeypatch.setenv("HDC_COLLECTION_MODE", "direct_collection")
    monkeypatch.setenv("HDC_FETCH_SEARCH_DERIVED_SOURCES", "true")
    monkeypatch.setenv("HDC_FETCH_MAX_TOTAL_SOURCES", "2")
    week40_req = "virginia_influenza_official_week_40_2024"
    week41_req = "virginia_influenza_official_week_41_2024"
    week40_bad = (
        "https://www.vdh.virginia.gov/content/uploads/sites/13/"
        "2024/10/Weekly-RDS-Report_Week-40.pdf"
    )
    week41_good = (
        "https://www.vdh.virginia.gov/content/uploads/sites/13/"
        "2024/10/Weekly-RDS-Report_Week-41.pdf"
    )
    week40_fallback = "https://data.virginia.gov/health/influenza-week-40-2024"
    bad_fixture = tmp_path / "vdh_week40_not_found.html"
    bad_fixture.write_text(
        "<html><title>Page not found - Virginia Department of Health</title>"
        "<body>The requested VDH report was not found.</body></html>",
        encoding="utf-8",
    )
    week41_fixture = tmp_path / "vdh_week41.html"
    week41_fixture.write_text(
        "<html><title>VDH Weekly RDS Report Week 41</title><body>"
        "Virginia influenza surveillance, MMWR Week 41, October 6 - October 12, "
        "2024. Positive influenza specimens: 55.</body></html>",
        encoding="utf-8",
    )
    fallback_fixture = tmp_path / "virginia_week40_fallback.html"
    fallback_fixture.write_text(
        "<html><title>Virginia influenza surveillance week 40 2024</title>"
        "<body>Virginia influenza surveillance, MMWR Week 40, September 29 - "
        "October 5, 2024. Positive influenza specimens: 42.</body></html>",
        encoding="utf-8",
    )
    fixture_map = tmp_path / "content_fixtures.json"
    fixture_map.write_text(
        json.dumps(
            {
                "fixtures": [
                    {
                        "canonical_url": week40_bad,
                        "fixture_path": str(bad_fixture),
                        "content_type": "text/html; charset=utf-8",
                    },
                    {
                        "canonical_url": week41_good,
                        "fixture_path": str(week41_fixture),
                        "content_type": "text/html; charset=utf-8",
                    },
                    {
                        "canonical_url": week40_fallback,
                        "fixture_path": str(fallback_fixture),
                        "content_type": "text/html; charset=utf-8",
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("HDC_CONTENT_FIXTURE_MAP_PATH", str(fixture_map))
    entries = [
        _search_entry(
            "src_vdh_generated_week40",
            url=week40_bad,
            discovery_method="official_coverage_requirement",
            publisher="Virginia Department of Health",
        )
        | {
            "must_fetch": True,
            "coverage_requirement_ids": [week40_req],
            "target_fit_status": "predicted_target_candidate",
            "target_verification_status": "predicted_unverified",
            "triage_role": "predicted_target_candidate",
            "official_report_key": "virginia_rds_weekly_report:2024:week_40",
        },
        _search_entry(
            "src_vdh_search_verified_week41",
            url=week41_good,
            discovery_method="live_search_result",
            publisher="Virginia Department of Health",
        )
        | {
            "must_fetch": True,
            "coverage_requirement_ids": [week41_req],
            "target_fit_status": "verified_target_collection",
            "target_verification_status": "verified",
            "triage_role": "verified_target_collection",
            "official_report_key": "virginia_rds_weekly_report:2024:week_41",
        },
        _search_entry(
            "src_virginia_task_fallback_week40",
            url=week40_fallback,
            discovery_method="live_search_result",
            publisher="Virginia Open Data",
            source_type="structured_database",
        )
        | {
            "coverage_requirement_ids": [week40_req],
            "target_fit_status": "task_record_collection_candidate",
            "target_verification_status": "candidate_task_record_source",
            "triage_role": "task_record_collection_candidate",
            "source_role_final": "collection",
        },
    ]
    state = _state_with_sources(entries)
    state["structured_task"] = {
        "disease": "FLU",
        "location": "VIRGINIA",
        "start_date": "2024-09-29",
        "end_date": "2024-10-12",
        "collection_mode": "direct_collection",
    }
    state["collection_spec"] = {
        "disease": "FLU",
        "geography": "VIRGINIA",
        "start_date": "2024-09-29",
        "end_date": "2024-10-12",
        "collection_mode": "direct_collection",
    }

    result = content_fetch_and_parse(state)

    request_ids = [request["source_id"] for request in result["content_fetch_requests"]]
    assert request_ids == [
        "src_vdh_generated_week40",
        "src_vdh_search_verified_week41",
        "src_virginia_task_fallback_week40",
    ]
    summary = result["content_fetch_summary"]
    assert summary["target_unusable_needs_fallback"] is True
    assert summary["fallback_fetch_selected_source_ids"] == [
        "src_virginia_task_fallback_week40"
    ]
    assert summary["usable_task_collection_document_count"] == 2
    assert week40_fallback in summary["usable_task_collection_urls"]


def test_direct_collection_fetches_task_candidate_without_requirement_id_after_target_error(
    monkeypatch,
    tmp_path,
):
    from hdc_workflow.nodes.content_processing import content_fetch_and_parse

    _clear_stage7_env(monkeypatch)
    monkeypatch.setenv("HDC_COLLECTION_MODE", "direct_collection")
    monkeypatch.setenv("HDC_FETCH_SEARCH_DERIVED_SOURCES", "true")
    monkeypatch.setenv("HDC_FETCH_MAX_TOTAL_SOURCES", "1")
    req_id = "virginia_influenza_official_week_40_2024"
    generated_bad = (
        "https://www.vdh.virginia.gov/content/uploads/sites/13/"
        "2024/10/Weekly-RDS-Report_Week-40.pdf"
    )
    fallback_good = "https://www.vdh.virginia.gov/epidemiology/influenza-flu-in-virginia"
    bad_fixture = tmp_path / "vdh_not_found.html"
    bad_fixture.write_text(
        "<html><title>Page not found - Virginia Department of Health</title>"
        "<body>Page not found. The page you requested was not found.</body></html>",
        encoding="utf-8",
    )
    fallback_fixture = tmp_path / "vdh_landing.html"
    fallback_fixture.write_text(
        "<html><title>Influenza (Flu) in Virginia - Epidemiology</title>"
        "<body>Virginia influenza surveillance for MMWR Week 40, 2024. "
        "Influenza-like illness visits were 2.1% and positive influenza "
        "specimens were 42 for September 29 - October 5, 2024.</body></html>",
        encoding="utf-8",
    )
    fixture_map = tmp_path / "content_fixtures.json"
    fixture_map.write_text(
        json.dumps(
            {
                "fixtures": [
                    {
                        "canonical_url": generated_bad,
                        "fixture_path": str(bad_fixture),
                        "content_type": "text/html; charset=utf-8",
                    },
                    {
                        "canonical_url": fallback_good,
                        "fixture_path": str(fallback_fixture),
                        "content_type": "text/html; charset=utf-8",
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("HDC_CONTENT_FIXTURE_MAP_PATH", str(fixture_map))
    entries = [
        _search_entry(
            "src_vdh_generated_week40",
            url=generated_bad,
            discovery_method="official_coverage_requirement",
            publisher="Virginia Department of Health",
        )
        | {
            "must_fetch": True,
            "must_fetch_reason": "official_coverage_requirement",
            "coverage_requirement_ids": [req_id],
            "target_fit_status": "predicted_target_candidate",
            "target_verification_status": "predicted_unverified",
            "triage_role": "predicted_target_candidate",
        },
        _search_entry(
            "src_vdh_landing_fallback",
            url=fallback_good,
            discovery_method="live_search_result",
            publisher="Virginia Department of Health",
            source_type="official_public_health_agency",
        )
        | {
            "target_fit_status": "task_record_collection_candidate",
            "target_verification_status": "candidate_task_record_source",
            "triage_role": "task_record_collection_candidate",
            "source_role_final": "collection",
            "coverage_requirement_ids": [],
        },
    ]
    state = _state_with_sources(entries)
    state["structured_task"] = {
        "disease": "FLU",
        "location": "VIRGINIA",
        "start_date": "2024-09-29",
        "end_date": "2024-10-05",
        "collection_mode": "direct_collection",
    }
    state["collection_spec"] = {
        "disease": "FLU",
        "geography": "VIRGINIA",
        "start_date": "2024-09-29",
        "end_date": "2024-10-05",
        "collection_mode": "direct_collection",
    }

    result = content_fetch_and_parse(state)

    request_ids = [request["source_id"] for request in result["content_fetch_requests"]]
    assert request_ids == [
        "src_vdh_generated_week40",
        "src_vdh_landing_fallback",
    ]
    summary = result["content_fetch_summary"]
    assert summary["fallback_fetch_attempted"] is True
    assert summary["fallback_fetch_selected_source_ids"] == [
        "src_vdh_landing_fallback"
    ]
    assert summary["usable_task_collection_document_count"] == 1
    assert fallback_good in summary["usable_task_collection_urls"]


def test_direct_collection_follows_landing_page_task_data_links_after_target_error(
    monkeypatch,
    tmp_path,
):
    from hdc_workflow.nodes.content_processing import content_fetch_and_parse

    _clear_stage7_env(monkeypatch)
    monkeypatch.setenv("HDC_COLLECTION_MODE", "direct_collection")
    monkeypatch.setenv("HDC_FETCH_SEARCH_DERIVED_SOURCES", "true")
    monkeypatch.setenv("HDC_FETCH_MAX_TOTAL_SOURCES", "1")
    monkeypatch.setenv("HDC_DIRECT_FALLBACK_LINK_FETCH_LIMIT", "2")
    req_id = "virginia_influenza_official_week_40_2024"
    generated_bad = (
        "https://www.vdh.virginia.gov/content/uploads/sites/13/"
        "2024/10/Weekly-RDS-Report_Week-40.pdf"
    )
    landing_url = "https://www.vdh.virginia.gov/epidemiology/influenza-flu-in-virginia"
    child_url = (
        "https://www.vdh.virginia.gov/epidemiology/"
        "respiratory-diseases-in-virginia/data/week-40-2024-influenza"
    )
    bad_fixture = tmp_path / "vdh_not_found.html"
    bad_fixture.write_text(
        "<html><title>Page not found - Virginia Department of Health</title>"
        "<body>Page not found. The page you requested was not found.</body></html>",
        encoding="utf-8",
    )
    landing_fixture = tmp_path / "vdh_landing.html"
    landing_fixture.write_text(
        "<html><title>Influenza (Flu) in Virginia - Epidemiology</title><body>"
        "Virginia influenza surveillance data and dashboards. "
        f"<a href=\"{child_url}\">Virginia influenza Week 40 2024 data table</a> "
        f"Direct data link: {child_url}"
        "</body></html>",
        encoding="utf-8",
    )
    child_fixture = tmp_path / "vdh_week40_data.html"
    child_fixture.write_text(
        "<html><title>Virginia influenza Week 40 2024 data table</title><body>"
        "Virginia influenza surveillance, MMWR Week 40, September 29 - "
        "October 5, 2024. Influenza-like illness visits were 2.1% and "
        "positive influenza specimens were 42.</body></html>",
        encoding="utf-8",
    )
    fixture_map = tmp_path / "content_fixtures.json"
    fixture_map.write_text(
        json.dumps(
            {
                "fixtures": [
                    {
                        "canonical_url": generated_bad,
                        "fixture_path": str(bad_fixture),
                        "content_type": "text/html; charset=utf-8",
                    },
                    {
                        "canonical_url": landing_url,
                        "fixture_path": str(landing_fixture),
                        "content_type": "text/html; charset=utf-8",
                    },
                    {
                        "canonical_url": child_url,
                        "fixture_path": str(child_fixture),
                        "content_type": "text/html; charset=utf-8",
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("HDC_CONTENT_FIXTURE_MAP_PATH", str(fixture_map))
    entries = [
        _search_entry(
            "src_vdh_generated_week40",
            url=generated_bad,
            discovery_method="official_coverage_requirement",
            publisher="Virginia Department of Health",
        )
        | {
            "must_fetch": True,
            "must_fetch_reason": "official_coverage_requirement",
            "coverage_requirement_ids": [req_id],
            "target_fit_status": "predicted_target_candidate",
            "target_verification_status": "predicted_unverified",
            "triage_role": "predicted_target_candidate",
        },
        _search_entry(
            "src_vdh_landing_fallback",
            url=landing_url,
            discovery_method="live_search_result",
            publisher="Virginia Department of Health",
            source_type="official_public_health_agency",
        )
        | {
            "target_fit_status": "task_record_collection_candidate",
            "target_verification_status": "candidate_task_record_source",
            "triage_role": "task_record_collection_candidate",
            "source_role_final": "collection",
            "coverage_requirement_ids": [],
        },
    ]
    state = _state_with_sources(entries)
    state["structured_task"] = {
        "disease": "FLU",
        "location": "VIRGINIA",
        "start_date": "2024-09-29",
        "end_date": "2024-10-05",
        "collection_mode": "direct_collection",
    }
    state["collection_spec"] = {
        "disease": "FLU",
        "geography": "VIRGINIA",
        "start_date": "2024-09-29",
        "end_date": "2024-10-05",
        "collection_mode": "direct_collection",
    }

    result = content_fetch_and_parse(state)

    request_urls = [request["url"] for request in result["content_fetch_requests"]]
    assert child_url in request_urls
    summary = result["content_fetch_summary"]
    link_summary = summary["fallback_link_discovery_summary"]
    assert link_summary["link_fetch_attempted_count"] == 1
    assert link_summary["selected_child_urls"] == [child_url]
    assert summary["usable_task_collection_document_count"] >= 1
    assert child_url in summary["usable_task_collection_urls"]


def test_subnational_context_source_does_not_count_as_task_collection_document(
    monkeypatch,
    tmp_path,
):
    from hdc_workflow.nodes.content_processing import content_fetch_and_parse

    _clear_stage7_env(monkeypatch)
    monkeypatch.setenv("HDC_COLLECTION_MODE", "direct_collection")
    monkeypatch.setenv("HDC_FETCH_SEARCH_DERIVED_SOURCES", "true")
    monkeypatch.setenv("HDC_FETCH_MAX_TOTAL_SOURCES", "2")
    req_id = "virginia_influenza_official_week_40_2024"
    vdh_bad = (
        "https://www.vdh.virginia.gov/content/uploads/sites/3/"
        "2024/10/Weekly-RDS-Report_Week-40.pdf"
    )
    cdc_context = "https://www.cdc.gov/fluview/surveillance/2024-week-40.html"
    bad_fixture = tmp_path / "vdh_not_found.html"
    bad_fixture.write_text(
        "<html><title>Page not found - Virginia Department of Health</title>"
        "<body>The page you requested was not found.</body></html>",
        encoding="utf-8",
    )
    cdc_fixture = tmp_path / "cdc_week40.html"
    cdc_fixture.write_text(
        "<html><title>CDC FluView Week 40</title><body>"
        "Weekly US Influenza Surveillance Report, Week 40, 2024. "
        "National percent positive specimens was 0.7%.</body></html>",
        encoding="utf-8",
    )
    fixture_map = tmp_path / "content_fixtures.json"
    fixture_map.write_text(
        json.dumps(
            {
                "fixtures": [
                    {
                        "canonical_url": vdh_bad,
                        "fixture_path": str(bad_fixture),
                        "content_type": "text/html; charset=utf-8",
                    },
                    {
                        "canonical_url": cdc_context,
                        "fixture_path": str(cdc_fixture),
                        "content_type": "text/html; charset=utf-8",
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("HDC_CONTENT_FIXTURE_MAP_PATH", str(fixture_map))
    entries = [
        _search_entry(
            "src_vdh_week40",
            url=vdh_bad,
            discovery_method="live_search_result",
            publisher="Virginia Department of Health",
        )
        | {
            "must_fetch": True,
            "coverage_requirement_ids": [req_id],
            "target_fit_status": "verified_target_collection",
            "target_verification_status": "verified",
            "triage_role": "verified_target_collection",
            "source_role_final": "collection",
            "official_report_key": "virginia_rds_weekly_report:2024:week_40",
        },
        _search_entry(
            "src_cdc_national_week40",
            url=cdc_context,
            discovery_method="live_search_result",
            publisher="Centers for Disease Control and Prevention",
        )
        | {
            "target_fit_status": "verified_target",
            "target_verification_status": "verified_target",
            "source_role_final": "context",
            "triage_role": "context_only",
            "coverage_requirement_ids": [],
        },
    ]
    state = _state_with_sources(entries)
    state["structured_task"] = {
        "disease": "FLU",
        "location": "VIRGINIA",
        "start_date": "2024-09-29",
        "end_date": "2024-10-05",
        "collection_mode": "direct_collection",
    }
    state["collection_spec"] = {
        "disease": "FLU",
        "geography": "VIRGINIA",
        "start_date": "2024-09-29",
        "end_date": "2024-10-05",
        "collection_mode": "direct_collection",
    }

    result = content_fetch_and_parse(state)

    summary = result["content_fetch_summary"]
    assert summary["error_page_document_count"] == 1
    assert summary["usable_target_document_count"] == 0
    assert summary["usable_task_collection_document_count"] == 0
    assert cdc_context not in summary["usable_task_collection_urls"]
    assert summary["target_unusable_needs_fallback"] is True


def test_needs_review_search_source_is_fetchable_when_allowed(monkeypatch):
    from hdc_workflow.nodes.content_processing import content_fetch_and_parse

    _clear_stage7_env(monkeypatch)
    monkeypatch.setenv("HDC_FETCH_SEARCH_DERIVED_SOURCES", "true")
    monkeypatch.setenv("HDC_FETCH_ALLOW_NEEDS_REVIEW", "true")
    entry = _search_entry(
        "src_review_allowed",
        final_role="needs_human_review",
        credibility_level="needs_review",
        requires_review=True,
    )

    result = content_fetch_and_parse(_state_with_sources([entry]))

    requests = result.get("content_fetch_requests") or []
    assert [request["source_id"] for request in requests] == ["src_review_allowed"]
    assert result["content_fetch_summary"]["high_risk_fetch_source_count"] == 1


def test_fetch_selection_prioritizes_official_and_validation_buckets(monkeypatch):
    from hdc_workflow.nodes.content_processing import content_fetch_and_parse

    _clear_stage7_env(monkeypatch)
    monkeypatch.setenv("HDC_FETCH_SEARCH_DERIVED_SOURCES", "true")
    monkeypatch.setenv("HDC_FETCH_MAX_SEARCH_DERIVED_SOURCES", "3")
    entries = [
        _search_entry(
            "src_news_one",
            url="https://example-news.test/hantavirus-story",
            final_role="collection",
            source_type="news_and_situation_report",
            publisher="Example News",
        ),
        _search_entry(
            "src_news_two",
            url="https://example-news.test/hantavirus-followup",
            final_role="collection",
            source_type="news_and_situation_report",
            publisher="Example News",
        ),
        _search_entry(
            "src_official",
            url="https://health.ny.gov/diseases/communicable/hantavirus",
            final_role="collection",
            source_type="official_public_health_agency",
            publisher="New York State Department of Health",
        ),
        _search_entry(
            "src_validation",
            url="https://www.cdc.gov/hantavirus/surveillance/index.html",
            final_role="validation",
            source_type="official_public_health_agency",
            publisher="CDC",
        ),
    ]

    result = content_fetch_and_parse(_state_with_sources(entries))

    selected_ids = [
        request["source_id"] for request in result.get("content_fetch_requests") or []
    ]
    assert selected_ids[:2] == ["src_official", "src_validation"]
    assert "src_news_one" in selected_ids
    assert "src_news_two" not in selected_ids
    bucket_counts = result["content_fetch_summary"]["selected_fetch_bucket_counts"]
    assert bucket_counts["official_authority"] >= 2
    assert bucket_counts["validation"] == 1


def test_must_fetch_target_official_sources_bypass_excluded_role_and_fetch_limits(monkeypatch):
    from hdc_workflow.nodes.content_processing import content_fetch_and_parse

    _clear_stage7_env(monkeypatch)
    monkeypatch.setenv("HDC_FETCH_SEARCH_DERIVED_SOURCES", "true")
    monkeypatch.setenv("HDC_FETCH_MAX_SEARCH_DERIVED_SOURCES", "1")
    monkeypatch.setenv("HDC_FETCH_MAX_TOTAL_SOURCES", "1")
    entries = [
        _search_entry(
            "src_cdc_context",
            url="https://www.cdc.gov/fluview/surveillance/2024-week-43.html",
            final_role="collection",
            publisher="CDC",
        ),
        _search_entry(
            "src_vdh_week_40",
            url="https://www.vdh.virginia.gov/content/uploads/sites/13/2024/10/Weekly-RDS-Report_Week-40.pdf",
            final_role="excluded",
            credibility_level="excluded",
            credibility_score=0.0,
            publisher="Virginia Department of Health",
            source_type="official_public_health_agency",
        ),
        _search_entry(
            "src_vdh_week_41",
            url="https://www.vdh.virginia.gov/content/uploads/sites/13/2024/10/2024-25_Weekly-RDS-Report_Week-41.pdf",
            final_role="excluded",
            credibility_level="excluded",
            credibility_score=0.0,
            publisher="Virginia Department of Health",
            source_type="official_public_health_agency",
        ),
    ]
    state = _state_with_sources(entries)
    state["structured_task"] = {
        "disease": "FLU",
        "location": "VIRGINIA",
        "start_date": "2024-10-01",
        "end_date": "2024-10-10",
    }
    state["collection_spec"] = {
        "disease": "FLU",
        "geography": "VIRGINIA",
        "start_date": "2024-10-01",
        "end_date": "2024-10-10",
    }

    result = content_fetch_and_parse(state)

    selected_ids = [request["source_id"] for request in result.get("content_fetch_requests") or []]
    assert "src_vdh_week_40" in selected_ids
    assert "src_vdh_week_41" in selected_ids
    manifest = {
        row["source_id"]: row
        for row in result["content_fetch_summary"]["selection_manifest"]
    }
    assert manifest["src_vdh_week_40"]["selected_for_fetch"] is True
    assert manifest["src_vdh_week_40"]["must_fetch"] is True
    assert manifest["src_vdh_week_40"]["skip_reason"] is None
    assert result["content_fetch_summary"]["must_fetch_selected_count"] == 2


def test_direct_collection_fast_path_skips_non_target_sources_when_target_official_exists(monkeypatch):
    from hdc_workflow.nodes.content_processing import content_fetch_and_parse

    _clear_stage7_env(monkeypatch)
    monkeypatch.setenv("HDC_COLLECTION_MODE", "direct_collection")
    monkeypatch.setenv("HDC_FETCH_SEARCH_DERIVED_SOURCES", "true")
    monkeypatch.setenv("HDC_FETCH_MAX_SEARCH_DERIVED_SOURCES", "10")
    monkeypatch.setenv("HDC_FETCH_MAX_TOTAL_SOURCES", "10")
    entries = [
        _search_entry(
            "src_ny_target_week",
            url=(
                "https://www.health.ny.gov/diseases/communicable/influenza/"
                "surveillance/2024-2025/archive/2024-11-02_flu_report.pdf"
            ),
            final_role="collection",
            publisher="New York State Department of Health",
            source_type="official_public_health_agency",
        ),
        _search_entry(
            "src_cdc_2025_context",
            url="https://www.cdc.gov/fluview/surveillance/2025-week-04.html",
            final_role="collection",
            publisher="CDC",
            source_type="official_public_health_agency",
        ),
        _search_entry(
            "src_mississippi_official",
            url="https://msdh.ms.gov/msdhsite/index.cfm/14,20797,199,pdf/Flu_Surveillance_2024_44.pdf",
            final_role="collection",
            publisher="Mississippi State Department of Health",
            source_type="official_public_health_agency",
        ),
        _search_entry(
            "src_instagram",
            url="https://www.instagram.com/reel/DTeGGvXgj32/",
            final_role="collection",
            publisher="Instagram",
            source_type="social_media",
        ),
        _search_entry(
            "src_contagionlive",
            url="https://www.contagionlive.com/view/flu-surveillance-news",
            final_role="collection",
            publisher="ContagionLive",
            source_type="news_and_situation_report",
        ),
    ]
    state = _state_with_sources(entries)
    state["structured_task"] = {
        "disease": "FLU",
        "location": "New York",
        "start_date": "2024-11-01",
        "end_date": "2024-11-03",
        "collection_mode": "direct_collection",
    }
    state["collection_spec"] = {
        "disease": "FLU",
        "geography": "New York",
        "start_date": "2024-11-01",
        "end_date": "2024-11-03",
        "collection_mode": "direct_collection",
    }

    result = content_fetch_and_parse(state)

    selected_ids = [request["source_id"] for request in result.get("content_fetch_requests") or []]
    assert selected_ids == ["src_ny_target_week"]
    manifest = {
        row["source_id"]: row
        for row in result["content_fetch_summary"]["selection_manifest"]
    }
    assert manifest["src_ny_target_week"]["fetch_bucket"] == "target_official_authority"
    assert manifest["src_ny_target_week"]["selected_for_fetch"] is True
    for skipped_id in (
        "src_cdc_2025_context",
        "src_mississippi_official",
        "src_instagram",
        "src_contagionlive",
    ):
        assert manifest[skipped_id]["selected_for_fetch"] is False
        assert manifest[skipped_id]["skip_reason"] == "direct_target_official_fast_path"


def test_united_states_cdc_fluview_target_week_bypasses_context_fetch_cap(monkeypatch):
    from hdc_workflow.nodes.content_processing import content_fetch_and_parse

    _clear_stage7_env(monkeypatch)
    monkeypatch.setenv("HDC_COLLECTION_MODE", "direct_collection")
    monkeypatch.setenv("HDC_FETCH_SEARCH_DERIVED_SOURCES", "true")
    monkeypatch.setenv("HDC_FETCH_MAX_SEARCH_DERIVED_SOURCES", "1")
    monkeypatch.setenv("HDC_FETCH_MAX_TOTAL_SOURCES", "1")
    entries = [
        _search_entry(
            "src_pmc_full_season",
            url="https://pmc.ncbi.nlm.nih.gov/articles/PMC12425177",
            final_role="collection",
            publisher="National Center for Biotechnology Information",
            source_type="official_public_health_agency",
            credibility_score=0.9,
            credibility_level="high",
        ),
        _search_entry(
            "src_cdc_wrong_year",
            url="https://www.cdc.gov/fluview/surveillance/2025-week-40.html",
            final_role="context",
            publisher="CDC",
            source_type="official_public_health_agency",
            credibility_score=0.88,
            credibility_level="high",
        ),
        _search_entry(
            "src_youtube_context",
            url="https://www.youtube.com/watch?v=wN-6nVGBBc0",
            final_role="context",
            publisher="YouTube",
            source_type="social_media",
            credibility_score=0.8,
            credibility_level="high",
        ),
        _search_entry(
            "src_cdc_week_40",
            url="https://www.cdc.gov/fluview/surveillance/2024-week-40.html",
            final_role="context",
            publisher="CDC",
            source_type="official_public_health_agency",
            credibility_score=0.88,
            credibility_level="high",
        ),
    ]
    state = _state_with_sources(entries)
    state["structured_task"] = {
        "disease": "FLU",
        "location": "UNITED STATES",
        "start_date": "2024-09-29",
        "end_date": "2024-10-05",
        "collection_mode": "direct_collection",
    }
    state["collection_spec"] = {
        "disease": "FLU",
        "geography": "UNITED STATES",
        "start_date": "2024-09-29",
        "end_date": "2024-10-05",
        "collection_mode": "direct_collection",
    }

    result = content_fetch_and_parse(state)

    selected_ids = [request["source_id"] for request in result.get("content_fetch_requests") or []]
    assert selected_ids == ["src_cdc_week_40"]
    summary = result["content_fetch_summary"]
    assert summary["source_coverage_requirement_count"] == 1
    assert summary["must_fetch_selected_count"] == 1
    assert summary["direct_target_official_fast_path"] is True
    manifest = {row["source_id"]: row for row in summary["selection_manifest"]}
    assert manifest["src_cdc_week_40"]["must_fetch"] is True
    assert manifest["src_cdc_week_40"]["fetch_bucket"] == "target_official_authority"
    assert manifest["src_cdc_week_40"]["skip_reason"] is None
    for skipped_id in ("src_pmc_full_season", "src_cdc_wrong_year", "src_youtube_context"):
        assert manifest[skipped_id]["selected_for_fetch"] is False
        assert manifest[skipped_id]["skip_reason"] == "direct_target_official_fast_path"


def test_high_credibility_forum_like_source_is_not_official_fetch_bucket(monkeypatch):
    from hdc_workflow.nodes.content_processing import content_fetch_and_parse

    _clear_stage7_env(monkeypatch)
    monkeypatch.setenv("HDC_FETCH_SEARCH_DERIVED_SOURCES", "true")
    entries = [
        _search_entry(
            "src_cdph_official",
            url="https://www.cdph.ca.gov/Programs/CID/DCDC/Pages/Immunization/Influenza.aspx",
            final_role="collection",
            publisher="California Department of Public Health",
            source_type="official_public_health_agency",
        ),
        _search_entry(
            "src_flutrackers",
            url="https://flutrackers.com/forum/forum/united-states/seasonal-flu-2024",
            final_role="collection",
            publisher="FluTrackers",
            source_type="news_and_situation_report",
            credibility_score=0.99,
            credibility_level="high",
        ),
    ]

    result = content_fetch_and_parse(_state_with_sources(entries))
    manifest = {
        row["source_id"]: row
        for row in result["content_fetch_summary"]["selection_manifest"]
    }

    assert manifest["src_cdph_official"]["fetch_bucket"] == "official_authority"
    assert manifest["src_flutrackers"]["fetch_bucket"] == "forum_social"
    assert manifest["src_flutrackers"]["fetch_bucket"] != "official_authority"


def test_tavily_extract_success_populates_document_and_provider_summary(monkeypatch):
    from hdc_workflow.nodes import content_processing
    from hdc_workflow.nodes.content_processing import content_fetch_and_parse

    _clear_stage7_env(monkeypatch)
    monkeypatch.setenv("HDC_ENABLE_LIVE_FETCH", "true")
    monkeypatch.setenv("HDC_FETCH_SEARCH_DERIVED_SOURCES", "true")
    monkeypatch.setenv("HDC_EXTERNAL_FETCH_ENABLED", "true")
    monkeypatch.setenv("TAVILY_API_KEY", "tvly-test")

    def fake_extract(request, source_entry, fetch_config):
        return {
            "success": True,
            "body": b"# Hantavirus update\nNew York reported one confirmed hantavirus case.",
            "content_type": "text/markdown",
            "provider": "tavily_extract",
            "http_status_code": 200,
            "metadata": {"request_id": "req_test_001"},
        }

    monkeypatch.setattr(content_processing, "_tavily_extract_fetch", fake_extract)
    result = content_fetch_and_parse(_state_with_sources([_search_entry()]))

    documents = result.get("documents") or []
    assert len(documents) == 1
    assert documents[0]["fetch_provider"] == "tavily_extract"
    assert documents[0]["fetch_status"] == "fetched"
    assert "confirmed hantavirus case" in documents[0]["clean_text"].lower()
    summary = result["content_fetch_summary"]
    assert summary["external_fetch_enabled"] is True
    assert summary["fetch_provider_counts"]["tavily_extract"] == 1


def test_tavily_extract_failure_falls_back_to_native_requests(monkeypatch):
    from hdc_workflow.nodes import content_processing
    from hdc_workflow.nodes.content_processing import content_fetch_and_parse

    _clear_stage7_env(monkeypatch)
    monkeypatch.setenv("HDC_ENABLE_LIVE_FETCH", "true")
    monkeypatch.setenv("HDC_FETCH_SEARCH_DERIVED_SOURCES", "true")
    monkeypatch.setenv("HDC_EXTERNAL_FETCH_ENABLED", "true")
    monkeypatch.setenv("TAVILY_API_KEY", "tvly-test")

    def fake_extract(request, source_entry, fetch_config):
        return {
            "success": False,
            "provider": "tavily_extract",
            "error": "provider_error:timeout",
            "failed_results": [{"url": request.url, "error": "timeout"}],
        }

    def fake_native(request, source_entry, policy, fetch_config):
        return content_processing._make_parsed_document(
            request,
            source_entry,
            body=b"<html><title>Official update</title><body>One confirmed hantavirus case.</body></html>",
            content_type="text/html",
            http_status_code=200,
            fetch_status="fetched",
            fetched_at="2026-06-11T00:00:00+00:00",
            live=True,
            fetch_config=fetch_config,
            extra_metadata={"native_fallback_after": "tavily_extract"},
            fetch_provider="native_requests",
            provider_attempts=[
                {"provider": "tavily_extract", "success": False, "error": "provider_error:timeout"},
                {"provider": "native_requests", "success": True},
            ],
        )

    monkeypatch.setattr(content_processing, "_tavily_extract_fetch", fake_extract)
    monkeypatch.setattr(content_processing, "_fetch_live_document", fake_native)
    result = content_fetch_and_parse(_state_with_sources([_search_entry()]))

    doc = (result.get("documents") or [])[0]
    assert doc["fetch_provider"] == "native_requests"
    assert doc["metadata"]["native_fallback_after"] == "tavily_extract"
    summary = result["content_fetch_summary"]
    assert summary["fetch_provider_counts"]["native_requests"] == 1
    assert summary["external_fetch_failure_counts"]["tavily_extract"] == 1


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


def test_pdf_parser_uses_optional_fallback_when_pypdf_fails(monkeypatch):
    from hdc_workflow.nodes import content_processing
    from hdc_workflow.nodes.content_processing import _parse_pdf_content

    def fake_pypdf(_body: bytes):
        raise RuntimeError("malformed xref")

    def fake_fallback(_body: bytes):
        return {
            "clean_text": "Virginia influenza surveillance table",
            "parser_used": "pdf_test_fallback_parser",
            "parse_error": None,
        }

    monkeypatch.setattr(content_processing, "_parse_pdf_text_with_pypdf", fake_pypdf)
    monkeypatch.setattr(
        content_processing,
        "_parse_pdf_text_with_optional_fallback",
        fake_fallback,
    )

    result = _parse_pdf_content(b"%PDF-1.4 broken", parse_pdf_text=True)

    assert result["parse_status"] == "parsed_pdf"
    assert result["clean_text"] == "Virginia influenza surveillance table"
    assert result["parser_used"] == "pdf_test_fallback_parser"
    assert result["parse_error"] is None


def test_pdf_url_with_tavily_markdown_body_is_parsed_as_text_not_pdf():
    from hdc_workflow.nodes.content_processing import _parse_document_content

    result = _parse_document_content(
        b"# Weekly Respiratory Disease Surveillance Report\nWeek 45 influenza data",
        url="https://www.vdh.virginia.gov/content/uploads/sites/3/2024/11/2024-25_Weekly-RDS-Report_Week-45.pdf",
        content_type="text/markdown; charset=utf-8",
        parse_pdf_text=True,
        parse_tables=True,
    )

    assert result["parse_status"] == "parsed_text"
    assert result["parser_used"] == "text_parser"
    assert "Week 45 influenza data" in result["clean_text"]


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
