"""Stage 5 tests for controlled real source discovery/search providers."""

from __future__ import annotations

import importlib.util
import importlib
import json
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_SRC = _PROJECT_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))


SEARCH_ENV_KEYS = [
    "HDC_ENABLE_LIVE_SEARCH",
    "HDC_ENABLE_ITERATIVE_SOURCE_DISCOVERY",
    "HDC_ITERATIVE_SEARCH_ALLOW_DETERMINISTIC_FALLBACK",
    "HDC_SEARCH_MODE",
    "HDC_SEARCH_PROVIDER",
    "HDC_SEARCH_FIXTURE_PATH",
    "HDC_SEARCH_MAX_QUERIES",
    "HDC_SEARCH_MAX_RESULTS_PER_QUERY",
    "HDC_SEARCH_MAX_TOTAL_RESULTS",
    "HDC_SEARCH_TIMEOUT_SECONDS",
    "HDC_SEARCH_COMBINE_WITH_SEED_CATALOG",
    "HDC_SEARCH_CACHE_ENABLED",
    "HDC_SEARCH_PROVIDER_CHANNEL_ALLOWLIST",
]


def _clear_search_env(monkeypatch) -> None:
    for key in SEARCH_ENV_KEYS:
        monkeypatch.delenv(key, raising=False)


def _state_for(disease: str, location: str, year: str) -> dict:
    return {
        "structured_task": {
            "disease": disease,
            "location": location,
            "start_date": year,
            "end_date": year,
            "target_fields": [
                "cases_confirmed",
                "cases_unspecified",
                "deaths",
                "date_reported",
                "source_url",
                "source_type",
                "evidence_quote",
            ],
            "collection_mode": "standard",
            "user_request": f"Collect {disease} data for {location} in {year}.",
            "run_label": f"stage5_{disease}_{location}_{year}".replace(" ", "_"),
        },
        "collection_trace": [],
    }


def _run_to_source_discovery(state: dict) -> dict:
    from hdc_workflow.nodes.source_discovery import source_discovery
    from hdc_workflow.nodes.task_scope import (
        disease_intelligence_builder,
        executable_source_planning,
        profile_and_schema_setup,
        query_strategy_builder,
        task_intake_and_scope_planning,
    )

    state.update(task_intake_and_scope_planning(state))
    state.update(disease_intelligence_builder(state))
    state.update(profile_and_schema_setup(state))
    state.update(executable_source_planning(state))
    state.update(query_strategy_builder(state))
    state.update(source_discovery(state))
    return state


def _fixture_path(name: str) -> Path:
    return _PROJECT_ROOT / "src" / "hdc_workflow" / "resources" / "search_fixtures" / name


def test_direct_verified_target_sufficiency_requires_all_target_weeks():
    import importlib

    from hdc_workflow.models import SourceCandidate

    source_discovery_module = importlib.import_module(
        "hdc_workflow.nodes.source_discovery"
    )

    task = {
        "disease": "FLU",
        "location": "United States",
        "start_date": "2024-09-29",
        "end_date": "2024-10-12",
        "collection_mode": "direct_collection",
    }
    week_40 = SourceCandidate(
        source_id="src_cdc_week_40",
        url="https://www.cdc.gov/fluview/surveillance/2024-week-40.html",
        canonical_url="https://www.cdc.gov/fluview/surveillance/2024-week-40.html",
        title="CDC FluView Week 40, 2024",
        publisher="CDC",
        source_type="official_public_health_agency",
        discovery_method="live_search_result",
    )
    week_41 = SourceCandidate(
        source_id="src_cdc_week_41",
        url="https://www.cdc.gov/fluview/surveillance/2024-week-41.html",
        canonical_url="https://www.cdc.gov/fluview/surveillance/2024-week-41.html",
        title="CDC FluView Week 41, 2024",
        publisher="CDC",
        source_type="official_public_health_agency",
        discovery_method="live_search_result",
    )

    insufficient, one_week = source_discovery_module._verified_target_search_sufficient(
        [week_40],
        task,
    )
    sufficient, two_weeks = source_discovery_module._verified_target_search_sufficient(
        [week_40, week_41],
        task,
    )

    assert insufficient is False
    assert one_week["covered_target_weeks"] == [40]
    assert sufficient is True
    assert two_weeks["covered_target_weeks"] == [40, 41]


