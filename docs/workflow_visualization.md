# Workflow Visualization

## Purpose

The data collection workflow exports two visualization layers:

1. A live runtime event layer for in-progress runs.
2. Static workflow visualization artifacts for completed runs.

These artifacts make the run easier to inspect without changing source discovery, extraction, validation, dataset quality gates, graph topology, or human review decision semantics.

The static `workflow_visualization/` layer is artifact-only. It reads completed session outputs and writes HTML, JSON, Markdown, and CSV files. It does not call LLMs, search the web, fetch webpages, mutate records, apply human review decisions, or determine official truth.

## Output Directory

Each configured run writes:

```text
outputs/sessions/<session_id>/workflow_visualization/
```

The main entry point is:

```text
workflow_visualization/index.html
```

## Generated Files

- `workflow_visualization/index.html`
- `workflow_visualization/workflow_visualization_summary.json`
- `workflow_visualization/workflow_visualization_manifest.json`
- `workflow_visualization/workflow_timeline.html`
- `workflow_visualization/workflow_timeline.json`
- `workflow_visualization/workflow_timeline.md`
- `workflow_visualization/workflow_graph_topology.html`
- `workflow_visualization/workflow_graph_topology.json`
- `workflow_visualization/agentic_search_timeline.html`
- `workflow_visualization/agentic_search_timeline.json`
- `workflow_visualization/agentic_search_timeline.md`
- `workflow_visualization/evidence_flow_graph.html`
- `workflow_visualization/evidence_flow_graph.json`
- `workflow_visualization/evidence_flow_table.csv`
- `workflow_visualization/claim_comparison_cards.html`
- `workflow_visualization/claim_comparison_cards.json`
- `workflow_visualization/claim_comparison_cards.md`
- `workflow_visualization/dataset_decision_flow.html`
- `workflow_visualization/dataset_decision_flow.json`
- `workflow_visualization/dataset_decision_table.csv`
- `workflow_visualization/human_review_workflow.html`
- `workflow_visualization/human_review_workflow.json`
- `workflow_visualization/human_review_workflow.md`
- `workflow_visualization/visualization_styles.css`

Lightweight copies are also written under `diagnostics/`:

- `diagnostics/workflow_visualization_summary.json`
- `diagnostics/evidence_flow_graph.json`
- `diagnostics/dataset_decision_flow.json`

## Live Runtime Events

Every configured run writes compact live status files while the LangGraph graph
is executing:

```text
diagnostics/run_events.ndjson
diagnostics/run_status.json
diagnostics/node_status.json
```

The event stream records run start/completion, node start/completion/failure,
selected custom progress events from long-running nodes, and selected artifact
paths. Payloads are sanitized and summarized so API keys, tokens, and large
document text are not written into the event stream.

The default terminal entrypoints enable a Rich live status panel when the
terminal supports it. Use `--no-live-status` to disable the panel while still
writing runtime event files.

The optional Streamlit dashboard reads only an existing session directory:

```powershell
streamlit run scripts/live_workflow_dashboard.py -- --session-dir outputs/sessions/<session_id>
```

The optional replay notebook is written with `--write-run-notebook`:

```text
outputs/sessions/<session_id>/workflow_replay_notebook.ipynb
```

## Panels

### Workflow Timeline

`workflow_timeline` reconstructs the run sequence from `collection_trace`, `workflow_run_summary`, and node-level summaries. It shows which nodes ran, key counts, route information, warnings, and user-facing explanations.

### Workflow Graph Topology

`workflow_graph_topology` exports the current graph order documented in `src/hdc_workflow/graph.py`. It does not mutate the graph and does not add nodes.

### Agentic Search Timeline

`agentic_search_timeline` summarizes source planning, iterative search plans, observations, refinement decisions, executed query counts, search-derived candidate counts, and stop decisions.

### Evidence Flow Graph

`evidence_flow_graph` links available provenance across:

```text
source -> document -> evidence chunk -> record -> claim -> comparison/event -> dataset view -> human review item
```

Edges are only created when source IDs, document IDs, chunk IDs, record IDs, claim IDs, or dataset membership make the relationship auditable. Missing links are recorded as warnings instead of being invented.

### Claim Comparison Cards

`claim_comparison_cards` summarizes cross-source claim comparisons as cross-source supported, partially supported, conflicting, not comparable, duplicate, single-source/unverified, insufficient information, or needs human review. It does not claim official truth.

### Dataset Decision Flow

`dataset_decision_flow` shows how records move into accepted final datasets, context views, non-primary observations, quarantine, pending review, or post-review outputs. If `final_case_dataset_count = 0`, the visualization shows that explicitly rather than presenting technical completion as successful primary case collection.

### Human Review Workflow

`human_review_workflow` reads Optimization 6 artifacts and displays priority counts, top review items, decision template links, prefill links, and action guide links. Generated decision templates keep `apply_decision=false` unless a human reviewer edits them later through the existing review decision mechanism.

## Runner Integration

The configured runner now writes visualization artifacts automatically:

```powershell
python scripts\run_hdc_workflow_configured.py
```

The runner writes visualization after final package export, interpretive reports, and human review workflow artifacts, then builds the HTML console. This lets the console link the new visualization outputs.

If latest aliases are enabled, selected visualization files are copied to:

```text
outputs/workflow_visualization/
```

## Boundaries

- `workflow_visualization/` remains static artifact visualization only.
- The live dashboard reads runtime event files; it does not run search, fetch, LLM, or graph execution itself.
- No interactive human review editing.
- No source discovery, extraction, validation, quality-gate, or graph topology changes.
- No automatic truth determination.
- No medical advice or official surveillance conclusion.
- Visualization quality depends on upstream artifact completeness and provenance IDs.
