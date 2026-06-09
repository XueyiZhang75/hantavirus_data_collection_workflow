# Stage 9 Report: Duplicate Detection + Event Clustering

## 1. Stage goal

Stage 9 adds generic duplicate detection and event clustering so the data collection workflow can group records describing the same public-health event and avoid double counting.

The user-facing project name remains `data collection workflow`. The internal Python package name remains `hdc_workflow`.

## 2. Summary of changes

- Added event cluster models: `EventCluster`, `EventClusterMember`, and `DuplicateDetectionDecision`.
- Added explicit duplicate/countable fields to `PublicHealthRecord`.
- Upgraded the existing `record_linking` node to emit duplicate-aware event clusters without changing graph topology.
- Added deterministic duplicate rules for disease, location, date, count semantics, count values, source role, source credibility, and provenance.
- Added `countable` logic for representatives, non-countable duplicates, related records, conflicts, and singleton records.
- Added deterministic representative selection using source role, source type, credibility, completeness, and stable record ID.
- Added duplicate/event-clustering human review items for uncertain related records and conflicting counts.
- Added final package exports and diagnostics for `event_clusters`, `duplicate_clusters`, `event_clustering_summary`, and `duplicate_detection_summary`.
- Preserved `linked_events` and `linked_event_id` compatibility.

## 3. Files created or modified

Created:

- `docs/duplicate_event_clustering.md`
- `docs/stage_reports/STAGE_9_REPORT.md`
- `tests/test_duplicate_event_clustering.py`

Modified:

- `src/hdc_workflow/models.py`
- `src/hdc_workflow/state.py`
- `src/hdc_workflow/nodes/linking_validation.py`
- `src/hdc_workflow/nodes/finalization.py`
- `src/hdc_workflow/resources/final_package_policy.json`
- `src/hdc_workflow/export.py`
- `scripts/run_hdc_workflow_configured.py`
- `scripts/build_workflow_run_console.py`

No Stage 10 validation refactor or UI redesign was implemented.

## 4. Functional changes made

Record linking:

- Keeps the existing `record_linking` node name and graph position.
- Preserves existing `linked_events`.
- Adds event cluster generation after the existing event-key linking step.
- Maps `event_cluster_id` to `linked_event_id` for backward compatibility.

Normalized record updates:

- Every normalized record receives event cluster and duplicate detection fields.
- Duplicate records are marked with `countable=false` and `duplicate_of_record_id`.
- Related/conflicting records keep provenance and review reasons.

Linked events/event clusters:

- Existing `linked_events` remain available.
- New `event_clusters` contain representative, member, source, count, credibility, and review fields.
- `duplicate_clusters` is exported as the subset of duplicate clusters.

Duplicate summaries:

- `event_clustering_summary` counts clusters, singleton clusters, duplicate clusters, related clusters, conflict clusters, countable records, and non-countable duplicates.
- `duplicate_detection_summary` reports duplicate-specific counts and review counts.

Finalization:

- `FinalDataPackage` now includes `event_clusters` and `duplicate_clusters`.
- `final_dataset` retains old fields and adds Stage 9 clustering fields.
- Provenance manifest and finalization summary include clustering counts.

Diagnostics:

- Configured runs now export `diagnostics/event_clusters.json`.
- Configured runs now export `diagnostics/duplicate_clusters.json`.
- Configured runs now export `diagnostics/event_clustering_summary.json`.
- Configured runs now export `diagnostics/duplicate_detection_summary.json`.
- `diagnostics/normalized_records.json` includes clustering fields.

Configs:

- Stage 9 reused Stage 8 fixture/live extraction configs because clustering runs automatically after normalized records are produced.
- No API keys are stored in configs.

Tests:

- Added deterministic offline duplicate/event clustering tests.
- Existing Stage 1-8 tests continue to pass.

## 5. Duplicate detection behavior

Disease compatibility:

- Same-event duplicate clusters require compatible disease labels.
- COVID-19, dengue, and hantavirus records do not merge across diseases.

Location compatibility:

