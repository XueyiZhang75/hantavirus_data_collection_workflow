"""Pydantic schemas for the hantavirus data collection workflow."""

from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


class CollectionSpec(BaseModel):
    task_type: str
    disease: str
    target_population: str
    data_focus: str
    geography: str | None = None
    time_window: str | None = None
    required_fields: list[str]
    source_priority: list[str]


class DiseaseProfile(BaseModel):
    disease_standard_name: str
    disease_family: str | None = None
    include_terms: list[str]
    syndrome_terms: list[str]
    virus_terms: list[str]
    exclude_terms: list[str]
    target_population: str
    primary_data_objects: list[str]
    required_record_fields: list[str]


class SearchQuerySet(BaseModel):
    official_source_queries: list[str]
    literature_queries: list[str]
    news_and_report_queries: list[str]
    database_queries: list[str]


class DataFieldSpec(BaseModel):
    name: str
    type: str
    required: bool
    description: str


class CollectionSchema(BaseModel):
    schema_name: str
    schema_version: str
    description: str
    record_type: str
    core_fields: list[DataFieldSpec]
    extraction_rules: list[str]


class SourceCategory(BaseModel):
    source_type: str
    priority: int
    description: str
    example_domains: list[str] = Field(default_factory=list)
    example_databases: list[str] = Field(default_factory=list)
    example_sources: list[str] = Field(default_factory=list)


class ScreeningCriteria(BaseModel):
    include_if_all_apply: list[str]
    exclude_if_any_apply: list[str]
    uncertain_if_any_apply: list[str]


class SourceStrategy(BaseModel):
    source_categories: list[SourceCategory]
    screening_criteria: ScreeningCriteria


class SearchQuery(BaseModel):
    query_id: str
    query: str
    source_type: str
    priority: int
    rationale: str
    expected_fields: list[str]


class SourceCandidate(BaseModel):
    source_id: str
    title: str | None = None
    url: str
    publisher: str | None = None
    source_type: str | None = None
    published_date: str | None = None
    snippet: str | None = None
    query_used: str | None = None
    retrieved_at: str | None = None
    query_id: str | None = None
    discovery_method: str | None = None
    seed_source_id: str | None = None
    priority: int | None = None
    expected_fields: list[str] = Field(default_factory=list)
    matched_terms: list[str] = Field(default_factory=list)
    source_purpose: str | None = None
    notes: str | None = None


class SourceRegistryEntry(BaseModel):
    source_id: str
    canonical_url: str
    title: str | None = None
    publisher: str | None = None
    source_type: str | None = None
    published_date: str | None = None
    status: str
    screening_decision: str | None = None
    screening_confidence: float | None = None
    screening_reason: str | None = None
    critic_decision: str | None = None
    critic_confidence: float | None = None
    critic_reason: str | None = None
    query_id: str | None = None
    query_used: str | None = None
    discovery_method: str | None = None
    seed_source_id: str | None = None
    priority: int | None = None
    expected_fields: list[str] = Field(default_factory=list)
    matched_terms: list[str] = Field(default_factory=list)
    source_purpose: str | None = None
    notes: str | None = None
    source_role: str | None = None
    screening_flags: list[str] = Field(default_factory=list)
    expected_extractable_fields: list[str] = Field(default_factory=list)
    critic_agrees_with_screening: bool | None = None
    critic_flags: list[str] = Field(default_factory=list)
    final_screening_decision: str | None = None
    final_screening_confidence: float | None = None
    final_screening_reason: str | None = None
    ready_for_content_fetch: bool = False
    requires_human_review: bool = False
    routing_flags: list[str] = Field(default_factory=list)


class SeedSource(BaseModel):
    seed_source_id: str
    title: str
    url: str
    publisher: str
    source_type: str
    priority: int
    source_purpose: str
    expected_fields: list[str]
    match_terms: list[str]
    notes: str | None = None


class SeedSourceCatalog(BaseModel):
    catalog_name: str
    catalog_version: str
    description: str
    seed_sources: list[SeedSource]


