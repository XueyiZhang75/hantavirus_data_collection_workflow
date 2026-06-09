from __future__ import annotations

import csv
import json

from hdc_workflow.export import export_final_data_package
from hdc_workflow.human_review_application import apply_human_review_decisions
from hdc_workflow.nodes.finalization import final_data_package_builder


def _record(record_id: str, **overrides) -> dict:
    source_id = overrides.get("source_id", f"src_{record_id}")
    chunk_id = overrides.get("supporting_chunk_id", f"chunk_{record_id}")
    record = {
        "record_id": record_id,
        "disease": "Hantavirus disease",
        "disease_standard_name": "Hantavirus disease",
        "virus_or_syndrome": "Hantavirus pulmonary syndrome",
        "pathogen_or_syndrome": "hantavirus",
        "country": "United States of America",
        "subnational_location": "New Mexico",
        "date_reported": "2025-03-07",
        "date_anchor": "2025-03-07",
        "reporting_period": "2025",
        "cases_unspecified": 1.0,
        "deaths": 0.0,
        "source_id": source_id,
        "source_url": f"https://example.org/{source_id}",
        "source_title": "Example public health source",
        "source_type": "official_public_health_agency",
        "publisher": "Example Department of Health",
        "source_role_final": "collection",
        "credibility_score": 0.95,
        "credibility_level": "high",
        "discovery_method": "fixture_search_result",
        "search_provider": "fixture",
        "query_id": "q_fixture_001",
        "query_used": "hantavirus New Mexico cases deaths 2025",
        "evidence_quote": (
            "New Mexico reported a hantavirus pulmonary syndrome case in 2025."
        ),
        "supporting_chunk_id": chunk_id,
        "schema_status": "valid",
        "provenance_status": "verified",
        "normalization_status": "normalized",
        "record_schema": "generic_public_health_record",
        "event_cluster_id": "event_001",
        "countable": True,
        "requires_human_review": False,
    }
    record.update(overrides)
    return record


def _source(source_id: str, **overrides) -> dict:
    row = {
        "source_id": source_id,
        "canonical_url": f"https://example.org/{source_id}",
        "title": "Example source",
        "publisher": "Example Department of Health",
        "source_type": "official_public_health_agency",
        "status": "ready_for_content_fetch",
        "source_role_final": "collection",
        "credibility_score": 0.95,
        "credibility_level": "high",
        "final_screening_decision": "include_for_content_fetch",
        "ready_for_content_fetch": True,
        "source_disease_relevance_status": "target_disease_match",
    }
    row.update(overrides)
    return row


def _document(source_id: str, **overrides) -> dict:
    row = {
        "document_id": f"doc_{source_id}",
        "source_id": source_id,
        "url": f"https://example.org/{source_id}",
        "canonical_url": f"https://example.org/{source_id}",
        "title": "Example source",
        "publisher": "Example Department of Health",
        "source_type": "official_public_health_agency",
        "source_role_final": "collection",
        "fetch_purpose": "data_extraction",
        "fetch_status": "fetched",
        "parse_status": "parsed_html",
        "quality_status": "usable",
        "document_disease_relevance_status": "target_disease_match",
        "not_extractable_for_task_disease": False,
        "clean_text": "New Mexico reported a hantavirus pulmonary syndrome case.",
    }
    row.update(overrides)
    return row


def _chunk(chunk_id: str, source_id: str, **overrides) -> dict:
    row = {
        "chunk_id": chunk_id,
        "source_id": source_id,
        "text": "New Mexico reported a hantavirus pulmonary syndrome case.",
        "contains_target_data": True,
        "disease_relevance_status": "target_disease_match",
        "extraction_eligible_for_task_disease": True,
        "source_url": f"https://example.org/{source_id}",
        "source_role_final": "collection",
        "quality_status": "usable",
        "chunk_index": 1,
        "chunk_kind": "text",
    }
    row.update(overrides)
    return row