- Same-event duplicate clusters require compatible country/subnational/locality keys.
- New York and Florida do not merge.
- Related/nested location behavior remains conservative.

Date/time compatibility:

- Same-event duplicate clusters require compatible date anchors, reporting periods, or as-of dates.
- Different non-overlapping dates do not merge.
- Annual summary versus daily/weekly update is related/reviewed rather than deduplicated.

Count semantics compatibility:

- Cumulative, annual, weekly, newly reported, historical total, and subset semantics are not merged unsafely.
- Missing or incompatible semantics can produce related-record review items.

Count value compatibility:

- Identical count signatures for compatible disease/location/date records can form duplicate clusters.
- Conflicting counts for compatible disease/location/date records create `conflict_needs_review`.

Source/provenance compatibility:

- Same source URL/evidence chunk supports duplicate classification.
- Official source records are preferred over secondary/news support when representative selection is needed.
- Source ID, URL, source type, publisher, evidence quote, search provider, query ID, and credibility score are preserved.

Evidence similarity:

- Stage 9 uses lightweight deterministic matching from normalized fields and provenance.
- No heavy similarity dependency was added.

Unsafe merge prevention:

- Different diseases, incompatible locations, incompatible dates, and incompatible count semantics are not merged as duplicates.

## 6. Event clustering behavior

Each cluster has:

- `event_cluster_id`
- `cluster_status`
- disease/location/date/count fields
- representative record
- member records
- countable record IDs
- non-countable duplicate record IDs
- related record IDs
- conflict record IDs
- source/provenance fields
- canonical count fields
- human review reason and warnings when needed

Cluster status values used:

- `singleton`
- `duplicate_cluster`
- `related_records`
- `conflict_needs_review`
- `invalid_or_unclustered`

Member status values used:

- `representative`
- `singleton`
- `non_countable_duplicate`
- `related_not_merged`
- `conflicting_member`
- `invalid`

Representative selection:

- Prefers collection/validation source roles.
- Prefers official public-health agencies over secondary/news sources.
- Prefers higher credibility scores.
- Prefers more complete records.
- Uses stable `record_id` ordering as final tie-breaker.

Countable behavior:

- Singleton records are countable.
- Duplicate cluster representative is countable.
- Non-representative duplicate records are non-countable.
- Related records are countable by default and reviewed when ambiguous.
- Conflicting records are kept countable and routed to review unless duplicate confidence is high enough to suppress.

## 7. Human review routing

Stage 9 adds duplicate/event-clustering review items for:

- high duplicate suspicion but uncertain merge
- same disease/location/date with conflicting counts
- related aggregate/subset ambiguity
- unclear or incompatible count semantics
- annual summary versus event update ambiguity
- representative selection uncertainty when relevant

Review item payloads include:

- `event_cluster_id`
- `member_record_ids`
- `representative_record_id`
- reason
- suggested action
- source IDs and URLs
- count comparison summary

Human review decision application was not implemented.

## 8. Disease-specific examples

### COVID-19 / New York / 2024

Fixture smoke:

- Normalized record count: 2
- Event cluster count: 2
- Singleton count: 2
- Duplicate cluster count: 0
- Countable record count: 2
- Non-countable duplicate count: 0
- Human review duplicate item count: 0
- Example cluster: `event_001`, `singleton`, representative `rec_src_search_6dca14491140_002`

Live smoke:

- Normalized record count: 2
- Event cluster count: 2
- Singleton count: 2
- Duplicate cluster count: 0
- Countable record count: 2
- Non-countable duplicate count: 0
- Human review duplicate item count: 0

### Dengue / Florida / 2025

Fixture smoke:

- Normalized record count: 2
- Event cluster count: 2
- Singleton count: 2
- Duplicate cluster count: 0
- Countable record count: 2
- Non-countable duplicate count: 0
- Human review duplicate item count: 0
- Example cluster: `event_001`, `singleton`, representative `rec_src_search_2f25694b3ca0_002`

Live smoke:

- Normalized record count: 6
- Event cluster count: 5
- Singleton count: 3
- Duplicate cluster count: 0
- Related cluster count: 1
- Conflict cluster count: 1
- Countable record count: 6
- Non-countable duplicate count: 0
- Human review duplicate item count: 2

### Hantavirus / New Mexico compatibility

- Normalized record count: 5
- Event cluster count: 4
- Existing linked events remain available.
- `event_cluster_id` maps to `linked_event_id`.
- Compatibility status: passed with all LLM stages disabled.

## 9. Integration with workflow

Normalized records feed the existing `record_linking` node. The node first preserves existing linked-event behavior, then emits duplicate-aware event clusters.

Clustering outputs feed `cross_source_consistency_check` through the same normalized records and linked events. Stage 9 does not refactor the cross-source validation/checker into Stage 10 validation.

The final dataset now includes `event_cluster_id`, `event_cluster_status`, `event_member_status`, `countable`, duplicate IDs, representative IDs, duplicate confidence, duplicate reasons, review flags, and cluster warnings.

Workflow summaries expose `event_clustering_summary` and `duplicate_detection_summary`.

Diagnostics export event clusters, duplicate clusters, summaries, and updated normalized records.

## 10. Backward compatibility

- `linked_events` remains available.
- `linked_event_id` remains available.
- `event_cluster_id` maps to `linked_event_id`.
- Existing New Mexico/Hantavirus compatibility passes.
- Existing tests pass after preserving old `linked_events.requires_human_review` behavior.
- The graph topology was not changed.

## 11. Tests added or updated

Added:

- `tests/test_duplicate_event_clustering.py`

Test coverage includes:

- Every normalized record receives event cluster fields.
- Exact same-source duplicates cluster and count once.
- Official/source-support duplicate reports select the official representative.
- Different dates do not merge.
- Different locations do not merge.
- Different diseases do not merge.
- Cumulative versus newly reported records are related/reviewed, not duplicated.
- Annual summary versus single update is not duplicated.
- Conflicting counts route to human review.
- Human review queue receives duplicate/event-clustering review items.
- Final package exports clustering artifacts.
- COVID-19 fixture extraction clustering smoke.
- Dengue fixture extraction clustering smoke.
- Hantavirus compatibility clustering.

## 12. Commands run

Repository inspection:

```powershell
git status --short
git branch --show-current
git rev-parse HEAD
```

Targeted test:

```powershell
python -m pytest tests\test_duplicate_event_clustering.py -q
```

Regression subset:

```powershell
python -m pytest tests\test_generic_structured_extraction.py tests\test_fetch_parse_generalization.py tests\test_source_credibility_scoring.py tests\test_real_source_discovery.py tests\test_executable_source_planning.py tests\test_profile_schema_setup.py tests\test_disease_intelligence.py tests\test_structured_task_input.py -q
```

Full test suite:

```powershell
python -m pytest -q
```

Fixture clustering smokes:

```powershell
python scripts\run_hdc_workflow_configured.py --config configs\examples\covid19_new_york_2024_fixture_search_fetch_extract_task.jsonc --session-id stage9_covid19_fixture_cluster_smoke
python scripts\run_hdc_workflow_configured.py --config configs\examples\dengue_florida_2025_fixture_search_fetch_extract_task.jsonc --session-id stage9_dengue_fixture_cluster_smoke
```

Live clustering smokes:

```powershell
python scripts\run_hdc_workflow_configured.py --config configs\examples\covid19_new_york_2024_live_search_fetch_extract_smoke.jsonc --session-id stage9_covid19_live_cluster_smoke
python scripts\run_hdc_workflow_configured.py --config configs\examples\dengue_florida_2025_live_search_fetch_extract_smoke.jsonc --session-id stage9_dengue_live_cluster_smoke
```

Hantavirus/New Mexico compatibility:

```powershell
python scripts\run_hdc_workflow_configured.py --config configs\hdc_workflow_run_config.jsonc --disable-all-llm --session-id stage9_hantavirus_live_fetch_compat_no_llm
```

Secret scan:

