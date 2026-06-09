"""Pydantic schemas for the hantavirus data collection workflow."""

from __future__ import annotations

from typing import Literal

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
    start_date: str | None = None
    end_date: str | None = None
    target_fields: list[str] = Field(default_factory=list)
    source_preferences: list[str] | dict | None = None
    collection_mode: str | None = None
    user_request: str | None = None
    run_label: str | None = None
    task_input_source: str | None = None
    task_input_warnings: list[str] = Field(default_factory=list)


class StructuredTaskInput(BaseModel):
    disease: str | None = None
    location: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    target_fields: list[str] = Field(default_factory=list)
    source_preferences: list[str] | dict | None = None
    collection_mode: str | None = None
    user_request: str | None = None
    run_label: str | None = None


class DiseaseIntelligenceProfile(BaseModel):
    disease_input: str
    disease_standard_name: str
    disease_category: str | None = None
    aliases: list[str] = Field(default_factory=list)
    abbreviations: list[str] = Field(default_factory=list)
    pathogen_terms: list[str] = Field(default_factory=list)
    syndrome_terms: list[str] = Field(default_factory=list)
    clinical_terms: list[str] = Field(default_factory=list)
    transmission_terms: list[str] = Field(default_factory=list)
    case_count_terms: list[str] = Field(default_factory=list)
    death_terms: list[str] = Field(default_factory=list)
    hospitalization_terms: list[str] = Field(default_factory=list)
    surveillance_terms: list[str] = Field(default_factory=list)
    outbreak_terms: list[str] = Field(default_factory=list)
    official_source_terms: list[str] = Field(default_factory=list)
    likely_reporting_agencies: list[str] = Field(default_factory=list)
    preferred_source_categories: list[str] = Field(default_factory=list)
    validation_source_categories: list[str] = Field(default_factory=list)
    suggested_geographic_granularity: str | None = None
    suggested_time_granularity: str | None = None
    extraction_priority_fields: list[str] = Field(default_factory=list)
    count_semantics_notes: list[str] = Field(default_factory=list)
    disambiguation_risks: list[str] = Field(default_factory=list)
    exclusion_terms: list[str] = Field(default_factory=list)
    suggested_query_terms: list[str] = Field(default_factory=list)
    suggested_query_templates: list[str] = Field(default_factory=list)
    confidence: float | None = None
    generation_method: str = "curated_profile"
    warnings: list[str] = Field(default_factory=list)


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


SourceRoleHint = Literal[
    "collection",
    "validation",
    "context",
    "collection_support",
    "human_review",
]

ExecutableSourceType = Literal[
    "official_public_health_agency",
    "international_organization_report",
    "peer_reviewed_literature",
    "structured_database",
    "news_and_situation_report",
]

ExecutableQueryType = Literal[
    "general_web",
    "official_site",
    "domain_limited",
    "literature",
    "news",
    "database",
]

ExecutableProviderChannel = Literal[
    "web_search",
    "official_site_search",
    "literature_api",
    "news_search",
    "database_search",
    "manual_user_url",
]

ExecutableSourcePlanGenerationMethod = Literal[
    "deterministic_executable_source_plan",
    "llm_executable_source_plan",
    "llm_failed_deterministic_fallback",
    "invalid_llm_output_deterministic_fallback",
]

ExecutableSourcePlanExecutionStatus = Literal["planned_not_executed"]


class SourceDiscoveryObjective(BaseModel):
    objective_id: str
    objective: str
    source_role_hint: SourceRoleHint
    rationale: str
    priority: int = 5


class PlannedSourceCategory(BaseModel):
    source_category_id: str
    source_type: ExecutableSourceType
    role_hint: SourceRoleHint
    priority: int = 5
    expected_fields: list[str] = Field(default_factory=list)
    why_relevant: str
    risk_notes: list[str] = Field(default_factory=list)


class PlannedSearchQuery(BaseModel):
    query_id: str
    query: str
    query_type: ExecutableQueryType = "general_web"
    provider_channel: ExecutableProviderChannel = "web_search"
    source_type: ExecutableSourceType = "news_and_situation_report"
    role_hint: SourceRoleHint = "collection_support"
    priority: int = 5
    expected_fields: list[str] = Field(default_factory=list)
    disease_terms_used: list[str] = Field(default_factory=list)
    location_terms_used: list[str] = Field(default_factory=list)
    time_terms_used: list[str] = Field(default_factory=list)
    rationale: str
    execution_status: ExecutableSourcePlanExecutionStatus = "planned_not_executed"


