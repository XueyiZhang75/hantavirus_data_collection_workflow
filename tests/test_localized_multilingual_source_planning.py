"""Repair 4 tests for localized multilingual official-source planning."""

from __future__ import annotations

import os
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_SRC = _PROJECT_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))


CHINESE_HFRS_TERMS = {"汉坦病毒", "肾综合征出血热", "流行性出血热"}
SHANGHAI_TERMS = {"上海", "上海市"}
OFFICIAL_DOMAINS = {
    "wsjkw.sh.gov.cn",
    "shcdc.sh.cn",
    "chinacdc.cn",
    "nhc.gov.cn",
}


def _state_for(
    disease: str,
    location: str,
    *,
    start_date: str = "2024-01-01",
    end_date: str = "2026-06-09",
) -> dict:
    return {
        "structured_task": {
            "disease": disease,
            "location": location,
            "start_date": start_date,
            "end_date": end_date,
            "target_fields": [
                "disease",
                "country",
                "subnational_location",
                "date_reported",
                "cases_confirmed",
                "cases_probable",
                "cases_suspected",
                "cases_unspecified",
                "deaths",
                "source_url",
                "source_type",
                "evidence_quote",
            ],
            "source_preferences": [
                "official_public_health_agency",
                "international_organization_report",
                "structured_database",
                "peer_reviewed_literature",
                "news_and_situation_report",
            ],
            "collection_mode": "standard",
            "user_request": (
                f"Collect {disease} cases and deaths for {location} "
                f"from {start_date} to {end_date}."
            ),
            "run_label": f"{disease}_{location}_repair4".replace(" ", "_"),
        },
        "collection_trace": [],
    }


def _disable_llm(monkeypatch) -> None:
    monkeypatch.setenv("HDC_ENABLE_LLM_DISEASE_INTELLIGENCE", "false")
    monkeypatch.setenv("HDC_ENABLE_LLM_SOURCE_PLANNING", "false")
    monkeypatch.setenv("HDC_ENABLE_LLM_SOURCE_CRITIC", "false")
    monkeypatch.setenv("HDC_ENABLE_LLM_SOURCE_CREDIBILITY", "false")
    monkeypatch.setenv("HDC_ENABLE_LLM_EXTRACTION", "false")


def _run_to_plan(state: dict, monkeypatch) -> dict:
    from hdc_workflow.nodes.task_scope import (
        disease_intelligence_builder,
        executable_source_planning,
        profile_and_schema_setup,
        task_intake_and_scope_planning,
    )

    _disable_llm(monkeypatch)
    state.update(task_intake_and_scope_planning(state))
    state.update(disease_intelligence_builder(state))
    state.update(profile_and_schema_setup(state))
    state.update(executable_source_planning(state))
    return state


def _run_to_query_inventory(state: dict, monkeypatch) -> dict:
    from hdc_workflow.nodes.task_scope import query_strategy_builder

    state = _run_to_plan(state, monkeypatch)
    state.update(query_strategy_builder(state))
    return state


def _query_texts(plan_or_state: dict) -> list[str]:
    if "agentic_source_plan" in plan_or_state:
        plan_or_state = plan_or_state["agentic_source_plan"]
    return [
        str(item.get("query") or "")
        for item in plan_or_state.get("planned_queries") or []
    ]


def _all_query_text(plan_or_state: dict) -> str:
    return "\n".join(_query_texts(plan_or_state))


def _localized_queries(plan_or_state: dict) -> list[dict]:
    if "agentic_source_plan" in plan_or_state:
        plan_or_state = plan_or_state["agentic_source_plan"]
    return [
        item
        for item in plan_or_state.get("planned_queries") or []
        if item.get("localized_source_hint") is True
        or "localized official source planning" in str(item.get("rationale") or "").lower()
    ]


