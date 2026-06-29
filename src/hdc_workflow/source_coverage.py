"""Task-aware official source coverage requirements.

This module is deliberately deterministic. It protects task-critical official
sources from later LLM/source-role routing mistakes and gives diagnostics a
stable coverage table to audit against.
"""

from __future__ import annotations

import re
from copy import deepcopy
from datetime import date, datetime
from hashlib import sha256
from urllib.parse import urlsplit


_US_STATE_OFFICIAL_DOMAINS = {
    "united_states": {
        "slug": "united_states",
        "canonical_location": "United States",
        "aliases": {
            "united states",
            "united states of america",
            "usa",
            "us",
            "u.s.",
            "u.s.a.",
        },
        "official_domains": ["cdc.gov"],
        "agency": "Centers for Disease Control and Prevention",
        "report_title_hints": [
            "FluView",
            "Weekly US Influenza Surveillance Report",
            "Key Updates",
        ],
    },
    "virginia": {
        "slug": "virginia",
        "canonical_location": "Virginia",
        "aliases": {"virginia", "va"},
        "official_domains": ["vdh.virginia.gov"],
        "agency": "Virginia Department of Health",
        "report_title_hints": [
            "Weekly-RDS-Report",
            "Respiratory Disease Surveillance",
        ],
    },
    "new_york": {
        "slug": "new_york",
        "canonical_location": "New York",
        "aliases": {"new york", "new york state", "ny", "nys"},
        "official_domains": [
            "health.ny.gov",
            "health.state.ny.us",
            "nyshc.health.ny.gov",
        ],
        "agency": "New York State Department of Health",
        "report_title_hints": [
            "New York State Influenza Surveillance Report",
            "flu_report",
            "Respiratory Surveillance and Reports",
            "New York State Flu Tracker",
        ],
    },
}

_INFLUENZA_TERMS = {"flu", "influenza", "seasonal influenza"}
_GENERIC_METRIC_CATEGORIES = [
    "case_count",
    "death_count",
    "incidence_rate",
    "mortality_rate",
    "hospitalization_count",
    "hospitalization_rate",
    "lab_test_count",
    "lab_positive_count",
    "lab_positivity_percent",
    "ili_percent",
    "ed_visit_percent",
    "outbreak_count",
    "treatment_coverage_percent",
    "treatment_success_percent",
    "vaccination_coverage_percent",
    "public_health_metric",
]
_STRICT_FINAL_CONDITIONS = [
    "task_disease_match",
    "task_geography_match",
    "task_period_or_explicit_reporting_period_match",
    "interpretable_public_health_metric",
    "source_provenance_verified",
    "trusted_or_human_reviewed_source_provenance",
    "evidence_quote_or_source_row_binding",
]
_BEST_AVAILABLE_CONDITIONS = [
    "wrong_period_or_broader_than_task",
    "near_match_wrong_or_broader_period",
    "broader_than_task_geography_context",
    "season_or_multi_year_context_for_short_window",
]
_HUMAN_REVIEW_CONDITIONS = [
    "source_trust_boundary",
    "low_or_social_source_with_task_metric",
    "high_impact_source_aware_anomaly",
    "unresolved_period_or_column_semantics_but_potentially_useful",
    "borderline_source_trust",
]
_LOCATION_ALIAS_MAP = {
    "german": "Germany",
    "germany": "Germany",
    "deutschland": "Germany",
    "indian": "India",
    "india": "India",
    "american": "United States",
    "united states": "United States",
    "united states of america": "United States",
    "usa": "United States",
    "us": "United States",
    "u.s.": "United States",
    "british": "United Kingdom",
    "uk": "United Kingdom",
    "u.k.": "United Kingdom",
    "united kingdom": "United Kingdom",
}
_NY_FLU_REPORT_RE = re.compile(
    r"/influenza/surveillance/(?P<season>20\d{2}-(?:\d{2}|20\d{2}))/"
    r"archive/(?P<date>20\d{2}-\d{2}-\d{2})_flu_report\.pdf$",
    re.IGNORECASE,
)
_VDH_RDS_WEEK_RE = re.compile(
    r"weekly-rds-report[_-]week[_-]?(?P<week>\d{1,2})\.pdf$",
    re.IGNORECASE,
)
_CDC_FLUVIEW_WEEK_RE = re.compile(
    r"/fluview/surveillance/(?P<year>20\d{2})-week-(?P<week>\d{1,2})\.html$",
    re.IGNORECASE,
)


def _lower(value) -> str:
    return str(value or "").strip().lower()


def _as_date(value) -> date | None:
    text = str(value or "").strip()
    if not text:
        return None
    if re.fullmatch(r"\d{4}", text):
        text = f"{text}-01-01"
    parts = text.split("-")
    if len(parts) == 3:
        try:
            return date(int(parts[0]), int(parts[1]), int(parts[2]))
        except (TypeError, ValueError):
            return None
    try:
        return datetime.fromisoformat(text).date()
    except (TypeError, ValueError):
        return None


def _task_field(state: dict, key: str, *fallbacks: str) -> str:
    structured = state.get("structured_task") or {}
    collection = state.get("collection_spec") or {}
    for name in (key, *fallbacks):
        value = structured.get(name)
        if value not in (None, ""):
            return str(value)
        value = collection.get(name)
        if value not in (None, ""):
            return str(value)
    return ""


