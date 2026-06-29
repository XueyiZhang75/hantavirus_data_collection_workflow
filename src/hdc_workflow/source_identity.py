"""Source identity, publisher, and provenance assessment helpers.

This module is deterministic by default. Optional LLM calls are advisory and
must use only metadata or already fetched page text supplied by the workflow.
"""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from urllib.parse import urlsplit

from . import llm_clients
from .agents.source_identity_agent import assess_source_identity_with_llm
from .models import SourceIdentityAssessment, SourceIdentitySummary


SOURCE_IDENTITY_METHOD = "source_identity_publisher_credibility_v1"

_SEARCH_PROVIDERS = {"tavily", "fixture", "serpapi", "bing", "google", "brave"}
_SOCIAL_DOMAINS = (
    "facebook.com",
    "instagram.com",
    "x.com",
    "twitter.com",
    "threads.net",
    "tiktok.com",
    "youtube.com",
)
_NEWS_DOMAINS = (
    "ajmc.com",
    "nvdaily.com",
    "wsls.com",
    "wvtf.org",
    "reuters.com",
    "apnews.com",
    "cnn.com",
    "nbcnews.com",
    "abcnews.go.com",
    "nytimes.com",
    "washingtonpost.com",
)
_AGGREGATOR_DOMAINS = (
    "outbreaknewstoday.com",
    "substack.com",
    "wikipedia.org",
    "flutrackers.com",
    "healthmap.org",
    "promedmail.org",
)
_NON_OFFICIAL_DOMAIN_PUBLISHERS = {
    "cidrap.umn.edu": ("CIDRAP", "academic_or_peer_reviewed_source"),
    "www.cidrap.umn.edu": ("CIDRAP", "academic_or_peer_reviewed_source"),
}
_OFFICIAL_DOMAIN_PUBLISHERS = {
    "nmhealth.org": (
        "New Mexico Department of Health",
        "state_or_local_public_health_agency",
    ),
    "www.nmhealth.org": (
        "New Mexico Department of Health",
        "state_or_local_public_health_agency",
    ),
    "vdh.virginia.gov": (
        "Virginia Department of Health",
        "state_or_local_public_health_agency",
    ),
    "www.vdh.virginia.gov": (
        "Virginia Department of Health",
        "state_or_local_public_health_agency",
    ),
    "cdc.gov": (
        "Centers for Disease Control and Prevention",
        "national_public_health_agency",
    ),
    "www.cdc.gov": (
        "Centers for Disease Control and Prevention",
        "national_public_health_agency",
    ),
    "stacks.cdc.gov": (
        "Centers for Disease Control and Prevention",
        "national_public_health_agency",
    ),
    "who.int": ("World Health Organization", "international_public_health_agency"),
    "www.who.int": (
        "World Health Organization",
        "international_public_health_agency",
    ),
    "paho.org": (
        "Pan American Health Organization",
        "international_public_health_agency",
    ),
    "www.paho.org": (
        "Pan American Health Organization",
        "international_public_health_agency",
    ),
    "ecdc.europa.eu": (
        "European Centre for Disease Prevention and Control",
        "international_public_health_agency",
    ),
}
_PAGE_PUBLISHER_MARKERS = (
    ("Virginia Department of Health", "Virginia Department of Health"),
    ("Centers for Disease Control and Prevention", "Centers for Disease Control and Prevention"),
    ("CDC", "Centers for Disease Control and Prevention"),
    ("World Health Organization", "World Health Organization"),
    ("European Centre for Disease Prevention and Control", "European Centre for Disease Prevention and Control"),
    ("Outbreak News Today", "Outbreak News Today"),
    ("WSLS", "WSLS"),
    ("Reuters", "Reuters"),
)
_RECOMMENDED_SOURCE_ROLES = {
    "collection",
    "validation",
    "collection_support",
    "context",
    "excluded",
    "needs_human_review",
}
_FETCHABLE_RECOMMENDATIONS = {
    "fetch_for_extraction",
    "fetch_for_context",
    "already_fetched_review_only",
}


def _clean(value) -> str:
    return str(value or "").strip()


def _lower(value) -> str:
    return _clean(value).lower()


def _unique(values: list) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        text = _clean(value)
        if not text or text in seen:
            continue
        seen.add(text)
        out.append(text)
    return out


def _slug(value) -> str | None:
    text = _lower(value)
    if not text:
        return None
    chars: list[str] = []
    previous_sep = False
    for char in text:
        if char.isalnum():
            chars.append(char)
            previous_sep = False
        elif not previous_sep:
            chars.append("_")
            previous_sep = True
    return "".join(chars).strip("_") or None


def _domain_from_url(url: str | None) -> str | None:
    if not url:
        return None
    try:
        netloc = urlsplit(url).netloc.lower()
    except Exception:  # noqa: BLE001 - malformed input is a data issue
        return None
    if netloc.startswith("www."):
        return netloc
    return netloc or None


def _domain(entry: dict) -> str | None:
    return (
        _clean(entry.get("domain"))
        or _domain_from_url(entry.get("canonical_url") or entry.get("url"))
    )


def _raw_search_source(entry: dict) -> str | None:
    return (
        _clean(entry.get("search_result_source_raw"))
        or _clean(entry.get("search_provider_result_source"))
        or _clean(entry.get("result_source"))
        or _clean(entry.get("publisher_candidate_from_search_metadata"))
        or None
    )


def _search_provider(entry: dict) -> str | None:
    return _clean(entry.get("search_provider")) or None


def _raw_is_provider(raw: str | None, provider: str | None) -> bool:
    raw_norm = _slug(raw)
    provider_norm = _slug(provider)
    if not raw_norm:
        return False
    return raw_norm == provider_norm or raw_norm in _SEARCH_PROVIDERS


def _add_warning(warnings: list[str], flag: str) -> None:
    if flag and flag not in warnings:
        warnings.append(flag)


