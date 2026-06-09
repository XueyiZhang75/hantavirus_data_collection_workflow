# Duplicate Detection and Event Clustering

## 1. Purpose

Stage 9 groups generic public-health records into event clusters and identifies duplicate reports so the data collection workflow can avoid double-counting while preserving every source and evidence trail.

The workflow still exports `linked_events` for backward compatibility. Stage 9 adds explicit duplicate-aware fields such as `event_cluster_id`, `countable`, `event_member_status`, and `duplicate_of_record_id`.

## 2. Inputs

Event clustering consumes normalized records produced by Stage 8 and earlier workflow nodes:

- `normalized_records`
- `PublicHealthRecord` disease, location, date, count, provenance, and review fields
- disease and disease-standard-name fields
- country, subnational location, locality, and geographic scope
- date anchors, reporting periods, and as-of dates
- cases, deaths, hospitalizations, and other count fields
- `statistical_count_type` and `count_semantics`
- source registry metadata
- source credibility scores and levels
- source roles such as collection, validation, context, and collection support
- evidence quotes and supporting chunk IDs
- search/fetch provenance such as discovery method, search provider, query ID, and source URL

The clustering node does not fetch, search, browse, or call an LLM. It only uses data already in workflow state.

## 3. Outputs

Stage 9 outputs:

- `event_clusters`
- `duplicate_clusters`
- `event_clustering_summary`
- `duplicate_detection_summary`
- updated `linked_events`
- updated `normalized_records`
- duplicate/event-clustering human review items when needed

Every normalized record receives:

- `event_cluster_id`
- `event_cluster_status`
- `event_member_status`
- `countable`
- `duplicate_of_record_id`
- `representative_record_id`
- `duplicate_detection_method`
- `duplicate_detection_confidence`
- `duplicate_detection_reason`
- `duplicate_review_required`
- `duplicate_review_reason`
- `event_cluster_warnings`

Cluster outputs include representative records, countable records, non-countable duplicate records, related records, conflict records, source IDs, source URLs, source types, publishers, credibility score ranges, canonical counts, and review reasons.

## 4. Duplicate rules

Disease compatibility:

- Records must have compatible disease labels to be duplicate candidates.
- COVID-19 does not merge with dengue or hantavirus.
- Dengue/DENV records can cluster with dengue records when the rest of the event key is compatible.
- Hantavirus/HPS records can cluster with hantavirus records when the rest of the event key is compatible.

Location compatibility:

- Same-event duplicate clusters require compatible country/subnational/locality keys.
- Different states such as New York and Florida do not merge.
- Nested or related locations are treated conservatively and should be reviewed rather than silently merged.

Date/time compatibility:

- Same-event duplicates require compatible date anchors, reporting periods, or as-of dates.
- Different non-overlapping dates do not merge.
- Annual summary versus daily/weekly update is treated as related/not merged rather than duplicate.

Count semantics compatibility:

- Cumulative, annual, weekly, newly reported, historical total, subset, and unspecified count semantics are not merged aggressively.
- Incompatible semantics can create `related_records` and human review items.
- Missing semantics can create reviewable related clusters instead of silent duplicate suppression.

Count value compatibility:

- Identical count signatures for compatible disease/location/date records are duplicate candidates.
- Conflicting count values for the same disease/location/date create `conflict_needs_review`.
- Conflicting records remain auditable and are not silently dropped.

Source/provenance compatibility:

- Same source URL and same evidence chunk can mark repeated extraction as duplicate.
- Official and secondary/news reports with the same disease/location/date/count can cluster, with the official source selected as representative.
- Source IDs, URLs, evidence quotes, publishers, source roles, and credibility scores remain on all records.

Evidence similarity:

- Stage 9 uses lightweight deterministic provenance and count/date/location matching.
- It does not add heavy similarity dependencies.

Unsafe merge prevention:

- Different diseases do not merge.
- Incompatible locations do not merge.
- Incompatible dates do not merge.
- Incompatible count semantics are related/reviewed rather than deduplicated.

## 5. Countable records

Every record receives a `countable` flag.

Singleton clusters:

- `countable = true`
- `event_member_status = singleton`

Duplicate clusters:

- Representative record: `countable = true`
- Non-countable duplicate records: `countable = false`
- Duplicate records point to `duplicate_of_record_id`

Related records:

- `countable = true` by default
- `event_member_status = related_not_merged`
- Human review may be required when count semantics or aggregation levels are ambiguous

Conflicting records:

- Kept countable by default unless duplicate confidence is high enough to suppress counting
- Routed to human review with explicit conflict reasons

## 6. Human review routing

Stage 9 adds human review items for:

- same disease/location/date with conflicting counts
- high duplicate suspicion but unclear count semantics
- cumulative versus newly reported ambiguity
- annual summary versus single update ambiguity
- related aggregate/subset ambiguity
- same source producing multiple potentially overlapping records
- representative selection uncertainty when needed

Review items include:

- `event_cluster_id`
- `member_record_ids`
- `representative_record_id`
- reason
- suggested action
- source IDs and URLs
- count comparison summary

Stage 9 does not apply human review decisions.

## 7. Backward compatibility

Existing `linked_events` remain available. `event_cluster_id` maps to `linked_event_id` for compatibility.

Existing New Mexico/Hantavirus records remain compatible. `HantavirusRecord` remains available, and `PublicHealthRecord` keeps legacy fields while adding clustering fields.

## 8. What changes after Stage 9

After Stage 9:

- all normalized records get `event_cluster_id`
- all normalized records get `countable`
- duplicate records can be marked `countable=false`
- final package exports event clusters and duplicate clusters
- workflow summaries include event clustering and duplicate detection summaries
- generic COVID-19, dengue, and hantavirus records use the same clustering logic

## 9. What is still not implemented

Stage 9 does not implement:

- validation refactor
- trusted-source validation
- cross-source validation refactor
- anomaly detection
- human review decision application
- CLI redesign
- notebook redesign
- UI redesign
- uncontrolled crawling
- broad source expansion