def _canonical_location_label(value: str | None) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    return _LOCATION_ALIAS_MAP.get(_lower(text), text)


def _state_profile(location: str) -> dict | None:
    loc = _lower(location)
    for profile in _US_STATE_OFFICIAL_DOMAINS.values():
        if loc in profile["aliases"]:
            return profile
    return None


def _slug(value: str) -> str:
    text = re.sub(r"[^a-z0-9]+", "_", _lower(value)).strip("_")
    return text or "unknown"


def _years_between(start: date, end: date) -> list[int]:
    if end < start:
        start, end = end, start
    return list(range(start.year, end.year + 1))


def _full_calendar_year_range(start: date, end: date) -> bool:
    if end < start:
        start, end = end, start
    return start.month == 1 and start.day == 1 and end.month == 12 and end.day == 31


def _annual_periods_for_range(start: date, end: date) -> list[tuple[int, date, date]]:
    """Return full natural-year periods covered by an inclusive or exclusive range.

    User-facing date ranges often express a natural year either as
    2023-01-01..2023-12-31 or as the half-open interval
    2023-01-01..2024-01-01. Treating the latter as a generic task window makes
    otherwise equivalent annual requests behave differently.
    """

    if end < start:
        start, end = end, start
    if start.month != 1 or start.day != 1:
        return []
    if end.month == 12 and end.day == 31:
        final_year = end.year
    elif end.month == 1 and end.day == 1 and end.year > start.year:
        final_year = end.year - 1
    else:
        return []
    if final_year < start.year:
        return []
    return [
        (year, date(year, 1, 1), date(year, 12, 31))
        for year in range(start.year, final_year + 1)
    ]


def _generic_requirement(
    *,
    disease_label: str,
    canonical_location: str,
    disease_slug: str,
    location_slug: str,
    period_start: date,
    period_end: date,
    period_basis: str,
    label: str,
    requirement_suffix: str,
) -> dict:
    time_granularity = _time_granularity_for_period_basis(period_basis)
    return {
        "requirement_id": f"{location_slug}_{disease_slug}_{requirement_suffix}",
        "disease": disease_label.lower(),
        "location": canonical_location,
        "geography": canonical_location,
        "year": period_start.year if period_start.year == period_end.year else None,
        "period_start": period_start.isoformat(),
        "period_end": period_end.isoformat(),
        "reporting_period_start": period_start.isoformat(),
        "reporting_period_end": period_end.isoformat(),
        "reporting_period_label": label,
        "period_basis": period_basis,
        "time_granularity": time_granularity,
        "source_type": "task_relevant_public_health_evidence",
        "official_domains": [],
        "accepted_source_roles": [
            "official_public_health_agency",
            "national_public_health_agency",
            "state_or_local_public_health_agency",
            "international_public_health_agency",
            "academic_or_peer_reviewed_source",
            "public_health_dataset",
            "task_record_collection_candidate",
        ],
        "accepted_metric_categories": list(_GENERIC_METRIC_CATEGORIES),
        "accepted_metric_families": list(_GENERIC_METRIC_CATEGORIES),
        "strict_final_conditions": list(_STRICT_FINAL_CONDITIONS),
        "best_available_conditions": list(_BEST_AVAILABLE_CONDITIONS),
        "human_review_conditions": list(_HUMAN_REVIEW_CONDITIONS),
        "official_candidate_urls": [],
        "agency": "",
        "title_hints": [
            disease_label,
            canonical_location,
            str(period_start.year),
            str(period_end.year),
            "surveillance",
            "report",
            "dashboard",
            "data",
            "epidemiology",
            "statistics",
        ],
        "reason": (
            f"Target {canonical_location} {disease_label} task requires "
            f"task-relevant public health evidence for {label}."
        ),
    }


def _time_granularity_for_period_basis(period_basis: str) -> str:
    basis = str(period_basis or "").strip().lower()
    if basis == "week_ending_saturday":
        return "weekly"
    if basis == "annual":
        return "annual"
    if basis:
        return basis
    return "task_window"


def _is_influenza_task(disease: str, state: dict) -> bool:
    text = " ".join(
        [
            disease,
            str((state.get("structured_task") or {}).get("user_request") or ""),
            str((state.get("collection_spec") or {}).get("user_request") or ""),
        ]
    ).lower()
    return any(term in text for term in _INFLUENZA_TERMS)


def _week_numbers_between(start: date, end: date) -> list[tuple[int, int]]:
    if end < start:
        start, end = end, start
    weeks: set[tuple[int, int]] = set()
    current = start
    while current <= end:
        # CDC FluView, state influenza reports, and many US respiratory
        # surveillance reports use a week-ending-Saturday convention. Using the
        # Saturday anchor keeps a Sunday-Saturday task window such as
        # 2024-09-29..2024-10-05 attached to Week 40, not split into ISO weeks
        # 39 and 40.
        days_until_saturday = (5 - current.weekday()) % 7
        week_anchor = date.fromordinal(current.toordinal() + days_until_saturday)
        iso = week_anchor.isocalendar()
        weeks.add((iso.year, iso.week))
        current = date.fromordinal(current.toordinal() + 1)
    return sorted(weeks)


def _dates_for_iso_week(year: int, week: int) -> list[str]:
    try:
        monday = date.fromisocalendar(int(year), int(week), 1)
    except (TypeError, ValueError):
        return []
    return [
        date.fromordinal(monday.toordinal() + offset).isoformat()
        for offset in range(7)
    ]


