"""Content fetching, parsing, and document quality (Step 5).

Default behavior is fully offline: when `HDC_ENABLE_LIVE_FETCH` is not set to
"true", the workflow generates deterministic metadata-stub documents and does
NOT contact the network. Live HTTP fetching is gated behind that environment
variable so tests stay offline-safe.
"""

from __future__ import annotations

import hashlib
import json
import os
from collections import Counter
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

import re

from ..config import (
    get_collection_mode,
    load_content_fetch_policy,
    load_evidence_chunking_policy,
    load_hantavirus_fixture_documents,
    load_source_role_policy,
)
from ..disease_relevance import (
    TARGET_DISEASE_MATCH,
    UNRELATED_DISEASE,
    AMBIGUOUS_DISEASE,
    assessment_fields,
    assess_chunk_disease_relevance,
    assess_document_disease_relevance,
    build_disease_relevance_context,
    update_disease_relevance_summary,
)
from ..models import (
    ContentFetchPolicy,
    ContentFetchRequest,
    Document,
    EvidenceChunk,
    EvidenceChunkingPolicy,
    FixtureDocument,
    FixtureDocumentCatalog,
)
from ..state import DataCollectionState, append_trace

_OFFLINE_FIXED_TIMESTAMP = "2026-05-25T00:00:00Z"
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_SEARCH_DERIVED_DISCOVERY_METHODS = {"fixture_search_result", "live_search_result"}
_SEARCH_DERIVED_FETCH_FINAL_ROLES = {
    "collection",
    "validation",
    "collection_support",
    "context",
}
_SEARCH_DERIVED_BLOCKED_FINAL_ROLES = {
    "excluded",
    "search_endpoint",
    "needs_human_review",
}


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------


def _live_fetch_enabled() -> bool:
    """True only if HDC_ENABLE_LIVE_FETCH is set to "true" (case-insensitive)."""

    return (os.environ.get("HDC_ENABLE_LIVE_FETCH") or "").strip().lower() == "true"


def _fixture_documents_enabled() -> bool:
    """True only if HDC_USE_FIXTURE_DOCUMENTS is set to "true" (case-insensitive)."""

    return (os.environ.get("HDC_USE_FIXTURE_DOCUMENTS") or "").strip().lower() == "true"


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
    return value if value >= 0 else default


def _env_csv(name: str, default: list[str] | None = None) -> list[str]:
    raw = os.environ.get(name)
    if raw is None or not raw.strip():
        return list(default or [])
    values = [part.strip() for part in raw.split(",") if part.strip()]
    return values or list(default or [])


def _fetch_config_from_env(policy: ContentFetchPolicy) -> dict:
    request_cfg = policy.request or {}
    return {
        "fetch_search_derived_sources": _env_bool(
            "HDC_FETCH_SEARCH_DERIVED_SOURCES", False
        ),
        "max_search_derived_sources": _env_int(
            "HDC_FETCH_MAX_SEARCH_DERIVED_SOURCES", 2
        ),
        "max_total_sources": _env_int("HDC_FETCH_MAX_TOTAL_SOURCES", 10),
        "min_credibility_score": _env_float(
            "HDC_FETCH_MIN_CREDIBILITY_SCORE", 0.55
        ),
        "allowed_final_roles": _env_csv(
            "HDC_FETCH_ALLOWED_FINAL_ROLES",
            sorted(_SEARCH_DERIVED_FETCH_FINAL_ROLES),
        ),
        "allow_needs_review": _env_bool("HDC_FETCH_ALLOW_NEEDS_REVIEW", False),
        "domain_allowlist": _env_csv("HDC_FETCH_DOMAIN_ALLOWLIST", []),
        "domain_blocklist": _env_csv("HDC_FETCH_DOMAIN_BLOCKLIST", []),
        "max_bytes": _env_int(
            "HDC_FETCH_MAX_BYTES",
            int(request_cfg.get("max_response_bytes") or 5_000_000),
        ),
        "user_agent": (
            os.environ.get("HDC_FETCH_USER_AGENT")
            or request_cfg.get("user_agent")
            or "data-collection-workflow/0.1"
        ),
        "parse_pdf_text": _env_bool("HDC_FETCH_PARSE_PDF_TEXT", True),
        "parse_tables": _env_bool("HDC_FETCH_PARSE_TABLES", True),
        "store_raw_text": _env_bool("HDC_FETCH_STORE_RAW_TEXT", False),
        "content_fixture_map_path": (
            os.environ.get("HDC_CONTENT_FIXTURE_MAP_PATH") or ""
        ).strip()
        or None,
    }


def _parse_source_id_allowlist() -> set[str] | None:
    """Read HDC_SOURCE_ID_ALLOWLIST. Return a set of source IDs or None."""

    raw = os.environ.get("HDC_SOURCE_ID_ALLOWLIST") or ""
    if not raw.strip():
        return None
    ids = {part.strip() for part in raw.split(",") if part.strip()}
    return ids or None


def _load_fixture_document_map() -> dict[str, FixtureDocument]:
    """Load the fixture document catalog and map source_id -> FixtureDocument."""

    catalog = FixtureDocumentCatalog(**load_hantavirus_fixture_documents())
    result: dict[str, FixtureDocument] = {}
    for fixture in catalog.fixture_documents:
        if fixture.source_id not in result:
            result[fixture.source_id] = fixture
    return result


def _load_content_fixture_map(path_value: str | None) -> list[dict]:
    if not path_value:
        return []
    path = _resolve_project_path(path_value)
    if not path.exists():
        raise FileNotFoundError(f"HDC_CONTENT_FIXTURE_MAP_PATH points to a missing file: {path}")
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    fixtures = data.get("fixtures") if isinstance(data, dict) else None
    if not isinstance(fixtures, list):
        raise ValueError(f"Content fixture map must contain a fixtures list: {path}")
    result: list[dict] = []
    for item in fixtures:
        if not isinstance(item, dict):
            continue
        fixture_path = item.get("fixture_path")
        if not fixture_path:
            continue
        normalized = dict(item)
        normalized["fixture_path"] = str(_resolve_project_path(fixture_path))
        result.append(normalized)
    return result


def _fixture_for_request(
    request: ContentFetchRequest,
    source_entry: dict,
    fixture_map: list[dict],
) -> dict | None:
    if not fixture_map:
        return None
    canonical_url = request.canonical_url or request.url
    domain = _domain_for_entry(source_entry)
    for item in fixture_map:
        if item.get("source_id") and item.get("source_id") == request.source_id:
            return item
        if item.get("canonical_url") and item.get("canonical_url") == canonical_url:
            return item
        if item.get("url") and item.get("url") == request.url:
            return item
        if item.get("domain") and _domain_matches(domain, [item.get("domain")]):
            return item
    return None


def _now_fixed_or_utc(live: bool) -> str:
    if not live:
        return _OFFLINE_FIXED_TIMESTAMP
    return datetime.now(timezone.utc).isoformat()


def _hash_text(text: str | None) -> str | None:
    if not text:
        return None
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _resolve_project_path(value: str | Path) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = _PROJECT_ROOT / path
    return path


def _url_scheme(url: str) -> str:
    if not url:
        return ""
    return urlsplit(url).scheme.lower()


def _is_search_endpoint(entry: dict, policy: ContentFetchPolicy) -> bool:
    publisher = entry.get("publisher")
    return publisher in policy.search_endpoint_publishers


def _domain_for_entry(entry: dict) -> str:
    url = entry.get("canonical_url") or entry.get("url") or ""
    if not url:
        return ""
    netloc = urlsplit(url).netloc.lower()
    if netloc.startswith("www."):
        netloc = netloc[4:]
    return netloc


def _domain_matches(domain: str, patterns: list[str]) -> bool:
    if not patterns:
        return False
    normalized_domain = (domain or "").lower()
    if normalized_domain.startswith("www."):
        normalized_domain = normalized_domain[4:]
    for pattern in patterns:
        value = str(pattern or "").strip().lower()
        if not value:
            continue
        if value.startswith("www."):
            value = value[4:]
        if normalized_domain == value or normalized_domain.endswith("." + value):
            return True
    return False


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


def _is_validation_reserved_entry(
    entry: dict,
    collection_mode: str,
    role_policy: dict | None = None,
) -> bool:
    if collection_mode != "masked_validation":
        return False
    flags = set(entry.get("routing_flags") or [])
    has_reserved_marker = (
        entry.get("source_role") == "validation_reserved"
        or entry.get("final_screening_decision") == "reserved_for_validation"
        or "validation_reserved" in flags
        or "blocked_from_collection" in flags
    )
    if has_reserved_marker:
        return True
    if role_policy is None:
        return False

    reserved_ids = set(role_policy.get("validation_reserved_source_ids") or [])
    if entry.get("source_id") in reserved_ids:
        return True

    if not role_policy.get("domain_masking_enabled", False):
        return False
    reserved_domains = list(role_policy.get("validation_reserved_domains") or [])
    return _domain_matches_reserved(_domain_for_entry(entry), reserved_domains)


def _context_only_source_ids(role_policy: dict | None) -> set[str]:
    if not role_policy:
        return set()
    return {str(source_id) for source_id in role_policy.get("context_only_source_ids") or []}