def test_subnational_target_verification_requires_geography_signal():
    import importlib

    from hdc_workflow.models import SourceCandidate

    source_discovery_module = importlib.import_module(
        "hdc_workflow.nodes.source_discovery"
    )
    task = {
        "disease": "FLU",
        "location": "VIRGINIA",
        "start_date": "2024-10-06",
        "end_date": "2024-10-12",
        "collection_mode": "direct_collection",
    }
    candidates = [
        SourceCandidate(
            source_id="src_cdc_week41_national",
            title=(
                "Weekly US Influenza Surveillance Report: Key Updates for "
                "Week 41, ending October 12, 2024 | FluView | CDC"
            ),
            url="https://www.cdc.gov/fluview/surveillance/2024-week-41.html",
            canonical_url="https://www.cdc.gov/fluview/surveillance/2024-week-41.html",
            publisher="CDC",
            source_type="official_public_health_agency",
            snippet="United States seasonal influenza activity for Week 41.",
            discovery_method="fixture_search_result",
        ),
        SourceCandidate(
            source_id="src_vdh_week41",
            title="Virginia Weekly Respiratory Disease Surveillance Report Week 41 2024",
            url=(
                "https://www.vdh.virginia.gov/content/uploads/sites/3/"
                "2024/10/Weekly-RDS-Report_Week-41.pdf"
            ),
            canonical_url=(
                "https://www.vdh.virginia.gov/content/uploads/sites/3/"
                "2024/10/Weekly-RDS-Report_Week-41.pdf"
            ),
            publisher="Virginia Department of Health",
            source_type="official_public_health_agency",
            snippet="Virginia influenza-like illness activity for Week 41.",
            discovery_method="fixture_search_result",
        ),
    ]

    verification = source_discovery_module._verify_target_sources(candidates, task)

    assert verification["verified_target_source_ids"] == ["src_vdh_week41"]
    assert any(
        "lacks verified target geography evidence" in reason
        for reason in verification["target_source_miss_reasons"]
    )


def test_target_verification_excludes_explicit_validation_role_sources():
    import importlib

    from hdc_workflow.models import SourceCandidate

    source_discovery_module = importlib.import_module(
        "hdc_workflow.nodes.source_discovery"
    )
    task = {
        "disease": "FLU",
        "location": "United States",
        "start_date": "2024-09-29",
        "end_date": "2024-10-05",
        "collection_mode": "direct_collection",
    }
    candidates = [
        SourceCandidate(
            source_id="src_cdc_week40_collection",
            title=(
                "Weekly US Influenza Surveillance Report: Key Updates for "
                "Week 40, ending October 5, 2024 | FluView | CDC"
            ),
            url="https://www.cdc.gov/fluview/surveillance/2024-week-40.html",
            canonical_url="https://www.cdc.gov/fluview/surveillance/2024-week-40.html",
            publisher="CDC",
            source_type="official_public_health_agency",
            snippet="United States seasonal influenza activity for Week 40.",
            discovery_method="fixture_search_result",
            role_hint="collection",
        ),
        SourceCandidate(
            source_id="src_cdc_week40_validation",
            title=(
                "Validation summary for United States influenza Week 40, "
                "ending October 5, 2024"
            ),
            url="https://www.cdc.gov/validation/flu-week-40-2024.html",
            canonical_url="https://www.cdc.gov/validation/flu-week-40-2024.html",
            publisher="CDC",
            source_type="official_public_health_agency",
            snippet=(
                "United States influenza validation context for Week 40, "
                "not a primary collection report."
            ),
            discovery_method="fixture_search_result",
            role_hint="validation",
        ),
    ]

    verification = source_discovery_module._verify_target_sources(candidates, task)

    assert verification["verified_target_source_ids"] == ["src_cdc_week40_collection"]
    assert any(
        "not a target collection source" in reason
        for reason in verification["target_source_miss_reasons"]
    )


def _enable_fixture_search(monkeypatch, fixture_name: str) -> None:
    _clear_search_env(monkeypatch)
    monkeypatch.setenv("HDC_SEARCH_MODE", "fixture")
    monkeypatch.setenv("HDC_SEARCH_PROVIDER", "fixture")
    monkeypatch.setenv("HDC_SEARCH_FIXTURE_PATH", str(_fixture_path(fixture_name)))
    monkeypatch.setenv("HDC_SEARCH_MAX_QUERIES", "3")
    monkeypatch.setenv("HDC_SEARCH_MAX_RESULTS_PER_QUERY", "5")
    monkeypatch.setenv("HDC_SEARCH_MAX_TOTAL_RESULTS", "15")
    monkeypatch.setenv("HDC_SEARCH_TIMEOUT_SECONDS", "15")
    monkeypatch.setenv("HDC_SEARCH_COMBINE_WITH_SEED_CATALOG", "true")


