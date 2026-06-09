from __future__ import annotations

import json
from pathlib import Path

from hdc_workflow.disease_relevance import (
    assess_record_disease_compatibility,
    assess_source_disease_relevance,
    build_disease_relevance_context,
)
from hdc_workflow.nodes.content_processing import (
    document_quality_check,
    evidence_chunking_and_data_presence_flagging,
)
from hdc_workflow.nodes.extraction import (
    schema_validation_and_repair,
    structured_extraction,
)
from hdc_workflow.nodes.finalization import final_data_package_builder
from hdc_workflow.nodes.normalization import record_normalization


def _hantavirus_state(**overrides) -> dict:
    state = {
        "structured_task": {
            "disease": "hantavirus",
            "location": "Shanghai",
            "start_date": "2024-01-01",
            "end_date": "2026-06-09",
        },
        "collection_spec": {
            "disease": "hantavirus",
            "geography": "Shanghai",
            "time_window": "2024-01-01 to 2026-06-09",
            "target_population": "human",
        },
        "disease_intelligence": {
            "disease_input": "hantavirus",
            "disease_standard_name": "Hantavirus disease",
            "aliases": ["hantavirus", "hantavirus disease"],
            "abbreviations": ["HPS", "HFRS"],
            "pathogen_terms": ["hantavirus", "orthohantavirus"],
            "syndrome_terms": [
                "hantavirus pulmonary syndrome",
                "hemorrhagic fever with renal syndrome",
            ],
        },
        "collection_trace": [],
        "human_review_queue": [],
    }
    state.update(overrides)
    return state


def _covid_source() -> dict:
    return {
        "source_id": "src_yahoo_covid_shanghai",
        "canonical_url": "https://finance.yahoo.com/news/explainer-shanghai-death-numbers-raise-063847555.html",
        "url": "https://finance.yahoo.com/news/explainer-shanghai-death-numbers-raise-063847555.html",
        "title": "EXPLAINER-Shanghai death numbers raise questions over its COVID accounting",
        "publisher": "Yahoo Finance",
        "source_type": "news_and_situation_report",
        "snippet": "Shanghai reported COVID-19 deaths and confirmed infections.",
        "query_used": '"HFRS Shanghai" cases deaths public health shanghai 2024',
        "status": "candidate",
    }


def _covid_chunk(**overrides) -> dict:
    chunk = {
        "chunk_id": "chunk_src_yahoo_covid_shanghai_001",
        "source_id": "src_yahoo_covid_shanghai",
        "text": (
            "Shanghai had reported no COVID-19 deaths for more than a month. "
            "The city has now reported 285 COVID-related fatalities from "
            "around 500,000 confirmed cases."
        ),
        "contains_target_data": True,
        "data_types": ["case_count", "death_count", "location"],
        "context_types": [],
        "confidence": 0.95,
        "document_type": "html",
        "fetch_purpose": "data_extraction",
        "source_url": "https://finance.yahoo.com/news/explainer-shanghai-death-numbers-raise-063847555.html",
        "canonical_url": "https://finance.yahoo.com/news/explainer-shanghai-death-numbers-raise-063847555.html",
        "title": "EXPLAINER-Shanghai death numbers raise questions over its COVID accounting",
        "publisher": "Yahoo Finance",
        "source_type": "news_and_situation_report",
        "source_role": "data_source",
        "source_role_final": "collection",
        "quality_status": "usable",
        "chunk_index": 1,
        "chunk_kind": "text",
    }
    chunk.update(overrides)
    return chunk


def test_source_relevance_ignores_query_used_as_disease_proof():
    context = build_disease_relevance_context(_hantavirus_state())
    assessment = assess_source_disease_relevance(_covid_source(), context)

    assert assessment["status"] == "unrelated_disease"
    assert "COVID-19" in assessment["incompatible_disease_terms_found"]
    assert "query_used" not in " ".join(assessment["evidence_fields_used"])


def test_document_quality_marks_unrelated_covid_document_not_task_relevant():
    result = document_quality_check(
        _hantavirus_state(
            documents=[
                {
                    "source_id": "src_yahoo_covid_shanghai",
                    "document_type": "html",
                    "clean_text": _covid_chunk()["text"] * 5,
                    "tables": [],
                    "metadata": {},
                    "parse_status": "parsed_html",
                    "quality_status": None,
                    "quality_issues": [],
                    "url": _covid_source()["url"],
                    "canonical_url": _covid_source()["canonical_url"],
                    "title": _covid_source()["title"],
                    "publisher": "Yahoo Finance",
                    "source_type": "news_and_situation_report",
                    "source_role": "data_source",
                    "fetch_purpose": "data_extraction",
                    "is_live_fetched": True,
                    "is_offline_stub": False,
                }
            ]
        )
    )

    doc = result["documents"][0]
    assert doc["quality_status"] == "not_task_relevant"
    assert doc["not_extractable_for_task_disease"] is True
    assert doc["document_disease_relevance_status"] == "unrelated_disease"
    assert result["document_quality_summary"]["disease_relevance_status_counts"][
        "unrelated_disease"
    ] == 1


