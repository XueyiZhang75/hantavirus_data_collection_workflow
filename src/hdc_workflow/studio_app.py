"""LangGraph Studio entry point.

Exposes a compiled `graph` object that the LangGraph CLI / Studio can pick up
via `langgraph.json`. No LLM calls, no network, no scraping — the underlying
workflow is the same offline, deterministic graph used by the demo script.
"""

from __future__ import annotations

# Use an absolute import: LangGraph CLI loads this file by path (not as a
# package member), so `from .graph import build_graph` would raise
# "attempted relative import with no known parent package".
from hdc_workflow.graph import build_graph

graph = build_graph()
