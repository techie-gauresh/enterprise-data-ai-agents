# AI Architect Learning & Interview Prep Index

**Repository:** `enterprise-data-ai-agents`  
**Target Role:** Enterprise AI Architect (Agentic AI, NL-to-SQL, Data Quality & Governance)  
**Prep Track:** 4-Week Intensive Hands-On & System Design Roadmap

---

## Learning Logs by Week

### Week 1: Python for AI Systems, Guardrails & Advanced RAG
| Session | Topic | Key Files Built | Status | Learning Log |
| :--- | :--- | :--- | :--- | :--- |
| **W1 · D1 · H1** | Structured Outputs (Pydantic v2), Deterministic Guardrails, Dynamic Multi-Model Routing & 503 Failover | `src/schemas.py`, `src/model_router.py`, `src/llm_client.py`, `tests/test_schemas.py` | Completed | [Week 1, Day 1, Hour 1](./week1_day1_hour1_learning.md) |
| **W1 · D1 · H2** | `sqlglot` AST Guardrails & `AsyncIO` + `Semaphore` Concurrency | `src/schemas.py`, `src/async_client.py`, `tests/test_schemas.py` | Up Next | `week1_day1_hour2_learning.md` *(pending)* |
| **W1 · D1 · H3** | Hybrid RAG & Schema Indexing (`pgvector` / `Qdrant` + Reranking) | *TBD* | Planned | `week1_day1_hour3_learning.md` *(pending)* |
| **W1 · D2** | RAG Evaluation Frameworks (RAGAS / DeepEval) & Knowledge Graph RAG | *TBD* | Planned | *Pending* |

### Week 2: LangGraph & Project #1 — Enterprise NL-to-SQL Agent
| Session | Topic | Key Files Built | Status | Learning Log |
| :--- | :--- | :--- | :--- | :--- |
| **W2 · D1–D2** | Stateful Agent Graphs in LangGraph, Cycles & Critic Loops | *TBD* | Planned | *Pending* |
| **W2 · D3–D4** | Database Sandbox Execution, Error Self-Correction & MCP Tool Server | *TBD* | Planned | *Pending* |

### Week 3: Multi-Agent Systems & Project #2 — Self-Healing ETL + Data Lineage
| Session | Topic | Key Files Built | Status | Learning Log |
| :--- | :--- | :--- | :--- | :--- |
| **W3 · D1–D2** | Automated Column-Level Data Lineage (AST + LLM + OpenLineage) | *TBD* | Planned | *Pending* |
| **W3 · D3–D4** | Self-Healing ETL Pipeline Agent, Schema Drift & Human-in-the-Loop (`interrupt()`) | *TBD* | Planned | *Pending* |
| **W3 · D5** | AI Observability & Tracing (LangSmith / Arize Phoenix / MLflow) | *TBD* | Planned | *Pending* |

### Week 4: Classical ML/NLP Literacy & Mock Architecture Drills
| Session | Topic | Key Files Built | Status | Learning Log |
| :--- | :--- | :--- | :--- | :--- |
| **W4 · D1–D2** | Classical ML & NLP for Data Observability (XGBoost, Time-Series Anomaly Detection, NER/PII) | *TBD* | Planned | *Pending* |
| **W4 · D3–D4** | Enterprise System Design Whiteboarding (5 Core Use Cases) & Story Pitch | *TBD* | Planned | *Pending* |

---

## Quick Interview Topic Lookup

Use these direct anchors to revise specific architecture patterns before an interview:

* **Defense-in-Depth for NL-to-SQL Guardrails** -> [W1 D1 H1 — Theory & Q1](./week1_day1_hour1_learning.md#2-core-theory--architecture-concepts)
* **Dynamic Multi-Model Routing & Cascading Escalation** -> [W1 D1 H1 — Q2 & Q4](./week1_day1_hour1_learning.md#3-ai-architect-interview-questions--model-answers)
* **Handling LLM `429` Rate Limits & `503` Failover** -> [W1 D1 H1 — Q3](./week1_day1_hour1_learning.md#3-ai-architect-interview-questions--model-answers)
* **Multi-Cloud / Provider Decoupling & AI Gateways** -> [W1 D1 H1 — Q5](./week1_day1_hour1_learning.md#3-ai-architect-interview-questions--model-answers)

---

## Maintenance Workflow (Per Hour)

1. Complete the hands-on code and verify all `pytest` checks pass.
2. Save the session's learning log as `docs/week<W>_day<D>_hour<H>_learning.md`.
3. Update the table and **Quick Interview Topic Lookup** in this `docs/INDEX.md`.
4. Commit code + tests + docs together in a single clean commit.