def _known_domain_publisher(domain: str | None) -> tuple[str | None, str | None]:
    if not domain:
        return None, None
    domain_low = domain.lower().removeprefix("www.")
    if domain_low in _NON_OFFICIAL_DOMAIN_PUBLISHERS:
        return _NON_OFFICIAL_DOMAIN_PUBLISHERS[domain_low]
    for known, value in _NON_OFFICIAL_DOMAIN_PUBLISHERS.items():
        known_low = known.removeprefix("www.")
        if domain_low.endswith("." + known_low):
            return value
    if domain_low in _OFFICIAL_DOMAIN_PUBLISHERS:
        return _OFFICIAL_DOMAIN_PUBLISHERS[domain_low]
    for known, value in _OFFICIAL_DOMAIN_PUBLISHERS.items():
        known_low = known.removeprefix("www.")
        if domain_low.endswith("." + known_low):
            return value
    if domain_low.endswith(".gov") and (
        "health" in domain_low or "doh" in domain_low or "dhhs" in domain_low
    ):
        return domain_low, "state_or_local_public_health_agency"
    if any(domain_low == d or domain_low.endswith("." + d) for d in _SOCIAL_DOMAINS):
        return None, "social_media"
    if any(domain_low == d or domain_low.endswith("." + d) for d in _NEWS_DOMAINS):
        return None, "news_media"
    if any(domain_low == d or domain_low.endswith("." + d) for d in _AGGREGATOR_DOMAINS):
        return None, "secondary_aggregator"
    if "pubmed.ncbi.nlm.nih.gov" in domain_low:
        return "PubMed", "structured_database"
    if "ncbi.nlm.nih.gov" in domain_low:
        return "National Center for Biotechnology Information", "structured_database"
    return None, None


def _is_search_endpoint(entry: dict, domain: str | None) -> bool:
    url = _lower(entry.get("canonical_url") or entry.get("url"))
    title = _lower(entry.get("title"))
    if "pubmed.ncbi.nlm.nih.gov" in _lower(domain) and ("?term=" in url or "/?" in url):
        return True
    endpoint_terms = ("search", "query", "results")
    return any(term in title for term in endpoint_terms) and any(
        part in url for part in ("search", "query", "?q=", "?term=")
    )


def _classify_source(entry: dict, domain: str | None) -> tuple[str, str, list[str]]:
    text = " ".join(
        _clean(entry.get(field))
        for field in ("title", "snippet", "source_type", "source_purpose", "notes")
    ).lower()
    evidence: list[str] = []
    if _is_search_endpoint(entry, domain):
        return "search_endpoint", "high", ["url", "title"]
    _, domain_type = _known_domain_publisher(domain)
    if domain_type:
        evidence.append("domain")
        return domain_type, "high" if domain_type != "structured_database" else "medium", evidence
    if any(term in text for term in ("fact sheet", "factsheet", "about hantavirus", "symptoms", "prevention")):
        return "background_fact_sheet", "medium", ["title_or_snippet"]
    source_type = _lower(entry.get("source_type"))
    if source_type:
        if "news" in source_type:
            return "news_media", "medium", ["source_type"]
        if "social" in source_type:
            return "social_media", "medium", ["source_type"]
        if "official" in source_type or "public_health" in source_type:
            return "official_public_health_agency", "low", ["source_type"]
    return "unknown", "low", []


def _task_is_global(collection_spec: dict | None) -> bool:
    if not isinstance(collection_spec, dict):
        return False
    text = " ".join(
        _clean(collection_spec.get(field))
        for field in ("geography", "location", "jurisdiction", "scope")
    ).lower()
    return any(term in text for term in ("global", "worldwide", "world", "all"))


def _jurisdiction_scope(source_type: str, domain: str | None) -> str:
    domain_low = _lower(domain).removeprefix("www.")
    if source_type == "international_public_health_agency":
        return "international"
    if source_type == "national_public_health_agency":
        return "national"
    if source_type == "state_or_local_public_health_agency":
        return "subnational"
    if source_type == "official_public_health_agency":
        return "official_unspecified"
    if source_type in {"news_media", "secondary_aggregator", "social_media"}:
        return "non_authority"
    if domain_low.endswith(".gov"):
        return "government_unspecified"
    return "unknown"


def _page_function(entry: dict, source_type: str) -> str:
    text = " ".join(
        _clean(entry.get(field))
        for field in ("title", "snippet", "query_used", "source_purpose", "notes")
    ).lower()
    if any(term in text for term in ("disease outbreak news", "don", "outbreak news")):
        return "official_alert"
    if any(term in text for term in ("alert", "advisory", "health alert", "han")):
        return "official_alert"
    if any(term in text for term in ("annual report", "report", "pdf")):
        return "report"
    if any(term in text for term in ("dashboard", "database", "data portal")):
        return "dashboard_or_database"
    if source_type in {"background_fact_sheet", "public_health_context_page"}:
        return "context_page"
    if source_type in {"news_media", "secondary_aggregator"}:
        return "secondary_report"
    if source_type == "social_media":
        return "social_post"
    return "unknown"


def _primary_vs_secondary(source_type: str) -> str:
    if source_type in {
        "national_public_health_agency",
        "state_or_local_public_health_agency",
        "international_public_health_agency",
        "official_public_health_agency",
        "structured_database",
        "academic_or_peer_reviewed_source",
    }:
        return "primary_or_authoritative"
    if source_type in {"news_media", "secondary_aggregator", "personal_blog_or_forum"}:
        return "secondary"
    if source_type == "social_media":
        return "social"
    return "unknown"


def _authority_bucket(
    source_type: str,
    *,
    collection_spec: dict | None = None,
) -> str:
    if source_type == "social_media":
        return "social_media"
    if source_type in {"secondary_aggregator", "personal_blog_or_forum"}:
        return "secondary_aggregator"
    if source_type in {"news_media", "commercial_site"}:
        return "secondary_media"
    if source_type == "academic_or_peer_reviewed_source":
        return "academic_source"
    if source_type == "structured_database":
        return "structured_database"
    if source_type == "state_or_local_public_health_agency" and _task_is_global(
        collection_spec
    ):
        return "local_official_context"
    if source_type in {
        "national_public_health_agency",
        "state_or_local_public_health_agency",
        "international_public_health_agency",
        "official_public_health_agency",
    }:
        return "official_authority"
    return "unknown"


