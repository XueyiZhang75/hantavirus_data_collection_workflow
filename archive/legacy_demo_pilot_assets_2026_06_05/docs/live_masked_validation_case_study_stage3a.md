# Live Masked Validation Case Study Design — Stage 3A

## 1. Purpose

Stage 3A selects and designs the first real-data masked validation case study. It does not run live fetch, call an external LLM, modify workflow code, modify policy files, or change fixture data. The output is a conservative source-selection plan that supervisors can approve before Stage 3B implementation.

Current context from Stage 2D:

- The deterministic fixture system proves that graph execution, source masking, provenance preservation, row-level evaluation, and human review flags work in a controlled offline setting.
- It does not prove real-world epidemiological accuracy, broad web search, automated CDC/ECDC/WHO scraping, or production readiness.
- Stage 3A should design a live case study before running one because the first real-data pilot needs agreed source roles, leakage controls, validation curation strategy, and count-comparability rules.
- Source masking constraints must be preserved: held-out validation sources are registered but blocked from collection, validation records are not mixed into collection output, and leakage or non-comparable results must be flagged for human review.

## 2. Requirements inherited from Stage 2

- Source masking must block held-out validation sources during collection.
- Validation sources must be used only after the collection phase.
- Every extracted record must preserve `source_url`, `evidence_quote`, `supporting_chunk_id`, and `linked_event_id`.
- Mismatch, not comparable, missing collection, missing validation, or source leakage must trigger human review.
- Broad web search is not implemented yet, so the first live pilot should use an explicit source allowlist.
- Validation records may need to be manually curated for the first live pilot if automated parsing is risky.

## 3. Candidate case comparison

| criterion | Candidate 1 MV Hondius | Candidate 2 New Mexico | notes |
|---|---|---|---|
| Official held-out validation source | Strong: WHO DON600 is a clear official held-out validation source. | Mixed: CDC is official but may only align through 2023; NMDOH aggregate PDF/data is not directly available in the current workflow. | Candidate 1 is stronger for proving WHO-held-out validation. |
| Non-held-out collection sources | Reuters and VDH are available, but Reuters cites WHO. | Three NMDOH HTML press releases are available as collection candidates. | Candidate 2 has cleaner official collection sources. |
| HTML accessibility | WHO, Reuters, and VDH are listed as HTML URLs. | NMDOH press releases and CDC page are HTML; aggregate PDF/data candidate has high technical risk. | Candidate 2 is simpler if validation can be curated. |
| Expected numeric fields | Cases and deaths: WHO 8/3 as of 2026-05-08; Reuters 13/3 as of 2026-05-27. | Cases/deaths by state press release and prior-year aggregate statements. | Candidate 1 has event-level outbreak numbers, but evolving counts. |
| Count stability | Low to medium: current 2026 outbreak may update. | Medium to high for historical 2024/2025 press releases; lower for 2026 current case. | Candidate 2 may be more stable if using historical state-level counts. |
| Semantic leakage risk | High for Reuters because the article explicitly cites WHO. | Lower for NMDOH primary press releases. | Candidate 1 needs careful disclosure. |
| PDF/OCR risk | Low if using WHO/Reuters/VDH HTML only. | High if relying on NMDOH aggregate PDF/data as held-out validation. | PDF/OCR is not implemented. |
| Ease of professor demonstration | High: the WHO-held-out story is easy to explain. | Medium: state-level case vs aggregate validation is more nuanced. | Candidate 1 is clearer for source masking. |
| Suitability for first live pilot | Best if the goal is demonstrating WHO held-out validation and leakage controls. | Best as backup or second case if stable extraction is prioritized. | Recommended plan: Candidate 1 primary, Candidate 2 backup. |

## 4. Recommended primary case

Recommended primary candidate for Stage 3B: Candidate 1, the 2026 MV Hondius multi-country hantavirus cluster.

The reason is that it gives the cleanest demonstration of held-out WHO validation: WHO DON600 can be reserved as validation-only, while Reuters can serve as a non-held-out collection source. However, this recommendation is conservative: Reuters explicitly cites WHO, so the pilot should report semantic leakage risk and should not claim independent validation.

