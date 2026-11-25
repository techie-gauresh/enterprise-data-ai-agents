from typing import Protocol, Type, TypeVar
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

class TransientProviderError(Exception):
    """Vendor-agnostic error for 429 / 500 / 503 / 504."""

class LLMProvider(Protocol):
    def generate_structured(
        self,
        model_id: str,
        prompt: str,
        response_schema: Type[T],
        system_instruction: str | None = None,
    ) -> T: ...