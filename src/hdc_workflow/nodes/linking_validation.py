"""Record linking, cross-source consistency, and quality-gate routing.

Step 9 makes `record_linking` functional. `cross_source_consistency_check`
remains a placeholder that preserves any existing conflicts list. The
quality-gate router still ends Step 1's default route to "finalize".
"""

from __future__ import annotations

import re
from collections import Counter

from ..config import load_cross_source_consistency_policy, load_record_linking_policy
from ..models import (
    Conflict,
    CrossSourceConsistencyPolicy,
    FieldComparisonResult,
    HumanReviewItem,
    LinkedEvent,
    RecordLinkingPolicy,
    RecordLinkingResult,
)
from ..state import DataCollectionState, append_trace

_NUMERIC_FIELDS = (
    "cases_confirmed",
    "cases_probable",
    "cases_suspected",
    "cases_unspecified",
    "deaths",
)


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------


def _blank_to_none(value):
    if value is None:
        return None
    if isinstance(value, str):
        s = value.strip()
        return s if s else None
    return value


def _has_case_or_death_data(record: dict) -> bool:
    return any(record.get(f) is not None for f in _NUMERIC_FIELDS)


_MONTH_TO_NUM = {
    "january": "01",
    "february": "02",
    "march": "03",
    "april": "04",
    "may": "05",
    "june": "06",
    "july": "07",
    "august": "08",
    "september": "09",
    "october": "10",
    "november": "11",
    "december": "12",
    "jan": "01",
    "feb": "02",
    "mar": "03",
    "apr": "04",
    "jun": "06",
    "jul": "07",
    "aug": "08",
    "sep": "09",
    "sept": "09",
    "oct": "10",
    "nov": "11",
    "dec": "12",
}

_RE_ANCHOR_ISO_YMD = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_RE_ANCHOR_ISO_YM = re.compile(r"^\d{4}-\d{2}$")
_RE_ANCHOR_YEAR = re.compile(r"^\d{4}$")
_RE_ANCHOR_MONTH_YEAR = re.compile(r"^([A-Za-z]+)\s+(\d{4})$")

# Cutoff-style prefixes commonly emitted by LLMs inside `reporting_period`
# (e.g. "as of December 2020") — strip them so we can extract a clean anchor.
_DATE_ANCHOR_PREFIXES = (
    "reported through",
    "as of",
    "through",
    "as at",
    "up to",
)

# Step 16.1 backward-compat: previously-deployed policy files may not list
# as_of_date / reporting_period in date_anchor_preference. Treat them as
# implicit fallbacks so linking works even with older policy snapshots.
_FALLBACK_DATE_ANCHOR_FIELDS = ("as_of_date", "reporting_period")

_AGGREGATE_GEOGRAPHIC_SCOPE_TYPES = {"region", "multi_country", "global"}

# Step 16.1.1: lightweight alias map sufficient for linking-side decisions.
# Kept in sync with the canonical maps in extraction.py / normalization.py.
_GEOGRAPHIC_SCOPE_TYPE_LINKING_ALIASES: dict[str, str] = {
    "country": "country",
    "national": "country",
    "nation": "country",
    "single country": "country",
    "single_country": "country",
    "subnational": "subnational",
    "sub-national": "subnational",
    "sub national": "subnational",
    "sub_national": "subnational",
    "state": "subnational",
    "province": "subnational",
    "region": "region",
    "regional": "region",
    "multi_country": "multi_country",
    "multi-country": "multi_country",
    "multi country": "multi_country",
    "multicountry": "multi_country",
    "multinational": "multi_country",
    "multi-national": "multi_country",
    "multi national": "multi_country",
    "global": "global",
    "worldwide": "global",
    "world wide": "global",
    "world-wide": "global",
    "unknown": "unknown",
}

_STATISTICAL_COUNT_TYPE_LINKING_ALIASES: dict[str, str] = {
    "cumulative": "cumulative",
    "total": "cumulative",
    "cumulative total": "cumulative",
    "cumulative_total": "cumulative",
    "annual": "annual",
    "yearly": "annual",
    "newly_reported": "newly_reported",
    "newly reported": "newly_reported",
    "newly-reported": "newly_reported",
    "new cases": "newly_reported",
    "additional cases": "newly_reported",
    "historical_total": "historical_total",
    "historical total": "historical_total",
    "historic total": "historical_total",
    "reported through": "historical_total",
    "subset": "subset",
    "subgroup": "subset",
    "of which": "subset",
    "unknown": "unknown",
}


def _canonicalize_geographic_scope_type_for_linking(value):
    if value is None:
        return None
    if not isinstance(value, str):
        return value
    stripped = value.strip()
    if not stripped:
        return None
    key = re.sub(r"\s+", " ", stripped.lower())
    return _GEOGRAPHIC_SCOPE_TYPE_LINKING_ALIASES.get(key, stripped)


def _canonicalize_statistical_count_type_for_linking(value):
    if value is None:
        return None
    if not isinstance(value, str):
        return value
    stripped = value.strip()
    if not stripped:
        return None
    key = re.sub(r"\s+", " ", stripped.lower())
    return _STATISTICAL_COUNT_TYPE_LINKING_ALIASES.get(key, stripped)