def _routing_flags(obj: dict) -> list[str]:
    flags = list(obj.get("routing_flags") or [])
    metadata = obj.get("metadata") if isinstance(obj.get("metadata"), dict) else {}
    for flag in metadata.get("routing_flags") or []:
        if flag not in flags:
            flags.append(flag)
    return flags


def _is_search_derived_entry(entry: dict) -> bool:
    return entry.get("discovery_method") in _SEARCH_DERIVED_DISCOVERY_METHODS


def _source_provenance(source_entry: dict) -> dict:
    return {
        "discovery_method": source_entry.get("discovery_method"),
        "search_provider": source_entry.get("search_provider"),
        "query_id": source_entry.get("query_id"),
        "query_used": source_entry.get("query_used"),
        "planned_query_id": source_entry.get("planned_query_id"),
        "provider_channel": source_entry.get("provider_channel"),
        "role_hint": source_entry.get("role_hint"),
        "retrieved_at": source_entry.get("retrieved_at"),
        "source_role_final": source_entry.get("source_role_final"),
        "credibility_score": source_entry.get("credibility_score"),
        "credibility_level": source_entry.get("credibility_level"),
        "source_credibility_risk_flags": list(
            source_entry.get("risk_flags")
            or source_entry.get("credibility_flags")
            or []
        ),
        "search_rank": source_entry.get("search_rank"),
        "search_result_id": source_entry.get("search_result_id"),
        "result_source": source_entry.get("result_source"),
        "query_type": source_entry.get("query_type"),
        "source_disease_relevance_status": source_entry.get(
            "source_disease_relevance_status"
        ),
        "source_disease_relevance_score": source_entry.get(
            "source_disease_relevance_score"
        ),
        "source_target_disease_terms_found": list(
            source_entry.get("source_target_disease_terms_found") or []
        ),
        "source_incompatible_disease_terms_found": list(
            source_entry.get("source_incompatible_disease_terms_found") or []
        ),
        "source_disease_relevance_reason": source_entry.get(
            "source_disease_relevance_reason"
        ),
        "source_disease_relevance_data_signal_count": source_entry.get(
            "source_disease_relevance_data_signal_count"
        ),
    }


def _is_context_only_entry(entry: dict, role_policy: dict | None = None) -> bool:
    source_id = entry.get("source_id")
    if source_id in _context_only_source_ids(role_policy):
        return True
    flags = set(_routing_flags(entry))
    if "context_only" in flags or "blocked_from_structured_extraction" in flags:
        return True
    return (
        entry.get("source_role") in {"context_source", "context_only"}
        and entry.get("final_screening_decision") == "include_for_context_fetch"
    )


def _source_metadata(source_entry: dict) -> dict:
    return {
        "source_registry_status": source_entry.get("status"),
        "expected_fields": list(source_entry.get("expected_fields") or []),
        "matched_terms": list(source_entry.get("matched_terms") or []),
        "source_purpose": source_entry.get("source_purpose"),
        "notes": source_entry.get("notes"),
        "routing_flags": list(source_entry.get("routing_flags") or []),
        "requires_human_review": source_entry.get("requires_human_review"),
        "human_review_recommended": source_entry.get("human_review_recommended"),
        **_source_provenance(source_entry),
    }


def _is_context_only_document(doc: dict, role_policy: dict | None = None) -> bool:
    source_id = doc.get("source_id")
    if source_id in _context_only_source_ids(role_policy):
        return True
    flags = set(_routing_flags(doc))
    if "context_only" in flags or "blocked_from_structured_extraction" in flags:
        return True
    return (
        doc.get("source_role") in {"context_source", "context_only"}
        and doc.get("fetch_purpose") == "context_grounding"
    )


# ---------------------------------------------------------------------------
# Fetch-request construction
# ---------------------------------------------------------------------------


def _classify_skip_reason(
    entry: dict,
    policy: ContentFetchPolicy,
    allowlist: set[str] | None = None,
    collection_mode: str = "standard",
    role_policy: dict | None = None,
    fetch_config: dict | None = None,
) -> str | None:
    """Return a skip reason or None if the entry should be fetched.

    Order is intentional so the summary attributes each skipped source to the
    most informative reason: a PubMed search endpoint shows up as
    `search_endpoint` rather than the more generic `deferred`, and a seed://
    placeholder shows up as `blocked_scheme`.
    """

    # Allowlist takes priority: if the user opted into a small source list,
    # any other source_id should be skipped as `not_in_source_id_allowlist`
    # rather than falsely attributed to a downstream reason.
    if allowlist is not None and entry.get("source_id") not in allowlist:
        return "not_in_source_id_allowlist"
    if _is_validation_reserved_entry(entry, collection_mode, role_policy):
        return "validation_reserved"
    if entry.get("source_disease_relevance_status") == UNRELATED_DISEASE:
        return "disease_mismatch_source"
    url = entry.get("canonical_url") or entry.get("url") or ""
    scheme = _url_scheme(url)
    if _is_search_derived_entry(entry):
        cfg = fetch_config or {}
        if not bool(cfg.get("fetch_search_derived_sources", False)):
            return "search_derived_fetch_disabled"
        final_role = str(entry.get("source_role_final") or "").strip()
        if final_role in _SEARCH_DERIVED_BLOCKED_FINAL_ROLES:
            if final_role == "needs_human_review":
                return "needs_review_not_allowed"
            return f"final_role_{final_role}"
        allowed_roles = set(cfg.get("allowed_final_roles") or [])
        if final_role and allowed_roles and final_role not in allowed_roles:
            return "final_role_not_allowed"
        if not entry.get("source_type"):
            return "missing_source_type"
        if scheme not in {"http", "https"}:
            return "unsupported_url_scheme"
        score = entry.get("credibility_score")
        threshold = float(cfg.get("min_credibility_score", 0.55))
        if score is None:
            return "missing_credibility_score"
        try:
            score_value = float(score)
        except (TypeError, ValueError):
            return "invalid_credibility_score"
        if score_value < threshold:
            return "credibility_score_below_threshold"
        level = str(entry.get("credibility_level") or "").strip().lower()
        allow_needs_review = bool(cfg.get("allow_needs_review", False))
        if (
            level not in {"high", "medium"}
            or entry.get("human_review_recommended")
            or entry.get("requires_human_review")
        ) and not allow_needs_review:
            return "needs_review_not_allowed"
        if not entry.get("ready_for_content_fetch"):
            return "not_ready_for_content_fetch"
        final_decision = entry.get("final_screening_decision")
        if final_decision not in policy.fetchable_final_decisions:
            return "final_screening_decision_not_fetchable"
        domain = _domain_for_entry(entry)
        if _domain_matches(domain, list(cfg.get("domain_blocklist") or [])):
            return "domain_blocklisted"
        allowlist_domains = list(cfg.get("domain_allowlist") or [])
        if allowlist_domains and not _domain_matches(domain, allowlist_domains):
            return "domain_not_allowlisted"
        return None
    if entry.get("requires_human_review"):
        return "human_review"
    if _is_search_endpoint(entry, policy):
        return "search_endpoint"
    if scheme in {s.lower() for s in policy.blocked_url_schemes}:
        return "blocked_scheme"
    if scheme not in {s.lower() for s in policy.allowed_url_schemes}:
        return "non_allowed_scheme"
    final_decision = entry.get("final_screening_decision")
    if final_decision in policy.deferred_final_decisions:
        return "deferred"
    if final_decision not in policy.fetchable_final_decisions:
        return "not_fetchable"
    return None


