# PolicyMind TASK 1-10 Remediation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将当前骨架修复为具有真实鉴权、上传摄取、Hybrid RAG、GraphRAG、MCP、LangGraph HITL、前端与评测闭环的可演示系统。

**Architecture:** PostgreSQL保存身份、租户和业务状态；MinIO保存原始文件；Milvus提供Dense与Sparse混合检索；Neo4j保存来源绑定的制度关系；独立MCP Server提供企业工具；LangGraph负责可恢复的Agent编排。所有生产请求从认证后的`RequestContext`传递租户和权限，禁止由请求参数自行选择租户。

**Tech Stack:** Python 3.12、FastAPI、SQLAlchemy 2、Alembic、ARQ、Redis、Milvus、Neo4j、MinIO、LangChain、LangGraph、FastMCP、Vue3、TypeScript、Vitest、Playwright、OpenTelemetry、Prometheus、pytest。

---

## 修复顺序与提交边界

R1～R4是后端主链路，必须顺序执行；R5依赖R2～R4；R6依赖R1和R5；R7在功能闭环后执行。每个任务一个独立Git提交。

### Task R1：配置隔离、真实认证与租户边界

**Files:**

- Modify: `backend/src/policymind/core/config.py`
- Modify: `backend/src/policymind/api/dependencies.py`
- Modify: `backend/src/policymind/auth/schemas.py`
- Modify: `backend/src/policymind/auth/service.py`
- Modify: `backend/src/policymind/auth/router.py`
- Create: `backend/tests/api/test_auth_boundaries.py`
- Modify: `backend/tests/auth/test_auth.py`

- [ ] **Step 1：先写配置命名空间与伪造Token失败测试**

```python
def test_host_debug_variable_does_not_override_app_settings(monkeypatch):
    monkeypatch.setenv("DEBUG", "release")
    settings = Settings(_env_file=None)
    assert settings.DEBUG is False


def test_fake_bearer_token_is_rejected(client):
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer definitely-not-a-jwt"},
    )
    assert response.status_code == 401
```

- [ ] **Step 2：运行红灯测试**

```powershell
cd D:\project\backend
python -m pytest tests/api/test_auth_boundaries.py -q
```

预期：当前代码因读取宿主`DEBUG`且接受伪造Token而失败。

- [ ] **Step 3：隔离配置并实现认证上下文**

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="POLICYMIND_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
```

`get_current_context()`必须完成以下顺序：

1. 缺少Token时抛出`AuthenticationError`。
2. 使用`decode_token()`验证签名和过期时间。
3. 使用`sub`查询用户。
4. 校验用户存在、启用、`token_version`一致。
5. 从数据库用户记录构造`RequestContext`，不信任Token中的角色和权限快照。

- [ ] **Step 4：使登录具有明确租户标识**

```python
class LoginRequest(BaseModel):
    tenant_slug: str = Field(min_length=2, max_length=64)
    username: str = Field(min_length=1, max_length=150)
    password: str = Field(min_length=8, max_length=256)
```

查询条件必须同时包含`Tenant.slug`和`User.username`；刷新Token时同时校验用户所属租户。

- [ ] **Step 5：补齐越权测试**

覆盖匿名访问、伪造Token、禁用用户、Token版本撤销、重复用户名跨租户、角色不足、资源租户不匹配。

- [ ] **Step 6：运行门禁并提交**

```powershell
python -m ruff check src tests
python -m mypy src
python -m pytest tests/auth tests/api/test_auth_boundaries.py -q
git add backend/src/policymind/core backend/src/policymind/api backend/src/policymind/auth backend/tests
git commit -m "fix: enforce tenant-safe request authentication"
```

### Task R2：真实文档上传、版本服务与可恢复摄取

**Files:**

- Create: `backend/src/policymind/documents/service.py`
- Modify: `backend/src/policymind/documents/router.py`
- Modify: `backend/src/policymind/documents/pipeline.py`
- Modify: `backend/src/policymind/documents/jobs.py`
- Modify: `backend/src/policymind/infrastructure/redis/jobs.py`
- Modify: `backend/src/policymind/documents/storage.py`
- Create: `backend/tests/e2e/test_upload_to_index.py`

- [ ] **Step 1：写真实上传链路红灯测试**

```python
async def test_uploaded_markdown_reaches_ready_and_is_searchable(
    authenticated_client,
    inline_dependencies,
):
    response = authenticated_client.post(
        "/api/v1/documents",
        files={"file": ("travel.md", b"# Travel\nHotel limit is 500.", "text/markdown")},
        data={"logical_name": "Travel Policy", "version": "1"},
    )
    assert response.status_code == 202
    job_id = response.json()["job_id"]
    status = authenticated_client.get(f"/api/v1/documents/jobs/{job_id}")
    assert status.json()["status"] == "ready"
    assert "Hotel limit is 500" in inline_dependencies.vector_store.texts
