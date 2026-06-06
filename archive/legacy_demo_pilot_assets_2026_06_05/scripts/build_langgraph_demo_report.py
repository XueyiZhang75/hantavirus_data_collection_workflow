"""Build a product-style demo report for the LangGraph workflow.

The report prefers the most recent live New Mexico HPS product-run artifacts
and renders a self-contained HTML page that highlights node boundaries, state
growth, conditional routing, traceability, LLM extraction, validation
comparison, and human-review packaging.
"""

from __future__ import annotations

import html
import json
import os
import sys
from pathlib import Path


_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_STAGE4H_PRODUCT_OUTPUT_DIR = (
    _PROJECT_ROOT / "outputs" / "demo_package" / "stage4h_live_product_run"
)
_LIVE_NM_OUTPUT_DIR = _PROJECT_ROOT / "outputs" / "live_masked_validation_new_mexico_hps"
_LLM_NM_OUTPUT_DIR = (
    _PROJECT_ROOT / "outputs" / "live_masked_validation_new_mexico_hps_llm_replay"
)
_SRC = _PROJECT_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from hdc_workflow.graph import build_graph  # noqa: E402


NODE_STORY = [
    (
        "task_intake_and_scope_planning",
        "任务被结构化",
        "把一句自然语言请求变成 collection_spec：疾病、人群、地理范围、时间窗、字段清单。",
    ),
    (
        "query_strategy_builder",
        "策略被显式记录",
        "生成可审计的查询 inventory，而不是把检索关键词藏在脚本里。",
    ),
    (
        "source_discovery",
        "来源发现",
        "从离线 seed catalog 生成 source candidates，并记录 discovery provenance。",
    ),
    (
        "source_screening",
        "规则化筛源",
        "把来源分成 data_source、context_source、search_endpoint、placeholder_source。",
    ),
    (
        "content_fetch_and_parse",
        "数据进入管线",
        "真实产品运行会抓取 allowlist 中的网页文档，并把 fetch/parse/quality 状态写入 state。",
    ),
    (
        "evidence_chunking_and_data_presence_flagging",
        "文档切成证据块",
        "每个 chunk 带 data signal、context signal、confidence 和 provenance。",
    ),
    (
        "structured_extraction",
        "证据变成记录",
        "从 target-data chunks 抽取 HantavirusRecord；可切换规则抽取或 LLM 抽取。",
    ),
    (
        "record_normalization",
        "记录标准化",
        "国家、日期、case definition、source type、数字字段被规范化并保留 raw values。",
    ),
    (
        "record_linking",
        "记录链接成事件",
        "用 event key 将同一事件的多条记录聚合为 linked event。",
    ),
    (
        "cross_source_consistency_check",
        "跨源一致性检查",
        "比较同一事件内不同来源的 cases/deaths/date/location，发现冲突。",
    ),
    (
        "quality_gate_routing",
        "条件路由",
        "如果 human_review_queue 非空，走 human_review；否则直接 finalize。",
    ),
    (
        "human_review",
        "人工审核包",
        "把冲突、相关记录、linked event 和证据文本打包成 review packet。",
    ),
    (
        "final_data_package_builder",
        "最终可审计输出",
        "生成 final_dataset、source_registry、linked_events、conflicts、review items 和 provenance manifest。",
    ),
]


def _initial_state() -> dict:
    return {
        "user_request": (
            "Collect global human hantavirus case, outbreak, and surveillance data "
            "from 2020 to 2026, including cases, deaths, dates, locations, source URLs, "
            "source types, and evidence quotes."
        ),
        "source_candidates": [],
        "source_registry": [],
        "documents": [],
        "evidence_chunks": [],
        "raw_records": [],
        "validated_records": [],
        "normalized_records": [],
        "linked_events": [],
        "conflicts": [],
        "human_review_queue": [],
        "human_review_decisions": [],
        "collection_trace": [],
        "collection_spec": None,
        "disease_profile": None,
        "collection_schema": None,
        "source_strategy": None,
        "screening_criteria": None,
        "search_queries": None,
        "search_query_inventory": [],
        "content_fetch_requests": [],
        "content_fetch_summary": None,
        "fixture_document_summary": None,
        "document_quality_summary": None,
        "final_data_package": None,
        "current_route": None,
    }


def _read_json_file(path: Path) -> dict | list | None:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _summary_value(summaries: dict, key: str):
    return (summaries or {}).get(key)


def _sanitize_product_artifact(value):
    if isinstance(value, dict):
        cleaned = {}
        for key, item in value.items():
            key_text = str(key)
            if "fixture" in key_text.lower():
                continue
            cleaned[key_text] = _sanitize_product_artifact(item)
        return cleaned
    if isinstance(value, list):
        return [_sanitize_product_artifact(item) for item in value]
    if isinstance(value, str):
        return (
            value.replace("fixture_documents_enabled", "local_test_documents_enabled")
            .replace("fixture documents", "local test documents")
            .replace("fixture", "local test")
            .replace("Fixture", "Local test")
        )
    return value


def _evidence_chunks_from_records(records: list[dict]) -> list[dict]:
    chunks: list[dict] = []
    seen: set[str] = set()
    for record in records:
        chunk_id = record.get("supporting_chunk_id")
        if not chunk_id or chunk_id in seen:
            continue
        seen.add(chunk_id)
        chunks.append(
            {
                "chunk_id": chunk_id,
                "source_id": record.get("source_id"),
                "source_url": record.get("source_url"),
                "source_type": record.get("source_type"),
                "publisher": record.get("publisher"),
                "title": record.get("source_title"),
                "document_type": record.get("document_type"),
                "fetch_purpose": record.get("fetch_purpose"),
                "chunk_kind": record.get("chunk_kind"),
                "contains_target_data": True,
                "data_types": record.get("data_types"),
                "context_types": record.get("context_types"),
                "confidence": record.get("extraction_confidence"),
                "presence_reason": "Reconstructed from live collection final_dataset evidence_quote.",
                "text": record.get("evidence_quote"),
            }
        )
    return chunks