def test_shanghai_hantavirus_disease_intelligence_includes_chinese_hfrs_terms(monkeypatch):
    state = _run_to_plan(_state_for("hantavirus", "Shanghai"), monkeypatch)
    intelligence = state["disease_intelligence"]
    joined = "\n".join(
        str(term)
        for key in (
            "aliases",
            "pathogen_terms",
            "syndrome_terms",
            "surveillance_terms",
            "official_source_terms",
            "likely_reporting_agencies",
            "disambiguation_risks",
            "warnings",
        )
        for term in intelligence.get(key) or []
    )

    assert "汉坦病毒" in joined
    assert "肾综合征出血热" in joined
    assert "流行性出血热" in joined or "HFRS" in joined
    assert "Chinese" in joined or "中文" in joined or "English web search" in joined


def test_shanghai_executable_source_plan_includes_localized_official_queries(monkeypatch):
    state = _run_to_plan(_state_for("hantavirus", "Shanghai"), monkeypatch)
    plan = state["agentic_source_plan"]
    query_text = _all_query_text(plan)
    summary = state["localized_source_planning_summary"]

    assert plan["planned_queries"]
    assert summary["enabled"] is True
    assert summary["localized_query_count"] > 0
    assert any(term in query_text for term in CHINESE_HFRS_TERMS)
    assert any(term in query_text for term in SHANGHAI_TERMS)
    assert any(domain in query_text for domain in OFFICIAL_DOMAINS)
    assert "HFRS" in query_text or "hemorrhagic fever with renal syndrome" in query_text
    assert any(year in query_text for year in ("2024", "2025", "2026"))


def test_localized_official_queries_are_prioritized(monkeypatch):
    state = _run_to_plan(_state_for("hantavirus", "Shanghai"), monkeypatch)
    queries = state["agentic_source_plan"]["planned_queries"]
    first_three = queries[:3]

    assert first_three
    assert all(
        query.get("localized_source_hint") is True
        or "localized official source planning" in query.get("rationale", "").lower()
        for query in first_three
    )
    assert any(
        any(domain in query["query"] for domain in OFFICIAL_DOMAINS)
        for query in first_three
    )
    assert not any(query.get("provider_channel") == "news_search" for query in first_three)


def test_query_inventory_preserves_localized_query_metadata(monkeypatch):
    state = _run_to_query_inventory(_state_for("hantavirus", "Shanghai"), monkeypatch)
    localized_inventory = [
        item
        for item in state["search_query_inventory"]
        if item.get("localized_source_hint") is True
    ]

    assert localized_inventory
    assert all(item["query_source"] == "executable_source_plan" for item in localized_inventory)
    assert all(
        item["execution_status"] == "planned_not_executed"
        for item in localized_inventory
    )
    assert any(item.get("jurisdiction_hint") == "Shanghai / China" for item in localized_inventory)
    assert any(item.get("official_domain_hint") in OFFICIAL_DOMAINS for item in localized_inventory)
    assert any(
        "localized official source planning" in item.get("rationale", "").lower()
        for item in localized_inventory
    )


def test_site_queries_remain_queries_not_direct_source_urls(monkeypatch):
    from hdc_workflow.nodes.source_discovery import source_discovery

    state = _run_to_query_inventory(_state_for("hantavirus", "Shanghai"), monkeypatch)
    assert any(
        item.get("query", "").startswith("site:wsjkw.sh.gov.cn")
        for item in state["search_query_inventory"]
    )

    monkeypatch.setenv("HDC_ENABLE_SOURCE_SEARCH", "false")
    discovery = source_discovery(state)
    candidates = discovery["source_candidates"]
    registry_like_urls = [candidate.get("url") or "" for candidate in candidates]

    assert candidates
    assert not any(url.startswith("site:") for url in registry_like_urls)
    assert not any("site:wsjkw.sh.gov.cn" in url for url in registry_like_urls)


def test_covid19_new_york_does_not_get_shanghai_chinese_hints(monkeypatch):
    state = _run_to_plan(
        _state_for("COVID-19", "New York", start_date="2024", end_date="2024"),
        monkeypatch,
    )
    query_text = _all_query_text(state["agentic_source_plan"])
    summary = state["localized_source_planning_summary"]

    assert "covid-19" in query_text.lower() or "sars-cov-2" in query_text.lower()
    assert summary["enabled"] is False
    assert not any(term in query_text for term in SHANGHAI_TERMS)
    assert not any(domain in query_text for domain in OFFICIAL_DOMAINS)