def _build_fetch_requests(
    state: DataCollectionState,
    policy: ContentFetchPolicy,
    live: bool,
    fetch_config: dict,
    allowlist: set[str] | None = None,
    collection_mode: str = "standard",
    role_policy: dict | None = None,
) -> tuple[list[ContentFetchRequest], dict[str, int], list[dict]]:
    registry = list(state.get("source_registry") or [])
    skip_counts: Counter = Counter()
    accepted: list[ContentFetchRequest] = []
    selection_manifest: list[dict] = []
    selected_search_derived_count = 0

    for entry in registry:
        is_search_derived = _is_search_derived_entry(entry)
        skip_reason = _classify_skip_reason(
            entry,
            policy,
            allowlist,
            collection_mode,
            role_policy,
            fetch_config,
        )
        if skip_reason is not None:
            skip_counts[skip_reason] += 1
            selection_manifest.append(
                {
                    "source_id": entry.get("source_id"),
                    "canonical_url": entry.get("canonical_url") or entry.get("url"),
                    "domain": _domain_for_entry(entry),
                    "discovery_method": entry.get("discovery_method"),
                    "source_role_final": entry.get("source_role_final"),
                    "credibility_score": entry.get("credibility_score"),
                    "credibility_level": entry.get("credibility_level"),
                    "selected_for_fetch": False,
                    "skip_reason": skip_reason,
                }
            )
            continue
        if is_search_derived:
            max_search = int(fetch_config.get("max_search_derived_sources") or 2)
            if selected_search_derived_count >= max_search:
                skip_reason = "max_search_derived_sources_reached"
                skip_counts[skip_reason] += 1
                selection_manifest.append(
                    {
                        "source_id": entry.get("source_id"),
                        "canonical_url": entry.get("canonical_url") or entry.get("url"),
                        "domain": _domain_for_entry(entry),
                        "discovery_method": entry.get("discovery_method"),
                        "source_role_final": entry.get("source_role_final"),
                        "credibility_score": entry.get("credibility_score"),
                        "credibility_level": entry.get("credibility_level"),
                        "selected_for_fetch": False,
                        "skip_reason": skip_reason,
                    }
                )
                continue
        max_total = int(fetch_config.get("max_total_sources") or 10)
        if len(accepted) >= max_total:
            skip_reason = "max_total_sources_reached"
            skip_counts[skip_reason] += 1
            selection_manifest.append(
                {
                    "source_id": entry.get("source_id"),
                    "canonical_url": entry.get("canonical_url") or entry.get("url"),
                    "domain": _domain_for_entry(entry),
                    "discovery_method": entry.get("discovery_method"),
                    "source_role_final": entry.get("source_role_final"),
                    "credibility_score": entry.get("credibility_score"),
                    "credibility_level": entry.get("credibility_level"),
                    "selected_for_fetch": False,
                    "skip_reason": skip_reason,
                }
            )
            continue

        final_decision = entry.get("final_screening_decision") or ""
        fetch_purpose = policy.fetch_purpose_by_decision.get(final_decision, "unknown")
        if _is_context_only_entry(entry, role_policy):
            fetch_purpose = "context_grounding"
        url = entry.get("canonical_url") or entry.get("url") or ""
        accepted.append(
            ContentFetchRequest(
                source_id=entry.get("source_id", ""),
                url=url,
                canonical_url=entry.get("canonical_url") or url,
                publisher=entry.get("publisher"),
                source_type=entry.get("source_type"),
                source_role=entry.get("source_role"),
                **_source_provenance(entry),
                final_screening_decision=final_decision,
                fetch_purpose=fetch_purpose,
                priority=entry.get("priority"),
                live_fetch_enabled=live,
            )
        )
        if is_search_derived:
            selected_search_derived_count += 1
        selection_manifest.append(
            {
                "source_id": entry.get("source_id"),
                "canonical_url": entry.get("canonical_url") or entry.get("url"),
                "domain": _domain_for_entry(entry),
                "discovery_method": entry.get("discovery_method"),
                "source_role_final": entry.get("source_role_final"),
                "credibility_score": entry.get("credibility_score"),
                "credibility_level": entry.get("credibility_level"),
                "selected_for_fetch": True,
                "skip_reason": None,
            }
        )

    accepted.sort(key=lambda r: (r.priority is None, r.priority or 0, r.source_id))
    return accepted, dict(skip_counts), selection_manifest


# ---------------------------------------------------------------------------
# Offline stub document
# ---------------------------------------------------------------------------


def _stub_clean_text(source_entry: dict) -> str:
    """Build a deterministic metadata summary for offline stub documents."""

    title = source_entry.get("title") or ""
    publisher = source_entry.get("publisher") or ""
    source_type = source_entry.get("source_type") or ""
    source_role = source_entry.get("source_role") or ""
    source_purpose = source_entry.get("source_purpose") or ""
    expected_fields = source_entry.get("expected_fields") or []
    matched_terms = source_entry.get("matched_terms") or []
    notes = source_entry.get("notes") or ""

    lines = [
        "Offline metadata stub document",
        f"Title: {title}",
        f"Publisher: {publisher}",
        f"Source type: {source_type}",
        f"Source role: {source_role}",
        f"Source purpose: {source_purpose}",
        f"Expected fields: {', '.join(expected_fields)}",
        f"Matched terms: {', '.join(matched_terms)}",
        f"Notes: {notes}",
    ]
    return "\n".join(lines).strip()


def _make_fixture_document(
    request: ContentFetchRequest,
    source_entry: dict,
    fixture: FixtureDocument,
) -> Document:
    """Build a Document from a synthetic local fixture (offline, opt-in only)."""

    clean_text = fixture.clean_text
    return Document(
        source_id=request.source_id,
        document_type=fixture.document_type,
        clean_text=clean_text,
        tables=list(fixture.tables or []),
        metadata={
            "fixture_mode_enabled": True,
            "synthetic_fixture": True,
            "not_real_public_health_data": True,
            **_source_metadata(source_entry),
            "fixture_id": fixture.fixture_id,
            "fixture_notes": fixture.notes,
        },
        parse_status="fixture_loaded",
        quality_status=None,
        quality_issues=[],
        url=request.url,
        canonical_url=request.canonical_url,
        title=fixture.title,
        publisher=source_entry.get("publisher"),
        source_type=source_entry.get("source_type"),
        source_role=source_entry.get("source_role"),
        **_source_provenance(source_entry),
        final_screening_decision=request.final_screening_decision,
        fetch_purpose=request.fetch_purpose,
        fetch_status="fixture_loaded",
        fetch_error=None,
        http_status_code=None,
        content_type=None,
        fetched_at=_OFFLINE_FIXED_TIMESTAMP,
        parser_used="fixture_document_loader",
        text_char_count=len(clean_text or ""),
        table_count=len(fixture.tables or []),
        content_hash=_hash_text(clean_text),
        is_live_fetched=False,
        is_offline_stub=False,
        is_fixture_document=True,
        fixture_id=fixture.fixture_id,
        fixture_notes=fixture.notes,
    )


def _make_offline_stub_document(
    request: ContentFetchRequest,
    source_entry: dict,
) -> Document:
    clean_text = _stub_clean_text(source_entry)
    return Document(
        source_id=request.source_id,
        document_type="offline_metadata_stub",
        clean_text=clean_text,
        tables=[],
        metadata={
            "live_fetch_enabled": False,
            "offline_stub_reason": "Live fetching disabled; created metadata stub.",
            **_source_metadata(source_entry),
        },
        parse_status="offline_stub",
        quality_status=None,
        quality_issues=[],
        url=request.url,
        canonical_url=request.canonical_url,
        title=source_entry.get("title"),
        publisher=source_entry.get("publisher"),
        source_type=source_entry.get("source_type"),
        source_role=source_entry.get("source_role"),
        **_source_provenance(source_entry),
        final_screening_decision=request.final_screening_decision,
        fetch_purpose=request.fetch_purpose,
        fetch_status="offline_stub",
        fetch_error=None,
        http_status_code=None,
        content_type=None,
        fetched_at=_OFFLINE_FIXED_TIMESTAMP,
        parser_used="offline_metadata_stub",
        text_char_count=len(clean_text or ""),
        table_count=0,
        content_hash=_hash_text(clean_text),
        is_live_fetched=False,
        is_offline_stub=True,
    )


# ---------------------------------------------------------------------------
# Live fetch (opt-in)
# ---------------------------------------------------------------------------


def _looks_like_pdf(url: str, content_type: str | None) -> bool:
    if content_type and "pdf" in content_type.lower():
        return True
    return (url or "").lower().split("?")[0].endswith(".pdf")


class _VisibleHTMLTextParser(HTMLParser):
    """Small stdlib parser for visible text, titles, meta dates, and tables."""

    _SKIP_TAGS = {"script", "style", "nav", "footer", "noscript"}

    def __init__(self, *, parse_tables: bool = True) -> None:
        super().__init__(convert_charrefs=True)
        self.parse_tables = parse_tables
        self._skip_depth = 0
        self._tag_stack: list[str] = []
        self._current_text: list[str] = []
        self.title_parts: list[str] = []
        self.headings: list[str] = []
        self.text_parts: list[str] = []
        self.meta_description: str | None = None
        self.published_date: str | None = None
        self.tables: list[dict] = []
        self._in_table = False
        self._table_rows: list[list[str]] = []
        self._current_row: list[str] | None = None
        self._current_cell: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        self._tag_stack.append(tag)
        attr_map = {key.lower(): value for key, value in attrs if key}
        if tag in self._SKIP_TAGS:
            self._skip_depth += 1
            return
        if tag == "meta":
            name = (attr_map.get("name") or attr_map.get("property") or "").lower()
            content = (attr_map.get("content") or "").strip()
            if not content:
                return
            if name in {"description", "og:description"} and not self.meta_description:
                self.meta_description = content
            if name in {
                "date",
                "dc.date",
                "article:published_time",
                "pubdate",
                "publishdate",
                "published_date",
            } and not self.published_date:
                self.published_date = content[:10]
        if not self.parse_tables:
            return
        if tag == "table":
            self._in_table = True
            self._table_rows = []
        elif self._in_table and tag == "tr":
            self._current_row = []
        elif self._in_table and tag in {"td", "th"}:
            self._current_cell = []

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in self._SKIP_TAGS and self._skip_depth > 0:
            self._skip_depth -= 1
        if not self._tag_stack:
            return
        if self.parse_tables and self._in_table and tag in {"td", "th"}:
            if self._current_cell is not None and self._current_row is not None:
                cell = _normalize_whitespace(" ".join(self._current_cell))
                self._current_row.append(cell)
            self._current_cell = None
        elif self.parse_tables and self._in_table and tag == "tr":
            if self._current_row:
                self._table_rows.append(self._current_row)
            self._current_row = None
        elif self.parse_tables and self._in_table and tag == "table":
            if self._table_rows:
                self.tables.append(
                    {"table_index": len(self.tables), "rows": list(self._table_rows)}
                )
            self._table_rows = []
            self._in_table = False
        while self._tag_stack:
            popped = self._tag_stack.pop()
            if popped == tag:
                break

    def handle_data(self, data: str) -> None:
        if self._skip_depth > 0:
            return
        text = _normalize_whitespace(data)
        if not text:
            return
        current_tag = self._tag_stack[-1] if self._tag_stack else ""
        if current_tag == "title":
            self.title_parts.append(text)
        if current_tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self.headings.append(text)
        if self.parse_tables and self._in_table and self._current_cell is not None:
            self._current_cell.append(text)
        self.text_parts.append(text)