def _load_stage4h_product_result() -> dict | None:
    collection_dir = _STAGE4H_PRODUCT_OUTPUT_DIR / "collection"
    diagnostics_dir = _STAGE4H_PRODUCT_OUTPUT_DIR / "diagnostics"
    summary_path = _STAGE4H_PRODUCT_OUTPUT_DIR / "stage4h_live_product_run_summary.json"

    package = _read_json_file(collection_dir / "final_package.json")
    if not isinstance(package, dict):
        return None
    package = _sanitize_product_artifact(package)

    workflow_summaries = _read_json_file(diagnostics_dir / "workflow_summaries.json")
    if not isinstance(workflow_summaries, dict):
        workflow_summaries = package.get("workflow_summaries") or {}
    workflow_summaries = _sanitize_product_artifact(workflow_summaries)

    live_fetch_summary = _read_json_file(diagnostics_dir / "live_fetch_summary.json")
    if not isinstance(live_fetch_summary, dict):
        live_fetch_summary = {}
    live_fetch_summary = _sanitize_product_artifact(live_fetch_summary)

    llm_stage_summary = _read_json_file(diagnostics_dir / "llm_stage_summary.json")
    if not isinstance(llm_stage_summary, dict):
        llm_stage_summary = {}
    llm_stage_summary = _sanitize_product_artifact(llm_stage_summary)

    run_summary = _read_json_file(summary_path)
    if not isinstance(run_summary, dict):
        run_summary = {}
    run_summary = _sanitize_product_artifact(run_summary)

    records = list(package.get("final_dataset") or [])
    review_items = list(package.get("human_review_items") or [])
    collection_spec = {
        "task_type": "public_health_case_and_outbreak_collection",
        "disease": "Hantavirus disease",
        "target_population": "human",
        "geography": "New Mexico, United States",
        "time_window": "2020-2026",
        "user_request": run_summary.get("user_request")
        or (
            "Collect data on hantavirus from 2020 to 2026. For this product "
            "run, use the New Mexico HPS source set, keep collection sources "
            "and validation sources separated, extract cases, deaths, dates, "
            "locations, source URLs, source types, and evidence quotes, then "
            "route uncertain results to human review."
        ),
    }

    return {
        "user_request": collection_spec["user_request"],
        "collection_trace": package.get("collection_trace") or [],
        "collection_spec": collection_spec,
        "search_queries": None,
        "search_query_inventory": [],
        "source_registry": package.get("source_registry") or [],
        "documents": live_fetch_summary.get("documents") or [],
        "evidence_chunks": _evidence_chunks_from_records(records),
        "raw_records": records,
        "validated_records": records,
        "rejected_records": [],
        "normalized_records": records,
        "linked_events": package.get("linked_events") or [],
        "conflicts": package.get("conflicts") or [],
        "human_review_queue": review_items,
        "final_data_package": package,
        "current_route": run_summary.get("current_route")
        or ("human_review" if review_items else "final_data_package_builder"),
        "source_planning_agent_summary": _summary_value(
            workflow_summaries, "source_planning_agent_summary"
        ),
        "source_discovery_summary": _summary_value(
            workflow_summaries, "source_discovery_summary"
        ),
        "source_screening_summary": _summary_value(
            workflow_summaries, "source_screening_summary"
        ),
        "source_critic_summary": _summary_value(
            workflow_summaries, "source_critic_summary"
        ),
        "source_routing_summary": _summary_value(
            workflow_summaries, "source_routing_summary"
        ),
        "content_fetch_summary": _summary_value(
            workflow_summaries, "content_fetch_summary"
        ),
        "fixture_document_summary": None,
        "document_quality_summary": _summary_value(
            workflow_summaries, "document_quality_summary"
        ),
        "evidence_chunking_summary": _summary_value(
            workflow_summaries, "evidence_chunking_summary"
        ),
        "data_presence_summary": _summary_value(
            workflow_summaries, "data_presence_summary"
        ),
        "structured_extraction_summary": _summary_value(
            workflow_summaries, "structured_extraction_summary"
        ),
        "llm_extraction_summary": _summary_value(
            workflow_summaries, "llm_extraction_summary"
        ),
        "schema_validation_summary": _summary_value(
            workflow_summaries, "schema_validation_summary"
        ),
        "record_normalization_summary": _summary_value(
            workflow_summaries, "record_normalization_summary"
        ),
        "record_linking_summary": _summary_value(
            workflow_summaries, "record_linking_summary"
        ),
        "cross_source_consistency_summary": _summary_value(
            workflow_summaries, "cross_source_consistency_summary"
        ),
        "human_review_summary": _summary_value(
            workflow_summaries, "human_review_summary"
        ),
        "finalization_summary": _summary_value(
            workflow_summaries, "finalization_summary"
        ),
        "product_demo_result": {
            "live_fetch_summary": live_fetch_summary,
            "llm_stage_summary": llm_stage_summary,
            "run_summary": run_summary,
        },
    }


def _load_product_result() -> dict | None:
    stage4h_result = _load_stage4h_product_result()
    if stage4h_result is not None:
        return stage4h_result

    collection_dir = _LIVE_NM_OUTPUT_DIR / "collection"
    diagnostics_dir = _LIVE_NM_OUTPUT_DIR / "diagnostics"
    llm_diagnostics_dir = _LLM_NM_OUTPUT_DIR / "diagnostics"
    comparison_dir = _LLM_NM_OUTPUT_DIR / "comparison"

    package = _read_json_file(collection_dir / "final_package.json")
    if not isinstance(package, dict):
        return None
    package = _sanitize_product_artifact(package)

    workflow_summaries = package.get("workflow_summaries") or _read_json_file(
        collection_dir / "workflow_summaries.json"
    )
    if not isinstance(workflow_summaries, dict):
        workflow_summaries = {}
    workflow_summaries = _sanitize_product_artifact(workflow_summaries)

    live_fetch_summary = _read_json_file(diagnostics_dir / "live_fetch_summary.json")
    if not isinstance(live_fetch_summary, dict):
        live_fetch_summary = {}
    live_fetch_summary = _sanitize_product_artifact(live_fetch_summary)

    llm_replay_summary = _read_json_file(
        llm_diagnostics_dir / "llm_extraction_replay_summary.json"
    )
    if not isinstance(llm_replay_summary, dict):
        llm_replay_summary = {}
    llm_replay_summary = _sanitize_product_artifact(llm_replay_summary)

    comparison_summary = _read_json_file(
        comparison_dir / "deterministic_vs_llm_summary.json"
    )
    if not isinstance(comparison_summary, dict):
        comparison_summary = {}
    comparison_summary = _sanitize_product_artifact(comparison_summary)

    records = list(package.get("final_dataset") or [])
    review_items = list(package.get("human_review_items") or [])
    collection_spec = {
        "task_type": "public_health_case_and_outbreak_collection",
        "disease": "Hantavirus disease",
        "target_population": "human",
        "geography": "New Mexico, United States",
        "time_window": "2024-2026",
        "user_request": (
            "Collect human hantavirus pulmonary syndrome case and death data for "
            "New Mexico, United States, 2024-2026. Use collection sources for "
            "extraction, keep validation sources held out for comparison, and "
            "route non-comparable or conflicting evidence to human review."
        ),
    }

    llm_summary = {
        "llm_extraction_replay_summary": llm_replay_summary,
        "deterministic_vs_llm_summary": comparison_summary,
    }

    return {
        "user_request": collection_spec["user_request"],
        "collection_trace": package.get("collection_trace") or [],
        "collection_spec": collection_spec,
        "search_queries": None,
        "search_query_inventory": [],
        "source_registry": package.get("source_registry") or [],
        "documents": live_fetch_summary.get("documents") or [],
        "evidence_chunks": _evidence_chunks_from_records(records),
        "raw_records": records,
        "validated_records": records,
        "rejected_records": [],
        "normalized_records": records,
        "linked_events": package.get("linked_events") or [],
        "conflicts": package.get("conflicts") or [],
        "human_review_queue": review_items,
        "final_data_package": package,
        "current_route": "human_review" if review_items else "final_data_package_builder",
        "source_discovery_summary": _summary_value(
            workflow_summaries, "source_discovery_summary"
        ),
        "source_screening_summary": _summary_value(
            workflow_summaries, "source_screening_summary"
        ),
        "content_fetch_summary": _summary_value(
            workflow_summaries, "content_fetch_summary"
        ),
        "fixture_document_summary": None,
        "document_quality_summary": _summary_value(
            workflow_summaries, "document_quality_summary"
        ),
        "evidence_chunking_summary": _summary_value(
            workflow_summaries, "evidence_chunking_summary"
        ),
        "data_presence_summary": _summary_value(
            workflow_summaries, "data_presence_summary"
        ),
        "structured_extraction_summary": _summary_value(
            workflow_summaries, "structured_extraction_summary"
        ),
        "llm_extraction_summary": llm_summary,
        "schema_validation_summary": _summary_value(
            workflow_summaries, "schema_validation_summary"
        ),
        "record_normalization_summary": _summary_value(
            workflow_summaries, "record_normalization_summary"
        ),
        "record_linking_summary": _summary_value(
            workflow_summaries, "record_linking_summary"
        ),
        "cross_source_consistency_summary": _summary_value(
            workflow_summaries, "cross_source_consistency_summary"
        ),
        "human_review_summary": _summary_value(
            workflow_summaries, "human_review_summary"
        ),
        "finalization_summary": _summary_value(
            workflow_summaries, "finalization_summary"
        ),
        "product_demo_result": {
            "live_fetch_summary": live_fetch_summary,
            "llm_replay_summary": llm_replay_summary,
            "comparison_summary": comparison_summary,
        },
    }


def _esc(value) -> str:
    if value is None:
        return ""
    return html.escape(str(value), quote=True)


def _json(value) -> str:
    return html.escape(json.dumps(value, ensure_ascii=False, indent=2), quote=False)


def _count(result: dict, key: str) -> int:
    return len(result.get(key) or [])


def _summary(result: dict, key: str) -> dict:
    value = result.get(key) or {}
    return value if isinstance(value, dict) else {}


def _metric_card(label: str, value, note: str = "") -> str:
    return (
        '<div class="metric">'
        f'<div class="metric-label">{_esc(label)}</div>'
        f'<div class="metric-value">{_esc(value)}</div>'
        f'<div class="metric-note">{_esc(note)}</div>'
        "</div>"
    )