def _role_for_task_scope(role: dict, source_type: str, collection_spec: dict | None) -> dict:
    if source_type != "state_or_local_public_health_agency" or not _task_is_global(
        collection_spec
    ):
        return role
    adjusted = dict(role)
    if adjusted.get("recommended_source_role") == "collection":
        adjusted["recommended_source_role"] = "collection_support"
        adjusted["claim_support_role"] = "corroboration_support"
        adjusted["supports_primary_case_claims"] = False
    return adjusted


def _finalize_authority_metadata(
    assessment: dict,
    source_entry: dict,
    collection_spec: dict | None,
) -> dict:
    out = dict(assessment)
    source_type = _lower(out.get("source_type_final")) or "unknown"
    domain = out.get("domain") or _domain(source_entry)
    out["publisher_type"] = source_type if source_type != "unknown" else None
    out["jurisdiction_scope"] = _jurisdiction_scope(source_type, domain)
    out["page_function"] = _page_function(source_entry, source_type)
    out["primary_vs_secondary"] = _primary_vs_secondary(source_type)
    out["authority_bucket"] = _authority_bucket(
        source_type, collection_spec=collection_spec
    )
    scoped_role = _role_for_task_scope(
        {
            "claim_support_role": out.get("claim_support_role"),
            "recommended_source_role": out.get("recommended_source_role"),
            "supports_primary_case_claims": out.get("supports_primary_case_claims"),
        },
        source_type,
        collection_spec,
    )
    for key, value in scoped_role.items():
        if value not in (None, ""):
            out[key] = value
    return out


def _role_decision(source_type: str, entry: dict) -> dict:
    text = " ".join(
        _clean(entry.get(field)) for field in ("title", "snippet", "query_used")
    ).lower()
    has_case_signal = any(
        term in text
        for term in (
            "case",
            "death",
            "deaths",
            "surveillance",
            "reported",
            "confirmed",
            "data",
        )
    )
    has_zero_signal = any(term in text for term in ("no cases", "zero case", "0 cases"))
    has_exposure_signal = "monitoring" in text or "exposure" in text

    if source_type == "search_endpoint":
        return {
            "claim_support_role": "search_discovery_only",
            "recommended_source_role": "excluded",
            "recommended_fetch_use": "do_not_fetch",
            "recommended_extraction_use": "do_not_extract",
            "likely_contains_extractable_data": False,
            "supports_primary_case_claims": False,
            "supports_zero_case_claims": False,
            "supports_exposure_monitoring_claims": False,
            "supports_context_only": False,
        }
    if source_type == "social_media":
        return {
            "claim_support_role": "insufficient_information",
            "recommended_source_role": "needs_human_review",
            "recommended_fetch_use": "fetch_only_after_review",
            "recommended_extraction_use": "needs_human_review",
            "likely_contains_extractable_data": False,
            "supports_primary_case_claims": False,
            "supports_zero_case_claims": False,
            "supports_exposure_monitoring_claims": False,
            "supports_context_only": True,
        }
    if source_type in {"background_fact_sheet", "public_health_context_page"}:
        return {
            "claim_support_role": "context_only",
            "recommended_source_role": "context",
            "recommended_fetch_use": "fetch_for_context",
            "recommended_extraction_use": "extract_context_only",
            "likely_contains_extractable_data": False,
            "supports_primary_case_claims": False,
            "supports_zero_case_claims": False,
            "supports_exposure_monitoring_claims": False,
            "supports_context_only": True,
        }
    if source_type in {"news_media", "secondary_aggregator"}:
        return {
            "claim_support_role": "corroboration_support",
            "recommended_source_role": "collection_support",
            "recommended_fetch_use": "fetch_for_extraction",
            "recommended_extraction_use": "extract_public_health_observations"
            if has_case_signal
            else "needs_human_review",
            "likely_contains_extractable_data": has_case_signal,
            "supports_primary_case_claims": False,
            "supports_zero_case_claims": has_zero_signal,
            "supports_exposure_monitoring_claims": has_exposure_signal,
            "supports_context_only": not has_case_signal,
        }
    if source_type in {
        "state_or_local_public_health_agency",
        "national_public_health_agency",
        "international_public_health_agency",
        "official_public_health_agency",
        "structured_database",
    }:
        return {
            "claim_support_role": "primary_case_claim_support"
            if has_case_signal
            else "context_only",
            "recommended_source_role": "collection" if has_case_signal else "context",
            "recommended_fetch_use": "fetch_for_extraction"
            if has_case_signal
            else "fetch_for_context",
            "recommended_extraction_use": "extract_primary_case_claims"
            if has_case_signal
            else "extract_context_only",
            "likely_contains_extractable_data": has_case_signal,
            "supports_primary_case_claims": has_case_signal,
            "supports_zero_case_claims": has_zero_signal,
            "supports_exposure_monitoring_claims": has_exposure_signal,
            "supports_context_only": not has_case_signal,
        }
    return {
        "claim_support_role": "insufficient_information",
        "recommended_source_role": "needs_human_review",
        "recommended_fetch_use": "fetch_only_after_review",
        "recommended_extraction_use": "needs_human_review",
        "likely_contains_extractable_data": False,
        "supports_primary_case_claims": False,
        "supports_zero_case_claims": False,
        "supports_exposure_monitoring_claims": False,
        "supports_context_only": False,
    }