class SearchResult(BaseModel):
    title: str | None = None
    url: str | None = None
    snippet: str | None = None
    published_date: str | None = None
    source: str | None = None
    rank: int | None = None
    query: str | None = None
    query_id: str | None = None
    provider_channel: str | None = None
    source_type: str | None = None
    role_hint: str | None = None
    retrieved_at: str | None = None
    provider: str | None = None
    query_type: str | None = None
    raw: dict = Field(default_factory=dict)


class SearchProviderResponse(BaseModel):
    provider: str
    query_id: str | None = None
    query: str | None = None
    results: list[SearchResult] = Field(default_factory=list)
    raw_result_count: int = 0
    error: str | None = None
    warnings: list[str] = Field(default_factory=list)


class LLMSourceCredibilitySuggestion(BaseModel):
    source_role_recommendation: str | None = None
    credibility_level: str | None = None
    risk_flags: list[str] = Field(default_factory=list)
    human_review_recommended: bool = False
    explanation: str | None = None
    confidence: float | None = None


class SourceCredibilityAssessment(BaseModel):
    source_id: str
    canonical_url: str | None = None
    title: str | None = None
    publisher: str | None = None
    domain: str | None = None
    source_type: str | None = None
    discovery_method: str | None = None
    query_id: str | None = None
    query_used: str | None = None
    role_hint: str | None = None
    source_role_recommendation: str
    source_role_final: str
    credibility_score: float
    credibility_level: str
    authority_score: float
    local_relevance_score: float
    disease_relevance_score: float
    timeliness_score: float
    geographic_granularity_score: float
    data_granularity_score: float
    machine_readability_score: float
    independence_score: float
    provenance_score: float
    risk_penalty: float
    final_score_explanation: str
    role_assignment_reason: str
    risk_flags: list[str] = Field(default_factory=list)
    human_review_recommended: bool = False
    human_review_reason: str | None = None
    assessment_method: str
    llm_used: bool = False
    llm_failed: bool = False
    llm_error_type: str | None = None
    llm_source_role_recommendation: str | None = None
    llm_source_credibility_explanation: str | None = None
    llm_source_credibility_confidence: float | None = None
    warnings: list[str] = Field(default_factory=list)


class SourcePlanningRisk(BaseModel):
    risk_id: str
    risk: str
    severity: str = "medium"
    applies_to: list[str] = Field(default_factory=list)
    mitigation: str
    human_review_trigger: bool = False


class ExecutableSourcePlan(BaseModel):
    plan_id: str
    disease: str
    location: str | None = None
    time_window: str | None = None
    target_fields: list[str] = Field(default_factory=list)
    generation_method: ExecutableSourcePlanGenerationMethod
    llm_enabled: bool = False
    execution_status: ExecutableSourcePlanExecutionStatus = "planned_not_executed"
    warnings: list[str] = Field(default_factory=list)
    source_discovery_objectives: list[SourceDiscoveryObjective] = Field(
        default_factory=list
    )
    planned_source_categories: list[PlannedSourceCategory] = Field(
        default_factory=list
    )
    planned_queries: list[PlannedSearchQuery] = Field(default_factory=list)
    source_planning_risks: list[SourcePlanningRisk] = Field(default_factory=list)
    structured_output_mode: str | None = None


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
    search_provider: str | None = None
    search_rank: int | None = None
    provider_channel: str | None = None
    role_hint: str | None = None
    planned_query_id: str | None = None
    planned_query_source_type: str | None = None
    search_result_id: str | None = None
    canonical_url: str | None = None
    domain: str | None = None
    result_source: str | None = None
    query_type: str | None = None
    additional_query_ids: list[str] = Field(default_factory=list)