class SourceScreeningPolicy(BaseModel):
    policy_name: str
    policy_version: str
    description: str
    decision_labels: dict
    thresholds: dict
    target_data_fields: list[str]
    context_fields: list[str]
    data_source_signals: list[str]
    context_source_signals: list[str]
    search_endpoint_publishers: list[str]
    placeholder_uri_prefixes: list[str]
    human_review_triggers: list[str]


class SourceScreeningResult(BaseModel):
    source_id: str
    screening_decision: str
    screening_confidence: float
    screening_reason: str
    source_role: str
    screening_flags: list[str] = Field(default_factory=list)
    expected_extractable_fields: list[str] = Field(default_factory=list)


class SourceCriticResult(BaseModel):
    source_id: str
    critic_decision: str
    critic_confidence: float
    critic_reason: str
    critic_agrees_with_screening: bool
    critic_flags: list[str] = Field(default_factory=list)


class SourceFinalRoutingDecision(BaseModel):
    source_id: str
    final_decision: str
    final_confidence: float
    final_reason: str
    ready_for_content_fetch: bool
    requires_human_review: bool
    routing_flags: list[str] = Field(default_factory=list)


class ContentFetchPolicy(BaseModel):
    policy_name: str
    policy_version: str
    description: str
    fetchable_final_decisions: list[str]
    deferred_final_decisions: list[str]
    fetch_purpose_by_decision: dict[str, str]
    allowed_url_schemes: list[str]
    blocked_url_schemes: list[str]
    search_endpoint_publishers: list[str]
    request: dict
    document_quality: dict


class ContentFetchRequest(BaseModel):
    source_id: str
    url: str
    canonical_url: str
    publisher: str | None = None
    source_type: str | None = None
    source_role: str | None = None
    final_screening_decision: str
    fetch_purpose: str
    priority: int | None = None
    live_fetch_enabled: bool = False


class FixtureDocument(BaseModel):
    fixture_id: str
    source_id: str
    title: str
    document_type: str
    clean_text: str
    tables: list[dict] = Field(default_factory=list)
    notes: str | None = None


class FixtureDocumentCatalog(BaseModel):
    catalog_name: str
    catalog_version: str
    description: str
    fixture_documents: list[FixtureDocument]


class ContentFetchResult(BaseModel):
    source_id: str
    url: str
    fetch_status: str
    document_type: str | None = None
    http_status_code: int | None = None
    content_type: str | None = None
    fetched_at: str | None = None
    error: str | None = None


class EvidenceChunkingPolicy(BaseModel):
    policy_name: str
    policy_version: str
    description: str
    chunkable_quality_statuses: list[str]
    excluded_quality_statuses: list[str]
    max_chunk_chars: int
    chunk_overlap_chars: int
    min_chunk_chars: int
    table_chunking: dict
    target_data_signals: dict[str, list[str]]
    context_signals: dict[str, list[str]]
    presence_thresholds: dict[str, int]


class StructuredExtractionPolicy(BaseModel):
    policy_name: str
    policy_version: str
    description: str
    default_disease: str
    extraction_method: str
    extractable_chunk_conditions: dict
    virus_or_syndrome_terms: dict[str, list[str]]
    case_keywords: dict[str, list[str]]
    death_keywords: list[str]
    date_patterns: dict
    required_provenance_fields: list[str]
    required_core_fields_for_valid_record: list[str]
    fields_that_trigger_human_review_if_missing: list[str]
    minimum_content_requirement: str
    repair_rules: list[str]
    statistical_count_type_aliases: dict[str, list[str]] = Field(default_factory=dict)


class SchemaValidationResult(BaseModel):
    record_id: str
    schema_status: str
    provenance_status: str
    validation_errors: list[str] = Field(default_factory=list)
    missing_fields: list[str] = Field(default_factory=list)
    repair_actions: list[str] = Field(default_factory=list)
    requires_human_review: bool = False


class RecordNormalizationPolicy(BaseModel):
    policy_name: str
    policy_version: str
    description: str
    country_aliases: dict[str, str]
    subnational_country_map: dict[str, str]
    non_country_geographic_terms: list[str]
    virus_or_syndrome_aliases: dict[str, str]
    case_definition_aliases: dict[str, str]
    allowed_source_types: list[str]
    date_normalization: dict
    normalization_statuses: list[str]
    review_triggers: list[str]
    region_geographic_terms: list[str] = Field(default_factory=list)


