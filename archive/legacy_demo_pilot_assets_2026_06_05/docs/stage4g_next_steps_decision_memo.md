# Stage 4G Next Steps Decision Memo

## Option A — Prepare meeting only and pause implementation

- Benefit: Preserves the current clean narrative and avoids introducing new moving parts before supervisor review.
- Effort: Low.
- Risk: Low; no new technical risk.
- Recommendation: Recommended for this week.
- Professor approval needed: Confirm that the current Stage 0-4F narrative is sufficient for the meeting.

## Option B — Add deterministic pattern support for spelled-out annual counts

- Benefit: Makes the New Mexico annual count reproducible without LLM extraction for this pattern.
- Effort: Medium.
- Risk: Medium; overly broad patterns can create false positives.
- Recommendation: Good next implementation if the priority is deterministic reproducibility.
- Professor approval needed: Confirm that deterministic extraction should be strengthened before more LLM integration.

## Option C — Add validation PDF/OCR support

- Benefit: Reduces reliance on manually curated ground truth and supports richer held-out validation.
- Effort: High.
- Risk: High; OCR errors and PDF table parsing can affect validation quality.
- Recommendation: Valuable, but should be scoped carefully after the meeting.
- Professor approval needed: Confirm whether validation automation is more important than expanding source coverage.

## Option D — Expand to another real-source hantavirus scenario

- Benefit: Tests whether the workflow generalizes beyond New Mexico HPS.
- Effort: Medium to high.
- Risk: Medium; source availability and validation data may vary.
- Recommendation: Strong next step if supervisors want external validity.
- Professor approval needed: Select the next geography/source scenario and acceptable validation source.

## Option E — Integrate LLM extraction into full live workflow

- Benefit: Moves from replay to end-to-end controlled hybrid extraction.
- Effort: Medium.
- Risk: Medium to high; needs strict source-role enforcement and cost controls.
- Recommendation: Do only after supervisor approval.
- Professor approval needed: Approve when and how LLM extraction may run in live workflows.

## Recommendation

For this week: prepare the meeting and pause implementation. After the meeting, decide whether to prioritize deterministic extraction reproducibility, PDF/OCR, or broader real-source expansion.
