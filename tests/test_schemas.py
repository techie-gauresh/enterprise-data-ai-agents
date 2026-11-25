import pytest
from pydantic import ValidationError
from src.schemas import SQLQueryPlan


def test_valid_select_query_passes():
    plan = SQLQueryPlan(
        reasoning="Aggregating revenue by region.",
        tables_used=["orders"],
        sql_query="SELECT region, SUM(total_amount) FROM orders GROUP BY region;",
        confidence="high",
    )
    assert plan.confidence == "high"


@pytest.mark.parametrize(
    "bad_sql",
    [
        "DROP TABLE orders;",
        "SELECT * FROM orders; DELETE FROM orders;",
        "UPDATE orders SET total_amount = 0;",
    ],
)
def test_destructive_sql_is_blocked(bad_sql):
    with pytest.raises(ValidationError, match="Guardrail violation"):
        SQLQueryPlan(
            reasoning="Malicious or accidental mutation.",
            tables_used=["orders"],
            sql_query=bad_sql,
            confidence="low",
        )