def _week_ending_saturday(year: int, week: int) -> date | None:
    try:
        return date.fromisocalendar(int(year), int(week), 6)
    except (TypeError, ValueError):
        return None


def _week_reporting_period(year: int, week: int) -> tuple[str | None, str | None, str | None]:
    ending = _week_ending_saturday(year, week)
    if not ending:
        return None, None, None
    start = date.fromordinal(ending.toordinal() - 6)
    return (
        start.isoformat(),
        ending.isoformat(),
        f"MMWR week {int(week)}, {int(year)}",
    )


def _influenza_season_for_week(year: int, week: int) -> str:
    ending = _week_ending_saturday(year, week)
    if not ending:
        return f"{year}-{str(year + 1)[-2:]}"
    if ending.month >= 7:
        return f"{ending.year}-{str(ending.year + 1)[-2:]}"
    return f"{ending.year - 1}-{str(ending.year)[-2:]}"


def _official_candidate_urls(profile: dict, year: int, week: int) -> list[str]:
    slug = str(profile.get("slug") or "")
    ending = _week_ending_saturday(year, week)
    if slug == "united_states":
        return [
            f"https://www.cdc.gov/fluview/surveillance/{year}-week-{week}.html"
        ]
    if slug == "new_york" and ending:
        season = _influenza_season_for_week(year, week)
        return [
            (
                "https://www.health.ny.gov/diseases/communicable/influenza/"
                f"surveillance/{season}/archive/{ending.isoformat()}_flu_report.pdf"
            )
        ]
    if slug == "virginia" and ending:
        season = _influenza_season_for_week(year, week)
        month = f"{ending.month:02d}"
        return [
            (
                "https://www.vdh.virginia.gov/content/uploads/sites/13/"
                f"{ending.year}/{month}/Weekly-RDS-Report_Week-{week}.pdf"
            ),
            (
                "https://www.vdh.virginia.gov/content/uploads/sites/3/"
                f"{ending.year}/{month}/{season}_Weekly-RDS-Report_Week-{week}.pdf"
            ),
        ]
    return []


def build_source_coverage_requirements(state: dict) -> list[dict]:
    """Build task-specific source coverage requirements for a run."""

    disease = _task_field(state, "disease")
    location = _canonical_location_label(_task_field(state, "location", "geography"))
    start = _as_date(_task_field(state, "start_date"))
    end = _as_date(_task_field(state, "end_date")) or start
    state_profile = _state_profile(location)
    if not start or not end:
        return []
    if not state_profile or not _is_influenza_task(disease, state):
        disease_slug = _slug(disease)
        location_slug = _slug(location)
        canonical_location = str(location or "").strip() or location_slug
        disease_label = str(disease or "").strip() or disease_slug
        requirements: list[dict] = []
        annual_periods = _annual_periods_for_range(start, end)
        if annual_periods:
            for year, period_start, period_end in annual_periods:
                requirements.append(
                    _generic_requirement(
                        disease_label=disease_label,
                        canonical_location=canonical_location,
                        disease_slug=disease_slug,
                        location_slug=location_slug,
                        period_start=period_start,
                        period_end=period_end,
                        period_basis="annual",
                        label=str(year),
                        requirement_suffix=f"annual_{year}",
                    )
                )
            return requirements

        period_start = min(start, end)
        period_end = max(start, end)
        requirements.append(
            _generic_requirement(
                disease_label=disease_label,
                canonical_location=canonical_location,
                disease_slug=disease_slug,
                location_slug=location_slug,
                period_start=period_start,
                period_end=period_end,
                period_basis="task_window",
                label=f"{period_start.isoformat()} to {period_end.isoformat()}",
                requirement_suffix=(
                    "task_window_"
                    f"{period_start.isoformat().replace('-', '_')}_"
                    f"{period_end.isoformat().replace('-', '_')}"
                ),
            )
        )
        return requirements

    requirements: list[dict] = []
    for year, week in _week_numbers_between(start, end):
        slug = state_profile.get("slug") or _lower(location).replace(" ", "_")
        canonical_location = state_profile.get("canonical_location") or location
        report_hints = list(state_profile.get("report_title_hints") or [])
        candidate_urls = _official_candidate_urls(state_profile, year, week)
        period_start, period_end, period_label = _week_reporting_period(year, week)
        requirements.append(
            {
                "requirement_id": f"{slug}_influenza_official_week_{week}_{year}",
                "disease": "influenza",
                "location": canonical_location,
                "geography": canonical_location,
                "year": year,
                "week": week,
                "date_hints": _dates_for_iso_week(year, week),
                "period_start": period_start,
                "period_end": period_end,
                "reporting_period_start": period_start,
                "reporting_period_end": period_end,
                "reporting_period_label": period_label,
                "period_basis": "week_ending_saturday",
                "time_granularity": "weekly",
                "source_type": "official_weekly_surveillance_report",
                "official_domains": list(state_profile["official_domains"]),
                "accepted_metric_categories": list(_GENERIC_METRIC_CATEGORIES),
                "accepted_metric_families": list(_GENERIC_METRIC_CATEGORIES),
                "strict_final_conditions": list(_STRICT_FINAL_CONDITIONS),
                "best_available_conditions": list(_BEST_AVAILABLE_CONDITIONS),
                "human_review_conditions": list(_HUMAN_REVIEW_CONDITIONS),
                "official_candidate_urls": candidate_urls,
                "agency": state_profile["agency"],
                "title_hints": [
                    f"Week-{week}",
                    f"Week {week}",
                    *[url.rsplit("/", 1)[-1] for url in candidate_urls],
                    *report_hints,
                ],
                "reason": (
                    f"Target {canonical_location} seasonal influenza task requires "
                    f"the {state_profile['agency']} weekly surveillance report "
                    f"for week {week}, {year}."
                ),
            }
        )
    return requirements


