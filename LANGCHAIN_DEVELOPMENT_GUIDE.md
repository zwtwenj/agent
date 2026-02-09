# LangChain 开发完整指南

## 1. 工具（Tools）- 你已经在使用 ✅

将现有业务封装成工具，让 Agent 调用：
- 数据库查询工具
- API 调用工具
- 文件操作工具
- 业务逻辑工具

## 2. 提示词工程（Prompt Engineering）

### 系统提示词优化
```python
system_prompt = """
你是一个专业的助手，需要：
1. 理解用户意图
2. 选择合适的工具
3. 提供准确的回答
"""
```

### 动态提示词
- 根据上下文调整提示词
- 使用模板变量
- 多轮对话上下文管理

## 3. 记忆管理（Memory）

### 对话记忆
```python
from langchain.memory import ConversationBufferMemory

memory = ConversationBufferMemory(
    return_messages=True,
    memory_key="chat_history"
)
```

### 记忆类型
- **ConversationBufferMemory**: 保存完整对话历史
- **ConversationSummaryMemory**: 保存对话摘要
- **ConversationBufferWindowMemory**: 只保存最近 N 轮对话
- **ConversationSummaryBufferMemory**: 结合摘要和窗口

## 4. 检索增强生成（RAG）

### 向量数据库集成
```python
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings

# 将文档向量化并存储
vectorstore = Chroma.from_documents(documents, embeddings)

# Agent 可以检索相关文档
retriever = vectorstore.as_retriever()
```

### 应用场景
- 知识库问答
- 文档检索
- 上下文增强

## 5. 输出解析器（Output Parsers）

### 结构化输出
```python
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

class MovieInfo(BaseModel):
    title: str
    year: int
    rating: float

parser = PydanticOutputParser(pydantic_object=MovieInfo)
```

### 解析器类型
- **PydanticOutputParser**: 解析为 Pydantic 模型
- **StructuredOutputParser**: 结构化输出
- **OutputFixingParser**: 自动修复格式错误

## 6. 链（Chains）

### 自定义链
```python
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

prompt = PromptTemplate(
    input_variables=["question"],
    template="回答：{question}"
)

chain = LLMChain(llm=llm, prompt=prompt)
```

### 链的组合
- **SequentialChain**: 顺序执行多个链
- **RouterChain**: 根据条件路由到不同链
- **TransformChain**: 数据转换链

## 7. 回调函数（Callbacks）

### 监控和日志
```python
from langchain.callbacks import StdOutCallbackHandler

callbacks = [StdOutCallbackHandler()]

result = agent.invoke(
    {"messages": messages},
    config={"callbacks": callbacks}
)
```

### 回调类型
- **Token 使用监控**: 跟踪 API 调用成本
- **执行时间监控**: 性能分析
- **自定义日志**: 记录 Agent 决策过程

## 8. 多代理系统（Multi-Agent）

### 代理协作
```python
# 创建多个专业 Agent
research_agent = create_agent(...)  # 研究 Agent
writing_agent = create_agent(...)   # 写作 Agent
review_agent = create_agent(...)    # 审核 Agent

# Agent 之间可以协作
```

### 应用场景
- 复杂任务分解
- 专业分工
- 多步骤工作流

## 9. 错误处理和重试

### 自动重试
```python
from langchain.llms import OpenAI
from tenacity import retry, stop_after_attempt

@retry(stop=stop_after_attempt(3))
def call_agent_with_retry():
    return agent.invoke(...)
```

### 错误处理策略
- API 调用失败重试
- 工具调用异常处理
- 降级方案

## 10. 成本控制

### Token 使用监控
```python
from langchain.callbacks import get_openai_callback

with get_openai_callback() as cb:
    result = agent.invoke(...)
    print(f"总成本: ${cb.total_cost}")
    print(f"Token 使用: {cb.total_tokens}")
```

### 优化策略
- 限制最大 Token
- 使用更便宜的模型
- 缓存常见查询

## 11. 评估和测试

### Agent 评估
```python
from langchain.evaluation import AgentEvaluator

evaluator = AgentEvaluator()
results = evaluator.evaluate(agent, test_cases)
```

### 测试框架
- 单元测试 Agent 工具
- 集成测试完整流程
- 性能基准测试

## 12. 流式处理（Streaming）

### 流式输出
```python
# 虽然 create_agent 对非 OpenAI 支持不好
# 但可以：
# 1. 使用 invoke + 逐字符输出（你现在的方案）
# 2. 直接使用 LLM 的流式（不通过 Agent）
# 3. 使用回调函数实现流式
```

## 13. 数据持久化

### 对话历史保存
```python
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import FileChatMessageHistory

history = FileChatMessageHistory("chat_history.json")
memory = ConversationBufferMemory(
    chat_memory=history,
    return_messages=True
)
```

## 14. 安全性和权限控制

### 工具权限
```python
# 限制 Agent 可以使用的工具
allowed_tools = ["get_time", "get_user_history"]
agent = create_agent(
    model=llm,
    tools=[tool for tool in tools if tool.name in allowed_tools]
)
```

## 15. 性能优化

### 并行处理
```python
from concurrent.futures import ThreadPoolExecutor

# 并行调用多个工具
with ThreadPoolExecutor() as executor:
    results = executor.map(call_tool, tool_list)
```

### 缓存
```python
from langchain.cache import InMemoryCache
from langchain.globals import set_llm_cache

set_llm_cache(InMemoryCache())
```

## 实际开发建议

### 优先级排序
1. **工具开发** ✅ (你已经在做)
2. **提示词优化** - 提升 Agent 理解能力
3. **记忆管理** - 支持多轮对话
4. **错误处理** - 提高稳定性
5. **成本监控** - 控制 API 费用
6. **RAG** - 如果需要知识库功能
7. **评估测试** - 确保质量

### 你的项目下一步建议

基于你当前的项目结构，建议：

1. **添加记忆管理**
   ```python
   # 让 Agent 记住之前的对话
   memory = ConversationBufferMemory(...)
   ```

2. **优化提示词**
   ```python
   # 让 Agent 更好地理解你的业务场景
   system_prompt = """
   你是一个帮助用户进行日常记录的智能助手。
   你可以：
   - 记录用户的行为（使用 add_user_history 工具）
   - 查询用户的历史记录（使用 get_user_chat_history 工具）
   - 获取当前时间（使用 get_time 工具）
   """
   ```

3. **添加错误处理**
   ```python
   try:
       result = agent.invoke(...)
   except Exception as e:
       # 降级处理
       return fallback_response()
   ```

4. **成本监控**
   ```python
   # 跟踪每次调用的成本
   with get_openai_callback() as cb:
       result = agent.invoke(...)
   ```

## 总结

LangChain 开发不仅仅是工具封装，还包括：
- ✅ 工具开发（你已经在做）
- 📝 提示词工程
- 🧠 记忆管理
- 🔍 RAG 检索
- 🔗 链式组合
- 📊 监控和评估
- 🛡️ 错误处理
- 💰 成本控制
- 🚀 性能优化

根据你的项目需求，逐步添加这些功能。
