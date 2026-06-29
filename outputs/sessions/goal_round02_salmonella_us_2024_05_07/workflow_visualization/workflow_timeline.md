# Workflow Timeline

1. `task_intake_and_scope_planning` - executed - Turns the user request into structured task scope.
2. `disease_intelligence_builder` - executed - Workflow node state and summaries are reconstructed from completed run artifacts.
3. `profile_and_schema_setup` - executed - Workflow node state and summaries are reconstructed from completed run artifacts.
4. `executable_source_planning` - executed - Workflow node state and summaries are reconstructed from completed run artifacts.
5. `query_strategy_builder` - executed - Workflow node state and summaries are reconstructed from completed run artifacts.
6. `source_discovery` - executed - Executes configured source discovery and records search-derived candidates.
7. `source_dedup_and_registry` - executed - Workflow node state and summaries are reconstructed from completed run artifacts.
8. `source_screening` - executed - Workflow node state and summaries are reconstructed from completed run artifacts.
9. `source_critic_and_uncertainty_routing` - executed - Workflow node state and summaries are reconstructed from completed run artifacts.
10. `content_fetch_and_parse` - executed - Fetches and parses allowed source documents.
11. `document_quality_check` - executed - Workflow node state and summaries are reconstructed from completed run artifacts.
12. `evidence_chunking_and_data_presence_flagging` - executed - Workflow node state and summaries are reconstructed from completed run artifacts.
13. `structured_extraction` - executed - Extracts structured public-health records from evidence chunks.
14. `schema_validation_and_repair` - executed - Workflow node state and summaries are reconstructed from completed run artifacts.
15. `record_normalization` - executed - Workflow node state and summaries are reconstructed from completed run artifacts.
16. `record_linking` - executed - Workflow node state and summaries are reconstructed from completed run artifacts.
17. `cross_source_consistency_check` - executed - Compares claims across sources without deciding official truth.
18. `quality_gate_routing` - executed - Workflow node state and summaries are reconstructed from completed run artifacts.
19. `human_review` - not_observed_in_trace - Packages uncertain or high-impact evidence for manual review.
20. `final_data_package_builder` - executed - Exports auditable datasets, diagnostics, reports, and review artifacts.
