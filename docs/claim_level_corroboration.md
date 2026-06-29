# Claim-Level Cross-Source Corroboration

## 1. Purpose

This optimization upgrades validation in the data collection workflow from a mostly held-out source comparison into claim-level cross-source corroboration across all collected evidence. The workflow now turns extracted records into explicit public-health claims, compares those claims across sources, and exports corroborated events, conflicting claims, and unverified claims.

Corroboration means evidence support. It does not mean automatic truth determination.

## 2. Why This Was Needed

The Hantavirus / Virginia live run exposed two weak accepted observations:

- A Virginia Department of Health page described exposed people completing public-health monitoring and remaining healthy. That is exposure monitoring, not a confirmed hantavirus case.
- A secondary source stated that no confirmed Virginia cases had been reported. That is a zero-case statement, not confirmed surveillance evidence for a case.

The workflow needed a way to ask whether multiple sources support the same disease, location, time, count, and evidence claim. Source role is still useful as a trust hint, but it is not enough as a rigid collection-versus-validation split.

## 3. Claims

Each normalized record can produce one or more `PublicHealthClaim` entries. A record with separate case, death, or hospitalization counts can produce separate claims while keeping the same `source_record_id`.

Important claim fields include:

- Identity: `claim_id`, `source_record_id`, `event_cluster_id`, `linked_event_id`, `claim_type`
- Disease and geography: `disease`, `disease_standard_name`, `pathogen_or_syndrome`, `country`, `subnational_location`, `locality`, `geographic_scope`
- Time: `date_or_period`, `date_reported`, `event_start_date`, `event_end_date`, `reporting_period`, `as_of_date`
- Counts: `count_field`, `count_value`, case/death/hospitalization fields, `statistical_count_type`, `count_semantics`, `count_unit`
- Semantics: `observation_type`, `is_case_claim`, `is_death_claim`, `is_zero_case_statement`, `is_exposure_monitoring_claim`, `is_background_context_claim`, `primary_case_dataset_eligible`
- Provenance: `source_id`, `source_url`, `source_title`, `publisher`, `source_type`, `source_role_final`, `document_id`, `supporting_chunk_id`, `evidence_quote`, `evidence_context`
- Status: `claim_status`, `confidence`, `warnings`, `requires_human_review`, `human_review_reason`

The minimum observation types are:

- `confirmed_case_record`
- `probable_case_record`
- `suspected_case_record`
- `unspecified_case_record`
- `death_record`
- `hospitalization_record`
- `zero_case_statement`
- `exposure_monitoring_record`
- `surveillance_summary`
- `outbreak_summary`
- `background_context`
- `non_task_record`
- `ambiguous_public_health_observation`

## 4. Claim Comparisons

The comparison engine compares active or pending claims across these dimensions:

- Disease compatibility
- Geography compatibility, including explicit national-to-local support
- Time or period compatibility
- Observation type compatibility
- Count field and count semantics compatibility
- Count value match, minor numeric difference, conflict, or insufficient information
- Source independence

Comparison outputs include:

- `corroborates`: independent claims match on disease, geography, time, count field, and count value.
- `partially_supports`: claims are compatible but less exact, such as explicit national aggregate support for a local claim or minor numeric differences.
- `conflicts`: comparable claims disagree in a meaningful way and need review.
- `duplicate_same_source`: claims come from the same URL/source and do not count as independent support.
- `not_comparable`: claims cannot be compared as the same public-health event.
- `insufficient_information`: one or both claims lack enough information.

Same-source duplicates are preserved for audit but do not increase independent source count.

## 5. Corroborated Events

The workflow groups comparable claims into `CorroboratedEvent` outputs. Each event preserves supporting, conflicting, and unverified claim IDs plus source IDs, source URLs, publishers, and evidence.

Key statuses:

- `corroborated`: at least two independent sources support the same claim.
- `cross_source_supported`: independent sources support a compatible claim with partial support.
- `single_source_unverified`: a primary case/death/hospitalization claim has no independent corroboration.
- `conflicting_claims`: comparable claims conflict and should go to human review.
- `zero_case_statement_unverified`: a zero-case statement is present without independent support.
- `exposure_monitoring_only`: evidence describes monitoring or exposure follow-up, not a case record.
- `context_only`: evidence is background, symptoms, prevention, or fact-sheet content.

## 6. Virginia Example

For Hantavirus / Virginia / 2025-01-01 to 2026-06-01:

- VDH monitoring text such as people completing a 42-day monitoring period and remaining healthy should be classified as `exposure_monitoring_record`, not `confirmed_case_record`.
- A single secondary statement saying no confirmed cases have been reported should be classified as `zero_case_statement` and remain unverified unless another independent source supports it.
- If two independent sources report the same Virginia hantavirus case in the same time window, the workflow should create a single corroborated event with both source IDs and evidence quotes preserved.

## 7. Outputs

Diagnostics:

- `diagnostics/claims.json`
- `diagnostics/claim_comparisons.json`
- `diagnostics/corroborated_events.json`
- `diagnostics/corroboration_summary.json`

Collection/final package exports:

- `collection/claims.json`
- `collection/claims.csv`
- `collection/claim_comparisons.json`
- `collection/corroborated_events.json`
- `collection/corroborated_events.csv`
- `collection/corroborated_case_events.csv`
- `collection/uncorroborated_claims.csv`
- `collection/conflicting_claims.csv`

Workflow summaries include `corroboration_summary`.

## Acceptance repair: final dataset alignment

Claim-level `primary_case_dataset_eligible` now controls final dataset inclusion
before the final quality-gated package is exported. Records explicitly annotated
as `primary_case_dataset_eligible=false` are excluded from `final_dataset`
unless an explicit applied human-review decision later accepts them.

Excluded non-primary observations are preserved separately as
`non_primary_observations` in collection and diagnostics outputs. This keeps
zero-case statements, exposure-monitoring text, background context, and
ambiguous non-primary observations auditable without making them look like
accepted epidemiological case records.

`final_dataset` no longer contains records with explicit
`primary_case_dataset_eligible=false`. `final_dataset_pre_quality_gate` still
preserves all normalized candidate records for audit, and
`final_dataset_post_review` equals the repaired `final_dataset` when no
human-review decisions exist.

A Virginia live run can legitimately finish with no primary case records
accepted. In that situation the run quality summary reports
`no_primary_case_dataset_records` or `no_corroborated_primary_case_events`, and
the report/console should not describe the result as a successful final
epidemiological case dataset.

## 8. Limitations

- This optimization does not determine official truth automatically.
- Source discovery is not changed in this optimization.
- Source identity and publisher extraction are not overhauled in this optimization.
- The final primary-case dataset split is not fully implemented in this optimization.
- Human review decisions are queued but not applied here.
- No human review UI is created here.
- No workflow live visualization is created here.
- Live web availability may limit whether corroborating sources are found.