```powershell
rg -n "tvly-|sk-ant-|ANTHROPIC_API_KEY=\S+|TAVILY_API_KEY=\S+" .env.example configs docs outputs scripts src tests
```

## 13. Test results

Targeted Stage 9 tests:

```text
14 passed in 0.35s
```

Regression subset:

```text
85 passed in 1.48s
```

Full pytest:

```text
305 passed in 7.15s
```

Secret scan:

```text
Matches were limited to the mocked tvly-test-key in tests and documented scan commands in stage reports. No real API key was found or printed.
```

## 14. Fixture clustering smoke results

### COVID-19 fixture clustering smoke

- Status: PASSED
- Command: `python scripts\run_hdc_workflow_configured.py --config configs\examples\covid19_new_york_2024_fixture_search_fetch_extract_task.jsonc --session-id stage9_covid19_fixture_cluster_smoke`
- Output directory: `outputs/sessions/stage9_covid19_fixture_cluster_smoke`
- Normalized record count: 2
- Event cluster count: 2
- Duplicate cluster count: 0
- Countable record count: 2
- Human review duplicate item count: 0
- Example cluster: `event_001`, singleton, representative `rec_src_search_6dca14491140_002`
- No live web required.
- No API key required.

### Dengue fixture clustering smoke

- Status: PASSED
- Command: `python scripts\run_hdc_workflow_configured.py --config configs\examples\dengue_florida_2025_fixture_search_fetch_extract_task.jsonc --session-id stage9_dengue_fixture_cluster_smoke`
- Output directory: `outputs/sessions/stage9_dengue_fixture_cluster_smoke`
- Normalized record count: 2
- Event cluster count: 2
- Duplicate cluster count: 0
- Countable record count: 2
- Human review duplicate item count: 0
- Example cluster: `event_001`, singleton, representative `rec_src_search_2f25694b3ca0_002`
- No live web required.
- No API key required.

## 15. Live clustering smoke results

### COVID-19 live clustering smoke

- Status: PASSED
- Command: `python scripts\run_hdc_workflow_configured.py --config configs\examples\covid19_new_york_2024_live_search_fetch_extract_smoke.jsonc --session-id stage9_covid19_live_cluster_smoke`
- Provider: Tavily
- API key present: true, value not printed
- Output directory: `outputs/sessions/stage9_covid19_live_cluster_smoke`
- Live-search-derived source count: 5
- Usable/partial document count: 1 usable, 1 partial
- Normalized record count: 2
- Event cluster count: 2
- Duplicate cluster count: 0
- Singleton count: 2
- Countable record count: 2
- Non-countable duplicate count: 0
- Example cluster: `event_001`, singleton, representative `rec_src_search_af2355dda632_002`
- Disease stayed non-hantavirus: yes
- No API keys printed.

### Dengue live clustering smoke

- Status: PASSED
- Command: `python scripts\run_hdc_workflow_configured.py --config configs\examples\dengue_florida_2025_live_search_fetch_extract_smoke.jsonc --session-id stage9_dengue_live_cluster_smoke`
- Provider: Tavily
- API key present: true, value not printed
- Output directory: `outputs/sessions/stage9_dengue_live_cluster_smoke`
- Live-search-derived source count: 3
- Usable/partial document count: 1 usable, 0 partial, 1 parse deferred
- Normalized record count: 6
- Event cluster count: 5
- Duplicate cluster count: 0
- Singleton count: 3
- Countable record count: 6
- Non-countable duplicate count: 0
- Example cluster: `event_001`, singleton, representative `rec_src_search_53763309bf94_006`
- Disease stayed non-hantavirus: yes
- No API keys printed.

## 16. Hantavirus live-fetch compatibility

- Status: PASSED
- Command: `python scripts\run_hdc_workflow_configured.py --config configs\hdc_workflow_run_config.jsonc --disable-all-llm --session-id stage9_hantavirus_live_fetch_compat_no_llm`
- Output directory: `outputs/sessions/stage9_hantavirus_live_fetch_compat_no_llm`
- `live_fetch_enabled`: true
- `live_search_enabled`: false
- All LLM stages disabled: yes
- Document count: 5
- Usable document count: 5
- Normalized record count: 5
- Event cluster count: 4
- Linked event count: 4
- Human review item count: 11
- Compatibility notes: Hantavirus/New Mexico records remain compatible; `linked_events` remain available and `event_cluster_id` maps to `linked_event_id`.
- No API keys printed.

