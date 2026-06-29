# Human Review Priority Summary

## 1. Review status

- Session: `goal_round04_norovirus_us_2024_12_2025_02`
- Task: Norovirus / United States / 2024-12-01 to 2025-02-28
- Run quality status: `partial_with_quarantined_records`
- Primary case dataset status: `no_primary_case_dataset_records`
- Review items in queue: `81`
- Prioritized items generated: `81`

## 2. Priority counts

```json
{
  "P0_critical": 0,
  "P1_high": 38,
  "P2_medium": 0,
  "P3_low": 43
}
```

## 3. Top review items

| Rank | Priority | Category | Title | Action |
|---:|---|---|---|---|
| 1 | P1_high | claim_corroboration_review | claim corroboration review - review_claim_corroboration_review_corr_event_005 - US noro... | review_claim_corroboration |
| 2 | P1_high | source_identity_review | source identity review - review_source_credibility_src_search_3b4e2043d3a5 - Norovirus... | Open source identity assessments and source registry metadata. |
| 3 | P1_high | source_identity_review | source identity review - review_source_credibility_src_search_926b43baa66c - WDEF News... | Open source identity assessments and source registry metadata. |
| 4 | P1_high | source_identity_review | source identity review - review_source_credibility_src_search_e119c616592e - Norovirus... | Open source identity assessments and source registry metadata. |
| 5 | P1_high | claim_corroboration_review | claim corroboration review - review_duplicate_event_001 - CDC: 2024-2025 seasonal norov... | Open claims, claim comparisons, and corroborated events. |
| 6 | P1_high | claim_corroboration_review | claim corroboration review - review_duplicate_event_004 - Staying Healthy: Norovirus In... | Open claims, claim comparisons, and corroborated events. |
| 7 | P1_high | claim_corroboration_review | claim corroboration review - review_duplicate_event_005 - US norovirus outbreaks are up... | Open claims, claim comparisons, and corroborated events. |
| 8 | P1_high | claim_corroboration_review | claim corroboration review - review_duplicate_event_007 - Norovirus outbreaks surging a... | Open claims, claim comparisons, and corroborated events. |
| 9 | P1_high | claim_corroboration_review | claim corroboration review - review_duplicate_event_008 - Norovirus outbreaks surging a... | Open claims, claim comparisons, and corroborated events. |
| 10 | P1_high | claim_corroboration_review | claim corroboration review - review_duplicate_event_009 - Norovirus Outbreaks - CDC | Open claims, claim comparisons, and corroborated events. |

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
