"""Source discovery and registry nodes (Step 3: offline seed catalog, no network)."""

from __future__ import annotations

from collections import Counter
from urllib.parse import urlsplit, urlunsplit

from ..config import load_hantavirus_seed_sources
from ..models import SeedSource, SeedSourceCatalog, SourceCandidate, SourceRegistryEntry
from ..state import DataCollectionState, append_trace

_FIXED_RETRIEVED_AT = "2026-05-25T00:00:00Z"
_DISCOVERY_METHOD = "offline_seed_catalog"


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


def source_discovery(state: DataCollectionState) -> dict:
    """Produce SourceCandidates from the offline seed source catalog.

    No real web search is performed in Step 3.
    """

    catalog_dict = load_hantavirus_seed_sources()
    catalog = SeedSourceCatalog(**catalog_dict)

    search_query_inventory = list(state.get("search_query_inventory") or [])

    candidates: list[SourceCandidate] = []
    for seed in catalog.seed_sources:
        matched = _best_matching_query(seed.model_dump(), search_query_inventory)
        candidates.append(_make_source_candidate(seed, matched))

    candidate_dicts = [c.model_dump() for c in candidates]

    source_type_counts = dict(
        Counter(c.source_type or "unknown" for c in candidates)
    )
    matched_query_count = sum(1 for c in candidates if c.query_id is not None)
    unmatched_query_count = len(candidates) - matched_query_count

    summary = {
        "discovery_method": _DISCOVERY_METHOD,
        "seed_source_count": len(catalog.seed_sources),
        "candidate_count": len(candidates),
        "source_type_counts": source_type_counts,
        "matched_query_count": matched_query_count,
        "unmatched_query_count": unmatched_query_count,
    }

    trace = append_trace(
        state,
        node_name="source_discovery",
        message=(
            f"Discovered {len(candidates)} source candidates from the offline seed "
            f"catalog (no web search)."
        ),
        metadata=summary,
    )
    return {
        "source_candidates": candidate_dicts,
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
        )
        registry.append(entry)

    registry_dicts = [e.model_dump() for e in registry]
    source_type_counts = dict(
        Counter(e.source_type or "unknown" for e in registry)
    )

    summary = {
        "input_candidate_count": len(candidates),
        "registry_entry_count": len(registry),
        "duplicate_count": duplicate_count,
        "source_type_counts": source_type_counts,
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
