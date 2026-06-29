"""Final data package builder (Step 13).

Assembles a hardened, auditable `FinalDataPackage` from the workflow state.
Adds package metadata, workflow-summary aggregation, data dictionary,
provenance manifest, export manifest, and synthetic-fixture detection.

Does NOT call LLMs, does NOT touch the network, does NOT resolve conflicts,
and does NOT apply human review decisions to modify records.
"""

from __future__ import annotations

import re
from datetime import date

from ..config import load_final_package_policy
from ..claim_corroboration import annotate_records_with_claim_corroboration
from ..models import (
    AnomalyResult,
    AppliedHumanReviewDecision,
    ClaimComparison,
    Conflict,
    CorroboratedEvent,
    EventCluster,
    FinalDataPackage,
    FinalPackagePolicy,
    HumanReviewAuditEntry,
    HumanReviewItem,
    LinkedEvent,
    PublicHealthRecord,
    PublicHealthClaim,
    RejectedHumanReviewDecision,
    SourceIdentityAssessment,
    SourceRegistryEntry,
    ValidationCase,
    ValidationComparison,
    ValidationResult,
)
from ..observation_type_datasets import (
    DATASET_VIEW_KEYS,
    apply_observation_type_counts_to_summaries,
    build_observation_type_dataset_split,
)
from ..run_quality_gates import apply_run_quality_gates
from ..source_coverage import (
    build_source_coverage_audit,
    build_task_evidence_contract,
)
from ..state import DataCollectionState, append_trace


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------


def _fixed_generated_at(policy: FinalPackagePolicy) -> str:
    return policy.fixed_generated_at


def _safe_list(state: DataCollectionState, key: str) -> list:
    return list(state.get(key) or [])


def _source_lookup(rows: list[dict]) -> dict[str, dict]:
    return {str(row.get("source_id") or ""): row for row in rows if row.get("source_id")}


def _human_review_items_from_core_metric_gaps(
    gaps: list[dict],
    source_registry: list[dict],
    documents: list[dict],
) -> list[dict]:
    source_by_id = _source_lookup(source_registry)
    docs_by_source: dict[str, list[dict]] = {}
    for doc in documents:
        source_id = str(doc.get("source_id") or "")
        if source_id:
            docs_by_source.setdefault(source_id, []).append(doc)

    items: list[dict] = []
    for idx, gap in enumerate(gaps, start=1):
        source_id = str(gap.get("source_id") or "")
        source = source_by_id.get(source_id) or {}
        docs = docs_by_source.get(source_id) or []
        source_urls = []
        for value in (
            source.get("canonical_url"),
            source.get("url"),
            *(doc.get("canonical_url") or doc.get("url") for doc in docs),
        ):
            if value and value not in source_urls:
                source_urls.append(value)
        reason = str(
            gap.get("reason") or "core_metric_text_attempted_but_no_records_extracted"
        )
        items.append(
            {
                "review_id": f"review_core_metric_gap_{source_id or idx}",
                "item_type": "core_metric_extraction_gap",
                "related_ids": [source_id] if source_id else [],
                "reason": reason,
                "status": "pending",
                "priority": 1,
                "source_ids": [source_id] if source_id else [],
                "source_urls": source_urls,
                "severity": "medium",
                "evidence_summary": (
                    "Task-relevant source text appeared to contain core "
                    "epidemiology metric signals, but extraction produced no "
                    "structured records."
                ),
                "suggested_action": "review_source_for_core_metric_extraction",
                "decision_options": [
                    "extract_metric_record",
                    "mark_no_extractable_task_metric",
                    "send_to_best_available_context",
                ],
                "review_packet": {
                    "core_metric_extraction_gap": gap,
                    "source": source,
                    "documents": docs[:3],
                },
            }
        )
    return items


def _append_missing_human_review_items(
    existing: list[dict],
    additions: list[dict],
) -> list[dict]:
    output = list(existing or [])
    seen = {str(item.get("review_id") or "") for item in output}
    for item in additions:
        review_id = str(item.get("review_id") or "")
        if review_id and review_id in seen:
            continue
        output.append(item)
        if review_id:
            seen.add(review_id)
    return output


def _lower(value) -> str:
    return str(value or "").strip().lower()


def _iso_date(value) -> date | None:
    text = str(value or "").strip()
    if not text:
        return None
    match = re.search(r"\d{4}-\d{2}-\d{2}", text)
    if not match:
        return None
    try:
        return date.fromisoformat(match.group(0))
    except ValueError:
        return None


def _record_requirement_ids(record: dict) -> set[str]:
    return {
        str(value)
        for value in (record.get("coverage_requirement_ids") or [])
        if value not in (None, "")
    }


def _record_period_dates(record: dict) -> tuple[date | None, date | None]:
    start = None
    end = None
    for key in ("metric_period_start", "period_start_date", "event_start_date", "start_date"):
        start = _iso_date(record.get(key))
        if start:
            break
    for key in ("metric_period_end", "period_end_date", "event_end_date", "end_date"):
        end = _iso_date(record.get(key))
        if end:
            break
    return start, end


def _requirement_period_dates(requirement: dict) -> tuple[date | None, date | None]:
    start = _iso_date(
        requirement.get("period_start") or requirement.get("reporting_period_start")
    )
    end = _iso_date(
        requirement.get("period_end") or requirement.get("reporting_period_end")
    )
    return start, end


def _record_period_conflicts_requirement(record: dict, requirement: dict) -> bool:
    req_start, req_end = _requirement_period_dates(requirement)
    if not req_start or not req_end:
        return False
    rec_start, rec_end = _record_period_dates(record)
    if rec_start and rec_end:
        if rec_end < rec_start:
            rec_start, rec_end = rec_end, rec_start
        if req_end < req_start:
            req_start, req_end = req_end, req_start
        return rec_start != req_start or rec_end != req_end
    requirement_year = requirement.get("year")
    if not requirement_year and req_start.year == req_end.year:
        requirement_year = req_start.year
    if _lower(requirement.get("period_basis")) == "annual" and requirement_year:
        text = _lower(
            " ".join(
                str(record.get(key) or "")
                for key in (
                    "reporting_period",
                    "metric_period_label",
                    "count_semantics",
                    "statistical_count_type",
                    "evidence_quote",
                )
            )
        )
        if str(requirement_year) in text and "annual" in text:
            return False
        return True
    anchor = _iso_date(record.get("date_anchor") or record.get("date_reported"))
    if anchor and (req_start <= anchor <= req_end):
        return False
    return False


def _record_matches_requirement_exact(
    record: dict,
    requirement: dict,
    source_ids: set[str],
) -> bool:
    requirement_id = str(requirement.get("requirement_id") or "")
    explicit_ids = _record_requirement_ids(record)
    if explicit_ids:
        if requirement_id not in explicit_ids:
            return False
    elif str(record.get("source_id") or "") not in source_ids:
        return False
    if _record_period_conflicts_requirement(record, requirement):
        return False
    req_location = _lower(requirement.get("geography") or requirement.get("location"))
    if req_location:
        record_geo = _lower(
            " ".join(
                str(record.get(key) or "")
                for key in (
                    "geographic_scope",
                    "subnational_location",
                    "country",
                    "location",
                )
            )
        )
        if req_location not in record_geo:
            return False
    req_disease = _lower(requirement.get("disease"))
    if req_disease:
        record_disease = _lower(
            " ".join(
                str(record.get(key) or "")
                for key in (
                    "disease",
                    "disease_standard_name",
                    "virus_or_syndrome",
                    "pathogen_or_syndrome",
                )
            )
        )
        if req_disease not in record_disease:
            return False
    return True


def _direct_collection_mode(state: dict) -> bool:
    structured = state.get("structured_task") or {}
    spec = state.get("collection_spec") or {}
    return (
        str(
            structured.get("collection_mode")
            or spec.get("collection_mode")
            or state.get("collection_mode")
            or ""
        ).strip()
        == "direct_collection"
    )


def _record_has_public_health_metric(record: dict) -> bool:
    if record.get("metric_name") or record.get("metric_category"):
        return True
    if record.get("metric_value") not in (None, ""):
        return True
    metric_fields = (
        "tests_positive",
        "tests_total",
        "positivity_rate",
        "ili_percentage",
        "ed_visit_percentage",
        "hospitalizations",
        "deaths",
        "outbreak_count",
    )
    return any(record.get(field) not in (None, "") for field in metric_fields)


_EDGE_METRIC_RE = re.compile(
    r"\b("
    r"missing|unknown|not\s+reported|not\s+available|"
    r"race|ethnicity|birth\s+origin|age\s+missing|demographic"
    r")\b",
    re.IGNORECASE,
)


def _requirement_core_metric_families(requirement: dict) -> set[str]:
    raw = (
        requirement.get("core_metric_families")
        or requirement.get("accepted_metric_families")
        or []
    )
    return {
        re.sub(r"[^a-z0-9]+", "_", str(value).strip().lower()).strip("_")
        for value in raw
        if str(value or "").strip()
    }


def _record_is_edge_metric(record: dict) -> bool:
    text = " ".join(
        str(record.get(key) or "")
        for key in (
            "metric_name",
            "metric_category",
            "evidence_quote",
            "source_row_label",
            "source_column_label",
            "metric_column_label",
        )
    )
    return bool(_EDGE_METRIC_RE.search(text))