def _publisher_from_page(document: dict) -> tuple[str | None, list[str], list[str]]:
    title = _clean(document.get("title"))
    metadata = document.get("metadata") if isinstance(document.get("metadata"), dict) else {}
    fields = {
        "page_title": title,
        "meta_site_name": metadata.get("site_name") or metadata.get("og:site_name"),
        "meta_author": metadata.get("author"),
        "clean_text": _clean(document.get("clean_text"))[:1200],
    }
    evidence_fields: list[str] = []
    evidence_quotes: list[str] = []
    for field, value in fields.items():
        text = _clean(value)
        if not text:
            continue
        for marker, publisher in _PAGE_PUBLISHER_MARKERS:
            if marker.lower() in text.lower():
                evidence_fields.append(field)
                evidence_quotes.append(text[:220])
                return publisher, _unique(evidence_fields), _unique(evidence_quotes)
    return None, [], []


def _base_assessment(entry: dict, collection_spec: dict | None = None) -> dict:
    domain = _domain(entry)
    raw = _raw_search_source(entry)
    provider = _search_provider(entry)
    warnings = list(entry.get("source_identity_warnings") or [])
    publisher_evidence_fields: list[str] = []
    publisher_evidence_quotes: list[str] = []
    publisher_source = None
    actual_publisher = None
    actual_confidence = "low"
    known_publisher, domain_type = _known_domain_publisher(domain)

    if raw:
        if _raw_is_provider(raw, provider):
            _add_warning(warnings, "search_provider_not_publisher")
            _add_warning(warnings, "publisher_from_search_metadata_unverified")
        else:
            actual_publisher = raw
            actual_confidence = "low"
            publisher_source = "search_metadata"
            publisher_evidence_fields.append("search_result_source_raw")
            _add_warning(warnings, "publisher_from_search_metadata_unverified")

    if known_publisher:
        if actual_publisher and _slug(actual_publisher) != _slug(known_publisher):
            _add_warning(warnings, "publisher_conflict_between_search_and_domain")
        actual_publisher = known_publisher
        actual_confidence = "high" if domain else actual_confidence
        publisher_source = "domain"
        publisher_evidence_fields.append("domain")

    if not actual_publisher:
        _add_warning(warnings, "actual_publisher_unknown")

    source_type, type_confidence, type_evidence = _classify_source(entry, domain)
    if domain_type and source_type == "unknown":
        source_type = domain_type
    role = _role_for_task_scope(
        _role_decision(source_type, entry), source_type, collection_spec
    )
    publisher_type = source_type if source_type != "unknown" else None
    jurisdiction_scope = _jurisdiction_scope(source_type, domain)
    page_function = _page_function(entry, source_type)
    primary_vs_secondary = _primary_vs_secondary(source_type)
    authority_bucket = _authority_bucket(
        source_type, collection_spec=collection_spec
    )
    actual_norm = _slug(actual_publisher) if actual_publisher else None
    if role.get("recommended_source_role") == "collection_support":
        independence_prefix = (
            "upstream" if source_type in {"news_media", "secondary_aggregator"} else "publisher"
        )
    else:
        independence_prefix = "publisher"
    independence_group = (
        f"{independence_prefix}:{actual_norm}"
        if actual_norm
        else f"domain:{_slug(domain)}"
        if domain
        else None
    )

    return {
        "source_id": _clean(entry.get("source_id")) or _clean(entry.get("canonical_url")),
        "source_url": entry.get("url") or entry.get("canonical_url"),
        "canonical_url": entry.get("canonical_url") or entry.get("url"),
        "domain": domain,
        "title": entry.get("title"),
        "snippet": entry.get("snippet"),
        "search_provider": provider,
        "search_result_source_raw": raw,
        "search_provider_result_source": raw,
        "search_rank": entry.get("search_rank"),
        "query_used": entry.get("query_used"),
        "discovery_method": entry.get("discovery_method"),
        "actual_publisher": actual_publisher,
        "actual_publisher_normalized": actual_norm,
        "actual_publisher_confidence": actual_confidence,
        "publisher_evidence_fields": _unique(publisher_evidence_fields),
        "publisher_evidence_quotes": publisher_evidence_quotes,
        "publisher_source": publisher_source,
        "source_owner": actual_publisher,
        "source_owner_confidence": actual_confidence if actual_publisher else "low",
        "source_type_final": source_type,
        "source_type_confidence": type_confidence,
        "source_type_evidence": type_evidence,
        "source_type_warning_flags": [],
        "publisher_type": publisher_type,
        "jurisdiction_scope": jurisdiction_scope,
        "page_function": page_function,
        "primary_vs_secondary": primary_vs_secondary,
        "authority_bucket": authority_bucket,
        "task_relevance_assessment": "possibly_relevant",
        "disease_relevance_assessment": entry.get("source_disease_relevance_status")
        or "not_assessed",
        "geography_relevance_assessment": "not_assessed",
        "time_relevance_assessment": "not_assessed",
        **role,
        "credibility_level_llm": None,
        "credibility_rationale": None,
        "trust_basis": (
            "Official domain pattern" if publisher_source == "domain" else "Search metadata only"
        ),
        "source_independence_group": independence_group,
        "independence_confidence": "medium" if independence_group else "low",
        "likely_syndicated_or_aggregated": source_type in {"news_media", "secondary_aggregator"},
        "aggregation_or_syndication_reason": (
            "News or aggregator source may summarize upstream official reporting"
            if source_type in {"news_media", "secondary_aggregator"}
            else None
        ),
        "upstream_source_mentions": [],
        "method": SOURCE_IDENTITY_METHOD,
        "source_identity_status": "assessed",
        "assessed_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "llm_used": False,
        "warnings": _unique(warnings),
        "errors": list(entry.get("source_identity_errors") or []),
    }


