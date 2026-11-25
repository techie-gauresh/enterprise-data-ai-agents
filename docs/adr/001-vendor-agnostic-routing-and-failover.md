# ADR-001: Vendor-Agnostic LLM Abstraction, Dynamic Routing, and Cross-Model Failover

- **Status:** Accepted
- **Date:** 2026-11-25

## Context
Enterprise NL-to-SQL and data governance agents face three immediate production challenges:
1. **Vendor Lock-In:** Coupling orchestration logic directly to a single model SDK makes multi-cloud deployment (GCP, AWS Bedrock, Azure) and offline unit testing expensive.
2. **Cost vs. Reasoning Trade-off:** Routing trivial single-table aggregations to frontier reasoning models wastes latency and token budget, while routing complex multi-CTE window queries to lightweight models degrades SQL accuracy.
3. **Transient Upstream Failures:** Hosted LLM endpoints routinely experience temporary congestion (`HTTP 503`) and quota ceilings (`HTTP 429`).

## Decision
1. **Ports & Adapters (`LLMProvider` Protocol):** Define a vendor-agnostic `LLMProvider` interface and `TransientProviderError` in `src/providers/base.py`. Isolate all `google-genai` SDK imports inside `src/providers/gemini_provider.py`.
2. **Dynamic Complexity Routing:** Use a low-latency classifier (`select_tier`) returning a strict Pydantic `RouteDecision` (`fast`, `balanced`, `deep`) to dispatch queries to the appropriate tier.
3. **Ordered Fallback Chains & Escalation:** Configure per-tier fallback chains in `SQLAgentService`. Automatically fail over on `TransientProviderError` (429/500/503/504) or Pydantic guardrail violations, fail fast on client errors (400/401/403), and escalate to the `deep` tier when a lighter model reports `confidence == "low"`.
4. **Deterministic Schema Guardrails:** Enforce structured JSON output and read-only SQL validation via Pydantic v2 (`SQLQueryPlan`).

## Consequences
- **Positive:** Zero vendor imports in core routing/orchestration; deterministic offline `pytest` verification of 503 failover and confidence escalation in <0.1s; automatic resilience to model-specific outages.
- **Trade-offs:** The routing step adds one lightweight LLM call (~200–400ms) before SQL generation.
- **Next Iteration (ADR-002):** Replace the initial regex SQL validator with a deterministic `sqlglot` AST parser to block writable CTEs and hallucinated tables, and introduce `AsyncIO` + `Semaphore` concurrency.
EOF