def _record_matches_core_metric_family(record: dict, families: set[str]) -> bool:
    if not families:
        return True
    if _record_is_edge_metric(record):
        return False
    text = _lower(
        " ".join(
            str(record.get(key) or "")
            for key in (
                "metric_name",
                "metric_category",
                "observation_type",
                " ".join(str(value) for value in record.get("observation_types") or []),
                "evidence_quote",
            )
        )
    )
    normalized_text = re.sub(r"[^a-z0-9]+", "_", text).strip("_")
    if families & set(filter(None, normalized_text.split("_"))):
        return True
    if "case_count" in families and (
        record.get("cases_confirmed") not in (None, "")
        or record.get("cases_probable") not in (None, "")
        or record.get("cases_suspected") not in (None, "")
        or record.get("cases_unspecified") not in (None, "")
        or "case_count" in normalized_text
        or "total_cases" in normalized_text
        or "confirmed_cases" in normalized_text
        or "reported_cases" in normalized_text
        or "notified_cases" in normalized_text
    ):
        return True
    if "incidence_rate" in families and (
        record.get("incidence_rate") not in (None, "")
        or "incidence_rate" in normalized_text
        or ("incidence" in text and "rate" in text)
    ):
        return True
    if families & {"death_count", "mortality", "mortality_rate", "death_rate"} and (
        record.get("deaths") not in (None, "")
        or "death" in text
        or "mortality" in text
    ):
        return True
    if families & {"hospitalization", "hospitalization_count", "hospitalization_rate"} and (
        record.get("hospitalizations") not in (None, "")
        or "hospital" in text
    ):
        return True
    if families & {"treatment_coverage", "vaccination_coverage", "coverage"} and (
        "coverage" in text or "treatment" in text or "vaccination" in text
    ):
        return True
    for family in families:
        if family and family in normalized_text:
            return True
    return False


def _record_source_high_trust(record: dict, registry_by_id: dict[str, dict]) -> bool:
    source_id = str(record.get("source_id") or "")
    source = registry_by_id.get(source_id) or {}
    level = str(
        record.get("credibility_level") or source.get("credibility_level") or ""
    ).strip().lower()
    if level in {"high", "medium"}:
        return True
    publisher = str(
        record.get("publisher")
        or record.get("actual_publisher")
        or source.get("publisher")
        or source.get("actual_publisher")
        or ""
    ).lower()
    url = str(record.get("source_url") or source.get("canonical_url") or "").lower()
    source_type = str(
        record.get("source_type_final")
        or record.get("source_type")
        or source.get("source_type_final")
        or source.get("source_type")
        or ""
    ).lower()
    return (
        ".gov" in url
        or "department of health" in publisher
        or "public health" in publisher
        or "health agency" in source_type
        or "official" in source_type
    )


def _task_period_from_state(state: dict) -> tuple[date | None, date | None]:
    structured = state.get("structured_task") or {}
    spec = state.get("collection_spec") or {}
    start = _iso_date(
        structured.get("start_date")
        or structured.get("date_start")
        or spec.get("start_date")
        or spec.get("date_start")
    )
    end = _iso_date(
        structured.get("end_date")
        or structured.get("date_end")
        or spec.get("end_date")
        or spec.get("date_end")
    ) or start
    if start and end and end < start:
        start, end = end, start
    return start, end


def _record_period_from_record(record: dict) -> tuple[date | None, date | None]:
    start = _iso_date(
        record.get("metric_period_start")
        or record.get("date_start")
        or record.get("event_start_date")
        or record.get("date_reported")
        or record.get("date_anchor")
    )
    end = _iso_date(
        record.get("metric_period_end")
        or record.get("date_end")
        or record.get("event_end_date")
        or record.get("date_reported")
        or record.get("date_anchor")
    ) or start
    if start and end and end < start:
        start, end = end, start
    return start, end


def _best_available_period_fit(record: dict, state: dict) -> str:
    task_start, task_end = _task_period_from_state(state)
    record_start, record_end = _record_period_from_record(record)
    if not task_start or not task_end or not record_start or not record_end:
        return "period_uncertain"
    if record_start == task_start and record_end == task_end:
        return "exact"
    if record_start <= task_start and record_end >= task_end:
        return "broader_than_task"
    if record_end < task_start or record_start > task_end:
        return "outside_task_window"
    return "partial_overlap"


def _best_available_geography_fit(record: dict, state: dict) -> str:
    task = state.get("structured_task") or {}
    spec = state.get("collection_spec") or {}
    task_location = _lower(task.get("location") or spec.get("geography"))
    if not task_location:
        return "unknown"
    record_geo = _lower(
        " ".join(
            str(record.get(key) or "")
            for key in (
                "geographic_scope",
                "subnational_location",
                "country",
                "locality",
                "admin_area",
                "location",
                "place",
            )
        )
    )
    if task_location and task_location in record_geo:
        return "exact"
    scope_type = _lower(record.get("geographic_scope_type"))
    scope = _lower(record.get("geographic_scope"))
    if scope_type in {"global", "region", "international", "multi country", "multi-country"}:
        return "broader_than_task"
    if scope in {"global", "world", "worldwide", "americas", "europe", "eu/eea", "region of the americas"}:
        return "broader_than_task"
    if record_geo:
        return "outside_task_geography"
    return "unknown"


def _requirement_ids_for_best_available_record(
    record: dict,
    state: dict,
    registry_by_id: dict[str, dict],
) -> list[str]:
    ids = [
        str(value)
        for value in (record.get("coverage_requirement_ids") or [])
        if str(value or "").strip()
    ]
    if ids:
        return sorted(dict.fromkeys(ids))
    source = registry_by_id.get(str(record.get("source_id") or "")) or {}
    ids = [
        str(value)
        for value in (source.get("coverage_requirement_ids") or [])
        if str(value or "").strip()
    ]
    if ids:
        return sorted(dict.fromkeys(ids))
    requirements = _safe_list(state, "source_coverage_requirements")
    if len(requirements) == 1 and requirements[0].get("requirement_id"):
        return [str(requirements[0]["requirement_id"])]
    return []


def _build_record_linkage_indexes(state: dict) -> tuple[dict[str, dict], dict[str, list[dict]], dict[str, dict]]:
    registry_by_id = {
        str(row.get("source_id")): row
        for row in _safe_list(state, "source_registry")
        if isinstance(row, dict) and row.get("source_id")
    }
    documents_by_source: dict[str, list[dict]] = {}
    for document in _safe_list(state, "documents"):
        if not isinstance(document, dict):
            continue
        source_id = str(document.get("source_id") or "")
        if source_id:
            documents_by_source.setdefault(source_id, []).append(document)
    chunks_by_id = {
        str(row.get("chunk_id")): row
        for row in _safe_list(state, "evidence_chunks")
        if isinstance(row, dict) and row.get("chunk_id")
    }
    return registry_by_id, documents_by_source, chunks_by_id


def _record_requirement_ids_from_lineage(
    record: dict,
    state: dict,
    registry_by_id: dict[str, dict],
    documents_by_source: dict[str, list[dict]],
    chunks_by_id: dict[str, dict],
) -> list[str]:
    ids: list[str] = [
        str(value)
        for value in (record.get("coverage_requirement_ids") or [])
        if str(value or "").strip()
    ]
    if ids:
        return sorted(dict.fromkeys(ids))
    chunk = chunks_by_id.get(str(record.get("supporting_chunk_id") or ""))
    if chunk:
        ids.extend(
            str(value)
            for value in (chunk.get("coverage_requirement_ids") or [])
            if str(value or "").strip()
        )
    source_id = str(record.get("source_id") or "")
    source = registry_by_id.get(source_id) or {}
    ids.extend(
        str(value)
        for value in (source.get("coverage_requirement_ids") or [])
        if str(value or "").strip()
    )
    for document in documents_by_source.get(source_id, []):
        ids.extend(
            str(value)
            for value in (document.get("coverage_requirement_ids") or [])
            if str(value or "").strip()
        )
    if ids:
        return sorted(dict.fromkeys(ids))
    requirements = _safe_list(state, "source_coverage_requirements")
    if len(requirements) == 1 and requirements[0].get("requirement_id"):
        return [str(requirements[0]["requirement_id"])]
    return []


def _requirement_lookup(state: dict) -> dict[str, dict]:
    return {
        str(row.get("requirement_id")): row
        for row in _safe_list(state, "source_coverage_requirements")
        if isinstance(row, dict) and row.get("requirement_id")
    }


def _unique_nonempty(values) -> list[str]:
    output: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = str(value or "").strip()
        if not text or text in seen:
            continue
        output.append(text)
        seen.add(text)
    return output


def _joined_requirement_value(requirements: list[dict], *keys: str) -> str | None:
    values = _unique_nonempty(
        requirement.get(key)
        for requirement in requirements
        for key in keys
    )
    if not values:
        return None
    if len(values) == 1:
        return values[0]
    return " | ".join(values)


def _requirement_period_bound(
    requirements: list[dict],
    *,
    start: bool,
) -> str | None:
    keys = (
        ("period_start", "reporting_period_start")
        if start
        else ("period_end", "reporting_period_end")
    )
    dated: list[tuple[date, str]] = []
    fallback: list[str] = []
    for requirement in requirements:
        for key in keys:
            text = str(requirement.get(key) or "").strip()
            if not text:
                continue
            parsed = _iso_date(text)
            if parsed:
                dated.append((parsed, text))
            elif text not in fallback:
                fallback.append(text)
    if dated:
        selected = (
            min(dated, key=lambda item: item[0])
            if start
            else max(dated, key=lambda item: item[0])
        )
        return selected[1]
    if not fallback:
        return None
    return fallback[0] if len(fallback) == 1 else " | ".join(fallback)