def _normalize_date_anchor_value(value):
    """Best-effort canonicalization of a value selected as the date anchor.

    Handles ISO formats and common natural-language forms emitted by LLMs in
    `reporting_period` / `as_of_date` such as ``"December 2020"``,
    ``"through December 2020"``, and ``"as of December 2020"``.
    """

    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None

    lowered = s.lower()
    for prefix in _DATE_ANCHOR_PREFIXES:
        if lowered.startswith(prefix):
            s = s[len(prefix) :].strip()
            lowered = s.lower()
            break
    if not s:
        return None

    if _RE_ANCHOR_ISO_YMD.fullmatch(s):
        return s
    if _RE_ANCHOR_ISO_YM.fullmatch(s):
        return s
    if _RE_ANCHOR_YEAR.fullmatch(s):
        return s

    m = _RE_ANCHOR_MONTH_YEAR.fullmatch(s)
    if m:
        month = _MONTH_TO_NUM.get(m.group(1).lower())
        if month:
            return f"{m.group(2)}-{month}"

    return s


def _date_anchor(
    record: dict,
    policy: RecordLinkingPolicy,
) -> tuple[str | None, str | None, list[str]]:
    fields = list(policy.date_anchor_preference)
    for fallback in _FALLBACK_DATE_ANCHOR_FIELDS:
        if fallback not in fields:
            fields.append(fallback)
    for field in fields:
        value = _blank_to_none(record.get(field))
        if value:
            normalized = _normalize_date_anchor_value(value)
            if normalized:
                return str(normalized), field, [f"selected_date_anchor:{field}"]
    return None, None, []


def _normalized_key_part(value, missing_token: str) -> str:
    if value is None:
        return missing_token
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return missing_token
        return re.sub(r"\s+", " ", s).lower()
    return str(value).lower()


def _unique_non_empty(values: list) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for v in values:
        if v is None:
            continue
        s = str(v).strip()
        if not s or s in seen:
            continue
        seen.add(s)
        result.append(s)
    return result


# ---------------------------------------------------------------------------
# Event-key construction
# ---------------------------------------------------------------------------


def _build_event_key(
    record: dict,
    policy: RecordLinkingPolicy,
) -> tuple[str, dict, list[str], list[str], str | None, str | None]:
    actions: list[str] = []
    warnings: list[str] = []

    disease = _blank_to_none(record.get("disease"))
    virus = _blank_to_none(record.get("virus_or_syndrome"))
    country = _blank_to_none(record.get("country"))
    subnational = _blank_to_none(record.get("subnational_location"))
    date_anchor, date_anchor_field, date_actions = _date_anchor(record, policy)
    actions.extend(date_actions)

    # Step 16 semantic fields. Step 16.1.1 canonicalizes the enum-like ones
    # before they enter the event key so hyphen / underscore / free-text
    # variants from the LLM do not split otherwise-identical events.
    statistical_count_type = _canonicalize_statistical_count_type_for_linking(
        _blank_to_none(record.get("statistical_count_type"))
    )
    reporting_period = _blank_to_none(record.get("reporting_period"))
    geographic_scope = _blank_to_none(record.get("geographic_scope"))
    geographic_scope_type = _canonicalize_geographic_scope_type_for_linking(
        _blank_to_none(record.get("geographic_scope_type"))
    )

    if virus is None:
        actions.append("used_unspecified_virus_or_syndrome_token")
    if subnational is None:
        actions.append("used_unspecified_subnational_location_token")
    if country is None or date_anchor is None:
        actions.append("used_missing_value_token")

    components = {
        "disease": _normalized_key_part(disease, policy.missing_value_token),
        "virus_or_syndrome": _normalized_key_part(virus, policy.unspecified_virus_token),
        "country": _normalized_key_part(country, policy.missing_value_token),
        "subnational_location": _normalized_key_part(
            subnational, policy.unspecified_subnational_token
        ),
        "date_anchor": _normalized_key_part(date_anchor, policy.missing_value_token),
        "statistical_count_type": _normalized_key_part(
            statistical_count_type, policy.missing_value_token
        ),
        "reporting_period": _normalized_key_part(
            reporting_period, policy.missing_value_token
        ),
        "geographic_scope": _normalized_key_part(
            geographic_scope, policy.missing_value_token
        ),
        "geographic_scope_type": _normalized_key_part(
            geographic_scope_type, policy.missing_value_token
        ),
    }
    event_key = (
        f"disease={components['disease']}|"
        f"virus_or_syndrome={components['virus_or_syndrome']}|"
        f"country={components['country']}|"
        f"subnational_location={components['subnational_location']}|"
        f"date_anchor={components['date_anchor']}|"
        f"statistical_count_type={components['statistical_count_type']}|"
        f"reporting_period={components['reporting_period']}|"
        f"geographic_scope={components['geographic_scope']}|"
        f"geographic_scope_type={components['geographic_scope_type']}"
    )

    if country is None and _has_case_or_death_data(record):
        if (
            geographic_scope
            and geographic_scope_type in _AGGREGATE_GEOGRAPHIC_SCOPE_TYPES
        ):
            warnings.append("regional_or_aggregate_geographic_scope")
        else:
            warnings.append("missing_country_for_case_data")
    if date_anchor is None:
        warnings.append("missing_date_anchor")
    if "non_country_geography_used_as_country" in (
        record.get("normalization_warnings") or []
    ):
        warnings.append("non_country_geography")
    if record.get("requires_human_review"):
        warnings.append("existing_record_requires_human_review")

    return event_key, components, actions, warnings, date_anchor, date_anchor_field


