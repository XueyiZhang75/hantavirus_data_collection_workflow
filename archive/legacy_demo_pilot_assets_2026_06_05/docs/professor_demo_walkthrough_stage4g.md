# Professor Demo Walkthrough — Stage 4G

## 1. Demo objective

This demo shows the evolution from a deterministic LangGraph workflow to a hybrid agentic real-source masked-validation workflow. The goal is to show what is now working, where LLMs enter, where deterministic guardrails remain in charge, and what decisions are needed before moving toward a broader system.

## 2. Recommended 45-minute flow

### Part A — Project framing

- Purpose: Frame the project as an auditable hantavirus public-health data collection workflow.
- Command or artifact to show: `docs/current_project_status_stage4f.md`.
- Expected output: A compact status document with implemented capabilities and current results.
- What to say: The system is a workflow with guardrails, not an unrestricted web agent.
- Chinese speaking note: "我们现在展示的是一个可审计的 hantavirus 数据收集 workflow，不是生产级自动监测系统。"
- What it proves: The project has a coherent architecture and safety boundary.
- What it does not prove: It does not prove broad autonomous search or production readiness.

### Part B — Existing LangGraph backbone

- Purpose: Show that the project has a staged orchestration backbone.
- Command or artifact to show: `python scripts/run_workflow_demo.py`.
- Expected output: Ordered node trace from task intake through final package builder.
- What to say: LangGraph coordinates the deterministic nodes and provides inspectable state transitions.
- Chinese speaking note: "LangGraph 在这里是 backbone，负责把 source screening、fetch、extraction、validation 串起来。"
- What it proves: The workflow can run offline and produce traceable node output.
- What it does not prove: This command does not fetch real webpages or use LLMs.

### Part C — Deterministic baseline and fixture sanity checks

- Purpose: Explain why synthetic fixture tests still matter.
- Command or artifact to show: `python -m pytest -q` and `python scripts/run_masked_validation_pilot.py`.
- Expected output: Passing tests and a deterministic masked-validation pilot report.
- What to say: Fixtures are regression checks, not the final scientific demo.
- Chinese speaking note: "fixture 只是 regression test，证明流程不会坏，不代表真实流行病学结论。"
- What it proves: Local safety and repeatability.
- What it does not prove: Real-source extraction quality.

### Part D — Source masking and held-out validation design

- Purpose: Show the core validation design.
- Command or artifact to show: `docs/masked_validation_design_spec.md`.
- Expected output: Source roles including collection, context-only, and validation-reserved.
- What to say: The validation source is blocked from collection and only used after extraction for comparison.
- Chinese speaking note: "held-out validation source 不允许进入 extraction；它只在最后评估时出现。"
- What it proves: The evaluation is designed to detect leakage.
- What it does not prove: Automated ground truth scraping.

### Part E — MV Hondius diagnostic pilot and why it was not enough

- Purpose: Explain the Stage 3 diagnostic path.
- Command or artifact to show: `docs/live_mv_hondius_context_guardrail_stage3d.md`.
- Expected output: WHO masking passed; Reuters was access/quality-limited; VDH was context-only.
- What to say: MV Hondius was useful diagnostically but not a positive validation case.
- Chinese speaking note: "MV Hondius 说明 guardrail 有效，但它不是最强 positive demo。"
- What it proves: Guardrail auditing works.
- What it does not prove: A successful real-source extraction-to-validation chain.

### Part F — Agentic upgrade: Source Planning and Source Critic

- Purpose: Show where agentic AI enters before extraction.
- Command or artifact to show: `outputs/professor_demo_package/stage4b4_structured_source_planning_results_summary.json`.
- Expected output: `source_planning_agent_succeeded=true`, `source_critic_agent_succeeded=true`.
- What to say: LLMs are used for advisory planning and critique, while guardrails remain deterministic.
- Chinese speaking note: "LLM 在这里做 planning 和 critic，不负责绕过 source masking。"
- What it proves: Agentic reasoning can be integrated as a controlled advisory layer.
- What it does not prove: LLMs are autonomous crawlers.

### Part G — New Mexico HPS real webpage live pilot

- Purpose: Show the strongest real-source case study.
- Command or artifact to show: `outputs/professor_demo_package/stage4c_new_mexico_hps_live_results_summary.json`.
- Expected output: real webpage fetch used; collection records created; validation source blocked.
- What to say: New Mexico HPS is still hantavirus, and the source is an official health department.
- Chinese speaking note: "New Mexico HPS 仍然是 hantavirus，不是换了疾病；这是官方网页真实抓取。"
- What it proves: Controlled real webpage collection works.
- What it does not prove: Broad web search.

### Part H — Deterministic extraction miss

- Purpose: Show why the next controlled LLM step was needed.
- Command or artifact to show: `outputs/live_masked_validation_new_mexico_hps/collection/final_dataset.csv`.
- Expected output: deterministic records exist, but annual case/death counts were not recovered.
- What to say: Deterministic extraction missed a spelled-out sentence.
- Chinese speaking note: "网页里有句子，但 deterministic extractor 没把 seven / three fatal 变成结构化数字。"
- What it proves: The baseline has a real limitation.
- What it does not prove: The source data was absent.