def _apply_requirement_linkage_metadata(
    record: dict,
    requirement_ids: list[str],
    requirements_by_id: dict[str, dict],
) -> None:
    if not requirement_ids:
        return
    record["matched_requirement_id"] = requirement_ids[0]
    record["matched_requirement_ids"] = requirement_ids
    matched = [requirements_by_id[req_id] for req_id in requirement_ids if req_id in requirements_by_id]
    if len(requirement_ids) == 1:
        record["requirement_match_status"] = "linked_to_task_requirement"
    else:
        record["requirement_match_status"] = "linked_to_multiple_task_requirements"
    if not matched:
        return
    geography = _joined_requirement_value(matched, "geography", "location")
    if geography:
        record["requirement_geography"] = geography
    period_start = _requirement_period_bound(matched, start=True)
    if period_start:
        record["requirement_period_start"] = period_start
    period_end = _requirement_period_bound(matched, start=False)
    if period_end:
        record["requirement_period_end"] = period_end
    period_label = _joined_requirement_value(
        matched,
        "reporting_period_label",
        "period_label",
        "year",
    )
    if period_label:
        record["requirement_period_label"] = period_label
    period_basis = _joined_requirement_value(matched, "period_basis")
    if period_basis:
        record["requirement_period_basis"] = period_basis
    granularity = _joined_requirement_value(matched, "time_granularity")
    if granularity:
        record["requirement_time_granularity"] = granularity


def _enrich_records_with_requirement_linkage(records: list[dict], state: dict) -> list[dict]:
    if not records:
        return []
    registry_by_id, documents_by_source, chunks_by_id = _build_record_linkage_indexes(state)
    requirements_by_id = _requirement_lookup(state)
    has_requirements = bool(_safe_list(state, "source_coverage_requirements"))
    enriched_records: list[dict] = []
    for record in records:
        if not isinstance(record, dict):
            continue
        row = dict(record)
        requirement_ids = _record_requirement_ids_from_lineage(
            row,
            state,
            registry_by_id,
            documents_by_source,
            chunks_by_id,
        )
        if requirement_ids:
            row["coverage_requirement_ids"] = requirement_ids
            _apply_requirement_linkage_metadata(row, requirement_ids, requirements_by_id)
        elif has_requirements:
            reasons = [
                str(value)
                for value in (row.get("record_task_fit_reasons") or [])
                if str(value or "").strip()
            ]
            if "requirement_linkage_missing" not in reasons:
                reasons.append("requirement_linkage_missing")
            row["record_task_fit_reasons"] = reasons
        source = registry_by_id.get(str(row.get("source_id") or "")) or {}
        if source:
            row.setdefault(
                "source_url",
                source.get("canonical_url") or source.get("url"),
            )
            row.setdefault("source_role_final", source.get("source_role_final"))
            row.setdefault("target_fit_status", source.get("target_fit_status"))
        if not row.get("record_geography_fit_status"):
            row["record_geography_fit_status"] = _best_available_geography_fit(row, state)
        if not row.get("record_period_fit_status"):
            row["record_period_fit_status"] = _best_available_period_fit(row, state)
        enriched_records.append(row)
    return enriched_records


def _best_available_reason(record: dict, state: dict) -> str:
    flags = {
        str(flag)
        for flag in (record.get("quality_gate_blocking_flags") or [])
        if flag
    }
    reason_text = _lower(
        " ".join(
            str(value or "")
            for value in (
                record.get("quarantine_reason"),
                " ".join(str(value) for value in record.get("quality_gate_reasons") or []),
                " ".join(flags),
            )
        )
    )
    period_fit = _best_available_period_fit(record, state)
    if period_fit != "exact" or "period" in reason_text or "date" in reason_text:
        return "period_mismatch_best_available_context"
    if "geography" in reason_text or "broader_than_task" in reason_text:
        return "geography_mismatch_best_available_context"
    return "near_match_best_available_context"


def _build_best_available_context_records(
    quarantined_records: list[dict],
    state: dict,
) -> list[dict]:
    """Keep useful near-miss records visible without relaxing strict final gates."""

    if not _direct_collection_mode(state):
        return []
    registry_by_id = {
        str(row.get("source_id")): row
        for row in _safe_list(state, "source_registry")
        if isinstance(row, dict) and row.get("source_id")
    }
    disallowed_flags = {
        "disease_pathogen_incompatible_with_task",
        "non_seasonal_influenza_subtype",
        "record_geography_outside_task",
        "missing_direct_collection_geography",
        "source_not_task_relevant",
        "source_period_mismatch",
        "metric_row_binding_unresolved",
        "missing_direct_collection_metric",
        "missing_direct_collection_source_provenance",
    }
    best_available: list[dict] = []
    for record in quarantined_records:
        if not isinstance(record, dict):
            continue
        flags = {
            str(flag)
            for flag in (record.get("quality_gate_blocking_flags") or [])
            if flag
        }
        if flags & disallowed_flags:
            continue
        if not _record_has_public_health_metric(record):
            continue
        if not _record_source_high_trust(record, registry_by_id):
            continue
        if not (record.get("source_url") or record.get("source_id")):
            continue
        if not (record.get("evidence_quote") or record.get("source_title")):
            continue
        row = dict(record)
        requirement_ids = _requirement_ids_for_best_available_record(
            row, state, registry_by_id
        )
        if requirement_ids:
            row["coverage_requirement_ids"] = requirement_ids
            row.setdefault("source_url", (registry_by_id.get(str(row.get("source_id") or "")) or {}).get("canonical_url"))
        if not row.get("record_geography_fit_status"):
            row["record_geography_fit_status"] = _best_available_geography_fit(row, state)
        if not row.get("record_period_fit_status"):
            row["record_period_fit_status"] = _best_available_period_fit(row, state)
        if not row.get("best_available_reason"):
            row["best_available_reason"] = _best_available_reason(row, state)
        best_available.append(row)
    return best_available


def _refresh_source_coverage_audit(
    requirements: list[dict],
    registry: list[dict],
    documents: list[dict],
    extracted_records: list[dict],
    accepted_records: list[dict],
    existing_audit: dict | None = None,
) -> dict:
    if not requirements:
        return existing_audit or {}
    audit = build_source_coverage_audit(requirements, registry, documents)
    extracted_by_source: dict[str, int] = {}
    accepted_by_source: dict[str, int] = {}
    extracted_record_ids_by_requirement: dict[str, set[str]] = {}
    accepted_record_ids_by_requirement: dict[str, set[str]] = {}
    for record in extracted_records:
        source_id = str(record.get("source_id") or "")
        if source_id:
            extracted_by_source[source_id] = extracted_by_source.get(source_id, 0) + 1
        record_id = str(record.get("record_id") or record.get("source_record_id") or "")
        for requirement_id in record.get("coverage_requirement_ids") or []:
            if record_id and requirement_id:
                extracted_record_ids_by_requirement.setdefault(str(requirement_id), set()).add(record_id)
    for record in accepted_records:
        source_id = str(record.get("source_id") or "")
        if source_id:
            accepted_by_source[source_id] = accepted_by_source.get(source_id, 0) + 1
        record_id = str(record.get("record_id") or record.get("source_record_id") or "")
        for requirement_id in record.get("coverage_requirement_ids") or []:
            if record_id and requirement_id:
                accepted_record_ids_by_requirement.setdefault(str(requirement_id), set()).add(record_id)

    extracted_requirement_count = 0
    accepted_requirement_count = 0
    best_available_requirement_count = 0
    total_extracted = 0
    total_accepted = 0
    total_best_available = 0
    parsed_requirement_count = 0
    rows: list[dict] = []
    for row in audit.get("requirements") or []:
        source_ids = {
            str(source_id)
            for source_id in (
                row.get("matched_source_ids")
                or row.get("fetched_source_ids")
                or row.get("parsed_source_ids")
                or []
            )
            if source_id
        }
        extracted_count = sum(extracted_by_source.get(source_id, 0) for source_id in source_ids)
        accepted_count = sum(accepted_by_source.get(source_id, 0) for source_id in source_ids)
        requirement_id = str(row.get("requirement_id") or "")
        extracted_record_ids = {
            str(record.get("record_id") or record.get("source_record_id") or "")
            for record in extracted_records
            if _record_matches_requirement_exact(record, row, source_ids)
            and (record.get("record_id") or record.get("source_record_id"))
        }
        accepted_record_ids = {
            str(record.get("record_id") or record.get("source_record_id") or "")
            for record in accepted_records
            if _record_matches_requirement_exact(record, row, source_ids)
            and (record.get("record_id") or record.get("source_record_id"))
        }
        core_families = _requirement_core_metric_families(row)
        accepted_core_record_ids = {
            str(record.get("record_id") or record.get("source_record_id") or "")
            for record in accepted_records
            if str(record.get("record_id") or record.get("source_record_id") or "")
            in accepted_record_ids
            and _record_matches_core_metric_family(record, core_families)
        }
        source_record_ids = {
            str(record.get("record_id") or record.get("source_record_id") or "")
            for record in extracted_records
            if str(record.get("source_id") or "") in source_ids
            and (record.get("record_id") or record.get("source_record_id"))
        }
        best_available_record_ids = sorted(source_record_ids - extracted_record_ids)
        accepted_source_ids = {
            str(record.get("source_id") or "")
            for record in accepted_records
            if str(record.get("record_id") or record.get("source_record_id") or "") in accepted_record_ids
            and record.get("source_id")
        }
        extracted_count = len(extracted_record_ids)
        accepted_count = len(accepted_record_ids)
        has_core_requirement = bool(core_families)
        core_accepted = bool(accepted_core_record_ids)
        requirement_complete = bool(accepted_count) and (
            core_accepted or not has_core_requirement
        )
        if requirement_complete:
            strict_status = "core_metric_accepted" if core_accepted else "accepted_exact_record"
        elif accepted_count:
            strict_status = "edge_metric_only"
        elif best_available_record_ids:
            strict_status = "best_available_only"
        elif extracted_count:
            strict_status = "records_quarantined"
        elif row.get("parsed"):
            strict_status = "parsed_no_records"
        elif row.get("unusable"):
            strict_status = "target_source_unusable"
        else:
            strict_status = "target_source_missing"
        refreshed = dict(row)
        refreshed.update(
            {
                "extracted": extracted_count > 0,
                "extracted_record_count": extracted_count,
                "extracted_record_ids": sorted(extracted_record_ids),
                "accepted": accepted_count > 0,
                "coverage_complete": requirement_complete,
                "strict_status": strict_status,
                "task_value_status": strict_status,
                "accepted_core_record_count": len(accepted_core_record_ids),
                "accepted_core_record_ids": sorted(accepted_core_record_ids),
                "accepted_record_count": accepted_count,
                "accepted_record_ids": sorted(accepted_record_ids),
                "accepted_source_ids": sorted(accepted_source_ids),
                "best_available_record_count": len(best_available_record_ids),
                "best_available_record_ids": best_available_record_ids,
            }
        )
        if refreshed.get("parsed"):
            parsed_requirement_count += 1
        if extracted_count:
            extracted_requirement_count += 1
            total_extracted += extracted_count
        if accepted_count:
            accepted_requirement_count += 1
            total_accepted += accepted_count
        if best_available_record_ids and not accepted_count:
            best_available_requirement_count += 1
            total_best_available += len(best_available_record_ids)
        if requirement_complete:
            refreshed["missing_reason"] = None
        elif accepted_count:
            refreshed["missing_reason"] = "edge_metric_only"
        elif refreshed.get("extracted"):
            refreshed["missing_reason"] = "records_quarantined"
        elif best_available_record_ids:
            refreshed["missing_reason"] = "best_available_only"
        elif refreshed.get("parsed"):
            refreshed["missing_reason"] = "parsed_no_records"
        elif refreshed.get("unusable"):
            refreshed["missing_reason"] = "target_alias_error_page"
        elif refreshed.get("fetch_failed") or (
            refreshed.get("fetch_attempted") and not refreshed.get("fetched")
        ):
            refreshed["missing_reason"] = "target_fetch_failed"
        elif refreshed.get("discovered"):
            refreshed["missing_reason"] = "target_source_discovered_not_fetched"
        else:
            refreshed["missing_reason"] = "target_source_missing"
        rows.append(refreshed)

    requirement_count = len(rows)
    complete_requirement_count = sum(1 for row in rows if row.get("coverage_complete"))
    partial_requirement_count = (
        requirement_count - complete_requirement_count if requirement_count else 0
    )
    missing_requirement_ids = [
        row.get("requirement_id")
        for row in rows
        if row.get("requirement_id")
        and not row.get("coverage_complete")
    ]
    if not requirement_count:
        coverage_completeness_status = "not_required"
    elif complete_requirement_count == requirement_count:
        coverage_completeness_status = "complete_target_coverage"
    elif complete_requirement_count:
        coverage_completeness_status = "partial_target_coverage"
    else:
        coverage_completeness_status = "no_target_coverage"

    audit.update(
        {
            "requirements": rows,
            "extracted_requirement_count": extracted_requirement_count,
            "accepted_requirement_count": accepted_requirement_count,
            "extracted_record_count": total_extracted,
            "accepted_record_count": total_accepted,
            "best_available_requirement_count": best_available_requirement_count,
            "best_available_record_count": total_best_available,
            "complete_requirement_count": complete_requirement_count,
            "partial_requirement_count": partial_requirement_count,
            "missing_requirement_ids": missing_requirement_ids,
            "coverage_completeness_status": coverage_completeness_status,
        }
    )
    if requirement_count and complete_requirement_count == requirement_count:
        audit["coverage_status"] = "target_official_source_accepted"
    elif complete_requirement_count:
        audit["coverage_status"] = "partial_target_coverage"
    elif accepted_requirement_count:
        audit["coverage_status"] = "edge_metric_only"
    elif extracted_requirement_count:
        audit["coverage_status"] = "records_quarantined"
    elif best_available_requirement_count:
        audit["coverage_status"] = "best_available_only"
    elif parsed_requirement_count:
        audit["coverage_status"] = "parsed_no_records"
    return audit