def _is_linkable_record(
    record: dict,
    key_components: dict,  # noqa: ARG001 — reserved for future LLM linker
    policy: RecordLinkingPolicy,
) -> tuple[bool, list[str]]:
    if not _blank_to_none(record.get("disease")):
        return False, ["missing_disease"]
    country = _blank_to_none(record.get("country"))
    subnational = _blank_to_none(record.get("subnational_location"))
    date_anchor, _, _ = _date_anchor(record, policy)
    # Step 16.1.1: any non-empty geographic_scope (including canonical
    # aggregate scopes such as EU/EEA or Europe) counts as valid geography
    # for linking, so regional records still produce a linkable event.
    geographic_scope = _blank_to_none(record.get("geographic_scope"))
    if (
        country is None
        and subnational is None
        and date_anchor is None
        and geographic_scope is None
    ):
        return False, ["insufficient_event_key"]
    return True, []


# ---------------------------------------------------------------------------
# LinkedEvent assembly
# ---------------------------------------------------------------------------


def _status_for_event(
    records: list[dict],
    warnings: list[str],
    policy: RecordLinkingPolicy,
) -> tuple[str, bool]:
    review_triggers = set(policy.review_triggers or [])
    if "insufficient_event_key" in warnings:
        return "not_linkable", True
    if any(w in review_triggers for w in warnings):
        return "needs_review", True
    if len(records) == 1:
        return "single_record_event", False
    source_ids = {r.get("source_id") for r in records if _blank_to_none(r.get("source_id"))}
    source_urls = {r.get("source_url") for r in records if _blank_to_none(r.get("source_url"))}
    if len(source_ids) > 1 or len(source_urls) > 1:
        return "linked_multi_source_event", False
    return "linked_multi_record_event", False


def _event_id_for_index(index: int) -> str:
    return f"event_{index:03d}"


def _make_linked_event(
    event_id: str,
    event_key: str,
    records: list[dict],
    key_components: dict,
    policy: RecordLinkingPolicy,
    warnings: list[str],
) -> LinkedEvent:
    sorted_records = sorted(records, key=lambda r: r.get("record_id") or "")
    record_ids = [r.get("record_id") for r in sorted_records if r.get("record_id")]

    source_ids = _unique_non_empty([r.get("source_id") for r in sorted_records])
    source_urls = _unique_non_empty([r.get("source_url") for r in sorted_records])
    source_types = _unique_non_empty([r.get("source_type") for r in sorted_records])
    publishers = _unique_non_empty([r.get("publisher") for r in sorted_records])

    status, requires_review = _status_for_event(sorted_records, warnings, policy)

    basis: list[str] = ["same_disease"]
    if key_components["virus_or_syndrome"] != policy.unspecified_virus_token:
        basis.append("same_virus_or_syndrome")
    if key_components["country"] != policy.missing_value_token:
        basis.append("same_country")
    if key_components["subnational_location"] != policy.unspecified_subnational_token:
        basis.append("same_subnational_location")
    if key_components["date_anchor"] != policy.missing_value_token:
        basis.append("same_date_anchor")
    if key_components.get("statistical_count_type", policy.missing_value_token) != policy.missing_value_token:
        basis.append("same_statistical_count_type")
    if key_components.get("reporting_period", policy.missing_value_token) != policy.missing_value_token:
        basis.append("same_reporting_period")
    if key_components.get("geographic_scope", policy.missing_value_token) != policy.missing_value_token:
        basis.append("same_geographic_scope")

    country_present = key_components["country"] != policy.missing_value_token
    date_present = key_components["date_anchor"] != policy.missing_value_token
    if status in {"needs_review", "not_linkable"}:
        confidence = 0.60
    elif len(sorted_records) > 1 and country_present and date_present:
        confidence = 0.95
    elif len(sorted_records) > 1:
        confidence = 0.85
    else:
        confidence = 0.75

    representative = record_ids[0] if record_ids else None
    first = sorted_records[0] if sorted_records else {}

    return LinkedEvent(
        linked_event_id=event_id,
        record_ids=record_ids,
        linking_basis=basis,
        linking_confidence=confidence,
        event_key=event_key,
        disease=first.get("disease"),
        virus_or_syndrome=first.get("virus_or_syndrome"),
        country=first.get("country"),
        subnational_location=first.get("subnational_location"),
        date_anchor=first.get("date_anchor"),
        date_anchor_field=first.get("date_anchor_field"),
        record_count=len(sorted_records),
        source_ids=source_ids,
        source_urls=source_urls,
        source_types=source_types,
        publishers=publishers,
        representative_record_id=representative,
        linking_status=status,
        linking_method=policy.linking_method,
        linking_warnings=list(warnings),
        requires_human_review=requires_review,
    )


# ---------------------------------------------------------------------------
# Node
# ---------------------------------------------------------------------------


