from enum import Enum
from typing import Literal
from pydantic import BaseModel, Field
from src.providers.base import LLMProvider


class ReasoningTier(str, Enum):
    FAST = "fast"          # Classification, extraction, simple 1-table SQL
    BALANCED = "balanced"  # Multi-table joins, aggregations, standard coding
    DEEP = "deep"          # Complex CTEs, window functions, root-cause ETL analysis


class RouteDecision(BaseModel):
    tier: Literal["fast", "balanced", "deep"] = Field(
        ...,
        description=(
            "fast: simple lookup or single-table aggregation; "
            "balanced: joins, grouping, date filtering; "
            "deep: complex multi-CTE analytics, anomaly root-cause, or ambiguous logic."
        ),
    )
    reason: str = Field(..., description="One-sentence justification for selecting this tier.")


def select_tier(
    provider: LLMProvider,
    user_question: str,
    router_model_id: str,
) -> RouteDecision:
    """Classifies task complexity using any LLMProvider to select the target reasoning tier."""
    return provider.generate_structured(
        model_id=router_model_id,
        prompt=f"Classify the SQL reasoning complexity for this request:\n{user_question}",
        response_schema=RouteDecision,
    )