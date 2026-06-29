# Human Review Priority Summary

## 1. Review status

- Session: `goal_round03_salmonella_us_2024_05_07`
- Task: Salmonella / United States / 2024-05-01 to 2024-07-31
- Run quality status: `partial_with_quarantined_records`
- Primary case dataset status: `primary_case_records_present`
- Review items in queue: `58`
- Prioritized items generated: `58`

## 2. Priority counts

```json
{
  "P0_critical": 4,
  "P1_high": 22,
  "P2_medium": 0,
  "P3_low": 32
}
```

## 3. Top review items

| Rank | Priority | Category | Title | Action |
|---:|---|---|---|---|
| 1 | P0_critical | conflicting_claims_review | conflicting claims review - review_claim_corroboration_conflict_corr_event_001 - Reoccu... | review_claim_corroboration |
| 2 | P0_critical | validation_conflict_review | validation conflict review - review_anomaly_anom_004 - Reoccurring Salmonella Cotham Ou... | resolve_validation_conflict |
| 3 | P0_critical | validation_conflict_review | validation conflict review - review_anomaly_anom_005 - FoodNet 2024 Preliminary Data /... | resolve_validation_conflict |
| 4 | P0_critical | claim_corroboration_review | claim corroboration review - review_anomaly_anom_003 - Reoccurring Salmonella Cotham Ou... | confirm_scope_or_reject_record |
| 5 | P1_high | validation_conflict_review | validation conflict review - review_duplicate_event_003 - Reoccurring Salmonella Cotham... | Inspect the linked artifacts and only then edit a decision file if needed. |
| 6 | P1_high | claim_corroboration_review | claim corroboration review - review_claim_corroboration_review_corr_event_002 - FoodNet... | review_claim_corroboration |
| 7 | P1_high | source_identity_review | source identity review - review_source_credibility_src_search_15fc5f8d47e2 - Food for T... | Open source identity assessments and source registry metadata. |
| 8 | P1_high | source_identity_review | source identity review - review_source_credibility_src_search_58ef4c36918e - Food Recal... | Open source identity assessments and source registry metadata. |
| 9 | P1_high | source_identity_review | source identity review - review_source_credibility_src_search_793a8dd9911b - Outbreak I... | Open source identity assessments and source registry metadata. |
| 10 | P1_high | claim_corroboration_review | claim corroboration review - review_duplicate_event_004 - Reoccurring Salmonella Cotham... | Open claims, claim comparisons, and corroborated events. |

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