def build_task_evidence_contract(state: dict) -> dict:
    """Build the generic evidence contract shared by discovery, extraction, and gate.

    The contract is intentionally a thin deterministic layer over coverage
    requirements. Its job is to keep every downstream agent aligned to the same
    disease/location/time/metric semantics without encoding source-specific
    shortcuts as the workflow's primary mechanism.
    """

    requirements = build_source_coverage_requirements(state)
    disease = _task_field(state, "disease")
    location = _canonical_location_label(_task_field(state, "location", "geography"))
    start = _as_date(_task_field(state, "start_date"))
    end = _as_date(_task_field(state, "end_date")) or start
    period_bases = {
        str(req.get("period_basis") or "task_window")
        for req in requirements
        if isinstance(req, dict)
    }
    if not period_bases:
        time_granularity = "unknown"
    elif len(period_bases) == 1:
        only = next(iter(period_bases))
        if only == "week_ending_saturday":
            time_granularity = "weekly"
        elif only == "annual":
            time_granularity = "annual"
        else:
            time_granularity = only
    else:
        time_granularity = "mixed"
    return {
        "contract_version": "hdc_task_evidence_contract_v1",
        "disease": str(disease or "").strip(),
        "location": str(location or "").strip(),
        "time_granularity": time_granularity,
        "task_period_start": start.isoformat() if start else None,
        "task_period_end": end.isoformat() if end else None,
        "requirements": [dict(row) for row in requirements],
        "accepted_metric_families": list(_GENERIC_METRIC_CATEGORIES),
        "strict_final_conditions": list(_STRICT_FINAL_CONDITIONS),
        "best_available_conditions": list(_BEST_AVAILABLE_CONDITIONS),
        "human_review_conditions": list(_HUMAN_REVIEW_CONDITIONS),
        "partial_output_allowed": True,
    }


def build_official_coverage_candidates(state: dict) -> list[dict]:
    """Build deterministic target official source candidates for a task."""

    candidates: list[dict] = []
    for requirement in build_source_coverage_requirements(state):
        urls = list(requirement.get("official_candidate_urls") or [])
        for index, url in enumerate(urls, start=1):
            canonical = str(url).strip()
            if not canonical:
                continue
            digest = sha256(canonical.encode("utf-8")).hexdigest()[:12]
            filename = canonical.rsplit("/", 1)[-1]
            candidates.append(
                {
                    "source_id": f"src_official_{digest}",
                    "title": (
                        f"{requirement.get('agency')} {requirement.get('source_type')} "
                        f"week {requirement.get('week')}, {requirement.get('year')}"
                    ),
                    "url": canonical,
                    "canonical_url": canonical,
                    "publisher": requirement.get("agency"),
                    "source_type": "official_public_health_agency",
                    "published_date": (
                        (requirement.get("date_hints") or [None])[-2]
                        if len(requirement.get("date_hints") or []) >= 2
                        else (requirement.get("date_hints") or [None])[-1]
                    ),
                    "snippet": requirement.get("reason"),
                    "query_used": None,
                    "retrieved_at": "2026-05-25T00:00:00Z",
                    "query_id": requirement.get("requirement_id"),
                    "discovery_method": "official_coverage_requirement",
                    "priority": index - 1,
                    "expected_fields": [
                        "cases",
                        "deaths",
                        "hospitalizations",
                        "tests_positive",
                        "reporting_period",
                        "source_url",
                    ],
                    "matched_terms": [
                        "influenza",
                        str(requirement.get("location") or ""),
                        f"week {requirement.get('week')}",
                        str(requirement.get("year") or ""),
                        filename,
                    ],
                    "source_purpose": "target_official_surveillance_report",
                    "notes": requirement.get("reason"),
                    "provider_channel": "official_site_search",
                    "role_hint": "collection",
                    "planned_query_id": requirement.get("requirement_id"),
                    "planned_query_source_type": requirement.get("source_type"),
                    "domain": _domain_for_url(canonical),
                    "query_type": "deterministic_official_url",
                    "query_source": "source_coverage_requirement",
                    "source_disease_relevance_status": "target_disease_match",
                    "source_disease_relevance_score": 1.0,
                    "source_target_disease_terms_found": ["influenza", "flu"],
                    "source_disease_relevance_reason": requirement.get("reason"),
                    "source_disease_relevance_data_signal_count": 1,
                    "coverage_requirement_ids": [requirement.get("requirement_id")],
                    "must_fetch": True,
                    "must_fetch_reason": requirement.get("reason"),
                    "reporting_period_start": requirement.get("reporting_period_start"),
                    "reporting_period_end": requirement.get("reporting_period_end"),
                    "reporting_period_label": requirement.get("reporting_period_label"),
                    "period_basis": requirement.get("period_basis"),
                }
            )
    return candidates