def _decode_body(body: bytes) -> str:
    return body.decode("utf-8", errors="replace")


def _parse_pdf_content(body: bytes, *, parse_pdf_text: bool) -> dict:
    if not parse_pdf_text:
        return {
            "document_type": "pdf",
            "clean_text": None,
            "tables": [],
            "parse_status": "parse_deferred",
            "parser_used": "pdf_parse_deferred",
            "title": None,
            "published_date": None,
            "content_type": "application/pdf",
            "parse_error": "pdf_text_parsing_disabled",
        }
    try:
        from io import BytesIO
        from pypdf import PdfReader  # type: ignore
    except Exception as exc:  # noqa: BLE001 - optional dependency.
        return {
            "document_type": "pdf",
            "clean_text": None,
            "tables": [],
            "parse_status": "parse_deferred",
            "parser_used": "pdf_parse_deferred",
            "title": None,
            "published_date": None,
            "content_type": "application/pdf",
            "parse_error": f"pypdf_unavailable:{type(exc).__name__}",
        }
    try:
        reader = PdfReader(BytesIO(body))
        pages = []
        for page in reader.pages:
            pages.append(page.extract_text() or "")
        clean_text = "\n".join(part.strip() for part in pages if part.strip()) or None
    except Exception as exc:  # noqa: BLE001 - malformed PDFs should not crash.
        return {
            "document_type": "pdf",
            "clean_text": None,
            "tables": [],
            "parse_status": "parse_failed",
            "parser_used": "pdf_parse_failed",
            "title": None,
            "published_date": None,
            "content_type": "application/pdf",
            "parse_error": f"pypdf_parse_failed:{type(exc).__name__}",
        }
    return {
        "document_type": "pdf",
        "clean_text": clean_text,
        "tables": [],
        "parse_status": "parsed_pdf" if clean_text else "parse_failed",
        "parser_used": "pdf_pypdf_parser" if clean_text else "pdf_parse_failed",
        "title": None,
        "published_date": None,
        "content_type": "application/pdf",
        "parse_error": None if clean_text else "pdf_no_extractable_text",
    }


def _parse_document_content(
    body: bytes,
    *,
    url: str,
    content_type: str | None,
    parse_pdf_text: bool,
    parse_tables: bool,
) -> dict:
    """Parse fetched bytes into auditable clean text and parse metadata."""

    normalized_content_type = content_type or ""
    if _looks_like_pdf(url, normalized_content_type):
        result = _parse_pdf_content(body, parse_pdf_text=parse_pdf_text)
    elif "html" in normalized_content_type.lower() or body.lstrip().startswith(b"<"):
        parser = _VisibleHTMLTextParser(parse_tables=parse_tables)
        parser.feed(_decode_body(body))
        title = _normalize_whitespace(" ".join(parser.title_parts)) or None
        clean_parts = []
        if parser.meta_description:
            clean_parts.append(parser.meta_description)
        clean_parts.extend(parser.headings)
        clean_parts.extend(parser.text_parts)
        clean_text = "\n".join(
            line for line in (_normalize_whitespace(part) for part in clean_parts) if line
        )
        result = {
            "document_type": "html",
            "clean_text": clean_text or None,
            "tables": parser.tables if parse_tables else [],
            "parse_status": "parsed_html",
            "parser_used": "html_stdlib_parser",
            "title": title,
            "published_date": parser.published_date,
            "content_type": normalized_content_type or "text/html",
            "parse_error": None,
        }
    else:
        clean_text = _decode_body(body)
        lowered = normalized_content_type.lower()
        parser_used = "text_parser"
        if "json" in lowered:
            parser_used = "json_text_parser"
        elif "csv" in lowered:
            parser_used = "csv_text_parser"
        result = {
            "document_type": "text",
            "clean_text": clean_text,
            "tables": [],
            "parse_status": "parsed_text",
            "parser_used": parser_used,
            "title": None,
            "published_date": None,
            "content_type": normalized_content_type or "text/plain",
            "parse_error": None,
        }
    clean_text = result.get("clean_text") or ""
    tables = result.get("tables") or []
    result["text_char_count"] = len(clean_text)
    result["table_count"] = len(tables)
    return result


def _fetch_live_document(
    request: ContentFetchRequest,
    source_entry: dict,
    policy: ContentFetchPolicy,
) -> Document:
    """Perform a live HTTP fetch. Only invoked when live mode is on."""

    import requests  # local import; offline path never touches the network

    request_cfg = policy.request or {}
    timeout = float(
        os.environ.get("HDC_FETCH_TIMEOUT_SECONDS")
        or request_cfg.get("timeout_seconds")
        or 15
    )
    max_bytes = int(request_cfg.get("max_response_bytes") or 5_000_000)
    user_agent = request_cfg.get(
        "user_agent",
        "HantavirusDataCollectionWorkflow/0.1 academic research prototype",
    )
    headers = {"User-Agent": user_agent}
    fetched_at = _now_fixed_or_utc(live=True)

    document_kwargs: dict = {
        "source_id": request.source_id,
        "url": request.url,
        "canonical_url": request.canonical_url,
        "title": source_entry.get("title"),
        "publisher": source_entry.get("publisher"),
        "source_type": source_entry.get("source_type"),
        "source_role": source_entry.get("source_role"),
        "final_screening_decision": request.final_screening_decision,
        "fetch_purpose": request.fetch_purpose,
        "is_live_fetched": True,
        "is_offline_stub": False,
        "fetched_at": fetched_at,
        "metadata": {
            "live_fetch_enabled": True,
            **_source_metadata(source_entry),
        },
    }

    try:
        response = requests.get(
            request.url,
            timeout=timeout,
            headers=headers,
            stream=True,
        )
        http_status = response.status_code
        content_type = response.headers.get("Content-Type")
        body = response.content[:max_bytes]
    except Exception as exc:  # pragma: no cover — manual live-fetch only
        return Document(
            **document_kwargs,
            document_type=None,
            clean_text=None,
            tables=[],
            parse_status="fetch_failed",
            fetch_status="fetch_failed",
            fetch_error=str(exc),
            http_status_code=None,
            content_type=None,
            content_hash=None,
        )

    if _looks_like_pdf(request.url, content_type):
        return Document(
            **document_kwargs,
            document_type="pdf",
            clean_text=None,
            tables=[],
            parse_status="pdf_parsing_deferred",
            fetch_status="fetched_pdf_parse_deferred",
            fetch_error=None,
            http_status_code=http_status,
            content_type=content_type,
            content_hash=None,
        )

    is_html = bool(content_type and "html" in content_type.lower())
    if is_html or body.lstrip().startswith(b"<"):
        clean_text, title, tables = _html_to_clean_text(body)
        if title:
            document_kwargs["title"] = title
        return Document(
            **document_kwargs,
            document_type="html",
            clean_text=clean_text,
            tables=tables,
            parse_status="parsed_html",
            fetch_status="fetched",
            fetch_error=None,
            http_status_code=http_status,
            content_type=content_type,
            content_hash=_hash_text(clean_text),
        )

    try:
        clean_text = body.decode("utf-8", errors="replace")
    except Exception as exc:  # pragma: no cover
        clean_text = None
        return Document(
            **document_kwargs,
            document_type=None,
            clean_text=None,
            tables=[],
            parse_status="fetch_failed",
            fetch_status="fetch_failed",
            fetch_error=f"decode_error: {exc}",
            http_status_code=http_status,
            content_type=content_type,
            content_hash=None,
        )

    return Document(
        **document_kwargs,
        document_type="text",
        clean_text=clean_text,
        tables=[],
        parse_status="parsed_text",
        fetch_status="fetched",
        fetch_error=None,
        http_status_code=http_status,
        content_type=content_type,
        content_hash=_hash_text(clean_text),
    )


def _base_document_kwargs(
    request: ContentFetchRequest,
    source_entry: dict,
    *,
    live: bool,
    fetched_at: str,
) -> dict:
    return {
        "source_id": request.source_id,
        "url": request.url,
        "canonical_url": request.canonical_url,
        "title": source_entry.get("title"),
        "published_date": source_entry.get("published_date"),
        "publisher": source_entry.get("publisher"),
        "source_type": source_entry.get("source_type"),
        "source_role": source_entry.get("source_role"),
        **_source_provenance(source_entry),
        "final_screening_decision": request.final_screening_decision,
        "fetch_purpose": request.fetch_purpose,
        "is_live_fetched": live,
        "is_offline_stub": False,
        "fetched_at": fetched_at,
        "metadata": {
            "live_fetch_enabled": live,
            **_source_metadata(source_entry),
        },
    }


