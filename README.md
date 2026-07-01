# PolicyMind — Enterprise Policy Knowledge Q&A Platform

基于 Multi-Agent、Hybrid RAG、GraphRAG 与 MCP 的企业内部制度知识问答平台。

## 快速开始

```bash
# 后端
cd backend
pip install -e ".[dev]"
pytest

# 前端
cd frontend
npm ci
npm run dev
```

## 技术栈

- **后端**: Python 3.12, FastAPI, LangGraph, PostgreSQL, Milvus, Neo4j
- **前端**: Vue3, TypeScript, Vite, Pinia

## 许可证

MIT