def _merge_llm_decision(assessment: dict, decision: dict | None) -> dict:
    if not decision:
        return assessment
    merged = dict(assessment)
    for key in (
        "actual_publisher",
        "actual_publisher_normalized",
        "actual_publisher_confidence",
        "publisher_source",
        "source_owner",
        "source_owner_confidence",
        "source_type_llm",
        "source_type_final",
        "source_type_confidence",
        "publisher_type",
        "jurisdiction_scope",
        "page_function",
        "primary_vs_secondary",
        "authority_bucket",
        "task_relevance_assessment",
        "disease_relevance_assessment",
        "geography_relevance_assessment",
        "time_relevance_assessment",
        "likely_contains_extractable_data",
        "supports_primary_case_claims",
        "supports_zero_case_claims",
        "supports_exposure_monitoring_claims",
        "supports_context_only",
        "claim_support_role",
        "recommended_source_role",
        "recommended_fetch_use",
        "recommended_extraction_use",
        "credibility_level_llm",
        "credibility_rationale",
        "trust_basis",
        "source_independence_group",
        "independence_confidence",
        "likely_syndicated_or_aggregated",
        "aggregation_or_syndication_reason",
    ):
        value = decision.get(key)
        if value not in (None, "", []):
            merged[key] = value
    for key in (
        "publisher_evidence_fields",
        "publisher_evidence_quotes",
        "source_type_evidence",
        "upstream_source_mentions",
        "warnings",
        "errors",
    ):
        merged[key] = _unique(list(merged.get(key) or []) + list(decision.get(key) or []))
    if merged.get("actual_publisher") and not merged.get("actual_publisher_normalized"):
        merged["actual_publisher_normalized"] = _slug(merged.get("actual_publisher"))
    merged["llm_used"] = True
    settings = llm_clients.get_llm_settings()
    merged["llm_provider"] = settings.get("provider")
    merged["llm_model"] = settings.get("model")
    return merged


def _apply_domain_identity_guardrails(assessment: dict, source_entry: dict) -> dict:
    """Keep page publisher identity separate from upstream agencies quoted in text."""

    out = dict(assessment)
    domain = out.get("domain") or _domain(source_entry)
    known_publisher, domain_type = _known_domain_publisher(domain)
    if not domain_type:
        return out
    source_type = _lower(out.get("source_type_final"))
    domain_type_norm = _lower(domain_type)
    official_types = {
        "official_public_health_agency",
        "national_public_health_agency",
        "state_or_local_public_health_agency",
        "international_public_health_agency",
    }
    non_official_domain_types = {
        "news_media",
        "secondary_aggregator",
        "academic_or_peer_reviewed_source",
        "social_media",
        "personal_blog_or_forum",
        "commercial_site",
    }
    if domain_type_norm not in non_official_domain_types:
        return out
    if source_type in official_types or _lower(out.get("actual_publisher")) in {
        "centers for disease control and prevention",
        "virginia department of health",
        "world health organization",
        "pan american health organization",
        "european centre for disease prevention and control",
    }:
        warnings = list(out.get("warnings") or [])
        _add_warning(warnings, "llm_official_identity_conflicts_with_domain")
        _add_warning(warnings, "publisher_from_upstream_quote_not_page_publisher")
        out["warnings"] = _unique(warnings)
        out["source_type_final"] = domain_type
        out["source_type_confidence"] = "high"
        evidence = list(out.get("source_type_evidence") or [])
        evidence.append("domain_guardrail")
        out["source_type_evidence"] = _unique(evidence)
        page_publisher = known_publisher or domain
        out["actual_publisher"] = page_publisher
        out["actual_publisher_normalized"] = _slug(page_publisher)
        out["actual_publisher_confidence"] = "high" if known_publisher else "medium"
        out["publisher_source"] = "domain_guardrail"
        out["source_owner"] = page_publisher
        out["source_owner_confidence"] = out["actual_publisher_confidence"]
        out["source_independence_group"] = (
            f"publisher:{out['actual_publisher_normalized']}"
            if out.get("actual_publisher_normalized")
            else f"domain:{_slug(domain)}"
        )
        role = _role_decision(domain_type, source_entry)
        out.update(role)
        if domain_type_norm in {"news_media", "secondary_aggregator", "social_media"}:
            out["recommended_source_role"] = "needs_human_review"
            out["recommended_extraction_use"] = "needs_human_review"
            out["claim_support_role"] = "corroboration_support"
    return out


def assess_source_identity(
    source_entry: dict,
    collection_spec: dict | None = None,
    llm_decision: dict | None = None,
) -> dict:
    """Assess publisher/source identity for one source entry."""

    assessment = _base_assessment(source_entry, collection_spec)
    assessment = _merge_llm_decision(assessment, llm_decision)
    assessment = _apply_domain_identity_guardrails(assessment, source_entry)
    assessment = _finalize_authority_metadata(
        assessment, source_entry, collection_spec
    )
    return SourceIdentityAssessment(**assessment).model_dump()


def _entry_with_assessment(entry: dict, assessment: dict) -> dict:
    out = dict(entry)
    raw = assessment.get("search_result_source_raw")
    out["search_result_source_raw"] = raw
    out["search_provider_result_source"] = raw
    if raw:
        out["publisher_candidate_from_search_metadata"] = raw
        out.setdefault("result_source", raw)
    for key in (
        "actual_publisher",
        "actual_publisher_normalized",
        "actual_publisher_confidence",
        "publisher_evidence_fields",
        "publisher_evidence_quotes",
        "publisher_source",
        "source_owner",
        "source_owner_confidence",
        "source_type_llm",
        "source_type_final",
        "source_type_confidence",
        "source_type_evidence",
        "source_type_warning_flags",
        "publisher_type",
        "jurisdiction_scope",
        "page_function",
        "primary_vs_secondary",
        "authority_bucket",
        "task_relevance_assessment",
        "disease_relevance_assessment",
        "geography_relevance_assessment",
        "time_relevance_assessment",
        "likely_contains_extractable_data",
        "supports_primary_case_claims",
        "supports_zero_case_claims",
        "supports_exposure_monitoring_claims",
        "supports_context_only",
        "claim_support_role",
        "recommended_source_role",
        "recommended_fetch_use",
        "recommended_extraction_use",
        "credibility_level_llm",
        "credibility_rationale",
        "trust_basis",
        "source_independence_group",
        "independence_confidence",
        "likely_syndicated_or_aggregated",
        "aggregation_or_syndication_reason",
        "upstream_source_mentions",
        "page_title",
        "page_publisher_candidate",
        "page_site_name_candidate",
        "page_author_or_org_candidate",
        "page_identity_excerpt",
        "page_identity_evidence",
        "post_fetch_identity_assessed",
        "post_fetch_identity_confidence",
    ):
        if key in assessment:
            out[key] = assessment.get(key)
    out["publisher_warning_flags"] = list(assessment.get("warnings") or [])
    out["source_identity_method"] = assessment.get("method")
    out["source_identity_status"] = assessment.get("source_identity_status")
    out["source_identity_assessed_at"] = assessment.get("assessed_at")
    out["source_identity_llm_used"] = bool(assessment.get("llm_used"))
    out["source_identity_llm_provider"] = assessment.get("llm_provider")
    out["source_identity_llm_model"] = assessment.get("llm_model")
    out["source_identity_warnings"] = list(assessment.get("warnings") or [])
    out["source_identity_errors"] = list(assessment.get("errors") or [])
    if assessment.get("actual_publisher") and (
        not out.get("publisher") or _raw_is_provider(out.get("publisher"), out.get("search_provider"))
    ):
        out["publisher"] = assessment.get("actual_publisher")
    return apply_source_identity_routing_guardrails(out)