def _make_parsed_document(
    request: ContentFetchRequest,
    source_entry: dict,
    *,
    body: bytes,
    content_type: str | None,
    http_status_code: int | None,
    fetch_status: str,
    fetched_at: str,
    live: bool,
    fetch_config: dict,
    extra_metadata: dict | None = None,
) -> Document:
    parsed = _parse_document_content(
        body,
        url=request.url,
        content_type=content_type,
        parse_pdf_text=bool(fetch_config.get("parse_pdf_text", True)),
        parse_tables=bool(fetch_config.get("parse_tables", True)),
    )
    clean_text = parsed.get("clean_text")
    metadata = {
        **_source_metadata(source_entry),
        "parse_error": parsed.get("parse_error"),
        "raw_text_stored": bool(fetch_config.get("store_raw_text", False)),
    }
    if extra_metadata:
        metadata.update(extra_metadata)
    if bool(fetch_config.get("store_raw_text", False)) and clean_text:
        metadata["raw_text"] = clean_text
    base_kwargs = _base_document_kwargs(
        request,
        source_entry,
        live=live,
        fetched_at=fetched_at,
    )
    base_kwargs["metadata"] = metadata
    base_kwargs["title"] = parsed.get("title") or source_entry.get("title")
    base_kwargs["published_date"] = (
        parsed.get("published_date") or source_entry.get("published_date")
    )
    return Document(
        **base_kwargs,
        document_type=parsed.get("document_type"),
        clean_text=clean_text,
        tables=list(parsed.get("tables") or []),
        parse_status=parsed.get("parse_status") or "parse_failed",
        quality_status=None,
        quality_issues=[],
        fetch_status=fetch_status,
        fetch_error=parsed.get("parse_error"),
        http_status_code=http_status_code,
        content_type=parsed.get("content_type") or content_type,
        parser_used=parsed.get("parser_used"),
        text_char_count=parsed.get("text_char_count"),
        table_count=parsed.get("table_count"),
        content_hash=_hash_text(clean_text),
        is_fixture_document=bool(
            extra_metadata and extra_metadata.get("local_content_fixture")
        ),
        fixture_id=(extra_metadata or {}).get("fixture_id"),
        fixture_notes=(extra_metadata or {}).get("fixture_notes"),
    )


def _fetch_fixture_content_document(
    request: ContentFetchRequest,
    source_entry: dict,
    fixture_entry: dict,
    fetch_config: dict,
) -> Document:
    fixture_path = Path(fixture_entry["fixture_path"])
    body = fixture_path.read_bytes()
    max_bytes = int(fetch_config.get("max_bytes") or len(body))
    return _make_parsed_document(
        request,
        source_entry,
        body=body[:max_bytes],
        content_type=fixture_entry.get("content_type") or "text/html; charset=utf-8",
        http_status_code=int(fixture_entry.get("http_status_code") or 200),
        fetch_status="fixture_content_loaded",
        fetched_at=_OFFLINE_FIXED_TIMESTAMP,
        live=False,
        fetch_config=fetch_config,
        extra_metadata={
            "local_content_fixture": True,
            "synthetic_fixture": True,
            "not_real_public_health_data": True,
            "fixture_id": fixture_entry.get("fixture_id") or fixture_path.stem,
            "fixture_path": str(fixture_path),
            "fixture_notes": fixture_entry.get("notes"),
        },
    )


def _fetch_live_document(
    request: ContentFetchRequest,
    source_entry: dict,
    policy: ContentFetchPolicy,
    fetch_config: dict,
) -> Document:
    """Perform a live HTTP fetch and parse through the generalized parser."""

    import requests  # local import; offline path never touches the network

    request_cfg = policy.request or {}
    timeout = float(
        os.environ.get("HDC_FETCH_TIMEOUT_SECONDS")
        or request_cfg.get("timeout_seconds")
        or 15
    )
    max_bytes = int(fetch_config.get("max_bytes") or 5_000_000)
    user_agent = fetch_config.get("user_agent") or request_cfg.get(
        "user_agent", "data-collection-workflow/0.1"
    )
    headers = {"User-Agent": user_agent}
    fetched_at = _now_fixed_or_utc(live=True)

    try:
        response = requests.get(
            request.url,
            timeout=timeout,
            headers=headers,
            stream=True,
        )
        http_status = response.status_code
        content_type = response.headers.get("Content-Type")
        chunks: list[bytes] = []
        total = 0
        for chunk in response.iter_content(chunk_size=65536):
            if not chunk:
                continue
            remaining = max_bytes - total
            if remaining <= 0:
                break
            chunks.append(chunk[:remaining])
            total += len(chunks[-1])
        body = b"".join(chunks)
    except Exception as exc:  # pragma: no cover - manual live-fetch only
        return Document(
            **_base_document_kwargs(
                request,
                source_entry,
                live=True,
                fetched_at=fetched_at,
            ),
            document_type=None,
            clean_text=None,
            tables=[],
            parse_status="fetch_failed",
            fetch_status="fetch_failed",
            fetch_error=str(exc),
            http_status_code=None,
            content_type=None,
            parser_used=None,
            text_char_count=0,
            table_count=0,
            content_hash=None,
        )

    fetch_status = "fetched" if http_status < 400 else "fetch_failed"
    return _make_parsed_document(
        request,
        source_entry,
        body=body,
        content_type=content_type,
        http_status_code=http_status,
        fetch_status=fetch_status,
        fetched_at=fetched_at,
        live=True,
        fetch_config=fetch_config,
    )


# ---------------------------------------------------------------------------
# Nodes
# ---------------------------------------------------------------------------