Recommended backup: Candidate 2, the New Mexico HPS state-level surveillance / press-release case. It has simpler official HTML collection sources from NMDOH, but its held-out validation path is weaker unless supervisors approve a manually curated NMDOH aggregate validation file or another stable held-out source.

## 5. Proposed source roles for the selected case

### collection_allowed sources

- Source title: Reuters: Hantavirus cases from cruise outbreak rise to 13 following new case in Spain, WHO says
- URL: `https://www.reuters.com/business/healthcare-pharmaceuticals/hantavirus-cases-cruise-outbreak-rise-13-following-new-case-spain-who-says-2026-05-27/`
- Proposed source_id: `src_reuters_mv_hondius_2026_05_27`
- Reason: Non-held-out news source with extractable case and death counts.
- Leakage risk: High semantic leakage risk because it cites WHO.
- Expected fields: cases, deaths, report date, outbreak location, source URL, evidence quote.

### validation_reserved sources

- Source title: WHO Disease Outbreak News: Hantavirus cluster linked to cruise ship travel, Multi-country
- URL: `https://www.who.int/emergencies/disease-outbreak-news/item/2026-DON600`
- Proposed source_id: `src_who_don600_mv_hondius_2026`
- Reason: Official held-out validation source.
- Leakage risk: Low technical leakage risk if source ID is explicitly reserved and blocked during collection.
- Expected fields: cases, deaths, report date, location, case definitions, source URL, evidence quote.

### context_only sources

- Source title: Virginia Department of Health hantavirus page
- URL: `https://www.vdh.virginia.gov/hantavirus/`
- Proposed source_id: `src_vdh_hantavirus_mv_hondius_context`
- Reason: Public health context page mentioning the WHO-notified MV Hondius outbreak.
- Leakage risk: Medium semantic leakage risk if it repeats WHO content.
- Expected fields: disease, context, source URL, evidence quote.

### excluded sources

- Existing reserved sources not part of the selected case should remain out of collection if listed as validation-reserved by policy.
- Broad search endpoints should remain excluded because broad web search is not implemented.
- PDF-only validation sources should be excluded from the first live attempt unless a manual `ground_truth_records.csv` is prepared.

## 6. Proposed source_role_policy extension for live pilot

Do not edit `source_role_policy.json` in Stage 3A. A future Stage 3B case-specific extension could look like this:

```json
{
  "live_case_study_id": "mv_hondius_multicountry_2026",
  "validation_reserved_source_ids": [
    "src_who_don600_mv_hondius_2026"
  ],
  "validation_reserved_domains": [
    "who.int"
  ],
  "collection_allowed_source_ids": [
    "src_reuters_mv_hondius_2026_05_27"
  ],
  "context_only_source_ids": [
    "src_vdh_hantavirus_mv_hondius_context"
  ],
  "notes": "Design proposal only. Reuters is collection-allowed but carries high semantic leakage risk because it cites WHO."
}
```

For the first live pilot, source-ID masking should be preferred over broad domain masking unless supervisors explicitly want to block whole domains.

## 7. Proposed source inventory additions

Do not edit `hantavirus_seed_sources.json` in Stage 3A. Stage 3B could add these seed sources:

### `seed_who_don600_mv_hondius_2026`

- title: `WHO Disease Outbreak News: Hantavirus cluster linked to cruise ship travel, Multi-country`
- url: `https://www.who.int/emergencies/disease-outbreak-news/item/2026-DON600`
- publisher: `WHO`
- source_type: `international_organization_report`
- source_purpose: Held-out validation source for the MV Hondius multi-country hantavirus cluster.
- expected_fields: `["cases", "deaths", "date", "location", "case_definition", "source_url", "source_type", "evidence_quote"]`
- match_terms: `["hantavirus", "MV Hondius", "cruise ship", "multi-country", "WHO"]`
- priority: `1`
- allowed_in_collection: `false`

### `seed_reuters_mv_hondius_2026_05_27`

