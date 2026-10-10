# Enterprise-Grade Secure RAG Engine

A production-grade, multi-tenant Retrieval-Augmented Generation (RAG) backend built with FastAPI, Qdrant, SQLAlchemy, and Sentence Transformers. Designed to solve core enterprise challenges: zero data leakage via security-first metadata pre-filtering, API cost reduction via role-aware semantic caching, and intelligent compute allocation through cost-aware model routing.

---

## Architecture & Key Pillars

1. **Role-Based Access Control (RBAC) Pre-Filtering**
   - Implemented at the vector database level using Qdrant payload filters. 
   - Ensures that unauthorized documents are filtered *before* retrieval, achieving zero data leakage by design.

2. **Role-Aware Semantic Caching**
   - Computes cosine similarity thresholds (`0.85+`) via Sentence Transformers (`all-MiniLM-L6-v2`) on incoming queries.
   - Strictly enforces user-role separation in cache lookups to prevent cross-tenant data exposure while saving 100% on LLM inference costs for repetitive queries.

3. **Cost-Aware Model Router**
   - Dynamically analyzes query complexity and intent to route low-complexity or administrative queries to fast local models (e.g., Llama-3-8B) and deep analytical queries to advanced enterprise models (e.g., GPT-4 / Claude-3.5).

4. **Immutable Audit Logging**
   - Automatically records every access attempt, role validation, cache hit/miss status, and security block into an SQLite audit trail for compliance tracking.

---

## Tech Stack
- **Backend:** FastAPI, Pydantic, Uvicorn
- **Database & ORM:** SQLite / PostgreSQL, SQLAlchemy (Audit Logs & User Management)
- **Vector Database:** Qdrant (Local Persistent Storage)
- **Embeddings & Similarity:** HuggingFace Sentence Transformers (`all-MiniLM-L6-v2`)

---

## Project Structure
```text
enterprise-rag-engine/
│
├── api/                  # API routers & endpoint definitions
├── core/
│   ├── security.py       # Qdrant RBAC metadata pre-filtering
│   └── router_cache.py   # Semantic cache & cost-aware model router
├── database/
│   └── models.py         # SQLAlchemy User & AuditLog schemas
├── ingestion/
│   └── ingest.py         # Document chunking & security metadata tagging
├── main.py               # FastAPI application entrypoint
└── requirements.txt      # Project dependencies