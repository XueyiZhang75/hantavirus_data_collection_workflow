# Live New Mexico HPS Real-Source Pilot - Stage 4C

## 1. Purpose

Stage 4C runs a controlled real-source masked validation pilot for hantavirus pulmonary syndrome (HPS) in New Mexico. It moves beyond fixture-only and source-planning-only demos while preserving explicit source roles, held-out validation, context-only guardrails, and offline-safe tests.

## 2. Why New Mexico HPS after Stage 4B.4

Stage 4B.4 successfully ran the Source Planning Agent for `new_mexico_hps` with provider-native structured output. The plan recommended NMDOH/state health department sources, CDC context, and official validation candidates. New Mexico HPS is a better first live pilot than MV Hondius because it uses accessible official public health pages and avoids the Reuters access limitation and VDH context-only mismatch observed in the MV Hondius pilot.

## 3. Source roles

Collection-allowed sources are the three NMDOH HTML press releases:

- `src_nmdoh_hps_2024_first_case`
- `src_nmdoh_hps_2025_first_case_death`
- `src_nmdoh_hps_2026_first_case_prior_year_summary`

Context-only sources are:

- `src_nmdoh_hps_overview_1975_2025`
- `src_cdc_hantavirus_reported_cases_through_2023`

The held-out validation source is:

- `src_nmdoh_hps_cases_by_county_1975_2025_pdf`

Domain masking is disabled for this pilot; masking is source-id based.

## 4. What was implemented

Stage 4C adds a New Mexico HPS seed-source overlay, a source-role policy overlay, a manually curated ground truth CSV, a controlled live pilot runner, offline-safe tests, diagnostics, and professor-facing planning/output artifacts.

The live runner disables LLM source planning, LLM source critic, and LLM extraction during the live fetch. It does not perform broad web search or parse the held-out PDF automatically.

## 5. How to run dry-run

```bash
python scripts/run_new_mexico_hps_live_masked_pilot.py --dry-run
```

Dry-run prints planned environment variables and paths. It does not contact the network.

## 6. How to run controlled live fetch

```bash
python scripts/run_new_mexico_hps_live_masked_pilot.py --allow-live-fetch
```

This is the only Stage 4C command that enables live HTTP fetch. It uses the explicit New Mexico HPS source-id allowlist.

## 7. What outputs are generated

The default output directory is `outputs/live_masked_validation_new_mexico_hps`.

Generated outputs include:

- `collection/final_dataset.csv`
- `collection/source_registry.json`
- `validation/ground_truth_records.csv`
- `validation/validation_source_registry.json`
- `evaluation/evaluation_report.csv`
- `evaluation/evaluation_summary.json`
- `evaluation/professor_demo_report.md`
- `diagnostics/source_leakage_check.json`
- `diagnostics/live_fetch_summary.json`
- `diagnostics/extraction_diagnostics.md`
- `diagnostics/source_role_audit.md`
- `diagnostics/llm_planning_reference.md`

The professor-package summary is written to `outputs/professor_demo_package/stage4c_new_mexico_hps_live_results_summary.json`.

## 8. How to inspect masking compliance

Inspect `diagnostics/source_leakage_check.json` first. The key fields are:

- `validation_reserved_source_present_in_registry`
- `validation_reserved_ready_for_content_fetch`
- `reserved_source_leakage_count`
- `reserved_source_leakage_source_ids`
- `technical_masking_status`

The expected masking result is that the validation source appears in the registry, has `ready_for_content_fetch=false`, and does not appear in `collection/final_dataset.csv`.

## 9. How to interpret collection vs validation

Collection records come only from collection-allowed NMDOH HTML press releases. Validation records come from the manually curated held-out NMDOH county/year ground truth CSV.

A match means deterministic extraction aligned with the held-out annual count. A mismatch or missing row should be interpreted conservatively because the collection pages are event-level press releases, while the ground truth is an annual count source.

## 10. Limitations

- The held-out NMDOH PDF/data page is not scraped or OCR-parsed.
- Live pages can change after the run.
- Deterministic extraction may under-extract from real HTML.
- Collection sources and validation source may use different reporting dates or statistical scopes.
- No broad web search, crawler, or LLM extraction is enabled in Stage 4C.

## 11. Next decision

After inspecting live fetch quality and deterministic extraction output, the next decision is whether Stage 4D should enable controlled LLM extraction on the same allowlisted pages, add PDF/OCR for the held-out NMDOH data page, or first refine deterministic New Mexico HPS extraction rules.