def apply_source_identity_routing_guardrails(entry: dict) -> dict:
    """Conservatively apply source identity recommendations to routing fields."""

    out = dict(entry)
    flags = list(out.get("routing_flags") or [])
    source_type = _lower(out.get("source_type_final"))
    recommended_role = _lower(out.get("recommended_source_role"))
    fetch_use = _lower(out.get("recommended_fetch_use"))
    extraction_use = _lower(out.get("recommended_extraction_use"))
    source_role = _lower(out.get("source_role"))
    source_role_final = _lower(out.get("source_role_final"))
    final_decision = _lower(out.get("final_screening_decision"))
    llm_identity_used = bool(out.get("source_identity_llm_used"))
    critic_blocked = bool(out.get("llm_source_critic_block_fetch")) or (
        "llm_source_critic_block_fetch"
        in _lower(out.get("blocked_from_fetch_reason"))
    )
    must_fetch_target = bool(out.get("must_fetch")) and bool(
        out.get("coverage_requirement_ids")
    )
    validation_reserved_boundary = (
        source_role == "validation_reserved"
        or final_decision == "reserved_for_validation"
        or "validation_reserved" in flags
        or "blocked_from_collection" in flags
    )
    context_only_boundary = source_role == "context_source"
    search_boundary = (
        source_role in {"search_endpoint", "placeholder_source"}
        or source_role_final in {"search_endpoint", "placeholder_source"}
        or final_decision == "defer_to_search_expansion"
        or source_type == "search_endpoint"
    )
    protected_boundary = (
        validation_reserved_boundary or context_only_boundary or search_boundary
    )

    if (
        llm_identity_used
        and recommended_role in _RECOMMENDED_SOURCE_ROLES
        and not critic_blocked
        and not protected_boundary
        and not (must_fetch_target and recommended_role == "excluded")
    ):
        out["source_role_final"] = recommended_role
        if recommended_role in {"collection", "validation", "collection_support"}:
            out["final_screening_decision"] = "include_for_content_fetch"
            out["status"] = "ready_for_content_fetch"
        elif recommended_role == "context":
            out["final_screening_decision"] = "include_for_context_fetch"
            out["status"] = "ready_for_context_fetch"
        elif recommended_role == "needs_human_review":
            out["requires_human_review"] = True
            out["status"] = "needs_human_review"
        elif recommended_role == "excluded":
            out["final_screening_decision"] = "exclude"
            out["ready_for_content_fetch"] = False
            out["blocked_from_fetch"] = True
            out["blocked_from_fetch_reason"] = (
                "source_identity_recommended_excluded"
            )
            _add_warning(flags, "source_identity_recommended_excluded")
    elif llm_identity_used and must_fetch_target and recommended_role == "excluded":
        out["source_role_final"] = "collection"
        out["final_screening_decision"] = "include_for_content_fetch"
        out["ready_for_content_fetch"] = True
        out["blocked_from_fetch"] = False
        out["blocked_from_fetch_reason"] = None
        out["status"] = "ready_for_content_fetch"
        _add_warning(flags, "source_identity_recommended_excluded_for_must_fetch")

    if (
        llm_identity_used
        and
        fetch_use in _FETCHABLE_RECOMMENDATIONS
        and not out.get("blocked_from_fetch")
        and not critic_blocked
        and not protected_boundary
    ):
        out["ready_for_content_fetch"] = True

    if source_type == "search_endpoint" or (
        fetch_use == "do_not_fetch" and not must_fetch_target
    ):
        out["ready_for_content_fetch"] = False
        out["blocked_from_fetch"] = True
        out["blocked_from_fetch_reason"] = (
            "source_identity_recommended_do_not_fetch"
        )
        _add_warning(flags, "source_identity_do_not_fetch")
        out["source_role_final"] = (
            "search_endpoint"
            if source_type == "search_endpoint"
            else out.get("source_role_final")
        )
    elif fetch_use == "do_not_fetch" and must_fetch_target:
        out["ready_for_content_fetch"] = True
        out["blocked_from_fetch"] = False
        out["blocked_from_fetch_reason"] = None
        out["final_screening_decision"] = "include_for_content_fetch"
        out["source_role_final"] = "collection"
        out["status"] = "ready_for_content_fetch"
        _add_warning(flags, "source_identity_do_not_fetch_for_must_fetch")
    if source_type == "social_media":
        out["ready_for_content_fetch"] = False
        out["requires_human_review"] = True
        _add_warning(flags, "source_identity_social_media_requires_review")
        if out.get("source_role_final") == "collection":
            out["source_role_final"] = "needs_human_review"
    if extraction_use == "do_not_extract":
        _add_warning(flags, "source_identity_do_not_extract")
    out["routing_flags"] = _unique(flags)
    return out


