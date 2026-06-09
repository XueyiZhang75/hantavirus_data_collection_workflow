# Post-Acceptance Repair 4 Report: Localized Multilingual Official-Source Planning

## 1. Repair goal

Repair 4 improves source planning for local-language and jurisdiction-specific official public-health sources in the data collection workflow. The graph topology was not changed; the existing disease intelligence, executable source planning, query strategy, and source discovery nodes now receive deterministic localized hints when the task calls for them.

## 2. Failure case being addressed

The previous Shanghai hantavirus/HFRS run used the task `hantavirus / shanghai / 2024-01-01 to 2026-06-09`.

The run showed that source planning relied too much on English generic search. The first selected live Tavily queries were:

- `"hantavirus Shanghai" cases deaths public health shanghai 2024-1-1-2026-6-9 2024`
- `"HFRS Shanghai" cases deaths public health shanghai 2024-1-1-2026-6-9 2024`
- `"hantavirus Shanghai" outbreak report surveillance shanghai 2024-1-1-2026-6-9 2024`

Those queries did not include Chinese HFRS terms, Chinese Shanghai terms, or official China/Shanghai site restrictions. The old run returned broad or irrelevant sources, including COVID-era Shanghai results. Repairs 1-3 gated wrong-disease records and incompatible validation sources, but the source-planning layer still needed to search official Chinese sources earlier.

## 3. Files created or modified

Created:

- `src/hdc_workflow/localized_source_planning.py`
- `tests/test_localized_multilingual_source_planning.py`
- `docs/localized_multilingual_source_planning.md`
- `docs/stage_reports/POST_ACCEPTANCE_REPAIR_4_REPORT.md`

Modified in this repair:

- `src/hdc_workflow/models.py`
- `src/hdc_workflow/nodes/task_scope.py`
- `src/hdc_workflow/nodes/source_discovery.py`
- `src/hdc_workflow/resources/disease_intelligence/hantavirus.json`
- `src/hdc_workflow/resources/final_package_policy.json`
- `src/hdc_workflow/state.py`
- `scripts/run_hdc_workflow_configured.py`
- `scripts/build_workflow_run_console.py`

The working tree also contains earlier uncommitted Repair 1-3 changes that were not reverted.

## 4. Functional changes made

- Added a deterministic localized source planning helper for Shanghai / China hantavirus-HFRS tasks.
- Added Chinese HFRS/hantavirus terms and China official reporting context to the curated hantavirus disease intelligence profile.
- Enriched deterministic executable source plans with localized official-source objectives, official source category notes, and prioritized localized planned queries.
- Added LLM post-processing so generic English LLM source plans preserve deterministic localized official queries for Shanghai/HFRS tasks.
- Added auditable query metadata: `query_language`, `jurisdiction_hint`, `official_domain_hint`, `localized_source_hint`, and `source_priority_reason`.
- Preserved localized query metadata into `search_query_inventory` and live source search execution records.
- Added `localized_source_planning_summary` to state, final package workflow summaries, runner diagnostics, and console data loading.

## 5. Shanghai/Hantavirus planning behavior

Localized disease terms include:

- `汉坦病毒`
- `肾综合征出血热`
- `流行性出血热`
- `HFRS`
- `hantavirus`
- `hemorrhagic fever with renal syndrome`

Localized location terms include:

- `上海`
- `上海市`
- `Shanghai`

Official agency hints include:

- `上海市卫生健康委员会`
- `上海市疾病预防控制中心`
- `中国疾病预防控制中心`
- `国家卫生健康委员会`
- `Shanghai Municipal Health Commission`
- `Shanghai CDC`
- `China CDC`
- `National Health Commission`

Official domain hints include:

- `wsjkw.sh.gov.cn`
- `shcdc.sh.cn`
- `chinacdc.cn`
- `nhc.gov.cn`

Example planned queries:

- `site:wsjkw.sh.gov.cn 肾综合征出血热 上海 2024`
- `site:wsjkw.sh.gov.cn 汉坦病毒 上海 2024`
- `site:shcdc.sh.cn 肾综合征出血热 上海`
- `site:chinacdc.cn 肾综合征出血热 上海`
- `site:nhc.gov.cn 肾综合征出血热 法定传染病`

These localized official queries are inserted before generic web/news queries, so small `max_queries` live runs execute them first.

## 6. Backward compatibility

- COVID-19/New York source planning still generates COVID/SARS-CoV-2/New York queries and does not receive Shanghai Chinese official-source hints.
- Dengue/Florida source planning still generates dengue/DENV/Florida queries and does not receive Shanghai Chinese official-source hints.
- Hantavirus/New Mexico compatibility was preserved in `outputs/sessions/repair4_hantavirus_new_mexico_compat_no_llm`.
- Repair 1 disease relevance, Repair 2 source critic, and Repair 3 validation compatibility tests still pass.

## 7. Live Shanghai smoke behavior

Command:

```powershell
python scripts\run_hdc_workflow_configured.py --config outputs\generated_configs\hantavirus_shanghai_2024_1_1_2026_6_9_20260609_141441_utc.json --session-id repair4_hantavirus_shanghai_localized_source_planning
```

Output session:

- `outputs/sessions/repair4_hantavirus_shanghai_localized_source_planning`

Observed behavior:

- Localized source planning enabled: true
- Planned localized query count: 9
- Official domain hints used: `wsjkw.sh.gov.cn`, `shcdc.sh.cn`, `chinacdc.cn`, `nhc.gov.cn`
- Source search planned query count: 19
- Source search selected query count: 3
- Localized selected query count: 3
- Source search executed query count: 2
- Localized executed query count: 2
- Search-derived source candidates returned: 6
- Source critic attempted source count: 6
- Source critic assessed source count: 5
- Normalized record count: 0
- Final post-review dataset count: 0
- Accepted wrong-disease COVID record count: 0
- Validation source compatibility status: `incompatible_validation_source_disabled`

The first selected live queries were localized official queries:

- `site:wsjkw.sh.gov.cn 肾综合征出血热 上海 2024`
- `site:wsjkw.sh.gov.cn 汉坦病毒 上海 2024`
- `site:shcdc.sh.cn 肾综合征出血热 上海`

No reliable extractable documents were fetched in this live smoke, so no final records were produced. That is acceptable for Repair 4 because the acceptance target is improved localized source planning and safe downstream gating, not guaranteed discovery of Shanghai HFRS records.

## 8. Tests added or updated

Added:

- `tests/test_localized_multilingual_source_planning.py`

The tests cover:

- Shanghai hantavirus disease intelligence includes Chinese HFRS terms.
- Shanghai executable source plan includes localized official queries.
- Localized official queries are prioritized.
- Query inventory preserves localized query metadata.
- `site:` queries remain search queries, not source URLs.
- COVID-19/New York and dengue/Florida do not receive Shanghai hints.
- Unsupported locations fall back safely.
- LLM source plan post-processing preserves deterministic localized hints.

## 9. Commands run

Git/state inspection:

```powershell
git status --short
git branch --show-current
git rev-parse HEAD
git diff --check
```

TDD red check:

```powershell
python -m pytest tests\test_localized_multilingual_source_planning.py -q
```

Targeted green check:

```powershell
python -m pytest tests\test_localized_multilingual_source_planning.py -q
```

Repair 1-3 regression:

```powershell
python -m pytest tests\test_disease_relevance_gating.py tests\test_source_critic_live_integration.py tests\test_task_compatible_validation_sources.py -q
```

Source planning / source discovery regression subset:

```powershell
python -m pytest tests\test_disease_intelligence.py tests\test_executable_source_planning.py tests\test_real_source_discovery.py tests\test_workflow_run_config.py tests\test_graph_smoke.py -q
```

Full suite:

```powershell
python -m pytest -q
```

Hantavirus/New Mexico compatibility:

```powershell
python scripts\run_hdc_workflow_configured.py --config configs\hdc_workflow_run_config.jsonc --disable-all-llm --session-id repair4_hantavirus_new_mexico_compat_no_llm
```

Shanghai live smoke:

```powershell
python scripts\run_hdc_workflow_configured.py --config outputs\generated_configs\hantavirus_shanghai_2024_1_1_2026_6_9_20260609_141441_utc.json --session-id repair4_hantavirus_shanghai_localized_source_planning
```

Secret scans:

```powershell
rg -n "tvly-|sk-ant-|ANTHROPIC_API_KEY=\S+|TAVILY_API_KEY=\S+" .env.example configs docs examples notebooks scripts src tests outputs
rg -n "sk-ant-[A-Za-z0-9_-]{20,}|tvly-[A-Za-z0-9_-]{20,}|ANTHROPIC_API_KEY\s*=\s*[A-Za-z0-9_-]{20,}|TAVILY_API_KEY\s*=\s*[A-Za-z0-9_-]{20,}" .env.example configs docs scripts src tests outputs
```

## 10. Test results

- Initial TDD red check: 9 failed in 0.26s, failing for missing Chinese terms, missing localized summary, missing localized metadata, and missing LLM post-processing preservation.
- Repair 4 targeted tests: 9 passed in 0.16s.
- Repair 1-3 regression tests: 33 passed in 0.51s.
- Source planning / discovery regression subset: 159 passed in 6.76s.
- Full test suite: 403 passed in 21.04s.
- `git diff --check`: exit 0; only Git CRLF conversion warnings were printed.
- Required broad secret scan: matched only mocked test keys and documented scan-command text; it also reported missing `notebooks` directory.
- Strict long-token secret scan: no matches.

Branch and HEAD:

- Branch: `main`
- HEAD: `6d1faebebf643375e270106c8d91119662bb6578`

## 11. Live acceptance result

PASSED: pytest passed, Shanghai live smoke completed, localized official queries were present and selected/executed within the live search query limit, no wrong-disease records were accepted, and New Mexico HPS validation ground truth was not active.

## 12. Output artifacts

- `docs/localized_multilingual_source_planning.md`
- `docs/stage_reports/POST_ACCEPTANCE_REPAIR_4_REPORT.md`
- `tests/test_localized_multilingual_source_planning.py`
- `outputs/sessions/repair4_hantavirus_shanghai_localized_source_planning`
- `outputs/sessions/repair4_hantavirus_new_mexico_compat_no_llm`

## 13. Known limitations

- Repair 4 does not guarantee official source pages exist or are indexed.
- Repair 4 does not implement a full global agency resolver for every country.
- Run-quality-gated final dataset redesign is not fixed in Repair 4.
- Full HTML/report dynamic cleanup is not fixed in Repair 4.
- Source critic remains metadata-only before fetch.
- Search provider behavior depends on Tavily/network/index coverage.
- The console may render Chinese correctly in the browser, while some PowerShell JSON excerpts display mojibake because of terminal encoding.

## 14. Review checklist

- [x] User-facing project name remains "data collection workflow"
- [x] Internal package name hdc_workflow was not renamed
- [x] Graph topology unchanged
- [x] Shanghai/Hantavirus plan includes Chinese HFRS terms
- [x] Shanghai/Hantavirus plan includes 上海 / 上海市 terms
- [x] Shanghai/Hantavirus plan includes official China/Shanghai agency hints
- [x] Shanghai/Hantavirus plan includes official domain/site queries
- [x] Localized official queries are prioritized before generic news queries
- [x] site: queries are not inserted as source URLs
- [x] COVID-19/New York plan does not get Shanghai Chinese hints
- [x] Dengue/Florida plan does not get Shanghai Chinese hints
- [x] Repair 1 disease relevance tests still pass
- [x] Repair 2 source critic tests still pass
- [x] Repair 3 validation compatibility tests still pass
- [x] pytest was run
- [x] No API keys or secrets were printed
- [x] Repair 5/6 were not implemented
