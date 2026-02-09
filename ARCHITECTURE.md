# 项目架构说明

## 当前结构
```
jihua/
├── agent/          # 智能体服务
│   ├── api/        # HTTP 客户端（调用 server）
│   └── tools/      # Agent 工具封装
├── server/         # 后端 API 服务
│   ├── routes/     # 路由定义
│   ├── models/     # 数据模型
│   └── services/   # 业务逻辑层（待创建）
└── web/            # 前端应用
```

## 推荐优化结构

### 方案 1：共享业务逻辑层（推荐用于中小型项目）

```
jihua/
├── agent/              # 智能体服务
│   ├── main.py        # Agent 主程序
│   └── tools/         # Agent 工具（直接调用 services）
│       └── user.py    # 从 services 导入，而非 HTTP 调用
│
├── server/            # 后端 API 服务
│   ├── app.py         # Flask 应用入口
│   ├── routes/        # 路由定义
│   │   ├── user.py    # 用户相关路由
│   │   └── agent.py   # Agent 相关路由
│   ├── models/        # 数据模型（SQLAlchemy）
│   │   └── user.py
│   ├── services/      # 业务逻辑层（核心！）
│   │   └── user_service.py  # 业务逻辑，agent 和 server 都调用
│   └── utils/         # 工具函数
│       └── response.py  # 标准化响应
│
└── web/               # 前端应用
    └── src/
        └── api/       # API 调用封装
```

### 方案 2：保持当前结构但优化（快速方案）

保持当前结构，但：
1. `agent/api/` 改为直接调用 `server` 的业务逻辑（如果可能）
2. 或者创建共享的 `common/` 目录存放业务逻辑

## 市面上常见 AI 产品架构

### 1. ChatGPT / Claude 架构
```
Frontend (Web/App)
    ↓
API Gateway (统一入口)
    ↓
┌───────────┬──────────────┬─────────────┐
│ Chat API  │  Tool API    │  User API   │
└─────┬─────┴──────┬───────┴──────┬──────┘
      │            │              │
  ┌───▼───┐   ┌───▼───┐     ┌───▼───┐
  │ Agent │   │ Tools │     │ User  │
  │Service│   │Service│     │Service│
  └───┬───┘   └───┬───┘     └───┬───┘
      └───────────┴─────────────┘
              │
        ┌─────▼─────┐
        │ Database  │
        └───────────┘
```

### 2. 国内 AI 产品（如文心一言、通义千问）
- **前端层**：Web + 移动端
- **API 层**：统一 REST API（FastAPI/Flask）
- **服务层**：
  - LLM 服务（调用大模型 API）
  - Agent 服务（工具调用、推理）
  - 业务服务（用户、数据管理）
- **数据层**：MySQL + Redis（缓存）

## 关键设计原则

1. **单一数据源**：业务逻辑只在一个地方实现
2. **接口统一**：前端和 Agent 都调用同一个 API
3. **工具复用**：Agent 的工具可以直接调用业务逻辑，而非 HTTP
4. **清晰分层**：Routes → Services → Models → Database

## 实施建议

### 短期（保持当前结构）
1. ✅ 保持 `server/` 作为统一 API 入口
2. ✅ `agent/api/` 通过 HTTP 调用 `server`（当前方式）
3. ⚠️ 注意：确保接口稳定，避免频繁变更

### 长期（推荐优化）
1. 创建 `server/services/` 业务逻辑层
2. `agent/tools/` 直接导入 `services`，而非 HTTP 调用
3. `server/routes/` 也调用 `services`
4. 这样业务逻辑只维护一份

## 示例：优化后的调用关系

### 当前方式（HTTP 调用）
```python
# agent/api/user.py
response = httpx_client.post("http://localhost:5000/api/user/chat/history", ...)
```

### 优化后（直接调用）
```python
# agent/tools/user.py
from server.services.user_service import get_user_chat_history

def get_user_chat_history_tool(user_id):
    return get_user_chat_history(user_id)  # 直接调用，无需 HTTP
```

```python
# server/routes/user.py
from server.services.user_service import get_user_chat_history

@app.route('/api/user/chat/history/<user_id>')
def get_history(user_id):
    data = get_user_chat_history(user_id)  # 同样调用
    return standard_response(code=1, data=data)
```