class RecordNormalizationResult(BaseModel):
    record_id: str
    normalization_status: str
    normalization_actions: list[str] = Field(default_factory=list)
    normalization_warnings: list[str] = Field(default_factory=list)
    requires_human_review: bool = False


class RecordLinkingPolicy(BaseModel):
    policy_name: str
    policy_version: str
    description: str
    linking_method: str
    allowed_input_normalization_statuses: list[str]
    event_key_fields: list[str]
    date_anchor_preference: list[str]
    missing_value_token: str
    unspecified_virus_token: str
    unspecified_subnational_token: str
    linking_statuses: list[str]
    review_triggers: list[str]
    minimum_event_key_requirements: dict
    source_diversity_fields: list[str]


class RecordLinkingResult(BaseModel):
    record_id: str
    linked_event_id: str | None = None
    event_key: str | None = None
    linking_status: str
    linking_actions: list[str] = Field(default_factory=list)
    linking_warnings: list[str] = Field(default_factory=list)
    requires_human_review: bool = False


class CrossSourceConsistencyPolicy(BaseModel):
    policy_name: str
    policy_version: str
    description: str
    consistency_method: str
    comparable_numeric_fields: list[str]
    comparable_text_fields: list[str]
    comparable_date_fields: list[str]
    numeric_conflict_thresholds: dict
    severity_levels: list[str]
    conflict_types: list[str]
    human_review_triggers: list[str]
    source_authority_priority: dict[str, int]
    event_consistency_statuses: list[str]
    record_conflict_statuses: list[str]


class HumanReviewPolicy(BaseModel):
    policy_name: str
    policy_version: str
    description: str
    review_item_types: list[str]
    allowed_decisions: list[str]
    review_statuses: list[str]
    priority_by_item_type: dict[str, int]
    decision_to_status: dict[str, str]
    packet_sections_by_item_type: dict[str, list[str]]
    synthetic_fixture_warning: str


class HumanReviewDecision(BaseModel):
    review_id: str
    decision: str
    reviewer_id: str | None = None
    notes: str | None = None
    modified_values: dict = Field(default_factory=dict)
    decided_at: str | None = None


class HumanReviewPacket(BaseModel):
    review_id: str
    item_type: str
    priority: int
    status: str
    reason: str
    related_ids: list[str]
    packet_sections: dict = Field(default_factory=dict)
    synthetic_fixture_warning: str | None = None


class FieldComparisonResult(BaseModel):
    linked_event_id: str
    field: str
    compared_record_ids: list[str] = Field(default_factory=list)
    unique_values: list = Field(default_factory=list)
    conflict_detected: bool
    conflict_type: str | None = None
    severity: str | None = None
    possible_reason: str | None = None
    recommended_action: str | None = None
    requires_human_review: bool = False


class Document(BaseModel):
    source_id: str
    document_type: str | None = None
    clean_text: str | None = None
    tables: list[dict] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
    parse_status: str = "not_started"
    quality_status: str | None = None
    quality_issues: list[str] = Field(default_factory=list)
    url: str | None = None
    canonical_url: str | None = None
    title: str | None = None
    publisher: str | None = None
    source_type: str | None = None
    source_role: str | None = None
    final_screening_decision: str | None = None
    fetch_purpose: str | None = None
    fetch_status: str | None = None
    fetch_error: str | None = None
    http_status_code: int | None = None
    content_type: str | None = None
    fetched_at: str | None = None
    content_hash: str | None = None
    is_live_fetched: bool = False
    is_offline_stub: bool = False
    is_fixture_document: bool = False
    fixture_id: str | None = None
    fixture_notes: str | None = None


class EvidenceChunk(BaseModel):
    chunk_id: str
    source_id: str
    text: str
    section: str | None = None
    page: int | None = None
    table_id: str | None = None
    contains_target_data: bool | None = None
    data_types: list[str] = Field(default_factory=list)
    confidence: float | None = None
    document_type: str | None = None
    fetch_purpose: str | None = None
    source_url: str | None = None
    canonical_url: str | None = None
    title: str | None = None
    publisher: str | None = None
    source_type: str | None = None
    source_role: str | None = None
    quality_status: str | None = None
    chunk_index: int | None = None
    chunk_kind: str | None = None
    char_start: int | None = None
    char_end: int | None = None
    context_types: list[str] = Field(default_factory=list)
    presence_reason: str | None = None


