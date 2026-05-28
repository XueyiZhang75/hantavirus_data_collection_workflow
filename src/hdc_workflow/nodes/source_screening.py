"""Source screening, critic review, and source-level routing (Step 4).

Deterministic rule-based implementation. No LLM, no network. Later steps can
replace the rule-based logic with structured-output LLM agents without
changing node names or graph topology.
"""

from __future__ import annotations

from collections import Counter

from ..config import load_source_screening_policy
from ..models import (
    HumanReviewItem,
    SourceCriticResult,
    SourceFinalRoutingDecision,
    SourceRegistryEntry,
    SourceScreeningPolicy,
    SourceScreeningResult,
)
from ..state import DataCollectionState, append_trace


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------


def _text_blob(entry: dict) -> str:
    """Combine relevant metadata fields into a single lowercase text blob."""

    parts: list[str] = []
    for key in ("title", "publisher", "source_type", "source_purpose", "notes"):
        value = entry.get(key)
        if value:
            parts.append(str(value))
    for key in ("matched_terms", "expected_fields"):
        items = entry.get(key) or []
        if items:
            parts.append(" ".join(str(item) for item in items))
    query_used = entry.get("query_used")
    if query_used:
        parts.append(str(query_used))
    return " ".join(parts).lower()


def _source_content_text(entry: dict) -> str:
    """Source-only text for signal scans.

    Excludes `query_used` because the query string describes *how we found*
    the source, not *what the source itself contains*. Including the query
    would otherwise make every candidate inherit terms like "cases" or
    "deaths" from the discovery query and incorrectly classify context pages
    as data sources.
    """

    parts: list[str] = []
    for key in ("title", "publisher", "source_type", "source_purpose", "notes"):
        value = entry.get(key)
        if value:
            parts.append(str(value))
    matched_terms = entry.get("matched_terms") or []
    if matched_terms:
        parts.append(" ".join(str(item) for item in matched_terms))
    return " ".join(parts).lower()


def _contains_any(text: str, terms: list[str]) -> bool:
    for term in terms:
        if not term:
            continue
        if term.lower() in text:
            return True
    return False


# ---------------------------------------------------------------------------
# Role classification
# ---------------------------------------------------------------------------


def _classify_source_role(
    entry: dict,
    policy: SourceScreeningPolicy,
) -> tuple[str, list[str]]:
    """Return (source_role, flags) using rule-based metadata classification."""

    flags: list[str] = []

    url = entry.get("canonical_url") or entry.get("url") or ""
    publisher = entry.get("publisher")
    expected_fields = entry.get("expected_fields") or []
    # Signal scans use source-only text so the discovery query string does
    # not bleed data-source terms into every candidate.
    source_text = _source_content_text(entry)

    # 1. Placeholder URI
    for prefix in policy.placeholder_uri_prefixes:
        if url.startswith(prefix):
            return "placeholder_source", flags

    # 2. Search endpoint publisher
    if publisher in policy.search_endpoint_publishers:
        return "search_endpoint", flags

    # 3. expected_fields indicates case/death/date/location
    data_fields = {"cases", "deaths", "date", "location"}
    if any(f in data_fields for f in expected_fields):
        return "data_source", flags

    # 4. Source-only text contains data-source signals
    if _contains_any(source_text, policy.data_source_signals):
        return "data_source", flags

    # 5. expected_fields indicates context/definition material
    context_fields = {"case_definition", "disease", "virus_or_syndrome"}
    if any(f in context_fields for f in expected_fields):
        return "context_source", flags

    # 6. Source-only text contains context signals
    if _contains_any(source_text, policy.context_source_signals):
        return "context_source", flags

    # 7. Fallback: ambiguous / irrelevant
    flags.append("ambiguous_source_role")
    return "irrelevant_source", flags


# ---------------------------------------------------------------------------
# Screening
# ---------------------------------------------------------------------------


_SCREENING_PROFILE: dict[str, tuple[str, float, str]] = {
    "data_source": (
        "include",
        0.90,
        "Source metadata indicates it is likely to contain extractable hantavirus "
        "case, death, date, location, or surveillance data.",
    ),
    "context_source": (
        "include",
        0.78,
        "Source is relevant context or definition material for hantavirus disease, "
        "though it may not contain extractable case counts.",
    ),
    "search_endpoint": (
        "uncertain",
        0.70,
        "Source is a literature search endpoint and should be expanded into "
        "article-level candidates by a later real-search step rather than fetched "
        "directly as a source document.",
    ),
    "placeholder_source": (
        "uncertain",
        0.65,
        "Source is an internal seed placeholder URI and should be deferred until "
        "real connectors (structured database / news) are implemented.",
    ),
    "irrelevant_source": (
        "exclude",
        0.60,
        "Source does not clearly match the hantavirus human case, outbreak, or "
        "surveillance collection scope based on available metadata.",
    ),
}


