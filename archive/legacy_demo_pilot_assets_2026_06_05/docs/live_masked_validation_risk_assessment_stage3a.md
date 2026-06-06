# Live Masked Validation Risk Assessment — Stage 3A

## 1. Summary

The first live masked validation pilot should be small, explicitly allowlisted, and conservative. The main risks are leakage from held-out validation sources into collection, semantic dependence when a collection source quotes a validation source, non-comparable counts, unstable live pages, and overclaiming. Stage 3A does not run live fetch; it defines controls for Stage 3B.

## 2. Leakage risks

### Technical leakage

Technical leakage occurs if a reserved URL, source ID, or domain is fetched during the collection phase. The mitigation is explicit `validation_reserved` source IDs, collection blocking before fetch, and a post-run assertion that no reserved source ID appears in collection `final_dataset`.

### Semantic leakage

Semantic leakage occurs when a non-held-out source quotes or summarizes a held-out validation source. Candidate 1 has this risk because the Reuters article explicitly cites WHO. This does not necessarily make the pilot invalid, but it means the result should be described as source-masked collection with semantic leakage risk, not fully independent validation.

### Analytic leakage

Analytic leakage occurs if ground truth is used to tune extraction prompts, source selection, or normalization rules before evaluation. Stage 3B should freeze the collection extraction setup before inspecting held-out validation results. If manual ground truth is curated, it should be used only after collection output is exported.

## 3. Source reliability risks

Official sources such as WHO, CDC, VDH, and NMDOH are generally stronger for validation or authoritative context. News sources can be useful collection sources, but they may depend on official releases and may update, summarize, or omit details. Context pages may mention outbreaks without providing extractable case/death records.

## 4. Data comparability risks

- Cumulative, annual, outbreak-specific, and newly reported counts must not be compared as if they are the same count type.
- Confirmed, probable, suspected, and unspecified cases may not be equivalent.
- Deaths among confirmed cases may differ from deaths among all reported cases.
- Event date and report date can differ, especially for an evolving outbreak.
- Country, ship, multi-country, state, and county locations may represent different aggregation levels.
- Candidate 1 may compare WHO counts as of 8 May 2026 with Reuters counts as of 27 May 2026, which may be an evolving count rather than a true conflict.
- Candidate 2 may mix current press-release cases with prior-year state aggregates.

## 5. Technical risks

- HTML parsing may fail if pages have unusual structure.
- PDF parsing and OCR are not implemented.
- JavaScript-rendered pages may not expose source text to the current fetch/parser path.
- Live pages may change after the pilot is designed.
- Evidence quote extraction may capture too much or too little context.
- Broad web search is not implemented, so the first live pilot must use an explicit allowlist.

## 6. Recommended conservative controls

- Use a source allowlist for the first live pilot.
- Use explicit reserved source IDs for held-out validation.
- Do not fetch validation sources during collection.
- Retain `source_url`, `evidence_quote`, `supporting_chunk_id`, and `linked_event_id`.
- Use a manually curated `ground_truth_records.csv` for the first live validation comparison if automated validation parsing is risky.
- Route `not_comparable`, mismatch, missing collection, missing validation, and leakage rows to human review.
- Do not use LLM extraction in the first live attempt unless deterministic extraction fails and supervisors approve a second pass.
- Freeze source snapshots where possible, or at minimum record retrieval dates and source URLs.
- Keep professor-facing reports clear that this is a controlled pilot, not a production surveillance system.
