"""Offline-safe tests for optional LLM agent hooks in the workflow."""

from __future__ import annotations

import sys
import importlib
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_SRC = _PROJECT_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from hdc_workflow import llm_clients  # noqa: E402
from hdc_workflow.agents import source_planning_agent  # noqa: E402
from hdc_workflow.graph import build_graph  # noqa: E402

source_screening_module = importlib.import_module(  # noqa: E402
    "hdc_workflow.nodes.source_screening"
)

_LIVE_CASE_DIR = _SRC / "hdc_workflow" / "resources" / "live_case_studies"
_SEED_OVERLAY = _LIVE_CASE_DIR / "mv_hondius_seed_sources.json"
_POLICY_OVERLAY = _LIVE_CASE_DIR / "mv_hondius_source_role_policy_overlay.json"
_VDH = "src_vdh_hantavirus_mv_hondius_context"
_WHO = "src_who_don600_mv_hondius_2026"


@pytest.fixture(autouse=True)
def _safe_offline_env(monkeypatch):
    for name in (
        "HDC_ENABLE_LLM_SOURCE_PLANNING",
        "HDC_ENABLE_LLM_SOURCE_CRITIC",
        "HDC_ENABLE_LLM_EXTRACTION",
        "HDC_ENABLE_LIVE_FETCH",
        "HDC_USE_FIXTURE_DOCUMENTS",
        "HDC_COLLECTION_MODE",
        "HDC_SEED_SOURCE_OVERLAY_PATH",
        "HDC_SOURCE_ROLE_POLICY_OVERLAY_PATH",
        "HDC_SOURCE_ID_ALLOWLIST",
    ):
        monkeypatch.delenv(name, raising=False)


def _initial_state() -> dict:
    return {
        "user_request": (
            "Collect global human hantavirus case, outbreak, and surveillance data "
            "from 2020 to 2026."
        ),
        "source_candidates": [],
        "source_discovery_summary": None,
        "source_registry": [],
        "source_registry_summary": None,
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
        "agentic_source_plan": None,
        "source_planning_agent_summary": None,
        "content_fetch_requests": [],
        "content_fetch_summary": None,
        "fixture_document_summary": None,
        "document_quality_summary": None,
        "final_data_package": None,
        "current_route": None,
    }


def _registry_by_id(result: dict) -> dict[str, dict]:
    return {
        entry.get("source_id"): entry
        for entry in (result.get("source_registry") or [])
    }


def test_llm_agent_feature_flags_default_off_and_no_real_helper_call(
    monkeypatch,
):
    def fail_if_called(*args, **kwargs):  # noqa: ARG001
        raise AssertionError("LLM helper should not be called when flags are off")

    monkeypatch.setattr(llm_clients, "run_structured_llm_json", fail_if_called)
    monkeypatch.setattr(llm_clients, "run_pydantic_structured_llm", fail_if_called)

    result = build_graph().invoke(_initial_state())

    planning_summary = result.get("source_planning_agent_summary") or {}
    routing_summary = result.get("source_routing_summary") or {}
    assert planning_summary.get("llm_source_planning_enabled") is False
    assert routing_summary.get("llm_source_critic_enabled") is False
    assert result.get("agentic_source_plan") is None
    assert not [
        item for item in (result.get("search_query_inventory") or [])
        if item.get("query_source") == "llm_source_planning_agent"
    ]


def test_source_planning_agent_mocked_output_appends_queries(monkeypatch):
    def mock_llm_json(*args, **kwargs):  # noqa: ARG001
        return {
            "agent_name": "source_planning_agent",
            "agent_version": "0.3-test",
            "_structured_output_mode": "provider_native",
            "disease": "Hantavirus disease",
            "geography": "global",
            "time_window": "2020-2026",
            "target_fields": ["cases", "deaths", "date", "location"],
            "source_categories": ["official_public_health_agency"],
            "proposed_search_queries": [
                {
                    "query": '"Andes virus" "MV Hondius" local health agency',
                    "source_type": "official_public_health_agency",
                    "priority": 1,
                    "rationale": "Look for non-held-out local authority coverage.",
                    "expected_fields": ["cases", "deaths", "date", "location"],
                }
            ],
            "proposed_collection_source_types": [
                "official_public_health_agency"
            ],
            "proposed_validation_source_types": [
                "international_organization_report"
            ],
            "proposed_context_source_types": ["official_background_page"],
            "candidate_source_hints": ["https://example.org/mv-hondius"],
            "reasoning_summary": "Prefer accessible non-WHO sources.",
            "human_review_recommended": True,
            "warnings": ["candidate_urls_unverified"],
        }

    monkeypatch.setenv("HDC_ENABLE_LLM_SOURCE_PLANNING", "true")
    monkeypatch.setattr(llm_clients, "run_pydantic_structured_llm", mock_llm_json)

    result = build_graph().invoke(_initial_state())
    inventory = result.get("search_query_inventory") or []
    agent_queries = [
        item for item in inventory
        if item.get("query_source") == "llm_source_planning_agent"
    ]

    assert result.get("agentic_source_plan")
    assert result["source_planning_agent_summary"]["status"] == "success"
    assert result["source_planning_agent_summary"]["agent_query_added_count"] == 1
    assert result["agentic_source_plan"]["structured_output_mode"] == "provider_native"
    assert agent_queries
    assert agent_queries[0]["query"] == (
        '"Andes virus" "MV Hondius" local health agency'
    )
    assert any(item.get("query_id", "").startswith("q_official_") for item in inventory)


