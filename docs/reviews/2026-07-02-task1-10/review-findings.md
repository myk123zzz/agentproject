# Review Findings: PolicyMind TASK 1-10

## Requirements
- Review completed TASK 1-10 in `D:\project`.
- Compare implementation with the implementation plan and detailed development guide.
- Verify code, tests, security boundaries, and real integration paths.
- Report issues with severity and exact file/line references.

## Research Findings
- Repository HEAD is `5fe45d5`; TASK commits run from `5690b49` through `a8df14c`, followed by `5fe45d5`.
- `frontend/package-lock.json` is untracked and must not be overwritten or included in review commits.
- Review planning files are temporary working-memory artifacts and are not business-code changes.
- The implementation plan contains exactly ten task sections, from project gates through deployment/evaluation.
- Commit mapping is coarse-grained: TASK 1 (`5690b49`), TASK 2/3 order is reversed in history (`a91cb0e` then `4f42a5f`), TASK 4 (`0ca1b4a`), TASK 5 (`3141e0d`), TASK 6 (`1feb968`), TASK 7 (`04b2ba4`), and TASK 8-10 combined in `a8df14c`.
- TASK 8-10 being combined into one release commit is not itself a defect, but it increases the need to verify each acceptance item independently.
- Authentication is not wired: `/auth/me` returns a fixed user (`auth/router.py:45-56`) and `get_current_context` accepts any supplied bearer token as tenant 1/user 1 without decoding or querying status (`api/dependencies.py:26-39`).
- Login lookup is username-only (`auth/service.py:85-88`) despite the required `(tenant_id, username)` identity boundary; the request schema needs inspection to see how tenant selection was intended.
- Readiness checks only the default JWT condition and does not probe PostgreSQL, Redis, Milvus, Neo4j, object storage, MCP, or model dependencies (`main.py:59-63`).
- TASK 4 is still a simulated pipeline: it hard-codes test bytes, tenant/document IDs and dates, does not persist stage state, performs no graph upsert, and production jobs construct it with five `None` adapters (`documents/pipeline.py:90-149`, `documents/jobs.py:4-20`).
- Document API accepts a generic JSON dictionary, queues nothing, persists nothing, exposes no authentication, and always reports synthetic queued state (`documents/router.py:11-31`).
- Production job queue is an abstract object whose `enqueue` raises `NotImplementedError`; the inline runner does not execute the requested function (`infrastructure/redis/jobs.py:8-30`).
- There is no production embedding provider or reranker; only fixed-vector/pass-through testing classes exist (`retrieval/embeddings.py:16-26`, `retrieval/rerank.py:19-28`).
- The file named as the Milvus adapter contains only `MemoryVectorStore`; it never imports or connects to Milvus and its dense scores are synthetic (`infrastructure/milvus/store.py:1-83`).
- `MemoryVectorStore.delete_document_version` ignores `version_id` and deletes every chunk for the tenant (`infrastructure/milvus/store.py:85-91`), a data-loss bug if used beyond tests.
- Retrieval catches any store failure and returns an empty successful bundle (`retrieval/service.py:49-68`), which can make downstream agents answer without evidence instead of surfacing the required unavailable condition.
- Citation objects omit bbox because `SearchHit` has no bbox field and `build_citations` never sets it (`retrieval/ports.py:6-27`, `retrieval/citations.py:8-23`).
- GraphRAG has no Neo4j adapter at all. Extraction always returns empty entities/relations, the repository is memory-only, and path search implements one-hop substring matching despite the required 1-3 hop traversal (`graph/extraction.py:85-92`, `graph/repository.py:23-71`).
- Graph extraction defaults every object to tenant 1 and permits missing source version (`graph/extraction.py:12-31`), so source binding is not mandatory as required.
- The path ranker claims to include version in its score but only computes confidence, query substring matching, and path length (`graph/path_ranker.py:6-42`).
- MCP is direct Python import/call rather than a real transport (`mcp/client.py:24-104`); tools return hard-coded dictionaries and the write tool creates no persisted review ticket (`mcp/tools.py:7-140`).
- `create_review_ticket` is executed before merely labelling its result as requiring approval (`mcp/client.py:92-104`); there is no approval token, argument hash, idempotency key, policy module, or pre-execution block.
- No LangGraph graph is built. Agent modules contain disconnected rule functions and fixed observations; `ChatService` returns/streams canned responses and `resume` does not call `Command(resume=...)` (`agents/*.py`, `conversations/service.py:7-36`).
- Planned PostgreSQL checkpointer, conversation router, graph topology module, JSON parser, prompts, MCP server and policy modules are absent.
- API endpoints are unauthenticated and mostly return fixed/empty data. Chat streaming does not invoke `ChatService`; graph accepts caller-provided `tenant_id=1`; review approve/reject changes no state (`api/v1/chat.py:11-40`, `api/v1/graph.py:10-26`, `api/v1/reviews.py:10-27`).
- The frontend is a static shell: sending a chat only appends “处理中...”, document/graph/review/evaluation pages are six-line placeholders, and no login/settings view or route guard exists (`frontend/src/views/*.vue`, `frontend/src/router/index.ts:3-34`).
- `renderSafeMarkdown` returns raw source despite marked/DOMPurify dependencies, leaving the promised XSS boundary unimplemented (`frontend/src/api/client.ts:48-50`).
- SSE parsing emits the event name and data as separate callbacks rather than pairing them, and blindly `JSON.parse`s each data line without checking HTTP status/content type (`frontend/src/api/client.ts:9-45`).
- Evaluation has only 3 cases rather than at least 120; its runner fabricates perfect scores without invoking retrieval/agent code, aggregate metrics are never computed, and API reports are placeholders (`evaluation/datasets/golden_v1.jsonl`, `evaluation/runner.py:39-66`, `api/v1/evaluations.py:10-29`).
- Telemetry is explicitly a no-op and the custom integer counters are not Prometheus metrics (`core/telemetry.py:6-31`).
- The full compose runs standalone Milvus without etcd/MinIO configuration while the infrastructure compose includes them; it also lacks MinIO in the full stack, so the declared full deployment is internally inconsistent (`deploy/compose.full.yml:42-58`, `deploy/compose.infrastructure.yml:19-45`).
- The backend dependency list does not include LangChain, LangGraph, Milvus SDK, Neo4j driver, ARQ, Redis client, MCP, OpenTelemetry, Prometheus, Ragas, boto/S3, OCR, or an LLM SDK (`backend/pyproject.toml:13-29`), so the named production stack cannot run.
- There are 55 backend tests but zero frontend tests. There are no API, evaluation, E2E, integration, adapter contract, disabled-user-token, cross-tenant, real upload-to-search, MCP transport, LangGraph interrupt/resume, or deployment tests.
- Auth tests cover settings/password/JWT primitives only; they do not exercise `get_current_context`, `/auth/me`, disabled-user token reuse, tenant-safe login, refresh rotation/revocation, or role checks (`backend/tests/auth/test_auth.py`).
- `LoginRequest` has no tenant slug/id while usernames are tenant-scoped (`auth/schemas.py:6-8`), and `AuthService` searches globally by username, making duplicate usernames across tenants produce `MultipleResultsFound` or ambiguous authentication.
- TASK 3 is partial: there is no `S3ObjectStorage`, OCR protocol, VLM protocol, or legacy XLS/image parser. Several extensions are declared allowed but have no MIME mapping/parser.
- Hierarchical chunking does not enforce the documented sizes: parents are always the entire source block and may exceed 1600 chars; leaves can be below the declared minimum; constants say parent minimum 800/leaf minimum 200 instead of 1000/300 (`documents/chunking.py:7-11,55-100`).
- PDF bbox provenance is the entire page for every paragraph, not the paragraph bounding box (`documents/parsers/pdf_parser.py:18-35`), reducing citation localization quality.
- The “idempotency” pipeline tests only rerun an in-memory simulation; the implementation creates a fresh random storage key and appends duplicate chunks every time, so it is not idempotent (`documents/pipeline.py:90-149`).
- Docker images cannot build as written: each build context is already `backend` or `frontend`, but Dockerfiles `COPY ../backend/...` / `COPY ../frontend/...`, which reference files outside the build context. The worker also invokes `arq` although ARQ is not installed, and the MCP image targets an absent `policymind.mcp.server` module.
- Executable backend gates with the available Python 3.13 interpreter: Ruff passes; strict mypy passes for 73 source files; pytest fails 10/55 tests (45 passed) with total coverage 31%.
- All 10 pytest failures are caused by ambient environment variable `DEBUG=release` being parsed as the app's boolean `DEBUG`. Settings use generic, unprefixed environment names (`core/config.py:11-30`), so unrelated host variables can prevent app/test startup. This is both a reproducibility and deployment-safety defect.
- Coverage confirms critical production paths are untested: auth service/router/models, all API routes, conversations, telemetry, evaluation, Milvus adapter, MCP client, Redis jobs, document jobs/parsers/ORM, and most graph code are at 0%.
- With `DEBUG=false` explicitly controlled, all 55 backend unit tests pass and coverage rises to 44%; this isolates the previous failures to configuration namespace pollution rather than those unit assertions.
- `pytest -m integration` selects zero tests and exits 5, confirming the required production-adapter integration suite does not exist.
- Frontend typecheck and production build pass, but `npm test -- --run` fails because no test files exist. Thus TASK 9's five required frontend behavior/security test areas are absent.
- Direct TestClient probes reproduce the authorization failures: anonymous `/auth/me` returns the fixed tenant-1 user; a syntactically invalid bearer token returns the same 200; anonymous document creation returns 200/accepted; caller-selected `tenant_id=999` graph access returns 200; readiness returns 200 without external dependencies.
- The evaluation CLI exits successfully after “evaluating” exactly 3 fabricated cases, demonstrating that a green script exit is not evidence of the required 120-case or real-agent evaluation.
- Systematic root-cause result for the initial pytest failures: source is the host's `DEBUG=release`; unprefixed `BaseSettings` consumes it for a boolean field. Minimal one-variable test (`DEBUG=false`) changes the result from 10 failures to 55 passes. Recommended repair belongs at the configuration boundary (namespaced environment variables), not in individual tests.