def _validation_result(record_id: str, **overrides) -> dict:
    row = {
        "validation_result_id": f"val_result_{record_id}",
        "validation_case_id": "val_case_001",
        "validation_type": "scope_check",
        "validation_unit": "record",
        "comparison_id": f"val_cmp_{record_id}",
        "left_record_ids": [record_id],
        "right_record_ids": [],
        "left_event_cluster_ids": ["event_001"],
        "right_event_cluster_ids": [],
        "left_source_ids": [f"src_{record_id}"],
        "right_source_ids": [],
        "left_source_urls": [f"https://example.org/src_{record_id}"],
        "right_source_urls": [],
        "compared_field": "record_scope",
        "disease": "Hantavirus disease",
        "location": "New Mexico",
        "date_or_period": "2025",
        "left_value": "New Mexico / 2025",
        "right_value": "New Mexico / 2025",
        "comparability_status": "comparable",
        "match_status": "matched",
        "validation_status": "validated",
        "confidence": 0.9,
        "reason": "record is within requested task scope",
        "evidence_summary": "scope check",
        "needs_human_review": False,
        "warnings": [],
    }
    row.update(overrides)
    return row


def _anomaly(record_id: str, **overrides) -> dict:
    row = {
        "anomaly_id": f"anom_{record_id}",
        "anomaly_type": "deaths_greater_than_cases",
        "anomaly_unit": "record",
        "severity": "high",
        "record_id": record_id,
        "source_id": f"src_{record_id}",
        "source_ids": [f"src_{record_id}"],
        "source_urls": [f"https://example.org/src_{record_id}"],
        "reason": "deaths exceed available case count for the same record",
        "recommended_action": "review_case_and_death_counts",
        "needs_human_review": True,
        "human_review_reason": "review high-severity anomaly",
    }
    row.update(overrides)
    return row


