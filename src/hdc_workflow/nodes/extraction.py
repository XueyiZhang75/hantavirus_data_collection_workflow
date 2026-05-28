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

from .. import llm_clients


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
from ..config import (
    load_llm_structured_extraction_policy,
    load_structured_extraction_policy,
)
from ..models import (
    HantavirusRecord,
    HumanReviewItem,
    LLMExtractedRecord,
    LLMExtractionOutput,
    LLMStructuredExtractionPolicy,
    SchemaValidationResult,
    StructuredExtractionPolicy,
)
from ..state import DataCollectionState, append_trace

_FIELD_DETECTION_KEYS = (
    "cases_confirmed",
    "cases_probable",
    "cases_suspected",
    "cases_unspecified",
    "deaths",
    "date_reported",
    "country",
    "subnational_location",
    "virus_or_syndrome",
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
        if field in ("cases_confirmed", "cases_probable", "cases_suspected", "cases_unspecified", "deaths"):
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
    """Always force disease to the canonical 'Hantavirus disease' label."""

    canonical = "Hantavirus disease"
    warnings: list[str] = []
    if value is None or not isinstance(value, str):
        return canonical, warnings
    if value.strip() != canonical:
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
) -> dict:
    out = dict(record_dict)
    existing_warnings = list(out.get("semantic_warnings") or [])

    disease, w_d = _standardize_disease(out.get("disease"))
    out["disease"] = disease
    existing_warnings.extend(w_d)

    vos, w_v = _clean_virus_or_syndrome(out.get("virus_or_syndrome"))
    out["virus_or_syndrome"] = vos
    existing_warnings.extend(w_v)

    chunk_text = chunk.get("text") if isinstance(chunk, dict) else None
    sct, w_s = _standardize_statistical_count_type(
        out.get("statistical_count_type"), chunk_text
    )
    out["statistical_count_type"] = sct
    existing_warnings.extend(w_s)

    out, w_g = _standardize_geographic_scope(out)
    existing_warnings.extend(w_g)

    out["semantic_warnings"] = existing_warnings
    return out


def _chunk_is_extractable(
    chunk: dict,
    policy: StructuredExtractionPolicy,
) -> bool:
    conditions = policy.extractable_chunk_conditions or {}
    if conditions.get("requires_contains_target_data", True):
        if not chunk.get("contains_target_data"):
            return False
    allowed_purposes = conditions.get("allowed_fetch_purposes") or []
    if allowed_purposes and chunk.get("fetch_purpose") not in allowed_purposes:
        return False
    allowed_kinds = conditions.get("allowed_chunk_kinds") or []
    if allowed_kinds and (chunk.get("chunk_kind") or "text") not in allowed_kinds:
        return False
    text = chunk.get("text") or ""
    if not text.strip():
        return False
    return True


def _build_record_from_chunk(
    chunk: dict,
    index: int,
    policy: StructuredExtractionPolicy,
) -> HantavirusRecord | None:
    if not _chunk_is_extractable(chunk, policy):
        return None

    text = chunk.get("text") or ""
    chunk_kind = chunk.get("chunk_kind") or "text"

    virus_or_syndrome = _detect_virus_or_syndrome(text, policy)
    date_reported = _extract_year_or_date(text, policy)
    country, subnational_location = _extract_country_or_location(text)
    case_counts = _extract_case_counts(text, policy)
    deaths = _extract_deaths(text, policy)

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
        "disease": policy.default_disease,
        "virus_or_syndrome": virus_or_syndrome,
        "country": country,
        "subnational_location": subnational_location,
        "date_reported": date_reported,
        "cases_confirmed": case_counts["cases_confirmed"],
        "cases_probable": case_counts["cases_probable"],
        "cases_suspected": case_counts["cases_suspected"],
        "cases_unspecified": case_counts["cases_unspecified"],
        "deaths": deaths,
        "case_definition": case_counts["case_definition"],
    }
    cleaned = _apply_extraction_semantic_guardrails(pre_record, chunk)

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

    return HantavirusRecord(
        record_id=record_id,
        disease=cleaned.get("disease") or policy.default_disease,
        virus_or_syndrome=cleaned.get("virus_or_syndrome"),
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
        aggregation_level=cleaned.get("aggregation_level"),
        geographic_scope=cleaned.get("geographic_scope"),
        geographic_scope_type=cleaned.get("geographic_scope_type"),
        population_scope=cleaned.get("population_scope"),
        source_section=cleaned.get("source_section"),
        semantic_warnings=list(cleaned.get("semantic_warnings") or []),
    )


