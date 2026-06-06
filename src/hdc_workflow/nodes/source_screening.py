"""Source screening, critic review, and source-level routing (Step 4).

Deterministic rule-based implementation. No LLM, no network. Later steps can
replace the rule-based logic with structured-output LLM agents without
changing node names or graph topology.
"""

from __future__ import annotations

import os
from collections import Counter
from urllib.parse import urlsplit

from .. import llm_clients
from ..agents.source_critic_agent import assess_source_with_llm
from ..config import (
    get_collection_mode,
    load_source_role_policy,
    load_source_screening_policy,
)
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


def _parse_csv_env(name: str) -> set[str] | None:
    raw = os.environ.get(name) or ""
    if not raw.strip():
        return None
    values = {part.strip() for part in raw.split(",") if part.strip()}
    return values or None


def _parse_positive_int_env(name: str) -> int | None:
    raw = (os.environ.get(name) or "").strip()
    if not raw:
        return None
    try:
        value = int(raw)
    except (TypeError, ValueError):
        return None
    return value if value > 0 else None


def _llm_source_critic_review_blocks_fetch() -> bool:
    value = (
        os.environ.get("HDC_LLM_SOURCE_CRITIC_REVIEW_BLOCKS_FETCH") or ""
    ).strip().lower()
    return value != "false"


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


def _append_flag(flags: list[str], flag: str) -> list[str]:
    if flag not in flags:
        flags.append(flag)
    return flags


def _apply_llm_source_critic_assessment(
    entry: dict,
    assessment: dict,
) -> dict:
    updated = dict(entry)
    routing_flags = list(updated.get("routing_flags") or [])
    critic_flags = list(updated.get("critic_flags") or [])

    semantic_leakage_risk = bool(assessment.get("semantic_leakage_risk", False))
    needs_human_review = bool(assessment.get("needs_human_review", False))
    context_only_risk = bool(assessment.get("context_only_risk", False))
    validation_candidate_risk = bool(
        assessment.get("validation_candidate_risk", False)
    )

    if semantic_leakage_risk:
        _append_flag(routing_flags, "llm_semantic_leakage_risk")
        _append_flag(critic_flags, "llm_semantic_leakage_risk")
    if context_only_risk:
        _append_flag(routing_flags, "llm_context_only_risk")
        _append_flag(critic_flags, "llm_context_only_risk")
    if validation_candidate_risk:
        _append_flag(routing_flags, "llm_validation_candidate_risk")
        _append_flag(critic_flags, "llm_validation_candidate_risk")
    if needs_human_review:
        _append_flag(routing_flags, "llm_human_review_recommended")
        _append_flag(critic_flags, "llm_human_review_recommended")
        if _llm_source_critic_review_blocks_fetch():
            reason = (
                assessment.get("human_review_reason")
                or "LLM source critic recommended human review."
            )
            updated.update(
                {
                    "final_screening_decision": "needs_human_review",
                    "final_screening_reason": _append_note(
                        updated.get("final_screening_reason"), str(reason)
                    ),
                    "ready_for_content_fetch": False,
                    "requires_human_review": True,
                    "status": "needs_human_review",
                }
            )

    updated.update(
        {
            "llm_source_critic_enabled": True,
            "llm_source_critic_failed": False,
            "llm_source_critic_error": None,
            "llm_proposed_source_role": assessment.get("proposed_source_role"),
            "llm_proposed_screening_decision": assessment.get(
                "proposed_screening_decision"
            ),
            "llm_credibility_level": assessment.get("credibility_level"),
            "llm_credibility_reason": assessment.get("credibility_reason"),
            "llm_expected_extractable_fields": list(
                assessment.get("expected_extractable_fields") or []
            ),
            "llm_semantic_leakage_risk": semantic_leakage_risk,
            "llm_semantic_leakage_reason": assessment.get(
                "semantic_leakage_reason"
            ),
            "llm_context_only_risk": context_only_risk,
            "llm_validation_candidate_risk": validation_candidate_risk,
            "llm_needs_human_review": needs_human_review,
            "llm_human_review_reason": assessment.get("human_review_reason"),
            "llm_source_critic_confidence": assessment.get("confidence"),
            "llm_reasoning_summary": assessment.get("reasoning_summary"),
            "routing_flags": routing_flags,
            "critic_flags": critic_flags,
        }
    )
    return updated