def test_source_planning_pydantic_schema_defaults_and_validation():
    output = source_planning_agent.SourcePlanningOutput()

    assert output.agent_name == "source_planning_agent"
    assert output.agent_version == "0.3"
    assert output.proposed_search_queries == []
    assert output.candidate_source_hints == []

    parsed = source_planning_agent.SourcePlanningOutput(
        proposed_search_queries=[
            {
                "query": '"hantavirus" "New Mexico"',
                "source_type": "official_public_health_agency",
                "priority": "2",
            }
        ]
    )
    assert parsed.proposed_search_queries[0].priority == 2

    with pytest.raises(Exception):
        source_planning_agent.SourcePlanningOutput(
            proposed_search_queries=[{"priority": "not-an-int"}]
        )


def test_run_pydantic_structured_llm_uses_provider_native(monkeypatch):
    class FakeStructuredModel:
        def invoke(self, messages):
            assert messages
            return source_planning_agent.SourcePlanningOutput(
                proposed_search_queries=[
                    {"query": '"hantavirus" "New Mexico" official data'}
                ]
            )

    class FakeChatModel:
        def with_structured_output(self, schema_model):
            assert schema_model is source_planning_agent.SourcePlanningOutput
            return FakeStructuredModel()

    monkeypatch.setattr(
        llm_clients, "build_chat_model", lambda settings=None: FakeChatModel()
    )

    result = llm_clients.run_pydantic_structured_llm(
        system_prompt="system",
        user_prompt="user",
        schema_model=source_planning_agent.SourcePlanningOutput,
        model="fake-model",
    )

    assert result["_structured_output_mode"] == "provider_native"
    assert result["proposed_search_queries"][0]["query"] == (
        '"hantavirus" "New Mexico" official data'
    )


def test_source_planning_prompt_requires_json_only_with_skeleton():
    prompt_text = source_planning_agent._load_prompt_text()

    assert "Return exactly one JSON object" in prompt_text
    assert "Do not wrap the JSON in Markdown" in prompt_text
    assert "If uncertain" in prompt_text
    assert '"proposed_search_queries"' in prompt_text
    assert '"candidate_source_hints"' in prompt_text
    assert '"warnings"' in prompt_text


def test_source_planning_agent_empty_output_retries_once(monkeypatch):
    calls = []

    def mock_llm_json(*args, **kwargs):
        calls.append(kwargs)
        if len(calls) == 1:
            raise ValueError("LLM returned empty output.")
        return {
            "agent_name": "source_planning_agent",
            "_structured_output_mode": "provider_native",
            "proposed_search_queries": [
                {
                    "query": '"hantavirus" "New Mexico" health department cases',
                    "source_type": "official_public_health_agency",
                }
            ],
            "proposed_collection_source_types": [
                "official_public_health_agency"
            ],
            "proposed_validation_source_types": [
                "international_organization_report"
            ],
            "proposed_context_source_types": ["official_background_page"],
            "reasoning_summary": "Retry returned a minimal source plan.",
            "warnings": [],
        }

    monkeypatch.setattr(llm_clients, "run_pydantic_structured_llm", mock_llm_json)

    plan = source_planning_agent.plan_sources_with_llm(
        user_request="Plan New Mexico HPS sources without fetching webpages.",
        collection_spec={"disease": "Hantavirus disease"},
        disease_profile={
            "disease_standard_name": "Hantavirus disease",
            "include_terms": ["hantavirus"],
        },
        source_strategy={"source_categories": []},
        collection_schema={"core_fields": [{"name": "cases_confirmed"}]},
    )

    assert len(calls) == 2
    assert plan["retry_attempted"] is True
    assert plan["retry_succeeded"] is True
    assert plan["structured_output_attempted"] is True
    assert plan["structured_output_mode"] == "provider_native"
    assert plan["proposed_search_queries"][0]["query"] == (
        '"hantavirus" "New Mexico" health department cases'
    )
    assert "Return a minimal source planning JSON object" in calls[1]["user_prompt"]


