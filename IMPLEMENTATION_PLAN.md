# Implementation Plan: AI-Powered University Student Services Assistant

## Phase 1: Planning (Current)
- Understand the 33-point requirements.
- Produce this plan.

## Phase 2: Project Structure & Configuration
- Create `app/` directory and its subdirectories (`api`, `schemas`, `graph`, `services`, `interfaces`, `core`, `tests`).
- Create `.env.example` with required config variables (Ollama, Mock flags).
- Create `app/core/config.py` for settings management.

## Phase 3: Pydantic Schemas & API Endpoints
- Implement schemas for `/ask`, `/ingest`, `/health`, `/sources`, `/audit/{trace_id}`.
- Implement the FastAPI application with routers for these endpoints in `app/api/`.
- Ensure endpoints conform to the required JSON schemas and headers (e.g., `X-Student-Id`).

## Phase 4: LangGraph State & Workflow
- Define the state using TypedDict/Pydantic in `app/graph/state.py`.
- Define nodes for routing, RAG retrieval, Tool execution, and answer synthesis.
- Construct the StateGraph in `app/graph/graph.py`.

## Phase 5: Routing Logic
- Implement deterministic and LLM-assisted routing in `app/graph/routing.py`.
- Support route decisions: `RAG`, `TOOL`, `RAG + TOOL`, `CLARIFICATION`, `REFUSAL`.

## Phase 6: Service Interfaces & Mocks
- Define interfaces for `RAGService`, `ToolRegistry`, `StudentRepository`, `IngestionService`, `SourceRegisterService` in `app/interfaces/`.
- Create mock implementations of these in `app/services/` that can be toggled via config.

## Phase 7: Audit & Trace System
- Implement `AuditService` to store and retrieve trace data.
- Ensure every `/ask` request generates a `trace_id` and logs the workflow steps without leaking sensitive chain-of-thought or cross-student data.

## Phase 8: Ollama Integration
- Create `LLMService` wrapper around Ollama (using LangChain or direct API).
- Implement `MOCK_LLM` flag for offline testing.

## Phase 9: Testing
- Write comprehensive `pytest` tests in `tests/` covering endpoints and routing behavior.

## Phase 10: Execution & Final Polish
- Ensure `uvicorn app.main:app --reload` runs cleanly.
- Verify Swagger UI at `/docs`.
- Generate `IMPLEMENTATION_NOTES.md` outlining final architecture.
