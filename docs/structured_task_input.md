# Structured Task Input

## 1. Purpose

Stage 1 makes the main task parameters explicit structured inputs for the **data collection workflow**. Instead of relying only on a free-text `user_request`, the workflow can now receive machine-readable values for disease, location, time range, target fields, source preferences, collection mode, and run label.

This layer improves auditability and makes LangGraph Studio / configured runner inputs clearer, while preserving the current backward-compatible hantavirus/New Mexico default behavior.

## 2. Supported Fields

- `disease`: Disease or syndrome requested by the user, such as `hantavirus`, `COVID-19`, or `dengue`.
- `location`: Geographic scope requested by the user, such as `New Mexico`, `New York`, `Florida`, `United States`, or `global`.
- `start_date`: Start of the requested collection window. Stage 1 stores it as provided.
- `end_date`: End of the requested collection window. Stage 1 stores it as provided.
- `target_fields`: Requested output fields, such as `cases_confirmed`, `deaths`, `date_reported`, `source_url`, and `evidence_quote`.
- `source_preferences`: Preferred source categories, such as `official_public_health_agency`, `international_organization_report`, `peer_reviewed_literature`, `structured_database`, and `news_and_situation_report`.
- `collection_mode`: Workflow mode, currently used to carry values such as `masked_validation` or `standard`.
- `user_request`: Human-readable task text retained for Studio display and backward compatibility.
- `run_label` / `profile_name`: Human-readable run or profile label used in task metadata and reporting. `profile_name` remains a runtime config label; `run_label` is carried into the structured task and `CollectionSpec`.

## 3. Priority Order

The task intake node resolves inputs in this order:

1. Structured fields from `structured_task` or explicit graph state fields.
2. Runner/config overrides when available, such as a `--user-request` override.
3. Legacy config `user_request`.
4. Backward-compatible default fallback: the current hantavirus/New Mexico behavior.

Structured fields take priority over conflicting text in `user_request`. For example, if `user_request` mentions hantavirus but `structured_task.disease` is `COVID-19`, Stage 1 preserves `COVID-19` in `CollectionSpec`.

## 4. Examples

### Hantavirus / New Mexico / 2020-2026

```json
{
  "structured_task": {
    "disease": "hantavirus",
    "location": "New Mexico",
    "start_date": "2020",
    "end_date": "2026",
    "target_fields": [
      "cases_confirmed",
      "deaths",
      "date_reported",
      "source_url",
      "evidence_quote"
    ],
    "source_preferences": [
      "official_public_health_agency"
    ],
    "collection_mode": "masked_validation",
    "user_request": "Collect data on hantavirus from 2020 to 2026.",
    "run_label": "new_mexico_hps_live_llm_workflow_run"
  }
}
```

### COVID-19 / New York / 2024

```json
{
  "structured_task": {
    "disease": "COVID-19",
    "location": "New York",
    "start_date": "2024",
    "end_date": "2024",
    "target_fields": [
      "cases_confirmed",
      "deaths",
      "date_reported",
      "source_url",
      "evidence_quote"
    ],
    "source_preferences": [
      "official_public_health_agency",
      "structured_database"
    ],
    "collection_mode": "standard",
    "user_request": "Collect COVID-19 data for New York in 2024.",
    "run_label": "covid19_new_york_2024_task_input_example"
  }
}
```

### Dengue / Florida / 2025

```json
{
  "structured_task": {
    "disease": "dengue",
    "location": "Florida",
    "start_date": "2025",
    "end_date": "2025",
    "target_fields": [
      "cases_unspecified",
      "deaths",
      "source_url",
      "source_type",
      "evidence_quote"
    ],
    "source_preferences": [
      "official_public_health_agency",
      "international_organization_report"
    ],
    "collection_mode": "standard",
    "user_request": "Collect dengue data for Florida in 2025.",
    "run_label": "dengue_florida_2025_task_input_example"
  }
}
```

## 5. Current Limitations

- Disease intelligence layer is now implemented by Stage 2.
- Generic disease profile/schema setup is now implemented by Stage 3 for active profile/schema resources.
- Executable LLM source planning is not implemented yet.
- Real source discovery/search provider is not implemented yet.
- Source credibility overhaul is not implemented yet.
- Validation refactor is not implemented yet.
- Non-hantavirus runs may produce empty records or warnings until later stages.
- Non-hantavirus tasks no longer use the static hantavirus profile/schema as active resources. They still include explicit future-stage warnings such as `source_discovery_not_yet_disease_generic` and `extraction_record_model_still_hantavirus_named`.
