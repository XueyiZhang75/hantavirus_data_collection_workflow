# Task-Compatible Validation Sources

The data collection workflow uses held-out validation records only when they are
compatible with the active task. Compatibility is checked before validation
records enter held-out comparison or evaluation reporting.

## Purpose

Held-out validation records are useful only when their disease, geography, and
time window match the task being collected. A New Mexico hantavirus ground-truth
record should not be used to validate a COVID-19/New York run, a dengue/Florida
run, or a hantavirus/Shanghai run. When no compatible held-out validation source
exists, the workflow records that fact instead of producing misleading
`missing_collection_record` or `missing_validation_record` rows.

## Compatibility Checks

Each validation record is assessed against the active task using deterministic,
offline checks:

- Disease compatibility: reuses the workflow disease relevance assessment.
- Geography compatibility: compares task location with validation record
  locality, subnational location, geographic scope, and country.
- Time compatibility: checks overlap between task years and validation record
  date/reporting-period metadata.

The resolver returns three auditable fields:

- `active_validation_records`: records allowed into held-out validation.
- `inactive_validation_records`: records loaded but disabled for this task.
- `validation_source_compatibility_summary`: counts, status, warnings, and task
  metadata explaining the decision.

## Status Values

- `compatible`: all loaded validation records are task-compatible.
- `partially_compatible`: at least one validation record is compatible and at
  least one is inactive.
- `no_task_compatible_validation_source`: default validation records were
  loaded, but none matched the task.
- `incompatible_validation_source_disabled`: an explicit validation CSV was
  configured, but it did not match the task and was disabled.
- `validation_source_missing`: the configured validation CSV path did not exist.
- `validation_source_empty`: the configured validation CSV had no records.
- `insufficient_validation_metadata`: records could not be safely assessed
  because required metadata was missing.
- `explicit_validation_source_loaded_with_warning`: incompatible validation
  records were force-loaded by override for diagnostic use.
- `validation_disabled_by_config`: reserved status for profiles that disable
  validation records entirely.

## Configuration

The default behavior is conservative:

```jsonc
"validation": {
  "allow_incompatible_validation_records": false
}
```

Keep this value `false` for normal runs. Set it to `true` only for diagnostic
experiments where the goal is to inspect what would happen if an incompatible
explicit validation source were force-loaded. The same override can also be set
with `HDC_ALLOW_INCOMPATIBLE_VALIDATION_RECORDS=true`.

The configured path is still read from:

```jsonc
"workflow": {
  "validation_ground_truth_records_path": "..."
}
```

If this path is omitted, the historical New Mexico HPS validation CSV remains
the default candidate, but it will now be disabled automatically for unrelated
tasks.

## Output Artifacts

Each configured run writes these validation artifacts into its session folder:

- `validation/ground_truth_records.csv`: active validation records only.
- `validation/inactive_validation_records.csv`: loaded but disabled records.
- `validation/inactive_validation_records.json`: inactive records with
  compatibility reasons.
- `validation/validation_source_compatibility_summary.json`: task metadata,
  active/inactive counts, status, and warnings.
- `diagnostics/active_validation_records.json`: active records used by the graph.
- `diagnostics/inactive_validation_records.json`: inactive records preserved for
  audit.
- `diagnostics/validation_source_compatibility_summary.json`: diagnostic copy of
  the resolver summary.

The final package workflow summaries also include
`validation_source_compatibility_summary`.

## Expected Behavior

For the New Mexico HPS profile, the New Mexico HPS held-out source remains
active. For a Shanghai hantavirus run, COVID-19/New York run, or dengue/Florida
run, the New Mexico HPS validation source is inactive. The workflow still
completes and reports that no task-compatible held-out validation source was
available.

## Limitations

This repair does not discover new validation sources. It only prevents
incompatible validation records from being used. Future source discovery and
curation work can provide task-specific validation CSVs for additional diseases
and geographies.