def record_linking(state: DataCollectionState) -> dict:
    """Group normalized records into candidate LinkedEvent objects."""

    policy = RecordLinkingPolicy(**load_record_linking_policy())
    normalized_records = list(state.get("normalized_records") or [])
    existing_queue = list(state.get("human_review_queue") or [])
    existing_review_ids = {item.get("review_id") for item in existing_queue}

    action_counter: Counter = Counter()
    warning_counter: Counter = Counter()
    status_counter: Counter = Counter()

    # Per-record processing first.
    groups: dict[str, list[dict]] = {}
    group_components: dict[str, dict] = {}
    group_warnings: dict[str, list[str]] = {}
    not_linkable: list[tuple[str, dict, list[str], dict]] = []
    updated_records: list[dict] = []

    for original in normalized_records:
        record = dict(original)
        norm_status = record.get("normalization_status")
        if (
            norm_status is not None
            and norm_status not in policy.allowed_input_normalization_statuses
        ):
            # Pass through without linking metadata; no event assignment.
            updated_records.append(record)
            continue

        record_warnings: list[str] = []
        if norm_status is None:
            record_warnings.append("missing_normalization_status")

        (
            event_key,
            components,
            actions,
            key_warnings,
            date_anchor,
            date_anchor_field,
        ) = _build_event_key(record, policy)

        warnings = record_warnings + key_warnings
        linkable, lnk_warnings = _is_linkable_record(record, components, policy)
        warnings.extend(lnk_warnings)

        record["event_key"] = event_key
        record["date_anchor"] = date_anchor
        record["date_anchor_field"] = date_anchor_field
        record["record_linking_actions"] = list(actions)
        record["record_linking_warnings"] = list(warnings)

        for a in actions:
            action_counter[a] += 1
        for w in warnings:
            warning_counter[w] += 1

        if linkable:
            groups.setdefault(event_key, []).append(record)
            group_components[event_key] = components
            existing_group_warnings = group_warnings.setdefault(event_key, [])
            for w in warnings:
                if w not in existing_group_warnings:
                    existing_group_warnings.append(w)
        else:
            not_linkable.append((event_key, components, warnings, record))

        updated_records.append(record)

    # Assemble linked events.
    linked_events: list[LinkedEvent] = []
    new_review_items: list[HumanReviewItem] = []
    event_index = 0

    for event_key in sorted(groups.keys()):
        event_index += 1
        event_id = _event_id_for_index(event_index)
        records_in_group = groups[event_key]
        components = group_components[event_key]
        warnings = group_warnings[event_key]

        linked_event = _make_linked_event(
            event_id, event_key, records_in_group, components, policy, warnings
        )
        linked_events.append(linked_event)
        status_counter[linked_event.linking_status] += 1

        for r in records_in_group:
            r["linked_event_id"] = event_id
            r["record_linking_status"] = linked_event.linking_status

        if linked_event.requires_human_review:
            review_id = f"review_linking_{event_id}"
            if review_id not in existing_review_ids:
                reason = (
                    "Linked event requires review: " + ", ".join(warnings)
                ) if warnings else "Linked event requires review."
                new_review_items.append(
                    HumanReviewItem(
                        review_id=review_id,
                        item_type="record_linking",
                        related_ids=list(linked_event.record_ids),
                        reason=reason,
                        status="pending",
                    )
                )
                existing_review_ids.add(review_id)

    # Singleton not-linkable groups follow, deterministic ordering by record_id.
    for event_key, components, warnings, record in sorted(
        not_linkable, key=lambda t: t[3].get("record_id") or ""
    ):
        event_index += 1
        event_id = _event_id_for_index(event_index)
        linked_event = _make_linked_event(
            event_id, event_key, [record], components, policy, warnings
        )
        linked_events.append(linked_event)
        status_counter[linked_event.linking_status] += 1
        record["linked_event_id"] = event_id
        record["record_linking_status"] = linked_event.linking_status

        if linked_event.requires_human_review:
            review_id = f"review_linking_{event_id}"
            if review_id not in existing_review_ids:
                reason = (
                    "Linked event requires review: " + ", ".join(warnings)
                ) if warnings else "Linked event requires review."
                new_review_items.append(
                    HumanReviewItem(
                        review_id=review_id,
                        item_type="record_linking",
                        related_ids=[record.get("record_id")] if record.get("record_id") else [],
                        reason=reason,
                        status="pending",
                    )
                )
                existing_review_ids.add(review_id)

    human_review_queue = list(existing_queue) + [
        item.model_dump() for item in new_review_items
    ]

    records_with_event_id = sum(1 for r in updated_records if r.get("linked_event_id"))
    single_record_event_count = sum(
        1 for e in linked_events if e.linking_status == "single_record_event"
    )
    multi_record_event_count = sum(
        1 for e in linked_events if e.linking_status == "linked_multi_record_event"
    )
    multi_source_event_count = sum(
        1 for e in linked_events if e.linking_status == "linked_multi_source_event"
    )
    needs_review_event_count = sum(
        1 for e in linked_events if e.linking_status == "needs_review"
    )
    not_linkable_event_count = sum(
        1 for e in linked_events if e.linking_status == "not_linkable"
    )

    summary = {
        "input_normalized_record_count": len(normalized_records),
        "linked_event_count": len(linked_events),
        "single_record_event_count": single_record_event_count,
        "multi_record_event_count": multi_record_event_count,
        "multi_source_event_count": multi_source_event_count,
        "needs_review_event_count": needs_review_event_count,
        "not_linkable_event_count": not_linkable_event_count,
        "records_with_linked_event_id_count": records_with_event_id,
        "linking_status_counts": dict(status_counter),
        "linking_warning_counts": dict(warning_counter),
        "linking_action_counts": dict(action_counter),
        "human_review_item_count": len(new_review_items),
    }

    trace = append_trace(
        state,
        node_name="record_linking",
        message=(
            f"Linked {records_with_event_id}/{len(normalized_records)} normalized "
            f"records into {len(linked_events)} candidate events."
        ),
        metadata=summary,
    )
    return {
        "normalized_records": updated_records,
        "linked_events": [e.model_dump() for e in linked_events],
        "human_review_queue": human_review_queue,
        "record_linking_summary": summary,
        "collection_trace": trace,
    }


# ---------------------------------------------------------------------------
# Placeholders (untouched by Step 9 beyond preserving incoming state)
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Cross-source consistency helpers
# ---------------------------------------------------------------------------