# ---------------------------------------------------------------------------
# Schema validation + repair
# ---------------------------------------------------------------------------


_CONTENT_FIELDS = (
    "cases_confirmed",
    "cases_probable",
    "cases_suspected",
    "cases_unspecified",
    "deaths",
    "date_reported",
    "country",
    "subnational_location",
)


def _has_any_case_or_death(record: dict) -> bool:
    for f in ("cases_confirmed", "cases_probable", "cases_suspected", "cases_unspecified", "deaths"):
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


def _validate_record(
    record: dict,
    policy: StructuredExtractionPolicy,
) -> tuple[dict, SchemaValidationResult]:
    repaired, repair_actions = _repair_record(record, policy)

    validation_errors: list[str] = []
    try:
        HantavirusRecord(**repaired)
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

    missing_fields = sorted({*missing_core, *review_trigger_missing})

    if not pydantic_ok or missing_core or not has_min_content:
        schema_status = "rejected"
        if missing_core:
            validation_errors.append(f"missing_required_core_fields: {missing_core}")
        if not has_min_content:
            validation_errors.append("no_minimum_content")
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
    if chunk.get("fetch_purpose") not in llm_policy.allowed_fetch_purposes:
        return False
    if (chunk.get("chunk_kind") or "text") not in llm_policy.allowed_chunk_kinds:
        return False
    text = chunk.get("text") or ""
    if not text.strip():
        return False
    return True


def _has_any_llm_content_signal(record_data: dict) -> bool:
    for field in (
        "cases_confirmed",
        "cases_probable",
        "cases_suspected",
        "cases_unspecified",
        "deaths",
        "date_reported",
        "country",
        "subnational_location",
    ):
        if record_data.get(field) is not None:
            return True
    return False


def _build_record_from_llm_output(
    llm_record: LLMExtractedRecord,
    chunk: dict,
    index: int,
    llm_policy: LLMStructuredExtractionPolicy,
    settings: dict,
) -> HantavirusRecord | None:
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
    cleaned = _apply_extraction_semantic_guardrails(data, chunk)
    disease = cleaned.get("disease") or "Hantavirus disease"

    required_core = ("disease", "source_url", "source_type", "evidence_quote")
    field_values = {
        "disease": disease,
        "source_url": chunk.get("source_url"),
        "source_type": chunk.get("source_type"),
        "evidence_quote": text,
    }
    missing_fields = [
        f
        for f in required_core
        if not field_values.get(f)
        or (isinstance(field_values.get(f), str) and not str(field_values[f]).strip())
    ]

    return HantavirusRecord(
        record_id=record_id,
        disease=disease,
        virus_or_syndrome=cleaned.get("virus_or_syndrome"),
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
        case_definition=cleaned.get("case_definition"),
        source_id=source_id,
        source_url=chunk.get("source_url"),
        source_type=chunk.get("source_type"),
        evidence_quote=text,
        extraction_confidence=float(extraction_confidence),
        missing_fields=missing_fields,
        schema_status=None,
        provenance_status=None,
        supporting_chunk_id=chunk.get("chunk_id"),
        source_title=chunk.get("title"),
        publisher=chunk.get("publisher"),
        document_type=chunk.get("document_type"),
        fetch_purpose=chunk.get("fetch_purpose"),
        chunk_kind=chunk.get("chunk_kind") or "text",
        data_types=list(chunk.get("data_types") or []),
        context_types=list(chunk.get("context_types") or []),
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
        reporting_period=cleaned.get("reporting_period"),
        as_of_date=cleaned.get("as_of_date"),
        aggregation_level=cleaned.get("aggregation_level"),
        geographic_scope=cleaned.get("geographic_scope"),
        geographic_scope_type=cleaned.get("geographic_scope_type"),
        population_scope=cleaned.get("population_scope"),
        source_section=cleaned.get("source_section"),
        semantic_warnings=list(cleaned.get("semantic_warnings") or []),
    )


