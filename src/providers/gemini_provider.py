from typing import Type, TypeVar
from google import genai
from google.genai import types
from google.genai.errors import APIError
from pydantic import BaseModel
from src.providers.base import TransientProviderError

T = TypeVar("T", bound=BaseModel)

TRANSIENT_STATUS_CODES = {429, 500, 503, 504}


class GeminiProvider:
    """Google Gemini adapter implementing the LLMProvider Protocol."""

    def __init__(self, client: genai.Client | None = None) -> None:
        self._client = client or genai.Client()

    def generate_structured(
        self,
        model_id: str,
        prompt: str,
        response_schema: Type[T],
        system_instruction: str | None = None,
    ) -> T:
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema=response_schema,
            temperature=0.0,
        )
        try:
            response = self._client.models.generate_content(
                model=model_id,
                contents=prompt,
                config=config,
            )
        except APIError as e:
            if e.code in TRANSIENT_STATUS_CODES:
                raise TransientProviderError(
                    f"Gemini model '{model_id}' unavailable (HTTP {e.code})"
                ) from e
            raise  # Fail fast on 400/401/403 client errors

        return response_schema.model_validate_json(response.text)