def apply_source_identity_to_registry(
    registry: list[dict],
    collection_spec: dict | None = None,
    *,
    llm_enabled: bool = False,
    max_sources: int | None = None,
    require_llm: bool = False,
    allow_deterministic_fallback: bool = True,
) -> tuple[list[dict], list[dict], dict]:
    """Apply source identity assessment to source registry rows."""

    updated: list[dict] = []
    assessments: list[dict] = []
    selected = 0
    collection_mode = _lower((collection_spec or {}).get("collection_mode"))
    direct_identity_fast_path = collection_mode == "direct_collection" and any(
        bool(entry.get("must_fetch")) for entry in registry
    )
    direct_identity_skipped_source_ids: list[str] = []
    for entry in registry:
        llm_decision = None
        should_call_llm = bool(llm_enabled) and (
            max_sources is None or selected < max_sources
        )
        fast_path_skip_reason = None
        if should_call_llm and direct_identity_fast_path:
            should_call_llm = False
            fast_path_skip_reason = (
                "direct_target_official_fast_path_skips_source_identity"
            )
            if entry.get("source_id"):
                direct_identity_skipped_source_ids.append(str(entry.get("source_id")))
        if should_call_llm:
            selected += 1
            try:
                llm_decision = assess_source_identity_with_llm(
                    source_entry=entry,
                    collection_spec=collection_spec,
                    parsed_page_identity=None,
                )
            except Exception as exc:  # noqa: BLE001 - advisory fallback
                if require_llm and not allow_deterministic_fallback:
                    base = _base_assessment(entry, collection_spec)
                    base = _finalize_authority_metadata(
                        base, entry, collection_spec
                    )
                    base["errors"] = _unique(
                        list(base.get("errors") or [])
                        + [f"llm_source_identity_unavailable:{type(exc).__name__}"]
                    )
                    base["warnings"] = _unique(
                        list(base.get("warnings") or [])
                        + ["llm_source_identity_required_but_unavailable"]
                    )
                    base["source_identity_status"] = "blocked_llm_required"
                    assessment = SourceIdentityAssessment(**base).model_dump()
                    assessments.append(assessment)
                    updated.append(_entry_with_assessment(entry, assessment))
                    continue
                llm_decision = {
                    "warnings": [f"llm_source_identity_failed:{type(exc).__name__}"],
                    "errors": [str(exc)],
                }
        assessment = assess_source_identity(
            entry,
            collection_spec=collection_spec,
            llm_decision=llm_decision,
        )
        if fast_path_skip_reason:
            assessment = dict(assessment)
            warnings = list(assessment.get("warnings") or [])
            if fast_path_skip_reason not in warnings:
                warnings.append(fast_path_skip_reason)
            assessment["warnings"] = _unique(warnings)
            assessment["source_identity_llm_skipped_reason"] = fast_path_skip_reason
        assessments.append(assessment)
        updated.append(_entry_with_assessment(entry, assessment))
    summary = build_source_identity_summary(assessments)
    summary.update(
        {
            "direct_identity_fast_path": direct_identity_fast_path,
            "direct_identity_fast_path_skipped_count": len(
                direct_identity_skipped_source_ids
            ),
            "direct_identity_fast_path_skipped_source_ids": (
                direct_identity_skipped_source_ids
            ),
        }
    )
    return updated, assessments, summary


def enrich_source_identity_post_fetch(
    source_entry: dict,
    assessment: dict,
    document: dict,
    llm_decision: dict | None = None,
    collection_spec: dict | None = None,
) -> dict:
    """Enrich one source identity assessment using already fetched document text."""

    enriched = dict(assessment)
    title = _clean(document.get("title")) or _clean(source_entry.get("title"))
    text = _clean(document.get("clean_text"))
    page_publisher, evidence_fields, evidence_quotes = _publisher_from_page(document)
    enriched["page_title"] = title or None
    enriched["page_identity_excerpt"] = text[:600] or None
    enriched["page_identity_evidence"] = _unique(evidence_quotes)
    enriched["page_publisher_candidate"] = page_publisher
    enriched["page_site_name_candidate"] = (
        (document.get("metadata") or {}).get("site_name")
        if isinstance(document.get("metadata"), dict)
        else None
    )
    enriched["post_fetch_identity_assessed"] = True
    enriched["post_fetch_identity_confidence"] = "low"

    warnings = list(enriched.get("warnings") or [])
    raw = _raw_search_source(source_entry)
    provider = _search_provider(source_entry)
    if page_publisher:
        if raw and not _raw_is_provider(raw, provider) and _slug(raw) != _slug(page_publisher):
            _add_warning(warnings, "publisher_conflict_between_search_and_page_metadata")
            enriched["actual_publisher_confidence"] = "medium"
        elif not enriched.get("actual_publisher") or _raw_is_provider(
            enriched.get("actual_publisher"), provider
        ):
            enriched["actual_publisher_confidence"] = "high"
        enriched["actual_publisher"] = page_publisher
        enriched["actual_publisher_normalized"] = _slug(page_publisher)
        enriched["publisher_source"] = "page_metadata_or_text"
        enriched["publisher_evidence_fields"] = _unique(
            list(enriched.get("publisher_evidence_fields") or []) + evidence_fields
        )
        enriched["publisher_evidence_quotes"] = _unique(
            list(enriched.get("publisher_evidence_quotes") or []) + evidence_quotes
        )
        enriched["post_fetch_identity_confidence"] = enriched.get(
            "actual_publisher_confidence"
        ) or "medium"
    if llm_decision:
        enriched = _merge_llm_decision(enriched, llm_decision)
    enriched["warnings"] = _unique(warnings + list(enriched.get("warnings") or []))
    if enriched.get("actual_publisher") and not enriched.get("source_independence_group"):
        enriched["source_independence_group"] = (
            f"publisher:{_slug(enriched.get('actual_publisher'))}"
        )
    enriched = _finalize_authority_metadata(
        enriched, source_entry, collection_spec
    )
    return SourceIdentityAssessment(**enriched).model_dump()