```

- [ ] **Step 2：实现DocumentService**

`create_version()`必须接收`RequestContext`和`ValidatedUpload`，计算SHA-256，在同租户、同文档、同哈希时返回现有版本；否则写入随机存储Key、创建`DocumentVersionRecord`和`IngestionJobRecord`。

- [ ] **Step 3：替换Pipeline硬编码输入**

```python
async def run(self, version_id: int, ctx: RequestContext) -> IngestionResult:
    version = await self._versions.get_for_update(ctx.tenant_id, version_id)
    content = await self._storage.get(version.storage_key)
    parser = self._parsers.resolve(version.mime_type)
    # 每阶段成功后提交状态；失败时保存错误与当前阶段。
```

禁止固定`tenant_id=1`、固定文本、固定日期和随机重复Key。Graph阶段必须调用真实GraphExtractor和GraphRepository。

- [ ] **Step 4：实现ARQ与Inline共享入口**

生产`ARQJobQueue.enqueue()`调用Redis队列；`InlineJobRunner`调用同一个`ingest_document_job()`，不能只生成Job ID。

- [ ] **Step 5：实现S3ObjectStorage**

对象Key只接收服务端生成值；提供`put/get/delete`，MinIO与S3共用S3协议；所有异常转换为领域错误。

- [ ] **Step 6：验证恢复和幂等**

测试每个阶段失败后恢复、重复任务不重复写向量、同哈希不创建新版本、跨租户Job不可查询。

- [ ] **Step 7：运行并提交**

```powershell
python -m pytest tests/documents tests/e2e/test_upload_to_index.py -q
git add backend/src/policymind/documents backend/src/policymind/infrastructure/redis backend/tests
git commit -m "fix: connect uploads to resumable ingestion"
```

### Task R3：真实Milvus Hybrid RAG与完整引用

**Files:**

- Modify: `backend/src/policymind/retrieval/ports.py`
- Modify: `backend/src/policymind/retrieval/embeddings.py`
- Modify: `backend/src/policymind/retrieval/rerank.py`
- Modify: `backend/src/policymind/retrieval/service.py`
- Modify: `backend/src/policymind/retrieval/parent_expansion.py`
- Modify: `backend/src/policymind/retrieval/citations.py`
- Modify: `backend/src/policymind/infrastructure/milvus/store.py`
- Create: `backend/tests/integration/test_milvus_contract.py`

- [ ] **Step 1：建立Memory与Milvus共享Contract Test**

```python
@pytest.mark.parametrize("store_fixture", ["memory_store", "milvus_store"])
async def test_store_filters_tenant_access_and_effective_time(
    request, store_fixture, seeded_chunks
):
    store = request.getfixturevalue(store_fixture)
    result = await store.hybrid_search(
        query_text="travel",
        query_vector=[0.1] * 768,
        tenant_id=7,
        access_level=2,
        at=datetime(2026, 7, 2, tzinfo=UTC),
        limit_per_channel=30,
    )
    assert all(hit.tenant_id == 7 for hit in result.dense + result.sparse)
    assert all(hit.access_level <= 2 for hit in result.dense + result.sparse)
```

- [ ] **Step 2：修复删除范围**

`delete_document_version(tenant_id, version_id)`必须同时匹配两个字段，不能删除租户全部数据。

- [ ] **Step 3：实现生产适配器**

补充真实Embedding Provider、Milvus Dense/Sparse Schema、标量过滤表达式和批量Reranker。Embedding失败必须抛出`EmbeddingUnavailable`。

- [ ] **Step 4：完成检索顺序**

执行Dense Top30 + Sparse Top30 → RRF Top30 → Rerank Top8 → Parent Expansion。向量库不可用返回503；仅Reranker失败时允许记录降级并使用RRF结果。

- [ ] **Step 5：补齐引用字段**

`SearchHit`与`Citation`必须包含`tenant_id`、文档ID、版本ID/版本名、页码、bbox、原文、渠道和分数。回答出现未知引用ID时Critic不得通过。

- [ ] **Step 6：运行并提交**

```powershell
python -m pytest tests/retrieval -q
python -m pytest -m integration tests/integration/test_milvus_contract.py -q
git add backend/src/policymind/retrieval backend/src/policymind/infrastructure/milvus backend/tests
git commit -m "fix: implement filtered milvus hybrid retrieval"
```

### Task R4：来源绑定的Neo4j GraphRAG

**Files:**

- Modify: `backend/src/policymind/graph/extraction.py`
- Modify: `backend/src/policymind/graph/repository.py`
- Modify: `backend/src/policymind/graph/path_ranker.py`
- Modify: `backend/src/policymind/graph/search.py`
- Create: `backend/src/policymind/graph/context.py`
- Create: `backend/src/policymind/infrastructure/neo4j/repository.py`
- Create: `backend/tests/integration/test_neo4j_graph.py`

- [ ] **Step 1：写来源、租户和1～3跳测试**

```python
async def test_graph_paths_are_tenant_and_source_bound(graph_repository):
    paths = await graph_repository.search_paths(
        tenant_id=7,
        seed_entity_ids=["采购制度"],
        max_hops=3,
        limit=10,
    )
    assert paths
    assert all(path["tenant_id"] == 7 for path in paths)
    assert all(path["source_document_version_id"] for path in paths)
    assert all(1 <= path["length"] <= 3 for path in paths)
