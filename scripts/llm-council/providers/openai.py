"""OpenAI provider adapter."""

from typing import Optional
import httpx

from .base import BaseProvider, ProviderResponse


class OpenAIProvider(BaseProvider):
    """Provider adapter for OpenAI's API."""

    PROVIDER_NAME = "openai"
    ENV_KEY_NAME = "OPENAI_API_KEY"
    API_URL = "https://api.openai.com/v1/chat/completions"

    async def complete(
        self,
        prompt: str,
        model: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> ProviderResponse:
        """Send completion request to OpenAI API."""
        api_key = self.get_api_key()
        if not api_key:
            return self._create_error_response(
                f"API key not found. Set {self.ENV_KEY_NAME} environment variable.",
                model,
            )

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

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
                if data.get("choices") and len(data["choices"]) > 0:
                    content = data["choices"][0].get("message", {}).get("content", "")

                usage = data.get("usage", {})

                return ProviderResponse(
                    content=content,
                    model=data.get("model", model),
                    provider=self.PROVIDER_NAME,
                    input_tokens=usage.get("prompt_tokens"),
                    output_tokens=usage.get("completion_tokens"),
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
