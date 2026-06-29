"""Tests for bounded LLM-led iterative source discovery."""

from __future__ import annotations

import json
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_SRC = _PROJECT_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))


SEARCH_ENV_KEYS = [
    "HDC_ENABLE_LIVE_SEARCH",
    "HDC_SEARCH_MODE",
    "HDC_SEARCH_PROVIDER",
    "HDC_SEARCH_FIXTURE_PATH",
    "HDC_SEARCH_MAX_QUERIES",
    "HDC_SEARCH_MAX_RESULTS_PER_QUERY",
    "HDC_SEARCH_MAX_TOTAL_RESULTS",
    "HDC_SEARCH_TIMEOUT_SECONDS",
    "HDC_SEARCH_COMBINE_WITH_SEED_CATALOG",
    "HDC_SEARCH_PROVIDER_CHANNEL_ALLOWLIST",
    "HDC_ENABLE_ITERATIVE_SOURCE_DISCOVERY",
    "HDC_ITERATIVE_SEARCH_MAX_ITERATIONS",
    "HDC_ITERATIVE_SEARCH_MAX_QUERIES_PER_ITERATION",
    "HDC_ITERATIVE_SEARCH_MAX_TOTAL_QUERIES",
    "HDC_ITERATIVE_SEARCH_MAX_TOTAL_RESULTS",
    "HDC_ITERATIVE_SEARCH_REQUIRE_LLM",
    "HDC_ITERATIVE_SEARCH_ALLOW_DETERMINISTIC_FALLBACK",
]


def _clear_env(monkeypatch) -> None:
    for key in SEARCH_ENV_KEYS:
        monkeypatch.delenv(key, raising=False)


