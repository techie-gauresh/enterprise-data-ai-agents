# Week 1, Day 1, Hour 1: Enterprise AI Foundations — Structured Outputs, Guardrails & Multi-Model Routing

**Target Role:** Enterprise AI Architect (Agentic AI, NL-to-SQL, Data Quality & Governance)  
**Repository:** `enterprise-data-ai-agents`  
**Files Built Today:** `src/schemas.py`, `src/model_router.py`, `src/llm_client.py`, `tests/test_schemas.py`

---

## 1. What We Learned & Built Today (Hands-On Summary)

### A. Java/Spring to Modern Python AI Mental Model
| Java / Spring Ecosystem | Modern Python AI Equivalent | Role in Today's Build |
| :--- | :--- | :--- |
| Maven / Gradle + JDK | `python3 -m venv .venv` + `pip` | Per-project isolated dependency environment |
| Java `record` + Jackson + `@Valid` | **Pydantic v2 (`BaseModel`)** | Runtime validation + JSON Schema generation for LLMs |
| Resilience4j (Retry / Fallback) | `tenacity` (SDK) + Custom Fallback Chains | Handling transient `429` / `503` LLM API spikes |
| JUnit 5 | **`pytest`** | Automated deterministic testing of AI guardrails |
| Vendor-neutral Service Interface | Decoupled `schemas.py` + `llm_client.py` | Swapped AWS Bedrock -> Google Gemini with zero schema changes |

### B. Structured Outputs as a Contract (Not Prompt Hoping)
* Instead of asking an LLM to *"please respond in valid JSON"*, we passed `SQLQueryPlan` directly into the Gemini SDK (`response_mime_type="application/json"`, `response_schema=SQLQueryPlan`).
* Pydantic's `Field(description=...)` acts as part of the prompt—guiding the LLM on what to populate in each field (`reasoning`, `tables_used`, `sql_query`, `confidence`).
* Calling `SQLQueryPlan.model_validate_json(response.text)` guarantees both structural conformity and execution of custom Python validators.

### C. Deterministic Guardrails (`@field_validator`)
* Never rely solely on system prompts to prevent destructive SQL (`DROP`, `DELETE`, `UPDATE`, stacked queries).
* We implemented a deterministic Pydantic `@field_validator` and verified it with parameterized `pytest` unit tests (`4/4 passed`).
* **Architectural Limitation Identified:** Regex-based SQL validation is only a baseline—it can produce false positives on safe columns/literals (e.g., `deleted_at`, `'DELETE_TEST'`) and can be bypassed by PostgreSQL writable CTEs (`WITH x AS (DELETE ...) SELECT * FROM x`). We will upgrade this to `sqlglot` AST parsing in Hour 2.

### D. Dynamic Multi-Model Routing & Cross-Model Failover
* **Dynamic Routing (`src/model_router.py`):** Used the cheapest, fastest tier (`gemini-3.5-flash-lite`) as a semantic complexity classifier to route queries into three reasoning tiers:
  * `fast` -> `gemini-3.5-flash-lite` (simple lookups, single-table aggregations)
  * `balanced` -> `gemini-3.8-flash` (joins, grouping, date filters, window functions)
  * `deep` -> `gemini-4-hydrogen` (complex multi-CTE analytics, root-cause analysis)
* **Cascading Escalation:** If a lighter model returns `confidence == "low"` or violates a Pydantic guardrail, the client escalates to the `deep` tier.
* **Resilient Failover (`src/llm_client.py`):** Observed real-world `503 UNAVAILABLE` spikes on `gemini-3.8-flash` and `gemini-4-hydrogen`. Implemented ordered fallback chains for transient HTTP codes (`429`, `500`, `503`, `504`) while failing fast on client errors (`400`, `401`, `403`).

---

## 2. Core Theory & Architecture Concepts

1. **Constrained Decoding / Structured Outputs:**
   * Forces the model's token sampling to conform strictly to a JSON Schema grammar, eliminating malformed JSON parsing crashes in production pipelines.
2. **Defense-in-Depth for Enterprise NL-to-SQL:**
   * Layer 1: System Prompt instructions (soft guardrail).
   * Layer 2: Structured Output schema (structural guardrail).
   * Layer 3: Deterministic Python/AST validation (code guardrail).
   * Layer 4: Sandboxed read-only DB role + query timeout + row limit (infrastructure guardrail).
3. **LLM Routing vs. LLM Cascading:**
   * **Routing (Pre-execution):** Predicts task difficulty *before* running the main prompt to save cost and latency (e.g., sending 70% of routine queries to Flash-Lite).
   * **Cascading (Post-execution):** Starts cheap and escalates *only* when an automated quality check (confidence score, guardrail failure, or SQL execution error) fails.
4. **Provider Decoupling (Anti-Lock-In Architecture):**
   * Today's pivot from AWS Bedrock (`Error 002`) to Google Gemini proved why domain contracts (`schemas.py`), tests (`test_schemas.py`), and orchestration logic must remain independent of the underlying LLM SDK. In larger enterprises, this is further abstracted via an **AI Gateway** (e.g., LiteLLM, Portkey, or Cloud API Gateway).

---

## 3. AI Architect Interview Questions & Model Answers