def test_source_planning_agent_retry_failure_preserves_workflow_fallback(monkeypatch):
    call_count = {"count": 0}

    def empty_response(*args, **kwargs):  # noqa: ARG001
        call_count["count"] += 1
        raise ValueError("LLM returned empty output.")

    monkeypatch.setenv("HDC_ENABLE_LLM_SOURCE_PLANNING", "true")
    monkeypatch.setattr(llm_clients, "run_pydantic_structured_llm", empty_response)

    result = build_graph().invoke(_initial_state())
    inventory = result.get("search_query_inventory") or []
    summary = result.get("source_planning_agent_summary") or {}

    assert call_count["count"] == 2
    assert inventory
    assert summary.get("status") == "failed"
    assert "LLM returned empty output" in summary.get("failure_message")
    assert not [
        item for item in inventory
        if item.get("query_source") == "llm_source_planning_agent"
    ]


def test_source_planning_agent_uses_compact_payload(monkeypatch):
    captured = {}

    def mock_llm_json(*args, **kwargs):
        captured["user_prompt"] = kwargs["user_prompt"]
        return {
            "agent_name": "source_planning_agent",
            "_structured_output_mode": "provider_native",
            "proposed_search_queries": [],
            "proposed_collection_source_types": [],
            "proposed_validation_source_types": [],
            "proposed_context_source_types": [],
            "reasoning_summary": "No query needed in test.",
            "warnings": [],
        }

    monkeypatch.setattr(llm_clients, "run_pydantic_structured_llm", mock_llm_json)

    source_planning_agent.plan_sources_with_llm(
        user_request="Plan sources.",
        collection_spec={"required_fields": ["cases_confirmed"]},
        disease_profile={
            "disease_standard_name": "Hantavirus disease",
            "include_terms": ["hantavirus"],
            "raw_large_notes": "SHOULD_NOT_BE_SENT",
        },
        source_strategy={
            "source_categories": [
                {
                    "source_type": "official_public_health_agency",
                    "priority": 1,
                    "description": "SHOULD_NOT_BE_SENT",
                }
            ],
            "screening_criteria": {"include_if_all_apply": ["SHOULD_NOT_BE_SENT"]},
        },
        collection_schema={
            "core_fields": [
                {
                    "name": "cases_confirmed",
                    "description": "SHOULD_NOT_BE_SENT",
                }
            ]
        },
    )

    user_prompt = captured["user_prompt"]
    assert "cases_confirmed" in user_prompt
    assert "official_public_health_agency" in user_prompt
    assert "SHOULD_NOT_BE_SENT" not in user_prompt


def test_source_planning_agent_malformed_output_falls_back(monkeypatch):
    monkeypatch.setenv("HDC_ENABLE_LLM_SOURCE_PLANNING", "true")
    monkeypatch.setattr(
        llm_clients,
        "run_pydantic_structured_llm",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            ValueError("structured output validation failed")
        ),
    )

    result = build_graph().invoke(_initial_state())
    inventory = result.get("search_query_inventory") or []
    summary = result.get("source_planning_agent_summary") or {}

    assert inventory
    assert summary.get("status") == "failed"
    assert "llm_source_planning_failed_rule_based_fallback_used" in (
        summary.get("warnings") or []
    )
    assert not [
        item for item in inventory
        if item.get("query_source") == "llm_source_planning_agent"
    ]