def _domain_for_url(url: str) -> str:
    domain = urlsplit(str(url or "")).netloc.lower()
    return domain[4:] if domain.startswith("www.") else domain


def official_report_key_for_url(url: str | None) -> str | None:
    """Return a stable key for equivalent target official report URLs.

    Some state health sites expose the same influenza PDF under both short and
    long season aliases (for example NYSDOH `2024-25` and `2024-2025`). The
    workflow should treat those as one official report so fetch/extraction
    diagnostics do not contradict themselves.
    """

    if not url:
        return None
    parts = urlsplit(str(url).strip())
    domain = parts.netloc.lower()
    if domain.startswith("www."):
        domain = domain[4:]
    path = parts.path.lower()
    if domain in {"health.ny.gov", "health.state.ny.us", "nyshc.health.ny.gov"}:
        match = _NY_FLU_REPORT_RE.search(path)
        if match:
            return f"ny_influenza_weekly_report:{match.group('date')}"
    if domain == "vdh.virginia.gov":
        match = _VDH_RDS_WEEK_RE.search(path)
        if match:
            year_match = re.search(r"/(20\d{2})/", path)
            year = year_match.group(1) if year_match else "unknown_year"
            week = int(match.group("week"))
            return f"virginia_rds_weekly_report:{year}:week_{week:02d}"
    if domain == "cdc.gov":
        match = _CDC_FLUVIEW_WEEK_RE.search(path)
        if match:
            year = int(match.group("year"))
            week = int(match.group("week"))
            return f"cdc_fluview_weekly_report:{year}:week_{week:02d}"
    return None


def _domain_for_entry(entry: dict) -> str:
    url = entry.get("canonical_url") or entry.get("url") or ""
    if not url:
        return ""
    domain = urlsplit(str(url)).netloc.lower()
    return domain[4:] if domain.startswith("www.") else domain


def _matches_domain(domain: str, official_domains: list[str]) -> bool:
    for official in official_domains:
        official = _lower(official)
        if domain == official or domain.endswith("." + official):
            return True
    return False


def _entry_text(entry: dict) -> str:
    return " ".join(
        str(entry.get(key) or "")
        for key in (
            "canonical_url",
            "url",
            "title",
            "name",
            "source_title",
            "snippet",
            "publisher",
        )
    ).lower()


def _explicit_year_week_pairs(text: str) -> set[tuple[int, int]]:
    pairs: set[tuple[int, int]] = set()
    for match in re.finditer(
        r"\b(?P<year>20\d{2})[-_/ ]+week[-_/ ]?(?P<week>\d{1,2})\b",
        text,
        re.IGNORECASE,
    ):
        try:
            pairs.add((int(match.group("year")), int(match.group("week"))))
        except (TypeError, ValueError):
            continue
    for match in re.finditer(
        r"\bweek[-_/ ]?(?P<week>\d{1,2})\b.{0,40}?\b(?P<year>20\d{2})\b",
        text,
        re.IGNORECASE,
    ):
        try:
            pairs.add((int(match.group("year")), int(match.group("week"))))
        except (TypeError, ValueError):
            continue
    return pairs


def _explicit_years(text: str) -> set[int]:
    years: set[int] = set()
    for value in re.findall(r"\b20\d{2}\b", text or ""):
        try:
            years.add(int(value))
        except (TypeError, ValueError):
            continue
    return years


_GENERIC_TARGET_ROLES = {
    "verified_target_collection",
    "search_verified_target_collection",
    "fetch_verified_target_collection",
    "task_record_collection_candidate",
}
_GENERIC_COLLECTION_ROLES = {
    "collection",
    "data_source",
    "official_authority",
    "official_public_health_agency",
    "national_public_health_agency",
    "state_or_local_public_health_agency",
    "international_public_health_agency",
    "academic_or_peer_reviewed_source",
    "public_health_dataset",
}
_GENERIC_REJECT_FITS = {
    "mismatch",
    "wrong_period",
    "wrong_year",
    "wrong_week",
    "wrong_geography",
    "outside_scope",
    "excluded",
    "non_target",
    "context_only",
}


def _fit_rejected(value) -> bool:
    return _lower(value) in _GENERIC_REJECT_FITS


def _period_tokens_for_requirement(requirement: dict) -> set[str]:
    tokens: set[str] = set()
    for key in ("reporting_period_start", "reporting_period_end", "reporting_period_label"):
        value = str(requirement.get(key) or "").strip().lower()
        if value:
            tokens.add(value)
    year = requirement.get("year")
    if year:
        tokens.add(str(year))
    for value in (requirement.get("date_hints") or []):
        text = str(value or "").strip().lower()
        if text:
            tokens.add(text)
    return tokens