def _record_by_id(records: list[dict]) -> dict[str, dict]:
    return {r.get("record_id"): r for r in records if r.get("record_id")}


def _records_for_event(linked_event: dict, record_map: dict[str, dict]) -> list[dict]:
    out: list[dict] = []
    for rid in linked_event.get("record_ids") or []:
        rec = record_map.get(rid)
        if rec is not None:
            out.append(rec)
    return out


def _canonical_compare_value(value):
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return None
        return re.sub(r"\s+", " ", s).lower()
    return value


def _source_priority(
    source_type: str | None,
    policy: CrossSourceConsistencyPolicy,
) -> int:
    if not source_type:
        return 99
    return int(policy.source_authority_priority.get(source_type, 99))


def _value_packet(
    record: dict,
    field: str,
    policy: CrossSourceConsistencyPolicy,
) -> dict:
    raw = record.get(field)
    return {
        "record_id": record.get("record_id"),
        "value": raw,
        "canonical_value": _canonical_compare_value(raw),
        "source_id": record.get("source_id"),
        "source_url": record.get("source_url"),
        "source_type": record.get("source_type"),
        "source_priority": _source_priority(record.get("source_type"), policy),
        "publisher": record.get("publisher"),
        "evidence_quote": record.get("evidence_quote"),
    }


def _non_null_packets(
    records: list[dict],
    field: str,
    policy: CrossSourceConsistencyPolicy,
) -> list[dict]:
    packets = []
    for r in records:
        p = _value_packet(r, field, policy)
        if p["canonical_value"] is not None:
            packets.append(p)
    return packets


def _numeric_difference_stats(values: list[float]) -> dict:
    if len(values) < 2:
        return {
            "min": values[0] if values else None,
            "max": values[0] if values else None,
            "absolute_difference": 0.0,
            "relative_difference": 0.0,
        }
    mn = min(values)
    mx = max(values)
    abs_diff = abs(mx - mn)
    denom = max(abs(mn), 1.0)
    return {
        "min": mn,
        "max": mx,
        "absolute_difference": abs_diff,
        "relative_difference": abs_diff / denom,
    }


def _ordered_unique_values(packets: list[dict]) -> list:
    seen: set = set()
    out: list = []
    for p in packets:
        cv = p["canonical_value"]
        if cv in seen:
            continue
        seen.add(cv)
        out.append(p["value"])
    return out


def _compare_numeric_field(
    linked_event_id: str,
    records: list[dict],
    field: str,
    policy: CrossSourceConsistencyPolicy,
) -> FieldComparisonResult:
    packets = _non_null_packets(records, field, policy)
    compared_ids = [p["record_id"] for p in packets if p.get("record_id")]
    if len(packets) < 2:
        return FieldComparisonResult(
            linked_event_id=linked_event_id,
            field=field,
            compared_record_ids=compared_ids,
            unique_values=_ordered_unique_values(packets),
            conflict_detected=False,
        )

    canonical_values = [p["canonical_value"] for p in packets]
    unique_canon = {round(v, 6) for v in canonical_values}
    unique_values = _ordered_unique_values(packets)
    if len(unique_canon) <= 1:
        return FieldComparisonResult(
            linked_event_id=linked_event_id,
            field=field,
            compared_record_ids=compared_ids,
            unique_values=unique_values,
            conflict_detected=False,
        )

    thresholds = policy.numeric_conflict_thresholds or {}
    minor_abs = float(thresholds.get("minor_absolute_difference", 1))
    minor_rel = float(thresholds.get("minor_relative_difference", 0.05))
    major_rel = float(thresholds.get("major_relative_difference", 0.20))

    stats = _numeric_difference_stats(canonical_values)
    abs_diff = stats["absolute_difference"]
    rel_diff = stats["relative_difference"]

    if abs_diff <= minor_abs or rel_diff <= minor_rel:
        return FieldComparisonResult(
            linked_event_id=linked_event_id,
            field=field,
            compared_record_ids=compared_ids,
            unique_values=unique_values,
            conflict_detected=True,
            conflict_type="minor_numeric_difference",
            severity="low",
            possible_reason=(
                "Different sources may use slightly different reporting cutoffs or rounding."
            ),
            recommended_action=(
                "Keep all values with conflict flag; no immediate human review required."
            ),
            requires_human_review=False,
        )
    if rel_diff >= major_rel:
        return FieldComparisonResult(
            linked_event_id=linked_event_id,
            field=field,
            compared_record_ids=compared_ids,
            unique_values=unique_values,
            conflict_detected=True,
            conflict_type="major_numeric_difference",
            severity="high",
            possible_reason=(
                "Sources report substantially different numeric values for the same linked event."
            ),
            recommended_action=(
                "Send to human review and verify against the highest-authority source."
            ),
            requires_human_review=True,
        )
    return FieldComparisonResult(
        linked_event_id=linked_event_id,
        field=field,
        compared_record_ids=compared_ids,
        unique_values=unique_values,
        conflict_detected=True,
        conflict_type="numeric_mismatch",
        severity="medium",
        possible_reason="Sources report different numeric values for the same linked event.",
        recommended_action="Review source definitions, reporting dates, and case definitions.",
        requires_human_review=True,
    )