def _screen_entry(
    entry: dict,
    policy: SourceScreeningPolicy,
    screening_criteria: dict | None,  # noqa: ARG001 — reserved for future LLM step
) -> SourceScreeningResult:
    role, role_flags = _classify_source_role(entry, policy)
    decision, confidence, reason = _SCREENING_PROFILE[role]

    flags = list(role_flags)

    if not (entry.get("canonical_url") or entry.get("url")):
        flags.append("missing_url")
        confidence = min(confidence, 0.50)
    if not entry.get("source_type"):
        flags.append("missing_source_type")
        confidence = min(confidence, 0.50)

    allowed_fields = set(policy.target_data_fields) | set(policy.context_fields)
    expected_extractable = [
        f for f in (entry.get("expected_fields") or []) if f in allowed_fields
    ]

    return SourceScreeningResult(
        source_id=entry.get("source_id", ""),
        screening_decision=decision,
        screening_confidence=confidence,
        screening_reason=reason,
        source_role=role,
        screening_flags=flags,
        expected_extractable_fields=expected_extractable,
    )


# ---------------------------------------------------------------------------
# Critic
# ---------------------------------------------------------------------------


_CRITIC_PROFILE: dict[str, tuple[str, float, str, str | None]] = {
    "data_source": (
        "include",
        0.88,
        "Critic confirms: source has clear data-oriented signals and expected "
        "extractable case/death/date/location fields.",
        None,
    ),
    "context_source": (
        "include",
        0.74,
        "Critic confirms: source is relevant context for hantavirus terminology "
        "or case definition, but is not necessarily a case-count source.",
        "context_only_or_low_case_data_signal",
    ),
    "search_endpoint": (
        "uncertain",
        0.76,
        "Critic flags: search endpoints should not be parsed as final source "
        "documents — they must be expanded into article-level candidates first.",
        "requires_article_level_expansion",
    ),
    "placeholder_source": (
        "uncertain",
        0.72,
        "Critic flags: internal seed placeholder URI; should be deferred until "
        "real connector implementation provides actual sources.",
        "requires_connector_implementation",
    ),
    "irrelevant_source": (
        "exclude",
        0.65,
        "Critic confirms: source metadata does not clearly tie it to human "
        "hantavirus case or outbreak data.",
        None,
    ),
}


def _critic_review_entry(
    entry: dict,
    policy: SourceScreeningPolicy,  # noqa: ARG001 — reserved for future LLM step
) -> SourceCriticResult:
    role = entry.get("source_role") or "irrelevant_source"
    screening_decision = entry.get("screening_decision")

    critic_decision, critic_confidence, critic_reason, critic_flag = _CRITIC_PROFILE[role]

    if role == "data_source":
        agrees = screening_decision == "include"
    elif role == "context_source":
        agrees = screening_decision == "include"
    elif role == "search_endpoint":
        agrees = screening_decision == "uncertain"
    elif role == "placeholder_source":
        agrees = screening_decision == "uncertain"
    else:  # irrelevant_source
        agrees = screening_decision == "exclude"

    flags = [critic_flag] if critic_flag else []

    return SourceCriticResult(
        source_id=entry.get("source_id", ""),
        critic_decision=critic_decision,
        critic_confidence=critic_confidence,
        critic_reason=critic_reason,
        critic_agrees_with_screening=agrees,
        critic_flags=flags,
    )


# ---------------------------------------------------------------------------
# Final routing
# ---------------------------------------------------------------------------


_FINAL_STATUS_MAP: dict[str, str] = {
    "include_for_content_fetch": "ready_for_content_fetch",
    "include_for_context_fetch": "ready_for_context_fetch",
    "defer_to_search_expansion": "deferred_search_expansion",
    "needs_human_review": "needs_human_review",
    "exclude": "excluded",
}


