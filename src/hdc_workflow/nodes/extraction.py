"""Structured extraction and schema validation / repair.

Step 7 implemented the deterministic rule-based extractor; Step 14 adds an
optional LLM-based extractor that runs only when `HDC_ENABLE_LLM_EXTRACTION`
is true. Default behavior remains deterministic and offline-safe.

Important: tests monkeypatch `llm_clients.extract_chunk_with_llm` via the
module attribute. Therefore this file imports the module — not the function —
so the patched reference is observed at call time.
"""

from __future__ import annotations

import os
import re
from collections import Counter
from datetime import date, timedelta
from urllib.parse import urlsplit

from .. import llm_clients
from ..source_coverage import (
    build_source_coverage_requirements,
    official_report_key_for_url,
)


def _parse_llm_max_chunks() -> int | None:
    """Read HDC_LLM_MAX_CHUNKS. Return positive int cap or None when unset/invalid."""

    raw = (os.environ.get("HDC_LLM_MAX_CHUNKS") or "").strip()
    if not raw:
        return None
    try:
        value = int(raw)
    except (TypeError, ValueError):
        return None
    return value if value > 0 else None


def _parse_positive_int_env(name: str, default: int) -> int:
    raw = (os.environ.get(name) or "").strip()
    if not raw:
        return default
    try:
        value = int(raw)
    except (TypeError, ValueError):
        return default
    return value if value > 0 else default


def _env_flag(name: str, *, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "y", "on"}


def _collection_mode_from_context(context: dict | None) -> str:
    if isinstance(context, dict):
        for key in ("collection_mode",):
            value = context.get(key)
            if value:
                return str(value)
        for key in ("structured_task", "collection_spec"):
            nested = context.get(key)
            if isinstance(nested, dict) and nested.get("collection_mode"):
                return str(nested["collection_mode"])
    return (os.environ.get("HDC_COLLECTION_MODE") or "standard").strip() or "standard"


def _direct_collection_enabled(context: dict | None) -> bool:
    return _collection_mode_from_context(context) == "direct_collection"


def _first_text(*values: object) -> str | None:
    for value in values:
        text = str(value or "").strip()
        if text:
            return text
    return None


def _task_location_from_context(context: dict | None) -> str | None:
    if not isinstance(context, dict):
        return None
    contract = context.get("task_acceptance_contract")
    structured_task = context.get("structured_task")
    collection_spec = context.get("collection_spec")
    return _first_text(
        contract.get("location") if isinstance(contract, dict) else None,
        structured_task.get("location") if isinstance(structured_task, dict) else None,
        collection_spec.get("geography") if isinstance(collection_spec, dict) else None,
        collection_spec.get("location") if isinstance(collection_spec, dict) else None,
        context.get("task_location"),
    )


def _is_united_states_location(value: str | None) -> bool:
    normalized = re.sub(r"[^a-z]+", " ", str(value or "").lower()).strip()
    return normalized in {
        "united states",
        "united states of america",
        "usa",
        "us",
        "u s",
        "u s a",
    }
from ..config import (
    load_source_role_policy,
    load_llm_structured_extraction_policy,
    load_structured_extraction_policy,
)
from ..disease_relevance import (
    AMBIGUOUS_DISEASE,
    COMPATIBLE,
    INCOMPATIBLE_DISEASE,
    INSUFFICIENT_TEXT,
    TARGET_DISEASE_MATCH,
    assessment_fields,
    assess_chunk_disease_relevance,
    assess_record_disease_compatibility,
    build_disease_relevance_context,
    record_compatibility_fields,
    update_disease_relevance_summary,
)
from ..models import (
    HantavirusRecord,
    HumanReviewItem,
    LLMExtractedRecord,
    LLMExtractionOutput,
    LLMStructuredExtractionPolicy,
    PublicHealthRecord,
    SchemaValidationResult,
    StructuredExtractionPolicy,
)
from ..run_events import emit_workflow_progress
from ..state import DataCollectionState, append_trace

_FIELD_DETECTION_KEYS = (
    "cases_confirmed",
    "cases_probable",
    "cases_suspected",
    "cases_unspecified",
    "deaths",
    "hospitalizations",
    "date_reported",
    "country",
    "subnational_location",
    "virus_or_syndrome",
    "pathogen_or_syndrome",
)

# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------


def _lower(text: str | None) -> str:
    return (text or "").lower()


def _normalize_number(value: str | None) -> float | None:
    if value is None:
        return None
    s = str(value).strip().replace(",", "")
    if not s:
        return None
    try:
        num = float(s)
    except (TypeError, ValueError):
        return None
    if num < 0:
        return None
    return num


def _detect_virus_or_syndrome(
    text: str,
    policy: StructuredExtractionPolicy,
) -> str | None:
    lowered = _lower(text)
    for canonical_key, terms in policy.virus_or_syndrome_terms.items():
        for term in terms:
            if not term:
                continue
            if term.lower() in lowered:
                return canonical_key
    return None


def _canonical_disease_name(value: str | None) -> str | None:
    if value is None:
        return None
    lowered = str(value).strip().lower()
    if not lowered:
        return None
    if lowered in {
        "hantavirus",
        "hantavirus disease",
        "hps",
        "hantavirus pulmonary syndrome",
    }:
        return "Hantavirus disease"
    if lowered in {"covid", "covid-19", "covid 19", "sars-cov-2"}:
        return "COVID-19"
    if lowered in {"dengue", "dengue fever", "denv", "dengue virus"}:
        return "Dengue"
    return str(value).strip()


def _build_extraction_context(
    state: DataCollectionState | None,
    policy: StructuredExtractionPolicy,
) -> dict:
    state = state or {}
    structured_task = state.get("structured_task") or {}
    collection_spec = state.get("collection_spec") or {}
    disease_intelligence = state.get("disease_intelligence") or {}
    explicit_disease_value = (
        disease_intelligence.get("disease_standard_name")
        or structured_task.get("disease")
        or collection_spec.get("disease")
    )

    disease_standard_name = _canonical_disease_name(
        explicit_disease_value or policy.default_disease
    ) or policy.default_disease

    terms: list[str] = []
    for key in ("disease_input", "disease_standard_name"):
        value = disease_intelligence.get(key)
        if isinstance(value, str):
            terms.append(value)
    for key in ("aliases", "abbreviations", "pathogen_terms", "syndrome_terms"):
        values = disease_intelligence.get(key) or []
        if isinstance(values, list):
            terms.extend(str(v) for v in values if v)
    for value in (structured_task.get("disease"), collection_spec.get("disease")):
        if value:
            terms.append(str(value))

    pathogen_terms = [
        str(v)
        for key in ("pathogen_terms", "abbreviations", "syndrome_terms")
        for v in (disease_intelligence.get(key) or [])
        if v
    ]
    if disease_standard_name == "COVID-19":
        terms.extend(["COVID-19", "SARS-CoV-2"])
        pathogen_terms.extend(["SARS-CoV-2", "COVID-19"])
    elif disease_standard_name == "Dengue":
        terms.extend(["dengue", "DENV", "dengue virus"])
        pathogen_terms.extend(["DENV", "dengue virus", "dengue"])
    elif disease_standard_name == "Hantavirus disease":
        terms.extend(["hantavirus", "HPS", "Sin Nombre virus"])

    source_registry_by_id = {
        str(row.get("source_id")): row
        for row in (state.get("source_registry") or [])
        if isinstance(row, dict) and row.get("source_id")
    }
    official_report_key_by_source_id: dict[str, str] = {}
    for source_id, row in source_registry_by_id.items():
        key = official_report_key_for_url(row.get("canonical_url") or row.get("url"))
        if key:
            official_report_key_by_source_id[source_id] = key
    must_fetch_source_ids = {
        str(row.get("source_id"))
        for row in (state.get("must_fetch_sources") or [])
        if isinstance(row, dict) and row.get("source_id")
    }
    must_fetch_source_ids.update(
        str(source_id)
        for source_id, row in source_registry_by_id.items()
        if isinstance(row, dict) and row.get("must_fetch") is True
    )
    documents_by_source_id: dict[str, list[dict]] = {}
    for document in state.get("documents") or []:
        if not isinstance(document, dict):
            continue
        source_id = document.get("source_id")
        if source_id:
            documents_by_source_id.setdefault(str(source_id), []).append(document)

    seen: set[str] = set()
    disease_terms = [
        term
        for term in terms
        if term and not (term.lower() in seen or seen.add(term.lower()))
    ]
    seen_pathogen: set[str] = set()
    pathogen_terms = [
        term
        for term in pathogen_terms
        if term
        and not (term.lower() in seen_pathogen or seen_pathogen.add(term.lower()))
    ]

    return {
        "collection_mode": (
            structured_task.get("collection_mode")
            or collection_spec.get("collection_mode")
            or os.environ.get("HDC_COLLECTION_MODE")
            or "standard"
        ),
        "structured_task": {
            "disease": disease_standard_name if explicit_disease_value else None,
            "location": structured_task.get("location"),
            "start_date": structured_task.get("start_date"),
            "end_date": structured_task.get("end_date"),
            "collection_mode": structured_task.get("collection_mode"),
        },
        "collection_spec": {
            "disease": disease_standard_name if explicit_disease_value else None,
            "geography": structured_task.get("location")
            or collection_spec.get("geography"),
            "time_window": collection_spec.get("time_window")
            or structured_task.get("start_date")
            or structured_task.get("end_date"),
            "target_population": collection_spec.get("target_population")
            or "humans",
            "collection_mode": collection_spec.get("collection_mode"),
        },
        "disease_intelligence": {
            "disease_standard_name": (
                disease_standard_name if explicit_disease_value else None
            ),
            "aliases": disease_terms,
            "pathogen_terms": pathogen_terms,
            "syndrome_terms": disease_terms,
        },
        "disease_standard_name": disease_standard_name,
        "disease_terms": disease_terms,
        "pathogen_terms": pathogen_terms,
        "target_population": collection_spec.get("target_population") or "humans",
        "task_location": structured_task.get("location") or collection_spec.get("geography"),
        "time_window": collection_spec.get("time_window")
        or structured_task.get("start_date")
        or structured_task.get("end_date"),
        "target_fields": list(structured_task.get("target_fields") or []),
        "task_acceptance_contract": state.get("task_acceptance_contract") or {},
        "is_hantavirus": disease_standard_name == "Hantavirus disease",
        "must_fetch_source_ids": sorted(must_fetch_source_ids),
        "source_registry_by_id": source_registry_by_id,
        "official_report_key_by_source_id": official_report_key_by_source_id,
        "documents_by_source_id": documents_by_source_id,
        "source_coverage_audit": state.get("source_coverage_audit") or {},
    }


def _chunk_with_task_context(chunk: dict, context: dict | None) -> dict:
    updated = dict(chunk)
    contract = (context or {}).get("task_acceptance_contract") or {}
    if contract:
        updated["task_acceptance_contract"] = contract
        updated["record_acceptance_rules"] = list(
            contract.get("record_acceptance_rules") or []
        )
        updated["context_or_quarantine_rules"] = list(
            contract.get("context_or_quarantine_rules") or []
        )
    return updated


def _metric_row_batch_size() -> int:
    return _parse_positive_int_env("HDC_METRIC_ROW_BATCH_SIZE", 8)


def _direct_min_target_metric_records() -> int:
    return _parse_positive_int_env("HDC_DIRECT_MIN_TARGET_METRIC_RECORDS", 6)


def _direct_text_fallback_after_row_extraction_enabled() -> bool:
    return _env_flag(
        "HDC_DIRECT_ENABLE_TEXT_FALLBACK_AFTER_ROW_EXTRACTION",
        default=False,
    )


def _chunk_is_metric_row(chunk: dict) -> bool:
    return str(chunk.get("chunk_kind") or "").lower() == "metric_row"


def _metric_row_key(chunk: dict) -> tuple[str, str]:
    return (
        str(chunk.get("source_id") or "unknown"),
        str(chunk.get("table_id") or "table"),
    )


def _metric_row_id(chunk: dict, fallback_index: int) -> str:
    return str(
        chunk.get("row_id")
        or chunk.get("chunk_id")
        or f"metric_row_{fallback_index}"
    )


def _numeric_tokens(text: str) -> set[str]:
    tokens: set[str] = set()
    for match in re.findall(r"-?\d+(?:,\d{3})*(?:\.\d+)?%?", str(text or "")):
        compact = match.replace(",", "")
        tokens.add(compact)
        if compact.endswith("%"):
            tokens.add(compact[:-1])
    return {token for token in tokens if token}


def _make_metric_row_batch_chunk(
    rows: list[dict],
    *,
    batch_index: int,
) -> dict:
    first = rows[0]
    source_id = str(first.get("source_id") or "unknown")
    table_id = str(first.get("table_id") or "table")
    metric_rows: list[dict] = []
    row_quote_by_id: dict[str, str] = {}
    row_chunk_id_by_id: dict[str, str] = {}
    row_metadata_by_id: dict[str, dict] = {}
    text_lines: list[str] = []
    for index, row in enumerate(rows, start=1):
        row_id = _metric_row_id(row, index)
        row_quote = str(row.get("row_quote") or row.get("text") or "")
        metric_rows.append(
            {
                "row_id": row_id,
                "chunk_id": row.get("chunk_id"),
                "text": row.get("text"),
                "row_quote": row_quote,
                "table_id": row.get("table_id"),
                "source_id": row.get("source_id"),
                "source_column_label": row.get("source_column_label"),
                "metric_column_label": row.get("metric_column_label"),
                "source_column_labels": list(row.get("source_column_labels") or []),
                "table_header": row.get("table_header"),
                "heading_context": row.get("heading_context"),
                "row_context_type": row.get("row_context_type"),
                "reporting_period_start": row.get("reporting_period_start"),
                "reporting_period_end": row.get("reporting_period_end"),
                "reporting_period_label": row.get("reporting_period_label"),
            }
        )
        row_quote_by_id[row_id] = row_quote
        if row.get("chunk_id"):
            row_chunk_id_by_id[row_id] = str(row.get("chunk_id"))
        row_metadata_by_id[row_id] = {
            key: row.get(key)
            for key in (
                "chunk_id",
                "chunk_kind",
                "data_types",
                "context_types",
                "contains_target_data",
                "disease_relevance_status",
                "extraction_eligible_for_task_disease",
                "presence_reason",
                "table_id",
                "row_id",
                "row_quote",
                "source_column_labels",
                "source_column_label",
                "metric_column_label",
                "table_header",
                "heading_context",
                "row_context_type",
                "reporting_period_start",
                "reporting_period_end",
                "reporting_period_label",
                "period_basis",
            )
        }
        row_metadata_by_id[row_id]["row_numeric_tokens"] = sorted(
            _numeric_tokens(row_quote or row.get("text") or "")
        )
        text_lines.append(f"[{row_id}] {row.get('text') or row_quote}")
    batch = dict(first)
    batch.update(
        {
            "chunk_id": f"batch_{source_id}_{table_id}_{batch_index}",
            "chunk_kind": "metric_row_batch",
            "text": "\n".join(text_lines),
            "metric_rows": metric_rows,
            "row_quote_by_id": row_quote_by_id,
            "row_chunk_id_by_id": row_chunk_id_by_id,
            "row_metadata_by_id": row_metadata_by_id,
            "metric_row_batch_size": len(rows),
            "context_types": sorted(
                set(
                    [
                        *(first.get("context_types") or []),
                        "metric_row_batch",
                    ]
                )
            ),
        }
    )
    return batch


def _clean_metric_cell_text(value: str | None) -> str:
    text = re.sub(r"[*_`]+", "", str(value or ""))
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _pipe_table_cells(row_text: str | None) -> list[str]:
    text = str(row_text or "").strip()
    if "|" not in text:
        return []
    cells = [_clean_metric_cell_text(cell) for cell in text.strip("|").split("|")]
    return [cell for cell in cells if cell]


def _parse_metric_cell_value(cell: str) -> tuple[float | None, float | None]:
    text = _clean_metric_cell_text(cell)
    count_match = re.search(r"(-?\d[\d,]*(?:\.\d+)?)", text)
    percent_match = re.search(r"\((-?\d[\d,]*(?:\.\d+)?)\s*%\)", text)
    if not percent_match:
        percent_match = re.search(r"(-?\d[\d,]*(?:\.\d+)?)\s*%", text)

    def _to_float(match: re.Match[str] | None) -> float | None:
        if not match:
            return None
        try:
            return float(match.group(1).replace(",", ""))
        except (TypeError, ValueError):
            return None

    return _to_float(count_match), _to_float(percent_match)


def _metric_row_column_labels(row: dict, value_count: int) -> list[str]:
    raw = row.get("source_column_labels") or row.get("column_labels") or []
    labels: list[str] = []
    if isinstance(raw, list):
        labels = [str(item).strip() for item in raw if str(item or "").strip()]
    elif isinstance(raw, str) and raw.strip():
        labels = [part.strip() for part in re.split(r"\s*\|\s*|\s*,\s*", raw) if part.strip()]
    if len(labels) >= value_count:
        return labels[:value_count]
    if _can_infer_weekly_clinical_lab_comparison_columns(row, value_count):
        return ["Current Week", "Previous Week"]
    if value_count == 1:
        fallback = row.get("source_column_label") or row.get("metric_column_label")
        return [
            str(fallback).strip()
            if fallback and not _is_weak_column_label(str(fallback))
            else "Current Week"
        ]
    defaults = [f"Column {index + 1}" for index in range(value_count)]
    while len(defaults) < value_count:
        defaults.append(f"Column {len(defaults) + 1}")
    merged = labels + defaults[len(labels) :]
    return merged[:value_count]


def _can_infer_weekly_clinical_lab_comparison_columns(
    row: dict,
    value_count: int,
) -> bool:
    """Infer current/previous week only for narrow weekly lab comparison rows.

    Some public-health pages expose table rows without the original header, but
    keep a section heading such as "Results of tests from Clinical Laboratories".
    In that recurring surveillance layout, two numeric columns represent the
    current reporting week and the previous week. Keep this deliberately narrow
    so unrelated two-column tables remain quarantined as ambiguous.
    """

    if value_count != 2:
        return False
    if not (row.get("reporting_period_start") and row.get("reporting_period_end")):
        return False
    context_text = " ".join(
        str(value or "")
        for value in (
            row.get("heading_context"),
            row.get("table_header"),
            row.get("table_id"),
            row.get("title"),
            row.get("reporting_period_label"),
        )
    ).lower()
    if "clinical laborator" not in context_text:
        return False
    if any(
        marker in context_text
        for marker in (
            "season to date",
            "season-to-date",
            "cumulative",
            "public health laborator",
        )
    ):
        return False
    cells = _pipe_table_cells(str(row.get("row_quote") or row.get("text") or ""))
    if len(cells) != 3:
        return False
    row_label = cells[0].lower()
    return bool(
        any(term in row_label for term in ("specimen", "test", "positive", "percent"))
        and any(re.search(r"\d", cell) for cell in cells[1:])
    )


def _deterministic_metric_payloads_from_row(row: dict) -> list[dict]:
    row_text = str(row.get("row_quote") or row.get("text") or "")
    cells = _pipe_table_cells(row_text)
    if len(cells) < 2:
        return []
    label = cells[0]
    label_lower = label.lower()
    value_cells = cells[1:]
    column_labels = _metric_row_column_labels(row, len(value_cells))
    payloads: list[dict] = []

    positive_specimen_row = (
        "positive" in label_lower
        and ("specimen" in label_lower or "test" in label_lower)
    )
    tested_specimen_row = (
        ("specimen" in label_lower or "test" in label_lower)
        and ("tested" in label_lower or "performed" in label_lower)
        and "positive" not in label_lower
    )
    if not positive_specimen_row and not tested_specimen_row:
        return []
    parsed_cells = [
        (*_parse_metric_cell_value(cell), cell)
        for cell in value_cells
    ]
    has_percent = any(percent_value is not None for _, percent_value, _ in parsed_cells)
    has_count = any(count_value is not None for count_value, _, _ in parsed_cells)
    if not has_percent and not (
        tested_specimen_row
        and has_count
        and _can_infer_weekly_clinical_lab_comparison_columns(row, len(value_cells))
    ):
        return []

    for index, (count_value, percent_value, _cell) in enumerate(parsed_cells):
        column_label = column_labels[index] if index < len(column_labels) else None
        if tested_specimen_row and count_value is not None:
            payloads.append(
                {
                    "metric_name": "Number of specimens tested",
                    "metric_value": count_value,
                    "metric_unit": "count",
                    "metric_category": "lab_test_count",
                    "tests_total": count_value,
                    "source_column_label": column_label,
                    "source_row_id": _metric_row_id(row, 1),
                    "observation_type": "surveillance_summary",
                    "observation_types": ["surveillance_summary"],
                    "primary_case_dataset_eligible": False,
                    "count_semantics": "laboratory test count",
                    "statistical_count_type": "newly_reported",
                }
            )
        if positive_specimen_row and count_value is not None:
            payloads.append(
                {
                    "metric_name": "Number of positive specimens",
                    "metric_value": count_value,
                    "metric_unit": "count",
                    "metric_category": "lab_positive_count",
                    "tests_positive": count_value,
                    "source_column_label": column_label,
                    "source_row_id": _metric_row_id(row, 1),
                    "observation_type": "surveillance_summary",
                    "observation_types": ["surveillance_summary"],
                    "primary_case_dataset_eligible": False,
                    "count_semantics": "laboratory positive specimen count",
                    "statistical_count_type": "newly_reported",
                }
            )
        if positive_specimen_row and percent_value is not None:
            payloads.append(
                {
                    "metric_name": "Percent positive specimens",
                    "metric_value": percent_value,
                    "metric_unit": "percent",
                    "metric_category": "lab_positivity_percent",
                    "metric_denominator": "specimens_tested",
                    "positivity_rate": percent_value,
                    "source_column_label": column_label,
                    "source_row_id": _metric_row_id(row, 1),
                    "observation_type": "surveillance_summary",
                    "observation_types": ["surveillance_summary"],
                    "primary_case_dataset_eligible": False,
                    "count_semantics": "laboratory positivity percent",
                    "statistical_count_type": "newly_reported",
                }
            )
    return payloads


def _deterministic_metric_row_records(
    row: dict,
    *,
    start_index: int,
    llm_policy: LLMStructuredExtractionPolicy,
    settings: dict,
    context: dict | None,
) -> list[PublicHealthRecord]:
    payloads = _deterministic_metric_payloads_from_row(row)
    if not payloads:
        return []
    batch_chunk = _make_metric_row_batch_chunk([row], batch_index=0)
    records: list[PublicHealthRecord] = []
    for offset, payload in enumerate(payloads):
        llm_record = LLMExtractedRecord(**payload)
        record = _build_record_from_llm_output(
            llm_record,
            batch_chunk,
            start_index + offset,
            llm_policy,
            settings,
            context,
        )
        if record is None:
            continue
        warnings = list(record.semantic_warnings or [])
        if "deterministic_metric_row_splitter" not in warnings:
            warnings.append("deterministic_metric_row_splitter")
        record = record.model_copy(
            update={
                "llm_used": False,
                "llm_model": None,
                "llm_provider": None,
                "extraction_mode": "deterministic",
                "extraction_method": "deterministic_metric_row_splitter",
                "extraction_reason": (
                    "Deterministic metric-row split from explicit table row"
                ),
                "semantic_warnings": warnings,
                "extraction_warnings": warnings,
            }
        )
        records.append(record)
    return records


