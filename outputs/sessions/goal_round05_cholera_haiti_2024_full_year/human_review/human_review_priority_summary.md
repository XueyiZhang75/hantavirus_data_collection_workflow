# Human Review Priority Summary

## 1. Review status

- Session: `goal_round05_cholera_haiti_2024_full_year`
- Task: Cholera / Haiti / 2024-01-01 to 2024-12-31
- Run quality status: `failed_quality_gate`
- Primary case dataset status: `no_corroborated_primary_case_events`
- Review items in queue: `42`
- Prioritized items generated: `42`

## 2. Priority counts

```json
{
  "P0_critical": 0,
  "P1_high": 15,
  "P2_medium": 0,
  "P3_low": 27
}
```

## 3. Top review items

| Rank | Priority | Category | Title | Action |
|---:|---|---|---|---|
| 1 | P1_high | claim_corroboration_review | claim corroboration review - review_claim_corroboration_review_corr_event_001 - Cholera... | review_claim_corroboration |
| 2 | P1_high | source_identity_review | source identity review - review_source_credibility_src_search_9551dc7b0b7e - Situation... | Open source identity assessments and source registry metadata. |
| 3 | P1_high | source_identity_review | source identity review - review_source_credibility_src_search_25902466ae28 - UNICEF Hai... | Open source identity assessments and source registry metadata. |
| 4 | P1_high | source_identity_review | source identity review - review_source_credibility_src_search_42c6ab0993b9 - UNICEF Hai... | Open source identity assessments and source registry metadata. |
| 5 | P1_high | source_identity_review | source identity review - review_source_credibility_src_search_52b7f0d4d92b - UNICEF Hai... | Open source identity assessments and source registry metadata. |
| 6 | P1_high | source_identity_review | source identity review - review_source_credibility_src_search_6dc5eabed325 - Water Inse... | Open source identity assessments and source registry metadata. |
| 7 | P1_high | source_identity_review | source identity review - review_source_credibility_src_search_76ddaf069a83 - [PDF] Hait... | Open source identity assessments and source registry metadata. |
| 8 | P1_high | source_identity_review | source identity review - review_source_credibility_src_search_802ab0048156 - Haiti: Cho... | Open source identity assessments and source registry metadata. |
| 9 | P1_high | source_identity_review | source identity review - review_source_credibility_src_search_9aefe8d01e47 - Cholera ou... | Open source identity assessments and source registry metadata. |
| 10 | P1_high | source_identity_review | source identity review - review_source_credibility_src_search_b3f2bb1a4939 - UNICEF Hai... | Open source identity assessments and source registry metadata. |

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