def content_fetch_and_parse(state: DataCollectionState) -> dict:
    """Build fetch requests and produce Document objects.

    Offline by default; live HTTP only when HDC_ENABLE_LIVE_FETCH=true.
    """

    policy = ContentFetchPolicy(**load_content_fetch_policy())
    role_policy = load_source_role_policy()
    collection_mode = get_collection_mode(role_policy)
    live = _live_fetch_enabled()
    fetch_config = _fetch_config_from_env(policy)
    fixture_enabled = _fixture_documents_enabled()
    fixture_map: dict[str, FixtureDocument] = (
        _load_fixture_document_map() if fixture_enabled else {}
    )
    content_fixture_map = _load_content_fixture_map(
        fetch_config.get("content_fixture_map_path")
    )
    allowlist = _parse_source_id_allowlist()

    fetch_requests, skip_counts, selection_manifest = _build_fetch_requests(
        state, policy, live, fetch_config, allowlist, collection_mode, role_policy
    )

    registry = list(state.get("source_registry") or [])
    registry_by_id = {e.get("source_id"): e for e in registry}

    documents: list[Document] = []
    fixture_loaded_source_ids: list[str] = []
    for request in fetch_requests:
        source_entry = registry_by_id.get(request.source_id) or {}
        fixture = fixture_map.get(request.source_id) if fixture_enabled else None
        content_fixture = _fixture_for_request(
            request, source_entry, content_fixture_map
        )
        if fixture is not None:
            doc = _make_fixture_document(request, source_entry, fixture)
            fixture_loaded_source_ids.append(request.source_id)
        elif content_fixture is not None:
            doc = _fetch_fixture_content_document(
                request, source_entry, content_fixture, fetch_config
            )
            fixture_loaded_source_ids.append(request.source_id)
        elif live:
            doc = _fetch_live_document(request, source_entry, policy, fetch_config)
        else:
            doc = _make_offline_stub_document(request, source_entry)
        documents.append(doc)

    document_dicts = [d.model_dump() for d in documents]
    request_dicts = [r.model_dump() for r in fetch_requests]

    fetch_status_counts = dict(Counter(d.fetch_status or "unknown" for d in documents))
    document_type_counts = dict(Counter(d.document_type or "unknown" for d in documents))
    parser_status_counts = dict(Counter(d.parse_status or "unknown" for d in documents))
    parser_used_counts = dict(Counter(d.parser_used or "unknown" for d in documents))
    content_type_counts = dict(Counter(d.content_type or "unknown" for d in documents))
    total_table_count = sum(int(d.table_count or len(d.tables or [])) for d in documents)
    total_text_char_count = sum(int(d.text_char_count or len(d.clean_text or "")) for d in documents)
    fetch_purpose_counts = dict(
        Counter(r.fetch_purpose or "unknown" for r in fetch_requests)
    )
    search_derived_registry = [e for e in registry if _is_search_derived_entry(e)]
    selected_search_derived_ids = [
        r.source_id for r in fetch_requests
        if r.discovery_method in _SEARCH_DERIVED_DISCOVERY_METHODS
    ]
    skipped_search_derived_by_reason = {
        reason: count
        for reason, count in skip_counts.items()
        if reason
        in {
            "search_derived_fetch_disabled",
            "final_role_excluded",
            "final_role_search_endpoint",
            "needs_review_not_allowed",
            "final_role_not_allowed",
            "missing_source_type",
            "unsupported_url_scheme",
            "missing_credibility_score",
            "invalid_credibility_score",
            "credibility_score_below_threshold",
            "not_ready_for_content_fetch",
            "final_screening_decision_not_fetchable",
            "domain_blocklisted",
            "domain_not_allowlisted",
            "max_search_derived_sources_reached",
            "max_total_sources_reached",
        }
    }
    skipped_validation_reserved_ids = [
        e.get("source_id")
        for e in registry
        if _is_validation_reserved_entry(e, collection_mode, role_policy)
    ]
    context_only_source_ids = sorted(
        {
            e.get("source_id")
            for e in registry
            if e.get("source_id") and _is_context_only_entry(e, role_policy)
        }
    )
    context_only_fetched_source_ids = sorted(
        {
            d.source_id
            for d in documents
            if d.source_id and d.source_id in set(context_only_source_ids)
        }
    )

    summary = {
        "collection_mode": collection_mode,
        "live_fetch_enabled": live,
        "fixture_documents_enabled": fixture_enabled,
        "content_fixture_map_enabled": bool(content_fixture_map),
        "fixture_document_count": len(fixture_loaded_source_ids),
        "fixture_source_ids": list(fixture_loaded_source_ids),
        "source_id_allowlist_enabled": allowlist is not None,
        "source_id_allowlist": sorted(allowlist) if allowlist else [],
        "search_derived_fetch_enabled": bool(
            fetch_config.get("fetch_search_derived_sources")
        ),
        "search_derived_input_count": len(search_derived_registry),
        "selected_search_derived_fetch_count": len(selected_search_derived_ids),
        "selected_search_derived_source_ids": selected_search_derived_ids,
        "skipped_search_derived_fetch_disabled_count": skip_counts.get(
            "search_derived_fetch_disabled", 0
        ),
        "skipped_search_derived_fetch_limit_count": skip_counts.get(
            "max_search_derived_sources_reached", 0
        ),
        "skipped_search_derived_by_reason_counts": skipped_search_derived_by_reason,
        "max_search_derived_sources": fetch_config.get(
            "max_search_derived_sources"
        ),
        "max_total_sources": fetch_config.get("max_total_sources"),
        "min_credibility_score": fetch_config.get("min_credibility_score"),
        "allowed_final_roles": list(fetch_config.get("allowed_final_roles") or []),
        "allow_needs_review": bool(fetch_config.get("allow_needs_review")),
        "domain_allowlist": list(fetch_config.get("domain_allowlist") or []),
        "domain_blocklist": list(fetch_config.get("domain_blocklist") or []),
        "skipped_not_in_allowlist_count": skip_counts.get("not_in_source_id_allowlist", 0),
        "skipped_validation_reserved_count": skip_counts.get(
            "validation_reserved", 0
        ),
        "skipped_validation_reserved_source_ids": [
            sid for sid in skipped_validation_reserved_ids if sid
        ],
        "context_only_source_count": len(context_only_source_ids),
        "context_only_source_ids": context_only_source_ids,
        "context_only_fetched_source_ids": context_only_fetched_source_ids,
        "input_registry_count": len(registry),
        "fetch_request_count": len(fetch_requests),
        "document_count": len(documents),
        "fetch_status_counts": fetch_status_counts,
        "document_type_counts": document_type_counts,
        "parser_status_counts": parser_status_counts,
        "parser_used_counts": parser_used_counts,
        "content_type_counts": content_type_counts,
        "total_table_count": total_table_count,
        "total_text_char_count": total_text_char_count,
        "fetch_purpose_counts": fetch_purpose_counts,
        "skipped_deferred_count": skip_counts.get("deferred", 0)
        + skip_counts.get("not_fetchable", 0),
        "skipped_search_endpoint_count": skip_counts.get("search_endpoint", 0),
        "skipped_blocked_scheme_count": skip_counts.get("blocked_scheme", 0)
        + skip_counts.get("non_allowed_scheme", 0),
        "skipped_human_review_count": skip_counts.get("human_review", 0),
    }

    fixture_summary = {
        "fixture_documents_enabled": fixture_enabled,
        "available_fixture_count": len(fixture_map),
        "loaded_fixture_count": len(fixture_loaded_source_ids),
        "loaded_fixture_source_ids": list(fixture_loaded_source_ids),
        "synthetic_fixture_notice": (
            "Fixture documents are synthetic and not real public health data."
        ),
    }
    parse_summary = {
        "document_count": len(documents),
        "parser_status_counts": parser_status_counts,
        "parser_used_counts": parser_used_counts,
        "content_type_counts": content_type_counts,
        "parsed_document_count": sum(
            count
            for status, count in parser_status_counts.items()
            if str(status).startswith("parsed")
        ),
        "parse_deferred_count": parser_status_counts.get("parse_deferred", 0)
        + parser_status_counts.get("pdf_parsing_deferred", 0),
        "parse_failed_count": parser_status_counts.get("parse_failed", 0)
        + parser_status_counts.get("fetch_failed", 0),
        "total_text_char_count": total_text_char_count,
        "total_table_count": total_table_count,
        "documents": [
            {
                "source_id": d.source_id,
                "canonical_url": d.canonical_url,
                "discovery_method": d.discovery_method,
                "source_role_final": d.source_role_final,
                "credibility_score": d.credibility_score,
                "credibility_level": d.credibility_level,
                "fetch_status": d.fetch_status,
                "parse_status": d.parse_status,
                "parser_used": d.parser_used,
                "content_type": d.content_type,
                "title": d.title,
                "published_date": d.published_date,
                "text_char_count": d.text_char_count,
                "table_count": d.table_count,
            }
            for d in documents
        ],
    }
    fetch_manifest = []
    document_by_source_id = {d.source_id: d for d in documents}
    for item in selection_manifest:
        source_id = item.get("source_id")
        doc = document_by_source_id.get(source_id)
        enriched = dict(item)
        if doc is not None:
            enriched.update(
                {
                    "fetch_status": doc.fetch_status,
                    "parse_status": doc.parse_status,
                    "parser_used": doc.parser_used,
                    "content_type": doc.content_type,
                    "http_status_code": doc.http_status_code,
                    "text_char_count": doc.text_char_count,
                    "table_count": doc.table_count,
                }
            )
        fetch_manifest.append(enriched)

    trace = append_trace(
        state,
        node_name="content_fetch_and_parse",
        message=(
            f"Built {len(fetch_requests)} fetch requests, produced {len(documents)} "
            f"documents (live_fetch_enabled={live}, "
            f"fixture_documents_enabled={fixture_enabled}, "
            f"fixtures_loaded={len(fixture_loaded_source_ids)})."
        ),
        metadata=summary,
    )
    return {
        "content_fetch_requests": request_dicts,
        "documents": document_dicts,
        "content_fetch_summary": summary,
        "document_parse_summary": parse_summary,
        "fetch_manifest": fetch_manifest,
        "fixture_document_summary": fixture_summary,
        "collection_trace": trace,
    }


def document_quality_check(state: DataCollectionState) -> dict:
    """Annotate documents with quality status and surface issues."""

    policy = ContentFetchPolicy(**load_content_fetch_policy())
    documents = list(state.get("documents") or [])

    quality_cfg = policy.document_quality or {}
    min_usable = int(quality_cfg.get("min_clean_text_chars_for_usable", 300))
    min_partial = int(quality_cfg.get("min_clean_text_chars_for_partial", 80))

    updated: list[dict] = []
    quality_counter: Counter = Counter()
    disease_status_counter: Counter = Counter()
    usable = partial = offline_stub = parse_deferred = unusable = 0
    not_task_relevant = 0
    context = build_disease_relevance_context(state)

    for doc in documents:
        new_doc = dict(doc)
        issues: list[str] = list(doc.get("quality_issues") or [])
        fetch_status = doc.get("fetch_status")
        parse_status = doc.get("parse_status")
        is_offline_stub = bool(doc.get("is_offline_stub"))
        is_fixture = bool(doc.get("is_fixture_document"))
        clean_text = doc.get("clean_text") or ""
        text_len = len(clean_text)

        if fetch_status == "fetch_failed":
            quality_status = "unusable"
            if "fetch_failed" not in issues:
                issues.append("fetch_failed")
            unusable += 1
        elif is_offline_stub:
            quality_status = "offline_stub_pending_live_fetch"
            if "not_real_source_content" not in issues:
                issues.append("not_real_source_content")
            offline_stub += 1
        elif parse_status in {"pdf_parsing_deferred", "parse_deferred"}:
            quality_status = "parse_deferred"
            if "pdf_parsing_deferred" not in issues:
                issues.append("pdf_parsing_deferred")
            parse_deferred += 1
        elif text_len >= min_usable:
            quality_status = "usable"
            usable += 1
        elif text_len >= min_partial:
            quality_status = "partial"
            partial += 1
        else:
            quality_status = "unusable"
            if "insufficient_clean_text" not in issues:
                issues.append("insufficient_clean_text")
            unusable += 1

        if is_fixture and "synthetic_fixture_document" not in issues:
            issues.append("synthetic_fixture_document")

        disease_assessment = assess_document_disease_relevance(new_doc, context)
        new_doc.update(assessment_fields(disease_assessment, "document"))
        disease_status = disease_assessment.get("status") or "unknown"
        disease_status_counter[disease_status] += 1
        if (
            quality_status in {"usable", "partial"}
            and disease_status == UNRELATED_DISEASE
        ):
            if quality_status == "usable":
                usable = max(0, usable - 1)
            elif quality_status == "partial":
                partial = max(0, partial - 1)
            quality_status = "not_task_relevant"
            not_task_relevant += 1
            if "disease_mismatch_not_task_relevant" not in issues:
                issues.append("disease_mismatch_not_task_relevant")
            new_doc["not_extractable_for_task_disease"] = True
        else:
            new_doc["not_extractable_for_task_disease"] = False

        new_doc["quality_status"] = quality_status
        new_doc["quality_issues"] = issues
        new_doc["text_char_count"] = len(clean_text)
        new_doc["table_count"] = len(doc.get("tables") or [])
        updated.append(new_doc)
        quality_counter[quality_status] += 1

    summary = {
        "document_count": len(updated),
        "quality_status_counts": dict(quality_counter),
        "usable_count": usable,
        "partial_count": partial,
        "offline_stub_count": offline_stub,
        "parse_deferred_count": parse_deferred,
        "unusable_count": unusable,
        "not_task_relevant_count": not_task_relevant,
        "disease_relevance_status_counts": dict(disease_status_counter),
    }

    trace = append_trace(
        state,
        node_name="document_quality_check",
        message=(
            f"Quality-checked {len(updated)} documents: "
            f"{usable} usable, {partial} partial, {offline_stub} offline stub, "
            f"{parse_deferred} parse deferred, {unusable} unusable."
        ),
        metadata=summary,
    )
    return {
        "documents": updated,
        "document_quality_summary": summary,
        "disease_relevance_summary": update_disease_relevance_summary(
            {**state, "documents": updated}
        ),
        "collection_trace": trace,
    }


