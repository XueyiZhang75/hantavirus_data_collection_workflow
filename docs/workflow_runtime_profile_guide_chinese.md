# HDC Workflow Runtime Profile 说明

## 这是什么

`configs/hdc_workflow_run_config.jsonc` 是 HDC workflow 的运行配置文件，不是一次性汇报分支。

它服务于整个 workflow：控制 graph 输入、source overlay、source role policy、真实网页抓取、LLM 调用、collection/validation/context source 分工、held-out validation evidence 和输出路径。

technical workshop 只是把这个 workflow runtime profile 跑给教授看。New Mexico HPS 是为了现场展示而缩小的案例范围，不代表 workflow 只能跑 New Mexico。

## 为什么用 New Mexico HPS

New Mexico HPS profile 的作用是把完整 workflow 缩到一个可控、可解释、可复现的范围：

- source 数量少，现场能讲清楚
- NMDOH/CDC source 是真实网页
- 有 collection source、context source、validation-reserved source 三种角色
- 三个 LLM 环节都能被调用
- 最后能导出人读报告和 validation comparison

完整 workflow 的能力不是只服务这个案例。以后换疾病、地区或数据源，主要应换 runtime profile 里的 source overlay、source role policy、validation evidence 和 user request。

## 设置怎么调

| Config field | 能调什么 | 改了会怎样 |
|---|---|---|
| `workflow.graph_name` | 选择要运行的 LangGraph graph | 当前固定为 `hantavirus_data_collection_workflow`；以后新增 graph 后可切换 |
| `workflow.collection_mode` | workflow 运行模式 | `masked_validation` 会隔离 collection 和 validation source |
| `workflow.seed_source_overlay_path` | source candidates 来源 | 换这个文件可以跑其他地区/疾病/source set |
| `workflow.source_role_policy_overlay_path` | source role policy | 决定哪些 source 可 collection、哪些仅 context、哪些 held out validation |
| `workflow.validation_ground_truth_records_path` | validation 对照记录 | 改这里会改变最终 validation comparison |
| `workflow.use_fixture_documents` | 是否使用本地 fixture 文档 | `false` 跑真实网页；`true` 适合离线测试 |
| `user_request` | 用户输入任务 | 会影响 source planning、fetch、extraction 和 final report |
| `studio.port` | Studio 端口 | `null` 用默认端口；固定数字可用于现场固定 URL |
| `studio.no_reload` | Studio 是否自动 reload | `true` 更稳定；`false` 适合开发调试 |
| `live_web.enabled` | 是否真实抓网页 | `true` 是真实 workflow run；`false` 适合测试 |
| `live_web.timeout_seconds` | 网页请求等待时间 | 调大更耐慢网页；调小更快失败 |
| `llm.provider` | LLM provider | 改 provider 需要对应 API key |
| `llm.model` | LLM model | 会影响质量、速度和成本 |
| `llm.source_planning_enabled` | 是否启用 LLM source planning | `true` 让 LLM 辅助规划 source/query；`false` 用规则策略 |
| `llm.source_critic_enabled` | 是否启用 LLM source critic | `true` 让 LLM 评估 source 风险；`false` 只用 deterministic screening |
| `llm.structured_extraction_enabled` | 是否启用 LLM structured extraction | `true` 用 LLM 抽 records；`false` 用 rule-based extraction |
| `llm.max_chunks` | 最多送入 LLM extraction 的 evidence chunks | 调大更全但更慢更贵；调小更快但可能漏抽 |
| `llm.max_tokens` | LLM 单次输出长度 | 调大减少截断；调小控制成本 |
| `llm.fallback_to_rule_based` | LLM 失败时是否回退规则抽取 | `false` 让失败暴露，适合审计；`true` 提高连续运行能力 |
| `llm.source_critic.max_sources` | LLM critic 最多评估多少 source | 调大覆盖更多 source；调小省时间和 API |
| `llm.source_critic.review_blocks_fetch` | LLM critic 是否能阻止抓取 | `false` 表示 LLM advisory，安全边界由 deterministic policy 控制 |
| `source_sets.collection_source_ids` | collection source IDs | 这些 source 可以抓取并生成 records |
| `source_sets.context_source_ids` | context-only source IDs | 这些 source 可提供背景，但不生成 records |
| `source_sets.validation_reserved_source_ids` | held-out validation source IDs | 这些 source 不进入 collection，只用于 validation comparison |
| `source_sets.workflow_source_ids` | 本次 workflow 允许处理的 source IDs | 新增 source 时通常要同步 overlay 和 role policy |
| `source_sets.llm_source_critic_source_ids` | 允许 LLM critic 评价的 source IDs | 可以小于 workflow source set 来控制成本 |
| `output.run_output_root` | 输出根目录 | 每次 run 默认写到 `sessions/<timestamp>/` |
| `output.sessionized` | 是否按 session 保存 | `true` 不覆盖旧 run；`false` 直接写到 root |
| `output.auto_build_console` | 是否自动生成 HTML console | `true` 跑完 workflow 后自动导出 HTML 可视化页 |

## 展示时一句话

这不是 presentation-only 配置。它是 HDC workflow 的 runtime profile。New Mexico HPS 只是一个缩小案例，用来展示完整 workflow 如何从用户任务出发，抓真实网页，调用 LLM，隔离 collection/validation source，做 validation comparison，并输出可读报告。每次运行输出保存在 `outputs/sessions/<timestamp>/`，latest alias 和可视化控制台保存在 `outputs/workflow_console/hdc_workflow_console.html`。
