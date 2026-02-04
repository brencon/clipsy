"""Base provider interface for LLM Council.

All provider adapters must implement this interface for unified access.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
import os


@dataclass
class ProviderResponse:
    """Standardized response from any LLM provider."""

    content: str
    model: str
    provider: str
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    error: Optional[str] = None

    @property
    def success(self) -> bool:
        return self.error is None


class BaseProvider(ABC):
    """Abstract base class for LLM provider adapters.

    Each provider must implement:
    - get_api_key(): Return the API key from environment
    - is_available(): Check if provider is configured
    - complete(): Send a completion request
    """

    PROVIDER_NAME: str = "base"
    ENV_KEY_NAME: str = "API_KEY"

    def __init__(self):
        self._api_key: Optional[str] = None

    def get_api_key(self) -> Optional[str]:
        """Get API key from environment variable."""
        if self._api_key is None:
            self._api_key = os.getenv(self.ENV_KEY_NAME)
        return self._api_key

    def is_available(self) -> bool:
        """Check if this provider is configured and available."""
        key = self.get_api_key()
        return key is not None and len(key) > 0

    @abstractmethod
    async def complete(
        self,
        prompt: str,
        model: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> ProviderResponse:
        """Send a completion request to the provider.

        Args:
            prompt: The user message/prompt
            model: The model identifier (e.g., "claude-sonnet-4-20250514")
            system_prompt: Optional system message
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature

        Returns:
            ProviderResponse with the completion or error
        """
        pass

    def _create_error_response(self, error: str, model: str) -> ProviderResponse:
        """Helper to create an error response."""
        return ProviderResponse(
            content="",
            model=model,
            provider=self.PROVIDER_NAME,
            error=error,
        )