def _refine_direct_coverage_status(
    audit: dict,
    *,
    content_fetch_summary: dict | None = None,
    structured_extraction_summary: dict | None = None,
) -> dict:
    if not audit:
        return audit
    coverage_completeness_status = str(
        audit.get("coverage_completeness_status") or ""
    )
    if coverage_completeness_status in {
        "complete_target_coverage",
        "partial_target_coverage",
    }:
        return audit

    content_fetch_summary = content_fetch_summary or {}
    structured_extraction_summary = structured_extraction_summary or {}
    usable_task_docs = int(
        content_fetch_summary.get("usable_task_collection_document_count") or 0
    )
    if usable_task_docs > 0:
        return audit

    refined_status: str | None = None
    if content_fetch_summary.get("target_unusable_needs_fallback"):
        if content_fetch_summary.get("fallback_fetch_attempted"):
            refined_status = "fallback_target_fetch_failed"
        else:
            refined_status = "target_alias_error_page_needs_fallback"
    elif structured_extraction_summary.get("no_task_collection_document"):
        refined_status = "no_task_collection_document"

    if not refined_status:
        return audit

    out = dict(audit)
    out["coverage_status"] = refined_status
    out["coverage_failure_stage"] = refined_status
    rows: list[dict] = []
    for row in out.get("requirements") or []:
        refreshed = dict(row)
        if not (
            refreshed.get("accepted")
            or refreshed.get("extracted")
            or refreshed.get("parsed")
        ):
            refreshed["missing_reason"] = refined_status
        rows.append(refreshed)
    out["requirements"] = rows
    return out


def _records_need_claim_annotation(records: list[dict]) -> bool:
    return any(
        isinstance(record, dict)
        and record.get("record_id")
        and not record.get("claim_ids")
        for record in records
    )


def _claim_annotated_records_for_finalization(
    state: DataCollectionState,
    records: list[dict],
) -> list[dict]:
    claims = _safe_list(state, "claims")
    if not claims or not _records_need_claim_annotation(records):
        return records
    return annotate_records_with_claim_corroboration(
        [dict(record) for record in records if isinstance(record, dict)],
        claims,
        _safe_list(state, "corroborated_events"),
    )


def _collect_workflow_summaries(
    state: DataCollectionState,
    policy: FinalPackagePolicy,
) -> dict:
    return {field: state.get(field) for field in policy.workflow_summary_fields}


def _build_data_dictionary(
    state: DataCollectionState,
    policy: FinalPackagePolicy,
) -> list[dict]:
    schema = state.get("collection_schema") or {}
    core_fields = schema.get("core_fields") if isinstance(schema, dict) else None
    if core_fields:
        result: list[dict] = []
        for field in core_fields:
            result.append(
                {
                    "name": field.get("name"),
                    "type": field.get("type"),
                    "required": field.get("required", False),
                    "description": field.get("description") or "",
                }
            )
        return result
    return [
        {"name": name, "type": "unknown", "required": False, "description": ""}
        for name in policy.final_dataset_field_order
    ]


# ---------------------------------------------------------------------------
# Synthetic fixture detection
# ---------------------------------------------------------------------------


def _section_has_fixture(obj, markers: list[str]) -> bool:
    if obj is None:
        return False
    if isinstance(obj, dict):
        if obj.get("is_fixture_document") is True:
            return True
        if obj.get("fixture_id"):
            return True
        meta = obj.get("metadata")
        if isinstance(meta, dict):
            if meta.get("synthetic_fixture") is True:
                return True
            if meta.get("not_real_public_health_data") is True:
                return True
            if meta.get("fixture_id"):
                return True
        for value in obj.values():
            if _section_has_fixture(value, markers):
                return True
        return False
    if isinstance(obj, list):
        return any(_section_has_fixture(v, markers) for v in obj)
    if isinstance(obj, str):
        return any(marker in obj for marker in markers)
    return False


def _detect_synthetic_fixture_data(
    state: DataCollectionState,
    policy: FinalPackagePolicy,
) -> tuple[bool, str | None]:
    markers = list(policy.synthetic_fixture_markers or [])
    for key in (
        "documents",
        "evidence_chunks",
        "raw_records",
        "validated_records",
        "normalized_records",
        "conflicts",
        "human_review_queue",
    ):
        items = state.get(key) or []
        if _section_has_fixture(items, markers):
            return (
                True,
                (
                    "This final data package contains synthetic fixture data used "
                    "only for deterministic workflow testing; it is not real "
                    "public health data."
                ),
            )
    return False, None


# ---------------------------------------------------------------------------
# Provenance + metadata
# ---------------------------------------------------------------------------


