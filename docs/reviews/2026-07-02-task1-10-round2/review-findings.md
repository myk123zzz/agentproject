# Review Findings: PolicyMind TASK 1-10 Round 2

## Requirements
- Review the current `main` branch in `D:\project` after the first remediation wave.
- Compare implementation against:
  - `docs/policymind/2026-07-01-policymind-design.md`
  - `docs/policymind/DEVELOPMENT_GUIDE.md`
  - `docs/policymind/2026-07-01-policymind-implementation.md`
  - `docs/reviews/2026-07-02-task1-10/remediation-plan.md`
- Verify code, tests, runtime behavior, and remaining acceptance gaps.
- Produce a second-round report with severity and exact file references.

## Research Findings
- Repository HEAD is `3464c55` (`fix: deliver secure api web workflows and production delivery`), following earlier remediation commits `4229a3f`, `e00c4fb`, and `4ac0181`.
- The configuration namespace bug from round 1 is fixed: `Settings` now uses `env_prefix="POLICYMIND_"` (`backend/src/policymind/core/config.py:8-15`), and backend tests no longer fail under ambient host `DEBUG`.
- Anonymous access to protected APIs is also fixed at the HTTP boundary: direct TestClient probes against `/api/v1/auth/me`, `/api/v1/documents/`, `/api/v1/chat`, `/api/v1/graph/subgraph`, `/api/v1/reviews/1`, and `/api/v1/evaluations/runs/r1` all returned `401`.
- However, `create_app(settings=...)` does not override the dependency-injected `get_settings()` instance. The app factory uses the passed `settings` only for startup and route registration (`backend/src/policymind/main.py:24-50`), while `get_current_context` still resolves `Settings` through `Depends(get_settings)` (`backend/src/policymind/api/dependencies.py:34-37`). In direct probing, an access token minted from the same `settings` object used to create the app was rejected with `401`, proving the runtime auth path is not reliably driven by the caller-supplied config.
- `get_current_context` still does not query the database or validate `is_active` / `token_version`; it trusts token claims for `tenant_id`, `role`, and `access_level` after signature verification (`backend/src/policymind/api/dependencies.py:44-72`). This leaves the first-round R1 requirement incomplete.
- `/api/v1/auth/me` now depends on `get_current_context`, but still synthesizes `username` as `user-{ctx.user_id}` rather than loading canonical user info (`backend/src/policymind/auth/router.py:37-48`).
- The document service remains a stub. `DocumentService.create_version()` computes a hash and random key, but does not persist document versions, deduplicate by `(tenant, document, hash)`, or store objects (`backend/src/policymind/documents/service.py:22-43`).
- The ingestion pipeline is still simulated: it uses fixed markdown bytes, fixed tenant/document IDs, a random storage key, no persisted stage state, and no real graph indexing (`backend/src/policymind/documents/pipeline.py:90-149`).
- The public document API is still synthetic. It accepts a generic JSON payload instead of multipart upload, returns a generated `job_id`, lists no documents, and always reports `queued` job status (`backend/src/policymind/api/v1/documents.py:13-41`).
- The Redis/ARQ queue adapter still is not implemented. Production `JobQueue.enqueue()` raises `NotImplementedError`, while `InlineJobRunner.enqueue()` returns a placeholder ID without invoking any job function (`backend/src/policymind/infrastructure/redis/jobs.py:8-30`).
- Retrieval still uses a memory-only adapter rather than a real Milvus client. The file named as the production Milvus adapter exports only `MemoryVectorStore` (`backend/src/policymind/infrastructure/milvus/store.py:1-91`).
- Retrieval still swallows vector-store failures and returns an empty successful bundle (`backend/src/policymind/retrieval/service.py:48-68`) instead of surfacing a dependency-unavailable error as required by the development guide.
- There is still no production Neo4j adapter under `backend/src/policymind/infrastructure/neo4j/`; only `__init__.py` exists. Graph search is still one-hop substring matching inside `MemoryGraphRepository` (`backend/src/policymind/graph/repository.py:23-71`), so R4 remains unimplemented.
- MCP is still direct in-process import/call rather than stdio/HTTP transport. `EnterpriseMCPClient.call_tool()` imports Python functions directly from `policymind.mcp.tools` (`backend/src/policymind/mcp/client.py:70-114`), and there is still no MCP server module.
- HITL and LangGraph are still absent in practice. `ChatService` returns a stub answer or canned events (`backend/src/policymind/conversations/service.py:14-36`), while API chat routes do not even call `ChatService`; they emit fixed JSON/SSE responses directly (`backend/src/policymind/api/v1/chat.py:13-53`).
- Review, graph, and evaluation APIs remain placeholders that return fixed empty or synthetic data without persistence (`backend/src/policymind/api/v1/reviews.py:12-37`, `backend/src/policymind/api/v1/graph.py:12-33`, `backend/src/policymind/api/v1/evaluations.py:12-43`).
- The frontend remains mostly a shell. The router has no auth guard (`frontend/src/router/index.ts:1-39`); `ChatView` still only appends `"处理中..."` locally instead of calling the backend (`frontend/src/views/ChatView.vue:19-31`); document/graph/review/evaluation views are static headings plus one sentence (`frontend/src/views/DocumentsView.vue:1-6`, `frontend/src/views/GraphView.vue:1-6`, `frontend/src/views/ReviewsView.vue:1-6`, `frontend/src/views/EvaluationView.vue:1-6`).
- Frontend test coverage is still zero. `npm test -- --run` exits with “No test files found”.
- The evaluation dataset has grown from 3 to 20 rows, but still misses the documented minimum of 120 cases. The evaluation runner is still stubbed and fabricates per-case success metrics without invoking retrieval or agent code (`backend/src/policymind/evaluation/runner.py:39-66`).
- Deployment is still not production-complete. The full compose file still lacks MinIO and etcd for Milvus and wires only bare service containers (`deploy/compose.full.yml:1-72`).
- The backend dependency list still omits the production stack named by the docs: no LangGraph, LangChain, pymilvus, Neo4j driver, Redis client/ARQ, MCP package, OpenTelemetry, Prometheus client, or S3 SDK (`backend/pyproject.toml:13-39`).
- The backend quality gates are green (`ruff`, `mypy`, `pytest`), but `pytest -m integration -q` deselects all 66 tests and exits non-zero, so required adapter/integration coverage still does not exist.