def _matches_generic_requirement(entry: dict, requirement: dict) -> bool:
    labels = {
        _lower(entry.get("target_fit_status")),
        _lower(entry.get("triage_role")),
        _lower(entry.get("source_role_final")),
        _lower(entry.get("source_role")),
        _lower(entry.get("source_type")),
        _lower(entry.get("source_type_final")),
    }
    if labels & _NON_TARGET_COVERAGE_STATUSES:
        return False
    if any(
        _fit_rejected(entry.get(key))
        for key in ("disease_fit", "geography_fit", "date_fit", "period_fit")
    ):
        return False

    text = _entry_text(entry)
    disease = _lower(requirement.get("disease"))
    location = _lower(requirement.get("location"))
    disease_signal = (
        _lower(entry.get("disease_fit")) in {"match", "candidate", "possible"}
        or any(token and token in text for token in {disease, disease.replace("flu", "influenza")})
    )
    geography_signal = (
        _lower(entry.get("geography_fit")) in {"match", "candidate", "possible"}
        or (location and location in text)
    )
    period_signal = (
        _lower(entry.get("date_fit")) in {"match", "candidate", "possible"}
        or any(token and token in text for token in _period_tokens_for_requirement(requirement))
    )
    role_signal = bool(labels & (_GENERIC_TARGET_ROLES | _GENERIC_COLLECTION_ROLES))

    if labels & _GENERIC_TARGET_ROLES:
        return disease_signal and geography_signal and period_signal
    return role_signal and disease_signal and geography_signal and period_signal


def _matches_requirement(entry: dict, requirement: dict) -> bool:
    if requirement.get("source_type") == "task_relevant_public_health_evidence":
        return _matches_generic_requirement(entry, requirement)
    domain = _domain_for_entry(entry)
    if not _matches_domain(domain, list(requirement.get("official_domains") or [])):
        return False
    text = _entry_text(entry)
    try:
        week_int = int(requirement.get("week"))
        year_int = int(requirement.get("year"))
    except (TypeError, ValueError):
        return False
    explicit_pairs = _explicit_year_week_pairs(text)
    if explicit_pairs and (year_int, week_int) not in explicit_pairs:
        return False
    explicit_year_values = _explicit_years(text)
    if explicit_year_values and year_int not in explicit_year_values:
        return False
    week = str(week_int)
    year = str(year_int)
    has_week = (
        f"week-{week}" in text
        or f"week_{week}" in text
        or f"week {week}" in text
        or f"week-{int(week):02d}" in text
        or f"week_{int(week):02d}" in text
        or f"week {int(week):02d}" in text
    )
    has_report = "weekly-rds-report" in text or "respiratory disease surveillance" in text
    title_hints = [
        str(value or "").strip().lower()
        for value in (requirement.get("title_hints") or [])
        if str(value or "").strip()
    ]
    has_profile_report_hint = any(hint in text for hint in title_hints)
    has_date_hint = any(
        str(value or "").strip().lower() in text
        for value in (requirement.get("date_hints") or [])
        if str(value or "").strip()
    )
    return (has_week or has_date_hint) and (
        year in text or has_report or has_profile_report_hint
    )


def _append_unique(items: list, value: str) -> None:
    if value and value not in items:
        items.append(value)


def _http_status_ok(value) -> bool:
    try:
        status = int(value)
    except (TypeError, ValueError):
        return True
    return status < 400


def _looks_like_error_page(doc: dict) -> bool:
    text = " ".join(
        str(doc.get(key) or "")
        for key in ("title", "clean_text", "raw_text", "text", "excerpt")
    ).lower()
    return any(
        marker in text
        for marker in (
            "page not found",
            "404",
            "not found |",
            "error page",
            "the page you requested was not found",
        )
    )


def _fetch_succeeded(doc: dict) -> bool:
    if _lower(doc.get("fetch_status")) == "fetch_failed":
        return False
    if not _http_status_ok(doc.get("http_status_code")):
        return False
    return True


def _parse_succeeded(doc: dict) -> bool:
    if not _fetch_succeeded(doc):
        return False
    if _lower(doc.get("quality_status")) == "unusable":
        return False
    if _looks_like_error_page(doc):
        return False
    parse_status = _lower(doc.get("parse_status"))
    return parse_status not in {"", "parse_failed", "parse_deferred", "fetch_failed"}


_NON_TARGET_COVERAGE_STATUSES = {
    "best_available_context_candidate",
    "context_only",
    "wrong_period_context",
    "validation_only",
    "excluded",
}


def _entry_is_non_target_context(entry: dict) -> bool:
    labels = {
        _lower(entry.get("target_fit_status")),
        _lower(entry.get("triage_role")),
        _lower(entry.get("source_role_final")),
        _lower(entry.get("source_role")),
    }
    return bool(labels & _NON_TARGET_COVERAGE_STATUSES) or "context" in labels


def _coverage_parse_succeeded(entry: dict, doc: dict) -> bool:
    if not _parse_succeeded(doc):
        return False
    if doc.get("usable_for_task_collection") is False:
        return False
    if _entry_is_non_target_context(entry) and doc.get("usable_for_task_collection") is not True:
        return False
    return True


def _doc_text(doc: dict) -> str:
    return _lower(
        " ".join(
            str(doc.get(key) or "")
            for key in (
                "title",
                "clean_text",
                "raw_text",
                "text",
                "excerpt",
                "url",
                "canonical_url",
                "source_url",
                "reporting_period_label",
            )
        )
    )


def _iso_date(value) -> date | None:
    if not value:
        return None
    text = str(value).strip()
    match = re.search(r"\d{4}-\d{2}-\d{2}", text)
    if not match:
        return None
    try:
        return date.fromisoformat(match.group(0))
    except ValueError:
        return None


def _requirement_years(requirement: dict) -> set[int]:
    years: set[int] = set()
    try:
        if requirement.get("year") not in (None, ""):
            years.add(int(requirement.get("year")))
    except (TypeError, ValueError):
        pass
    for key in ("reporting_period_start", "reporting_period_end"):
        parsed = _iso_date(requirement.get(key))
        if parsed:
            years.add(parsed.year)
    return years


