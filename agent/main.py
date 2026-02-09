import os
import sys
from pathlib import Path

# 添加 agent 目录到 Python 路径，确保可以导入 api 模块
agent_dir = Path(__file__).parent
if str(agent_dir) not in sys.path:
    sys.path.insert(0, str(agent_dir))

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from tools.tools import tools

# 1. 加载环境变量（建议将 API Key 放在 .env 文件中）
load_dotenv()
# 完全禁用 LangSmith 追踪（避免认证错误）
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGCHAIN_ENDPOINT"] = ""  # 清空端点
os.environ["LANGCHAIN_API_KEY"] = ""  # 清空 API Key
ali_key = os.getenv("ali_key")
openai_api_key = os.getenv("OPENAI_API_KEY")

# 3. 配置 LLM（大语言模型）
llm = ChatOpenAI(
    model_name="deepseek-v3.2",
    temperature=0.5,
    api_key=ali_key,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    streaming=False  # Agent 需要非流式模式
)

# 4. 构建系统提示词
system_prompt = """
你是一个专业的日常记录助手，帮助用户记录、查询和管理日常行为。

【核心功能】
1. 记录：使用 add_user_history 工具记录用户的行为和事件
2. 查询：使用 get_user_chat_history 工具查询历史记录
3. 时间：使用 get_time 工具获取当前时间信息

【工具使用规则】

1. get_time 工具
   - 用途：获取当前时间（年、月、日、时、分）
   - 使用场景：需要当前时间时，或记录时用户未提供时间

2. get_user_chat_history 工具
   - 用途：查询用户的历史记录
   - 参数：user_id (必需，整数，默认 1000001)
   - 可选参数：date (日期字符串，格式 "YYYY-MM-DD")
   - 使用场景：用户要查看、查询、回顾历史记录时

3. add_user_history 工具
   - 用途：添加新的记录
   - 参数：
     * time: 时间字符串，格式 "YYYY-MM-DD HH:MM"
     * text: 记录内容（字符串）
     * userId: 用户ID（整数，默认 1000001）
   - 使用场景：用户要记录、添加、保存内容时
   - 注意：如果用户没提供时间，先调用 get_time 获取

【对话规则】
1. 理解用户意图：仔细分析用户的需求
2. 确认参数：如果缺少必需参数，询问用户或使用合理默认值（userId 默认 1000001）
3. 执行操作：按顺序调用工具
4. 总结结果：操作完成后，用清晰的方式展示结果

【回答风格】
- 使用中文，简洁友好
- 操作前说明："我来帮你..."
- 操作后总结："已完成，..."
- 错误时说明："抱歉，...，建议..."

【示例】
用户："记录一下，今天下午去图书馆学习了"
你：先调用 get_time 获取时间，然后调用 add_user_history 记录
    回复："已记录：今天下午去图书馆学习了（时间：2026-02-03 14:30）"

用户："查看我昨天的记录"
你：调用 get_user_chat_history(user_id=1000001, date="2026-02-02")
    整理查询结果并回复
"""

# 5. 使用新的 create_agent API 创建 Agent
agent = create_agent(
    model=llm,
    system_prompt=system_prompt,
    tools=tools,
    debug=False  # 开启详细日志，能看到 Agent 的思考和工具调用过程
)

def userScanf():
    try:
        text=input('')
        messages = []
        # if memory_summary and "最后查询页码" in memory_summary:
        #     # 将记忆信息作为上下文添加到消息中
        #     context_message = f"[当前记忆状态：{memory_summary}]"
        #     messages.append(HumanMessage(content=context_message))
        
        messages.append(HumanMessage(content=text))
        result=agent.invoke({"messages": messages})
        response_content = result["messages"][-1].content
        print(response_content)
        userScanf()
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

def startAgent():
    result=agent.invoke({"messages": [HumanMessage(content="你好，介绍一下自己")]})
    print(result["messages"][-1].content)
    # userScanf()

if __name__ == "__main__":
    startAgent()
    # result=get_user_chat_history(1000001)
    # print(result)