## Technical Decisions

| Decision | Rationale |
|----------|-----------|
| Re-run executable gates even though unit tests were green | Round 2 needed to distinguish “green tests” from “real runtime completeness” |
| Add direct TestClient probes with a locally minted token | Needed to verify whether the repaired auth layer supports a positive path, not only anonymous rejection |
| Compare against remediation-plan tasks R1-R7, not only against round-1 findings | Some issues were partially fixed and needed a fresh acceptance judgment |

## TASK 1-10 Acceptance Matrix

| Task | Verdict | Evidence summary |
|------|---------|------------------|
| TASK 1 | Pass | Repo skeleton, liveness, namespaced settings, Ruff/mypy/pytest all pass reproducibly |
| TASK 2 | Partial | Anonymous auth bypass is fixed and login schema is tenant-scoped, but request auth still does not re-load user state from DB and app-level settings injection is inconsistent |
| TASK 3 | Partial | Parsers and validation exist, but version service, object storage persistence, true idempotency, OCR/VLM, and contract-sized chunking are still incomplete |
| TASK 4 | Fail | Upload/jobs/ingestion remain simulated; there is still no real upload-to-ready searchable path |
| TASK 5 | Fail | Retrieval helpers exist, but Milvus integration, production embeddings/rerank, parent-expansion closure, and failure semantics are still not real |
| TASK 6 | Fail | No Neo4j adapter, no 1-3 hop repository traversal, and no source-bound GraphRAG flow |
| TASK 7 | Fail | No MCP transport/server, no real LangGraph orchestration, and no HITL interrupt/resume persistence |
| TASK 8 | Partial | Protected routes now reject anonymous callers, but many APIs still return placeholders and auth context is still token-trusting rather than DB-backed |
| TASK 9 | Fail | Frontend builds, but actual chat/documents/graph/review/evaluation workflows and test coverage are still missing |
| TASK 10 | Fail | Dataset is only 20 cases, evaluator is stubbed, integration/frontend/deployment coverage is missing, and production dependencies remain absent |