def _date_ranges_overlap(
    left_start: date | None,
    left_end: date | None,
    right_start: date | None,
    right_end: date | None,
) -> bool | None:
    if not (left_start and left_end and right_start and right_end):
        return None
    return left_start <= right_end and right_start <= left_end


def _entry_doc_requirement_period_mismatch(
    entry: dict,
    doc: dict,
    requirement: dict,
) -> bool:
    """Reject stale coverage ids when the fetched document clearly says another period."""

    text = f"{_entry_text(entry)} {_doc_text(doc)}"
    if requirement.get("source_type") != "task_relevant_public_health_evidence":
        try:
            week_int = int(requirement.get("week"))
            year_int = int(requirement.get("year"))
        except (TypeError, ValueError):
            week_int = None
            year_int = None
        if week_int is not None and year_int is not None:
            explicit_pairs = _explicit_year_week_pairs(text)
            if explicit_pairs and (year_int, week_int) not in explicit_pairs:
                return True
            explicit_year_values = _explicit_years(text)
            if explicit_year_values and year_int not in explicit_year_values:
                return True

    requirement_years = _requirement_years(requirement)
    explicit_year_values = _explicit_years(text)
    if explicit_year_values and requirement_years and not (explicit_year_values & requirement_years):
        return True

    req_start = _iso_date(requirement.get("reporting_period_start"))
    req_end = _iso_date(requirement.get("reporting_period_end"))
    source_start = _iso_date(
        doc.get("reporting_period_start")
        or doc.get("metric_period_start")
        or entry.get("reporting_period_start")
    )
    source_end = _iso_date(
        doc.get("reporting_period_end")
        or doc.get("metric_period_end")
        or entry.get("reporting_period_end")
    )
    overlap = _date_ranges_overlap(req_start, req_end, source_start, source_end)
    if overlap is False:
        return True
    return False


def _not_task_collection_document(entry: dict, doc: dict) -> bool:
    if not _parse_succeeded(doc):
        return False
    if doc.get("usable_for_task_collection") is False:
        return True
    return _entry_is_non_target_context(entry) and doc.get("usable_for_task_collection") is not True


def _coverage_missing_reason(row: dict) -> str | None:
    if row.get("accepted"):
        return None
    if row.get("parsed"):
        return "parsed_no_records"
    if row.get("period_mismatch"):
        return "source_period_mismatch"
    if row.get("not_task_collection_document"):
        return "no_task_collection_document"
    if row.get("unusable"):
        return "target_alias_error_page"
    if row.get("fetch_failed"):
        return "target_fetch_failed"
    if row.get("fetch_attempted") and not row.get("fetched"):
        return "target_fetch_failed"
    if row.get("discovered"):
        return "target_source_discovered_not_fetched"
    return "target_source_missing"


def _repair_must_fetch_routing(entry: dict, requirement_ids: list[str], reason: str) -> dict:
    out = dict(entry)
    warnings = list(out.get("routing_conflict_warnings") or [])
    flags = list(out.get("routing_flags") or [])
    old_role = _lower(out.get("source_role_final"))
    old_level = _lower(out.get("credibility_level"))
    if old_role in {"excluded", "search_endpoint", "needs_human_review"}:
        _append_unique(warnings, f"source_role_final:{old_role}")
    if out.get("blocked_from_fetch"):
        _append_unique(warnings, "blocked_from_fetch:true")
    if _lower(out.get("final_screening_decision")) not in {
        "include_for_content_fetch",
        "include_for_context_fetch",
    }:
        _append_unique(
            warnings,
            f"final_screening_decision:{out.get('final_screening_decision')}",
        )
    out.update(
        {
            "must_fetch": True,
            "must_fetch_reason": reason,
            "coverage_requirement_ids": requirement_ids,
            "routing_conflict_warnings": warnings,
            "source_role_final": "collection",
            "final_screening_decision": "include_for_content_fetch",
            "ready_for_content_fetch": True,
            "blocked_from_fetch": False,
            "blocked_from_fetch_reason": None,
            "status": "ready_for_content_fetch",
        }
    )
    if old_level in {"", "excluded", "low", "needs_review"}:
        out["credibility_level"] = "high"
    if not out.get("credibility_score"):
        out["credibility_score"] = 0.95
    _append_unique(flags, "target_official_must_fetch")
    out["routing_flags"] = flags
    return out


