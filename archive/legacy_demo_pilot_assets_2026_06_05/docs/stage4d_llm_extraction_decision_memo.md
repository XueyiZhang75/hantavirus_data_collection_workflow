# Stage 4D LLM Extraction Decision Memo

## 1. Decision point

Stage 4C showed that source masking, live fetch, and context-only guardrails worked, but deterministic extraction did not produce a collection record aligned with the held-out 2025 annual ground truth. Stage 4D decides whether controlled LLM extraction is justified before changing workflow code.

The audit confirms the relevant 2025 annual phrase is present in fetched evidence, so controlled LLM extraction is now technically justified as a narrow Stage 4E experiment.

## 2. Option A - Controlled LLM extraction on already-fetched NMDOH text

- Expected benefit: tests whether an LLM can map "seven cases in 2025" and "three of them fatal" into structured `reporting_period`, `cases_unspecified`, and `deaths`.
- Implementation effort: medium.
- Risk: medium; must prevent hallucinated counts and keep validation-reserved source blocked.
- Addresses no-count extraction: yes.
- Addresses annual-vs-event scope mismatch: partially; only if prompt/schema asks for annual summary extraction.
- Suitable before professor meeting: medium; useful if run as a carefully labeled controlled comparison.
- Recommendation level: high.

## 3. Option B - Improve deterministic extraction

- Expected benefit: makes the pipeline more explainable and reduces reliance on external LLMs.
- Implementation effort: medium to high.
- Risk: low to medium; regex/pattern expansion may overfit to NMDOH phrasing.
- Addresses no-count extraction: yes, if spelled-out counts and fatality phrases are added.
- Addresses annual-vs-event scope mismatch: partially.
- Suitable before professor meeting: medium; may require more test design.
- Recommendation level: medium.

## 4. Option C - Improve normalization/linking/evaluation alignment

- Expected benefit: improves comparison between annual validation records and event-level collection records.
- Implementation effort: medium.
- Risk: medium; careless alignment could create false matches between different statistical scopes.
- Addresses no-count extraction: no.
- Addresses annual-vs-event scope mismatch: yes.
- Suitable before professor meeting: medium.
- Recommendation level: medium.

## 5. Option D - PDF/OCR support later

- Expected benefit: enables direct parsing of NMDOH county/year validation source.
- Implementation effort: high.
- Risk: medium; PDF layout/OCR errors could degrade ground truth quality.
- Addresses no-count extraction: no for collection HTML.
- Addresses annual-vs-event scope mismatch: no, but improves validation automation.
- Suitable before professor meeting: low.
- Recommendation level: low for now.

## 6. Option E - Present diagnostic result first

- Expected benefit: communicates a clean engineering result: source masking passed, live fetch worked, extraction limitations are visible and measurable.
- Implementation effort: low.
- Risk: low, as long as claims are conservative.
- Addresses no-count extraction: no.
- Addresses annual-vs-event scope mismatch: no.
- Suitable before professor meeting: high.
- Recommendation level: high for meeting readiness.

## 7. Recommendation

Recommended next technical stage: `Stage 4E - Controlled LLM extraction on already-fetched New Mexico HTML text`.

Recommended meeting posture: present Stage 4C/4D as a diagnostic real-source pilot first, then propose Stage 4E as a controlled comparison. Do not claim that Stage 4C achieved epidemiological validation; claim that it successfully isolated the next bottleneck.

Implementation constraints for Stage 4E should be:

- no broad web search;
- no validation-reserved PDF fetch;
- use only allowlisted New Mexico collection HTML text;
- keep deterministic extraction as baseline;
- require provenance and short evidence quotes;
- label the run as experimental LLM extraction, not final validation.

## 8. Questions for professors

1. Should annual surveillance summaries from press releases be considered comparable to the held-out county/year ground truth?
2. Should the next demo prioritize controlled LLM extraction accuracy or deterministic reproducibility?
3. Is manual ground truth acceptable for the pilot phase, or should PDF/OCR be prioritized before further extraction work?
4. What level of human review is acceptable when event-level sources contain annual summary sentences?
