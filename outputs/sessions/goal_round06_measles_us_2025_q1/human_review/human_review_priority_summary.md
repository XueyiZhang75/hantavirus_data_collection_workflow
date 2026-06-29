# Human Review Priority Summary

## 1. Review status

- Session: `goal_round06_measles_us_2025_q1`
- Task: Measles / United States / 2025-01-01 to 2025-03-31
- Run quality status: `partial_with_quarantined_records`
- Primary case dataset status: `no_primary_case_dataset_records`
- Review items in queue: `119`
- Prioritized items generated: `119`

## 2. Priority counts

```json
{
  "P0_critical": 44,
  "P1_high": 46,
  "P2_medium": 2,
  "P3_low": 27
}
```

## 3. Top review items

| Rank | Priority | Category | Title | Action |
|---:|---|---|---|---|
| 1 | P0_critical | primary_case_dataset_blocker | primary case dataset blocker - review_linking_event_006 - Measles Cases Surge in 2025:... | Inspect the record, evidence quote, source identity, and quality-gate reasons before ed... |
| 2 | P0_critical | primary_case_dataset_blocker | primary case dataset blocker - review_normalization_rec_src_search_b285c8bbed4b_001 - M... | Inspect the record, evidence quote, source identity, and quality-gate reasons before ed... |
| 3 | P0_critical | conflicting_claims_review | conflicting claims review - review_claim_corroboration_conflict_corr_event_002 - Over 2... | review_claim_corroboration |
| 4 | P0_critical | possible_primary_case_evidence | possible primary case evidence - review_duplicate_event_001 - Situation Report #2: Meas... | Inspect corroboration and source identity before deciding whether a structured human de... |
| 5 | P0_critical | possible_primary_case_evidence | possible primary case evidence - review_duplicate_event_002 - Over 2K measles cases rep... | Inspect corroboration and source identity before deciding whether a structured human de... |
| 6 | P0_critical | possible_primary_case_evidence | possible primary case evidence - review_duplicate_event_003 - Measles Update — United S... | Inspect corroboration and source identity before deciding whether a structured human de... |
| 7 | P0_critical | possible_primary_case_evidence | possible primary case evidence - review_duplicate_event_004 - CDC Records Two New Measl... | Inspect corroboration and source identity before deciding whether a structured human de... |
| 8 | P0_critical | possible_primary_case_evidence | possible primary case evidence - review_duplicate_event_005 - Texas Declares Measles Ou... | Inspect corroboration and source identity before deciding whether a structured human de... |
| 9 | P0_critical | possible_primary_case_evidence | possible primary case evidence - review_duplicate_event_006 - Measles Cases Surge in 20... | Inspect corroboration and source identity before deciding whether a structured human de... |
| 10 | P0_critical | possible_primary_case_evidence | possible primary case evidence - review_duplicate_event_007 - Measles Update — United S... | Inspect corroboration and source identity before deciding whether a structured human de... |

## 4. Why these items matter

P0/P1 items are listed first because they may affect primary case dataset inclusion, source identity, validation limits, or claim corroboration. Validation-limited items do not prove a negative finding; they tell the reviewer that held-out validation coverage needs inspection.

## 5. Suggested review workflow

1. Open `human_review/top_review_items.csv` and review P0/P1 rows first.
2. Use `recommended_artifacts_to_open` to inspect source, record, claim, anomaly, and validation evidence.
3. Copy `human_review/review_decision_prefill.json` to a working decision file.
4. Edit reviewer metadata, target IDs, decision type, reason, notes, and patches only after human review.
5. Set `apply_decision=true` only for explicit decisions the reviewer wants to apply.
6. Re-run the workflow with the existing decision-application mechanism and inspect post-review outputs.

## 6. Decision file instructions

`review_decision_template.json` and `review_decision_prefill.json` are templates only. Every generated decision keeps `apply_decision=false` by default. Optimization 6 does not approve, reject, correct, or determine truth automatically.

## 7. Key artifacts

- `human_review/human_review_priority_summary.json`
- `human_review/top_review_items.csv`
- `human_review/top_review_items.json`
- `human_review/review_decision_template.json`
- `human_review/review_decision_prefill.json`
- `human_review/review_packet_index.json`
- `human_review/review_action_guide.md`

## 8. Boundaries

This artifact is generated from existing session outputs only. It does not call LLMs, search the web, fetch pages, apply human review decisions, provide medical advice, or make official surveillance conclusions.