def _rule_based_extract_records_from_chunks(
    evidence_chunks: list[dict],
    deterministic_policy: StructuredExtractionPolicy,
    start_index: int = 1,
    only_chunk_ids: set[str] | None = None,
) -> tuple[list[HantavirusRecord], dict]:
    """Refactored deterministic loop; preserves Step 7 behavior."""

    records: list[HantavirusRecord] = []
    chunk_index_by_source: dict[str, int] = {}
    target_data_count = 0
    extractable_count = 0
    skipped_count = 0
    field_counters: Counter = Counter()

    for chunk in evidence_chunks:
        if only_chunk_ids is not None and chunk.get("chunk_id") not in only_chunk_ids:
            continue
        if chunk.get("contains_target_data"):
            target_data_count += 1
        if not _chunk_is_extractable(chunk, deterministic_policy):
            skipped_count += 1
            continue
        extractable_count += 1
        source_id = chunk.get("source_id") or ""
        if source_id not in chunk_index_by_source:
            chunk_index_by_source[source_id] = start_index - 1
        chunk_index_by_source[source_id] += 1
        idx = chunk_index_by_source[source_id]

        record = _build_record_from_chunk(chunk, idx, deterministic_policy)
        if record is None:
            skipped_count += 1
            chunk_index_by_source[source_id] -= 1
            continue
        records.append(record)
        rec_dict = record.model_dump()
        for field in _FIELD_DETECTION_KEYS:
            if rec_dict.get(field) is not None:
                field_counters[field] += 1

    stats = {
        "target_data_chunk_count": target_data_count,
        "extractable_chunk_count": extractable_count,
        "skipped_chunk_count": skipped_count,
        "field_detection_counts": {
            f: field_counters.get(f, 0) for f in _FIELD_DETECTION_KEYS
        },
    }
    return records, stats


def _llm_extract_records_from_chunks(
    evidence_chunks: list[dict],
    llm_policy: LLMStructuredExtractionPolicy,
    deterministic_policy: StructuredExtractionPolicy,
    fallback_to_rule_based: bool,
) -> tuple[list[HantavirusRecord], dict]:
    """LLM extraction loop with optional per-chunk deterministic fallback."""

    settings = llm_clients.get_llm_settings()
    records: list[HantavirusRecord] = []
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

    for chunk in evidence_chunks:
        if chunk.get("contains_target_data"):
            target_data_count += 1
        if not _chunk_allowed_for_llm(chunk, llm_policy):
            continue
        llm_eligible_chunk_count += 1
        # Enforce the optional per-pilot LLM chunk cap. Once the cap has been
        # reached, additional eligible chunks are counted but skipped without
        # incurring further LLM calls.
        if max_chunks is not None and llm_call_count >= max_chunks:
            llm_skipped_due_to_chunk_cap_count += 1
            continue
        llm_call_count += 1
        source_id = chunk.get("source_id") or ""

        try:
            output = llm_clients.extract_chunk_with_llm(chunk, llm_policy)
            llm_success_count += 1
            if not output.records:
                llm_empty_output_count += 1
            for llm_record in output.records[: llm_policy.max_records_per_chunk]:
                chunk_index_by_source[source_id] = chunk_index_by_source.get(source_id, 0) + 1
                idx = chunk_index_by_source[source_id]
                record = _build_record_from_llm_output(
                    llm_record, chunk, idx, llm_policy, settings
                )
                if record is None:
                    chunk_index_by_source[source_id] -= 1
                    continue
                records.append(record)
        except Exception as exc:  # noqa: BLE001 — caller decides fallback
            llm_error_count += 1
            llm_error_messages.append(f"{type(exc).__name__}: {exc}")
            if fallback_to_rule_based:
                llm_fallback_count += 1
                start_idx = chunk_index_by_source.get(source_id, 0) + 1
                fallback_records, _ = _rule_based_extract_records_from_chunks(
                    [chunk], deterministic_policy, start_index=start_idx
                )
                rule_based_fallback_record_count += len(fallback_records)
                records.extend(fallback_records)
                chunk_index_by_source[source_id] = (
                    chunk_index_by_source.get(source_id, 0) + len(fallback_records)
                )

    field_counters: Counter = Counter()
    for record in records:
        rec_dict = record.model_dump()
        for field in _FIELD_DETECTION_KEYS:
            if rec_dict.get(field) is not None:
                field_counters[field] += 1

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
    }
    return records, stats