def _record_task_fit_assessments(
    records: list[dict],
    context: dict | None,
) -> list[dict]:
    contract = (context or {}).get("task_acceptance_contract") or {}
    task_location = str(contract.get("location") or (context or {}).get("task_location") or "")
    task_location_lower = task_location.lower()
    assessments: list[dict] = []
    for record in records:
        text = " ".join(
            str(record.get(key) or "")
            for key in (
                "subnational_location",
                "geographic_scope",
                "country",
                "evidence_quote",
                "source_title",
            )
        ).lower()
        geography_fit = (
            "matches_task_location"
            if not task_location_lower or task_location_lower in text
            else "needs_final_gate_review"
        )
        has_date = any(
            record.get(key)
            for key in (
                "date_reported",
                "date_anchor",
                "event_start_date",
                "reporting_period",
                "metric_period_start",
                "metric_period_end",
            )
        )
        has_count = any(
            record.get(key) not in (None, "")
            for key in (
                "cases_confirmed",
                "cases_probable",
                "cases_suspected",
                "cases_unspecified",
                "deaths",
                "hospitalizations",
                "tests_positive",
                "positivity_rate",
                "cumulative_count",
                "new_count",
                "metric_value",
            )
        )
        assessments.append(
            {
                "record_id": record.get("record_id"),
                "source_id": record.get("source_id"),
                "record_task_fit_agent": "record_task_fit_assessor",
                "contract_version": contract.get("contract_version"),
                "geography_fit": geography_fit,
                "date_fit": "has_date_or_period" if has_date else "missing_date_anchor",
                "count_semantics_fit": (
                    "has_interpretable_metric"
                    if has_count
                    else "missing_interpretable_metric"
                ),
                "record_acceptance_rules": list(
                    contract.get("record_acceptance_rules") or []
                ),
                "context_or_quarantine_rules": list(
                    contract.get("context_or_quarantine_rules") or []
                ),
            }
        )
    return assessments


def _detect_disease_alias_used(text: str, context: dict | None) -> str | None:
    lowered = _lower(text)
    for term in (context or {}).get("disease_terms") or []:
        if term and term.lower() in lowered:
            return term
    return None


def _detect_pathogen_or_syndrome(text: str, context: dict | None) -> str | None:
    lowered = _lower(text)
    for term in (context or {}).get("pathogen_terms") or []:
        if term and term.lower() in lowered:
            canonical = _canonical_disease_name(term)
            if canonical in {"COVID-19", "Dengue"} and term.lower() not in {
                "sars-cov-2",
                "denv",
                "dengue virus",
            }:
                return canonical
            return term
    return None


_ISO_DATE_RE = re.compile(r"\b(20\d{2}-\d{2}-\d{2})\b")
_YEAR_RE = re.compile(r"\b(20\d{2})\b")


def _extract_year_or_date(
    text: str,
    policy: StructuredExtractionPolicy,
) -> str | None:
    if not text:
        return None
    iso = _ISO_DATE_RE.search(text)
    if iso:
        return iso.group(1)
    year_start = int(policy.date_patterns.get("year_range_start", 2020))
    year_end = int(policy.date_patterns.get("year_range_end", 2026))
    for year in _YEAR_RE.findall(text):
        if year_start <= int(year) <= year_end:
            return year
    return None


# Country / location patterns. Order matters — longer / more specific first.
_LOCATION_PATTERNS: list[tuple[re.Pattern, tuple[str | None, str | None]]] = [
    (re.compile(r"\bin\s+the\s+United\s+States\b", re.IGNORECASE), ("United States of America", None)),
    (re.compile(r"\bin\s+United\s+States\b", re.IGNORECASE), ("United States of America", None)),
    (re.compile(r"\bin\s+USA\b"), ("United States of America", None)),
    (re.compile(r"\bin\s+New\s+Mexico\b", re.IGNORECASE), ("United States of America", "New Mexico")),
    (re.compile(r"\bNew\s+York\s+City\b|\bNYC\b", re.IGNORECASE), ("United States of America", "New York City")),
    (re.compile(r"\bNew\s+York\b", re.IGNORECASE), ("United States of America", "New York")),
    (re.compile(r"\bFlorida\b", re.IGNORECASE), ("United States of America", "Florida")),
    (re.compile(r"\bin\s+China\b", re.IGNORECASE), ("China", None)),
    (re.compile(r"\bin\s+Chile\b", re.IGNORECASE), ("Chile", None)),
    (re.compile(r"\bin\s+Argentina\b", re.IGNORECASE), ("Argentina", None)),
    (re.compile(r"\bin\s+Europe\b", re.IGNORECASE), (None, "Europe")),
    (re.compile(r"\bin\s+Germany\b", re.IGNORECASE), ("Germany", None)),
    (re.compile(r"\bin\s+Sweden\b", re.IGNORECASE), ("Sweden", None)),
    (re.compile(r"\bin\s+Finland\b", re.IGNORECASE), ("Finland", None)),
    (re.compile(r"\bin\s+France\b", re.IGNORECASE), ("France", None)),
    (re.compile(r"\bin\s+Spain\b", re.IGNORECASE), ("Spain", None)),
]
# Generic "Country X" / "Country Y" style placeholders (uppercase token).
_COUNTRY_X_RE = re.compile(r"\bin\s+(Country\s+[A-Z][\w-]*)\b")


def _extract_country_or_location(text: str) -> tuple[str | None, str | None]:
    if not text:
        return None, None
    for pattern, result in _LOCATION_PATTERNS:
        if pattern.search(text):
            return result
    m = _COUNTRY_X_RE.search(text)
    if m:
        return m.group(1), None
    return None, None


# ---------------------------------------------------------------------------
# Case + death extraction
# ---------------------------------------------------------------------------


# "12 ... cases" — up to 5 short tokens between the number and "case(s)".
_CASE_NUMERIC_RE = re.compile(
    r"(?P<num>\d+(?:,\d{3})*(?:\.\d+)?)\s+"
    r"(?P<between>(?:[\w-]+\s+){0,5})?"
    r"cases?\b",
    re.IGNORECASE,
)
# "(confirmed/probable/suspected/laboratory-confirmed) cases?: 12"  OR  "cases: 12"
_CASE_COLON_RE = re.compile(
    r"(?P<prefix>(?:laboratory-?\s*)?confirmed\s+cases?"
    r"|probable\s+cases?"
    r"|suspected\s+cases?"
    r"|cases?)\s*:\s*"
    r"(?P<num>\d+(?:,\d{3})*(?:\.\d+)?)",
    re.IGNORECASE,
)


def _classify_case_bucket(prefix_or_between: str) -> str:
    lowered = prefix_or_between.lower()
    if "confirmed" in lowered or "laboratory" in lowered:
        return "cases_confirmed"
    if "probable" in lowered:
        return "cases_probable"
    if "suspected" in lowered:
        return "cases_suspected"
    return "cases_unspecified"


_BUCKET_TO_LABEL = {
    "cases_confirmed": "confirmed",
    "cases_probable": "probable",
    "cases_suspected": "suspected",
    "cases_unspecified": "unspecified",
}


def _extract_case_counts(
    text: str,
    policy: StructuredExtractionPolicy,  # noqa: ARG001 — reserved for future LLM step
) -> dict:
    result = {
        "cases_confirmed": None,
        "cases_probable": None,
        "cases_suspected": None,
        "cases_unspecified": None,
        "case_definition": None,
    }
    if not text:
        return result

    ordered_labels: list[str] = []

    for m in _CASE_NUMERIC_RE.finditer(text):
        num = _normalize_number(m.group("num"))
        if num is None:
            continue
        between = m.group("between") or ""
        bucket = _classify_case_bucket(between)
        if result[bucket] is None:
            result[bucket] = num
            ordered_labels.append(_BUCKET_TO_LABEL[bucket])

    for m in _CASE_COLON_RE.finditer(text):
        num = _normalize_number(m.group("num"))
        if num is None:
            continue
        bucket = _classify_case_bucket(m.group("prefix"))
        if result[bucket] is None:
            result[bucket] = num
            ordered_labels.append(_BUCKET_TO_LABEL[bucket])

    if ordered_labels:
        seen: set[str] = set()
        unique = [lbl for lbl in ordered_labels if not (lbl in seen or seen.add(lbl))]
        result["case_definition"] = ",".join(unique)
    return result


def _extract_deaths(
    text: str,
    policy: StructuredExtractionPolicy,
) -> float | None:
    if not text:
        return None
    keywords = [k for k in policy.death_keywords if k and k != "died"]
    if not keywords:
        return None
    pattern = re.compile(
        rf"(?P<num>\d+(?:,\d{{3}})*(?:\.\d+)?)\s+(?:[\w-]+\s+){{0,3}}"
        rf"(?:{'|'.join(re.escape(k) for k in keywords)})\b",
        re.IGNORECASE,
    )
    m = pattern.search(text)
    if m:
        return _normalize_number(m.group("num"))

    colon_pattern = re.compile(
        rf"(?:{'|'.join(re.escape(k) for k in keywords)})\s*:\s*"
        rf"(?P<num>\d+(?:,\d{{3}})*(?:\.\d+)?)",
        re.IGNORECASE,
    )
    m = colon_pattern.search(text)
    if m:
        return _normalize_number(m.group("num"))
    return None


_HOSPITALIZATION_NUMERIC_RE = re.compile(
    r"(?P<num>\d+(?:,\d{3})*(?:\.\d+)?)\s+"
    r"(?:[\w-]+\s+){0,3}hospitali[sz]ations?\b",
    re.IGNORECASE,
)
_HOSPITALIZATION_COLON_RE = re.compile(
    r"hospitali[sz]ations?\s*:\s*"
    r"(?P<num>\d+(?:,\d{3})*(?:\.\d+)?)",
    re.IGNORECASE,
)
_CORE_CASE_BURDEN_RE = re.compile(
    r"(?:\b(?:reported|notified|recorded|confirmed)\s+)?"
    r"(?P<num>\d+(?:,\d{3})*(?:\.\d+)?)\s+"
    r"(?:[\w-]+\s+){0,6}?"
    r"(?P<label>(?:tb|tuberculosis|measles|influenza|flu|covid-19|covid)\s+)?"
    r"cases?\b",
    re.IGNORECASE,
)
_CORE_INCIDENCE_RATE_RE = re.compile(
    r"\bincidence\s+rate(?:\s+(?:was|of|is))?\s+"
    r"(?P<num>\d+(?:,\d{3})*(?:\.\d+)?)\s+"
    r"(?:cases?\s+)?per\s+100,?000(?:\s+(?:persons?|population))?",
    re.IGNORECASE,
)
_CORE_MORTALITY_RATE_RE = re.compile(
    r"\bmortality\s+rate(?:\s+(?:was|of|is))?\s+"
    r"(?P<num>\d+(?:,\d{3})*(?:\.\d+)?)\s+"
    r"(?:deaths?\s+)?per\s+100,?000(?:\s+(?:persons?|population))?",
    re.IGNORECASE,
)
_CORE_METRIC_CONTEXT_TYPES = {
    "narrative_metric",
    "markdown_metric_line",
    "annual_metric",
    "public_health_metric",
}
_CORE_METRIC_DATA_TYPES = {
    "case_count",
    "incidence_rate",
    "mortality_rate",
    "death_count",
    "burden_metric",
}
_EDGE_DEMOGRAPHIC_QUALIFIERS = {
    "unknown",
    "missing",
    "birth origin",
    "race",
    "ethnicity",
    "age",
    "sex",
    "gender",
}


def _extract_hospitalizations(text: str) -> float | None:
    if not text:
        return None
    for pattern in (_HOSPITALIZATION_NUMERIC_RE, _HOSPITALIZATION_COLON_RE):
        m = pattern.search(text)
        if m:
            return _normalize_number(m.group("num"))
    return None


def _chunk_looks_like_core_metric_text(chunk: dict) -> bool:
    context_types = {
        str(value).lower() for value in (chunk.get("context_types") or []) if value
    }
    data_types = {
        str(value).lower() for value in (chunk.get("data_types") or []) if value
    }
    if context_types.intersection(_CORE_METRIC_CONTEXT_TYPES):
        return True
    if data_types.intersection(_CORE_METRIC_DATA_TYPES):
        return True
    return str(chunk.get("chunk_kind") or "").lower() in {
        "narrative_metric",
        "metric_text",
    }


def _core_metric_period_fields(
    chunk: dict,
    context: dict | None,
) -> tuple[str | None, str | None, str | None]:
    start, end, label = _source_period_from_chunk(chunk, context)
    if start and end:
        return start, end, label
    structured = (context or {}).get("structured_task") or {}
    collection = (context or {}).get("collection_spec") or {}
    start = structured.get("start_date") or collection.get("start_date")
    end = structured.get("end_date") or collection.get("end_date") or start
    return (
        str(start) if start else None,
        str(end) if end else None,
        str(label) if label else None,
    )


def _core_metric_location_fields(
    chunk: dict,
    context: dict | None,
) -> tuple[str | None, str | None, str | None]:
    task_location = _task_location_from_context(context)
    country = _first_text(chunk.get("country"))
    geographic_scope = _first_text(
        chunk.get("geographic_scope"),
        chunk.get("subnational_location"),
        country,
        task_location,
    )
    geographic_scope_type = _first_text(chunk.get("geographic_scope_type"))
    if _is_united_states_location(geographic_scope):
        country = country or "United States"
        geographic_scope = "United States"
        geographic_scope_type = geographic_scope_type or "country"
    elif geographic_scope and not geographic_scope_type:
        geographic_scope_type = "country" if geographic_scope == country else "subnational"
    return country, geographic_scope, geographic_scope_type


def _match_has_edge_demographic_context(match: re.Match[str], text: str) -> bool:
    start = max(0, match.start() - 80)
    end = min(len(text), match.end() + 80)
    window = text[start:end].lower()
    return any(marker in window for marker in _EDGE_DEMOGRAPHIC_QUALIFIERS)


def _core_metric_payloads_from_chunk(
    chunk: dict,
    context: dict | None,
) -> list[dict]:
    text = str(chunk.get("row_quote") or chunk.get("text") or "")
    if not text.strip() or not _chunk_looks_like_core_metric_text(chunk):
        return []
    payloads: list[dict] = []
    period_start, period_end, period_label = _core_metric_period_fields(chunk, context)
    period_source = (
        "filled_from_source_reporting_period"
        if period_start and period_end
        else "unresolved"
    )

    case_match = _CORE_CASE_BURDEN_RE.search(text)
    if case_match and not _match_has_edge_demographic_context(case_match, text):
        value = _normalize_number(case_match.group("num"))
        if value is not None:
            payloads.append(
                {
                    "metric_name": "reported case count",
                    "metric_value": value,
                    "metric_unit": "count",
                    "metric_category": "case_count",
                    "count_semantics": "annual public health case aggregate",
                    "statistical_count_type": "annual",
                }
            )

    incidence_match = _CORE_INCIDENCE_RATE_RE.search(text)
    if incidence_match:
        value = _normalize_number(incidence_match.group("num"))
        if value is not None:
            payloads.append(
                {
                    "metric_name": "incidence rate",
                    "metric_value": value,
                    "metric_unit": "per 100,000 population",
                    "metric_category": "incidence_rate",
                    "incidence_rate": value,
                    "metric_denominator": "100,000 population",
                    "count_semantics": "annual public health incidence rate",
                    "statistical_count_type": "annual",
                }
            )

    mortality_match = _CORE_MORTALITY_RATE_RE.search(text)
    if mortality_match:
        value = _normalize_number(mortality_match.group("num"))
        if value is not None:
            payloads.append(
                {
                    "metric_name": "mortality rate",
                    "metric_value": value,
                    "metric_unit": "per 100,000 population",
                    "metric_category": "mortality_rate",
                    "metric_denominator": "100,000 population",
                    "count_semantics": "annual public health mortality rate",
                    "statistical_count_type": "annual",
                }
            )

    if not payloads:
        return []
    for payload in payloads:
        if period_start:
            payload["metric_period_start"] = period_start
        if period_end:
            payload["metric_period_end"] = period_end
            payload["date_reported"] = period_end
        if period_label:
            payload["metric_period_label"] = period_label
            payload["reporting_period"] = period_label
        payload["metric_period_source"] = period_source
    return payloads


# ---------------------------------------------------------------------------
# Table extraction
# ---------------------------------------------------------------------------


def _classify_table_column(header_lower: str) -> str | None:
    if not header_lower:
        return None
    if "confirmed case" in header_lower or header_lower == "confirmed":
        return "cases_confirmed"
    if "probable case" in header_lower or header_lower == "probable":
        return "cases_probable"
    if "suspected case" in header_lower or header_lower == "suspected":
        return "cases_suspected"
    if "case" in header_lower or header_lower == "cases":
        return "cases_unspecified"
    if "death" in header_lower or "fatality" in header_lower:
        return "deaths"
    if "hospitalization" in header_lower or "hospitalisation" in header_lower:
        return "hospitalizations"
    if "country" in header_lower:
        return "country"
    if (
        "location" in header_lower
        or "region" in header_lower
        or "state" in header_lower
        or "province" in header_lower
        or "district" in header_lower
    ):
        return "subnational_location"
    if "year" in header_lower or "date" in header_lower:
        return "date_reported"
    return None


def _extract_from_table_text(
    text: str,
    policy: StructuredExtractionPolicy,  # noqa: ARG001 — reserved
) -> dict | None:
    if not text or "|" not in text:
        return None
    lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
    if len(lines) < 2:
        return None

    header_cells = [c.strip() for c in lines[0].split("|")]
    column_map: dict[str, int] = {}
    for i, header in enumerate(header_cells):
        field = _classify_table_column(header.lower())
        if field and field not in column_map:
            column_map[field] = i
    if not column_map:
        return None

    data_cells = [c.strip() for c in lines[1].split("|")]
    result: dict = {}
    for field, idx in column_map.items():
        if idx >= len(data_cells):
            continue
        value = data_cells[idx]
        if not value:
            continue
        if field in (
            "cases_confirmed",
            "cases_probable",
            "cases_suspected",
            "cases_unspecified",
            "deaths",
            "hospitalizations",
        ):
            num = _normalize_number(value)
            if num is not None:
                result[field] = num
        elif field == "date_reported":
            if re.fullmatch(r"20\d{2}", value):
                result[field] = value
            else:
                result[field] = value
        else:
            result[field] = value
    return result or None


# ---------------------------------------------------------------------------
# Chunk → record
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Step 16: post-extraction semantic guardrails (shared by LLM + rule paths)
# ---------------------------------------------------------------------------


_GENERIC_VIRUS_OR_SYNDROME_VALUES = {
    "hantavirus",
    "hantavirus disease",
    "hantavirus infection",
    "hantaviridae",
    "orthohantavirus",
    "orthohantavirus infection",
}

_CANONICAL_VIRUS_OR_SYNDROME = {
    "hps": "HPS",
    "hfrs": "HFRS",
    "andes virus": "Andes virus",
    "seoul virus": "Seoul virus",
    "sin nombre virus": "Sin Nombre virus",
    "hantaan virus": "Hantaan virus",
    "puumala virus": "Puumala virus",
    "dobrava-belgrade virus": "Dobrava-Belgrade virus",
    "dobrava virus": "Dobrava-Belgrade virus",
}

_REGION_TERMS = {
    "eu/eea": "EU/EEA",
    "eu/eea (28 countries)": "EU/EEA",
    "european union": "EU/EEA",
    "european union/european economic area": "EU/EEA",
    "eea": "EU/EEA",
    "europe": "Europe",
    "americas": "Americas",
    "north america": "North America",
    "south america": "South America",
}

_ALLOWED_STATISTICAL_COUNT_TYPES = {
    "cumulative",
    "annual",
    "newly_reported",
    "historical_total",
    "subset",
    "unknown",
}

_ALLOWED_GEOGRAPHIC_SCOPE_TYPES = {
    "country",
    "subnational",
    "region",
    "multi_country",
    "global",
    "unknown",
}