def _apply_llm_source_critic_failure(entry: dict, exc: Exception) -> dict:
    updated = dict(entry)
    flags = list(updated.get("routing_flags") or [])
    _append_flag(flags, "llm_source_critic_failed")
    updated.update(
        {
            "llm_source_critic_enabled": True,
            "llm_source_critic_failed": True,
            "llm_source_critic_error": f"{type(exc).__name__}: {exc}",
            "routing_flags": flags,
        }
    )
    return updated


# ---------------------------------------------------------------------------
# Final routing
# ---------------------------------------------------------------------------


_FINAL_STATUS_MAP: dict[str, str] = {
    "include_for_content_fetch": "ready_for_content_fetch",
    "include_for_context_fetch": "ready_for_context_fetch",
    "defer_to_search_expansion": "deferred_search_expansion",
    "needs_human_review": "needs_human_review",
    "exclude": "excluded",
    "reserved_for_validation": "reserved_for_validation",
}

_VALIDATION_RESERVED_REASON = (
    "Held out for masked validation ground-truth comparison."
)
_CONTEXT_ONLY_REASON = (
    "Configured as context-only by source-role policy; fetch for context "
    "grounding only, not structured record extraction."
)


def _domain_for_entry(entry: dict) -> str:
    url = entry.get("canonical_url") or entry.get("url") or ""
    if not url:
        return ""
    netloc = urlsplit(url).netloc.lower()
    if netloc.startswith("www."):
        netloc = netloc[4:]
    return netloc


def _domain_matches_reserved(domain: str, reserved_domains: list[str]) -> bool:
    if not domain:
        return False
    for reserved in reserved_domains:
        normalized = str(reserved or "").strip().lower()
        if not normalized:
            continue
        if domain == normalized or domain.endswith("." + normalized):
            return True
    return False


def _is_validation_reserved_source(
    entry: dict,
    role_policy: dict,
    collection_mode: str,
) -> bool:
    if collection_mode != "masked_validation":
        return False
    reserved_ids = set(role_policy.get("validation_reserved_source_ids") or [])
    source_id = entry.get("source_id")
    if source_id in reserved_ids:
        return True
    if not role_policy.get("domain_masking_enabled", False):
        return False
    reserved_domains = list(role_policy.get("validation_reserved_domains") or [])
    return _domain_matches_reserved(_domain_for_entry(entry), reserved_domains)


def _is_context_only_source(entry: dict, role_policy: dict) -> bool:
    context_only_ids = set(role_policy.get("context_only_source_ids") or [])
    return entry.get("source_id") in context_only_ids


def _append_note(existing: str | None, note: str) -> str:
    if not existing:
        return note
    if note in existing:
        return existing
    return f"{existing} {note}"


def _entry_text_for_credibility(entry: dict) -> str:
    parts = [
        str(entry.get("publisher") or ""),
        str(entry.get("source_type") or ""),
        str(entry.get("title") or ""),
        str(entry.get("canonical_url") or entry.get("url") or ""),
    ]
    return " ".join(parts).lower()


def _publisher_authority_score(entry: dict) -> tuple[float, list[str]]:
    text = _entry_text_for_credibility(entry)
    if any(
        term in text
        for term in (
            "department of health",
            "cdc",
            "who",
            "ecdc",
            "paho",
            "ministry of health",
            ".gov",
            "nmhealth.org",
        )
    ):
        return 1.0, ["official_or_public_health_authority"]
    if any(term in text for term in ("pubmed", "europe pmc", "openalex", "academic")):
        return 0.82, ["academic_or_literature_source"]
    if any(term in text for term in ("news", "media", "press")):
        return 0.62, ["news_or_media_source"]
    return 0.55, ["authority_unclear"]