- title: `Reuters: Hantavirus cases from cruise outbreak rise to 13 following new case in Spain, WHO says`
- url: `https://www.reuters.com/business/healthcare-pharmaceuticals/hantavirus-cases-cruise-outbreak-rise-13-following-new-case-spain-who-says-2026-05-27/`
- publisher: `Reuters`
- source_type: `news_and_situation_report`
- source_purpose: Non-held-out collection source for the MV Hondius case study.
- expected_fields: `["cases", "deaths", "date", "location", "source_url", "source_type", "evidence_quote"]`
- match_terms: `["hantavirus", "cruise outbreak", "Spain", "WHO says"]`
- priority: `2`
- allowed_in_collection: `true`

### `seed_vdh_hantavirus_mv_hondius_context`

- title: `Virginia Department of Health hantavirus page`
- url: `https://www.vdh.virginia.gov/hantavirus/`
- publisher: `Virginia Department of Health`
- source_type: `official_public_health_agency`
- source_purpose: Context source for hantavirus background and possible mention of WHO-notified outbreak.
- expected_fields: `["disease", "virus_or_syndrome", "case_definition", "source_url", "source_type", "evidence_quote"]`
- match_terms: `["hantavirus", "MV Hondius", "WHO"]`
- priority: `3`
- allowed_in_collection: `context_only`

## 8. Proposed ground_truth_records.csv schema for live pilot

The first live pilot should use a manually curated `ground_truth_records.csv` if automated validation parsing is risky. Proposed fields:

- `record_id`
- `linked_event_id`
- `disease`
- `virus_or_syndrome`
- `country`
- `subnational_location`
- `date_anchor`
- `date_anchor_field`
- `date_reported`
- `reporting_period`
- `statistical_count_type`
- `cases_unspecified`
- `deaths`
- `source_id`
- `source_url`
- `source_type`
- `evidence_quote`
- `supporting_chunk_id`
- `ground_truth_role`
- `curation_note`

The manual record should preserve enough fields to work with the existing `evaluation_report_builder.py` grouping and comparison logic.

## 9. Proposed Stage 3B implementation plan

Stage 3B should be implementation, not Stage 3A.

1. Add live pilot seed source entries.
2. Add source-role policy support for case-specific reserved sources, or use an explicit allowlist plus reserved IDs.
3. Add a live masked validation pilot script or extend the existing pilot with a case-study config.
4. Add a manually curated `ground_truth_records.csv` for held-out validation if automated parsing is risky.
5. Run collection with live fetch enabled but LLM disabled first.
6. Inspect evidence chunks and extraction quality.
7. Only then optionally test LLM extraction.
8. Generate `evaluation_report.csv` and `professor_demo_report.md`.
9. Review leakage and provenance before showing results.

## 10. Risks and mitigations

| risk | mitigation |
|---|---|
| Source leakage risk | Use explicit reserved source IDs and fail the run if a reserved source appears in collection `final_dataset`. |
| Semantic leakage where Reuters quotes WHO | Label Reuters as collection-allowed with high semantic leakage risk; do not claim independence. |
| Dynamic source update risk | Record retrieval date and, if possible, freeze a local source snapshot before evaluation. |
| PDF/OCR risk | Avoid PDF-only validation sources in the first live pilot or manually curate ground truth. |
| Count-type mismatch risk | Preserve `statistical_count_type`, `reporting_period`, and `date_anchor`; route not-comparable rows to review. |
| Cumulative vs incident case mismatch | Do not compare outbreak-specific counts with cumulative surveillance totals as clean matches. |
| Date mismatch | Compare WHO 8 May 2026 and Reuters 27 May 2026 as different report dates unless explicitly normalized as the same evolving outbreak. |
| Location granularity mismatch | Preserve multi-country, ship, country, and subnational location fields separately where possible. |
| Copyright/quote-length risk for news evidence | Store short evidence quotes and avoid reproducing long news passages in professor-facing reports. |
| Overclaiming risk | Present Stage 3B as a controlled pilot, not as a benchmark or production validation. |

## 11. Decision needed from supervisors

- Should we prioritize WHO-held-out validation or stable state-level extraction?
- Are news sources acceptable collection sources if they cite WHO?
- Should validation be based on official web pages only or manually curated ground truth?
- Do professors prefer a current outbreak case or a stable historical surveillance case?
- Should the first live pilot use deterministic extraction only, or may it test LLM extraction after deterministic inspection?