class HantavirusRecord(BaseModel):
    record_id: str
    disease: str
    virus_or_syndrome: str | None = None
    country: str | None = None
    subnational_location: str | None = None
    date_reported: str | None = None
    event_start_date: str | None = None
    event_end_date: str | None = None
    cases_confirmed: float | None = None
    cases_probable: float | None = None
    cases_suspected: float | None = None
    cases_unspecified: float | None = None
    deaths: float | None = None
    case_definition: str | None = None
    source_id: str | None = None
    source_url: str | None = None
    source_type: str | None = None
    evidence_quote: str | None = None
    extraction_confidence: float | None = None
    missing_fields: list[str] = Field(default_factory=list)
    schema_status: str | None = None
    provenance_status: str | None = None
    supporting_chunk_id: str | None = None
    source_title: str | None = None
    publisher: str | None = None
    document_type: str | None = None
    fetch_purpose: str | None = None
    chunk_kind: str | None = None
    data_types: list[str] = Field(default_factory=list)
    context_types: list[str] = Field(default_factory=list)
    extraction_method: str | None = None
    extraction_reason: str | None = None
    validation_errors: list[str] = Field(default_factory=list)
    repair_actions: list[str] = Field(default_factory=list)
    requires_human_review: bool = False
    country_raw: str | None = None
    subnational_location_raw: str | None = None
    date_reported_raw: str | None = None
    event_start_date_raw: str | None = None
    event_end_date_raw: str | None = None
    virus_or_syndrome_raw: str | None = None
    case_definition_raw: str | None = None
    source_type_raw: str | None = None
    normalization_status: str | None = None
    normalization_actions: list[str] = Field(default_factory=list)
    normalization_warnings: list[str] = Field(default_factory=list)
    normalized_by: str | None = None
    linked_event_id: str | None = None
    event_key: str | None = None
    date_anchor: str | None = None
    date_anchor_field: str | None = None
    record_linking_status: str | None = None
    record_linking_actions: list[str] = Field(default_factory=list)
    record_linking_warnings: list[str] = Field(default_factory=list)
    conflict_ids: list[str] = Field(default_factory=list)
    record_conflict_status: str | None = None
    record_consistency_warnings: list[str] = Field(default_factory=list)
    llm_used: bool = False
    llm_model: str | None = None
    llm_provider: str | None = None
    llm_extraction_error: str | None = None
    extraction_mode: str | None = None
    statistical_count_type: str | None = None
    reporting_period: str | None = None
    as_of_date: str | None = None
    aggregation_level: str | None = None
    geographic_scope: str | None = None
    geographic_scope_type: str | None = None
    population_scope: str | None = None
    source_section: str | None = None
    semantic_warnings: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _non_negative_counts(self) -> "HantavirusRecord":
        numeric_fields = (
            "cases_confirmed",
            "cases_probable",
            "cases_suspected",
            "cases_unspecified",
            "deaths",
        )
        for field_name in numeric_fields:
            value = getattr(self, field_name)
            if value is not None and value < 0:
                raise ValueError(
                    f"{field_name} must be non-negative when provided (got {value})."
                )
        return self


class LinkedEvent(BaseModel):
    linked_event_id: str
    record_ids: list[str]
    linking_basis: list[str]
    linking_confidence: float | None = None
    event_key: str | None = None
    disease: str | None = None
    virus_or_syndrome: str | None = None
    country: str | None = None
    subnational_location: str | None = None
    date_anchor: str | None = None
    date_anchor_field: str | None = None
    record_count: int | None = None
    source_ids: list[str] = Field(default_factory=list)
    source_urls: list[str] = Field(default_factory=list)
    source_types: list[str] = Field(default_factory=list)
    publishers: list[str] = Field(default_factory=list)
    representative_record_id: str | None = None
    linking_status: str | None = None
    linking_method: str | None = None
    linking_warnings: list[str] = Field(default_factory=list)
    requires_human_review: bool = False
    consistency_status: str | None = None
    conflict_ids: list[str] = Field(default_factory=list)
    consistency_warnings: list[str] = Field(default_factory=list)
    checked_by: str | None = None


