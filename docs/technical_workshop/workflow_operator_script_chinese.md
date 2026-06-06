# HDC Workflow 技术展示操作脚本

## 1. 打开项目

```powershell
cd "C:\Users\zhang\OneDrive - University of Virginia\桌面\FLU\Epidemics-ML\Data_Collection\hantavirus_data_collection_workflow"
```

现场说法：

这次不是展示一个为了汇报临时拼出来的结果，而是展示 HDC workflow 本身怎么运行。我们先看 workflow runtime profile，然后启动 LangGraph Studio，在 Studio 里提交任务，看 workflow 节点逐步运行，最后导出一份人读报告。

## 2. 先展示 workflow runtime profile

打开：

```text
configs/hdc_workflow_run_config.jsonc
```

现场说法：

这不是单独为了演示做的配置，而是 workflow 运行配置。这里能看到 graph 名称、collection mode、source overlay、source role policy、validation ground-truth 路径、本次任务、是否开启真实网页抓取、调用哪个 provider/model、三个 LLM 环节是否开启、哪些 source 是 collection、哪些 source 是 validation reserved、哪些 source 是 context only，以及输出目录在哪里。

重点指给教授看：

```text
workflow.graph_name
workflow.collection_mode
workflow.seed_source_overlay_path
workflow.source_role_policy_overlay_path
workflow.validation_ground_truth_records_path
user_request
live_web.enabled
llm.provider
llm.model
llm.source_planning_enabled
llm.source_critic_enabled
llm.structured_extraction_enabled
source_sets.collection_source_ids
source_sets.validation_reserved_source_ids
source_sets.context_source_ids
output.run_output_root
output.sessionized
output.auto_build_console
```

## 3. 检查 API key，但不展示 key

```powershell
$env:ANTHROPIC_API_KEY = [Environment]::GetEnvironmentVariable("ANTHROPIC_API_KEY", "User")
[bool]$env:ANTHROPIC_API_KEY
```

现场说法：

API key 保存在 User-scope environment variable。workflow 只从环境变量读取 key，不会把 key 写进 HTML、Markdown、CSV、JSON 或日志。本次三个 LLM 环节都使用 config 里的同一个 provider/model。

## 4. 预览本次运行配置

```powershell
python scripts/start_hdc_workflow_studio.py --print-config-only
```

现场说法：

这一步不启动服务器，也不联网，只打印本次将要使用的配置。可以看到 live fetch 是 true，fixture documents 是 false，source planning、source critic、structured extraction 三个 LLM 环节都是 true，provider/model 是 config 里设置的值，并且只显示 api_key_present，不显示 key 本身。

## 5. 启动 LangGraph Studio 产品模式

```powershell
python scripts/start_hdc_workflow_studio.py
```

现场说法：

这个命令读取同一份 config，然后启动 Studio。它不是直接跑完并吐出结果，而是给我们一个可视化入口，让我们在 Studio 里提交任务并查看每个节点怎样写入 state。

打开 graph：

```text
hantavirus_data_collection_workflow
```

## 6. 在 Studio 输入任务

如果 Studio 显示输入框，使用 config 里的 `user_request`。如果 Studio 显示 JSON 输入，填：

```json
{
  "user_request": "Collect data on hantavirus from 2020 to 2026. For this workflow run, use the New Mexico HPS source set, keep collection sources and validation sources separated, extract cases, deaths, dates, locations, source URLs, source types, and evidence quotes, then route uncertain results to human review."
}
```

需要重新打印这个输入时运行：

```powershell
python scripts/print_studio_initial_state.py --minimal
```

现场说法：

这一步解决“用户任务在哪里输入”的问题。任务作为 LangGraph state 的 `user_request` 字段进入 workflow，后续节点都基于这个 state 继续写入 source plan、source registry、documents、evidence chunks、records、validation comparison 和 review routing。

## 7. 点击 Submit，看 workflow 节点

Studio trace 里按顺序看：

```text
task_intake_and_scope_planning
query_strategy_builder
source_discovery
source_dedup_and_registry
source_screening
source_critic_and_uncertainty_routing
content_fetch_and_parse
document_quality_check
evidence_chunking_and_data_presence_flagging
structured_extraction
schema_validation_and_repair
record_normalization
record_linking
cross_source_consistency_check
quality_gate_routing
human_review
final_data_package_builder
```

现场说法：

这个 workflow 主体是串行 state pipeline。每个节点读取上一步 state，再写入新的 structured artifacts。关键条件分支发生在 `quality_gate_routing`：如果 validation comparison、schema validation 或 evidence consistency 发现不确定项，就进入 `human_review`；否则进入 `final_data_package_builder`。

## 8. 展示三个 LLM 环节

第一个节点：

```text
query_strategy_builder
```

看：

```text
source_planning_agent_summary
agentic_source_plan
search_query_inventory
```

说法：

这里是 LLM source planning。LLM 根据用户任务提出 source planning advice 和 candidate queries；deterministic guardrail 再决定哪些建议进入后续流程。

第二个节点：

```text
source_critic_and_uncertainty_routing
```

看：

```text
source_critic_summary
source_routing_summary
source_registry
```

说法：

这里是 LLM source critic。每个 source 先经过规则筛选，再由 LLM 给 advisory critic，包括 validation leakage risk、context-only risk、是否建议 human review。最终 source role 仍然由 deterministic policy 和 masking rule 控制。

第三个节点：

```text
structured_extraction
```

看：

```text
structured_extraction_summary
llm_extraction_summary
raw_records
```

说法：

这里是 LLM structured extraction。它只处理允许进入 collection extraction 的 evidence chunks。validation-reserved source 不会被用于 collection；context-only source 可以提供背景，但不会产生 structured records。

## 9. 展示 source 分工

打开：

```text
docs/technical_workshop/new_mexico_hps_source_split_table.md
```

现场说法：

source 被明确分成三类。`collection` source 允许抓取并用于 structured extraction；`validation_reserved` source 被 held out，只用于 validation comparison；`context_only` source 可以提供背景，但 blocked from structured extraction。

本次 held-out validation source 是：

```text
src_nmdoh_hps_cases_by_county_1975_2025_pdf
```

## 10. 导出人读报告

Studio 用来看过程；命令行复跑同一份 workflow runtime profile，用来导出报告和 artifacts：

```powershell
python scripts/run_hdc_workflow_configured.py
```

打开：

```text
outputs/sessions/<timestamp>/workflow_run_report_chinese.md
outputs/workflow_runs/latest_workflow_run_report_chinese.md
```

现场说法：

这份报告不是工程审计 JSON，而是给人读的运行结果。它写清楚本次输入任务、抓取的真实网页、source 分工、三个 LLM 环节调用情况、最终 records、validation 对比、human review flag，以及当前 workflow 已经做到什么。

## 11. 最后一段总结

本次 workshop 展示的是 workflow 的完整运行能力：打开 runtime profile，确认 API key，启动 Studio，在 Studio 输入任务并 Submit，观察 LangGraph 节点逐步运行，真实抓取 NMDOH/CDC 网页，三个 LLM 环节在同一次 workflow 中被调用，collection source 与 validation source 被隔离，最终输出可审计数据包和一份人读报告。