def enrich_source_identity_registry_post_fetch(
    registry: list[dict],
    assessments: list[dict],
    documents: list[dict],
    collection_spec: dict | None = None,
    *,
    llm_enabled: bool = False,
    max_sources: int | None = None,
    require_llm: bool = False,
    allow_deterministic_fallback: bool = True,
) -> tuple[list[dict], list[dict], dict]:
    """Update registry identity from already fetched documents."""

    assessment_by_id = {a.get("source_id"): a for a in assessments}
    doc_by_id = {d.get("source_id"): d for d in documents if d.get("source_id")}
    updated_registry: list[dict] = []
    updated_assessments: list[dict] = []
    selected = 0
    collection_mode = _lower((collection_spec or {}).get("collection_mode"))
    direct_identity_fast_path = collection_mode == "direct_collection" and any(
        bool(entry.get("must_fetch")) or entry.get("coverage_requirement_ids")
        for entry in registry
    )
    direct_identity_skipped_source_ids: list[str] = []
    for entry in registry:
        source_id = entry.get("source_id")
        assessment = assessment_by_id.get(source_id) or assess_source_identity(
            entry, collection_spec=collection_spec
        )
        doc = doc_by_id.get(source_id)
        if doc:
            llm_decision = None
            should_call_llm = bool(llm_enabled) and (
                max_sources is None or selected < max_sources
            )
            fast_path_skip_reason = None
            if should_call_llm and direct_identity_fast_path:
                should_call_llm = False
                fast_path_skip_reason = (
                    "direct_target_official_fast_path_skips_source_identity"
                )
                if source_id:
                    direct_identity_skipped_source_ids.append(str(source_id))
            if should_call_llm:
                selected += 1
                try:
                    llm_decision = assess_source_identity_with_llm(
                        source_entry=entry,
                        collection_spec=collection_spec,
                        parsed_page_identity={
                            "page_title": doc.get("title"),
                            "parse_status": doc.get("parse_status"),
                            "http_status_code": doc.get("http_status_code"),
                            "text_excerpt": _clean(doc.get("clean_text"))[:1200],
                        },
                    )
                except Exception as exc:  # noqa: BLE001 - advisory fallback
                    if require_llm and not allow_deterministic_fallback:
                        assessment = dict(assessment)
                        assessment["errors"] = _unique(
                            list(assessment.get("errors") or [])
                            + [f"llm_source_identity_post_fetch_unavailable:{type(exc).__name__}"]
                        )
                    else:
                        llm_decision = {
                            "warnings": [
                                f"llm_source_identity_post_fetch_failed:{type(exc).__name__}"
                            ],
                            "errors": [str(exc)],
                        }
            assessment = enrich_source_identity_post_fetch(
                entry,
                assessment,
                doc,
                llm_decision=llm_decision,
                collection_spec=collection_spec,
            )
            if fast_path_skip_reason:
                assessment = dict(assessment)
                warnings = list(assessment.get("warnings") or [])
                if fast_path_skip_reason not in warnings:
                    warnings.append(fast_path_skip_reason)
                assessment["warnings"] = _unique(warnings)
                assessment["source_identity_llm_skipped_reason"] = (
                    fast_path_skip_reason
                )
                assessment["llm_used"] = False
                assessment["llm_provider"] = None
                assessment["llm_model"] = None
        updated_assessments.append(assessment)
        updated_registry.append(_entry_with_assessment(entry, assessment))
    summary = build_source_identity_summary(updated_assessments)
    summary.update(
        {
            "direct_identity_fast_path": direct_identity_fast_path,
            "direct_identity_fast_path_skipped_count": len(
                direct_identity_skipped_source_ids
            ),
            "direct_identity_fast_path_skipped_source_ids": (
                direct_identity_skipped_source_ids
            ),
        }
    )
    return (
        updated_registry,
        updated_assessments,
        summary,
    )


def build_source_identity_summary(assessments: list[dict]) -> dict:
    """Summarize source identity assessments."""

    source_type_counter: Counter = Counter()
    claim_role_counter: Counter = Counter()
    fetch_counter: Counter = Counter()
    extraction_counter: Counter = Counter()
    warning_counter: Counter = Counter()
    status_counter: Counter = Counter()
    publisher_counter: Counter = Counter()
    independence_counter: Counter = Counter()
    llm_count = 0
    post_fetch_count = 0
    unknown_publisher_count = 0
    for item in assessments:
        source_type_counter[item.get("source_type_final") or "unknown"] += 1
        claim_role_counter[item.get("claim_support_role") or "unknown"] += 1
        fetch_counter[item.get("recommended_fetch_use") or "unknown"] += 1
        extraction_counter[item.get("recommended_extraction_use") or "unknown"] += 1
        publisher = item.get("actual_publisher") or "unknown"
        publisher_counter[publisher] += 1
        if publisher == "unknown":
            unknown_publisher_count += 1
        group = item.get("source_independence_group") or "unknown"
        independence_counter[group] += 1
        if item.get("llm_used"):
            llm_count += 1
        status_counter[item.get("source_identity_status") or "assessed"] += 1
        if item.get("post_fetch_identity_assessed"):
            post_fetch_count += 1
        for warning in item.get("warnings") or []:
            warning_counter[warning] += 1
    return SourceIdentitySummary(
        identity_assessed_count=len(assessments),
        llm_identity_assessed_count=llm_count,
        post_fetch_identity_assessed_count=post_fetch_count,
        unknown_publisher_count=unknown_publisher_count,
        blocked_llm_required_count=status_counter.get("blocked_llm_required", 0),
        source_type_counts=dict(source_type_counter),
        claim_support_role_counts=dict(claim_role_counter),
        recommended_fetch_use_counts=dict(fetch_counter),
        recommended_extraction_use_counts=dict(extraction_counter),
        warning_counts=dict(warning_counter),
        publisher_counts=dict(publisher_counter),
        independence_group_counts=dict(independence_counter),
    ).model_dump()