def _search_candidates(result: dict) -> list[dict]:
    return [
        candidate
        for candidate in result.get("source_candidates") or []
        if candidate.get("discovery_method") in {"fixture_search_result", "live_search_result"}
    ]


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
    assert env_updates["HDC_ENABLE_LLM_SOURCE_PLANNING"] == "false"
    assert env_updates["HDC_ENABLE_LLM_SOURCE_CRITIC"] == "false"
    assert env_updates["HDC_ENABLE_LLM_EXTRACTION"] == "false"
    assert env_updates["HDC_SEARCH_MODE"] == "fixture"
    with temporary_workflow_env(env_updates):
        return build_graph().invoke(workflow_initial_state_from_config(config))


def test_search_provider_abstraction_and_fixture_provider_exist():
    assert importlib.util.find_spec("hdc_workflow.search_providers") is not None

    from hdc_workflow.search_providers import FixtureSearchProvider, SearchProvider

    assert SearchProvider is not None
    assert FixtureSearchProvider is not None


def test_search_disabled_preserves_offline_seed_catalog_behavior(monkeypatch):
    _clear_search_env(monkeypatch)

    result = _run_to_source_discovery(_state_for("hantavirus", "New Mexico", "2024"))

    discovery = result.get("source_discovery_summary") or {}
    search_summary = result.get("source_search_execution_summary") or {}
    assert discovery.get("discovery_method") == "offline_seed_catalog"
    assert search_summary
    assert search_summary["search_enabled"] is False
    assert search_summary["live_search_enabled"] is False
    assert search_summary["fixture_search_enabled"] is False
    assert search_summary["executed_query_count"] == 0
    assert search_summary["candidate_from_search_count"] == 0
    assert {c.get("discovery_method") for c in result.get("source_candidates") or []} == {
        "offline_seed_catalog"
    }


def test_fixture_search_provider_executes_planned_queries(monkeypatch):
    _enable_fixture_search(monkeypatch, "covid19_new_york_search_results.json")

    result = _run_to_source_discovery(_state_for("COVID-19", "New York", "2024"))

    summary = result.get("source_search_execution_summary") or {}
    search_candidates = _search_candidates(result)
    assert summary["fixture_search_enabled"] is True
    assert summary["executed_query_count"] > 0
    assert summary["raw_search_result_count"] > 0
    assert summary["candidate_from_search_count"] > 0
    assert search_candidates


