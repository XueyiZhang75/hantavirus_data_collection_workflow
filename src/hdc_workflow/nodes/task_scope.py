"""Task scoping nodes: scope planning, profile/schema setup, query strategy."""

from __future__ import annotations

import re

from .. import llm_clients
from ..agents.source_planning_agent import plan_sources_with_llm
from ..config import (
    load_hantavirus_collection_schema,
    load_hantavirus_profile,
    load_source_strategy,
)
from ..models import (
    CollectionSchema,
    CollectionSpec,
    DiseaseProfile,
    SearchQuery,
    SearchQuerySet,
    SourceStrategy,
)
from ..state import DataCollectionState, append_trace

_TIME_WINDOW_PATTERN = re.compile(r"(\d{4})\s*(?:-|to|–|—)\s*(\d{4})", re.IGNORECASE)
_US_TOKEN_PATTERN = re.compile(r"\b(US|USA|United States)\b")


def _infer_geography(user_request: str) -> str | None:
    lowered = user_request.lower()
    if "global" in lowered or "worldwide" in lowered:
        return "global"
    if _US_TOKEN_PATTERN.search(user_request):
        return "United States of America"
    return None


def _infer_time_window(user_request: str) -> str | None:
    match = _TIME_WINDOW_PATTERN.search(user_request)
    if not match:
        return None
    start, end = match.group(1), match.group(2)
    return f"{start}-{end}"


def task_intake_and_scope_planning(state: DataCollectionState) -> dict:
    """Build a deterministic CollectionSpec with light scope inference."""

    user_request = state.get("user_request", "") or ""

    geography = _infer_geography(user_request)
    time_window = _infer_time_window(user_request)

    spec = CollectionSpec(
        task_type="public_health_case_and_outbreak_collection",
        disease="Hantavirus disease",
        target_population="human",
        data_focus="human hantavirus case, outbreak, and surveillance data",
        geography=geography,
        time_window=time_window,
        required_fields=[
            "disease",
            "virus_or_syndrome",
            "country",
            "subnational_location",
            "date_reported",
            "event_start_date",
            "event_end_date",
            "cases_confirmed",
            "cases_probable",
            "cases_suspected",
            "cases_unspecified",
            "deaths",
            "case_definition",
            "source_url",
            "source_type",
            "evidence_quote",
        ],
        source_priority=[
            "official_public_health_agency",
            "international_organization_report",
            "peer_reviewed_literature",
            "structured_database",
            "news_and_situation_report",
        ],
    )
    trace = append_trace(
        state,
        node_name="task_intake_and_scope_planning",
        message="Built deterministic CollectionSpec for hantavirus human case, outbreak, and surveillance data.",
        metadata={
            "task_type": spec.task_type,
            "disease": spec.disease,
            "geography": spec.geography,
            "time_window": spec.time_window,
        },
    )
    return {
        "collection_spec": spec.model_dump(),
        "collection_trace": trace,
    }


def hantavirus_profile_and_schema_setup(state: DataCollectionState) -> dict:
    """Load and validate the hantavirus profile, collection schema, and source strategy."""

    profile_dict = load_hantavirus_profile()
    schema_dict = load_hantavirus_collection_schema()
    strategy_dict = load_source_strategy()

    profile = DiseaseProfile(**profile_dict)
    schema = CollectionSchema(**schema_dict)
    strategy = SourceStrategy(**strategy_dict)

    trace = append_trace(
        state,
        node_name="hantavirus_profile_and_schema_setup",
        message=f"Loaded hantavirus profile ({profile.disease_standard_name}), collection schema ({schema.schema_name}), and source strategy.",
        metadata={
            "disease_standard_name": profile.disease_standard_name,
            "include_term_count": len(profile.include_terms),
            "virus_term_count": len(profile.virus_terms),
            "core_field_count": len(schema.core_fields),
            "source_category_count": len(strategy.source_categories),
        },
    )
    return {
        "disease_profile": profile.model_dump(),
        "collection_schema": schema.model_dump(),
        "source_strategy": strategy.model_dump(),
        "screening_criteria": strategy.screening_criteria.model_dump(),
        "collection_trace": trace,
    }