def build_source_coverage_audit(
    requirements: list[dict],
    registry: list[dict],
    documents: list[dict] | None = None,
) -> dict:
    documents = documents or []
    docs_by_source = {str(doc.get("source_id")): doc for doc in documents if isinstance(doc, dict)}
    rows: list[dict] = []
    for requirement in requirements:
        rid = requirement["requirement_id"]
        matches = [
            entry for entry in registry
            if rid in (entry.get("coverage_requirement_ids") or [])
        ]
        attempted = [
            entry
            for entry in matches
            if str(entry.get("source_id")) in docs_by_source
        ]
        fetched = [
            entry
            for entry in attempted
            if _fetch_succeeded(docs_by_source[str(entry.get("source_id"))])
        ]
        fetch_failed = [
            entry
            for entry in attempted
            if not _fetch_succeeded(docs_by_source[str(entry.get("source_id"))])
        ]
        period_mismatch = [
            entry
            for entry in fetched
            if _entry_doc_requirement_period_mismatch(
                entry,
                docs_by_source[str(entry.get("source_id"))],
                requirement,
            )
        ]
        period_mismatch_ids = {str(entry.get("source_id")) for entry in period_mismatch}
        parsed = [
            entry for entry in fetched
            if _coverage_parse_succeeded(entry, docs_by_source[str(entry.get("source_id"))])
            and str(entry.get("source_id")) not in period_mismatch_ids
        ]
        not_task_collection = [
            entry
            for entry in fetched
            if _not_task_collection_document(
                entry,
                docs_by_source[str(entry.get("source_id"))],
            )
        ]
        unusable = [
            entry
            for entry in attempted
            if not _coverage_parse_succeeded(
                entry,
                docs_by_source[str(entry.get("source_id"))],
            )
        ]
        row = {
                **requirement,
                "discovered": bool(matches),
                "matched_source_ids": [m.get("source_id") for m in matches],
                "fetched": bool(fetched),
                "fetched_source_ids": [m.get("source_id") for m in fetched],
                "fetch_attempted": bool(attempted),
                "fetch_attempted_source_ids": [m.get("source_id") for m in attempted],
                "fetch_failed": bool(fetch_failed),
                "fetch_failed_source_ids": [m.get("source_id") for m in fetch_failed],
                "parsed": bool(parsed),
                "parsed_source_ids": [m.get("source_id") for m in parsed],
                "period_mismatch": bool(period_mismatch),
                "period_mismatch_source_ids": [
                    m.get("source_id") for m in period_mismatch
                ],
                "not_task_collection_document": bool(not_task_collection),
                "not_task_collection_source_ids": [
                    m.get("source_id") for m in not_task_collection
                ],
                "unusable": bool(unusable),
                "unusable_source_ids": [m.get("source_id") for m in unusable],
            }
        row["missing_reason"] = _coverage_missing_reason(row)
        rows.append(row)
    requirement_count = len(requirements)
    discovered_count = sum(1 for row in rows if row["discovered"])
    fetched_count = sum(1 for row in rows if row["fetched"])
    fetch_failed_count = sum(1 for row in rows if row["fetch_failed"])
    unusable_count = sum(1 for row in rows if row["unusable"])
    period_mismatch_count = sum(1 for row in rows if row.get("period_mismatch"))
    parsed_count = sum(1 for row in rows if row["parsed"])
    # Initial source coverage is intentionally pre-extraction and therefore
    # cannot prove strict target coverage. Finalization refreshes this audit
    # with accepted exact record ids; until then parsed documents mean
    # "available for extraction", not "requirement complete".
    complete_requirement_count = 0
    partial_requirement_count = (
        requirement_count - complete_requirement_count if requirement_count else 0
    )
    missing_requirement_ids = [
        row.get("requirement_id")
        for row in rows
        if row.get("requirement_id") and not row.get("accepted")
    ]
    if not requirement_count:
        coverage_completeness_status = "not_required"
    else:
        coverage_completeness_status = "no_target_coverage"
    if not requirement_count:
        coverage_status = "not_required"
    elif parsed_count:
        coverage_status = "parsed_no_records"
    elif period_mismatch_count:
        coverage_status = "target_source_period_mismatch"
    elif fetch_failed_count and not fetched_count:
        coverage_status = "target_official_source_fetch_failed"
    elif fetched_count and unusable_count and not parsed_count:
        coverage_status = "target_official_source_unusable"
    elif fetched_count:
        coverage_status = "fetched_not_parsed"
    elif discovered_count:
        coverage_status = "target_official_source_discovered_not_fetched"
    else:
        coverage_status = "target_official_source_missing"
    return {
        "requirement_count": len(requirements),
        "discovered_requirement_count": discovered_count,
        "fetched_requirement_count": fetched_count,
        "fetch_failed_requirement_count": fetch_failed_count,
        "unusable_requirement_count": unusable_count,
        "period_mismatch_requirement_count": period_mismatch_count,
        "parsed_requirement_count": parsed_count,
        "complete_requirement_count": complete_requirement_count,
        "partial_requirement_count": partial_requirement_count,
        "missing_requirement_ids": missing_requirement_ids,
        "coverage_completeness_status": coverage_completeness_status,
        "coverage_status": coverage_status,
        "requirements": rows,
    }


def annotate_source_coverage(
    registry: list[dict],
    state: dict,
    *,
    documents: list[dict] | None = None,
) -> tuple[list[dict], list[dict], dict]:
    """Annotate task-critical official sources and return coverage diagnostics."""

    requirements = build_source_coverage_requirements(state)
    if not requirements:
        return [dict(row) for row in registry], [], build_source_coverage_audit([], [], documents)

    updated: list[dict] = []
    for entry in registry:
        row = deepcopy(entry)
        matched = [req for req in requirements if _matches_requirement(row, req)]
        if matched:
            ids = [req["requirement_id"] for req in matched]
            reason = " ".join(req["reason"] for req in matched)
            row = _repair_must_fetch_routing(row, ids, reason)
            first = matched[0]
            for key in (
                "reporting_period_start",
                "reporting_period_end",
                "reporting_period_label",
                "period_basis",
            ):
                if not row.get(key):
                    row[key] = first.get(key)
        updated.append(row)
    audit = build_source_coverage_audit(requirements, updated, documents)
    return updated, requirements, audit