## Technical Decisions
| Decision | Rationale |
|----------|-----------|
| Use static tracing plus executable gates | Either method alone can miss fake wiring or runtime breakage |
| Check task commits and current tree | Current behavior matters, while commit boundaries help map TASK 1-10 |

## TASK 1-10 Acceptance Matrix
| Task | Verdict | Evidence summary |
|------|---------|------------------|
| TASK 1 | Partial | Skeleton, liveness, Ruff and mypy exist; tests pass only after neutralizing ambient `DEBUG`, so the gate is not reproducible as-is |
| TASK 2 | Fail | Models/JWT primitives exist, but request authentication and tenant/user revalidation are placeholders; tenant-safe login and revocation flows are unverified |
| TASK 3 | Partial | Basic parsers, validation, local storage and chunking exist; S3/OCR/VLM/version service/idempotency and documented chunk sizing are missing |
| TASK 4 | Fail | Upload, jobs, state persistence and ingestion are simulated; no upload-to-search vertical path |
| TASK 5 | Fail | RRF/citation helpers exist, but no Milvus, real embedding/rerank, adapter contract tests, parent expansion wiring, or complete provenance |
| TASK 6 | Fail | No Neo4j adapter; extraction is empty; only memory one-hop graph behavior exists |
| TASK 7 | Fail | No MCP transport/server, LangGraph graph, PostgreSQL checkpointer, interrupt/resume, approval token or real tool execution policy |
| TASK 8 | Fail | APIs are mostly anonymous fixed responses; security, schemas, rate limiting, readiness and cross-tenant checks are absent |
| TASK 9 | Fail | Static Vue shell compiles, but no real workflows, auth guard, SSE integration, safe Markdown, settings page, or frontend tests |
| TASK 10 | Fail | 3/120 golden cases, fake evaluator, no telemetry, no integration/E2E tests, and broken deployment definitions |