def structured_extraction(state: DataCollectionState) -> dict:
    """Convert target-data evidence chunks into HantavirusRecord objects.

    Default = deterministic rule-based extraction (Step 7 behavior). When
    `HDC_ENABLE_LLM_EXTRACTION=true`, run the optional LLM extractor with
    per-chunk fallback to the deterministic extractor when configured.
    """

    deterministic_policy = StructuredExtractionPolicy(
        **load_structured_extraction_policy()
    )
    llm_policy = _load_llm_policy()
    chunks = list(state.get("evidence_chunks") or [])

    llm_enabled = llm_clients.llm_extraction_enabled()
    fallback_to_rule_based = llm_clients.llm_fallback_to_rule_based()

    if llm_enabled:
        records, llm_stats = _llm_extract_records_from_chunks(
            chunks, llm_policy, deterministic_policy, fallback_to_rule_based
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
            "llm_max_chunks": llm_stats.get("llm_max_chunks"),
            "llm_skipped_due_to_chunk_cap_count": llm_stats.get(
                "llm_skipped_due_to_chunk_cap_count", 0
            ),
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
            "fallback_to_rule_based": fallback_to_rule_based,
            "llm_max_chunks": llm_stats.get("llm_max_chunks"),
            "llm_skipped_due_to_chunk_cap_count": llm_stats.get(
                "llm_skipped_due_to_chunk_cap_count", 0
            ),
        }
    else:
        records, det_stats = _rule_based_extract_records_from_chunks(
            chunks, deterministic_policy
        )
        raw_record_dicts = [r.model_dump() for r in records]
        summary = {
            "input_chunk_count": len(chunks),
            "target_data_chunk_count": det_stats["target_data_chunk_count"],
            "extractable_chunk_count": det_stats["extractable_chunk_count"],
            "raw_record_count": len(records),
            "skipped_chunk_count": det_stats["skipped_chunk_count"],
            "extraction_method": deterministic_policy.extraction_method,
            "field_detection_counts": det_stats["field_detection_counts"],
            "extraction_mode": "deterministic_rule_based",
            "llm_enabled": False,
            "llm_call_count": 0,
            "llm_success_count": 0,
            "llm_error_count": 0,
            "llm_fallback_count": 0,
            "llm_max_chunks": _parse_llm_max_chunks(),
            "llm_skipped_due_to_chunk_cap_count": 0,
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
            "llm_max_chunks": _parse_llm_max_chunks(),
            "llm_skipped_due_to_chunk_cap_count": 0,
        }

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
        "collection_trace": trace,
    }


def schema_validation_and_repair(state: DataCollectionState) -> dict:
    """Validate raw records, apply deterministic repair, route to review/reject."""

    policy = StructuredExtractionPolicy(**load_structured_extraction_policy())
    raw_records = list(state.get("raw_records") or [])
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

    for record in raw_records:
        validated_record, _result = _validate_record(record, policy)
        status = validated_record.get("schema_status") or "rejected"
        status_counter[status] += 1
        prov_counter[validated_record.get("provenance_status") or "unknown"] += 1
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
    }

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
        "collection_trace": trace,
    }
