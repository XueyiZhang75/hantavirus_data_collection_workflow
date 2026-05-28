"""Optional LLM client factory + extraction call (Step 14).

Tests must NOT call real LLMs. The recommended monkeypatch pattern is:

    from hdc_workflow import llm_clients
    monkeypatch.setattr(llm_clients, "extract_chunk_with_llm", mock_fn)

Provider-specific dependencies (langchain_anthropic, langchain_openai) are
imported lazily inside `build_chat_model`, so importing this module does NOT
require those packages to be installed.
"""

from __future__ import annotations

import os

from .models import LLMExtractionOutput, LLMStructuredExtractionPolicy


def llm_extraction_enabled() -> bool:
    """True only if HDC_ENABLE_LLM_EXTRACTION is set to "true" (case-insensitive)."""

    return (
        (os.environ.get("HDC_ENABLE_LLM_EXTRACTION") or "")
        .strip()
        .lower()
        == "true"
    )


def llm_fallback_to_rule_based() -> bool:
    """True unless HDC_LLM_FALLBACK_TO_RULE_BASED is explicitly "false"."""

    value = (os.environ.get("HDC_LLM_FALLBACK_TO_RULE_BASED") or "").strip().lower()
    if value == "false":
        return False
    return True


def get_llm_settings() -> dict:
    """Read provider settings from the environment with safe defaults."""

    provider = (os.environ.get("HDC_LLM_PROVIDER") or "anthropic").strip().lower()
    model = (os.environ.get("HDC_LLM_MODEL") or "").strip()
    try:
        temperature = float(os.environ.get("HDC_LLM_TEMPERATURE") or "0")
    except (TypeError, ValueError):
        temperature = 0.0
    try:
        max_tokens = int(os.environ.get("HDC_LLM_MAX_TOKENS") or "4096")
    except (TypeError, ValueError):
        max_tokens = 4096
    return {
        "provider": provider,
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }


def _validate_provider_settings(settings: dict) -> None:
    provider = settings.get("provider")
    model = settings.get("model")
    if provider == "anthropic":
        if not model:
            raise ValueError(
                "LLM extraction enabled with provider=anthropic but HDC_LLM_MODEL "
                "is empty. Set HDC_LLM_MODEL to a Claude model name available in "
                "your Anthropic account."
            )
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise ValueError(
                "LLM extraction enabled with provider=anthropic but ANTHROPIC_API_KEY "
                "is not set. Set ANTHROPIC_API_KEY to a valid Anthropic API key."
            )
        return
    if provider == "openai":
        if not model:
            raise ValueError(
                "LLM extraction enabled with provider=openai but HDC_LLM_MODEL is "
                "empty. Set HDC_LLM_MODEL to an OpenAI model name."
            )
        if not os.environ.get("OPENAI_API_KEY"):
            raise ValueError(
                "LLM extraction enabled with provider=openai but OPENAI_API_KEY is "
                "not set. Set OPENAI_API_KEY to a valid OpenAI API key."
            )
        return
    raise ValueError(
        f"Unsupported HDC_LLM_PROVIDER='{provider}'. "
        "Supported providers: 'anthropic', 'openai'."
    )


def build_chat_model():
    """Build a chat model for the configured provider. Does NOT invoke it."""

    settings = get_llm_settings()
    _validate_provider_settings(settings)
    provider = settings["provider"]
    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic  # local import keeps tests light

        return ChatAnthropic(
            model=settings["model"],
            temperature=settings["temperature"],
            max_tokens=settings["max_tokens"],
        )
    if provider == "openai":
        from langchain_openai import ChatOpenAI  # local import keeps tests light

        return ChatOpenAI(
            model=settings["model"],
            temperature=settings["temperature"],
        )
    raise ValueError(f"Unsupported provider: {provider}")


def _format_required_rules(policy: LLMStructuredExtractionPolicy) -> str:
    return "\n".join(
        f"{i + 1}. {rule}" for i, rule in enumerate(policy.required_output_rules)
    )


def _build_llm_messages(chunk: dict, policy: LLMStructuredExtractionPolicy) -> list:
    system_text = (
        policy.system_prompt
        + "\n\nRequired output rules:\n"
        + _format_required_rules(policy)
    )
    user_text = "\n".join(
        [
            f"source_id: {chunk.get('source_id')}",
            f"source_url: {chunk.get('source_url')}",
            f"source_type: {chunk.get('source_type')}",
            f"title: {chunk.get('title')}",
            f"publisher: {chunk.get('publisher')}",
            f"supporting_chunk_id: {chunk.get('chunk_id')}",
            f"fetch_purpose: {chunk.get('fetch_purpose')}",
            f"chunk_kind: {chunk.get('chunk_kind')}",
            f"data_types: {chunk.get('data_types')}",
            f"context_types: {chunk.get('context_types')}",
            "",
            "Evidence chunk text:",
            chunk.get("text") or "",
        ]
    )
    return [
        {"role": "system", "content": system_text},
        {"role": "user", "content": user_text},
    ]


def extract_chunk_with_llm(
    chunk: dict,
    policy: LLMStructuredExtractionPolicy,
) -> LLMExtractionOutput:
    """Call the configured LLM and return a validated LLMExtractionOutput.

    Raises on any provider/configuration/parse error so that the caller can
    decide whether to fall back to deterministic extraction.
    """

    model = build_chat_model()
    structured_model = model.with_structured_output(LLMExtractionOutput)
    messages = _build_llm_messages(chunk, policy)
    result = structured_model.invoke(messages)
    if isinstance(result, LLMExtractionOutput):
        return result
    if isinstance(result, dict):
        return LLMExtractionOutput(**result)
    raise ValueError(f"Unexpected LLM output type: {type(result)!r}")
