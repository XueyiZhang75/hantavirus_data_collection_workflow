# Human Review Priority Summary

## 1. Review status

- Session: `goal_round05_legionnaires_nyc_2025_08`
- Task: Legionnaires' disease / New York City / 2025-08-01 to 2025-08-31
- Run quality status: `partial_with_quarantined_records`
- Primary case dataset status: `no_primary_case_dataset_records`
- Review items in queue: `79`
- Prioritized items generated: `79`

## 2. Priority counts

```json
{
  "P0_critical": 18,
  "P1_high": 25,
  "P2_medium": 0,
  "P3_low": 36
}
```

## 3. Top review items

| Rank | Priority | Category | Title | Action |
|---:|---|---|---|---|
| 1 | P0_critical | conflicting_claims_review | conflicting claims review - review_claim_corroboration_conflict_corr_event_001 - NYC Le... | review_claim_corroboration |
| 2 | P0_critical | conflicting_claims_review | conflicting claims review - review_claim_corroboration_conflict_corr_event_002 - Three... | review_claim_corroboration |
| 3 | P0_critical | conflicting_claims_review | conflicting claims review - review_claim_corroboration_conflict_corr_event_004 - Legion... | review_claim_corroboration |
| 4 | P0_critical | possible_primary_case_evidence | possible primary case evidence - review_duplicate_event_001 - 2025 Legionnaires’ Diseas... | Inspect corroboration and source identity before deciding whether a structured human de... |
| 5 | P0_critical | possible_primary_case_evidence | possible primary case evidence - review_duplicate_event_002 - 2025 Legionnaires’ Diseas... | Inspect corroboration and source identity before deciding whether a structured human de... |
| 6 | P0_critical | possible_primary_case_evidence | possible primary case evidence - review_duplicate_event_016 - Legionnaires’ outbreak ki... | Inspect corroboration and source identity before deciding whether a structured human de... |
| 7 | P0_critical | possible_primary_case_evidence | possible primary case evidence - review_duplicate_event_017 - Legionnaires’ outbreak ki... | Inspect corroboration and source identity before deciding whether a structured human de... |
| 8 | P0_critical | validation_conflict_review | validation conflict review - review_anomaly_anom_014 - NYC Health Department Provides U... | resolve_validation_conflict |
| 9 | P0_critical | validation_conflict_review | validation conflict review - review_duplicate_event_003 - NYC Legionnaires Outbreak 6 D... | Inspect the linked artifacts and only then edit a decision file if needed. |
| 10 | P0_critical | validation_conflict_review | validation conflict review - review_duplicate_event_004 - NYC Health Department Investi... | Inspect the linked artifacts and only then edit a decision file if needed. |

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