# Step 16.1.1: LLMs sometimes emit hyphenated / free-text variants for the
# semantic enum fields. Canonicalize them to the internal vocabulary used by
# downstream nodes so e.g. "multi-country" still triggers the regional-scope
# exception in normalization / linking. Mapping is exhaustive enough for the
# real-world variants we have observed; unmapped inputs are surfaced as a
# warning rather than silently dropped.
_GEOGRAPHIC_SCOPE_TYPE_ALIASES: dict[str, str] = {
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

_STATISTICAL_COUNT_TYPE_ALIASES: dict[str, str] = {
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


def _normalize_enum_lookup_key(value: str) -> str:
    """Lowercase + collapse internal whitespace; keep '-' and '_' intact for
    direct alias lookup. Used to find an LLM-emitted value in the alias maps.
    """

    return re.sub(r"\s+", " ", value.strip().lower())


def _canonicalize_geographic_scope_type(
    value: str | None,
) -> tuple[str | None, list[str]]:
    if value is None:
        return None, []
    if not isinstance(value, str):
        return value, []
    stripped = value.strip()
    if not stripped:
        return None, []
    key = _normalize_enum_lookup_key(stripped)
    canonical = _GEOGRAPHIC_SCOPE_TYPE_ALIASES.get(key)
    if canonical is None:
        return stripped, ["unrecognized_geographic_scope_type"]
    if canonical != stripped:
        return canonical, ["canonicalized_geographic_scope_type"]
    return canonical, []


def _canonicalize_statistical_count_type(
    value: str | None,
) -> tuple[str | None, list[str]]:
    if value is None:
        return None, []
    if not isinstance(value, str):
        return value, []
    stripped = value.strip()
    if not stripped:
        return None, []
    key = _normalize_enum_lookup_key(stripped)
    canonical = _STATISTICAL_COUNT_TYPE_ALIASES.get(key)
    if canonical is None:
        return stripped, ["unrecognized_statistical_count_type"]
    if canonical != stripped:
        return canonical, ["canonicalized_statistical_count_type"]
    return canonical, []


def _standardize_disease(
    value: str | None,
) -> tuple[str, list[str]]:
    return _standardize_disease_for_context(value, None)


def _standardize_disease_for_context(
    value: str | None,
    context: dict | None = None,
) -> tuple[str, list[str]]:
    """Standardize disease to the active task disease.

    The legacy no-context behavior remains Hantavirus disease. Stage 8 passes
    context from structured task / disease intelligence so non-hantavirus
    records keep their disease label.
    """

    canonical = (
        _canonical_disease_name((context or {}).get("disease_standard_name"))
        if context
        else None
    ) or "Hantavirus disease"
    warnings: list[str] = []
    if value is None or not isinstance(value, str):
        return canonical, warnings
    input_canonical = _canonical_disease_name(value)
    if input_canonical and input_canonical != canonical:
        warnings.append("standardized_disease_name")
    elif value.strip() != canonical:
        warnings.append("standardized_disease_name")
    return canonical, warnings


def _clean_virus_or_syndrome(
    value: str | None,
) -> tuple[str | None, list[str]]:
    if value is None:
        return None, []
    if not isinstance(value, str):
        return None, []
    stripped = value.strip()
    if not stripped:
        return None, []
    lowered = stripped.lower()
    if lowered in _GENERIC_VIRUS_OR_SYNDROME_VALUES:
        return None, ["removed_generic_virus_or_syndrome"]
    if lowered in _CANONICAL_VIRUS_OR_SYNDROME:
        canonical = _CANONICAL_VIRUS_OR_SYNDROME[lowered]
        return canonical, []
    return stripped, ["unrecognized_virus_or_syndrome_semantics"]


def _standardize_statistical_count_type(
    value: str | None,
    text: str | None,
    aliases: dict[str, list[str]] | None = None,
) -> tuple[str | None, list[str]]:
    """Normalize or infer statistical_count_type from value or chunk text."""

    if isinstance(value, str) and value.strip():
        canonical, w = _canonicalize_statistical_count_type(value)
        if canonical in _ALLOWED_STATISTICAL_COUNT_TYPES:
            return canonical, w
    if text:
        lowered = text.lower()
        # Order matters: more specific first.
        if any(m in lowered for m in ("newly reported", "new cases", "additional cases")):
            return "newly_reported", ["inferred_statistical_count_type_from_text"]
        if any(m in lowered for m in ("of which", "among", "subset")):
            return "subset", ["inferred_statistical_count_type_from_text"]
        if any(
            m in lowered
            for m in (
                "reported through",
                "as of december",
                "as of january",
                "as of february",
                "as of march",
                "as of april",
                "as of may",
                "as of june",
                "as of july",
                "as of august",
                "as of september",
                "as of october",
                "as of november",
                "prior to",
            )
        ):
            return "historical_total", ["inferred_statistical_count_type_from_text"]
        if any(
            m in lowered
            for m in (
                "annual",
                "during 2020",
                "during 2021",
                "during 2022",
                "during 2023",
                "during 2024",
                "during 2025",
                "during 2026",
                "in 2020",
                "in 2021",
                "in 2022",
                "in 2023",
                "in 2024",
                "in 2025",
                "in 2026",
            )
        ):
            return "annual", ["inferred_statistical_count_type_from_text"]
        if any(m in lowered for m in ("cumulative", "total", "through ", "since ")):
            return "cumulative", ["inferred_statistical_count_type_from_text"]
    return None, []


def _standardize_geographic_scope(
    record: dict,
) -> tuple[dict, list[str]]:
    out = dict(record)
    warnings: list[str] = []

    # Step 16.1.1: canonicalize any LLM-emitted scope_type variant (e.g.
    # "multi-country", "national") before downstream nodes inspect it.
    raw_scope_type = out.get("geographic_scope_type")
    canonical_scope_type, scope_type_warnings = _canonicalize_geographic_scope_type(
        raw_scope_type
    )
    if canonical_scope_type != raw_scope_type:
        out["geographic_scope_type"] = canonical_scope_type
    warnings.extend(scope_type_warnings)

    country = out.get("country")
    scope = out.get("geographic_scope")
    scope_type = out.get("geographic_scope_type")
    subnational = out.get("subnational_location")

    if isinstance(country, str) and country.strip():
        lowered = country.strip().lower()
        if lowered in _REGION_TERMS:
            canonical_region = _REGION_TERMS[lowered]
            if not scope:
                out["geographic_scope"] = canonical_region
            if not scope_type:
                # Single-region term like Europe maps to region; aggregates
                # like EU/EEA are multi_country at semantic level.
                out["geographic_scope_type"] = (
                    "multi_country" if canonical_region == "EU/EEA" else "region"
                )
            out["country"] = None
            warnings.append("regional_geographic_scope_not_country")

    # Fill scope from country when country is a single nation.
    if (
        out.get("country")
        and not out.get("geographic_scope")
        and isinstance(out.get("country"), str)
    ):
        out["geographic_scope"] = out["country"]
        if not out.get("geographic_scope_type"):
            out["geographic_scope_type"] = "country"

    if subnational and out.get("country") and not out.get("aggregation_level"):
        out["aggregation_level"] = "subnational"

    if out.get("geographic_scope") and not out.get("geographic_scope_type"):
        out["geographic_scope_type"] = "unknown"

    return out, warnings


def _apply_extraction_semantic_guardrails(
    record_dict: dict,
    chunk: dict | None,
    context: dict | None = None,
) -> dict:
    out = dict(record_dict)
    existing_warnings = list(out.get("semantic_warnings") or [])

    disease, w_d = _standardize_disease_for_context(out.get("disease"), context)
    out["disease"] = disease
    out["disease_standard_name"] = disease
    existing_warnings.extend(w_d)

    if context and not context.get("is_hantavirus"):
        pathogen = out.get("pathogen_or_syndrome")
        if not pathogen and chunk:
            pathogen = _detect_pathogen_or_syndrome(chunk.get("text") or "", context)
        out["pathogen_or_syndrome"] = pathogen
        if not out.get("virus_or_syndrome"):
            out["virus_or_syndrome"] = pathogen
    else:
        vos, w_v = _clean_virus_or_syndrome(out.get("virus_or_syndrome"))
        out["virus_or_syndrome"] = vos
        if not out.get("pathogen_or_syndrome"):
            out["pathogen_or_syndrome"] = vos
        existing_warnings.extend(w_v)

    chunk_text = chunk.get("text") if isinstance(chunk, dict) else None
    sct, w_s = _standardize_statistical_count_type(
        out.get("statistical_count_type"), chunk_text
    )
    out["statistical_count_type"] = sct
    existing_warnings.extend(w_s)

    out, w_g = _standardize_geographic_scope(out)
    existing_warnings.extend(w_g)

    outbreak_text = " ".join(
        str(value or "")
        for value in (
            out.get("count_semantics"),
            out.get("statistical_count_type"),
            out.get("case_definition"),
            out.get("source_section"),
            chunk_text,
        )
    ).lower()
    explicit_outbreak_count = any(
        token in outbreak_text
        for token in (
            "outbreak_count",
            "outbreak count",
            "number of outbreaks",
            "reported outbreaks",
            "outbreaks reported",
            "outbreaks were reported",
        )
    ) or bool(
        re.search(r"\b\d[\d,]*(?:\s+\w+){0,4}\s+outbreaks?\b", outbreak_text)
        or re.search(r"\boutbreaks?\s+(?:reported|total(?:ed)?|count(?:ed)?)\s+\d[\d,]*\b", outbreak_text)
    )
    explicit_case_count = bool(
        re.search(r"\b\d[\d,]*(?:\s+\w+){0,4}\s+(?:cases?|patients?|infections?)\b", outbreak_text)
        or re.search(r"\b(?:cases?|patients?|infections?)\s+(?:reported|total(?:ed)?|count(?:ed)?)\s+\d[\d,]*\b", outbreak_text)
    )
    if (
        out.get("cases_unspecified") is not None
        and explicit_outbreak_count
        and not explicit_case_count
    ):
        outbreak_count = out.get("cases_unspecified")
        if out.get("cumulative_count") is None and out.get("new_count") is None:
            out["cumulative_count"] = outbreak_count
        out["cases_unspecified"] = None
        out["observation_type"] = "outbreak_summary"
        observation_types = list(out.get("observation_types") or [])
        if "outbreak_summary" not in observation_types:
            observation_types.append("outbreak_summary")
        out["observation_types"] = observation_types
        out["primary_case_dataset_eligible"] = False
        if not out.get("count_semantics"):
            out["count_semantics"] = "outbreak_count"
        existing_warnings.append("outbreak_count_not_case_count")

    metric_text = " ".join(
        str(value or "")
        for value in (
            out.get("metric_name"),
            out.get("metric_category"),
            out.get("metric_unit"),
            out.get("metric_denominator"),
            out.get("count_semantics"),
            out.get("statistical_count_type"),
            out.get("source_section"),
            chunk_text,
        )
    ).lower()
    ed_visit_metric = any(
        token in metric_text
        for token in (
            "emergency department",
            "ed visit",
            "ed visits",
            "nssp",
            "emergency room",
            "er visit",
        )
    )
    if ed_visit_metric and out.get("positivity_rate") is not None:
        if out.get("metric_value") is None:
            out["metric_value"] = out.get("positivity_rate")
        if not out.get("metric_name"):
            out["metric_name"] = "nssp_ed_visit_percent"
        if not out.get("metric_category"):
            out["metric_category"] = "ed_visit_percent"
        if not out.get("metric_unit"):
            out["metric_unit"] = "percent"
        if not out.get("metric_denominator"):
            out["metric_denominator"] = "emergency_department_visits"
        out["positivity_rate"] = None
        existing_warnings.append("ed_visit_percent_moved_from_positivity_rate")

    if out.get("metric_value") is None:
        metric_candidates = [
            ("tests_positive", "lab_positive_count", "positive_tests", "count"),
            ("tests_total", "lab_test_count", "tests_total", "count"),
            ("hospitalizations", "hospitalization_count", "hospitalizations", "count"),
            ("icu_admissions", "icu_admission_count", "icu_admissions", "count"),
            ("deaths", "death_count", "deaths", "count"),
            ("cumulative_count", "aggregate_count", "cumulative_count", "count"),
            ("new_count", "new_count", "new_count", "count"),
            ("incidence_rate", "incidence_rate", "incidence_rate", "rate"),
            ("positivity_rate", "lab_positivity_percent", "positivity_rate", "percent"),
        ]
        for field, category, name, unit in metric_candidates:
            if out.get(field) is not None:
                out["metric_value"] = out.get(field)
                out["metric_category"] = out.get("metric_category") or category
                out["metric_name"] = out.get("metric_name") or name
                out["metric_unit"] = out.get("metric_unit") or unit
                if field == "tests_positive" and out.get("tests_total") is not None:
                    out["metric_denominator"] = (
                        out.get("metric_denominator") or "tests_total"
                    )
                break

    if out.get("metric_value") is not None:
        metric_category = str(out.get("metric_category") or "").lower()
        metric_name = str(out.get("metric_name") or "").lower()
        if not out.get("metric_name"):
            out["metric_name"] = out.get("metric_category") or "public_health_metric"
        if not out.get("metric_category"):
            out["metric_category"] = out.get("metric_name")
        if not out.get("metric_unit"):
            if "percent" in metric_category or "percent" in metric_name:
                out["metric_unit"] = "percent"
            elif "rate" in metric_category or "rate" in metric_name:
                out["metric_unit"] = "rate"
            else:
                out["metric_unit"] = "count"
        if not out.get("count_semantics"):
            out["count_semantics"] = out.get("metric_category") or out.get("metric_name")

    out["semantic_warnings"] = existing_warnings
    return out


def _chunk_is_extractable(
    chunk: dict,
    policy: StructuredExtractionPolicy,
    context: dict | None = None,
) -> bool:
    conditions = policy.extractable_chunk_conditions or {}
    if conditions.get("requires_contains_target_data", True):
        if not chunk.get("contains_target_data"):
            return False
    if chunk.get("extraction_eligible_for_task_disease") is False:
        return False
    disease_status = chunk.get("disease_relevance_status")
    if disease_status and disease_status != TARGET_DISEASE_MATCH:
        return False
    allowed_purposes = conditions.get("allowed_fetch_purposes") or []
    if allowed_purposes and chunk.get("fetch_purpose") not in allowed_purposes:
        if not (
            not _direct_collection_enabled(context)
            and chunk.get("fetch_purpose") == "context_grounding"
            and chunk.get("contains_target_data")
        ):
            return False
    allowed_kinds = conditions.get("allowed_chunk_kinds") or []
    if allowed_kinds and (chunk.get("chunk_kind") or "text") not in allowed_kinds:
        return False
    text = chunk.get("text") or ""
    if not text.strip():
        return False
    return True


def _context_only_source_ids(role_policy: dict | None) -> set[str]:
    if not role_policy:
        return set()
    return {str(source_id) for source_id in role_policy.get("context_only_source_ids") or []}


def _chunk_routing_flags(chunk: dict) -> list[str]:
    flags = list(chunk.get("routing_flags") or [])
    metadata = chunk.get("metadata") if isinstance(chunk.get("metadata"), dict) else {}
    for flag in metadata.get("routing_flags") or []:
        if flag not in flags:
            flags.append(flag)
    return flags


def _is_context_only_chunk(chunk: dict, role_policy: dict | None = None) -> bool:
    if chunk.get("source_id") in _context_only_source_ids(role_policy):
        return True
    flags = set(_chunk_routing_flags(chunk))
    if "context_only" in flags or "blocked_from_structured_extraction" in flags:
        return True
    if chunk.get("fetch_purpose") == "context_grounding":
        return True
    return chunk.get("source_role") in {"context_source", "context_only"}


def _chunk_has_explicit_context_only_role(
    chunk: dict,
    role_policy: dict | None = None,
) -> bool:
    if chunk.get("source_id") in _context_only_source_ids(role_policy):
        return True
    flags = set(_chunk_routing_flags(chunk))
    if "context_only" in flags or "blocked_from_structured_extraction" in flags:
        return True
    return chunk.get("source_role") in {"context_source", "context_only"}


def _build_record_from_chunk(
    chunk: dict,
    index: int,
    policy: StructuredExtractionPolicy,
    context: dict | None = None,
) -> PublicHealthRecord | None:
    if not _chunk_is_extractable(chunk, policy, context):
        return None

    text = chunk.get("text") or ""
    chunk_kind = chunk.get("chunk_kind") or "text"

    virus_or_syndrome = _detect_virus_or_syndrome(text, policy)
    pathogen_or_syndrome = _detect_pathogen_or_syndrome(text, context)
    disease_alias_used = _detect_disease_alias_used(text, context)
    date_reported = _extract_year_or_date(text, policy)
    country, subnational_location = _extract_country_or_location(text)
    case_counts = _extract_case_counts(text, policy)
    deaths = _extract_deaths(text, policy)
    hospitalizations = _extract_hospitalizations(text)

    if chunk_kind == "table":
        table_data = _extract_from_table_text(text, policy)
        if table_data:
            if table_data.get("date_reported") is not None:
                date_reported = table_data["date_reported"]
            if table_data.get("country") is not None:
                country = table_data["country"]
            if table_data.get("subnational_location") is not None:
                subnational_location = table_data["subnational_location"]
            for f in ("cases_confirmed", "cases_probable", "cases_suspected", "cases_unspecified"):
                if table_data.get(f) is not None:
                    case_counts[f] = table_data[f]
            if table_data.get("deaths") is not None:
                deaths = table_data["deaths"]
            if table_data.get("hospitalizations") is not None:
                hospitalizations = table_data["hospitalizations"]
            # Refresh case_definition if table populated any case bucket.
            if any(case_counts[b] is not None for b in (
                "cases_confirmed", "cases_probable", "cases_suspected", "cases_unspecified"
            )) and not case_counts.get("case_definition"):
                labels = [
                    _BUCKET_TO_LABEL[b] for b in (
                        "cases_confirmed", "cases_probable", "cases_suspected", "cases_unspecified"
                    ) if case_counts[b] is not None
                ]
                case_counts["case_definition"] = ",".join(labels) or None

    has_any_signal = (
        case_counts["cases_confirmed"] is not None
        or case_counts["cases_probable"] is not None
        or case_counts["cases_suspected"] is not None
        or case_counts["cases_unspecified"] is not None
        or deaths is not None
        or hospitalizations is not None
        or date_reported is not None
        or country is not None
        or subnational_location is not None
    )
    if not has_any_signal:
        return None

    source_id = chunk.get("source_id") or ""
    record_id = f"rec_{source_id}_{index:03d}"

    chunk_confidence = chunk.get("confidence")
    extraction_confidence = (
        float(chunk_confidence) if chunk_confidence is not None else 0.50
    )

    # Apply Step 16 semantic guardrails to the rule-based pre-record so that
    # statistical_count_type / geographic_scope / virus_or_syndrome are kept
    # consistent with the LLM path.
    pre_record = {
        "disease": (context or {}).get("disease_standard_name") or policy.default_disease,
        "disease_standard_name": (context or {}).get("disease_standard_name") or policy.default_disease,
        "disease_alias_used": disease_alias_used,
        "virus_or_syndrome": virus_or_syndrome,
        "pathogen_or_syndrome": pathogen_or_syndrome,
        "country": country,
        "subnational_location": subnational_location,
        "date_reported": date_reported,
        "cases_confirmed": case_counts["cases_confirmed"],
        "cases_probable": case_counts["cases_probable"],
        "cases_suspected": case_counts["cases_suspected"],
        "cases_unspecified": case_counts["cases_unspecified"],
        "deaths": deaths,
        "hospitalizations": hospitalizations,
        "case_definition": case_counts["case_definition"],
    }
    cleaned = _apply_extraction_semantic_guardrails(pre_record, chunk, context)

    required_core = policy.required_core_fields_for_valid_record
    field_values = {
        "disease": cleaned.get("disease") or policy.default_disease,
        "source_url": chunk.get("source_url"),
        "source_type": chunk.get("source_type"),
        "evidence_quote": text,
    }
    missing_fields = [
        f for f in required_core
        if not field_values.get(f) or (isinstance(field_values.get(f), str) and not str(field_values[f]).strip())
    ]

    semantic_warnings = list(cleaned.get("semantic_warnings") or [])
    if _has_any_case_or_death({**cleaned, "hospitalizations": hospitalizations}):
        if not cleaned.get("date_reported"):
            semantic_warnings.append("missing_date_for_count_bearing_record")
        if not (cleaned.get("country") or cleaned.get("subnational_location") or cleaned.get("geographic_scope")):
            semantic_warnings.append("missing_location_for_count_bearing_record")
    compatibility = assess_record_disease_compatibility(
        {
            **cleaned,
            "disease": cleaned.get("disease") or policy.default_disease,
            "evidence_quote": text,
            "source_title": chunk.get("title"),
            "source_url": chunk.get("source_url"),
        },
        _as_disease_relevance_context(context),
    )

    return PublicHealthRecord(
        record_id=record_id,
        disease=cleaned.get("disease") or policy.default_disease,
        disease_standard_name=cleaned.get("disease_standard_name")
        or cleaned.get("disease")
        or policy.default_disease,
        disease_alias_used=cleaned.get("disease_alias_used"),
        virus_or_syndrome=cleaned.get("virus_or_syndrome"),
        pathogen_or_syndrome=cleaned.get("pathogen_or_syndrome"),
        target_population=(context or {}).get("target_population"),
        observation_type=cleaned.get("observation_type"),
        observation_types=list(cleaned.get("observation_types") or []),
        primary_case_dataset_eligible=cleaned.get(
            "primary_case_dataset_eligible"
        ),
        country=cleaned.get("country"),
        subnational_location=cleaned.get("subnational_location"),
        date_reported=cleaned.get("date_reported"),
        event_start_date=None,
        event_end_date=None,
        cases_confirmed=cleaned.get("cases_confirmed"),
        cases_probable=cleaned.get("cases_probable"),
        cases_suspected=cleaned.get("cases_suspected"),
        cases_unspecified=cleaned.get("cases_unspecified"),
        deaths=cleaned.get("deaths"),
        hospitalizations=cleaned.get("hospitalizations"),
        icu_admissions=cleaned.get("icu_admissions"),
        tests_positive=cleaned.get("tests_positive"),
        tests_total=cleaned.get("tests_total"),
        positivity_rate=cleaned.get("positivity_rate"),
        incidence_rate=cleaned.get("incidence_rate"),
        cumulative_count=cleaned.get("cumulative_count"),
        new_count=cleaned.get("new_count"),
        case_definition=cleaned.get("case_definition"),
        source_id=source_id,
        source_url=chunk.get("source_url"),
        source_type=chunk.get("source_type"),
        evidence_quote=text,
        extraction_confidence=extraction_confidence,
        missing_fields=missing_fields,
        schema_status=None,
        provenance_status=None,
        supporting_chunk_id=chunk.get("chunk_id"),
        source_title=chunk.get("title"),
        publisher=chunk.get("publisher"),
        source_role_final=chunk.get("source_role_final"),
        credibility_score=chunk.get("credibility_score"),
        credibility_level=chunk.get("credibility_level"),
        actual_publisher=chunk.get("actual_publisher"),
        actual_publisher_normalized=chunk.get("actual_publisher_normalized"),
        source_type_final=chunk.get("source_type_final"),
        source_independence_group=chunk.get("source_independence_group"),
        claim_support_role=chunk.get("claim_support_role"),
        recommended_source_role=chunk.get("recommended_source_role"),
        recommended_fetch_use=chunk.get("recommended_fetch_use"),
        recommended_extraction_use=chunk.get("recommended_extraction_use"),
        likely_syndicated_or_aggregated=chunk.get(
            "likely_syndicated_or_aggregated"
        ),
        upstream_source_mentions=list(chunk.get("upstream_source_mentions") or []),
        discovery_method=chunk.get("discovery_method"),
        search_provider=chunk.get("search_provider"),
        query_id=chunk.get("query_id"),
        query_used=chunk.get("query_used"),
        document_id=chunk.get("document_id"),
        document_type=chunk.get("document_type"),
        fetch_purpose=chunk.get("fetch_purpose"),
        chunk_kind=chunk_kind,
        data_types=list(chunk.get("data_types") or []),
        context_types=list(chunk.get("context_types") or []),
        extraction_method=policy.extraction_method,
        extraction_reason="deterministic extraction from evidence chunk",
        validation_errors=[],
        repair_actions=[],
        requires_human_review=False,
        statistical_count_type=cleaned.get("statistical_count_type"),
        reporting_period=cleaned.get("reporting_period"),
        as_of_date=cleaned.get("as_of_date"),
        count_semantics=cleaned.get("count_semantics") or cleaned.get("statistical_count_type") or "unspecified",
        aggregation_level=cleaned.get("aggregation_level"),
        geographic_scope=cleaned.get("geographic_scope"),
        geographic_scope_type=cleaned.get("geographic_scope_type"),
        population_scope=cleaned.get("population_scope"),
        source_section=cleaned.get("source_section"),
        semantic_warnings=semantic_warnings,
        extraction_warnings=semantic_warnings,
        **record_compatibility_fields(compatibility),
        record_schema="generic_public_health_record",
        legacy_record_type=(
            "HantavirusRecord" if ((context or {}).get("is_hantavirus") is True) else None
        ),
    )


def _build_core_metric_records_from_chunk(
    chunk: dict,
    start_index: int,
    policy: StructuredExtractionPolicy,
    context: dict | None = None,
) -> list[PublicHealthRecord]:
    payloads = _core_metric_payloads_from_chunk(chunk, context)
    if not payloads:
        return []

    text = str(chunk.get("row_quote") or chunk.get("text") or "")
    source_id = chunk.get("source_id") or ""
    disease = (context or {}).get("disease_standard_name") or policy.default_disease
    virus_or_syndrome = _detect_virus_or_syndrome(text, policy)
    pathogen_or_syndrome = _detect_pathogen_or_syndrome(text, context)
    disease_alias_used = _detect_disease_alias_used(text, context)
    country, geographic_scope, geographic_scope_type = _core_metric_location_fields(
        chunk,
        context,
    )
    if not country and geographic_scope_type == "country":
        country = geographic_scope
    compatibility = assess_record_disease_compatibility(
        {
            "disease": disease,
            "evidence_quote": text,
            "source_title": chunk.get("title"),
            "source_url": chunk.get("source_url"),
        },
        _as_disease_relevance_context(context),
    )
    records: list[PublicHealthRecord] = []
    for offset, payload in enumerate(payloads):
        record_id = f"rec_{source_id}_{start_index + offset:03d}"
        warnings = list(chunk.get("semantic_warnings") or [])
        warnings.append("deterministic_core_metric_text_fallback")
        records.append(
            PublicHealthRecord(
                record_id=record_id,
                disease=disease,
                disease_standard_name=disease,
                disease_alias_used=disease_alias_used,
                virus_or_syndrome=virus_or_syndrome,
                pathogen_or_syndrome=pathogen_or_syndrome,
                target_population=(context or {}).get("target_population"),
                observation_type="surveillance_summary",
                observation_types=["surveillance_summary"],
                primary_case_dataset_eligible=False,
                country=country,
                subnational_location=chunk.get("subnational_location"),
                date_reported=payload.get("date_reported"),
                event_start_date=None,
                event_end_date=None,
                cases_confirmed=None,
                cases_probable=None,
                cases_suspected=None,
                cases_unspecified=None,
                deaths=None,
                hospitalizations=None,
                icu_admissions=None,
                tests_positive=None,
                tests_total=None,
                positivity_rate=None,
                incidence_rate=payload.get("incidence_rate"),
                cumulative_count=None,
                new_count=None,
                metric_name=payload.get("metric_name"),
                metric_value=payload.get("metric_value"),
                metric_unit=payload.get("metric_unit"),
                metric_category=payload.get("metric_category"),
                metric_denominator=payload.get("metric_denominator"),
                metric_period_start=payload.get("metric_period_start"),
                metric_period_end=payload.get("metric_period_end"),
                metric_period_source=payload.get("metric_period_source"),
                metric_period_label=payload.get("metric_period_label"),
                case_definition=None,
                source_id=source_id,
                source_url=chunk.get("source_url"),
                source_type=chunk.get("source_type"),
                evidence_quote=text,
                extraction_confidence=float(chunk.get("confidence") or 0.55),
                missing_fields=[],
                schema_status=None,
                provenance_status=None,
                supporting_chunk_id=chunk.get("chunk_id"),
                source_title=chunk.get("title"),
                publisher=chunk.get("publisher"),
                source_role_final=chunk.get("source_role_final"),
                credibility_score=chunk.get("credibility_score"),
                credibility_level=chunk.get("credibility_level"),
                actual_publisher=chunk.get("actual_publisher"),
                actual_publisher_normalized=chunk.get(
                    "actual_publisher_normalized"
                ),
                source_type_final=chunk.get("source_type_final"),
                source_independence_group=chunk.get("source_independence_group"),
                claim_support_role=chunk.get("claim_support_role"),
                recommended_source_role=chunk.get("recommended_source_role"),
                recommended_fetch_use=chunk.get("recommended_fetch_use"),
                recommended_extraction_use=chunk.get(
                    "recommended_extraction_use"
                ),
                likely_syndicated_or_aggregated=chunk.get(
                    "likely_syndicated_or_aggregated"
                ),
                upstream_source_mentions=list(
                    chunk.get("upstream_source_mentions") or []
                ),
                discovery_method=chunk.get("discovery_method"),
                search_provider=chunk.get("search_provider"),
                query_id=chunk.get("query_id"),
                query_used=chunk.get("query_used"),
                document_id=chunk.get("document_id"),
                document_type=chunk.get("document_type"),
                fetch_purpose=chunk.get("fetch_purpose"),
                chunk_kind=chunk.get("chunk_kind") or "text",
                data_types=list(chunk.get("data_types") or []),
                context_types=list(chunk.get("context_types") or []),
                extraction_method="deterministic_core_metric_text_fallback",
                extraction_reason="deterministic extraction of core public-health metric from narrative text",
                validation_errors=[],
                repair_actions=[],
                requires_human_review=False,
                statistical_count_type=payload.get("statistical_count_type"),
                reporting_period=payload.get("reporting_period"),
                as_of_date=None,
                count_semantics=payload.get("count_semantics"),
                aggregation_level="national",
                geographic_scope=geographic_scope,
                geographic_scope_type=geographic_scope_type,
                population_scope=chunk.get("population_scope"),
                source_section=chunk.get("source_section"),
                semantic_warnings=warnings,
                extraction_warnings=warnings,
                **record_compatibility_fields(compatibility),
                record_schema="generic_public_health_record",
                legacy_record_type=(
                    "HantavirusRecord"
                    if ((context or {}).get("is_hantavirus") is True)
                    else None
                ),
            )
        )
    return records


def _filter_redundant_core_metric_records(
    primary_record: PublicHealthRecord | None,
    core_records: list[PublicHealthRecord],
    context: dict | None = None,
) -> list[PublicHealthRecord]:
    if _direct_collection_enabled(context):
        return core_records
    if primary_record is None or not core_records:
        return core_records
    primary_values = {
        float(value)
        for value in (
            primary_record.cases_confirmed,
            primary_record.cases_probable,
            primary_record.cases_suspected,
            primary_record.cases_unspecified,
        )
        if value is not None
    }
    if not primary_values:
        return core_records
    filtered: list[PublicHealthRecord] = []
    for record in core_records:
        category = str(record.metric_category or record.metric_name or "").lower()
        value = record.metric_value
        if "case" in category and value is not None:
            try:
                if float(value) in primary_values:
                    continue
            except (TypeError, ValueError):
                pass
        filtered.append(record)
    return filtered


# ---------------------------------------------------------------------------
# Schema validation + repair
# ---------------------------------------------------------------------------


_CONTENT_FIELDS = (
    "cases_confirmed",
    "cases_probable",
    "cases_suspected",
    "cases_unspecified",
    "deaths",
    "hospitalizations",
    "date_reported",
    "country",
    "subnational_location",
    "geographic_scope",
)


def _has_any_case_or_death(record: dict) -> bool:
    for f in (
        "cases_confirmed",
        "cases_probable",
        "cases_suspected",
        "cases_unspecified",
        "deaths",
        "hospitalizations",
    ):
        if record.get(f) is not None:
            return True
    return False


def _has_minimum_content(record: dict) -> bool:
    for f in _CONTENT_FIELDS:
        value = record.get(f)
        if value is None:
            continue
        if isinstance(value, str) and not value.strip():
            continue
        return True
    return False


def _repair_record(
    record: dict,
    policy: StructuredExtractionPolicy,
) -> tuple[dict, list[str]]:
    repaired = dict(record)
    actions: list[str] = []

    disease = repaired.get("disease")
    if not disease or (isinstance(disease, str) and not disease.strip()):
        repaired["disease"] = policy.default_disease
        actions.append("set_disease_to_default")

    if repaired.get("extraction_confidence") is None:
        repaired["extraction_confidence"] = 0.50
        actions.append("set_default_extraction_confidence")

    return repaired, actions


_ISO_DATE_FULL_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_PERIOD_WEEK_RE = re.compile(r"\b(?:mmwr\s*)?week\s+(\d{1,2})\b", re.IGNORECASE)


def _metric_period_start_after_end(record: dict) -> bool:
    start = str(record.get("metric_period_start") or "").strip()
    end = str(record.get("metric_period_end") or "").strip()
    if not (_ISO_DATE_FULL_RE.match(start) and _ISO_DATE_FULL_RE.match(end)):
        return False
    return start > end


def _has_strong_metric_period_disambiguator(record: dict) -> bool:
    for key in ("source_column_label", "metric_column_label"):
        value = str(record.get(key) or "").strip()
        if value and not _is_weak_column_label(value):
            return True
    return str(record.get("metric_period_source") or "").strip() in {
        "llm_extracted",
        "filled_from_row_column_label",
        "filled_from_column_label",
    }


def _ambiguous_multi_period_metric_quote(record: dict) -> bool:
    if record.get("metric_value") in (None, "") and not record.get("metric_name"):
        return False
    quote = str(record.get("evidence_quote") or "").strip()
    if not quote:
        return False
    mentioned_weeks = {
        int(match.group(1))
        for match in _PERIOD_WEEK_RE.finditer(quote)
        if match.group(1).isdigit()
    }
    if len(mentioned_weeks) < 2:
        return False
    return not _has_strong_metric_period_disambiguator(record)


def _validate_record(
    record: dict,
    policy: StructuredExtractionPolicy,
) -> tuple[dict, SchemaValidationResult]:
    repaired, repair_actions = _repair_record(record, policy)

    validation_errors: list[str] = []
    try:
        PublicHealthRecord(**repaired)
        pydantic_ok = True
    except Exception as exc:
        pydantic_ok = False
        validation_errors.append(f"pydantic_validation_failed: {exc}")

    def _missing(field: str) -> bool:
        value = repaired.get(field)
        if value is None:
            return True
        if isinstance(value, str) and not value.strip():
            return True
        return False

    missing_core = [f for f in policy.required_core_fields_for_valid_record if _missing(f)]
    missing_provenance = [f for f in policy.required_provenance_fields if _missing(f)]
    provenance_status = "verified" if not missing_provenance else "incomplete"
    has_min_content = _has_minimum_content(repaired)
    review_trigger_missing = [
        f for f in policy.fields_that_trigger_human_review_if_missing if _missing(f)
    ]
    has_count_signal = _has_any_case_or_death(repaired)
    has_location_signal = any(
        not _missing(f)
        for f in ("country", "subnational_location", "locality", "geographic_scope")
    )
    has_date_signal = any(
        not _missing(f)
        for f in (
            "date_reported",
            "event_start_date",
            "event_end_date",
            "reporting_period",
            "as_of_date",
        )
    )
    if has_count_signal and not has_location_signal:
        review_trigger_missing.append("location")
    if has_count_signal and not has_date_signal:
        review_trigger_missing.append("date")

    missing_fields = sorted({*missing_core, *review_trigger_missing})
    metric_period_invalid = _metric_period_start_after_end(repaired)
    ambiguous_metric_period = _ambiguous_multi_period_metric_quote(repaired)

    if (
        not pydantic_ok
        or missing_core
        or not has_min_content
        or metric_period_invalid
        or ambiguous_metric_period
    ):
        schema_status = "rejected"
        if missing_core:
            validation_errors.append(f"missing_required_core_fields: {missing_core}")
        if not has_min_content:
            validation_errors.append("no_minimum_content")
        if metric_period_invalid:
            validation_errors.append("metric_period_invalid_start_after_end")
        if ambiguous_metric_period:
            validation_errors.append("ambiguous_multi_period_metric_quote")
    elif review_trigger_missing or provenance_status == "incomplete":
        schema_status = "needs_review"
        if review_trigger_missing:
            validation_errors.append(
                f"missing_review_trigger_fields: {review_trigger_missing}"
            )
        if provenance_status == "incomplete":
            validation_errors.append(
                f"incomplete_provenance: {missing_provenance}"
            )
    else:
        schema_status = "valid"

    requires_human_review = schema_status == "needs_review"

    repaired["schema_status"] = schema_status
    repaired["provenance_status"] = provenance_status
    repaired["missing_fields"] = missing_fields
    repaired["validation_errors"] = validation_errors
    repaired["repair_actions"] = repair_actions
    repaired["requires_human_review"] = requires_human_review

    result = SchemaValidationResult(
        record_id=repaired.get("record_id", ""),
        schema_status=schema_status,
        provenance_status=provenance_status,
        validation_errors=validation_errors,
        missing_fields=missing_fields,
        repair_actions=repair_actions,
        requires_human_review=requires_human_review,
    )
    return repaired, result


# ---------------------------------------------------------------------------
# Nodes
# ---------------------------------------------------------------------------


def _load_llm_policy() -> LLMStructuredExtractionPolicy:
    return LLMStructuredExtractionPolicy(**load_llm_structured_extraction_policy())


def _chunk_allowed_for_llm(
    chunk: dict, llm_policy: LLMStructuredExtractionPolicy
) -> bool:
    if not chunk.get("contains_target_data"):
        return False
    if chunk.get("extraction_eligible_for_task_disease") is False:
        return False
    disease_status = chunk.get("disease_relevance_status")
    if disease_status and disease_status != TARGET_DISEASE_MATCH:
        return False
    if chunk.get("fetch_purpose") not in llm_policy.allowed_fetch_purposes:
        return False
    if (chunk.get("chunk_kind") or "text") not in llm_policy.allowed_chunk_kinds:
        return False
    text = chunk.get("text") or ""
    if not text.strip():
        return False
    return True


def _as_disease_relevance_context(context: dict | None) -> dict:
    if not context:
        return build_disease_relevance_context(None)
    if "target_disease_terms" in context or "guard_enabled" in context:
        return context
    return build_disease_relevance_context(context)


def _assess_chunk_for_extraction(chunk: dict, context: dict | None) -> dict:
    if chunk.get("disease_relevance_status"):
        return {
            "status": chunk.get("disease_relevance_status"),
            "score": chunk.get("disease_relevance_score"),
            "target_disease_terms_found": list(
                chunk.get("target_disease_terms_found") or []
            ),
            "incompatible_disease_terms_found": list(
                chunk.get("incompatible_disease_terms_found") or []
            ),
            "reason": chunk.get("disease_relevance_reason"),
            "data_signal_count": chunk.get("disease_relevance_data_signal_count", 0),
        }
    return assess_chunk_disease_relevance(chunk, _as_disease_relevance_context(context))


def _chunk_blocked_by_disease_gate(
    chunk: dict,
    context: dict | None,
) -> tuple[bool, dict]:
    assessment = _assess_chunk_for_extraction(chunk, context)
    if chunk.get("extraction_eligible_for_task_disease") is False:
        return True, assessment
    return assessment.get("status") != TARGET_DISEASE_MATCH, assessment


def _source_context_for_chunk(chunk: dict, context: dict | None) -> dict:
    source_id = str(chunk.get("source_id") or "")
    if isinstance(context, dict):
        source = (context.get("source_registry_by_id") or {}).get(source_id)
        if isinstance(source, dict):
            return source
    return {}


def _chunk_is_must_fetch(chunk: dict, context: dict | None) -> bool:
    source_id = str(chunk.get("source_id") or "")
    must_fetch_ids = set()
    if isinstance(context, dict):
        must_fetch_ids = {str(v) for v in (context.get("must_fetch_source_ids") or [])}
    source = _source_context_for_chunk(chunk, context)
    return (
        bool(source_id and source_id in must_fetch_ids)
        or chunk.get("must_fetch") is True
        or source.get("must_fetch") is True
    )


def _chunk_is_official_or_high_trust(chunk: dict, context: dict | None) -> bool:
    source = _source_context_for_chunk(chunk, context)
    values = [
        chunk.get("source_type"),
        chunk.get("source_type_final"),
        chunk.get("publisher"),
        chunk.get("actual_publisher"),
        chunk.get("source_url"),
        chunk.get("credibility_level"),
        source.get("source_type"),
        source.get("source_type_final"),
        source.get("publisher"),
        source.get("actual_publisher"),
        source.get("canonical_url"),
        source.get("url"),
        source.get("credibility_level"),
    ]
    text = _lower(" ".join(str(value or "") for value in values))
    return (
        "high" in {_lower(chunk.get("credibility_level")), _lower(source.get("credibility_level"))}
        or "official_public_health_agency" in text
        or "public_health_agency" in text
        or "department of health" in text
        or "state_or_local_public_health_agency" in text
        or ".gov" in text
    )


_TASK_COLLECTION_CANDIDATE_LABELS = {
    "verified_target_collection",
    "search_verified_target_collection",
    "fetch_verified_target_collection",
    "task_record_collection_candidate",
}
_TASK_COLLECTION_REJECT_LABELS = {
    "context",
    "context_only",
    "validation",
    "validation_only",
    "best_available_context_candidate",
    "wrong_period_context",
    "excluded",
    "non_target_or_context",
}


def _chunk_is_task_collection_candidate(chunk: dict, context: dict | None) -> bool:
    source = _source_context_for_chunk(chunk, context)
    labels = {
        _lower(chunk.get("target_fit_status")),
        _lower(chunk.get("triage_role")),
        _lower(chunk.get("source_role_final")),
        _lower(chunk.get("source_role")),
        _lower(source.get("target_fit_status")),
        _lower(source.get("triage_role")),
        _lower(source.get("source_role_final")),
        _lower(source.get("source_role")),
    }
    if labels & _TASK_COLLECTION_REJECT_LABELS:
        return False
    if chunk.get("usable_for_task_collection") is True or source.get("usable_for_task_collection") is True:
        return True
    if labels & _TASK_COLLECTION_CANDIDATE_LABELS:
        return True
    return (
        "collection" in labels
        and _lower(source.get("geography_fit") or chunk.get("geography_fit"))
        in {"match", "candidate", "possible", ""}
        and _lower(source.get("date_fit") or chunk.get("date_fit"))
        in {"match", "candidate", "possible", ""}
    )


def _domain_from_text_url(value: str) -> str:
    domain = urlsplit(str(value or "")).netloc.lower()
    return domain[4:] if domain.startswith("www.") else domain


def _domain_matches(domain: str, official_domains: list[str]) -> bool:
    if not domain:
        return False
    for official in official_domains:
        official = str(official or "").strip().lower()
        if official and (domain == official or domain.endswith("." + official)):
            return True
    return False


def _chunk_text_for_target_matching(chunk: dict, context: dict | None) -> str:
    source = _source_context_for_chunk(chunk, context)
    values = [
        chunk.get("source_url"),
        chunk.get("canonical_url"),
        chunk.get("title"),
        chunk.get("publisher"),
        chunk.get("text"),
        source.get("canonical_url"),
        source.get("url"),
        source.get("title"),
        source.get("publisher"),
        source.get("actual_publisher"),
    ]
    return _lower(" ".join(str(value or "") for value in values))


def _chunk_domain(chunk: dict, context: dict | None) -> str:
    source = _source_context_for_chunk(chunk, context)
    for value in (
        chunk.get("source_url"),
        chunk.get("canonical_url"),
        source.get("canonical_url"),
        source.get("url"),
    ):
        domain = _domain_from_text_url(str(value or ""))
        if domain:
            return domain
    return ""


def _chunk_official_report_key(chunk: dict, context: dict | None) -> str | None:
    source_id = str(chunk.get("source_id") or "")
    key_by_source = (context or {}).get("official_report_key_by_source_id") or {}
    if source_id and isinstance(key_by_source, dict):
        key = key_by_source.get(source_id)
        if key:
            return str(key)
    source = _source_context_for_chunk(chunk, context)
    for value in (
        chunk.get("source_url"),
        chunk.get("canonical_url"),
        source.get("canonical_url"),
        source.get("url"),
    ):
        key = official_report_key_for_url(str(value or ""))
        if key:
            return key
    return None


def _chunk_matches_target_official_requirement(
    chunk: dict,
    context: dict | None,
) -> bool:
    if not _direct_collection_enabled(context):
        return False
    requirements = build_source_coverage_requirements(context or {})
    if not requirements:
        return False
    domain = _chunk_domain(chunk, context)
    text = _chunk_text_for_target_matching(chunk, context)
    for requirement in requirements:
        if not _domain_matches(domain, list(requirement.get("official_domains") or [])):
            continue
        week = str(requirement.get("week") or "")
        year = str(requirement.get("year") or "")
        week_hints = {
            f"week-{week}",
            f"week_{week}",
            f"week {week}",
        }
        try:
            week_int = int(week)
            week_hints.update(
                {
                    f"week-{week_int:02d}",
                    f"week_{week_int:02d}",
                    f"week {week_int:02d}",
                }
            )
        except (TypeError, ValueError):
            pass
        date_match = any(
            str(value or "").strip().lower() in text
            for value in (requirement.get("date_hints") or [])
            if str(value or "").strip()
        )
        title_match = any(
            str(value or "").strip().lower() in text
            for value in (requirement.get("title_hints") or [])
            if str(value or "").strip()
        )
        week_match = any(hint and hint in text for hint in week_hints)
        if (date_match or week_match or title_match) and (not year or year in text or title_match):
            return True
    return False


def _chunk_priority(chunk: dict, context: dict | None) -> int:
    if _chunk_is_must_fetch(chunk, context):
        return 0
    if (
        _chunk_matches_target_official_requirement(chunk, context)
        or _chunk_is_task_collection_candidate(chunk, context)
    ):
        return 1
    if _chunk_is_official_or_high_trust(chunk, context):
        return 2
    role = _lower(chunk.get("source_role_final") or chunk.get("source_role"))
    if role in {"collection", "collection_support"}:
        return 3
    return 4


_TARGET_SOURCE_UNUSABLE_COVERAGE_STATUSES = {
    "partial_target_coverage",
    "target_official_source_missing",
    "target_source_missing_or_unverified",
    "target_official_source_fetch_failed",
    "target_official_source_unusable",
    "target_official_all_aliases_unusable",
    "target_alias_error_page",
    "target_source_unusable_error_page",
    "fallback_target_fetch_failed",
    "no_task_collection_document",
}


def _direct_should_skip_non_target_extraction(
    chunks: list[dict],
    context: dict | None,
) -> bool:
    if not _direct_collection_enabled(context):
        return False
    coverage_status = _lower(
        ((context or {}).get("source_coverage_audit") or {}).get("coverage_status")
    )
    if coverage_status not in _TARGET_SOURCE_UNUSABLE_COVERAGE_STATUSES:
        return False
    return not any(
        isinstance(chunk, dict) and _chunk_priority(chunk, context) <= 1
        for chunk in chunks
    )


def _ordered_llm_chunks(evidence_chunks: list[dict], context: dict | None) -> list[dict]:
    min_per_source = _parse_positive_int_env(
        "HDC_LLM_MUST_FETCH_MIN_CHUNKS_PER_SOURCE",
        6,
    )
    official_max = _parse_positive_int_env(
        "HDC_LLM_OFFICIAL_EXTRACTION_MAX_CHUNKS",
        30,
    )
    indexed = [
        (index, chunk)
        for index, chunk in enumerate(evidence_chunks)
        if isinstance(chunk, dict)
    ]
    must_fetch = [(idx, chunk) for idx, chunk in indexed if _chunk_priority(chunk, context) == 0]
    others = [(idx, chunk) for idx, chunk in indexed if _chunk_priority(chunk, context) != 0]

    grouped: dict[str, list[tuple[int, dict]]] = {}
    source_order: list[str] = []
    for item in must_fetch:
        source_id = str(item[1].get("source_id") or "")
        if source_id not in grouped:
            grouped[source_id] = []
            source_order.append(source_id)
        grouped[source_id].append(item)

    prioritized: list[tuple[int, dict]] = []
    for round_index in range(min_per_source):
        for source_id in source_order:
            group = grouped.get(source_id) or []
            if round_index < len(group):
                prioritized.append(group[round_index])
    for source_id in source_order:
        group = grouped.get(source_id) or []
        prioritized.extend(group[min_per_source:])

    prioritized_ids = {id(chunk) for _, chunk in prioritized}
    remaining = [
        item
        for item in others
        if id(item[1]) not in prioritized_ids
    ]
    remaining.sort(
        key=lambda item: (
            _chunk_priority(item[1], context),
            item[1].get("source_id") or "",
            item[1].get("chunk_index") or item[0],
            item[0],
        )
    )
    if _direct_collection_enabled(context):
        official_remaining: list[tuple[int, dict]] = []
        non_official_remaining: list[tuple[int, dict]] = []
        for item in remaining:
            if _chunk_priority(item[1], context) == 1:
                official_remaining.append(item)
            else:
                non_official_remaining.append(item)
        remaining = [
            *official_remaining[:official_max],
            *non_official_remaining,
            *official_remaining[official_max:],
        ]
    return [chunk for _, chunk in [*prioritized, *remaining]]


def _direct_llm_chunk_allowed(
    chunk: dict,
    llm_policy: LLMStructuredExtractionPolicy,
    context: dict | None,
) -> bool:
    if not _direct_collection_enabled(context) or not _chunk_is_must_fetch(chunk, context):
        return _chunk_allowed_for_llm(chunk, llm_policy)
    if chunk.get("fetch_purpose") not in llm_policy.allowed_fetch_purposes:
        return False
    if (chunk.get("chunk_kind") or "text") not in llm_policy.allowed_chunk_kinds:
        return False
    return bool((chunk.get("text") or "").strip())


def _source_budget_row(
    budget_by_source: dict[str, dict],
    chunk: dict,
    context: dict | None,
) -> dict:
    source_id = str(chunk.get("source_id") or "unknown")
    official_report_key = _chunk_official_report_key(chunk, context)
    priority = _chunk_priority(chunk, context)
    if priority <= 1:
        budget_bucket = "verified_target_collection"
        target_fit_status = "verified_target"
    elif _chunk_is_official_or_high_trust(chunk, context):
        budget_bucket = "official_or_high_trust"
        target_fit_status = "non_target_or_context"
    elif _is_context_only_chunk(chunk, None):
        budget_bucket = "context"
        target_fit_status = "non_target_or_context"
    else:
        budget_bucket = "other"
        target_fit_status = "non_target_or_context"
    row = budget_by_source.setdefault(
        source_id,
        {
            "source_id": source_id,
            "official_report_key": official_report_key,
            "must_fetch": _chunk_is_must_fetch(chunk, context),
            "official_or_high_trust": _chunk_is_official_or_high_trust(chunk, context),
            "budget_bucket": budget_bucket,
            "target_fit_status": target_fit_status,
            "attempted_before_target_sources": False,
            "queued_count": 0,
            "eligible_count": 0,
            "attempted_count": 0,
            "skipped_due_to_cap_count": 0,
            "skipped_context_only_count": 0,
            "skipped_disease_mismatch_count": 0,
            "record_count": 0,
        },
    )
    row["must_fetch"] = bool(row.get("must_fetch") or _chunk_is_must_fetch(chunk, context))
    row["official_or_high_trust"] = bool(
        row.get("official_or_high_trust")
        or _chunk_is_official_or_high_trust(chunk, context)
    )
    if official_report_key and not row.get("official_report_key"):
        row["official_report_key"] = official_report_key
    if priority <= 1:
        row["budget_bucket"] = "verified_target_collection"
        row["target_fit_status"] = "verified_target"
    return row


def _has_any_llm_content_signal(record_data: dict) -> bool:
    for field in (
        "cases_confirmed",
        "cases_probable",
        "cases_suspected",
        "cases_unspecified",
        "deaths",
        "hospitalizations",
        "icu_admissions",
        "tests_positive",
        "tests_total",
        "positivity_rate",
        "incidence_rate",
        "cumulative_count",
        "new_count",
        "metric_name",
        "metric_value",
        "metric_period_start",
        "metric_period_end",
        "date_reported",
        "country",
        "subnational_location",
    ):
        if record_data.get(field) is not None:
            return True
    return False


def _task_period_from_context(context: dict | None) -> tuple[str | None, str | None]:
    context = context or {}
    structured = context.get("structured_task") or {}
    collection = context.get("collection_spec") or {}
    start = structured.get("start_date") or collection.get("start_date")
    end = structured.get("end_date") or collection.get("end_date") or start
    return (str(start) if start else None, str(end) if end else None)


def _source_period_from_chunk(
    chunk: dict,
    context: dict | None = None,
) -> tuple[str | None, str | None, str | None]:
    start = chunk.get("reporting_period_start")
    end = chunk.get("reporting_period_end")
    label = chunk.get("reporting_period_label")
    if start and end:
        return str(start), str(end), str(label) if label else None
    metadata = chunk.get("metadata") if isinstance(chunk.get("metadata"), dict) else {}
    start = metadata.get("reporting_period_start")
    end = metadata.get("reporting_period_end")
    label = metadata.get("reporting_period_label")
    if start and end:
        return str(start), str(end), str(label) if label else None
    source = _source_context_for_chunk(chunk, context)
    for container in (source,):
        start = container.get("reporting_period_start")
        end = container.get("reporting_period_end")
        label = container.get("reporting_period_label")
        if start and end:
            return str(start), str(end), str(label) if label else None
    source_values = [
        chunk.get("source_url"),
        chunk.get("canonical_url"),
        source.get("canonical_url"),
        source.get("url"),
    ]
    source_keys = {
        official_report_key_for_url(str(value or ""))
        for value in source_values
        if value
    }
    source_keys.discard(None)
    for requirement in build_source_coverage_requirements(context or {}):
        req_start = requirement.get("reporting_period_start")
        req_end = requirement.get("reporting_period_end")
        if not req_start or not req_end:
            continue
        req_keys = {
            official_report_key_for_url(str(value or ""))
            for value in (requirement.get("official_candidate_urls") or [])
            if value
        }
        req_keys.discard(None)
        if source_keys and req_keys and source_keys.intersection(req_keys):
            return (
                str(req_start),
                str(req_end),
                str(requirement.get("reporting_period_label") or ""),
            )
    return None, None, None


def _source_requirement_from_chunk(
    chunk: dict,
    context: dict | None = None,
) -> dict | None:
    source = _source_context_for_chunk(chunk, context)
    source_values = [
        chunk.get("source_url"),
        chunk.get("canonical_url"),
        source.get("canonical_url"),
        source.get("url"),
    ]
    source_keys = {
        official_report_key_for_url(str(value or ""))
        for value in source_values
        if value
    }
    source_keys.discard(None)
    for requirement in build_source_coverage_requirements(context or {}):
        req_keys = {
            official_report_key_for_url(str(value or ""))
            for value in (requirement.get("official_candidate_urls") or [])
            if value
        }
        req_keys.discard(None)
        if source_keys and req_keys and source_keys.intersection(req_keys):
            return requirement
    return None


def _inherit_task_source_context_for_metric_record(
    cleaned: dict,
    chunk: dict,
    row_metadata: dict,
    context: dict | None,
) -> dict:
    if cleaned.get("metric_value") in (None, "") and not cleaned.get("metric_name"):
        return cleaned
    out = dict(cleaned)
    requirement = _source_requirement_from_chunk(chunk, context)
    task_location = _task_location_from_context(context)
    inherited_location = _first_text(
        row_metadata.get("country"),
        chunk.get("country"),
        requirement.get("location") if isinstance(requirement, dict) else None,
        task_location,
    )
    if not out.get("country") and _is_united_states_location(inherited_location):
        out["country"] = "United States"
    if not out.get("geographic_scope"):
        out["geographic_scope"] = _first_text(
            row_metadata.get("geographic_scope"),
            chunk.get("geographic_scope"),
            inherited_location,
        )
    if not out.get("geographic_scope_type") and out.get("geographic_scope"):
        out["geographic_scope_type"] = (
            "country"
            if _is_united_states_location(out.get("geographic_scope"))
            else "subnational"
        )

    period_start = _first_text(
        row_metadata.get("reporting_period_start"),
        chunk.get("reporting_period_start"),
        requirement.get("reporting_period_start")
        if isinstance(requirement, dict)
        else None,
    )
    period_end = _first_text(
        row_metadata.get("reporting_period_end"),
        chunk.get("reporting_period_end"),
        requirement.get("reporting_period_end")
        if isinstance(requirement, dict)
        else None,
    )
    period_label = _first_text(
        row_metadata.get("reporting_period_label"),
        chunk.get("reporting_period_label"),
        requirement.get("reporting_period_label")
        if isinstance(requirement, dict)
        else None,
    )
    if period_label and not out.get("reporting_period"):
        out["reporting_period"] = period_label
    if period_end and not out.get("date_reported"):
        out["date_reported"] = period_end
    if period_end and not out.get("date_anchor"):
        out["date_anchor"] = period_end
    return out


def _fill_metric_period_from_verified_source(
    cleaned: dict,
    chunk: dict,
    context: dict | None,
) -> dict:
    if not _direct_collection_enabled(context):
        return cleaned
    if cleaned.get("metric_value") in (None, "") and not cleaned.get("metric_name"):
        return cleaned
    if cleaned.get("metric_period_start") and cleaned.get("metric_period_end"):
        out = dict(cleaned)
        out["metric_period_source"] = out.get("metric_period_source") or "llm_extracted"
        return out
    if _chunk_priority(chunk, context) > 1:
        return cleaned
    start, end, _label = _source_period_from_chunk(chunk, context)
    if not start or not end:
        return cleaned
    out = dict(cleaned)
    if not out.get("metric_period_start"):
        out["metric_period_start"] = start
    if not out.get("metric_period_end"):
        out["metric_period_end"] = end
    out["metric_period_source"] = (
        out.get("metric_period_source") or "filled_from_source_reporting_period"
    )
    warnings = list(out.get("semantic_warnings") or [])
    if "filled_metric_period_from_source_reporting_period" not in warnings:
        warnings.append("filled_metric_period_from_source_reporting_period")
    out["semantic_warnings"] = warnings
    return out


_WEAK_COLUMN_LABEL_RE = re.compile(r"^column[_\s-]?\d+$", re.IGNORECASE)


def _is_weak_column_label(value: str | None) -> bool:
    text = str(value or "").strip()
    if not text:
        return True
    return bool(_WEAK_COLUMN_LABEL_RE.match(text))


def _preferred_column_label(
    llm_value: str | None,
    row_or_chunk_value: str | None,
) -> str | None:
    if _is_weak_column_label(llm_value) and not _is_weak_column_label(
        row_or_chunk_value
    ):
        return str(row_or_chunk_value)
    return str(llm_value).strip() if str(llm_value or "").strip() else (
        str(row_or_chunk_value).strip()
        if str(row_or_chunk_value or "").strip()
        else None
    )


def _column_semantics_text(
    cleaned: dict,
    row_metadata: dict,
    chunk: dict,
) -> str:
    values = [
        cleaned.get("source_column_label"),
        cleaned.get("metric_column_label"),
        row_metadata.get("source_column_label"),
        row_metadata.get("metric_column_label"),
        chunk.get("source_column_label"),
        chunk.get("metric_column_label"),
        " ".join(str(item) for item in (row_metadata.get("source_column_labels") or [])),
        " ".join(str(item) for item in (chunk.get("source_column_labels") or [])),
        row_metadata.get("table_header"),
        chunk.get("table_header"),
        row_metadata.get("heading_context"),
        chunk.get("heading_context"),
        cleaned.get("reporting_period"),
        row_metadata.get("reporting_period_label"),
        chunk.get("reporting_period_label"),
    ]
    return " ".join(str(value or "") for value in values).lower()


def _cumulative_reporting_period_label(
    cleaned: dict,
    row_metadata: dict,
    chunk: dict,
) -> str | None:
    labels = [
        cleaned.get("metric_column_label"),
        cleaned.get("source_column_label"),
        row_metadata.get("metric_column_label"),
        row_metadata.get("source_column_label"),
        chunk.get("metric_column_label"),
        chunk.get("source_column_label"),
    ]
    clean_labels = [
        str(label).strip()
        for label in labels
        if str(label or "").strip() and not _is_weak_column_label(str(label))
    ]
    for label in clean_labels:
        lowered = label.lower()
        if "through" in lowered and any(
            marker in lowered for marker in ("season", "cumulative", "to date")
        ):
            return label
    cumulative_label = next(
        (
            label
            for label in clean_labels
            if any(
                marker in label.lower()
                for marker in ("season", "cumulative", "to date")
            )
        ),
        None,
    )
    period_label = (
        cleaned.get("reporting_period")
        or row_metadata.get("reporting_period_label")
        or chunk.get("reporting_period_label")
    )
    if cumulative_label and period_label:
        return f"{cumulative_label} through {period_label}"
    if period_label:
        return f"Season-to-date through {period_label}"
    return cumulative_label


def _parse_iso_date_value(value: object) -> date | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return date.fromisoformat(text[:10])
    except (TypeError, ValueError):
        return None


def _previous_period_from_source(
    chunk: dict,
    context: dict | None,
) -> tuple[str | None, str | None]:
    start, end, _label = _source_period_from_chunk(chunk, context)
    start_date = _parse_iso_date_value(start)
    end_date = _parse_iso_date_value(end)
    if not start_date or not end_date:
        return None, None
    if end_date < start_date:
        start_date, end_date = end_date, start_date
    period_length = (end_date - start_date).days + 1
    previous_end = start_date - timedelta(days=1)
    previous_start = previous_end - timedelta(days=period_length - 1)
    return previous_start.isoformat(), previous_end.isoformat()


def _metric_column_label_text(
    cleaned: dict,
    row_metadata: dict,
    chunk: dict,
) -> str:
    labels = [
        cleaned.get("source_column_label"),
        cleaned.get("metric_column_label"),
        row_metadata.get("source_column_label"),
        row_metadata.get("metric_column_label"),
        chunk.get("source_column_label"),
        chunk.get("metric_column_label"),
    ]
    return " ".join(str(label or "") for label in labels).strip().lower()


_NARRATIVE_WEEK_RE = re.compile(
    r"\b(?:during|for|in)\s+(?:mmwr\s+)?week\s+\d{1,2}\b|\bthis week\b",
    re.IGNORECASE,
)


def _row_context_type_set(row_metadata: dict, chunk: dict) -> set[str]:
    values = {
        str(row_metadata.get("row_context_type") or ""),
        str(chunk.get("row_context_type") or ""),
    }
    values.update(str(item) for item in (row_metadata.get("context_types") or []))
    values.update(str(item) for item in (chunk.get("context_types") or []))
    return {value for value in values if value}


def _narrative_metric_text(row_metadata: dict, chunk: dict) -> str:
    return str(
        row_metadata.get("row_quote")
        or row_metadata.get("text")
        or chunk.get("row_quote")
        or chunk.get("text")
        or ""
    )


def _is_narrative_metric_line(row_metadata: dict, chunk: dict) -> bool:
    text = _narrative_metric_text(row_metadata, chunk)
    if not text or "|" in text:
        return False
    context_types = _row_context_type_set(row_metadata, chunk)
    return bool(
        "markdown_metric_line" in context_types
        or row_metadata.get("row_context_type") == "markdown_metric_line"
        or chunk.get("row_context_type") == "markdown_metric_line"
    )


def _source_period_available(chunk: dict, context: dict | None) -> bool:
    start, end, _label = _source_period_from_chunk(chunk, context)
    return bool(start and end)


def _narrative_metric_resolves_current_period(
    row_metadata: dict,
    chunk: dict,
    context: dict | None,
) -> bool:
    if not _is_narrative_metric_line(row_metadata, chunk):
        return False
    if not _source_period_available(chunk, context):
        return False
    text = _narrative_metric_text(row_metadata, chunk)
    return bool(_NARRATIVE_WEEK_RE.search(text))


def _resolve_metric_column_period_type(
    cleaned: dict,
    row_metadata: dict,
    chunk: dict,
    context: dict | None = None,
) -> tuple[str, str, str, list[str]]:
    label_text = _metric_column_label_text(cleaned, row_metadata, chunk)
    semantics_text = _column_semantics_text(cleaned, row_metadata, chunk)
    source_label = str(cleaned.get("source_column_label") or "").strip()
    metric_label = str(cleaned.get("metric_column_label") or "").strip()
    warning_flags: list[str] = []
    cumulative_markers = (
        "cumulative",
        "season-to-date",
        "season to date",
        "season_to_date",
        "to date",
        "through week",
        "since season",
    )
    previous_markers = (
        "previous week",
        "prior week",
        "last week",
        "previous period",
        "prior period",
    )
    current_markers = (
        "current week",
        "this week",
        "reporting week",
        "current period",
    )
    if any(marker in semantics_text for marker in cumulative_markers):
        return (
            "resolved",
            "cumulative_period",
            "resolved_from_cumulative_column_label",
            warning_flags,
        )
    if any(marker in label_text for marker in previous_markers):
        return (
            "resolved",
            "previous_period",
            "resolved_from_previous_column_label",
            warning_flags,
        )
    if any(marker in label_text for marker in current_markers):
        return (
            "resolved",
            "current_period",
            "resolved_from_current_column_label",
            warning_flags,
        )
    if _narrative_metric_resolves_current_period(row_metadata, chunk, context):
        return (
            "resolved",
            "current_period",
            "resolved_from_narrative_week_phrase",
            warning_flags,
        )
    if _is_weak_column_label(source_label) or _is_weak_column_label(metric_label):
        warning_flags.append("ambiguous_metric_column_semantics")
        return (
            "ambiguous",
            "ambiguous_column",
            "weak_column_label_without_header_semantics",
            warning_flags,
        )
    if source_label or metric_label:
        return (
            "resolved",
            "current_period",
            "treated_as_current_period_from_explicit_metric_column_label",
            warning_flags,
        )
    warning_flags.append("ambiguous_metric_column_semantics")
    return (
        "ambiguous",
        "ambiguous_column",
        "missing_column_label_semantics",
        warning_flags,
    )


def _apply_metric_column_semantics(
    cleaned: dict,
    row_metadata: dict,
    chunk: dict,
    context: dict | None = None,
) -> dict:
    if cleaned.get("metric_value") in (None, "") and not cleaned.get("metric_name"):
        return cleaned
    out = dict(cleaned)
    source_label = _preferred_column_label(
        out.get("source_column_label"),
        row_metadata.get("source_column_label") or chunk.get("source_column_label"),
    )
    metric_label = _preferred_column_label(
        out.get("metric_column_label"),
        row_metadata.get("metric_column_label") or chunk.get("metric_column_label"),
    )
    if source_label:
        out["source_column_label"] = source_label
    if metric_label:
        out["metric_column_label"] = metric_label

    (
        semantics_status,
        period_type,
        resolution_reason,
        column_warning_flags,
    ) = _resolve_metric_column_period_type(out, row_metadata, chunk, context)
    out["metric_column_semantics_status"] = semantics_status
    out["resolved_column_period_type"] = period_type
    out["column_period_resolution_reason"] = resolution_reason
    if resolution_reason == "resolved_from_narrative_week_phrase":
        out["column_semantics_resolution_method"] = "narrative_week_phrase"
        out["column_semantics_confidence"] = 0.85
    elif semantics_status == "resolved":
        out["column_semantics_resolution_method"] = "column_label"
        out["column_semantics_confidence"] = 0.95
    else:
        out["column_semantics_resolution_method"] = "unresolved"
        out["column_semantics_confidence"] = 0.0
    merged_column_warnings = list(out.get("column_period_warning_flags") or [])
    for warning in column_warning_flags:
        if warning not in merged_column_warnings:
            merged_column_warnings.append(warning)
    out["column_period_warning_flags"] = merged_column_warnings

    semantic_warnings = list(out.get("semantic_warnings") or [])
    for warning in column_warning_flags:
        if warning not in semantic_warnings:
            semantic_warnings.append(warning)
    out["semantic_warnings"] = semantic_warnings

    if period_type == "previous_period":
        previous_start, previous_end = _previous_period_from_source(chunk, context)
        if previous_start and previous_end:
            out["metric_period_start"] = previous_start
            out["metric_period_end"] = previous_end
            out["metric_period_source"] = "filled_from_previous_column_label"
            out["date_reported"] = previous_end
            out["date_anchor"] = previous_end
        else:
            out["metric_column_semantics_status"] = "ambiguous"
            out["resolved_column_period_type"] = "ambiguous_previous_period"
            out["column_period_resolution_reason"] = (
                "previous_column_label_without_source_reporting_period"
            )
            if "ambiguous_previous_period" not in out["column_period_warning_flags"]:
                out["column_period_warning_flags"].append("ambiguous_previous_period")
            if "ambiguous_previous_period" not in out["semantic_warnings"]:
                out["semantic_warnings"].append("ambiguous_previous_period")
        return out

    if period_type == "current_period":
        if resolution_reason == "resolved_from_narrative_week_phrase":
            out["metric_period_source"] = "filled_from_narrative_week_phrase"
        else:
            out["metric_period_source"] = (
                out.get("metric_period_source") or "filled_from_source_reporting_period"
            )
        return out

    if period_type == "cumulative_period":
        out["statistical_count_type"] = "cumulative"
        out["count_semantics"] = "cumulative"
        out["metric_period_source"] = "filled_from_column_label"
        cumulative_period = _cumulative_reporting_period_label(
            out,
            row_metadata,
            chunk,
        )
        if cumulative_period:
            out["reporting_period"] = cumulative_period
            out["metric_period_label"] = cumulative_period
        if "inferred_cumulative_metric_from_column_label" not in out["semantic_warnings"]:
            out["semantic_warnings"].append(
                "inferred_cumulative_metric_from_column_label"
            )
        return out

    return out


_METRIC_ROW_STOPWORDS = {
    "number",
    "specimens",
    "specimen",
    "total",
    "count",
    "rate",
    "percent",
    "percentage",
    "reported",
    "reports",
    "with",
    "from",
    "this",
    "that",
    "week",
}


def _metric_text_tokens(value: str | None) -> set[str]:
    tokens = {
        token
        for token in re.findall(r"[a-z0-9]+", str(value or "").lower())
        if len(token) >= 3 and token not in _METRIC_ROW_STOPWORDS
    }
    return tokens


def _record_value_tokens(cleaned: dict) -> set[str]:
    tokens: set[str] = set()
    for key in (
        "metric_value",
        "tests_positive",
        "tests_total",
        "hospitalizations",
        "deaths",
        "cases_confirmed",
        "cases_probable",
        "cases_suspected",
        "cases_unspecified",
        "positivity_rate",
        "incidence_rate",
    ):
        value = cleaned.get(key)
        if value in (None, ""):
            continue
        text = str(value)
        tokens.add(text)
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            continue
        if numeric.is_integer():
            tokens.add(str(int(numeric)))
        tokens.add(f"{numeric:g}")
    return tokens


def _row_match_score(row_metadata: dict, row_quote: str, cleaned: dict) -> int:
    row_text = str(row_quote or row_metadata.get("row_quote") or row_metadata.get("text") or "")
    row_lower = row_text.lower()
    row_numbers = set(row_metadata.get("row_numeric_tokens") or _numeric_tokens(row_text))
    value_tokens = _record_value_tokens(cleaned)
    score = 0
    if value_tokens and row_numbers.intersection(value_tokens):
        score += 6
    metric_tokens = (
        _metric_text_tokens(cleaned.get("metric_name"))
        | _metric_text_tokens(cleaned.get("metric_category"))
    )
    if metric_tokens:
        overlap = {token for token in metric_tokens if token in row_lower}
        score += len(overlap) * 2
        if len(overlap) >= min(2, len(metric_tokens)):
            score += 2
    return score


def _resolve_metric_row_binding(
    cleaned: dict,
    chunk: dict,
    requested_row_id: str | None,
) -> tuple[str | None, dict, str, list[str]]:
    row_quote_by_id = chunk.get("row_quote_by_id") or {}
    row_metadata_by_id = chunk.get("row_metadata_by_id") or {}
    warnings: list[str] = []
    if not isinstance(row_metadata_by_id, dict) or not row_metadata_by_id:
        return requested_row_id, {}, "not_applicable", warnings

    def _metadata_for(row_id: str | None) -> dict:
        if not row_id:
            return {}
        metadata = row_metadata_by_id.get(str(row_id))
        return metadata if isinstance(metadata, dict) else {}

    def _quote_for(row_id: str | None, metadata: dict) -> str:
        if row_id and isinstance(row_quote_by_id, dict):
            quote = row_quote_by_id.get(str(row_id))
            if quote:
                return str(quote)
        return str(metadata.get("row_quote") or metadata.get("text") or "")

    requested_metadata = _metadata_for(requested_row_id)
    if requested_metadata:
        requested_score = _row_match_score(
            requested_metadata,
            _quote_for(requested_row_id, requested_metadata),
            cleaned,
        )
        if requested_score > 0:
            return requested_row_id, requested_metadata, "resolved", warnings

    best_row_id: str | None = None
    best_metadata: dict = {}
    best_score = 0
    for candidate_row_id, metadata in row_metadata_by_id.items():
        if not isinstance(metadata, dict):
            continue
        score = _row_match_score(
            metadata,
            _quote_for(str(candidate_row_id), metadata),
            cleaned,
        )
        if score > best_score:
            best_score = score
            best_row_id = str(candidate_row_id)
            best_metadata = metadata

    if best_row_id and best_score > 0:
        if requested_row_id and best_row_id != str(requested_row_id):
            warnings.append("metric_row_rebound_from_llm_source_row_id")
            return best_row_id, best_metadata, "rebinding_resolved", warnings
        return best_row_id, best_metadata, "resolved", warnings

    warnings.append("metric_row_binding_unresolved")
    return requested_row_id, requested_metadata, "unresolved", warnings


def _build_record_from_llm_output(
    llm_record: LLMExtractedRecord,
    chunk: dict,
    index: int,
    llm_policy: LLMStructuredExtractionPolicy,
    settings: dict,
    context: dict | None = None,
) -> PublicHealthRecord | None:
    data = llm_record.model_dump()
    if not _has_any_llm_content_signal(data):
        return None

    source_id = chunk.get("source_id") or ""
    record_id = f"rec_{source_id}_{index:03d}"
    text = chunk.get("text") or ""
    extraction_confidence = chunk.get("confidence")
    if extraction_confidence is None:
        extraction_confidence = 0.50

    # Apply Step 16 semantic guardrails over LLM output (disease standardization,
    # virus_or_syndrome cleanup, statistical_count_type inference, geographic
    # scope handling). Returns a cleaned dict + accumulates semantic_warnings.
    cleaned = _apply_extraction_semantic_guardrails(data, chunk, context)
    cleaned = _fill_metric_period_from_verified_source(cleaned, chunk, context)
    row_quote_by_id = chunk.get("row_quote_by_id") or {}
    row_chunk_id_by_id = chunk.get("row_chunk_id_by_id") or {}
    row_metadata_by_id = chunk.get("row_metadata_by_id") or {}
    requested_source_row_id = cleaned.get("source_row_id") or chunk.get("row_id")
    source_row_id, row_metadata, metric_row_binding_status, binding_warnings = (
        _resolve_metric_row_binding(cleaned, chunk, requested_source_row_id)
    )
    if binding_warnings:
        warnings = list(cleaned.get("semantic_warnings") or [])
        for warning in binding_warnings:
            if warning not in warnings:
                warnings.append(warning)
        cleaned["semantic_warnings"] = warnings
    if (
        row_metadata
        and not cleaned.get("metric_period_start")
        and row_metadata.get("reporting_period_start")
    ):
        cleaned["metric_period_start"] = row_metadata.get("reporting_period_start")
        cleaned["metric_period_end"] = row_metadata.get("reporting_period_end")
        cleaned["metric_period_source"] = "filled_from_row_column_label"
    cleaned = _inherit_task_source_context_for_metric_record(
        cleaned,
        chunk,
        row_metadata,
        context,
    )

    def _row_or_chunk(key: str):
        value = row_metadata.get(key)
        return value if value not in (None, "") else chunk.get(key)

    cleaned = _apply_metric_column_semantics(cleaned, row_metadata, chunk, context)

    evidence_quote = text
    supporting_chunk_id = chunk.get("chunk_id")
    if source_row_id and isinstance(row_quote_by_id, dict):
        row_quote = row_quote_by_id.get(str(source_row_id))
        if row_quote:
            evidence_quote = str(row_quote)
    elif chunk.get("row_quote"):
        evidence_quote = str(chunk.get("row_quote"))
    if source_row_id and isinstance(row_chunk_id_by_id, dict):
        supporting_chunk_id = row_chunk_id_by_id.get(str(source_row_id)) or supporting_chunk_id
    record_chunk_kind = _row_or_chunk("chunk_kind") or "text"
    record_data_types = list(_row_or_chunk("data_types") or [])
    record_context_types = sorted(
        {
            *[str(item) for item in (chunk.get("context_types") or [])],
            *[str(item) for item in (row_metadata.get("context_types") or [])],
        }
    )
    row_context_type = _row_or_chunk("row_context_type")
    if not row_context_type and "markdown_metric_line" in record_context_types:
        row_context_type = "markdown_metric_line"
    elif not row_context_type and "markdown_table_row" in record_context_types:
        row_context_type = "markdown_table_row"
    disease = (
        cleaned.get("disease")
        or (context or {}).get("disease_standard_name")
        or "Hantavirus disease"
    )

    required_core = ("disease", "source_url", "source_type", "evidence_quote")
    field_values = {
        "disease": disease,
        "source_url": chunk.get("source_url"),
        "source_type": chunk.get("source_type"),
        "evidence_quote": evidence_quote,
    }
    missing_fields = [
        f
        for f in required_core
        if not field_values.get(f)
        or (isinstance(field_values.get(f), str) and not str(field_values[f]).strip())
    ]
    compatibility = assess_record_disease_compatibility(
        {
            **cleaned,
            "disease": disease,
            "evidence_quote": evidence_quote,
            "source_title": chunk.get("title"),
            "source_url": chunk.get("source_url"),
        },
        _as_disease_relevance_context(context),
    )

    return PublicHealthRecord(
        record_id=record_id,
        disease=disease,
        disease_standard_name=cleaned.get("disease_standard_name") or disease,
        disease_alias_used=cleaned.get("disease_alias_used")
        or _detect_disease_alias_used(text, context),
        virus_or_syndrome=cleaned.get("virus_or_syndrome"),
        pathogen_or_syndrome=cleaned.get("pathogen_or_syndrome")
        or _detect_pathogen_or_syndrome(text, context),
        target_population=(context or {}).get("target_population"),
        observation_type=cleaned.get("observation_type"),
        observation_types=list(cleaned.get("observation_types") or []),
        primary_case_dataset_eligible=cleaned.get(
            "primary_case_dataset_eligible"
        ),
        country=cleaned.get("country"),
        subnational_location=cleaned.get("subnational_location"),
        date_reported=cleaned.get("date_reported"),
        event_start_date=cleaned.get("event_start_date"),
        event_end_date=cleaned.get("event_end_date"),
        cases_confirmed=cleaned.get("cases_confirmed"),
        cases_probable=cleaned.get("cases_probable"),
        cases_suspected=cleaned.get("cases_suspected"),
        cases_unspecified=cleaned.get("cases_unspecified"),
        deaths=cleaned.get("deaths"),
        hospitalizations=cleaned.get("hospitalizations"),
        icu_admissions=cleaned.get("icu_admissions"),
        tests_positive=cleaned.get("tests_positive"),
        tests_total=cleaned.get("tests_total"),
        positivity_rate=cleaned.get("positivity_rate"),
        incidence_rate=cleaned.get("incidence_rate"),
        cumulative_count=cleaned.get("cumulative_count"),
        new_count=cleaned.get("new_count"),
        metric_name=cleaned.get("metric_name"),
        metric_value=cleaned.get("metric_value"),
        metric_unit=cleaned.get("metric_unit"),
        metric_category=cleaned.get("metric_category"),
        metric_denominator=cleaned.get("metric_denominator"),
        metric_period_start=cleaned.get("metric_period_start"),
        metric_period_end=cleaned.get("metric_period_end"),
        metric_period_source=cleaned.get("metric_period_source"),
        source_column_label=cleaned.get("source_column_label")
        or _row_or_chunk("source_column_label"),
        metric_column_label=cleaned.get("metric_column_label")
        or _row_or_chunk("metric_column_label"),
        metric_row_binding_status=metric_row_binding_status,
        metric_column_semantics_status=cleaned.get(
            "metric_column_semantics_status"
        ),
        resolved_column_period_type=cleaned.get("resolved_column_period_type"),
        column_period_resolution_reason=cleaned.get(
            "column_period_resolution_reason"
        ),
        column_period_warning_flags=list(
            cleaned.get("column_period_warning_flags") or []
        ),
        metric_period_label=cleaned.get("metric_period_label"),
        column_semantics_resolution_method=cleaned.get(
            "column_semantics_resolution_method"
        ),
        column_semantics_confidence=cleaned.get("column_semantics_confidence"),
        source_column_labels=list(_row_or_chunk("source_column_labels") or []),
        table_header=_row_or_chunk("table_header"),
        heading_context=_row_or_chunk("heading_context"),
        row_context_type=row_context_type,
        case_definition=cleaned.get("case_definition"),
        source_id=source_id,
        source_url=chunk.get("source_url"),
        source_type=chunk.get("source_type"),
        evidence_quote=evidence_quote,
        extraction_confidence=float(extraction_confidence),
        missing_fields=missing_fields,
        schema_status=None,
        provenance_status=None,
        supporting_chunk_id=supporting_chunk_id,
        source_row_id=source_row_id,
        source_title=chunk.get("title"),
        publisher=chunk.get("publisher"),
        source_role_final=chunk.get("source_role_final"),
        credibility_score=chunk.get("credibility_score"),
        credibility_level=chunk.get("credibility_level"),
        actual_publisher=chunk.get("actual_publisher"),
        actual_publisher_normalized=chunk.get("actual_publisher_normalized"),
        source_type_final=chunk.get("source_type_final"),
        source_independence_group=chunk.get("source_independence_group"),
        claim_support_role=chunk.get("claim_support_role"),
        recommended_source_role=chunk.get("recommended_source_role"),
        recommended_fetch_use=chunk.get("recommended_fetch_use"),
        recommended_extraction_use=chunk.get("recommended_extraction_use"),
        likely_syndicated_or_aggregated=chunk.get(
            "likely_syndicated_or_aggregated"
        ),
        upstream_source_mentions=list(chunk.get("upstream_source_mentions") or []),
        discovery_method=chunk.get("discovery_method"),
        search_provider=chunk.get("search_provider"),
        query_id=chunk.get("query_id"),
        query_used=chunk.get("query_used"),
        document_id=chunk.get("document_id"),
        document_type=chunk.get("document_type"),
        fetch_purpose=chunk.get("fetch_purpose"),
        chunk_kind=record_chunk_kind,
        data_types=record_data_types,
        context_types=record_context_types,
        extraction_method=llm_policy.llm_extraction_method,
        extraction_reason="LLM structured extraction from evidence chunk",
        validation_errors=[],
        repair_actions=[],
        requires_human_review=False,
        llm_used=True,
        llm_model=settings.get("model"),
        llm_provider=settings.get("provider"),
        llm_extraction_error=None,
        extraction_mode="llm",
        statistical_count_type=cleaned.get("statistical_count_type"),
        count_semantics=cleaned.get("count_semantics") or cleaned.get("statistical_count_type") or "unspecified",
        reporting_period=cleaned.get("reporting_period"),
        as_of_date=cleaned.get("as_of_date"),
        aggregation_level=cleaned.get("aggregation_level"),
        geographic_scope=cleaned.get("geographic_scope"),
        geographic_scope_type=cleaned.get("geographic_scope_type"),
        population_scope=cleaned.get("population_scope"),
        source_section=cleaned.get("source_section"),
        semantic_warnings=list(cleaned.get("semantic_warnings") or []),
        extraction_warnings=list(cleaned.get("semantic_warnings") or []),
        **record_compatibility_fields(compatibility),
        record_schema="generic_public_health_record",
        legacy_record_type=(
            "HantavirusRecord" if ((context or {}).get("is_hantavirus") is True) else None
        ),
    )


def _rule_based_extract_records_from_chunks(
    evidence_chunks: list[dict],
    deterministic_policy: StructuredExtractionPolicy,
    start_index: int = 1,
    only_chunk_ids: set[str] | None = None,
    context: dict | None = None,
) -> tuple[list[PublicHealthRecord], dict]:
    """Refactored deterministic loop; preserves Step 7 behavior."""

    records: list[PublicHealthRecord] = []
    chunk_index_by_source: dict[str, int] = {}
    target_data_count = 0
    extractable_count = 0
    skipped_count = 0
    skipped_context_only_chunk_count = 0
    skipped_context_only_source_ids: set[str] = set()
    skipped_disease_mismatch_chunk_count = 0
    skipped_disease_mismatch_source_ids: set[str] = set()
    field_counters: Counter = Counter()
    role_policy = load_source_role_policy()

    for chunk in evidence_chunks:
        if only_chunk_ids is not None and chunk.get("chunk_id") not in only_chunk_ids:
            continue
        if _is_context_only_chunk(chunk, role_policy) and (
            _direct_collection_enabled(context)
            or _chunk_has_explicit_context_only_role(chunk, role_policy)
        ):
            skipped_count += 1
            skipped_context_only_chunk_count += 1
            if chunk.get("source_id"):
                skipped_context_only_source_ids.add(chunk.get("source_id"))
            continue
        disease_blocked, disease_assessment = _chunk_blocked_by_disease_gate(
            chunk, context
        )
        if disease_blocked:
            skipped_count += 1
            skipped_disease_mismatch_chunk_count += 1
            if chunk.get("source_id"):
                skipped_disease_mismatch_source_ids.add(chunk.get("source_id"))
            continue
        if chunk.get("contains_target_data"):
            target_data_count += 1
        if not _chunk_is_extractable(chunk, deterministic_policy, context):
            skipped_count += 1
            continue
        extractable_count += 1
        source_id = chunk.get("source_id") or ""
        if source_id not in chunk_index_by_source:
            chunk_index_by_source[source_id] = start_index - 1
        chunk_index_by_source[source_id] += 1
        idx = chunk_index_by_source[source_id]

        record = _build_record_from_chunk(
            chunk,
            idx,
            deterministic_policy,
            context,
        )
        if record is None:
            core_records = _build_core_metric_records_from_chunk(
                chunk,
                idx,
                deterministic_policy,
                context,
            )
            if not core_records:
                skipped_count += 1
                chunk_index_by_source[source_id] -= 1
                continue
            records.extend(core_records)
            chunk_index_by_source[source_id] = (
                chunk_index_by_source.get(source_id, 0) + len(core_records) - 1
            )
            for core_record in core_records:
                rec_dict = core_record.model_dump()
                for field in _FIELD_DETECTION_KEYS:
                    if rec_dict.get(field) is not None:
                        field_counters[field] += 1
            continue
        records.append(record)
        rec_dict = record.model_dump()
        for field in _FIELD_DETECTION_KEYS:
            if rec_dict.get(field) is not None:
                field_counters[field] += 1
        core_records = _build_core_metric_records_from_chunk(
            chunk,
            idx + 1,
            deterministic_policy,
            context,
        )
        core_records = _filter_redundant_core_metric_records(
            record,
            core_records,
            context,
        )
        if core_records:
            records.extend(core_records)
            chunk_index_by_source[source_id] = (
                chunk_index_by_source.get(source_id, 0) + len(core_records)
            )
            for core_record in core_records:
                rec_dict = core_record.model_dump()
                for field in _FIELD_DETECTION_KEYS:
                    if rec_dict.get(field) is not None:
                        field_counters[field] += 1

    stats = {
        "target_data_chunk_count": target_data_count,
        "extractable_chunk_count": extractable_count,
        "skipped_chunk_count": skipped_count,
        "skipped_context_only_chunk_count": skipped_context_only_chunk_count,
        "skipped_context_only_source_ids": sorted(skipped_context_only_source_ids),
        "skipped_disease_mismatch_chunk_count": skipped_disease_mismatch_chunk_count,
        "skipped_disease_mismatch_source_ids": sorted(
            skipped_disease_mismatch_source_ids
        ),
        "field_detection_counts": {
            f: field_counters.get(f, 0) for f in _FIELD_DETECTION_KEYS
        },
    }
    return records, stats


def _chunk_text_preview(chunk: dict, *, max_chars: int = 280) -> str:
    text = str(chunk.get("row_quote") or chunk.get("text") or "")
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= max_chars:
        return text
    return f"{text[: max_chars - 3].rstrip()}..."


def _sample_chunks_for_source(
    evidence_chunks: list[dict],
    source_id: str,
    *,
    max_samples: int = 3,
) -> list[dict]:
    samples: list[dict] = []
    for chunk in evidence_chunks:
        if str(chunk.get("source_id") or "") != source_id:
            continue
        samples.append(
            {
                "chunk_id": chunk.get("chunk_id"),
                "chunk_kind": chunk.get("chunk_kind") or "text",
                "chunk_index": chunk.get("chunk_index"),
                "row_id": chunk.get("row_id"),
                "table_id": chunk.get("table_id"),
                "contains_target_data": chunk.get("contains_target_data"),
                "extraction_eligible_for_task_disease": (
                    chunk.get("extraction_eligible_for_task_disease")
                ),
                "disease_relevance_status": chunk.get("disease_relevance_status"),
                "data_types": list(chunk.get("data_types") or []),
                "context_types": list(chunk.get("context_types") or []),
                "text_preview": _chunk_text_preview(chunk),
            }
        )
        if len(samples) >= max_samples:
            break
    return samples


def _core_metric_extraction_gaps(
    evidence_chunks: list[dict],
    extraction_budget_by_source: dict[str, dict],
    context: dict | None,
) -> list[dict]:
    chunks_by_source: dict[str, list[dict]] = {}
    for chunk in evidence_chunks:
        source_id = str(chunk.get("source_id") or "")
        if source_id:
            chunks_by_source.setdefault(source_id, []).append(chunk)

    gaps: list[dict] = []
    for source_id, row in sorted(extraction_budget_by_source.items()):
        if int(row.get("attempted_count") or 0) <= 0:
            continue
        if int(row.get("record_count") or 0) > 0:
            continue
        source_chunks = chunks_by_source.get(str(source_id), [])
        core_chunks = [
            chunk
            for chunk in source_chunks
            if _chunk_looks_like_core_metric_text(chunk)
            and not _is_context_only_chunk(chunk, None)
            and (
                _chunk_is_task_collection_candidate(chunk, context)
                or _chunk_is_official_or_high_trust(chunk, context)
            )
        ]
        if not core_chunks:
            continue
        gaps.append(
            {
                "source_id": source_id,
                "reason": "core_metric_text_attempted_but_no_records_extracted",
                "budget": dict(row),
                "sample_chunks": _sample_chunks_for_source(
                    evidence_chunks, source_id
                ),
                "core_metric_chunk_count": len(core_chunks),
            }
        )
    return gaps


def _llm_extract_records_from_chunks(
    evidence_chunks: list[dict],
    llm_policy: LLMStructuredExtractionPolicy,
    deterministic_policy: StructuredExtractionPolicy,
    fallback_to_rule_based: bool,
    context: dict | None = None,
) -> tuple[list[PublicHealthRecord], dict]:
    """LLM extraction loop with optional per-chunk deterministic fallback."""

    settings = llm_clients.get_llm_settings()
    records: list[PublicHealthRecord] = []
    chunk_index_by_source: dict[str, int] = {}
    llm_eligible_chunk_count = 0
    llm_call_count = 0
    llm_success_count = 0
    llm_empty_output_count = 0
    llm_error_count = 0
    llm_fallback_count = 0
    rule_based_fallback_record_count = 0
    llm_error_messages: list[str] = []
    target_data_count = 0
    max_chunks = _parse_llm_max_chunks()
    llm_skipped_due_to_chunk_cap_count = 0
    skipped_context_only_chunk_count = 0
    skipped_context_only_source_ids: set[str] = set()
    skipped_disease_mismatch_chunk_count = 0
    skipped_disease_mismatch_source_ids: set[str] = set()
    must_fetch_disease_gate_bypass_count = 0
    extraction_budget_by_source: dict[str, dict] = {}
    official_extraction_queue: list[dict] = []
    role_policy = load_source_role_policy()
    ordered_chunks = _ordered_llm_chunks(evidence_chunks, context)
    processed_metric_row_chunk_ids: set[str] = set()
    batched_metric_row_call_count = 0
    metric_row_batch_record_count = 0
    metric_row_record_count_by_source: dict[str, int] = {}
    deterministic_metric_row_record_count = 0
    fallback_text_chunk_call_count = 0
    skipped_text_fallback_after_row_record_count = 0
    target_source_llm_call_count = 0
    skipped_context_extraction_count = 0
    no_task_collection_document = False
    extraction_blocking_reason: str | None = None
    has_target_source_chunks = any(
        _chunk_priority(chunk, context) <= 1
        for chunk in ordered_chunks
        if isinstance(chunk, dict)
    )
    if _direct_should_skip_non_target_extraction(ordered_chunks, context):
        for chunk in ordered_chunks:
            if not isinstance(chunk, dict):
                continue
            budget_row = _source_budget_row(extraction_budget_by_source, chunk, context)
            budget_row["queued_count"] += 1
            budget_row["skipped_context_only_count"] += 1
        skipped_context_extraction_count += sum(
            1 for chunk in ordered_chunks if isinstance(chunk, dict)
        )
        no_task_collection_document = True
        extraction_blocking_reason = "no_task_collection_document"
        ordered_chunks = []
        has_target_source_chunks = False
    target_source_attempted = False

    metric_row_groups: dict[tuple[str, str], list[dict]] = {}
    metric_row_group_order: list[tuple[str, str]] = []
    if _direct_collection_enabled(context):
        for chunk in ordered_chunks:
            if not isinstance(chunk, dict) or not _chunk_is_metric_row(chunk):
                continue
            source_id = str(chunk.get("source_id") or "")
            budget_row = _source_budget_row(extraction_budget_by_source, chunk, context)
            budget_row["queued_count"] += 1
            if _is_context_only_chunk(chunk, role_policy) and (
                _direct_collection_enabled(context)
                or _chunk_has_explicit_context_only_role(chunk, role_policy)
            ):
                skipped_context_only_chunk_count += 1
                budget_row["skipped_context_only_count"] += 1
                if source_id:
                    skipped_context_only_source_ids.add(source_id)
                processed_metric_row_chunk_ids.add(str(chunk.get("chunk_id") or ""))
                continue
            disease_blocked, _ = _chunk_blocked_by_disease_gate(chunk, context)
            direct_must_fetch_bypass = (
                disease_blocked
                and _chunk_is_must_fetch(chunk, context)
            )
            if disease_blocked and not direct_must_fetch_bypass:
                skipped_disease_mismatch_chunk_count += 1
                budget_row["skipped_disease_mismatch_count"] += 1
                if source_id:
                    skipped_disease_mismatch_source_ids.add(source_id)
                processed_metric_row_chunk_ids.add(str(chunk.get("chunk_id") or ""))
                continue
            if direct_must_fetch_bypass:
                must_fetch_disease_gate_bypass_count += 1
            if not _direct_llm_chunk_allowed(chunk, llm_policy, context):
                continue
            llm_eligible_chunk_count += 1
            budget_row["eligible_count"] += 1
            deterministic_records = _deterministic_metric_row_records(
                chunk,
                start_index=chunk_index_by_source.get(source_id, 0) + 1,
                llm_policy=llm_policy,
                settings=settings,
                context=context,
            )
            if deterministic_records:
                records.extend(deterministic_records)
                metric_row_record_count_by_source[source_id] = (
                    metric_row_record_count_by_source.get(source_id, 0)
                    + len(deterministic_records)
                )
                chunk_index_by_source[source_id] = (
                    chunk_index_by_source.get(source_id, 0)
                    + len(deterministic_records)
                )
                deterministic_metric_row_record_count += len(deterministic_records)
                metric_row_batch_record_count += len(deterministic_records)
                budget_row["attempted_count"] += 1
                budget_row["record_count"] += len(deterministic_records)
                processed_metric_row_chunk_ids.add(str(chunk.get("chunk_id") or ""))
                if _chunk_priority(chunk, context) <= 1:
                    target_source_attempted = True
                emit_workflow_progress(
                    "structured_extraction",
                    "Deterministic metric-row split completed",
                    {
                        "chunk_id": chunk.get("chunk_id"),
                        "source_id": source_id,
                        "record_count": len(deterministic_records),
                    },
                    status="completed",
                )
                continue
            key = _metric_row_key(chunk)
            if key not in metric_row_groups:
                metric_row_groups[key] = []
                metric_row_group_order.append(key)
            metric_row_groups[key].append(chunk)

    metric_row_batch_size = max(1, _metric_row_batch_size())
    for key in metric_row_group_order:
        rows = metric_row_groups.get(key) or []
        for offset in range(0, len(rows), metric_row_batch_size):
            batch_rows = rows[offset : offset + metric_row_batch_size]
            if not batch_rows:
                continue
            if max_chunks is not None and llm_call_count >= max_chunks:
                llm_skipped_due_to_chunk_cap_count += len(batch_rows)
                for row in batch_rows:
                    budget_row = _source_budget_row(
                        extraction_budget_by_source, row, context
                    )
                    budget_row["skipped_due_to_cap_count"] += 1
                    processed_metric_row_chunk_ids.add(str(row.get("chunk_id") or ""))
                continue
            batch_chunk = _make_metric_row_batch_chunk(
                batch_rows,
                batch_index=(offset // metric_row_batch_size) + 1,
            )
            chunk_for_llm = _chunk_with_task_context(batch_chunk, context)
            llm_call_count += 1
            batched_metric_row_call_count += 1
            source_id = str(batch_chunk.get("source_id") or "")
            if _chunk_priority(batch_chunk, context) <= 1:
                target_source_attempted = True
                target_source_llm_call_count += 1
            for row in batch_rows:
                budget_row = _source_budget_row(
                    extraction_budget_by_source, row, context
                )
                budget_row["attempted_count"] += 1
                processed_metric_row_chunk_ids.add(str(row.get("chunk_id") or ""))
            emit_workflow_progress(
                "structured_extraction",
                "LLM metric-row batch extraction started",
                {
                    "chunk_id": batch_chunk.get("chunk_id"),
                    "source_id": source_id,
                    "row_count": len(batch_rows),
                    "llm_call_count": llm_call_count,
                    "max_chunks": max_chunks,
                },
            )
            try:
                output = llm_clients.extract_chunk_with_llm(chunk_for_llm, llm_policy)
                llm_success_count += 1
                if not output.records:
                    llm_empty_output_count += 1
                record_limit = max(llm_policy.max_records_per_chunk, len(batch_rows))
                for llm_record in output.records[:record_limit]:
                    chunk_index_by_source[source_id] = chunk_index_by_source.get(source_id, 0) + 1
                    idx = chunk_index_by_source[source_id]
                    record = _build_record_from_llm_output(
                        llm_record, chunk_for_llm, idx, llm_policy, settings, context
                    )
                    if record is None:
                        chunk_index_by_source[source_id] -= 1
                        continue
                    records.append(record)
                    metric_row_batch_record_count += 1
                    metric_row_record_count_by_source[source_id] = (
                        metric_row_record_count_by_source.get(source_id, 0) + 1
                    )
                    for row in batch_rows:
                        if row.get("row_id") == record.source_row_id:
                            budget_row = _source_budget_row(
                                extraction_budget_by_source, row, context
                            )
                            budget_row["record_count"] += 1
                            break
                emit_workflow_progress(
                    "structured_extraction",
                    "LLM metric-row batch extraction completed",
                    {
                        "chunk_id": batch_chunk.get("chunk_id"),
                        "source_id": source_id,
                        "record_count": len(output.records),
                        "llm_success_count": llm_success_count,
                    },
                    status="completed",
                )
            except Exception as exc:  # noqa: BLE001
                llm_error_count += 1
                llm_error_messages.append(f"{type(exc).__name__}: {exc}")
                emit_workflow_progress(
                    "structured_extraction",
                    "LLM metric-row batch extraction failed",
                    {
                        "chunk_id": batch_chunk.get("chunk_id"),
                        "source_id": source_id,
                        "error_type": exc.__class__.__name__,
                    },
                    status="error",
                )

    for queue_index, chunk in enumerate(ordered_chunks, start=1):
        chunk_id = str(chunk.get("chunk_id") or "")
        if chunk_id and chunk_id in processed_metric_row_chunk_ids:
            continue
        source_id = str(chunk.get("source_id") or "")
        budget_row = _source_budget_row(extraction_budget_by_source, chunk, context)
        budget_row["queued_count"] += 1
        priority = _chunk_priority(chunk, context)
        if priority <= 1:
            official_extraction_queue.append(
                {
                    "queue_index": queue_index,
                    "source_id": source_id,
                    "official_report_key": budget_row.get("official_report_key"),
                    "chunk_id": chunk.get("chunk_id"),
                    "priority": "must_fetch" if priority == 0 else "official_or_high_trust",
                    "must_fetch": _chunk_is_must_fetch(chunk, context),
                    "official_or_high_trust": _chunk_is_official_or_high_trust(chunk, context),
                    "chunk_index": chunk.get("chunk_index"),
                    "title": chunk.get("title"),
                    "source_url": chunk.get("source_url"),
                }
            )
        if _is_context_only_chunk(chunk, role_policy) and (
            _direct_collection_enabled(context)
            or _chunk_has_explicit_context_only_role(chunk, role_policy)
        ):
            skipped_context_only_chunk_count += 1
            budget_row["skipped_context_only_count"] += 1
            if chunk.get("source_id"):
                skipped_context_only_source_ids.add(chunk.get("source_id"))
            continue
        disease_blocked, disease_assessment = _chunk_blocked_by_disease_gate(
            chunk, context
        )
        direct_must_fetch_bypass = (
            disease_blocked
            and _direct_collection_enabled(context)
            and _chunk_is_must_fetch(chunk, context)
        )
        if disease_blocked and not direct_must_fetch_bypass:
            skipped_disease_mismatch_chunk_count += 1
            budget_row["skipped_disease_mismatch_count"] += 1
            if chunk.get("source_id"):
                skipped_disease_mismatch_source_ids.add(chunk.get("source_id"))
            continue
        if direct_must_fetch_bypass:
            must_fetch_disease_gate_bypass_count += 1
        if chunk.get("contains_target_data") or direct_must_fetch_bypass:
            target_data_count += 1
        if not _direct_llm_chunk_allowed(chunk, llm_policy, context):
            continue
        if (
            _direct_collection_enabled(context)
            and metric_row_batch_record_count >= _direct_min_target_metric_records()
        ):
            if not _direct_text_fallback_after_row_extraction_enabled():
                source_metric_row_records = metric_row_record_count_by_source.get(
                    source_id, 0
                )
                if source_metric_row_records >= _direct_min_target_metric_records():
                    skipped_text_fallback_after_row_record_count += 1
                    budget_row["skipped_text_fallback_after_row_record_count"] = (
                        budget_row.get("skipped_text_fallback_after_row_record_count", 0)
                        + 1
                    )
                    continue
                if str(budget_row.get("budget_bucket")) != "verified_target_collection":
                    skipped_context_extraction_count += 1
                    budget_row["skipped_context_only_count"] += 1
                    continue
            if str(budget_row.get("budget_bucket")) != "verified_target_collection":
                skipped_context_extraction_count += 1
                budget_row["skipped_context_only_count"] += 1
                continue
        llm_eligible_chunk_count += 1
        budget_row["eligible_count"] += 1
        # Enforce the optional per-run LLM chunk cap. Once the cap has been
        # reached, additional eligible chunks are counted but skipped without
        # incurring further LLM calls.
        if max_chunks is not None and llm_call_count >= max_chunks:
            llm_skipped_due_to_chunk_cap_count += 1
            budget_row["skipped_due_to_cap_count"] += 1
            continue
        llm_call_count += 1
        if str(chunk.get("chunk_kind") or "") != "metric_row_batch":
            fallback_text_chunk_call_count += 1
        if (
            has_target_source_chunks
            and not target_source_attempted
            and str(budget_row.get("budget_bucket")) != "verified_target_collection"
        ):
            budget_row["attempted_before_target_sources"] = True
        if str(budget_row.get("budget_bucket")) == "verified_target_collection":
            target_source_attempted = True
            target_source_llm_call_count += 1
        budget_row["attempted_count"] += 1
        emit_workflow_progress(
            "structured_extraction",
            "LLM extraction chunk started",
            {
                "chunk_id": chunk.get("chunk_id"),
                "source_id": source_id,
                "llm_call_count": llm_call_count,
                "max_chunks": max_chunks,
            },
        )

        try:
            chunk_for_llm = _chunk_with_task_context(chunk, context)
            output = llm_clients.extract_chunk_with_llm(chunk_for_llm, llm_policy)
            llm_success_count += 1
            if not output.records:
                llm_empty_output_count += 1
                if (
                    fallback_to_rule_based
                    and str(chunk.get("chunk_kind") or "") != "metric_row_batch"
                    and _core_metric_payloads_from_chunk(chunk, context)
                ):
                    llm_fallback_count += 1
                    start_idx = chunk_index_by_source.get(source_id, 0) + 1
                    fallback_records, _ = _rule_based_extract_records_from_chunks(
                        [chunk],
                        deterministic_policy,
                        start_index=start_idx,
                        context=context,
                    )
                    rule_based_fallback_record_count += len(fallback_records)
                    records.extend(fallback_records)
                    budget_row["record_count"] += len(fallback_records)
                    chunk_index_by_source[source_id] = (
                        chunk_index_by_source.get(source_id, 0)
                        + len(fallback_records)
                    )
            emit_workflow_progress(
                "structured_extraction",
                "LLM extraction chunk completed",
                {
                    "chunk_id": chunk.get("chunk_id"),
                    "source_id": source_id,
                    "record_count": len(output.records),
                    "llm_success_count": llm_success_count,
                },
                status="completed",
            )
            for llm_record in output.records[: llm_policy.max_records_per_chunk]:
                chunk_index_by_source[source_id] = chunk_index_by_source.get(source_id, 0) + 1
                idx = chunk_index_by_source[source_id]
                record = _build_record_from_llm_output(
                    llm_record, chunk_for_llm, idx, llm_policy, settings, context
                )
                if record is None:
                    chunk_index_by_source[source_id] -= 1
                    continue
                records.append(record)
                budget_row["record_count"] += 1
        except Exception as exc:  # noqa: BLE001 — caller decides fallback
            llm_error_count += 1
            llm_error_messages.append(f"{type(exc).__name__}: {exc}")
            if fallback_to_rule_based:
                llm_fallback_count += 1
                start_idx = chunk_index_by_source.get(source_id, 0) + 1
                fallback_records, _ = _rule_based_extract_records_from_chunks(
                    [chunk],
                    deterministic_policy,
                    start_index=start_idx,
                    context=context,
                )
                rule_based_fallback_record_count += len(fallback_records)
                records.extend(fallback_records)
                budget_row["record_count"] += len(fallback_records)
                chunk_index_by_source[source_id] = (
                    chunk_index_by_source.get(source_id, 0) + len(fallback_records)
                )
            emit_workflow_progress(
                "structured_extraction",
                "LLM extraction chunk failed",
                {
                    "chunk_id": chunk.get("chunk_id"),
                    "source_id": source_id,
                    "error_type": exc.__class__.__name__,
                    "fallback_to_rule_based": fallback_to_rule_based,
                },
                status="error",
            )

    field_counters: Counter = Counter()
    for record in records:
        rec_dict = record.model_dump()
        for field in _FIELD_DETECTION_KEYS:
            if rec_dict.get(field) is not None:
                field_counters[field] += 1
    successful_official_report_keys = {
        str(row.get("official_report_key"))
        for row in extraction_budget_by_source.values()
        if row.get("official_report_key") and int(row.get("record_count") or 0) > 0
    }
    official_extraction_failures: list[dict] = []
    official_extraction_resolved_by_equivalent_sources: list[dict] = []
    must_fetch_ids = {str(v) for v in (context or {}).get("must_fetch_source_ids") or []}
    for source_id in sorted(must_fetch_ids):
        row = extraction_budget_by_source.get(source_id)
        if not row:
            continue
        if int(row.get("record_count") or 0) > 0:
            continue
        official_report_key = row.get("official_report_key")
        if official_report_key and official_report_key in successful_official_report_keys:
            official_extraction_resolved_by_equivalent_sources.append(
                {
                    "source_id": source_id,
                    "official_report_key": official_report_key,
                    "reason": "resolved_by_equivalent_source",
                    "budget": dict(row),
                }
            )
            continue
        reason = "must_fetch_source_produced_no_records"
        if int(row.get("attempted_count") or 0) == 0:
            reason = "must_fetch_source_not_attempted_for_extraction"
        elif int(row.get("skipped_due_to_cap_count") or 0) > 0:
            reason = "must_fetch_source_partially_skipped_due_to_chunk_cap"
        official_extraction_failures.append(
            {
                "source_id": source_id,
                "reason": reason,
                "budget": dict(row),
                "sample_chunks": _sample_chunks_for_source(evidence_chunks, source_id),
            }
        )

    core_metric_extraction_gaps = _core_metric_extraction_gaps(
        evidence_chunks,
        extraction_budget_by_source,
        context,
    )

    stats = {
        "extraction_mode": "llm_structured_output",
        "llm_enabled": True,
        "llm_provider": settings.get("provider"),
        "llm_model": settings.get("model"),
        "llm_eligible_chunk_count": llm_eligible_chunk_count,
        "llm_call_count": llm_call_count,
        "llm_success_count": llm_success_count,
        "llm_empty_output_count": llm_empty_output_count,
        "llm_error_count": llm_error_count,
        "llm_fallback_count": llm_fallback_count,
        "llm_error_messages": llm_error_messages,
        "rule_based_fallback_record_count": rule_based_fallback_record_count,
        "target_data_chunk_count": target_data_count,
        "extractable_chunk_count": llm_eligible_chunk_count,
        "field_detection_counts": {
            f: field_counters.get(f, 0) for f in _FIELD_DETECTION_KEYS
        },
        "llm_max_chunks": max_chunks,
        "llm_skipped_due_to_chunk_cap_count": llm_skipped_due_to_chunk_cap_count,
        "skipped_context_only_chunk_count": skipped_context_only_chunk_count,
        "skipped_context_only_source_ids": sorted(skipped_context_only_source_ids),
        "skipped_disease_mismatch_chunk_count": skipped_disease_mismatch_chunk_count,
        "skipped_disease_mismatch_source_ids": sorted(
            skipped_disease_mismatch_source_ids
        ),
        "must_fetch_disease_gate_bypass_count": must_fetch_disease_gate_bypass_count,
        "official_extraction_queue": official_extraction_queue,
        "batched_metric_row_call_count": batched_metric_row_call_count,
        "metric_row_batch_record_count": metric_row_batch_record_count,
        "metric_row_record_count_by_source": dict(
            sorted(metric_row_record_count_by_source.items())
        ),
        "deterministic_metric_row_record_count": deterministic_metric_row_record_count,
        "fallback_text_chunk_call_count": fallback_text_chunk_call_count,
        "skipped_text_fallback_after_row_record_count": (
            skipped_text_fallback_after_row_record_count
        ),
        "target_source_llm_call_count": target_source_llm_call_count,
        "skipped_context_extraction_count": skipped_context_extraction_count,
        "no_task_collection_document": no_task_collection_document,
        "extraction_blocking_reason": extraction_blocking_reason,
        "official_extraction_failures": official_extraction_failures,
        "core_metric_extraction_gaps": core_metric_extraction_gaps,
        "core_metric_extraction_gap_count": len(core_metric_extraction_gaps),
        "official_extraction_resolved_by_equivalent_sources": (
            official_extraction_resolved_by_equivalent_sources
        ),
        "official_extraction_resolved_by_equivalent_source_count": len(
            official_extraction_resolved_by_equivalent_sources
        ),
        "extraction_budget_by_source": extraction_budget_by_source,
    }
    return records, stats


def structured_extraction(state: DataCollectionState) -> dict:
    """Convert target-data evidence chunks into generic public-health records.

    Default = deterministic rule-based extraction. When
    `HDC_ENABLE_LLM_EXTRACTION=true`, run the optional LLM extractor with
    per-chunk fallback to the deterministic extractor when configured.
    """

    deterministic_policy = StructuredExtractionPolicy(
        **load_structured_extraction_policy()
    )
    llm_policy = _load_llm_policy()
    chunks = list(state.get("evidence_chunks") or [])
    extraction_context = _build_extraction_context(state, deterministic_policy)

    llm_enabled = llm_clients.llm_extraction_enabled()
    fallback_to_rule_based = llm_clients.llm_fallback_to_rule_based()

    if llm_enabled:
        records, llm_stats = _llm_extract_records_from_chunks(
            chunks,
            llm_policy,
            deterministic_policy,
            fallback_to_rule_based,
            extraction_context,
        )
        raw_record_dicts = [r.model_dump() for r in records]
        skipped_count = max(
            0,
            len(chunks)
            - int(llm_stats.get("extractable_chunk_count", 0)),
        )
        summary = {
            "input_chunk_count": len(chunks),
            "target_data_chunk_count": llm_stats.get("target_data_chunk_count", 0),
            "extractable_chunk_count": llm_stats.get("extractable_chunk_count", 0),
            "raw_record_count": len(records),
            "skipped_chunk_count": skipped_count,
            "extraction_method": llm_policy.llm_extraction_method,
            "field_detection_counts": llm_stats.get("field_detection_counts") or {},
            "extraction_mode": "llm_structured_output",
            "llm_enabled": True,
            "llm_provider": llm_stats.get("llm_provider"),
            "llm_model": llm_stats.get("llm_model"),
            "llm_eligible_chunk_count": llm_stats.get("llm_eligible_chunk_count", 0),
            "llm_call_count": llm_stats.get("llm_call_count", 0),
            "llm_success_count": llm_stats.get("llm_success_count", 0),
            "llm_empty_output_count": llm_stats.get("llm_empty_output_count", 0),
            "llm_error_count": llm_stats.get("llm_error_count", 0),
            "llm_fallback_count": llm_stats.get("llm_fallback_count", 0),
            "rule_based_fallback_record_count": llm_stats.get(
                "rule_based_fallback_record_count", 0
            ),
            "core_metric_extraction_gaps": llm_stats.get(
                "core_metric_extraction_gaps"
            )
            or [],
            "core_metric_extraction_gap_count": llm_stats.get(
                "core_metric_extraction_gap_count", 0
            ),
            "skipped_context_only_chunk_count": llm_stats.get(
                "skipped_context_only_chunk_count", 0
            ),
            "skipped_context_only_source_ids": llm_stats.get(
                "skipped_context_only_source_ids"
            )
            or [],
            "skipped_disease_mismatch_chunk_count": llm_stats.get(
                "skipped_disease_mismatch_chunk_count", 0
            ),
            "skipped_disease_mismatch_source_ids": llm_stats.get(
                "skipped_disease_mismatch_source_ids"
            )
            or [],
            "llm_max_chunks": llm_stats.get("llm_max_chunks"),
            "llm_skipped_due_to_chunk_cap_count": llm_stats.get(
                "llm_skipped_due_to_chunk_cap_count", 0
            ),
            "must_fetch_disease_gate_bypass_count": llm_stats.get(
                "must_fetch_disease_gate_bypass_count", 0
            ),
            "official_extraction_queue": llm_stats.get("official_extraction_queue")
            or [],
            "batched_metric_row_call_count": llm_stats.get(
                "batched_metric_row_call_count", 0
            ),
            "metric_row_batch_record_count": llm_stats.get(
                "metric_row_batch_record_count", 0
            ),
            "metric_row_record_count_by_source": llm_stats.get(
                "metric_row_record_count_by_source"
            )
            or {},
            "deterministic_metric_row_record_count": llm_stats.get(
                "deterministic_metric_row_record_count", 0
            ),
            "fallback_text_chunk_call_count": llm_stats.get(
                "fallback_text_chunk_call_count", 0
            ),
            "skipped_text_fallback_after_row_record_count": llm_stats.get(
                "skipped_text_fallback_after_row_record_count", 0
            ),
            "target_source_llm_call_count": llm_stats.get(
                "target_source_llm_call_count", 0
            ),
            "skipped_context_extraction_count": llm_stats.get(
                "skipped_context_extraction_count", 0
            ),
            "no_task_collection_document": bool(
                llm_stats.get("no_task_collection_document", False)
            ),
            "extraction_blocking_reason": llm_stats.get(
                "extraction_blocking_reason"
            ),
            "official_extraction_failures": llm_stats.get(
                "official_extraction_failures"
            )
            or [],
            "core_metric_extraction_gaps": llm_stats.get(
                "core_metric_extraction_gaps"
            )
            or [],
            "core_metric_extraction_gap_count": llm_stats.get(
                "core_metric_extraction_gap_count", 0
            ),
            "official_extraction_resolved_by_equivalent_sources": llm_stats.get(
                "official_extraction_resolved_by_equivalent_sources"
            )
            or [],
            "official_extraction_resolved_by_equivalent_source_count": llm_stats.get(
                "official_extraction_resolved_by_equivalent_source_count",
                0,
            ),
            "extraction_budget_by_source": llm_stats.get(
                "extraction_budget_by_source"
            )
            or {},
        }
        llm_summary = {
            "extraction_mode": "llm_structured_output",
            "llm_enabled": True,
            "llm_provider": llm_stats.get("llm_provider"),
            "llm_model": llm_stats.get("llm_model"),
            "llm_eligible_chunk_count": llm_stats.get("llm_eligible_chunk_count", 0),
            "llm_call_count": llm_stats.get("llm_call_count", 0),
            "llm_success_count": llm_stats.get("llm_success_count", 0),
            "llm_empty_output_count": llm_stats.get("llm_empty_output_count", 0),
            "llm_error_count": llm_stats.get("llm_error_count", 0),
            "llm_fallback_count": llm_stats.get("llm_fallback_count", 0),
            "llm_error_messages": llm_stats.get("llm_error_messages") or [],
            "rule_based_fallback_record_count": llm_stats.get(
                "rule_based_fallback_record_count", 0
            ),
            "skipped_context_only_chunk_count": llm_stats.get(
                "skipped_context_only_chunk_count", 0
            ),
            "skipped_context_only_source_ids": llm_stats.get(
                "skipped_context_only_source_ids"
            )
            or [],
            "skipped_disease_mismatch_chunk_count": llm_stats.get(
                "skipped_disease_mismatch_chunk_count", 0
            ),
            "skipped_disease_mismatch_source_ids": llm_stats.get(
                "skipped_disease_mismatch_source_ids"
            )
            or [],
            "fallback_to_rule_based": fallback_to_rule_based,
            "llm_max_chunks": llm_stats.get("llm_max_chunks"),
            "llm_skipped_due_to_chunk_cap_count": llm_stats.get(
                "llm_skipped_due_to_chunk_cap_count", 0
            ),
            "must_fetch_disease_gate_bypass_count": llm_stats.get(
                "must_fetch_disease_gate_bypass_count", 0
            ),
            "official_extraction_failure_count": len(
                llm_stats.get("official_extraction_failures") or []
            ),
            "batched_metric_row_call_count": llm_stats.get(
                "batched_metric_row_call_count", 0
            ),
            "metric_row_batch_record_count": llm_stats.get(
                "metric_row_batch_record_count", 0
            ),
            "metric_row_record_count_by_source": llm_stats.get(
                "metric_row_record_count_by_source"
            )
            or {},
            "deterministic_metric_row_record_count": llm_stats.get(
                "deterministic_metric_row_record_count", 0
            ),
            "fallback_text_chunk_call_count": llm_stats.get(
                "fallback_text_chunk_call_count", 0
            ),
            "target_source_llm_call_count": llm_stats.get(
                "target_source_llm_call_count", 0
            ),
            "skipped_context_extraction_count": llm_stats.get(
                "skipped_context_extraction_count", 0
            ),
            "no_task_collection_document": bool(
                llm_stats.get("no_task_collection_document", False)
            ),
            "extraction_blocking_reason": llm_stats.get(
                "extraction_blocking_reason"
            ),
            "official_extraction_resolved_by_equivalent_source_count": llm_stats.get(
                "official_extraction_resolved_by_equivalent_source_count",
                0,
            ),
        }
    else:
        records, det_stats = _rule_based_extract_records_from_chunks(
            chunks, deterministic_policy, context=extraction_context
        )
        deterministic_metric_row_record_count = 0
        chunk_index_by_source: dict[str, int] = {}
        for chunk in chunks:
            if not isinstance(chunk, dict) or not _chunk_is_metric_row(chunk):
                continue
            source_id = str(chunk.get("source_id") or "")
            deterministic_records = _deterministic_metric_row_records(
                chunk,
                start_index=chunk_index_by_source.get(source_id, 0) + 1,
                llm_policy=llm_policy,
                settings=llm_clients.get_llm_settings(),
                context=extraction_context,
            )
            if not deterministic_records:
                continue
            records.extend(deterministic_records)
            chunk_index_by_source[source_id] = (
                chunk_index_by_source.get(source_id, 0)
                + len(deterministic_records)
            )
            deterministic_metric_row_record_count += len(deterministic_records)
        raw_record_dicts = [r.model_dump() for r in records]
        summary = {
            "input_chunk_count": len(chunks),
            "target_data_chunk_count": det_stats["target_data_chunk_count"],
            "extractable_chunk_count": det_stats["extractable_chunk_count"],
            "raw_record_count": len(records),
            "skipped_chunk_count": det_stats["skipped_chunk_count"],
            "extraction_method": deterministic_policy.extraction_method,
            "field_detection_counts": det_stats["field_detection_counts"],
            "skipped_context_only_chunk_count": det_stats.get(
                "skipped_context_only_chunk_count", 0
            ),
            "skipped_context_only_source_ids": det_stats.get(
                "skipped_context_only_source_ids"
            )
            or [],
            "skipped_disease_mismatch_chunk_count": det_stats.get(
                "skipped_disease_mismatch_chunk_count", 0
            ),
            "skipped_disease_mismatch_source_ids": det_stats.get(
                "skipped_disease_mismatch_source_ids"
            )
            or [],
            "extraction_mode": "deterministic_rule_based",
            "llm_enabled": False,
            "llm_call_count": 0,
            "llm_success_count": 0,
            "llm_error_count": 0,
            "llm_fallback_count": 0,
            "llm_max_chunks": _parse_llm_max_chunks(),
            "llm_skipped_due_to_chunk_cap_count": 0,
            "must_fetch_disease_gate_bypass_count": 0,
            "official_extraction_queue": [],
            "official_extraction_failures": [],
            "extraction_budget_by_source": {},
            "batched_metric_row_call_count": 0,
            "metric_row_batch_record_count": deterministic_metric_row_record_count,
            "deterministic_metric_row_record_count": deterministic_metric_row_record_count,
            "fallback_text_chunk_call_count": 0,
            "target_source_llm_call_count": 0,
            "skipped_context_extraction_count": 0,
        }
        llm_summary = {
            "extraction_mode": "deterministic_rule_based",
            "llm_enabled": False,
            "llm_provider": None,
            "llm_model": None,
            "llm_eligible_chunk_count": 0,
            "llm_call_count": 0,
            "llm_success_count": 0,
            "llm_empty_output_count": 0,
            "llm_error_count": 0,
            "llm_fallback_count": 0,
            "llm_error_messages": [],
            "rule_based_fallback_record_count": 0,
            "fallback_to_rule_based": fallback_to_rule_based,
            "skipped_disease_mismatch_chunk_count": det_stats.get(
                "skipped_disease_mismatch_chunk_count", 0
            ),
            "skipped_disease_mismatch_source_ids": det_stats.get(
                "skipped_disease_mismatch_source_ids"
            )
            or [],
            "llm_max_chunks": _parse_llm_max_chunks(),
            "llm_skipped_due_to_chunk_cap_count": 0,
            "must_fetch_disease_gate_bypass_count": 0,
            "official_extraction_failure_count": 0,
            "batched_metric_row_call_count": 0,
            "metric_row_batch_record_count": deterministic_metric_row_record_count,
            "deterministic_metric_row_record_count": deterministic_metric_row_record_count,
            "fallback_text_chunk_call_count": 0,
            "target_source_llm_call_count": 0,
            "skipped_context_extraction_count": 0,
        }

    record_task_fit_assessments = _record_task_fit_assessments(
        raw_record_dicts,
        extraction_context,
    )
    disease_counts = dict(
        Counter(str(r.get("disease") or "unknown") for r in raw_record_dicts)
    )
    source_type_counts = dict(
        Counter(str(r.get("source_type") or "unknown") for r in raw_record_dicts)
    )
    extraction_method_counts = dict(
        Counter(str(r.get("extraction_method") or "unknown") for r in raw_record_dicts)
    )
    warning_counter: Counter = Counter()
    for record in raw_record_dicts:
        for warning in (record.get("semantic_warnings") or []) + (
            record.get("extraction_warnings") or []
        ):
            warning_counter[warning] += 1
    metric_row_extraction_audit = [
        {
            "record_id": record.get("record_id"),
            "source_id": record.get("source_id"),
            "document_id": record.get("document_id"),
            "supporting_chunk_id": record.get("supporting_chunk_id"),
            "chunk_kind": record.get("chunk_kind"),
            "metric_name": record.get("metric_name"),
            "metric_value": record.get("metric_value"),
            "metric_unit": record.get("metric_unit"),
            "metric_category": record.get("metric_category"),
            "metric_denominator": record.get("metric_denominator"),
            "metric_period_start": record.get("metric_period_start"),
            "metric_period_end": record.get("metric_period_end"),
            "metric_period_source": record.get("metric_period_source"),
            "source_row_id": record.get("source_row_id"),
            "source_column_label": record.get("source_column_label"),
            "metric_column_label": record.get("metric_column_label"),
            "metric_row_binding_status": record.get("metric_row_binding_status"),
            "metric_column_semantics_status": record.get(
                "metric_column_semantics_status"
            ),
            "resolved_column_period_type": record.get(
                "resolved_column_period_type"
            ),
            "column_period_resolution_reason": record.get(
                "column_period_resolution_reason"
            ),
            "column_period_warning_flags": record.get(
                "column_period_warning_flags"
            )
            or [],
            "metric_period_label": record.get("metric_period_label"),
            "column_semantics_resolution_method": record.get(
                "column_semantics_resolution_method"
            ),
            "column_semantics_confidence": record.get(
                "column_semantics_confidence"
            ),
            "table_header": record.get("table_header"),
            "heading_context": record.get("heading_context"),
            "row_context_type": record.get("row_context_type"),
            "row_quote": record.get("row_quote") or record.get("evidence_quote"),
            "semantic_warnings": record.get("semantic_warnings") or [],
            "reporting_period": record.get("reporting_period"),
            "source_url": record.get("source_url"),
            "evidence_quote": record.get("evidence_quote"),
        }
        for record in raw_record_dicts
        if record.get("metric_value") not in (None, "")
    ]
    metric_category_counts = dict(
        Counter(
            str(row.get("metric_category") or "unknown")
            for row in metric_row_extraction_audit
        )
    )
    extraction_budget_rows = list(
        (summary.get("extraction_budget_by_source") or {}).values()
    )
    task_source_extraction_attempted_count = sum(
        1
        for row in extraction_budget_rows
        if int(row.get("attempted_count") or 0) > 0
        and (
            row.get("budget_bucket") == "verified_target_collection"
            or row.get("target_fit_status") == "verified_target"
            or row.get("must_fetch") is True
        )
    )
    best_available_extraction_count = sum(
        1
        for row in extraction_budget_rows
        if int(row.get("attempted_count") or 0) > 0
        and row.get("budget_bucket") == "official_or_high_trust"
    )
    target_metric_row_chunk_count = sum(
        1
        for chunk in chunks
        if (chunk.get("chunk_kind") or "text") == "metric_row"
        and _chunk_priority(chunk, extraction_context) <= 1
    )
    fallback_metric_row_chunk_count = sum(
        1
        for chunk in chunks
        if (chunk.get("chunk_kind") or "text") == "metric_row"
        and _chunk_priority(chunk, extraction_context) > 1
        and not _is_context_only_chunk(chunk, None)
        and _chunk_is_official_or_high_trust(chunk, extraction_context)
    )
    context_skipped_count = int(summary.get("skipped_context_only_chunk_count") or 0) + int(
        summary.get("skipped_context_extraction_count") or 0
    )
    metric_extraction_plan = {
        "metric_record_count": len(metric_row_extraction_audit),
        "metric_category_counts": metric_category_counts,
        "metric_source_count": len(
            {
                str(row.get("source_id") or "")
                for row in metric_row_extraction_audit
                if row.get("source_id")
            }
        ),
        "table_chunk_count": sum(
            1
            for chunk in chunks
            if (chunk.get("chunk_kind") or "text") in {"table", "metric_row"}
        ),
        "official_extraction_queue_count": len(
            summary.get("official_extraction_queue") or []
        ),
        "llm_call_count": summary.get("llm_call_count", 0),
        "llm_max_chunks": summary.get("llm_max_chunks"),
        "target_source_llm_call_count": summary.get("target_source_llm_call_count", 0),
        "task_source_extraction_attempted_count": (
            task_source_extraction_attempted_count
        ),
        "skipped_context_extraction_count": summary.get(
            "skipped_context_extraction_count", 0
        ),
        "context_extraction_skipped_count": summary.get(
            "skipped_context_extraction_count", 0
        ),
        "context_skipped_count": context_skipped_count,
        "best_available_extraction_count": best_available_extraction_count,
        "batched_metric_row_call_count": summary.get(
            "batched_metric_row_call_count", 0
        ),
        "metric_row_record_count_by_source": summary.get(
            "metric_row_record_count_by_source"
        )
        or {},
        "deterministic_metric_row_record_count": summary.get(
            "deterministic_metric_row_record_count", 0
        ),
        "fallback_text_chunk_call_count": summary.get(
            "fallback_text_chunk_call_count", 0
        ),
        "target_text_fallback_attempted_count": summary.get(
            "fallback_text_chunk_call_count", 0
        ),
        "skipped_text_fallback_after_row_record_count": summary.get(
            "skipped_text_fallback_after_row_record_count", 0
        ),
        "core_metric_extraction_gap_count": summary.get(
            "core_metric_extraction_gap_count", 0
        ),
        "core_metric_extraction_gaps": summary.get("core_metric_extraction_gaps")
        or [],
        "metric_row_chunk_count": sum(
            1
            for chunk in chunks
            if (chunk.get("chunk_kind") or "text") == "metric_row"
        ),
        "target_metric_row_chunk_count": target_metric_row_chunk_count,
        "fallback_metric_row_chunk_count": fallback_metric_row_chunk_count,
    }
    generic_record_count = sum(
        1
        for record in raw_record_dicts
        if record.get("record_schema") == "generic_public_health_record"
    )
    legacy_hantavirus_record_count = sum(
        1 for record in raw_record_dicts if record.get("disease") == "Hantavirus disease"
    )
    summary.update(
        {
            "generic_record_count": generic_record_count,
            "legacy_hantavirus_record_count": legacy_hantavirus_record_count,
            "disease_counts": disease_counts,
            "source_type_counts": source_type_counts,
            "extraction_method_counts": extraction_method_counts,
            "rejected_record_count": 0,
            "review_required_record_count": sum(
                1 for record in raw_record_dicts if record.get("requires_human_review")
            ),
            "unsupported_target_field_count": 0,
            "warnings": dict(warning_counter),
            "active_disease": extraction_context.get("disease_standard_name"),
            "record_schema": "generic_public_health_record",
            "record_task_fit_assessment_count": len(record_task_fit_assessments),
            "metric_extraction_plan": metric_extraction_plan,
            "metric_row_extraction_audit_count": len(metric_row_extraction_audit),
            "metric_category_counts": metric_category_counts,
        }
    )
    emit_workflow_progress(
        "structured_extraction",
        "structured extraction summary ready",
        {
            "input_chunk_count": summary.get("input_chunk_count"),
            "extractable_chunk_count": summary.get("extractable_chunk_count"),
            "raw_record_count": len(raw_record_dicts),
            "extraction_mode": summary.get("extraction_mode"),
            "llm_call_count": summary.get("llm_call_count", 0),
            "llm_error_count": summary.get("llm_error_count", 0),
        },
    )

    trace = append_trace(
        state,
        node_name="structured_extraction",
        message=(
            f"Built {len(raw_record_dicts)} raw records "
            f"(extraction_mode={summary['extraction_mode']}, "
            f"llm_enabled={summary['llm_enabled']})."
        ),
        metadata=summary,
    )
    return {
        "raw_records": raw_record_dicts,
        "structured_extraction_summary": summary,
        "llm_extraction_summary": llm_summary,
        "record_task_fit_assessments": record_task_fit_assessments,
        "metric_extraction_plan": metric_extraction_plan,
        "metric_row_extraction_audit": metric_row_extraction_audit,
        "official_extraction_queue": summary.get("official_extraction_queue") or [],
        "official_extraction_failures": summary.get("official_extraction_failures")
        or [],
        "official_extraction_resolved_by_equivalent_sources": summary.get(
            "official_extraction_resolved_by_equivalent_sources"
        )
        or [],
        "extraction_budget_by_source": summary.get("extraction_budget_by_source")
        or {},
        "disease_relevance_summary": update_disease_relevance_summary(
            {**state, "raw_records": raw_record_dicts},
            skipped_disease_mismatch_chunk_count=summary.get(
                "skipped_disease_mismatch_chunk_count", 0
            ),
        ),
        "collection_trace": trace,
    }


def schema_validation_and_repair(state: DataCollectionState) -> dict:
    """Validate raw records, apply deterministic repair, route to review/reject."""

    policy = StructuredExtractionPolicy(**load_structured_extraction_policy())
    raw_records = list(state.get("raw_records") or [])
    disease_context = build_disease_relevance_context(state)
    existing_queue = list(state.get("human_review_queue") or [])
    existing_review_ids = {item.get("review_id") for item in existing_queue}

    validated: list[dict] = []
    rejected: list[dict] = []
    new_review_items: list[HumanReviewItem] = []

    status_counter: Counter = Counter()
    prov_counter: Counter = Counter()
    missing_field_counter: Counter = Counter()
    repair_action_counter: Counter = Counter()
    needs_review_count = 0
    disease_counter: Counter = Counter()
    source_type_counter: Counter = Counter()
    extraction_method_counter: Counter = Counter()
    generic_record_count = 0
    legacy_hantavirus_record_count = 0
    disease_mismatch_rejected_count = 0
    disease_uncertain_review_count = 0

    for record in raw_records:
        validated_record, _result = _validate_record(record, policy)
        compatibility = assess_record_disease_compatibility(
            validated_record,
            disease_context,
        )
        validated_record.update(record_compatibility_fields(compatibility))
        compatibility_status = compatibility.get("status")
        if compatibility.get("reject_record"):
            validated_record["schema_status"] = "rejected"
            validated_record["requires_human_review"] = False
            errors = list(validated_record.get("validation_errors") or [])
            if "disease_mismatch" not in errors:
                errors.append("disease_mismatch")
            error = f"disease_mismatch: {compatibility.get('reason')}"
            if error not in errors:
                errors.append(error)
            validated_record["validation_errors"] = errors
            disease_mismatch_rejected_count += 1
        elif compatibility_status in {AMBIGUOUS_DISEASE, INSUFFICIENT_TEXT}:
            if validated_record.get("schema_status") != "rejected":
                validated_record["schema_status"] = "needs_review"
                validated_record["requires_human_review"] = True
                errors = list(validated_record.get("validation_errors") or [])
                if "disease_relevance_uncertain" not in errors:
                    errors.append("disease_relevance_uncertain")
                error = f"disease_relevance_uncertain: {compatibility.get('reason')}"
                if error not in errors:
                    errors.append(error)
                validated_record["validation_errors"] = errors
                disease_uncertain_review_count += 1
        status = validated_record.get("schema_status") or "rejected"
        status_counter[status] += 1
        prov_counter[validated_record.get("provenance_status") or "unknown"] += 1
        disease_counter[validated_record.get("disease") or "unknown"] += 1
        source_type_counter[validated_record.get("source_type") or "unknown"] += 1
        extraction_method_counter[
            validated_record.get("extraction_method") or "unknown"
        ] += 1
        if validated_record.get("record_schema") == "generic_public_health_record":
            generic_record_count += 1
        if validated_record.get("disease") == "Hantavirus disease":
            legacy_hantavirus_record_count += 1
        for f in validated_record.get("missing_fields") or []:
            missing_field_counter[f] += 1
        for a in validated_record.get("repair_actions") or []:
            repair_action_counter[a] += 1

        if status == "rejected":
            rejected.append(validated_record)
            continue

        validated.append(validated_record)
        if validated_record.get("requires_human_review"):
            needs_review_count += 1
            record_id = validated_record.get("record_id") or ""
            review_id = f"review_record_{record_id}"
            if review_id and review_id not in existing_review_ids:
                errs = validated_record.get("validation_errors") or []
                reason = (
                    "Record requires review after schema validation: "
                    + ", ".join(errs)
                ) if errs else "Record requires review after schema validation."
                new_review_items.append(
                    HumanReviewItem(
                        review_id=review_id,
                        item_type="record_schema_validation",
                        related_ids=[record_id],
                        reason=reason,
                        status="pending",
                    )
                )
                existing_review_ids.add(review_id)

    human_review_queue = list(existing_queue) + [
        item.model_dump() for item in new_review_items
    ]

    summary = {
        "raw_record_count": len(raw_records),
        "validated_record_count": len(validated),
        "rejected_record_count": len(rejected),
        "needs_review_count": needs_review_count,
        "human_review_item_count": len(new_review_items),
        "schema_status_counts": dict(status_counter),
        "provenance_status_counts": dict(prov_counter),
        "missing_field_counts": dict(missing_field_counter),
        "repair_action_counts": dict(repair_action_counter),
        "generic_record_count": generic_record_count,
        "legacy_hantavirus_record_count": legacy_hantavirus_record_count,
        "disease_counts": dict(disease_counter),
        "source_type_counts": dict(source_type_counter),
        "extraction_method_counts": dict(extraction_method_counter),
        "review_required_record_count": needs_review_count,
        "unsupported_target_field_count": 0,
        "warnings": {},
        "disease_mismatch_rejected_record_count": disease_mismatch_rejected_count,
        "disease_uncertain_review_record_count": disease_uncertain_review_count,
    }
    emit_workflow_progress(
        "schema_validation_and_repair",
        "schema validation summary ready",
        {
            "raw_record_count": len(raw_records),
            "validated_record_count": len(validated),
            "rejected_record_count": len(rejected),
            "needs_review_count": needs_review_count,
            "schema_status_counts": dict(status_counter),
            "repair_action_counts": dict(repair_action_counter),
        },
    )

    trace = append_trace(
        state,
        node_name="schema_validation_and_repair",
        message=(
            f"Validated {len(raw_records)} raw records: "
            f"{len(validated)} validated ({needs_review_count} need review), "
            f"{len(rejected)} rejected."
        ),
        metadata=summary,
    )
    return {
        "validated_records": validated,
        "rejected_records": rejected,
        "human_review_queue": human_review_queue,
        "schema_validation_summary": summary,
        "disease_relevance_summary": update_disease_relevance_summary(
            {**state, "validated_records": validated, "rejected_records": rejected},
            disease_mismatch_rejected_record_count=disease_mismatch_rejected_count,
            disease_uncertain_review_record_count=disease_uncertain_review_count,
        ),
        "collection_trace": trace,
    }
