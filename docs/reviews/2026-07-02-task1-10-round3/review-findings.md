# Review Findings: PolicyMind TASK 1-10 Round 3

## Findings

### Critical
1. Positive-path authentication is still broken in runtime verification. `create_app(settings=...)` continues to use the passed settings only inside the factory, while request dependencies still resolve `Settings` through `Depends(get_settings)` (`backend/src/policymind/main.py:24-50`, `backend/src/policymind/api/dependencies.py:34-72`). In direct probes, an access token minted from the same `Settings` instance still produced `401` on `/api/v1/auth/me`, `/api/v1/documents/`, `/api/v1/chat`, `/api/v1/reviews/1/approve`, and `/api/v1/evaluations/runs`. This means the round-2 auth wiring defect remains unresolved.
2. The document upload / ingestion path is still placeholder-only. `DocumentService.create_version()` still just hashes bytes and returns a synthetic receipt (`backend/src/policymind/documents/service.py:22-43`), and `/api/v1/documents/` still accepts generic JSON and returns a generated `job_id` without persistence, queueing, or multipart upload handling (`backend/src/policymind/api/v1/documents.py:13-41`).
3. The chat path is still not a real agent path. The API returns canned JSON/SSE responses and still does not call `ChatService` or any LangGraph flow (`backend/src/policymind/api/v1/chat.py:13-53`). So although the frontend now streams events, the backend side remains synthetic.

### Important
1. `get_current_context()` still does not query DB user state or enforce `is_active` / `token_version`; it trusts token claims after signature verification (`backend/src/policymind/api/dependencies.py:44-72`).
2. The evaluation runner is still a stub and the dataset is still far below the documented threshold: `golden_v1.jsonl` has only 25 lines, and `EvaluationRunner.run_case()` still fabricates perfect metrics (`backend/src/policymind/evaluation/runner.py:45-66`).
3. Integration and frontend test gaps remain unchanged. `pytest -m integration -q` deselects all tests, and `npm test -- --run` still exits because no frontend test files exist.

### Minor
1. Frontend auth guard and chat streaming UX have improved, so the UI is less obviously static than in round 2 (`frontend/src/router/index.ts:1-50`, `frontend/src/views/ChatView.vue:1-105`).
2. Those frontend improvements are currently blocked by the still-broken positive auth path on the backend, so they do not yet change acceptance status.

## Acceptance Update

Compared with round 2, this branch shows incremental polish but not a material acceptance change:

| Area | Round 2 | Round 3 |
|------|---------|---------|
| Anonymous auth rejection | fixed | still fixed |
| Positive auth path | fail | fail |
| Upload-to-ingest real path | fail | fail |
| Chat/Agent real path | fail | fail |
| Frontend shell quality | partial improvement | slightly better, still not complete |
| Evaluation realism | fail | fail |
| Integration/frontend tests | fail | fail |

## Overall Judgment

第二轮修复并没有把系统推进到新的验收阶段。当前最准确的状态仍然是：

- TASK 1：通过
- TASK 2：部分完成
- TASK 3：部分完成
- TASK 4～10：未通过

如果你要继续修，我建议下一轮别再铺新界面或新测试名目，先只收口三件事：

1. 让 `create_app(settings=...)` 和依赖注入共用同一份 `Settings`，把正向 token 探针修绿。
2. 把 `/api/v1/documents` 从 JSON 占位改成真实上传 + 持久化 + job 状态。
3. 把 `/api/v1/chat/stream` 真正接到 `ChatService`，哪怕先是最小可运行链路。
