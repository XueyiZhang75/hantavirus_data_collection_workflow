# Masked Validation Design Spec

## 1. Purpose

This design adds a source-masked validation protocol on top of the existing LangGraph backbone. It is not a rewrite of the workflow. The current graph already supports source discovery, source registry construction, screening, content processing, extraction, normalization, linking, consistency checking, human review packaging, and final package export.

The masked validation protocol adds a conservative validation boundary:

- The collection phase must not use held-out validation sources.
- The validation phase may use held-out sources separately for ground-truth comparison.
- Every extracted number must preserve source, evidence, and provenance fields.
- Mismatches, cross-source conflicts, low-confidence records, and single-source findings should be routed or flagged for human review.

The first implementation should be narrow, deterministic, and auditable. It should prove that the system can keep validation evidence out of collection while still preserving enough source metadata to explain the decision.

## 2. Relation to Existing Workflow

Current graph nodes:

1. `task_intake_and_scope_planning`
2. `hantavirus_profile_and_schema_setup`
3. `query_strategy_builder`
4. `source_discovery`
5. `source_dedup_and_registry`
6. `source_screening`
7. `source_critic_and_uncertainty_routing`
8. `content_fetch_and_parse`
9. `document_quality_check`
10. `evidence_chunking_and_data_presence_flagging`
11. `structured_extraction`
12. `schema_validation_and_repair`
13. `record_normalization`
14. `record_linking`
15. `cross_source_consistency_check`
16. `quality_gate_routing`
17. `human_review`
18. `final_data_package_builder`

Source masking does not require graph topology changes for the first narrowed workflow profile. It can be expressed as source registry state and enforced before collection documents are fetched.

Required behavior:

- `source_discovery` can still discover and register all seed sources.
- `source_screening` or `source_critic_and_uncertainty_routing` marks validation-held-out sources as `validation_reserved`.
- `content_fetch_and_parse` enforces the collection blocking rule.
- The final package and evaluation report show which sources were masked and how validation results compared with collection output.
- Downstream extraction, normalization, linking, and consistency nodes do not need to know how a source was masked. They should consume only the allowed collection documents.

## 3. Source Role Definitions

| Source role | Collection fetch? | Validation phase? | Keep in `source_registry`? | Professor-facing report? |
|---|---:|---:|---:|---:|
| `collection_allowed` | Yes | Optional, only if not held out | Yes | Yes |
| `validation_reserved` | No | Yes, separately | Yes | Yes |
| `context_only` | Yes, as context only | Optional | Yes | Yes, if relevant |
| `deferred` | No | No, unless a later connector expands it | Yes | Yes, as deferred |
| `rejected` | No | No | Yes | Optional, usually summary only |

Role details:

- `collection_allowed`: source may be fetched and used for collection extraction.
- `validation_reserved`: source is known to the system but blocked from collection; it may be used only in the validation phase.
- `context_only`: source may provide disease definitions, terminology, or interpretation context, but should not create case-count records unless explicitly reclassified.
- `deferred`: source cannot be used yet, usually because it is a search endpoint, placeholder URI, or future connector target.
- `rejected`: source is outside scope or fails screening criteria.

## 4. Initial Reserved Source Set

The first version uses a fixed held-out set:

`validation_reserved_source_ids`:

- `src_cdc_reported_cases`
- `src_ecdc_surveillance_updates`
- `src_ecdc_annual_report_2023`
- `src_who_hantavirus_fact_sheet`

`validation_reserved_domains`:

- `cdc.gov`
- `ecdc.europa.eu`
- `who.int`

During the collection phase, these sources must not be fetched, chunked, or used for extraction. They should remain visible in `source_registry` with a blocked status. During the validation phase, they may be fetched or loaded separately and used as held-out comparison evidence.

The initial narrowed workflow profile should prefer `source_id` matching over domain matching to avoid accidentally blocking every official source when the experiment only intends to reserve a small named subset. Domain matching can be enabled in a later stricter mode.

## 5. Proposed `source_role_policy.json` Schema

Future file path:

`src/hdc_workflow/resources/source_role_policy.json`

Example:

```json
{
  "policy_name": "hantavirus_source_role_policy",
  "policy_version": "0.1",
  "description": "Policy for assigning source roles for standard and masked-validation collection modes.",
  "default_collection_mode": "standard",
  "supported_collection_modes": [
    "standard",
    "masked_validation"
  ],
  "enabled_env_var": "HDC_COLLECTION_MODE",
  "validation_reserved_source_ids": [
    "src_cdc_reported_cases",
    "src_ecdc_surveillance_updates",
    "src_ecdc_annual_report_2023",
    "src_who_hantavirus_fact_sheet"
  ],
  "validation_reserved_domains": [
    "cdc.gov",
    "ecdc.europa.eu",
    "who.int"
  ],
  "source_role_rules": [
    {
      "rule_id": "explicit_validation_source_id",
      "applies_when": "collection_mode == masked_validation",
      "match_field": "source_id",
      "match_values_from": "validation_reserved_source_ids",
      "assigned_source_role": "validation_reserved",
      "reason": "Held out for masked validation ground-truth comparison."
    },
    {
      "rule_id": "optional_validation_domain",
      "applies_when": "collection_mode == masked_validation and domain_masking_enabled == true",
      "match_field": "canonical_url_domain",
      "match_values_from": "validation_reserved_domains",
      "assigned_source_role": "validation_reserved",
      "reason": "Domain held out for masked validation ground-truth comparison."
    },
    {
      "rule_id": "context_source_passthrough",
      "applies_when": "source_role == context_source and not validation_reserved",
      "assigned_source_role": "context_only",
      "reason": "Context source may be fetched for grounding but not treated as a validation source."
    },
    {
      "rule_id": "deferred_source_passthrough",
      "applies_when": "final_screening_decision == defer_to_search_expansion",
      "assigned_source_role": "deferred",
      "reason": "Search endpoints and connector placeholders are deferred."
    }
  ],
  "collection_blocking_behavior": {
    "preserve_in_registry": true,
    "set_ready_for_content_fetch": false,
    "final_screening_decision": "reserved_for_validation",
    "status": "reserved_for_validation",
    "routing_flags": [
      "validation_reserved",
      "blocked_from_collection"
    ]
  },
  "validation_phase_behavior": {
    "allow_separate_validation_fetch": true,
    "do_not_mix_validation_records_into_collection_dataset": true,
    "validation_output_section": "validation"
  },
  "reporting_behavior": {
    "include_reserved_sources_in_source_registry": true,
    "include_masking_summary_in_final_package": true,
    "include_masking_compliance_status_in_evaluation": true
  }
}
```

## 6. Registry Representation

The first version should not require new Pydantic model fields. It can reuse existing registry fields:

- `source_role`
- `final_screening_decision`
- `ready_for_content_fetch`
- `requires_human_review`
- `routing_flags`
- `status`
- `notes`

Expected registry entry shape:

```json
{
  "source_id": "src_cdc_reported_cases",
  "source_role": "validation_reserved",
  "final_screening_decision": "reserved_for_validation",
  "ready_for_content_fetch": false,
  "requires_human_review": false,
  "routing_flags": [
    "validation_reserved",
    "blocked_from_collection"
  ],
  "masking_reason": "Held out for masked validation ground-truth comparison."
}
```

Current `SourceRegistryEntry` does not include `masking_reason`. A later schema revision can either skip this field, store the reason in `routing_flags` / `notes`, or add a new optional model field if a cleaner schema is worth the small migration.

## 7. Node-Level Implementation Plan

No code is implemented in this document. This is the proposed next change set.

### 7.1 `config.py`

- Add `_SOURCE_ROLE_POLICY_PATH = _RESOURCES_DIR / "source_role_policy.json"`.
- Add `load_source_role_policy() -> dict`.
- Add a Pydantic model only if the policy needs strict validation in tests.
- Read only resource files and environment variable names; never read or print secrets.
- Default to `standard` mode unless an explicit env var such as `HDC_COLLECTION_MODE=masked_validation` enables masking.

### 7.2 `source_screening.py`

- Load the source role policy after normal screening and critic decisions.
- Classify validation-reserved sources by `source_id` first, then optionally by domain.
- Preserve reserved sources in the registry.
- Set `source_role="validation_reserved"` for the collection run.
- Set `ready_for_content_fetch=false`.
- Set `final_screening_decision="reserved_for_validation"` or add a compatible blocked decision.
- Add routing flags such as `validation_reserved` and `blocked_from_collection`.
- Avoid routing these sources to human review unless there is a separate screening problem.

### 7.3 `content_processing.py`

- Enforce the blocking rule before building fetch requests.
- Skip fetch for `validation_reserved` sources during collection phase.
- Count skipped reserved sources separately, for example `skipped_validation_reserved_count`.
- Emit a trace message or summary field explaining that reserved sources were skipped by masking policy.
- Keep offline behavior unchanged for standard mode.

### 7.4 `scripts/run_hdc_workflow_configured.py`

- Use the unified workflow runner rather than a separate presentation-specific branch.
- Set `HDC_COLLECTION_MODE=masked_validation`.
- Run the collection phase with validation-reserved sources excluded from fetch/extraction.
- Run a validation phase that reads either a separate ground truth artifact or separately fetched validation sources.
- Export to `outputs/workflow_runs/<run_profile>/`.
- Keep local test mode deterministic by default; live fetch and LLM calls should require explicit operator confirmation.

