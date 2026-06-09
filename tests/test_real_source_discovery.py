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
    assert {candidate["discovery_method"] for candidate in search_candidates} == {
        "fixture_search_result"
    }
    assert all(candidate.get("query_id") for candidate in search_candidates)
    assert all(candidate.get("query_used") for candidate in search_candidates)


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