_TEXT_FIELD_PROFILE: dict[str, tuple[str, str, bool, str, str]] = {
    "country": (
        "location_mismatch",
        "high",
        True,
        "Records linked into the same event have inconsistent geographic fields.",
        "Review whether records are truly the same event or should be separated.",
    ),
    "subnational_location": (
        "location_mismatch",
        "high",
        True,
        "Records linked into the same event have inconsistent geographic fields.",
        "Review whether records are truly the same event or should be separated.",
    ),
    "virus_or_syndrome": (
        "virus_or_syndrome_mismatch",
        "high",
        True,
        "Records linked into the same event refer to different virus or syndrome labels.",
        "Review disease terminology and whether records should be split.",
    ),
    "case_definition": (
        "case_definition_mismatch",
        "medium",
        False,
        "Sources may use different case definitions or reporting categories.",
        "Keep all values but flag case definition differences.",
    ),
}


def _compare_text_field(
    linked_event_id: str,
    records: list[dict],
    field: str,
    policy: CrossSourceConsistencyPolicy,
) -> FieldComparisonResult:
    packets = _non_null_packets(records, field, policy)
    compared_ids = [p["record_id"] for p in packets if p.get("record_id")]
    unique_values = _ordered_unique_values(packets)
    if len(packets) < 2:
        return FieldComparisonResult(
            linked_event_id=linked_event_id,
            field=field,
            compared_record_ids=compared_ids,
            unique_values=unique_values,
            conflict_detected=False,
        )
    unique_canon = {p["canonical_value"] for p in packets}
    if len(unique_canon) <= 1:
        return FieldComparisonResult(
            linked_event_id=linked_event_id,
            field=field,
            compared_record_ids=compared_ids,
            unique_values=unique_values,
            conflict_detected=False,
        )

    profile = _TEXT_FIELD_PROFILE.get(field)
    if profile is None:
        return FieldComparisonResult(
            linked_event_id=linked_event_id,
            field=field,
            compared_record_ids=compared_ids,
            unique_values=unique_values,
            conflict_detected=True,
            conflict_type="numeric_mismatch",
            severity="medium",
            possible_reason=f"Records disagree on textual field {field}.",
            recommended_action="Review source values.",
            requires_human_review=True,
        )
    conflict_type, severity, requires_review, reason, action = profile
    return FieldComparisonResult(
        linked_event_id=linked_event_id,
        field=field,
        compared_record_ids=compared_ids,
        unique_values=unique_values,
        conflict_detected=True,
        conflict_type=conflict_type,
        severity=severity,
        possible_reason=reason,
        recommended_action=action,
        requires_human_review=requires_review,
    )


def _compare_date_field(
    linked_event_id: str,
    records: list[dict],
    field: str,
    policy: CrossSourceConsistencyPolicy,
) -> FieldComparisonResult:
    packets = _non_null_packets(records, field, policy)
    compared_ids = [p["record_id"] for p in packets if p.get("record_id")]
    unique_values = _ordered_unique_values(packets)
    if len(packets) < 2:
        return FieldComparisonResult(
            linked_event_id=linked_event_id,
            field=field,
            compared_record_ids=compared_ids,
            unique_values=unique_values,
            conflict_detected=False,
        )
    unique_canon = {p["canonical_value"] for p in packets}
    if len(unique_canon) <= 1:
        return FieldComparisonResult(
            linked_event_id=linked_event_id,
            field=field,
            compared_record_ids=compared_ids,
            unique_values=unique_values,
            conflict_detected=False,
        )
    return FieldComparisonResult(
        linked_event_id=linked_event_id,
        field=field,
        compared_record_ids=compared_ids,
        unique_values=unique_values,
        conflict_detected=True,
        conflict_type="date_mismatch",
        severity="medium",
        possible_reason=(
            "Sources use different reporting dates, event dates, or update cutoffs."
        ),
        recommended_action=(
            "Review whether dates represent reporting date, event start, event end, or publication update."
        ),
        requires_human_review=True,
    )


def _make_conflict(
    conflict_id: str,
    comparison: FieldComparisonResult,
    records: list[dict],
    field: str,
    policy: CrossSourceConsistencyPolicy,
) -> Conflict:
    packets = _non_null_packets(records, field, policy)
    values = [
        {
            "record_id": p.get("record_id"),
            "value": p.get("value"),
            "source_id": p.get("source_id"),
            "source_url": p.get("source_url"),
            "source_type": p.get("source_type"),
            "source_priority": p.get("source_priority"),
        }
        for p in packets
    ]
    record_ids = _unique_non_empty([p.get("record_id") for p in packets])
    source_ids = _unique_non_empty([p.get("source_id") for p in packets])
    source_urls = _unique_non_empty([p.get("source_url") for p in packets])
    source_types = _unique_non_empty([p.get("source_type") for p in packets])
    evidence_quotes = _unique_non_empty([p.get("evidence_quote") for p in packets])

    warnings = ["human_review_required"] if comparison.requires_human_review else []

    return Conflict(
        conflict_id=conflict_id,
        linked_event_id=comparison.linked_event_id,
        field=field,
        values=values,
        conflict_type=comparison.conflict_type or "missing_comparable_values",
        severity=comparison.severity or "low",
        possible_reason=comparison.possible_reason,
        recommended_action=comparison.recommended_action,
        record_ids=record_ids,
        source_ids=source_ids,
        source_urls=source_urls,
        source_types=source_types,
        evidence_quotes=evidence_quotes,
        requires_human_review=comparison.requires_human_review,
        resolution_status="unresolved",
        comparison_basis="linked_event_field_comparison",
        conflict_warnings=warnings,
        created_by=policy.consistency_method,
    )


