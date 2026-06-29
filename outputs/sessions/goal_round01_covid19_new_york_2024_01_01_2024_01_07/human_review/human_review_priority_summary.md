# Human Review Priority Summary

## 1. Review status

- Session: `goal_round01_covid19_new_york_2024_01_01_2024_01_07`
- Task: COVID-19 / New York / 2024-01-01 to 2024-01-07
- Run quality status: `no_records_extracted`
- Primary case dataset status: `unknown_no_claim_outputs`
- Review items in queue: `41`
- Prioritized items generated: `41`

## 2. Priority counts

```json
{
  "P0_critical": 0,
  "P1_high": 13,
  "P2_medium": 0,
  "P3_low": 28
}
```

## 3. Top review items

| Rank | Priority | Category | Title | Action |
|---:|---|---|---|---|
| 1 | P1_high | source_identity_review | source identity review - review_source_credibility_src_search_b11655490f96 - How did CO... | Open source identity assessments and source registry metadata. |
| 2 | P1_high | source_identity_review | source identity review - review_source_credibility_src_search_d5900bb8aa62 - COVID-19 p... | Open source identity assessments and source registry metadata. |
| 3 | P1_high | source_identity_review | source identity review - review_source_credibility_src_search_f1a19efce8d2 - New York S... | Open source identity assessments and source registry metadata. |
| 4 | P1_high | source_identity_review | source identity review - review_source_credibility_src_search_000e4ff17a91 - GitHub - n... | Open source identity assessments and source registry metadata. |
| 5 | P1_high | source_identity_review | source identity review - review_source_credibility_src_search_0af03f2493e8 - COVID-19 D... | Open source identity assessments and source registry metadata. |
| 6 | P1_high | source_identity_review | source identity review - review_source_credibility_src_search_478ca202141b - United Sta... | Open source identity assessments and source registry metadata. |
| 7 | P1_high | source_identity_review | source identity review - review_source_credibility_src_search_58fde24d715b - Track Covi... | Open source identity assessments and source registry metadata. |
| 8 | P1_high | source_identity_review | source identity review - review_source_credibility_src_search_5ce266c03958 - COVID / NY... | Open source identity assessments and source registry metadata. |
| 9 | P1_high | source_identity_review | source identity review - review_source_credibility_src_search_650359dcfc71 - COVID-19 D... | Open source identity assessments and source registry metadata. |
| 10 | P1_high | source_identity_review | source identity review - review_source_credibility_src_search_68678448bb04 - New York -... | Open source identity assessments and source registry metadata. |

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
