# Enterprise Data AI Agents

A production-oriented Python repository implementing **Agentic AI architectures for enterprise data platforms**—covering Natural Language to SQL (NL-to-SQL), Automated Data Lineage, Self-Healing ETL Pipelines, and Intelligent Data Observability.

Built with a focus on **distributed systems rigor**: strict schema contracts, deterministic guardrails, dynamic multi-model routing, resilient failover, and automated testing.

---

## Architecture Overview (Current Baseline)

```text
User Question
      │
      ▼
┌──────────────────────────────────────────────┐
│  Dynamic Semantic Router (src/model_router)  │
│  Classifies complexity via Flash-Lite into:  │
│    • fast     -> gemini-3.5-flash-lite       │
│    • balanced -> gemini-3.8-flash            │
│    • deep     -> gemini-4-hydrogen           │
└─────────────────────┬────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────┐
│ Resilient Execution Client (src/llm_client)  │
│  • Constrained JSON Structured Outputs       │
│  • Cross-Model Failover (HTTP 429/500/503)   │
│  • Confidence & Guardrail Escalation         │
└─────────────────────┬────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────┐
│  Deterministic Guardrails (src/schemas.py)   │
│  • Pydantic v2 SQLQueryPlan contract         │
│  • Blocks DDL/DML & stacked SQL statements   │
└─────────────────────┬────────────────────────┘
                      │
                      ▼
        Validated Read-Only SQLQueryPlan
```

---

## Implemented Features

* **Constrained Structured Outputs (`src/schemas.py`):** Enforces a strict `SQLQueryPlan` Pydantic v2 contract (`reasoning`, `tables_used`, `sql_query`, `confidence`) directly via Gemini's native `response_schema`.
* **Deterministic SQL Guardrails (`src/schemas.py` & `tests/test_schemas.py`):** Blocks destructive SQL (`DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`, `TRUNCATE`) and stacked multi-statement queries in Python code, backed by parameterized `pytest` unit tests.
* **Dynamic Multi-Model Routing (`src/model_router.py`):** Uses a fast, low-cost tier (`gemini-3.5-flash-lite`) to classify query reasoning complexity and route requests to the most cost-effective model tier.
* **Cross-Model Failover & Cascading (`src/llm_client.py`):** Automatically fails over across ordered model chains on transient API errors (`429`, `500`, `503`, `504`), fails fast on client errors (`400`, `401`, `403`), and escalates to the `deep` reasoning tier when a lighter model reports `confidence="low"` or fails validation.

---

## Project Structure

```text
enterprise-data-ai-agents/
├── docs/
│   ├── INDEX.md                        # Roadmap & interview prep lookup index
│   └── week1_day1_hour1_learning.md    # Architecture notes, theory & Q&As
├── src/
│   ├── __init__.py
│   ├── schemas.py                      # Pydantic v2 contracts & SQL guardrails
│   ├── model_router.py                 # Semantic complexity router & tier mapping
│   └── llm_client.py                   # Resilient multi-model client & failover
├── tests/
│   ├── __init__.py
│   └── test_schemas.py                 # Deterministic guardrail unit tests
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Quickstart

### Prerequisites
* Python 3.11+
* A Google Gemini API key ([Google AI Studio](https://aistudio.google.com/apikey))

### 1. Clone & Set Up Virtual Environment
```bash
git clone https://github.com/techie-gauresh/enterprise-data-ai-agents.git
cd enterprise-data-ai-agents

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure API Key
```bash
export GEMINI_API_KEY="your-gemini-api-key"
```

### 3. Run Unit Tests & NL-to-SQL Demo
```bash
# Run deterministic guardrail tests
pytest -v

# Run dynamic multi-model routing & failover demo
python -m src.llm_client
```

---

## Roadmap

- [x] **Phase 1 — Foundations:** Pydantic v2 structured outputs, deterministic SQL guardrails, dynamic multi-model routing, and 503 failover.
- [ ] **Phase 2 — AST Guardrails & Concurrency:** Replace regex SQL checks with `sqlglot` AST parsing (blocking writable CTEs and hallucinated tables) and add `AsyncIO` + `Semaphore` batch execution.
- [ ] **Phase 3 — Hybrid RAG & Schema Linking:** Index enterprise table DDLs and business glossaries in a vector store (`pgvector` / `Qdrant`) with hybrid search and reranking.
- [ ] **Phase 4 — Stateful NL-to-SQL Agent (LangGraph + MCP):** Add sandboxed query execution, self-correcting error loops, and an MCP tool server.
- [ ] **Phase 5 — Automated Data Lineage & Self-Healing ETL:** Combine AST parsing with multi-agent orchestration, OpenLineage metadata emission, schema-drift remediation, and Human-in-the-Loop (`interrupt()`) approvals.

---

## Architecture Notes & Learning Index

Detailed session logs, design trade-offs, and AI Architect interview Q&As are maintained in **[`docs/INDEX.md`](./docs/INDEX.md)**.