class SourceRegistryEntry(BaseModel):
    source_id: str
    canonical_url: str
    title: str | None = None
    publisher: str | None = None
    source_type: str | None = None
    published_date: str | None = None
    snippet: str | None = None
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
    search_provider: str | None = None
    search_rank: int | None = None
    provider_channel: str | None = None
    role_hint: str | None = None
    planned_query_id: str | None = None
    planned_query_source_type: str | None = None
    search_result_id: str | None = None
    domain: str | None = None
    result_source: str | None = None
    query_type: str | None = None
    additional_query_ids: list[str] = Field(default_factory=list)
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
    llm_source_critic_enabled: bool = False
    llm_source_critic_failed: bool = False
    llm_source_critic_error: str | None = None
    llm_proposed_source_role: str | None = None
    llm_proposed_screening_decision: str | None = None
    llm_credibility_level: str | None = None
    llm_credibility_reason: str | None = None
    llm_expected_extractable_fields: list[str] = Field(default_factory=list)
    llm_semantic_leakage_risk: bool = False
    llm_semantic_leakage_reason: str | None = None
    llm_context_only_risk: bool = False
    llm_validation_candidate_risk: bool = False
    llm_needs_human_review: bool = False
    llm_human_review_reason: str | None = None
    llm_source_critic_confidence: float | None = None
    llm_reasoning_summary: str | None = None
    credibility_score: float | None = None
    credibility_level: str | None = None
    credibility_rubric_version: str | None = None
    credibility_score_components: dict = Field(default_factory=dict)
    credibility_flags: list[str] = Field(default_factory=list)
    credibility_reason: str | None = None
    source_role_recommendation: str | None = None
    source_role_final: str | None = None
    authority_score: float | None = None
    local_relevance_score: float | None = None
    disease_relevance_score: float | None = None
    timeliness_score: float | None = None
    geographic_granularity_score: float | None = None
    data_granularity_score: float | None = None
    machine_readability_score: float | None = None
    independence_score: float | None = None
    provenance_score: float | None = None
    risk_penalty: float | None = None
    final_score_explanation: str | None = None
    role_assignment_reason: str | None = None
    risk_flags: list[str] = Field(default_factory=list)
    human_review_recommended: bool = False
    human_review_reason: str | None = None
    assessment_method: str | None = None
    llm_used: bool = False
    llm_failed: bool = False
    llm_error_type: str | None = None
    llm_source_role_recommendation: str | None = None
    llm_source_credibility_explanation: str | None = None
    llm_source_credibility_confidence: float | None = None
    warnings: list[str] = Field(default_factory=list)
    source_excluded_by_human_review: bool = False
    source_review_status: str | None = None
    review_decision_ids: list[str] = Field(default_factory=list)
    human_review_audit_ids: list[str] = Field(default_factory=list)


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
    discovery_method: str | None = None
    search_provider: str | None = None
    query_id: str | None = None
    query_used: str | None = None
    planned_query_id: str | None = None
    provider_channel: str | None = None
    role_hint: str | None = None
    source_role_final: str | None = None
    credibility_score: float | None = None
    credibility_level: str | None = None
    source_credibility_risk_flags: list[str] = Field(default_factory=list)
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
    published_date: str | None = None
    publisher: str | None = None
    source_type: str | None = None
    source_role: str | None = None
    discovery_method: str | None = None
    search_provider: str | None = None
    query_id: str | None = None
    query_used: str | None = None
    planned_query_id: str | None = None
    provider_channel: str | None = None
    role_hint: str | None = None
    source_role_final: str | None = None
    credibility_score: float | None = None
    credibility_level: str | None = None
    source_credibility_risk_flags: list[str] = Field(default_factory=list)
    final_screening_decision: str | None = None
    fetch_purpose: str | None = None
    fetch_status: str | None = None
    fetch_error: str | None = None
    http_status_code: int | None = None
    content_type: str | None = None
    fetched_at: str | None = None
    retrieved_at: str | None = None
    parser_used: str | None = None
    text_char_count: int | None = None
    table_count: int | None = None
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
    source_role_final: str | None = None
    credibility_score: float | None = None
    credibility_level: str | None = None
    discovery_method: str | None = None
    search_provider: str | None = None
    query_id: str | None = None
    query_used: str | None = None
    planned_query_id: str | None = None
    provider_channel: str | None = None
    role_hint: str | None = None
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