## Severity Classification

### Critical
1. Positive-path authentication is not reliably wired: `create_app(settings=...)` and `Depends(get_settings)` can diverge, causing valid locally issued tokens to fail at runtime and making auth-sensitive tests/configuration unreliable (`backend/src/policymind/main.py:24-50`, `backend/src/policymind/api/dependencies.py:34-72`).
2. The claimed production ingestion/chat/agent stack is still largely non-executable: document upload, job execution, pipeline state, chat orchestration, MCP, and HITL all remain placeholder implementations (`backend/src/policymind/documents/service.py:22-43`, `backend/src/policymind/documents/pipeline.py:90-149`, `backend/src/policymind/api/v1/chat.py:13-53`, `backend/src/policymind/conversations/service.py:14-36`, `backend/src/policymind/mcp/client.py:70-114`).

### Important
1. Request authentication still trusts token claims for tenant/role/access rather than re-querying DB state and token version, so disabled users and stale authorization snapshots cannot be correctly enforced (`backend/src/policymind/api/dependencies.py:53-72`).
2. Retrieval, GraphRAG, and deployment adapters remain absent from both code and dependencies, so the documented production topology still cannot run (`backend/src/policymind/infrastructure/milvus/store.py:1-91`, `backend/src/policymind/graph/repository.py:23-71`, `backend/pyproject.toml:13-39`, `deploy/compose.full.yml:1-72`).
3. Evaluation remains non-representative: 20-case dataset, stubbed runner, no aggregate metric computation, and no integration/frontend test suite (`backend/src/policymind/evaluation/runner.py:39-66`, `evaluation/datasets/golden_v1.jsonl`).
4. Frontend workspace routes still present mostly static pages and local-only message appends; no auth guard or end-to-end evidence-bearing chat workflow exists (`frontend/src/router/index.ts:1-39`, `frontend/src/views/ChatView.vue:19-31`).

### Minor
1. `/auth/me` fabricates username text instead of returning canonical persisted user metadata (`backend/src/policymind/auth/router.py:41-48`).
2. Several modules still contain “In production...” comments that no longer reflect the claimed repository state, which makes completion status look more advanced than it is.

## Delta From Round 1
- **Fixed since round 1**
  - Namespaced settings now isolate host environment variables.
  - Anonymous requests to protected APIs are rejected with `401`.
  - `renderSafeMarkdown()` now sanitizes rendered HTML.
  - Frontend SSE parser now pairs `event:` and `data:` lines more sanely and checks `response.ok`.
  - Backend unit-test count increased from 55 to 66 and all pass.
- **Still unresolved from round 1**
  - DB-backed auth context and token-version enforcement.
  - Real document upload/job/pipeline persistence.
  - Real Milvus/Neo4j/MCP/LangGraph integrations.
  - Frontend real workflows and frontend tests.
  - Evaluation scale and realism.
- **Newly confirmed in round 2**
  - App factory settings and dependency-injected settings are not unified, which breaks positive-path auth verification.

## Resources
- `docs/policymind/2026-07-01-policymind-implementation.md`
- `docs/policymind/DEVELOPMENT_GUIDE.md`
- `docs/policymind/2026-07-01-policymind-design.md`
- `docs/reviews/2026-07-02-task1-10/remediation-plan.md`