def test_iterative_llm_failure_falls_back_to_existing_query_inventory(
    monkeypatch,
    tmp_path,
):
    _clear_search_env(monkeypatch)
    monkeypatch.setenv("HDC_SEARCH_MODE", "fixture")
    monkeypatch.setenv("HDC_SEARCH_PROVIDER", "fixture")
    monkeypatch.setenv("HDC_SEARCH_MAX_QUERIES", "3")
    monkeypatch.setenv("HDC_SEARCH_MAX_RESULTS_PER_QUERY", "5")
    monkeypatch.setenv("HDC_SEARCH_MAX_TOTAL_RESULTS", "15")
    monkeypatch.setenv("HDC_SEARCH_COMBINE_WITH_SEED_CATALOG", "false")
    monkeypatch.setenv("HDC_ENABLE_ITERATIVE_SOURCE_DISCOVERY", "true")
    monkeypatch.setenv("HDC_ITERATIVE_SEARCH_ALLOW_DETERMINISTIC_FALLBACK", "false")
    fixture_path = tmp_path / "tb_india_results.json"
    fixture_path.write_text(
        json.dumps(
            {
                "results": [
                    {
                        "title": "India TB Report 2023 annual tuberculosis statistics",
                        "url": "https://tbcindia.gov.in/reports/india-tb-report-2023",
                        "snippet": (
                            "Official India tuberculosis annual surveillance "
                            "statistics for 2023 include incidence, notified "
                            "cases, mortality, and treatment metrics."
                        ),
                        "published_date": "2024-03-01",
                        "source": "National TB Elimination Programme India",
                        "rank": 1,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("HDC_SEARCH_FIXTURE_PATH", str(fixture_path))

    from hdc_workflow.agents import iterative_source_discovery_agent

    def _raise_initial_plan(*args, **kwargs):  # noqa: ARG001
        raise ValueError("simulated iterative planner outage")

    monkeypatch.setattr(
        iterative_source_discovery_agent,
        "plan_initial_search_iteration",
        _raise_initial_plan,
    )
    state = _state_for("Tuberculosis", "India", "2023")
    state["structured_task"].update(
        {
            "start_date": "2023-01-01",
            "end_date": "2024-01-01",
            "collection_mode": "direct_collection",
            "user_request": (
                "Collect Tuberculosis public health metrics for India in 2023."
            ),
        }
    )

    result = _run_to_source_discovery(state)

    search_summary = result.get("source_search_execution_summary") or {}
    assert search_summary["planned_query_count"] > 0
    assert search_summary["executed_query_count"] > 0
    assert search_summary["candidate_from_search_count"] > 0
    assert search_summary["stop_decision"] == "fallback_to_one_shot_search"
    assert any(
        warning.startswith("iterative_llm_initial_plan_failed")
        for warning in search_summary.get("warnings") or []
    )


def test_source_discovery_executes_search_query_inventory_when_plan_is_empty(
    monkeypatch,
    tmp_path,
):
    _clear_search_env(monkeypatch)
    monkeypatch.setenv("HDC_SEARCH_MODE", "fixture")
    monkeypatch.setenv("HDC_SEARCH_PROVIDER", "fixture")
    monkeypatch.setenv("HDC_SEARCH_MAX_QUERIES", "2")
    monkeypatch.setenv("HDC_SEARCH_MAX_RESULTS_PER_QUERY", "5")
    monkeypatch.setenv("HDC_SEARCH_MAX_TOTAL_RESULTS", "10")
    monkeypatch.setenv("HDC_SEARCH_COMBINE_WITH_SEED_CATALOG", "false")
    fixture_path = tmp_path / "measles_virginia_results.json"
    fixture_path.write_text(
        json.dumps(
            {
                "queries": [
                    {
                        "match_terms": ["measles", "virginia", "2023"],
                        "provider_channels": ["web_search", "official_site_search"],
                        "results": [
                            {
                                "title": "Virginia measles annual cases 2023",
                                "url": "https://www.vdh.virginia.gov/measles/2023-cases",
                                "snippet": (
                                    "Virginia Department of Health annual measles "
                                    "case data for 2023."
                                ),
                                "published_date": "2024-01-15",
                                "source": "Virginia Department of Health",
                                "rank": 1,
                            }
                        ],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("HDC_SEARCH_FIXTURE_PATH", str(fixture_path))

    from hdc_workflow.nodes.source_discovery import source_discovery

    state = {
        "structured_task": {
            "disease": "Measles",
            "location": "Virginia",
            "start_date": "2023-01-01",
            "end_date": "2023-12-31",
            "collection_mode": "direct_collection",
        },
        "collection_spec": {
            "disease": "Measles",
            "geography": "Virginia",
            "start_date": "2023-01-01",
            "end_date": "2023-12-31",
            "collection_mode": "direct_collection",
        },
        "agentic_source_plan": {"planned_queries": []},
        "search_query_inventory": [
            {
                "query_id": "q_inventory_001",
                "query": "measles Virginia 2023 annual cases health department",
                "provider_channel": "web_search",
                "query_type": "general_web",
                "source_type": "official_public_health_agency",
                "role_hint": "collection",
                "priority": 1,
                "expected_fields": ["cases", "date", "location", "source_url"],
                "query_source": "query_strategy_inventory",
            }
        ],
        "collection_trace": [],
    }

    result = source_discovery(state)

    search_summary = result.get("source_search_execution_summary") or {}
    assert search_summary["planned_query_count"] == 1
    assert search_summary["executed_query_count"] == 1
    assert search_summary["candidate_from_search_count"] == 1
    assert result["source_candidates"][0]["query_id"] == "q_inventory_001"


def test_source_discovery_reports_query_generation_failure_for_requirements(
    monkeypatch,
):
    _enable_fixture_search(monkeypatch, "covid19_new_york_search_results.json")
    from hdc_workflow.nodes.source_discovery import source_discovery

    state = {
        "structured_task": {
            "disease": "Measles",
            "location": "Virginia",
            "start_date": "2023-01-01",
            "end_date": "2023-12-31",
            "collection_mode": "direct_collection",
        },
        "collection_spec": {
            "disease": "Measles",
            "geography": "Virginia",
            "start_date": "2023-01-01",
            "end_date": "2023-12-31",
            "collection_mode": "direct_collection",
        },
        "source_coverage_requirements": [
            {
                "requirement_id": "virginia_measles_annual_2023",
                "disease": "Measles",
                "geography": "Virginia",
                "period_start": "2023-01-01",
                "period_end": "2023-12-31",
            }
        ],
        "agentic_source_plan": {"planned_queries": []},
        "search_query_inventory": [],
        "collection_trace": [],
    }

    result = source_discovery(state)

    search_summary = result.get("source_search_execution_summary") or {}
    assert search_summary["planned_query_count"] == 0
    assert search_summary["executed_query_count"] == 0
    assert search_summary["stop_decision"] == "query_generation_failed_for_requirements"
    assert "query_generation_failed_for_requirements" in search_summary["warnings"]


def test_direct_collection_non_hantavirus_search_does_not_mix_hantavirus_seed_catalog(
    monkeypatch,
):
    _enable_fixture_search(monkeypatch, "covid19_new_york_search_results.json")
    state = _state_for("FLU", "California", "2024")
    state["structured_task"]["collection_mode"] = "direct_collection"

    result = _run_to_source_discovery(state)

    discovery = result.get("source_discovery_summary") or {}
    search_candidates = _search_candidates(result)
    assert discovery["search_enabled"] is True
    assert discovery["candidate_from_seed_count"] == 0
    assert discovery["discovery_method"] == "fixture_search_only"
    assert "offline_seed_catalog" not in {
        candidate.get("discovery_method")
        for candidate in result.get("source_candidates") or []
    }
    assert {candidate["discovery_method"] for candidate in search_candidates} == {
        "fixture_search_result"
    }
    assert all(candidate.get("query_id") for candidate in search_candidates)
    assert all(candidate.get("query_used") for candidate in search_candidates)


def test_direct_collection_searches_to_validate_generated_official_candidate(
    monkeypatch,
):
    _enable_fixture_search(monkeypatch, "covid19_new_york_search_results.json")
    monkeypatch.setenv("HDC_DIRECT_FAST_STOP_ON_VERIFIED_TARGET", "true")
    state = _state_for("FLU", "United States", "2024")
    state["structured_task"].update(
        {
            "start_date": "2024-09-29",
            "end_date": "2024-10-05",
            "collection_mode": "direct_collection",
            "user_request": "Collect FLU surveillance data for United States from 2024-09-29 to 2024-10-05.",
        }
    )

    result = _run_to_source_discovery(state)

    search_summary = result.get("source_search_execution_summary") or {}
    discovery_summary = result.get("source_discovery_summary") or {}
    official_candidates = result.get("official_coverage_candidates") or []
    assert official_candidates
    assert all(candidate.get("must_fetch") is True for candidate in official_candidates)
    assert all(candidate.get("coverage_requirement_ids") for candidate in official_candidates)
    assert {
        candidate.get("triage_role") for candidate in official_candidates
    } == {"predicted_target_candidate"}
    assert search_summary["executed_query_count"] > 0
    assert search_summary["search_stopped_reason"] != "verified_target_source_found"
    assert search_summary["verified_target_source_count"] == 0
    assert search_summary["predicted_target_candidate_count"] >= 1
    assert search_summary["search_verified_target_source_count"] == 0
    assert discovery_summary["search_stopped_reason"] != "verified_target_source_found"
    assert discovery_summary["verified_target_source_count"] == 0
    assert discovery_summary["predicted_target_candidate_count"] >= 1


def test_direct_collection_reports_skipped_search_validation_when_search_disabled(
    monkeypatch,
):
    _clear_search_env(monkeypatch)
    state = _state_for("FLU", "United States", "2024")
    state["structured_task"].update(
        {
            "start_date": "2024-09-29",
            "end_date": "2024-10-05",
            "collection_mode": "direct_collection",
        }
    )

    result = _run_to_source_discovery(state)

    search_summary = result.get("source_search_execution_summary") or {}
    discovery_summary = result.get("source_discovery_summary") or {}
    assert discovery_summary["predicted_target_candidate_count"] >= 1
    assert discovery_summary["verified_target_source_count"] == 0
    assert "search_validation_skipped_search_disabled" in (
        search_summary.get("warnings") or []
    )
    assert "search_validation_skipped_search_disabled" in (
        discovery_summary.get("warnings") or []
    )


def test_direct_collection_partial_week_coverage_does_not_stop_as_sufficient(
    monkeypatch,
    tmp_path,
):
    _clear_search_env(monkeypatch)
    monkeypatch.setenv("HDC_DIRECT_FAST_STOP_ON_VERIFIED_TARGET", "true")
    monkeypatch.setenv("HDC_SEARCH_MODE", "fixture")
    monkeypatch.setenv("HDC_SEARCH_PROVIDER", "fixture")
    monkeypatch.setenv("HDC_SEARCH_MAX_QUERIES", "4")
    monkeypatch.setenv("HDC_SEARCH_MAX_RESULTS_PER_QUERY", "5")
    monkeypatch.setenv("HDC_SEARCH_MAX_TOTAL_RESULTS", "20")
    monkeypatch.setenv("HDC_SEARCH_COMBINE_WITH_SEED_CATALOG", "false")
    fixture_path = tmp_path / "partial_virginia_week42_only.json"
    fixture_path.write_text(
        json.dumps(
            {
                "results": [
                    {
                        "title": "VDH Weekly Respiratory Disease Surveillance Report Week 42",
                        "url": "https://www.vdh.virginia.gov/content/uploads/sites/3/2024/10/2024-25_Weekly-RDS-Report_Week-42.pdf",
                        "snippet": "Virginia Department of Health Week 42 report for October 13 - October 19, 2024.",
                        "published_date": "2024-10-19",
                        "source": "Virginia Department of Health",
                        "rank": 1,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("HDC_SEARCH_FIXTURE_PATH", str(fixture_path))
    state = _state_for("FLU", "Virginia", "2024")
    state["structured_task"].update(
        {
            "start_date": "2024-10-11",
            "end_date": "2024-11-01",
            "collection_mode": "direct_collection",
            "user_request": "Collect FLU surveillance data for Virginia from 2024-10-11 to 2024-11-01.",
        }
    )
    result = _run_to_source_discovery(state)

    discovery_summary = result["source_discovery_summary"]
    search_summary = result["source_search_execution_summary"]
    assert discovery_summary["verified_target_source_count"] == 1
    assert discovery_summary["search_stopped_reason"] != "verified_target_source_found"
    assert search_summary["search_stopped_reason"] != "verified_target_source_found"
    assert set(search_summary["target_source_miss_reasons"])


def test_fixture_covid19_search_candidates_are_disease_specific(monkeypatch):
    _enable_fixture_search(monkeypatch, "covid19_new_york_search_results.json")

    result = _run_to_source_discovery(_state_for("COVID-19", "New York", "2024"))
    text = "\n".join(
        " ".join(
            str(candidate.get(key) or "")
            for key in ("title", "snippet", "query_used", "publisher", "url")
        )
        for candidate in _search_candidates(result)
    ).lower()

    assert any(term in text for term in ("covid-19", "sars-cov-2", "new york", "2024"))
    assert "hantavirus pulmonary syndrome" not in text
    assert not any(candidate.get("seed_source_id") for candidate in _search_candidates(result))


def test_fixture_dengue_search_candidates_are_disease_specific(monkeypatch):
    _enable_fixture_search(monkeypatch, "dengue_florida_search_results.json")

    result = _run_to_source_discovery(_state_for("dengue", "Florida", "2025"))
    text = "\n".join(
        " ".join(
            str(candidate.get(key) or "")
            for key in ("title", "snippet", "query_used", "publisher", "url")
        )
        for candidate in _search_candidates(result)
    ).lower()

    assert any(term in text for term in ("dengue", "denv", "florida", "2025"))
    assert "hantavirus pulmonary syndrome" not in text
    assert not any(candidate.get("seed_source_id") for candidate in _search_candidates(result))


def test_search_result_url_validation_and_deduplication(monkeypatch):
    _enable_fixture_search(monkeypatch, "covid19_new_york_search_results.json")

    result = _run_to_source_discovery(_state_for("COVID-19", "New York", "2024"))
    summary = result.get("source_search_execution_summary") or {}
    rejection_counts = summary.get("rejection_reason_counts") or {}
    candidates = _search_candidates(result)
    canonical_urls = [candidate.get("canonical_url") for candidate in candidates]

    assert candidates
    assert len(canonical_urls) == len(set(canonical_urls))
    assert rejection_counts.get("duplicate_url", 0) >= 1
    assert rejection_counts.get("unsupported_scheme", 0) >= 1
    assert rejection_counts.get("missing_url", 0) >= 1
    assert rejection_counts.get("empty_title_and_snippet", 0) >= 1


def test_query_and_result_limits_are_enforced(monkeypatch):
    _enable_fixture_search(monkeypatch, "covid19_new_york_search_results.json")
    monkeypatch.setenv("HDC_SEARCH_MAX_QUERIES", "2")
    monkeypatch.setenv("HDC_SEARCH_MAX_RESULTS_PER_QUERY", "2")
    monkeypatch.setenv("HDC_SEARCH_MAX_TOTAL_RESULTS", "3")

    result = _run_to_source_discovery(_state_for("COVID-19", "New York", "2024"))
    summary = result.get("source_search_execution_summary") or {}
    statuses = {
        record.get("execution_status")
        for record in summary.get("query_execution_records") or []
    }

    assert summary["executed_query_count"] <= 2
    assert summary["candidate_from_search_count"] <= 3
    assert summary["skipped_query_count"] > 0
    assert "skipped_query_limit" in statuses or "skipped_total_result_limit" in statuses


def test_source_candidate_and_registry_preserve_search_provenance(monkeypatch):
    from hdc_workflow.nodes.source_discovery import source_dedup_and_registry

    _enable_fixture_search(monkeypatch, "covid19_new_york_search_results.json")
    state = _run_to_source_discovery(_state_for("COVID-19", "New York", "2024"))
    candidates = _search_candidates(state)
    assert candidates
    candidate = candidates[0]
    for key in (
        "query_id",
        "query_used",
        "search_provider",
        "search_rank",
        "provider_channel",
        "role_hint",
        "discovery_method",
        "planned_query_id",
        "canonical_url",
    ):
        assert candidate.get(key) not in (None, "", [])

    state.update(source_dedup_and_registry(state))
    registry = [
        entry
        for entry in state.get("source_registry") or []
        if entry.get("discovery_method") == "fixture_search_result"
    ]
    assert registry
    entry = registry[0]
    for key in (
        "source_id",
        "canonical_url",
        "source_type",
        "query_id",
        "query_used",
        "search_provider",
        "discovery_method",
    ):
        assert entry.get(key) not in (None, "", [])


def test_full_graph_covid19_fixture_search_smoke():
    result = _run_full_graph_from_config("covid19_new_york_2024_fixture_search_task.jsonc")
    package = result.get("final_data_package") or {}
    metadata = package.get("package_metadata") or {}
    summaries = package.get("workflow_summaries") or {}
    search_summary = summaries.get("source_search_execution_summary") or {}
    discovery = result.get("source_discovery_summary") or {}
    registry = result.get("source_registry") or []

    assert package
    assert metadata.get("disease") == "COVID-19"
    assert metadata.get("geography") == "New York"
    assert metadata.get("time_window") == "2024"
    assert search_summary["executed_query_count"] > 0
    assert discovery["discovery_method"] == "fixture_search_plus_seed_catalog"
    assert any(entry.get("discovery_method") == "fixture_search_result" for entry in registry)


def test_full_graph_dengue_fixture_search_smoke():
    result = _run_full_graph_from_config("dengue_florida_2025_fixture_search_task.jsonc")
    package = result.get("final_data_package") or {}
    metadata = package.get("package_metadata") or {}
    summaries = package.get("workflow_summaries") or {}
    search_summary = summaries.get("source_search_execution_summary") or {}
    discovery = result.get("source_discovery_summary") or {}
    registry = result.get("source_registry") or []

    assert package
    assert (metadata.get("disease") or "").lower() == "dengue"
    assert metadata.get("geography") == "Florida"
    assert metadata.get("time_window") == "2025"
    assert search_summary["executed_query_count"] > 0
    assert discovery["discovery_method"] == "fixture_search_plus_seed_catalog"
    assert any(entry.get("discovery_method") == "fixture_search_result" for entry in registry)


def test_live_search_provider_is_not_called_unless_live_mode_is_explicit(monkeypatch):
    source_discovery_module = importlib.import_module(
        "hdc_workflow.nodes.source_discovery"
    )

    class ExplodingProvider:
        def search(self, *args, **kwargs):  # noqa: ANN002, ANN003
            raise AssertionError("live provider should not be called")

    monkeypatch.setattr(
        source_discovery_module,
        "_build_search_provider",
        lambda settings: ExplodingProvider(),
        raising=False,
    )

    _clear_search_env(monkeypatch)
    _run_to_source_discovery(_state_for("COVID-19", "New York", "2024"))

    _enable_fixture_search(monkeypatch, "covid19_new_york_search_results.json")
    _run_to_source_discovery(_state_for("COVID-19", "New York", "2024"))


def test_mocked_live_search_provider_works(monkeypatch):
    source_discovery_module = importlib.import_module(
        "hdc_workflow.nodes.source_discovery"
    )

    class MockLiveProvider:
        provider = "tavily"

        def search(self, planned_query, *, max_results, timeout_seconds):  # noqa: ARG002
            query = planned_query.get("query")
            return {
                "provider": "tavily",
                "query_id": planned_query.get("query_id"),
                "query": query,
                "results": [
                    {
                        "title": "Mocked New York COVID-19 surveillance 2024",
                        "url": "https://health.ny.gov/example/mocked-covid-19-2024",
                        "snippet": "Mocked live provider metadata for COVID-19 cases in New York.",
                        "published_date": "2024-05-01",
                        "source": "Mocked Search",
                        "rank": 1,
                    }
                ],
                "raw_result_count": 1,
                "error": None,
                "warnings": [],
            }

    _clear_search_env(monkeypatch)
    monkeypatch.setenv("HDC_SEARCH_MODE", "live")
    monkeypatch.setenv("HDC_SEARCH_PROVIDER", "tavily")
    monkeypatch.setenv("HDC_ENABLE_LIVE_SEARCH", "true")
    monkeypatch.setenv("HDC_SEARCH_MAX_QUERIES", "1")
    monkeypatch.setenv("HDC_SEARCH_MAX_RESULTS_PER_QUERY", "3")
    monkeypatch.setenv("HDC_SEARCH_MAX_TOTAL_RESULTS", "3")
    monkeypatch.setenv("HDC_SEARCH_COMBINE_WITH_SEED_CATALOG", "true")
    monkeypatch.setattr(
        source_discovery_module,
        "_build_search_provider",
        lambda settings: MockLiveProvider(),
        raising=False,
    )

    result = _run_to_source_discovery(_state_for("COVID-19", "New York", "2024"))
    summary = result.get("source_search_execution_summary") or {}
    candidates = _search_candidates(result)

    assert summary["search_mode"] == "live"
    assert summary["live_search_enabled"] is True
    assert summary["executed_query_count"] > 0
    assert summary["candidate_from_search_count"] > 0
    assert {candidate["discovery_method"] for candidate in candidates} == {
        "live_search_result"
    }
    assert any("mocked-covid-19-2024" in candidate["url"] for candidate in candidates)


def test_tavily_provider_uses_bearer_authorization_header(monkeypatch):
    from hdc_workflow.search_providers import TavilySearchProvider

    captured: dict[str, object] = {}

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):  # noqa: ANN001
            return False

        def read(self):
            return (
                b'{"results":[{"title":"Official result",'
                b'"url":"https://example.org/report",'
                b'"content":"Official source metadata."}]}'
            )

    def fake_urlopen(request, *, timeout):  # noqa: ANN001
        captured["authorization"] = request.get_header("Authorization")
        captured["content_type"] = request.get_header("Content-type")
        captured["payload"] = request.data
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setenv("TAVILY_API_KEY", "tvly-test-key")
    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    response = TavilySearchProvider().search(
        {"query_id": "q1", "query": "official COVID-19 New York 2024"},
        max_results=1,
        timeout_seconds=7,
    )
    payload = json.loads(captured["payload"].decode("utf-8"))

    assert captured["authorization"] == "Bearer tvly-test-key"
    assert captured["content_type"] == "application/json"
    assert "api_key" not in payload
    assert payload["query"] == "official COVID-19 New York 2024"
    assert captured["timeout"] == 7
    assert response.results[0].url == "https://example.org/report"