def _event_status(
    event_conflicts: list[Conflict],
    record_count: int,
) -> tuple[str, list[str], bool]:
    if record_count <= 1:
        return "single_record_no_comparison", [], False
    if not event_conflicts:
        return "consistent", [], False
    has_high = any(c.severity == "high" for c in event_conflicts)
    has_review = any(c.requires_human_review for c in event_conflicts)
    if has_high or has_review:
        return "needs_review", ["high_or_reviewable_conflicts_detected"], True
    only_low = all(c.severity == "low" for c in event_conflicts)
    if only_low:
        return "consistent_with_minor_differences", ["minor_differences_detected"], False
    return "conflict_detected", ["conflicts_detected"], False


def _conflict_record_ids(conflict_dict: dict) -> list[str]:
    explicit = conflict_dict.get("record_ids") or []
    if explicit:
        return [str(x) for x in explicit if x]
    return [
        v.get("record_id") for v in (conflict_dict.get("values") or [])
        if v.get("record_id")
    ]


def _annotate_records_with_conflicts(
    records: list[dict],
    conflicts: list[dict],
) -> list[dict]:
    # Build per-record conflict lookups.
    by_record: dict[str, list[dict]] = {}
    for c in conflicts:
        for rid in _conflict_record_ids(c):
            by_record.setdefault(rid, []).append(c)

    updated: list[dict] = []
    for record in records:
        new_record = dict(record)
        existing_ids = list(new_record.get("conflict_ids") or [])
        warnings = list(new_record.get("record_consistency_warnings") or [])
        rid = new_record.get("record_id")
        associated = by_record.get(rid, [])

        added_ids: list[str] = []
        any_review = False
        for c in associated:
            cid = c.get("conflict_id")
            if cid and cid not in existing_ids and cid not in added_ids:
                added_ids.append(cid)
            if c.get("requires_human_review"):
                any_review = True

        new_conflict_ids = existing_ids + added_ids

        has_link = bool(new_record.get("linked_event_id"))
        if any_review:
            status = "needs_review"
            if "associated_with_reviewable_conflict" not in warnings:
                warnings.append("associated_with_reviewable_conflict")
            if "associated_with_conflict" not in warnings:
                warnings.append("associated_with_conflict")
        elif new_conflict_ids:
            status = "has_conflict"
            if "associated_with_conflict" not in warnings:
                warnings.append("associated_with_conflict")
        elif has_link:
            status = "no_conflict"
        else:
            status = "not_checked"

        new_record["conflict_ids"] = new_conflict_ids
        new_record["record_conflict_status"] = status
        new_record["record_consistency_warnings"] = warnings
        updated.append(new_record)
    return updated


def _make_conflict_review_item(conflict: Conflict) -> HumanReviewItem:
    related = [conflict.conflict_id] + list(conflict.record_ids or [])
    return HumanReviewItem(
        review_id=f"review_conflict_{conflict.conflict_id}",
        item_type="cross_source_conflict",
        related_ids=related,
        reason=(
            "Cross-source conflict requires review: "
            f"{conflict.field} / {conflict.conflict_type}"
        ),
        status="pending",
    )


# ---------------------------------------------------------------------------
# Node
# ---------------------------------------------------------------------------