def _final_route_entry(
    entry: dict,
    critic: SourceCriticResult,
    policy: SourceScreeningPolicy,
) -> SourceFinalRoutingDecision:
    role = entry.get("source_role") or "irrelevant_source"
    screening_decision = entry.get("screening_decision")
    screening_confidence = float(entry.get("screening_confidence") or 0.0)
    screening_reason = entry.get("screening_reason") or ""

    avg_confidence = (screening_confidence + critic.critic_confidence) / 2.0
    routing_flags: list[str] = []

    # 1. Role-based tentative decision.
    if role == "data_source" and screening_decision == "include" and critic.critic_decision == "include":
        final_decision = "include_for_content_fetch"
        ready_for_content_fetch = True
        requires_human_review = False
        final_reason = (
            "Source classified as data_source; both screening and critic agree "
            "to include for content fetch."
        )
    elif role == "context_source" and screening_decision == "include" and critic.critic_decision == "include":
        final_decision = "include_for_context_fetch"
        ready_for_content_fetch = True
        requires_human_review = False
        final_reason = (
            "Source classified as context_source; both screening and critic "
            "agree to include for context fetch."
        )
    elif role == "search_endpoint":
        final_decision = "defer_to_search_expansion"
        ready_for_content_fetch = False
        requires_human_review = False
        final_reason = (
            "Search endpoint deferred: must be expanded into article-level "
            "candidates by a later real-search step."
        )
    elif role == "placeholder_source":
        final_decision = "defer_to_search_expansion"
        ready_for_content_fetch = False
        requires_human_review = False
        final_reason = (
            "Internal seed placeholder deferred: awaiting real connector "
            "implementation."
        )
    else:
        # Fallback for irrelevant_source or unrecognized combinations.
        final_decision = "exclude"
        ready_for_content_fetch = False
        requires_human_review = False
        final_reason = screening_reason or "Source excluded by default fallback."

    # 2. Disagreement override.
    if (
        screening_decision is not None
        and critic.critic_decision is not None
        and screening_decision != critic.critic_decision
    ):
        final_decision = "needs_human_review"
        ready_for_content_fetch = False
        requires_human_review = True
        routing_flags.append("screening_and_critic_disagree")
        final_reason = (
            "Screening and critic disagree on this source; routing to human "
            "review for resolution."
        )

    # 3. Low-confidence override.
    low_threshold = float(policy.thresholds.get("low_confidence", 0.50))
    if avg_confidence < low_threshold:
        final_decision = "needs_human_review"
        ready_for_content_fetch = False
        requires_human_review = True
        if "low_screening_confidence" not in routing_flags:
            routing_flags.append("low_screening_confidence")
        final_reason = (
            f"Combined screening+critic confidence ({avg_confidence:.2f}) is "
            f"below the low_confidence threshold ({low_threshold:.2f})."
        )

    # 4. Irrelevant-source final override (after disagree/low-conf checks).
    if role == "irrelevant_source":
        final_decision = "exclude"
        ready_for_content_fetch = False
        requires_human_review = False
        final_reason = (
            "Source role is irrelevant for the hantavirus collection scope; "
            "excluded from downstream content fetching."
        )

    return SourceFinalRoutingDecision(
        source_id=entry.get("source_id", ""),
        final_decision=final_decision,
        final_confidence=round(avg_confidence, 4),
        final_reason=final_reason,
        ready_for_content_fetch=ready_for_content_fetch,
        requires_human_review=requires_human_review,
        routing_flags=routing_flags,
    )


# ---------------------------------------------------------------------------
# Nodes
# ---------------------------------------------------------------------------


def source_screening(state: DataCollectionState) -> dict:
    """Deterministic source screening agent (rule-based, no LLM)."""

    policy = SourceScreeningPolicy(**load_source_screening_policy())
    registry = list(state.get("source_registry") or [])
    screening_criteria = state.get("screening_criteria")
    low_threshold = float(policy.thresholds.get("low_confidence", 0.50))

    updated: list[dict] = []
    decision_counter: Counter = Counter()
    role_counter: Counter = Counter()
    low_confidence_count = 0
    missing_url_count = 0
    missing_source_type_count = 0

    for entry in registry:
        result = _screen_entry(entry, policy, screening_criteria)
        new_entry = dict(entry)
        new_entry.update(
            {
                "screening_decision": result.screening_decision,
                "screening_confidence": result.screening_confidence,
                "screening_reason": result.screening_reason,
                "source_role": result.source_role,
                "screening_flags": list(result.screening_flags),
                "expected_extractable_fields": list(result.expected_extractable_fields),
                "status": "screened",
            }
        )
        # Validate via the model so any future field changes fail loudly here.
        validated = SourceRegistryEntry(**new_entry).model_dump()
        updated.append(validated)

        decision_counter[result.screening_decision] += 1
        role_counter[result.source_role] += 1
        if result.screening_confidence < low_threshold:
            low_confidence_count += 1
        if "missing_url" in result.screening_flags:
            missing_url_count += 1
        if "missing_source_type" in result.screening_flags:
            missing_source_type_count += 1

    summary = {
        "input_registry_count": len(registry),
        "screened_count": len(updated),
        "screening_decision_counts": dict(decision_counter),
        "source_role_counts": dict(role_counter),
        "low_confidence_count": low_confidence_count,
        "missing_url_count": missing_url_count,
        "missing_source_type_count": missing_source_type_count,
    }

    trace = append_trace(
        state,
        node_name="source_screening",
        message=f"Screened {len(updated)} sources using deterministic policy.",
        metadata=summary,
    )
    return {
        "source_registry": updated,
        "source_screening_summary": summary,
        "collection_trace": trace,
    }