### 7.5 `evaluation_report_builder.py`

- Read exported collection artifacts.
- Read `ground_truth_records.csv` or validation artifacts.
- Compare collection records against validation records by stable event fields.
- Produce:
  - `evaluation_report.csv`
  - `evaluation_summary.json`
  - `readable_evaluation_report.md`
- Keep the report conservative: mark uncertain rows for human review rather than claiming automatic correctness.

### 7.6 Tests

- Policy loader test for `source_role_policy.json`.
- Source screening test that reserved sources receive blocked collection status.
- Content fetch test that reserved sources are skipped during collection.
- Fixture masked run test proving no collection records come from reserved source IDs.
- Evaluation report builder smoke test with a small ground truth fixture.

## 8. Masked Validation Outputs

Expected output structure:

```text
outputs/workflow_runs/<run_profile>/
  collection/
    final_package.json
    final_dataset.csv
    source_registry.json
    linked_events.json
    conflicts.json
    human_review_items.json
    provenance_manifest.json
  validation/
    ground_truth_records.csv
    validation_source_registry.json
  evaluation/
    evaluation_report.csv
    evaluation_summary.json
    readable_evaluation_report.md
```

`collection/` is the masked collection output. `validation/` is held-out evidence and normalized ground truth. `evaluation/` is the comparison layer.

## 9. Evaluation Report Schema

Required `evaluation_report.csv` columns:

- `evaluation_row_id`
- `linked_event_id`
- `disease`
- `virus_or_syndrome`
- `country`
- `subnational_location`
- `date_start`
- `date_end`
- `reporting_period`
- `statistical_count_type`
- `collection_case_count`
- `collection_death_count`
- `collection_source_ids`
- `collection_source_urls`
- `collection_evidence_quotes`
- `validation_source_ids`
- `validation_source_urls`
- `validation_case_count`
- `validation_death_count`
- `validation_evidence_quotes`
- `case_count_difference`
- `death_count_difference`
- `field_level_match_status`
- `overall_match_status`
- `masking_compliance_status`
- `provenance_completeness_status`
- `human_review_flag`
- `review_reason`

Recommended status values:

- `field_level_match_status`: `match`, `mismatch`, `missing_collection_value`, `missing_validation_value`, `not_comparable`
- `overall_match_status`: `match`, `partial_match`, `mismatch`, `insufficient_evidence`, `not_comparable`
- `masking_compliance_status`: `passed`, `failed_validation_source_in_collection`, `not_checked`
- `provenance_completeness_status`: `complete`, `partial`, `missing`

## 10. Success Criteria for Masked Validation Workflow Runs

Version 0 success criteria:

- No `validation_reserved` source appears in collection `final_dataset`.
- Validation-reserved sources are preserved in `source_registry` with blocked status.
- Collection records retain `source_url`, `evidence_quote`, `supporting_chunk_id`, and `linked_event_id`.
- `evaluation_report.csv` is generated.
- `readable_evaluation_report.md` is generated.
- Mismatch, conflict, and single-source rows flag human review where appropriate.
- Deterministic local masking test passes without LLM or internet.
- Live masked workflow runs require explicit operator confirmation.

## 11. Current Non-Goals

The current narrowed workflow profile does not implement:

- Broad real web search.
- Full automated CDC/ECDC/WHO ground truth scraping.
- Dashboard UI.
- Human decision application back into records.
- Conflict resolution.
- Credibility scoring.
- PDF parsing or OCR.
- Full disease-generalization beyond hantavirus.

## 12. Risks and Mitigations

| Risk | Description | Mitigation |
|---|---|---|
| Leakage risk | Validation sources accidentally enter collection fetch or extraction. | Enforce masking in both source routing and content fetch; add tests that fail if reserved source IDs appear in collection records. |
| Semantic mismatch risk | Cumulative, annual, newly reported, and subset counts may be compared incorrectly. | Preserve and compare `statistical_count_type`, `reporting_period`, `as_of_date`, and `geographic_scope_type`; mark non-comparable rows for review. |
| LLM extraction risk | Optional LLM extraction may hallucinate or normalize fields inconsistently. | Keep deterministic fixture tests as baseline; use structured output; preserve evidence quotes; route low-confidence and malformed records to review. |
| Sparse non-official source risk | With CDC/ECDC/WHO held out, collection may have too few non-official records. | Start with fixture masking; add controlled non-held-out sources later; report sparse coverage honestly instead of overclaiming. |
| Overclaiming evaluation risk | A narrowed comparison could be mistaken for full epidemiological validation. | Label outputs as workflow evaluation results; distinguish local tests, live workflow runs, and full benchmarks; include limitations in human-readable reports. |