def test_chunking_suppresses_unrelated_covid_data_for_hantavirus_task():
    result = evidence_chunking_and_data_presence_flagging(
        _hantavirus_state(
            documents=[
                {
                    "source_id": "src_yahoo_covid_shanghai",
                    "document_type": "html",
                    "clean_text": _covid_chunk()["text"] * 4,
                    "tables": [],
                    "metadata": {},
                    "parse_status": "parsed_html",
                    "quality_status": "usable",
                    "quality_issues": [],
                    "url": _covid_source()["url"],
                    "canonical_url": _covid_source()["canonical_url"],
                    "title": _covid_source()["title"],
                    "publisher": "Yahoo Finance",
                    "source_type": "news_and_situation_report",
                    "source_role": "data_source",
                    "fetch_purpose": "data_extraction",
                    "is_live_fetched": True,
                    "is_offline_stub": False,
                }
            ]
        )
    )

    chunks = result["evidence_chunks"]
    assert chunks
    assert all(chunk["contains_target_data"] is False for chunk in chunks)
    assert all(
        chunk["disease_relevance_status"] == "unrelated_disease"
        for chunk in chunks
    )
    assert result["data_presence_summary"]["target_data_chunk_count"] == 0
    assert result["data_presence_summary"]["disease_mismatch_chunk_count"] >= 1


def test_structured_extraction_skips_disease_mismatch_chunk_even_if_marked_target():
    result = structured_extraction(
        _hantavirus_state(evidence_chunks=[_covid_chunk()])
    )

    assert result["raw_records"] == []
    summary = result["structured_extraction_summary"]
    assert summary["raw_record_count"] == 0
    assert summary["skipped_disease_mismatch_chunk_count"] == 1
    assert "src_yahoo_covid_shanghai" in summary["skipped_disease_mismatch_source_ids"]


def test_schema_validation_rejects_llm_record_from_incompatible_covid_evidence():
    raw_record = {
        "record_id": "rec_bad_covid_as_hantavirus",
        "disease": "Hantavirus disease",
        "disease_standard_name": "Hantavirus disease",
        "virus_or_syndrome": "SARS-CoV-2",
        "pathogen_or_syndrome": "SARS-CoV-2",
        "country": "China",
        "subnational_location": "Shanghai",
        "date_reported": "2022-04-28",
        "cases_confirmed": 500000,
        "deaths": 285,
        "source_id": "src_yahoo_covid_shanghai",
        "source_url": _covid_source()["url"],
        "source_type": "news_and_situation_report",
        "evidence_quote": _covid_chunk()["text"],
        "supporting_chunk_id": "chunk_src_yahoo_covid_shanghai_001",
        "extraction_confidence": 0.9,
        "extraction_method": "llm_structured_output_extractor",
    }

    result = schema_validation_and_repair(
        _hantavirus_state(raw_records=[raw_record])
    )

    assert result["validated_records"] == []
    assert len(result["rejected_records"]) == 1
    rejected = result["rejected_records"][0]
    assert rejected["schema_status"] == "rejected"
    assert rejected["record_disease_compatibility_status"] == "incompatible_disease"
    assert "disease_mismatch" in rejected["validation_errors"]


def test_normalization_quarantines_incompatible_validated_record():
    validated_record = {
        "record_id": "rec_bad_covid_validated",
        "disease": "Hantavirus disease",
        "disease_standard_name": "Hantavirus disease",
        "virus_or_syndrome": "SARS-CoV-2",
        "pathogen_or_syndrome": "SARS-CoV-2",
        "country": "China",
        "subnational_location": "Shanghai",
        "date_reported": "2022-04-28",
        "cases_confirmed": 500000,
        "deaths": 285,
        "source_id": "src_yahoo_covid_shanghai",
        "source_url": _covid_source()["url"],
        "source_type": "news_and_situation_report",
        "evidence_quote": _covid_chunk()["text"],
        "supporting_chunk_id": "chunk_src_yahoo_covid_shanghai_001",
        "schema_status": "valid",
        "provenance_status": "verified",
        "extraction_confidence": 0.9,
    }

    result = record_normalization(
        _hantavirus_state(validated_records=[validated_record])
    )

    assert result["normalized_records"] == []
    summary = result["record_normalization_summary"]
    assert summary["disease_mismatch_quarantined_record_count"] == 1
    assert len(result["disease_mismatch_records"]) == 1


def test_record_compatibility_accepts_target_hantavirus_evidence():
    context = build_disease_relevance_context(_hantavirus_state())
    assessment = assess_record_disease_compatibility(
        {
            "disease": "Hantavirus disease",
            "virus_or_syndrome": "HFRS",
            "evidence_quote": (
                "Shanghai reported one HFRS case caused by hantavirus in 2025."
            ),
        },
        context,
    )

    assert assessment["status"] == "compatible"
    assert assessment["target_disease_terms_found"]


def test_llm_extraction_policy_requires_task_disease_match():
    policy = json.loads(
        Path("src/hdc_workflow/resources/llm_structured_extraction_policy.json").read_text(
            encoding="utf-8"
        )
    )
    text = policy["system_prompt"] + " ".join(policy["required_output_rules"])

    assert "target task disease" in text
    assert "incompatible disease" in text


def test_final_package_includes_disease_relevance_summary():
    result = final_data_package_builder(
        _hantavirus_state(
            normalized_records=[],
            source_registry=[],
            linked_events=[],
            event_clusters=[],
            duplicate_clusters=[],
            validation_cases=[],
            validation_comparisons=[],
            validation_results=[],
            anomaly_results=[],
            conflicts=[],
            disease_relevance_summary={
                "target_disease": "Hantavirus disease",
                "rejected_incompatible_record_count": 1,
            },
        )
    )

    package = result["final_data_package"]
    summaries = package["workflow_summaries"]
    assert summaries["disease_relevance_summary"]["target_disease"] == (
        "Hantavirus disease"
    )