_WHITESPACE_RE = re.compile(r"\s+")


def _normalize_whitespace(text: str) -> str:
    if not text:
        return ""
    return _WHITESPACE_RE.sub(" ", text).strip()


def _document_is_chunkable(
    doc: dict,
    policy: EvidenceChunkingPolicy,
) -> tuple[bool, str]:
    if doc.get("is_offline_stub"):
        return False, "offline_stub"
    if doc.get("parse_status") in {"pdf_parsing_deferred", "parse_deferred"}:
        return False, "parse_deferred"
    quality_status = doc.get("quality_status")
    if quality_status in policy.excluded_quality_statuses:
        return False, quality_status or "excluded_quality_status"
    if quality_status == "not_task_relevant" or doc.get(
        "not_extractable_for_task_disease"
    ):
        return False, "not_task_relevant"
    clean_text = doc.get("clean_text") or ""
    if not clean_text.strip():
        return False, "missing_clean_text"
    if quality_status in policy.chunkable_quality_statuses:
        return True, "chunkable"
    return False, "not_chunkable_quality_status"


def _split_text_into_chunks(
    text: str,
    max_chars: int,
    overlap_chars: int,
    min_chars: int,
) -> list[dict]:
    text = _normalize_whitespace(text)
    if not text:
        return []
    if len(text) <= max_chars:
        return [{"text": text, "char_start": 0, "char_end": len(text)}]

    chunks: list[dict] = []
    start = 0
    text_len = len(text)
    while start < text_len:
        end = min(start + max_chars, text_len)
        if end < text_len:
            # Try to end on a sentence boundary in the last ~200 chars.
            window_start = max(start, end - 200)
            last_period = text.rfind(". ", window_start, end)
            if last_period >= 0:
                end = last_period + 2
        chunk_text = text[start:end].strip()
        if chunk_text:
            chunks.append(
                {"text": chunk_text, "char_start": start, "char_end": end}
            )
        if end >= text_len:
            break
        start = max(end - overlap_chars, start + 1)

    if len(chunks) > 1:
        long_enough = [c for c in chunks if len(c["text"]) >= min_chars]
        if long_enough:
            chunks = long_enough
    return chunks


def _table_to_text(table: dict) -> str:
    rows = table.get("rows") if isinstance(table, dict) else None
    if rows:
        return "\n".join(
            " | ".join(str(cell) for cell in row) for row in rows
        )
    return str(table)


def _chunk_table(table: dict, table_cfg: dict) -> list[dict]:
    rows = table.get("rows") if isinstance(table, dict) else None
    if not rows:
        return [{"text": _table_to_text(table), "table_id": "0"}]

    max_rows = int(table_cfg.get("max_rows_per_chunk", 20) or 20)
    table_index = table.get("table_index", 0)
    if len(rows) <= max_rows:
        text = "\n".join(" | ".join(str(c) for c in row) for row in rows)
        return [{"text": text, "table_id": str(table_index)}]

    chunks: list[dict] = []
    for offset in range(0, len(rows), max_rows):
        slice_rows = rows[offset : offset + max_rows]
        text = "\n".join(" | ".join(str(c) for c in row) for row in slice_rows)
        chunks.append(
            {"text": text, "table_id": f"{table_index}_{offset // max_rows}"}
        )
    return chunks


def _detect_signal_categories(
    text: str,
    signal_map: dict[str, list[str]],
) -> dict[str, int]:
    lowered = (text or "").lower()
    hits: dict[str, int] = {}
    for category, terms in signal_map.items():
        count = 0
        for term in terms:
            if not term:
                continue
            if term.lower() in lowered:
                count += 1
        if count > 0:
            hits[category] = count
    return hits


def _flag_data_presence(
    text: str,
    doc: dict,
    policy: EvidenceChunkingPolicy,
) -> tuple[bool, list[str], list[str], float, str]:
    data_hits = _detect_signal_categories(text, policy.target_data_signals)
    context_hits = _detect_signal_categories(text, policy.context_signals)
    data_types = list(data_hits.keys())
    context_types = list(context_hits.keys())
    total_data = sum(data_hits.values())

    strong = int(policy.presence_thresholds.get("strong_data_signal_count", 3))
    moderate = int(policy.presence_thresholds.get("moderate_data_signal_count", 2))

    fetch_purpose = doc.get("fetch_purpose")
    if total_data >= strong:
        return True, data_types, context_types, 0.85, "strong deterministic data signal"
    if total_data >= moderate:
        return True, data_types, context_types, 0.70, "moderate deterministic data signal"
    if fetch_purpose == "data_extraction" and data_types:
        return (
            True,
            data_types,
            context_types,
            0.60,
            "weak data signal in a data-extraction document",
        )
    confidence = 0.40 if context_types else 0.20
    return False, data_types, context_types, confidence, "context only or no target data signal"


def _flag_context_only_presence(
    text: str,
    policy: EvidenceChunkingPolicy,
) -> tuple[bool, list[str], list[str], float, str, bool]:
    data_hits = _detect_signal_categories(text, policy.target_data_signals)
    context_hits = _detect_signal_categories(text, policy.context_signals)
    context_types = list(context_hits.keys())
    suppressed = bool(data_hits)
    confidence = 0.40 if context_types else 0.20
    return (
        False,
        [],
        context_types,
        confidence,
        "context-only source; target data suppressed",
        suppressed,
    )


def _make_evidence_chunk(
    doc: dict,
    chunk_index: int,
    chunk_kind: str,
    text: str,
    char_start: int | None,
    char_end: int | None,
    table_id: str | None,
    contains_target_data: bool,
    data_types: list[str],
    context_types: list[str],
    confidence: float,
    presence_reason: str,
    disease_assessment: dict | None = None,
    extraction_eligible_for_task_disease: bool | None = None,
) -> EvidenceChunk:
    source_id = doc.get("source_id") or ""
    chunk_id = f"chunk_{source_id}_{chunk_index:03d}"
    return EvidenceChunk(
        chunk_id=chunk_id,
        source_id=source_id,
        text=text,
        section=None,
        page=None,
        table_id=table_id,
        contains_target_data=contains_target_data,
        data_types=list(data_types),
        confidence=confidence,
        document_type=doc.get("document_type"),
        fetch_purpose=doc.get("fetch_purpose"),
        source_url=doc.get("url"),
        canonical_url=doc.get("canonical_url"),
        title=doc.get("title"),
        publisher=doc.get("publisher"),
        source_type=doc.get("source_type"),
        source_role=doc.get("source_role"),
        source_role_final=doc.get("source_role_final"),
        credibility_score=doc.get("credibility_score"),
        credibility_level=doc.get("credibility_level"),
        discovery_method=doc.get("discovery_method"),
        search_provider=doc.get("search_provider"),
        query_id=doc.get("query_id"),
        query_used=doc.get("query_used"),
        planned_query_id=doc.get("planned_query_id"),
        provider_channel=doc.get("provider_channel"),
        role_hint=doc.get("role_hint"),
        quality_status=doc.get("quality_status"),
        chunk_index=chunk_index,
        chunk_kind=chunk_kind,
        char_start=char_start,
        char_end=char_end,
        context_types=list(context_types),
        presence_reason=presence_reason,
        **assessment_fields(disease_assessment or {}, ""),
        extraction_eligible_for_task_disease=extraction_eligible_for_task_disease,
    )