```

- [ ] **Step 2：强化抽取校验**

保留Regex JSON提取，但`tenant_id`和`source_document_version_id`由调用上下文覆盖，禁止使用LLM提供值或默认租户1。关系端点、Ontology、置信度范围和来源必须全部验证。

- [ ] **Step 3：实现Neo4jRepository**

所有Cypher以`tenant_id`过滤；节点和关系写入来源版本、置信度；MERGE键包含租户与稳定实体键；路径查询限制1～3跳并返回关系类型和来源。

- [ ] **Step 4：完善排序与上下文**

路径分数包含Query匹配、置信度、有效版本和路径长度。Graph Context必须携带可映射到文档引用的来源版本。

- [ ] **Step 5：运行并提交**

```powershell
python -m pytest tests/graph -q
python -m pytest -m integration tests/integration/test_neo4j_graph.py -q
git add backend/src/policymind/graph backend/src/policymind/infrastructure/neo4j backend/tests
git commit -m "fix: add source-bound neo4j graphrag"
```

### Task R5：真实MCP、LangGraph编排与HITL恢复

**Files:**

- Create: `backend/src/policymind/mcp/server.py`
- Create: `backend/src/policymind/mcp/policy.py`
- Modify: `backend/src/policymind/mcp/client.py`
- Modify: `backend/src/policymind/mcp/tools.py`
- Create: `backend/src/policymind/agents/graph.py`
- Create: `backend/src/policymind/agents/json_parser.py`
- Create: `backend/src/policymind/conversations/checkpoint.py`
- Modify: `backend/src/policymind/conversations/service.py`
- Create: `backend/tests/integration/test_mcp_transport.py`
- Create: `backend/tests/agents/test_hitl_resume.py`

- [ ] **Step 1：写“审批前不得执行”测试**

```python
async def test_write_tool_does_not_execute_before_approval(
    mcp_client, review_repository
):
    with pytest.raises(ApprovalRequired):
        await mcp_client.call_tool(
            "create_review_ticket",
            {"question": "q", "evidence": "e"},
        )
    assert await review_repository.count() == 0
```

- [ ] **Step 2：实现独立MCP Transport**

FastMCP Server注册五个工具；Client只通过stdio或HTTP transport执行，禁止导入`policymind.mcp.tools`直接调用。工具服务端再次验证租户和权限。

- [ ] **Step 3：实现审批策略**

Approval Token绑定`thread_id`、工具名、参数哈希、用户、租户和过期时间；单次使用。写操作在验证Token前不得调用Repository；使用Idempotency Key防止恢复时重复创建。

- [ ] **Step 4：构建LangGraph**

```text
Supervisor → Retrieval | Graph | Planner
Planner → Executor
Executor → Executor | Synthesizer
Synthesizer → Critic
Critic → END | Replan | Interrupt
Replan → Planner
```

使用PostgreSQL Checkpointer；所有节点读写统一`AgentState`；限制Tool Call、重试、步骤和Token预算。

- [ ] **Step 5：实现真正恢复**

`ChatService.resume()`必须使用原`thread_id`执行`Command(resume=decision)`。SSE只发公开事件、引用、Graph Path和审核状态，不泄漏隐藏推理。

- [ ] **Step 6：运行并提交**

```powershell
python -m pytest tests/mcp tests/agents tests/conversations -q
python -m pytest -m integration tests/integration/test_mcp_transport.py -q
git add backend/src/policymind/mcp backend/src/policymind/agents backend/src/policymind/conversations backend/tests
git commit -m "fix: implement mcp langgraph and resumable hitl"
```

### Task R6：安全API与可用Vue工作台

**Files:**

- Modify: `backend/src/policymind/main.py`
- Modify: `backend/src/policymind/api/v1/*.py`
- Modify: `frontend/src/api/client.ts`
- Modify: `frontend/src/stores/chat.ts`
- Modify: `frontend/src/router/index.ts`
- Modify: `frontend/src/views/*.vue`
- Create: `frontend/src/views/LoginView.vue`
- Create: `frontend/src/views/SettingsView.vue`
- Create: `frontend/src/**/*.spec.ts`
- Create: `frontend/e2e/core-flow.spec.ts`

- [ ] **Step 1：写API安全与readiness测试**

匿名业务请求必须401；跨租户资源必须404或403；上传使用multipart并限制大小/MIME；必要依赖不可用时`/health/ready`必须503。

- [ ] **Step 2：接入真实Service**

API不得创建空`ChatService()`或返回固定字典。所有Service由依赖容器注入，并接收认证`RequestContext`。响应使用Pydantic Schema。

- [ ] **Step 3：修复SSE解析**

前端必须将同一SSE消息的`event`和`data`组合后再派发；非2xx、非SSE响应和JSON错误应显式显示；取消请求使用同一`AbortController`。

- [ ] **Step 4：实现Markdown安全边界**

```typescript
export function renderSafeMarkdown(source: string): string {
  return DOMPurify.sanitize(marked.parse(source) as string);
}
```

- [ ] **Step 5：完成页面闭环**

实现登录守卫、三栏问答、引用定位、文档上传/版本、Graph子图、审核批准/拒绝、评测对比和设置页。不得以说明文字代替交互。

- [ ] **Step 6：运行并提交**

```powershell
cd D:\project\backend
python -m pytest tests/api tests/e2e -q

