"""Optional LLM client factory + structured LLM calls.

Tests must NOT call real LLMs. The recommended monkeypatch pattern is:

    from hdc_workflow import llm_clients
    monkeypatch.setattr(llm_clients, "extract_chunk_with_llm", mock_fn)
    monkeypatch.setattr(llm_clients, "run_structured_llm_json", mock_fn)

Provider-specific dependencies (langchain_anthropic, langchain_openai) are
imported lazily inside `build_chat_model`, so importing this module does NOT
require those packages to be installed.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any

from pydantic import BaseModel

from .models import LLMExtractionOutput, LLMStructuredExtractionPolicy


def _env_flag(name: str) -> bool:
    return (os.environ.get(name) or "").strip().lower() == "true"


def llm_extraction_enabled() -> bool:
    """True only if HDC_ENABLE_LLM_EXTRACTION is set to "true" (case-insensitive)."""

    return _env_flag("HDC_ENABLE_LLM_EXTRACTION")


def llm_source_planning_enabled() -> bool:
    """True only if HDC_ENABLE_LLM_SOURCE_PLANNING is explicitly true."""

    return _env_flag("HDC_ENABLE_LLM_SOURCE_PLANNING")


def llm_source_critic_enabled() -> bool:
    """True only if HDC_ENABLE_LLM_SOURCE_CRITIC is explicitly true."""

    return _env_flag("HDC_ENABLE_LLM_SOURCE_CRITIC")


def llm_source_credibility_enabled() -> bool:
    """True only if HDC_ENABLE_LLM_SOURCE_CREDIBILITY is explicitly true."""

    return _env_flag("HDC_ENABLE_LLM_SOURCE_CREDIBILITY")


def llm_source_identity_enabled() -> bool:
    """True only if HDC_ENABLE_LLM_SOURCE_IDENTITY is explicitly true."""

    return _env_flag("HDC_ENABLE_LLM_SOURCE_IDENTITY")


def llm_disease_intelligence_enabled() -> bool:
    """True only if HDC_ENABLE_LLM_DISEASE_INTELLIGENCE is explicitly true."""

    return _env_flag("HDC_ENABLE_LLM_DISEASE_INTELLIGENCE")


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


def build_chat_model(settings: dict | None = None):
    """Build a chat model for the configured provider. Does NOT invoke it."""

    settings = dict(settings or get_llm_settings())
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


def _langsmith_runnable_config(run_name: str, *, stage: str) -> dict:
    settings = get_llm_settings()
    metadata = {
        "session_id": os.environ.get("HDC_TRACE_SESSION_ID"),
        "trace_id": os.environ.get("HDC_TRACE_ID"),
        "langsmith_project": os.environ.get("LANGSMITH_PROJECT"),
        "llm_provider": settings.get("provider"),
        "llm_model": settings.get("model"),
        "hdc_stage": stage,
    }
    return {
        "run_name": run_name,
        "tags": ["hdc-workflow", "hdc-llm", stage],
        "metadata": {key: value for key, value in metadata.items() if value},
    }


def _invoke_with_config(runnable: Any, messages: list, config: dict) -> Any:
    try:
        return runnable.invoke(messages, config=config)
    except TypeError as exc:
        # Some tests and lightweight fakes implement invoke(messages) only.
        if "config" not in str(exc) and "positional" not in str(exc):
            raise
        return runnable.invoke(messages)


def _message_content(result) -> str:
    if isinstance(result, str):
        return result
    if isinstance(result, dict):
        return json.dumps(result)
    content = getattr(result, "content", None)
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                text = item.get("text") or item.get("content")
                if text:
                    parts.append(str(text))
        return "\n".join(parts)
    return str(result)


def _strip_markdown_fence(text: str) -> str:
    stripped = (text or "").strip()
    fence_match = re.fullmatch(
        r"```(?:json|JSON)?\s*(.*?)\s*```",
        stripped,
        flags=re.DOTALL,
    )
    if fence_match:
        return fence_match.group(1).strip()
    return stripped


def _json_object_substrings(text: str) -> list[str]:
    substrings: list[str] = []
    start: int | None = None
    depth = 0
    in_string = False
    escaped = False

    for index, char in enumerate(text):
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
        elif char == "{":
            if depth == 0:
                start = index
            depth += 1
        elif char == "}" and depth > 0:
            depth -= 1
            if depth == 0 and start is not None:
                substrings.append(text[start:index + 1])
                start = None
    return substrings


def _parse_json_object(text: str) -> dict:
    stripped = _strip_markdown_fence(text)
    if not stripped:
        raise ValueError("LLM returned empty output.")
    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError:
        candidates = sorted(
            _json_object_substrings(stripped),
            key=len,
            reverse=True,
        )
        last_error: json.JSONDecodeError | None = None
        for candidate in candidates:
            try:
                parsed = json.loads(candidate)
                break
            except json.JSONDecodeError as exc:
                last_error = exc
        else:
            if last_error is not None:
                raise last_error
            raise
    if not isinstance(parsed, dict):
        raise ValueError(f"Expected JSON object from LLM, got {type(parsed)!r}.")
    return parsed


def _model_to_dict(result, schema_model: type[BaseModel]) -> dict:
    if isinstance(result, schema_model):
        model_instance = result
    elif isinstance(result, BaseModel):
        model_instance = schema_model.model_validate(result.model_dump())
    elif isinstance(result, dict):
        model_instance = schema_model.model_validate(result)
    else:
        model_instance = schema_model.model_validate(_parse_json_object(_message_content(result)))
    return model_instance.model_dump()


def run_structured_llm_json(
    system_prompt: str,
    user_prompt: str,
    expected_schema_name: str,
    model: str | None = None,
    temperature: float = 0.0,
) -> dict:
    """Call the configured chat model and parse a JSON object response.

    This generic helper is intentionally small. Agent nodes use it only behind
    explicit feature flags, and tests monkeypatch it so no external API call is
    made during normal verification.
    """

    settings = get_llm_settings()
    if model:
        settings["model"] = model
    settings["temperature"] = temperature
    chat_model = build_chat_model(settings)
    messages = [
        {
            "role": "system",
            "content": (
                system_prompt
                + "\n\nReturn only one valid JSON object for schema: "
                + expected_schema_name
                + "."
            ),
        },
        {"role": "user", "content": user_prompt},
    ]
    result = _invoke_with_config(
        chat_model,
        messages,
        _langsmith_runnable_config(
            f"llm.{expected_schema_name}",
            stage=expected_schema_name,
        ),
    )
    if isinstance(result, dict):
        return result
    return _parse_json_object(_message_content(result))


def run_pydantic_structured_llm(
    system_prompt: str,
    user_prompt: str,
    schema_model: type[BaseModel],
    model: str | None = None,
    temperature: float = 0.0,
) -> dict:
    """Call the configured chat model with a Pydantic structured output schema."""

    settings = get_llm_settings()
    if model:
        settings["model"] = model
    settings["temperature"] = temperature
    chat_model = build_chat_model(settings)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    provider_error: Exception | None = None
    try:
        structured_model = chat_model.with_structured_output(schema_model)
        result = _invoke_with_config(
            structured_model,
            messages,
            _langsmith_runnable_config(
                f"llm.{schema_model.__name__}",
                stage=schema_model.__name__,
            ),
        )
        payload = _model_to_dict(result, schema_model)
        payload["_structured_output_mode"] = "provider_native"
        return payload
    except Exception as exc:  # noqa: BLE001 - fallback keeps advisory agents robust
        provider_error = exc

    try:
        raw = run_structured_llm_json(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            expected_schema_name=schema_model.__name__,
            model=settings.get("model"),
            temperature=temperature,
        )
        payload = _model_to_dict(raw, schema_model)
        payload["_structured_output_mode"] = "fallback_json"
        return payload
    except Exception as fallback_exc:
        raise ValueError(
            "Pydantic structured LLM call failed. "
            f"provider_native_error={type(provider_error).__name__}: {provider_error}; "
            f"fallback_json_error={type(fallback_exc).__name__}: {fallback_exc}"
        ) from fallback_exc


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
    user_parts = [
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
    ]
    if chunk.get("task_acceptance_contract"):
        user_parts.extend(
            [
                "",
                "Task acceptance contract:",
                json.dumps(
                    chunk.get("task_acceptance_contract"),
                    ensure_ascii=True,
                    sort_keys=True,
                ),
            ]
        )
    user_parts.extend(
        [
            "",
            "Evidence chunk text:",
            chunk.get("text") or "",
        ]
    )
    user_text = "\n".join(user_parts)
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
    result = _invoke_with_config(
        structured_model,
        messages,
        _langsmith_runnable_config(
            "llm.LLMExtractionOutput",
            stage="structured_extraction",
        ),
    )
    if isinstance(result, LLMExtractionOutput):
        return result
    if isinstance(result, dict):
        return LLMExtractionOutput(**result)
    raise ValueError(f"Unexpected LLM output type: {type(result)!r}")