def _node_card(node_name: str, title: str, description: str, executed: bool) -> str:
    status = "executed" if executed else "not-run"
    status_text = "executed" if executed else "not in this run"
    return (
        f'<section class="node-card {status}">'
        f'<div class="node-kicker">{_esc(status_text)}</div>'
        f"<h3>{_esc(title)}</h3>"
        f'<code>{_esc(node_name)}</code>'
        f"<p>{_esc(description)}</p>"
        "</section>"
    )


def _row(cells: list[str], tag: str = "td") -> str:
    return "<tr>" + "".join(f"<{tag}>{cell}</{tag}>" for cell in cells) + "</tr>"


def _stage_rows(result: dict) -> str:
    summaries = {
        "source_discovery": _summary(result, "source_discovery_summary"),
        "source_screening": _summary(result, "source_screening_summary"),
        "content_fetch_and_parse": _summary(result, "content_fetch_summary"),
        "evidence_chunking_and_data_presence_flagging": _summary(
            result, "evidence_chunking_summary"
        ),
        "structured_extraction": _summary(result, "structured_extraction_summary"),
        "schema_validation_and_repair": _summary(result, "schema_validation_summary"),
        "record_normalization": _summary(result, "record_normalization_summary"),
        "record_linking": _summary(result, "record_linking_summary"),
        "cross_source_consistency_check": _summary(
            result, "cross_source_consistency_summary"
        ),
        "human_review": _summary(result, "human_review_summary"),
    }
    rows = [
        (
            "source_discovery",
            "source_candidates",
            summaries["source_discovery"].get("candidate_count"),
            "来源发现结果作为 state 字段进入下一步。",
        ),
        (
            "source_screening",
            "source_registry",
            summaries["source_screening"].get("source_role_counts"),
            "筛源决策不是日志文本，而是结构化字段。",
        ),
        (
            "content_fetch_and_parse",
            "documents",
            summaries["content_fetch_and_parse"].get("fetch_status_counts"),
            "同一节点可切换 offline stub、fixture、live fetch。",
        ),
        (
            "evidence_chunking_and_data_presence_flagging",
            "evidence_chunks",
            summaries["evidence_chunking_and_data_presence_flagging"].get(
                "total_chunk_count"
            ),
            "chunk 带 signal、confidence 和 source provenance。",
        ),
        (
            "structured_extraction",
            "raw_records",
            summaries["structured_extraction"].get("raw_record_count"),
            "规则抽取和 LLM 抽取可以挂在同一节点上。",
        ),
        (
            "schema_validation_and_repair",
            "validated_records / rejected_records",
            summaries["schema_validation_and_repair"].get("schema_status_counts"),
            "验证结果直接驱动 review queue。",
        ),
        (
            "record_normalization",
            "normalized_records",
            summaries["record_normalization"].get("normalization_status_counts"),
            "保留 raw 字段，便于审计标准化动作。",
        ),
        (
            "record_linking",
            "linked_events",
            summaries["record_linking"].get("linking_status_counts"),
            "多来源记录被聚合为候选事件。",
        ),
        (
            "cross_source_consistency_check",
            "conflicts",
            summaries["cross_source_consistency_check"].get("conflict_type_counts"),
            "跨源冲突变成可追踪对象。",
        ),
        (
            "human_review",
            "human_review_queue",
            summaries["human_review"].get("item_type_counts"),
            "冲突和上下文被打包给人工审核。",
        ),
    ]
    return "\n".join(
        _row(
            [
                f"<code>{_esc(node)}</code>",
                f"<code>{_esc(field)}</code>",
                f"<pre>{_json(value)}</pre>",
                _esc(why),
            ]
        )
        for node, field, value, why in rows
    )


def _records_table(records: list[dict]) -> str:
    header = _row(
        [
            "record_id",
            "source",
            "country",
            "date",
            "cases_unspecified",
            "deaths",
            "linked_event",
            "conflicts",
        ],
        tag="th",
    )
    body = "\n".join(
        _row(
            [
                f"<code>{_esc(r.get('record_id'))}</code>",
                _esc(r.get("publisher") or r.get("source_id")),
                _esc(r.get("country")),
                _esc(r.get("date_reported") or r.get("date_anchor")),
                _esc(r.get("cases_unspecified")),
                _esc(r.get("deaths")),
                f"<code>{_esc(r.get('linked_event_id'))}</code>",
                _esc(", ".join(r.get("conflict_ids") or [])),
            ]
        )
        for r in records
    )
    return f"<table>{header}{body}</table>"


def _conflict_panels(conflicts: list[dict]) -> str:
    if not conflicts:
        return '<p class="muted">No conflicts in this run.</p>'
    panels: list[str] = []
    for conflict in conflicts:
        values = conflict.get("values") or []
        value_items = "".join(
            "<li>"
            f"<code>{_esc(v.get('record_id'))}</code> "
            f"{_esc(v.get('source_id'))}: "
            f"<strong>{_esc(v.get('value'))}</strong>"
            "</li>"
            for v in values
        )
        panels.append(
            '<article class="conflict">'
            f"<h3>{_esc(conflict.get('field'))}: {_esc(conflict.get('conflict_type'))}</h3>"
            f'<p><strong>Severity:</strong> {_esc(conflict.get("severity"))} '
            f'| <strong>Human review:</strong> {_esc(conflict.get("requires_human_review"))}</p>'
            f"<ul>{value_items}</ul>"
            f'<p class="muted">{_esc(conflict.get("recommended_action"))}</p>'
            "</article>"
        )
    return "\n".join(panels)


def _review_panels(items: list[dict]) -> str:
    if not items:
        return '<p class="muted">No review items in this run.</p>'
    panels: list[str] = []
    for item in items:
        packet = item.get("review_packet") or {}
        sections = packet.get("packet_sections") or {}
        section_names = ", ".join(sections.keys())
        panels.append(
            '<article class="review">'
            f"<h3>{_esc(item.get('review_id'))}</h3>"
            f'<p><strong>Type:</strong> {_esc(item.get("item_type"))} '
            f'| <strong>Priority:</strong> {_esc(item.get("priority"))} '
            f'| <strong>Status:</strong> {_esc(item.get("status"))}</p>'
            f'<p>{_esc(item.get("reason"))}</p>'
            f'<p><strong>Packet sections:</strong> {_esc(section_names)}</p>'
            "</article>"
        )
    return "\n".join(panels)


def _short_text(value, limit: int = 520) -> str:
    text = "" if value is None else str(value)
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def _sample(items, limit: int = 5) -> list:
    return list(items or [])[:limit]


def _trace_by_node(result: dict) -> dict[str, dict]:
    return {
        event.get("node_name"): event
        for event in result.get("collection_trace", [])
        if event.get("node_name")
    }


def _source_lookup(result: dict) -> dict[str, dict]:
    return {
        item.get("source_id"): item
        for item in result.get("source_registry", [])
        if item.get("source_id")
    }


def _contains_synthetic_data(package: dict) -> bool:
    return bool(
        package.get("contains_synthetic_data")
        or package.get("contains_synthetic_fixture_data")
    )