### Q1: Why isn't prompt engineering enough to guarantee safe SQL in an enterprise NL-to-SQL system?
> **Strong Architect Answer:** Prompts are probabilistic, not deterministic. Prompt injection, complex edge cases, or model drift can still cause an LLM to emit DDL/DML statements or reference unauthorized tables. Production systems require **Defense-in-Depth**: constrained structured outputs (Pydantic), deterministic code-level validation (AST parsing via `sqlglot` rather than brittle regex), and database-level enforcement (least-privilege read-only credentials, RBAC, and execution timeouts).

### Q2: How do you optimize token cost and latency in a high-volume enterprise AI platform?
> **Strong Architect Answer:** By avoiding a "one-model-fits-all" design. I use **tiered model routing**—a lightweight, low-cost model (or classical classifier) categorizes request complexity and dispatches routine extraction/lookups to fast, cheap models (like Flash-Lite), reserving frontier reasoning models strictly for multi-step analytics or ambiguous queries. Pair this with **cascading escalation** (retry on a stronger model only on low confidence or validation failure), prompt caching, and semantic caching for repeated business questions.

### Q3: How do you handle LLM rate limits (`429`) and model overload (`503`) in production?
> **Strong Architect Answer:** First, differentiate transient errors (`429`, `500`, `503`, `504`) from permanent client errors (`400`, `401`, `403`) so you fail fast on bugs/auth issues. For transient failures, combine exponential backoff with jitter (e.g., `tenacity`), concurrency caps (`asyncio.Semaphore`), and **cross-model or cross-region fallback chains**—automatically failing over from an overloaded tier to an available backup model while logging telemetry (fallback rate, latency, and token spend) for observability.

### Q4: What is the trade-off of using an LLM-as-a-Router?
> **Strong Architect Answer:** Using an LLM as a router adds one extra network hop (latency) and small token overhead on every request. It pays off when the downstream task has high variance in complexity and expensive output tokens (like multi-CTE SQL or code generation). For ultra-low-latency workloads, you can replace the LLM router with a lightweight embedding/semantic router or a fine-tuned encoder classifier (e.g., DeBERTa) running locally in milliseconds.

### Q5: How do you design an AI system to avoid vendor lock-in across AWS Bedrock, GCP Vertex AI, and OpenAI?
> **Strong Architect Answer:** Keep domain models (Pydantic schemas), guardrails, evaluation suites, and business workflows completely decoupled from vendor SDKs behind a thin provider adapter or an enterprise AI Gateway (like LiteLLM). Standardize on open protocols—such as **MCP (Model Context Protocol)** for tool integrations and **OpenTelemetry** for tracing—so swapping models is a configuration change rather than a rewrite.

---

## 4. Official Documentation & Theory References

* **Python Virtual Environments (`venv`):** [docs.python.org/3/library/venv.html](https://docs.python.org/3/library/venv.html)
* **Pydantic v2 Documentation (Models, Validators, JSON Schema):** [docs.pydantic.dev](https://docs.pydantic.dev/latest/)
* **pytest Documentation (Parametrize & Fixtures):** [docs.pytest.org](https://docs.pytest.org/)
* **Google GenAI Python SDK & Structured Outputs:** [ai.google.dev/gemini-api/docs/structured-output](https://ai.google.dev/gemini-api/docs/structured-output)
* **Gemini API Rate Limits & Quotas Dashboard:** [aistudio.google.com/rate-limit](https://aistudio.google.com/rate-limit)

---

## 5. Recommended Courses & Learning Material

### Udemy Courses (Aligned to This 4-Week Roadmap)
1. **AI FDE: The Forward Deployed Engineer & Agentic AI Architect (Ed Donner)** — Covers Agent Harness Engineering, LangGraph, MCP, AWS AgentCore, and Evals.
2. **LangChain & LangGraph AI Engineer: Agents, Agentic RAG & MCP (Eden Marco)** — Deep hands-on Python track for stateful agent graphs, Agentic RAG, and MCP.
3. **AI Engineer Production Track: Deploy LLMs & Agents at Scale (Ed Donner / Ligency)** — Production deployment across AWS Bedrock, SageMaker, GCP Vertex AI, and Azure with MLOps & observability.
4. **FastAPI – The Complete Course (Eric Roby & Chad Darby)** — Structured refresher for Python virtual environments, Pydantic validation, async REST APIs, and `pytest`.

### Video References for Hour 1 Topics
* **Pydantic v2 Deep Dive:** [Pydantic V2 Full Course - Data Validation and Parsing](https://www.youtube.com/watch?v=7aBRk_JP-qY)
* **Gemini Structured Outputs in Python:** [Structured Responses with Gemini AI and Python](https://www.youtube.com/watch?v=iZqK0Z2kqWs)
* **Google AI Pro $10/mo API Credits Setup:** [How to Use Your Free $10 Google AI Pro API Credits](https://www.youtube.com/watch?v=VmtSm9VjIPU)

---

## 6. Key Takeaways & Next Step (Hour 2 Preview)

* **Takeaway:** Production AI engineering is 80% distributed systems rigor (contracts, validation, resilience, observability) and 20% LLM prompting.
* **Next (Week 1, Day 1, Hour 2):**
  1. Replace regex SQL validation in `src/schemas.py` with **`sqlglot` AST parsing** (blocking writable CTEs and hallucinated tables while laying the foundation for Automated Data Lineage).
  2. Introduce **`AsyncIO` + `asyncio.Semaphore`** in `src/async_client.py` to execute LLM queries concurrently without tripping rate limits.