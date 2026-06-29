# Human Review Priority Summary

## 1. Review status

- Session: `goal_round02_west_nile_california_2024_08`
- Task: West Nile virus / California / 2024-08-01 to 2024-08-31
- Run quality status: `no_primary_case_dataset_records`
- Primary case dataset status: `no_primary_case_dataset_records`
- Review items in queue: `157`
- Prioritized items generated: `157`

## 2. Priority counts

```json
{
  "P0_critical": 76,
  "P1_high": 44,
  "P2_medium": 9,
  "P3_low": 28
}
```

## 3. Top review items

| Rank | Priority | Category | Title | Action |
|---:|---|---|---|---|
| 1 | P0_critical | primary_case_dataset_blocker | primary case dataset blocker - review_linking_event_008 - 2024 Mosquito-Borne Disease Y... | Inspect the record, evidence quote, source identity, and quality-gate reasons before ed... |
| 2 | P0_critical | primary_case_dataset_blocker | primary case dataset blocker - review_linking_event_014 - Westnile.ca.gov / California... | Inspect the record, evidence quote, source identity, and quality-gate reasons before ed... |
| 3 | P0_critical | primary_case_dataset_blocker | primary case dataset blocker - review_linking_event_016 - Westnile.ca.gov / California... | Inspect the record, evidence quote, source identity, and quality-gate reasons before ed... |
| 4 | P0_critical | primary_case_dataset_blocker | primary case dataset blocker - review_linking_event_019 - WEEKLY UPDATE - California We... | Inspect the record, evidence quote, source identity, and quality-gate reasons before ed... |
| 5 | P0_critical | primary_case_dataset_blocker | primary case dataset blocker - review_linking_event_023 - Westnile.ca.gov / California... | Inspect the record, evidence quote, source identity, and quality-gate reasons before ed... |
| 6 | P0_critical | primary_case_dataset_blocker | primary case dataset blocker - review_linking_event_024 - West Nile virus death confirm... | Inspect the record, evidence quote, source identity, and quality-gate reasons before ed... |
| 7 | P0_critical | primary_case_dataset_blocker | primary case dataset blocker - review_linking_event_027 - West Nile virus death confirm... | Inspect the record, evidence quote, source identity, and quality-gate reasons before ed... |
| 8 | P0_critical | primary_case_dataset_blocker | primary case dataset blocker - review_linking_event_033 - West Nile virus death confirm... | Inspect the record, evidence quote, source identity, and quality-gate reasons before ed... |
| 9 | P0_critical | primary_case_dataset_blocker | primary case dataset blocker - review_linking_event_036 - West Nile virus, spread by mo... | Inspect the record, evidence quote, source identity, and quality-gate reasons before ed... |
| 10 | P0_critical | primary_case_dataset_blocker | primary case dataset blocker - review_normalization_rec_src_search_14d0fc5d0793_001 - W... | Inspect the record, evidence quote, source identity, and quality-gate reasons before ed... |

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
