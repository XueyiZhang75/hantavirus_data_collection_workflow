# Stage 4G Professor Meeting Narrative

## 1. Opening summary

We now have a working, auditable hybrid workflow for hantavirus public-health data collection. The strongest demonstration is New Mexico HPS: real official webpages were fetched, a held-out validation source was blocked, deterministic extraction missed an annual prose count, controlled LLM extraction recovered it, and annual evaluation alignment allowed comparison to held-out ground truth.

## 2. What the professors asked for

The project needed to move beyond a toy workflow and show a credible path toward real public-health data collection. It also needed source separation, validation logic, provenance, and a clear distinction between automation and human review.

## 3. What has been implemented

The repository now includes a LangGraph workflow backbone, deterministic offline defaults, source registry and screening, source masking, context-only guardrails, live-source overlays, masked validation reports, LLM Source Planning Agent, LLM Source Critic Agent, controlled LLM extraction replay, annual comparison alignment, and professor-facing artifacts.

## 4. What the current best demo shows

The New Mexico HPS chain shows that the workflow can fetch real NMDOH pages under explicit controls, prevent the validation source from entering extraction, identify a deterministic extraction miss, recover the annual count with controlled LLM extraction, and compare that count with held-out annual ground truth.

## 5. How agentic AI is now represented

Agentic AI is present in three controlled places: source planning, source critic review, and LLM extraction replay. It is not used to bypass source masking, crawl broadly, scrape validation ground truth, or decide final evaluation status.

## 6. Why guardrails are deterministic

Source masking, context-only blocking, evaluation grouping, provenance checks, and human-review flags remain deterministic so the safety-critical parts of the workflow are inspectable. LLMs can help with semantic reasoning, but the validation boundary is code-enforced.

## 7. What the New Mexico result proves

It proves that controlled LLM extraction can recover a structured annual HPS count from real collection evidence that deterministic extraction missed. It also proves that the masked-validation evaluator can align an annual collection record with held-out validation evidence using `reporting_period`.

## 8. Why human review remains needed

The final annual row is `partial_match_not_comparable`, not `match`, because the case count matched but the validation ground truth has no comparable death field. Human review remains part of the workflow by design when fields are missing, partial, or not comparable.

## 9. What decisions are needed from professors

The main decision is whether to pause implementation for the meeting or continue building. If continuing, professors should choose the priority: deterministic support for spelled-out annual counts, validation PDF/OCR, another real-source hantavirus scenario, controlled broad search, or full workflow integration of LLM extraction.
