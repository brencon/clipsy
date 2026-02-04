"""LLM Provider abstraction for PDF semantic analysis.

Supports Anthropic (primary) and OpenAI (fallback).
"""

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class LLMResponse:
    """Response from an LLM provider."""

    content: str
    model: str
    input_tokens: int
    output_tokens: int


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def complete(self, system: str, messages: list[dict], max_tokens: int = 4096) -> LLMResponse:
        """Send a completion request to the LLM."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available (has API key)."""
        pass


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider."""

    def __init__(self, model: str = "claude-sonnet-4-20250514"):
        self.model = model
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self._client = None

    def is_available(self) -> bool:
        return bool(self.api_key)

    def _get_client(self):
        if self._client is None:
            import anthropic
            self._client = anthropic.Anthropic(api_key=self.api_key)
        return self._client

    def complete(self, system: str, messages: list[dict], max_tokens: int = 4096) -> LLMResponse:
        client = self._get_client()
        response = client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system,
            messages=messages,
        )
        return LLMResponse(
            content=response.content[0].text,
            model=self.model,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
        )


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider."""

    def __init__(self, model: str = "gpt-4o"):
        self.model = model
        self.api_key = os.getenv("OPENAI_API_KEY")
        self._client = None

    def is_available(self) -> bool:
        return bool(self.api_key)

    def _get_client(self):
        if self._client is None:
            import openai
            self._client = openai.OpenAI(api_key=self.api_key)
        return self._client

    def complete(self, system: str, messages: list[dict], max_tokens: int = 4096) -> LLMResponse:
        client = self._get_client()
        openai_messages = [{"role": "system", "content": system}]
        for msg in messages:
            openai_messages.append({"role": msg["role"], "content": msg["content"]})

        response = client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=openai_messages,
        )
        return LLMResponse(
            content=response.choices[0].message.content,
            model=self.model,
            input_tokens=response.usage.prompt_tokens,
            output_tokens=response.usage.completion_tokens,
        )


def get_provider(preferred: str = "anthropic") -> LLMProvider:
    """Get an available LLM provider.

    Args:
        preferred: Preferred provider ("anthropic" or "openai")

    Returns:
        An available LLM provider

    Raises:
        RuntimeError: If no provider is available
    """
    providers = {
        "anthropic": AnthropicProvider,
        "openai": OpenAIProvider,
    }

    if preferred in providers:
        provider = providers[preferred]()
        if provider.is_available():
            return provider

    for name, provider_class in providers.items():
        if name != preferred:
            provider = provider_class()
            if provider.is_available():
                return provider

    raise RuntimeError(
        "No LLM provider available. Set ANTHROPIC_API_KEY or OPENAI_API_KEY in .env"
    )