### Part I — Controlled LLM extraction replay

- Purpose: Show LLM extraction on already-fetched collection evidence only.
- Command or artifact to show: `outputs/live_masked_validation_new_mexico_hps_llm_replay/llm_extraction/normalized_records.csv`.
- Expected output: 2 LLM records, including 2025 annual `cases=7`, `deaths=3`.
- What to say: The LLM did not see the validation source; it only saw selected collection evidence.
- Chinese speaking note: "LLM 没有看 held-out ground truth，只看 collection-side evidence。"
- What it proves: Controlled LLM extraction can recover the missed annual count.
- What it does not prove: General LLM extraction accuracy.

### Part J — Annual alignment and evaluation result

- Purpose: Explain Stage 4F.
- Command or artifact to show: `outputs/live_masked_validation_new_mexico_hps_llm_replay/evaluation/evaluation_report.csv`.
- Expected output: annual row with `case_count_match;death_count_not_comparable`.
- What to say: Annual records should compare by `reporting_period`, not by later publication date.
- Chinese speaking note: "这是 annual summary，所以比较时应该按 2025 reporting_period，而不是 2026 发布日期。"
- What it proves: Evaluation can align the extracted annual count with held-out ground truth.
- What it does not prove: Death validation, because the held-out ground truth lacks deaths.

### Part K — Limitations and next decisions

- Purpose: End with explicit boundaries and supervisor decisions.
- Command or artifact to show: `docs/stage4g_next_steps_decision_memo.md`.
- Expected output: Options A-E with benefit, effort, risk, and approval needs.
- What to say: The next step should be chosen deliberately.
- Chinese speaking note: "下一步我们需要老师决定：继续做 deterministic reproducibility、PDF/OCR、更多真实案例，还是 controlled broad search。"
- What it proves: The project has clear next-stage choices.
- What it does not prove: That implementation should continue before supervisor feedback.

## 3. Safe command sequence for meeting

Run only:

```powershell
python -m pytest -q
python scripts/run_workflow_demo.py
python scripts/run_masked_validation_pilot.py
python scripts/run_new_mexico_hps_llm_extraction_replay.py --dry-run
python scripts/run_new_mexico_hps_llm_extraction_replay.py --reevaluate-existing
```

Do not rerun live fetch or LLM extraction during the meeting unless supervisors explicitly request it.

## 4. Artifact opening sequence

1. `docs/current_project_status_stage4f.md`
2. `docs/stage4f_annual_alignment_review.md`
3. `outputs/professor_demo_package/stage4f_annual_alignment_summary.md`
4. `outputs/live_masked_validation_new_mexico_hps/collection/final_dataset.csv`
5. `outputs/live_masked_validation_new_mexico_hps/collection/source_registry.json`
6. `outputs/live_masked_validation_new_mexico_hps_llm_replay/llm_extraction/normalized_records.csv`
7. `outputs/live_masked_validation_new_mexico_hps_llm_replay/evaluation/evaluation_report.csv`
8. `outputs/live_masked_validation_new_mexico_hps_llm_replay/comparison/deterministic_vs_llm_report.md`
9. `outputs/live_masked_validation_new_mexico_hps_llm_replay/diagnostics/source_role_safety_check.json`
10. `outputs/live_masked_validation_new_mexico_hps_llm_replay/diagnostics/llm_extraction_replay_summary.json`

## 5. How to explain the final evaluation row

The collection source is `src_nmdoh_hps_2026_first_case_prior_year_summary`. The validation source is `src_nmdoh_hps_cases_by_county_1975_2025_pdf`. The collection annual record has `collection_case_count=7`; the validation annual record has `validation_case_count=7`; therefore the case field is `case_count_match`. The collection record also has `collection_death_count=3`, but the validation ground truth has a blank death field, so the death field is `death_count_not_comparable`. The overall row is `partial_match_not_comparable`, human review remains appropriate, and `reserved_source_leakage_count=0`.

## 6. Expected professor questions and suggested answers

- Is this still hantavirus? Yes. HPS is hantavirus pulmonary syndrome.
- Did you use real webpages? Yes, Stage 4C fetched real NMDOH/CDC webpages under explicit allowlist.
- Did you use synthetic data? Synthetic fixtures remain regression tests; the best demo chain is the real-source New Mexico HPS chain.
- Where exactly did LLM enter? Source planning, source critic, and controlled extraction replay.
- Did LLM see the ground truth? No. Stage 4E used only collection-side evidence.
- Did the validation source leak? No. `reserved_source_leakage_count=0`.
- Why is status not clean match? The case count matched, but validation deaths are blank, so death count is not comparable.
- Why not parse PDF automatically? PDF/OCR is not implemented yet; current ground truth is manually curated.
- Why no broad web search yet? The project prioritized auditability and controlled source overlays first.
- What is LangGraph contributing? It orchestrates node order, state, provenance, and reproducible workflow traces.
- What is the scientific contribution? A guarded hybrid workflow for auditable public-health data collection and masked validation.
- What are the next steps? Decide between pausing for meeting, deterministic count parsing, PDF/OCR, another real-source case, or controlled broad search.