def _granularity_score(entry: dict) -> tuple[float, list[str]]:
    fields = set(
        entry.get("expected_extractable_fields")
        or entry.get("expected_fields")
        or []
    )
    role = entry.get("source_role")
    target_fields = {"cases", "deaths", "date", "location"}
    if role == "validation_reserved":
        return 0.92, ["validation_ground_truth_candidate"]
    if target_fields <= fields:
        return 1.0, ["case_death_date_location_expected"]
    if target_fields & fields:
        return 0.78, ["partial_target_fields_expected"]
    if role == "context_source":
        return 0.55, ["context_only_granularity"]
    if role in {"search_endpoint", "placeholder_source"}:
        return 0.40, ["not_directly_extractable"]
    return 0.45, ["granularity_unclear"]


def _timeliness_score(entry: dict) -> tuple[float, list[str]]:
    published = str(entry.get("published_date") or "").strip()
    if not published:
        return 0.62, ["published_date_missing"]
    if any(
        year in published
        for year in ("2026", "2025", "2024", "2023", "2022", "2021", "2020")
    ):
        return 0.90, ["published_date_in_requested_window_or_recent"]
    return 0.72, ["published_date_available"]


def _provenance_score(entry: dict) -> tuple[float, list[str]]:
    flags: list[str] = []
    url = entry.get("canonical_url") or entry.get("url")
    publisher = entry.get("publisher")
    title = entry.get("title")
    score = 1.0
    if not url:
        score -= 0.35
        flags.append("missing_url")
    elif str(url).startswith("seed://"):
        score -= 0.30
        flags.append("placeholder_uri")
    if not publisher:
        score -= 0.20
        flags.append("missing_publisher")
    if not title:
        score -= 0.10
        flags.append("missing_title")
    if not flags:
        flags.append("complete_source_metadata")
    return max(0.0, round(score, 4)), flags


def _independence_score(entry: dict) -> tuple[float, list[str]]:
    if entry.get("source_role") == "validation_reserved":
        return 0.90, ["held_out_validation_source"]
    if entry.get("publisher"):
        return 0.75, ["named_publisher"]
    return 0.50, ["independence_unclear"]


def _risk_score(entry: dict) -> tuple[float, list[str]]:
    flags = set(entry.get("routing_flags") or []) | set(
        entry.get("critic_flags") or []
    )
    risk_flags = {
        "llm_semantic_leakage_risk",
        "llm_context_only_risk",
        "llm_validation_candidate_risk",
        "screening_and_critic_disagree",
        "low_screening_confidence",
    }
    matched = sorted(flags & risk_flags)
    if not matched:
        return 0.95, ["low_source_use_risk"]
    if (
        "screening_and_critic_disagree" in matched
        or "low_screening_confidence" in matched
    ):
        return 0.35, matched
    return 0.60, matched


def _credibility_level(score: float) -> str:
    if score >= 0.80:
        return "high"
    if score >= 0.60:
        return "medium"
    return "low"


def _apply_source_credibility_rubric(entry: dict) -> dict:
    """Attach an auditable source credibility rubric to a registry entry."""

    component_specs = {
        "authority": _publisher_authority_score(entry),
        "granularity": _granularity_score(entry),
        "provenance": _provenance_score(entry),
        "timeliness": _timeliness_score(entry),
        "independence": _independence_score(entry),
        "risk": _risk_score(entry),
    }
    components = {
        name: round(float(score), 4)
        for name, (score, _flags) in component_specs.items()
    }
    flags: list[str] = []
    for _name, (_score, component_flags) in component_specs.items():
        for flag in component_flags:
            if flag not in flags:
                flags.append(flag)

    score = round(sum(components.values()) / len(components), 4)
    level = _credibility_level(score)
    updated = dict(entry)
    updated.update(
        {
            "credibility_score": score,
            "credibility_level": level,
            "credibility_rubric_version": "source_credibility_v1",
            "credibility_score_components": components,
            "credibility_flags": flags,
            "credibility_reason": (
                f"{level} credibility by source_credibility_v1 "
                f"(score={score:.2f}; authority={components['authority']:.2f}; "
                f"granularity={components['granularity']:.2f}; "
                f"provenance={components['provenance']:.2f})."
            ),
        }
    )
    return updated