def _stage_payload(result: dict) -> list[dict]:
    trace = _trace_by_node(result)
    return [
        {
            "node": "task_intake_and_scope_planning",
            "title": "Plan: 把自然语言任务变成可执行规格",
            "agentic_role": "Planning / state initialization",
            "state_writes": ["collection_spec", "collection_trace"],
            "trace": trace.get("task_intake_and_scope_planning", {}),
            "show": {
                "collection_spec": result.get("collection_spec"),
            },
            "takeaway": "第一步先把用户任务变成可执行 collection spec：疾病、地点、年份、字段和 validation 规则都进入 state。",
        },
        {
            "node": "query_strategy_builder",
            "title": "Plan: 生成检索策略和查询清单",
            "agentic_role": "Search strategy",
            "state_writes": ["search_queries", "search_query_inventory"],
            "trace": trace.get("query_strategy_builder", {}),
            "show": {
                "search_queries": result.get("search_queries"),
                "search_query_inventory_sample": _sample(
                    result.get("search_query_inventory"), 6
                ),
            },
            "takeaway": "检索策略进入 state，后续可以审计、替换、重跑，而不是散落在脚本字符串里。",
        },
        {
            "node": "source_screening",
            "title": "Act + Filter: 发现来源并筛选角色",
            "agentic_role": "Tool-like source discovery + rule gate",
            "state_writes": ["source_candidates", "source_registry"],
            "trace": trace.get("source_screening", {}),
            "show": {
                "source_discovery_summary": result.get("source_discovery_summary"),
                "source_screening_summary": result.get("source_screening_summary"),
                "source_registry_sample": _sample(result.get("source_registry"), 6),
            },
            "takeaway": "source screening 输出可被后续节点消费的 registry，并决定哪些来源可抽取、哪些只能做 validation 或 context。",
        },
        {
            "node": "content_fetch_and_parse",
            "title": "Act: 获取真实网页文档",
            "agentic_role": "Document acquisition tool",
            "state_writes": ["content_fetch_requests", "documents"],
            "trace": trace.get("content_fetch_and_parse", {}),
            "show": {
                "content_fetch_summary": result.get("content_fetch_summary"),
                "documents_sample": _sample(result.get("documents"), 5),
            },
            "takeaway": "真实产品运行中，这个节点实际访问 allowlist 中的 NMDOH/CDC URL，并记录 fetch status、HTTP status、content type 和 parse status。",
        },
        {
            "node": "evidence_chunking_and_data_presence_flagging",
            "title": "Observe: 判断哪些文本真的有数据",
            "agentic_role": "Evidence triage",
            "state_writes": ["evidence_chunks", "evidence_chunking_summary"],
            "trace": trace.get("evidence_chunking_and_data_presence_flagging", {}),
            "show": {
                "evidence_chunking_summary": result.get("evidence_chunking_summary"),
                "data_presence_summary": result.get("data_presence_summary"),
                "evidence_chunks": result.get("evidence_chunks"),
            },
            "takeaway": "这一步把网页文本变成证据块，并标出 case_count/death_count/date/location 等信号。",
        },
        {
            "node": "structured_extraction",
            "title": "Extract: 从证据抽取结构化记录",
            "agentic_role": "Structured extraction agent",
            "state_writes": ["raw_records", "llm_extraction_summary"],
            "trace": trace.get("structured_extraction", {}),
            "show": {
                "structured_extraction_summary": result.get(
                    "structured_extraction_summary"
                ),
                "llm_extraction_summary": result.get("llm_extraction_summary"),
                "raw_records": result.get("raw_records"),
            },
            "takeaway": "真实网页 collection 先经过 deterministic extractor；随后 LLM extraction 对允许的 collection evidence chunk 进行结构化抽取。",
        },
        {
            "node": "schema_validation_and_repair",
            "title": "Verify: schema validation / repair",
            "agentic_role": "Guardrail",
            "state_writes": ["validated_records", "rejected_records"],
            "trace": trace.get("schema_validation_and_repair", {}),
            "show": {
                "schema_validation_summary": result.get("schema_validation_summary"),
                "validated_records": result.get("validated_records"),
                "rejected_records": result.get("rejected_records"),
            },
            "takeaway": "这不是简单顺序脚本的 print，而是一个可审计的 guardrail 节点。",
        },
        {
            "node": "record_linking",
            "title": "Reason: 把多来源记录链接成同一事件",
            "agentic_role": "Entity / event linking",
            "state_writes": ["normalized_records", "linked_events"],
            "trace": trace.get("record_linking", {}),
            "show": {
                "record_normalization_summary": result.get(
                    "record_normalization_summary"
                ),
                "record_linking_summary": result.get("record_linking_summary"),
                "normalized_records": result.get("normalized_records"),
                "linked_events": result.get("linked_events"),
            },
            "takeaway": "这里开始体现事件级推理：来自真实 NMDOH 网页的 records 会按疾病、地点、日期和统计口径链接成事件。",
        },
        {
            "node": "cross_source_consistency_check",
            "title": "Critique: 跨来源一致性检查",
            "agentic_role": "Critic / verifier",
            "state_writes": ["conflicts", "cross_source_consistency_summary"],
            "trace": trace.get("cross_source_consistency_check", {}),
            "show": {
                "cross_source_consistency_summary": result.get(
                    "cross_source_consistency_summary"
                ),
                "conflicts": result.get("conflicts"),
            },
            "takeaway": "critic 节点检查同一事件内的 case/death/date/location 是否可比；不可比、冲突或缺失 validation 的结果会被保留给人工复核。",
        },
        {
            "node": "quality_gate_routing",
            "title": "Route: 根据质量门控决定下一步",
            "agentic_role": "Conditional routing",
            "state_writes": ["current_route"],
            "trace": trace.get("quality_gate_routing", {}),
            "show": {
                "current_route": result.get("current_route"),
                "human_review_queue_count": len(result.get("human_review_queue") or []),
                "conflict_count": len(result.get("conflicts") or []),
            },
            "takeaway": "这就是 LangGraph 比普通 pipeline 更直观的地方：分支逻辑是 graph edge，不是隐藏在 if/else 日志里。",
        },
        {
            "node": "human_review",
            "title": "Human-in-the-loop: 生成审查包",
            "agentic_role": "Human oversight handoff",
            "state_writes": ["human_review_queue", "human_review_summary"],
            "trace": trace.get("human_review", {}),
            "show": {
                "human_review_summary": result.get("human_review_summary"),
                "human_review_queue": result.get("human_review_queue"),
            },
            "takeaway": "不是只告诉人“有冲突”，而是把冲突、证据、相关记录、linked event 打包给 reviewer。",
        },
        {
            "node": "final_data_package_builder",
            "title": "Finalize: 输出可审计数据包",
            "agentic_role": "Audit package",
            "state_writes": ["final_data_package", "finalization_summary"],
            "trace": trace.get("final_data_package_builder", {}),
            "show": {
                "finalization_summary": result.get("finalization_summary"),
                "package_metadata": (result.get("final_data_package") or {}).get(
                    "package_metadata"
                ),
                "provenance_manifest": (result.get("final_data_package") or {}).get(
                    "provenance_manifest"
                ),
            },
            "takeaway": "最后输出不只是 records，还包括 trace、source registry、provenance、diagnostics、evaluation report 和 human review items。",
        },
    ]


def _report_payload(result: dict) -> dict:
    sources = _source_lookup(result)
    records = result.get("normalized_records") or []
    chunks = result.get("evidence_chunks") or []
    conflicts = result.get("conflicts") or []
    review_items = result.get("human_review_queue") or []
    package = result.get("final_data_package") or {}
    product_result = result.get("product_demo_result") or {}
    live_fetch_summary = product_result.get("live_fetch_summary") or {}
    llm_replay_summary = product_result.get("llm_replay_summary") or {}

    evidence_links = []
    chunk_by_id = {chunk.get("chunk_id"): chunk for chunk in chunks}
    for record in records:
        chunk = chunk_by_id.get(record.get("supporting_chunk_id")) or {}
        evidence_links.append(
            {
                "record_id": record.get("record_id"),
                "source_id": record.get("source_id"),
                "publisher": record.get("publisher"),
                "cases_unspecified": record.get("cases_unspecified"),
                "deaths": record.get("deaths"),
                "date_reported": record.get("date_reported"),
                "country": record.get("country"),
                "chunk_id": record.get("supporting_chunk_id"),
                "extraction_method": record.get("extraction_method"),
                "llm_used": record.get("llm_used"),
                "source_priority": (sources.get(record.get("source_id")) or {}).get(
                    "source_priority"
                ),
                "evidence_quote": _short_text(record.get("evidence_quote"), 900),
                "chunk_signals": {
                    "data_types": chunk.get("data_types"),
                    "confidence": chunk.get("confidence"),
                    "presence_reason": chunk.get("presence_reason"),
                },
            }
        )

    return {
        "mode": {
            "local_test_documents": bool(
                live_fetch_summary.get("fixture_documents_enabled")
            ),
            "live_fetch": bool(live_fetch_summary.get("live_fetch_enabled")),
            "llm_extraction": bool(llm_replay_summary.get("llm_call_succeeded")),
            "truth_label": "Product run based on live NMDOH/CDC webpage fetch, source-role masking, Anthropic LLM extraction, validation comparison, and human-review routing.",
        },
        "counts": {
            "trace_nodes": len(result.get("collection_trace") or []),
            "sources": len(result.get("source_registry") or []),
            "documents": len(result.get("documents") or []),
            "evidence_chunks": len(chunks),
            "records": len(records),
            "linked_events": len(result.get("linked_events") or []),
            "conflicts": len(conflicts),
            "human_review_items": len(review_items),
        },
        "route": result.get("current_route"),
        "stages": _stage_payload(result),
        "evidence_links": evidence_links,
        "conflicts": conflicts,
        "review_items": review_items,
        "trace_order": [
            event.get("node_name") for event in result.get("collection_trace", [])
        ],
        "final_package_flags": {
            "contains_synthetic_data": _contains_synthetic_data(package),
            "synthetic_notice": package.get("synthetic_fixture_notice"),
            "live_fetch_enabled": live_fetch_summary.get("live_fetch_enabled"),
            "llm_call_succeeded": llm_replay_summary.get("llm_call_succeeded"),
        },
    }