def test_dengue_florida_does_not_get_shanghai_chinese_hints(monkeypatch):
    state = _run_to_plan(
        _state_for("dengue", "Florida", start_date="2025", end_date="2025"),
        monkeypatch,
    )
    query_text = _all_query_text(state["agentic_source_plan"])
    summary = state["localized_source_planning_summary"]

    assert "dengue" in query_text.lower() or "denv" in query_text.lower()
    assert summary["enabled"] is False
    assert not any(term in query_text for term in SHANGHAI_TERMS)
    assert not any(domain in query_text for domain in OFFICIAL_DOMAINS)


def test_unknown_location_falls_back_safely(monkeypatch):
    state = _run_to_plan(
        _state_for("hantavirus", "SomeUnknownPlace", start_date="2025", end_date="2025"),
        monkeypatch,
    )
    query_text = _all_query_text(state["agentic_source_plan"])
    summary = state["localized_source_planning_summary"]

    assert state["agentic_source_plan"]["planned_queries"]
    assert "hantavirus" in query_text.lower() or "hfrs" in query_text.lower()
    assert "someunknownplace" in query_text.lower()
    assert summary["enabled"] is False
    assert "no_localized_jurisdiction_hints_available" in summary["warnings"]


def test_llm_source_plan_post_processing_preserves_localized_hints(monkeypatch):
    from hdc_workflow import llm_clients
    from hdc_workflow.nodes.task_scope import (
        disease_intelligence_builder,
        executable_source_planning,
        profile_and_schema_setup,
        task_intake_and_scope_planning,
    )

    def fake_structured_llm(*, schema_model, **kwargs):  # noqa: ARG001
        return {
            "plan_id": "plan_llm_generic_shanghai",
            "disease": "Hantavirus disease",
            "location": "Shanghai",
            "time_window": "2024-01-01-2026-06-09",
            "target_fields": ["cases_confirmed", "deaths", "source_url"],
            "generation_method": "llm_executable_source_plan",
            "llm_enabled": True,
            "execution_status": "planned_not_executed",
            "warnings": [],
            "source_discovery_objectives": [],
            "planned_source_categories": [],
            "planned_queries": [
                {
                    "query_id": "q_llm_001",
                    "query": '"hantavirus Shanghai" cases deaths public health 2024',
                    "query_type": "general_web",
                    "provider_channel": "web_search",
                    "source_type": "official_public_health_agency",
                    "role_hint": "collection",
                    "priority": 1,
                    "expected_fields": ["cases_confirmed", "deaths", "source_url"],
                    "disease_terms_used": ["hantavirus"],
                    "location_terms_used": ["Shanghai"],
                    "time_terms_used": ["2024"],
                    "rationale": "Generic English LLM source planning query.",
                    "execution_status": "planned_not_executed",
                }
            ],
            "source_planning_risks": [],
        }

    monkeypatch.setenv("HDC_ENABLE_LLM_DISEASE_INTELLIGENCE", "false")
    monkeypatch.setenv("HDC_ENABLE_LLM_SOURCE_PLANNING", "true")
    monkeypatch.setattr(llm_clients, "run_pydantic_structured_llm", fake_structured_llm)

    state = _state_for("hantavirus", "Shanghai")
    state.update(task_intake_and_scope_planning(state))
    state.update(disease_intelligence_builder(state))
    state.update(profile_and_schema_setup(state))
    state.update(executable_source_planning(state))

    plan = state["agentic_source_plan"]
    query_text = _all_query_text(plan)
    localized = _localized_queries(plan)

    assert plan["generation_method"] == "llm_executable_source_plan"
    assert localized
    assert any(term in query_text for term in CHINESE_HFRS_TERMS)
    assert any(domain in query_text for domain in OFFICIAL_DOMAINS)
    assert not any("https://" in query["query"] for query in plan["planned_queries"])
    assert not any("www." in query["query"] for query in plan["planned_queries"])