class PublicHealthRecord(HantavirusRecord):
    """Disease-generic public-health record.

    This extends the legacy HantavirusRecord field set instead of replacing it.
    Downstream code that expects the old fields can still read them, while
    Stage 8 cross-disease runs can preserve disease, count, geography, and
    provenance fields that are not hantavirus-specific.
    """

    disease_standard_name: str | None = None
    disease_alias_used: str | None = None
    pathogen_or_syndrome: str | None = None
    target_population: str | None = None

    locality: str | None = None
    locality_raw: str | None = None
    admin_level: str | None = None
    location_confidence: float | None = None
    location_notes: str | None = None

    reporting_period_raw: str | None = None
    as_of_date_raw: str | None = None
    date_confidence: float | None = None
    date_notes: str | None = None

    hospitalizations: float | None = None
    icu_admissions: float | None = None
    tests_positive: float | None = None
    tests_total: float | None = None
    positivity_rate: float | None = None
    incidence_rate: float | None = None
    cumulative_count: float | None = None
    new_count: float | None = None
    count_value_raw: str | None = None
    count_unit: str | None = None
    count_semantics: str | None = None
    count_confidence: float | None = None
    count_notes: str | None = None

    source_role_final: str | None = None
    credibility_score: float | None = None
    credibility_level: str | None = None
    discovery_method: str | None = None
    search_provider: str | None = None
    query_id: str | None = None
    query_used: str | None = None
    document_id: str | None = None
    evidence_context: str | None = None
    extraction_model: str | None = None
    extraction_warnings: list[str] = Field(default_factory=list)
    human_review_reason: str | None = None
    notes: str | None = None
    record_schema: str = "generic_public_health_record"
    legacy_record_type: str | None = None

    event_cluster_id: str | None = None
    event_cluster_status: str | None = None
    event_member_status: str | None = None
    countable: bool | None = None
    duplicate_of_record_id: str | None = None
    representative_record_id: str | None = None
    duplicate_detection_method: str | None = None
    duplicate_detection_confidence: float | None = None
    duplicate_detection_reason: str | None = None
    duplicate_review_required: bool = False
    duplicate_review_reason: str | None = None
    event_cluster_warnings: list[str] = Field(default_factory=list)
    review_status: str | None = None
    review_decision_ids: list[str] = Field(default_factory=list)
    record_excluded_by_human_review: bool = False
    final_dataset_included: bool | None = None
    human_review_applied: bool = False
    human_review_audit_ids: list[str] = Field(default_factory=list)
    anomaly_status: str | None = None
    anomaly_ids: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _non_negative_generic_counts(self) -> "PublicHealthRecord":
        numeric_fields = (
            "hospitalizations",
            "icu_admissions",
            "tests_positive",
            "tests_total",
            "positivity_rate",
            "incidence_rate",
            "cumulative_count",
            "new_count",
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


class EventClusterMember(BaseModel):
    record_id: str
    event_member_status: str
    countable: bool
    duplicate_of_record_id: str | None = None
    duplicate_detection_confidence: float | None = None
    duplicate_detection_reason: str | None = None
    source_id: str | None = None
    source_url: str | None = None
    source_type: str | None = None
    publisher: str | None = None
    evidence_quote: str | None = None


class EventCluster(BaseModel):
    event_cluster_id: str
    cluster_status: str
    disease: str | None = None
    disease_standard_name: str | None = None
    location_key: str | None = None
    country: str | None = None
    subnational_location: str | None = None
    locality: str | None = None
    admin_level: str | None = None
    date_key: str | None = None
    date_reported: str | None = None
    event_start_date: str | None = None
    event_end_date: str | None = None
    reporting_period: str | None = None
    as_of_date: str | None = None
    statistical_count_type: str | None = None
    count_semantics: str | None = None
    representative_record_id: str | None = None
    representative_selection_reason: str | None = None
    member_record_ids: list[str] = Field(default_factory=list)
    members: list[EventClusterMember] = Field(default_factory=list)
    countable_record_ids: list[str] = Field(default_factory=list)
    non_countable_duplicate_record_ids: list[str] = Field(default_factory=list)
    related_record_ids: list[str] = Field(default_factory=list)
    conflict_record_ids: list[str] = Field(default_factory=list)
    source_ids: list[str] = Field(default_factory=list)
    source_urls: list[str] = Field(default_factory=list)
    source_types: list[str] = Field(default_factory=list)
    publishers: list[str] = Field(default_factory=list)
    discovery_methods: list[str] = Field(default_factory=list)
    search_providers: list[str] = Field(default_factory=list)
    source_role_final_values: list[str] = Field(default_factory=list)
    credibility_score_range: dict = Field(default_factory=dict)
    canonical_cases_confirmed: float | None = None
    canonical_cases_probable: float | None = None
    canonical_cases_suspected: float | None = None
    canonical_cases_unspecified: float | None = None
    canonical_deaths: float | None = None
    canonical_hospitalizations: float | None = None
    canonical_count_notes: str | None = None
    source_count: int = 0
    independent_source_count: int = 0
    same_event_score: float | None = None
    cluster_reason: str | None = None
    duplicate_reason: str | None = None
    needs_human_review: bool = False
    human_review_reason: str | None = None
    warnings: list[str] = Field(default_factory=list)
    review_status: str | None = None
    review_decision_ids: list[str] = Field(default_factory=list)
    human_review_applied: bool = False
    human_review_audit_ids: list[str] = Field(default_factory=list)


class DuplicateDetectionDecision(BaseModel):
    event_cluster_id: str
    member_record_ids: list[str] = Field(default_factory=list)
    representative_record_id: str | None = None
    decision: str
    confidence: float | None = None
    reason: str | None = None
    requires_human_review: bool = False


ValidationUnit = Literal[
    "record",
    "event_cluster",
    "aggregate",
    "field",
    "source",
    "scope",
]

ValidationType = Literal[
    "trusted_source_comparison",
    "held_out_source_comparison",
    "cross_source_support",
    "cross_source_conflict",
    "event_cluster_support",
    "aggregate_comparison",
    "scope_check",
    "count_semantics_check",
    "provenance_check",
]

ComparabilityStatus = Literal[
    "comparable",
    "partially_comparable",
    "not_comparable",
    "insufficient_information",
    "needs_human_review",
]

MatchStatus = Literal[
    "matched",
    "partially_matched",
    "conflict",
    "missing_collection",
    "missing_validation",
    "not_comparable",
    "outside_requested_scope",
    "insufficient_information",
    "needs_human_review",
]

ValidationStatus = Literal[
    "validated",
    "partially_validated",
    "conflict",
    "not_comparable",
    "missing_counterpart",
    "outside_scope",
    "needs_human_review",
    "unvalidated",
]


class ComparabilityAssessment(BaseModel):
    comparability_status: ComparabilityStatus
    match_status: MatchStatus
    validation_status: ValidationStatus
    reason: str
    warnings: list[str] = Field(default_factory=list)


class ValidationCase(BaseModel):
    validation_case_id: str
    validation_type: ValidationType
    validation_unit: ValidationUnit
    record_ids: list[str] = Field(default_factory=list)
    event_cluster_ids: list[str] = Field(default_factory=list)
    source_ids: list[str] = Field(default_factory=list)
    source_urls: list[str] = Field(default_factory=list)
    disease: str | None = None
    location: str | None = None
    date_or_period: str | None = None
    reason: str | None = None
    metadata: dict = Field(default_factory=dict)


class ValidationComparison(BaseModel):
    comparison_id: str
    validation_case_id: str
    validation_type: ValidationType
    validation_unit: ValidationUnit
    left_record_ids: list[str] = Field(default_factory=list)
    right_record_ids: list[str] = Field(default_factory=list)
    left_event_cluster_ids: list[str] = Field(default_factory=list)
    right_event_cluster_ids: list[str] = Field(default_factory=list)
    left_source_ids: list[str] = Field(default_factory=list)
    right_source_ids: list[str] = Field(default_factory=list)
    compared_field: str | None = None
    left_value: float | str | bool | dict | list | None = None
    right_value: float | str | bool | dict | list | None = None
    comparability_status: ComparabilityStatus = "insufficient_information"
    reason: str | None = None


class ValidationResult(BaseModel):
    validation_result_id: str
    validation_case_id: str
    validation_type: ValidationType
    validation_unit: ValidationUnit
    comparison_id: str
    left_record_ids: list[str] = Field(default_factory=list)
    right_record_ids: list[str] = Field(default_factory=list)
    left_event_cluster_ids: list[str] = Field(default_factory=list)
    right_event_cluster_ids: list[str] = Field(default_factory=list)
    left_source_ids: list[str] = Field(default_factory=list)
    right_source_ids: list[str] = Field(default_factory=list)
    left_source_urls: list[str] = Field(default_factory=list)
    right_source_urls: list[str] = Field(default_factory=list)
    left_source_roles: list[str] = Field(default_factory=list)
    right_source_roles: list[str] = Field(default_factory=list)
    left_discovery_methods: list[str] = Field(default_factory=list)
    right_discovery_methods: list[str] = Field(default_factory=list)
    compared_field: str
    disease: str | None = None
    location: str | None = None
    geographic_scope: str | None = None
    date_or_period: str | None = None
    reporting_period: str | None = None
    as_of_date: str | None = None
    statistical_count_type: str | None = None
    count_semantics: str | None = None
    left_value: float | str | bool | dict | list | None = None
    right_value: float | str | bool | dict | list | None = None
    tolerance: float | None = None
    comparability_status: ComparabilityStatus
    match_status: MatchStatus
    validation_status: ValidationStatus
    confidence: float | None = None
    reason: str
    evidence_summary: str | None = None
    needs_human_review: bool = False
    human_review_reason: str | None = None
    warnings: list[str] = Field(default_factory=list)
    review_status: str | None = None
    review_decision_ids: list[str] = Field(default_factory=list)
    human_review_applied: bool = False
    human_review_audit_ids: list[str] = Field(default_factory=list)


class TrustedSourceValidationResult(ValidationResult):
    """ValidationResult specialization for trusted/held-out validation."""


class CrossSourceValidationResult(ValidationResult):
    """ValidationResult specialization for event-cluster cross-source checks."""


AnomalyUnit = Literal[
    "record",
    "event_cluster",
    "aggregate",
    "validation_result",
    "source",
    "workflow_run",
]

AnomalySeverity = Literal["info", "low", "medium", "high", "critical"]


class AnomalyRule(BaseModel):
    rule_id: str
    anomaly_type: str
    description: str
    severity: AnomalySeverity = "medium"
    deterministic: bool = True


class AnomalyDetectionDecision(BaseModel):
    anomaly_id: str
    decision: str
    reason: str | None = None
    reviewer_id: str | None = None
    decided_at: str | None = None


class AnomalyResult(BaseModel):
    anomaly_id: str
    anomaly_type: str
    anomaly_unit: AnomalyUnit
    severity: AnomalySeverity
    record_id: str | None = None
    event_cluster_id: str | None = None
    validation_result_id: str | None = None
    source_id: str | None = None
    compared_field: str | None = None
    disease: str | None = None
    location: str | None = None
    date_or_period: str | None = None
    source_ids: list[str] = Field(default_factory=list)
    source_urls: list[str] = Field(default_factory=list)
    evidence_summary: str | None = None
    observed_value: float | str | bool | dict | list | None = None
    expected_or_reference_value: float | str | bool | dict | list | None = None
    threshold: float | str | None = None
    reason: str
    recommended_action: str | None = None
    needs_human_review: bool = False
    human_review_reason: str | None = None
    detection_method: str = "deterministic_anomaly_detection"
    warnings: list[str] = Field(default_factory=list)
    anomaly_status: str = "open"
    review_decision_ids: list[str] = Field(default_factory=list)
    human_review_audit_ids: list[str] = Field(default_factory=list)


class AnomalySummary(BaseModel):
    anomaly_result_count: int = 0
    needs_human_review_count: int = 0
    severity_counts: dict[str, int] = Field(default_factory=dict)
    anomaly_type_counts: dict[str, int] = Field(default_factory=dict)
    detection_method: str = "deterministic_anomaly_detection"
    thresholds: dict = Field(default_factory=dict)


class HumanReviewDecisionInput(BaseModel):
    decision_id: str
    decision_type: str
    target_type: str
    target_ids: list[str] = Field(default_factory=list)
    review_id: str | None = None
    reviewer_id: str | None = None
    decided_at: str | None = None
    reason: str | None = None
    notes: str | None = None
    patch: dict = Field(default_factory=dict)
    corrected_fields: dict = Field(default_factory=dict)
    confidence: float | None = None
    apply_decision: bool = False


class AppliedHumanReviewDecision(BaseModel):
    decision_id: str
    review_id: str | None = None
    decision_type: str
    reviewer_id: str | None = None
    decided_at: str | None = None
    applied_at: str
    target_type: str
    target_ids: list[str] = Field(default_factory=list)
    reason: str | None = None
    notes: str | None = None
    confidence: float | None = None
    audit_ids: list[str] = Field(default_factory=list)
    apply_status: str = "applied"


class RejectedHumanReviewDecision(BaseModel):
    decision_id: str | None = None
    review_id: str | None = None
    decision_type: str | None = None
    target_type: str | None = None
    target_ids: list[str] = Field(default_factory=list)
    rejection_reason: str
    apply_status: str = "rejected"
    raw_decision: dict = Field(default_factory=dict)


class HumanReviewAuditEntry(BaseModel):
    audit_id: str
    decision_id: str | None = None
    review_id: str | None = None
    reviewer_id: str | None = None
    decided_at: str | None = None
    applied_at: str
    decision_type: str
    target_type: str
    target_ids: list[str] = Field(default_factory=list)
    field_name: str | None = None
    before_value: float | str | bool | dict | list | None = None
    after_value: float | str | bool | dict | list | None = None
    apply_status: str
    rejection_reason: str | None = None
    reason: str | None = None
    notes: str | None = None
    provenance: dict = Field(default_factory=dict)


class HumanReviewApplicationSummary(BaseModel):
    records_before_review: int = 0
    records_after_review: int = 0
    records_excluded_by_review: int = 0
    records_corrected_by_review: int = 0
    clusters_modified_by_review: int = 0
    validation_results_modified_by_review: int = 0
    sources_modified_by_review: int = 0
    anomalies_resolved_by_review: int = 0
    decisions_provided_count: int = 0
    decisions_applied_count: int = 0
    decisions_rejected_count: int = 0
    audit_entry_count: int = 0


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
    anomaly_id: str | None = None
    record_id: str | None = None
    event_cluster_id: str | None = None
    validation_result_id: str | None = None
    source_ids: list[str] = Field(default_factory=list)
    source_urls: list[str] = Field(default_factory=list)
    severity: str | None = None
    evidence_summary: str | None = None
    suggested_action: str | None = None
    decision_options: list[str] = Field(default_factory=list)


class FinalDataPackage(BaseModel):
    final_dataset: list[PublicHealthRecord]
    final_dataset_post_review: list[PublicHealthRecord] = Field(default_factory=list)
    records_excluded_by_human_review: list[PublicHealthRecord] = Field(default_factory=list)
    source_registry: list[SourceRegistryEntry]
    linked_events: list[LinkedEvent]
    event_clusters: list[EventCluster] = Field(default_factory=list)
    duplicate_clusters: list[EventCluster] = Field(default_factory=list)
    validation_cases: list[ValidationCase] = Field(default_factory=list)
    validation_comparisons: list[ValidationComparison] = Field(default_factory=list)
    validation_results: list[ValidationResult] = Field(default_factory=list)
    validation_summary: dict = Field(default_factory=dict)
    trusted_source_validation_summary: dict = Field(default_factory=dict)
    cross_source_validation_summary: dict = Field(default_factory=dict)
    anomaly_results: list[AnomalyResult] = Field(default_factory=list)
    anomaly_summary: dict = Field(default_factory=dict)
    applied_human_review_decisions: list[AppliedHumanReviewDecision] = Field(default_factory=list)
    rejected_human_review_decisions: list[RejectedHumanReviewDecision] = Field(default_factory=list)
    human_review_audit_trail: list[HumanReviewAuditEntry] = Field(default_factory=list)
    human_review_application_summary: dict = Field(default_factory=dict)
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
    hospitalizations: float | None = None
    icu_admissions: float | None = None
    tests_positive: float | None = None
    tests_total: float | None = None
    positivity_rate: float | None = None
    incidence_rate: float | None = None
    case_definition: str | None = None
    extraction_notes: str | None = None
    statistical_count_type: str | None = None
    count_semantics: str | None = None
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