def _apply_validation_reserved_override(
    entry: dict,
    role_policy: dict,
) -> dict:
    behavior = role_policy.get("collection_blocking_behavior") or {}
    flags = list(entry.get("routing_flags") or [])
    for flag in behavior.get("routing_flags") or [
        "validation_reserved",
        "blocked_from_collection",
    ]:
        if flag not in flags:
            flags.append(flag)

    final_decision = behavior.get(
        "final_screening_decision", "reserved_for_validation"
    )
    status = behavior.get("status", "reserved_for_validation")
    updated = dict(entry)
    updated.update(
        {
            "source_role": "validation_reserved",
            "final_screening_decision": final_decision,
            "final_screening_confidence": entry.get("final_screening_confidence"),
            "final_screening_reason": _VALIDATION_RESERVED_REASON,
            "ready_for_content_fetch": bool(
                behavior.get("set_ready_for_content_fetch", False)
            ),
            "requires_human_review": False,
            "routing_flags": flags,
            "status": status,
            "notes": _append_note(entry.get("notes"), _VALIDATION_RESERVED_REASON),
        }
    )
    return updated


def _apply_context_only_override(entry: dict) -> dict:
    flags = list(entry.get("routing_flags") or [])
    for flag in ("context_only", "blocked_from_structured_extraction"):
        if flag not in flags:
            flags.append(flag)

    updated = dict(entry)
    updated.update(
        {
            "source_role": "context_source",
            "final_screening_decision": "include_for_context_fetch",
            "final_screening_reason": _CONTEXT_ONLY_REASON,
            "ready_for_content_fetch": True,
            "requires_human_review": False,
            "routing_flags": flags,
            "status": "ready_for_context_fetch",
            "notes": _append_note(entry.get("notes"), _CONTEXT_ONLY_REASON),
        }
    )
    return updated


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
    role_policy = load_source_role_policy()
    collection_mode = get_collection_mode(role_policy)
    registry = list(state.get("source_registry") or [])
    existing_queue = list(state.get("human_review_queue") or [])
    existing_review_ids = {item.get("review_id") for item in existing_queue}
    llm_source_critic_enabled = llm_clients.llm_source_critic_enabled()
    llm_source_critic_allowlist = _parse_csv_env(
        "HDC_LLM_SOURCE_CRITIC_SOURCE_ID_ALLOWLIST"
    )
    llm_source_critic_max_sources = _parse_positive_int_env(
        "HDC_LLM_SOURCE_CRITIC_MAX_SOURCES"
    )
    llm_review_blocks_fetch = _llm_source_critic_review_blocks_fetch()

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
    validation_reserved_source_ids: list[str] = []
    context_only_source_ids: list[str] = []
    llm_attempted_source_count = 0
    llm_assessed_source_count = 0
    llm_skipped_source_count = 0
    llm_skipped_source_ids: list[str] = []
    llm_source_critic_failure_count = 0
    llm_semantic_leakage_count = 0
    llm_human_review_recommended_count = 0
    credibility_level_counter: Counter = Counter()
    low_credibility_source_count = 0

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
        if llm_source_critic_enabled:
            source_id = new_entry.get("source_id") or ""
            should_skip_llm = False
            if (
                llm_source_critic_allowlist is not None
                and source_id not in llm_source_critic_allowlist
            ):
                should_skip_llm = True
            if (
                not should_skip_llm
                and llm_source_critic_max_sources is not None
                and llm_attempted_source_count >= llm_source_critic_max_sources
            ):
                should_skip_llm = True

            if should_skip_llm:
                llm_skipped_source_count += 1
                if source_id:
                    llm_skipped_source_ids.append(source_id)
            else:
                llm_attempted_source_count += 1
                try:
                    assessment = assess_source_with_llm(
                        source_entry=new_entry,
                        collection_spec=state.get("collection_spec"),
                        screening_policy=policy.model_dump(),
                        source_role_policy=role_policy,
                    )
                    llm_assessed_source_count += 1
                    if assessment.get("semantic_leakage_risk"):
                        llm_semantic_leakage_count += 1
                    if assessment.get("needs_human_review"):
                        llm_human_review_recommended_count += 1
                    new_entry = _apply_llm_source_critic_assessment(
                        new_entry, assessment
                    )
                except Exception as exc:  # noqa: BLE001 - advisory fallback
                    llm_source_critic_failure_count += 1
                    new_entry = _apply_llm_source_critic_failure(new_entry, exc)

        if _is_validation_reserved_source(new_entry, role_policy, collection_mode):
            new_entry = _apply_validation_reserved_override(new_entry, role_policy)
            validation_reserved_source_ids.append(new_entry.get("source_id", ""))
        elif _is_context_only_source(new_entry, role_policy):
            new_entry = _apply_context_only_override(new_entry)
            context_only_source_ids.append(new_entry.get("source_id", ""))

        new_entry = _apply_source_credibility_rubric(new_entry)
        validated = SourceRegistryEntry(**new_entry).model_dump()
        updated.append(validated)

        critic_decision_counter[critic.critic_decision] += 1
        for flag in critic.critic_flags:
            critic_flag_counter[flag] += 1
        if critic.critic_agrees_with_screening:
            agreement_count += 1
        else:
            disagreement_count += 1

        final_decision = validated.get("final_screening_decision") or routing.final_decision
        final_decision_counter[final_decision] += 1
        if validated.get("ready_for_content_fetch"):
            ready_for_content_fetch_count += 1
        if validated.get("requires_human_review"):
            requires_human_review_count += 1
        if final_decision == "defer_to_search_expansion":
            deferred_search_expansion_count += 1
        if final_decision == "exclude":
            excluded_count += 1
        credibility_level = validated.get("credibility_level") or "unknown"
        credibility_level_counter[credibility_level] += 1
        if credibility_level == "low":
            low_credibility_source_count += 1

        if validated.get("requires_human_review"):
            review_id = f"review_source_{validated.get('source_id', '')}"
            if review_id and review_id not in existing_review_ids:
                new_review_items.append(
                    HumanReviewItem(
                        review_id=review_id,
                        item_type="source_screening",
                        related_ids=[validated.get("source_id", "")],
                        reason=validated.get("final_screening_reason")
                        or routing.final_reason,
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
        "collection_mode": collection_mode,
        "llm_source_critic_enabled": llm_source_critic_enabled,
        "llm_source_critic_attempted_source_count": llm_attempted_source_count,
        "llm_assessed_source_count": llm_assessed_source_count,
        "llm_skipped_source_count": llm_skipped_source_count,
        "llm_skipped_source_ids": llm_skipped_source_ids,
        "llm_source_critic_allowlist_enabled": (
            llm_source_critic_allowlist is not None
        ),
        "llm_source_critic_allowlist": (
            sorted(llm_source_critic_allowlist)
            if llm_source_critic_allowlist is not None
            else []
        ),
        "llm_source_critic_max_sources": llm_source_critic_max_sources,
        "llm_source_critic_review_blocks_fetch": llm_review_blocks_fetch,
        "llm_source_critic_failure_count": llm_source_critic_failure_count,
        "llm_semantic_leakage_count": llm_semantic_leakage_count,
        "llm_human_review_recommended_count": llm_human_review_recommended_count,
        "credibility_rubric_version": "source_credibility_v1",
        "credibility_level_counts": dict(credibility_level_counter),
        "low_credibility_source_count": low_credibility_source_count,
    }
    routing_summary = {
        "collection_mode": collection_mode,
        "final_decision_counts": dict(final_decision_counter),
        "ready_for_content_fetch_count": ready_for_content_fetch_count,
        "requires_human_review_count": requires_human_review_count,
        "deferred_search_expansion_count": deferred_search_expansion_count,
        "excluded_count": excluded_count,
        "validation_reserved_source_count": len(validation_reserved_source_ids),
        "validation_reserved_source_ids": list(validation_reserved_source_ids),
        "context_only_source_count": len(context_only_source_ids),
        "context_only_source_ids": list(context_only_source_ids),
        "llm_source_critic_enabled": llm_source_critic_enabled,
        "llm_source_critic_attempted_source_count": llm_attempted_source_count,
        "llm_assessed_source_count": llm_assessed_source_count,
        "llm_skipped_source_count": llm_skipped_source_count,
        "llm_source_critic_review_blocks_fetch": llm_review_blocks_fetch,
        "llm_semantic_leakage_count": llm_semantic_leakage_count,
        "llm_human_review_recommended_count": llm_human_review_recommended_count,
        "credibility_rubric_version": "source_credibility_v1",
        "credibility_level_counts": dict(credibility_level_counter),
        "low_credibility_source_count": low_credibility_source_count,
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