cd D:\project\frontend
npm run typecheck
npm test -- --run
npm run build
npx playwright test
git add backend/src/policymind/api backend/src/policymind/main.py backend/tests frontend
git commit -m "fix: deliver secure api and web workflows"
```

### Task R7：真实评测、观测与可构建部署

**Files:**

- Modify: `evaluation/datasets/golden_v1.jsonl`
- Modify: `backend/src/policymind/evaluation/metrics.py`
- Modify: `backend/src/policymind/evaluation/runner.py`
- Modify: `backend/src/policymind/core/telemetry.py`
- Modify: `deploy/compose.infrastructure.yml`
- Modify: `deploy/compose.full.yml`
- Modify: `deploy/docker/*`
- Create: `backend/tests/evaluation/`
- Modify: `docs/runbook.md`

- [ ] **Step 1：扩展Golden Dataset**

达到至少120题，覆盖单文档、跨文档、关系、历史版本、表格/图片、拒答、Prompt Injection和跨租户越权。每题包含预期来源、事实、路由、工具或Graph Path。

- [ ] **Step 2：让Runner调用真实系统**

删除固定答案和固定1.0分；每个Case调用与线上相同的Agent入口，记录检索、路由、工具、引用、延迟、Token与成本。

- [ ] **Step 3：实现指标与消融**

计算Recall@K、MRR、NDCG、Citation Precision/Recall、Graph Path、Routing、Tool、Faithfulness、拒答准确率、P50/P95延迟和成本。运行Dense、Hybrid、+Rerank、+Graph、完整Agent五组变体。

- [ ] **Step 4：接入观测**

OpenTelemetry覆盖API、摄取、检索、Graph、Agent和MCP；Prometheus使用Counter/Histogram/Gauge暴露请求、错误、延迟、队列和模型调用指标。

- [ ] **Step 5：修复镜像和Compose**

Dockerfile的`COPY`路径必须相对于各自build context；安装ARQ/MCP等实际依赖；完整Compose包含Milvus所需etcd/MinIO、健康检查、持久卷和服务依赖条件。

- [ ] **Step 6：最终门禁**

```powershell
cd D:\project\backend
python -m ruff check src tests
python -m mypy src
python -m pytest -m "not integration" --cov=policymind
python -m pytest -m integration

cd D:\project\frontend
npm run typecheck
npm test -- --run
npm run build
npx playwright test

cd D:\project
docker compose -f deploy/compose.infrastructure.yml config
docker compose -f deploy/compose.full.yml config
docker compose -f deploy/compose.full.yml build
python scripts/run_evaluation.py
```

预期：所有命令退出码为0，Golden Case不少于120，报告包含五组消融结果。

- [ ] **Step 7：提交**

```powershell
git add evaluation backend/src/policymind/evaluation backend/src/policymind/core/telemetry.py backend/tests deploy docs scripts
git commit -m "fix: add measurable production delivery"
```

## 最终完成标准

- 匿名、伪造Token和跨租户请求均被拒绝。
- 上传真实文档后可通过Hybrid RAG查询并返回可定位引用。
- Graph回答来自Neo4j 1～3跳、具有租户与版本来源。
- MCP经过独立Transport；写操作审批前零副作用，批准后只执行一次。
- LangGraph可使用相同`thread_id`中断并恢复。
- 前端六类页面具有真实交互，Vitest与Playwright均有测试。
- 评测不少于120题，不允许固定答案或固定分数。
- 单元、集成、E2E、构建、Compose和评测命令全部通过。
