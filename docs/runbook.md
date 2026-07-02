# PolicyMind 运维手册

## 本地开发

```bash
# 后端
cd backend
pip install -e ".[dev]"
alembic upgrade head
uvicorn policymind.main:create_app --reload --factory

# 前端
cd frontend
npm ci
npm run dev
```

## Docker 部署

```bash
# 仅启动基础设施
docker compose -f deploy/compose.infrastructure.yml up -d

# 完整部署
docker compose -f deploy/compose.full.yml up -d
```

## 健康检查

- Liveness: `GET /health/live`
- Readiness: `GET /health/ready`

## 评测

```bash
python scripts/run_evaluation.py
```

## 环境变量

见 `.env.example`
