# Interpretive Human-Readable Reports

## 1. Purpose

The `data collection workflow` now produces human-readable interpretive reports in addition to the existing engineering/debug report.

The existing `workflow_run_report_chinese.md` is still preserved. It remains useful for debugging node counts, source counts, fetch status, LLM calls, validation diagnostics, and artifact paths. The new interpretive reports explain the same completed run in a form that is easier for professors, public-health users, and project reviewers to read.

## 2. Why this was needed

The workflow can now produce many auditable outputs, including primary case records, zero-case statements, exposure-monitoring records, context records, quarantined records, claim corroboration outputs, and source identity diagnostics.

Those engineering artifacts are important, but users need a clear answer to practical questions:

- Was primary case data found?
- Were non-case observations found instead?
- Were primary case claims cross-source supported?
- Were sources identifiable and credible enough to inspect?
- Was held-out validation available or limited?
- What evidence was quarantined?
- What should a human reviewer check next?
- Can this run be used as a final epidemiological dataset?

## 3. Report files

Each configured run now writes these files in the session root:

- `workflow_interpretive_report_chinese.md`
- `workflow_interpretive_report.md`
- `workflow_interpretive_report_summary.json`

If latest aliases are enabled, the workflow also writes:

- `outputs/workflow_runs/latest_workflow_interpretive_report_chinese.md`
- `outputs/workflow_runs/latest_workflow_interpretive_report.md`
- `outputs/workflow_runs/latest_workflow_interpretive_report_summary.json`

## 4. Report content

The Chinese report contains:

1. 本次任务
2. 一句话结论
3. 最终数据状态
4. Primary case dataset 结果
5. 非病例但有用的公共卫生观察
6. 跨来源印证结果
7. 数据源质量与可信度
8. Validation 状态
9. 被排除 / quarantined 的内容
10. Human review 重点
11. 可否作为最终流行病学数据集使用？
12. 下一步建议
13. 关键文件索引
14. 重要声明

The English report contains:

1. Task
2. One-sentence conclusion
3. Final data status
4. Primary case dataset findings
5. Useful non-case public-health observations
6. Cross-source corroboration
7. Source quality and credibility
8. Validation status
9. Excluded / quarantined evidence
10. Human review priorities
11. Can this be used as a final epidemiological dataset?
12. Recommended next steps
13. Key artifact index
14. Important disclaimer

## 5. How conclusions are generated

The interpretive reports are deterministic. They read existing session artifacts only:

- `workflow_run_summary.json`
- `collection/final_package.json`
- `collection/final_case_dataset.json`
- `collection/final_dataset.json`
- `collection/final_dataset_pre_quality_gate.json`
- `collection/zero_case_statements.json`
- `collection/exposure_monitoring_records.json`
- `collection/context_records.json`
- `collection/quarantined_records.json`
- `diagnostics/run_quality_summary.json`
- `diagnostics/final_dataset_quality_summary.json`
- `diagnostics/observation_type_dataset_summary.json`
- `diagnostics/corroboration_summary.json`
- `diagnostics/source_identity_summary.json`
- `diagnostics/validation_source_compatibility_summary.json`
- `diagnostics/anomaly_summary.json`
- `diagnostics/human_review_application_summary.json`

The report builder does not call LLMs, run web search, fetch webpages, mutate records, or apply human review decisions.

The key rule is conservative: if `final_case_dataset_count = 0`, the report must clearly say that no accepted primary case dataset records were found and that the run should not be interpreted as a final epidemiological case dataset.

## 6. Virginia example

For a Virginia hantavirus run, the workflow may technically complete live search, webpage fetch, extraction, screening, and export while still producing `final_case_dataset_count = 0`.

In that case, the interpretive report should say:

- no accepted primary case dataset records were found
- non-primary or context evidence may still exist
- zero-case statements are not confirmed case records
- exposure monitoring is not a confirmed/probable/suspected case record
- validation may be limited if no task-compatible held-out validation source is active
- expert review remains required

## 7. Limitations

- The interpretive report does not implement a human review UI.
- The interpretive report does not implement workflow visualization.
- The interpretive report does not add new evidence.
- The interpretive report does not improve source discovery.
- The interpretive report does not make automatic truth determinations.
- Report quality depends on upstream extraction, source identity, corroboration, dataset split, validation, and quality-gate artifacts.
- Expert review remains required.
