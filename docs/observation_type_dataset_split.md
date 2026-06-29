# Observation-Type Dataset Split

## 1. Purpose

This optimization separates primary epidemiological case records from other useful public-health observations in the data collection workflow.

The main user-facing case dataset is now `final_case_dataset`. Other evidence is preserved in explicit dataset views instead of being mixed into the primary case table.

## 2. Why This Was Needed

Virginia live runs found useful evidence that should not be interpreted as confirmed hantavirus case data:

- VDH monitoring language can describe exposed people who remained healthy.
- A no-case statement can say no confirmed cases were reported.
- Fact sheets can explain symptoms, transmission, and prevention.
- Outbreak summaries can describe another geography or a broad aggregate.

Those observations matter for audit and interpretation, but they are not the same as confirmed, probable, suspected, or unspecified case records.

## 3. Dataset Views

- `final_case_dataset`: primary task-compatible case records.
- `probable_case_dataset`: probable case records.
- `suspected_case_dataset`: suspected case records.
- `unspecified_case_dataset`: unspecified case records.
- `death_dataset`: task-compatible records with death observations.
- `hospitalization_dataset`: task-compatible records with hospitalization observations.
- `zero_case_statements`: statements that report no cases or zero confirmed cases.
- `exposure_monitoring_records`: monitoring or exposure follow-up observations, including remained healthy / no symptoms evidence.
- `surveillance_summary_records`: aggregate surveillance summaries.
- `outbreak_summary_records`: outbreak summaries, including summaries that may be outside the task geography/time window.
- `context_records`: fact sheets, prevention, symptoms, transmission, and other background context.
- `unclassified_observation_records`: ambiguous observations that cannot be safely assigned to a specific view.
- `non_primary_observations`: preserved non-primary observations from the quality gate path.
- `quarantined_records`: records excluded by hard quality gates.
- `pending_review_records`: records held for unresolved human review.

## 4. Observation Types

The split consumes existing record and claim observation semantics:

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
- `ambiguous_public_health_observation`

The splitter uses explicit claim observation types first, then record observation types, corroborated-event status, claim flags, count fields, evidence text, and source identity fields.

## 5. Virginia Example

For Hantavirus / Virginia / 2025-01-01 to 2026-06-01:

- VDH monitoring / remained healthy evidence goes to `exposure_monitoring_records`.
- A secondary no-case statement goes to `zero_case_statements`.
- Fact sheets and general prevention pages go to `context_records`.
- If no confirmed/corroborated primary Virginia case is accepted, `final_case_dataset` is empty.

An empty `final_case_dataset` is a valid workflow result when the run found non-primary evidence but no accepted primary case records. It should not be read as a failed run or as an automatic truth determination.

## 6. Outputs

Collection outputs:

- `collection/final_case_dataset.csv`
- `collection/final_case_dataset.json`
- `collection/probable_case_dataset.csv`
- `collection/probable_case_dataset.json`
- `collection/suspected_case_dataset.csv`
- `collection/suspected_case_dataset.json`
- `collection/unspecified_case_dataset.csv`
- `collection/unspecified_case_dataset.json`
- `collection/death_dataset.csv`
- `collection/death_dataset.json`
- `collection/hospitalization_dataset.csv`
- `collection/hospitalization_dataset.json`
- `collection/zero_case_statements.csv`
- `collection/zero_case_statements.json`
- `collection/exposure_monitoring_records.csv`
- `collection/exposure_monitoring_records.json`
- `collection/surveillance_summary_records.csv`
- `collection/surveillance_summary_records.json`
- `collection/outbreak_summary_records.csv`
- `collection/outbreak_summary_records.json`
- `collection/context_records.csv`
- `collection/context_records.json`
- `collection/unclassified_observation_records.csv`
- `collection/unclassified_observation_records.json`
- `collection/observation_type_dataset_summary.json`

Diagnostics outputs:

- `diagnostics/final_case_dataset.json`
- `diagnostics/zero_case_statements.json`
- `diagnostics/exposure_monitoring_records.json`
- `diagnostics/surveillance_summary_records.json`
- `diagnostics/outbreak_summary_records.json`
- `diagnostics/context_records.json`
- `diagnostics/unclassified_observation_records.json`
- `diagnostics/observation_type_dataset_summary.json`

The final package also includes all new dataset views and `observation_type_dataset_summary`.

## 7. Limitations

- This optimization does not implement the interpretive human-readable report redesign.
- This optimization does not implement a human review UI.
- This optimization does not implement workflow visualization.
- This optimization does not create automatic truth determination.
- Observation type classification can still be imperfect.
- Live web availability may still limit whether primary case data is found.
- Source identity and claim corroboration remain auditable but not infallible.
