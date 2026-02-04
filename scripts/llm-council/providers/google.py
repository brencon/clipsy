"""Google AI (Gemini) provider adapter."""

from typing import Optional
import httpx

from .base import BaseProvider, ProviderResponse


class GoogleProvider(BaseProvider):
    """Provider adapter for Google's Gemini API."""

    PROVIDER_NAME = "google"
    ENV_KEY_NAME = "GOOGLE_AI_API_KEY"
    API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"

    async def complete(
        self,
        prompt: str,
        model: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> ProviderResponse:
        """Send completion request to Google AI API."""
        api_key = self.get_api_key()
        if not api_key:
            return self._create_error_response(
                f"API key not found. Set {self.ENV_KEY_NAME} environment variable.",
                model,
            )

        url = f"{self.API_BASE}/{model}:generateContent?key={api_key}"

        headers = {
            "Content-Type": "application/json",
        }

        contents = []
        if system_prompt:
            contents.append({
                "role": "user",
                "parts": [{"text": f"System instruction: {system_prompt}"}],
            })
            contents.append({
                "role": "model",
                "parts": [{"text": "Understood. I will follow these instructions."}],
            })

        contents.append({
            "role": "user",
            "parts": [{"text": prompt}],
        })

        payload = {
            "contents": contents,
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": temperature,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    url,
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
                candidates = data.get("candidates", [])
                if candidates and len(candidates) > 0:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts and len(parts) > 0:
                        content = parts[0].get("text", "")

                usage = data.get("usageMetadata", {})

                return ProviderResponse(
                    content=content,
                    model=model,
                    provider=self.PROVIDER_NAME,
                    input_tokens=usage.get("promptTokenCount"),
                    output_tokens=usage.get("candidatesTokenCount"),
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