def _fixture_path(tmp_path: Path) -> Path:
    path = tmp_path / "search_fixture.json"
    path.write_text(
        json.dumps(
            {
                "queries": [
                    {
                        "match_terms": ["first official"],
                        "results": [
                            {
                                "title": "Official first result",
                                "url": "https://health.example.gov/first",
                                "snippet": "Official metadata for hantavirus Virginia 2025.",
                                "source": "Health Example",
                                "published_date": "2025-04-01",
                            }
                        ],
                    },
                    {
                        "match_terms": ["refined surveillance"],
                        "results": [
                            {
                                "title": "Refined surveillance result",
                                "url": "https://surveillance.example.gov/refined",
                                "snippet": "Refined metadata with case surveillance signals.",
                                "source": "Surveillance Example",
                                "published_date": "2025-05-01",
                            }
                        ],
                    },
                    {
                        "match_terms": ["gap query"],
                        "results": [
                            {
                                "title": "Gap-filling result",
                                "url": "https://reports.example.org/gap",
                                "snippet": "Metadata returned for a non-first-N gap query.",
                                "source": "Reports Example",
                            }
                        ],
                    },
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return path


def _flu_week_fixture_path(tmp_path: Path) -> Path:
    path = tmp_path / "flu_week_search_fixture.json"
    path.write_text(
        json.dumps(
            {
                "queries": [
                    {
                        "match_terms": ["fluview week 40"],
                        "results": [
                            {
                                "title": (
                                    "Weekly US Influenza Surveillance Report: "
                                    "Key Updates for Week 47, ending November 23, 2024"
                                ),
                                "url": "https://www.cdc.gov/fluview/surveillance/2024-week-47.html",
                                "snippet": (
                                    "CDC FluView week 47 data for the 2024-2025 season."
                                ),
                                "source": "CDC",
                                "published_date": "2024-11-29",
                            },
                            {
                                "title": (
                                    "Weekly US Influenza Surveillance Report: "
                                    "Key Updates for Week 40, ending October 4, 2025"
                                ),
                                "url": "https://www.cdc.gov/fluview/surveillance/2025-week-40.html",
                                "snippet": "CDC FluView week 40 data for 2025.",
                                "source": "CDC",
                                "published_date": "2025-10-10",
                            },
                            {
                                "title": (
                                    "Weekly US Influenza Surveillance Report: "
                                    "Key Updates for Week 36, ending September 7, 2024"
                                ),
                                "url": "https://www.cdc.gov/fluview/surveillance/2024-week-36.html",
                                "snippet": "CDC FluView week 36 data for 2024.",
                                "source": "CDC",
                                "published_date": "2024-09-13",
                            },
                        ],
                    }
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return path


def _flu_week40_verified_fixture_path(tmp_path: Path) -> Path:
    path = tmp_path / "flu_week40_verified_search_fixture.json"
    path.write_text(
        json.dumps(
            {
                "queries": [
                    {
                        "match_terms": ["fluview week 40 verified"],
                        "results": [
                            {
                                "title": (
                                    "Weekly US Influenza Surveillance Report: "
                                    "Key Updates for Week 40, ending October 5, 2024"
                                ),
                                "url": "https://www.cdc.gov/fluview/surveillance/2024-week-40.html",
                                "snippet": (
                                    "CDC FluView Week 40 reports national influenza "
                                    "surveillance metrics for September 29 through "
                                    "October 5, 2024."
                                ),
                                "source": "CDC",
                                "published_date": "2024-10-11",
                            }
                        ],
                    },
                    {
                        "match_terms": ["unneeded fallback"],
                        "results": [
                            {
                                "title": "Unneeded fallback result",
                                "url": "https://example.org/fallback",
                                "snippet": "This should not be searched after target coverage.",
                                "source": "Example",
                            }
                        ],
                    },
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return path


def _flu_us_week40_state() -> dict:
    return {
        "user_request": (
            "Collect FLU surveillance data for United States from "
            "2024-09-29 to 2024-10-05."
        ),
        "structured_task": {
            "disease": "FLU",
            "location": "United States",
            "start_date": "2024-09-29",
            "end_date": "2024-10-05",
            "collection_mode": "direct_collection",
        },
        "collection_spec": {
            "disease": "FLU",
            "geography": "United States",
            "time_window": "2024-09-29 to 2024-10-05",
            "start_date": "2024-09-29",
            "end_date": "2024-10-05",
            "collection_mode": "direct_collection",
        },
        "task_acceptance_contract": {
            "disease": "FLU",
            "location": "United States",
            "start_date": "2024-09-29",
            "end_date": "2024-10-05",
        },
        "agentic_source_plan": {"planned_queries": []},
        "search_query_inventory": [],
        "collection_trace": [],
    }


def _enable_fixture_search(monkeypatch, fixture_path: Path) -> None:
    _clear_env(monkeypatch)
    monkeypatch.setenv("HDC_SEARCH_MODE", "fixture")
    monkeypatch.setenv("HDC_SEARCH_PROVIDER", "fixture")
    monkeypatch.setenv("HDC_SEARCH_FIXTURE_PATH", str(fixture_path))
    monkeypatch.setenv("HDC_SEARCH_MAX_QUERIES", "3")
    monkeypatch.setenv("HDC_SEARCH_MAX_RESULTS_PER_QUERY", "5")
    monkeypatch.setenv("HDC_SEARCH_MAX_TOTAL_RESULTS", "15")
    monkeypatch.setenv("HDC_SEARCH_COMBINE_WITH_SEED_CATALOG", "false")


def _enable_iterative(monkeypatch, *, max_iterations: int = 3) -> None:
    monkeypatch.setenv("HDC_ENABLE_ITERATIVE_SOURCE_DISCOVERY", "true")
    monkeypatch.setenv("HDC_ITERATIVE_SEARCH_MAX_ITERATIONS", str(max_iterations))
    monkeypatch.setenv("HDC_ITERATIVE_SEARCH_MAX_QUERIES_PER_ITERATION", "2")
    monkeypatch.setenv("HDC_ITERATIVE_SEARCH_MAX_TOTAL_QUERIES", "4")
    monkeypatch.setenv("HDC_ITERATIVE_SEARCH_MAX_TOTAL_RESULTS", "10")
    monkeypatch.setenv("HDC_ITERATIVE_SEARCH_REQUIRE_LLM", "true")
    monkeypatch.setenv("HDC_ITERATIVE_SEARCH_ALLOW_DETERMINISTIC_FALLBACK", "false")


def _state() -> dict:
    planned = [
        {
            "query_id": "q_exec_001",
            "query": "first official hantavirus Virginia",
            "provider_channel": "web_search",
            "query_type": "general_web",
            "source_type": "official_public_health_agency",
            "role_hint": "collection",
            "priority": 1,
            "expected_fields": ["cases", "deaths"],
            "execution_status": "planned_not_executed",
            "query_source": "executable_source_plan",
        },
        {
            "query_id": "q_exec_002",
            "query": "second first-N query",
            "provider_channel": "web_search",
            "query_type": "general_web",
            "source_type": "news_and_situation_report",
            "role_hint": "collection_support",
            "priority": 2,
            "expected_fields": ["cases"],
            "execution_status": "planned_not_executed",
            "query_source": "executable_source_plan",
        },
    ]
    return {
        "user_request": "Collect hantavirus data for Virginia from 2025 to 2026.",
        "structured_task": {
            "disease": "hantavirus",
            "location": "Virginia",
            "start_date": "2025-01-01",
            "end_date": "2026-06-01",
        },
        "collection_spec": {
            "disease": "Hantavirus disease",
            "geography": "Virginia",
            "time_window": "2025-01-01 to 2026-06-01",
        },
        "agentic_source_plan": {"planned_queries": planned},
        "search_query_inventory": planned,
        "collection_trace": [],
    }


def _query(
    query_id: str,
    query: str,
    *,
    provider_channel: str = "web_search",
    source_type: str = "official_public_health_agency",
) -> dict:
    return {
        "query_id": query_id,
        "query": query,
        "provider_channel": provider_channel,
        "query_type": "general_web",
        "source_type": source_type,
        "role_hint": "collection",
        "priority": 1,
        "expected_fields": ["cases", "deaths"],
        "query_rationale": "mock LLM selected this query.",
        "expected_source_type_or_evidence": "case data",
        "expected_trust_signal": "public health metadata",
        "language": "en",
        "target_disease_terms": ["hantavirus"],
        "target_location_terms": ["Virginia"],
        "time_terms": ["2025"],
    }


def _patch_two_iteration_agent(monkeypatch):
    from hdc_workflow.agents import iterative_source_discovery_agent as agent

    calls: dict[str, list[dict]] = {"plans": [], "observations": []}

    def fake_initial(**kwargs):  # noqa: ANN003
        calls["plans"].append(kwargs)
        return {
            "iteration_index": 1,
            "search_objective": "Find an official first source.",
            "search_reasoning": "Start with an official query.",
            "query_batch": [_query("iter_q1", "first official hantavirus Virginia")],
            "expected_evidence": ["case/death metadata"],
            "expected_source_characteristics": ["official"],
            "language_or_localization_reasoning": "English task.",
            "trust_considerations": ["public health source"],
            "stop_condition_hypothesis": "Stop if sufficient.",
            "warnings": [],
        }

    def fake_refine(**kwargs):  # noqa: ANN003
        observation = kwargs["observation"]
        calls["observations"].append(observation)
        if len(calls["observations"]) == 1:
            return {
                "iteration_index": 1,
                "decision": "continue_search",
                "decision_reason": "Need a second independent source type.",
                "coverage_assessment": "limited",
                "source_diversity_assessment": "limited",
                "trustworthiness_assessment": "promising",
                "disease_location_time_fit_assessment": "on task",
                "corroboration_potential_assessment": "needs more evidence",
                "next_query_batch": [
                    _query(
                        "iter_q2",
                        "refined surveillance hantavirus Virginia",
                        source_type="structured_database",
                    )
                ],
                "stop_reason": None,
                "warnings": [],
            }
        return {
            "iteration_index": 2,
            "decision": "stop_sufficient",
            "decision_reason": "Two metadata sources are enough for discovery.",
            "coverage_assessment": "sufficient for downstream fetch/critic",
            "source_diversity_assessment": "two domains",
            "trustworthiness_assessment": "reasonable",
            "disease_location_time_fit_assessment": "on task",
            "corroboration_potential_assessment": "possible",
            "next_query_batch": [],
            "stop_reason": "sufficient metadata coverage",
            "warnings": [],
        }

    monkeypatch.setattr(agent, "plan_initial_search_iteration", fake_initial)
    monkeypatch.setattr(agent, "refine_search_iteration", fake_refine)
    return calls


def test_iterative_mode_disabled_preserves_one_shot_behavior(monkeypatch, tmp_path):
    from hdc_workflow.nodes.source_discovery import source_discovery

    _enable_fixture_search(monkeypatch, _fixture_path(tmp_path))
    monkeypatch.setenv("HDC_SEARCH_MAX_QUERIES", "1")

    result = source_discovery(_state())

    summary = result["source_search_execution_summary"]
    iterative = result["iterative_source_discovery_summary"]
    assert summary["executed_query_count"] == 1
    assert summary["iterative_source_discovery_enabled"] is False
    assert iterative["iterative_source_discovery_enabled"] is False
    assert result["search_iteration_plans"] == []


def test_iterative_mode_calls_llm_initial_and_refinement_plan(monkeypatch, tmp_path):
    from hdc_workflow.nodes.source_discovery import source_discovery

    _enable_fixture_search(monkeypatch, _fixture_path(tmp_path))
    _enable_iterative(monkeypatch)
    calls = _patch_two_iteration_agent(monkeypatch)

    result = source_discovery(_state())

    summary = result["iterative_source_discovery_summary"]
    assert len(calls["plans"]) == 1
    assert len(calls["observations"]) == 2
    assert summary["search_iteration_count"] == 2
    assert summary["llm_refinement_call_count"] == 2
    assert summary["stop_decision"] == "stop_sufficient"
    assert result["source_search_execution_summary"]["query_source_counts"] == {
        "iterative_llm_initial_search_plan": 1,
        "iterative_llm_refinement": 1,
    }


def test_llm_observes_search_metadata_without_page_bodies(monkeypatch, tmp_path):
    from hdc_workflow.nodes.source_discovery import source_discovery

    _enable_fixture_search(monkeypatch, _fixture_path(tmp_path))
    _enable_iterative(monkeypatch)
    calls = _patch_two_iteration_agent(monkeypatch)

    source_discovery(_state())

    first_observation = calls["observations"][0]
    assert first_observation["top_result_summaries"][0]["title"] == "Official first result"
    assert first_observation["top_result_summaries"][0]["snippet"]
    assert first_observation["top_result_summaries"][0]["domain"] == "health.example.gov"
    serialized = json.dumps(first_observation, ensure_ascii=False).lower()
    assert "clean_text" not in serialized
    assert "page_body" not in serialized
    assert "raw_html" not in serialized


def test_follow_up_query_creates_candidates_with_iteration_provenance(
    monkeypatch,
    tmp_path,
):
    from hdc_workflow.nodes.source_discovery import source_discovery

    _enable_fixture_search(monkeypatch, _fixture_path(tmp_path))
    _enable_iterative(monkeypatch)
    _patch_two_iteration_agent(monkeypatch)

    result = source_discovery(_state())
    candidates = [
        candidate for candidate in result["source_candidates"]
        if candidate["discovery_method"] == "fixture_search_result"
    ]

    assert {candidate["query_source"] for candidate in candidates} == {
        "iterative_llm_initial_search_plan",
        "iterative_llm_refinement",
    }
    assert {candidate["iteration_index"] for candidate in candidates} == {1, 2}
    assert any(candidate["query_id"] == "iter_q2" for candidate in candidates)


def test_iteration_query_and_result_bounds_are_enforced(monkeypatch, tmp_path):
    from hdc_workflow.agents import iterative_source_discovery_agent as agent
    from hdc_workflow.nodes.source_discovery import source_discovery

    _enable_fixture_search(monkeypatch, _fixture_path(tmp_path))
    _enable_iterative(monkeypatch, max_iterations=5)
    monkeypatch.setenv("HDC_ITERATIVE_SEARCH_MAX_TOTAL_QUERIES", "3")
    monkeypatch.setenv("HDC_ITERATIVE_SEARCH_MAX_QUERIES_PER_ITERATION", "2")

    def fake_initial(**kwargs):  # noqa: ANN003
        return {
            "iteration_index": 1,
            "search_objective": "Run too many queries.",
            "search_reasoning": "The workflow must bound this.",
            "query_batch": [
                _query("iter_q1", "first official hantavirus Virginia"),
                _query("iter_q2", "refined surveillance hantavirus Virginia"),
                _query("iter_q3", "gap query hantavirus Virginia"),
            ],
            "expected_evidence": [],
            "expected_source_characteristics": [],
            "language_or_localization_reasoning": "",
            "trust_considerations": [],
            "stop_condition_hypothesis": "",
            "warnings": [],
        }

    def keep_going(**kwargs):  # noqa: ANN003
        return {
            "iteration_index": kwargs["observation"]["iteration_index"],
            "decision": "continue_search",
            "decision_reason": "Keep going until bounds stop it.",
            "coverage_assessment": "limited",
            "source_diversity_assessment": "limited",
            "trustworthiness_assessment": "unknown",
            "disease_location_time_fit_assessment": "unknown",
            "corroboration_potential_assessment": "unknown",
            "next_query_batch": [
                _query("iter_q4", "gap query hantavirus Virginia"),
                _query("iter_q5", "refined surveillance hantavirus Virginia"),
            ],
            "stop_reason": None,
            "warnings": [],
        }

    monkeypatch.setattr(agent, "plan_initial_search_iteration", fake_initial)
    monkeypatch.setattr(agent, "refine_search_iteration", keep_going)

    result = source_discovery(_state())
    summary = result["iterative_source_discovery_summary"]

    assert summary["total_queries_executed"] <= 3
    assert summary["stop_decision"] == "stop_limits_reached"
    assert "limit" in summary["stop_reason"]


def test_stop_sufficient_stops_after_first_observation(monkeypatch, tmp_path):
    from hdc_workflow.agents import iterative_source_discovery_agent as agent
    from hdc_workflow.nodes.source_discovery import source_discovery

    _enable_fixture_search(monkeypatch, _fixture_path(tmp_path))
    _enable_iterative(monkeypatch)

    monkeypatch.setattr(
        agent,
        "plan_initial_search_iteration",
        lambda **kwargs: {
            "iteration_index": 1,
            "search_objective": "Find one result.",
            "search_reasoning": "One query should be enough.",
            "query_batch": [_query("iter_q1", "first official hantavirus Virginia")],
            "expected_evidence": [],
            "expected_source_characteristics": [],
            "language_or_localization_reasoning": "",
            "trust_considerations": [],
            "stop_condition_hypothesis": "",
            "warnings": [],
        },
    )
    monkeypatch.setattr(
        agent,
        "refine_search_iteration",
        lambda **kwargs: {
            "iteration_index": 1,
            "decision": "stop_sufficient",
            "decision_reason": "Enough for this bounded discovery pass.",
            "coverage_assessment": "enough",
            "source_diversity_assessment": "enough",
            "trustworthiness_assessment": "enough",
            "disease_location_time_fit_assessment": "enough",
            "corroboration_potential_assessment": "enough",
            "next_query_batch": [],
            "stop_reason": "LLM decided current results are sufficient.",
            "warnings": [],
        },
    )

    result = source_discovery(_state())

    assert result["iterative_source_discovery_summary"]["search_iteration_count"] == 1
    assert result["iterative_source_discovery_summary"]["stop_decision"] == "stop_sufficient"
    assert result["source_search_execution_summary"]["executed_query_count"] == 1


def test_stop_sufficient_is_rejected_when_only_wrong_fluview_weeks_are_found(
    monkeypatch,
    tmp_path,
):
    from hdc_workflow.agents import iterative_source_discovery_agent as agent
    from hdc_workflow.nodes.source_discovery import source_discovery

    _enable_fixture_search(monkeypatch, _flu_week_fixture_path(tmp_path))
    _enable_iterative(monkeypatch, max_iterations=1)

    monkeypatch.setattr(
        agent,
        "plan_initial_search_iteration",
        lambda **kwargs: {
            "iteration_index": 1,
            "search_objective": "Find CDC FluView week 40.",
            "search_reasoning": "Search metadata may include nearby weeks.",
            "query_batch": [
                _query(
                    "iter_flu_week40",
                    "CDC FluView week 40 2024 United States influenza",
                )
            ],
            "expected_evidence": [],
            "expected_source_characteristics": [],
            "language_or_localization_reasoning": "",
            "trust_considerations": [],
            "stop_condition_hypothesis": "",
            "warnings": [],
        },
    )
    monkeypatch.setattr(
        agent,
        "refine_search_iteration",
        lambda **kwargs: {
            "iteration_index": 1,
            "decision": "stop_sufficient",
            "decision_reason": "LLM mistakenly considers the metadata sufficient.",
            "coverage_assessment": "sufficient",
            "source_diversity_assessment": "sufficient",
            "trustworthiness_assessment": "sufficient",
            "disease_location_time_fit_assessment": "sufficient",
            "corroboration_potential_assessment": "sufficient",
            "next_query_batch": [],
            "stop_reason": "CDC FluView Week 40 has been confirmed.",
            "warnings": [],
        },
    )

    result = source_discovery(_flu_us_week40_state())
    iterative_summary = result["iterative_source_discovery_summary"]
    search_summary = result["source_search_execution_summary"]

    assert iterative_summary["stop_decision"] == "target_source_missing_or_unverified"
    assert search_summary["verified_target_source_count"] == 0
    assert search_summary.get("search_stopped_reason") != "verified_target_source_found"
    assert search_summary["candidate_from_official_coverage_count"] >= 1
    assert search_summary["predicted_target_candidate_count"] >= 1
    assert search_summary["executed_query_count"] >= 1


def test_direct_collection_stops_before_refinement_when_target_week_is_verified(
    monkeypatch,
    tmp_path,
):
    from hdc_workflow.agents import iterative_source_discovery_agent as agent
    from hdc_workflow.nodes.source_discovery import source_discovery

    _enable_fixture_search(monkeypatch, _flu_week40_verified_fixture_path(tmp_path))
    _enable_iterative(monkeypatch, max_iterations=3)

    monkeypatch.setattr(
        agent,
        "plan_initial_search_iteration",
        lambda **kwargs: {
            "iteration_index": 1,
            "search_objective": "Find CDC FluView week 40.",
            "search_reasoning": "The first query should verify the target week.",
            "query_batch": [
                _query(
                    "iter_flu_week40_verified",
                    "CDC FluView week 40 verified 2024 United States influenza",
                ),
                _query(
                    "iter_fallback",
                    "unneeded fallback influenza United States 2024",
                ),
            ],
            "expected_evidence": [],
            "expected_source_characteristics": [],
            "language_or_localization_reasoning": "",
            "trust_considerations": [],
            "stop_condition_hypothesis": "",
            "warnings": [],
        },
    )

    def fail_refinement(**kwargs):
        raise AssertionError("refine_search_iteration should not be called")

    monkeypatch.setattr(agent, "refine_search_iteration", fail_refinement)

    result = source_discovery(_flu_us_week40_state())
    search_summary = result["source_search_execution_summary"]
    iterative_summary = result["iterative_source_discovery_summary"]

    assert search_summary["verified_target_source_count"] == 1
    assert search_summary["search_stopped_reason"] == "verified_target_source_found"
    assert search_summary["executed_query_count"] == 1
    assert search_summary["skipped_query_count"] == 1
    assert search_summary["query_source_counts"] == {
        "iterative_llm_initial_search_plan": 1
    }
    assert iterative_summary["search_iteration_count"] == 1


def test_invalid_llm_output_records_blocked_status_without_fake_success(
    monkeypatch,
    tmp_path,
):
    from hdc_workflow.agents import iterative_source_discovery_agent as agent
    from hdc_workflow.nodes.source_discovery import source_discovery

    _enable_fixture_search(monkeypatch, _fixture_path(tmp_path))
    _enable_iterative(monkeypatch)

    monkeypatch.setattr(
        agent,
        "plan_initial_search_iteration",
        lambda **kwargs: (_ for _ in ()).throw(ValueError("invalid llm output")),
    )

    result = source_discovery(_state())
    summary = result["iterative_source_discovery_summary"]

    assert summary["status"] == "blocked"
    assert summary["stop_decision"] == "stop_llm_unavailable"
    assert summary["total_queries_executed"] == 0
    assert result["source_candidates"] == []


def test_llm_proposed_direct_urls_are_not_inserted_as_candidates(
    monkeypatch,
    tmp_path,
):
    from hdc_workflow.agents import iterative_source_discovery_agent as agent
    from hdc_workflow.nodes.source_discovery import source_discovery

    _enable_fixture_search(monkeypatch, _fixture_path(tmp_path))
    _enable_iterative(monkeypatch)

    monkeypatch.setattr(
        agent,
        "plan_initial_search_iteration",
        lambda **kwargs: {
            "iteration_index": 1,
            "search_objective": "Unsafe URL-like query.",
            "search_reasoning": "The workflow must not ingest LLM URLs.",
            "query_batch": [_query("iter_url", "https://evil.example/path")],
            "expected_evidence": [],
            "expected_source_characteristics": [],
            "language_or_localization_reasoning": "",
            "trust_considerations": [],
            "stop_condition_hypothesis": "",
            "warnings": [],
        },
    )
    monkeypatch.setattr(
        agent,
        "refine_search_iteration",
        lambda **kwargs: {
            "iteration_index": 1,
            "decision": "stop_no_promising_sources",
            "decision_reason": "Invalid query was skipped.",
            "coverage_assessment": "none",
            "source_diversity_assessment": "none",
            "trustworthiness_assessment": "none",
            "disease_location_time_fit_assessment": "none",
            "corroboration_potential_assessment": "none",
            "next_query_batch": [],
            "stop_reason": "No valid search query.",
            "warnings": [],
        },
    )

    result = source_discovery(_state())

    assert not [c for c in result["source_candidates"] if "evil.example" in c["url"]]
    statuses = {
        record["execution_status"]
        for record in result["source_search_execution_summary"]["query_execution_records"]
    }
    assert "skipped_invalid_query" in statuses


def test_virginia_style_iterative_planning_is_not_first_n_only(
    monkeypatch,
    tmp_path,
):
    from hdc_workflow.agents import iterative_source_discovery_agent as agent
    from hdc_workflow.nodes.source_discovery import source_discovery

    _enable_fixture_search(monkeypatch, _fixture_path(tmp_path))
    _enable_iterative(monkeypatch)
    monkeypatch.setenv("HDC_SEARCH_MAX_QUERIES", "1")

    monkeypatch.setattr(
        agent,
        "plan_initial_search_iteration",
        lambda **kwargs: {
            "iteration_index": 1,
            "search_objective": "Fill source gap.",
            "search_reasoning": "Do not simply run the first planned query.",
            "query_batch": [_query("iter_gap", "gap query hantavirus Virginia")],
            "expected_evidence": [],
            "expected_source_characteristics": [],
            "language_or_localization_reasoning": "",
            "trust_considerations": [],
            "stop_condition_hypothesis": "",
            "warnings": [],
        },
    )
    monkeypatch.setattr(
        agent,
        "refine_search_iteration",
        lambda **kwargs: {
            "iteration_index": 1,
            "decision": "stop_sufficient",
            "decision_reason": "The gap query found metadata.",
            "coverage_assessment": "better than first-N",
            "source_diversity_assessment": "ok",
            "trustworthiness_assessment": "ok",
            "disease_location_time_fit_assessment": "ok",
            "corroboration_potential_assessment": "ok",
            "next_query_batch": [],
            "stop_reason": "gap query was enough",
            "warnings": [],
        },
    )

    result = source_discovery(_state())
    executed = [
        record["query"]
        for record in result["source_search_execution_summary"]["query_execution_records"]
        if record["selected_for_execution"]
    ]

    assert executed == ["gap query hantavirus Virginia"]
    assert executed[0] not in {
        query["query"] for query in _state()["agentic_source_plan"]["planned_queries"][:1]
    }


def test_skipped_iterative_queries_make_stop_status_partially_sufficient(
    monkeypatch,
    tmp_path,
):
    from hdc_workflow.agents import iterative_source_discovery_agent as agent
    from hdc_workflow.nodes.source_discovery import source_discovery

    _enable_fixture_search(monkeypatch, _fixture_path(tmp_path))
    _enable_iterative(monkeypatch)
    monkeypatch.setenv("HDC_SEARCH_MAX_TOTAL_RESULTS", "1")
    monkeypatch.setenv("HDC_ITERATIVE_SEARCH_MAX_TOTAL_RESULTS", "1")

    monkeypatch.setattr(
        agent,
        "plan_initial_search_iteration",
        lambda **kwargs: {
            "iteration_index": 1,
            "search_objective": "Collect two official query buckets.",
            "search_reasoning": "Second query should be skipped by result cap.",
            "query_batch": [
                _query("iter_first", "first official hantavirus Virginia"),
                _query("iter_refined", "refined surveillance hantavirus Virginia"),
            ],
            "expected_evidence": [],
            "expected_source_characteristics": [],
            "language_or_localization_reasoning": "",
            "trust_considerations": [],
            "stop_condition_hypothesis": "",
            "warnings": [],
        },
    )
    monkeypatch.setattr(
        agent,
        "refine_search_iteration",
        lambda **kwargs: {
            "iteration_index": 1,
            "decision": "stop_sufficient",
            "decision_reason": "LLM thinks the first result is enough.",
            "coverage_assessment": "sufficient",
            "source_diversity_assessment": "ok",
            "trustworthiness_assessment": "ok",
            "disease_location_time_fit_assessment": "ok",
            "corroboration_potential_assessment": "ok",
            "next_query_batch": [],
            "stop_reason": "enough",
            "warnings": [],
        },
    )

    result = source_discovery(_state())
    summary = result["iterative_source_discovery_summary"]

    assert summary["skipped_query_count"] == 1
    assert summary["skipped_query_ids"] == ["iter_refined"]
    assert summary["stop_decision"] == "partially_sufficient_with_unexecuted_queries"


def test_workflow_summaries_include_iterative_source_discovery_summary(
    monkeypatch,
    tmp_path,
):
    from hdc_workflow.nodes.finalization import final_data_package_builder
    from hdc_workflow.nodes.source_discovery import source_discovery

    _enable_fixture_search(monkeypatch, _fixture_path(tmp_path))
    _enable_iterative(monkeypatch)
    _patch_two_iteration_agent(monkeypatch)

    state = _state()
    state.update(source_discovery(state))
    state.update(
        {
            "source_registry": [],
            "normalized_records": [],
            "linked_events": [],
            "event_clusters": [],
            "duplicate_clusters": [],
            "validation_cases": [],
            "validation_comparisons": [],
            "validation_results": [],
            "anomaly_results": [],
            "conflicts": [],
        }
    )
    package_result = final_data_package_builder(state)

    summaries = package_result["final_data_package"]["workflow_summaries"]
    assert "iterative_source_discovery_summary" in summaries
    assert summaries["iterative_source_discovery_summary"]["search_iteration_count"] == 2
