# Dynamic report and console cleanup

This note documents how the data collection workflow should present each run in
the Markdown report, HTML console, and console summary JSON.

## Goal

The report and console must describe the selected session artifacts, not a
hard-coded demo case. A run can complete technically while still producing zero
quality-gated accepted records. That distinction must be visible in every
human-facing output.

## Dynamic task fields

The console and reports should read task fields from exported artifacts in this
order:

- `diagnostics/workflow_summaries.json` -> `task_intake_summary.collection_spec`
- `diagnostics/workflow_summaries.json` -> `task_intake_summary.structured_task`
- `collection/final_package.json` -> `package_metadata`

If no task fields are available, the UI should say
`collection_spec unavailable in artifacts` rather than substituting a disease,
location, or time window from an older run.

## Run quality wording

The user-facing status should come from `run_quality_summary.run_quality_status`
through `user_facing_run_status()`. In particular:

- `passed` means accepted quality-gated records exist.
- `partial_with_quarantined_records` means accepted records exist, with some
  candidate records quarantined.
- `no_records_extracted`, `no_task_relevant_records`, and
  `failed_quality_gate` mean the workflow completed technically but did not
  produce a successful final collection result.
- `validation_limited` means held-out validation was limited because no
  task-compatible validation source was available.

## Dataset views

The final dataset view must separate these counts:

- Accepted `final_dataset`
- Pre-quality-gate records
- Quarantined records
- Pending-review records
- Post-review final dataset
- Normalized records

The report must not list normalized or pre-quality records as final accepted
records. Accepted-record tables should be built from `final_dataset` only.

## Console panels

The HTML console should display these dynamic summaries when present:

- Source search execution summary
- Localized source planning summary
- Source critic summary
- Disease relevance summary
- Validation source compatibility summary
- Run quality and final dataset quality summaries
- Key artifact paths for audit

## Stale wording to avoid

Do not use fixed New Mexico, NMDOH/CDC, Hantavirus-only, or success-only text in
generic console/report templates. Those strings can appear only when they are
present in the current run's task, source, or evidence artifacts.
