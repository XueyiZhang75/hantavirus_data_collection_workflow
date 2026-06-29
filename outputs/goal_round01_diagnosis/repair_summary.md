# Goal Round 01 Repair Summary

## TDD Repairs Applied

1. Non-interactive CLI default user request
   - Failure observed: fully specified CLI command still prompted for `user_request`, causing EOF in automated runs.
   - RED: `test_collect_inputs_uses_default_request_for_fully_specified_cli_even_when_tty` failed.
   - Fix: `_collect_inputs` now prompts for user request only in prompt-mode; fully specified CLI args use generated default request.

2. UTF-8 stdout/stderr for Windows paths
   - Failure observed: printing paths under `??` crashed with `UnicodeEncodeError` under cp1252.
   - RED: `test_configure_utf8_stdio_reconfigures_non_utf8_streams` failed.
   - Fix: `run_interactive_workflow.main()` now calls `_configure_utf8_stdio()` before printing.

3. LangSmith external trace suppression by default
   - Failure observed: live runs attempted to upload very large trace payloads to LangSmith and hit a 25MB API limit; this also created an external data-disclosure risk.
   - RED: `test_run_graph_with_events_suppresses_external_langsmith_env_by_default` failed.
   - Fix: `_run_graph_with_events` now temporarily removes LangSmith/LangChain API keys and sets tracing env flags to `false` unless `HDC_ENABLE_LANGSMITH_TRACE` is explicitly enabled.

## Verification

- Target RED tests failed before implementation: 3 failures.
- Target GREEN tests after implementation: `3 passed`.
- Related regression tests: `20 passed`.
- Full suite: `789 passed, 1 warning`.

## Data-side Findings Not Relaxed This Round

- COVID/New York: workflow fetched 31 documents and attempted 30 structured extraction calls, but all LLM outputs were empty; no records were extracted. Root area: extraction strategy / chunk selection / table or API-derived source handling, not a node crash.
- Dengue/Florida: workflow extracted 43 normalized records, but all were routed to pending review. Dominant blockers were `source_role_final_excluded` and `source_trust_requires_human_review`, plus broad/out-of-window periods. Existing tests intentionally protect this behavior for non-authoritative or uncertain sources.
- Measles/Texas: workflow produced 8 final records, with 12 quarantined and 3 pending review. This is the only one with accepted primary case records.

## Artifacts

- `diagnosis_summary.json`: machine-readable three-session diagnosis.
- `node_matrix.csv`: 01-20 node status/duration matrix.
- `diagnosis_report.md`: human-readable session and node summary.
