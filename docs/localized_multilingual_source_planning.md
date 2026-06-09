# Localized Multilingual Source Planning

## 1. Purpose

This repair improves source planning for tasks where relevant public-health data may be reported in local languages or official local-government domains. It keeps the project name as data collection workflow and keeps the existing graph topology unchanged.

The change is deterministic and advisory: it adds localized source hints and planned search queries. It does not search, fetch, crawl, parse, or extract by itself.

## 2. Failure Mode

A Shanghai hantavirus/HFRS task relied too much on English generic search terms such as `"hantavirus Shanghai"` and `"HFRS Shanghai"`. Those queries can return broad pages, news pages, or unrelated COVID-era Shanghai results instead of local public-health sources.

HFRS in China may be reported through Chinese official notifiable infectious disease tables or local public-health bulletins. English-only search is therefore a weak first pass for Shanghai tasks.

## 3. Localized Hints

For Shanghai / Hantavirus or Shanghai / HFRS tasks, the source plan now adds:

- Localized disease terms: `汉坦病毒`, `肾综合征出血热`, `流行性出血热`, `HFRS`, `hantavirus`, `hemorrhagic fever with renal syndrome`.
- Localized location terms: `上海`, `上海市`, `Shanghai`.
- Agency/source hints: `上海市卫生健康委员会`, `上海市疾病预防控制中心`, `中国疾病预防控制中心`, `国家卫生健康委员会`, `Shanghai Municipal Health Commission`, `Shanghai CDC`, `China CDC`, `National Health Commission`.
- Official domain hints: `wsjkw.sh.gov.cn`, `shcdc.sh.cn`, `chinacdc.cn`, `nhc.gov.cn`.
- Query metadata: `query_language`, `jurisdiction_hint`, `official_domain_hint`, `localized_source_hint`, and `source_priority_reason`.

These hints are used to prioritize official local/national public-health search queries before generic web or news queries.

## 4. Shanghai / Hantavirus Example

Example planned queries include:

```text
上海 肾综合征出血热 病例 2024
site:wsjkw.sh.gov.cn 肾综合征出血热 上海
site:shcdc.sh.cn 汉坦病毒 上海
site:nhc.gov.cn 肾综合征出血热 法定传染病
```

The actual generated queries use the task time window and may include 2024, 2025, or 2026 when those years are present in the user request.

## 5. Safety Boundaries

- Search remains bounded by existing max query and max result limits.
- No crawling or recursive browsing is introduced.
- `site:` expressions are search queries, not fetched source URLs.
- Direct URLs proposed by an LLM are still sanitized and are not inserted as source candidates.
- Source critic, source credibility, disease relevance, and validation compatibility gates still control downstream fetch/extraction and evaluation behavior.

## 6. What Is Still Not Fixed

- Run-quality-gated final dataset redesign is not fixed in Repair 4.
- Full HTML/report dynamic cleanup is not fixed in Repair 4.
- This repair does not guarantee official source pages exist or are reachable.
- This repair does not implement a full global public-health agency resolver for every country.
- Source critic remains metadata-only before fetch.
- Search provider behavior still depends on Tavily/network/index coverage when live search is enabled.
