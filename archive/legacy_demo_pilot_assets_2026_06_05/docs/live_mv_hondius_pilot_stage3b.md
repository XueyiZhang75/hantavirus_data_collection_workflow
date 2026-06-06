# Live MV Hondius Masked Validation Pilot - Stage 3B

## 1. Purpose

Stage 3B implements a controlled live masked validation pilot for the 2026 MV Hondius multi-country hantavirus cluster. The pilot uses an explicit source allowlist, blocks WHO DON600 from collection, fetches only non-held-out collection/context sources live, and compares collection output against a manually curated WHO ground truth CSV.

This is not broad web search, automated WHO scraping, a Reuters access-control bypass, or a production epidemiological benchmark.

## 2. Case study source roles

- `src_reuters_mv_hondius_2026_05_27`: collection-allowed Reuters source.
- `src_vdh_hantavirus_mv_hondius_context`: context-only Virginia Department of Health source.
- `src_who_don600_mv_hondius_2026`: held-out validation source, reserved by source ID and blocked from collection.

WHO is intentionally included in the source allowlist so the run can prove it is known to the system but blocked by masked-validation routing.

## 3. What was implemented

- `HDC_SEED_SOURCE_OVERLAY_PATH` support in `load_hantavirus_seed_sources()`.
- `HDC_SOURCE_ROLE_POLICY_OVERLAY_PATH` support in `load_source_role_policy()`.
- A case-specific MV Hondius seed source overlay.
- A case-specific source-role policy overlay.
- A manually curated WHO ground truth CSV.
- `scripts/run_mv_hondius_live_masked_pilot.py`, safe by default and live-fetch gated by `--allow-live-fetch`.
- Offline-safe tests for overlays, routing, script safety, dry-run behavior, and ground truth CSV shape.

## 4. How to run

Dry-run only, no network:

```powershell
python scripts/run_mv_hondius_live_masked_pilot.py --dry-run
```

Controlled live pilot:

```powershell
python scripts/run_mv_hondius_live_masked_pilot.py --allow-live-fetch
```

Optional output directory:

```powershell
python scripts/run_mv_hondius_live_masked_pilot.py --allow-live-fetch --output-dir outputs/live_masked_validation_mv_hondius
```

## 5. What outputs are generated

- `outputs/live_masked_validation_mv_hondius/collection/final_package.json`
- `outputs/live_masked_validation_mv_hondius/collection/final_dataset.csv`
- `outputs/live_masked_validation_mv_hondius/collection/source_registry.json`
- `outputs/live_masked_validation_mv_hondius/validation/ground_truth_records.csv`
- `outputs/live_masked_validation_mv_hondius/validation/validation_source_registry.json`
- `outputs/live_masked_validation_mv_hondius/evaluation/evaluation_report.csv`
- `outputs/live_masked_validation_mv_hondius/evaluation/evaluation_summary.json`
- `outputs/live_masked_validation_mv_hondius/evaluation/professor_demo_report.md`
- `outputs/live_masked_validation_mv_hondius/diagnostics/collection_diagnostics.json`
- `outputs/live_masked_validation_mv_hondius/diagnostics/source_leakage_check.json`
- `outputs/live_masked_validation_mv_hondius/diagnostics/live_fetch_summary.json`
- `outputs/live_masked_validation_mv_hondius/diagnostics/extraction_diagnostics.md`
- `outputs/live_masked_validation_mv_hondius/diagnostics/semantic_leakage_assessment.md`

## 6. How to inspect source masking

Check `diagnostics/source_leakage_check.json`:

- `who_blocked_from_collection` should be `true`.
- `reserved_source_leakage_count` should be `0`.
- `who_final_screening_decision` should be `reserved_for_validation`.
- `who_ready_for_content_fetch` should be `false`.

Check `collection/source_registry.json` to confirm WHO remains visible in the registry as a reserved source rather than disappearing from provenance.

## 7. How to interpret collection vs validation

The evaluation compares any live collection records against one manual WHO ground truth record. A mismatch, missing collection row, missing validation row, or not-comparable result is expected to require human review.

Reuters reports a later state of the evolving outbreak than WHO DON600. A numeric difference may reflect a later reporting date rather than an extraction error.

## 8. Semantic leakage warning

Reuters explicitly cites WHO. Therefore this pilot can show technical source masking, but it cannot prove independent validation. Any professor-facing interpretation must describe the result as source-masked comparison with semantic leakage risk.

## 9. Current limitations

- WHO ground truth is manually curated, not automatically scraped.
- Live pages may change after the run.
- Reuters may be inaccessible or return insufficient text; the script records this as a limitation.
- Deterministic extraction may under-extract from live HTML.
- Broad web search is not implemented.
- PDF/OCR is not implemented.
- External LLM extraction is disabled for this pilot.

## 10. Next step after Stage 3B

Stage 3C should review live pilot outputs, inspect the source masking diagnostics, and decide whether to add an approved LLM extraction pass or switch to the New Mexico backup case for cleaner source independence.
