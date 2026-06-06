# Stage 3C Next Experiment Decision Matrix

## Compact Comparison

| Option | Expected benefit | Implementation effort | Risk | Addresses Reuters failure? | Addresses VDH context-only records? | Improves independence from WHO? | Suitable before next professor meeting? | Recommendation |
|---|---|---:|---|---|---|---|---|---|
| A. Add context-only extraction guardrail | Prevents context-only pages from becoming collection records unless explicitly allowed. Clarifies source-role semantics. | Medium | Could suppress useful data from context pages if too strict. Needs careful diagnostics. | No | Yes | No direct effect | Yes, if scoped narrowly | High |
| B. Try LLM extraction on current MV Hondius sources | May parse messy live pages and extract richer structure from VDH or accessible text. | Medium to high | Adds cost, secret/config risk, and may overfit before policy guardrails are fixed. | No, because Reuters text is access/quality-limited | Partially, but may worsen false positives without guardrail | No | No | Low |
| C. Find another non-held-out MV Hondius collection source | Could provide a usable collection source after Reuters limitation. | Medium | Requires new source review and possible semantic leakage audit. Could drift into broad search if not controlled. | Yes | Indirectly | Maybe, depending on source | Maybe | Medium |
| D. Switch to New Mexico backup case | Likely cleaner accessible official collection sources and lower semantic leakage. | Medium to high | New case design/implementation needed; validation alignment must be defined. | Yes, by avoiding Reuters | Yes, by using better role design | Likely yes | Maybe, if time allows | Medium |
| E. Present Stage 3B as diagnostic pilot only | Fastest and honest: shows source masking works and identifies next engineering gap. | Low | Does not advance extraction performance. May look negative unless framed clearly. | Documents it | Documents it | No | Yes | High |

## Final Recommendation

Recommended path:

1. Present Stage 3B as a diagnostic pilot for the professor meeting.
2. Do not add LLM extraction yet.
3. Next implementation should be Stage 3D: add a context-only extraction guardrail and rerun MV Hondius, unless professors prefer switching to the New Mexico backup case for cleaner independent sources.

## Rationale

Stage 3B already proved the most important safety property: WHO DON600 was registered, held out, blocked from content fetch, and did not leak into collection records. The failure mode is not masking. The failure mode is that Reuters did not provide usable article text, and VDH, despite being intended as context-only, was classified and processed as data extraction.

Adding LLM extraction now would put a more flexible extractor on top of an unresolved source-role policy gap. That is the wrong order. The conservative path is to first make the source-role intent enforceable or at least visible in evaluation warnings.

## What To Ask Professors Before Proceeding

- Should context-only sources be strictly prevented from producing collection records?
- Is the current Stage 3B negative/diagnostic result acceptable for the next meeting?
- Do they prefer hardening the MV Hondius pilot or switching to the New Mexico backup case?
- Are news sources acceptable if they cite WHO or other validation sources?
- Should a future LLM pass be used only after source-role guardrails are in place?
