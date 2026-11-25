# Enterprise Data AI Agents

Production-oriented reference architecture for **Enterprise NL-to-SQL**, **Deterministic SQL Guardrails**, and **Automated Data Lineage** built with vendor-agnostic Python design patterns.

## Architecture Overview

```text
User Query + Schema Context
         │
         ▼
┌─────────────────────┐
│  Complexity Router  │  (Classifies into FAST / BALANCED / DEEP tier)
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│   SQLAgentService   │  (Depends only on LLMProvider Protocol)
│  - Fallback Chains  │  ──► Auto-failover on HTTP 429/500/503/504
│  - Confidence Check │  ──► Escalates low-confidence plans to DEEP tier
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Pydantic v2 Schema │  (Strict JSON contract + Read-Only SQL Guardrails)
└─────────────────────┘