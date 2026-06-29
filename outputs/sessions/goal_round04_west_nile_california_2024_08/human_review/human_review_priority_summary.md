# Human Review Priority Summary

## 1. Review status

- Session: `goal_round04_west_nile_california_2024_08`
- Task: West Nile virus / California / 2024-08-01 to 2024-08-31
- Run quality status: `partial_with_quarantined_records`
- Primary case dataset status: `primary_case_records_present`
- Review items in queue: `95`
- Prioritized items generated: `95`

## 2. Priority counts

```json
{
  "P0_critical": 17,
  "P1_high": 45,
  "P2_medium": 0,
  "P3_low": 33
}
```

## 3. Top review items

| Rank | Priority | Category | Title | Action |
|---:|---|---|---|---|
| 1 | P0_critical | conflicting_claims_review | conflicting claims review - review_claim_corroboration_conflict_corr_event_001 - Arbobu... | review_claim_corroboration |
| 2 | P0_critical | primary_case_dataset_blocker | primary case dataset blocker - review_linking_event_010 - 2024 Mosquito-Borne Disease Y... | Inspect the record, evidence quote, source identity, and quality-gate reasons before ed... |
| 3 | P0_critical | primary_case_dataset_blocker | primary case dataset blocker - review_linking_event_011 - Westnile.ca.gov / California... | Inspect the record, evidence quote, source identity, and quality-gate reasons before ed... |
| 4 | P0_critical | primary_case_dataset_blocker | primary case dataset blocker - review_linking_event_016 - Arbobulletin_2024_29.pdf | Inspect the record, evidence quote, source identity, and quality-gate reasons before ed... |
| 5 | P0_critical | primary_case_dataset_blocker | primary case dataset blocker - review_normalization_rec_src_search_99932da268a1_001 - 2... | Inspect the record, evidence quote, source identity, and quality-gate reasons before ed... |
| 6 | P0_critical | primary_case_dataset_blocker | primary case dataset blocker - review_normalization_rec_src_search_a39e4fa28013_003 - A... | Inspect the record, evidence quote, source identity, and quality-gate reasons before ed... |
| 7 | P0_critical | primary_case_dataset_blocker | primary case dataset blocker - review_normalization_rec_src_search_fc3322f3069f_001 - W... | Inspect the record, evidence quote, source identity, and quality-gate reasons before ed... |
| 8 | P0_critical | claim_corroboration_review | claim corroboration review - review_anomaly_anom_004 - Arbobulletin_2024_29.pdf | confirm_scope_or_reject_record |
| 9 | P0_critical | claim_corroboration_review | claim corroboration review - review_anomaly_anom_005 - Health officials report 3 West N... | confirm_scope_or_reject_record |
| 10 | P0_critical | claim_corroboration_review | claim corroboration review - review_anomaly_anom_006 - Health officials report 3 West N... | confirm_scope_or_reject_record |

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
