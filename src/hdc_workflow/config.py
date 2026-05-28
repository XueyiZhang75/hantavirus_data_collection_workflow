"""Configuration helpers for the hantavirus data collection workflow."""

from __future__ import annotations

import json
from pathlib import Path

_RESOURCES_DIR = Path(__file__).parent / "resources"
_HANTAVIRUS_PROFILE_PATH = _RESOURCES_DIR / "hantavirus_profile.json"
_HANTAVIRUS_SCHEMA_PATH = _RESOURCES_DIR / "hantavirus_collection_schema.json"
_SOURCE_STRATEGY_PATH = _RESOURCES_DIR / "source_strategy.json"
_HANTAVIRUS_SEED_SOURCES_PATH = _RESOURCES_DIR / "hantavirus_seed_sources.json"
_SOURCE_SCREENING_POLICY_PATH = _RESOURCES_DIR / "source_screening_policy.json"
_CONTENT_FETCH_POLICY_PATH = _RESOURCES_DIR / "content_fetch_policy.json"
_EVIDENCE_CHUNKING_POLICY_PATH = _RESOURCES_DIR / "evidence_chunking_policy.json"
_STRUCTURED_EXTRACTION_POLICY_PATH = _RESOURCES_DIR / "structured_extraction_policy.json"
_RECORD_NORMALIZATION_POLICY_PATH = _RESOURCES_DIR / "record_normalization_policy.json"
_RECORD_LINKING_POLICY_PATH = _RESOURCES_DIR / "record_linking_policy.json"
_CROSS_SOURCE_CONSISTENCY_POLICY_PATH = _RESOURCES_DIR / "cross_source_consistency_policy.json"
_HANTAVIRUS_FIXTURE_DOCUMENTS_PATH = _RESOURCES_DIR / "hantavirus_fixture_documents.json"
_HUMAN_REVIEW_POLICY_PATH = _RESOURCES_DIR / "human_review_policy.json"
_FINAL_PACKAGE_POLICY_PATH = _RESOURCES_DIR / "final_package_policy.json"
_LLM_STRUCTURED_EXTRACTION_POLICY_PATH = _RESOURCES_DIR / "llm_structured_extraction_policy.json"


def _load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_hantavirus_profile() -> dict:
    """Load the static hantavirus disease profile JSON as a dict."""

    return _load_json(_HANTAVIRUS_PROFILE_PATH)


def load_hantavirus_collection_schema() -> dict:
    """Load the hantavirus human case/outbreak collection schema JSON as a dict."""

    return _load_json(_HANTAVIRUS_SCHEMA_PATH)


def load_source_strategy() -> dict:
    """Load the source strategy (categories + screening criteria) JSON as a dict."""

    return _load_json(_SOURCE_STRATEGY_PATH)


def load_hantavirus_seed_sources() -> dict:
    """Load the offline hantavirus seed source catalog JSON as a dict."""

    return _load_json(_HANTAVIRUS_SEED_SOURCES_PATH)


def load_source_screening_policy() -> dict:
    """Load the deterministic source screening policy JSON as a dict."""

    return _load_json(_SOURCE_SCREENING_POLICY_PATH)


def load_content_fetch_policy() -> dict:
    """Load the content fetching / document quality policy JSON as a dict."""

    return _load_json(_CONTENT_FETCH_POLICY_PATH)


def load_evidence_chunking_policy() -> dict:
    """Load the evidence chunking / data presence flagging policy JSON as a dict."""

    return _load_json(_EVIDENCE_CHUNKING_POLICY_PATH)


def load_structured_extraction_policy() -> dict:
    """Load the deterministic structured extraction policy JSON as a dict."""

    return _load_json(_STRUCTURED_EXTRACTION_POLICY_PATH)


def load_record_normalization_policy() -> dict:
    """Load the deterministic record normalization policy JSON as a dict."""

    return _load_json(_RECORD_NORMALIZATION_POLICY_PATH)


def load_record_linking_policy() -> dict:
    """Load the deterministic record linking policy JSON as a dict."""

    return _load_json(_RECORD_LINKING_POLICY_PATH)


def load_cross_source_consistency_policy() -> dict:
    """Load the deterministic cross-source consistency policy JSON as a dict."""

    return _load_json(_CROSS_SOURCE_CONSISTENCY_POLICY_PATH)


def load_hantavirus_fixture_documents() -> dict:
    """Load the synthetic local fixture document catalog JSON as a dict."""

    return _load_json(_HANTAVIRUS_FIXTURE_DOCUMENTS_PATH)


def load_human_review_policy() -> dict:
    """Load the deterministic human review policy JSON as a dict."""

    return _load_json(_HUMAN_REVIEW_POLICY_PATH)


def load_final_package_policy() -> dict:
    """Load the deterministic final package assembly policy JSON as a dict."""

    return _load_json(_FINAL_PACKAGE_POLICY_PATH)


def load_llm_structured_extraction_policy() -> dict:
    """Load the optional LLM-based structured extraction policy JSON as a dict."""

    return _load_json(_LLM_STRUCTURED_EXTRACTION_POLICY_PATH)
