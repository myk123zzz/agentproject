# Review Progress Log: PolicyMind TASK 1-10 Round 2

## Session: 2026-07-02

### Phase 1: Establish review baseline
- **Status:** complete
- Actions taken:
  - Confirmed clean worktree on `main`.
  - Captured recent history through HEAD `3464c55`.
  - Mapped second-round scope against the first-round findings and remediation plan.

### Phase 2: Static implementation review
- **Status:** complete
- Actions taken:
  - Re-read core documentation in `docs/policymind/`.
  - Re-read first-round review artifacts in `docs/reviews/2026-07-02-task1-10/`.
  - Audited backend modules for auth, documents, retrieval, graph, MCP, conversations, evaluation, deployment and dependencies.
  - Audited frontend router, API client and all workspace views.

### Phase 3: Automated verification
- **Status:** complete
- Actions taken:
  - Ran backend Ruff, mypy and pytest.
  - Ran `pytest -m integration` to check adapter/integration coverage.
  - Ran frontend `typecheck`, `build`, and `npm test -- --run`.
  - Counted golden dataset rows.
  - Executed direct TestClient probes against protected APIs and health endpoints.

### Phase 4: Acceptance review
- **Status:** complete
- Actions taken:
  - Re-evaluated TASK 1-10 against the implementation plan and development guide.
  - Separated issues fixed since round 1 from issues still unresolved.
  - Recorded new round-2 issue around app settings injection versus dependency resolution.

## Test Results

| Test | Expected | Actual | Status |
|------|----------|--------|--------|
| `python -m ruff check src tests` | No lint errors | All checks passed | pass |
| `python -m mypy src` | No type errors | Success on 75 source files | pass |
| `python -m pytest -q` | Tests pass | 66 passed | pass |
| `python -m pytest -m integration -q` | Integration suite exists and runs | 66 deselected, exit 1 | fail |
| `npm run typecheck` | No TS errors | Passed | pass |
| `npm run build` | Production bundle builds | Passed | pass |
| `npm test -- --run` | Frontend tests exist and pass | No test files found, exit 1 | fail |
| Golden dataset size | At least 120 cases | 20 lines in `golden_v1.jsonl` | fail |
| TestClient protected API probe | Valid token can reach protected APIs | Anonymous 401 is correct, but locally issued access token also gets 401 | fail |

## Probe Notes

- `/health/ready` returned `200 {"status":"ok"}` without probing PostgreSQL, Redis, Milvus, Neo4j, object storage, MCP, or models.
- Protected routes now reject anonymous requests, which is an improvement over round 1.
- However, an access token issued from the same `Settings` object used to build the app still failed on `/api/v1/auth/me`, indicating `create_app(settings=...)` does not actually wire that settings object into dependency resolution.

## Commands Run

```powershell
git -C D:\project status --short --branch
git -C D:\project log --oneline --decorate --graph -n 20
python -m ruff check src tests
python -m mypy src
python -m pytest -q
python -m pytest -m integration -q
npm run typecheck
npm run build
npm test -- --run
```
