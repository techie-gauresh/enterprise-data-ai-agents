from typing import Any, Type, TypeVar
from pydantic import BaseModel
from src.llm_client import SQLAgentService
from src.model_router import ReasoningTier, RouteDecision
from src.providers.base import TransientProviderError
from src.schemas import SQLQueryPlan

T = TypeVar("T", bound=BaseModel)


class FakeLLMProvider:
    """In-memory mock provider for deterministic unit testing of routing & failover."""

    def __init__(self, responses: list[Any]) -> None:
        self._responses = list(responses)
        self.called_models: list[str] = []

    def generate_structured(
        self,
        model_id: str,
        prompt: str,
        response_schema: Type[T],
        system_instruction: str | None = None,
    ) -> T:
        self.called_models.append(model_id)
        outcome = self._responses.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def test_failover_on_503_transient_error():
    valid_plan = SQLQueryPlan(
        reasoning="Aggregating revenue.",
        tables_used=["orders"],
        sql_query="SELECT SUM(total_amount) FROM orders;",
        confidence="high",
    )
    fake = FakeLLMProvider(
        responses=[
            RouteDecision(tier="balanced", reason="Standard aggregation."),
            TransientProviderError("model-primary 503"),
            valid_plan,
        ]
    )
    chains = {
        ReasoningTier.FAST: ["model-fast"],
        ReasoningTier.BALANCED: ["model-primary", "model-backup"],
        ReasoningTier.DEEP: ["model-deep"],
    }

    service = SQLAgentService(provider=fake, fallback_chains=chains)
    result = service.generate_sql_plan("Total revenue?", schema_context="orders(total_amount)")

    assert result.sql_query == "SELECT SUM(total_amount) FROM orders;"
    assert fake.called_models == ["model-fast", "model-primary", "model-backup"]


def test_low_confidence_escalates_to_deep_tier():
    low_conf_plan = SQLQueryPlan(
        reasoning="Unsure about schema.",
        tables_used=["orders"],
        sql_query="SELECT * FROM orders;",
        confidence="low",
    )
    high_conf_plan = SQLQueryPlan(
        reasoning="Resolved with deep reasoning.",
        tables_used=["orders"],
        sql_query="SELECT region, SUM(total_amount) FROM orders GROUP BY region;",
        confidence="high",
    )
    fake = FakeLLMProvider(
        responses=[
            RouteDecision(tier="fast", reason="Looks simple."),
            low_conf_plan,
            high_conf_plan,
        ]
    )
    chains = {
        ReasoningTier.FAST: ["model-fast"],
        ReasoningTier.BALANCED: ["model-balanced"],
        ReasoningTier.DEEP: ["model-deep"],
    }

    service = SQLAgentService(provider=fake, fallback_chains=chains)
    result = service.generate_sql_plan("Revenue by region?", schema_context="orders(region, total_amount)")

    assert result.confidence == "high"
    assert fake.called_models == ["model-fast", "model-fast", "model-deep"]