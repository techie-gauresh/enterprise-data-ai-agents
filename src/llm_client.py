import logging
from pydantic import ValidationError
from src.model_router import ReasoningTier, select_tier
from src.providers.base import LLMProvider, TransientProviderError
from src.schemas import SQLQueryPlan

logger = logging.getLogger(__name__)

DEFAULT_FALLBACK_CHAINS: dict[ReasoningTier, list[str]] = {
    ReasoningTier.FAST: [
        "gemini-3.5-flash-lite",
        "gemini-3.8-flash",
    ],
    ReasoningTier.BALANCED: [
        "gemini-3.8-flash",
        "gemini-4-hydrogen",
        "gemini-3.5-flash-lite",
    ],
    ReasoningTier.DEEP: [
        "gemini-4-hydrogen",
        "gemini-3.8-flash",
        "gemini-3.5-flash-lite",
    ],
}


class SQLAgentService:
    """Vendor-agnostic NL-to-SQL orchestrator with routing, failover, and confidence escalation."""

    def __init__(
        self,
        provider: LLMProvider,
        fallback_chains: dict[ReasoningTier, list[str]] | None = None,
    ) -> None:
        self._provider = provider
        self._fallback_chains = fallback_chains or DEFAULT_FALLBACK_CHAINS

    def _execute_with_fallback(
        self, tier: ReasoningTier, user_question: str, schema_context: str
    ) -> tuple[SQLQueryPlan, str]:
        system_prompt = (
            "You are a senior data engineer. Generate strictly read-only SQL "
            f"using ONLY this schema:\n{schema_context}"
        )
        last_error: Exception | None = None

        for model_id in self._fallback_chains[tier]:
            try:
                plan = self._provider.generate_structured(
                    model_id=model_id,
                    prompt=user_question,
                    response_schema=SQLQueryPlan,
                    system_instruction=system_prompt,
                )
                return plan, model_id
            except TransientProviderError as e:
                logger.warning("[Fallback] %s. Trying next model...", e)
                last_error = e
                continue
            except ValidationError as e:
                logger.warning(
                    "[Fallback] '%s' violated Pydantic guardrail. Trying next model...",
                    model_id,
                )
                last_error = e
                continue

        raise RuntimeError(f"All fallback models failed for tier={tier.value}") from last_error

    def generate_sql_plan(self, user_question: str, schema_context: str) -> SQLQueryPlan:
        router_model = self._fallback_chains[ReasoningTier.FAST][0]

        # Step 1: Route based on reasoning complexity
        try:
            decision = select_tier(self._provider, user_question, router_model_id=router_model)
            tier = ReasoningTier(decision.tier)
            logger.info("[Router] Selected tier='%s' -> %s", tier.value, decision.reason)
        except TransientProviderError as e:
            tier = ReasoningTier.BALANCED
            logger.warning("[Router] Classifier unavailable (%s). Defaulting to 'balanced'.", e)

        # Step 2: Execute with cross-model failover
        plan, used_model = self._execute_with_fallback(tier, user_question, schema_context)
        logger.info("[Success] Served by '%s'", used_model)

        # Step 3: Escalate to DEEP tier if a lighter model returned low confidence
        deep_primary = self._fallback_chains[ReasoningTier.DEEP][0]
        if plan.confidence == "low" and used_model != deep_primary:
            logger.info("[Cascade] Low confidence detected. Escalating to DEEP tier...")
            plan, used_model = self._execute_with_fallback(
                ReasoningTier.DEEP, user_question, schema_context
            )
            logger.info("[Success] Escalated response served by '%s'", used_model)

        return plan


if __name__ == "__main__":
    from src.providers.gemini_provider import GeminiProvider

    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")

    sample_schema = """
    Tables:
    - orders(order_id INT, customer_id INT, region VARCHAR, order_date DATE, total_amount DECIMAL)
    - customers(customer_id INT, segment VARCHAR, country VARCHAR)
    """

    service = SQLAgentService(provider=GeminiProvider())
    questions = [
        "Count total orders.",
        "Show month-over-month revenue growth % by customer segment and region for 2026 using window functions.",
    ]
    for q in questions:
        print(f"\n--- Question: {q} ---")
        plan = service.generate_sql_plan(q, schema_context=sample_schema)
        print(plan.model_dump_json(indent=2))