def _state(records: list[dict] | None = None, **overrides) -> dict:
    records = records if records is not None else [_record("rec_001")]
    source_ids = sorted(
        {
            str(record["source_id"])
            for record in records
            if isinstance(record, dict) and record.get("source_id")
        }
    )
    chunks = [
        _chunk(
            str(record.get("supporting_chunk_id") or f"chunk_{record['record_id']}"),
            str(record["source_id"]),
        )
        for record in records
        if isinstance(record, dict) and record.get("source_id")
    ]
    state = {
        "structured_task": {
            "disease": "hantavirus",
            "location": "New Mexico",
            "start_date": "2024",
            "end_date": "2026",
            "target_fields": ["cases", "deaths", "dates", "locations", "source URLs"],
        },
        "collection_spec": {
            "disease": "hantavirus",
            "geography": "New Mexico",
            "start_date": "2024",
            "end_date": "2026",
            "time_window": "2024 to 2026",
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
        "normalized_records": records,
        "source_registry": [_source(source_id) for source_id in source_ids],
        "documents": [_document(source_id) for source_id in source_ids],
        "evidence_chunks": chunks,
        "linked_events": [],
        "event_clusters": [],
        "duplicate_clusters": [],
        "validation_cases": [],
        "validation_comparisons": [],
        "validation_results": [],
        "conflicts": [],
        "human_review_queue": [],
        "human_review_decisions": [],
        "collection_trace": [],
    }
    state.update(overrides)
    return state


def _finalize(state: dict) -> tuple[dict, dict]:
    result = final_data_package_builder(state)
    return result["final_data_package"], result


def _record_ids(rows: list[dict]) -> set[str]:
    return {str(row.get("record_id")) for row in rows}


def test_clean_record_is_accepted_into_quality_gated_final_dataset():
    package, result = _finalize(_state())

    assert _record_ids(package["final_dataset"]) == {"rec_001"}
    record = package["final_dataset"][0]
    assert record["final_dataset_included"] is True
    assert record["record_final_inclusion_status"] in {"accepted", "accepted_with_warnings"}
    assert package["quarantined_records"] == []
    assert result["run_quality_summary"]["run_quality_status"] in {"passed", "passed_with_review"}


def test_disease_mismatch_record_is_quarantined():
    bad = _record(
        "rec_covid_as_hanta",
        disease="COVID-19",
        disease_standard_name="COVID-19",
        virus_or_syndrome="SARS-CoV-2",
        pathogen_or_syndrome="SARS-CoV-2",
        evidence_quote="Shanghai reported COVID-19 cases and SARS-CoV-2 deaths.",
        record_disease_compatibility_status="incompatible_disease",
        record_disease_compatibility_reject=True,
    )

    package, _ = _finalize(_state([bad]))

    assert package["final_dataset"] == []
    assert _record_ids(package["quarantined_records"]) == {"rec_covid_as_hanta"}
    quarantined = package["quarantined_records"][0]
    assert quarantined["record_final_inclusion_status"] == "quarantined_disease_mismatch"
    assert "disease_pathogen_incompatible_with_task" in quarantined["quality_gate_blocking_flags"]


def test_source_critic_blocked_record_is_quarantined():
    record = _record("rec_blocked")
    state = _state(
        [record],
        source_registry=[
            _source(
                "src_rec_blocked",
                blocked_from_fetch=True,
                blocked_from_fetch_reason="source critic marked not task relevant",
                llm_source_critic_block_fetch=True,
            )
        ],
    )

    package, _ = _finalize(state)

    assert package["final_dataset"] == []
    quarantined = package["quarantined_records"][0]
    assert quarantined["record_final_inclusion_status"] == "quarantined_source_not_task_relevant"
    assert any("source" in reason for reason in quarantined["quality_gate_reasons"])


def test_document_or_chunk_not_task_relevant_record_is_quarantined():
    record = _record("rec_bad_chunk")
    state = _state(
        [record],
        documents=[
            _document(
                "src_rec_bad_chunk",
                quality_status="not_task_relevant",
                document_disease_relevance_status="unrelated_disease",
                not_extractable_for_task_disease=True,
            )
        ],
        evidence_chunks=[
            _chunk(
                "chunk_rec_bad_chunk",
                "src_rec_bad_chunk",
                contains_target_data=False,
                disease_relevance_status="unrelated_disease",
                extraction_eligible_for_task_disease=False,
            )
        ],
    )

    package, _ = _finalize(state)

    assert package["final_dataset"] == []
    quarantined = package["quarantined_records"][0]
    assert quarantined["record_final_inclusion_status"] in {
        "quarantined_document_not_task_relevant",
        "quarantined_chunk_not_task_relevant",
    }
    assert any("task relevant" in reason for reason in quarantined["quality_gate_reasons"])


def test_outside_scope_validation_result_blocks_accepted_final_dataset():
    record = _record("rec_outside")
    validation = _validation_result(
        "rec_outside",
        match_status="outside_requested_scope",
        validation_status="outside_scope",
        reason="record is outside_time_window for requested task",
        warnings=["outside_time_window"],
    )

    package, _ = _finalize(_state([record], validation_results=[validation]))

    assert package["final_dataset"] == []
    assert _record_ids(package["quarantined_records"]) == {"rec_outside"}
    assert package["quarantined_records"][0]["record_final_inclusion_status"] == "quarantined_outside_scope"


def test_trusted_source_validation_conflict_quarantines_record():
    record = _record("rec_conflict")
    validation = _validation_result(
        "rec_conflict",
        validation_type="trusted_source_comparison",
        match_status="conflict",
        validation_status="conflict",
        reason="collection and held-out validation disagree for cases_unspecified",
        warnings=["trusted_source_conflict"],
    )

    package, _ = _finalize(_state([record], validation_results=[validation]))

    assert package["final_dataset"] == []
    assert _record_ids(package["quarantined_records"]) == {"rec_conflict"}
    assert package["quarantined_records"][0]["record_final_inclusion_status"] == "quarantined_validation_conflict"


def test_no_compatible_validation_source_warns_but_does_not_quarantine_clean_record():
    package, result = _finalize(
        _state(
            validation_source_compatibility_summary={
                "compatibility_status": "no_task_compatible_validation_source",
                "warnings": ["no_task_compatible_validation_source"],
            }
        )
    )

    assert _record_ids(package["final_dataset"]) == {"rec_001"}
    assert package["quarantined_records"] == []
    assert result["run_quality_summary"]["validation_limited"] is True
    assert result["run_quality_summary"]["no_compatible_validation_source"] is True
    assert "no_task_compatible_validation_source" in result["run_quality_summary"]["warnings"]
    assert result["run_quality_summary"]["run_quality_status"] != "failed_quality_gate"


def test_high_or_critical_anomaly_quarantines_record():
    record = _record("rec_anom", cases_unspecified=1, deaths=5)

    package, _ = _finalize(_state([record], anomaly_results=[_anomaly("rec_anom")]))

    assert package["final_dataset"] == []
    quarantined = package["quarantined_records"][0]
    assert quarantined["record_final_inclusion_status"] == "quarantined_critical_anomaly"
    assert "deaths_greater_than_cases" in quarantined["quality_gate_blocking_flags"]


def test_human_review_reject_excludes_post_review_dataset_and_preserves_audit():
    state = _state(
        human_review_decisions=[
            {
                "decision_id": "decision_reject_001",
                "review_id": "review_001",
                "decision_type": "reject_record",
                "reviewer_id": "reviewer_test_public_health_001",
                "decided_at": "2026-06-01T00:00:00Z",
                "target_type": "record",
                "target_ids": ["rec_001"],
                "reason": "erroneous record",
                "apply_decision": True,
            }
        ]
    )
    state.update(apply_human_review_decisions(state))

    package, result = _finalize(state)

    assert package["final_dataset"] == []
    assert package["final_dataset_post_review"] == []
    assert _record_ids(package["records_excluded_by_human_review"]) == {"rec_001"}
    assert result["human_review_audit_trail"]


def test_post_review_dataset_matches_quality_gated_final_dataset_without_decisions():
    clean = _record("rec_clean")
    bad = _record(
        "rec_bad",
        disease="COVID-19",
        virus_or_syndrome="SARS-CoV-2",
        evidence_quote="COVID-19 evidence",
        record_disease_compatibility_reject=True,
    )

    package, _ = _finalize(_state([clean, bad]))

    assert _record_ids(package["final_dataset"]) == {"rec_clean"}
    assert _record_ids(package["final_dataset_post_review"]) == {"rec_clean"}
    assert _record_ids(package["final_dataset_pre_quality_gate"]) == {"rec_clean", "rec_bad"}


def test_shanghai_failure_style_wrong_disease_records_do_not_look_successful():
    bad = _record(
        "rec_shanghai_covid",
        disease="COVID-19",
        disease_standard_name="COVID-19",
        virus_or_syndrome="SARS-CoV-2",
        pathogen_or_syndrome="SARS-CoV-2",
        country="China",
        subnational_location="Shanghai",
        date_reported="2024-04-01",
        reporting_period="2024",
        query_used="hantavirus Shanghai 2024",
        evidence_quote="Shanghai reported COVID-19 and SARS-CoV-2 case counts.",
    )
    state = _state(
        [bad],
        structured_task={
            "disease": "hantavirus",
            "location": "Shanghai",
            "start_date": "2024",
            "end_date": "2026",
        },
        collection_spec={
            "disease": "hantavirus",
            "geography": "Shanghai",
            "time_window": "2024 to 2026",
        },
        validation_source_compatibility_summary={
            "compatibility_status": "incompatible_validation_source_disabled",
            "warnings": ["no_task_compatible_validation_source"],
        },
    )

    package, result = _finalize(state)

    assert package["final_dataset"] == []
    assert _record_ids(package["quarantined_records"]) == {"rec_shanghai_covid"}
    assert result["run_quality_summary"]["run_quality_status"] in {
        "failed_quality_gate",
        "no_task_relevant_records",
    }
    assert all(
        "SARS-CoV-2" not in json.dumps(record, ensure_ascii=False)
        for record in package["final_dataset"]
    )


def test_no_records_extracted_gets_explicit_run_quality_status():
    package, result = _finalize(
        _state(
            [],
            disease_relevance_summary={
                "target_data_chunk_count": 0,
                "chunk_status_counts": {"unrelated_disease": 2},
            },
        )
    )

    assert package["final_dataset"] == []
    assert result["run_quality_summary"]["run_quality_status"] in {
        "no_records_extracted",
        "no_task_relevant_records",
    }
    assert result["run_quality_summary"]["recommended_user_message"]


def test_final_package_and_export_include_all_quality_dataset_views(tmp_path):
    clean = _record("rec_clean")
    bad = _record(
        "rec_bad",
        disease="COVID-19",
        virus_or_syndrome="SARS-CoV-2",
        evidence_quote="COVID-19 evidence",
        record_disease_compatibility_reject=True,
    )
    package, _ = _finalize(_state([clean, bad]))

    for key in (
        "final_dataset",
        "final_dataset_pre_quality_gate",
        "quarantined_records",
        "pending_review_records",
        "record_inclusion_decisions",
        "run_quality_summary",
        "final_dataset_quality_summary",
    ):
        assert key in package
    assert "run_quality_summary" in package["workflow_summaries"]
    assert "final_dataset_quality_summary" in package["workflow_summaries"]

    manifest = export_final_data_package(package, tmp_path)
    expected_files = {
        "final_dataset_json": "final_dataset.json",
        "final_dataset_pre_quality_gate_json": "final_dataset_pre_quality_gate.json",
        "final_dataset_pre_quality_gate_csv": "final_dataset_pre_quality_gate.csv",
        "quarantined_records_json": "quarantined_records.json",
        "quarantined_records_csv": "quarantined_records.csv",
        "pending_review_records_json": "pending_review_records.json",
        "pending_review_records_csv": "pending_review_records.csv",
        "record_inclusion_decisions_json": "record_inclusion_decisions.json",
    }
    for manifest_key, filename in expected_files.items():
        assert manifest_key in manifest["files"]
        assert (tmp_path / filename).exists()

    with (tmp_path / "final_dataset.csv").open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    assert [row["record_id"] for row in rows] == ["rec_clean"]


def test_clean_covid_dengue_and_hantavirus_records_remain_accepted():
    cases = [
        (
            "COVID-19",
            "New York",
            _record(
                "rec_covid",
                disease="COVID-19",
                disease_standard_name="COVID-19",
                virus_or_syndrome="SARS-CoV-2",
                pathogen_or_syndrome="SARS-CoV-2",
                subnational_location="New York",
                evidence_quote="New York reported COVID-19 cases in 2024.",
            ),
        ),
        (
            "dengue",
            "Florida",
            _record(
                "rec_dengue",
                disease="Dengue",
                disease_standard_name="Dengue",
                virus_or_syndrome="DENV",
                pathogen_or_syndrome="dengue virus",
                subnational_location="Florida",
                evidence_quote="Florida reported dengue cases in 2025.",
            ),
        ),
        ("hantavirus", "New Mexico", _record("rec_hanta")),
    ]

    for disease, location, record in cases:
        package, _ = _finalize(
            _state(
                [record],
                structured_task={
                    "disease": disease,
                    "location": location,
                    "start_date": "2024",
                    "end_date": "2026",
                },
                collection_spec={
                    "disease": disease,
                    "geography": location,
                    "time_window": "2024 to 2026",
                },
            )
        )
        assert _record_ids(package["final_dataset"]) == {record["record_id"]}
        assert package["quarantined_records"] == []