def _build_provenance_manifest(state: DataCollectionState) -> dict:
    normalized = _safe_list(state, "normalized_records")
    conflicts = _safe_list(state, "conflicts")

    def _count(records, field):
        return sum(
            1
            for r in records
            if isinstance(r, dict)
            and r.get(field) not in (None, "", [], {})
        )

    return {
        "source_count": len(_safe_list(state, "source_registry")),
        "source_identity_assessment_count": len(
            _safe_list(state, "source_identity_assessments")
        ),
        "document_count": len(_safe_list(state, "documents")),
        "evidence_chunk_count": len(_safe_list(state, "evidence_chunks")),
        "raw_record_count": len(_safe_list(state, "raw_records")),
        "validated_record_count": len(_safe_list(state, "validated_records")),
        "normalized_record_count": len(normalized),
        "linked_event_count": len(_safe_list(state, "linked_events")),
        "event_cluster_count": len(_safe_list(state, "event_clusters")),
        "duplicate_cluster_count": len(_safe_list(state, "duplicate_clusters")),
        "validation_case_count": len(_safe_list(state, "validation_cases")),
        "validation_comparison_count": len(_safe_list(state, "validation_comparisons")),
        "validation_result_count": len(_safe_list(state, "validation_results")),
        "claim_count": len(_safe_list(state, "claims")),
        "claim_comparison_count": len(_safe_list(state, "claim_comparisons")),
        "corroborated_event_count": len(_safe_list(state, "corroborated_events")),
        "anomaly_result_count": len(_safe_list(state, "anomaly_results")),
        "applied_human_review_decision_count": len(
            _safe_list(state, "applied_human_review_decisions")
        ),
        "rejected_human_review_decision_count": len(
            _safe_list(state, "rejected_human_review_decisions")
        ),
        "human_review_audit_entry_count": len(
            _safe_list(state, "human_review_audit_trail")
        ),
        "final_dataset_post_review_count": len(
            _safe_list(state, "final_dataset_post_review")
        ),
        "conflict_count": len(conflicts),
        "human_review_item_count": len(_safe_list(state, "human_review_queue")),
        "records_with_source_url_count": _count(normalized, "source_url"),
        "records_with_evidence_quote_count": _count(normalized, "evidence_quote"),
        "records_with_supporting_chunk_id_count": _count(normalized, "supporting_chunk_id"),
        "records_with_linked_event_id_count": _count(normalized, "linked_event_id"),
        "records_with_event_cluster_id_count": _count(normalized, "event_cluster_id"),
        "countable_record_count": sum(
            1 for r in normalized if isinstance(r, dict) and r.get("countable") is True
        ),
        "non_countable_duplicate_count": sum(
            1
            for r in normalized
            if isinstance(r, dict)
            and r.get("event_member_status") == "non_countable_duplicate"
        ),
        "generic_record_count": sum(
            1
            for r in normalized
            if isinstance(r, dict)
            and r.get("record_schema") == "generic_public_health_record"
        ),
        "legacy_hantavirus_record_count": sum(
            1
            for r in normalized
            if isinstance(r, dict) and r.get("disease") == "Hantavirus disease"
        ),
        "conflicts_with_record_ids_count": sum(
            1
            for c in conflicts
            if isinstance(c, dict) and (c.get("record_ids") or [])
        ),
        "conflicts_requiring_human_review_count": sum(
            1
            for c in conflicts
            if isinstance(c, dict) and c.get("requires_human_review")
        ),
    }


def _detect_llm_used(state: DataCollectionState) -> bool:
    for key in ("normalized_records", "validated_records", "raw_records"):
        for record in state.get(key) or []:
            if isinstance(record, dict) and record.get("llm_used"):
                return True
    summary = state.get("llm_extraction_summary") or {}
    if isinstance(summary, dict):
        if summary.get("llm_enabled") and (summary.get("llm_success_count") or 0) > 0:
            return True
    return False


def _build_package_metadata(
    state: DataCollectionState,
    policy: FinalPackagePolicy,
    contains_fixture: bool,
    fixture_notice: str | None,
    trace: list[dict],
    llm_used: bool,
) -> dict:
    spec = state.get("collection_spec") or {}
    llm_summary = state.get("llm_extraction_summary") or {}
    search_summary = state.get("source_search_execution_summary") or {}
    return {
        "package_name": "data_collection_workflow_final_package",
        "package_version": policy.package_version,
        "package_builder": policy.package_builder,
        "generated_at": _fixed_generated_at(policy),
        "disease": spec.get("disease") if isinstance(spec, dict) else None,
        "geography": spec.get("geography") if isinstance(spec, dict) else None,
        "time_window": spec.get("time_window") if isinstance(spec, dict) else None,
        "workflow_node_count": len(trace),
        "contains_synthetic_fixture_data": contains_fixture,
        "synthetic_fixture_notice": fixture_notice,
        "llm_used": llm_used,
        "llm_provider": llm_summary.get("llm_provider") if isinstance(llm_summary, dict) else None,
        "llm_model": llm_summary.get("llm_model") if isinstance(llm_summary, dict) else None,
        "web_search_used": bool(
            isinstance(search_summary, dict)
            and (search_summary.get("executed_query_count") or 0) > 0
        ),
        "baseline_comparison_included": False,
        "evaluation_metrics_included": False,
    }


def _build_export_manifest(
    package: FinalDataPackage,
    policy: FinalPackagePolicy,
) -> dict:
    return {
        "exportable_sections": list(policy.exportable_sections),
        "section_counts": {
            "final_dataset": len(package.final_dataset),
            "final_dataset_pre_quality_gate": len(
                package.final_dataset_pre_quality_gate
            ),
            "final_dataset_post_review": len(package.final_dataset_post_review),
            "quarantined_records": len(package.quarantined_records),
            "pending_review_records": len(package.pending_review_records),
            "non_primary_observations": len(package.non_primary_observations),
            "final_case_dataset": len(package.final_case_dataset),
            "global_outbreak_event_dataset": len(package.global_outbreak_event_dataset),
            "regional_surveillance_dataset": len(package.regional_surveillance_dataset),
            "country_year_aggregate_dataset": len(package.country_year_aggregate_dataset),
            "official_alert_dataset": len(package.official_alert_dataset),
            "zero_case_statements": len(package.zero_case_statements),
            "exposure_monitoring_records": len(
                package.exposure_monitoring_records
            ),
            "surveillance_summary_records": len(
                package.surveillance_summary_records
            ),
            "outbreak_summary_records": len(package.outbreak_summary_records),
            "context_records": len(package.context_records),
            "unclassified_observation_records": len(
                package.unclassified_observation_records
            ),
            "observation_type_dataset_summary": (
                1 if package.observation_type_dataset_summary else 0
            ),
            "record_inclusion_decisions": len(package.record_inclusion_decisions),
            "run_quality_summary": 1 if package.run_quality_summary else 0,
            "final_dataset_quality_summary": (
                1 if package.final_dataset_quality_summary else 0
            ),
            "records_excluded_by_human_review": len(
                package.records_excluded_by_human_review
            ),
            "source_registry": len(package.source_registry),
            "source_identity_assessments": len(package.source_identity_assessments),
            "source_identity_summary": 1 if package.source_identity_summary else 0,
            "linked_events": len(package.linked_events),
            "event_clusters": len(package.event_clusters),
            "duplicate_clusters": len(package.duplicate_clusters),
            "validation_cases": len(package.validation_cases),
            "validation_comparisons": len(package.validation_comparisons),
            "validation_results": len(package.validation_results),
            "claims": len(package.claims),
            "claim_comparisons": len(package.claim_comparisons),
            "corroborated_events": len(package.corroborated_events),
            "corroboration_summary": 1 if package.corroboration_summary else 0,
            "anomaly_results": len(package.anomaly_results),
            "applied_human_review_decisions": len(
                package.applied_human_review_decisions
            ),
            "rejected_human_review_decisions": len(
                package.rejected_human_review_decisions
            ),
            "human_review_audit_trail": len(package.human_review_audit_trail),
            "conflicts": len(package.conflicts),
            "human_review_items": len(package.human_review_items),
            "excluded_sources": len(package.excluded_sources),
            "collection_trace": len(package.collection_trace),
            "data_dictionary": len(package.data_dictionary),
            "evidence_chunks": len(package.evidence_chunks),
        },
    }


def _build_finalization_summary(
    package: FinalDataPackage,
    workflow_summaries: dict,
    contains_fixture: bool,
) -> dict:
    package_dict = package.model_dump()
    disease_counts: dict[str, int] = {}
    source_type_counts: dict[str, int] = {}
    extraction_method_counts: dict[str, int] = {}
    for record in package_dict.get("final_dataset") or []:
        disease = str(record.get("disease") or "unknown")
        source_type = str(record.get("source_type") or "unknown")
        method = str(record.get("extraction_method") or "unknown")
        disease_counts[disease] = disease_counts.get(disease, 0) + 1
        source_type_counts[source_type] = source_type_counts.get(source_type, 0) + 1
        extraction_method_counts[method] = extraction_method_counts.get(method, 0) + 1
    return {
        "final_dataset_count": len(package.final_dataset),
        "final_dataset_pre_quality_gate_count": len(
            package.final_dataset_pre_quality_gate
        ),
        "final_dataset_post_review_count": len(package.final_dataset_post_review),
        "quarantined_record_count": len(package.quarantined_records),
        "pending_review_record_count": len(package.pending_review_records),
        "non_primary_observation_count": len(package.non_primary_observations),
        "final_case_dataset_count": len(package.final_case_dataset),
        "global_outbreak_event_dataset_count": len(
            package.global_outbreak_event_dataset
        ),
        "regional_surveillance_dataset_count": len(
            package.regional_surveillance_dataset
        ),
        "country_year_aggregate_dataset_count": len(
            package.country_year_aggregate_dataset
        ),
        "official_alert_dataset_count": len(package.official_alert_dataset),
        "zero_case_statement_count": len(package.zero_case_statements),
        "exposure_monitoring_record_count": len(
            package.exposure_monitoring_records
        ),
        "surveillance_summary_record_count": len(
            package.surveillance_summary_records
        ),
        "outbreak_summary_record_count": len(package.outbreak_summary_records),
        "context_record_count": len(package.context_records),
        "unclassified_observation_count": len(
            package.unclassified_observation_records
        ),
        "run_quality_status": package.run_quality_summary.get("run_quality_status"),
        "final_dataset_mode": package.run_quality_summary.get("final_dataset_mode"),
        "records_excluded_by_human_review_count": len(
            package.records_excluded_by_human_review
        ),
        "generic_record_count": sum(
            1
            for record in package_dict.get("final_dataset") or []
            if record.get("record_schema") == "generic_public_health_record"
        ),
        "legacy_hantavirus_record_count": sum(
            1
            for record in package_dict.get("final_dataset") or []
            if record.get("disease") == "Hantavirus disease"
        ),
        "disease_counts": disease_counts,
        "source_type_counts": source_type_counts,
        "extraction_method_counts": extraction_method_counts,
        "source_registry_count": len(package.source_registry),
        "source_identity_assessment_count": len(package.source_identity_assessments),
        "excluded_source_count": len(package.excluded_sources),
        "linked_event_count": len(package.linked_events),
        "event_cluster_count": len(package.event_clusters),
        "duplicate_cluster_count": len(package.duplicate_clusters),
        "validation_case_count": len(package.validation_cases),
        "validation_comparison_count": len(package.validation_comparisons),
        "validation_result_count": len(package.validation_results),
        "claim_count": len(package.claims),
        "claim_comparison_count": len(package.claim_comparisons),
        "corroborated_event_count": len(package.corroborated_events),
        "corroborated_primary_case_event_count": package.corroboration_summary.get(
            "corroborated_primary_case_event_count", 0
        ),
        "anomaly_result_count": len(package.anomaly_results),
        "applied_human_review_decision_count": len(
            package.applied_human_review_decisions
        ),
        "rejected_human_review_decision_count": len(
            package.rejected_human_review_decisions
        ),
        "human_review_audit_entry_count": len(package.human_review_audit_trail),
        "countable_record_count": sum(
            1
            for record in package_dict.get("final_dataset") or []
            if record.get("countable") is True
        ),
        "non_countable_duplicate_count": sum(
            1
            for record in package_dict.get("final_dataset") or []
            if record.get("event_member_status") == "non_countable_duplicate"
        ),
        "conflict_count": len(package.conflicts),
        "human_review_item_count": len(package.human_review_items),
        "collection_trace_count": len(package.collection_trace),
        "workflow_summary_count": len(workflow_summaries),
        "contains_synthetic_fixture_data": contains_fixture,
        "final_package_keys": sorted(package_dict.keys()),
}