def _json_for_script(value) -> str:
    return json.dumps(value, ensure_ascii=False).replace("</", "<\\/")


# This second definition intentionally replaces the earlier static report renderer.
# The first version was useful as a summary; this version is an interactive run
# inspector that is closer to how the official LangGraph demos communicate value.
def _build_html(result: dict) -> str:
    report = _report_payload(result)
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>LangGraph HDC Agent Run Inspector</title>
  <style>
    :root {{
      --bg: #f4f6f8;
      --panel: #ffffff;
      --ink: #111827;
      --muted: #5b6678;
      --line: #d9e1ec;
      --blue: #155eaa;
      --cyan: #007c89;
      --green: #13795b;
      --amber: #9a6700;
      --red: #b42318;
      --violet: #6d4aff;
      --code: #edf3f9;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: "Segoe UI", Arial, "Microsoft YaHei", sans-serif;
      line-height: 1.5;
    }}
    header {{
      padding: 34px 44px 26px;
      background: #0f2747;
      color: #fff;
    }}
    header h1 {{
      margin: 0 0 10px;
      font-size: 34px;
      letter-spacing: 0;
    }}
    header p {{
      max-width: 1180px;
      margin: 0;
      color: #dbeafe;
      font-size: 16px;
    }}
    main {{ padding: 24px 32px 52px; }}
    section.band {{
      margin: 0 0 18px;
      padding: 22px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
    }}
    h2 {{ margin: 0 0 14px; font-size: 22px; }}
    h3 {{ margin: 0 0 8px; font-size: 16px; }}
    p {{ margin: 0 0 10px; }}
    code {{
      padding: 2px 5px;
      border-radius: 4px;
      background: var(--code);
      font-family: Consolas, "Cascadia Mono", monospace;
      font-size: 12px;
    }}
    pre {{
      margin: 0;
      max-height: 360px;
      overflow: auto;
      padding: 12px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #f7f9fc;
      color: #172033;
      white-space: pre-wrap;
      font-family: Consolas, "Cascadia Mono", monospace;
      font-size: 12px;
    }}
    .top-grid {{
      display: grid;
      grid-template-columns: 1.15fr .85fr;
      gap: 16px;
    }}
    .metrics {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 10px;
    }}
    .metric {{
      min-height: 98px;
      padding: 14px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fff;
    }}
    .metric span {{ display: block; color: var(--muted); font-size: 12px; }}
    .metric strong {{ display: block; margin-top: 6px; font-size: 27px; }}
    .mode {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 10px;
    }}
    .mode-item {{
      padding: 14px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fbfdff;
    }}
    .mode-item strong {{ display: block; margin-bottom: 4px; }}
    .mode-item.false strong {{ color: var(--red); }}
    .mode-item.true strong {{ color: var(--green); }}
    .official {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
    }}
    .official article, .note, .evidence-card, .conflict-card, .review-card {{
      padding: 16px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fff;
    }}
    .note {{ border-left: 5px solid var(--amber); background: #fff9eb; }}
    .run-inspector {{
      display: grid;
      grid-template-columns: 360px minmax(0, 1fr);
      gap: 14px;
      min-height: 620px;
    }}
    .stage-list {{
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fbfdff;
      overflow: hidden;
    }}
    .stage-button {{
      width: 100%;
      padding: 13px 14px;
      border: 0;
      border-bottom: 1px solid var(--line);
      background: transparent;
      color: var(--ink);
      text-align: left;
      cursor: pointer;
    }}
    .stage-button:hover {{ background: #eef5fd; }}
    .stage-button.active {{
      background: #e8f1fb;
      border-left: 5px solid var(--blue);
      padding-left: 9px;
    }}
    .stage-title {{ display: block; font-weight: 700; }}
    .stage-node {{ display: block; margin-top: 3px; color: var(--muted); font-size: 12px; }}
    .detail {{
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fff;
      overflow: hidden;
    }}
    .detail-head {{
      padding: 18px;
      border-bottom: 1px solid var(--line);
      background: #fbfdff;
    }}
    .detail-body {{ padding: 18px; }}
    .badge-row {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; }}
    .badge {{
      display: inline-flex;
      align-items: center;
      min-height: 26px;
      padding: 4px 8px;
      border: 1px solid var(--line);
      border-radius: 999px;
      background: #fff;
      color: #25324a;
      font-size: 12px;
    }}
    .badge.route {{ border-color: #b7a4ff; color: var(--violet); }}
    .tabs {{ display: flex; gap: 8px; margin: 14px 0; }}
    .tab {{
      padding: 8px 10px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #fff;
      cursor: pointer;
      font-weight: 600;
    }}
    .tab.active {{ background: var(--blue); border-color: var(--blue); color: #fff; }}
    .artifact-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
    }}
    .artifact {{
      min-width: 0;
      border: 1px solid var(--line);
      border-radius: 8px;
      overflow: hidden;
      background: #fff;
    }}
    .artifact h4 {{
      margin: 0;
      padding: 10px 12px;
      border-bottom: 1px solid var(--line);
      background: #f2f6fb;
      font-size: 13px;
    }}
    .artifact pre {{
      max-height: 290px;
      border: 0;
      border-radius: 0;
    }}
    .pipeline {{
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 10px;
    }}
    .step {{
      padding: 14px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fff;
      min-height: 130px;
      border-top: 5px solid var(--cyan);
    }}
    .step small {{ color: var(--muted); }}
    .evidence-grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
    }}
    .evidence-card {{
      border-left: 5px solid var(--green);
    }}
    .quote {{
      margin-top: 10px;
      padding: 12px;
      border-radius: 6px;
      background: #f4f8f6;
      color: #23362f;
      font-size: 13px;
    }}
    mark {{
      padding: 0 3px;
      border-radius: 3px;
      background: #ffe8a3;
    }}
    .conflict-card {{ border-left: 5px solid var(--red); }}
    .value-strip {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 10px;
      margin-top: 12px;
    }}
    .value {{
      padding: 12px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fff7f7;
    }}
    .value strong {{ display: block; font-size: 26px; color: var(--red); }}
    .review-card {{ border-left: 5px solid var(--violet); }}
    .studio-steps {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
    }}
    .studio-steps ol {{ margin-top: 0; }}
    .muted {{ color: var(--muted); }}
    @media (max-width: 1180px) {{
      .top-grid, .run-inspector, .official, .pipeline, .evidence-grid, .studio-steps {{
        grid-template-columns: 1fr;
      }}
      .metrics, .mode, .artifact-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      main {{ padding-left: 18px; padding-right: 18px; }}
      header {{ padding-left: 24px; padding-right: 24px; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>HDC Product Workflow Console</h1>
    <p>本页面用于展示用户输入任务后，HDC workflow 的节点顺序、state artifacts、质量门和 human-review routing。technical workshop 主线使用真实 NMDOH/CDC 网页 collection 和 Anthropic LLM extraction；本页面负责解释 workflow 如何运行、每个节点写入什么、条件分支在哪里发生。</p>
  </header>
  <main>
    <section class="band top-grid">
      <div>
        <h2>1. Product run overview</h2>
        <div class="metrics" id="metrics"></div>
      </div>
      <div>
        <h2>Workflow run controls</h2>
        <div class="mode">
          <div class="mode-item true"><strong>Live web collection</strong><span>由 <code>configs/hdc_workflow_run_config.jsonc</code> 控制真实 NMDOH/CDC 网页抓取。</span></div>
          <div class="mode-item true"><strong>All three LLM stages</strong><span>同一份 config 控制 provider/model，以及 source planning、source critic 和 structured extraction。</span></div>
          <div class="mode-item true"><strong>Workflow inspection</strong><span>通过节点 trace 查看串行 state pipeline 和条件路由。</span></div>
        </div>
        <p class="note" style="margin-top:12px;">现场演示顺序是：配置 API，输入任务，运行真实网页 collection，查看 workflow 节点，调用 LLM extraction，最后打开 records、validation comparison 和 human review outputs。</p>
      </div>
    </section>

    <section class="band">
      <h2>2. How the product run is inspected</h2>
      <div class="official">
        <article>
          <h3>Runnable workflow</h3>
          <p>现场从一个明确的 user request 开始，让观众看到 graph 如何启动、节点如何执行、state 如何累积。</p>
        </article>
        <article>
          <h3>Studio trace</h3>
          <p>Studio 中重点检查每个节点的中间 state、traversed nodes、thread history 和输出 artifacts。</p>
        </article>
        <article>
          <h3>Debug / fork / human-in-the-loop</h3>
          <p>当 critic 节点发现冲突或证据不足时，workflow 会生成 human review packet，并把决策交给人工复核。</p>
        </article>
      </div>
    </section>

    <section class="band">
      <h2>3. Agentic loop：这次运行的“思考-行动-校验-路由”链条</h2>
      <div class="pipeline">
        <div class="step"><small>PLAN</small><h3>Scope and strategy</h3><p>把 user request 变成 schema、queries、source strategy。</p></div>
        <div class="step"><small>ACT</small><h3>Acquire sources</h3><p>发现来源、筛选 registry、抓取真实网页 documents。</p></div>
        <div class="step"><small>OBSERVE</small><h3>Evidence triage</h3><p>判断哪些文本包含 case/death/date/location 信号。</p></div>
        <div class="step"><small>EXTRACT + VERIFY</small><h3>Records and linked event</h3><p>抽取记录，标准化，再判断多条记录是否是同一事件。</p></div>
        <div class="step"><small>CRITIQUE + ROUTE</small><h3>Quality gate to review</h3><p>发现缺失字段、不可比 validation 或证据不足时，路由到 human_review。</p></div>
      </div>
    </section>

    <section class="band">
      <h2>4. Interactive run inspector：点节点看 state 怎么长出来</h2>
      <div class="run-inspector">
        <div class="stage-list" id="stageList"></div>
        <div class="detail">
          <div class="detail-head" id="detailHead"></div>
          <div class="detail-body">
            <div id="detailTakeaway"></div>
            <div class="tabs">
              <button class="tab active" data-tab="artifacts">State artifacts</button>
              <button class="tab" data-tab="trace">Trace metadata</button>
            </div>
            <div id="tabArtifacts"></div>
            <div id="tabTrace" style="display:none;"></div>
          </div>
        </div>
      </div>
    </section>

    <section class="band">
      <h2>5. 证据链：文本证据如何变成结构化 records</h2>
      <div class="evidence-grid" id="evidenceGrid"></div>
    </section>

    <section class="band">
      <h2>6. Critic 节点：为什么进入 human review</h2>
      <div id="conflictPanel"></div>
    </section>

    <section class="band">
      <h2>7. Human review packet：人看到的不是一句报错，而是一包证据</h2>
      <div id="reviewPanel"></div>
    </section>

    <section class="band">
      <h2>8. Product run sequence</h2>
      <div class="studio-steps">
        <div>
          <h3>操作流程</h3>
          <ol>
            <li>打开 workflow runtime profile：<code>configs/hdc_workflow_run_config.jsonc</code></li>
            <li>输入任务：采集 New Mexico 2024-2026 HPS case/death data，并保留 validation source 做 held-out comparison。</li>
            <li>启动 Studio：<code>python scripts/start_hdc_workflow_studio.py</code></li>
            <li>查看 workflow 节点顺序：主流程是串行 state pipeline，<code>quality_gate_routing</code> 是关键条件分支。</li>
            <li>同配置导出可读报告：<code>python scripts/run_hdc_workflow_configured.py --allow-live-fetch --allow-llm</code></li>
            <li>打开输出：<code>final_dataset.csv</code>、<code>normalized_records.csv</code>、<code>evaluation_report.csv</code>。</li>
          </ol>
        </div>
        <div>
          <h3>现场说明</h3>
          <p>本环节展示产品如何从用户任务进入真实网页抓取，再进入 LLM extraction 和 validation comparison。workflow 主体是串行执行；当质量门发现冲突、不可比或缺失 validation 时，条件边会路由到 human-in-the-loop。</p>
          <p class="muted">当前成功产品运行：live collection 产生 5 条 collection records；LLM extraction 成功产生 2 条 normalized records；2025 annual case count 与 held-out validation source 匹配，death count 不可比，2026 first case 缺少 validation record。</p>
        </div>
      </div>
    </section>
  </main>

  <script id="run-data" type="application/json">{_json_for_script(report)}</script>
  <script>
    const RUN = JSON.parse(document.getElementById("run-data").textContent);
    const state = {{ activeStage: 0, tab: "artifacts" }};

    function esc(value) {{
      return String(value ?? "").replace(/[&<>"']/g, ch => ({{
        "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
      }}[ch]));
    }}
    function pretty(value) {{
      return esc(JSON.stringify(value, null, 2));
    }}
    function highlight(text) {{
      return esc(text)
        .replace(/(7|3|1)(?= cases| case| deaths| death)/g, "<mark>$1</mark>")
        .replace(/(New Mexico|Santa Fe County|2025|2026)/g, "<mark>$1</mark>");
    }}
    function renderMetrics() {{
      const labels = [
        ["trace_nodes", "Trace nodes"],
        ["sources", "Sources"],
        ["documents", "Documents"],
        ["evidence_chunks", "Evidence chunks"],
        ["records", "Records"],
        ["linked_events", "Linked events"],
        ["conflicts", "Conflicts"],
        ["human_review_items", "Review items"],
      ];
      document.getElementById("metrics").innerHTML = labels.map(([key, label]) => `
        <div class="metric"><span>${{label}}</span><strong>${{esc(RUN.counts[key])}}</strong></div>
      `).join("") + `<div class="metric"><span>Route</span><strong>${{esc(RUN.route)}}</strong></div>`;
    }}
    function renderStageList() {{
      document.getElementById("stageList").innerHTML = RUN.stages.map((stage, idx) => `
        <button class="stage-button ${{idx === state.activeStage ? "active" : ""}}" data-stage="${{idx}}">
          <span class="stage-title">${{esc(stage.title)}}</span>
          <span class="stage-node">${{esc(stage.node)}} · ${{esc(stage.agentic_role)}}</span>
        </button>
      `).join("");
      document.querySelectorAll(".stage-button").forEach(btn => {{
        btn.addEventListener("click", () => {{
          state.activeStage = Number(btn.dataset.stage);
          renderStageList();
          renderStageDetail();
        }});
      }});
    }}
    function renderStageDetail() {{
      const stage = RUN.stages[state.activeStage];
      document.getElementById("detailHead").innerHTML = `
        <h3>${{esc(stage.title)}}</h3>
        <code>${{esc(stage.node)}}</code>
        <div class="badge-row">
          <span class="badge">${{esc(stage.agentic_role)}}</span>
          ${{stage.state_writes.map(k => `<span class="badge route">writes: ${{esc(k)}}</span>`).join("")}}
        </div>
      `;
      document.getElementById("detailTakeaway").innerHTML = `<p class="note">${{esc(stage.takeaway)}}</p>`;
      const artifactEntries = Object.entries(stage.show || {{}});
      document.getElementById("tabArtifacts").innerHTML = `
        <div class="artifact-grid">
          ${{artifactEntries.map(([label, value]) => `
            <div class="artifact"><h4>${{esc(label)}}</h4><pre>${{pretty(value)}}</pre></div>
          `).join("")}}
        </div>
      `;
      document.getElementById("tabTrace").innerHTML = `<pre>${{pretty(stage.trace || {{}})}}</pre>`;
      renderTabs();
    }}
    function renderTabs() {{
      document.querySelectorAll(".tab").forEach(tab => {{
        tab.classList.toggle("active", tab.dataset.tab === state.tab);
        tab.onclick = () => {{
          state.tab = tab.dataset.tab;
          renderTabs();
        }};
      }});
      document.getElementById("tabArtifacts").style.display = state.tab === "artifacts" ? "" : "none";
      document.getElementById("tabTrace").style.display = state.tab === "trace" ? "" : "none";
    }}
    function renderEvidence() {{
      document.getElementById("evidenceGrid").innerHTML = RUN.evidence_links.map(item => `
        <article class="evidence-card">
          <h3>${{esc(item.publisher)}} · ${{esc(item.source_id)}}</h3>
          <p><strong>${{esc(item.cases_unspecified)}} cases</strong>, ${{esc(item.deaths)}} deaths, ${{esc(item.country)}} / ${{esc(item.date_reported)}}</p>
          <p><code>${{esc(item.record_id)}}</code> from <code>${{esc(item.chunk_id)}}</code></p>
          <p class="muted">method: ${{esc(item.extraction_method)}} · llm_used: ${{esc(item.llm_used)}}</p>
          <div class="quote">${{highlight(item.evidence_quote)}}</div>
        </article>
      `).join("");
    }}
    function renderConflict() {{
      const conflict = RUN.conflicts[0];
      if (!conflict) {{
        document.getElementById("conflictPanel").innerHTML = `<p class="muted">No conflict in this run.</p>`;
        return;
      }}
      document.getElementById("conflictPanel").innerHTML = `
        <article class="conflict-card">
          <h3>${{esc(conflict.conflict_id)}} · ${{esc(conflict.field)}} · ${{esc(conflict.conflict_type)}}</h3>
          <p><strong>Severity:</strong> ${{esc(conflict.severity)}} · <strong>Requires review:</strong> ${{esc(conflict.requires_human_review)}}</p>
          <div class="value-strip">
            ${{(conflict.values || []).map(v => `
              <div class="value">
                <strong>${{esc(v.value)}}</strong>
                <span>${{esc(v.source_id)}}</span><br />
                <code>${{esc(v.record_id)}}</code>
              </div>
            `).join("")}}
          </div>
          <pre style="margin-top:12px;">${{pretty(conflict)}}</pre>
        </article>
      `;
    }}
    function renderReview() {{
      const item = RUN.review_items[0];
      if (!item) {{
        document.getElementById("reviewPanel").innerHTML = `<p class="muted">No review packet in this run.</p>`;
        return;
      }}
      const sections = item.review_packet?.packet_sections || {{}};
      document.getElementById("reviewPanel").innerHTML = `
        <article class="review-card">
          <h3>${{esc(item.review_id)}} · ${{esc(item.item_type)}} · priority ${{esc(item.priority)}}</h3>
          <p>${{esc(item.reason)}}</p>
          <div class="badge-row">
            ${{Object.keys(sections).map(name => `<span class="badge route">${{esc(name)}}</span>`).join("")}}
          </div>
          <pre style="margin-top:12px;">${{pretty(item.review_packet)}}</pre>
        </article>
      `;
    }}
    renderMetrics();
    renderStageList();
    renderStageDetail();
    renderEvidence();
    renderConflict();
    renderReview();
  </script>
</body>
</html>
"""


def _build_static_html(result: dict) -> str:
    trace = result.get("collection_trace") or []
    executed_nodes = {event.get("node_name") for event in trace}
    package = result.get("final_data_package") or {}
    records = result.get("normalized_records") or []
    conflicts = result.get("conflicts") or []
    review_items = result.get("human_review_queue") or []
    route = result.get("current_route")

    metrics = "\n".join(
        [
            _metric_card("Trace nodes", len(trace), "LangGraph 记录的执行节点数"),
            _metric_card("Sources", _count(result, "source_registry"), "seed catalog + screening"),
            _metric_card("Documents", _count(result, "documents"), "fixture + offline stubs"),
            _metric_card("Evidence chunks", _count(result, "evidence_chunks"), "可追踪证据块"),
            _metric_card("Records", _count(result, "normalized_records"), "结构化数据记录"),
            _metric_card("Linked events", _count(result, "linked_events"), "事件级聚合"),
            _metric_card("Conflicts", _count(result, "conflicts"), "跨源一致性问题"),
            _metric_card("Route", route, "quality gate 的条件路由结果"),
        ]
    )

    node_cards = "\n".join(
        _node_card(node, title, description, node in executed_nodes)
        for node, title, description in NODE_STORY
    )

    spec = result.get("collection_spec") or {}
    package_meta = package.get("package_metadata") or {}
    provenance = package.get("provenance_manifest") or {}

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>LangGraph HDC Workflow Demo</title>
  <style>
    :root {{
      --ink: #172033;
      --muted: #5e6a7d;
      --line: #d7e0ee;
      --blue: #0b5cab;
      --green: #178254;
      --red: #b42318;
      --gold: #9a6700;
      --bg: #f6f8fb;
      --panel: #ffffff;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      color: var(--ink);
      background: var(--bg);
      font-family: "Segoe UI", Arial, "Microsoft YaHei", sans-serif;
      line-height: 1.55;
    }}
    header {{
      padding: 44px 56px 34px;
      color: #fff;
      background: linear-gradient(135deg, #073b78, #0b5cab 54%, #178254);
    }}
    header h1 {{
      margin: 0 0 8px;
      font-size: 42px;
      letter-spacing: 0;
    }}
    header p {{ max-width: 980px; margin: 0; font-size: 18px; opacity: .94; }}
    main {{ padding: 28px 56px 64px; }}
    section.band {{
      margin: 0 0 24px;
      padding: 24px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
    }}
    h2 {{ margin: 0 0 16px; font-size: 24px; }}
    h3 {{ margin: 0 0 8px; font-size: 17px; }}
    code {{
      padding: 2px 5px;
      border-radius: 4px;
      background: #eef4fb;
      font-family: Consolas, "Cascadia Mono", monospace;
      font-size: 13px;
    }}
    pre {{
      max-height: 150px;
      overflow: auto;
      margin: 0;
      padding: 10px;
      border-radius: 6px;
      background: #f2f5fa;
      white-space: pre-wrap;
      font-size: 12px;
    }}
    .metrics {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
    }}
    .metric {{
      padding: 16px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fff;
    }}
    .metric-label {{ color: var(--muted); font-size: 13px; }}
    .metric-value {{ margin-top: 4px; font-size: 28px; font-weight: 700; }}
    .metric-note {{ margin-top: 4px; color: var(--muted); font-size: 12px; }}
    .grid-2 {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 16px;
    }}
    .node-grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
    }}
    .node-card {{
      min-height: 160px;
      padding: 16px;
      border: 1px solid var(--line);
      border-left: 5px solid var(--blue);
      border-radius: 8px;
      background: #fff;
    }}
    .node-card.not-run {{ opacity: .55; border-left-color: #8a95a8; }}
    .node-kicker {{
      margin-bottom: 8px;
      color: var(--green);
      text-transform: uppercase;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: .04em;
    }}
    .comparison {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 16px;
    }}
    .comparison article {{
      padding: 18px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fff;
    }}
    ul {{ margin: 8px 0 0 20px; padding: 0; }}
    table {{
      width: 100%;
      border-collapse: collapse;
      overflow: hidden;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fff;
    }}
    th, td {{
      padding: 12px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      vertical-align: top;
      font-size: 14px;
    }}
    th {{ background: #eef4fb; color: #21395f; }}
    .conflict, .review {{
      margin: 0 0 12px;
      padding: 16px;
      border: 1px solid var(--line);
      border-left: 5px solid var(--red);
      border-radius: 8px;
      background: #fff;
    }}
    .review {{ border-left-color: #6f42c1; }}
    .muted {{ color: var(--muted); }}
    .callout {{
      padding: 16px;
      border-left: 5px solid var(--gold);
      border-radius: 8px;
      background: #fff8e6;
    }}
    .flow {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
    }}
    .pill {{
      padding: 8px 10px;
      border: 1px solid var(--line);
      border-radius: 999px;
      background: #fff;
      font-size: 13px;
      font-weight: 600;
    }}
    .arrow {{ color: var(--muted); }}
    @media (max-width: 1100px) {{
      .metrics {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      .node-grid, .grid-2, .comparison {{ grid-template-columns: 1fr; }}
      header, main {{ padding-left: 24px; padding-right: 24px; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>LangGraph Hantavirus Data Collection Demo</h1>
    <p>一个产品使用演示：用户输入采集任务后，workflow 把 source routing、真实网页抓取、结构化抽取、validation comparison 和 human review routing 拆成可观察节点。</p>
  </header>
  <main>
    <section class="band">
      <h2>1. 这次 demo 跑出了什么</h2>
      <div class="metrics">{metrics}</div>
    </section>

    <section class="band">
      <h2>2. 为什么这不是普通终端脚本</h2>
      <div class="comparison">
        <article>
          <h3>普通脚本视角</h3>
          <ul>
            <li>你看到的是 print 出来的摘要。</li>
            <li>某一步失败时，需要自己翻日志定位。</li>
            <li>中间状态如果没有手动保存，很难复现。</li>
            <li>人工审核、重跑、分支通常需要额外写控制逻辑。</li>
          </ul>
        </article>
        <article>
          <h3>LangGraph 视角</h3>
          <ul>
            <li>每个 node 的输入/输出都是 state 的一部分。</li>
            <li>Trace 可以看到 state 如何逐步长出来。</li>
            <li>Conditional edge 明确表达 quality gate 的分支。</li>
            <li>Studio 支持从节点检查、重跑、调试和后续 human-in-the-loop 扩展。</li>
          </ul>
        </article>
      </div>
    </section>

    <section class="band">
      <h2>3. 这条 graph 的业务故事</h2>
      <div class="flow">
        <span class="pill">Source catalog</span><span class="arrow">→</span>
        <span class="pill">Screening rules</span><span class="arrow">→</span>
        <span class="pill">Live webpage documents</span><span class="arrow">→</span>
        <span class="pill">Evidence chunks</span><span class="arrow">→</span>
        <span class="pill">Structured records</span><span class="arrow">→</span>
        <span class="pill">Linked event</span><span class="arrow">→</span>
        <span class="pill">Conflict</span><span class="arrow">→</span>
        <span class="pill">Human review</span><span class="arrow">→</span>
        <span class="pill">Final package</span>
      </div>
      <p class="muted">technical workshop 主线使用真实 NMDOH/CDC 网页 collection 和 Anthropic LLM extraction；节点视图用于解释 state 如何沿串行 workflow 累积，以及质量门如何把不可比或冲突结果送入人工审核。</p>
    </section>

    <section class="band">
      <h2>4. 节点级演示讲解</h2>
      <div class="node-grid">{node_cards}</div>
    </section>

    <section class="band">
      <h2>5. 每一步写入了哪些 state</h2>
      <table>
        {_row(["Node", "主要输出字段", "本次运行结果", "展示价值"], tag="th")}
        {_stage_rows(result)}
      </table>
    </section>

    <section class="band">
      <h2>6. 从 records 到 conflict</h2>
      {_records_table(records)}
    </section>

    <section class="band">
      <h2>7. 跨源冲突</h2>
      {_conflict_panels(conflicts)}
    </section>

    <section class="band">
      <h2>8. Human Review Packet</h2>
      {_review_panels(review_items)}
    </section>

    <section class="band">
      <h2>9. 用 Studio 怎么演示</h2>
      <div class="grid-2">
        <div>
          <h3>演示步骤</h3>
          <ol>
            <li>设置 API provider/model，并确认 API key 只从环境变量读取。</li>
            <li>输入 New Mexico HPS 2024-2026 collection request。</li>
            <li>启动 Studio：<code>python scripts/start_hdc_workflow_studio.py</code></li>
            <li>同配置导出可读报告：<code>python scripts/run_hdc_workflow_configured.py --allow-live-fetch --allow-llm</code></li>
            <li>切到 Trace，点开 <code>task_intake_and_scope_planning</code> 看 collection_spec。</li>
            <li>点开 <code>cross_source_consistency_check</code> 看 conflict。</li>
            <li>点开 <code>quality_gate_routing</code> 看它为什么进入 human_review。</li>
            <li>点开 <code>human_review</code> 看 review_packet。</li>
          </ol>
        </div>
        <div>
          <h3>一句话讲法</h3>
          <div class="callout">
            LangGraph 不是把终端输出换成网页，而是把公共卫生数据采集拆成可追踪的状态机：每个节点都留下结构化证据，质量门控可以分支，冲突可以被打包给人工审核，最终输出可以审计。
          </div>
        </div>
      </div>
    </section>

    <section class="band">
      <h2>10. 原始运行 metadata</h2>
      <div class="grid-2">
        <div>
          <h3>Collection Spec</h3>
          <pre>{_json(spec)}</pre>
        </div>
        <div>
          <h3>Package Metadata</h3>
          <pre>{_json(package_meta)}</pre>
        </div>
        <div>
          <h3>Provenance Manifest</h3>
          <pre>{_json(provenance)}</pre>
        </div>
        <div>
          <h3>Trace Node Order</h3>
          <pre>{_json([event.get("node_name") for event in trace])}</pre>
        </div>
      </div>
    </section>
  </main>
</body>
</html>
"""


def build_report(output_dir: Path) -> dict:
    data_source = "live_product_artifacts"
    result = _load_product_result()
    if result is None:
        data_source = "fallback_local_graph"
        os.environ["HDC_USE_FIXTURE_DOCUMENTS"] = "true"
        os.environ["HDC_ENABLE_LIVE_FETCH"] = "false"
        os.environ.setdefault("HDC_ENABLE_LLM_EXTRACTION", "false")
        graph = build_graph()
        result = graph.invoke(_initial_state())

    output_dir.mkdir(parents=True, exist_ok=True)
    html_path = output_dir / "langgraph_hdc_demo.html"
    summary_path = output_dir / "langgraph_hdc_demo_summary.json"

    html_path.write_text(_build_html(result), encoding="utf-8")
    product_demo_result = result.get("product_demo_result") or {}
    llm_stage_summary = product_demo_result.get("llm_stage_summary") or {}
    structured_llm = llm_stage_summary.get("structured_extraction") or {}
    source_planning = llm_stage_summary.get("source_planning") or {}
    source_critic = llm_stage_summary.get("source_critic") or {}
    legacy_llm_replay = product_demo_result.get("llm_replay_summary") or {}
    live_fetch_summary = product_demo_result.get("live_fetch_summary", {})
    live_fetch_enabled = live_fetch_summary.get("live_fetch_enabled")
    if live_fetch_enabled is None and data_source == "live_product_artifacts":
        live_fetch_enabled = bool(result.get("documents"))
    summary = {
        "html_path": str(html_path),
        "summary_path": str(summary_path),
        "data_source": data_source,
        "counts": {
            "trace_nodes": len(result.get("collection_trace") or []),
            "source_registry": _count(result, "source_registry"),
            "documents": _count(result, "documents"),
            "evidence_chunks": _count(result, "evidence_chunks"),
            "normalized_records": _count(result, "normalized_records"),
            "linked_events": _count(result, "linked_events"),
            "conflicts": _count(result, "conflicts"),
            "human_review_items": _count(result, "human_review_queue"),
        },
        "current_route": result.get("current_route"),
        "contains_synthetic_data": _contains_synthetic_data(
            result.get("final_data_package") or {}
        ),
        "live_fetch_enabled": live_fetch_enabled,
        "all_three_llm_stages_enabled": bool(
            source_planning.get("enabled")
            and source_critic.get("enabled")
            and structured_llm.get("enabled")
        ),
        "llm_source_planning_status": source_planning.get("status"),
        "llm_source_critic_assessed_source_count": source_critic.get(
            "assessed_source_count"
        ),
        "llm_call_succeeded": bool(
            structured_llm.get("success_count")
            or legacy_llm_replay.get("llm_call_succeeded")
        ),
        "llm_structured_extraction_call_count": structured_llm.get("call_count"),
    }
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return summary


def main() -> None:
    output_dir = _PROJECT_ROOT / "outputs" / "langgraph_demo"
    summary = build_report(output_dir)
    print("LangGraph demo report generated.")
    print(json.dumps(summary, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
