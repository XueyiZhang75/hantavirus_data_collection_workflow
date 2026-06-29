# Human Review Priority Summary

## 1. Review status

- Session: `goal_round08_flu_united_states_2024_09_29_2024_10_05`
- Task: Influenza / United States / 2024-09-29 to 2024-10-05
- Run quality status: `partial_with_quarantined_records`
- Primary case dataset status: `no_primary_case_dataset_records`
- Review items in queue: `29`
- Prioritized items generated: `29`

## 2. Priority counts

```json
{
  "P0_critical": 0,
  "P1_high": 9,
  "P2_medium": 0,
  "P3_low": 20
}
```

## 3. Top review items

| Rank | Priority | Category | Title | Action |
|---:|---|---|---|---|
| 1 | P1_high | claim_corroboration_review | claim corroboration review - review_claim_corroboration_review_corr_event_002 - Weekly... | review_claim_corroboration |
| 2 | P1_high | claim_corroboration_review | claim corroboration review - review_duplicate_event_001 - Weekly US Influenza Surveilla... | Open claims, claim comparisons, and corroborated events. |
| 3 | P1_high | claim_corroboration_review | claim corroboration review - review_duplicate_event_002 - Weekly US Influenza Surveilla... | Open claims, claim comparisons, and corroborated events. |
| 4 | P1_high | claim_corroboration_review | claim corroboration review - review_duplicate_event_003 - Weekly US Influenza Surveilla... | Open claims, claim comparisons, and corroborated events. |
| 5 | P1_high | claim_corroboration_review | claim corroboration review - review_duplicate_event_004 - Weekly US Influenza Surveilla... | Open claims, claim comparisons, and corroborated events. |
| 6 | P1_high | claim_corroboration_review | claim corroboration review - review_duplicate_event_005 - Weekly US Influenza Surveilla... | Open claims, claim comparisons, and corroborated events. |
| 7 | P1_high | claim_corroboration_review | claim corroboration review - review_duplicate_event_006 - Weekly US Influenza Surveilla... | Open claims, claim comparisons, and corroborated events. |
| 8 | P1_high | claim_corroboration_review | claim corroboration review - review_duplicate_event_007 - Weekly US Influenza Surveilla... | Open claims, claim comparisons, and corroborated events. |
| 9 | P1_high | source_identity_review | source identity review - review_source_credibility_src_search_50b73d583e75 - US CDC say... | Open source identity assessments and source registry metadata. |
| 10 | P3_low | general_review | general review - review_core_metric_gap_src_search_1b15a2673061 - Regional Update, Infl... | review_source_for_core_metric_extraction |

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