## 17. Live acceptance result

PASSED.

Evidence:

- `pytest` passed.
- Fixture clustering smokes passed.
- Live clustering smokes for COVID-19 and dengue ran and produced event clusters.
- Hantavirus/New Mexico compatibility passed.
- All normalized records in smoke runs received `event_cluster_id` and `countable`.
- Final package and diagnostics export clustering artifacts.
- No API keys or secrets were printed.
- Stage 10 and future-stage features were not implemented.

## 18. Output artifacts

Documentation:

- `docs/duplicate_event_clustering.md`
- `docs/stage_reports/STAGE_9_REPORT.md`

Tests:

- `tests/test_duplicate_event_clustering.py`

Session directories:

- `outputs/sessions/stage9_covid19_fixture_cluster_smoke`
- `outputs/sessions/stage9_dengue_fixture_cluster_smoke`
- `outputs/sessions/stage9_covid19_live_cluster_smoke`
- `outputs/sessions/stage9_dengue_live_cluster_smoke`
- `outputs/sessions/stage9_hantavirus_live_fetch_compat_no_llm`

Diagnostics:

- `diagnostics/event_clusters.json`
- `diagnostics/duplicate_clusters.json`
- `diagnostics/event_clustering_summary.json`
- `diagnostics/duplicate_detection_summary.json`
- `diagnostics/normalized_records.json`

Final package exports:

- `collection/event_clusters.json`
- `collection/duplicate_clusters.json`
- `collection/final_dataset.csv`
- `collection/final_package.json`

## 19. Known limitations

- Validation refactor not implemented yet.
- Trusted-source validation not implemented yet.
- Cross-source validation refactor not implemented yet.
- Anomaly detection not implemented yet.
- Human review decision application not implemented yet.
- CLI/notebook/UI redesign not implemented yet.
- Duplicate detection remains deterministic and conservative.
- Live sources may not naturally contain duplicate records.
- Time-window validation is not fully implemented yet.
- Nested-location similarity remains conservative.
- LLM duplicate review was not implemented in Stage 9.

## 20. Future-stage items explicitly NOT implemented

- validation refactor
- trusted-source validation
- cross-source validation
- anomaly detection
- human review decision application
- CLI/notebook/UI
- notebook redesign
- UI redesign
- uncontrolled crawling
- recursive crawling
- browser automation
- JavaScript rendering
- OCR

## 21. Review checklist

- [x] User-facing project name remains "data collection workflow"
- [x] Internal package name hdc_workflow was not mass-renamed
- [x] Graph topology unchanged unless documented
- [x] Event cluster model/output exists
- [x] Duplicate detection summary exists
- [x] Every normalized record has event_cluster_id
- [x] Every normalized record has countable flag
- [x] Exact duplicates cluster and count once
- [x] Official/source-support same-event duplicates cluster correctly
- [x] Different diseases do not merge
- [x] Different locations do not merge
- [x] Different dates do not unsafely merge
- [x] Cumulative vs newly reported records do not unsafely merge
- [x] Annual summary vs event update records do not unsafely merge
- [x] Conflicting counts route to human review
- [x] Representative selection is deterministic and auditable
- [x] Final package exports event/duplicate clusters
- [x] Final dataset includes event_cluster_id and countable
- [x] Existing Hantavirus/New Mexico compatibility passes
- [x] Fixture COVID-19 clustering smoke completed
- [x] Fixture dengue clustering smoke completed
- [x] Live COVID-19 clustering smoke attempted
- [x] Live dengue clustering smoke attempted
- [x] pytest was run
- [x] No API keys or secrets were printed
- [x] No validation refactor was implemented
- [x] No anomaly detection was implemented
- [x] No human review decision application was implemented
- [x] No future-stage features were implemented
