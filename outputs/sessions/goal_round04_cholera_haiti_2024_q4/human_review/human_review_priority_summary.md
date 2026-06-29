# Human Review Priority Summary

## 1. Review status

- Session: `goal_round04_cholera_haiti_2024_q4`
- Task: Cholera / Haiti / 2024-10-01 to 2024-12-31
- Run quality status: `human_review_required`
- Primary case dataset status: `no_corroborated_primary_case_events`
- Review items in queue: `36`
- Prioritized items generated: `36`

## 2. Priority counts

```json
{
  "P0_critical": 2,
  "P1_high": 9,
  "P2_medium": 1,
  "P3_low": 24
}
```

## 3. Top review items

| Rank | Priority | Category | Title | Action |
|---:|---|---|---|---|
| 1 | P0_critical | conflicting_claims_review | conflicting claims review - review_claim_corroboration_conflict_corr_event_001 - [PDF]... | review_claim_corroboration |
| 2 | P0_critical | validation_conflict_review | validation conflict review - review_duplicate_event_001 - [PDF] Multi-country outbreak... | Inspect the linked artifacts and only then edit a decision file if needed. |
| 3 | P1_high | claim_corroboration_review | claim corroboration review - review_anomaly_anom_003 - event_001 | review_cluster_canonical_count |
| 4 | P1_high | source_identity_review | source identity review - review_source_credibility_src_search_4f1e08e3f365 - Haïti : La... | Open source identity assessments and source registry metadata. |
| 5 | P1_high | source_identity_review | source identity review - review_source_credibility_src_search_505b2ac21551 - An Update... | Open source identity assessments and source registry metadata. |
| 6 | P1_high | source_identity_review | source identity review - review_source_credibility_src_search_5b9b31558c67 - Haiti Coun... | Open source identity assessments and source registry metadata. |
| 7 | P1_high | source_identity_review | source identity review - review_source_credibility_src_search_664c22f9e3a2 - Éliminatio... | Open source identity assessments and source registry metadata. |
| 8 | P1_high | source_identity_review | source identity review - review_source_credibility_src_search_8929f93c6a7e - Multi-Coun... | Open source identity assessments and source registry metadata. |
| 9 | P1_high | source_identity_review | source identity review - review_source_credibility_src_search_a0ed0f2ccd87 - Cholera, H... | Open source identity assessments and source registry metadata. |
| 10 | P1_high | source_identity_review | source identity review - review_source_credibility_src_search_bd6f7e5cf18e - 2 February... | Open source identity assessments and source registry metadata. |

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