def _default_post_review_records(records: list[dict]) -> list[dict]:
    out: list[dict] = []
    for record in records:
        row = dict(record)
        row.setdefault("review_status", "unreviewed")
        row.setdefault("review_decision_ids", [])
        row.setdefault("record_excluded_by_human_review", False)
        row.setdefault("final_dataset_included", True)
        row.setdefault("human_review_applied", False)
        row.setdefault("human_review_audit_ids", [])
        row.setdefault("anomaly_status", None)
        row.setdefault("anomaly_ids", [])
        out.append(row)
    return out


def _default_human_review_application_summary(records: list[dict]) -> dict:
    return {
        "records_before_review": len(records),
        "records_after_review": len(records),
        "records_excluded_by_review": 0,
        "records_corrected_by_review": 0,
        "clusters_modified_by_review": 0,
        "validation_results_modified_by_review": 0,
        "sources_modified_by_review": 0,
        "anomalies_resolved_by_review": 0,
        "decisions_provided_count": 0,
        "decisions_applied_count": 0,
        "decisions_rejected_count": 0,
        "audit_entry_count": 0,
    }


# ---------------------------------------------------------------------------
# Node
# ---------------------------------------------------------------------------


def final_data_package_builder(state: DataCollectionState) -> dict:
    """Assemble the hardened, auditable FinalDataPackage."""

    policy = FinalPackagePolicy(**load_final_package_policy())

    normalized_records = _claim_annotated_records_for_finalization(
        state,
        _safe_list(state, "normalized_records"),
    )
    state = dict(state)
    state["normalized_records"] = normalized_records
    post_review_records = _safe_list(state, "final_dataset_post_review")
    records_excluded_by_review = _safe_list(state, "records_excluded_by_human_review")
    quality_state = dict(state)
    quality_state.update(
        {
            "normalized_records": normalized_records,
            "final_dataset_post_review": post_review_records,
            "records_excluded_by_human_review": records_excluded_by_review,
        }
    )
    quality_result = apply_run_quality_gates(quality_state)
    pre_quality_records = _safe_list(
        quality_result, "final_dataset_pre_quality_gate"
    )
    accepted_records = _safe_list(quality_result, "final_dataset")
    post_review_records = _safe_list(quality_result, "final_dataset_post_review")
    quarantined_records = _safe_list(quality_result, "quarantined_records")
    pending_review_records = _safe_list(quality_result, "pending_review_records")
    non_primary_observations = _safe_list(
        quality_result, "non_primary_observations"
    )
    record_inclusion_decisions = _safe_list(
        quality_result, "record_inclusion_decisions"
    )
    run_quality_summary = quality_result.get("run_quality_summary") or {}
    final_dataset_quality_summary = (
        quality_result.get("final_dataset_quality_summary") or {}
    )
    direct_collection_summary = quality_result.get("direct_collection_summary") or {}
    collection_decision_summary = (
        quality_result.get("collection_decision_summary") or {}
    )
    task_acceptance_contract = state.get("task_acceptance_contract") or {}
    task_evidence_contract = state.get("task_evidence_contract") or build_task_evidence_contract(
        state
    )
    evidence_strategy_plan = state.get("evidence_strategy_plan") or {}
    source_triage_results = _safe_list(state, "source_triage_results")
    evidence_chunks = _safe_list(state, "evidence_chunks")
    chunk_relevance_assessments = _safe_list(
        state, "chunk_relevance_assessments"
    )
    record_task_fit_assessments = _safe_list(
        state, "record_task_fit_assessments"
    )
    source_critic_summary = state.get("source_critic_summary") or {}
    direct_fast_path_summary = (
        state.get("direct_fast_path_summary")
        or source_critic_summary.get("direct_fast_path_summary")
        or {}
    )
    metric_extraction_plan = state.get("metric_extraction_plan") or {}
    metric_row_extraction_audit = _safe_list(state, "metric_row_extraction_audit")
    content_fetch_summary = state.get("content_fetch_summary") or {}
    structured_extraction_summary = state.get("structured_extraction_summary") or {}
    source_registry = _safe_list(state, "source_registry")
    documents = _safe_list(state, "documents")
    source_identity_assessments = _safe_list(state, "source_identity_assessments")
    official_coverage_candidates = _safe_list(state, "official_coverage_candidates")
    source_coverage_requirements = _safe_list(state, "source_coverage_requirements")

    lineage_state = dict(state)
    lineage_state.update(
        {
            "source_registry": source_registry,
            "documents": documents,
            "evidence_chunks": evidence_chunks,
            "source_coverage_requirements": source_coverage_requirements,
        }
    )
    normalized_records = _enrich_records_with_requirement_linkage(
        normalized_records,
        lineage_state,
    )
    pre_quality_records = _enrich_records_with_requirement_linkage(
        pre_quality_records,
        lineage_state,
    )
    accepted_records = _enrich_records_with_requirement_linkage(
        accepted_records,
        lineage_state,
    )
    post_review_records = _enrich_records_with_requirement_linkage(
        post_review_records,
        lineage_state,
    )
    quarantined_records = _enrich_records_with_requirement_linkage(
        quarantined_records,
        lineage_state,
    )
    pending_review_records = _enrich_records_with_requirement_linkage(
        pending_review_records,
        lineage_state,
    )
    non_primary_observations = _enrich_records_with_requirement_linkage(
        non_primary_observations,
        lineage_state,
    )

    source_coverage_audit = _refresh_source_coverage_audit(
        source_coverage_requirements,
        source_registry,
        documents,
        normalized_records,
        accepted_records,
        state.get("source_coverage_audit") or {},
    )
    source_coverage_audit = _refine_direct_coverage_status(
        source_coverage_audit,
        content_fetch_summary=content_fetch_summary,
        structured_extraction_summary=structured_extraction_summary,
    )
    if source_coverage_audit:
        refreshed_coverage_status = source_coverage_audit.get("coverage_status")
        should_override_summary_coverage = bool(
            source_coverage_audit.get("requirement_count")
            or refreshed_coverage_status
            in {
                "partial_target_coverage",
                "target_alias_error_page",
                "all_target_aliases_unusable",
                "no_task_collection_document",
                "target_alias_error_page_needs_fallback",
                "fallback_target_fetch_failed",
                "target_official_source_missing",
                "target_official_source_fetch_failed",
                "target_official_source_unusable",
            }
        )
        direct_collection_summary = dict(direct_collection_summary)
        run_quality_summary = dict(run_quality_summary)
        collection_decision_summary = dict(collection_decision_summary)
        if refreshed_coverage_status and should_override_summary_coverage:
            direct_collection_summary["coverage_status"] = refreshed_coverage_status
            run_quality_summary["coverage_status"] = refreshed_coverage_status
            collection_decision_summary["coverage_status"] = refreshed_coverage_status
        for key in (
            "coverage_completeness_status",
            "complete_requirement_count",
            "partial_requirement_count",
            "missing_requirement_ids",
        ):
            if key in source_coverage_audit:
                direct_collection_summary[key] = source_coverage_audit.get(key)
                collection_decision_summary[key] = source_coverage_audit.get(key)
    target_official_fetch_plan = _safe_list(state, "target_official_fetch_plan")
    must_fetch_sources = _safe_list(state, "must_fetch_sources")
    fetch_failures_blocking = _safe_list(state, "fetch_failures_blocking")
    linked_events = _safe_list(state, "linked_events")
    event_clusters = _safe_list(state, "event_clusters")
    duplicate_clusters = _safe_list(state, "duplicate_clusters")
    validation_cases = _safe_list(state, "validation_cases")
    validation_comparisons = _safe_list(state, "validation_comparisons")
    validation_results = _safe_list(state, "validation_results")
    claims = _safe_list(state, "claims")
    claim_comparisons = _safe_list(state, "claim_comparisons")
    corroborated_events = _safe_list(state, "corroborated_events")
    corroboration_summary = state.get("corroboration_summary") or {}
    anomaly_results = _safe_list(state, "anomaly_results")
    applied_decisions = _safe_list(state, "applied_human_review_decisions")
    rejected_decisions = _safe_list(state, "rejected_human_review_decisions")
    audit_trail = _safe_list(state, "human_review_audit_trail")
    conflicts = _safe_list(state, "conflicts")
    human_review_queue = _safe_list(state, "human_review_queue")
    core_metric_extraction_gaps = (
        structured_extraction_summary.get("core_metric_extraction_gaps")
        or metric_extraction_plan.get("core_metric_extraction_gaps")
        or []
    )
    human_review_queue = _append_missing_human_review_items(
        human_review_queue,
        _human_review_items_from_core_metric_gaps(
            core_metric_extraction_gaps,
            source_registry,
            documents,
        ),
    )

    split_state = dict(state)
    split_state.update(
        {
            "final_dataset_pre_quality_gate": pre_quality_records,
            "final_dataset": accepted_records,
            "final_dataset_post_review": post_review_records,
            "quarantined_records": quarantined_records,
            "pending_review_records": pending_review_records,
            "non_primary_observations": non_primary_observations,
            "record_inclusion_decisions": record_inclusion_decisions,
            "run_quality_summary": run_quality_summary,
            "final_dataset_quality_summary": final_dataset_quality_summary,
            "direct_collection_summary": direct_collection_summary,
            "collection_decision_summary": collection_decision_summary,
        }
    )
    observation_type_dataset_split = build_observation_type_dataset_split(split_state)
    run_quality_summary, final_dataset_quality_summary = (
        apply_observation_type_counts_to_summaries(
            run_quality_summary,
            final_dataset_quality_summary,
            observation_type_dataset_split,
        )
    )
    observation_type_dataset_summary = observation_type_dataset_split[
        "observation_type_dataset_summary"
    ]
    observation_dataset_views = {
        key: _safe_list(observation_type_dataset_split, key)
        for key in DATASET_VIEW_KEYS
    }
    best_available_context_records = _build_best_available_context_records(
        quarantined_records,
        state,
    )

    final_dataset_pre_quality_gate = [
        PublicHealthRecord(**r) for r in pre_quality_records
    ]
    final_dataset = [PublicHealthRecord(**r) for r in accepted_records]
    final_dataset_post_review = [
        PublicHealthRecord(**r) for r in post_review_records
    ]
    quarantined_record_models = [
        PublicHealthRecord(**r) for r in quarantined_records
    ]
    pending_review_record_models = [
        PublicHealthRecord(**r) for r in pending_review_records
    ]
    non_primary_observation_models = [
        PublicHealthRecord(**r) for r in non_primary_observations
    ]
    final_case_dataset_models = [
        PublicHealthRecord(**r)
        for r in observation_dataset_views["final_case_dataset"]
    ]
    global_outbreak_event_models = [
        PublicHealthRecord(**r)
        for r in observation_dataset_views["global_outbreak_event_dataset"]
    ]
    regional_surveillance_models = [
        PublicHealthRecord(**r)
        for r in observation_dataset_views["regional_surveillance_dataset"]
    ]
    country_year_aggregate_models = [
        PublicHealthRecord(**r)
        for r in observation_dataset_views["country_year_aggregate_dataset"]
    ]
    official_alert_models = [
        PublicHealthRecord(**r)
        for r in observation_dataset_views["official_alert_dataset"]
    ]
    probable_case_dataset_models = [
        PublicHealthRecord(**r)
        for r in observation_dataset_views["probable_case_dataset"]
    ]
    suspected_case_dataset_models = [
        PublicHealthRecord(**r)
        for r in observation_dataset_views["suspected_case_dataset"]
    ]
    unspecified_case_dataset_models = [
        PublicHealthRecord(**r)
        for r in observation_dataset_views["unspecified_case_dataset"]
    ]
    death_dataset_models = [
        PublicHealthRecord(**r) for r in observation_dataset_views["death_dataset"]
    ]
    hospitalization_dataset_models = [
        PublicHealthRecord(**r)
        for r in observation_dataset_views["hospitalization_dataset"]
    ]
    zero_case_statement_models = [
        PublicHealthRecord(**r)
        for r in observation_dataset_views["zero_case_statements"]
    ]
    exposure_monitoring_models = [
        PublicHealthRecord(**r)
        for r in observation_dataset_views["exposure_monitoring_records"]
    ]
    surveillance_summary_models = [
        PublicHealthRecord(**r)
        for r in observation_dataset_views["surveillance_summary_records"]
    ]
    outbreak_summary_models = [
        PublicHealthRecord(**r)
        for r in observation_dataset_views["outbreak_summary_records"]
    ]
    context_record_models = [
        PublicHealthRecord(**r) for r in observation_dataset_views["context_records"]
    ]
    best_available_context_record_models = [
        PublicHealthRecord(**r) for r in best_available_context_records
    ]
    unclassified_observation_models = [
        PublicHealthRecord(**r)
        for r in observation_dataset_views["unclassified_observation_records"]
    ]
    records_excluded_models = [
        PublicHealthRecord(**r) for r in records_excluded_by_review
    ]
    registry_models = [SourceRegistryEntry(**e) for e in source_registry]
    source_identity_models = [
        SourceIdentityAssessment(**item) for item in source_identity_assessments
    ]
    excluded_sources = [
        e
        for e in registry_models
        if e.screening_decision == "exclude"
        or e.critic_decision == "exclude"
        or e.final_screening_decision == "exclude"
        or e.status == "excluded"
    ]
    included_registry = [e for e in registry_models if e not in excluded_sources]

    direct_collection_summary = dict(direct_collection_summary or {})
    direct_collection_summary["final_dataset_count"] = len(final_dataset)
    direct_collection_summary["quarantined_record_count"] = len(
        quarantined_record_models
    )
    direct_collection_summary["pending_review_record_count"] = len(
        pending_review_record_models
    )
    direct_collection_summary["human_review_record_count"] = len(
        pending_review_record_models
    )
    direct_collection_summary["final_case_dataset_count"] = len(
        final_case_dataset_models
    )
    direct_collection_summary["dataset_view_counts"] = (
        observation_type_dataset_summary.get("dataset_view_counts") or {}
    )
    direct_collection_summary["best_available_context_record_count"] = len(
        best_available_context_record_models
    )
    direct_collection_summary["best_available_context_record_ids"] = [
        record.record_id for record in best_available_context_record_models
    ]
    direct_collection_summary["core_metric_extraction_gap_count"] = int(
        structured_extraction_summary.get("core_metric_extraction_gap_count")
        or metric_extraction_plan.get("core_metric_extraction_gap_count")
        or len(core_metric_extraction_gaps)
        or 0
    )
    direct_collection_summary["core_metric_extraction_gap_source_ids"] = sorted(
        {
            str(gap.get("source_id") or "")
            for gap in core_metric_extraction_gaps
            if gap.get("source_id")
        }
    )
    run_quality_summary = dict(run_quality_summary or {})
    final_dataset_quality_summary = dict(final_dataset_quality_summary or {})
    run_quality_summary["direct_collection_summary"] = direct_collection_summary
    final_dataset_quality_summary["direct_collection_summary"] = (
        direct_collection_summary
    )

    linked_event_models = [LinkedEvent(**le) for le in linked_events]
    event_cluster_models = [EventCluster(**cluster) for cluster in event_clusters]
    duplicate_cluster_models = [
        EventCluster(**cluster) for cluster in duplicate_clusters
    ]
    validation_case_models = [ValidationCase(**item) for item in validation_cases]
    validation_comparison_models = [
        ValidationComparison(**item) for item in validation_comparisons
    ]
    validation_result_models = [
        ValidationResult(**item) for item in validation_results
    ]
    claim_models = [PublicHealthClaim(**item) for item in claims]
    claim_comparison_models = [
        ClaimComparison(**item) for item in claim_comparisons
    ]
    corroborated_event_models = [
        CorroboratedEvent(**item) for item in corroborated_events
    ]
    anomaly_result_models = [AnomalyResult(**item) for item in anomaly_results]
    applied_decision_models = [
        AppliedHumanReviewDecision(**item) for item in applied_decisions
    ]
    rejected_decision_models = [
        RejectedHumanReviewDecision(**item) for item in rejected_decisions
    ]
    audit_models = [HumanReviewAuditEntry(**item) for item in audit_trail]
    conflict_models = [Conflict(**c) for c in conflicts]
    human_review_items = [HumanReviewItem(**item) for item in human_review_queue]

    contains_fixture, fixture_notice = _detect_synthetic_fixture_data(state, policy)
    summary_state = dict(state)
    summary_state.update(
        {
            "run_quality_summary": run_quality_summary,
            "final_dataset_quality_summary": final_dataset_quality_summary,
            "direct_collection_summary": direct_collection_summary,
            "collection_decision_summary": collection_decision_summary,
        }
    )
    workflow_summaries = _collect_workflow_summaries(summary_state, policy)
    data_dictionary = _build_data_dictionary(state, policy)
    provenance_manifest = _build_provenance_manifest(state)
    llm_used = _detect_llm_used(state)
    human_review_application_summary = state.get(
        "human_review_application_summary"
    ) or _default_human_review_application_summary(normalized_records)

    # Append trace before building the package so package.collection_trace
    # includes this very event and stays length-aligned with state trace.
    trace = append_trace(
        state,
        node_name="final_data_package_builder",
        message="Assembled hardened FinalDataPackage from current state.",
        metadata={
            "final_dataset_size": len(final_dataset),
            "final_dataset_pre_quality_gate_size": len(
                final_dataset_pre_quality_gate
            ),
            "quarantined_record_count": len(quarantined_record_models),
            "pending_review_record_count": len(pending_review_record_models),
            "non_primary_observation_count": len(non_primary_observation_models),
            "final_case_dataset_count": len(final_case_dataset_models),
            "global_outbreak_event_dataset_count": len(global_outbreak_event_models),
            "regional_surveillance_dataset_count": len(regional_surveillance_models),
            "country_year_aggregate_dataset_count": len(country_year_aggregate_models),
            "official_alert_dataset_count": len(official_alert_models),
            "zero_case_statement_count": len(zero_case_statement_models),
            "exposure_monitoring_record_count": len(exposure_monitoring_models),
            "context_record_count": len(context_record_models),
            "best_available_context_record_count": len(
                best_available_context_record_models
            ),
            "observation_type_dataset_summary": observation_type_dataset_summary,
            "run_quality_status": run_quality_summary.get("run_quality_status"),
            "source_registry_size": len(included_registry),
            "source_identity_assessment_count": len(source_identity_models),
            "excluded_source_count": len(excluded_sources),
            "linked_event_count": len(linked_event_models),
            "event_cluster_count": len(event_cluster_models),
            "duplicate_cluster_count": len(duplicate_cluster_models),
            "validation_result_count": len(validation_result_models),
            "claim_count": len(claim_models),
            "claim_comparison_count": len(claim_comparison_models),
            "corroborated_event_count": len(corroborated_event_models),
            "anomaly_result_count": len(anomaly_result_models),
            "applied_human_review_decision_count": len(applied_decision_models),
            "rejected_human_review_decision_count": len(rejected_decision_models),
            "human_review_audit_entry_count": len(audit_models),
            "conflict_count": len(conflict_models),
            "human_review_item_count": len(human_review_items),
            "contains_synthetic_fixture_data": contains_fixture,
            "llm_used": llm_used,
            "package_version": policy.package_version,
        },
    )
    package_metadata = _build_package_metadata(
        state, policy, contains_fixture, fixture_notice, trace, llm_used
    )

    package = FinalDataPackage(
        final_dataset=final_dataset,
        final_dataset_pre_quality_gate=final_dataset_pre_quality_gate,
        final_dataset_post_review=final_dataset_post_review,
        quarantined_records=quarantined_record_models,
        pending_review_records=pending_review_record_models,
        non_primary_observations=non_primary_observation_models,
        final_case_dataset=final_case_dataset_models,
        global_outbreak_event_dataset=global_outbreak_event_models,
        regional_surveillance_dataset=regional_surveillance_models,
        country_year_aggregate_dataset=country_year_aggregate_models,
        official_alert_dataset=official_alert_models,
        probable_case_dataset=probable_case_dataset_models,
        suspected_case_dataset=suspected_case_dataset_models,
        unspecified_case_dataset=unspecified_case_dataset_models,
        death_dataset=death_dataset_models,
        hospitalization_dataset=hospitalization_dataset_models,
        zero_case_statements=zero_case_statement_models,
        exposure_monitoring_records=exposure_monitoring_models,
        surveillance_summary_records=surveillance_summary_models,
        outbreak_summary_records=outbreak_summary_models,
        context_records=context_record_models,
        best_available_context_records=best_available_context_record_models,
        unclassified_observation_records=unclassified_observation_models,
        observation_type_dataset_summary=observation_type_dataset_summary,
        record_inclusion_decisions=record_inclusion_decisions,
        run_quality_summary=run_quality_summary,
        final_dataset_quality_summary=final_dataset_quality_summary,
        task_acceptance_contract=task_acceptance_contract,
        task_evidence_contract=task_evidence_contract,
        evidence_strategy_plan=evidence_strategy_plan,
        source_triage_results=source_triage_results,
        evidence_chunks=evidence_chunks,
        chunk_relevance_assessments=chunk_relevance_assessments,
        record_task_fit_assessments=record_task_fit_assessments,
        direct_fast_path_summary=direct_fast_path_summary,
        metric_extraction_plan=metric_extraction_plan,
        metric_row_extraction_audit=metric_row_extraction_audit,
        collection_decision_summary=collection_decision_summary,
        records_excluded_by_human_review=records_excluded_models,
        source_registry=included_registry,
        source_identity_assessments=source_identity_models,
        source_identity_summary=state.get("source_identity_summary") or {},
        official_coverage_candidates=official_coverage_candidates,
        source_coverage_requirements=source_coverage_requirements,
        source_coverage_audit=source_coverage_audit,
        target_official_fetch_plan=target_official_fetch_plan,
        must_fetch_sources=must_fetch_sources,
        fetch_failures_blocking=fetch_failures_blocking,
        linked_events=linked_event_models,
        event_clusters=event_cluster_models,
        duplicate_clusters=duplicate_cluster_models,
        validation_cases=validation_case_models,
        validation_comparisons=validation_comparison_models,
        validation_results=validation_result_models,
        validation_summary=state.get("validation_summary") or {},
        trusted_source_validation_summary=state.get(
            "trusted_source_validation_summary"
        )
        or {},
        cross_source_validation_summary=state.get(
            "cross_source_validation_summary"
        )
        or {},
        claims=claim_models,
        claim_comparisons=claim_comparison_models,
        corroborated_events=corroborated_event_models,
        corroboration_summary=corroboration_summary,
        anomaly_results=anomaly_result_models,
        anomaly_summary=state.get("anomaly_summary") or {},
        applied_human_review_decisions=applied_decision_models,
        rejected_human_review_decisions=rejected_decision_models,
        human_review_audit_trail=audit_models,
        human_review_application_summary=state.get(
            "human_review_application_summary"
        )
        or human_review_application_summary,
        conflicts=conflict_models,
        human_review_items=human_review_items,
        excluded_sources=excluded_sources,
        collection_trace=trace,
        package_metadata=package_metadata,
        workflow_summaries=workflow_summaries,
        data_dictionary=data_dictionary,
        provenance_manifest=provenance_manifest,
        export_manifest={},
        export_warnings=(
            ["contains_synthetic_fixture_data"] if contains_fixture else []
        ),
        contains_synthetic_fixture_data=contains_fixture,
        synthetic_fixture_notice=fixture_notice,
    )
    # Export manifest needs the final package; fill it now.
    package.export_manifest = _build_export_manifest(package, policy)

    finalization_summary = _build_finalization_summary(
        package, workflow_summaries, contains_fixture
    )

    return {
        "final_data_package": package.model_dump(),
        "finalization_summary": finalization_summary,
        "final_dataset_pre_quality_gate": [
            record.model_dump() for record in final_dataset_pre_quality_gate
        ],
        "quarantined_records": [
            record.model_dump() for record in quarantined_record_models
        ],
        "pending_review_records": [
            record.model_dump() for record in pending_review_record_models
        ],
        "non_primary_observations": [
            record.model_dump() for record in non_primary_observation_models
        ],
        "final_case_dataset": [
            record.model_dump() for record in final_case_dataset_models
        ],
        "global_outbreak_event_dataset": [
            record.model_dump() for record in global_outbreak_event_models
        ],
        "regional_surveillance_dataset": [
            record.model_dump() for record in regional_surveillance_models
        ],
        "country_year_aggregate_dataset": [
            record.model_dump() for record in country_year_aggregate_models
        ],
        "official_alert_dataset": [
            record.model_dump() for record in official_alert_models
        ],
        "probable_case_dataset": [
            record.model_dump() for record in probable_case_dataset_models
        ],
        "suspected_case_dataset": [
            record.model_dump() for record in suspected_case_dataset_models
        ],
        "unspecified_case_dataset": [
            record.model_dump() for record in unspecified_case_dataset_models
        ],
        "death_dataset": [record.model_dump() for record in death_dataset_models],
        "hospitalization_dataset": [
            record.model_dump() for record in hospitalization_dataset_models
        ],
        "zero_case_statements": [
            record.model_dump() for record in zero_case_statement_models
        ],
        "exposure_monitoring_records": [
            record.model_dump() for record in exposure_monitoring_models
        ],
        "surveillance_summary_records": [
            record.model_dump() for record in surveillance_summary_models
        ],
        "outbreak_summary_records": [
            record.model_dump() for record in outbreak_summary_models
        ],
        "context_records": [record.model_dump() for record in context_record_models],
        "best_available_context_records": [
            record.model_dump() for record in best_available_context_record_models
        ],
        "unclassified_observation_records": [
            record.model_dump() for record in unclassified_observation_models
        ],
        "observation_type_dataset_summary": observation_type_dataset_summary,
        "record_inclusion_decisions": list(record_inclusion_decisions),
        "run_quality_summary": run_quality_summary,
        "final_dataset_quality_summary": final_dataset_quality_summary,
        "direct_collection_summary": direct_collection_summary,
        "collection_decision_summary": collection_decision_summary,
        "task_acceptance_contract": task_acceptance_contract,
        "task_evidence_contract": task_evidence_contract,
        "evidence_strategy_plan": evidence_strategy_plan,
        "source_triage_results": source_triage_results,
        "evidence_chunks": evidence_chunks,
        "chunk_relevance_assessments": chunk_relevance_assessments,
        "record_task_fit_assessments": record_task_fit_assessments,
        "direct_fast_path_summary": direct_fast_path_summary,
        "metric_extraction_plan": metric_extraction_plan,
        "metric_row_extraction_audit": metric_row_extraction_audit,
        "source_coverage_requirements": source_coverage_requirements,
        "source_coverage_audit": source_coverage_audit,
        "final_dataset_post_review": [
            record.model_dump() for record in final_dataset_post_review
        ],
        "records_excluded_by_human_review": [
            record.model_dump() for record in records_excluded_models
        ],
        "applied_human_review_decisions": [
            decision.model_dump() for decision in applied_decision_models
        ],
        "rejected_human_review_decisions": [
            decision.model_dump() for decision in rejected_decision_models
        ],
        "human_review_audit_trail": [entry.model_dump() for entry in audit_models],
        "human_review_application_summary": human_review_application_summary,
        "collection_trace": trace,
    }