def _priority_for(source_type: str, strategy: SourceStrategy) -> int:
    for category in strategy.source_categories:
        if category.source_type == source_type:
            return category.priority
    return 99


def _expected_fields_default() -> list[str]:
    return [
        "cases",
        "deaths",
        "date",
        "location",
        "source_url",
        "source_type",
        "evidence_quote",
    ]


def _add_query(
    inventory: list[SearchQuery],
    seen_queries: set[str],
    next_index: dict[str, int],
    bucket_key: str,
    query_string: str,
    source_type: str,
    priority: int,
    rationale: str,
    expected_fields: list[str],
) -> None:
    if query_string in seen_queries:
        return
    seen_queries.add(query_string)
    next_index[bucket_key] = next_index.get(bucket_key, 0) + 1
    query_id = f"q_{bucket_key}_{next_index[bucket_key]:03d}"
    inventory.append(
        SearchQuery(
            query_id=query_id,
            query=query_string,
            source_type=source_type,
            priority=priority,
            rationale=rationale,
            expected_fields=expected_fields,
        )
    )


def _append_agent_queries(
    inventory_dicts: list[dict],
    seen_queries: set[str],
    agentic_source_plan: dict,
) -> int:
    added_count = 0
    proposed = agentic_source_plan.get("proposed_search_queries") or []
    if not isinstance(proposed, list):
        raise ValueError("agentic_source_plan.proposed_search_queries must be a list")

    for item in proposed:
        if not isinstance(item, dict):
            raise ValueError("agent-proposed search query must be an object")
        query = str(item.get("query") or "").strip()
        if not query or query in seen_queries:
            continue
        seen_queries.add(query)
        added_count += 1
        new_query = {
            "query_id": item.get("query_id") or f"q_agent_{added_count:03d}",
            "query": query,
            "source_type": item.get("source_type") or "news_and_situation_report",
            "priority": int(item.get("priority") or 5),
            "rationale": item.get("rationale")
            or "LLM source planning agent proposed this search query.",
            "expected_fields": list(item.get("expected_fields") or _expected_fields_default()),
            "query_source": "llm_source_planning_agent",
            "discovery_method": "llm_source_planning_agent",
        }
        inventory_dicts.append(new_query)
    return added_count