def source_critic_and_uncertainty_routing(state: DataCollectionState) -> dict:
    """Deterministic source critic + final routing (rule-based, no LLM)."""

    policy = SourceScreeningPolicy(**load_source_screening_policy())
    registry = list(state.get("source_registry") or [])
    existing_queue = list(state.get("human_review_queue") or [])
    existing_review_ids = {item.get("review_id") for item in existing_queue}

    updated: list[dict] = []
    critic_decision_counter: Counter = Counter()
    final_decision_counter: Counter = Counter()
    critic_flag_counter: Counter = Counter()
    agreement_count = 0
    disagreement_count = 0
    ready_for_content_fetch_count = 0
    requires_human_review_count = 0
    deferred_search_expansion_count = 0
    excluded_count = 0

    new_review_items: list[HumanReviewItem] = []

    for entry in registry:
        critic = _critic_review_entry(entry, policy)
        routing = _final_route_entry(entry, critic, policy)

        new_entry = dict(entry)
        new_entry.update(
            {
                "critic_decision": critic.critic_decision,
                "critic_confidence": critic.critic_confidence,
                "critic_reason": critic.critic_reason,
                "critic_agrees_with_screening": critic.critic_agrees_with_screening,
                "critic_flags": list(critic.critic_flags),
                "final_screening_decision": routing.final_decision,
                "final_screening_confidence": routing.final_confidence,
                "final_screening_reason": routing.final_reason,
                "ready_for_content_fetch": routing.ready_for_content_fetch,
                "requires_human_review": routing.requires_human_review,
                "routing_flags": list(routing.routing_flags),
                "status": _FINAL_STATUS_MAP.get(routing.final_decision, "screened"),
            }
        )
        validated = SourceRegistryEntry(**new_entry).model_dump()
        updated.append(validated)

        critic_decision_counter[critic.critic_decision] += 1
        for flag in critic.critic_flags:
            critic_flag_counter[flag] += 1
        if critic.critic_agrees_with_screening:
            agreement_count += 1
        else:
            disagreement_count += 1

        final_decision_counter[routing.final_decision] += 1
        if routing.ready_for_content_fetch:
            ready_for_content_fetch_count += 1
        if routing.requires_human_review:
            requires_human_review_count += 1
        if routing.final_decision == "defer_to_search_expansion":
            deferred_search_expansion_count += 1
        if routing.final_decision == "exclude":
            excluded_count += 1

        if routing.requires_human_review:
            review_id = f"review_source_{validated.get('source_id', '')}"
            if review_id and review_id not in existing_review_ids:
                new_review_items.append(
                    HumanReviewItem(
                        review_id=review_id,
                        item_type="source_screening",
                        related_ids=[validated.get("source_id", "")],
                        reason=routing.final_reason,
                        status="pending",
                    )
                )
                existing_review_ids.add(review_id)

    human_review_queue = list(existing_queue) + [
        item.model_dump() for item in new_review_items
    ]

    critic_summary = {
        "input_registry_count": len(registry),
        "critic_reviewed_count": len(updated),
        "critic_decision_counts": dict(critic_decision_counter),
        "agreement_count": agreement_count,
        "disagreement_count": disagreement_count,
        "critic_flag_counts": dict(critic_flag_counter),
    }
    routing_summary = {
        "final_decision_counts": dict(final_decision_counter),
        "ready_for_content_fetch_count": ready_for_content_fetch_count,
        "requires_human_review_count": requires_human_review_count,
        "deferred_search_expansion_count": deferred_search_expansion_count,
        "excluded_count": excluded_count,
    }

    trace = append_trace(
        state,
        node_name="source_critic_and_uncertainty_routing",
        message=(
            f"Critic reviewed {len(updated)} sources; "
            f"{ready_for_content_fetch_count} ready for fetch, "
            f"{deferred_search_expansion_count} deferred, "
            f"{requires_human_review_count} flagged for human review."
        ),
        metadata={**critic_summary, **routing_summary},
    )
    return {
        "source_registry": updated,
        "human_review_queue": human_review_queue,
        "source_critic_summary": critic_summary,
        "source_routing_summary": routing_summary,
        "collection_trace": trace,
    }