## Severity Classification

### Critical
1. Authentication/authorization bypass across `/auth/me`, documents, graph, chat, reviews and evaluation APIs.
2. Claimed production ingestion/retrieval/GraphRAG/Agent/MCP/HITL paths are not executable; most return synthetic results.
3. MCP write operation is executed before approval is checked, defeating the HITL safety boundary.

### Important
1. Production dependencies and adapters are absent from code and `pyproject.toml`.
2. Docker build contexts/commands are invalid and the full compose topology is incomplete.
3. Evaluation fabricates success, dataset size is 3, telemetry is a no-op, and required integration/E2E/frontend tests do not exist.
4. Configuration consumes generic host environment variables, making startup and test gates non-reproducible.
5. Version/provenance/chunking semantics diverge from the development contract.

### Minor
1. TASK 8-10 were bundled into one commit instead of independently reviewable task commits.
2. Several comments/docstrings state “production” behavior that is not implemented, which makes completion status harder to judge.

## Issues Encountered
| Issue | Resolution |
|-------|------------|
| `uv` is absent and the first PowerShell gate wrapper displayed stale zero exit codes | Discarded those results; use interpreter/module discovery and explicit process exit codes |
| Ambient `DEBUG=release` causes 10 test startup failures | Reproduced consistently and isolated with `DEBUG=false`; root cause is unprefixed settings namespace |

## Resources
- `docs/policymind/2026-07-01-policymind-implementation.md`
- `docs/policymind/DEVELOPMENT_GUIDE.md`
- `docs/policymind/2026-07-01-policymind-design.md`