def query_strategy_builder(state: DataCollectionState) -> dict:
    """Build deterministic queries grouped both as SearchQuerySet and a typed inventory."""

    profile_dict = state.get("disease_profile") or load_hantavirus_profile()
    profile = DiseaseProfile(**profile_dict)

    strategy_dict = state.get("source_strategy") or load_source_strategy()
    strategy = SourceStrategy(**strategy_dict)

    spec_dict = state.get("collection_spec") or {}
    geography = spec_dict.get("geography")
    time_window = spec_dict.get("time_window")
    schema_dict = state.get("collection_schema") or load_hantavirus_collection_schema()

    include_terms = profile.include_terms
    syndrome_terms = profile.syndrome_terms
    virus_terms = profile.virus_terms

    geo_suffix = ""
    if geography and geography.lower() != "global":
        geo_suffix = f" {geography}"

    time_suffix = ""
    if time_window:
        time_suffix = f" {time_window}"

    expected_fields = _expected_fields_default()

    inventory: list[SearchQuery] = []
    seen: set[str] = set()
    next_index: dict[str, int] = {}

    official_priority = _priority_for("official_public_health_agency", strategy)
    international_priority = _priority_for("international_organization_report", strategy)
    literature_priority = _priority_for("peer_reviewed_literature", strategy)
    database_priority = _priority_for("structured_database", strategy)
    news_priority = _priority_for("news_and_situation_report", strategy)

    # --- official_public_health_agency ---
    official_sites = ["cdc.gov", "who.int", "ecdc.europa.eu"]
    for site in official_sites:
        for term in include_terms[:4]:
            q = f'"{term}" cases deaths site:{site}{geo_suffix}{time_suffix}'.strip()
            _add_query(
                inventory, seen, next_index, "official",
                q, "official_public_health_agency", official_priority,
                f"Target official agency content on {site} for hantavirus human cases and deaths.",
                expected_fields,
            )
        for term in syndrome_terms[:3]:
            q = f'"{term}" surveillance site:{site}{geo_suffix}{time_suffix}'.strip()
            _add_query(
                inventory, seen, next_index, "official",
                q, "official_public_health_agency", official_priority,
                f"Find {term} surveillance content from {site}.",
                expected_fields,
            )

    # --- international_organization_report ---
    intl_sites = ["who.int", "paho.org", "ecdc.europa.eu"]
    for site in intl_sites:
        for term in include_terms[:3]:
            q = f'"{term}" outbreak report site:{site}{geo_suffix}{time_suffix}'.strip()
            _add_query(
                inventory, seen, next_index, "international",
                q, "international_organization_report", international_priority,
                f"Retrieve outbreak/situation reports about {term} from {site}.",
                expected_fields,
            )
        for term in syndrome_terms[:2]:
            q = f'"{term}" surveillance report site:{site}{geo_suffix}{time_suffix}'.strip()
            _add_query(
                inventory, seen, next_index, "international",
                q, "international_organization_report", international_priority,
                f"Retrieve {term} surveillance reports from {site}.",
                expected_fields,
            )

    # --- peer_reviewed_literature ---
    for term in include_terms:
        q = f'"{term}" outbreak cases deaths epidemiology{geo_suffix}{time_suffix}'.strip()
        _add_query(
            inventory, seen, next_index, "literature",
            q, "peer_reviewed_literature", literature_priority,
            f"Find peer-reviewed epidemiology studies of {term}.",
            expected_fields,
        )
    for term in syndrome_terms:
        q = f'"{term}" human cases outbreak{geo_suffix}{time_suffix}'.strip()
        _add_query(
            inventory, seen, next_index, "literature",
            q, "peer_reviewed_literature", literature_priority,
            f"Find peer-reviewed human case series for {term}.",
            expected_fields,
        )
    for virus in virus_terms:
        q = f'"{virus}" human cases outbreak{geo_suffix}{time_suffix}'.strip()
        _add_query(
            inventory, seen, next_index, "literature",
            q, "peer_reviewed_literature", literature_priority,
            f"Find peer-reviewed studies reporting human {virus} cases.",
            expected_fields,
        )

    # --- structured_database ---
    for term in include_terms[:4]:
        q = f'"{term}" surveillance dataset{geo_suffix}{time_suffix}'.strip()
        _add_query(
            inventory, seen, next_index, "database",
            q, "structured_database", database_priority,
            f"Locate structured surveillance datasets for {term}.",
            expected_fields,
        )
        q2 = f'"{term}" outbreak data{geo_suffix}{time_suffix}'.strip()
        _add_query(
            inventory, seen, next_index, "database",
            q2, "structured_database", database_priority,
            f"Locate structured outbreak datasets for {term}.",
            expected_fields,
        )
    for term in syndrome_terms[:3]:
        q = f'"{term}" line list cases deaths{geo_suffix}{time_suffix}'.strip()
        _add_query(
            inventory, seen, next_index, "database",
            q, "structured_database", database_priority,
            f"Locate line lists or case-level data for {term}.",
            expected_fields,
        )

    # --- news_and_situation_report ---
    for term in include_terms[:4]:
        q = f'"{term}" outbreak report cases deaths{geo_suffix}{time_suffix}'.strip()
        _add_query(
            inventory, seen, next_index, "news",
            q, "news_and_situation_report", news_priority,
            f"Pick up news / situation reports about {term} outbreaks.",
            expected_fields,
        )
    for term in syndrome_terms[:3]:
        q = f'"{term}" human cases outbreak report{geo_suffix}{time_suffix}'.strip()
        _add_query(
            inventory, seen, next_index, "news",
            q, "news_and_situation_report", news_priority,
            f"Pick up news / situation reports about {term}.",
            expected_fields,
        )
    for virus in virus_terms:
        q = f'"{virus}" confirmed cases deaths{geo_suffix}{time_suffix}'.strip()
        _add_query(
            inventory, seen, next_index, "news",
            q, "news_and_situation_report", news_priority,
            f"Pick up news / alerts about confirmed {virus} cases.",
            expected_fields,
        )

    inventory_dicts = [q.model_dump() for q in inventory]

    planning_enabled = llm_clients.llm_source_planning_enabled()
    agentic_source_plan: dict | None = None
    source_planning_agent_summary = {
        "llm_source_planning_enabled": planning_enabled,
        "status": "disabled",
        "agent_query_count": 0,
        "agent_query_added_count": 0,
        "agent_candidate_hint_count": 0,
        "warnings": [],
    }

    if planning_enabled:
        try:
            agentic_source_plan = plan_sources_with_llm(
                user_request=state.get("user_request", "") or "",
                collection_spec=spec_dict,
                disease_profile=profile.model_dump(),
                source_strategy=strategy.model_dump(),
                collection_schema=schema_dict,
            )
            agent_query_count = len(
                agentic_source_plan.get("proposed_search_queries") or []
            )
            added_count = _append_agent_queries(
                inventory_dicts, seen, agentic_source_plan
            )
            source_planning_agent_summary.update(
                {
                    "status": "success",
                    "agent_name": agentic_source_plan.get("agent_name"),
                    "agent_version": agentic_source_plan.get("agent_version"),
                    "agent_query_count": agent_query_count,
                    "agent_query_added_count": added_count,
                    "agent_candidate_hint_count": len(
                        agentic_source_plan.get("candidate_source_hints") or []
                    ),
                    "human_review_recommended": bool(
                        agentic_source_plan.get("human_review_recommended", False)
                    ),
                    "warnings": list(agentic_source_plan.get("warnings") or []),
                }
            )
        except Exception as exc:  # noqa: BLE001 - agent is advisory only
            agentic_source_plan = None
            source_planning_agent_summary.update(
                {
                    "status": "failed",
                    "failure_type": type(exc).__name__,
                    "failure_message": str(exc),
                    "warnings": [
                        "llm_source_planning_failed_rule_based_fallback_used"
                    ],
                }
            )

    # Group into the backward-compatible SearchQuerySet structure.
    official_source_queries = [
        item["query"] for item in inventory_dicts
        if item.get("source_type") == "official_public_health_agency"
    ]
    literature_queries = [
        item["query"] for item in inventory_dicts
        if item.get("source_type") == "peer_reviewed_literature"
    ]
    news_and_report_queries = [
        item["query"] for item in inventory_dicts
        if item.get("source_type") in (
            "news_and_situation_report",
            "international_organization_report",
        )
    ]
    database_queries = [
        item["query"] for item in inventory_dicts
        if item.get("source_type") == "structured_database"
    ]

    query_set = SearchQuerySet(
        official_source_queries=official_source_queries,
        literature_queries=literature_queries,
        news_and_report_queries=news_and_report_queries,
        database_queries=database_queries,
    )

    trace = append_trace(
        state,
        node_name="query_strategy_builder",
        message=(
            f"Built {len(inventory_dicts)} search queries across 5 source "
            f"categories (llm_source_planning_enabled={planning_enabled})."
        ),
        metadata={
            "inventory_size": len(inventory_dicts),
            "deterministic_inventory_size": len(inventory),
            "official_source_query_count": len(query_set.official_source_queries),
            "literature_query_count": len(query_set.literature_queries),
            "news_and_report_query_count": len(query_set.news_and_report_queries),
            "database_query_count": len(query_set.database_queries),
            "geography": geography,
            "time_window": time_window,
            **source_planning_agent_summary,
        },
    )
    return {
        "search_queries": query_set.model_dump(),
        "search_query_inventory": inventory_dicts,
        "agentic_source_plan": agentic_source_plan,
        "source_planning_agent_summary": source_planning_agent_summary,
        "collection_trace": trace,
    }
