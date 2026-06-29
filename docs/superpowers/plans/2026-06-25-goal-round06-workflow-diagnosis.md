# Goal Round06 Workflow Diagnosis Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Run a new stratified three-session workflow evaluation, diagnose nodes 01-20, and apply only evidence-backed generic TDD fixes.

**Architecture:** Treat live workflow sessions as the integration test surface and `run_quality_gates.py` plus related tests as the first likely repair boundary. Preserve the user's existing dirty worktree and add only round-scoped reports under `outputs/goal_round06_diagnosis` unless a failing regression test proves a generic code fix is needed.

**Tech Stack:** Python, pytest, `scripts/run_interactive_workflow.py`, JSON/CSV diagnostics under `outputs/sessions`.

---

### Task 1: Run Stratified Live Sessions

**Files:**
- Read: `scripts/run_interactive_workflow.py`
- Output: `outputs/sessions/goal_round06_*`

- [ ] **Step 1: Use three stratified tasks**

Use these session definitions:

```text
goal_round06_measles_us_2025_q1
Disease: Measles
Location: United States
Start: 2025-01-01
End: 2025-03-31
Rationale: official national/state surveillance, strong case-count expectation, outbreak-news noise.

goal_round06_dengue_brazil_2024_q1
Disease: Dengue
Location: Brazil
Start: 2024-01-01
End: 2024-03-31
Rationale: large international outbreak, likely official ministry/PAHO sources, language and cumulative-metric risk.

goal_round06_legionnaires_ontario_2025_07
Disease: Legionnaires' disease
Location: Ontario
Start: 2025-07-01
End: 2025-07-31
Rationale: city/province event style, case-vs-environmental metric ambiguity.
```

- [ ] **Step 2: Run each workflow**

```powershell
python scripts\run_interactive_workflow.py --disease "Measles" --location "United States" --start-date 2025-01-01 --end-date 2025-03-31 --session-id goal_round06_measles_us_2025_q1 --no-dashboard --no-run-notebook --no-live-status
python scripts\run_interactive_workflow.py --disease "Dengue" --location "Brazil" --start-date 2024-01-01 --end-date 2024-03-31 --session-id goal_round06_dengue_brazil_2024_q1 --no-dashboard --no-run-notebook --no-live-status
python scripts\run_interactive_workflow.py --disease "Legionnaires' disease" --location "Ontario" --start-date 2025-07-01 --end-date 2025-07-31 --session-id goal_round06_legionnaires_ontario_2025_07 --no-dashboard --no-run-notebook --no-live-status
```

Expected: each command exits 0 and writes a session directory under `outputs/sessions`.

### Task 2: Diagnose Nodes 01-20

**Files:**
- Read: `outputs/sessions/goal_round06_*/diagnostics/*.json`
- Read: `outputs/sessions/goal_round06_*/collection/*.csv`
- Output: `outputs/goal_round06_diagnosis/diagnosis_summary.json`
- Output: `outputs/goal_round06_diagnosis/node_matrix.csv`
- Output: `outputs/goal_round06_diagnosis/diagnosis_report.md`

- [ ] **Step 1: Build a node matrix**

For each session, inspect node evidence for:

```text
01 task scope
02 source discovery
03 source split
04 source screening
05 source credibility
06 source critic
07 fetch
08 parse/document quality
09 extraction
10 normalization
11 schema validation
12 disease relevance
13 validation source compatibility
14 trusted source validation
15 linking/deduplication
16 anomaly/conflict checks
17 human review
18 final quality gate
19 post-review application
20 final package/report
```

- [ ] **Step 2: Write diagnosis artifacts**

Summarize for each session:

```text
workflow_status
duration_ms
documents_fetched
raw_records
normalized_records
final_records
final_case_records
quarantined_records
pending_review_records
run_quality_status
primary_case_dataset_status
top_block_reasons
candidate_generic_defects
```

### Task 3: Apply TDD Only For Generic Defects

**Files:**
- Likely test: `tests/test_run_quality_gated_final_dataset.py`
- Likely implementation: `src/hdc_workflow/run_quality_gates.py`
- Output: `outputs/goal_round06_diagnosis/repair_summary.md`

- [ ] **Step 1: Confirm root cause before fixing**

Use diagnostic artifacts and representative records to decide whether the issue is:

```text
generic workflow bug -> write a failing test and fix
task/source limitation -> document, do not relax gates
policy decision -> stop and ask user
```

- [ ] **Step 2: RED**

For a confirmed generic workflow bug, add one focused pytest case that reproduces the wrong inclusion/exclusion behavior and run only that test. Expected: FAIL for the intended reason.

- [ ] **Step 3: GREEN**

Implement the smallest production change needed to make the RED test pass. Run the same targeted test. Expected: PASS.

- [ ] **Step 4: Regression verification**

Run the relevant test file and then the full test suite:

```powershell
python -m pytest tests\test_run_quality_gated_final_dataset.py -q
$env:PYTHONIOENCODING='utf-8'; python -m pytest -q
```

Expected: no failures.

### Task 4: Loop Decision

**Files:**
- Output: `outputs/goal_round06_diagnosis/repair_summary.md`

- [ ] **Step 1: Decide next action**

Continue to Round07 only if Round06 reveals a generic fix that has just landed and needs live validation. Stop and report if remaining failures are source scarcity, human-review policy, or unsafe threshold-relaxation decisions.