class Conflict(BaseModel):
    conflict_id: str
    linked_event_id: str | None = None
    field: str
    values: list[dict]
    conflict_type: str
    severity: str
    possible_reason: str | None = None
    recommended_action: str | None = None
    record_ids: list[str] = Field(default_factory=list)
    source_ids: list[str] = Field(default_factory=list)
    source_urls: list[str] = Field(default_factory=list)
    source_types: list[str] = Field(default_factory=list)
    evidence_quotes: list[str] = Field(default_factory=list)
    requires_human_review: bool = False
    resolution_status: str = "unresolved"
    comparison_basis: str | None = None
    conflict_warnings: list[str] = Field(default_factory=list)
    created_by: str | None = None


class HumanReviewItem(BaseModel):
    review_id: str
    item_type: str
    related_ids: list[str]
    reason: str
    status: str = "pending"
    human_decision: str | None = None
    notes: str | None = None
    priority: int | None = None
    review_packet: dict | None = None
    decision_source: str | None = None
    reviewer_id: str | None = None
    decided_at: str | None = None
    modified_values: dict = Field(default_factory=dict)
    decision_applied: bool = False
    decision_warnings: list[str] = Field(default_factory=list)


class FinalDataPackage(BaseModel):
    final_dataset: list[HantavirusRecord]
    source_registry: list[SourceRegistryEntry]
    linked_events: list[LinkedEvent]
    conflicts: list[Conflict]
    human_review_items: list[HumanReviewItem]
    excluded_sources: list[SourceRegistryEntry]
    collection_trace: list[dict]
    package_metadata: dict = Field(default_factory=dict)
    workflow_summaries: dict = Field(default_factory=dict)
    data_dictionary: list[dict] = Field(default_factory=list)
    provenance_manifest: dict = Field(default_factory=dict)
    export_manifest: dict = Field(default_factory=dict)
    export_warnings: list[str] = Field(default_factory=list)
    contains_synthetic_fixture_data: bool = False
    synthetic_fixture_notice: str | None = None


class LLMStructuredExtractionPolicy(BaseModel):
    policy_name: str
    policy_version: str
    description: str
    enabled_env_var: str
    default_enabled: bool
    fallback_to_rule_based_env_var: str
    default_fallback_to_rule_based: bool
    llm_extraction_method: str
    system_prompt: str
    required_output_rules: list[str]
    allowed_fetch_purposes: list[str]
    allowed_chunk_kinds: list[str]
    max_records_per_chunk: int
    allowed_statistical_count_types: list[str] = Field(default_factory=list)
    allowed_geographic_scope_types: list[str] = Field(default_factory=list)


class LLMExtractedRecord(BaseModel):
    disease: str | None = None
    virus_or_syndrome: str | None = None
    country: str | None = None
    subnational_location: str | None = None
    date_reported: str | None = None
    event_start_date: str | None = None
    event_end_date: str | None = None
    cases_confirmed: float | None = None
    cases_probable: float | None = None
    cases_suspected: float | None = None
    cases_unspecified: float | None = None
    deaths: float | None = None
    case_definition: str | None = None
    extraction_notes: str | None = None
    statistical_count_type: str | None = None
    reporting_period: str | None = None
    as_of_date: str | None = None
    aggregation_level: str | None = None
    geographic_scope: str | None = None
    geographic_scope_type: str | None = None
    population_scope: str | None = None
    source_section: str | None = None


class LLMExtractionOutput(BaseModel):
    records: list[LLMExtractedRecord] = Field(default_factory=list)
    chunk_is_relevant: bool = False
    extraction_notes: str | None = None


class FinalPackagePolicy(BaseModel):
    policy_name: str
    policy_version: str
    description: str
    package_version: str
    package_builder: str
    fixed_generated_at: str
    final_dataset_field_order: list[str]
    workflow_summary_fields: list[str]
    synthetic_fixture_markers: list[str]
    exportable_sections: list[str]


class TraceEvent(BaseModel):
    node_name: str
    message: str
    metadata: dict = Field(default_factory=dict)