def cross_source_consistency_check(state: DataCollectionState) -> dict:
    """Detect cross-source inconsistencies within each linked event."""

    policy = CrossSourceConsistencyPolicy(**load_cross_source_consistency_policy())
    normalized_records = list(state.get("normalized_records") or [])
    linked_events = list(state.get("linked_events") or [])
    existing_conflicts = list(state.get("conflicts") or [])
    existing_queue = list(state.get("human_review_queue") or [])
    existing_review_ids = {item.get("review_id") for item in existing_queue}

    record_map = _record_by_id(normalized_records)

    new_conflicts: list[Conflict] = []
    new_review_items: list[HumanReviewItem] = []
    updated_events: list[dict] = []

    next_conflict_index = len(existing_conflicts) + 1
    comparable_event_count = 0
    single_record_event_count = 0
    events_with_conflicts_count = 0
    events_requiring_human_review_count = 0
    event_status_counter: Counter = Counter()
    conflict_field_counter: Counter = Counter()
    conflict_type_counter: Counter = Counter()
    severity_counter: Counter = Counter()
    numeric_comparison_skipped_count = 0
    numeric_comparison_skip_reason_counter: Counter = Counter()

    def _numeric_comparison_skip_reason(recs: list[dict]) -> str | None:
        types = {
            r.get("statistical_count_type")
            for r in recs
            if r.get("statistical_count_type")
        }
        if len(types) > 1:
            return "different_statistical_count_type"
        periods = {
            r.get("reporting_period") for r in recs if r.get("reporting_period")
        }
        if len(periods) > 1:
            return "different_reporting_period"
        return None

    for event in linked_events:
        new_event = dict(event)
        event_id = new_event.get("linked_event_id") or ""
        records_in_event = _records_for_event(new_event, record_map)
        record_count = len(records_in_event)

        event_conflicts: list[Conflict] = []
        extra_event_warnings: list[str] = []
        if record_count <= 1:
            single_record_event_count += 1
        else:
            comparable_event_count += 1
            # Step 16: skip numeric comparison when records inside this event
            # carry different statistical meanings — comparing cumulative vs
            # annual vs subset counts produces spurious "conflicts".
            skip_reason = _numeric_comparison_skip_reason(records_in_event)
            if skip_reason is not None:
                numeric_comparison_skipped_count += 1
                numeric_comparison_skip_reason_counter[skip_reason] += 1
                if skip_reason == "different_statistical_count_type":
                    extra_event_warnings.append(
                        "numeric_comparison_skipped_due_to_different_statistical_count_type"
                    )
                else:
                    extra_event_warnings.append(
                        "numeric_comparison_skipped_due_to_different_reporting_period"
                    )
            else:
                for field in policy.comparable_numeric_fields:
                    cmp = _compare_numeric_field(event_id, records_in_event, field, policy)
                    if cmp.conflict_detected:
                        conflict_id = f"conf_{next_conflict_index:03d}"
                        next_conflict_index += 1
                        conflict = _make_conflict(conflict_id, cmp, records_in_event, field, policy)
                        new_conflicts.append(conflict)
                        event_conflicts.append(conflict)
            for field in policy.comparable_text_fields:
                cmp = _compare_text_field(event_id, records_in_event, field, policy)
                if cmp.conflict_detected:
                    conflict_id = f"conf_{next_conflict_index:03d}"
                    next_conflict_index += 1
                    conflict = _make_conflict(conflict_id, cmp, records_in_event, field, policy)
                    new_conflicts.append(conflict)
                    event_conflicts.append(conflict)
            for field in policy.comparable_date_fields:
                cmp = _compare_date_field(event_id, records_in_event, field, policy)
                if cmp.conflict_detected:
                    conflict_id = f"conf_{next_conflict_index:03d}"
                    next_conflict_index += 1
                    conflict = _make_conflict(conflict_id, cmp, records_in_event, field, policy)
                    new_conflicts.append(conflict)
                    event_conflicts.append(conflict)

        status, warnings, requires_review = _event_status(event_conflicts, record_count)

        # Merge in any numeric-comparison-skip warnings from Step 16.
        merged_warnings = list(warnings)
        for w in extra_event_warnings:
            if w not in merged_warnings:
                merged_warnings.append(w)

        new_event["consistency_status"] = status
        new_event["conflict_ids"] = [c.conflict_id for c in event_conflicts]
        new_event["consistency_warnings"] = merged_warnings
        new_event["checked_by"] = policy.consistency_method
        if requires_review:
            new_event["requires_human_review"] = True
        # else: preserve any earlier requires_human_review value
        event_status_counter[status] += 1
        if event_conflicts:
            events_with_conflicts_count += 1
        if requires_review:
            events_requiring_human_review_count += 1

        # Per-event review items.
        for conflict in event_conflicts:
            conflict_field_counter[conflict.field] += 1
            conflict_type_counter[conflict.conflict_type] += 1
            severity_counter[conflict.severity] += 1
            if conflict.requires_human_review:
                review_item = _make_conflict_review_item(conflict)
                if review_item.review_id not in existing_review_ids:
                    new_review_items.append(review_item)
                    existing_review_ids.add(review_item.review_id)

        updated_events.append(new_event)

    combined_conflict_dicts = list(existing_conflicts) + [c.model_dump() for c in new_conflicts]
    annotated_records = _annotate_records_with_conflicts(
        normalized_records, combined_conflict_dicts
    )

    record_status_counter: Counter = Counter()
    records_with_conflicts_count = 0
    for r in annotated_records:
        status = r.get("record_conflict_status") or "not_checked"
        record_status_counter[status] += 1
        if status in {"has_conflict", "needs_review"}:
            records_with_conflicts_count += 1

    human_review_queue = list(existing_queue) + [
        item.model_dump() for item in new_review_items
    ]

    summary = {
        "input_linked_event_count": len(linked_events),
        "input_normalized_record_count": len(normalized_records),
        "comparable_event_count": comparable_event_count,
        "single_record_event_count": single_record_event_count,
        "conflict_count": len(combined_conflict_dicts),
        "new_conflict_count": len(new_conflicts),
        "events_with_conflicts_count": events_with_conflicts_count,
        "events_requiring_human_review_count": events_requiring_human_review_count,
        "records_with_conflicts_count": records_with_conflicts_count,
        "human_review_conflict_count": len(new_review_items),
        "conflict_field_counts": dict(conflict_field_counter),
        "conflict_type_counts": dict(conflict_type_counter),
        "severity_counts": dict(severity_counter),
        "event_consistency_status_counts": dict(event_status_counter),
        "record_conflict_status_counts": dict(record_status_counter),
        "numeric_comparison_skipped_count": numeric_comparison_skipped_count,
        "numeric_comparison_skip_reason_counts": dict(
            numeric_comparison_skip_reason_counter
        ),
    }

    trace = append_trace(
        state,
        node_name="cross_source_consistency_check",
        message=(
            f"Checked {comparable_event_count} multi-record events; "
            f"found {len(new_conflicts)} new conflicts "
            f"({events_requiring_human_review_count} events need review)."
        ),
        metadata=summary,
    )
    return {
        "normalized_records": annotated_records,
        "linked_events": updated_events,
        "conflicts": combined_conflict_dicts,
        "human_review_queue": human_review_queue,
        "cross_source_consistency_summary": summary,
        "collection_trace": trace,
    }


def quality_gate_routing(state: DataCollectionState) -> dict:
    """Route to human_review if any review items are pending, else finalize."""

    queue = list(state.get("human_review_queue") or [])
    if queue:
        route = "human_review"
        message = (
            f"Human review required: {len(queue)} item(s) in human_review_queue."
        )
    else:
        route = "finalize"
        message = "No human review required; routing to final_data_package_builder."
    trace = append_trace(
        state,
        node_name="quality_gate_routing",
        message=message,
        metadata={"current_route": route, "human_review_queue_size": len(queue)},
    )
    return {
        "current_route": route,
        "collection_trace": trace,
    }