def test_source_critic_agent_mocked_assessment_annotates_registry(monkeypatch):
    def mock_assess(source_entry, collection_spec, screening_policy, source_role_policy):  # noqa: ARG001
        source_id = source_entry.get("source_id")
        risky = source_id == "src_cdc_reported_cases"
        return {
            "source_id": source_id,
            "proposed_source_role": "data_source",
            "proposed_screening_decision": "include",
            "credibility_level": "high",
            "credibility_reason": "Official public health source.",
            "expected_extractable_fields": ["cases", "deaths"],
            "semantic_leakage_risk": risky,
            "semantic_leakage_reason": "May cite reserved authority." if risky else "",
            "context_only_risk": False,
            "validation_candidate_risk": risky,
            "needs_human_review": risky,
            "human_review_reason": "Review semantic leakage." if risky else "",
            "confidence": 0.84,
            "reasoning_summary": "Mocked source critic assessment.",
        }

    monkeypatch.setenv("HDC_ENABLE_LLM_SOURCE_CRITIC", "true")
    monkeypatch.setattr(
        source_screening_module, "assess_source_with_llm", mock_assess
    )

    result = build_graph().invoke(_initial_state())
    registry = _registry_by_id(result)
    entry = registry["src_cdc_reported_cases"]

    assert entry["llm_source_critic_enabled"] is True
    assert entry["llm_semantic_leakage_risk"] is True
    assert entry["llm_needs_human_review"] is True
    assert entry["llm_reasoning_summary"] == "Mocked source critic assessment."
    assert entry.get("screening_decision")
    assert entry.get("source_role")
    assert result["source_routing_summary"]["llm_semantic_leakage_count"] == 1


def test_llm_source_critic_cannot_override_validation_reserved(monkeypatch):
    def mock_assess(source_entry, collection_spec, screening_policy, source_role_policy):  # noqa: ARG001
        return {
            "source_id": source_entry.get("source_id"),
            "proposed_source_role": "data_source",
            "proposed_screening_decision": "include",
            "credibility_level": "high",
            "credibility_reason": "Mock says collect it.",
            "expected_extractable_fields": ["cases", "deaths"],
            "semantic_leakage_risk": False,
            "semantic_leakage_reason": "",
            "context_only_risk": False,
            "validation_candidate_risk": False,
            "needs_human_review": False,
            "human_review_reason": "",
            "confidence": 0.9,
            "reasoning_summary": "Mock tries to keep source collectable.",
        }

    monkeypatch.setenv("HDC_COLLECTION_MODE", "masked_validation")
    monkeypatch.setenv("HDC_ENABLE_LLM_SOURCE_CRITIC", "true")
    monkeypatch.setattr(
        source_screening_module, "assess_source_with_llm", mock_assess
    )

    result = build_graph().invoke(_initial_state())
    entry = _registry_by_id(result)["src_cdc_reported_cases"]

    assert entry["llm_proposed_source_role"] == "data_source"
    assert entry["source_role"] == "validation_reserved"
    assert entry["final_screening_decision"] == "reserved_for_validation"
    assert entry["ready_for_content_fetch"] is False
    assert {"validation_reserved", "blocked_from_collection"} <= set(
        entry.get("routing_flags") or []
    )


def test_llm_source_critic_cannot_override_context_only(monkeypatch):
    def mock_assess(source_entry, collection_spec, screening_policy, source_role_policy):  # noqa: ARG001
        return {
            "source_id": source_entry.get("source_id"),
            "proposed_source_role": "data_source",
            "proposed_screening_decision": "include",
            "credibility_level": "medium",
            "credibility_reason": "Mock says source has data.",
            "expected_extractable_fields": ["cases", "date", "location"],
            "semantic_leakage_risk": False,
            "semantic_leakage_reason": "",
            "context_only_risk": False,
            "validation_candidate_risk": False,
            "needs_human_review": False,
            "human_review_reason": "",
            "confidence": 0.88,
            "reasoning_summary": "Mock tries to override context-only.",
        }

    monkeypatch.setenv("HDC_COLLECTION_MODE", "masked_validation")
    monkeypatch.setenv("HDC_SEED_SOURCE_OVERLAY_PATH", str(_SEED_OVERLAY))
    monkeypatch.setenv("HDC_SOURCE_ROLE_POLICY_OVERLAY_PATH", str(_POLICY_OVERLAY))
    monkeypatch.setenv("HDC_ENABLE_LLM_SOURCE_CRITIC", "true")
    monkeypatch.setattr(
        source_screening_module, "assess_source_with_llm", mock_assess
    )

    result = build_graph().invoke(_initial_state())
    registry = _registry_by_id(result)
    vdh = registry[_VDH]
    who = registry[_WHO]

    assert vdh["llm_proposed_source_role"] == "data_source"
    assert vdh["source_role"] == "context_source"
    assert vdh["final_screening_decision"] == "include_for_context_fetch"
    assert vdh["ready_for_content_fetch"] is True
    assert {"context_only", "blocked_from_structured_extraction"} <= set(
        vdh.get("routing_flags") or []
    )
    assert who["source_role"] == "validation_reserved"
