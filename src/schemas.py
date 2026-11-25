import re
from typing import List, Literal
from pydantic import BaseModel, Field, field_validator


class SQLQueryPlan(BaseModel):
    """Structured output contract for an Enterprise NL-to-SQL Agent."""

    reasoning: str = Field(
        ...,
        description="Step-by-step explanation of how the user's question maps to tables and joins."
    )
    tables_used: List[str] = Field(
        ...,
        min_length=1,
        description="Exact table names referenced in the SQL query."
    )
    sql_query: str = Field(
        ...,
        description="A single read-only PostgreSQL SELECT query. Must not mutate data."
    )
    confidence: Literal["high", "medium", "low"] = Field(
        ...,
        description="Confidence level based on whether the schema fully answers the question."
    )

    @field_validator("sql_query")
    @classmethod
    def enforce_read_only_sql(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned.upper().startswith(("SELECT", "WITH")):
            raise ValueError("Guardrail violation: Only SELECT or CTE (WITH) queries are allowed.")

        forbidden = r"\b(DROP|DELETE|UPDATE|INSERT|ALTER|TRUNCATE|GRANT|REVOKE)\b"
        if re.search(forbidden, cleaned, re.IGNORECASE):
            raise ValueError("Guardrail violation: Destructive or DDL SQL keyword detected.")

        if ";" in cleaned.rstrip(";"):
            raise ValueError("Guardrail violation: Multiple SQL statements are not permitted.")

        return cleaned