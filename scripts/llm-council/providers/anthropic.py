"""Anthropic (Claude) provider adapter."""

from typing import Optional
import httpx

from .base import BaseProvider, ProviderResponse


class AnthropicProvider(BaseProvider):
    """Provider adapter for Anthropic's Claude API."""

    PROVIDER_NAME = "anthropic"
    ENV_KEY_NAME = "ANTHROPIC_API_KEY"
    API_URL = "https://api.anthropic.com/v1/messages"
    API_VERSION = "2023-06-01"

    async def complete(
        self,
        prompt: str,
        model: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> ProviderResponse:
        """Send completion request to Anthropic API."""
        api_key = self.get_api_key()
        if not api_key:
            return self._create_error_response(
                f"API key not found. Set {self.ENV_KEY_NAME} environment variable.",
                model,
            )

        headers = {
            "Content-Type": "application/json",
            "X-API-Key": api_key,
            "anthropic-version": self.API_VERSION,
        }

        messages = [{"role": "user", "content": prompt}]

        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        if system_prompt:
            payload["system"] = system_prompt

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.API_URL,
                    headers=headers,
                    json=payload,
                )

                if response.status_code != 200:
                    error_detail = response.text
                    return self._create_error_response(
                        f"API error ({response.status_code}): {error_detail}",
                        model,
                    )

                data = response.json()

                content = ""
                if data.get("content") and len(data["content"]) > 0:
                    content = data["content"][0].get("text", "")

                usage = data.get("usage", {})

                return ProviderResponse(
                    content=content,
                    model=data.get("model", model),
                    provider=self.PROVIDER_NAME,
                    input_tokens=usage.get("input_tokens"),
                    output_tokens=usage.get("output_tokens"),
                )

        except httpx.TimeoutException:
            return self._create_error_response(
                "Request timed out after 60 seconds",
                model,
            )
        except httpx.RequestError as e:
            return self._create_error_response(
                f"Request failed: {str(e)}",
                model,
            )
        except Exception as e:
            return self._create_error_response(
                f"Unexpected error: {str(e)}",
                model,
            )
