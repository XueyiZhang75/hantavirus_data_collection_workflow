"""Source discovery and registry nodes.

Default behavior remains the offline seed catalog. Stage 5 adds controlled,
bounded fixture/live search execution from agentic_source_plan.planned_queries.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from hashlib import sha256
import os
import re
from urllib.parse import urlsplit, urlunsplit

from ..config import load_hantavirus_seed_sources
from ..models import (
    SearchProviderResponse,
    SearchResult,
    SeedSource,
    SeedSourceCatalog,
    SourceCandidate,
    SourceRegistryEntry,
)
from ..search_providers import FixtureSearchProvider, build_search_provider
from ..state import DataCollectionState, append_trace

_FIXED_RETRIEVED_AT = "2026-05-25T00:00:00Z"
_DISCOVERY_METHOD = "offline_seed_catalog"
_SEARCH_RESULT_DISCOVERY_METHOD = {
    "fixture": "fixture_search_result",
    "live": "live_search_result",
}
_DEFAULT_PROVIDER_CHANNEL_ALLOWLIST = [
    "web_search",
    "official_site_search",
    "news_search",
    "literature_api",
    "database_search",
]
_ALLOWED_SEARCH_STATUSES = {
    "executed",
    "skipped_search_disabled",
    "skipped_provider_channel_not_supported",
    "skipped_query_limit",
    "skipped_total_result_limit",
    "skipped_invalid_query",
    "provider_error",
    "no_results",
}
_RAW_URL_ONLY_RE = re.compile(r"^\s*(https?://|www\.)\S+\s*$", re.IGNORECASE)


@dataclass(frozen=True)
class SourceSearchSettings:
    mode: str = "disabled"
    provider: str = "tavily"
    fixture_path: str | None = None
    max_queries: int = 3
    max_results_per_query: int = 5
    max_total_results: int = 15
    timeout_seconds: float = 15.0
    combine_with_seed_catalog: bool = True
    cache_enabled: bool = True
    provider_channel_allowlist: list[str] = field(
        default_factory=lambda: list(_DEFAULT_PROVIDER_CHANNEL_ALLOWLIST)
    )

    @property
    def fixture_search_enabled(self) -> bool:
        return self.mode == "fixture"

    @property
    def live_search_enabled(self) -> bool:
        return self.mode == "live" and _env_bool("HDC_ENABLE_LIVE_SEARCH", False)

    @property
    def search_enabled(self) -> bool:
        return self.fixture_search_enabled or self.live_search_enabled


def canonicalize_url(url: str) -> str:
    """Canonicalize a URL or seed:// URI for deduplication.

    - strip surrounding whitespace
    - drop URL fragment (after "#")
    - strip trailing slash on the path
    - lowercase scheme and host when present
    - preserve query string (search endpoints depend on it)
    - leave seed:// URIs intact (lowercase scheme; preserve the rest)
    """

    if url is None:
        return ""
    stripped = url.strip()
    if not stripped:
        return ""

    parts = urlsplit(stripped)
    scheme = parts.scheme.lower()
    netloc = parts.netloc.lower()
    path = parts.path or ""
    if scheme in {"http", "https"}:
        path = re.sub(r"/{2,}", "/", path)
    if path.endswith("/") and len(path) > 1:
        path = path.rstrip("/")
    # Drop fragment, preserve query.
    rebuilt = urlunsplit((scheme, netloc, path, parts.query, ""))

    # urlsplit on seed://... places "structured-database" in netloc — that's fine.
    # If there was no scheme and no netloc, fall back to stripped form minus fragment.
    if not scheme and not netloc:
        rebuilt = stripped.split("#", 1)[0]
        if rebuilt.endswith("/") and len(rebuilt) > 1:
            rebuilt = rebuilt.rstrip("/")
    return rebuilt


def _env_bool(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None or not str(raw).strip():
        return default
    return str(raw).strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    raw = (os.environ.get(name) or "").strip()
    if not raw:
        return default
    try:
        value = int(raw)
    except ValueError:
        return default
    return value if value > 0 else default


def _env_float(name: str, default: float) -> float:
    raw = (os.environ.get(name) or "").strip()
    if not raw:
        return default
    try:
        value = float(raw)
    except ValueError:
        return default
    return value if value > 0 else default


def _env_csv(name: str, default: list[str]) -> list[str]:
    raw = os.environ.get(name)
    if raw is None or not raw.strip():
        return list(default)
    values = [part.strip() for part in raw.split(",") if part.strip()]
    return values or list(default)


def _source_search_settings_from_env() -> SourceSearchSettings:
    mode = (os.environ.get("HDC_SEARCH_MODE") or "disabled").strip().lower()
    if mode not in {"disabled", "fixture", "live"}:
        mode = "disabled"
    provider = (os.environ.get("HDC_SEARCH_PROVIDER") or "").strip().lower()
    if not provider:
        provider = "fixture" if mode == "fixture" else "tavily"
    return SourceSearchSettings(
        mode=mode,
        provider=provider,
        fixture_path=(os.environ.get("HDC_SEARCH_FIXTURE_PATH") or "").strip() or None,
        max_queries=_env_int("HDC_SEARCH_MAX_QUERIES", 3),
        max_results_per_query=_env_int("HDC_SEARCH_MAX_RESULTS_PER_QUERY", 5),
        max_total_results=_env_int("HDC_SEARCH_MAX_TOTAL_RESULTS", 15),
        timeout_seconds=_env_float("HDC_SEARCH_TIMEOUT_SECONDS", 15.0),
        combine_with_seed_catalog=_env_bool(
            "HDC_SEARCH_COMBINE_WITH_SEED_CATALOG", True
        ),
        cache_enabled=_env_bool("HDC_SEARCH_CACHE_ENABLED", True),
        provider_channel_allowlist=_env_csv(
            "HDC_SEARCH_PROVIDER_CHANNEL_ALLOWLIST",
            _DEFAULT_PROVIDER_CHANNEL_ALLOWLIST,
        ),
    )


def _best_matching_query(
    seed_source: dict,
    search_query_inventory: list[dict],
) -> dict | None:
    """Pick the most relevant query for a seed source, or None.

    Preference order:
      1. queries whose source_type matches and whose query string contains
         any of the seed source's match_terms (case-insensitive).
      2. the first query whose source_type matches.
      3. None.
    """

    if not search_query_inventory:
        return None

    target_type = seed_source.get("source_type")
    same_type = [
        q for q in search_query_inventory
        if q.get("source_type") == target_type
    ]
    if not same_type:
        return None

    match_terms = [t.lower() for t in seed_source.get("match_terms", []) if t]
    for query in same_type:
        query_text = (query.get("query") or "").lower()
        if any(term in query_text for term in match_terms):
            return query
    return same_type[0]


def _make_source_candidate(
    seed_source: SeedSource,
    matched_query: dict | None,
) -> SourceCandidate:
    """Build a deterministic SourceCandidate from a seed source."""

    source_id = seed_source.seed_source_id
    if source_id.startswith("seed_"):
        source_id = "src_" + source_id[len("seed_"):]

    query_id = matched_query.get("query_id") if matched_query else None
    query_used = matched_query.get("query") if matched_query else None

    return SourceCandidate(
        source_id=source_id,
        title=seed_source.title,
        url=seed_source.url,
        publisher=seed_source.publisher,
        source_type=seed_source.source_type,
        published_date=None,
        snippet=None,
        query_used=query_used,
        retrieved_at=_FIXED_RETRIEVED_AT,
        query_id=query_id,
        discovery_method=_DISCOVERY_METHOD,
        seed_source_id=seed_source.seed_source_id,
        priority=seed_source.priority,
        expected_fields=list(seed_source.expected_fields),
        matched_terms=list(seed_source.match_terms),
        source_purpose=seed_source.source_purpose,
        notes=seed_source.notes,
    )


def _planned_queries(state: DataCollectionState) -> list[dict]:
    plan = state.get("agentic_source_plan") or {}
    queries = plan.get("planned_queries") if isinstance(plan, dict) else None
    return [dict(item) for item in queries or [] if isinstance(item, dict)]


def _search_execution_record(
    query: dict,
    *,
    provider: str,
    status: str,
    selected: bool = False,
    result_count: int = 0,
    skipped_reason: str | None = None,
    error: str | None = None,
) -> dict:
    if status not in _ALLOWED_SEARCH_STATUSES:
        raise ValueError(f"unsupported search execution status: {status}")
    return {
        "query_id": query.get("query_id"),
        "query": query.get("query"),
        "provider_channel": query.get("provider_channel"),
        "query_type": query.get("query_type"),
        "source_type": query.get("source_type"),
        "role_hint": query.get("role_hint"),
        "selected_for_execution": bool(selected),
        "execution_status": status,
        "provider": provider,
        "result_count": int(result_count or 0),
        "skipped_reason": skipped_reason,
        "error": error,
    }


def _is_invalid_query(query: dict) -> bool:
    text = str(query.get("query") or "").strip()
    if not text:
        return True
    if _RAW_URL_ONLY_RE.match(text):
        return True
    return str(query.get("execution_status") or "planned_not_executed") != (
        "planned_not_executed"
    )


def _domain(url: str) -> str | None:
    netloc = urlsplit(url).netloc.lower()
    if not netloc:
        return None
    return netloc[4:] if netloc.startswith("www.") else netloc


def _validate_search_url(url: str | None) -> tuple[str | None, str | None]:
    if url is None or not str(url).strip():
        return None, "missing_url"
    canonical = canonicalize_url(str(url))
    parts = urlsplit(canonical)
    if not parts.scheme:
        return None, "invalid_url"
    if parts.scheme not in {"http", "https"}:
        return None, "unsupported_scheme"
    if not parts.netloc:
        return None, "invalid_url"
    return canonical, None


def _source_id_from_canonical_url(canonical_url: str) -> str:
    digest = sha256(canonical_url.encode("utf-8")).hexdigest()[:12]
    return f"src_search_{digest}"


def _response_from_provider_output(
    output,
    *,
    provider: str,
    planned_query: dict,
) -> SearchProviderResponse:
    if isinstance(output, SearchProviderResponse):
        return output
    if isinstance(output, dict):
        raw_results = output.get("results") or []
        results = []
        for index, item in enumerate(raw_results, start=1):
            if isinstance(item, SearchResult):
                results.append(item)
            elif isinstance(item, dict):
                results.append(
                    SearchResult(
                        title=item.get("title"),
                        url=item.get("url"),
                        snippet=item.get("snippet") or item.get("content"),
                        published_date=item.get("published_date") or item.get("date"),
                        source=item.get("source") or item.get("publisher"),
                        rank=int(item.get("rank") or index),
                        query=planned_query.get("query"),
                        query_id=planned_query.get("query_id"),
                        provider_channel=planned_query.get("provider_channel"),
                        source_type=planned_query.get("source_type"),
                        role_hint=planned_query.get("role_hint"),
                        retrieved_at=item.get("retrieved_at") or _FIXED_RETRIEVED_AT,
                        provider=output.get("provider") or provider,
                        query_type=planned_query.get("query_type"),
                        raw=dict(item),
                    )
                )
        return SearchProviderResponse(
            provider=output.get("provider") or provider,
            query_id=output.get("query_id") or planned_query.get("query_id"),
            query=output.get("query") or planned_query.get("query"),
            results=results,
            raw_result_count=int(output.get("raw_result_count") or len(results)),
            error=output.get("error"),
            warnings=list(output.get("warnings") or []),
        )
    raise TypeError(f"Unsupported search provider response type: {type(output)!r}")


def _build_search_provider(settings: SourceSearchSettings):
    return build_search_provider(
        provider=settings.provider,
        mode=settings.mode,
        fixture_path=settings.fixture_path,
    )


def _provider_for_settings(settings: SourceSearchSettings):
    if settings.mode == "fixture":
        if not settings.fixture_path:
            raise ValueError("fixture search mode requires HDC_SEARCH_FIXTURE_PATH")
        return FixtureSearchProvider(settings.fixture_path)
    return _build_search_provider(settings)


def _candidate_from_search_result(
    result: SearchResult,
    planned_query: dict,
    *,
    settings: SourceSearchSettings,
    canonical_url: str,
) -> SourceCandidate:
    domain = _domain(canonical_url)
    discovery_method = _SEARCH_RESULT_DISCOVERY_METHOD.get(settings.mode)
    source_id = _source_id_from_canonical_url(canonical_url)
    matched_terms = [
        *list(planned_query.get("disease_terms_used") or []),
        *list(planned_query.get("location_terms_used") or []),
        *list(planned_query.get("time_terms_used") or []),
    ]
    return SourceCandidate(
        source_id=source_id,
        title=result.title,
        url=result.url or canonical_url,
        publisher=result.source or domain,
        source_type=planned_query.get("source_type") or result.source_type,
        published_date=result.published_date,
        snippet=result.snippet,
        query_used=planned_query.get("query") or result.query,
        retrieved_at=result.retrieved_at or _FIXED_RETRIEVED_AT,
        query_id=planned_query.get("query_id") or result.query_id,
        discovery_method=discovery_method,
        seed_source_id=None,
        priority=planned_query.get("priority"),
        expected_fields=list(planned_query.get("expected_fields") or []),
        matched_terms=matched_terms,
        source_purpose=(
            f"{planned_query.get('role_hint')}_search_result"
            if planned_query.get("role_hint")
            else "search_discovered_source"
        ),
        notes=(
            f"Search-derived source candidate from {settings.mode} "
            f"{settings.provider} metadata; page body not fetched by search."
        ),
        search_provider=settings.provider,
        search_rank=result.rank,
        provider_channel=planned_query.get("provider_channel") or result.provider_channel,
        role_hint=planned_query.get("role_hint") or result.role_hint,
        planned_query_id=planned_query.get("query_id"),
        planned_query_source_type=planned_query.get("source_type"),
        search_result_id=f"{planned_query.get('query_id')}_{result.rank or 0}",
        canonical_url=canonical_url,
        domain=domain,
        result_source=result.source,
        query_type=planned_query.get("query_type") or result.query_type,
        additional_query_ids=[],
    )


def _execute_source_search(
    state: DataCollectionState,
    settings: SourceSearchSettings,
) -> tuple[list[SourceCandidate], list[dict], dict]:
    planned_queries = _planned_queries(state)
    query_records: list[dict] = []
    search_results_manifest: list[dict] = []
    search_candidates: list[SourceCandidate] = []
    rejection_counter: Counter = Counter()
    warnings: list[str] = []
    provider_error_count = 0
    selected_query_count = 0
    executed_query_count = 0
    raw_result_count = 0
    deduped_result_count = 0
    seen_canonical_urls: set[str] = set()

    provider = None
    if settings.search_enabled:
        try:
            provider = _provider_for_settings(settings)
        except (OSError, ValueError) as exc:
            provider_error_count += 1
            warnings.append(f"search_provider_setup_failed:{exc}")

    for query in planned_queries:
        channel = str(query.get("provider_channel") or "")
        if not settings.search_enabled:
            query_records.append(
                _search_execution_record(
                    query,
                    provider=settings.provider,
                    status="skipped_search_disabled",
                    skipped_reason="search_disabled",
                )
            )
            continue
        if _is_invalid_query(query):
            query_records.append(
                _search_execution_record(
                    query,
                    provider=settings.provider,
                    status="skipped_invalid_query",
                    skipped_reason="empty_non_planned_or_raw_url_query",
                )
            )
            continue
        if channel not in set(settings.provider_channel_allowlist):
            query_records.append(
                _search_execution_record(
                    query,
                    provider=settings.provider,
                    status="skipped_provider_channel_not_supported",
                    skipped_reason="provider_channel_not_in_allowlist",
                )
            )
            continue
        if selected_query_count >= settings.max_queries:
            query_records.append(
                _search_execution_record(
                    query,
                    provider=settings.provider,
                    status="skipped_query_limit",
                    skipped_reason="max_queries_reached",
                )
            )
            continue
        if deduped_result_count >= settings.max_total_results:
            query_records.append(
                _search_execution_record(
                    query,
                    provider=settings.provider,
                    status="skipped_total_result_limit",
                    skipped_reason="max_total_results_reached",
                )
            )
            continue
        if provider is None:
            provider_error_count += 1
            query_records.append(
                _search_execution_record(
                    query,
                    provider=settings.provider,
                    status="provider_error",
                    selected=True,
                    error="provider_unavailable",
                )
            )
            continue

        selected_query_count += 1
        try:
            provider_output = provider.search(
                query,
                max_results=settings.max_results_per_query,
                timeout_seconds=settings.timeout_seconds,
            )
            response = _response_from_provider_output(
                provider_output,
                provider=settings.provider,
                planned_query=query,
            )
        except Exception as exc:  # pragma: no cover - provider faults are summarized.
            provider_error_count += 1
            query_records.append(
                _search_execution_record(
                    query,
                    provider=settings.provider,
                    status="provider_error",
                    selected=True,
                    error=f"{exc.__class__.__name__}",
                )
            )
            continue

        if response.error:
            provider_error_count += 1
            query_records.append(
                _search_execution_record(
                    query,
                    provider=response.provider,
                    status="provider_error",
                    selected=True,
                    error=response.error,
                )
            )
            continue

        raw_result_count += response.raw_result_count
        warnings.extend(response.warnings or [])
        if not response.results:
            query_records.append(
                _search_execution_record(
                    query,
                    provider=response.provider,
                    status="no_results",
                    selected=True,
                )
            )
            continue

        accepted_for_query = 0
        for result in response.results:
            if deduped_result_count >= settings.max_total_results:
                rejection_counter["result_limit_reached"] += 1
                search_results_manifest.append(
                    {
                        **result.model_dump(),
                        "result_status": "rejected",
                        "rejection_reason": "result_limit_reached",
                    }
                )
                continue
            canonical_url, rejection_reason = _validate_search_url(result.url)
            if rejection_reason:
                rejection_counter[rejection_reason] += 1
                search_results_manifest.append(
                    {
                        **result.model_dump(),
                        "result_status": "rejected",
                        "rejection_reason": rejection_reason,
                    }
                )
                continue
            if not ((result.title or "").strip() or (result.snippet or "").strip()):
                rejection_counter["empty_title_and_snippet"] += 1
                search_results_manifest.append(
                    {
                        **result.model_dump(),
                        "canonical_url": canonical_url,
                        "result_status": "rejected",
                        "rejection_reason": "empty_title_and_snippet",
                    }
                )
                continue
            if canonical_url in seen_canonical_urls:
                rejection_counter["duplicate_url"] += 1
                search_results_manifest.append(
                    {
                        **result.model_dump(),
                        "canonical_url": canonical_url,
                        "result_status": "rejected",
                        "rejection_reason": "duplicate_url",
                    }
                )
                continue

            seen_canonical_urls.add(canonical_url)
            deduped_result_count += 1
            accepted_for_query += 1
            candidate = _candidate_from_search_result(
                result,
                query,
                settings=settings,
                canonical_url=canonical_url,
            )
            search_candidates.append(candidate)
            search_results_manifest.append(
                {
                    **result.model_dump(),
                    "source_id": candidate.source_id,
                    "canonical_url": canonical_url,
                    "domain": candidate.domain,
                    "result_status": "accepted",
                    "rejection_reason": None,
                }
            )

        executed_query_count += 1
        query_records.append(
            _search_execution_record(
                query,
                provider=response.provider,
                status="executed" if accepted_for_query else "no_results",
                selected=True,
                result_count=accepted_for_query,
            )
        )

    skipped_query_count = sum(
        1
        for record in query_records
        if str(record.get("execution_status") or "").startswith("skipped_")
    )
    summary = {
        "search_enabled": settings.search_enabled,
        "live_search_enabled": settings.live_search_enabled,
        "fixture_search_enabled": settings.fixture_search_enabled,
        "search_mode": settings.mode,
        "search_provider": settings.provider,
        "combine_with_seed_catalog": settings.combine_with_seed_catalog,
        "planned_query_count": len(planned_queries),
        "selected_query_count": selected_query_count,
        "executed_query_count": executed_query_count,
        "skipped_query_count": skipped_query_count,
        "raw_search_result_count": raw_result_count,
        "deduplicated_search_result_count": deduped_result_count,
        "rejected_search_result_count": sum(rejection_counter.values()),
        "candidate_from_search_count": len(search_candidates),
        "candidate_from_seed_count": 0,
        "total_candidate_count": len(search_candidates),
        "provider_error_count": provider_error_count,
        "max_queries": settings.max_queries,
        "max_results_per_query": settings.max_results_per_query,
        "max_total_results": settings.max_total_results,
        "query_execution_records": query_records,
        "rejection_reason_counts": dict(rejection_counter),
        "search_result_source_ids": [candidate.source_id for candidate in search_candidates],
        "warnings": sorted(set(warnings)),
    }
    return search_candidates, search_results_manifest, summary


def source_discovery(state: DataCollectionState) -> dict:
    """Produce SourceCandidates from seed catalog and optional source search."""

    catalog_dict = load_hantavirus_seed_sources()
    catalog = SeedSourceCatalog(**catalog_dict)
    settings = _source_search_settings_from_env()

    search_query_inventory = list(state.get("search_query_inventory") or [])

    seed_candidates: list[SourceCandidate] = []
    for seed in catalog.seed_sources:
        matched = _best_matching_query(seed.model_dump(), search_query_inventory)
        seed_candidates.append(_make_source_candidate(seed, matched))

    search_candidates, search_results_manifest, search_summary = _execute_source_search(
        state, settings
    )
    include_seeds = (not settings.search_enabled) or settings.combine_with_seed_catalog
    candidates = [
        *(seed_candidates if include_seeds else []),
        *search_candidates,
    ]

    candidate_dicts = [c.model_dump() for c in candidates]

    source_type_counts = dict(
        Counter(c.source_type or "unknown" for c in candidates)
    )
    matched_query_count = sum(1 for c in candidates if c.query_id is not None)
    unmatched_query_count = len(candidates) - matched_query_count
    candidate_from_seed_count = len(seed_candidates) if include_seeds else 0
    candidate_from_search_count = len(search_candidates)

    if not settings.search_enabled:
        discovery_method = _DISCOVERY_METHOD
    elif settings.mode == "fixture":
        discovery_method = (
            "fixture_search_plus_seed_catalog"
            if include_seeds else "fixture_search_only"
        )
    elif settings.mode == "live":
        discovery_method = (
            "live_search_plus_seed_catalog"
            if include_seeds else "live_search_only"
        )
    else:
        discovery_method = _DISCOVERY_METHOD

    search_summary.update(
        {
            "candidate_from_seed_count": candidate_from_seed_count,
            "total_candidate_count": len(candidates),
        }
    )

    summary = {
        "discovery_method": discovery_method,
        "seed_source_count": len(catalog.seed_sources),
        "candidate_count": len(candidates),
        "source_type_counts": source_type_counts,
        "matched_query_count": matched_query_count,
        "unmatched_query_count": unmatched_query_count,
        "search_enabled": settings.search_enabled,
        "search_mode": settings.mode,
        "search_provider": settings.provider,
        "candidate_from_search_count": candidate_from_search_count,
        "candidate_from_seed_count": candidate_from_seed_count,
        "total_candidate_count": len(candidates),
        "executed_query_count": search_summary.get("executed_query_count", 0),
        "raw_search_result_count": search_summary.get("raw_search_result_count", 0),
        "rejected_search_result_count": search_summary.get(
            "rejected_search_result_count", 0
        ),
    }

    trace = append_trace(
        state,
        node_name="source_discovery",
        message=(
            f"Discovered {len(candidates)} source candidates using "
            f"{discovery_method}."
        ),
        metadata={**summary, "source_search_execution_summary": search_summary},
    )
    return {
        "source_candidates": candidate_dicts,
        "source_search_results": search_results_manifest,
        "source_search_execution_summary": search_summary,
        "source_discovery_summary": summary,
        "collection_trace": trace,
    }


def source_dedup_and_registry(state: DataCollectionState) -> dict:
    """Canonicalize, deduplicate, and register source candidates.

    Keeps the first occurrence per canonical URL and counts duplicates.
    """

    candidates = list(state.get("source_candidates") or [])
    registry: list[SourceRegistryEntry] = []
    seen_urls: set[str] = set()
    duplicate_count = 0

    for candidate in candidates:
        url = candidate.get("url") or ""
        canonical = canonicalize_url(url)
        if not canonical:
            duplicate_count += 1
            continue
        if canonical in seen_urls:
            duplicate_count += 1
            continue
        seen_urls.add(canonical)

        entry = SourceRegistryEntry(
            source_id=candidate.get("source_id") or canonical,
            canonical_url=canonical,
            title=candidate.get("title"),
            publisher=candidate.get("publisher"),
            source_type=candidate.get("source_type"),
            published_date=candidate.get("published_date"),
            status="registered",
            query_id=candidate.get("query_id"),
            query_used=candidate.get("query_used"),
            discovery_method=candidate.get("discovery_method"),
            seed_source_id=candidate.get("seed_source_id"),
            priority=candidate.get("priority"),
            expected_fields=list(candidate.get("expected_fields") or []),
            matched_terms=list(candidate.get("matched_terms") or []),
            source_purpose=candidate.get("source_purpose"),
            notes=candidate.get("notes"),
            search_provider=candidate.get("search_provider"),
            search_rank=candidate.get("search_rank"),
            provider_channel=candidate.get("provider_channel"),
            role_hint=candidate.get("role_hint"),
            planned_query_id=candidate.get("planned_query_id"),
            planned_query_source_type=candidate.get("planned_query_source_type"),
            search_result_id=candidate.get("search_result_id"),
            domain=candidate.get("domain"),
            result_source=candidate.get("result_source"),
            query_type=candidate.get("query_type"),
            additional_query_ids=list(candidate.get("additional_query_ids") or []),
        )
        registry.append(entry)

    registry_dicts = [e.model_dump() for e in registry]
    source_type_counts = dict(
        Counter(e.source_type or "unknown" for e in registry)
    )
    search_derived_entry_count = sum(
        1
        for entry in registry_dicts
        if entry.get("discovery_method")
        in {"fixture_search_result", "live_search_result"}
    )

    summary = {
        "input_candidate_count": len(candidates),
        "registry_entry_count": len(registry),
        "duplicate_count": duplicate_count,
        "source_type_counts": source_type_counts,
        "search_derived_entry_count": search_derived_entry_count,
    }

    trace = append_trace(
        state,
        node_name="source_dedup_and_registry",
        message=(
            f"Built source registry with {len(registry)} entries "
            f"({duplicate_count} duplicates dropped)."
        ),
        metadata=summary,
    )
    return {
        "source_registry": registry_dicts,
        "source_registry_summary": summary,
        "collection_trace": trace,
    }