def evidence_chunking_and_data_presence_flagging(state: DataCollectionState) -> dict:
    """Split usable real documents into evidence chunks and flag data presence."""

    policy = EvidenceChunkingPolicy(**load_evidence_chunking_policy())
    role_policy = load_source_role_policy()
    documents = list(state.get("documents") or [])

    evidence_chunks: list[EvidenceChunk] = []
    skip_reason_counter: Counter = Counter()
    data_type_counter: Counter = Counter()
    context_type_counter: Counter = Counter()
    fetch_purpose_counter: Counter = Counter()
    skipped_count = 0
    chunkable_count = 0
    text_chunk_count = 0
    table_chunk_count = 0
    target_data_count = 0
    context_only_count = 0
    no_signal_count = 0
    context_only_document_ids: set[str] = set()
    context_only_chunk_count = 0
    context_only_target_data_suppressed_count = 0
    disease_status_counter: Counter = Counter()
    disease_mismatch_chunk_count = 0
    disease_mismatch_source_ids: set[str] = set()
    context = build_disease_relevance_context(state)

    table_cfg = policy.table_chunking or {}
    table_enabled = bool(table_cfg.get("enabled", False))

    for doc in documents:
        is_chunkable, reason = _document_is_chunkable(doc, policy)
        if not is_chunkable:
            skip_reason_counter[reason] += 1
            skipped_count += 1
            continue
        chunkable_count += 1
        doc_is_context_only = _is_context_only_document(doc, role_policy)
        if doc_is_context_only and doc.get("source_id"):
            context_only_document_ids.add(doc.get("source_id"))
        chunk_index = 0

        # Text chunks.
        text_chunks = _split_text_into_chunks(
            doc.get("clean_text") or "",
            policy.max_chunk_chars,
            policy.chunk_overlap_chars,
            policy.min_chunk_chars,
        )
        for tc in text_chunks:
            chunk_index += 1
            if doc_is_context_only:
                contains, data_types, context_types, confidence, reason_text, suppressed = (
                    _flag_context_only_presence(tc["text"], policy)
                )
                context_only_chunk_count += 1
                if suppressed:
                    context_only_target_data_suppressed_count += 1
            else:
                contains, data_types, context_types, confidence, reason_text = (
                    _flag_data_presence(tc["text"], doc, policy)
                )
            disease_assessment = assess_chunk_disease_relevance(
                {**doc, "text": tc["text"], "title": doc.get("title")},
                context,
            )
            disease_status = disease_assessment.get("status") or "unknown"
            disease_status_counter[disease_status] += 1
            extraction_eligible = bool(
                contains and disease_status == TARGET_DISEASE_MATCH
            )
            if contains and disease_status != TARGET_DISEASE_MATCH:
                contains = False
                data_types = []
                if "disease_mismatch_context" not in context_types:
                    context_types.append("disease_mismatch_context")
                confidence = min(float(confidence or 0.0), 0.40)
                reason_text = (
                    "disease relevance gate suppressed extraction: "
                    f"{disease_assessment.get('reason')}"
                )
                disease_mismatch_chunk_count += 1
                if doc.get("source_id"):
                    disease_mismatch_source_ids.add(doc.get("source_id"))
            chunk = _make_evidence_chunk(
                doc=doc,
                chunk_index=chunk_index,
                chunk_kind="text",
                text=tc["text"],
                char_start=tc.get("char_start"),
                char_end=tc.get("char_end"),
                table_id=None,
                contains_target_data=contains,
                data_types=data_types,
                context_types=context_types,
                confidence=confidence,
                presence_reason=reason_text,
                disease_assessment=disease_assessment,
                extraction_eligible_for_task_disease=extraction_eligible,
            )
            evidence_chunks.append(chunk)
            text_chunk_count += 1
            for cat in data_types:
                data_type_counter[cat] += 1
            for cat in context_types:
                context_type_counter[cat] += 1
            fp = doc.get("fetch_purpose") or "unknown"
            fetch_purpose_counter[fp] += 1
            if contains:
                target_data_count += 1
            elif context_types:
                context_only_count += 1
            else:
                no_signal_count += 1

        # Table chunks.
        if table_enabled:
            tables = doc.get("tables") or []
            for table in tables:
                for tc in _chunk_table(table, table_cfg):
                    chunk_index += 1
                    if doc_is_context_only:
                        (
                            contains,
                            data_types,
                            context_types,
                            confidence,
                            reason_text,
                            suppressed,
                        ) = _flag_context_only_presence(tc["text"], policy)
                        context_only_chunk_count += 1
                        if suppressed:
                            context_only_target_data_suppressed_count += 1
                    else:
                        contains, data_types, context_types, confidence, reason_text = (
                            _flag_data_presence(tc["text"], doc, policy)
                        )
                    disease_assessment = assess_chunk_disease_relevance(
                        {**doc, "text": tc["text"], "title": doc.get("title")},
                        context,
                    )
                    disease_status = disease_assessment.get("status") or "unknown"
                    disease_status_counter[disease_status] += 1
                    extraction_eligible = bool(
                        contains and disease_status == TARGET_DISEASE_MATCH
                    )
                    if contains and disease_status != TARGET_DISEASE_MATCH:
                        contains = False
                        data_types = []
                        if "disease_mismatch_context" not in context_types:
                            context_types.append("disease_mismatch_context")
                        confidence = min(float(confidence or 0.0), 0.40)
                        reason_text = (
                            "disease relevance gate suppressed extraction: "
                            f"{disease_assessment.get('reason')}"
                        )
                        disease_mismatch_chunk_count += 1
                        if doc.get("source_id"):
                            disease_mismatch_source_ids.add(doc.get("source_id"))
                    chunk = _make_evidence_chunk(
                        doc=doc,
                        chunk_index=chunk_index,
                        chunk_kind="table",
                        text=tc["text"],
                        char_start=None,
                        char_end=None,
                        table_id=tc.get("table_id"),
                        contains_target_data=contains,
                        data_types=data_types,
                        context_types=context_types,
                        confidence=confidence,
                        presence_reason=reason_text,
                        disease_assessment=disease_assessment,
                        extraction_eligible_for_task_disease=extraction_eligible,
                    )
                    evidence_chunks.append(chunk)
                    table_chunk_count += 1
                    for cat in data_types:
                        data_type_counter[cat] += 1
                    for cat in context_types:
                        context_type_counter[cat] += 1
                    fp = doc.get("fetch_purpose") or "unknown"
                    fetch_purpose_counter[fp] += 1
                    if contains:
                        target_data_count += 1
                    elif context_types:
                        context_only_count += 1
                    else:
                        no_signal_count += 1

    chunk_dicts = [c.model_dump() for c in evidence_chunks]

    chunking_summary = {
        "input_document_count": len(documents),
        "chunkable_document_count": chunkable_count,
        "skipped_document_count": skipped_count,
        "skip_reason_counts": dict(skip_reason_counter),
        "text_chunk_count": text_chunk_count,
        "table_chunk_count": table_chunk_count,
        "total_chunk_count": text_chunk_count + table_chunk_count,
        "context_only_document_count": len(context_only_document_ids),
        "context_only_source_ids": sorted(context_only_document_ids),
        "context_only_chunk_count": context_only_chunk_count,
        "disease_relevance_status_counts": dict(disease_status_counter),
        "disease_mismatch_chunk_count": disease_mismatch_chunk_count,
        "disease_mismatch_source_ids": sorted(disease_mismatch_source_ids),
    }
    presence_summary = {
        "total_chunk_count": text_chunk_count + table_chunk_count,
        "target_data_chunk_count": target_data_count,
        "context_only_chunk_count": context_only_count,
        "no_signal_chunk_count": no_signal_count,
        "context_only_document_count": len(context_only_document_ids),
        "context_only_source_ids": sorted(context_only_document_ids),
        "context_only_guardrail_chunk_count": context_only_chunk_count,
        "context_only_target_data_suppressed_count": (
            context_only_target_data_suppressed_count
        ),
        "data_type_counts": dict(data_type_counter),
        "context_type_counts": dict(context_type_counter),
        "fetch_purpose_counts": dict(fetch_purpose_counter),
        "disease_relevance_status_counts": dict(disease_status_counter),
        "disease_mismatch_chunk_count": disease_mismatch_chunk_count,
        "disease_mismatch_source_ids": sorted(disease_mismatch_source_ids),
    }

    trace = append_trace(
        state,
        node_name="evidence_chunking_and_data_presence_flagging",
        message=(
            f"Chunked {chunkable_count}/{len(documents)} documents into "
            f"{text_chunk_count + table_chunk_count} evidence chunks "
            f"({target_data_count} flagged as containing target data)."
        ),
        metadata={**chunking_summary, **presence_summary},
    )
    return {
        "evidence_chunks": chunk_dicts,
        "evidence_chunking_summary": chunking_summary,
        "data_presence_summary": presence_summary,
        "disease_relevance_summary": update_disease_relevance_summary(
            {**state, "evidence_chunks": chunk_dicts},
            disease_mismatch_chunk_count=disease_mismatch_chunk_count,
        ),
        "collection_trace": trace,
    }
