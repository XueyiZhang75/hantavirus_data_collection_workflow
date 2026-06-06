"""Content fetching, parsing, and document quality (Step 5).

Default behavior is fully offline: when `HDC_ENABLE_LIVE_FETCH` is not set to
"true", the workflow generates deterministic metadata-stub documents and does
NOT contact the network. Live HTTP fetching is gated behind that environment
variable so tests stay offline-safe.
"""

from __future__ import annotations

import hashlib
import os
from collections import Counter
from datetime import datetime, timezone
from urllib.parse import urlsplit

import re

from ..config import (
    get_collection_mode,
    load_content_fetch_policy,
    load_evidence_chunking_policy,
    load_hantavirus_fixture_documents,
    load_source_role_policy,
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


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------


def _live_fetch_enabled() -> bool:
    """True only if HDC_ENABLE_LIVE_FETCH is set to "true" (case-insensitive)."""

    return (os.environ.get("HDC_ENABLE_LIVE_FETCH") or "").strip().lower() == "true"


def _fixture_documents_enabled() -> bool:
    """True only if HDC_USE_FIXTURE_DOCUMENTS is set to "true" (case-insensitive)."""

    return (os.environ.get("HDC_USE_FIXTURE_DOCUMENTS") or "").strip().lower() == "true"


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


def _now_fixed_or_utc(live: bool) -> str:
    if not live:
        return _OFFLINE_FIXED_TIMESTAMP
    return datetime.now(timezone.utc).isoformat()


def _hash_text(text: str | None) -> str | None:
    if not text:
        return None
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


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
    if entry.get("requires_human_review"):
        return "human_review"
    if _is_search_endpoint(entry, policy):
        return "search_endpoint"
    url = entry.get("canonical_url") or entry.get("url") or ""
    scheme = _url_scheme(url)
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
    allowlist: set[str] | None = None,
    collection_mode: str = "standard",
    role_policy: dict | None = None,
) -> tuple[list[ContentFetchRequest], dict[str, int]]:
    registry = list(state.get("source_registry") or [])
    skip_counts: Counter = Counter()
    accepted: list[ContentFetchRequest] = []

    for entry in registry:
        skip_reason = _classify_skip_reason(
            entry, policy, allowlist, collection_mode, role_policy
        )
        if skip_reason is not None:
            skip_counts[skip_reason] += 1
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
                final_screening_decision=final_decision,
                fetch_purpose=fetch_purpose,
                priority=entry.get("priority"),
                live_fetch_enabled=live,
            )
        )

    accepted.sort(key=lambda r: (r.priority is None, r.priority or 0, r.source_id))
    return accepted, dict(skip_counts)


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
        final_screening_decision=request.final_screening_decision,
        fetch_purpose=request.fetch_purpose,
        fetch_status="fixture_loaded",
        fetch_error=None,
        http_status_code=None,
        content_type=None,
        fetched_at=_OFFLINE_FIXED_TIMESTAMP,
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
        final_screening_decision=request.final_screening_decision,
        fetch_purpose=request.fetch_purpose,
        fetch_status="offline_stub",
        fetch_error=None,
        http_status_code=None,
        content_type=None,
        fetched_at=_OFFLINE_FIXED_TIMESTAMP,
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


def _html_to_clean_text(html_bytes: bytes) -> tuple[str | None, str | None, list[dict]]:
    """Return (clean_text, title, tables) from HTML bytes."""

    try:
        from bs4 import BeautifulSoup
    except ImportError:
        return None, None, []

    soup = BeautifulSoup(html_bytes, "html.parser")

    for tag_name in ("script", "style", "nav", "footer", "noscript"):
        for tag in soup.find_all(tag_name):
            tag.decompose()

    title = None
    if soup.title and soup.title.string:
        title = soup.title.string.strip()

    text = soup.get_text(separator="\n", strip=True)
    clean_lines = [line for line in (l.strip() for l in text.splitlines()) if line]
    clean_text = "\n".join(clean_lines) or None

    tables: list[dict] = []
    for i, table in enumerate(soup.find_all("table")):
        rows: list[list[str]] = []
        for tr in table.find_all("tr"):
            cells = [c.get_text(strip=True) for c in tr.find_all(["th", "td"])]
            if cells:
                rows.append(cells)
        if rows:
            tables.append({"table_index": i, "rows": rows})

    return clean_text, title, tables


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
    fixture_enabled = _fixture_documents_enabled()
    fixture_map: dict[str, FixtureDocument] = (
        _load_fixture_document_map() if fixture_enabled else {}
    )
    allowlist = _parse_source_id_allowlist()

    fetch_requests, skip_counts = _build_fetch_requests(
        state, policy, live, allowlist, collection_mode, role_policy
    )

    registry = list(state.get("source_registry") or [])
    registry_by_id = {e.get("source_id"): e for e in registry}

    documents: list[Document] = []
    fixture_loaded_source_ids: list[str] = []
    for request in fetch_requests:
        source_entry = registry_by_id.get(request.source_id) or {}
        fixture = fixture_map.get(request.source_id) if fixture_enabled else None
        if fixture is not None:
            doc = _make_fixture_document(request, source_entry, fixture)
            fixture_loaded_source_ids.append(request.source_id)
        elif live:
            doc = _fetch_live_document(request, source_entry, policy)
        else:
            doc = _make_offline_stub_document(request, source_entry)
        documents.append(doc)

    document_dicts = [d.model_dump() for d in documents]
    request_dicts = [r.model_dump() for r in fetch_requests]

    fetch_status_counts = dict(Counter(d.fetch_status or "unknown" for d in documents))
    document_type_counts = dict(Counter(d.document_type or "unknown" for d in documents))
    fetch_purpose_counts = dict(
        Counter(r.fetch_purpose or "unknown" for r in fetch_requests)
    )
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
        "fixture_document_count": len(fixture_loaded_source_ids),
        "fixture_source_ids": list(fixture_loaded_source_ids),
        "source_id_allowlist_enabled": allowlist is not None,
        "source_id_allowlist": sorted(allowlist) if allowlist else [],
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
    usable = partial = offline_stub = parse_deferred = unusable = 0

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
        elif parse_status == "pdf_parsing_deferred":
            quality_status = "parse_deferred"
            if "pdf_parsing_not_implemented" not in issues:
                issues.append("pdf_parsing_not_implemented")
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

        new_doc["quality_status"] = quality_status
        new_doc["quality_issues"] = issues
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
    if doc.get("parse_status") == "pdf_parsing_deferred":
        return False, "pdf_parsing_deferred"
    quality_status = doc.get("quality_status")
    if quality_status in policy.excluded_quality_statuses:
        return False, quality_status or "excluded_quality_status"
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
        quality_status=doc.get("quality_status"),
        chunk_index=chunk_index,
        chunk_kind=chunk_kind,
        char_start=char_start,
        char_end=char_end,
        context_types=list(context_types),
        presence_reason=presence_reason,
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
        "collection_trace": trace,
    }
