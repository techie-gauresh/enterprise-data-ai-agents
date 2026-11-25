# Architecture Documentation Index

Engineering specifications and Architecture Decision Records (ADRs) for `enterprise-data-ai-agents`.

## Architecture Decision Records (ADRs)

| ID | Title | Status | Key Patterns |
| :--- | :--- | :--- | :--- |
| [ADR-001](adr/001-vendor-agnostic-routing-and-failover.md) | Vendor-Agnostic LLM Abstraction, Dynamic Routing & Failover | Accepted | Ports & Adapters (`Protocol`), Tiered Routing, 503 Failover, Pydantic v2 |
| ADR-002 | Deterministic SQL AST Guardrails & Bounded Async Concurrency | Planned | `sqlglot` AST Parsing, Writable-CTE Blocking, `AsyncIO` + `Semaphore` |
| ADR-003 | Hybrid Schema RAG & Vector Indexing | Planned | Metadata Embeddings, Hybrid Retrieval, Dynamic Context Injection |
| ADR-004 | Multi-Step Agentic Orchestration & Automated Data Lineage | Planned | State Graphs, Column-Level AST Lineage, Self-Healing Execution |
EOF